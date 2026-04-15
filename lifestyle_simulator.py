import streamlit as st
import plotly.graph_objects as go
from fpdf import FPDF
import math
import json
import os
import hashlib

st.set_page_config(
    page_title="Lifestyle Budget Simulator",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=DM+Serif+Display:ital@0;1&display=swap');

/* ── Design tokens ── */
:root {
  --bg:      #090B12;
  --surface: #0E1120;
  --card:    #121726;
  --card-hi: #18203A;
  --border:  #1C2340;
  --bd-sub:  #111526;
  --sidebar: #0B0D18;
  --t1: #EEF0FF;
  --t2: rgba(238,240,255,0.50);
  --t3: rgba(238,240,255,0.24);
  --t-12: rgba(238,240,255,0.12);
  --t-25: rgba(238,240,255,0.25);
  --t-35: rgba(238,240,255,0.35);
  --t-60: rgba(238,240,255,0.60);
  --t-70: rgba(238,240,255,0.70);
  --t-75: rgba(238,240,255,0.75);
  --gold:   #C4A35A;
  --green:  #4BB88A;
  --red:    #DC6060;
  --purple: #8B6FD4;
  --blue:   #5090C4;
}

/* ── Reset & base ── */
html, body, [class*="css"] {
  font-family: 'Inter', sans-serif;
  font-size: 14px;
  color: var(--t1);
  -webkit-font-smoothing: antialiased;
  background: var(--bg);
}
h1, h2, h3, h4, h5 { font-family: 'Inter', sans-serif; color: var(--t1); }

/* Backgrounds */
.main, [data-testid="stAppViewContainer"],
[data-testid="stAppViewBlockContainer"],
.block-container { background: var(--bg) !important; }
[data-testid="stSidebar"] {
  background: var(--sidebar) !important;
  border-right: 1px solid var(--border) !important;
}

/* Sidebar text */
[data-testid="stSidebar"] label   { color: var(--t1) !important; font-size: 12.5px !important; font-weight: 400 !important; }
[data-testid="stSidebar"] p       { color: var(--t1) !important; }
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3      { color: var(--t1) !important; }
[data-testid="stSidebar"] h4      { color: var(--t3) !important; font-size: 10px !important; font-weight: 700 !important; letter-spacing: 0.14em !important; text-transform: uppercase !important; margin-bottom: 8px !important; }
[data-testid="stSidebar"] .stRadio label     { color: var(--t1) !important; }
[data-testid="stSidebar"] .stSelectbox label { color: var(--t1) !important; }
[data-testid="stSidebar"] .stCaption p       { color: var(--t2) !important; font-size: 11.5px !important; }
[data-testid="stSidebar"] [data-testid="stExpander"] summary p   { color: var(--t1) !important; font-weight: 500 !important; }
[data-testid="stSidebar"] [data-testid="stExpander"] summary svg { color: var(--t1) !important; }

/* Native Streamlit elements */
[data-testid="stMetricLabel"] p { color: var(--t3) !important; font-size: 10.5px !important; font-weight: 600 !important; letter-spacing: 0.1em; text-transform: uppercase; }
[data-testid="stMetricValue"]   { color: var(--t1) !important; font-weight: 700 !important; letter-spacing: -0.01em; }
[data-testid="stMetricDelta"] p { font-size: 11px !important; }
.stCaption p { color: var(--t2) !important; font-size: 11.5px !important; }
hr { border-color: var(--border) !important; margin: 32px 0 !important; }
[data-testid="stExpander"] { border-color: var(--border) !important; background: var(--surface) !important; border-radius: 10px !important; }
[data-testid="stExpander"] summary p { color: var(--t1) !important; font-weight: 500 !important; font-size: 13px !important; }

/* Sidebar buttons */
[data-testid="stSidebar"] button {
  background: var(--card) !important; color: var(--t1) !important;
  border: 1px solid var(--border) !important; border-radius: 8px !important; font-size: 13px !important;
}
[data-testid="stSidebar"] button:hover { background: var(--card-hi) !important; }

/* Tags */
.location-tag {
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(75,184,138,.07); color: #4BB88A;
    border: 1px solid rgba(75,184,138,.18); border-radius: 20px;
    padding: 4px 13px; font-size: 11.5px; font-weight: 500;
}
.tier-tag { display: inline-flex; align-items: center; border-radius: 20px; padding: 4px 13px; font-size: 11.5px; font-weight: 500; margin-left: 8px; }
.tier-frugal      { background: rgba(75,184,138,.07);  color: #4BB88A; border: 1px solid rgba(75,184,138,.2); }
.tier-comfortable { background: rgba(80,144,196,.07);  color: #5090C4; border: 1px solid rgba(80,144,196,.2); }
.tier-lavish      { background: rgba(196,163,90,.07);  color: #C4A35A; border: 1px solid rgba(196,163,90,.2); }

/* Section headings */
.section-head {
  font-size: 10.5px; font-weight: 700; color: var(--t3);
  letter-spacing: 0.14em; text-transform: uppercase;
  margin-bottom: 18px; margin-top: 4px;
}

/* Category rows */
.cat-row {
    display: flex; align-items: center; gap: 14px;
    padding: 13px 16px; border-radius: 10px;
    background: var(--card); margin-bottom: 5px;
    border: 1px solid var(--border);
    border-left: 3px solid transparent;
}
.cat-row:hover { background: var(--card-hi); }
.cat-row-name   { font-size: 13px; font-weight: 500; color: var(--t1); width: 150px; flex-shrink: 0; }
.cat-row-bar-wrap { flex: 1; height: 3px; background: var(--bd-sub); border-radius: 3px; overflow: hidden; }
.cat-row-bar-fill { height: 3px; border-radius: 3px; }
.cat-row-amount { font-size: 14px; font-weight: 600; color: var(--t1); width: 80px; text-align: right; flex-shrink: 0; }
.cat-row-meta   { font-size: 10.5px; color: var(--t3); width: 36px; text-align: right; flex-shrink: 0; }

/* Insight boxes */
.insight-box {
    background: rgba(75,184,138,.04); border: 1px solid rgba(75,184,138,.12);
    border-left: 3px solid #4BB88A; border-radius: 10px;
    padding: 14px 18px; margin-bottom: 10px;
    font-size: 13px; color: var(--t1); line-height: 1.72;
}

/* Goal / debt cards */
.goal-card { background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 24px 28px; margin-bottom: 16px; }
.goal-big   { font-family: 'DM Serif Display', serif; font-size: 44px; color: var(--purple); line-height: 1; letter-spacing: -0.02em; }
.goal-label { font-size: 10px; font-weight: 700; color: var(--t3); text-transform: uppercase; letter-spacing: 0.1em; margin-top: 6px; }
.debt-big   { font-family: 'DM Serif Display', serif; font-size: 44px; color: var(--red); line-height: 1; letter-spacing: -0.02em; }

/* Intro / survey */
.intro-eyebrow      { font-size: 10px; font-weight: 700; letter-spacing: 0.18em; text-transform: uppercase; color: var(--gold); margin-bottom: 22px; }
.intro-title        { font-family: 'DM Serif Display', serif; font-size: 54px; color: var(--t1); line-height: 1.06; letter-spacing: -0.03em; margin-bottom: 20px; }
.intro-sub          { font-size: 15.5px; color: var(--t2); font-weight: 300; line-height: 1.75; margin-bottom: 44px; }
.intro-feature      { display: flex; align-items: center; gap: 10px; font-size: 13px; color: var(--t2); margin-bottom: 11px; }
.intro-feature-dot  { width: 5px; height: 5px; border-radius: 50%; background: var(--gold); flex-shrink: 0; }
.intro-card      { background: var(--card); border: 1px solid var(--border); border-radius: 16px; padding: 36px 36px 40px; margin-top: 36px; }
.intro-card-title   { font-size: 18px; font-weight: 600; color: var(--t1); margin-bottom: 4px; }
.intro-card-sub     { font-size: 13px; color: var(--t2); font-weight: 300; margin-bottom: 26px; }
.intro-section-label { font-size: 10px; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; color: var(--t3); margin-bottom: 7px; margin-top: 20px; }

/* NW / EF / retirement cards */
.nw-card { background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 22px 26px; }
.nw-big-pos { font-family: 'DM Serif Display', serif; font-size: 38px; color: var(--green);  line-height: 1; letter-spacing: -0.02em; }
.nw-big-neg { font-family: 'DM Serif Display', serif; font-size: 38px; color: var(--red);    line-height: 1; letter-spacing: -0.02em; }
.nw-big-neu { font-family: 'DM Serif Display', serif; font-size: 38px; color: var(--t1);     line-height: 1; letter-spacing: -0.02em; }
.ef-bar-wrap { height: 8px; background: var(--bd-sub); border-radius: 6px; overflow: hidden; margin: 12px 0 6px; }
.sub-row     { display: flex; justify-content: space-between; align-items: center; padding: 6px 0; border-bottom: 1px solid var(--border); font-size: 12.5px; }
.wi-col-head { font-size: 10.5px; font-weight: 700; letter-spacing: .1em; text-transform: uppercase; color: var(--t3); margin-bottom: 14px; padding-bottom: 10px; border-bottom: 1px solid var(--border); }

/* Auth page */
.auth-logo    { font-family: 'DM Serif Display', serif; font-size: 30px; color: var(--t1); text-align: center; margin-bottom: 6px; letter-spacing: -0.02em; }
.auth-tagline { font-size: 13px; color: var(--t2); text-align: center; margin-bottom: 34px; font-weight: 300; }
.auth-card    { background: var(--card); border: 1px solid var(--border); border-radius: 16px; padding: 36px 36px 40px; }
.auth-label   { font-size: 10px; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; color: var(--t3); margin-bottom: 7px; margin-top: 18px; }
.auth-error   { background: rgba(220,96,96,.07); border: 1px solid rgba(220,96,96,.22); border-radius: 8px; padding: 10px 14px; font-size: 13px; color: var(--red); margin-top: 12px; }
.auth-success { background: rgba(75,184,138,.07); border: 1px solid rgba(75,184,138,.22); border-radius: 8px; padding: 10px 14px; font-size: 13px; color: var(--green); margin-top: 12px; }

/* ── Animated entries ── */
@keyframes fadeSlideUp {
  from { opacity: 0; transform: translateY(8px); }
  to   { opacity: 1; transform: translateY(0); }
}
@keyframes scalePop {
  from { opacity: 0; transform: scale(0.94); }
  to   { opacity: 1; transform: scale(1); }
}
@keyframes pieSpinIn {
  0%   { opacity: 0; transform: rotate(-270deg) scale(0.35); }
  60%  { opacity: 1; transform: rotate(18deg)   scale(1.04); }
  80%  { transform: rotate(-6deg)  scale(0.98); }
  100% { opacity: 1; transform: rotate(0deg)    scale(1); }
}
/* Targets only the pie layer SVG group inside Plotly */
.js-plotly-plot .pielayer {
  transform-origin: center;
  animation: pieSpinIn 0.85s cubic-bezier(0.34, 1.1, 0.64, 1) both;
}

.cat-row { animation: fadeSlideUp 0.32s ease-out both; }
.cat-row:nth-child(1) { animation-delay: 0.04s; }
.cat-row:nth-child(2) { animation-delay: 0.08s; }
.cat-row:nth-child(3) { animation-delay: 0.12s; }
.cat-row:nth-child(4) { animation-delay: 0.16s; }
.cat-row:nth-child(5) { animation-delay: 0.20s; }
.cat-row:nth-child(6) { animation-delay: 0.24s; }
.cat-row:nth-child(7) { animation-delay: 0.28s; }
.cat-row:nth-child(8) { animation-delay: 0.32s; }
.cat-row:nth-child(9) { animation-delay: 0.36s; }
[data-testid="stMetricValue"] { animation: fadeSlideUp 0.4s ease-out both; }
.nw-big-pos, .nw-big-neg, .nw-big-neu, .goal-big, .debt-big {
  animation: scalePop 0.45s cubic-bezier(0.34,1.56,0.64,1) both;
}
.nw-card { animation: fadeSlideUp 0.35s ease-out both; }
.insight-box { animation: fadeSlideUp 0.3s ease-out both; }

/* ── Section hover grow ── */
/* Cards & rows */
.cat-row, .nw-card, .goal-card, .health-card, .equiv-row, .insight-box, .sub-row {
  transition: transform 0.18s ease, box-shadow 0.18s ease, background 0.12s ease;
}
.nw-card:hover, .goal-card:hover, .health-card:hover {
  transform: scale(1.012);
  box-shadow: 0 8px 28px rgba(139,111,212,.13), 0 0 0 1px var(--border);
}
.insight-box:hover { transform: scale(1.008); }
.equiv-row:hover   { transform: scale(1.008); background: var(--card-hi); }

/* Plotly chart containers — lift & grow slightly on hover */
[data-testid="stPlotlyChart"] {
  transition: transform 0.22s ease, box-shadow 0.22s ease;
  border-radius: 12px;
}
[data-testid="stPlotlyChart"]:hover {
  transform: scale(1.018);
  box-shadow: 0 10px 34px rgba(80,144,196,.12);
}

/* Section-level blocks — very subtle scale so the whole section breathes */
[data-testid="stVerticalBlockBorderWrapper"] {
  transition: transform 0.2s ease;
}
[data-testid="stVerticalBlockBorderWrapper"]:hover {
  transform: scale(1.004);
}

/* ── Health score card ── */
.health-card {
  background: var(--card); border: 1px solid var(--border);
  border-radius: 14px; padding: 22px 26px; margin-bottom: 0;
}
.health-score-ring {
  font-family: 'DM Serif Display', serif;
  font-size: 52px; line-height: 1; letter-spacing: -0.03em;
}
.health-sub-bar {
  height: 5px; background: var(--bd-sub); border-radius: 4px; overflow: hidden; margin: 6px 0 3px;
}
.health-sub-label {
  font-size: 9.5px; font-weight: 700; letter-spacing: .10em;
  text-transform: uppercase; color: var(--t3); margin-bottom: 4px;
}

/* ── Archetype card ── */
.archetype-pill {
  display: inline-flex; align-items: center; gap: 7px;
  border-radius: 24px; padding: 5px 14px 5px 10px;
  font-size: 12px; font-weight: 600;
  border: 1px solid; margin-left: 10px;
  vertical-align: middle;
  animation: fadeSlideUp 0.5s ease-out both;
  animation-delay: 0.15s;
}

/* ── Salary equivalency ── */
.equiv-row {
  display: flex; align-items: center; justify-content: space-between;
  padding: 10px 14px; border-radius: 9px;
  background: var(--card); border: 1px solid var(--border);
  margin-bottom: 5px; font-size: 12.5px;
  animation: fadeSlideUp 0.3s ease-out both;
}
.equiv-city { color: var(--t1); font-weight: 500; flex: 1; }
.equiv-col-badge {
  font-size: 10px; font-weight: 600; letter-spacing: .05em;
  padding: 2px 7px; border-radius: 10px; margin: 0 12px;
  flex-shrink: 0;
}
.equiv-salary { color: var(--t1); font-weight: 700; font-size: 13px; text-align: right; flex-shrink: 0; }
.equiv-delta { font-size: 11px; margin-left: 6px; flex-shrink: 0; }
</style>
""", unsafe_allow_html=True)

# ── Cost of living index data (national average = 100) ──────────────────────
_CITIES_RAW = {
    # AK
    "Anchorage, AK":               {"index": 135,  "housing_mult": 1.80, "food_mult": 1.28, "transport_mult": 1.15, "health_mult": 1.18},

    # AL
    "Birmingham, AL":              {"index": 89,  "housing_mult": 0.78, "food_mult": 0.95, "transport_mult": 0.96, "health_mult": 0.95},
    "Huntsville, AL":              {"index": 90,  "housing_mult": 0.80, "food_mult": 0.96, "transport_mult": 0.96, "health_mult": 0.95},
    "Montgomery, AL":              {"index": 84,  "housing_mult": 0.68, "food_mult": 0.93, "transport_mult": 0.94, "health_mult": 0.93},

    # AR
    "El Dorado, AR":               {"index": 79,  "housing_mult": 0.60, "food_mult": 0.91, "transport_mult": 0.92, "health_mult": 0.91},
    "Fayetteville, AR":            {"index": 83,  "housing_mult": 0.66, "food_mult": 0.92, "transport_mult": 0.93, "health_mult": 0.92},
    "Little Rock, AR":             {"index": 82,  "housing_mult": 0.65, "food_mult": 0.92, "transport_mult": 0.93, "health_mult": 0.92},

    # AZ
    "Phoenix, AZ":                 {"index": 116,  "housing_mult": 1.45, "food_mult": 1.02, "transport_mult": 1.03, "health_mult": 1.01},
    "Scottsdale, AZ":              {"index": 128,  "housing_mult": 1.70, "food_mult": 1.06, "transport_mult": 1.05, "health_mult": 1.04},
    "Tucson, AZ":                  {"index": 107,  "housing_mult": 1.20, "food_mult": 1.01, "transport_mult": 1.02, "health_mult": 1.00},

    # CA
    "Fresno, CA":                  {"index": 115,  "housing_mult": 1.40, "food_mult": 1.05, "transport_mult": 1.04, "health_mult": 1.03},
    "Los Angeles, CA":             {"index": 163,  "housing_mult": 2.60, "food_mult": 1.14, "transport_mult": 1.18, "health_mult": 1.10},
    "Oakland, CA":                 {"index": 175,  "housing_mult": 2.85, "food_mult": 1.20, "transport_mult": 1.16, "health_mult": 1.16},
    "Riverside, CA":               {"index": 122,  "housing_mult": 1.55, "food_mult": 1.08, "transport_mult": 1.06, "health_mult": 1.04},
    "Sacramento, CA":              {"index": 142,  "housing_mult": 2.05, "food_mult": 1.12, "transport_mult": 1.08, "health_mult": 1.08},
    "San Diego, CA":               {"index": 164,  "housing_mult": 2.65, "food_mult": 1.16, "transport_mult": 1.14, "health_mult": 1.12},
    "San Francisco, CA":           {"index": 182,  "housing_mult": 3.10, "food_mult": 1.20, "transport_mult": 1.15, "health_mult": 1.18},
    "San Jose, CA":                {"index": 193,  "housing_mult": 3.40, "food_mult": 1.22, "transport_mult": 1.18, "health_mult": 1.18},

    # CO
    "Boulder, CO":                 {"index": 148,  "housing_mult": 2.18, "food_mult": 1.12, "transport_mult": 1.08, "health_mult": 1.09},
    "Colorado Springs, CO":        {"index": 115,  "housing_mult": 1.40, "food_mult": 1.05, "transport_mult": 1.03, "health_mult": 1.04},
    "Denver, CO":                  {"index": 135,  "housing_mult": 1.80, "food_mult": 1.08, "transport_mult": 1.05, "health_mult": 1.06},
    "Fort Collins, CO":            {"index": 122,  "housing_mult": 1.55, "food_mult": 1.07, "transport_mult": 1.04, "health_mult": 1.05},

    # CT
    "Hartford, CT":                {"index": 132,  "housing_mult": 1.75, "food_mult": 1.10, "transport_mult": 1.08, "health_mult": 1.09},
    "New Haven, CT":               {"index": 138,  "housing_mult": 1.85, "food_mult": 1.11, "transport_mult": 1.09, "health_mult": 1.10},

    # DC
    "Washington, DC":              {"index": 155,  "housing_mult": 2.40, "food_mult": 1.13, "transport_mult": 1.10, "health_mult": 1.11},

    # DE
    "Wilmington, DE":              {"index": 115,  "housing_mult": 1.40, "food_mult": 1.05, "transport_mult": 1.04, "health_mult": 1.04},

    # FL
    "Jacksonville, FL":            {"index": 100,  "housing_mult": 1.00, "food_mult": 1.00, "transport_mult": 1.01, "health_mult": 0.99},
    "Miami, FL":                   {"index": 148,  "housing_mult": 2.20, "food_mult": 1.10, "transport_mult": 1.08, "health_mult": 1.08},
    "Orlando, FL":                 {"index": 110,  "housing_mult": 1.30, "food_mult": 1.02, "transport_mult": 1.02, "health_mult": 1.01},
    "St. Petersburg, FL":          {"index": 110,  "housing_mult": 1.30, "food_mult": 1.03, "transport_mult": 1.02, "health_mult": 1.01},
    "Tampa, FL":                   {"index": 113,  "housing_mult": 1.38, "food_mult": 1.03, "transport_mult": 1.03, "health_mult": 1.02},

    # GA
    "Atlanta, GA":                 {"index": 118,  "housing_mult": 1.48, "food_mult": 1.03, "transport_mult": 1.03, "health_mult": 1.02},
    "Augusta, GA":                 {"index": 88,  "housing_mult": 0.76, "food_mult": 0.95, "transport_mult": 0.96, "health_mult": 0.95},
    "Columbus, GA":                {"index": 86,  "housing_mult": 0.72, "food_mult": 0.94, "transport_mult": 0.95, "health_mult": 0.94},
    "Savannah, GA":                {"index": 98,  "housing_mult": 0.95, "food_mult": 0.99, "transport_mult": 1.00, "health_mult": 0.98},

    # HI
    "Honolulu, HI":                {"index": 191,  "housing_mult": 3.35, "food_mult": 1.35, "transport_mult": 1.22, "health_mult": 1.20},

    # IA
    "Cedar Rapids, IA":            {"index": 88,  "housing_mult": 0.76, "food_mult": 0.95, "transport_mult": 0.96, "health_mult": 0.95},
    "Des Moines, IA":              {"index": 92,  "housing_mult": 0.84, "food_mult": 0.96, "transport_mult": 0.97, "health_mult": 0.96},

    # ID
    "Boise, ID":                   {"index": 118,  "housing_mult": 1.48, "food_mult": 1.05, "transport_mult": 1.03, "health_mult": 1.03},

    # IL
    "Chicago, IL":                 {"index": 138,  "housing_mult": 1.85, "food_mult": 1.09, "transport_mult": 1.08, "health_mult": 1.06},
    "Rockford, IL":                {"index": 88,  "housing_mult": 0.76, "food_mult": 0.95, "transport_mult": 0.97, "health_mult": 0.96},
    "Springfield, IL":             {"index": 92,  "housing_mult": 0.84, "food_mult": 0.97, "transport_mult": 0.97, "health_mult": 0.96},

    # IN
    "Evansville, IN":              {"index": 86,  "housing_mult": 0.72, "food_mult": 0.94, "transport_mult": 0.95, "health_mult": 0.94},
    "Fort Wayne, IN":              {"index": 88,  "housing_mult": 0.75, "food_mult": 0.95, "transport_mult": 0.97, "health_mult": 0.95},
    "Indianapolis, IN":            {"index": 97,  "housing_mult": 0.90, "food_mult": 0.97, "transport_mult": 0.98, "health_mult": 0.97},

    # KS
    "Wichita, KS":                 {"index": 84,  "housing_mult": 0.68, "food_mult": 0.93, "transport_mult": 0.93, "health_mult": 0.93},

    # KY
    "Lexington, KY":               {"index": 90,  "housing_mult": 0.80, "food_mult": 0.96, "transport_mult": 0.97, "health_mult": 0.96},
    "Louisville, KY":              {"index": 91,  "housing_mult": 0.80, "food_mult": 0.95, "transport_mult": 0.96, "health_mult": 0.95},

    # LA
    "Baton Rouge, LA":             {"index": 90,  "housing_mult": 0.80, "food_mult": 0.96, "transport_mult": 0.97, "health_mult": 0.96},
    "New Orleans, LA":             {"index": 100,  "housing_mult": 1.00, "food_mult": 1.01, "transport_mult": 1.02, "health_mult": 1.00},
    "Shreveport, LA":              {"index": 86,  "housing_mult": 0.72, "food_mult": 0.94, "transport_mult": 0.95, "health_mult": 0.94},

    # MA
    "Boston, MA":                  {"index": 162,  "housing_mult": 2.55, "food_mult": 1.16, "transport_mult": 1.12, "health_mult": 1.14},
    "Springfield, MA":             {"index": 118,  "housing_mult": 1.48, "food_mult": 1.07, "transport_mult": 1.05, "health_mult": 1.06},
    "Worcester, MA":               {"index": 145,  "housing_mult": 2.10, "food_mult": 1.14, "transport_mult": 1.10, "health_mult": 1.12},

    # MD
    "Baltimore, MD":               {"index": 120,  "housing_mult": 1.52, "food_mult": 1.07, "transport_mult": 1.08, "health_mult": 1.07},

    # ME
    "Portland, ME":                {"index": 122,  "housing_mult": 1.55, "food_mult": 1.09, "transport_mult": 1.04, "health_mult": 1.07},

    # MI
    "Ann Arbor, MI":               {"index": 112,  "housing_mult": 1.35, "food_mult": 1.03, "transport_mult": 1.01, "health_mult": 1.02},
    "Detroit, MI":                 {"index": 95,  "housing_mult": 0.88, "food_mult": 0.98, "transport_mult": 1.00, "health_mult": 0.97},
    "Grand Rapids, MI":            {"index": 95,  "housing_mult": 0.88, "food_mult": 0.97, "transport_mult": 0.98, "health_mult": 0.97},
    "Lansing, MI":                 {"index": 90,  "housing_mult": 0.80, "food_mult": 0.96, "transport_mult": 0.97, "health_mult": 0.96},

    # MN
    "Minneapolis, MN":             {"index": 113,  "housing_mult": 1.38, "food_mult": 1.04, "transport_mult": 1.01, "health_mult": 1.03},

    # MO
    "Kansas City, MO":             {"index": 94,  "housing_mult": 0.85, "food_mult": 0.96, "transport_mult": 0.97, "health_mult": 0.96},
    "Springfield, MO":             {"index": 88,  "housing_mult": 0.76, "food_mult": 0.95, "transport_mult": 0.96, "health_mult": 0.95},
    "St. Louis, MO":               {"index": 93,  "housing_mult": 0.83, "food_mult": 0.96, "transport_mult": 0.97, "health_mult": 0.96},

    # MS
    "Jackson, MS":                 {"index": 80,  "housing_mult": 0.62, "food_mult": 0.91, "transport_mult": 0.92, "health_mult": 0.91},

    # MT
    "Billings, MT":                {"index": 94,  "housing_mult": 0.87, "food_mult": 0.97, "transport_mult": 0.97, "health_mult": 0.96},
    "Bozeman, MT":                 {"index": 115,  "housing_mult": 1.40, "food_mult": 1.05, "transport_mult": 1.02, "health_mult": 1.03},
    "Missoula, MT":                {"index": 105,  "housing_mult": 1.14, "food_mult": 1.02, "transport_mult": 1.01, "health_mult": 1.01},

    # NC
    "Asheville, NC":               {"index": 108,  "housing_mult": 1.22, "food_mult": 1.02, "transport_mult": 1.01, "health_mult": 1.01},
    "Charlotte, NC":               {"index": 108,  "housing_mult": 1.25, "food_mult": 1.01, "transport_mult": 1.01, "health_mult": 1.00},
    "Durham, NC":                  {"index": 118,  "housing_mult": 1.48, "food_mult": 1.04, "transport_mult": 1.02, "health_mult": 1.03},
    "Greensboro, NC":              {"index": 93,  "housing_mult": 0.86, "food_mult": 0.97, "transport_mult": 0.98, "health_mult": 0.97},
    "Raleigh, NC":                 {"index": 120,  "housing_mult": 1.52, "food_mult": 1.05, "transport_mult": 1.03, "health_mult": 1.03},

    # ND
    "Bismarck, ND":                {"index": 90,  "housing_mult": 0.80, "food_mult": 0.96, "transport_mult": 0.96, "health_mult": 0.95},
    "Fargo, ND":                   {"index": 93,  "housing_mult": 0.85, "food_mult": 0.97, "transport_mult": 0.97, "health_mult": 0.96},

    # NE
    "Lincoln, NE":                 {"index": 88,  "housing_mult": 0.75, "food_mult": 0.95, "transport_mult": 0.96, "health_mult": 0.95},
    "Omaha, NE":                   {"index": 90,  "housing_mult": 0.80, "food_mult": 0.96, "transport_mult": 0.97, "health_mult": 0.96},

    # NH
    "Manchester, NH":              {"index": 122,  "housing_mult": 1.56, "food_mult": 1.08, "transport_mult": 1.06, "health_mult": 1.07},

    # NJ
    "Jersey City, NJ":             {"index": 165,  "housing_mult": 2.68, "food_mult": 1.18, "transport_mult": 1.16, "health_mult": 1.13},
    "Newark, NJ":                  {"index": 158,  "housing_mult": 2.45, "food_mult": 1.16, "transport_mult": 1.15, "health_mult": 1.12},

    # NM
    "Albuquerque, NM":             {"index": 107,  "housing_mult": 1.20, "food_mult": 1.01, "transport_mult": 1.01, "health_mult": 1.00},

    # NV
    "Las Vegas, NV":               {"index": 112,  "housing_mult": 1.35, "food_mult": 1.04, "transport_mult": 1.05, "health_mult": 1.03},
    "Reno, NV":                    {"index": 118,  "housing_mult": 1.48, "food_mult": 1.05, "transport_mult": 1.04, "health_mult": 1.04},

    # NY
    "Albany, NY":                  {"index": 108,  "housing_mult": 1.22, "food_mult": 1.03, "transport_mult": 1.01, "health_mult": 1.02},
    "Buffalo, NY":                 {"index": 98,  "housing_mult": 0.96, "food_mult": 0.99, "transport_mult": 0.99, "health_mult": 0.98},
    "New York City, NY":           {"index": 187,  "housing_mult": 3.20, "food_mult": 1.22, "transport_mult": 1.18, "health_mult": 1.15},
    "Rochester, NY":               {"index": 96,  "housing_mult": 0.92, "food_mult": 0.98, "transport_mult": 0.99, "health_mult": 0.97},

    # OH
    "Akron, OH":                   {"index": 88,  "housing_mult": 0.75, "food_mult": 0.95, "transport_mult": 0.97, "health_mult": 0.96},
    "Cincinnati, OH":              {"index": 98,  "housing_mult": 0.95, "food_mult": 0.98, "transport_mult": 0.99, "health_mult": 0.98},
    "Cleveland, OH":               {"index": 93,  "housing_mult": 0.85, "food_mult": 0.97, "transport_mult": 0.98, "health_mult": 0.97},
    "Columbus, OH":                {"index": 103,  "housing_mult": 1.10, "food_mult": 1.00, "transport_mult": 1.00, "health_mult": 0.99},
    "Toledo, OH":                  {"index": 88,  "housing_mult": 0.74, "food_mult": 0.95, "transport_mult": 0.97, "health_mult": 0.96},

    # OK
    "Oklahoma City, OK":           {"index": 87,  "housing_mult": 0.73, "food_mult": 0.94, "transport_mult": 0.95, "health_mult": 0.94},
    "Tulsa, OK":                   {"index": 85,  "housing_mult": 0.70, "food_mult": 0.93, "transport_mult": 0.94, "health_mult": 0.93},

    # OR
    "Eugene, OR":                  {"index": 115,  "housing_mult": 1.40, "food_mult": 1.07, "transport_mult": 1.04, "health_mult": 1.05},
    "Portland, OR":                {"index": 127,  "housing_mult": 1.68, "food_mult": 1.07, "transport_mult": 1.05, "health_mult": 1.05},
    "Salem, OR":                   {"index": 108,  "housing_mult": 1.22, "food_mult": 1.05, "transport_mult": 1.03, "health_mult": 1.03},

    # PA
    "Allentown, PA":               {"index": 105,  "housing_mult": 1.14, "food_mult": 1.02, "transport_mult": 1.01, "health_mult": 1.01},
    "Philadelphia, PA":            {"index": 145,  "housing_mult": 2.10, "food_mult": 1.12, "transport_mult": 1.12, "health_mult": 1.10},
    "Pittsburgh, PA":              {"index": 96,  "housing_mult": 0.88, "food_mult": 0.97, "transport_mult": 0.98, "health_mult": 0.97},

    # RI
    "Providence, RI":              {"index": 128,  "housing_mult": 1.68, "food_mult": 1.09, "transport_mult": 1.07, "health_mult": 1.08},

    # SC
    "Charleston, SC":              {"index": 110,  "housing_mult": 1.30, "food_mult": 1.03, "transport_mult": 1.02, "health_mult": 1.01},
    "Columbia, SC":                {"index": 91,  "housing_mult": 0.82, "food_mult": 0.96, "transport_mult": 0.97, "health_mult": 0.96},
    "Greenville, SC":              {"index": 92,  "housing_mult": 0.84, "food_mult": 0.97, "transport_mult": 0.97, "health_mult": 0.96},

    # SD
    "Rapid City, SD":              {"index": 88,  "housing_mult": 0.76, "food_mult": 0.95, "transport_mult": 0.96, "health_mult": 0.95},
    "Sioux Falls, SD":             {"index": 88,  "housing_mult": 0.75, "food_mult": 0.95, "transport_mult": 0.96, "health_mult": 0.95},

    # TN
    "Chattanooga, TN":             {"index": 88,  "housing_mult": 0.76, "food_mult": 0.95, "transport_mult": 0.96, "health_mult": 0.95},
    "Knoxville, TN":               {"index": 90,  "housing_mult": 0.80, "food_mult": 0.96, "transport_mult": 0.97, "health_mult": 0.96},
    "Memphis, TN":                 {"index": 88,  "housing_mult": 0.75, "food_mult": 0.94, "transport_mult": 0.95, "health_mult": 0.94},
    "Nashville, TN":               {"index": 120,  "housing_mult": 1.55, "food_mult": 1.04, "transport_mult": 1.02, "health_mult": 1.02},

    # TX
    "Austin, TX":                  {"index": 128,  "housing_mult": 1.70, "food_mult": 1.06, "transport_mult": 1.04, "health_mult": 1.04},
    "Dallas, TX":                  {"index": 114,  "housing_mult": 1.42, "food_mult": 1.02, "transport_mult": 1.04, "health_mult": 1.01},
    "El Paso, TX":                 {"index": 91,  "housing_mult": 0.82, "food_mult": 0.95, "transport_mult": 0.96, "health_mult": 0.95},
    "Fort Worth, TX":              {"index": 108,  "housing_mult": 1.22, "food_mult": 1.01, "transport_mult": 1.02, "health_mult": 1.00},
    "Houston, TX":                 {"index": 105,  "housing_mult": 1.14, "food_mult": 1.02, "transport_mult": 1.04, "health_mult": 1.01},
    "Lubbock, TX":                 {"index": 86,  "housing_mult": 0.72, "food_mult": 0.94, "transport_mult": 0.95, "health_mult": 0.93},
    "San Antonio, TX":             {"index": 100,  "housing_mult": 1.00, "food_mult": 0.99, "transport_mult": 1.01, "health_mult": 0.99},
    "Waco, TX":                    {"index": 91,  "housing_mult": 0.82, "food_mult": 0.95, "transport_mult": 0.96, "health_mult": 0.95},

    # UT
    "Provo, UT":                   {"index": 112,  "housing_mult": 1.36, "food_mult": 1.04, "transport_mult": 1.02, "health_mult": 1.02},
    "Salt Lake City, UT":          {"index": 124,  "housing_mult": 1.60, "food_mult": 1.06, "transport_mult": 1.04, "health_mult": 1.04},

    # VA
    "Richmond, VA":                {"index": 113,  "housing_mult": 1.36, "food_mult": 1.03, "transport_mult": 1.02, "health_mult": 1.02},
    "Virginia Beach, VA":          {"index": 105,  "housing_mult": 1.14, "food_mult": 1.01, "transport_mult": 1.01, "health_mult": 1.00},

    # VT
    "Burlington, VT":              {"index": 128,  "housing_mult": 1.70, "food_mult": 1.10, "transport_mult": 1.05, "health_mult": 1.08},

    # WA
    "Seattle, WA":                 {"index": 158,  "housing_mult": 2.45, "food_mult": 1.14, "transport_mult": 1.10, "health_mult": 1.12},
    "Spokane, WA":                 {"index": 108,  "housing_mult": 1.22, "food_mult": 1.03, "transport_mult": 1.02, "health_mult": 1.02},
    "Tacoma, WA":                  {"index": 122,  "housing_mult": 1.56, "food_mult": 1.09, "transport_mult": 1.07, "health_mult": 1.08},

    # WI
    "Madison, WI":                 {"index": 108,  "housing_mult": 1.22, "food_mult": 1.02, "transport_mult": 1.00, "health_mult": 1.01},
    "Milwaukee, WI":               {"index": 102,  "housing_mult": 1.06, "food_mult": 1.00, "transport_mult": 1.00, "health_mult": 0.99},

    # WV
    "Charleston, WV":              {"index": 85,  "housing_mult": 0.70, "food_mult": 0.94, "transport_mult": 0.95, "health_mult": 0.94},

    # WY
    "Casper, WY":                  {"index": 90,  "housing_mult": 0.80, "food_mult": 0.96, "transport_mult": 0.97, "health_mult": 0.96},
    "Cheyenne, WY":                {"index": 91,  "housing_mult": 0.82, "food_mult": 0.96, "transport_mult": 0.97, "health_mult": 0.96},
}
COL_DATA = {"National Average": {"index": 100, "housing_mult": 1.00, "food_mult": 1.00, "transport_mult": 1.00, "health_mult": 1.00}}
COL_DATA.update(dict(sorted(_CITIES_RAW.items())))

# ── State income tax data ─────────────────────────────────────────────────────
STATE_TAX = {
    "AL": {"type": "brackets", "std_ded": 2500,  "brackets": [(500, 0.02), (3000, 0.04), (float("inf"), 0.05)]},
    "AK": {"type": "none"},
    "AZ": {"type": "flat",     "rate": 0.025},
    "AR": {"type": "brackets", "std_ded": 2200,  "brackets": [(4300, 0.02), (8500, 0.04), (float("inf"), 0.049)]},
    "CA": {"type": "brackets", "std_ded": 5202,  "brackets": [(10099, 0.01), (23942, 0.02), (37788, 0.04), (52455, 0.06), (66295, 0.08), (338639, 0.093), (406364, 0.103), (677275, 0.113), (float("inf"), 0.123)]},
    "CO": {"type": "flat",     "rate": 0.044},
    "CT": {"type": "brackets", "std_ded": 0,     "brackets": [(10000, 0.03), (50000, 0.05), (100000, 0.055), (200000, 0.06), (250000, 0.065), (500000, 0.069), (float("inf"), 0.0699)]},
    "DC": {"type": "brackets", "std_ded": 12950, "brackets": [(10000, 0.04), (40000, 0.06), (60000, 0.065), (350000, 0.085), (1000000, 0.0925), (float("inf"), 0.1075)]},
    "DE": {"type": "brackets", "std_ded": 3250,  "brackets": [(2000, 0.0), (5000, 0.022), (10000, 0.039), (20000, 0.048), (25000, 0.052), (60000, 0.055), (float("inf"), 0.066)]},
    "FL": {"type": "none"},
    "GA": {"type": "flat",     "rate": 0.0549},
    "HI": {"type": "brackets", "std_ded": 2200,  "brackets": [(2400, 0.014), (4800, 0.032), (9600, 0.055), (14400, 0.064), (19200, 0.068), (24000, 0.072), (36000, 0.076), (48000, 0.079), (150000, 0.0825), (175000, 0.09), (200000, 0.10), (float("inf"), 0.11)]},
    "ID": {"type": "flat",     "rate": 0.058},
    "IL": {"type": "flat",     "rate": 0.0495},
    "IN": {"type": "flat",     "rate": 0.0305},
    "IA": {"type": "flat",     "rate": 0.057},
    "KS": {"type": "brackets", "std_ded": 3500,  "brackets": [(15000, 0.031), (30000, 0.0525), (float("inf"), 0.057)]},
    "KY": {"type": "flat",     "rate": 0.045},
    "LA": {"type": "brackets", "std_ded": 4500,  "brackets": [(12500, 0.0185), (50000, 0.035), (float("inf"), 0.0425)]},
    "ME": {"type": "brackets", "std_ded": 13850, "brackets": [(24500, 0.058), (58050, 0.0675), (float("inf"), 0.0715)]},
    "MD": {"type": "brackets", "std_ded": 2400,  "brackets": [(1000, 0.02), (2000, 0.03), (3000, 0.04), (100000, 0.0475), (125000, 0.05), (150000, 0.0525), (250000, 0.055), (float("inf"), 0.0575)]},
    "MA": {"type": "flat",     "rate": 0.05},
    "MI": {"type": "flat",     "rate": 0.0425},
    "MN": {"type": "brackets", "std_ded": 14575, "brackets": [(31690, 0.0535), (104090, 0.068), (171220, 0.0785), (float("inf"), 0.0985)]},
    "MS": {"type": "flat",     "rate": 0.047},
    "MO": {"type": "brackets", "std_ded": 14600, "brackets": [(1121, 0.015), (2242, 0.02), (3363, 0.025), (4484, 0.03), (5605, 0.035), (6726, 0.04), (7847, 0.045), (8968, 0.05), (float("inf"), 0.048)]},
    "MT": {"type": "flat",     "rate": 0.059},
    "NE": {"type": "brackets", "std_ded": 7900,  "brackets": [(3700, 0.0246), (22170, 0.0351), (35730, 0.0501), (float("inf"), 0.0664)]},
    "NV": {"type": "none"},
    "NH": {"type": "none"},
    "NJ": {"type": "brackets", "std_ded": 0,     "brackets": [(20000, 0.014), (35000, 0.0175), (40000, 0.035), (75000, 0.05526), (500000, 0.0637), (1000000, 0.0897), (float("inf"), 0.1075)]},
    "NM": {"type": "brackets", "std_ded": 14600, "brackets": [(5500, 0.017), (11000, 0.032), (16000, 0.047), (210000, 0.049), (float("inf"), 0.059)]},
    "NY": {"type": "brackets", "std_ded": 8000,  "brackets": [(17150, 0.04), (23600, 0.045), (27900, 0.0525), (161550, 0.0585), (323200, 0.0625), (2155350, 0.0685), (5000000, 0.0965), (25000000, 0.103), (float("inf"), 0.109)]},
    "NC": {"type": "flat",     "rate": 0.045},
    "ND": {"type": "flat",     "rate": 0.0195},
    "OH": {"type": "brackets", "std_ded": 0,     "brackets": [(26050, 0.0), (100000, 0.02765), (float("inf"), 0.0350)]},
    "OK": {"type": "brackets", "std_ded": 6350,  "brackets": [(1000, 0.0025), (2500, 0.0075), (3750, 0.0175), (4900, 0.0275), (7200, 0.0375), (float("inf"), 0.0475)]},
    "OR": {"type": "brackets", "std_ded": 2420,  "brackets": [(10200, 0.0475), (25500, 0.0675), (125000, 0.0875), (float("inf"), 0.099)]},
    "PA": {"type": "flat",     "rate": 0.0307},
    "RI": {"type": "brackets", "std_ded": 10550, "brackets": [(73450, 0.0375), (166950, 0.0475), (float("inf"), 0.0599)]},
    "SC": {"type": "flat",     "rate": 0.064},
    "SD": {"type": "none"},
    "TN": {"type": "none"},
    "TX": {"type": "none"},
    "UT": {"type": "flat",     "rate": 0.0465},
    "VT": {"type": "brackets", "std_ded": 7000,  "brackets": [(45400, 0.0335), (110050, 0.066), (229550, 0.076), (float("inf"), 0.0875)]},
    "VA": {"type": "brackets", "std_ded": 8000,  "brackets": [(3000, 0.02), (5000, 0.03), (17000, 0.05), (float("inf"), 0.0575)]},
    "WA": {"type": "none"},
    "WV": {"type": "brackets", "std_ded": 0,     "brackets": [(10000, 0.0236), (25000, 0.0315), (40000, 0.0354), (60000, 0.0472), (float("inf"), 0.0512)]},
    "WI": {"type": "brackets", "std_ded": 12760, "brackets": [(14320, 0.0354), (28640, 0.0465), (315310, 0.053), (float("inf"), 0.0765)]},
    "WY": {"type": "none"},
}

# Maps each city to its state abbreviation
CITY_STATE = {
    "National Average": None,
    "Anchorage, AK": "AK", "Birmingham, AL": "AL", "Huntsville, AL": "AL", "Montgomery, AL": "AL",
    "El Dorado, AR": "AR", "Fayetteville, AR": "AR", "Little Rock, AR": "AR", "Phoenix, AZ": "AZ",
    "Scottsdale, AZ": "AZ", "Tucson, AZ": "AZ", "Fresno, CA": "CA", "Los Angeles, CA": "CA",
    "Oakland, CA": "CA", "Riverside, CA": "CA", "Sacramento, CA": "CA", "San Diego, CA": "CA",
    "San Francisco, CA": "CA", "San Jose, CA": "CA", "Boulder, CO": "CO", "Colorado Springs, CO": "CO",
    "Denver, CO": "CO", "Fort Collins, CO": "CO", "Hartford, CT": "CT", "New Haven, CT": "CT",
    "Washington, DC": "DC", "Wilmington, DE": "DE", "Jacksonville, FL": "FL", "Miami, FL": "FL",
    "Orlando, FL": "FL", "St. Petersburg, FL": "FL", "Tampa, FL": "FL", "Atlanta, GA": "GA",
    "Augusta, GA": "GA", "Columbus, GA": "GA", "Savannah, GA": "GA", "Honolulu, HI": "HI",
    "Cedar Rapids, IA": "IA", "Des Moines, IA": "IA", "Boise, ID": "ID", "Chicago, IL": "IL",
    "Rockford, IL": "IL", "Springfield, IL": "IL", "Evansville, IN": "IN", "Fort Wayne, IN": "IN",
    "Indianapolis, IN": "IN", "Wichita, KS": "KS", "Lexington, KY": "KY", "Louisville, KY": "KY",
    "Baton Rouge, LA": "LA", "New Orleans, LA": "LA", "Shreveport, LA": "LA", "Boston, MA": "MA",
    "Springfield, MA": "MA", "Worcester, MA": "MA", "Baltimore, MD": "MD", "Portland, ME": "ME",
    "Ann Arbor, MI": "MI", "Detroit, MI": "MI", "Grand Rapids, MI": "MI", "Lansing, MI": "MI",
    "Minneapolis, MN": "MN", "Kansas City, MO": "MO", "Springfield, MO": "MO", "St. Louis, MO": "MO",
    "Jackson, MS": "MS", "Billings, MT": "MT", "Bozeman, MT": "MT", "Missoula, MT": "MT",
    "Asheville, NC": "NC", "Charlotte, NC": "NC", "Durham, NC": "NC", "Greensboro, NC": "NC",
    "Raleigh, NC": "NC", "Bismarck, ND": "ND", "Fargo, ND": "ND", "Lincoln, NE": "NE",
    "Omaha, NE": "NE", "Manchester, NH": "NH", "Jersey City, NJ": "NJ", "Newark, NJ": "NJ",
    "Albuquerque, NM": "NM", "Las Vegas, NV": "NV", "Reno, NV": "NV", "Albany, NY": "NY",
    "Buffalo, NY": "NY", "New York City, NY": "NY", "Rochester, NY": "NY", "Akron, OH": "OH",
    "Cincinnati, OH": "OH", "Cleveland, OH": "OH", "Columbus, OH": "OH", "Toledo, OH": "OH",
    "Oklahoma City, OK": "OK", "Tulsa, OK": "OK", "Eugene, OR": "OR", "Portland, OR": "OR",
    "Salem, OR": "OR", "Allentown, PA": "PA", "Philadelphia, PA": "PA", "Pittsburgh, PA": "PA",
    "Providence, RI": "RI", "Charleston, SC": "SC", "Columbia, SC": "SC", "Greenville, SC": "SC",
    "Rapid City, SD": "SD", "Sioux Falls, SD": "SD", "Chattanooga, TN": "TN", "Knoxville, TN": "TN",
    "Memphis, TN": "TN", "Nashville, TN": "TN", "Austin, TX": "TX", "Dallas, TX": "TX",
    "El Paso, TX": "TX", "Fort Worth, TX": "TX", "Houston, TX": "TX", "Lubbock, TX": "TX",
    "San Antonio, TX": "TX", "Waco, TX": "TX", "Provo, UT": "UT", "Salt Lake City, UT": "UT",
    "Richmond, VA": "VA", "Virginia Beach, VA": "VA", "Burlington, VT": "VT", "Seattle, WA": "WA",
    "Spokane, WA": "WA", "Tacoma, WA": "WA", "Madison, WI": "WI", "Milwaukee, WI": "WI",
    "Charleston, WV": "WV", "Casper, WY": "WY", "Cheyenne, WY": "WY",
}

NO_INCOME_TAX_STATES = {"AK", "FL", "NV", "NH", "SD", "TN", "TX", "WA", "WY"}

# ── Tax calculations ──────────────────────────────────────────────────────────
def calc_federal_tax(gross):
    brackets = [(11600, 0.10), (44725, 0.12), (95375, 0.22),
                (201050, 0.24), (383900, 0.32), (487450, 0.35), (float("inf"), 0.37)]
    std_deduction = 14600
    taxable = max(0, gross - std_deduction)
    tax = 0
    prev = 0
    for top, rate in brackets:
        if taxable <= prev:
            break
        tax += (min(taxable, top) - prev) * rate
        prev = top
    tax += gross * 0.0765  # FICA
    return round(tax)

def calc_state_tax(gross, state_abbr):
    if not state_abbr or state_abbr not in STATE_TAX:
        return 0
    info = STATE_TAX[state_abbr]
    if info["type"] == "none":
        return 0
    if info["type"] == "flat":
        return round(gross * info["rate"])
    std_ded = info.get("std_ded", 0)
    taxable = max(0, gross - std_ded)
    tax = 0
    prev = 0
    for top, rate in info["brackets"]:
        if taxable <= prev:
            break
        tax += (min(taxable, top) - prev) * rate
        prev = top
    return round(tax)

# ── Budget frameworks ────────────────────────────────────────────────────────
FRAMEWORKS = {
    "50/30/20 (Needs · Wants · Savings)": {
        "housing": 28, "food": 12, "transport": 10,
        "savings": 15, "entertainment": 8, "health": 6,
        "clothing": 5, "debt": 7, "other": 9,
    },
    "Zero-Based (Every dollar assigned)": {
        "housing": 30, "food": 14, "transport": 9,
        "savings": 12, "entertainment": 6, "health": 7,
        "clothing": 4, "debt": 10, "other": 8,
    },
    "Aggressive Savings (FIRE-adjacent)": {
        "housing": 22, "food": 9, "transport": 7,
        "savings": 30, "entertainment": 4, "health": 5,
        "clothing": 3, "debt": 12, "other": 8,
    },
    "Debt Avalanche (Pay it off fast)": {
        "housing": 25, "food": 11, "transport": 8,
        "savings": 8, "entertainment": 5, "health": 6,
        "clothing": 4, "debt": 25, "other": 8,
    },
}

CATEGORIES = [
    ("housing",       "Housing",             "#c8a96e"),
    ("food",          "Food & dining",        "#7ec8a0"),
    ("transport",     "Transportation",       "#7eafc8"),
    ("savings",       "Savings & investing",  "#a07ec8"),
    ("entertainment", "Entertainment",        "#c87ea0"),
    ("health",        "Health",               "#7ec8c8"),
    ("clothing",      "Clothing",             "#c8b07e"),
    ("debt",          "Debt repayment",       "#c87e7e"),
    ("other",         "Other / buffer",       "#8a8a8a"),
]

COL_AFFECTED = {"housing", "food", "transport", "health"}

# ── Lifestyle tiers ──────────────────────────────────────────────────────────
TIERS = {
    "🌿 Frugal": {
        "adj": {"housing": -2, "food": -2, "transport": -1, "savings": 5,
                "entertainment": -4, "health": 1, "clothing": -3, "debt": 3, "other": 3},
        "desc": "Prioritizes savings and debt payoff. Minimizes discretionary spending.",
        "css": "tier-frugal",
    },
    "😊 Comfortable": {
        "adj": {k: 0 for k in ["housing", "food", "transport", "savings",
                                "entertainment", "health", "clothing", "debt", "other"]},
        "desc": "Balanced lifestyle. Framework allocations applied as-is.",
        "css": "tier-comfortable",
    },
    "✨ Lavish": {
        "adj": {"housing": 4, "food": 3, "transport": 2, "savings": -7,
                "entertainment": 5, "health": 1, "clothing": 3, "debt": -4, "other": -7},
        "desc": "Maximizes lifestyle spending. Lower savings and debt repayment rates.",
        "css": "tier-lavish",
    },
}

PRIORITY_TO_FRAMEWORK = {
    "Build savings fast":         "Aggressive Savings (FIRE-adjacent)",
    "Pay off debt first":         "Debt Avalanche (Pay it off fast)",
    "Balanced and comfortable":   "50/30/20 (Needs · Wants · Savings)",
    "Track every dollar":         "Zero-Based (Every dollar assigned)",
}
LIFESTYLE_TO_TIER = {
    "Frugal — save more, spend less": "🌿 Frugal",
    "Comfortable — balanced approach": "😊 Comfortable",
    "Lavish — live it up":            "✨ Lavish",
}


# ── PDF generation ───────────────────────────────────────────────────────────
def generate_pdf(gross, net, federal_tax, state_tax_amt, state_abbr,
                 location, fw_name, tier_name, cat_data,
                 goal_name, goal_amount, goal_current, goal_months,
                 debt_balance, debt_rate, monthly_debt_payment, debt_months, debt_interest):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=20)
    weekly_net = net / 52
    total_tax = federal_tax + state_tax_amt

    pdf.set_fill_color(15, 15, 15)
    pdf.rect(0, 0, 220, 38, "F")
    pdf.set_xy(20, 10)
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(240, 234, 214)
    pdf.cell(0, 8, "Lifestyle Budget Simulator", ln=True)
    pdf.set_xy(20, 22)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(140, 140, 140)
    short_fw = fw_name.split("(")[0].strip()
    short_tier = tier_name.split(" ", 1)[-1]
    pdf.cell(0, 6, f"{location}  |  {short_fw}  |  {short_tier}", ln=True)
    pdf.set_y(46)

    def section(title):
        pdf.set_font("Helvetica", "B", 12)
        pdf.set_text_color(30, 30, 30)
        pdf.cell(0, 7, title, ln=True)
        pdf.set_draw_color(210, 210, 210)
        pdf.line(20, pdf.get_y(), 190, pdf.get_y())
        pdf.ln(3)

    def kv(label, value):
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(80, 5.5, label)
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_text_color(30, 30, 30)
        pdf.cell(0, 5.5, value, ln=True)

    eff_rate = round(total_tax / gross * 100) if gross else 0
    fed_rate  = round(federal_tax / gross * 100) if gross else 0
    st_rate   = round(state_tax_amt / gross * 100) if gross else 0

    section("Income Summary")
    kv("Gross Income", f"${gross:,.0f}")
    kv("Federal Tax (incl. FICA)", f"${federal_tax:,.0f}  ({fed_rate}% of gross)")
    state_label = f"{state_abbr} State Tax" if state_abbr else "State Tax"
    if state_abbr in NO_INCOME_TAX_STATES:
        kv(state_label, "No state income tax")
    else:
        kv(state_label, f"${state_tax_amt:,.0f}  ({st_rate}% of gross)")
    kv("Total Tax Burden", f"${total_tax:,.0f}  ({eff_rate}% effective rate)")
    kv("Take-Home (Annual)", f"${net:,.0f}")
    kv("Take-Home (Weekly)", f"${weekly_net:,.0f}")
    pdf.ln(6)

    section("Weekly Budget Breakdown")
    pdf.set_fill_color(235, 235, 235)
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(72, 6, "Category", fill=True)
    pdf.cell(20, 6, "Alloc.", fill=True, align="R")
    pdf.cell(42, 6, "Weekly", fill=True, align="R")
    pdf.cell(0,  6, "Annual", fill=True, align="R", ln=True)
    for i, d in enumerate(cat_data):
        bg = (248, 248, 248) if i % 2 == 0 else (255, 255, 255)
        pdf.set_fill_color(*bg)
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(30, 30, 30)
        pdf.cell(72, 5.5, d["label"], fill=True)
        pdf.cell(20, 5.5, f"{d['pct']}%", fill=True, align="R")
        pdf.cell(42, 5.5, f"${d['weekly']:,.0f}", fill=True, align="R")
        pdf.cell(0,  5.5, f"${d['annual']:,.0f}", fill=True, align="R", ln=True)
    pdf.ln(7)

    if goal_amount > 0:
        section(f"Savings Goal - {goal_name}")
        remaining = max(0, goal_amount - goal_current)
        kv("Target Amount", f"${goal_amount:,.0f}")
        kv("Already Saved", f"${goal_current:,.0f}")
        kv("Remaining", f"${remaining:,.0f}")
        if goal_months == 0:
            kv("Status", "Goal already reached!")
        elif goal_months is not None:
            yrs, mos = divmod(int(goal_months), 12)
            parts = []
            if yrs: parts.append(f"{yrs} yr{'s' if yrs != 1 else ''}")
            if mos: parts.append(f"{mos} mo")
            kv("Estimated Timeline", " ".join(parts) or "< 1 month")
        else:
            kv("Status", "No savings allocated - adjust your framework.")
        pdf.ln(6)

    if debt_balance > 0:
        section("Debt Payoff Estimate")
        kv("Current Balance", f"${debt_balance:,.0f}")
        kv("APR", f"{debt_rate:.1f}%")
        kv("Monthly Payment (from allocation)", f"${monthly_debt_payment:,.0f}")
        if debt_months is None or debt_months == float("inf"):
            kv("Status", "Payment does not cover interest - increase debt allocation.")
        else:
            yrs, mos = divmod(int(debt_months), 12)
            parts = []
            if yrs: parts.append(f"{yrs} yr{'s' if yrs != 1 else ''}")
            if mos: parts.append(f"{mos} mo")
            kv("Payoff Timeline", " ".join(parts) or "< 1 month")
            kv("Total Interest Paid", f"${debt_interest:,.0f}")
        pdf.ln(6)

    pdf.set_y(-18)
    pdf.set_font("Helvetica", "I", 7)
    pdf.set_text_color(160, 160, 160)
    pdf.multi_cell(0, 4,
        "Tax estimates use 2024 US federal brackets + 7.65% FICA + simplified state income tax rates. "
        "Cost of living multipliers are estimates. All figures are for planning purposes only.",
        align="C")

    return bytes(pdf.output())


# ── Account / persistence helpers ────────────────────────────────────────────
_USERS_FILE = os.path.join(os.path.dirname(__file__), "users.json")

def _load_users() -> dict:
    if os.path.exists(_USERS_FILE):
        try:
            with open(_USERS_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def _save_users(users: dict):
    with open(_USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

def _hash_pw(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()

_PROFILE_KEYS = [
    "s_name", "s_gross", "s_income_type", "s_hourly",
    "s_location", "s_framework", "s_tier", "intro_done",
]

def _save_profile(username: str):
    users = _load_users()
    if username in users:
        users[username]["profile"] = {
            k: st.session_state.get(k) for k in _PROFILE_KEYS
        }
        _save_users(users)

def _load_profile(username: str):
    users = _load_users()
    profile = users.get(username, {}).get("profile", {})
    for k, v in profile.items():
        if v is not None:
            st.session_state[k] = v


# ── About page ────────────────────────────────────────────────────────────────
if not st.session_state.get("about_done", False):

    ab_l, ab_r = st.columns([1.1, 0.9], gap="large")

    with ab_l:
        st.markdown("""
<div style="padding:60px 48px 60px 0">
  <div style="font-size:10px;font-weight:700;letter-spacing:0.18em;text-transform:uppercase;color:#c8a96e;margin-bottom:24px">Lifestyle Budget Simulator</div>
  <div style="font-family:'DM Serif Display',serif;font-size:54px;color:var(--t1);line-height:1.05;letter-spacing:-0.03em;margin-bottom:24px">
    Your money.<br>Your future.<br><span style="color:#c8a96e">Your plan.</span>
  </div>
  <div style="font-size:16px;color:var(--t2);font-weight:300;line-height:1.8;margin-bottom:40px;max-width:480px">
    Most people spend more time planning a vacation than planning their finances. The result?
    78% of Americans live paycheck to paycheck — not because they don't earn enough,
    but because no one ever showed them where the money actually goes.
  </div>
  <div style="display:grid;gap:20px;max-width:500px">
    <div style="background:var(--card);border:1px solid var(--border);border-left:3px solid #c8a96e;border-radius:10px;padding:18px 22px">
      <div style="font-size:28px;font-family:'DM Serif Display',serif;color:#c8a96e;line-height:1">$1,000</div>
      <div style="font-size:12px;color:var(--t2);margin-top:4px">The average American spends this much monthly on non-essentials without realizing it.</div>
    </div>
    <div style="background:var(--card);border:1px solid var(--border);border-left:3px solid #7ec8a0;border-radius:10px;padding:18px 22px">
      <div style="font-size:28px;font-family:'DM Serif Display',serif;color:#7ec8a0;line-height:1">10 years</div>
      <div style="font-size:12px;color:var(--t2);margin-top:4px">How much earlier people who start budgeting in their 20s can retire vs. those who don't.</div>
    </div>
    <div style="background:var(--card);border:1px solid var(--border);border-left:3px solid #a07ec8;border-radius:10px;padding:18px 22px">
      <div style="font-size:28px;font-family:'DM Serif Display',serif;color:#b09ad8;line-height:1">3x</div>
      <div style="font-size:12px;color:var(--t2);margin-top:4px">The net worth difference between people who track their spending and those who don't, at retirement.</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

    with ab_r:
        st.markdown("""
<div style="padding:60px 0 60px 0">
  <div style="background:var(--card);border:1px solid var(--border);border-radius:16px;padding:40px 36px">
    <div style="font-size:20px;font-weight:600;color:var(--t1);margin-bottom:8px;font-family:'DM Serif Display',serif">A clearer picture changes everything.</div>
    <div style="font-size:13px;color:var(--t2);margin-bottom:32px;line-height:1.7">
      This isn't a spreadsheet. It's a living, real-time view of what your income actually means —
      broken into the categories that shape your day-to-day life.
    </div>
    <div style="display:grid;gap:16px;margin-bottom:32px">
      <div style="display:flex;gap:14px;align-items:flex-start">
        <div style="width:32px;height:32px;border-radius:8px;background:rgba(200,169,110,.1);border:1px solid rgba(200,169,110,.2);display:flex;align-items:center;justify-content:center;flex-shrink:0;font-size:15px">📍</div>
        <div>
          <div style="font-size:13px;font-weight:600;color:var(--t1);margin-bottom:2px">Real cost-of-living data</div>
          <div style="font-size:12px;color:var(--t2);line-height:1.5">Budgets adjust automatically for 100+ US cities. Moving to Austin vs. San Francisco makes a $30,000 difference — we show you that.</div>
        </div>
      </div>
      <div style="display:flex;gap:14px;align-items:flex-start">
        <div style="width:32px;height:32px;border-radius:8px;background:rgba(126,200,160,.1);border:1px solid rgba(126,200,160,.2);display:flex;align-items:center;justify-content:center;flex-shrink:0;font-size:15px">🏦</div>
        <div>
          <div style="font-size:13px;font-weight:600;color:var(--t1);margin-bottom:2px">See your full financial picture</div>
          <div style="font-size:12px;color:var(--t2);line-height:1.5">Net worth, emergency fund health, debt payoff timeline, retirement projections — all in one place, personalized to your numbers.</div>
        </div>
      </div>
      <div style="display:flex;gap:14px;align-items:flex-start">
        <div style="width:32px;height:32px;border-radius:8px;background:rgba(160,126,200,.1);border:1px solid rgba(160,126,200,.2);display:flex;align-items:center;justify-content:center;flex-shrink:0;font-size:15px">📈</div>
        <div>
          <div style="font-size:13px;font-weight:600;color:var(--t1);margin-bottom:2px">Plan the life you actually want</div>
          <div style="font-size:12px;color:var(--t2);line-height:1.5">Model promotions, compare cities, audit subscriptions, and project your retirement — before making any decision.</div>
        </div>
      </div>
      <div style="display:flex;gap:14px;align-items:flex-start">
        <div style="width:32px;height:32px;border-radius:8px;background:rgba(126,200,200,.1);border:1px solid rgba(126,200,200,.2);display:flex;align-items:center;justify-content:center;flex-shrink:0;font-size:15px">⚡</div>
        <div>
          <div style="font-size:13px;font-weight:600;color:var(--t1);margin-bottom:2px">Up and running in 30 seconds</div>
          <div style="font-size:12px;color:var(--t2);line-height:1.5">No imports, no spreadsheets, no financial jargon. Enter your income, pick your city, and your complete budget is ready instantly.</div>
        </div>
      </div>
    </div>
    <div style="font-size:12px;color:var(--t-25);text-align:center;margin-bottom:16px">The best time to start was yesterday. The second best time is now.</div>
  </div>
</div>
""", unsafe_allow_html=True)

        if st.button("Get started →", use_container_width=True, type="primary"):
            st.session_state["about_done"] = True
            st.rerun()

    st.stop()


# ── Auth page ─────────────────────────────────────────────────────────────────
if not st.session_state.get("auth_done", False):
    _, mid, _ = st.columns([1, 1.6, 1])
    with mid:
        st.markdown("""
<div class="auth-logo">Lifestyle Budget Simulator</div>
<div class="auth-tagline">Sign in to save and reload your budget across sessions.</div>
""", unsafe_allow_html=True)

        tab_in, tab_up = st.tabs(["Sign in", "Create account"])

        with tab_in:
            st.markdown('<div class="auth-label">Username</div>', unsafe_allow_html=True)
            si_user = st.text_input("Username", key="si_user", placeholder="your username",
                                    label_visibility="collapsed")
            st.markdown('<div class="auth-label">Password</div>', unsafe_allow_html=True)
            si_pw = st.text_input("Password", key="si_pw", type="password",
                                  label_visibility="collapsed")
            if st.button("Sign in", use_container_width=True, type="primary", key="btn_signin"):
                _users = _load_users()
                if si_user in _users and _users[si_user]["pw"] == _hash_pw(si_pw):
                    st.session_state["auth_done"] = True
                    st.session_state["auth_user"] = si_user
                    _load_profile(si_user)
                    st.rerun()
                else:
                    st.markdown('<div class="auth-error">Incorrect username or password.</div>',
                                unsafe_allow_html=True)
            st.markdown('<div style="height:6px"></div>', unsafe_allow_html=True)
            if st.button("Continue without an account →", use_container_width=True, key="btn_guest"):
                st.session_state["auth_done"] = True
                st.session_state["auth_user"] = None
                st.rerun()

        with tab_up:
            st.markdown('<div class="auth-label">Username</div>', unsafe_allow_html=True)
            su_user = st.text_input("Username", key="su_user", placeholder="pick a username",
                                    label_visibility="collapsed")
            st.markdown('<div class="auth-label">Password</div>', unsafe_allow_html=True)
            su_pw = st.text_input("Password", key="su_pw", type="password",
                                  label_visibility="collapsed")
            st.markdown('<div class="auth-label">Confirm password</div>', unsafe_allow_html=True)
            su_pw2 = st.text_input("Confirm password", key="su_pw2", type="password",
                                   label_visibility="collapsed")
            if st.button("Create account", use_container_width=True, type="primary", key="btn_signup"):
                _users = _load_users()
                if not su_user.strip():
                    st.markdown('<div class="auth-error">Please enter a username.</div>',
                                unsafe_allow_html=True)
                elif su_user in _users:
                    st.markdown('<div class="auth-error">That username is already taken.</div>',
                                unsafe_allow_html=True)
                elif len(su_pw) < 6:
                    st.markdown('<div class="auth-error">Password must be at least 6 characters.</div>',
                                unsafe_allow_html=True)
                elif su_pw != su_pw2:
                    st.markdown('<div class="auth-error">Passwords do not match.</div>',
                                unsafe_allow_html=True)
                else:
                    _users[su_user] = {"pw": _hash_pw(su_pw), "profile": {}}
                    _save_users(_users)
                    st.session_state["auth_done"] = True
                    st.session_state["auth_user"] = su_user
                    st.rerun()

    st.stop()


# ── Intro page ────────────────────────────────────────────────────────────────
if not st.session_state.get("intro_done", False):

    hero, form = st.columns([1.05, 0.95], gap="large")

    with hero:
        st.markdown("""
<div class="intro-hero">
  <div class="intro-eyebrow">Lifestyle Budget Simulator</div>
  <div class="intro-title">See exactly what<br>your money<br>looks like.</div>
  <div class="intro-sub">Real cost-of-living data. Clear, honest numbers.<br>No vague advice — just your actual budget.</div>
  <div>
    <div class="intro-feature"><span class="intro-feature-dot"></span>Adjusts for your city's cost of living</div>
    <div class="intro-feature"><span class="intro-feature-dot"></span>9 budget categories broken down weekly &amp; annually</div>
    <div class="intro-feature"><span class="intro-feature-dot"></span>Savings goal tracker with projected timeline</div>
    <div class="intro-feature"><span class="intro-feature-dot"></span>Debt payoff calculator with amortization chart</div>
    <div class="intro-feature"><span class="intro-feature-dot"></span>Export your full budget as a PDF</div>
  </div>
</div>
""", unsafe_allow_html=True)

    with form:
        st.markdown("""
<div class="intro-card">
  <div class="intro-card-title">Build your budget</div>
  <div class="intro-card-sub">Takes about 30 seconds.</div>
</div>
""", unsafe_allow_html=True)

        st.markdown('<div class="intro-section-label">Your name (optional)</div>', unsafe_allow_html=True)
        intro_name = st.text_input("Name", placeholder="e.g. Alex", label_visibility="collapsed")

        st.markdown('<div class="intro-section-label">How do you earn?</div>', unsafe_allow_html=True)
        intro_income_type = st.radio("Income type", ["Annual salary", "Hourly wage"],
                                     horizontal=True, label_visibility="collapsed")
        intro_hourly = 25.0  # default, overwritten below if hourly selected
        if intro_income_type == "Annual salary":
            intro_gross = st.number_input("Annual salary ($)", min_value=0, max_value=2_000_000,
                                          value=75_000, step=1_000, format="%d", label_visibility="collapsed")
        else:
            intro_hourly = st.number_input("Hourly wage ($)", min_value=0.0, max_value=500.0,
                                           value=25.0, step=0.5, format="%.2f", label_visibility="collapsed")
            intro_gross = intro_hourly * 40 * 52
            st.caption(f"→ ${intro_gross:,.0f} / year  (40 hrs × 52 wks)")

        st.markdown('<div class="intro-section-label">Where do you live?</div>', unsafe_allow_html=True)
        intro_location = st.selectbox("Location", list(COL_DATA.keys()),
                                      index=0, label_visibility="collapsed")

        st.markdown('<div class="intro-section-label">What\'s your main financial goal?</div>', unsafe_allow_html=True)
        intro_priority = st.radio("Priority", list(PRIORITY_TO_FRAMEWORK.keys()),
                                  label_visibility="collapsed")

        st.markdown('<div class="intro-section-label">How would you describe your lifestyle?</div>', unsafe_allow_html=True)
        intro_lifestyle = st.radio("Lifestyle", list(LIFESTYLE_TO_TIER.keys()),
                                   index=1, label_visibility="collapsed")

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        if st.button("See my budget →", use_container_width=True, type="primary"):
            st.session_state.update({
                "intro_done":     True,
                "s_name":         intro_name,
                "s_gross":        int(intro_gross),
                "s_income_type":  intro_income_type,
                "s_hourly":       intro_hourly if intro_income_type == "Hourly wage" else 25.0,
                "s_location":     intro_location,
                "s_framework":    PRIORITY_TO_FRAMEWORK[intro_priority],
                "s_tier":         LIFESTYLE_TO_TIER[intro_lifestyle],
            })
            st.rerun()

    st.stop()


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    s_name = st.session_state.get("s_name", "") or st.session_state.get("auth_user", "")
    greeting = f"Hey, {s_name}" if s_name else "Your Budget"
    st.markdown(f'<p style="font-family:\'DM Serif Display\',serif;font-size:20px;color:var(--t1);margin-bottom:2px;letter-spacing:-0.01em">{greeting}</p>', unsafe_allow_html=True)
    st.markdown('<p style="font-size:12px;color:var(--t1);margin-bottom:20px;font-weight:300;opacity:.5">Adjust any variable below to update your budget.</p>', unsafe_allow_html=True)

    st.markdown("#### Income")
    _it_default = 0 if st.session_state.get("s_income_type", "Annual salary") == "Annual salary" else 1
    income_type = st.radio("Income type", ["Annual salary", "Hourly wage"],
                           horizontal=True, index=_it_default, label_visibility="collapsed")

    if income_type == "Annual salary":
        gross = st.number_input("Annual salary ($)", min_value=0, max_value=2_000_000,
                                value=st.session_state.get("s_gross", 75_000), step=1_000, format="%d")
    else:
        hourly = st.number_input("Hourly wage ($)", min_value=0.0, max_value=500.0,
                                 value=st.session_state.get("s_hourly", 25.0), step=0.50, format="%.2f")
        gross = hourly * 40 * 52
        st.caption(f"→ ${gross:,.0f} / year (40 hrs × 52 wks)")

    st.divider()

    st.markdown("#### Location")
    _loc_list = list(COL_DATA.keys()) + ["My city isn't listed →"]
    _loc_default = st.session_state.get("s_location", "National Average")
    _loc_idx = _loc_list.index(_loc_default) if _loc_default in _loc_list else 0
    location_sel = st.selectbox("Type or select a city", _loc_list, index=_loc_idx)

    if location_sel == "My city isn't listed →":
        custom_col_idx = st.slider("Estimated cost of living index", 60, 250, 100)
        st.caption("100 = US average · NYC ≈ 187 · Rural Midwest ≈ 80–90")
        col_idx  = custom_col_idx
        col_info = {
            "index":          custom_col_idx,
            "housing_mult":   round((custom_col_idx / 100) ** 2.0, 3),
            "food_mult":      round(max(0.88, 1.0 + (custom_col_idx - 100) * 0.0022), 3),
            "transport_mult": round(max(0.90, 1.0 + (custom_col_idx - 100) * 0.0018), 3),
            "health_mult":    round(max(0.90, 1.0 + (custom_col_idx - 100) * 0.0015), 3),
        }
        location   = f"Custom city (COL {custom_col_idx})"
        state_abbr = None
    else:
        location   = location_sel
        col_info   = COL_DATA[location]
        col_idx    = col_info["index"]
        state_abbr = CITY_STATE.get(location)
        if col_idx != 100:
            diff = col_idx - 100
            direction = "higher" if diff > 0 else "lower"
            st.caption(f"Cost of living is **{abs(diff)}% {direction}** than the national average.")

    st.divider()

    st.markdown("#### Budgeting framework")
    _fw_list = list(FRAMEWORKS.keys())
    _fw_default = st.session_state.get("s_framework", _fw_list[0])
    _fw_idx = _fw_list.index(_fw_default) if _fw_default in _fw_list else 0
    fw_name = st.selectbox("Framework", _fw_list, index=_fw_idx)

    # Reset pinned amounts and custom sliders whenever the framework changes
    if st.session_state.get("_last_fw") != fw_name:
        for key, _, _ in CATEGORIES:
            st.session_state.pop(f"pin_chk_{key}", None)
            st.session_state.pop(f"pin_val_{key}", None)
            st.session_state.pop(f"sl_{key}", None)
        st.session_state["_last_fw"] = fw_name

    pcts = FRAMEWORKS[fw_name]

    with st.expander("Customize allocations"):
        custom_pcts = {}
        total = 0
        for key, label, _ in CATEGORIES:
            val = st.slider(label, 0, 60, pcts[key], key=f"sl_{key}")
            custom_pcts[key] = val
            total += val
        if total != 100:
            st.warning(f"Total: {total}% (needs to be 100%)")
        else:
            st.success("Total: 100% ✓")
            pcts = custom_pcts

    st.divider()

    st.markdown("#### Real dollar amounts")
    st.caption("Pin specific categories to exact monthly amounts. Remaining take-home is split across unpinned categories.")
    with st.expander("Enter known expenses"):
        pinned = {}
        pin_items = [
            ("housing",       "Rent / mortgage ($/mo)"),
            ("food",          "Food & dining ($/mo)"),
            ("transport",     "Transportation ($/mo)"),
            ("health",        "Health ($/mo)"),
            ("entertainment", "Entertainment ($/mo)"),
            ("clothing",      "Clothing ($/mo)"),
            ("debt",          "Debt repayment ($/mo)"),
            ("other",         "Other / buffer ($/mo)"),
            ("savings",       "Savings & investing ($/mo)"),
        ]
        for key, pin_label in pin_items:
            use_pin = st.checkbox(f"I know my {pin_label.split('(')[0].strip().lower()}", key=f"pin_chk_{key}")
            if use_pin:
                val = st.number_input(pin_label, min_value=0, max_value=50_000,
                                      value=0, step=50, format="%d", key=f"pin_val_{key}")
                pinned[key] = val
        if pinned:
            total_pinned = sum(pinned.values())
            st.caption(f"Pinned total: **${total_pinned:,.0f}/mo**")

    if pinned:
        st.markdown("**Effective allocation after pinning:**")
        _mn = (gross - calc_federal_tax(gross) - calc_state_tax(gross, state_abbr)) / 12
        # Apply tier adjustment to get accurate pcts matching the main cards
        _tier_adj = TIERS.get(st.session_state.get("s_tier", "😊 Comfortable"), TIERS["😊 Comfortable"])["adj"]
        _adj_pcts = {key: max(0, pcts.get(key, 0) + _tier_adj.get(key, 0)) for key, _, _ in CATEGORIES}
        _adj_total = sum(_adj_pcts.values())
        if _adj_total > 0 and _adj_total != 100:
            _scale = 100 / _adj_total
            _adj_pcts = {k: round(v * _scale) for k, v in _adj_pcts.items()}
            _diff = 100 - sum(_adj_pcts.values())
            if _diff != 0:
                _mk = max(_adj_pcts, key=_adj_pcts.get)
                _adj_pcts[_mk] += _diff
        _pinned_total = sum(pinned.values())
        _remaining = max(0, _mn - _pinned_total)
        _unpinned_keys = [k for k, _, _ in CATEGORIES if k not in pinned]
        _unpinned_pct_total = sum(_adj_pcts.get(k, 0) for k in _unpinned_keys) or 1
        _rows = ""
        for _key, _label, _color in CATEGORIES:
            if _key in pinned:
                _mo = float(pinned[_key])
            else:
                _mo = _remaining * _adj_pcts.get(_key, 0) / _unpinned_pct_total
            _pct = round(_mo / _mn * 100) if _mn > 0 else 0
            _pin_marker = " 📌" if _key in pinned else ""
            _rows += f'<div style="display:flex;justify-content:space-between;align-items:center;padding:4px 0;border-bottom:1px solid var(--border);font-size:12px"><span style="color:var(--t-60)">{_label}{_pin_marker}</span><span style="color:var(--t1);font-weight:500">${_mo:,.0f}/mo &nbsp;<span style="color:var(--t3);font-weight:400">({_pct}%)</span></span></div>'
        st.markdown(f'<div style="background:var(--surface);border:1px solid var(--border);border-radius:8px;padding:12px 14px;margin-top:4px">{_rows}<div style="display:flex;justify-content:space-between;padding-top:6px;font-size:12px;font-weight:600"><span style="color:var(--t2)">Take-home</span><span style="color:#c8a96e">${_mn:,.0f}/mo &nbsp;(100%)</span></div></div>', unsafe_allow_html=True)

    st.divider()

    st.markdown("#### Lifestyle tier")
    _tier_list = list(TIERS.keys())
    _tier_default = st.session_state.get("s_tier", "😊 Comfortable")
    _tier_idx = _tier_list.index(_tier_default) if _tier_default in _tier_list else 1
    tier = st.radio("Lifestyle tier", _tier_list, index=_tier_idx,
                    horizontal=True, label_visibility="collapsed")
    st.caption(TIERS[tier]["desc"])

    st.divider()

    st.markdown("#### Savings goal")
    with st.expander("Set a savings goal"):
        goal_name    = st.text_input("Goal name", value="Emergency Fund")
        goal_amount  = st.number_input("Target amount ($)", min_value=0, max_value=10_000_000, value=10_000, step=500, format="%d")
        goal_current = st.number_input("Already saved ($)", min_value=0, max_value=10_000_000, value=0, step=500, format="%d")

    st.divider()

    st.markdown("#### Debt payoff")
    with st.expander("Enter debt details"):
        debt_balance = st.number_input("Total debt balance ($)", min_value=0, max_value=2_000_000, value=0, step=500, format="%d")
        debt_rate    = st.slider("Annual interest rate (APR %)", 0.0, 36.0, 18.0, step=0.1)

    st.divider()

    st.markdown("#### Income projections")
    with st.expander("Add promotions / raises"):
        num_promos = st.number_input("How many promotions?", min_value=1, max_value=10,
                                     value=1, step=1, format="%d")
        promotions = []
        for _i in range(int(num_promos)):
            st.markdown(f'<div style="font-size:10px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:var(--t3);margin-top:{"0" if _i == 0 else "18"}px;margin-bottom:6px">Promotion {_i + 1}</div>', unsafe_allow_html=True)
            _label = st.text_input("Label", value=f"Promotion {_i + 1}",
                                   placeholder="e.g. Mid-year raise",
                                   key=f"promo_label_{_i}", label_visibility="collapsed")
            _months = st.number_input("Months from now", min_value=1, max_value=240,
                                      value=12 * (_i + 1), step=1, format="%d",
                                      key=f"promo_months_{_i}",
                                      help="How many months until this raise takes effect")
            _ptype = st.radio("Type", ["% raise", "New salary"],
                              horizontal=True, key=f"promo_type_{_i}",
                              label_visibility="collapsed")
            if _ptype == "% raise":
                _val = st.number_input("Raise (%)", min_value=0.0, max_value=200.0,
                                       value=5.0, step=0.5, format="%.1f",
                                       key=f"promo_val_{_i}", label_visibility="collapsed")
            else:
                _val = st.number_input("New salary ($)", min_value=0, max_value=5_000_000,
                                       value=max(gross + 10_000, 1), step=1_000, format="%d",
                                       key=f"promo_val_{_i}", label_visibility="collapsed")
            promotions.append({
                "label":  _label or f"Promotion {_i + 1}",
                "months": int(_months),
                "type":   _ptype,
                "value":  _val,
            })
        # sort by month so the timeline is always in order
        promotions.sort(key=lambda x: x["months"])

    st.divider()

    st.markdown("#### Emergency fund")
    with st.expander("Current liquid savings"):
        ef_savings = st.number_input(
            "Liquid savings ($)", min_value=0, max_value=10_000_000, value=0, step=500, format="%d",
            help="Cash in checking/savings accounts you could access in an emergency",
            label_visibility="collapsed",
        )

    st.divider()

    st.markdown("#### Subscriptions")
    _PRESET_SUBS = [
        ("Netflix", 15.49), ("Hulu", 7.99), ("Disney+", 7.99),
        ("Max (HBO)", 15.99), ("Apple TV+", 9.99), ("Paramount+", 7.99),
        ("Peacock", 5.99), ("Spotify", 10.99), ("Apple Music", 10.99),
        ("YouTube Premium", 13.99), ("Amazon Prime", 14.99),
        ("iCloud+", 2.99), ("Google One", 2.99),
        ("Xbox Game Pass", 14.99), ("PS Plus", 8.33),
        ("Adobe Creative Cloud", 54.99), ("Microsoft 365", 9.99),
        ("Dropbox", 11.99), ("Gym membership", 40.00),
        ("News subscription", 15.00),
    ]
    sub_checked = []
    sub_total   = 0.0
    with st.expander("Audit your subscriptions"):
        for _sname, _sprice in _PRESET_SUBS:
            _c1, _c2 = st.columns([3, 1.4])
            with _c1:
                _on = st.checkbox(_sname, key=f"sub_{_sname}")
            with _c2:
                if _on:
                    _p = st.number_input("$", min_value=0.0, max_value=2000.0,
                                         value=float(_sprice), step=0.01, format="%.2f",
                                         key=f"sub_price_{_sname}", label_visibility="collapsed")
                    sub_total += _p
                    sub_checked.append((_sname, _p))
        st.markdown("---")
        _add_custom = st.checkbox("Add custom subscription", key="sub_custom_on")
        if _add_custom:
            _cname = st.text_input("Name", key="sub_custom_name", placeholder="e.g. Duolingo Plus")
            _camt  = st.number_input("Monthly cost ($)", min_value=0.0, max_value=10_000.0,
                                     value=0.0, step=1.0, format="%.2f", key="sub_custom_amt")
            if _cname.strip():
                sub_total += _camt
                sub_checked.append((_cname.strip(), _camt))
        st.caption(f"Total: **${sub_total:,.2f}/mo**  (${sub_total * 12:,.0f}/yr)")

    st.divider()

    st.markdown("#### Net worth")
    with st.expander("Add assets & liabilities"):
        st.markdown('<div class="intro-section-label">Assets</div>', unsafe_allow_html=True)
        nw_checking     = st.number_input("Checking & savings ($)", min_value=0, max_value=100_000_000, value=0, step=1_000, format="%d", key="nw_checking")
        nw_investments  = st.number_input("Investments — stocks, ETFs ($)", min_value=0, max_value=100_000_000, value=0, step=1_000, format="%d", key="nw_investments")
        nw_retirement_a = st.number_input("Retirement accounts — 401k, IRA ($)", min_value=0, max_value=100_000_000, value=0, step=1_000, format="%d", key="nw_retirement_a")
        nw_home         = st.number_input("Home value ($)", min_value=0, max_value=100_000_000, value=0, step=5_000, format="%d", key="nw_home")
        nw_vehicle      = st.number_input("Vehicle value ($)", min_value=0, max_value=500_000, value=0, step=1_000, format="%d", key="nw_vehicle")
        nw_other_asset  = st.number_input("Other assets ($)", min_value=0, max_value=100_000_000, value=0, step=1_000, format="%d", key="nw_other_asset")
        st.markdown('<div class="intro-section-label" style="margin-top:14px">Liabilities</div>', unsafe_allow_html=True)
        nw_mortgage     = st.number_input("Mortgage balance ($)", min_value=0, max_value=100_000_000, value=0, step=5_000, format="%d", key="nw_mortgage")
        nw_student      = st.number_input("Student loans ($)", min_value=0, max_value=1_000_000, value=0, step=1_000, format="%d", key="nw_student")
        nw_car_loan     = st.number_input("Car loan ($)", min_value=0, max_value=500_000, value=0, step=1_000, format="%d", key="nw_car_loan")
        nw_credit       = st.number_input("Credit card debt ($)", min_value=0, max_value=500_000, value=0, step=500, format="%d", key="nw_credit")
        nw_other_liab   = st.number_input("Other liabilities ($)", min_value=0, max_value=100_000_000, value=0, step=1_000, format="%d", key="nw_other_liab")

    st.divider()

    st.markdown("#### Retirement")
    with st.expander("Retirement projector"):
        ret_age         = st.slider("Your current age", 18, 70, 30, key="ret_age")
        ret_target_age  = st.slider("Target retirement age", 45, 80, 65, key="ret_target_age")
        ret_current_ret = st.number_input("Current retirement savings ($)", min_value=0, max_value=100_000_000, value=0, step=1_000, format="%d", key="ret_current_ret")
        ret_return_rate = st.slider("Expected annual return (%)", 1.0, 15.0, 7.0, step=0.5, key="ret_return")
        ret_inflation   = st.slider("Assumed inflation (%)", 0.0, 6.0, 2.5, step=0.25, key="ret_inflation")


# ── Calculations ──────────────────────────────────────────────────────────────
federal_tax    = calc_federal_tax(gross)
state_tax_amt  = calc_state_tax(gross, state_abbr)
total_tax      = federal_tax + state_tax_amt
net            = gross - total_tax
weekly_net     = net / 52
total_tax_rate = round(total_tax / gross * 100) if gross > 0 else 0
fed_rate       = round(federal_tax / gross * 100) if gross > 0 else 0
st_rate        = round(state_tax_amt / gross * 100) if gross > 0 else 0

tier_adj = TIERS[tier]["adj"]
adjusted_pcts = {key: max(0, pcts.get(key, 0) + tier_adj.get(key, 0))
                 for key, _, _ in CATEGORIES}
total_adj = sum(adjusted_pcts.values())
if total_adj > 0 and total_adj != 100:
    scale = 100 / total_adj
    adjusted_pcts = {k: round(v * scale) for k, v in adjusted_pcts.items()}
    diff = 100 - sum(adjusted_pcts.values())
    if diff != 0:
        max_key = max(adjusted_pcts, key=adjusted_pcts.get)
        adjusted_pcts[max_key] += diff
pcts = adjusted_pcts

def apply_col(key, base_weekly):
    if key == "housing":   return base_weekly * col_info["housing_mult"]
    if key == "food":      return base_weekly * col_info["food_mult"]
    if key == "transport": return base_weekly * col_info["transport_mult"]
    if key == "health":    return base_weekly * col_info["health_mult"]
    return base_weekly

monthly_net = net / 12

# ── Apply pinned dollar amounts ───────────────────────────────────────────────
# pinned dict comes from sidebar; keys are category keys, values are $/month.
# Pinned categories get their exact monthly amount.
# Remaining take-home is distributed to unpinned categories using pct weights.
pinned_total_monthly = sum(pinned.values()) if pinned else 0
remaining_monthly    = max(0, monthly_net - pinned_total_monthly)
unpinned_keys        = [key for key, _, _ in CATEGORIES if key not in pinned]
unpinned_pct_total   = sum(pcts.get(k, 0) for k in unpinned_keys) or 1

cat_data = []
for key, label, color in CATEGORIES:
    if key in pinned:
        monthly_amt = float(pinned[key])
        weekly_amt  = monthly_amt * 12 / 52
        annual_amt  = monthly_amt * 12
        # compute effective pct of take-home for display
        eff_pct = round(monthly_amt / monthly_net * 100) if monthly_net > 0 else 0
        base_weekly = weekly_net * pcts.get(key, 0) / 100
    else:
        base_weekly = weekly_net * pcts.get(key, 0) / 100
        # scale to fill remaining budget
        share       = pcts.get(key, 0) / unpinned_pct_total
        monthly_amt = remaining_monthly * share
        weekly_amt  = monthly_amt * 12 / 52
        annual_amt  = monthly_amt * 12
        eff_pct     = round(monthly_amt / monthly_net * 100) if monthly_net > 0 else 0

    cat_data.append({
        "key":        key,
        "label":      label,
        "color":      color,
        "pct":        eff_pct,
        "pinned":     key in pinned,
        "weekly_base": base_weekly,
        "weekly":     weekly_amt,
        "monthly":    monthly_amt,
        "annual":     annual_amt,
    })

savings_weekly = next(d["weekly"] for d in cat_data if d["key"] == "savings")
savings_annual = savings_weekly * 52
debt_weekly    = next(d["weekly"] for d in cat_data if d["key"] == "debt")

goal_months = None
if goal_amount > 0:
    remaining = max(0, goal_amount - goal_current)
    if remaining == 0:
        goal_months = 0
    elif savings_annual > 0:
        goal_months = math.ceil(remaining / (savings_annual / 12))

monthly_debt_payment = debt_weekly * 52 / 12
debt_months   = None
debt_interest = None
amort_balances    = []
amort_months_list = []

if debt_balance > 0 and monthly_debt_payment > 0:
    monthly_rate = debt_rate / 100 / 12
    if monthly_rate == 0:
        debt_months   = math.ceil(debt_balance / monthly_debt_payment)
        debt_interest = 0.0
    elif monthly_debt_payment <= monthly_rate * debt_balance:
        debt_months   = float("inf")
        debt_interest = float("inf")
    else:
        raw = -math.log(1 - (monthly_rate * debt_balance) / monthly_debt_payment) / math.log(1 + monthly_rate)
        debt_months   = math.ceil(raw)
        debt_interest = debt_months * monthly_debt_payment - debt_balance

    if debt_months not in (None, float("inf")):
        bal = float(debt_balance)
        for m in range(min(int(debt_months) + 1, 601)):
            amort_balances.append(bal)
            amort_months_list.append(m)
            interest_charge = bal * (debt_rate / 100 / 12)
            bal = max(0.0, bal - (monthly_debt_payment - interest_charge))

# ── Emergency fund calc ───────────────────────────────────────────────────────
monthly_expenses = max(1.0, monthly_net - savings_annual / 12)
ef_months_covered = ef_savings / monthly_expenses

# ── Net worth calc ────────────────────────────────────────────────────────────
nw_total_assets      = nw_checking + nw_investments + nw_retirement_a + nw_home + nw_vehicle + nw_other_asset
nw_total_liabilities = nw_mortgage + nw_student + nw_car_loan + nw_credit + nw_other_liab
net_worth            = nw_total_assets - nw_total_liabilities

# ── Retirement calc ───────────────────────────────────────────────────────────
ret_years = max(0, ret_target_age - ret_age)
_r = ret_return_rate / 100
if ret_years > 0:
    if _r > 0:
        ret_fv = ret_current_ret * (1 + _r) ** ret_years + savings_annual * (((1 + _r) ** ret_years - 1) / _r)
    else:
        ret_fv = ret_current_ret + savings_annual * ret_years
else:
    ret_fv = float(ret_current_ret)
# Real (inflation-adjusted) value
_ri = (1 + _r) / (1 + ret_inflation / 100) - 1
if ret_years > 0 and _ri > 0:
    ret_fv_real = ret_current_ret * (1 + _ri) ** ret_years + savings_annual * (((1 + _ri) ** ret_years - 1) / _ri)
elif ret_years > 0:
    ret_fv_real = ret_current_ret + savings_annual * ret_years
else:
    ret_fv_real = float(ret_current_ret)
ret_monthly_4pct      = ret_fv * 0.04 / 12        # nominal
ret_monthly_4pct_real = ret_fv_real * 0.04 / 12   # inflation-adjusted

# Build retirement growth curve (nominal)
ret_curve_years  = list(range(ret_years + 1))
ret_curve_values = []
for _y in ret_curve_years:
    if _r > 0:
        _v = ret_current_ret * (1 + _r) ** _y + savings_annual * (((1 + _r) ** _y - 1) / _r)
    else:
        _v = ret_current_ret + savings_annual * _y
    ret_curve_values.append(_v)

# ── Financial Archetype ───────────────────────────────────────────────────────
savings_pct_val      = next(d["pct"] for d in cat_data if d["key"] == "savings")
housing_pct_val      = next(d["pct"] for d in cat_data if d["key"] == "housing")
entertainment_pct_val = next((d["pct"] for d in cat_data if d["key"] == "entertainment"), 0)
debt_income_ratio    = (monthly_debt_payment / monthly_net * 100) if monthly_net > 0 else 0

if savings_pct_val >= 20 and debt_income_ratio < 15:
    archetype       = "The Builder"
    archetype_desc  = "You prioritize long-term wealth. Your savings rate puts you on track to retire well ahead of most Americans."
    archetype_color = "#4BB88A"
    archetype_icon  = "🏗"
elif housing_pct_val >= 36:
    archetype       = "The Urban Dweller"
    archetype_desc  = "A large share of income goes to housing — typical of high-COL cities. Reducing this one category would unlock significant cash flow."
    archetype_color = "#5090C4"
    archetype_icon  = "🏙"
elif entertainment_pct_val >= 15 or (savings_pct_val < 8 and debt_income_ratio < 8):
    archetype       = "The Experiencer"
    archetype_desc  = "You spend richly on the present. There's joy in that — just make sure future-you has a seat at the table too."
    archetype_color = "#C4A35A"
    archetype_icon  = "✦"
elif ef_months_covered >= 6 and savings_pct_val >= 10:
    archetype       = "The Security-Seeker"
    archetype_desc  = "You've built a solid safety net and keep it well-stocked. Stability is your financial superpower."
    archetype_color = "#8B6FD4"
    archetype_icon  = "🛡"
elif debt_income_ratio >= 20:
    archetype       = "The Overextended"
    archetype_desc  = "Debt is claiming a significant share of your income. Paying it down aggressively now will unlock major breathing room within a few years."
    archetype_color = "#DC6060"
    archetype_icon  = "⚡"
else:
    archetype       = "The Balancer"
    archetype_desc  = "You're managing a healthy spread across all categories — not chasing any single extreme, just building steadily across the board."
    archetype_color = "#4BB88A"
    archetype_icon  = "⚖"

# ── Budget Health Score ───────────────────────────────────────────────────────
# Savings rate (0–25 pts)
if savings_pct_val >= 20:    _sc_sav = 25
elif savings_pct_val >= 15:  _sc_sav = 20
elif savings_pct_val >= 10:  _sc_sav = 15
elif savings_pct_val >= 5:   _sc_sav = 8
else:                        _sc_sav = 2

# Emergency fund (0–25 pts)
if ef_months_covered >= 6:    _sc_ef = 25
elif ef_months_covered >= 3:  _sc_ef = 18
elif ef_months_covered >= 1:  _sc_ef = 10
else:                         _sc_ef = 0

# Debt-to-income (0–25 pts)
if debt_income_ratio == 0:      _sc_debt = 25
elif debt_income_ratio < 10:    _sc_debt = 20
elif debt_income_ratio < 20:    _sc_debt = 13
elif debt_income_ratio < 30:    _sc_debt = 6
else:                           _sc_debt = 0

# Housing affordability (0–25 pts)
if housing_pct_val <= 25:    _sc_house = 25
elif housing_pct_val <= 30:  _sc_house = 20
elif housing_pct_val <= 35:  _sc_house = 12
else:                        _sc_house = 5

health_score = _sc_sav + _sc_ef + _sc_debt + _sc_house
if health_score >= 85:    health_grade, health_color = "A", "#4BB88A"
elif health_score >= 70:  health_grade, health_color = "B", "#7ec8a0"
elif health_score >= 55:  health_grade, health_color = "C", "#C4A35A"
elif health_score >= 40:  health_grade, health_color = "D", "#DC8050"
else:                     health_grade, health_color = "F", "#DC6060"

# ── Salary Equivalency ────────────────────────────────────────────────────────
# For each comparison city, estimate what gross salary you'd need to maintain
# the same lifestyle (same net spending power after COL adjustment).
_EQUIV_CITIES = [
    "New York City, NY", "San Francisco, CA", "Los Angeles, CA", "Seattle, WA",
    "Austin, TX", "Chicago, IL", "Miami, FL", "Denver, CO",
    "Nashville, TN", "Phoenix, AZ", "Atlanta, GA", "Dallas, TX",
]
_eff_tax_rate = (total_tax / gross) if gross > 0 else 0.28
_col_affected_share = sum(d["pct"] for d in cat_data if d["key"] in COL_AFFECTED) / 100

equiv_data = []
for _ecity in _EQUIV_CITIES:
    if _ecity == location:
        continue
    _ei = COL_DATA.get(_ecity, {})
    if not _ei:
        continue
    _dest_col = _ei["index"]
    _curr_col = col_idx if col_idx > 0 else 100
    # Scale only COL-affected portion of spending; back-solve for gross
    _dest_net_needed = net * (_col_affected_share * (_dest_col / _curr_col) + (1 - _col_affected_share))
    _dest_gross = _dest_net_needed / max(0.01, 1 - _eff_tax_rate)
    _delta = _dest_gross - gross
    equiv_data.append({
        "city":  _ecity,
        "col":   _dest_col,
        "gross": _dest_gross,
        "delta": _delta,
    })
equiv_data.sort(key=lambda x: x["gross"])

# ── Header ────────────────────────────────────────────────────────────────────
tier_css = TIERS[tier]["css"]
s_name   = st.session_state.get("s_name", "")
headline = f"{s_name}'s financial life at" if s_name else "Your financial life at"

st.markdown(f"""
<div style="padding:36px 0 28px;border-bottom:1px solid var(--border);margin-bottom:32px">
  <div style="font-size:10px;font-weight:700;letter-spacing:0.16em;text-transform:uppercase;color:var(--t3);margin-bottom:18px">Lifestyle Budget Simulator</div>
  <div style="display:flex;align-items:flex-end;justify-content:space-between;flex-wrap:wrap;gap:16px">
    <div>
      <div style="font-size:13px;color:var(--t2);font-weight:400;margin-bottom:6px">{headline}</div>
      <div style="font-family:'DM Serif Display',serif;font-size:42px;color:var(--t1);letter-spacing:-0.025em;line-height:1">
        <span style="color:var(--gold)">${gross:,.0f}</span><span style="font-size:18px;color:var(--t3);font-family:'Inter',sans-serif;font-weight:300;margin-left:6px">/ yr gross</span>
      </div>
    </div>
    <div style="text-align:right;padding-bottom:4px">
      <div style="font-size:11px;color:var(--t3);font-weight:600;letter-spacing:.1em;text-transform:uppercase;margin-bottom:4px">Take-home</div>
      <div style="font-family:'DM Serif Display',serif;font-size:28px;color:var(--green);letter-spacing:-0.02em">${net:,.0f}<span style="font-size:14px;color:var(--t3);font-family:'Inter',sans-serif;font-weight:300;margin-left:5px">/ yr</span></div>
    </div>
  </div>
  <div style="margin-top:16px;display:flex;gap:8px;flex-wrap:wrap;align-items:center">
    <span class="location-tag">📍 {location} &nbsp;·&nbsp; COL {col_idx}</span>
    <span class="tier-tag {tier_css}">{tier}</span>
    <span class="archetype-pill" style="color:{archetype_color};background:{archetype_color}18;border-color:{archetype_color}35">{archetype_icon} {archetype}</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Top metrics ───────────────────────────────────────────────────────────────
c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    st.metric("Gross income", f"${gross:,.0f}", help="Before taxes")
with c2:
    st.metric("Federal tax", f"${federal_tax:,.0f}", delta=f"-{fed_rate}% + FICA", delta_color="inverse")
with c3:
    if state_abbr in NO_INCOME_TAX_STATES:
        st.metric(f"{state_abbr} state tax", "$0", delta="No state income tax", delta_color="off")
    elif state_abbr:
        st.metric(f"{state_abbr} state tax", f"${state_tax_amt:,.0f}", delta=f"-{st_rate}% rate", delta_color="inverse")
    else:
        st.metric("State tax", "$0", delta="Select a city for state tax", delta_color="off")
with c4:
    st.metric("Take-home (annual)", f"${net:,.0f}", delta=f"-{total_tax_rate}% total", delta_color="inverse")
with c5:
    st.metric("Take-home (monthly)", f"${monthly_net:,.0f}", help="Annual take-home ÷ 12")

st.divider()

# ── Budget Health Score ───────────────────────────────────────────────────────
st.markdown('<div class="section-head">Budget health score</div>', unsafe_allow_html=True)

_hs_cols = st.columns([1, 2.2], gap="large")
with _hs_cols[0]:
    st.markdown(f"""
<div class="health-card" style="text-align:center">
  <div class="health-score-ring" style="color:{health_color}">{health_score}</div>
  <div style="font-size:36px;font-weight:800;color:{health_color};line-height:1;margin-top:2px">{health_grade}</div>
  <div style="font-size:10.5px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:var(--t3);margin-top:10px">out of 100</div>
  <div style="font-size:12px;color:var(--t2);margin-top:10px;line-height:1.5">{archetype_icon} {archetype}<br><span style="font-size:11px">{archetype_desc}</span></div>
</div>""", unsafe_allow_html=True)

with _hs_cols[1]:
    def _score_bar(label, score, max_score, color):
        pct = round(score / max_score * 100)
        return f"""
<div style="margin-bottom:14px">
  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:5px">
    <div class="health-sub-label">{label}</div>
    <div style="font-size:11px;font-weight:700;color:{color}">{score}/{max_score}</div>
  </div>
  <div class="health-sub-bar"><div style="height:5px;width:{pct}%;background:{color};border-radius:4px"></div></div>
</div>"""

    st.markdown(
        _score_bar("Savings rate", _sc_sav, 25, "#4BB88A") +
        _score_bar("Emergency fund", _sc_ef, 25, "#8B6FD4") +
        _score_bar("Debt load", _sc_debt, 25, "#5090C4") +
        _score_bar("Housing cost", _sc_house, 25, "#C4A35A"),
        unsafe_allow_html=True
    )
    _tips = []
    if _sc_sav < 15:    _tips.append(f"Boost savings above 15% of take-home to unlock the full score.")
    if _sc_ef < 18:     _tips.append(f"Build your emergency fund to 3–6 months of expenses.")
    if _sc_debt < 20:   _tips.append(f"Paying down high-interest debt would quickly improve your score.")
    if _sc_house >= 12: pass
    else:               _tips.append(f"Housing above 35% of income limits flexibility — consider if this is right for your goals.")
    if _tips:
        for _tip in _tips[:2]:
            st.markdown(f'<div class="insight-box" style="margin-bottom:8px;font-size:12px">💡 {_tip}</div>', unsafe_allow_html=True)

st.divider()

# ── View toggle ───────────────────────────────────────────────────────────────
tog_col, _ = st.columns([1, 3])
with tog_col:
    view_mode = st.radio("View", ["Weekly", "Monthly"], horizontal=True, label_visibility="collapsed")

# ── Two-column layout ─────────────────────────────────────────────────────────
left, right = st.columns([1.05, 1], gap="large")

with left:
    period_label = "monthly" if view_mode == "Monthly" else "weekly"
    st.markdown(f'<div class="section-head">{view_mode} budget breakdown</div>', unsafe_allow_html=True)

    rows_html = ""
    for d in cat_data:
        primary_amt = d["monthly"] if view_mode == "Monthly" else d["weekly"]
        pin_badge = (' <span style="font-size:9px;background:rgba(80,144,196,.12);color:#5090C4;'
                     'border:1px solid rgba(80,144,196,.25);border-radius:4px;padding:1px 5px;'
                     'vertical-align:middle;margin-left:4px">pinned</span>') if d["pinned"] else ""
        rows_html += (
            f'<div class="cat-row" style="border-left-color:{d["color"]}">'
            f'<div class="cat-row-name">{d["label"]}{pin_badge}</div>'
            f'<div class="cat-row-bar-wrap">'
            f'<div class="cat-row-bar-fill" style="width:{d["pct"]}%;background:{d["color"]}40"></div>'
            f'</div>'
            f'<div class="cat-row-amount">${primary_amt:,.0f}</div>'
            f'<div class="cat-row-meta">{d["pct"]}%</div>'
            f'</div>'
        )
    st.markdown(rows_html, unsafe_allow_html=True)

with right:
    st.markdown('<div class="section-head">Allocation</div>', unsafe_allow_html=True)

    fig = go.Figure(go.Pie(
        labels=[d["label"] for d in cat_data],
        values=[d["pct"] for d in cat_data],
        hole=0.62,
        marker=dict(colors=[d["color"] for d in cat_data], line=dict(color="#0a0a0f", width=2)),
        textinfo="none",
        hovertemplate="<b>%{label}</b><br>%{value}% — $%{customdata:,.0f}/" + period_label + "<extra></extra>",
        customdata=[d["monthly"] if view_mode == "Monthly" else d["weekly"] for d in cat_data],
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=0, b=0, l=0, r=0),
        height=280,
        showlegend=True,
        legend=dict(font=dict(color="rgba(238,240,255,0.6)", size=11, family="Inter"),
                    bgcolor="rgba(0,0,0,0)", bordercolor="rgba(0,0,0,0)"),
        annotations=[dict(
            text=f"<b>${monthly_net:,.0f}</b><br><span style='font-size:11px'>/month</span>" if view_mode == "Monthly" else f"<b>${weekly_net:,.0f}</b><br><span style='font-size:11px'>/week</span>",
            x=0.5, y=0.5, showarrow=False,
            font=dict(color="#EEF0FF", size=16, family="Inter"),
        )],
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div class="section-head" style="margin-top:8px">Cost of living impact</div>', unsafe_allow_html=True)

    affected = [d for d in cat_data if d["key"] in COL_AFFECTED]
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(
        name="National avg",
        x=[d["label"] for d in affected],
        y=[round(d["weekly_base"] * 52 / 12) if view_mode == "Monthly" else round(d["weekly_base"]) for d in affected],
        marker_color="#1c1c2e", marker_line_color="#2e2e44", marker_line_width=1,
    ))
    fig2.add_trace(go.Bar(
        name=location,
        x=[d["label"] for d in affected],
        y=[round(d["monthly"]) if view_mode == "Monthly" else round(d["weekly"]) for d in affected],
        marker_color=[d["color"] for d in affected],
    ))
    fig2.update_layout(
        barmode="group",
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        height=200, margin=dict(t=10, b=0, l=0, r=0),
        font=dict(color="rgba(238,240,255,0.7)", size=11, family="Inter"),
        xaxis=dict(gridcolor="#111526", linecolor="#1C2340"),
        yaxis=dict(gridcolor="#111526", linecolor="#1C2340", tickprefix="$"),
        legend=dict(font=dict(color="rgba(238,240,255,0.5)", size=10), bgcolor="rgba(0,0,0,0)"),
    )
    st.plotly_chart(fig2, use_container_width=True)


# ── Insights ──────────────────────────────────────────────────────────────────
st.divider()
st.markdown('<div class="section-head">Insights for your situation</div>', unsafe_allow_html=True)

housing_weekly = next(d["weekly"] for d in cat_data if d["key"] == "housing")
insights = []

if col_idx > 130:
    insights.append(f"🏙️ <b>{location}</b> has a cost of living {col_idx - 100}% above the national average. Your housing budget of <b>${housing_weekly:,.0f}/wk</b> may feel tight — consider a longer commute or roommates to stay within budget.")
elif col_idx < 90:
    insights.append(f"🌱 <b>{location}</b> is {100 - col_idx}% below the national average cost of living. Your dollar stretches further here — consider redirecting savings toward investing.")

if state_abbr and state_abbr not in NO_INCOME_TAX_STATES and state_tax_amt > 0:
    insights.append(f"🏛️ <b>{state_abbr} state income tax</b> adds <b>${state_tax_amt:,.0f}/yr</b> ({st_rate}% of gross) on top of your federal burden. Your total tax rate is {total_tax_rate}%.")
elif state_abbr in NO_INCOME_TAX_STATES:
    insights.append(f"✅ <b>{state_abbr} has no state income tax</b> — you keep more of every paycheck compared to most states.")

if savings_annual < 3000 and gross > 30000:
    insights.append(f"⚠️ Your current savings allocation is <b>${savings_annual:,.0f}/yr</b>. Financial planners typically recommend 3–6 months of expenses (~${weekly_net * 12:,.0f}) as an emergency fund baseline.")
else:
    months_to_efund = max(1, round(weekly_net * 26 / savings_annual)) if savings_annual > 0 else None
    efund_str = f" in about {months_to_efund} year(s)" if months_to_efund else ""
    insights.append(f"✅ You're on track to save <b>${savings_annual:,.0f}/yr</b>. At this rate, you'd have a 6-month emergency fund (~${weekly_net * 26:,.0f}){efund_str}.")

if debt_weekly * 52 > net * 0.20:
    insights.append(f"💳 Debt repayment takes up more than 20% of your take-home pay. Consider the avalanche method (highest interest first) to minimize total interest paid.")

if gross < 40000:
    insights.append(f"📌 At your income level, the <b>Earned Income Tax Credit (EITC)</b> may apply to you — consult a tax professional to see if you qualify for additional refunds.")

if tier == "✨ Lavish":
    insights.append(f"✨ <b>Lavish mode</b> is active. Lifestyle spending is elevated — keep an eye on your savings rate to ensure long-term financial health.")
elif tier == "🌿 Frugal":
    insights.append(f"🌿 <b>Frugal mode</b> is active. Your savings rate is boosted and discretionary spending is trimmed. Great for building wealth or paying off debt fast.")

ic1, ic2 = st.columns(2)
for i, insight in enumerate(insights):
    col = ic1 if i % 2 == 0 else ic2
    col.markdown(f'<div class="insight-box">{insight}</div>', unsafe_allow_html=True)


# ── Emergency Fund Status ─────────────────────────────────────────────────────
st.divider()
st.markdown('<div class="section-head">Emergency fund status</div>', unsafe_allow_html=True)

ef_left, ef_right = st.columns([1, 1.4], gap="large")
with ef_left:
    if ef_months_covered >= 6:
        ef_color, ef_status, ef_label_color = "#7ec8a0", "You're covered", "#7ec8a0"
    elif ef_months_covered >= 3:
        ef_color, ef_status, ef_label_color = "#c8b07e", "Getting there", "#c8b07e"
    else:
        ef_color, ef_status, ef_label_color = "#d48888", "Build this up", "#d48888"

    ef_bar_pct = min(100, round(ef_months_covered / 6 * 100))
    st.markdown(f"""
<div class="nw-card">
  <div style="font-size:10px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:var(--t2);margin-bottom:8px">Months of expenses covered</div>
  <div style="font-family:'DM Serif Display',serif;font-size:48px;color:{ef_label_color};line-height:1;letter-spacing:-0.02em">{ef_months_covered:.1f}</div>
  <div style="font-size:12px;color:{ef_label_color};font-weight:500;margin-top:6px">{ef_status}</div>
  <div class="ef-bar-wrap"><div style="height:10px;background:{ef_color};border-radius:6px;width:{ef_bar_pct}%"></div></div>
  <div style="display:flex;justify-content:space-between;font-size:11px;color:var(--t2)"><span>0 mo</span><span style="color:{ef_label_color}">3 mo</span><span>6 mo+</span></div>
  <div style="margin-top:18px;display:grid;grid-template-columns:1fr 1fr;gap:10px">
    <div>
      <div style="font-size:16px;font-family:'DM Serif Display',serif;color:var(--t1)">${ef_savings:,.0f}</div>
      <div style="font-size:10px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--t2);margin-top:2px">Liquid savings</div>
    </div>
    <div>
      <div style="font-size:16px;font-family:'DM Serif Display',serif;color:var(--t1)">${monthly_expenses:,.0f}</div>
      <div style="font-size:10px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--t2);margin-top:2px">Monthly expenses</div>
    </div>
  </div>
</div>""", unsafe_allow_html=True)

with ef_right:
    ef_target_3 = monthly_expenses * 3
    ef_target_6 = monthly_expenses * 6
    ef_target_12 = monthly_expenses * 12
    months_to_3  = max(0, math.ceil((ef_target_3  - ef_savings) / (savings_annual / 12))) if savings_annual > 0 else None
    months_to_6  = max(0, math.ceil((ef_target_6  - ef_savings) / (savings_annual / 12))) if savings_annual > 0 else None
    months_to_12 = max(0, math.ceil((ef_target_12 - ef_savings) / (savings_annual / 12))) if savings_annual > 0 else None

    def _mo_str(m):
        if m is None: return "No savings allocated"
        if m == 0:    return "Already reached"
        y, mo = divmod(m, 12)
        p = []
        if y:  p.append(f"{y} yr{'s' if y!=1 else ''}")
        if mo: p.append(f"{mo} mo")
        return " ".join(p) or "< 1 month"

    st.markdown(f"""
<div class="nw-card">
  <div class="wi-col-head">Time to reach each milestone</div>
  <div style="display:grid;gap:12px">
    <div style="display:flex;justify-content:space-between;align-items:center">
      <div>
        <div style="font-size:13px;font-weight:600;color:var(--t1)">3-month fund</div>
        <div style="font-size:11px;color:var(--t2);margin-top:2px">${ef_target_3:,.0f} target</div>
      </div>
      <div style="text-align:right">
        <div style="font-size:14px;font-weight:600;color:{"#7ec8a0" if ef_savings >= ef_target_3 else "#c8b07e"}">{_mo_str(months_to_3)}</div>
      </div>
    </div>
    <div style="display:flex;justify-content:space-between;align-items:center">
      <div>
        <div style="font-size:13px;font-weight:600;color:var(--t1)">6-month fund</div>
        <div style="font-size:11px;color:var(--t2);margin-top:2px">${ef_target_6:,.0f} target</div>
      </div>
      <div style="text-align:right">
        <div style="font-size:14px;font-weight:600;color:{"#7ec8a0" if ef_savings >= ef_target_6 else "#c8b07e"}">{_mo_str(months_to_6)}</div>
      </div>
    </div>
    <div style="display:flex;justify-content:space-between;align-items:center">
      <div>
        <div style="font-size:13px;font-weight:600;color:var(--t1)">12-month fund</div>
        <div style="font-size:11px;color:var(--t2);margin-top:2px">${ef_target_12:,.0f} target</div>
      </div>
      <div style="text-align:right">
        <div style="font-size:14px;font-weight:600;color:{"#7ec8a0" if ef_savings >= ef_target_12 else "#c8b07e"}">{_mo_str(months_to_12)}</div>
      </div>
    </div>
  </div>
  <div style="margin-top:20px;background:var(--surface);border:1px solid rgba(200,169,110,.15);border-left:3px solid #c8a96e;border-radius:8px;padding:12px 14px;font-size:12px;color:var(--t1);line-height:1.6">
    Monthly expenses = take-home minus savings allocation (${monthly_net:,.0f} &minus; ${savings_annual/12:,.0f} = ${monthly_expenses:,.0f}/mo).
    Adjust your savings in the sidebar to see timelines update.
  </div>
</div>""", unsafe_allow_html=True)


# ── Subscription Audit ────────────────────────────────────────────────────────
st.divider()
st.markdown('<div class="section-head">Subscription audit</div>', unsafe_allow_html=True)

if not sub_checked:
    st.info("Open the **Subscriptions** expander in the sidebar and check off your active subscriptions.")
else:
    ent_annual   = next(d["annual"] for d in cat_data if d["key"] == "entertainment")
    other_annual = next(d["annual"] for d in cat_data if d["key"] == "other")
    sub_annual   = sub_total * 12
    budget_pool  = ent_annual + other_annual

    sa_left, sa_right = st.columns([1, 1.2], gap="large")

    with sa_left:
        over = sub_annual > budget_pool
        color = "#d48888" if over else "#7ec8a0"
        rows_html = "".join(
            f'<div class="sub-row"><span style="color:var(--t-75)">{n}</span><span style="color:var(--t1);font-weight:500">${p:.2f}/mo</span></div>'
            for n, p in sub_checked
        )
        st.markdown(f"""
<div class="nw-card">
  <div class="wi-col-head">Your subscriptions</div>
  {rows_html}
  <div style="display:flex;justify-content:space-between;padding-top:10px;font-size:13px;font-weight:600">
    <span style="color:var(--t2)">Total monthly</span>
    <span style="color:{color}">${sub_total:,.2f}/mo</span>
  </div>
  <div style="display:flex;justify-content:space-between;padding-top:4px;font-size:12px">
    <span style="color:var(--t2)">Total annual</span>
    <span style="color:{color}">${sub_annual:,.0f}/yr</span>
  </div>
</div>""", unsafe_allow_html=True)

    with sa_right:
        used_pct  = min(100, round(sub_annual / budget_pool * 100)) if budget_pool > 0 else 100
        remain    = max(0, budget_pool - sub_annual)
        bar_color = "#d48888" if over else "#7ec8c8"
        st.markdown(f"""
<div class="nw-card">
  <div class="wi-col-head">vs. your entertainment + other budget</div>
  <div style="font-family:'DM Serif Display',serif;font-size:36px;color:{bar_color};line-height:1;letter-spacing:-0.02em">{used_pct}%</div>
  <div style="font-size:12px;color:var(--t2);margin-top:4px;margin-bottom:12px">of entertainment + other budget used by subscriptions</div>
  <div class="ef-bar-wrap" style="height:8px">
    <div style="height:8px;background:{bar_color};border-radius:6px;width:{used_pct}%"></div>
  </div>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:14px">
    <div>
      <div style="font-size:15px;font-family:'DM Serif Display',serif;color:var(--t1)">${budget_pool:,.0f}</div>
      <div style="font-size:10px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--t2);margin-top:2px">Annual budget</div>
    </div>
    <div>
      <div style="font-size:15px;font-family:'DM Serif Display',serif;color:{"#d48888" if over else "#7ec8a0"}">${remain:,.0f} {"over" if over else "left"}</div>
      <div style="font-size:10px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--t2);margin-top:2px">Remaining</div>
    </div>
  </div>
  {"<div style='margin-top:14px;background:rgba(200,80,80,.08);border:1px solid rgba(200,80,80,.2);border-radius:8px;padding:10px 14px;font-size:12px;color:#d48888'>Subscriptions exceed your entertainment + other budget by <b>${abs(sub_annual - budget_pool):,.0f}/yr</b>. Consider trimming or raising your entertainment allocation.</div>" if over else ""}
</div>""", unsafe_allow_html=True)


# ── Savings Goal Tracker ──────────────────────────────────────────────────────
st.divider()
st.markdown('<div class="section-head">Savings goal tracker</div>', unsafe_allow_html=True)

if savings_annual <= 0:
    st.warning("Your current savings allocation is $0. Adjust your framework or tier to see a goal timeline.")
elif goal_amount <= 0:
    st.info("Open the **Savings goal** expander in the sidebar to set a target.")
else:
    sg_left, sg_right = st.columns([1, 1.2], gap="large")
    remaining = max(0, goal_amount - goal_current)
    progress_pct = min(100, round(goal_current / goal_amount * 100)) if goal_amount else 0

    with sg_left:
        if goal_months == 0:
            st.markdown(f"""
<div class="goal-card">
  <div style="font-size:13px;color:#5dbe5d;margin-bottom:8px">Goal already reached!</div>
  <div class="goal-big">${goal_amount:,.0f}</div>
  <div class="goal-label">{goal_name}</div>
</div>""", unsafe_allow_html=True)
        else:
            yrs, mos = divmod(int(goal_months), 12)
            parts = []
            if yrs: parts.append(f"{yrs} yr{'s' if yrs != 1 else ''}")
            if mos: parts.append(f"{mos} mo")
            timeline_str = " ".join(parts) or "< 1 month"
            st.markdown(f"""
<div class="goal-card">
  <div style="font-size:10px;font-weight:700;color:var(--t1);text-transform:uppercase;letter-spacing:.1em;margin-bottom:8px;opacity:.45">Time to reach goal</div>
  <div class="goal-big">{timeline_str}</div>
  <div class="goal-label">{goal_name} · ${goal_amount:,.0f} target</div>
  <div style="margin-top:18px;display:grid;grid-template-columns:1fr 1fr;gap:12px">
    <div>
      <div style="font-size:20px;color:var(--t1);font-family:'DM Serif Display',serif">${goal_current:,.0f}</div>
      <div class="goal-label">Already saved</div>
    </div>
    <div>
      <div style="font-size:20px;color:var(--t1);font-family:'DM Serif Display',serif">${remaining:,.0f}</div>
      <div class="goal-label">Remaining</div>
    </div>
  </div>
  <div style="margin-top:18px">
    <div style="font-size:10px;font-weight:700;color:var(--t1);margin-bottom:6px;text-transform:uppercase;letter-spacing:.1em;opacity:.45">Progress</div>
    <div style="height:3px;background:var(--border);border-radius:2px">
      <div style="height:3px;background:#b09ad8;border-radius:2px;width:{progress_pct}%"></div>
    </div>
    <div style="display:flex;justify-content:space-between;margin-top:6px;font-size:11px;color:var(--t1);opacity:.5">
      <span>{progress_pct}% saved</span>
      <span>${savings_annual:,.0f}/yr</span>
    </div>
  </div>
</div>""", unsafe_allow_html=True)

    with sg_right:
        months_to_show = min((goal_months or 120) + 6, 360)
        m_list   = list(range(months_to_show + 1))
        bal_list = [min(goal_current + (savings_annual / 12) * m, goal_amount * 1.05) for m in m_list]

        fig_goal = go.Figure()
        fig_goal.add_trace(go.Scatter(
            x=m_list, y=bal_list, mode="lines",
            line=dict(color="#a07ec8", width=2),
            fill="tozeroy", fillcolor="rgba(160,126,200,0.08)",
            hovertemplate="Month %{x}: $%{y:,.0f}<extra></extra>",
        ))
        fig_goal.add_hline(y=goal_amount, line=dict(color="#c8a96e", width=1, dash="dash"),
                           annotation_text=f"${goal_amount:,.0f} goal",
                           annotation_font=dict(color="#c8a96e", size=10))
        if goal_months and goal_months <= months_to_show:
            fig_goal.add_vline(x=goal_months, line=dict(color="#5dbe5d", width=1, dash="dot"))
        fig_goal.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            height=240, margin=dict(t=10, b=0, l=0, r=10),
            font=dict(color="#ffffff", size=10, family="DM Sans"),
            xaxis=dict(gridcolor="#14141f", linecolor="#1c1c2e", title="Month"),
            yaxis=dict(gridcolor="#14141f", linecolor="#1c1c2e", tickprefix="$"),
            showlegend=False,
        )
        st.plotly_chart(fig_goal, use_container_width=True)


# ── Debt Payoff Calculator ────────────────────────────────────────────────────
st.divider()
st.markdown('<div class="section-head">Debt payoff calculator</div>', unsafe_allow_html=True)

if debt_balance == 0:
    st.info("Open the **Debt payoff** expander in the sidebar and enter your balance to see a payoff timeline.")
elif monthly_debt_payment <= 0:
    st.warning("Your debt repayment allocation is $0. Increase the debt slice in your framework to calculate a payoff timeline.")
else:
    dp_left, dp_right = st.columns([1, 1.2], gap="large")

    with dp_left:
        if debt_months == float("inf"):
            monthly_interest_charge = debt_balance * (debt_rate / 100 / 12)
            st.markdown(f"""
<div class="goal-card">
  <div style="font-size:13px;color:#d48888;margin-bottom:10px;font-weight:600">Payment doesn't cover interest</div>
  <div style="font-size:13px;color:var(--t1);line-height:1.7">
    At <b style="color:var(--t1)">{debt_rate:.1f}% APR</b>, your monthly interest charge is
    <b style="color:var(--t1)">${monthly_interest_charge:,.0f}</b>, but your debt payment is only
    <b style="color:var(--t1)">${monthly_debt_payment:,.0f}/mo</b>.<br><br>
    Increase your debt repayment allocation or choose a framework with a higher debt slice.
  </div>
</div>""", unsafe_allow_html=True)
        else:
            yrs, mos = divmod(int(debt_months), 12)
            parts = []
            if yrs: parts.append(f"{yrs} yr{'s' if yrs != 1 else ''}")
            if mos: parts.append(f"{mos} mo")
            timeline_str  = " ".join(parts) or "< 1 month"
            interest_pct  = min(100, round(debt_interest / (debt_balance + debt_interest) * 100)) if (debt_balance + debt_interest) > 0 else 0

            st.markdown(f"""
<div class="goal-card">
  <div style="font-size:11px;font-weight:600;color:var(--t1);text-transform:uppercase;letter-spacing:.08em;margin-bottom:6px">Payoff timeline</div>
  <div class="debt-big">{timeline_str}</div>
  <div class="goal-label">${debt_balance:,.0f} balance · {debt_rate:.1f}% APR</div>
  <div style="margin-top:18px;display:grid;grid-template-columns:1fr 1fr;gap:12px">
    <div>
      <div style="font-size:20px;color:var(--t1);font-family:'DM Serif Display',serif">${monthly_debt_payment:,.0f}</div>
      <div class="goal-label">Monthly payment</div>
    </div>
    <div>
      <div style="font-size:20px;color:#d48888;font-family:'DM Serif Display',serif">${debt_interest:,.0f}</div>
      <div class="goal-label">Total interest</div>
    </div>
  </div>
  <div style="margin-top:18px">
    <div style="font-size:11px;font-weight:600;color:var(--t1);margin-bottom:6px;text-transform:uppercase;letter-spacing:.08em">Interest as % of total paid</div>
    <div style="height:3px;background:var(--border);border-radius:2px">
      <div style="height:3px;background:#d48888;border-radius:2px;width:{interest_pct}%"></div>
    </div>
    <div style="font-size:11px;color:var(--t1);margin-top:6px;opacity:.5">{interest_pct}% of total payments go toward interest</div>
  </div>
</div>""", unsafe_allow_html=True)

    with dp_right:
        if amort_balances:
            fig_debt = go.Figure()
            fig_debt.add_trace(go.Scatter(
                x=amort_months_list, y=amort_balances, mode="lines",
                line=dict(color="#c87e7e", width=2),
                fill="tozeroy", fillcolor="rgba(200,126,126,0.08)",
                hovertemplate="Month %{x}: $%{y:,.0f} remaining<extra></extra>",
            ))
            fig_debt.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                height=240, margin=dict(t=10, b=0, l=0, r=10),
                font=dict(color="#ffffff", size=10, family="DM Sans"),
                xaxis=dict(gridcolor="#14141f", linecolor="#1c1c2e", title="Month"),
                yaxis=dict(gridcolor="#14141f", linecolor="#1c1c2e", tickprefix="$", title="Remaining balance"),
                showlegend=False,
            )
            st.plotly_chart(fig_debt, use_container_width=True)


# ── Income Projections ────────────────────────────────────────────────────────
st.divider()
st.markdown('<div class="section-head">Income projections</div>', unsafe_allow_html=True)

if not promotions:
    st.info("Open the **Income projections** expander in the sidebar to add expected raises.")
else:
    # Build step timeline: chain promotions so % raises compound off the previous salary
    max_month = max(p["months"] for p in promotions) + 18
    max_month = min(max_month, 240)

    # Compute salary at each promotion, chaining % raises
    steps = []   # list of (month, gross_salary)
    cur = float(gross)
    for p in promotions:
        if p["type"] == "% raise":
            cur = cur * (1 + p["value"] / 100)
        else:
            cur = float(p["value"])
        steps.append((p["months"], cur, p["label"]))

    # Build month-by-month gross and net arrays for the chart
    timeline_months = list(range(max_month + 1))
    timeline_gross  = []
    timeline_net    = []
    for m in timeline_months:
        g = float(gross)
        for month, new_g, _ in steps:
            if m >= month:
                g = new_g
        timeline_gross.append(g)
        timeline_net.append(g - calc_federal_tax(g) - calc_state_tax(g, state_abbr))

    # ── Chart ──
    ip_left, ip_right = st.columns([1.3, 1], gap="large")

    with ip_left:
        fig_ip = go.Figure()

        fig_ip.add_trace(go.Scatter(
            x=timeline_months, y=timeline_gross,
            mode="lines", name="Gross income",
            line=dict(color="#c8a96e", width=2),
            hovertemplate="Month %{x}<br>Gross: $%{y:,.0f}<extra></extra>",
        ))
        fig_ip.add_trace(go.Scatter(
            x=timeline_months, y=timeline_net,
            mode="lines", name="Est. take-home",
            line=dict(color="#7ec8a0", width=2, dash="dot"),
            fill="tozeroy", fillcolor="rgba(126,200,160,0.05)",
            hovertemplate="Month %{x}<br>Take-home: $%{y:,.0f}<extra></extra>",
        ))

        # Markers at each promotion
        marker_x = [s[0] for s in steps]
        marker_y = [s[1] for s in steps]
        marker_labels = [s[2] for s in steps]
        fig_ip.add_trace(go.Scatter(
            x=marker_x, y=marker_y,
            mode="markers+text",
            marker=dict(color="#c8a96e", size=8, symbol="circle"),
            text=marker_labels,
            textposition="top center",
            textfont=dict(color="#c8a96e", size=10),
            hovertemplate="%{text}<br>Month %{x}<br>$%{y:,.0f}<extra></extra>",
            showlegend=False,
        ))

        # Reference line at current gross
        fig_ip.add_hline(y=gross, line=dict(color="rgba(255,255,255,0.12)", width=1, dash="dash"),
                         annotation_text="Current salary",
                         annotation_font=dict(color="rgba(255,255,255,0.4)", size=9))

        fig_ip.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            height=300, margin=dict(t=20, b=0, l=0, r=10),
            font=dict(color="#ffffff", size=11, family="DM Sans"),
            xaxis=dict(gridcolor="#14141f", linecolor="#1c1c2e", title="Months from now"),
            yaxis=dict(gridcolor="#14141f", linecolor="#1c1c2e", tickprefix="$"),
            legend=dict(font=dict(color="#a0a0b8", size=10), bgcolor="rgba(0,0,0,0)"),
        )
        st.plotly_chart(fig_ip, use_container_width=True)

    with ip_right:
        st.markdown('<div class="section-head" style="margin-top:4px">Promotion summary</div>', unsafe_allow_html=True)

        cur_display = float(gross)
        for month, new_g, label in steps:
            prev_net  = cur_display - calc_federal_tax(cur_display) - calc_state_tax(cur_display, state_abbr)
            new_net   = new_g - calc_federal_tax(new_g) - calc_state_tax(new_g, state_abbr)
            delta_g   = new_g - cur_display
            delta_net = new_net - prev_net
            yrs_disp, mos_disp = divmod(month, 12)
            time_parts = []
            if yrs_disp: time_parts.append(f"{yrs_disp} yr{'s' if yrs_disp != 1 else ''}")
            if mos_disp: time_parts.append(f"{mos_disp} mo")
            time_str = " ".join(time_parts) or f"{month} mo"

            st.markdown(f"""
<div class="goal-card" style="margin-bottom:12px;padding:18px 22px">
  <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:10px">
    <div style="font-size:13px;font-weight:600;color:var(--t1)">{label}</div>
    <div style="font-size:11px;color:var(--t2);white-space:nowrap;margin-left:12px">in {time_str}</div>
  </div>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px">
    <div>
      <div style="font-size:18px;font-family:'DM Serif Display',serif;color:#c8a96e">${new_g:,.0f}</div>
      <div style="font-size:10px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--t2);margin-top:2px">New gross</div>
    </div>
    <div>
      <div style="font-size:18px;font-family:'DM Serif Display',serif;color:#7ec8a0">${new_net:,.0f}</div>
      <div style="font-size:10px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--t2);margin-top:2px">Est. take-home</div>
    </div>
    <div>
      <div style="font-size:14px;color:{"#7ec8a0" if delta_g >= 0 else "#d48888"};font-weight:500">{"+" if delta_g >= 0 else ""}{delta_g:,.0f} gross</div>
      <div style="font-size:10px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--t2);margin-top:2px">Change</div>
    </div>
    <div>
      <div style="font-size:14px;color:{"#7ec8a0" if delta_net >= 0 else "#d48888"};font-weight:500">{"+" if delta_net >= 0 else ""}{delta_net:,.0f} take-home</div>
      <div style="font-size:10px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--t2);margin-top:2px">Change</div>
    </div>
  </div>
</div>""", unsafe_allow_html=True)
            cur_display = new_g

        # Overall summary
        final_gross = steps[-1][1]
        final_net   = final_gross - calc_federal_tax(final_gross) - calc_state_tax(final_gross, state_abbr)
        total_delta = final_gross - gross
        total_pct   = round(total_delta / gross * 100, 1) if gross else 0
        st.markdown(f"""
<div style="background:var(--surface);border:1px solid rgba(200,169,110,0.2);border-left:3px solid #c8a96e;border-radius:8px;padding:14px 18px;font-size:13px;color:var(--t1);line-height:1.7">
  After all {len(steps)} promotion{"s" if len(steps) != 1 else ""},
  your salary grows from <b>${gross:,.0f}</b> to <b style="color:#c8a96e">${final_gross:,.0f}</b>
  — a <b>+{total_pct}%</b> increase. Estimated take-home rises to
  <b style="color:#7ec8a0">${final_net:,.0f}/yr</b> (${final_net/12:,.0f}/mo).
</div>""", unsafe_allow_html=True)


# ── Net Worth Tracker ─────────────────────────────────────────────────────────
st.divider()
st.markdown('<div class="section-head">Net worth tracker</div>', unsafe_allow_html=True)

if nw_total_assets == 0 and nw_total_liabilities == 0:
    st.info("Open the **Net worth** expander in the sidebar to add your assets and liabilities.")
else:
    nw_color = "nw-big-pos" if net_worth >= 0 else "nw-big-neg"
    nw_l, nw_m, nw_r = st.columns([1, 1, 1.3], gap="large")

    with nw_l:
        st.markdown(f"""
<div class="nw-card">
  <div style="font-size:10px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:var(--t2);margin-bottom:8px">Total assets</div>
  <div class="nw-big-pos">${nw_total_assets:,.0f}</div>
  <div style="margin-top:14px;display:grid;gap:7px">
    {"".join(f'<div style="display:flex;justify-content:space-between;font-size:12px;padding:3px 0;border-bottom:1px solid var(--border)"><span style="color:var(--t-60)">{n}</span><span style="color:var(--t1)">${v:,.0f}</span></div>' for n,v in [("Checking & savings",nw_checking),("Investments",nw_investments),("Retirement accts",nw_retirement_a),("Home",nw_home),("Vehicle",nw_vehicle),("Other",nw_other_asset)] if v > 0)}
  </div>
</div>""", unsafe_allow_html=True)

    with nw_m:
        st.markdown(f"""
<div class="nw-card">
  <div style="font-size:10px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:var(--t2);margin-bottom:8px">Total liabilities</div>
  <div class="nw-big-neg">${nw_total_liabilities:,.0f}</div>
  <div style="margin-top:14px;display:grid;gap:7px">
    {"".join(f'<div style="display:flex;justify-content:space-between;font-size:12px;padding:3px 0;border-bottom:1px solid var(--border)"><span style="color:var(--t-60)">{n}</span><span style="color:#d48888">${v:,.0f}</span></div>' for n,v in [("Mortgage",nw_mortgage),("Student loans",nw_student),("Car loan",nw_car_loan),("Credit cards",nw_credit),("Other",nw_other_liab)] if v > 0)}
  </div>
</div>""", unsafe_allow_html=True)

    with nw_r:
        nw_sign = "+" if net_worth >= 0 else ""
        debt_to_asset = round(nw_total_liabilities / nw_total_assets * 100) if nw_total_assets > 0 else 0

        _asset_labels = ["Checking & savings", "Investments", "Retirement", "Home", "Vehicle", "Other"]
        _asset_vals   = [nw_checking, nw_investments, nw_retirement_a, nw_home, nw_vehicle, nw_other_asset]
        _asset_colors = ["#7ec8c8", "#a07ec8", "#c8a96e", "#7eafc8", "#c8b07e", "#8a8a8a"]
        _asset_data   = [(l, v, c) for l, v, c in zip(_asset_labels, _asset_vals, _asset_colors) if v > 0]

        if _asset_data:
            fig_nw = go.Figure(go.Pie(
                labels=[x[0] for x in _asset_data],
                values=[x[1] for x in _asset_data],
                hole=0.6,
                marker=dict(colors=[x[2] for x in _asset_data], line=dict(color="#0a0a0f", width=2)),
                textinfo="none",
                hovertemplate="<b>%{label}</b><br>$%{value:,.0f}<extra></extra>",
            ))
            fig_nw.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                height=200, margin=dict(t=0, b=0, l=0, r=0),
                showlegend=True,
                legend=dict(font=dict(color="#ffffff", size=10), bgcolor="rgba(0,0,0,0)"),
                annotations=[dict(text=f"<b>${nw_total_assets/1e6:.2f}M</b>" if nw_total_assets >= 1e6 else f"<b>${nw_total_assets:,.0f}</b>",
                                  x=0.5, y=0.5, showarrow=False,
                                  font=dict(color="#ffffff", size=12))],
            )
            st.plotly_chart(fig_nw, use_container_width=True)

        nw_sign_color = "#7ec8a0" if net_worth >= 0 else "#d48888"
        st.markdown(f"""
<div style="background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:16px 20px">
  <div style="display:flex;justify-content:space-between;align-items:center">
    <div style="font-size:10px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:var(--t2)">Net worth</div>
    <div style="font-size:24px;font-family:'DM Serif Display',serif;color:{nw_sign_color}">{nw_sign}${abs(net_worth):,.0f}</div>
  </div>
  <div style="display:flex;justify-content:space-between;margin-top:10px;font-size:12px">
    <span style="color:var(--t2)">Debt-to-asset ratio</span>
    <span style="color:{"#d48888" if debt_to_asset > 50 else "#7ec8a0"}">{debt_to_asset}%</span>
  </div>
  <div style="display:flex;justify-content:space-between;margin-top:6px;font-size:12px">
    <span style="color:var(--t2)">Annual savings adds</span>
    <span style="color:#7ec8a0">+${savings_annual:,.0f}/yr</span>
  </div>
</div>""", unsafe_allow_html=True)


# ── Retirement Projector ──────────────────────────────────────────────────────
st.divider()
st.markdown('<div class="section-head">Retirement projector</div>', unsafe_allow_html=True)

rp_left, rp_right = st.columns([1.2, 1], gap="large")

with rp_left:
    if ret_years <= 0:
        st.info("Your target retirement age is at or before your current age — adjust the sliders in the sidebar.")
    else:
        fig_ret = go.Figure()
        fig_ret.add_trace(go.Scatter(
            x=[ret_age + y for y in ret_curve_years],
            y=ret_curve_values,
            mode="lines",
            line=dict(color="#a07ec8", width=2),
            fill="tozeroy", fillcolor="rgba(160,126,200,0.07)",
            hovertemplate="Age %{x}: $%{y:,.0f}<extra></extra>",
        ))
        if nw_retirement_a > 0:
            fig_ret.add_hline(y=nw_retirement_a,
                              line=dict(color="rgba(255,255,255,.2)", width=1, dash="dash"),
                              annotation_text="Starting savings",
                              annotation_font=dict(color="rgba(255,255,255,.4)", size=9))
        fig_ret.add_vline(x=ret_target_age,
                          line=dict(color="#c8a96e", width=1, dash="dot"))
        fig_ret.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            height=280, margin=dict(t=20, b=0, l=0, r=10),
            font=dict(color="#ffffff", size=11, family="DM Sans"),
            xaxis=dict(gridcolor="#14141f", linecolor="#1c1c2e", title="Age"),
            yaxis=dict(gridcolor="#14141f", linecolor="#1c1c2e", tickprefix="$"),
            showlegend=False,
        )
        st.plotly_chart(fig_ret, use_container_width=True)

with rp_right:
    st.markdown(f"""
<div class="nw-card" style="margin-bottom:12px">
  <div style="font-size:10px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:var(--t2);margin-bottom:8px">Projected nest egg at {ret_target_age}</div>
  <div style="font-family:'DM Serif Display',serif;font-size:38px;color:#b09ad8;line-height:1;letter-spacing:-0.02em">${ret_fv:,.0f}</div>
  <div style="font-size:11px;color:var(--t2);margin-top:6px">nominal · {ret_return_rate}% annual return</div>
  <div style="margin-top:14px;display:grid;grid-template-columns:1fr 1fr;gap:10px">
    <div>
      <div style="font-size:16px;font-family:'DM Serif Display',serif;color:#7ec8a0">${ret_monthly_4pct:,.0f}</div>
      <div style="font-size:10px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--t2);margin-top:2px">Monthly income (4% rule)</div>
    </div>
    <div>
      <div style="font-size:16px;font-family:'DM Serif Display',serif;color:#7ec8c8">${ret_fv_real:,.0f}</div>
      <div style="font-size:10px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--t2);margin-top:2px">Inflation-adjusted ({ret_inflation}%)</div>
    </div>
  </div>
</div>""", unsafe_allow_html=True)

    st.markdown(f"""
<div style="background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:14px 18px;font-size:12px;line-height:1.8;color:var(--t-70)">
  <div style="display:grid;gap:4px">
    <div style="display:flex;justify-content:space-between"><span>Years to retirement</span><span style="color:var(--t1);font-weight:500">{ret_years} yrs</span></div>
    <div style="display:flex;justify-content:space-between"><span>Annual contribution</span><span style="color:var(--t1);font-weight:500">${savings_annual:,.0f}/yr</span></div>
    <div style="display:flex;justify-content:space-between"><span>Starting savings</span><span style="color:var(--t1);font-weight:500">${ret_current_ret:,.0f}</span></div>
    <div style="display:flex;justify-content:space-between"><span>Return rate</span><span style="color:var(--t1);font-weight:500">{ret_return_rate}%</span></div>
    <div style="display:flex;justify-content:space-between"><span>Inflation</span><span style="color:var(--t1);font-weight:500">{ret_inflation}%</span></div>
  </div>
</div>""", unsafe_allow_html=True)
    st.caption("Projections use compound interest. 4% rule estimates safe annual withdrawal as 4% of nest egg. Not financial advice.")


# ── Salary Equivalency ────────────────────────────────────────────────────────
st.divider()
st.markdown('<div class="section-head">What would I need to earn?</div>', unsafe_allow_html=True)
st.caption(f"To maintain your exact lifestyle from **{location}**, here's what you'd need to earn in other cities — adjusted for local cost of living.")

_eq_left, _eq_right = st.columns(2, gap="large")
_eq_half = len(equiv_data) // 2 + len(equiv_data) % 2
for _ei, _ed in enumerate(equiv_data):
    _col = _eq_left if _ei < _eq_half else _eq_right
    _col_delta = _ed["col"] - col_idx
    _col_label = f"+{_col_delta}" if _col_delta >= 0 else str(_col_delta)
    _col_badge_bg  = "rgba(220,96,96,.10)"  if _col_delta > 0 else "rgba(75,184,138,.10)"
    _col_badge_fg  = "#DC6060" if _col_delta > 0 else "#4BB88A"
    _delta_sign    = "+" if _ed["delta"] >= 0 else ""
    _delta_color   = "#DC6060" if _ed["delta"] > 0 else "#4BB88A"
    with _col:
        st.markdown(f"""
<div class="equiv-row">
  <div class="equiv-city">{_ed["city"]}</div>
  <div class="equiv-col-badge" style="background:{_col_badge_bg};color:{_col_badge_fg}">COL {_ed["col"]} ({_col_label})</div>
  <div class="equiv-salary">${_ed["gross"]:,.0f}<span class="equiv-delta" style="color:{_delta_color}">({_delta_sign}${abs(_ed["delta"]):,.0f})</span></div>
</div>""", unsafe_allow_html=True)

st.markdown(f'<div style="font-size:11px;color:var(--t3);margin-top:10px">Based on your current gross of <b style="color:var(--t1)">${gross:,.0f}</b> in {location} (COL {col_idx}). COL-sensitive categories (housing, food, transport, health) are scaled to destination city; savings, debt, and other categories are held constant.</div>', unsafe_allow_html=True)


# ── What-If Scenario Comparison ───────────────────────────────────────────────
st.divider()
st.markdown('<div class="section-head">What-if scenario comparison</div>', unsafe_allow_html=True)
st.caption("Compare your current budget against a different city, framework, income, or tier.")

with st.expander("Configure Scenario B"):
    wi_col1, wi_col2 = st.columns(2)
    with wi_col1:
        wi_gross = st.number_input("Income (gross, $/yr)", min_value=0, max_value=2_000_000,
                                    value=gross, step=1_000, format="%d", key="wi_gross")
        _wi_loc_list = list(COL_DATA.keys())
        _wi_loc_idx  = _wi_loc_list.index(location) if location in _wi_loc_list else 0
        wi_location  = st.selectbox("City", _wi_loc_list, index=_wi_loc_idx, key="wi_location")
    with wi_col2:
        _wi_fw_list = list(FRAMEWORKS.keys())
        _wi_fw_idx  = _wi_fw_list.index(fw_name) if fw_name in _wi_fw_list else 0
        wi_fw_name  = st.selectbox("Framework", _wi_fw_list, index=_wi_fw_idx, key="wi_framework")
        _wi_tier_list = list(TIERS.keys())
        _wi_tier_idx  = _wi_tier_list.index(tier) if tier in _wi_tier_list else 1
        wi_tier       = st.radio("Tier", _wi_tier_list, index=_wi_tier_idx,
                                  horizontal=True, key="wi_tier", label_visibility="collapsed")

# Compute Scenario B
wi_col_info   = COL_DATA.get(wi_location, COL_DATA["National Average"])
wi_state_abbr = CITY_STATE.get(wi_location)
wi_federal    = calc_federal_tax(wi_gross)
wi_state_tax  = calc_state_tax(wi_gross, wi_state_abbr)
wi_net        = wi_gross - wi_federal - wi_state_tax
wi_monthly    = wi_net / 12
wi_weekly     = wi_net / 52

wi_pcts_base  = FRAMEWORKS[wi_fw_name]
wi_tier_adj   = TIERS[wi_tier]["adj"]
wi_adj_pcts   = {k: max(0, wi_pcts_base.get(k, 0) + wi_tier_adj.get(k, 0)) for k, _, _ in CATEGORIES}
_wi_tot = sum(wi_adj_pcts.values())
if _wi_tot > 0 and _wi_tot != 100:
    _ws = 100 / _wi_tot
    wi_adj_pcts = {k: round(v * _ws) for k, v in wi_adj_pcts.items()}
    _wd = 100 - sum(wi_adj_pcts.values())
    if _wd != 0:
        wi_adj_pcts[max(wi_adj_pcts, key=wi_adj_pcts.get)] += _wd

def _wi_col(key, base_weekly):
    if key == "housing":   return base_weekly * wi_col_info["housing_mult"]
    if key == "food":      return base_weekly * wi_col_info["food_mult"]
    if key == "transport": return base_weekly * wi_col_info["transport_mult"]
    if key == "health":    return base_weekly * wi_col_info["health_mult"]
    return base_weekly

wi_cat_data = []
for _k, _lbl, _clr in CATEGORIES:
    _bw  = wi_weekly * wi_adj_pcts.get(_k, 0) / 100
    _bw  = _wi_col(_k, _bw)
    _mo  = _bw * 52 / 12
    _ann = _mo * 12
    wi_cat_data.append({"key": _k, "label": _lbl, "color": _clr,
                         "monthly": _mo, "annual": _ann,
                         "pct": wi_adj_pcts.get(_k, 0)})

# Side-by-side table
wi_a, wi_b = st.columns(2, gap="large")

def _wi_header(title, sub, gross_val, net_val, location_val, fw_val, tier_val):
    return f"""
<div class="nw-card" style="margin-bottom:14px">
  <div class="wi-col-head">{title}</div>
  <div style="font-size:11px;color:var(--t2);margin-bottom:10px">{sub}</div>
  <div style="display:grid;gap:6px;font-size:12px">
    <div style="display:flex;justify-content:space-between"><span style="color:var(--t2)">Gross</span><span style="color:#c8a96e;font-weight:600">${gross_val:,.0f}</span></div>
    <div style="display:flex;justify-content:space-between"><span style="color:var(--t2)">Take-home</span><span style="color:#7ec8a0;font-weight:600">${net_val:,.0f}/yr</span></div>
    <div style="display:flex;justify-content:space-between"><span style="color:var(--t2)">City</span><span style="color:var(--t1)">{location_val}</span></div>
    <div style="display:flex;justify-content:space-between"><span style="color:var(--t2)">Framework</span><span style="color:var(--t1)">{fw_val.split("(")[0].strip()}</span></div>
    <div style="display:flex;justify-content:space-between"><span style="color:var(--t2)">Tier</span><span style="color:var(--t1)">{tier_val}</span></div>
  </div>
</div>"""

with wi_a:
    st.markdown(_wi_header("Scenario A — Current", "Your active sidebar settings",
                            gross, net, location, fw_name, tier), unsafe_allow_html=True)
    for d in cat_data:
        delta = d["monthly"] - next(x["monthly"] for x in wi_cat_data if x["key"] == d["key"])
        dcolor = "#7ec8a0" if delta >= 0 else "#d48888"
        dsign  = "+" if delta >= 0 else ""
        st.markdown(f'<div class="sub-row"><span style="color:var(--t-70)">{d["label"]}</span><div><span style="color:var(--t1);font-weight:500">${d["monthly"]:,.0f}/mo</span>&nbsp;<span style="font-size:11px;color:{dcolor}">({dsign}${abs(delta):,.0f})</span></div></div>', unsafe_allow_html=True)

with wi_b:
    st.markdown(_wi_header("Scenario B — Comparison", "Configured in the expander above",
                            wi_gross, wi_net, wi_location, wi_fw_name, wi_tier), unsafe_allow_html=True)
    for d in wi_cat_data:
        st.markdown(f'<div class="sub-row"><span style="color:var(--t-70)">{d["label"]}</span><span style="color:var(--t1);font-weight:500">${d["monthly"]:,.0f}/mo</span></div>', unsafe_allow_html=True)

# Net delta summary
net_delta = wi_net - net
st.markdown(f"""
<div style="margin-top:16px;background:var(--surface);border:1px solid rgba({"80,180,100" if net_delta >= 0 else "200,80,80"},.2);border-left:3px solid {"#7ec8a0" if net_delta >= 0 else "#d48888"};border-radius:8px;padding:14px 18px;font-size:13px;color:var(--t1);line-height:1.7">
  Scenario B {"increases" if net_delta >= 0 else "decreases"} your estimated take-home by
  <b style="color:{"#7ec8a0" if net_delta >= 0 else "#d48888"}">{"+" if net_delta >= 0 else ""}{net_delta:,.0f}/yr</b>
  (${abs(net_delta)/12:,.0f}/mo) compared to Scenario A.
  Housing changes by <b>${(next(x["monthly"] for x in wi_cat_data if x["key"]=="housing") - next(x["monthly"] for x in cat_data if x["key"]=="housing")):+,.0f}/mo</b> with cost-of-living adjustments applied.
</div>""", unsafe_allow_html=True)


# ── Sidebar Part 2: PDF export ────────────────────────────────────────────────
with st.sidebar:
    st.divider()
    st.markdown("#### Export")
    pdf_bytes = generate_pdf(
        gross=gross, net=net,
        federal_tax=federal_tax, state_tax_amt=state_tax_amt, state_abbr=state_abbr,
        location=location, fw_name=fw_name, tier_name=tier,
        cat_data=cat_data,
        goal_name=goal_name, goal_amount=goal_amount,
        goal_current=goal_current, goal_months=goal_months,
        debt_balance=debt_balance, debt_rate=debt_rate,
        monthly_debt_payment=monthly_debt_payment,
        debt_months=debt_months, debt_interest=debt_interest,
    )
    st.download_button(
        label="📄 Download budget as PDF",
        data=pdf_bytes,
        file_name=f"lifestyle_budget_{gross:,.0f}.pdf",
        mime="application/pdf",
        use_container_width=True,
    )

    st.divider()

    # ── Account controls ──
    _auth_user = st.session_state.get("auth_user")
    if _auth_user:
        st.markdown("#### Account")
        st.caption(f"Signed in as **{_auth_user}**")
        if st.button("💾 Save my progress", use_container_width=True):
            _save_profile(_auth_user)
            st.success("Progress saved!")
        if st.button("← Start over", use_container_width=True):
            st.session_state.intro_done = False
            st.rerun()
        if st.button("Log out", use_container_width=True):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()
    else:
        st.markdown("#### Account")
        st.caption("Guest session — progress won't be saved.")
        if st.button("← Start over", use_container_width=True):
            st.session_state.intro_done = False
            st.rerun()
        if st.button("Create an account", use_container_width=True):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()

st.divider()
st.caption("Tax estimates use 2024 US federal brackets + 7.65% FICA + simplified state income tax rates. Cost of living multipliers are estimates based on composite index data. All figures are for planning purposes only.")
