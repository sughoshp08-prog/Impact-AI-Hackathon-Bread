🥗 Salad Tastes Better
AI-Powered Indian Nutrition Coach
Team: Bread Tastes Better  •  Impact AI Hackathon

📋 Project Overview
Team	Bread Tastes Better
Solution	Salad Tastes Better
Hackathon	Impact AI Hackathon
Problem Statement	AI Nutrition Coach
Domain	Health & Wellness AI
Stack	Python · FastAPI · scikit-learn · Google Gemini

🎯 What is Salad Tastes Better?
Salad Tastes Better is an AI-powered, end-to-end Indian nutrition coach that combines machine learning with a large language model to deliver personalised, budget-aware, culturally relevant diet plans — instantly.

Unlike generic calorie apps, our solution understands the Indian food landscape. It speaks in dal, roti, and sabzi — not chicken breast and quinoa — while still hitting precise macro targets.

❗ Problem Statement
India faces a dual nutrition crisis: widespread undernutrition alongside rising obesity and lifestyle diseases. Existing nutrition tools suffer from three key gaps:

•	Generic, Western-centric food databases that don't reflect Indian eating habits
•	Expensive dietitian consultations that are inaccessible to most of the population
•	Cookie-cutter plans that ignore individual body metrics, activity levels, and daily budgets

💡 Our Solution
A two-stage AI pipeline (initial draft):

Stage 1 — Smart Macro Calculation
A Random Forest Regressor model trained on anthropometric data predicts personalised calorie targets based on age, gender, weight, height, and activity level. The model falls back gracefully to the Mifflin–St Jeor BMR formula if the model file is unavailable, ensuring the API is always production-ready.

Stage 2 — LLM Meal Planning
Calculated macros are passed to Google Gemini (gemini-1.5-flash) with a carefully engineered prompt that enforces Indian food context, user dietary preferences (veg/non-veg), budget constraints (in INR), and strict JSON output — making the response directly parseable by any frontend.

🏗️ Architecture
Request flow through the system:

POST /generate-plan
       │
       ▼
  UserInput (age, gender, weight, height, activity, goal, diet, budget)
       │
       ▼
  calculate_macros()  ──►  RandomForestRegressor (.pkl)
       │                        └── fallback: Mifflin-St Jeor BMR
       │                        └── goal adjustment (±10–15%)
       ▼
  { calories, protein, carbs, fats }
       │
       ▼
  generate_meal_plan()  ──►  Google Gemini 1.5 Flash
       │                        └── Indian nutritionist persona
       │                        └── budget + diet preference
       ▼
  Structured JSON meal plan  (breakfast / lunch / dinner / snacks)

🛠️ Tech Stack
Component	Technology	Purpose
API Framework	FastAPI	REST endpoints, validation, auto Swagger docs
ML Model	scikit-learn (RandomForestRegressor)	Personalised calorie prediction
Fallback Formula	Mifflin–St Jeor BMR	Calorie estimation when model unavailable
LLM	Google Gemini 1.5 Flash	Indian meal plan generation
Data Validation	Pydantic v2	Schema enforcement on all inputs
Model Serialisation	joblib	Save and load trained .pkl model
Config Management	python-dotenv	Secure API key handling via .env
Server	uvicorn	ASGI server for FastAPI

📁 Project Structure
salad-tastes-better/
├── main.py                  # Integrated FastAPI app (all-in-one)
├── demo.py                  # Demo version of the API
├── weight_loss_model.ipynb  # Model training notebook
├── models/
│   └── regression_model.pkl # Trained RandomForest model
├── .env                     # API keys (never commit this)
├── .env.example             # Template for teammates
├── .gitignore
└── requirements.txt

🔌 API Endpoints
GET  /	Health check — confirms the API is running
POST /macros	Returns only macro targets (calories, protein, carbs, fats) — useful for testing the ML model independently
POST /generate-plan	Full pipeline: macros + AI-generated Indian meal plan in structured JSON

📤 Sample Request & Response
Request — POST /generate-plan
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

Response
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

🚀 Getting Started
1. Clone & Install
git clone https://github.com/your-org/salad-tastes-better.git
cd salad-tastes-better
pip install fastapi uvicorn google-generativeai scikit-learn joblib numpy python-dotenv

2. Add your API Key
# Create a .env file in the project root
GEMINI_API_KEY=your_actual_gemini_api_key_here

3. Add the trained model
Place the trained model file at models/regression_model.pkl. If absent, the app automatically falls back to the BMR formula — no crash, no downtime.

4. Run the server
python main.py
# or
uvicorn main:app --reload

5. Open Swagger UI
http://localhost:8000/docs

🤖 ML Model — Weight Loss Predictor
The notebook weight_loss_model.ipynb trains a Random Forest Regressor on anthropometric data to predict weight change (and thus daily calorie needs). Key pipeline steps:

•	Dataset: weight_category.csv with columns — Age, Gender, Height, Weight, BMI, PhysicalActivityLevel, ObesityCategory
•	Feature engineering: CalorieIntake assigned by obesity category, CaloriesBurned = PhysicalActivityLevel × Weight × 5
•	Target: WeightChange = CalorieIntake − CaloriesBurned
•	Preprocessing: duplicate removal, outlier filtering, median/mode imputation, one-hot encoding of ObesityCategory
•	Model: RandomForestRegressor(n_estimators=100, random_state=42)
•	Serialisation: saved as model_joblib.pkl via joblib

⚖️ Goal-Based Calorie Adjustments
weight_loss	−15% calorie deficit from predicted maintenance calories
maintenance	No adjustment — predicted calories used as-is
muscle_gain	+10% calorie surplus above predicted maintenance calories

👥 Team — Bread Tastes Better
We are Bread Tastes Better, a team of developers who believe great nutrition advice shouldn't be expensive or complicated. We built Salad Tastes Better for the Impact AI Hackathon to prove that AI can democratise access to personalised health guidance for every Indian household — regardless of income or location.


Built with ❤️ by Bread Tastes Better  •  Impact AI Hackathon  •  Salad Tastes Better
