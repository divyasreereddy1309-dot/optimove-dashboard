"""
OptiMove V2 — Fleet Demand & Allocation Intelligence
Master's Capstone Project | IS6611 Data Visualization | Cork University Business School | Group 27
═══════════════════════════════════════════════════════════════════════════════════════════════

PROBLEM SOLVED:
- Operations Managers (Hourly): "Which routes need bus reallocation RIGHT NOW? Why? At what cost?"
- Strategic Planners (Weekly): "Should I implement dynamic allocation? Cost vs. service quality trade-off?"

RESEARCH BACKING:
- Liang et al. (2024): Multi-objective bus timetable optimization (cost + comfort)
- Weng et al. (2023): Bus operations vs. passenger satisfaction (headway + crowding)
- Devasurendra et al. (2025): Level of Service analysis (headway + crowding → quality)
- OECD/ITF (2013): Service quality measurement, headway-crowding LOS thresholds
- Cargoson (2025): KPIs must be actionable, not data dumps
- UITP (2025): Headway improvement = revenue + satisfaction
- Efficient Scheduling (2025): Real-time visibility reduces dispatcher errors

DESIGN PRINCIPLES (PPT Slides 47, 54, 19):
- Colorblind-safe palette: Navy | Teal | Charcoal | Gray (NO red+green)
- White space delineation (Slide 47)
- Muted professional colors (Slide 54)
- Color hierarchy for decisions (Slide 19)
- Date format: DD/MM/YYYY (global standard)

FEATURES (Complete):
Operations Manager: 4 KPIs | Pressure Map | Demand Trend | Reallocation Thresholds | Reallocation Schedule | Score Decomposition | Pressure Matrix
Strategic Planner: 4 KPIs | Trade-Off Assessment | Demand by Week | Demand by Day | Risk Distribution | Fleet Comparison | Cost Composition | Route Profile | Planning Scenario
Strategic Planner: 4 KPIs | Trade-Off Panel | Demand by Week | Demand by Day | Risk Pie | Fleet Comparison | Savings | Route Profile | Scenario
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import date, datetime

st.set_page_config(
    page_title="OptiMove V2 — Fleet Intelligence",
    page_icon="🚌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ════════════════════════════════════════════════════════════════════════════
# MASTER'S LEVEL STYLING — Navy/Teal/Charcoal/Gray (Colorblind-Safe)
# ════════════════════════════════════════════════════════════════════════════

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

* { font-family: 'Inter', sans-serif; }

[data-testid="stAppViewContainer"] { background-color: #f3f4f6; }
[data-testid="stSidebar"] { background-color: #1f2937; }

/* Light text for sidebar labels/headings only */
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stMarkdown,
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
    color: #e5e7eb !important;
}
[data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 { color: #ffffff !important; }

/* Input WIDGETS keep dark text on their light backgrounds (fixes white-on-white) */
[data-testid="stSidebar"] [data-baseweb="select"] *,
[data-testid="stSidebar"] [data-baseweb="input"] *,
[data-testid="stSidebar"] input,
[data-testid="stSidebar"] [data-testid="stDateInput"] input {
    color: #1f2937 !important;
}
/* Date input + multiselect field background readable */
[data-testid="stSidebar"] [data-baseweb="input"],
[data-testid="stSidebar"] [data-testid="stDateInput"] > div > div {
    background-color: #ffffff !important;
}
/* Selected multiselect tags */
[data-testid="stSidebar"] [data-baseweb="tag"] {
    background-color: #1e40af !important;
}
[data-testid="stSidebar"] [data-baseweb="tag"] * { color: #ffffff !important; }
/* Radio button labels stay light */
[data-testid="stSidebar"] [role="radiogroup"] label { color: #e5e7eb !important; }

.block-container { padding: 1rem 1.5rem; max-width: 100%; }

/* Header */
.header-box {
    background: linear-gradient(135deg, #1e40af 0%, #1f2937 100%);
    color: white;
    padding: 24px 28px;
    border-radius: 10px;
    margin-bottom: 20px;
    box-shadow: 0 4px 12px rgba(30, 64, 175, 0.15);
}
.header-box h1 { color: white; margin: 0; font-size: 1.7rem; font-weight: 800; }
.header-box p { color: #cbd5e1; margin: 6px 0 0 0; font-size: 0.88rem; }

/* Panels */
.panel {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 10px;
    padding: 20px;
    margin-bottom: 18px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
.panel-title {
    font-size: 0.9rem;
    font-weight: 700;
    color: #1e40af;
    margin-bottom: 16px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

/* KPI Cards */
.kpi-card {
    background: white;
    border: 1px solid #e5e7eb;
    border-left: 4px solid #1e40af;
    border-radius: 10px;
    padding: 18px;
    height: 100%;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
.kpi-card.alert { border-left-color: #1e40af; background: #eff6ff; }
.kpi-card.positive { border-left-color: #0891b2; background: #f0f9ff; }
.kpi-card.neutral { border-left-color: #6b7280; }

.kpi-label {
    font-size: 0.72rem;
    font-weight: 700;
    color: #6b7280;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: 6px;
}
.kpi-value {
    font-size: 1.6rem;
    font-weight: 800;
    color: #1e40af;
    line-height: 1.1;
    margin: 4px 0;
}
.kpi-subtitle {
    font-size: 0.78rem;
    color: #6b7280;
    line-height: 1.35;
}

/* Action/Priority Items */
.action-item {
    padding: 12px 14px;
    margin-bottom: 8px;
    border-left: 4px solid #1e40af;
    background-color: #eff6ff;
    border-radius: 6px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.action-item.safe { border-left-color: #0891b2; background-color: #f0f9ff; }
.action-item.normal { border-left-color: #6b7280; background-color: #f9fafb; }

.action-route { font-weight: 700; color: #1f2937; font-size: 0.92rem; }
.action-detail { font-size: 0.82rem; color: #6b7280; margin-top: 2px; }
.action-badge {
    font-size: 0.68rem;
    font-weight: 700;
    padding: 4px 10px;
    border-radius: 4px;
    color: white;
    text-transform: uppercase;
}
.badge-urgent { background-color: #1e40af; }
.badge-safe { background-color: #0891b2; }
.badge-normal { background-color: #6b7280; }

/* Decision Framework Panel */
.framework-row {
    padding: 12px 14px;
    margin-bottom: 8px;
    border-radius: 6px;
    border-left: 4px solid #1e40af;
}
.framework-row.high { border-left-color: #1e40af; background: #eff6ff; }
.framework-row.moderate { border-left-color: #6b7280; background: #f9fafb; }
.framework-row.low { border-left-color: #0891b2; background: #f0f9ff; }
.framework-label { font-weight: 700; color: #1f2937; font-size: 0.88rem; }
.framework-text { font-size: 0.82rem; color: #4b5563; margin-top: 4px; line-height: 1.4; }

/* Formula Breakdown */

/* Caption */
.caption-text {
    font-size: 0.8rem;
    color: #6b7280;
    line-height: 1.4;
    margin-top: 8px;
}

/* Citation */
.citation {
    font-size: 0.72rem;
    color: #9ca3af;
    font-style: italic;
    margin-top: 6px;
}

/* Tables */
[data-testid="stDataFrame"] {
    border: 1px solid #e5e7eb;
    border-radius: 8px;
}

/* Buttons */
[data-testid="stButton"] button {
    background-color: #1e40af !important;
    color: white !important;
    border: none !important;
    font-weight: 600 !important;
}
[data-testid="stButton"] button:hover {
    background-color: #1e3a8a !important;
}
[data-testid="stDownloadButton"] button {
    background-color: #0891b2 !important;
    color: white !important;
    border: none !important;
    font-weight: 600 !important;
}

/* Footer */
.footer-text {
    text-align: center;
    font-size: 0.74rem;
    color: #9ca3af;
    margin-top: 28px;
    padding-top: 16px;
    border-top: 1px solid #e5e7eb;
    line-height: 1.6;
}
</style>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# CONSTANTS & FORMULAS (Research-Backed)
# ════════════════════════════════════════════════════════════════════════════
# Thresholds reflect OECD/ITF (2013) headway-crowding LOS breaks.
# Demand score weights: Delay 72% (primary, Weng et al. 2023), Rainfall 28% (secondary).

HIGH_RISK_THRESHOLD = 85
LOW_THRESHOLD = 15
PSO_FLOOR = 6
COST_PER_BUS_HOUR = 15  # €/hour (NTA 2021)

def delay_component(delay_mins):
    return float(np.clip((delay_mins / 15.0) * 100, 0, 100)) * 0.72

def rain_component(rainfall_mm):
    return float(np.clip((rainfall_mm / 10.0) * 100, 0, 100)) * 0.28

def demand_score(delay_mins, rainfall_mm):
    return float(np.clip(delay_component(delay_mins) + rain_component(rainfall_mm), 0, 100))

def recommendation(ds, scheduled):
    if ds >= HIGH_RISK_THRESHOLD:
        return "Add 2", scheduled + 2, "High Risk"
    if ds <= LOW_THRESHOLD:
        opt = max(PSO_FLOOR, scheduled - 2)
        if opt == scheduled:
            return "Maintain", scheduled, "Underutilised"
        return "Reduce 2", opt, "Underutilised"
    return "Maintain", scheduled, "Moderate"

# ════════════════════════════════════════════════════════════════════════════
# ROUTE DATA (10 Irish Routes: 5 Cork + 5 Dublin)
# ════════════════════════════════════════════════════════════════════════════

ROUTES = {
    "220": {"lat": 51.8879, "lon": -8.5893, "city": "Cork", "desc": "Ballincollig", "base": 1.15},
    "202": {"lat": 51.8814, "lon": -8.5234, "city": "Cork", "desc": "Bishopstown", "base": 0.94},
    "215": {"lat": 51.8767, "lon": -8.4486, "city": "Cork", "desc": "Douglas", "base": 1.04},
    "205": {"lat": 51.8783, "lon": -8.4297, "city": "Cork", "desc": "Mahon", "base": 0.83},
    "226": {"lat": 51.8167, "lon": -8.3989, "city": "Cork", "desc": "Carrigaline", "base": 1.20},
    "46A": {"lat": 53.2896, "lon": -6.1432, "city": "Dublin", "desc": "Dún Laoghaire", "base": 1.82},
    "27": {"lat": 53.3950, "lon": -6.2730, "city": "Dublin", "desc": "Coolock", "base": 1.46},
    "44": {"lat": 53.1929, "lon": -6.1735, "city": "Dublin", "desc": "Enniskerry", "base": 1.25},
    "145": {"lat": 53.1865, "lon": -6.1145, "city": "Dublin", "desc": "Ballywaltrim", "base": 1.09},
    "25X": {"lat": 53.3572, "lon": -6.4467, "city": "Dublin", "desc": "Lucan", "base": 1.35},
}

ALL_ROUTES = list(ROUTES.keys())
IRELAND_CENTER = {"lat": 52.5, "lon": -7.5}

def classify_day(d):
    if d.day in {6, 12, 18, 24}:
        return "GAA Match Day"
    if d.strftime("%m-%d") in {"01-01", "03-17", "04-18"}:
        return "Public Holiday"
    if d.month in {2, 3, 4} and d.day <= 14:
        return "School Holiday"
    if d.dayofweek >= 5:
        return "Weekend"
    return "Normal Day"

def generate_route_hour(h, day_type, base, rng):
    is_peak = (7 <= h <= 9 or 17 <= h <= 18)
    is_off = 10 <= h <= 15
    rain = max(0, rng.normal(2.6, 1.9)) * (1.25 if day_type == "GAA Match Day" else 1.0)
    if is_peak:
        delay = rng.uniform(8, 13.5) * base + (3.0 if day_type == "GAA Match Day" else 0)
    elif is_off:
        delay = rng.uniform(0.5, 2.5) * base * (0.6 if day_type == "School Holiday" else 1.0)
    else:
        delay = rng.uniform(2.5, 5.5) * base * (0.75 if day_type == "Weekend" else 1.0)
    return round(max(0.1, delay), 1), round(max(0, rain), 1)

@st.cache_data
def build_ops_profile(start_d, end_d, routes_list, day_types):
    """Operations Manager: single focus-day hourly profile."""
    focus_date = None
    for d in pd.date_range(start_d, end_d, freq="D"):
        if classify_day(d) in day_types:
            focus_date = d
            break
    if focus_date is None:
        focus_date = pd.Timestamp(start_d)
    
    dtype = classify_day(focus_date)
    seed = int(focus_date.strftime("%Y%m%d"))
    rows = []
    for route in routes_list:
        rng = np.random.default_rng(seed + sum(ord(c) for c in route))
        for h in range(7, 20):
            delay, rain = generate_route_hour(h, dtype, ROUTES[route]["base"], rng)
            ds = demand_score(delay, rain)
            label, fleet, risk = recommendation(ds, 12)
            rows.append({
                "Route": route, "Hour": h, "Time": f"{h:02d}:00", "DayType": dtype,
                "Delay": delay, "Rainfall": rain, "Demand": ds,
                "Recommendation": label, "Scheduled": 12, "Recommended": fleet,
                "Delta": fleet - 12, "Cost": (fleet - 12) * COST_PER_BUS_HOUR, "Risk": risk,
            })
    df = pd.DataFrame(rows)
    df.attrs["focus_date"] = focus_date.date()
    df.attrs["day_type"] = dtype
    return df

@st.cache_data
def build_strategic(start_d, end_d, routes_list, day_types):
    """Strategic Planner: full period, all route-hours."""
    rows = []
    for d in pd.date_range(start_d, end_d, freq="D"):
        dtype = classify_day(d)
        if dtype not in day_types:
            continue
        seed = int(d.strftime("%Y%m%d"))
        week = ((d - pd.Timestamp(start_d)).days // 7) + 1
        for route in routes_list:
            rng = np.random.default_rng(seed + sum(ord(c) for c in route))
            for h in range(7, 20):
                delay, rain = generate_route_hour(h, dtype, ROUTES[route]["base"], rng)
                ds = demand_score(delay, rain)
                label, fleet, risk = recommendation(ds, 12)
                rows.append({
                    "Date": d.date(), "Week": week, "DayType": dtype, "Route": route,
                    "Hour": h, "Demand": ds, "Scheduled": 12, "Recommended": fleet,
                    "Delta": fleet - 12, "Cost": (fleet - 12) * COST_PER_BUS_HOUR, "Risk": risk,
                })
    return pd.DataFrame(rows)

# ════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ════════════════════════════════════════════════════════════════════════════

st.sidebar.markdown("## 🚌 OptiMove V2")
st.sidebar.caption("Fleet Intelligence Dashboard")
st.sidebar.markdown("---")

view = st.sidebar.radio("Dashboard View", ["Operations Manager", "Strategic Planner"])
st.sidebar.markdown("---")

city = st.sidebar.radio("City", ["Cork", "Dublin", "Both"], index=2, horizontal=True)
city_routes = ALL_ROUTES if city == "Both" else [r for r in ALL_ROUTES if ROUTES[r]["city"] == city]

routes_sel = st.sidebar.multiselect("Routes", city_routes, default=city_routes)
if not routes_sel:
    routes_sel = city_routes

day_types_sel = st.sidebar.multiselect(
    "Day Types",
    ["Normal Day", "GAA Match Day", "School Holiday", "Weekend", "Public Holiday"],
    default=["Normal Day", "GAA Match Day", "School Holiday", "Weekend", "Public Holiday"]
)
if not day_types_sel:
    day_types_sel = ["Normal Day", "GAA Match Day", "School Holiday", "Weekend", "Public Holiday"]

date_range = st.sidebar.date_input(
    "Date Range",
    value=(date(2026, 1, 6), date(2026, 4, 30)),
    min_value=date(2026, 1, 1),
    max_value=date(2026, 4, 30),
    format="DD/MM/YYYY"
)
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_d, end_d = date_range
else:
    start_d = end_d = date_range if not isinstance(date_range, tuple) else date_range[0]

focus_hour = st.sidebar.select_slider("Focus Hour", options=list(range(7, 20)), value=8,
                                       format_func=lambda h: f"{h:02d}:00")

# ════════════════════════════════════════════════════════════════════════════
# DATA LOADING
# ════════════════════════════════════════════════════════════════════════════

ops_df = build_ops_profile(start_d, end_d, tuple(routes_sel), tuple(day_types_sel))
strat_df = build_strategic(start_d, end_d, tuple(routes_sel), tuple(day_types_sel))

focus_date = ops_df.attrs["focus_date"]
day_type = ops_df.attrs["day_type"]

# ════════════════════════════════════════════════════════════════════════════
# HEADER
# ════════════════════════════════════════════════════════════════════════════

st.markdown(f"""
<div class="header-box">
    <h1>OptiMove Fleet Intelligence</h1>
    <p>Predictive fleet allocation for Irish bus networks</p>
</div>
""", unsafe_allow_html=True)

# Color palette (Navy/Teal/Charcoal/Gray)
NAVY = "#1e40af"
TEAL = "#0891b2"
CHARCOAL = "#1f2937"
GRAY = "#6b7280"
LIGHT_GRAY = "#e5e7eb"

PLOT_CFG = dict(
    paper_bgcolor="white", plot_bgcolor="white",
    font=dict(family="Inter", color="#374151", size=11),
    margin=dict(l=50, r=30, t=30, b=40),
)

RISK_COLORS = {"High Risk": NAVY, "Moderate": GRAY, "Underutilised": TEAL}

# [PART 2 CONTINUES IN NEXT FILE: Operations Manager & Strategic Planner views]

# ════════════════════════════════════════════════════════════════════════════
# OPERATIONS MANAGER VIEW — ALL FEATURES
# ════════════════════════════════════════════════════════════════════════════

if view == "Operations Manager":
    
    focus_routes = ops_df[ops_df["Hour"] == focus_hour].copy()
    action_routes = focus_routes[focus_routes["Delta"] != 0].sort_values("Demand", ascending=False)
    
    # ─────────────────────────────────────────────────────────────────────────
    # 4 KPI CARDS
    # RESEARCH: Cargoson (2025) — KPIs must be actionable, show scale of work
    # ─────────────────────────────────────────────────────────────────────────
    hours_needing_action = len(action_routes)
    buses_to_move = int(action_routes["Delta"].abs().sum())
    
    if len(focus_routes) > 0:
        peak_row = focus_routes.loc[focus_routes["Demand"].idxmax()]
        peak_label = f"{peak_row['Route']} at {focus_hour:02d}:00"
        peak_sub = f"Demand {peak_row['Demand']:.1f}, highest in network"
    else:
        peak_label = "—"
        peak_sub = "No data"
    
    pso_breaches = len(focus_routes[focus_routes["Recommended"] < PSO_FLOOR])
    pso_status = "All clear" if pso_breaches == 0 else f"{pso_breaches} breach(es)"
    
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f"""<div class="kpi-card alert">
            <div class="kpi-label">Hours Needing Action</div>
            <div class="kpi-value">{hours_needing_action}</div>
            <div class="kpi-subtitle">Route-hours where fleet differs from scheduled</div>
        </div>""", unsafe_allow_html=True)
    with k2:
        st.markdown(f"""<div class="kpi-card positive">
            <div class="kpi-label">Buses to Reallocate</div>
            <div class="kpi-value">{buses_to_move}</div>
            <div class="kpi-subtitle">Total vehicle moves recommended</div>
        </div>""", unsafe_allow_html=True)
    with k3:
        st.markdown(f"""<div class="kpi-card alert">
            <div class="kpi-label">Highest-Pressure</div>
            <div class="kpi-value" style="font-size:1.3rem;">{peak_label}</div>
            <div class="kpi-subtitle">{peak_sub}</div>
        </div>""", unsafe_allow_html=True)
    with k4:
        card_class = "alert" if pso_breaches > 0 else "positive"
        st.markdown(f"""<div class="kpi-card {card_class}">
            <div class="kpi-label">PSO Floor Status</div>
            <div class="kpi-value" style="font-size:1.3rem;">{pso_status}</div>
            <div class="kpi-subtitle">Minimum {PSO_FLOOR} buses/route-hour</div>
        </div>""", unsafe_allow_html=True)
    
    st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
    
    # ─────────────────────────────────────────────────────────────────────────
    # ROUTE PRESSURE MAP
    # RESEARCH: Efficient Scheduling (2025) — Visual risk overlay helps dispatch
    # ─────────────────────────────────────────────────────────────────────────
    st.markdown('<div class="panel"><div class="panel-title">Route Pressure Locator</div>', unsafe_allow_html=True)
    
    map_df = focus_routes.copy()
    map_df["lat"] = map_df["Route"].map(lambda r: ROUTES[r]["lat"])
    map_df["lon"] = map_df["Route"].map(lambda r: ROUTES[r]["lon"])
    
    fig_map = go.Figure()
    for risk, color in RISK_COLORS.items():
        sub = map_df[map_df["Risk"] == risk]
        if not sub.empty:
            fig_map.add_trace(go.Scattermapbox(
                lat=sub["lat"], lon=sub["lon"], mode="markers",
                marker=dict(size=sub["Demand"].clip(15) / 1.8, color=color, opacity=0.88),
                text=sub["Route"], name=risk,
                customdata=sub[["Demand", "Recommendation"]].values,
                hovertemplate="<b>Route %{text}</b><br>Risk band: " + risk + "<br>Demand score: %{customdata[0]:.1f}<br>Recommended action: %{customdata[1]}<extra></extra>"
            ))
    
    if city == "Both":
        center, zoom = IRELAND_CENTER, 6.3
    elif city == "Cork":
        center, zoom = {"lat": 51.87, "lon": -8.5}, 10
    else:
        center, zoom = {"lat": 53.3, "lon": -6.25}, 9.5
    
    fig_map.update_layout(
        mapbox_style="carto-positron",
        mapbox=dict(center=center, zoom=zoom),
        height=360, margin=dict(l=0, r=0, t=0, b=0), showlegend=True,
        legend=dict(title=dict(text="Risk band", font=dict(size=10)), x=0.01, y=0.99, bgcolor="rgba(255,255,255,0.92)", bordercolor=LIGHT_GRAY, borderwidth=1, font=dict(size=10)),
        uirevision=f"{city}_{','.join(sorted(routes_sel))}"
    )
    st.plotly_chart(fig_map, use_container_width=True, config={"scrollZoom": True, "displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)
    
    # ─────────────────────────────────────────────────────────────────────────
    # DEMAND SCORE TREND
    # RESEARCH: Weng et al. (2023) — Know which hours are critical
    # ─────────────────────────────────────────────────────────────────────────
    st.markdown('<div class="panel"><div class="panel-title">Demand Score Trend</div>', unsafe_allow_html=True)
    
    hourly = ops_df.groupby(["Hour", "Time"], as_index=False)["Demand"].mean()
    # Derive the prevailing band + action per hour for richer hover context
    def _band_action(score):
        if score >= HIGH_RISK_THRESHOLD:
            return "High Risk", "Add buses"
        if score <= LOW_THRESHOLD:
            return "Underutilised", "Reduce buses"
        return "Moderate", "Maintain fleet"
    hourly[["Band", "Action"]] = hourly["Demand"].apply(lambda s: pd.Series(_band_action(s)))
    
    fig_trend = go.Figure()
    fig_trend.add_trace(go.Scatter(
        x=hourly["Time"], y=hourly["Demand"], mode="lines+markers",
        line=dict(color=NAVY, width=3), marker=dict(size=7),
        fill="tozeroy", fillcolor="rgba(30,64,175,0.07)", name="Network demand",
        customdata=hourly[["Band", "Action"]].values,
        hovertemplate="<b>%{x}</b><br>Network demand score: %{y:.1f}<br>Band: %{customdata[0]}<br>Recommended action: %{customdata[1]}<extra></extra>"
    ))
    fig_trend.add_hline(y=85, line_dash="dash", line_color=CHARCOAL)
    fig_trend.add_hline(y=15, line_dash="dash", line_color=TEAL)
    # Legend-only entries explaining the threshold lines
    fig_trend.add_trace(go.Scatter(x=[None], y=[None], mode="lines",
        line=dict(color=CHARCOAL, width=1.5, dash="dash"), name="High-risk threshold (85)"))
    fig_trend.add_trace(go.Scatter(x=[None], y=[None], mode="lines",
        line=dict(color=TEAL, width=1.5, dash="dash"), name="Reduction threshold (15)"))
    
    hours_str = [f"{h:02d}:00" for h in range(7, 20)]
    if f"{focus_hour:02d}:00" in hours_str:
        fig_trend.add_vline(x=hours_str.index(f"{focus_hour:02d}:00"), line_dash="dot", line_color=GRAY)
    
    fig_trend.update_layout(
        xaxis=dict(title="Hour of day", showgrid=False, ticks="outside", tickcolor="#cbd5e1"),
        yaxis=dict(title="Demand score", range=[0, 105], showgrid=True, gridcolor="#f1f5f9", ticks="outside", tickcolor="#cbd5e1"),
        height=300, showlegend=True,
        legend=dict(orientation="h", yanchor="top", y=1.14, xanchor="left", x=0, font=dict(size=9)),
        paper_bgcolor="white", plot_bgcolor="white",
        font=dict(family="Inter", color="#374151", size=11),
        margin=dict(l=50, r=30, t=44, b=40)
    )
    st.plotly_chart(fig_trend, use_container_width=True, config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)
    
    # ─────────────────────────────────────────────────────────────────────────
    # TODAY'S PLAN + WHY THIS RECOMMENDATION (two columns)
    # RESEARCH: Cargoson (2025) actionable; Liang et al. (2024) explainability
    # ─────────────────────────────────────────────────────────────────────────
    col_left, col_right = st.columns([1.3, 1])
    
    with col_left:
        st.markdown('<div class="panel"><div class="panel-title">Recommended Reallocation Schedule</div>', unsafe_allow_html=True)
        
        if len(action_routes) == 0:
            st.info("No reallocation is required at this hour; all selected routes fall within the moderate operating band.")
        else:
            plan = action_routes[["Route", "Demand", "Risk", "Scheduled", "Recommended", "Delta"]].copy()
            plan.insert(0, "Apply", True)
            plan.columns = ["Apply", "Route", "Demand", "Risk", "Current fleet", "Recommended fleet", "Change"]
            plan["Demand"] = plan["Demand"].round(1)
            
            edited = st.data_editor(plan, column_config={
                "Apply": st.column_config.CheckboxColumn("Apply", width="small"),
                "Route": st.column_config.TextColumn("Route", disabled=True, width="small"),
                "Demand": st.column_config.NumberColumn("Demand score", format="%.1f", disabled=True),
                "Risk": st.column_config.TextColumn("Risk band", disabled=True),
                "Current fleet": st.column_config.NumberColumn("Current fleet", format="%d", disabled=True),
                "Recommended fleet": st.column_config.NumberColumn("Recommended fleet", format="%d", disabled=True),
                "Change": st.column_config.NumberColumn("Change", format="%+d", disabled=True),
            }, hide_index=True, use_container_width=True, height=300)
            
            csv = edited.to_csv(index=False)
            st.download_button("Download schedule (CSV)", csv, f"optimove_plan_{focus_date.strftime('%d_%m_%Y')}.csv", "text/csv", use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col_right:
        st.markdown('<div class="panel"><div class="panel-title">Demand Score Decomposition</div>', unsafe_allow_html=True)
        
        sel_route = st.selectbox("Route", routes_sel, label_visibility="collapsed")
        sel = focus_routes[focus_routes["Route"] == sel_route]
        
        if not sel.empty:
            r = sel.iloc[0]
            delay_contrib = delay_component(r["Delay"])
            rain_contrib = rain_component(r["Rainfall"])
            
            st.markdown(f'<div style="font-size:0.85rem; color:#374151; margin-bottom:10px;"><b>Route {sel_route}</b> &nbsp;|&nbsp; {ROUTES[sel_route]["desc"]} &nbsp;|&nbsp; {focus_hour:02d}:00</div>', unsafe_allow_html=True)
            
            # Two horizontal bars; categories on the y-axis (PPT R7: not a legend)
            fig_decomp = go.Figure(go.Bar(
                y=["Delay", "Rainfall"],
                x=[delay_contrib, rain_contrib],
                orientation="h",
                marker_color=NAVY,
                text=[f"{delay_contrib:.1f}", f"{rain_contrib:.1f}"],
                textposition="outside", cliponaxis=False,
                customdata=[[r["Delay"], 0.72], [r["Rainfall"], 0.28]],
                hovertemplate="<b>%{y}</b><br>Input %{customdata[0]:.1f}, weight %{customdata[1]}<br>Contribution: %{x:.1f}<extra></extra>"
            ))
            fig_decomp.add_vline(x=85, line_dash="dash", line_color=CHARCOAL, line_width=1,
                                 annotation_text="High risk 85", annotation_position="top", annotation_font_size=9)
            fig_decomp.add_vline(x=15, line_dash="dash", line_color=GRAY, line_width=1,
                                 annotation_text="Reduce 15", annotation_position="top", annotation_font_size=9)
            fig_decomp.update_layout(
                xaxis=dict(title="Contribution to demand score", range=[0, 100], showgrid=True, gridcolor="#f1f5f9", ticks="outside", tickcolor="#cbd5e1"),
                yaxis=dict(title="", ticks=""),
                height=300, showlegend=False,
                paper_bgcolor="white", plot_bgcolor="white",
                font=dict(family="Inter", color="#374151", size=11),
                margin=dict(l=70, r=40, t=40, b=40)
            )
            st.plotly_chart(fig_decomp, use_container_width=True, config={"displayModeBar": False})
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ─────────────────────────────────────────────────────────────────────────
    # ROUTE × HOUR HEATMAP
    # RESEARCH: UITP (2025) — Identify chronic pressure patterns
    # ─────────────────────────────────────────────────────────────────────────
    st.markdown('<div class="panel"><div class="panel-title">Route &times; Hour Pressure Matrix</div>', unsafe_allow_html=True)
    
    key_hours = [7, 8, 9, 12, 17, 18]
    heat_data = ops_df[ops_df["Hour"].isin(key_hours)].pivot_table(
        index="Route", columns="Hour", values="Demand", aggfunc="mean"
    )
    ordered_routes = [r for r in routes_sel if r in heat_data.index]
    heat_data = heat_data.reindex(ordered_routes)
    route_labels = [f"Route {r}" for r in ordered_routes]
    
    fig_heat = go.Figure(data=go.Heatmap(
        z=heat_data.values,
        x=[f"{h:02d}:00" for h in heat_data.columns],
        y=route_labels,
        zmin=0, zmax=100,
        colorscale=[
            [0.00, "#eff6ff"],
            [0.15, "#bfdbfe"],
            [0.45, "#93c5fd"],
            [0.85, "#3b82f6"],
            [1.00, NAVY],
        ],
        text=heat_data.values, texttemplate="%{text:.0f}",
        textfont=dict(size=12, family="Inter"),
        xgap=4, ygap=4,
        colorbar=dict(
            title=dict(text="Demand", side="right", font=dict(size=11)),
            tickvals=[0, 25, 50, 75, 100],
            thickness=14, len=0.9, outlinewidth=0
        ),
        hovertemplate="<b>%{y}</b> at %{x}<br>Demand score: %{z:.1f}<extra></extra>"
    ))
    n_routes = max(len(route_labels), 1)
    fig_heat.update_layout(
        height=max(280, 50 * n_routes + 70),
        xaxis=dict(side="top", title="", type="category", fixedrange=True),
        yaxis=dict(
            title="", type="category", fixedrange=True,
            categoryorder="array", categoryarray=list(reversed(route_labels))
        ),
        paper_bgcolor="white", plot_bgcolor="white",
        font=dict(family="Inter", color="#374151", size=11),
        margin=dict(l=70, r=20, t=34, b=20)
    )
    st.plotly_chart(fig_heat, use_container_width=True, config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# STRATEGIC PLANNER VIEW — ALL FEATURES
# ════════════════════════════════════════════════════════════════════════════

else:
    
    if strat_df.empty:
        st.warning("No data for selected filters.")
        st.stop()
    
    # ─────────────────────────────────────────────────────────────────────────
    # 4 KPI CARDS
    # RESEARCH: Liang et al. (2024) — bottom-line financial + service metrics
    # ─────────────────────────────────────────────────────────────────────────
    # Cost = (fleet - 12) * COST_PER_BUS_HOUR.
    # Reductions (Delta<0) produce negative Cost  -> money saved (positive saving).
    # Additions  (Delta>0) produce positive Cost  -> money spent (operating expense).
    saving_from_reductions = -strat_df.loc[strat_df["Delta"] < 0, "Cost"].sum()  # negate -> positive saving
    expense_from_additions = strat_df.loc[strat_df["Delta"] > 0, "Cost"].sum()    # already positive
    net_total = saving_from_reductions - expense_from_additions
    n_days = (end_d - start_d).days + 1
    net_per_day = net_total / max(n_days, 1)
    annualised = net_per_day * 300
    avg_demand = strat_df["Demand"].mean()
    high_risk_hours = len(strat_df[strat_df["Demand"] >= HIGH_RISK_THRESHOLD])
    
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        cls = "positive" if net_per_day >= 0 else "alert"
        st.markdown(f"""<div class="kpi-card {cls}">
            <div class="kpi-label">Net Daily Saving</div>
            <div class="kpi-value">€{net_per_day:,.0f}</div>
            <div class="kpi-subtitle">Off-peak cuts minus peak additions</div>
        </div>""", unsafe_allow_html=True)
    with k2:
        st.markdown(f"""<div class="kpi-card positive">
            <div class="kpi-label">Annualised Projection</div>
            <div class="kpi-value">€{annualised:,.0f}</div>
            <div class="kpi-subtitle">Net daily saving extrapolated across 300 operating days</div>
        </div>""", unsafe_allow_html=True)
    with k3:
        st.markdown(f"""<div class="kpi-card neutral">
            <div class="kpi-label">Average Demand</div>
            <div class="kpi-value">{avg_demand:.1f}</div>
            <div class="kpi-subtitle">Network baseline pressure</div>
        </div>""", unsafe_allow_html=True)
    with k4:
        st.markdown(f"""<div class="kpi-card alert">
            <div class="kpi-label">High-Risk Windows</div>
            <div class="kpi-value">{high_risk_hours:,}</div>
            <div class="kpi-subtitle">Route-hours exceeding the high-risk threshold of 85</div>
        </div>""", unsafe_allow_html=True)
    
    st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
    
    # ─────────────────────────────────────────────────────────────────────────
    # DEMAND BY WEEK & DAY TYPE  +  DEMAND BY DAY TYPE (two columns)
    # RESEARCH: Devasurendra et al. (2025); OECD/ITF (2013) — day-type variance
    # ─────────────────────────────────────────────────────────────────────────
    col1, col2 = st.columns(2)
    
    DAY_COLORS = {
        "Normal Day": NAVY, "GAA Match Day": CHARCOAL, "School Holiday": TEAL,
        "Weekend": GRAY, "Public Holiday": "#0e7490"
    }
    
    with col1:
        st.markdown('<div class="panel"><div class="panel-title">Demand by Week and Day Type</div>', unsafe_allow_html=True)
        
        week_day = strat_df.groupby(["Week", "DayType"], as_index=False)["Demand"].mean()
        fig_week = go.Figure()
        for dt in day_types_sel:
            sub = week_day[week_day["DayType"] == dt]
            if not sub.empty:
                fig_week.add_trace(go.Scatter(
                    x=sub["Week"], y=sub["Demand"], mode="lines+markers",
                    name=dt, line=dict(color=DAY_COLORS.get(dt, GRAY), width=2), marker=dict(size=5),
                    hovertemplate="<b>" + dt + "</b><br>Week %{x}<br>Mean demand: %{y:.1f}<extra></extra>"
                ))
        fig_week.update_layout(
            xaxis=dict(title="Week of period", showgrid=False, ticks="outside", tickcolor="#cbd5e1", dtick=1),
            yaxis=dict(title="Mean demand score", range=[0, 100], showgrid=True, gridcolor="#f1f5f9", ticks="outside", tickcolor="#cbd5e1"),
            height=300, showlegend=True,
            legend=dict(orientation="h", yanchor="top", y=1.12, xanchor="left", x=0, font=dict(size=9), bgcolor="rgba(255,255,255,0)"),
            paper_bgcolor="white", plot_bgcolor="white",
            font=dict(family="Inter", color="#374151", size=11),
            margin=dict(l=50, r=20, t=40, b=40)
        )
        st.plotly_chart(fig_week, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="panel"><div class="panel-title">Mean Demand by Day Type</div>', unsafe_allow_html=True)
        
        day_avg = strat_df.groupby("DayType", as_index=False)["Demand"].mean().sort_values("Demand", ascending=False)
        fig_day = go.Figure(go.Bar(
            x=day_avg["Demand"], y=day_avg["DayType"], orientation="h",
            marker_color=NAVY,
            text=day_avg["Demand"].round(1), textposition="outside", cliponaxis=False,
            hovertemplate="<b>%{y}</b><br>Mean demand score: %{x:.1f}<extra></extra>"
        ))
        fig_day.update_layout(
            xaxis=dict(title="Mean demand score", range=[0, 100], showgrid=True, gridcolor="#f1f5f9", ticks="outside", tickcolor="#cbd5e1"),
            yaxis=dict(title="", autorange="reversed", ticks=""),
            height=300, showlegend=False,
            paper_bgcolor="white", plot_bgcolor="white",
            font=dict(family="Inter", color="#374151", size=11),
            margin=dict(l=110, r=40, t=20, b=40)
        )
        st.plotly_chart(fig_day, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ─────────────────────────────────────────────────────────────────────────
    # RISK PIE  +  SCHEDULED VS RECOMMENDED FLEET (two columns)
    # RESEARCH: Devasurendra (2025) risk distribution; Liang (2024) fleet trade-off
    # ─────────────────────────────────────────────────────────────────────────
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown('<div class="panel"><div class="panel-title">Risk Band Composition</div>', unsafe_allow_html=True)
        
        bands = strat_df["Risk"].value_counts().reindex(["High Risk", "Moderate", "Underutilised"], fill_value=0)
        total_b = bands.sum()
        pct = (bands / total_b * 100).round(1)
        # Horizontal bars (length encoding) instead of a pie, per Few / Slide 36 & 17
        order = ["High Risk", "Moderate", "Underutilised"]
        band_colors = {"High Risk": NAVY, "Moderate": GRAY, "Underutilised": TEAL}
        max_band = max(bands[o] for o in order)
        fig_band = go.Figure(go.Bar(
            x=[bands[o] for o in order],
            y=order,
            orientation="h",
            marker_color=[band_colors[o] for o in order],
            text=[f"{pct[o]:.0f}%  ({bands[o]:,})" for o in order],
            textposition="outside", cliponaxis=False,
            customdata=[[pct[o]] for o in order],
            hovertemplate="<b>%{y}</b><br>%{x:,} route-hours (%{customdata[0]:.1f}%)<extra></extra>"
        ))
        fig_band.update_layout(
            height=300,
            xaxis=dict(title="Route-hours", range=[0, max_band * 1.18], showgrid=True, gridcolor="#f1f5f9", ticks="outside", tickcolor="#cbd5e1"),
            yaxis=dict(title="", autorange="reversed", ticks=""),
            showlegend=False,
            paper_bgcolor="white", plot_bgcolor="white",
            font=dict(family="Inter", color="#374151", size=11),
            margin=dict(l=100, r=40, t=20, b=40)
        )
        st.plotly_chart(fig_band, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="panel"><div class="panel-title">Scheduled vs Recommended Fleet</div>', unsafe_allow_html=True)
        
        fleet_hourly = strat_df.groupby("Hour", as_index=False).agg(
            Scheduled=("Scheduled", "mean"), Recommended=("Recommended", "mean")
        )
        fleet_hourly["TimeLabel"] = fleet_hourly["Hour"].apply(lambda h: f"{h:02d}:00")
        fig_fleet = go.Figure()
        fig_fleet.add_trace(go.Scatter(
            x=fleet_hourly["TimeLabel"], y=fleet_hourly["Scheduled"], mode="lines",
            line=dict(color=GRAY, width=2, dash="dash"), name="Scheduled fleet",
            hovertemplate="<b>Scheduled</b><br>%{x}<br>%{y:.1f} vehicles<extra></extra>"
        ))
        fig_fleet.add_trace(go.Scatter(
            x=fleet_hourly["TimeLabel"], y=fleet_hourly["Recommended"], mode="lines+markers",
            line=dict(color=NAVY, width=2.5), marker=dict(size=5),
            fill="tonexty", fillcolor="rgba(30,64,175,0.08)", name="Recommended fleet",
            hovertemplate="<b>Recommended</b><br>%{x}<br>%{y:.1f} vehicles<extra></extra>"
        ))
        fig_fleet.update_layout(
            xaxis=dict(title="Hour of day", showgrid=False, ticks="outside", tickcolor="#cbd5e1"),
            yaxis=dict(title="Mean fleet size (vehicles)", rangemode="tozero", showgrid=True, gridcolor="#f1f5f9", ticks="outside", tickcolor="#cbd5e1"),
            height=300, showlegend=True,
            legend=dict(orientation="h", yanchor="top", y=1.12, xanchor="left", x=0, font=dict(size=9), bgcolor="rgba(255,255,255,0)"),
            paper_bgcolor="white", plot_bgcolor="white",
            font=dict(family="Inter", color="#374151", size=11),
            margin=dict(l=50, r=20, t=40, b=40)
        )
        st.plotly_chart(fig_fleet, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ─────────────────────────────────────────────────────────────────────────
    # SAVINGS BREAKDOWN  +  ROUTE PROFILE (two columns)
    # RESEARCH: Cargoson (2025) savings source; Weng (2023) route provisioning
    # ─────────────────────────────────────────────────────────────────────────
    col5, col6 = st.columns(2)
    
    with col5:
        st.markdown('<div class="panel"><div class="panel-title">Cost Composition</div>', unsafe_allow_html=True)
        
        fig_sav = go.Figure()
        fig_sav = go.Figure(go.Bar(
            y=["Saving (reductions)", "Expense (additions)", "Net effect"],
            x=[saving_from_reductions, -expense_from_additions, net_total],
            orientation="h",
            marker_color=[TEAL, CHARCOAL, NAVY if net_total >= 0 else CHARCOAL],
            text=[f"€{saving_from_reductions:,.0f}", f"-€{expense_from_additions:,.0f}", f"€{net_total:,.0f}"],
            textposition="outside", cliponaxis=False,
            hovertemplate="<b>%{y}</b><br>€%{x:,.0f} over the period<extra></extra>"
        ))
        fig_sav.add_vline(x=0, line_color=GRAY, line_width=1)
        fig_sav.update_layout(
            xaxis=dict(title="Cost impact over period (€)", showgrid=True, gridcolor="#f1f5f9", ticks="outside", tickcolor="#cbd5e1", zeroline=False),
            yaxis=dict(title="", autorange="reversed", ticks=""),
            height=300, showlegend=False,
            paper_bgcolor="white", plot_bgcolor="white",
            font=dict(family="Inter", color="#374151", size=11),
            margin=dict(l=130, r=60, t=20, b=40)
        )
        st.plotly_chart(fig_sav, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col6:
        st.markdown('<div class="panel"><div class="panel-title">Single-Route Hourly Profile</div>', unsafe_allow_html=True)
        
        profile_route = st.selectbox("Route", routes_sel, key="profile_route", label_visibility="collapsed")
        prof = strat_df[strat_df["Route"] == profile_route].groupby("Hour", as_index=False).agg(
            Demand=("Demand", "mean"), Cost=("Cost", "mean")
        )
        prof["TimeLabel"] = prof["Hour"].apply(lambda h: f"{h:02d}:00")
        
        fig_prof = go.Figure()
        fig_prof.add_trace(go.Bar(
            x=prof["TimeLabel"], y=prof["Demand"], name="Mean demand (left axis)",
            marker_color=NAVY, opacity=0.85, yaxis="y",
            hovertemplate="<b>%{x}</b><br>Mean demand score: %{y:.1f}<extra></extra>"
        ))
        fig_prof.add_trace(go.Scatter(
            x=prof["TimeLabel"], y=prof["Cost"], name="Mean cost impact (right axis)",
            mode="lines+markers", line=dict(color=TEAL, width=2.5), marker=dict(size=5), yaxis="y2",
            hovertemplate="<b>%{x}</b><br>Mean cost impact: €%{y:.0f}<extra></extra>"
        ))
        fig_prof.update_layout(
            xaxis=dict(title="Hour of day", showgrid=False, ticks="outside", tickcolor="#cbd5e1"),
            yaxis=dict(title="Demand score", range=[0, 100], showgrid=True, gridcolor="#f1f5f9", ticks="outside", tickcolor="#cbd5e1"),
            yaxis2=dict(title="Cost impact (€)", overlaying="y", side="right", showgrid=False, ticks="outside", tickcolor="#cbd5e1"),
            height=300, showlegend=True,
            legend=dict(orientation="h", yanchor="top", y=1.12, xanchor="left", x=0, font=dict(size=9), bgcolor="rgba(255,255,255,0)"),
            paper_bgcolor="white", plot_bgcolor="white",
            font=dict(family="Inter", color="#374151", size=11),
            margin=dict(l=50, r=50, t=40, b=40)
        )
        st.plotly_chart(fig_prof, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ─────────────────────────────────────────────────────────────────────────
    # PLANNING SCENARIO TABLE + CSV
    # RESEARCH: Industry guides (2025) — exportable scenarios for board review
    # ─────────────────────────────────────────────────────────────────────────
    st.markdown(f'<div class="panel"><div class="panel-title">Planning Scenario at {focus_hour:02d}:00</div>', unsafe_allow_html=True)
    
    scenario = strat_df[strat_df["Hour"] == focus_hour].groupby("Route", as_index=False).agg(
        Demand=("Demand", "mean"), Risk=("Risk", "first"),
        Scheduled=("Scheduled", "first"), Recommended=("Recommended", "first"), Delta=("Delta", "first")
    )
    scenario = scenario[scenario["Delta"] != 0].sort_values("Demand", ascending=False)
    
    if len(scenario) > 0:
        scenario.insert(0, "Apply", True)
        scenario["Demand"] = scenario["Demand"].round(1)
        scenario.columns = ["Apply", "Route", "Demand", "Risk", "Current fleet", "Recommended fleet", "Change"]
        
        edited_s = st.data_editor(scenario, column_config={
            "Apply": st.column_config.CheckboxColumn("Apply", width="small"),
            "Route": st.column_config.TextColumn("Route", disabled=True, width="small"),
            "Demand": st.column_config.NumberColumn("Mean demand score", format="%.1f", disabled=True),
            "Risk": st.column_config.TextColumn("Risk band", disabled=True),
            "Current fleet": st.column_config.NumberColumn("Current fleet", format="%d", disabled=True),
            "Recommended fleet": st.column_config.NumberColumn("Recommended fleet", format="%d", disabled=True),
            "Change": st.column_config.NumberColumn("Change", format="%+d", disabled=True),
        }, hide_index=True, use_container_width=True)
        
        csv_s = edited_s.to_csv(index=False)
        st.download_button("Download scenario (CSV)", csv_s, f"optimove_scenario_{focus_hour:02d}00_{focus_date.strftime('%d_%m_%Y')}.csv", "text/csv", use_container_width=True)
    else:
        st.info("No fleet changes are recommended at this hour for the current selection.")
    
    st.markdown('</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# FOOTER
# ════════════════════════════════════════════════════════════════════════════

st.markdown(f"""
<div class="footer-text">
Period: {start_d.strftime('%d/%m/%Y')} to {end_d.strftime('%d/%m/%Y')} &nbsp;|&nbsp; Focus Hour: {focus_hour:02d}:00 &nbsp;|&nbsp; Operating cost €{COST_PER_BUS_HOUR}/bus-hour &nbsp;|&nbsp; Minimum service floor: {PSO_FLOOR} buses/route-hour
</div>
""", unsafe_allow_html=True)