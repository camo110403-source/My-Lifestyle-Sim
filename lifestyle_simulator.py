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
def calc_tax(gross):
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
tax = calc_tax(gross)
net = gross - tax
weekly_net = net / 52
tax_rate = round(tax / gross * 100) if gross > 0 else 0

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
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Gross income", f"${gross:,.0f}", help="Before taxes")
with c2:
    st.metric("Estimated taxes", f"${tax:,.0f}", delta=f"-{tax_rate}% effective rate", delta_color="inverse")
with c3:
    st.metric("Take-home (annual)", f"${net:,.0f}")
with c4:
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
st.caption("Tax estimate uses simplified 2024 US federal brackets + 7.65% FICA. State taxes not included. Cost of living multipliers are estimates based on composite index data. All figures are for planning purposes only.")
