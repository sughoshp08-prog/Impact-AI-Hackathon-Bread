# 🥗 Salad Tastes Better
**AI-Powered Indian Nutrition Coach**  
**Team:** Bread Tastes Better • Impact AI Hackathon
View demo version here deployed on render
Backend and RandomForest : https://impact-ai-hackathon-bread-backend.onrender.com
Frontend : https://impact-ai-hackathon-bread.onrender.com
(If frontend does not load properly, open backend link and let it load first)

## 📋 Project Overview
- **Solution:** Salad Tastes Better
- **Hackathon:** Impact AI Hackathon
- **Problem:** Personalized AI Nutrition Coach for India
- **Domain:** Health & Wellness
- **Stack:** Python · FastAPI · scikit-learn · Google Gemini


## 🎯 About Salad Tastes Better

Salad Tastes Better is an AI-powered end-to-end Indian nutrition coach built for accessibility and cultural relevance. It delivers personalized, budget-friendly meal plans centered on Indian foods. Unlike generic apps, it understands Indian culinary habits and macronutrient needs.


### Key Features

- Personalized calorie and macro prediction (Random Forest, fallback to BMR)
- Indian meal generation (Google Gemini LLM)
- Supports diet preference (veg/non-veg), activity level, and user budget
- Simple REST API with FastAPI backend and sample frontend

---

## 🗂️ Repository Structure

```
/
├── Backend/
│   ├── demo.py                    # Backend demo/script
│   ├── ml_model.ipynb             # ML model training notebook
│   ├── requirements.txt           # Backend dependencies
│   ├── weight_change_predictor_rf.pkl # Trained RandomForestRegressor model
│   └── weight_loss_model.ipynb    # Weight loss model notebook
├── Frontend/
│   ├── frontend.py                # Frontend script (e.g. Streamlit or other UI)
│   └── requirements.txt           # Frontend dependencies
├── README.md
└── requirements.txt               # (Possibly global dependencies)
```

- **Backend/**: Contains API code, ML models, and notebooks.
- **Frontend/**: Contains UI/client code and dependencies.

---

## 🔌 API Endpoints

_Serve from the Backend directory_

- `GET /` — Health check
- `POST /macros` — Returns macro targets
- `POST /generate-plan` — Generates complete, structured meal plan using the ML model and LLM

---

## 🚀 Getting Started

### 1. Clone the repo

```sh
git clone https://github.com/sughoshp08-prog/Impact-AI-Hackathon-Bread.git
cd Impact-AI-Hackathon-Bread/Backend
```

### 2. Install backend dependencies

```sh
pip install -r requirements.txt
```

### 3. Add any necessary config (API keys, models)

- Ensure `weight_change_predictor_rf.pkl` is present for predictions.
- Add environment variables as needed for LLM access (see code for details).

### 4. Run the backend server

```sh
python demo.py
# or if using FastAPI standard
uvicorn main:app --reload
```

### 5. (Optional) Run the frontend

```sh
cd ../Frontend
pip install -r requirements.txt
python frontend.py
```

---

## 🧠 Model Details

- **Backend ML Model:** RandomForestRegressor trained on Indian anthropometric and dietary data.
- **Fallback:** Mifflin-St Jeor BMR formula.
- **LLM integration:** Google Gemini 1.5-Flash for meal plan creation.

---

## 💡 Example API Request

`POST /generate-plan`
```json
{
  "age": 25,
  "gender": "male",
  "weight": 72,
  "height": 175,
  "activity": "moderate",
  "goal": "weight_loss",
  "diet": "veg",
  "budget": 200
}
```

**Response:**
```json
{
  "macros": { "calories": 1938, "protein": 145, "carbs": 194, "fats": 65 },
  "meal_plan": {
    "diet_plan": {
      "breakfast": { "foods": ["Oats upma (1 cup)", "Boiled eggs (2)"], "calories": 430 },
      "lunch":     { "foods": ["Brown rice (1 cup)", "Dal (1 bowl)", "Sabzi (1 bowl)"], "calories": 620 },
      "dinner":    { "foods": ["Roti (2)", "Paneer bhurji (1 bowl)"], "calories": 580 },
      "snacks":    { "foods": ["Banana (1)", "Roasted chana (30g)"], "calories": 308 }
    },
    "total_calories": 1938,
    "notes": "Drink 8–10 glasses of water daily."
  }
}
```

---

## 👥 Team

Built by **Bread Tastes Better** for the Impact AI Hackathon — democratizing access to high-quality nutrition advice for India.

---
