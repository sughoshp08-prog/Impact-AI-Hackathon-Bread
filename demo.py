# main.py — Integrated FastAPI demo (macros + Gemini meal plan)

import json
import numpy as np
import joblib
import os
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Literal
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ─────────────────────────────────────────────
# APP
# ─────────────────────────────────────────────
app = FastAPI(
    title="Indian Diet Planner API",
    description="Predicts daily macros via a regression model and generates a personalised Indian meal plan using Gemini.",
    version="1.0.0",
)

# ─────────────────────────────────────────────
# GEMINI SETUP
# (set GEMINI_API_KEY in your environment)
# ─────────────────────────────────────────────
genai.configure(api_key=os.environ.get("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY"))

# ─────────────────────────────────────────────
# MODEL SETUP
# Loads the regression model if available;
# falls back to the Mifflin–St Jeor BMR formula
# for demo purposes when the .pkl is missing.
# ─────────────────────────────────────────────
MODEL_PATH = "models/regression_model.pkl"
_regression_model = None

if os.path.exists(MODEL_PATH):
    _regression_model = joblib.load(MODEL_PATH)
    print(f"[INFO] Regression model loaded from {MODEL_PATH}")
else:
    print(f"[WARN] {MODEL_PATH} not found — falling back to BMR formula.")

# ─────────────────────────────────────────────
# SCHEMA
# ─────────────────────────────────────────────
class UserInput(BaseModel):
    age: int
    gender: Literal["male", "female"]
    weight: float          # kg
    height: float          # cm
    activity: Literal["sedentary", "moderate", "active"]
    goal: Literal["weight_loss", "maintenance", "muscle_gain"]
    diet: Literal["veg", "non-veg"]
    budget: float          # INR per day

# ─────────────────────────────────────────────
# MACROS SERVICE  (from macros_calculator.py)
# ─────────────────────────────────────────────
_ACTIVITY_MAP = {
    "sedentary": 1.2,
    "moderate": 1.55,
    "active": 1.725,
}

def _gender_to_int(gender: str) -> int:
    """Encode gender the same way the training pipeline did (male=1, female=0)."""
    return 1 if gender == "male" else 0

def _activity_to_int(activity: str) -> int:
    """Encode activity level numerically for the model."""
    return {"sedentary": 0, "moderate": 1, "active": 2}.get(activity, 0)


def predict_calories(data: UserInput) -> float | None:
    """Return calorie prediction from the regression model, or None if unavailable."""
    if _regression_model is None:
        return None
    features = np.array([[
        data.age,
        _gender_to_int(data.gender),
        data.weight,
        data.height,
        _activity_to_int(data.activity),
    ]])
    return float(_regression_model.predict(features)[0])


def calculate_macros(data: UserInput) -> dict:
    """Calculate daily calorie target and macro breakdown."""
    calories = predict_calories(data)

    # Fallback: Mifflin–St Jeor BMR × activity multiplier
    if calories is None:
        if data.gender == "male":
            bmr = 10 * data.weight + 6.25 * data.height - 5 * data.age + 5
        else:
            bmr = 10 * data.weight + 6.25 * data.height - 5 * data.age - 161

        calories = bmr * _ACTIVITY_MAP.get(data.activity, 1.2)

    # Adjust for goal
    if data.goal == "weight_loss":
        calories *= 0.85        # ~15 % deficit
    elif data.goal == "muscle_gain":
        calories *= 1.10        # ~10 % surplus
    # maintenance → no change

    protein = (0.30 * calories) / 4   # 30 % of kcal, 4 kcal/g
    carbs   = (0.40 * calories) / 4   # 40 % of kcal, 4 kcal/g
    fats    = (0.30 * calories) / 9   # 30 % of kcal, 9 kcal/g

    return {
        "calories": round(calories),
        "protein":  round(protein),
        "carbs":    round(carbs),
        "fats":     round(fats),
    }

# ─────────────────────────────────────────────
# LLM SERVICE  (from llm.py)
# ─────────────────────────────────────────────
def generate_meal_plan(macros: dict, data: UserInput) -> dict:
    """Call Gemini to produce a structured Indian meal plan JSON."""
    model = genai.GenerativeModel("gemini-1.5-flash")

    prompt = f"""
You are a certified Indian nutritionist.

## User Profile
- Age: {data.age}
- Gender: {data.gender}
- Weight: {data.weight} kg
- Height: {data.height} cm
- Activity Level: {data.activity}
- Goal: {data.goal}
- Diet Preference: {data.diet}
- Daily Budget: ₹{data.budget}

## Daily Nutrition Targets
- Calories: {macros['calories']} kcal
- Protein: {macros['protein']}g
- Carbohydrates: {macros['carbs']}g
- Fat: {macros['fats']}g

## Instructions
- Generate a realistic Indian diet plan for 1 full day.
- Ensure meals match the calorie and macro targets approximately.
- Keep food simple, affordable, and commonly available in India.
- Respect diet preference (veg/non-veg).
- Distribute calories properly across meals.
- Avoid unhealthy or highly processed foods.

## Output Format (STRICT JSON ONLY)
Do NOT include explanations or markdown.

{{
  "diet_plan": {{
    "breakfast": {{
      "foods": ["item (quantity)"],
      "calories": number
    }},
    "lunch": {{
      "foods": ["item (quantity)"],
      "calories": number
    }},
    "dinner": {{
      "foods": ["item (quantity)"],
      "calories": number
    }},
    "snacks": {{
      "foods": ["item (quantity)"],
      "calories": number
    }}
  }},
  "total_calories": {macros['calories']},
  "notes": "short health tip"
}}

Ensure total calories ≈ target, balanced protein intake, and variety in meals.
"""

    response = model.generate_content(prompt)
    text = response.text.strip()

    # Strip markdown code fences if present
    if text.startswith("```"):
        parts = text.split("```")
        text = parts[1] if len(parts) > 1 else text
        if text.startswith("json"):
            text = text[4:]
    text = text.strip().rstrip("```").strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {"raw_output": text}

# ─────────────────────────────────────────────
# ENDPOINTS
# ─────────────────────────────────────────────
@app.get("/")
def root():
    return {"message": "Indian Diet Planner API is running. POST to /generate-plan to get started."}


@app.post("/macros")
def get_macros(data: UserInput):
    """
    Returns only the calculated macro targets.
    Useful for testing the regression / BMR logic independently.
    """
    return calculate_macros(data)


@app.post("/generate-plan")
def generate_plan(data: UserInput):
    """
    Full pipeline:
    1. Calculate daily macros (model or BMR fallback).
    2. Generate a personalised Indian meal plan via Gemini.
    """
    macros    = calculate_macros(data)
    meal_plan = generate_meal_plan(macros, data)

    return {
        "macros":    macros,
        "meal_plan": meal_plan,
    }

# ─────────────────────────────────────────────
# ENTRYPOINT  (python main.py)
# ─────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)