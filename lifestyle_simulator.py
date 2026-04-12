import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(
    page_title="Lifestyle Budget Simulator",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

h1, h2, h3 {
    font-family: 'DM Serif Display', serif;
}

.main { background-color: #0f0f0f; }
[data-testid="stAppViewContainer"] { background: #0f0f0f; }
[data-testid="stSidebar"] { background: #161616; border-right: 1px solid #2a2a2a; }

.metric-row {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
    margin-bottom: 24px;
}
.metric-card {
    background: #1a1a1a;
    border: 1px solid #2a2a2a;
    border-radius: 12px;
    padding: 16px 20px;
}
.metric-label {
    font-size: 11px;
    font-weight: 500;
    color: #666;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 6px;
}
.metric-value {
    font-family: 'DM Serif Display', serif;
    font-size: 28px;
    color: #f0ead6;
    line-height: 1.1;
}
.metric-sub {
    font-size: 11px;
    color: #555;
    margin-top: 4px;
}

.cat-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 10px;
    margin-bottom: 24px;
}
.cat-card {
    background: #1a1a1a;
    border: 1px solid #2a2a2a;
    border-radius: 10px;
    padding: 14px 16px;
}
.cat-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
}
.cat-name {
    font-size: 12px;
    font-weight: 500;
    color: #aaa;
}
.cat-pct {
    font-size: 11px;
    color: #555;
}
.cat-bar-bg {
    height: 3px;
    background: #2a2a2a;
    border-radius: 2px;
    margin-bottom: 10px;
}
.cat-bar {
    height: 3px;
    border-radius: 2px;
}
.cat-weekly {
    font-family: 'DM Serif Display', serif;
    font-size: 20px;
    color: #f0ead6;
}
.cat-annual {
    font-size: 11px;
    color: #555;
    margin-top: 2px;
}

.location-tag {
    display: inline-block;
    background: #1e2a1e;
    color: #5d9e5d;
    border: 1px solid #2d4a2d;
    border-radius: 20px;
    padding: 4px 14px;
    font-size: 12px;
    font-weight: 500;
    margin-bottom: 16px;
}

.section-head {
    font-family: 'DM Serif Display', serif;
    font-size: 18px;
    color: #f0ead6;
    margin-bottom: 14px;
    margin-top: 4px;
}

.insight-box {
    background: #141c14;
    border: 1px solid #2d4a2d;
    border-radius: 10px;
    padding: 14px 18px;
    margin-bottom: 10px;
    font-size: 13px;
    color: #8fc48f;
    line-height: 1.6;
}
</style>
""", unsafe_allow_html=True)


# ── Cost of living index data (national average = 100) ──────────────────────
COL_DATA = {
    "National Average": {"index": 100, "housing_mult": 1.00, "food_mult": 1.00, "transport_mult": 1.00, "health_mult": 1.00},
    # Major metros
    "New York City, NY":    {"index": 187, "housing_mult": 3.20, "food_mult": 1.22, "transport_mult": 1.18, "health_mult": 1.15},
    "San Francisco, CA":    {"index": 182, "housing_mult": 3.10, "food_mult": 1.20, "transport_mult": 1.15, "health_mult": 1.18},
    "Los Angeles, CA":      {"index": 163, "housing_mult": 2.60, "food_mult": 1.14, "transport_mult": 1.18, "health_mult": 1.10},
    "Boston, MA":           {"index": 162, "housing_mult": 2.55, "food_mult": 1.16, "transport_mult": 1.12, "health_mult": 1.14},
    "Seattle, WA":          {"index": 158, "housing_mult": 2.45, "food_mult": 1.14, "transport_mult": 1.10, "health_mult": 1.12},
    "Washington, DC":       {"index": 155, "housing_mult": 2.40, "food_mult": 1.13, "transport_mult": 1.10, "health_mult": 1.11},
    "Miami, FL":            {"index": 148, "housing_mult": 2.20, "food_mult": 1.10, "transport_mult": 1.08, "health_mult": 1.08},
    "Chicago, IL":          {"index": 138, "housing_mult": 1.85, "food_mult": 1.09, "transport_mult": 1.08, "health_mult": 1.06},
    "Denver, CO":           {"index": 135, "housing_mult": 1.80, "food_mult": 1.08, "transport_mult": 1.05, "health_mult": 1.06},
    "Austin, TX":           {"index": 128, "housing_mult": 1.70, "food_mult": 1.06, "transport_mult": 1.04, "health_mult": 1.04},
    "Portland, OR":         {"index": 127, "housing_mult": 1.68, "food_mult": 1.07, "transport_mult": 1.05, "health_mult": 1.05},
    "Nashville, TN":        {"index": 120, "housing_mult": 1.55, "food_mult": 1.04, "transport_mult": 1.02, "health_mult": 1.02},
    "Atlanta, GA":          {"index": 118, "housing_mult": 1.48, "food_mult": 1.03, "transport_mult": 1.03, "health_mult": 1.02},
    "Phoenix, AZ":          {"index": 116, "housing_mult": 1.45, "food_mult": 1.02, "transport_mult": 1.03, "health_mult": 1.01},
    "Dallas, TX":           {"index": 114, "housing_mult": 1.42, "food_mult": 1.02, "transport_mult": 1.04, "health_mult": 1.01},
    "Minneapolis, MN":      {"index": 113, "housing_mult": 1.38, "food_mult": 1.04, "transport_mult": 1.01, "health_mult": 1.03},
    "Charlotte, NC":        {"index": 108, "housing_mult": 1.25, "food_mult": 1.01, "transport_mult": 1.01, "health_mult": 1.00},
    "Columbus, OH":         {"index": 103, "housing_mult": 1.10, "food_mult": 1.00, "transport_mult": 1.00, "health_mult": 0.99},
    "Indianapolis, IN":     {"index": 97,  "housing_mult": 0.90, "food_mult": 0.97, "transport_mult": 0.98, "health_mult": 0.97},
    "Pittsburgh, PA":       {"index": 96,  "housing_mult": 0.88, "food_mult": 0.97, "transport_mult": 0.98, "health_mult": 0.97},
    "Kansas City, MO":      {"index": 94,  "housing_mult": 0.85, "food_mult": 0.96, "transport_mult": 0.97, "health_mult": 0.96},
    "St. Louis, MO":        {"index": 93,  "housing_mult": 0.83, "food_mult": 0.96, "transport_mult": 0.97, "health_mult": 0.96},
    "Louisville, KY":       {"index": 91,  "housing_mult": 0.80, "food_mult": 0.95, "transport_mult": 0.96, "health_mult": 0.95},
    "Memphis, TN":          {"index": 88,  "housing_mult": 0.75, "food_mult": 0.94, "transport_mult": 0.95, "health_mult": 0.94},
    "Oklahoma City, OK":    {"index": 87,  "housing_mult": 0.73, "food_mult": 0.94, "transport_mult": 0.95, "health_mult": 0.94},
    "Tulsa, OK":            {"index": 85,  "housing_mult": 0.70, "food_mult": 0.93, "transport_mult": 0.94, "health_mult": 0.93},
    "Wichita, KS":          {"index": 84,  "housing_mult": 0.68, "food_mult": 0.93, "transport_mult": 0.93, "health_mult": 0.93},
    "Fayetteville, AR":     {"index": 83,  "housing_mult": 0.66, "food_mult": 0.92, "transport_mult": 0.93, "health_mult": 0.92},
    "Little Rock, AR":      {"index": 82,  "housing_mult": 0.65, "food_mult": 0.92, "transport_mult": 0.93, "health_mult": 0.92},
    "Jackson, MS":          {"index": 80,  "housing_mult": 0.62, "food_mult": 0.91, "transport_mult": 0.92, "health_mult": 0.91},
}

# ── Tax calculation ──────────────────────────────────────────────────────────
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

# ── State income tax data ─────────────────────────────────────────────────────
# flat_rate: flat tax states. brackets: [(income_ceiling, rate), ...]. std_ded: standard deduction.
STATE_TAX = {
    "AL": {"type": "brackets", "std_ded": 2500,  "brackets": [(500, 0.02), (3000, 0.04), (float("inf"), 0.05)]},
    "AK": {"type": "none"},
    "AZ": {"type": "flat",     "rate": 0.025},
    "AR": {"type": "brackets", "std_ded": 2200,  "brackets": [(4300, 0.02), (8500, 0.04), (float("inf"), 0.049)]},
    "CA": {"type": "brackets", "std_ded": 5202,  "brackets": [(10099, 0.01), (23942, 0.02), (37788, 0.04), (52455, 0.06), (66295, 0.08), (338639, 0.093), (406364, 0.103), (677275, 0.113), (float("inf"), 0.123)]},
    "CO": {"type": "flat",     "rate": 0.044},
    "CT": {"type": "brackets", "std_ded": 0,     "brackets": [(10000, 0.03), (50000, 0.05), (100000, 0.055), (200000, 0.06), (250000, 0.065), (500000, 0.069), (float("inf"), 0.0699)]},
    "DC": {"type": "brackets", "std_ded": 12950, "brackets": [(10000, 0.04), (40000, 0.06), (60000, 0.065), (350000, 0.085), (1000000, 0.0925), (float("inf"), 0.1075)]},
    "FL": {"type": "none"},
    "GA": {"type": "flat",     "rate": 0.0549},
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

# Map each city to its state abbreviation
CITY_STATE = {
    "National Average": None,
    "New York City, NY": "NY", "San Francisco, CA": "CA", "Los Angeles, CA": "CA",
    "Boston, MA": "MA", "Seattle, WA": "WA", "Washington, DC": "DC",
    "Miami, FL": "FL", "Chicago, IL": "IL", "Denver, CO": "CO",
    "Austin, TX": "TX", "Portland, OR": "OR", "Nashville, TN": "TN",
    "Atlanta, GA": "GA", "Phoenix, AZ": "AZ", "Dallas, TX": "TX",
    "Minneapolis, MN": "MN", "Charlotte, NC": "NC", "Columbus, OH": "OH",
    "Indianapolis, IN": "IN", "Pittsburgh, PA": "PA", "Kansas City, MO": "MO",
    "St. Louis, MO": "MO", "Louisville, KY": "KY", "Memphis, TN": "TN",
    "Oklahoma City, OK": "OK", "Tulsa, OK": "OK", "Wichita, KS": "KS",
    "Fayetteville, AR": "AR", "Little Rock, AR": "AR", "Jackson, MS": "MS",
}

def calc_state_tax(gross, state_abbr):
    if state_abbr is None or state_abbr not in STATE_TAX:
        return 0
    info = STATE_TAX[state_abbr]
    if info["type"] == "none":
        return 0
    if info["type"] == "flat":
        return round(gross * info["rate"])
    # brackets
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

def calc_tax(gross, state_abbr=None):
    federal = calc_federal_tax(gross)
    state   = calc_state_tax(gross, state_abbr)
    return federal, state

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

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<p style="font-family:\'DM Serif Display\',serif;font-size:22px;color:#f0ead6;margin-bottom:4px">Lifestyle Simulator</p>', unsafe_allow_html=True)
    st.markdown('<p style="font-size:12px;color:#555;margin-bottom:24px">Budget planning based on real cost of living</p>', unsafe_allow_html=True)

    st.markdown("#### Income")
    income_type = st.radio("Income type", ["Annual salary", "Hourly wage"], horizontal=True, label_visibility="collapsed")

    if income_type == "Annual salary":
        gross = st.number_input("Annual salary ($)", min_value=0, max_value=2000000, value=75000, step=1000, format="%d")
    else:
        hourly = st.number_input("Hourly wage ($)", min_value=0.0, max_value=500.0, value=25.0, step=0.50, format="%.2f")
        gross = hourly * 40 * 52
        st.caption(f"→ ${gross:,.0f} / year (40 hrs × 52 wks)")

    st.divider()

    st.markdown("#### Location")
    location = st.selectbox("City / metro area", list(COL_DATA.keys()), index=0)
    col_info = COL_DATA[location]
    col_idx = col_info["index"]

    if col_idx != 100:
        diff = col_idx - 100
        direction = "higher" if diff > 0 else "lower"
        st.caption(f"Cost of living is **{abs(diff)}% {direction}** than the national average.")

    st.divider()

    st.markdown("#### Budgeting framework")
    fw_name = st.selectbox("Framework", list(FRAMEWORKS.keys()))
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

# ── Calculations ─────────────────────────────────────────────────────────────
state_abbr = CITY_STATE.get(location)
federal_tax, state_tax = calc_tax(gross, state_abbr)
tax = federal_tax + state_tax
net = gross - tax
weekly_net = net / 52
tax_rate = round(tax / gross * 100) if gross > 0 else 0
fed_rate  = round(federal_tax / gross * 100) if gross > 0 else 0
st_rate   = round(state_tax / gross * 100) if gross > 0 else 0

def apply_col(key, base_weekly):
    if key in COL_AFFECTED:
        mult_key = f"{key}_mult" if f"{key}_mult" in col_info else "index"
        if key == "housing":   return base_weekly * col_info["housing_mult"]
        if key == "food":      return base_weekly * col_info["food_mult"]
        if key == "transport": return base_weekly * col_info["transport_mult"]
        if key == "health":    return base_weekly * col_info["health_mult"]
    return base_weekly

cat_data = []
for key, label, color in CATEGORIES:
    base = weekly_net * pcts.get(key, 0) / 100
    adjusted = apply_col(key, base)
    cat_data.append({
        "key": key, "label": label, "color": color,
        "pct": pcts.get(key, 0),
        "weekly_base": base,
        "weekly": adjusted,
        "annual": adjusted * 52,
    })

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="margin-bottom:8px">
  <span style="font-family:'DM Serif Display',serif;font-size:32px;color:#f0ead6">
    Your financial life at <span style="color:#c8a96e">${gross:,.0f}/yr</span>
  </span>
</div>
<div class="location-tag">📍 {location} — COL index {col_idx}</div>
""", unsafe_allow_html=True)

# ── Top metrics ───────────────────────────────────────────────────────────────
c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    st.metric("Gross income", f"${gross:,.0f}", help="Before taxes")
with c2:
    st.metric("Federal tax", f"${federal_tax:,.0f}", delta=f"-{fed_rate}% + FICA", delta_color="inverse")
with c3:
    no_tax_states = {"AK","FL","NV","NH","SD","TN","TX","WA","WY"}
    state_label = f"{state_abbr} state tax" if state_abbr else "State tax"
    state_note = "No state income tax" if state_abbr in no_tax_states else f"-{st_rate}% rate"
    st.metric(state_label, f"${state_tax:,.0f}", delta=state_note, delta_color="inverse")
with c4:
    st.metric("Take-home (annual)", f"${net:,.0f}", delta=f"-{tax_rate}% total", delta_color="inverse")
with c5:
    st.metric("Take-home (weekly)", f"${weekly_net:,.0f}")

st.divider()

# ── Two-column layout ─────────────────────────────────────────────────────────
left, right = st.columns([1.05, 1], gap="large")

with left:
    st.markdown('<div class="section-head">Weekly budget breakdown</div>', unsafe_allow_html=True)

    for row_start in range(0, len(cat_data), 3):
        cols = st.columns(3)
        for i, col in enumerate(cols):
            if row_start + i >= len(cat_data):
                break
            d = cat_data[row_start + i]
            bar_w = min(int(d["pct"] * 2.5), 100)
            col.markdown(f"""
<div class="cat-card">
  <div class="cat-header">
    <span class="cat-name">{d["label"]}</span>
    <span class="cat-pct">{d["pct"]}%</span>
  </div>
  <div class="cat-bar-bg">
    <div class="cat-bar" style="width:{bar_w}%;background:{d["color"]}"></div>
  </div>
  <div class="cat-weekly">${d["weekly"]:,.0f}<span style="font-size:12px;color:#555">/wk</span></div>
  <div class="cat-annual">${d["annual"]:,.0f} / year</div>
</div>
""", unsafe_allow_html=True)

with right:
    st.markdown('<div class="section-head">Allocation</div>', unsafe_allow_html=True)

    fig = go.Figure(go.Pie(
        labels=[d["label"] for d in cat_data],
        values=[d["pct"] for d in cat_data],
        hole=0.62,
        marker=dict(colors=[d["color"] for d in cat_data], line=dict(color="#0f0f0f", width=2)),
        textinfo="none",
        hovertemplate="<b>%{label}</b><br>%{value}% — $%{customdata:,.0f}/wk<extra></extra>",
        customdata=[d["weekly"] for d in cat_data],
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=0, b=0, l=0, r=0),
        height=280,
        showlegend=True,
        legend=dict(
            font=dict(color="#888", size=11, family="DM Sans"),
            bgcolor="rgba(0,0,0,0)",
            bordercolor="rgba(0,0,0,0)",
        ),
        annotations=[dict(
            text=f"<b style='font-size:20px'>${weekly_net:,.0f}</b><br>/week",
            x=0.5, y=0.5, showarrow=False,
            font=dict(color="#f0ead6", size=14, family="DM Serif Display"),
        )],
    )
    st.plotly_chart(fig, use_container_width=True)

    # COL comparison bar chart
    st.markdown('<div class="section-head" style="margin-top:8px">Cost of living impact</div>', unsafe_allow_html=True)

    affected = [d for d in cat_data if d["key"] in COL_AFFECTED]
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(
        name="National avg",
        x=[d["label"] for d in affected],
        y=[round(d["weekly_base"]) for d in affected],
        marker_color="#2a2a2a",
        marker_line_color="#444",
        marker_line_width=1,
    ))
    fig2.add_trace(go.Bar(
        name=location,
        x=[d["label"] for d in affected],
        y=[round(d["weekly"]) for d in affected],
        marker_color=[d["color"] for d in affected],
    ))
    fig2.update_layout(
        barmode="group",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=200,
        margin=dict(t=10, b=0, l=0, r=0),
        font=dict(color="#888", size=11, family="DM Sans"),
        xaxis=dict(gridcolor="#1e1e1e", linecolor="#2a2a2a"),
        yaxis=dict(gridcolor="#1e1e1e", linecolor="#2a2a2a", tickprefix="$"),
        legend=dict(font=dict(color="#888", size=10), bgcolor="rgba(0,0,0,0)"),
    )
    st.plotly_chart(fig2, use_container_width=True)

# ── Insights ──────────────────────────────────────────────────────────────────
st.divider()
st.markdown('<div class="section-head">Insights for your situation</div>', unsafe_allow_html=True)

housing_weekly = next(d["weekly"] for d in cat_data if d["key"] == "housing")
savings_weekly = next(d["weekly"] for d in cat_data if d["key"] == "savings")
debt_weekly    = next(d["weekly"] for d in cat_data if d["key"] == "debt")

insights = []

if col_idx > 130:
    insights.append(f"🏙️ <b>{location}</b> has a cost of living {col_idx - 100}% above the national average. Your housing budget of <b>${housing_weekly:,.0f}/wk</b> may feel tight — consider a longer commute or roommates to stay within budget.")
elif col_idx < 90:
    insights.append(f"🌱 <b>{location}</b> is {100 - col_idx}% below the national average cost of living. Your dollar stretches further here — consider redirecting savings toward investing.")

if savings_weekly * 52 < 3000 and gross > 30000:
    insights.append(f"⚠️ Your current savings allocation is <b>${savings_weekly * 52:,.0f}/yr</b>. Financial planners typically recommend 3–6 months of expenses (~${weekly_net * 12:,.0f}) as an emergency fund baseline.")
else:
    insights.append(f"✅ You're on track to save <b>${savings_weekly * 52:,.0f}/yr</b>. At this rate, you'd have a 6-month emergency fund (~${weekly_net * 26:,.0f}) in about {max(1, round(weekly_net * 26 / (savings_weekly * 52)))} year(s).")

if debt_weekly * 52 > net * 0.20:
    insights.append(f"💳 Debt repayment takes up more than 20% of your take-home pay. Consider the avalanche method (highest interest first) to minimize total interest paid.")

if gross < 40000:
    insights.append(f"📌 At your income level, the <b>Earned Income Tax Credit (EITC)</b> may apply to you — consult a tax professional to see if you qualify for additional refunds.")

ic1, ic2 = st.columns(2)
for i, insight in enumerate(insights):
    col = ic1 if i % 2 == 0 else ic2
    col.markdown(f'<div class="insight-box">{insight}</div>', unsafe_allow_html=True)

st.divider()
st.caption("Tax estimates use 2024 US federal brackets (single filer) + 7.65% FICA + simplified state income tax rates. State taxes not included for 'National Average' selection. Cost of living multipliers are estimates based on composite index data. All figures are for planning purposes only — consult a tax professional for advice.")
