import json
import numpy as np
import joblib
import os
import re
# import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Literal, List, Optional
from google import genai
from dotenv import load_dotenv
import uvicorn

# ─── 1. Environment ───────────────────────────────────────────────────────────
load_dotenv()

app = FastAPI(
    title="Indian Diet Planner API",
    description="ML Regression for Macros + Gemini 2.0 for Meal Planning",
    version="3.0.0",
)

# Allow requests from Streamlit (localhost:8501)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── 2. AI Client ─────────────────────────────────────────────────────────────
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

# ─── 3. Model Loading ─────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "weight_change_predictor.pkl")

_regression_model = None
if os.path.exists(MODEL_PATH):
    try:
        _regression_model = joblib.load(MODEL_PATH)
        print("[INFO] Random Forest Model loaded successfully.")
    except Exception as e:
        print(f"[ERROR] Could not load model: {e}")
else:
    print("[WARN] Model file not found. API will use BMR math fallback.")


# ─── 4. Request Schemas ───────────────────────────────────────────────────────

class ClassifyRequest(BaseModel):
    """Used by Tab 1 — Quick Classify"""
    age: int
    gender: str                         # "Male" / "Female" / "Other"
    bmi: float
    activity_level: str                 # e.g. "moderately_active"
    weight_kg: float
    height_cm: float

class NutritionRequest(BaseModel):
    """Used by Tab 2 — Full Nutrition Plan & Tab 3 — Combined Analysis"""
    age: int
    gender: str
    bmi: float
    activity_level: str
    weight_kg: float
    height_cm: float
    chronic_conditions: List[str] = []
    budget_per_day_inr: float = 250.0
    food_preference: str = "veg"        # "veg" / "non-veg" / "vegan"
    plan_duration: str = "weekly"       # "weekly" / "monthly"
    allergies: List[str] = []


# ─── 5. Shared Helpers ────────────────────────────────────────────────────────

# Normalise gender from Streamlit ("Male"/"Female"/"Other") → model literal
def _norm_gender(g: str) -> str:
    return "male" if g.lower().startswith("m") else "female"

# Normalise activity level from Streamlit multi-word → model 3-value
_ACTIVITY_MAP = {
    "sedentary": 1,
    "lightly_active": 1,
    "moderately_active": 2,
    "moderate": 2,
    "very_active": 3,
    "extra_active": 3,
    "active": 3,
}

def _activity_val(a: str) -> int:
    return _ACTIVITY_MAP.get(a.lower(), 2)

def _bmi_category(bmi: float) -> str:
    if bmi < 18.5: return "Underweight (BMI < 18.5)"
    if bmi < 25:   return "Normal Weight (BMI 18.5–24.9)"
    if bmi < 30:   return "Overweight (BMI 25–29.9)"
    if bmi < 35:   return "Obese (BMI 30–34.9)"
    return "Extremely Obese (BMI ≥ 35)"

def _body_type(bmi: float) -> str:
    if bmi < 18.5: return "underweight"
    if bmi < 25:   return "normal"
    if bmi < 30:   return "overweight"
    return "obese"

def _risk_level(bmi: float, conditions: List[str]) -> str:
    has_condition = any(c not in ("none", "") for c in conditions)
    if bmi >= 30 or has_condition: return "high"
    if bmi >= 25:                  return "moderate"
    return "low"

def _model_confidence(bmi: float) -> float:
    """Simulate confidence: higher in clear BMI ranges, slightly lower near boundaries."""
    boundaries = [18.5, 25.0, 30.0, 35.0]
    min_dist = min(abs(bmi - b) for b in boundaries)
    return round(min(0.95, 0.72 + min_dist * 0.025), 2)


def _compute_macros(age, gender_str, weight, height, activity_str, goal_factor=1.0):
    """Core ML / BMR calorie + macro calculation. Returns flat dict."""
    height_m = height / 100
    bmi = weight / (height_m ** 2)
    gender_val = 1 if _norm_gender(gender_str) == "male" else 0
    act_val = _activity_val(activity_str)

    # One-hot BMI categories
    cat_obese = cat_overweight = cat_underweight = cat_extreme = cat_normal = 0
    if bmi < 18.5:          cat_underweight = 1
    elif bmi < 25:          cat_normal = 1
    elif bmi < 30:          cat_overweight = 1
    elif bmi < 35:          cat_obese = 1
    else:                   cat_extreme = 1

    features = [age, gender_val, height, weight, bmi,
                act_val,
                cat_obese, cat_overweight, cat_underweight, cat_extreme, cat_normal]

    try:
        if _regression_model:
            maintenance = float(_regression_model.predict([features])[0])
        else:
            raise Exception("fallback")
    except Exception:
        base = (10 * weight) + (6.25 * height) - (5 * age)
        maintenance = (base + 5) if _norm_gender(gender_str) == "male" else (base - 161)
        maintenance *= (1.1 + act_val * 0.1)

    target = round(maintenance * goal_factor)
    protein_g  = int((target * 0.25) / 4)
    carbs_g    = int((target * 0.45) / 4)
    fat_g      = int((target * 0.30) / 9)
    fiber_g    = 28 if _norm_gender(gender_str) == "male" else 25
    water_ml   = int(weight * 35)   # 35 ml/kg rule of thumb

    return {
        "calories":    target,
        "protein_g":   protein_g,
        "protein_pct": 25,
        "carbs_g":     carbs_g,
        "carbs_pct":   45,
        "fat_g":       fat_g,
        "fat_pct":     30,
        "fiber_g":     fiber_g,
        "water_ml":    water_ml,
    }


def _budget_label(inr: float) -> str:
    if inr < 150:  return "Low"
    if inr < 400:  return "Medium"
    return "High"

def _region_from_pref(food_pref: str) -> str:
    # Default — can be extended if region is exposed in sidebar later
    return "North Indian"

def _diet_type(food_pref: str) -> str:
    m = {"veg": "Vegetarian", "vegan": "Vegan", "non-veg": "Non-Vegetarian"}
    return m.get(food_pref, "Vegetarian")


# ─── 6. Gemini Helpers ────────────────────────────────────────────────────────

def _gemini_classify(age, gender, bmi, activity, weight, height):
    """Ask Gemini for risk factors & recommendations given vitals."""
    prompt = f"""
You are a clinical nutritionist. Given:
  Age={age}, Gender={gender}, BMI={bmi:.1f}, Activity={activity},
  Weight={weight}kg, Height={height}cm

Return ONLY valid JSON (no markdown fences):
{{
  "risk_factors": ["<short factor>", ...],
  "recommendations": ["<actionable tip>", ...]
}}
Provide 2-4 risk_factors and 3-5 recommendations relevant to this profile.
"""
    try:
        resp = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
        match = re.search(r'\{.*\}', resp.text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
    except Exception:
        pass
    # Fallback
    return {
        "risk_factors": ["Sedentary lifestyle risk", "BMI monitoring recommended"],
        "recommendations": [
            "Aim for 8,000–10,000 steps daily",
            "Include protein in every meal",
            "Limit refined carbohydrates",
            "Stay hydrated — 2–3 litres of water per day",
        ]
    }


def _gemini_nutrition_plan(macros, age, gender, food_pref, budget_inr,
                           plan_duration, conditions, allergies):
    """Ask Gemini for a multi-day Indian diet plan matching the frontend schema."""
    num_days = 7 if plan_duration == "weekly" else 30
    budget_label = _budget_label(budget_inr)
    diet_type = _diet_type(food_pref)
    allergy_str = ", ".join(allergies) if allergies else "None"
    condition_str = ", ".join(c for c in conditions if c != "none") or "None"

    prompt = f"""
You are an expert Indian clinical nutritionist.

Profile: Age={age}, Gender={gender}, Diet={diet_type},
         Budget=₹{budget_inr}/day ({budget_label}), Conditions={condition_str},
         Allergies={allergy_str}

Daily targets: {macros['calories']} kcal, Protein {macros['protein_g']}g,
               Carbs {macros['carbs_g']}g, Fat {macros['fat_g']}g

Generate a {num_days}-day Indian meal plan.

Return ONLY valid JSON (no markdown fences):
{{
  "diet_plan": [
    {{
      "day": "Day 1",
      "total_calories": <int>,
      "macros_summary": "P:XXg C:XXg F:XXg",
      "meals": [
        {{
          "time": "8:00 AM",
          "meal_name": "Breakfast",
          "calories": <int>,
          "foods": ["<food item>", ...],
          "notes": "<clinical tip>"
        }},
        {{ "time": "1:00 PM",  "meal_name": "Lunch",   "calories": <int>, "foods": [...], "notes": "" }},
        {{ "time": "4:00 PM",  "meal_name": "Snack",   "calories": <int>, "foods": [...], "notes": "" }},
        {{ "time": "8:00 PM",  "meal_name": "Dinner",  "calories": <int>, "foods": [...], "notes": "" }}
      ]
    }}
    // ... generate for all {num_days} days
  ],
  "foods_to_avoid": ["<food>", ...],
  "foods_to_include": ["<food>", ...],
  "hydration_recommendation": "<sentence>",
  "supplement_suggestions": ["<supplement>", ...],
  "notes": "<overall clinical note>"
}}
"""
    try:
        resp = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
            # Increase output budget for multi-day plans
        )
        match = re.search(r'\{.*\}', resp.text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
    except Exception:
        pass

    # ── Fallback demo plan ────────────────────────────────────────────────────
    day_template = {
        "total_calories": macros["calories"],
        "macros_summary": f"P:{macros['protein_g']}g C:{macros['carbs_g']}g F:{macros['fat_g']}g",
        "meals": [
            {"time": "8:00 AM", "meal_name": "Breakfast",
             "calories": int(macros["calories"] * 0.25),
             "foods": ["Masala Oats", "Boiled Eggs / Paneer", "Green Tea"],
             "notes": "High-fibre breakfast stabilises blood sugar."},
            {"time": "1:00 PM", "meal_name": "Lunch",
             "calories": int(macros["calories"] * 0.35),
             "foods": ["Dal Tadka", "Brown Rice / Multigrain Roti", "Sabzi", "Curd"],
             "notes": "Balanced macros; opt for seasonal vegetables."},
            {"time": "4:00 PM", "meal_name": "Snack",
             "calories": int(macros["calories"] * 0.10),
             "foods": ["Roasted Chana", "Coconut Water"],
             "notes": "Keeps metabolism active."},
            {"time": "8:00 PM", "meal_name": "Dinner",
             "calories": int(macros["calories"] * 0.30),
             "foods": ["Grilled Chicken / Tofu", "Roti", "Stir-fried Veggies"],
             "notes": "Light dinner aids overnight recovery."},
        ]
    }
    num_days = 7 if plan_duration == "weekly" else 30
    diet_plan = [{**day_template, "day": f"Day {i+1}"} for i in range(num_days)]

    return {
        "diet_plan": diet_plan,
        "foods_to_avoid": ["Maida products", "Fried snacks", "Sugary drinks", "Processed meats"],
        "foods_to_include": ["Dal", "Ragi", "Amla", "Flaxseeds", "Turmeric milk"],
        "hydration_recommendation": f"Drink at least {macros['water_ml']} ml of water daily, more on active days.",
        "supplement_suggestions": ["Vitamin D3", "Omega-3", "Magnesium Glycinate"],
        "notes": "Plan based on standard Indian dietary guidelines. Adjust portion sizes based on hunger cues."
    }


# ─── 7. Endpoints ─────────────────────────────────────────────────────────────

@app.get("/")
def home():
    return {"status": "API Active", "project": "Salad Tastes Better", "version": "3.0.0"}


# ── Tab 1: Body Classification ────────────────────────────────────────────────
@app.post("/api/v1/classify")
def classify(data: ClassifyRequest):
    bmi = data.bmi
    bt = _body_type(bmi)
    risk = _risk_level(bmi, [])
    conf = _model_confidence(bmi)
    extras = _gemini_classify(data.age, data.gender, bmi,
                              data.activity_level, data.weight_kg, data.height_cm)
    return {
        "body_type":        bt,
        "bmi":              round(bmi, 1),
        "bmi_category":     _bmi_category(bmi),
        "risk_level":       risk,
        "model_confidence": conf,
        "risk_factors":     extras.get("risk_factors", []),
        "recommendations":  extras.get("recommendations", []),
    }


# ── Tab 2: Full Nutrition Plan ────────────────────────────────────────────────
@app.post("/api/v1/nutrition-plan")
def nutrition_plan(data: NutritionRequest):
    # Goal factor: weight loss if obese/overweight, muscle gain if underweight
    bmi = data.bmi
    if bmi >= 25:       goal_factor = 0.85
    elif bmi < 18.5:    goal_factor = 1.10
    else:               goal_factor = 1.0

    macros = _compute_macros(data.age, data.gender, data.weight_kg,
                             data.height_cm, data.activity_level, goal_factor)

    plan = _gemini_nutrition_plan(
        macros, data.age, data.gender, data.food_preference,
        data.budget_per_day_inr, data.plan_duration,
        data.chronic_conditions, data.allergies
    )

    return {
        "status": "success",
        "daily_macros": macros,
        **plan   # diet_plan, foods_to_avoid, foods_to_include, hydration, supplements, notes
    }


# ── Tab 3: Combined / Full Analysis ──────────────────────────────────────────
@app.post("/api/v1/full-analysis")
def full_analysis(data: NutritionRequest):
    bmi = data.bmi
    bt = _body_type(bmi)
    risk = _risk_level(bmi, data.chronic_conditions)
    conf = _model_confidence(bmi)

    # Classification sub-result
    extras = _gemini_classify(data.age, data.gender, bmi,
                              data.activity_level, data.weight_kg, data.height_cm)

    classification = {
        "body_type":        bt,
        "bmi":              round(bmi, 1),
        "bmi_category":     _bmi_category(bmi),
        "risk_level":       risk,
        "model_confidence": conf,
        "risk_factors":     extras.get("risk_factors", []),
        "recommendations":  extras.get("recommendations", []),
    }

    # Nutrition sub-result
    if bmi >= 25:       goal_factor = 0.85
    elif bmi < 18.5:    goal_factor = 1.10
    else:               goal_factor = 1.0

    macros = _compute_macros(data.age, data.gender, data.weight_kg,
                             data.height_cm, data.activity_level, goal_factor)

    plan = _gemini_nutrition_plan(
        macros, data.age, data.gender, data.food_preference,
        data.budget_per_day_inr, data.plan_duration,
        data.chronic_conditions, data.allergies
    )

    return {
        "status": "success",
        "classification": classification,
        "nutrition_plan": {
            "daily_macros": macros,
            **plan
        }
    }


# ── Legacy endpoint (kept for backward compat) ────────────────────────────────
@app.post("/generate-plan")
def legacy_generate_plan(data: NutritionRequest):
    return nutrition_plan(data)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
