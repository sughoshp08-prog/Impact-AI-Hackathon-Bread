import streamlit as st
import requests
import json
from typing import Optional

# ─── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Salad Tastes Better — Personalised Indian Nutrition Planner",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

/* Root variables */
:root {
    --saffron: #FF6B2B;
    --turmeric: #F5A623;
    --leaf: #2ECC71;
    --deep: #0D1117;
    --card: #161B22;
    --border: #21262D;
    --text: #E6EDF3;
    --muted: #8B949E;
    --risk-low: #2ECC71;
    --risk-mod: #F5A623;
    --risk-high: #FF4757;
}

/* Global */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: var(--deep) !important;
    color: var(--text) !important;
}

.stApp {
    background-color: var(--deep) !important;
}

/* Hero Header */
.hero-header {
    background: linear-gradient(135deg, #FF6B2B08 0%, #F5A62308 50%, #2ECC7108 100%);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 2.5rem 3rem;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
}
.hero-header::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -10%;
    width: 400px;
    height: 400px;
    background: radial-gradient(circle, #FF6B2B15 0%, transparent 70%);
    border-radius: 50%;
}
.hero-title {
    font-family: 'Syne', sans-serif;
    font-size: 2.8rem;
    font-weight: 800;
    background: linear-gradient(135deg, #FF6B2B, #F5A623, #2ECC71);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0;
    line-height: 1.1;
}
.hero-sub {
    font-size: 1.05rem;
    color: var(--muted);
    margin-top: 0.5rem;
    font-weight: 300;
}
.hero-badges {
    display: flex;
    gap: 0.6rem;
    margin-top: 1.2rem;
    flex-wrap: wrap;
}
.badge {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 50px;
    padding: 0.3rem 0.9rem;
    font-size: 0.78rem;
    color: var(--muted);
    font-weight: 500;
}
.badge-orange { border-color: #FF6B2B44; color: #FF6B2B; }
.badge-green  { border-color: #2ECC7144; color: #2ECC71; }
.badge-yellow { border-color: #F5A62344; color: #F5A623; }

/* Pipeline Viz */
.pipeline {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 1rem 1.5rem;
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 12px;
    margin-bottom: 2rem;
    overflow-x: auto;
    flex-wrap: wrap;
}
.pipe-step {
    display: flex;
    align-items: center;
    gap: 0.4rem;
    white-space: nowrap;
}
.pipe-node {
    background: linear-gradient(135deg, #FF6B2B22, #FF6B2B11);
    border: 1px solid #FF6B2B44;
    border-radius: 8px;
    padding: 0.4rem 0.8rem;
    font-size: 0.78rem;
    font-weight: 600;
    color: #FF6B2B;
    font-family: 'Syne', sans-serif;
}
.pipe-node.active {
    background: linear-gradient(135deg, #FF6B2B, #F5A623);
    border-color: #FF6B2B;
    color: white;
    box-shadow: 0 0 16px #FF6B2B44;
}
.pipe-arrow { color: var(--muted); font-size: 1rem; }

/* Sidebar styling */
section[data-testid="stSidebar"] {
    background-color: var(--card) !important;
    border-right: 1px solid var(--border) !important;
}
section[data-testid="stSidebar"] * {
    color: var(--text) !important;
}
.sidebar-section {
    font-family: 'Syne', sans-serif;
    font-weight: 700;
    font-size: 0.7rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: var(--muted) !important;
    margin: 1.2rem 0 0.5rem 0;
    padding-bottom: 0.4rem;
    border-bottom: 1px solid var(--border);
}

/* Result Cards */
.result-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    transition: border-color 0.2s;
}
.result-card:hover { border-color: #FF6B2B44; }

.metric-row {
    display: flex;
    gap: 1rem;
    flex-wrap: wrap;
    margin-bottom: 1rem;
}
.metric-box {
    flex: 1;
    min-width: 100px;
    background: #0D1117;
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1rem;
    text-align: center;
}
.metric-val {
    font-family: 'Syne', sans-serif;
    font-size: 2rem;
    font-weight: 800;
    color: #FF6B2B;
    display: block;
}
.metric-label {
    font-size: 0.72rem;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

/* Body Type Badge */
.body-type-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 1.2rem;
    border-radius: 50px;
    font-family: 'Syne', sans-serif;
    font-weight: 700;
    font-size: 1rem;
    margin-bottom: 1rem;
}
.bt-normal      { background: #2ECC7120; border: 1px solid #2ECC7160; color: #2ECC71; }
.bt-overweight  { background: #F5A62320; border: 1px solid #F5A62360; color: #F5A623; }
.bt-obese       { background: #FF475720; border: 1px solid #FF475760; color: #FF4757; }
.bt-underweight { background: #5B8DEF20; border: 1px solid #5B8DEF60; color: #5B8DEF; }

/* Risk Badge */
.risk-badge {
    display: inline-block;
    padding: 0.2rem 0.7rem;
    border-radius: 50px;
    font-size: 0.78rem;
    font-weight: 600;
}
.risk-low  { background: #2ECC7120; color: #2ECC71; border: 1px solid #2ECC7144; }
.risk-moderate { background: #F5A62320; color: #F5A623; border: 1px solid #F5A62344; }
.risk-high { background: #FF475720; color: #FF4757; border: 1px solid #FF475744; }

/* Macro Bar */
.macro-bar-container { margin: 1rem 0; }
.macro-row {
    display: flex;
    align-items: center;
    gap: 0.8rem;
    margin-bottom: 0.6rem;
}
.macro-name {
    width: 80px;
    font-size: 0.8rem;
    color: var(--muted);
    font-weight: 500;
}
.macro-bar-track {
    flex: 1;
    height: 8px;
    background: var(--border);
    border-radius: 50px;
    overflow: hidden;
}
.macro-bar-fill {
    height: 100%;
    border-radius: 50px;
    transition: width 0.6s ease;
}
.macro-value {
    width: 80px;
    font-size: 0.8rem;
    color: var(--text);
    font-weight: 500;
    text-align: right;
}

/* Day Plan Card */
.day-card {
    background: var(--deep);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.8rem;
}
.day-title {
    font-family: 'Syne', sans-serif;
    font-weight: 700;
    color: #FF6B2B;
    font-size: 0.95rem;
    margin-bottom: 0.8rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.meal-item {
    padding: 0.5rem 0;
    border-bottom: 1px solid var(--border);
}
.meal-item:last-child { border-bottom: none; }
.meal-time {
    font-size: 0.72rem;
    color: var(--muted);
    font-weight: 500;
}
.meal-name {
    font-weight: 600;
    font-size: 0.88rem;
    color: var(--text);
}
.meal-cal {
    font-size: 0.75rem;
    color: #F5A623;
    font-weight: 600;
}
.food-tag {
    display: inline-block;
    background: #FF6B2B0D;
    border: 1px solid #FF6B2B22;
    border-radius: 6px;
    padding: 0.15rem 0.5rem;
    font-size: 0.72rem;
    color: var(--muted);
    margin: 0.1rem 0.15rem;
}

/* Recommendation list */
.rec-item {
    display: flex;
    align-items: flex-start;
    gap: 0.6rem;
    padding: 0.5rem 0;
    border-bottom: 1px solid var(--border);
    font-size: 0.88rem;
    color: var(--text);
}
.rec-item:last-child { border-bottom: none; }
.rec-dot { color: #2ECC71; margin-top: 2px; flex-shrink: 0; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: var(--card) !important;
    border-radius: 12px;
    border: 1px solid var(--border);
    padding: 0.3rem;
    gap: 0.2rem;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border-radius: 8px !important;
    color: var(--muted) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.88rem !important;
    padding: 0.4rem 1rem !important;
    border: none !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #FF6B2B, #F5A623) !important;
    color: white !important;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #FF6B2B, #F5A623) !important;
    border: none !important;
    color: white !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    padding: 0.6rem 2rem !important;
    border-radius: 10px !important;
    letter-spacing: 0.03em !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 4px 16px #FF6B2B33 !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 24px #FF6B2B55 !important;
}

/* Form elements */
.stSelectbox > div > div,
.stNumberInput > div > div > input,
.stSlider > div > div > div {
    background: var(--card) !important;
    border-color: var(--border) !important;
    color: var(--text) !important;
    border-radius: 10px !important;
}
.stMultiSelect > div > div {
    background: var(--card) !important;
    border-color: var(--border) !important;
    border-radius: 10px !important;
}

/* Info boxes */
.info-box {
    background: #5B8DEF10;
    border: 1px solid #5B8DEF33;
    border-radius: 10px;
    padding: 0.8rem 1rem;
    font-size: 0.85rem;
    color: #7BA3F5;
    margin: 0.5rem 0;
}
.warn-box {
    background: #FF475710;
    border: 1px solid #FF475733;
    border-radius: 10px;
    padding: 0.8rem 1rem;
    font-size: 0.85rem;
    color: #FF6B7A;
    margin: 0.5rem 0;
}
.success-box {
    background: #2ECC7110;
    border: 1px solid #2ECC7133;
    border-radius: 10px;
    padding: 0.8rem 1rem;
    font-size: 0.85rem;
    color: #3DD68C;
    margin: 0.5rem 0;
}

/* Supplement tag */
.supp-tag {
    display: inline-block;
    background: #5B8DEF15;
    border: 1px solid #5B8DEF33;
    border-radius: 8px;
    padding: 0.3rem 0.8rem;
    font-size: 0.8rem;
    color: #7BA3F5;
    margin: 0.2rem;
    font-weight: 500;
}

/* Section headings */
.section-heading {
    font-family: 'Syne', sans-serif;
    font-weight: 700;
    font-size: 1.1rem;
    color: var(--text);
    margin: 1.5rem 0 0.8rem 0;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.section-heading::after {
    content: '';
    flex: 1;
    height: 1px;
    background: var(--border);
    margin-left: 0.5rem;
}

/* Loading spinner override */
.stSpinner > div {
    border-top-color: #FF6B2B !important;
}

/* Streamlit element overrides */
div[data-testid="stMarkdownContainer"] p {
    color: var(--text) !important;
}
label { color: var(--text) !important; }
.stRadio > div { color: var(--text) !important; }

/* Divider */
hr { border-color: var(--border) !important; }

/* BMI gauge styling */
.bmi-gauge {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1rem 1.2rem;
}
.bmi-track {
    height: 12px;
    border-radius: 50px;
    background: linear-gradient(to right, #5B8DEF 0%, #2ECC71 30%, #F5A623 60%, #FF4757 100%);
    position: relative;
    margin: 0.5rem 0;
}

/* Confidence bar */
.conf-bar {
    height: 6px;
    border-radius: 50px;
    background: linear-gradient(135deg, #FF6B2B, #F5A623);
    margin-top: 0.3rem;
}

/* Avoid/Include food chips */
.avoid-chip {
    display: inline-block;
    background: #FF475710;
    border: 1px solid #FF475733;
    border-radius: 6px;
    padding: 0.2rem 0.6rem;
    font-size: 0.78rem;
    color: #FF6B7A;
    margin: 0.2rem;
}
.include-chip {
    display: inline-block;
    background: #2ECC7110;
    border: 1px solid #2ECC7133;
    border-radius: 6px;
    padding: 0.2rem 0.6rem;
    font-size: 0.78rem;
    color: #3DD68C;
    margin: 0.2rem;
}
</style>
""", unsafe_allow_html=True)


# ─── Config ───────────────────────────────────────────────────────────────────
API_BASE = "https://impact-ai-hackathon-bread-backend.onrender.com"


# --- Connectivity Check ---
def check_api_health():
    try:
        # FastAPI usually has a default 404 or root response
        response = requests.get(f"{API_BASE}/", timeout=5)
        if response.status_code < 500:
            return True
    except:
        return False

with st.sidebar:
    st.markdown("---")
    if check_api_health():
        st.success("● API Connected", icon="✅")
    else:
        st.error("○ API Offline", icon="🚨")
        st.info(f"Checking: {API_BASE}")

# ─── Helpers ──────────────────────────────────────────────────────────────────
def bmi_color(bmi):
    if bmi < 18.5: return "#5B8DEF"
    if bmi < 25:   return "#2ECC71"
    if bmi < 30:   return "#F5A623"
    return "#FF4757"

def body_type_class(bt):
    m = {"normal":"bt-normal","overweight":"bt-overweight","obese":"bt-obese","underweight":"bt-underweight"}
    return m.get(bt, "bt-normal")

def body_type_icon(bt):
    m = {"normal":"✅","overweight":"⚠️","obese":"🔴","underweight":"💙"}
    return m.get(bt, "●")

def risk_class(r):
    m = {"low":"risk-low","moderate":"risk-moderate","high":"risk-high"}
    return m.get(r, "risk-low")

def macro_color(name):
    m = {"Protein":"#FF6B2B","Carbs":"#F5A623","Fat":"#2ECC71","Fiber":"#5B8DEF"}
    return m.get(name, "#8B949E")

def call_api(endpoint, payload):
    try:
        r = requests.post(f"{API_BASE}/{endpoint}", json=payload, timeout=120)
        r.raise_for_status()
        return r.json(), None
    except requests.exceptions.ConnectionError:
        return None, "⚠️ Cannot connect to backend. Make sure the FastAPI server is running on `http://localhost:8000`."
    except requests.exceptions.HTTPError as e:
        detail = ""
        try: detail = e.response.json().get("detail", str(e))
        except: detail = str(e)
        return None, f"API Error: {detail}"
    except Exception as e:
        return None, str(e)


# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <style>
    .sidebar-title {
        font-family: 'Syne', sans-serif;
        font-size: 1.3rem;
        font-weight: 800;
        display: flex;
        align-items: center;
        gap: 0.4rem;
    }

    .gradient-text {
        background: linear-gradient(135deg, #FF6B2B, #F5A623);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .sidebar-sub {
        font-size: 0.75rem;
        color: #8B949E;
        margin-top: 0.2rem;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown(
        "<div class='sidebar-title'>🥗 <span class='gradient-text'>Salad Tastes Better</span></div>",
        unsafe_allow_html=True
    )

    st.markdown(
        "<div class='sidebar-sub'>Personalised Indian Nutrition Planner</div>",
        unsafe_allow_html=True
    )

    st.markdown('<div class="sidebar-section">👤 Personal Info</div>', unsafe_allow_html=True)
    age = st.number_input("Age (years)", min_value=1, max_value=100, value=28, step=1)
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])

    st.markdown('<div class="sidebar-section">📏 Body Measurements</div>', unsafe_allow_html=True)
    weight = st.number_input("Weight (kg)", min_value=30.0, max_value=250.0, value=70.0, step=0.5)
    height = st.number_input("Height (cm)", min_value=100.0, max_value=250.0, value=170.0, step=0.5)

    bmi_auto = weight / ((height / 100) ** 2)
    st.markdown(f"""
    <div class='bmi-gauge'>
        <div style='display:flex;justify-content:space-between;align-items:center;'>
            <span style='font-size:0.78rem;color:#8B949E;font-weight:500;'>AUTO BMI</span>
            <span style='font-family:Syne,sans-serif;font-weight:800;font-size:1.4rem;
                         color:{bmi_color(bmi_auto)};'>{bmi_auto:.1f}</span>
        </div>
        <div class='bmi-track'></div>
        <div style='display:flex;justify-content:space-between;font-size:0.68rem;color:#8B949E;'>
            <span>Under</span><span>Normal</span><span>Over</span><span>Obese</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    activity = st.selectbox("Activity Level", [
        "sedentary", "lightly_active", "moderately_active", "very_active", "extra_active"
    ], index=2)

    st.markdown('<div class="sidebar-section">🏥 Health Conditions</div>', unsafe_allow_html=True)
    conditions = st.multiselect("Chronic Conditions",
        ["diabetes","hypertension","hypothyroidism","pcos","heart_disease","none"],
        default=["none"])

    st.markdown('<div class="sidebar-section">🍽️ Diet Preferences</div>', unsafe_allow_html=True)
    food_pref = st.selectbox("Food Preference", ["veg", "non-veg", "vegan"], index=1)
    budget = st.slider("Daily Budget (₹)", 50, 1000, 250, step=25)
    plan_duration = st.radio("Plan Duration", ["weekly", "monthly"], horizontal=True)
    allergies_input = st.text_input("Allergies (comma separated)", placeholder="e.g. peanuts, shellfish")


# ─── Main Layout ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
.emoji {
    -webkit-text-fill-color: initial;
    background: none;
}
</style>

<div class='hero-header'>
    <div class='hero-title'>
        <span class="emoji">🥗</span> Salad Tastes Better
    </div>
</div>
""", unsafe_allow_html=True)


# Tabs
tab1, tab2, tab3 = st.tabs(["🎯 Quick Classify", "🥗 Full Nutrition Plan", "📋 Combined Analysis"])

allergies_list = [a.strip() for a in allergies_input.split(",") if a.strip()] if allergies_input else []

# ─── TAB 1: Body Classification ──────────────────────────────────────────────
with tab1:
    col_form, col_result = st.columns([1, 1.3], gap="large")

    with col_form:
        bmi_manual = st.number_input("BMI (or auto-computed from sidebar →)", min_value=10.0, max_value=60.0,
                                     value=round(bmi_auto, 1), step=0.1, key="bmi_cls")

        classify_btn = st.button("🔍 Classify Body Type", use_container_width=True)

    with col_result:
        if classify_btn:
            payload = {
                "age": age, "gender": gender, "bmi": bmi_manual,
                "activity_level": activity,
                "weight_kg": weight, "height_cm": height
            }
            with st.spinner("Running classifier..."):
                result, err = call_api("classify", payload)

            if err:
                st.markdown(f"<div class='warn-box'>{err}</div>", unsafe_allow_html=True)
            elif result:
                bt = result["body_type"]
                risk = result["risk_level"]
                conf = result["model_confidence"]

                st.markdown(f"""
                <div class='result-card'>
                    <div class='body-type-badge {body_type_class(bt)}'>
                        {body_type_icon(bt)} {bt.upper()}
                    </div>
                    <div style='display:flex;gap:0.6rem;align-items:center;margin-bottom:1rem;'>
                        <span style='font-size:0.85rem;color:#8B949E;'>Risk:</span>
                        <span class='risk-badge {risk_class(risk)}'>{risk.upper()}</span>
                        <span style='font-size:0.85rem;color:#8B949E;margin-left:0.8rem;'>Confidence:</span>
                        <span style='font-weight:700;color:#F5A623;font-size:0.9rem;'>{conf*100:.0f}%</span>
                    </div>
                    <div class='conf-bar' style='width:{conf*100}%;'></div>
                    <div style='margin-top:0.5rem;font-size:0.78rem;color:#8B949E;'>Model confidence</div>
                </div>
                """, unsafe_allow_html=True)

                # BMI detail
                st.markdown(f"""
                <div class='result-card'>
                    <div class='section-heading' style='font-size:0.9rem;margin-top:0;'>📊 BMI Detail</div>
                    <div class='metric-row'>
                        <div class='metric-box'>
                            <span class='metric-val' style='color:{bmi_color(result["bmi"])};'>
                                {result["bmi"]:.1f}
                            </span>
                            <span class='metric-label'>BMI</span>
                        </div>
                        <div class='metric-box'>
                            <span class='metric-val' style='font-size:1.1rem;'>{result["bmi_category"].split("(")[0].strip()}</span>
                            <span class='metric-label'>Category</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Risk factors
                if result.get("risk_factors"):
                    st.markdown('<div class="section-heading" style="font-size:0.9rem;">⚠️ Risk Factors</div>', unsafe_allow_html=True)
                    for rf in result["risk_factors"]:
                        st.markdown(f"<div class='rec-item'><span class='rec-dot' style='color:#FF4757;'>▸</span>{rf}</div>",
                                    unsafe_allow_html=True)

                # Recommendations
                if result.get("recommendations"):
                    st.markdown('<div class="section-heading" style="font-size:0.9rem;">💡 Recommendations</div>', unsafe_allow_html=True)
                    for rec in result["recommendations"]:
                        st.markdown(f"<div class='rec-item'><span class='rec-dot'>✓</span>{rec}</div>",
                                    unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style='height:200px;display:flex;align-items:center;justify-content:center;
                        border:1px dashed #21262D;border-radius:16px;'>
                <div style='text-align:center;color:#8B949E;'>
                    <div style='font-size:2.5rem;margin-bottom:0.5rem;'>🏋️</div>
                    <div style='font-size:0.88rem;'>Fill in your details and click Classify</div>
                </div>
            </div>
            """, unsafe_allow_html=True)


# ─── TAB 2: Full Nutrition Plan ───────────────────────────────────────────────
with tab2:
    st.markdown('<div class="section-heading">Generate Personalised Nutrition Plan</div>', unsafe_allow_html=True)

    gen_btn = st.button("🍛 Generate Full Nutrition Plan", use_container_width=True)

    if gen_btn:
        payload = {
            "age": age, "gender": gender,
            "bmi": round(bmi_auto, 1),
            "activity_level": activity,
            "weight_kg": weight, "height_cm": height,
            "chronic_conditions": conditions,
            "budget_per_day_inr": float(budget),
            "food_preference": food_pref,
            "plan_duration": plan_duration,
            "allergies": allergies_list
        }

        with st.spinner("We are cooking up your personalised plan..."):
            result, err = call_api("nutrition-plan", payload)

        if err:
            st.markdown(f"<div class='warn-box'>{err}</div>", unsafe_allow_html=True)
        elif result:
            macros = result["daily_macros"]

            # ── Macros Overview ────────────────────────────────────────────
            st.markdown('<div class="section-heading">📊 Daily Macro Targets</div>', unsafe_allow_html=True)

            total_cal = macros["calories"]
            col_m1, col_m2, col_m3, col_m4, col_m5 = st.columns(5)
            with col_m1:
                st.markdown(f"""
                <div class='metric-box' style='border-color:#FF6B2B44;'>
                    <span class='metric-val'>{total_cal}</span>
                    <span class='metric-label'>kcal / day</span>
                </div>""", unsafe_allow_html=True)
            with col_m2:
                st.markdown(f"""
                <div class='metric-box' style='border-color:#F5A62344;'>
                    <span class='metric-val' style='color:#F5A623;font-size:1.5rem;'>{macros["protein_g"]}g</span>
                    <span class='metric-label'>Protein ({macros["protein_pct"]}%)</span>
                </div>""", unsafe_allow_html=True)
            with col_m3:
                st.markdown(f"""
                <div class='metric-box' style='border-color:#5B8DEF44;'>
                    <span class='metric-val' style='color:#5B8DEF;font-size:1.5rem;'>{macros["carbs_g"]}g</span>
                    <span class='metric-label'>Carbs ({macros["carbs_pct"]}%)</span>
                </div>""", unsafe_allow_html=True)
            with col_m4:
                st.markdown(f"""
                <div class='metric-box' style='border-color:#2ECC7144;'>
                    <span class='metric-val' style='color:#2ECC71;font-size:1.5rem;'>{macros["fat_g"]}g</span>
                    <span class='metric-label'>Fat ({macros["fat_pct"]}%)</span>
                </div>""", unsafe_allow_html=True)
            with col_m5:
                st.markdown(f"""
                <div class='metric-box'>
                    <span class='metric-val' style='color:#8B949E;font-size:1.5rem;'>{macros["water_ml"]}ml</span>
                    <span class='metric-label'>Hydration</span>
                </div>""", unsafe_allow_html=True)

            # Macro bars
            st.markdown("""<div class='macro-bar-container'>""", unsafe_allow_html=True)
            macros_display = [
                ("Protein", macros["protein_pct"], macros["protein_g"], "g", "#FF6B2B"),
                ("Carbs",   macros["carbs_pct"],   macros["carbs_g"],   "g", "#5B8DEF"),
                ("Fat",     macros["fat_pct"],      macros["fat_g"],     "g", "#2ECC71"),
                ("Fiber",   min(macros["fiber_g"]/50*100, 100), macros["fiber_g"], "g", "#F5A623"),
            ]
            for name, pct, val, unit, color in macros_display:
                st.markdown(f"""
                <div class='macro-row'>
                    <span class='macro-name'>{name}</span>
                    <div class='macro-bar-track'>
                        <div class='macro-bar-fill' style='width:{pct}%;background:{color};'></div>
                    </div>
                    <span class='macro-value'>{val}{unit}</span>
                </div>""", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

            # ── Diet Plan ─────────────────────────────────────────────────
            st.markdown(f'<div class="section-heading">📅 {plan_duration.capitalize()} Diet Plan ({len(result["diet_plan"])} days)</div>',
                        unsafe_allow_html=True)

            days = result["diet_plan"]
            # Show in expandable sections
            for day_data in days:
                with st.expander(f"🗓️ {day_data['day']} — {day_data['total_calories']} kcal · {day_data['macros_summary']}"):
                    for meal in day_data["meals"]:
                        foods_html = "".join([f"<span class='food-tag'>{f}</span>" for f in meal["foods"]])
                        notes_html = f"<div style='font-size:0.75rem;color:#5B8DEF;margin-top:0.3rem;'>💡 {meal['notes']}</div>" if meal.get("notes") else ""
                        st.markdown(f"""
                        <div class='meal-item'>
                            <div style='display:flex;justify-content:space-between;align-items:baseline;'>
                                <div>
                                    <span class='meal-time'>{meal["time"]} · </span>
                                    <span class='meal-name'>{meal["meal_name"]}</span>
                                </div>
                                <span class='meal-cal'>~{meal["calories"]} kcal</span>
                            </div>
                            <div style='margin-top:0.3rem;'>{foods_html}</div>
                            {notes_html}
                        </div>
                        """, unsafe_allow_html=True)

            # ── Avoid / Include ───────────────────────────────────────────
            col_av, col_inc = st.columns(2)
            with col_av:
                st.markdown('<div class="section-heading" style="font-size:0.9rem;">🚫 Foods to Avoid</div>', unsafe_allow_html=True)
                avoid_html = "".join([f"<span class='avoid-chip'>{f}</span>" for f in result.get("foods_to_avoid", [])])
                st.markdown(f"<div>{avoid_html}</div>", unsafe_allow_html=True)
            with col_inc:
                st.markdown('<div class="section-heading" style="font-size:0.9rem;">✅ Foods to Include</div>', unsafe_allow_html=True)
                include_html = "".join([f"<span class='include-chip'>{f}</span>" for f in result.get("foods_to_include", [])])
                st.markdown(f"<div>{include_html}</div>", unsafe_allow_html=True)

            # ── Hydration + Supplements + Notes ──────────────────────────
            st.markdown(f"""
            <div class='info-box' style='margin-top:1rem;'>
                💧 <strong>Hydration:</strong> {result.get("hydration_recommendation","")}
            </div>""", unsafe_allow_html=True)

            supps = result.get("supplement_suggestions", [])
            if supps:
                st.markdown('<div class="section-heading" style="font-size:0.9rem;">💊 Supplement Suggestions</div>', unsafe_allow_html=True)
                supp_html = "".join([f"<span class='supp-tag'>💊 {s}</span>" for s in supps])
                st.markdown(f"<div>{supp_html}</div>", unsafe_allow_html=True)

            if result.get("notes"):
                st.markdown(f"""
                <div class='success-box' style='margin-top:1rem;'>
                    📋 <strong>Notes:</strong> {result["notes"]}
                </div>""", unsafe_allow_html=True)


# ─── TAB 3: Combined Analysis ─────────────────────────────────────────────────
with tab3:
    st.markdown('<div class="section-heading">Combined Full Analysis</div>', unsafe_allow_html=True)

    full_btn = st.button("⚡ Run Full Analysis (One-Shot)", use_container_width=True)

    if full_btn:
        payload = {
            "age": age, "gender": gender,
            "bmi": round(bmi_auto, 1),
            "activity_level": activity,
            "weight_kg": weight, "height_cm": height,
            "chronic_conditions": conditions,
            "budget_per_day_inr": float(budget),
            "food_preference": food_pref,
            "plan_duration": plan_duration,
            "allergies": allergies_list
        }

        with st.spinner("🔬 Running analysis..."):
            result, err = call_api("full-analysis", payload)

        if err:
            st.markdown(f"<div class='warn-box'>{err}</div>", unsafe_allow_html=True)
        elif result:
            clf = result["classification"]
            nut = result["nutrition_plan"]
            macros = nut["daily_macros"]
            bt = clf["body_type"]
            risk = clf["risk_level"]

            col_l, col_r = st.columns([1, 1.5], gap="large")

            with col_l:
                st.markdown('<div class="section-heading" style="font-size:0.95rem;">🏋️ Classification</div>', unsafe_allow_html=True)
                st.markdown(f"""
                <div class='result-card'>
                    <div class='body-type-badge {body_type_class(bt)}'>
                        {body_type_icon(bt)} {bt.upper()}
                    </div>
                    <div style='margin-bottom:0.7rem;'>
                        <span class='risk-badge {risk_class(risk)}'>{risk.upper()} RISK</span>
                    </div>
                    <div style='font-size:0.82rem;color:#8B949E;margin-bottom:0.3rem;'>
                        Confidence: <strong style='color:#F5A623;'>{clf["model_confidence"]*100:.0f}%</strong>
                    </div>
                    <div class='conf-bar' style='width:{clf["model_confidence"]*100}%;'></div>
                    <hr style='margin:0.8rem 0;border-color:#21262D;'/>
                    <div style='font-size:0.8rem;color:#8B949E;margin-bottom:0.4rem;font-weight:600;'>BMI</div>
                    <div style='font-family:Syne,sans-serif;font-size:1.8rem;font-weight:800;color:{bmi_color(clf["bmi"])};'>
                        {clf["bmi"]:.1f}
                    </div>
                    <div style='font-size:0.78rem;color:#8B949E;'>{clf["bmi_category"]}</div>
                </div>
                """, unsafe_allow_html=True)

                if clf.get("recommendations"):
                    st.markdown('<div class="section-heading" style="font-size:0.85rem;">💡 Recs</div>', unsafe_allow_html=True)
                    for rec in clf["recommendations"][:4]:
                        st.markdown(f"<div class='rec-item'><span class='rec-dot'>✓</span><span style='font-size:0.82rem;'>{rec}</span></div>",
                                    unsafe_allow_html=True)

            with col_r:
                st.markdown('<div class="section-heading" style="font-size:0.95rem;">📊 Nutrition Overview</div>', unsafe_allow_html=True)
                st.markdown(f"""
                <div class='result-card'>
                    <div class='metric-row'>
                        <div class='metric-box'>
                            <span class='metric-val'>{macros["calories"]}</span>
                            <span class='metric-label'>kcal / day</span>
                        </div>
                        <div class='metric-box'>
                            <span class='metric-val' style='color:#F5A623;font-size:1.4rem;'>{macros["protein_g"]}g</span>
                            <span class='metric-label'>Protein</span>
                        </div>
                        <div class='metric-box'>
                            <span class='metric-val' style='color:#5B8DEF;font-size:1.4rem;'>{macros["carbs_g"]}g</span>
                            <span class='metric-label'>Carbs</span>
                        </div>
                        <div class='metric-box'>
                            <span class='metric-val' style='color:#2ECC71;font-size:1.4rem;'>{macros["fat_g"]}g</span>
                            <span class='metric-label'>Fat</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # First few days preview
                st.markdown('<div class="section-heading" style="font-size:0.85rem;">📅 Meal Preview</div>', unsafe_allow_html=True)
                for day_data in nut["diet_plan"][:3]:
                    with st.expander(f"📆 {day_data['day']} — {day_data['total_calories']} kcal"):
                        for meal in day_data["meals"]:
                            foods_html = " · ".join(meal["foods"][:3])
                            if len(meal["foods"]) > 3:
                                foods_html += f" +{len(meal['foods'])-3} more"
                            st.markdown(f"""
                            <div style='padding:0.4rem 0;border-bottom:1px solid #21262D;'>
                                <span style='font-size:0.75rem;color:#8B949E;'>{meal["time"]}</span>
                                <span style='font-weight:600;font-size:0.85rem;color:#E6EDF3;margin-left:0.4rem;'>{meal["meal_name"]}</span>
                                <span style='font-size:0.73rem;color:#F5A623;float:right;'>{meal["calories"]} kcal</span>
                                <div style='font-size:0.75rem;color:#8B949E;margin-top:0.15rem;'>{foods_html}</div>
                            </div>""", unsafe_allow_html=True)

    else:
        st.markdown("""
        <div style='height:250px;display:flex;align-items:center;justify-content:center;
                    border:1px dashed #21262D;border-radius:16px;'>
            <div style='text-align:center;color:#8B949E;'>
                <div style='font-size:3rem;margin-bottom:0.8rem;'>⚡</div>
                <div style='font-size:0.95rem;font-weight:600;'>One-Shot Full Analysis</div>
            </div>
        </div>
        """, unsafe_allow_html=True)


# ─── Footer ───────────────────────────────────────────────────────────────────
st.markdown("""
<div style='margin-top:3rem;padding-top:1.5rem;border-top:1px solid #21262D;
            text-align:center;color:#8B949E;font-size:0.78rem;'>
    <strong style='color:#FF6B2B;font-family:Syne,sans-serif;'>Salad Tastes Better</strong>
    · Built for Indian diets, ingredients, and preferences
</div>
""", unsafe_allow_html=True)
