import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import date

st.set_page_config(
    page_title="OptiMove: Fleet Demand & Allocation",
    page_icon="🚌",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: #F8FAFC !important;
}

.block-container {
    padding: 0.9rem 1rem 1rem 1rem !important;
    max-width: 100%;
}

div[data-testid="stSidebar"] {
    background: #0F172A !important;
}

div[data-testid="stSidebar"] * {
    color: #E2E8F0 !important;
}

div[data-testid="stSidebar"] h2, div[data-testid="stSidebar"] h3 {
    color: #FFFFFF !important;
}

div[data-testid="stSidebar"] hr {
    border-color: rgba(255,255,255,0.12) !important;
}

.premium-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 1rem;
    background: linear-gradient(135deg, #123524 0%, #0F172A 100%);
    color: #FFFFFF;
    padding: 16px 18px;
    border-radius: 12px;
    margin-bottom: 14px;
    border: 1px solid rgba(255,255,255,0.08);
    box-shadow: 0 6px 18px rgba(15,23,42,0.08);
}

.kpi-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
    margin-bottom: 14px;
}

.kpi-card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-left: 4px solid #166534;
    padding: 13px 14px;
    border-radius: 12px;
    box-shadow: 0 1px 4px rgba(15,23,42,0.05);
    min-height: 92px;
}

.kpi-card.alert { border-left-color: #DC2626; }
.kpi-card.warn  { border-left-color: #D97706; }
.kpi-card.ok    { border-left-color: #166534; }

.kpi-title {
    color: #64748B;
    font-size: 0.68rem;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}

.kpi-value {
    color: #0F172A;
    font-size: 1.42rem;
    font-weight: 800;
    margin: 4px 0 2px 0;
    line-height: 1.1;
}

.kpi-tag {
    font-size: 0.75rem;
    color: #475569;
    line-height: 1.35;
}

/* Static/secondary text (st.caption) - match the .kpi-tag/.formula-subnote
   tone so captions read as part of the same visual language rather than
   Streamlit's default caption styling. */
div[data-testid="stCaptionContainer"],
div[data-testid="stCaptionContainer"] p {
    color: #64748B !important;
    font-size: 0.8rem !important;
}

/* Equal-height panels within a row of columns. Streamlit columns don't
   stretch their content by default, so a shorter panel (e.g. Today's Plan
   when few routes are actionable) leaves a page-background gap below it
   while its taller sibling (Why This Recommendation) continues - this
   makes both panels in a row fill the row's full height instead. */
div[data-testid="stHorizontalBlock"] {
    align-items: stretch;
}
div[data-testid="column"] {
    display: flex;
    flex-direction: column;
}
div[data-testid="column"] > div {
    width: 100%;
    display: flex;
    flex-direction: column;
    flex: 1;
}
div[data-testid="column"] div[data-testid="stVerticalBlock"] {
    display: flex;
    flex-direction: column;
    flex: 1;
    height: 100%;
}
div[data-testid="column"] .panel {
    flex: 1;
    display: flex;
    flex-direction: column;
}

.panel {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    padding: 12px 13px;
    box-shadow: 0 1px 4px rgba(15,23,42,0.04);
    margin-bottom: 12px;
}

.panel-title {
    font-size: 0.82rem;
    font-weight: 800;
    color: #0F172A;
    margin-bottom: 10px;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}

.smallcap {
    font-size: 0.72rem;
    text-transform: uppercase;
    color: #CBD5E1;
    letter-spacing: 0.06em;
    font-weight: 800;
}

div[data-testid="stDataFrame"] {
    border: 1px solid #E2E8F0;
    border-radius: 10px;
    overflow: hidden;
}

/* Formula breakdown */
.formula-box {
    background: #F8FAFC;
    border: 1px solid #E2E8F0;
    border-radius: 10px;
    padding: 14px 16px;
    margin-top: 10px;
}
.formula-row {
    display: flex;
    align-items: center;
    gap: 10px;
    margin: 6px 0;
    font-size: 0.88rem;
}
.formula-label { color: #475569; min-width: 170px; }
.formula-bar-track {
    flex: 1;
    height: 10px;
    background: #E2E8F0;
    border-radius: 6px;
    overflow: hidden;
    position: relative;
    display: flex;
}
.formula-bar-fill {
    height: 100%;
    flex: 0 0 auto;
}
.formula-threshold {
    position: absolute;
    top: -2px;
    bottom: -2px;
    width: 2px;
    background: #94A3B8;
    z-index: 2;
}
.formula-value {
    min-width: 64px;
    text-align: right;
    font-weight: 700;
    color: #0F172A;
    font-family: monospace;
}
.formula-subnote {
    font-size: 0.72rem;
    color: #94A3B8;
    margin: -2px 0 4px 180px;
}
.formula-verdict {
    margin-top: 10px;
    padding: 10px 12px;
    border-radius: 8px;
    font-size: 0.88rem;
    line-height: 1.5;
}

/* Accept / Override action buttons */
div[data-testid="stButton"] button[kind="primary"] {
    background-color: #166534 !important;
    border-color: #166534 !important;
    color: #FFFFFF !important;
}
div[data-testid="stButton"] button[kind="primary"]:hover {
    background-color: #14532D !important;
    border-color: #14532D !important;
}

/* Map size legend */
.size-legend {
    display: flex;
    align-items: center;
    gap: 14px;
    flex-wrap: wrap;
    padding: 8px 10px 2px 10px;
    font-size: 0.76rem;
    color: #475569;
}
.size-legend-title {
    font-weight: 800;
    text-transform: uppercase;
    font-size: 0.66rem;
    letter-spacing: 0.06em;
    color: #94A3B8;
}
.size-legend-item {
    display: flex;
    align-items: center;
    gap: 5px;
}
.size-legend-dot {
    display: inline-block;
    border-radius: 50%;
    background: #94A3B8;
    flex-shrink: 0;
}
.size-legend-note {
    margin-left: auto;
    color: #94A3B8;
    font-size: 0.72rem;
}
</style>
""", unsafe_allow_html=True)

# ────────────────────────────────────────────────────────────────────────────
# Demand-score formula (single source of truth)
#   Demand Score = 0.72 x (Delay/15 x 100) + 0.28 x (Rainfall/10 x 100), clipped 0-100
#   >= 85  -> High Risk    -> Add 2 buses
#   <= 15  -> Underutilised -> Reduce 2 buses (floor: 6)
#   else   -> Moderate     -> Maintain scheduled fleet
# ────────────────────────────────────────────────────────────────────────────
HIGH_RISK_THRESHOLD = 85
LOW_THRESHOLD = 15
PSO_FLOOR = 6
COST_PER_BUS_HOUR = 15  # EUR, NTA 2021 PSO operating-cost benchmark

def delay_component(delay_mins):
    return float(np.clip((delay_mins / 15.0) * 100, 0, 100)) * 0.72

def rain_component(rainfall_mm):
    return float(np.clip((rainfall_mm / 10.0) * 100, 0, 100)) * 0.28

def demand_score(delay_mins, rainfall_mm):
    return float(np.clip(delay_component(delay_mins) + rain_component(rainfall_mm), 0, 100))

def recommendation(ds, scheduled):
    if ds >= HIGH_RISK_THRESHOLD:
        return "Add 2 buses", scheduled + 2, "High Risk"
    if ds <= LOW_THRESHOLD:
        optimised = max(PSO_FLOOR, scheduled - 2)
        if optimised == scheduled:
            return "Maintain — already at floor", scheduled, "Underutilised"
        return "Reduce 2 buses", optimised, "Underutilised"
    return "Maintain scheduled fleet", scheduled, "Moderate"


# ── Route reference data ───────────────────────────────────────────────────────
# Route reference data — city, desc, base_delay and route_code match the
# notebook's ROUTES dict exactly (Appendix D.3). 'base' is derived from
# base_delay relative to the network average (116.5s), so each route's
# simulated delay scales the same way it does in the notebook's own model.
route_profiles = {
    # Cork
    "220": {"lat": 51.8879, "lon": -8.5893, "city": "Cork",   "desc": "Ballincollig → City Centre",
            "base_delay": 110, "route_code": "5352_122182"},
    "202": {"lat": 51.8814, "lon": -8.5234, "city": "Cork",   "desc": "Bishopstown → City Centre",
            "base_delay": 90,  "route_code": "5352_122183"},
    "215": {"lat": 51.8767, "lon": -8.4486, "city": "Cork",   "desc": "Douglas → City Centre",
            "base_delay": 100, "route_code": "5352_122184"},
    "205": {"lat": 51.8783, "lon": -8.4297, "city": "Cork",   "desc": "Mahon → City Centre",
            "base_delay": 80,  "route_code": "5352_122185"},
    "226": {"lat": 51.8167, "lon": -8.3989, "city": "Cork",   "desc": "Carrigaline → City Centre",
            "base_delay": 115, "route_code": "5352_122186"},
    # Dublin
    "46A": {"lat": 53.2896, "lon": -6.1432, "city": "Dublin", "desc": "Dún Laoghaire → City Centre",
            "base_delay": 175, "route_code": "1_46A"},
    "27":  {"lat": 53.3950, "lon": -6.2730, "city": "Dublin", "desc": "Coolock → City Centre",
            "base_delay": 140, "route_code": "1_27"},
    "44":  {"lat": 53.1929, "lon": -6.1735, "city": "Dublin", "desc": "Enniskerry → Dundrum",
            "base_delay": 120, "route_code": "1_44"},
    "145": {"lat": 53.1865, "lon": -6.1145, "city": "Dublin", "desc": "Ballywaltrim → UCD",
            "base_delay": 105, "route_code": "1_145"},
    "25X": {"lat": 53.3572, "lon": -6.4467, "city": "Dublin", "desc": "Lucan → City Centre (Exp)",
            "base_delay": 130, "route_code": "1_25X"},
}
ALL_ROUTES = list(route_profiles.keys())
_avg_base_delay = sum(p["base_delay"] for p in route_profiles.values()) / len(route_profiles)
for _p in route_profiles.values():
    _p["base"] = round(_p["base_delay"] / _avg_base_delay, 4)

# Ireland's real bounding box (approx.) — used for the "Both" city view so the
# island's outline is always recognisable, rather than an arbitrary
# Cork-Dublin rectangle that could be mistaken for any coastline.
IRELAND_BOUNDS = {"west": -10.7, "east": -5.3, "south": 51.4, "north": 55.4}


def bounds_to_zoom_center(bounds, zoom_buffer=0.4):
    """
    Convert a {west,east,south,north} box to an initial (center, zoom) for
    mapbox_center/mapbox_zoom.

    mapbox_bounds is a CONSTRAINT re-applied on every render - if the user
    zooms or pans, the next Streamlit rerun re-applies bounds and snaps the
    view back, so interactive zoom never sticks. zoom/center are just
    STARTING values: combined with uirevision, the user's own zoom/pan
    persists across reruns instead of being overridden.

    zoom is derived from the box's span in degrees (log2 of span -> zoom
    level). zoom_buffer is SUBTRACTED so the initial view is slightly more
    zoomed-OUT than a tight fit - if the formula is imperfect for the actual
    container width, the box stays fully visible (just with a bit of extra
    margin) rather than being cropped. The user can zoom in further, and
    that adjustment now sticks.
    """
    lat_span = max(bounds["north"] - bounds["south"], 0.01)
    lon_span = max(bounds["east"] - bounds["west"], 0.01)
    center = {"lat": (bounds["north"] + bounds["south"]) / 2,
              "lon": (bounds["east"] + bounds["west"]) / 2}
    zoom = 8 - np.log2(max(lat_span, lon_span)) - zoom_buffer
    return center, float(np.clip(zoom, 3, 14))


def map_bounds(routes, city_selected, pad_deg=0.07):
    """
    Geographic bounding box (west/east/south/north in degrees) for the map.
    Passed to fig.update_layout(mapbox_bounds=...), which is resolution-
    independent — Plotly computes whatever zoom/center is needed to fit this
    exact box, regardless of the container's actual pixel width. This
    replaces a zoom-level formula, which is tile-based and therefore looks
    different (and was looking wrong) depending on how wide the panel
    renders.

    "Both": Ireland's real bounds, so the island's shape is always visible.
    Single city: a tight box around just the selected routes + fixed padding,
    so individual route markers stay clearly separated.
    """
    if city_selected == "Both":
        return dict(IRELAND_BOUNDS)
    lats = [route_profiles[r]["lat"] for r in routes]
    lons = [route_profiles[r]["lon"] for r in routes]
    return {
        "west": min(lons) - pad_deg, "east": max(lons) + pad_deg,
        "south": min(lats) - pad_deg, "north": max(lats) + pad_deg,
    }


def route_seed_offset(route):
    """Deterministic per-route seed offset.

    Python's built-in hash() for strings is randomised per-process
    (PYTHONHASHSEED, since Python 3.3, for hash-DoS protection) - using
    hash(route) here would give each route a DIFFERENT random offset on
    every app restart/redeploy, so the same date could show different
    demand scores from one run to the next even though the date-based seed
    component is fixed. Summing character codes is deterministic and gives
    each route code its own stable, well-separated offset.
    """
    return sum(ord(c) for c in route) % 10_000


def classify_day(d):
    """Classify a date into the OptiMove day-type categories (deterministic)."""
    dow = d.dayofweek
    weekend = dow >= 5
    holiday = d.strftime("%m-%d") in {"01-01", "03-17", "04-18"}
    school = d.month in {2, 3, 4} and d.day <= 14
    gaa = d.day in {6, 12, 18, 24}
    if gaa:        return "GAA Match Day", gaa, holiday, school, weekend
    if holiday:    return "Public Holiday", gaa, holiday, school, weekend
    if school:     return "School Holiday", gaa, holiday, school, weekend
    if weekend:    return "Weekend", gaa, holiday, school, weekend
    return "Normal Day", gaa, holiday, school, weekend


def generate_route_hour(h, gaa, holiday, school, weekend, base, rng):
    """One (route, hour) sample of delay/rain, given day-type flags. Shared by all views."""
    is_peak = (7 <= h <= 9 or 17 <= h <= 18)
    is_off = 10 <= h <= 15
    rain = max(0, rng.normal(2.6, 1.9)) * (1.25 if gaa else 1.0) * (0.92 if weekend else 1.0)
    if is_peak:
        delay = rng.uniform(8, 13.5) * base
        delay += 3.0 if gaa else 0
        delay += 0.8 if holiday else 0
    elif is_off:
        delay = rng.uniform(0.5, 2.5) * base
        delay *= 0.6 if school else 1.0
        delay *= 0.7 if weekend else 1.0
        delay = max(0.1, delay)
    else:
        delay = rng.uniform(2.5, 5.5) * base
        delay *= 0.75 if weekend else 1.0
    return round(delay, 1), round(rain, 1)


@st.cache_data
def build_focus_day_profile(start_d, end_d, routes, day_types):
    """
    Per-route, per-hour profile for ONE representative day — the first date in
    [start_d, end_d] whose day-type is in day_types. Drives every Operations
    Manager component (KPIs, map, trend, table, heatmap, formula panel) from a
    single consistent source, so changing any sidebar control updates all of them.
    Falls back to the day-type's typical flags if no date in range matches
    (e.g. "GAA Match Day" selected but no 6th/12th/18th/24th falls in range).
    """
    focus_date, focus_flags = None, None
    for d in pd.date_range(start_d, end_d, freq="D"):
        dtype, gaa, holiday, school, weekend = classify_day(d)
        if dtype in day_types:
            focus_date = d
            focus_flags = (dtype, gaa, holiday, school, weekend)
            break

    if focus_date is None:
        dtype = day_types[0]
        focus_date = pd.Timestamp(start_d)
        flag_map = {
            "GAA Match Day":  (True, False, False, False),
            "Public Holiday": (False, True, False, False),
            "School Holiday": (False, False, True, False),
            "Weekend":        (False, False, False, True),
            "Normal Day":     (False, False, False, False),
        }
        gaa, holiday, school, weekend = flag_map.get(dtype, (False, False, False, False))
        focus_flags = (dtype, gaa, holiday, school, weekend)

    dtype, gaa, holiday, school, weekend = focus_flags
    seed = int(focus_date.strftime("%Y%m%d"))

    rows = []
    for route in routes:
        prof = route_profiles[route]
        rng = np.random.default_rng(seed + route_seed_offset(route))
        for h in range(7, 20):
            delay, rain = generate_route_hour(h, gaa, holiday, school, weekend, prof["base"], rng)
            ds = round(demand_score(delay, rain), 1)
            label, optimised, risk = recommendation(ds, 12)
            rows.append({
                "Route": route, "Hour": h, "Time": f"{h:02d}:00",
                "Delay_mins": delay, "Rainfall_mm": rain,
                "Demand_score": ds, "Risk": risk, "Recommendation": label,
                "Scheduled_fleet": 12, "Recommended_fleet": optimised,
                "Fleet_delta": optimised - 12,
                "Net_cost_impact_eur": (12 - optimised) * COST_PER_BUS_HOUR,
            })

    profile_df = pd.DataFrame(rows)
    profile_df.attrs["focus_date"] = focus_date.date()
    profile_df.attrs["day_type"] = dtype
    return profile_df


@st.cache_data
def build_strat_df(start_d, end_d, routes, day_types):
    """Multi-day, multi-route history for the Strategic Planner view. Each
    (date, route) combination gets its own independent RNG stream so results
    are reproducible regardless of call order, and share the same per-hour
    generation logic as the Operations Manager day profile."""
    rows = []
    for d in pd.date_range(start_d, end_d, freq="D"):
        dtype, gaa, holiday, school, weekend = classify_day(d)
        if dtype not in day_types:
            continue
        date_seed = int(d.strftime("%Y%m%d"))
        for route in routes:
            prof = route_profiles[route]
            rng = np.random.default_rng(date_seed + route_seed_offset(route))
            for h in range(7, 20):
                delay, rain = generate_route_hour(h, gaa, holiday, school, weekend, prof["base"], rng)
                ds = demand_score(delay, rain)
                scheduled = 12
                rec_label, optimized, risk_band = recommendation(ds, scheduled)
                rows.append({
                    "Date": d.date(), "DayType": dtype, "Route": route,
                    "Hour": h, "Time": f"{h:02d}:00",
                    "Rainfall_mm": rain, "Delay_mins": delay,
                    "Demand_score": round(ds, 1), "Risk_band": risk_band,
                    "Scheduled_fleet": scheduled, "Optimised_fleet": optimized,
                    "Fleet_delta": optimized - scheduled,
                    "Net_cost_impact_eur": (scheduled - optimized) * COST_PER_BUS_HOUR,
                    "Lat": prof["lat"] + rng.normal(0, 0.003),
                    "Lon": prof["lon"] + rng.normal(0, 0.003),
                })
    return pd.DataFrame(rows)


# ── Sidebar ────────────────────────────────────────────────────────────────────
st.sidebar.markdown("## 🚌 OptiMove")
st.sidebar.caption("Predictive fleet allocation for OptiMove V2")
st.sidebar.markdown("---")

view = st.sidebar.radio("View", ["Operations Manager", "Strategic Planner"])
st.sidebar.markdown("---")

city_selected = st.sidebar.radio("City", ["Cork", "Dublin", "Both"], index=2, horizontal=True)
city_routes = ALL_ROUTES if city_selected == "Both" else [r for r in ALL_ROUTES if route_profiles[r]["city"] == city_selected]

routes_selected = st.sidebar.multiselect(
    "Routes", city_routes, default=city_routes, key=f"routes_{city_selected}")
if not routes_selected:
    routes_selected = city_routes

day_types_selected = st.sidebar.multiselect(
    "Day types",
    ["School Holiday", "Normal Day", "GAA Match Day", "Weekend", "Public Holiday"],
    default=["School Holiday", "Normal Day", "GAA Match Day", "Weekend", "Public Holiday"])
if not day_types_selected:
    day_types_selected = ["School Holiday", "Normal Day", "GAA Match Day", "Weekend", "Public Holiday"]

date_range = st.sidebar.date_input(
    "Date range", value=(date(2026, 1, 6), date(2026, 4, 30)),
    min_value=date(2026, 1, 1), max_value=date(2026, 4, 30))

focus_hour = st.sidebar.select_slider(
    "Focus hour", options=[f"{h:02d}:00" for h in range(7, 20)], value="08:00")

if isinstance(date_range, tuple) and len(date_range) == 2:
    start_d, end_d = date_range
else:
    start_d = end_d = date_range if not isinstance(date_range, tuple) else date_range[0]

focus_hour_int = int(focus_hour[:2])

# Single source of truth for the Operations Manager view — regenerates whenever
# routes, day types, or the date range change.
ops_profile = build_focus_day_profile(start_d, end_d, tuple(routes_selected), tuple(day_types_selected))

df = build_strat_df(start_d, end_d, tuple(routes_selected), tuple(day_types_selected))


# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="premium-header">
  <div>
    <div class="smallcap">OptiMove Transport Intelligence</div>
    <h1 style="margin:4px 0 0 0; font-size:1.18rem; font-weight:800;">
      Fleet Demand &amp; Allocation
    </h1>
    <div style="font-size:0.8rem; opacity:0.88;">
      Route pressure monitoring and recommended fleet reallocation
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

ops_palette = {"High Risk": "#DC2626", "Moderate": "#F59E0B", "Underutilised": "#2563EB"}
day_palette = {"Normal Day": "#166534", "Public Holiday": "#0EA5A4",
               "School Holiday": "#60A5FA", "Weekend": "#EC4899", "GAA Match Day": "#DC2626"}

def card(title, value, tag, cls=""):
    return (f'<div class="kpi-card {cls}">'
            f'<div class="kpi-title">{title}</div>'
            f'<div class="kpi-value">{value}</div>'
            f'<div class="kpi-tag">{tag}</div></div>')

PLOT_CFG = dict(paper_bgcolor="white", plot_bgcolor="white",
                font=dict(family="Inter", color="#0F172A"))

def formula_breakdown_html(delay, rain, scheduled, route_label=None, route_desc=None):
    """Render the DS_Score formula as a transparent, visual breakdown with a verdict.

    Both component bars are drawn on the SAME 0-100 scale as the final Demand
    Score, rather than each maxing out at its own weighted ceiling (72 for
    delay, 28 for rain). A delay-only contribution of 64.8 and a rainfall-only
    contribution of 21.0 therefore both read against the same 0-100 axis as
    the 85-point High Risk threshold below — so "how close is this to tipping
    the recommendation" is directly comparable across both factors, the same
    way every row on the TFI departures board reads against one shared
    minutes-to-arrival scale regardless of route.
    """
    dc = delay_component(delay)
    rc = rain_component(rain)
    ds = round(dc + rc, 1)
    label, optimised, risk = recommendation(ds, scheduled)

    # Ceilings: delay component maxes at 72 (0.72 x 100), rain at 28 (0.28 x 100)
    dc_ceiling, rc_ceiling = 72.0, 28.0
    dc_of_ceiling = (dc / dc_ceiling) * 100  # how saturated is the delay factor itself
    rc_of_ceiling = (rc / rc_ceiling) * 100  # how saturated is the rain factor itself

    if risk == "High Risk":
        verdict_bg, verdict_fg = "#FEE2E2", "#7F1D1D"
        verdict_icon = "⚠"
        verdict_text = (f"Demand score <b>{ds}</b> is at or above the High Risk threshold "
                        f"({HIGH_RISK_THRESHOLD}). <b>{label}</b> — fleet moves from "
                        f"{scheduled} to {optimised} vehicles.")
    elif risk == "Underutilised":
        verdict_bg, verdict_fg = "#DBEAFE", "#1E40AF"
        verdict_icon = "↓"
        verdict_text = (f"Demand score <b>{ds}</b> is at or below the low-demand threshold "
                        f"({LOW_THRESHOLD}). <b>{label}</b> — fleet moves from "
                        f"{scheduled} to {optimised} vehicles "
                        f"(Minimum Service Floor: {PSO_FLOOR}).")
    else:
        verdict_bg, verdict_fg = "#FEF3C7", "#78350F"
        verdict_icon = "•"
        verdict_text = (f"Demand score <b>{ds}</b> is within the normal operating range "
                        f"({LOW_THRESHOLD}–{HIGH_RISK_THRESHOLD}). <b>{label}</b> "
                        f"at {scheduled} vehicles.")

    header = ""
    if route_label:
        header = (f'<div style="font-size:0.78rem;color:#64748B;margin-bottom:6px;">'
                  f'Route <b>{route_label}</b>'
                  + (f' &middot; {route_desc}' if route_desc else '')
                  + f' &middot; {focus_hour}</div>')

    return f"""
    {header}
    <div class="formula-box">
      <div class="formula-row">
        <div class="formula-label">Delay {delay:.1f} min &rarr; &times;0.72</div>
        <div class="formula-bar-track">
          <div class="formula-threshold" style="left:{LOW_THRESHOLD}%;"></div>
          <div class="formula-threshold" style="left:{HIGH_RISK_THRESHOLD}%;"></div>
          <div class="formula-bar-fill" style="width:{dc:.1f}%; background:#166534;"></div>
        </div>
        <div class="formula-value">{dc:.1f}</div>
      </div>
      <div class="formula-subnote">{dc_of_ceiling:.0f}% of the maximum possible delay contribution (72)</div>

      <div class="formula-row">
        <div class="formula-label">Rainfall {rain:.1f} mm/hr &rarr; &times;0.28</div>
        <div class="formula-bar-track">
          <div class="formula-threshold" style="left:{LOW_THRESHOLD}%;"></div>
          <div class="formula-threshold" style="left:{HIGH_RISK_THRESHOLD}%;"></div>
          <div class="formula-bar-fill" style="width:{rc:.1f}%; background:#0EA5A4;"></div>
        </div>
        <div class="formula-value">{rc:.1f}</div>
      </div>
      <div class="formula-subnote">{rc_of_ceiling:.0f}% of the maximum possible rainfall contribution (28)</div>

      <div class="formula-row" style="margin-top:8px;">
        <div class="formula-label"><b>Demand Score</b></div>
        <div class="formula-bar-track">
          <div class="formula-threshold" style="left:{LOW_THRESHOLD}%;"></div>
          <div class="formula-threshold" style="left:{HIGH_RISK_THRESHOLD}%;"></div>
          <div class="formula-bar-fill" style="width:{dc:.1f}%; background:#166534;"></div>
          <div class="formula-bar-fill" style="width:{rc:.1f}%; background:#0EA5A4;"></div>
        </div>
        <div class="formula-value" style="font-size:1.1rem;">{ds}</div>
      </div>
      <div class="formula-subnote">
        Markers at {LOW_THRESHOLD} (reduce fleet) and {HIGH_RISK_THRESHOLD} (add fleet) — same scale as the chart above.
      </div>

      <div class="formula-verdict" style="background:{verdict_bg};color:{verdict_fg};">
        {verdict_icon} {verdict_text}
      </div>
    </div>
    """

# ══════════════════════════════════════════════════════════════════════════════
#  VIEW 1 — OPERATIONS MANAGER
# ══════════════════════════════════════════════════════════════════════════════
if view == "Operations Manager":

    focus_date = ops_profile.attrs["focus_date"]

    # Network-level: average DS per hour across selected routes (one row per hour)
    network_hourly = (ops_profile.groupby(["Hour", "Time"], as_index=False)
                      .agg(Demand_score=("Demand_score", "mean"),
                           Recommended_fleet=("Recommended_fleet", "sum"),
                           Scheduled_fleet=("Scheduled_fleet", "sum"),
                           Fleet_delta=("Fleet_delta", "sum")))
    network_hourly["Demand_score"] = network_hourly["Demand_score"].round(1)

    n_actions = int((ops_profile["Fleet_delta"] != 0).sum())
    buses_to_move = int(ops_profile["Fleet_delta"].abs().sum())
    peak_row = ops_profile.loc[ops_profile["Demand_score"].idxmax()]
    pso_breaches = int((ops_profile["Recommended_fleet"] < PSO_FLOOR).sum())

    st.markdown(f"""<div class="kpi-grid">
      {card("Hours Needing Action", n_actions,
            f"Route-hours where the recommended fleet differs from scheduled, across {len(routes_selected)} route(s)",
            "warn" if n_actions else "")}
      {card("Buses to Reallocate", buses_to_move,
            "Total vehicle moves recommended across the day")}
      {card("Highest-Pressure Route-Hour", f"{peak_row['Route']} · {peak_row['Time']}",
            f"Demand score {peak_row['Demand_score']:.1f} — start reallocation here", "alert")}
      {card("Minimum Service Floor", "All clear" if pso_breaches == 0 else f"{pso_breaches} below floor",
            f"Floor: {PSO_FLOOR} buses/route-hour" + (" — review before applying" if pso_breaches else ""),
            "alert" if pso_breaches else "ok")}
    </div>""", unsafe_allow_html=True)

    # Map — derived from ops_profile at the focus hour, not hardcoded
    st.markdown("<div class='panel'><div class='panel-title'>Route Pressure Locator</div>", unsafe_allow_html=True)
    map_hour = ops_profile[ops_profile["Hour"] == focus_hour_int].copy()
    map_hour["lat"] = map_hour["Route"].map(lambda r: route_profiles[r]["lat"])
    map_hour["lon"] = map_hour["Route"].map(lambda r: route_profiles[r]["lon"])
    map_hour["Description"] = map_hour["Route"].map(lambda r: route_profiles[r]["desc"])
    map_hour["GTFS code"] = map_hour["Route"].map(lambda r: route_profiles[r]["route_code"])
    # Marker size is driven by this floored copy so a very low Demand Score
    # (e.g. an Underutilised route at an off-peak hour) still renders as a
    # visible dot. The true Demand_score (unclipped) stays in hover/colour.
    map_hour["Marker_size"] = map_hour["Demand_score"].clip(lower=15)
    bounds = map_bounds(routes_selected, city_selected)
    center, zoom = bounds_to_zoom_center(bounds)

    # Built directly with go.Scattermapbox - one explicit trace per Risk
    # band - rather than px.scatter_mapbox, so every marker property is
    # set explicitly (size, sizemode, sizeref, sizemin, color, opacity)
    # with nothing left to px's automatic colour/hover-data handling.
    # A single sizeref shared across all traces (based on the overall max
    # for this hour) keeps dot sizes comparable between bands.
    overall_max = max(map_hour["Marker_size"].max(), 1)
    shared_sizeref = 2.0 * overall_max / (30 ** 2)

    fig_map = go.Figure()
    for risk_band, colour in ops_palette.items():
        sub = map_hour[map_hour["Risk"] == risk_band]
        if sub.empty:
            continue
        fig_map.add_trace(go.Scattermapbox(
            lat=sub["lat"], lon=sub["lon"], mode="markers",
            marker=dict(size=sub["Marker_size"], sizemode="area",
                        sizeref=shared_sizeref, sizemin=4,
                        color=colour, opacity=0.9),
            name=risk_band, text=sub["Route"],
            customdata=sub[["Demand_score", "Description", "GTFS code"]],
            hovertemplate=("<b>%{text}</b><br>" + risk_band +
                            "<br>Demand score: %{customdata[0]:.1f}<br>"
                            "%{customdata[1]} (%{customdata[2]})<extra></extra>")))

    fig_map.update_layout(
        mapbox_style="carto-positron", mapbox_zoom=zoom, mapbox_center=center,
        # uirevision: as long as this string is unchanged across reruns,
        # Plotly keeps the user's current zoom/pan instead of resetting to
        # the values above. Keyed on city+routes so switching geographic
        # scope gives a fresh initial view; changing focus hour/day type
        # (which don't change the map's geography) preserves the user's zoom.
        uirevision=f"map_{city_selected}_{','.join(sorted(routes_selected))}",
        height=380, margin=dict(l=0, r=0, t=0, b=0), paper_bgcolor="white",
        hoverlabel=dict(bgcolor="white", font_size=12, font_family="Inter"),
        legend=dict(
            title=dict(text="Risk Band", font=dict(size=11)),
            x=0.01, y=0.99, xanchor="left", yanchor="top",
            bgcolor="rgba(255,255,255,0.92)", bordercolor="#E2E8F0", borderwidth=1,
            font=dict(size=11)))
    st.plotly_chart(fig_map, use_container_width=True,
                    config={"scrollZoom": True, "displayModeBar": True})

    # Size legend — marker size = Demand Score, which Plotly's mapbox legend
    # cannot show natively. Three reference circles at known values, drawn
    # with the same relative proportions as size_max=30 on a 0-100 scale.
    st.markdown(f"""
    <div class="size-legend">
      <span class="size-legend-title">Marker size — Demand Score</span>
      <span class="size-legend-item"><span class="size-legend-dot" style="width:8px;height:8px;"></span>≈20</span>
      <span class="size-legend-item"><span class="size-legend-dot" style="width:16px;height:16px;"></span>≈50</span>
      <span class="size-legend-item"><span class="size-legend-dot" style="width:26px;height:26px;"></span>≈85+</span>
      <span class="size-legend-note">Colour = risk band (legend on map)</span>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Demand trend — network average across selected routes
    st.markdown("<div class='panel'><div class='panel-title'>Demand Score Trend</div>", unsafe_allow_html=True)
    HOURS_STR = [f"{h:02d}:00" for h in range(7, 20)]
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=network_hourly["Time"], y=network_hourly["Demand_score"], mode="lines+markers+text",
        text=network_hourly["Demand_score"], textposition="top center",
        line=dict(color="#166534", width=3), fill="tozeroy", fillcolor="rgba(22,101,52,0.06)",
        marker=dict(size=7), name="Demand score"))
    fig.add_hline(y=HIGH_RISK_THRESHOLD, line_dash="dash", line_color="#DC2626",
                  annotation_text=f"Add buses ({HIGH_RISK_THRESHOLD})", annotation_position="top right",
                  annotation_font=dict(color="#DC2626", size=10))
    fig.add_hline(y=LOW_THRESHOLD, line_dash="dash", line_color="#2563EB",
                  annotation_text=f"Reduce buses ({LOW_THRESHOLD})", annotation_position="bottom right",
                  annotation_font=dict(color="#2563EB", size=10))
    focus_idx = HOURS_STR.index(focus_hour) if focus_hour in HOURS_STR else 1
    fig.add_vline(x=focus_idx, line=dict(color="#D97706", width=1.5, dash="dot"),
                  annotation_text=focus_hour, annotation_font=dict(color="#D97706", size=10))
    fig.update_layout(
        xaxis_title="Operating Hour", yaxis_title="Demand Score (0–100)",
        xaxis=dict(showgrid=True, gridcolor="#F1F5F9", title_font=dict(size=12)),
        yaxis=dict(range=[0, 105], showgrid=True, gridcolor="#F1F5F9",
                   tickvals=[0, 15, 50, 85, 100], title_font=dict(size=12)),
        height=320, margin=dict(l=16, r=16, t=20, b=16), showlegend=False, **PLOT_CFG)
    st.plotly_chart(fig, use_container_width=True)
    st.caption(f"Average demand score across {len(routes_selected)} selected route(s) at each hour.")
    st.markdown("</div>", unsafe_allow_html=True)

    col_rmt, col_why = st.columns([1.2, 1], gap="medium")

    with col_rmt:
        rmt_hour = ops_profile[ops_profile["Hour"] == focus_hour_int].copy()
        rmt_hour = rmt_hour.sort_values("Demand_score", ascending=False).reset_index(drop=True)
        n_actionable = int((rmt_hour["Fleet_delta"] != 0).sum())

        def highlight_risk(row):
            c = {"High Risk": "background-color:#FEE2E2;color:#7F1D1D;",
                 "Moderate": "background-color:#FEF3C7;color:#78350F;",
                 "Underutilised": "background-color:#DCFCE7;color:#14532D;"
                 }.get(row["Risk"], "")
            return [c] * len(row)

        if n_actionable == 0:
            st.markdown("<div class='panel'><div class='panel-title'>Route Monitoring</div>", unsafe_allow_html=True)
            display_rmt = rmt_hour[["Route", "Delay_mins", "Rainfall_mm", "Demand_score", "Risk", "Recommendation"]].copy()
            display_rmt.columns = ["Route", "Delay (mins)", "Rainfall (mm/hr)", "Demand Score", "Risk", "Recommendation"]
            st.dataframe(
                display_rmt.style.apply(highlight_risk, axis=1)
                   .format({"Demand Score": "{:.1f}", "Delay (mins)": "{:.1f}", "Rainfall (mm/hr)": "{:.1f}"})
                   .hide(axis="index"),
                use_container_width=True, height=min(360, 46 + 36 * len(display_rmt))
            )
        else:
            st.markdown("<div class='panel'><div class='panel-title'>Today's Plan</div>", unsafe_allow_html=True)
            editor_df = rmt_hour[["Route", "Demand_score", "Risk", "Recommendation",
                                   "Scheduled_fleet", "Recommended_fleet", "Fleet_delta"]].copy()
            editor_df.insert(0, "Apply", editor_df["Fleet_delta"] != 0)
            editor_df = editor_df.rename(columns={
                "Demand_score": "Demand Score", "Scheduled_fleet": "Scheduled",
                "Recommended_fleet": "Recommended", "Fleet_delta": "Δ Fleet"})

            edited = st.data_editor(
                editor_df,
                column_config={
                    "Apply": st.column_config.CheckboxColumn("Apply?", help="Apply OptiMove's recommendation for this route"),
                    "Route": st.column_config.TextColumn("Route", disabled=True),
                    "Demand Score": st.column_config.NumberColumn("Demand Score", format="%.1f", disabled=True),
                    "Risk": st.column_config.TextColumn("Risk", disabled=True),
                    "Recommendation": st.column_config.TextColumn("Recommendation", disabled=True),
                    "Scheduled": st.column_config.NumberColumn("Scheduled", format="%d", disabled=True),
                    "Recommended": st.column_config.NumberColumn("Recommended", format="%d", disabled=True),
                    "Δ Fleet": st.column_config.NumberColumn("Δ Fleet", format="%d", disabled=True),
                },
                hide_index=True, use_container_width=True,
                height=min(360, 46 + 36 * len(editor_df)),
                key=f"plan_editor_{focus_date}_{focus_hour}_{','.join(sorted(routes_selected))}")

            applying = edited[edited["Apply"] & (edited["Δ Fleet"] != 0)]
            n_applying = len(applying)
            bus_moves = int(applying["Δ Fleet"].abs().sum())
            net_eur = int(((applying["Scheduled"] - applying["Recommended"]) * COST_PER_BUS_HOUR).sum())

            if n_applying == 0:
                st.caption("Toggle 'Apply?' to build today's plan from OptiMove's recommendations.")
            else:
                sign = "saving" if net_eur >= 0 else "cost"
                st.caption(f"Applying {n_applying} of {n_actionable} recommendation(s): "
                           f"{bus_moves} bus-move(s), net €{abs(net_eur):,.0f}/hr {sign}.")

            plan_csv = edited.to_csv(index=False).encode("utf-8")
            st.download_button("Download today's plan (CSV)", data=plan_csv,
                                file_name=f"optimove_plan_{focus_date}_{focus_hour.replace(':','')}.csv",
                                mime="text/csv", type="primary", use_container_width=True, key="dl_plan")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_why:
        st.markdown("<div class='panel'><div class='panel-title'>Why This Recommendation</div>", unsafe_allow_html=True)
        focus_route = st.selectbox("Route", routes_selected, key="why_route")
        sel = rmt_hour[rmt_hour["Route"] == focus_route].iloc[0]
        st.markdown(
            formula_breakdown_html(sel["Delay_mins"], sel["Rainfall_mm"], int(sel["Scheduled_fleet"]),
                                    route_label=focus_route,
                                    route_desc=route_profiles[focus_route]["desc"]),
            unsafe_allow_html=True
        )
        st.markdown("</div>", unsafe_allow_html=True)

    # Route × Hour Pressure Map — full ops_profile, pivoted
    st.markdown("<div class='panel'><div class='panel-title'>Route × Hour Pressure Map</div>", unsafe_allow_html=True)
    heat_hours = ["07:00", "08:00", "09:00", "12:00", "17:00", "18:00"]
    pivot = ops_profile.pivot(index="Route", columns="Time", values="Demand_score")
    pivot = pivot.reindex(index=routes_selected, columns=heat_hours)
    route_labels = pivot.index.tolist()
    heat_matrix = pivot.values
    fig_heat = px.imshow(heat_matrix, x=heat_hours, y=route_labels, text_auto=".0f",
                          color_continuous_scale=["#EFF6FF", "#DBEAFE", "#FDE68A", "#FCA5A5", "#B91C1C"],
                          aspect="auto", labels=dict(x="Operating Hour", y="Route", color="Demand Score"),
                          zmin=0, zmax=100)
    fig_heat.update_yaxes(tickvals=list(range(len(route_labels))), ticktext=route_labels, type="category")
    fig_heat.update_layout(
        xaxis_title="Operating Hour", yaxis_title="Route",
        height=320, margin=dict(l=16, r=16, t=20, b=16), paper_bgcolor="white",
        coloraxis_colorbar=dict(title="Demand", tickvals=[0, 15, 50, 85, 100],
                                 ticktext=["0", f"{LOW_THRESHOLD}", "50", f"{HIGH_RISK_THRESHOLD}", "100"]))
    st.plotly_chart(fig_heat, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  VIEW 2 — STRATEGIC PLANNER
# ══════════════════════════════════════════════════════════════════════════════
else:
    if df.empty:
        st.warning("No data for current filters — adjust routes, day types or date range.")
        st.stop()

    offpeak_saving = df.loc[df["Fleet_delta"] < 0, "Net_cost_impact_eur"].sum()
    peak_cost = abs(df.loc[df["Fleet_delta"] > 0, "Net_cost_impact_eur"].sum())
    n_days = (end_d - start_d).days + 1
    avg_routes_per_day = df["Route"].nunique()
    net_total = offpeak_saving - peak_cost
    net_per_day = net_total / max(n_days, 1)
    avg_demand = df["Demand_score"].mean()
    peak_windows = int((df["Demand_score"] >= HIGH_RISK_THRESHOLD).sum())
    annualised = net_per_day * 300

    st.markdown(f"""<div class="kpi-grid">
      {card("Net Daily Saving", f"€{net_per_day:,.0f}",
            f"Off-peak reductions minus peak-period additions, at €{COST_PER_BUS_HOUR}/bus-hr",
            "ok" if net_per_day >= 0 else "alert")}
      {card("Annualised Projection", f"€{annualised:,.0f}",
            "Net daily saving × 300 operating days")}
      {card("Average Demand Score", f"{avg_demand:.1f}",
            "Mean route pressure across the selected period")}
      {card("Peak Pressure Windows", peak_windows,
            "Route-hours where the solver adds capacity", "alert" if peak_windows else "")}
    </div>""", unsafe_allow_html=True)

    # Weekly demand
    st.markdown("<div class='panel'><div class='panel-title'>Demand by Week and Day Type</div>", unsafe_allow_html=True)
    df["Week_num"] = df["Date"].apply(lambda d: (d - date(2026, 1, 1)).days // 7 + 1)
    weekly = df.groupby(["Week_num", "DayType"])["Demand_score"].mean().reset_index()
    weekly.columns = ["Week", "DayType", "Demand_score"]
    weekly = weekly.sort_values("Week")
    fig_week = px.line(weekly, x="Week", y="Demand_score", color="DayType",
                        markers=True, color_discrete_map=day_palette)
    fig_week.update_traces(line=dict(width=2.6), marker=dict(size=6), opacity=0.95)
    fig_week.update_layout(
        xaxis_title="Week Number", yaxis_title="Average Demand Score",
        xaxis=dict(showgrid=True, gridcolor="#F1F5F9", dtick=2, title_font=dict(size=12)),
        yaxis=dict(range=[0, 100], showgrid=True, gridcolor="#F1F5F9", title_font=dict(size=12)),
        height=360, margin=dict(l=16, r=16, t=55, b=16),
        legend_title_text="Day Type",
        legend=dict(orientation="h", y=1.18, x=0, xanchor="left", font=dict(size=11)),
        **PLOT_CFG)
    st.plotly_chart(fig_week, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    left, right = st.columns([1, 1], gap="large")

    with left:
        st.markdown("<div class='panel'><div class='panel-title'>Demand by Day Type</div>", unsafe_allow_html=True)
        day_cmp = (df.groupby("DayType", as_index=False)["Demand_score"]
                   .mean().sort_values("Demand_score", ascending=False))
        fig_day = px.bar(day_cmp, x="DayType", y="Demand_score",
                         color="DayType", color_discrete_map=day_palette, text="Demand_score")
        fig_day.update_traces(texttemplate="%{text:.1f}", textposition="outside", cliponaxis=False)
        fig_day.update_layout(
            xaxis_title="Day Type", yaxis_title="Average Demand Score",
            xaxis=dict(showgrid=False, title_font=dict(size=12)),
            yaxis=dict(range=[0, day_cmp["Demand_score"].max() + 14], showgrid=True,
                       gridcolor="#F1F5F9", title_font=dict(size=12)),
            height=360, margin=dict(l=16, r=16, t=20, b=16), showlegend=False, **PLOT_CFG)
        st.plotly_chart(fig_day, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown("<div class='panel'><div class='panel-title'>Risk Band Distribution</div>", unsafe_allow_html=True)
        band_counts = df["Risk_band"].value_counts()
        band_counts = band_counts.reindex(["High Risk", "Moderate", "Underutilised"], fill_value=0).reset_index()
        band_counts.columns = ["Risk band", "Route-hours"]
        total_hrs = int(band_counts["Route-hours"].sum())
        fig_pie = px.pie(band_counts, names="Risk band", values="Route-hours", hole=0.55,
                         color="Risk band", color_discrete_map=ops_palette)
        fig_pie.update_traces(
            textposition="outside",
            texttemplate="<b>%{label}</b><br>%{percent:.1%}",
            hovertemplate="<b>%{label}</b><br>%{value:,.0f} route-hours (%{percent:.1%})<extra></extra>",
            marker=dict(line=dict(color="white", width=2)),
            pull=[0.03, 0.03, 0.03])
        fig_pie.update_layout(
            height=380, margin=dict(l=40, r=40, t=20, b=55),
            paper_bgcolor="white", showlegend=True,
            legend=dict(orientation="h", y=-0.12, x=0.5, xanchor="center", font=dict(size=11), bgcolor="rgba(0,0,0,0)"),
            annotations=[dict(
                text=f"<b>{total_hrs:,}</b><br><span style='font-size:11px'>route-hours</span>",
                x=0.5, y=0.5, xref="paper", yref="paper", showarrow=False,
                font=dict(size=14, color="#0F172A", family="Inter"))])
        st.plotly_chart(fig_pie, use_container_width=True)

        high_pct = band_counts.loc[band_counts["Risk band"] == "High Risk", "Route-hours"].iloc[0] / total_hrs * 100
        under_pct = band_counts.loc[band_counts["Risk band"] == "Underutilised", "Route-hours"].iloc[0] / total_hrs * 100
        if high_pct > under_pct + 5:
            msg = (f"{high_pct:.0f}% of route-hours are High Risk vs {under_pct:.0f}% Underutilised — "
                   f"the network may need more total capacity at peak, not just reallocation.")
        elif under_pct > high_pct + 5:
            msg = (f"{under_pct:.0f}% of route-hours are Underutilised vs {high_pct:.0f}% High Risk — "
                   f"broad off-peak reductions are the main opportunity.")
        else:
            msg = (f"High Risk ({high_pct:.0f}%) and Underutilised ({under_pct:.0f}%) route-hours are "
                   f"roughly balanced — reallocation between them is the main lever.")
        st.caption(msg)
        st.markdown("</div>", unsafe_allow_html=True)

    left2, right2 = st.columns([1, 1], gap="large")

    with left2:
        st.markdown("<div class='panel'><div class='panel-title'>Scheduled vs Recommended Fleet</div>", unsafe_allow_html=True)

        hours_ord = [f"{h:02d}:00" for h in range(7, 20)]
        network_by_hour = (ops_profile.groupby("Time", as_index=False)
                           .agg(Demand_score=("Demand_score", "mean"),
                                Scheduled_fleet=("Scheduled_fleet", "sum"),
                                Recommended_fleet=("Recommended_fleet", "sum")))
        network_by_hour = network_by_hour.set_index("Time").reindex(hours_ord)

        sched_vals = network_by_hour["Scheduled_fleet"].tolist()
        opt_vals = network_by_hour["Recommended_fleet"].tolist()

        alloc = pd.DataFrame({"Hour": hours_ord, "Scheduled fleet": sched_vals, "Recommended fleet": opt_vals})

        fig_alloc = go.Figure()
        fig_alloc.add_trace(go.Scatter(
            x=alloc["Hour"], y=alloc["Scheduled fleet"], mode="lines+markers",
            name="Scheduled (static timetable)", line=dict(color="#94A3B8", width=2.5, dash="dash"),
            marker=dict(size=7, color="#94A3B8"),
            hovertemplate="<b>%{x}</b><br>Scheduled: %{y} vehicles<extra></extra>"))
        fig_alloc.add_trace(go.Scatter(
            x=alloc["Hour"], y=alloc["Recommended fleet"], mode="lines+markers",
            name="Recommended (OptiMove)", line=dict(color="#166534", width=3),
            marker=dict(size=8, color="#166534"),
            fill="tonexty", fillcolor="rgba(22,101,52,0.08)",
            hovertemplate="<b>%{x}</b><br>Recommended: %{y} vehicles<extra></extra>"))
        fig_alloc.update_layout(
            xaxis_title="Operating Hour", yaxis_title="Vehicles Allocated (selected routes)",
            xaxis=dict(tickangle=-30, showgrid=True, gridcolor="#F1F5F9", title_font=dict(size=12)),
            yaxis=dict(rangemode="tozero", showgrid=True, gridcolor="#F1F5F9", title_font=dict(size=12)),
            height=380, margin=dict(l=16, r=16, t=45, b=16),
            legend=dict(orientation="h", y=1.15, x=0, xanchor="left", font=dict(size=11), bgcolor="rgba(0,0,0,0)"),
            **PLOT_CFG)
        st.plotly_chart(fig_alloc, use_container_width=True)
        st.caption(f"Totals across {len(routes_selected)} selected route(s), each scheduled at {12} buses/hour.")
        st.markdown("</div>", unsafe_allow_html=True)

    with right2:
        st.markdown("<div class='panel'><div class='panel-title'>Savings Breakdown</div>", unsafe_allow_html=True)
        comp_data = [
            {"Component": "Off-peak reductions", "EUR": offpeak_saving,
             "Hover": (f"<b>Off-peak Reductions</b><br>Saving from removing buses during low-demand hours<br>"
                       f"Basis: €{COST_PER_BUS_HOUR}/bus-hr × reduced fleet-hours<br><b>Value: €{offpeak_saving:,.0f}</b>")},
            {"Component": "Peak-period additions", "EUR": peak_cost,
             "Hover": (f"<b>Peak-period Additions</b><br>Cost of deploying extra buses during high-demand hours<br>"
                       f"Basis: €{COST_PER_BUS_HOUR}/bus-hr × additional fleet-hours<br><b>Cost: €{peak_cost:,.0f}</b>")},
            {"Component": "Net effect", "EUR": net_total,
             "Hover": (f"<b>Net Effect</b><br>Off-peak savings minus peak-period costs<br>"
                       f"Off-peak saving: €{offpeak_saving:,.0f}<br>Peak cost: €{peak_cost:,.0f}<br>"
                       f"<b>{'Saving' if net_total >= 0 else 'Net cost'}: €{abs(net_total):,.0f}</b>")},
        ]
        # Two traces grouped by what the colour MEANS (Saving vs Cost), not by
        # component - this gives the legend two entries that explain the
        # green/red convention directly, rather than leaving it implicit.
        # "Net effect" lands in whichever group matches its sign.
        component_order = [c["Component"] for c in comp_data]
        saving = [c for c in comp_data if c["EUR"] >= 0]
        cost = [c for c in comp_data if c["EUR"] < 0]

        fig_comp = go.Figure()
        if saving:
            fig_comp.add_trace(go.Bar(
                x=[c["Component"] for c in saving], y=[c["EUR"] for c in saving],
                name="Saving (€)", marker_color="#166534",
                text=[f"€{c['EUR']:,.0f}" for c in saving], textposition="outside", cliponaxis=False,
                hovertemplate=[c["Hover"] + "<extra></extra>" for c in saving]))
        if cost:
            fig_comp.add_trace(go.Bar(
                x=[c["Component"] for c in cost], y=[c["EUR"] for c in cost],
                name="Cost (€)", marker_color="#DC2626",
                text=[f"€{c['EUR']:,.0f}" for c in cost], textposition="outside", cliponaxis=False,
                hovertemplate=[c["Hover"] + "<extra></extra>" for c in cost]))
        fig_comp.update_layout(
            xaxis_title="Cost Component", yaxis_title="Value (€)",
            xaxis=dict(showgrid=False, title_font=dict(size=12),
                       categoryorder="array", categoryarray=component_order),
            yaxis=dict(showgrid=True, gridcolor="#F1F5F9", zeroline=True, zerolinecolor="#94A3B8",
                       zerolinewidth=1.5,
                       range=[min(0, net_total) - abs(net_total) * 0.25,
                              max(offpeak_saving, peak_cost) * 1.25 + 100],
                       title_font=dict(size=12)),
            height=380, margin=dict(l=16, r=16, t=45, b=16), barmode="group",
            legend=dict(orientation="h", y=1.15, x=0, xanchor="left", font=dict(size=11), bgcolor="rgba(0,0,0,0)"),
            hoverlabel=dict(bgcolor="white", font_size=12, font_family="Inter"), **PLOT_CFG)
        st.plotly_chart(fig_comp, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # Route Deep-Dive — pick one route, see demand AND cost across all hours for the
    # selected period. Fills the gap between the heatmap (all routes x all hours,
    # demand only) and the Scenario table below (one hour x all routes).
    st.markdown("<div class='panel'><div class='panel-title'>Route Profile</div>", unsafe_allow_html=True)
    deepdive_route = st.selectbox("Route", routes_selected, key="deepdive_route")
    rd = (df[df["Route"] == deepdive_route]
          .groupby(["Hour", "Time"], as_index=False)
          .agg(Demand_score=("Demand_score", "mean"),
               Net_cost_impact_eur=("Net_cost_impact_eur", "mean"))
          .sort_values("Hour"))

    fig_rd = go.Figure()
    fig_rd.add_trace(go.Bar(
        x=rd["Time"], y=rd["Demand_score"], name="Avg Demand Score",
        marker_color="#166534", opacity=0.85,
        hovertemplate="<b>%{x}</b><br>Avg Demand Score: %{y:.1f}<extra></extra>"))
    fig_rd.add_hline(y=HIGH_RISK_THRESHOLD, line_dash="dash", line_color="#DC2626",
                     annotation_text=f"Add buses ({HIGH_RISK_THRESHOLD})", annotation_position="top right",
                     annotation_font=dict(color="#DC2626", size=10))
    fig_rd.add_hline(y=LOW_THRESHOLD, line_dash="dash", line_color="#2563EB",
                     annotation_text=f"Reduce buses ({LOW_THRESHOLD})", annotation_position="bottom right",
                     annotation_font=dict(color="#2563EB", size=10))
    fig_rd.add_trace(go.Scatter(
        x=rd["Time"], y=rd["Net_cost_impact_eur"], name="Avg Cost Impact (€, right axis)",
        mode="lines+markers", line=dict(color="#7C3AED", width=2.4),
        marker=dict(size=7, color="#7C3AED", line=dict(color="white", width=1.5)),
        yaxis="y2",
        hovertemplate="<b>%{x}</b><br>Avg Cost Impact: €%{y:,.0f}<extra></extra>"))
    fig_rd.update_layout(
        xaxis_title="Operating Hour", yaxis_title="Avg Demand Score (0–100)",
        yaxis=dict(range=[0, 105], tickvals=[0, 15, 50, 85, 100], showgrid=True,
                   gridcolor="#F1F5F9", title_font=dict(size=12)),
        yaxis2=dict(title="Avg Cost Impact (€, +ve = saving)", overlaying="y", side="right",
                    showgrid=False, title_font=dict(size=12)),
        xaxis=dict(tickangle=-30, showgrid=True, gridcolor="#F1F5F9", title_font=dict(size=12)),
        height=380, margin=dict(l=16, r=78, t=45, b=16),
        legend=dict(orientation="h", y=1.15, x=0, xanchor="left", font=dict(size=11), bgcolor="rgba(0,0,0,0)"),
        **PLOT_CFG)
    st.plotly_chart(fig_rd, use_container_width=True)
    n_days_actual = df["Date"].nunique()
    st.caption(f"{route_profiles[deepdive_route]['desc']} ({deepdive_route}) — averaged "
               f"across {n_days_actual} matching day(s).")
    st.markdown("</div>", unsafe_allow_html=True)

    # Scenario output — one row per route at this hour, averaged across the
    # selected date range (previously one row per date x route: up to
    # n_days x n_routes raw rows for a single hour).
    st.markdown("<div class='panel'><div class='panel-title'>Planning Scenario</div>", unsafe_allow_html=True)

    hour_rows = df[df["Hour"] == focus_hour_int]
    if hour_rows.empty:
        st.info(f"No data available for {focus_hour}. Adjust filters.")
        st.markdown("</div>", unsafe_allow_html=True)
        st.stop()

    scenario = (hour_rows.groupby("Route", as_index=False)
                .agg(Delay_mins=("Delay_mins", "mean"), Rainfall_mm=("Rainfall_mm", "mean"),
                     Demand_score=("Demand_score", "mean")))
    scenario["Demand_score"] = scenario["Demand_score"].round(1)
    recs = scenario["Demand_score"].apply(lambda ds: recommendation(ds, 12))
    scenario["Recommendation"] = recs.apply(lambda x: x[0])
    scenario["Scheduled_fleet"] = 12
    scenario["Recommended_fleet"] = recs.apply(lambda x: x[1])
    scenario["Risk"] = recs.apply(lambda x: x[2])
    scenario["Fleet_delta"] = scenario["Recommended_fleet"] - scenario["Scheduled_fleet"]
    scenario = scenario.sort_values("Demand_score", ascending=False).reset_index(drop=True)
    n_actionable_sp = int((scenario["Fleet_delta"] != 0).sum())

    def highlight_risk_sp(row):
        c = {"High Risk": "background-color:#FEE2E2;color:#7F1D1D;",
             "Moderate": "background-color:#FEF3C7;color:#78350F;",
             "Underutilised": "background-color:#DCFCE7;color:#14532D;"
             }.get(row["Risk"], "")
        return [c] * len(row)

    if n_actionable_sp == 0:
        display_sc = scenario[["Route", "Delay_mins", "Rainfall_mm", "Demand_score", "Risk", "Recommendation"]].copy()
        display_sc.columns = ["Route", "Avg Delay (mins)", "Avg Rainfall (mm/hr)", "Avg Demand Score", "Risk", "Recommendation"]
        st.dataframe(
            display_sc.style.apply(highlight_risk_sp, axis=1)
               .format({"Avg Demand Score": "{:.1f}", "Avg Delay (mins)": "{:.1f}", "Avg Rainfall (mm/hr)": "{:.1f}"})
               .hide(axis="index"),
            use_container_width=True, height=min(360, 46 + 36 * len(display_sc))
        )
    else:
        editor_sc = scenario[["Route", "Demand_score", "Risk", "Recommendation",
                               "Scheduled_fleet", "Recommended_fleet", "Fleet_delta"]].copy()
        editor_sc.insert(0, "Apply", editor_sc["Fleet_delta"] != 0)
        editor_sc = editor_sc.rename(columns={
            "Demand_score": "Avg Demand Score", "Scheduled_fleet": "Scheduled",
            "Recommended_fleet": "Recommended", "Fleet_delta": "Δ Fleet"})

        edited_sc = st.data_editor(
            editor_sc,
            column_config={
                "Apply": st.column_config.CheckboxColumn("Apply?", help="Include this route's recommendation in the plan"),
                "Route": st.column_config.TextColumn("Route", disabled=True),
                "Avg Demand Score": st.column_config.NumberColumn("Avg Demand Score", format="%.1f", disabled=True),
                "Risk": st.column_config.TextColumn("Risk", disabled=True),
                "Recommendation": st.column_config.TextColumn("Recommendation", disabled=True),
                "Scheduled": st.column_config.NumberColumn("Scheduled", format="%d", disabled=True),
                "Recommended": st.column_config.NumberColumn("Recommended", format="%d", disabled=True),
                "Δ Fleet": st.column_config.NumberColumn("Δ Fleet", format="%d", disabled=True),
            },
            hide_index=True, use_container_width=True,
            height=min(360, 46 + 36 * len(editor_sc)),
            key=(f"scenario_editor_{start_d}_{end_d}_{focus_hour}_"
                 f"{','.join(sorted(routes_selected))}_{','.join(sorted(day_types_selected))}"))

        applying_sc = edited_sc[edited_sc["Apply"] & (edited_sc["Δ Fleet"] != 0)]
        n_applying_sc = len(applying_sc)
        bus_moves_sc = int(applying_sc["Δ Fleet"].abs().sum())
        net_per_occurrence = int(((applying_sc["Scheduled"] - applying_sc["Recommended"]) * COST_PER_BUS_HOUR).sum())
        net_extrapolated = net_per_occurrence * n_days_actual

        if n_applying_sc == 0:
            st.caption(f"Toggle 'Apply?' to include routes in the plan for {focus_hour}.")
        else:
            sign = "saving" if net_per_occurrence >= 0 else "cost"
            st.caption(f"Applying {n_applying_sc} of {n_actionable_sp} route(s) at {focus_hour}: "
                       f"{bus_moves_sc} bus-move(s), net €{abs(net_per_occurrence):,.0f} per "
                       f"occurrence → ≈€{abs(net_extrapolated):,.0f} {sign} across "
                       f"{n_days_actual} matching day(s).")

        plan_sc_csv = edited_sc.to_csv(index=False).encode("utf-8")
        st.download_button("Download planning scenario (CSV)", data=plan_sc_csv,
                            file_name=f"optimove_scenario_{focus_hour.replace(':','')}.csv",
                            mime="text/csv", type="primary", use_container_width=True, key="dl_scenario")
    st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.markdown(f"""
<div style="text-align:center;font-size:0.68rem;color:#94A3B8;
     padding:10px 0 2px;border-top:1px solid #E2E8F0;margin-top:6px;">
  OptiMove V2 · €{COST_PER_BUS_HOUR}/bus-hr (NTA, 2021) · Minimum Service Floor {PSO_FLOOR} buses/route-hour
</div>
""", unsafe_allow_html=True)