"""
Global Swing Trading Dashboard
Multi-market Streamlit UI — US, Germany (XETRA), India (NSE).

Pages:
  1.  🏠 Overview            account metrics, market status, quick scan
  2.  📊 Market Regime       SPY/VIX regime, should-trade gate
  3.  🎯 Signals             live signals across all 3 markets (full universe)
  4.  📈 Fundamentals        fundamental scores and ratios
  5.  🔀 Combined Analysis   technical + fundamental combined
  6.  📅 Earnings Calendar   upcoming earnings risk calendar
  7.  👔 Insider Activity    recent insider transactions
  8.  🔍 Stock Screener      custom filter screener
  9.  📋 Trade Journal       log entries, close trades, view history
  10. 📊 Performance         monthly P&L tracking
  11. 💼 Portfolio           open positions, allocation
  12. 📐 Position Calculator  size trades with Fixed-Risk or ATR method
  13. 🔬 Signal Analysis      signal score distribution charts
  14. 🔄 Sector Rotation      US sector ETF relative strength rankings
  15. 🧪 Backtest Pro         walk-forward + Monte Carlo simulation
  16. 📓 Journal Analytics    MAE/MFE, regime & setup performance
  17. ⚙️ Settings             config display

Launch:  streamlit run dashboard.py   |   python run_dashboard.py
"""

# ── Bootstrap: add all module subdirectories to sys.path ───────────────────────
import sys as _sys, os as _os
_APP_ROOT = _os.path.dirname(_os.path.abspath(__file__))
for _sub in ["core", "analysis", "signals", "screening", "portfolio",
             "strategies", "research", "automation"]:
    _p = _os.path.join(_APP_ROOT, _sub)
    if _p not in _sys.path:
        _sys.path.insert(0, _p)

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import config

# ── Page config MUST be the very first Streamlit call ───────────────────────
st.set_page_config(
    page_title="Global Trading Dashboard",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ── Professional light-theme CSS ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:ital,opsz,wght@0,14..32,300..700;1,14..32,300..700&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Base font only — do NOT set color globally (breaks Streamlit internals) ── */
html, body { font-family: 'Inter', -apple-system, sans-serif; }

/* ── App background ──────────────────────────────────────────────────── */
.stApp { background-color: #f0f4f8 !important; }
.main .block-container { padding-top: 1.5rem; padding-bottom: 2rem; max-width: 1440px; }

/* ── Sidebar ─────────────────────────────────────────────────────────── */
section[data-testid="stSidebar"] {
    background: #ffffff !important;
    border-right: 1px solid #e2e8f0;
}
section[data-testid="stSidebar"] > div { padding-top: 0.5rem; }

/* ── Typography — target semantic elements, never bare span/div ──────── */
h1 {
    font-weight: 700 !important; font-size: 1.75rem !important;
    letter-spacing: -.025em !important; color: #0f172a !important;
    padding-bottom: .6rem !important;
    border-bottom: 2px solid #e2e8f0 !important; margin-bottom: 1.5rem !important;
}
h2 { font-weight: 600 !important; color: #1e293b !important; font-size: 1.25rem !important; }
h3 { font-weight: 600 !important; color: #374151 !important; font-size: 1.05rem !important; }
p, li, span, td, th { color: #1e293b; }

/* ── Widget labels ───────────────────────────────────────────────────── */
label,
[data-testid="stWidgetLabel"],
[data-testid="stWidgetLabel"] *,
[data-testid="stWidgetLabel"] p {
    color: #1e293b !important;
    font-size: .85rem !important;
    font-weight: 500 !important;
}

/* ── Text & number inputs ────────────────────────────────────────────── */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stTextArea > div > div > textarea {
    background: #ffffff !important;
    border: 1px solid #cbd5e1 !important;
    border-radius: 8px !important;
    color: #0f172a !important;
    caret-color: #0f172a !important;
    font-size: .875rem !important;
}
.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #0077b6 !important;
    box-shadow: 0 0 0 3px rgba(0,119,182,.12) !important;
    outline: none !important;
}

/* ── Selectbox ───────────────────────────────────────────────────────── */
.stSelectbox [data-baseweb="select"] > div,
.stSelectbox [data-baseweb="select"] > div:hover {
    background: #ffffff !important;
    border: 1px solid #cbd5e1 !important;
    border-radius: 8px !important;
}
.stSelectbox [data-baseweb="select"] span,
.stSelectbox [data-baseweb="select"] div,
.stSelectbox [data-baseweb="select"] input {
    color: #0f172a !important;
    background: transparent !important;
}
/* Selectbox dropdown list */
[data-baseweb="popover"] [role="listbox"],
[data-baseweb="popover"] [role="option"],
[data-baseweb="menu"] li {
    background: #ffffff !important;
    color: #0f172a !important;
}
[data-baseweb="popover"] [aria-selected="true"],
[data-baseweb="popover"] [role="option"]:hover {
    background: #eff6ff !important;
    color: #0077b6 !important;
}

/* ── Multiselect ─────────────────────────────────────────────────────── */
.stMultiSelect [data-baseweb="select"] > div {
    background: #ffffff !important;
    border: 1px solid #cbd5e1 !important;
    border-radius: 8px !important;
    min-height: 40px !important;
}
/* Placeholder text */
.stMultiSelect [data-baseweb="select"] input,
.stMultiSelect [data-baseweb="select"] [data-testid="stMultiSelectInput"],
.stMultiSelect [placeholder] {
    color: #64748b !important;
}
/* Selected tags */
.stMultiSelect span[data-baseweb="tag"] {
    background: #dbeafe !important;
    border: 1px solid #93c5fd !important;
    border-radius: 6px !important;
    color: #1d4ed8 !important;
    font-weight: 600 !important;
    font-size: .78rem !important;
}
/* Tag label text */
.stMultiSelect span[data-baseweb="tag"] span { color: #1d4ed8 !important; }
/* Tag remove × button */
.stMultiSelect span[data-baseweb="tag"] svg { fill: #1d4ed8 !important; }

/* ── Metric cards ────────────────────────────────────────────────────── */
[data-testid="metric-container"] {
    background: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 12px !important;
    padding: 1rem 1.25rem !important;
    box-shadow: 0 1px 4px rgba(15,23,42,.06) !important;
    transition: border-color .2s, box-shadow .2s;
}
[data-testid="metric-container"]:hover {
    border-color: #0077b6 !important;
    box-shadow: 0 4px 16px rgba(0,119,182,.1) !important;
}
[data-testid="stMetricLabel"] {
    font-size: .72rem !important; font-weight: 600 !important;
    text-transform: uppercase !important; letter-spacing: .09em !important;
    color: #64748b !important;
}
[data-testid="stMetricValue"] {
    font-size: 1.55rem !important; font-weight: 700 !important;
    font-family: 'JetBrains Mono', monospace !important;
    color: #0f172a !important;
}
[data-testid="stMetricDelta"] { font-size: .8rem !important; font-weight: 500 !important; }

/* ── Buttons ─────────────────────────────────────────────────────────── */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #0077b6 0%, #0096c7 100%) !important;
    border: none !important; border-radius: 8px !important; color: #fff !important;
    font-weight: 600 !important; font-size: .85rem !important; letter-spacing: .03em !important;
    padding: .5rem 1.6rem !important; transition: all .2s !important;
    box-shadow: 0 2px 10px rgba(0,119,182,.25) !important;
}
.stButton > button[kind="primary"]:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 18px rgba(0,119,182,.35) !important;
}
.stButton > button:not([kind="primary"]) {
    background: #ffffff !important; border: 1px solid #cbd5e1 !important;
    border-radius: 8px !important; color: #475569 !important;
    font-weight: 500 !important; transition: all .2s !important;
}
.stButton > button:not([kind="primary"]):hover {
    background: #f1f5f9 !important; border-color: #0077b6 !important; color: #0077b6 !important;
}

/* ── Tabs ────────────────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    background: #e2e8f0 !important; border-radius: 10px !important;
    padding: 4px !important; gap: 2px !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 7px !important; font-weight: 500 !important;
    font-size: .85rem !important; color: #475569 !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg,#0077b6,#0096c7) !important;
    color: #fff !important;
    box-shadow: 0 2px 8px rgba(0,119,182,.25) !important;
}

/* ── Slider ──────────────────────────────────────────────────────────── */
[data-baseweb="slider"] [data-testid="stThumbValue"] { color: #0077b6 !important; }
[role="slider"] { background: #0077b6 !important; }

/* ── Radio & Checkbox ────────────────────────────────────────────────── */
.stRadio div[role="radiogroup"] label,
.stCheckbox label { color: #1e293b !important; font-weight: 500 !important; }

/* ── DataFrames ──────────────────────────────────────────────────────── */
.stDataFrame {
    border-radius: 12px !important; overflow: hidden !important;
    border: 1px solid #e2e8f0 !important;
    box-shadow: 0 1px 4px rgba(15,23,42,.06) !important;
}

/* ── Expander ────────────────────────────────────────────────────────── */
[data-testid="stExpander"] {
    border: 1px solid #e2e8f0 !important;
    border-radius: 10px !important;
    background: #ffffff !important;
    margin-bottom: .5rem !important;
}
[data-testid="stExpander"] summary {
    background: #f8fafc !important;
    color: #1e293b !important;
    font-weight: 600 !important;
    font-size: .85rem !important;
    padding: .6rem 1rem !important;
}
[data-testid="stExpander"] [data-testid="stMarkdownContainer"] p,
[data-testid="stExpander"] [data-testid="stMarkdownContainer"] li,
[data-testid="stExpander"] [data-testid="stMarkdownContainer"] strong,
[data-testid="stExpander"] [data-testid="stMarkdownContainer"] em {
    color: #1e293b !important;
}
[data-testid="stExpander"] ul,
[data-testid="stExpander"] ol { padding-left: 1.2rem !important; }
.streamlit-expanderHeader {
    background: #f8fafc !important; border-radius: 8px 8px 0 0 !important;
    font-weight: 600 !important; color: #1e293b !important; font-size: .85rem !important;
}
.streamlit-expanderContent { background: #ffffff !important; color: #1e293b !important; }

/* ── Alerts (info / warning / success / error) ───────────────────────── */
[data-testid="stAlert"] p { color: inherit !important; }

/* ── Code ────────────────────────────────────────────────────────────── */
.stCode, code, pre {
    font-family: 'JetBrains Mono', monospace !important;
    background: #f1f5f9 !important;
    border: 1px solid #e2e8f0 !important; border-radius: 8px !important;
    color: #1e293b !important;
}

/* ── Divider ─────────────────────────────────────────────────────────── */
hr { border-color: #e2e8f0 !important; margin: 1.5rem 0 !important; }

/* ── Caption ─────────────────────────────────────────────────────────── */
.stCaption, [data-testid="stCaption"] { color: #64748b !important; font-size: .78rem !important; }

/* ── Scrollbar ───────────────────────────────────────────────────────── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: #f1f5f9; }
::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #94a3b8; }

/* ── Signal badge utility classes ────────────────────────────────────── */
.badge {
    display: inline-block; padding: 3px 10px; border-radius: 20px;
    font-size: .7rem; font-weight: 700; letter-spacing: .07em; text-transform: uppercase;
}
.badge-strong { background:#dcfce7; color:#15803d; border:1px solid #86efac; }
.badge-buy    { background:#d1fae5; color:#059669; border:1px solid #6ee7b7; }
.badge-watch  { background:#fef9c3; color:#a16207; border:1px solid #fde047; }
.badge-avoid  { background:#fee2e2; color:#dc2626; border:1px solid #fca5a5; }
.badge-hold   { background:#f1f5f9; color:#64748b; border:1px solid #cbd5e1; }

/* ── KPI stat card ───────────────────────────────────────────────────── */
.kpi-card {
    background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px;
    padding: 1rem 1.25rem; text-align: center;
    box-shadow: 0 1px 4px rgba(15,23,42,.06);
}
.kpi-label { font-size:.7rem; font-weight:600; text-transform:uppercase; letter-spacing:.09em; color:#64748b; }
.kpi-value { font-size:1.5rem; font-weight:700; font-family:'JetBrains Mono',monospace; color:#0f172a; margin:.2rem 0; }
.kpi-sub   { font-size:.75rem; color:#94a3b8; }

/* ── Sidebar nav (stray button fallback) ─────────────────────────────── */
section[data-testid="stSidebar"] .stButton > button {
    border-radius: 7px !important; font-size: .8rem !important;
    font-weight: 500 !important; transition: all .15s;
}
</style>
""", unsafe_allow_html=True)

# ── Optional module imports (graceful degradation if a module errors) ────────
# Each module tried individually — one bad import won't kill the whole UI.
def _try_import(name):
    try:
        return __import__(name)
    except Exception:
        return None

_gdf  = _try_import("global_data_fetcher")
_gsg  = _try_import("global_signal_generator")
_ta   = _try_import("technical_analyzer")
_fa   = _try_import("fundamental_analyzer")
_ca   = _try_import("combined_analyzer")
_mr   = _try_import("market_regime")
_pm   = _try_import("position_manager")
_tj   = _try_import("trade_journal")
_pt   = _try_import("performance_tracker")
_bt   = _try_import("backtester")
_ec   = _try_import("earnings_calendar")
_it   = _try_import("insider_tracker")
_ss   = _try_import("stock_screener")
_sr   = _try_import("sector_rotation")
_mc   = _try_import("market_config")
_yf   = _try_import("yfinance")
_wi   = _try_import("weekend_investing_strategy")

# Availability flags used throughout for guarding UI sections
HAS_GDF    = _gdf  is not None
HAS_WI     = _wi   is not None
HAS_GSG    = _gsg  is not None
HAS_TA     = _ta   is not None
HAS_FA     = _fa   is not None
HAS_CA     = _ca   is not None
HAS_REGIME = _mr   is not None
HAS_PM     = _pm   is not None
HAS_JOURNAL= _tj   is not None
HAS_PT     = _pt   is not None
HAS_BT     = _bt   is not None
HAS_EARN   = _ec   is not None
HAS_INSIDER= _it   is not None
HAS_SS     = _ss   is not None
HAS_SR     = _sr   is not None
HAS_MC     = _mc   is not None
HAS_YF     = _yf   is not None

# ── Cached resource initialisation ──────────────────────────────────────────
# st.cache_resource keeps one instance alive across all Streamlit reruns.
@st.cache_resource
def _init_resources():
    res = {}
    if HAS_GDF:    res["fetcher"]  = _gdf.GlobalDataFetcher()
    if HAS_GSG:    res["gen"]      = _gsg.GlobalSignalGenerator()
    if HAS_TA:     res["analyzer"] = _ta.TechnicalAnalyzer()
    if HAS_FA:     res["fa"]       = _fa.FundamentalAnalyzer()
    if HAS_CA:     res["ca"]       = _ca.CombinedAnalyzer()
    if HAS_REGIME: res["regime"]   = _mr.MarketRegimeFilter()
    if HAS_PM:     res["pm"]       = _pm.PositionManager()
    if HAS_JOURNAL:res["journal"]  = _tj.TradeJournal()
    if HAS_PT:     res["pt"]       = _pt.PerformanceTracker()
    if HAS_BT:     res["bt"]       = _bt.Backtester()
    if HAS_EARN:   res["earn"]     = _ec.EarningsCalendar()
    if HAS_INSIDER:res["insider"]  = _it.InsiderTracker()
    if HAS_SS:     res["screener"] = _ss.StockScreener()
    return res

C = _init_resources()

# ── Page help utility ────────────────────────────────────────────────────────
def _help(md: str):
    """Collapsible info panel shown at the top of each page for new users."""
    with st.expander("ℹ️  How to use this page", expanded=False):
        st.markdown(md)

# ── Sidebar navigation ───────────────────────────────────────────────────────
st.sidebar.markdown("""
<div style="padding:.75rem 1rem 1rem; border-bottom:1px solid #e2e8f0; margin-bottom:.75rem;">
  <div style="font-size:1.2rem;font-weight:800;color:#0f172a;letter-spacing:-.02em;">
    🌍 Global Trading
  </div>
  <div style="font-size:.72rem;color:#94a3b8;font-weight:500;letter-spacing:.05em;text-transform:uppercase;margin-top:.15rem;">
    Multi-Market Dashboard
  </div>
</div>
""", unsafe_allow_html=True)

_acct_target = config.ACCOUNT_SIZE * config.MONTHLY_TARGET
st.sidebar.markdown(f"""
<div style="background:#f8fafc;
            border:1px solid #e2e8f0;border-radius:10px;
            padding:.65rem 1rem;margin:.5rem 0 1rem;font-size:.78rem;">
  <div style="display:flex;justify-content:space-between;margin-bottom:.3rem;">
    <span style="color:#64748b;font-weight:600;text-transform:uppercase;letter-spacing:.06em;font-size:.68rem;">Account</span>
    <span style="color:#0f172a;font-family:'JetBrains Mono',monospace;font-weight:700;">${config.ACCOUNT_SIZE:,}</span>
  </div>
  <div style="display:flex;justify-content:space-between;">
    <span style="color:#64748b;font-weight:600;text-transform:uppercase;letter-spacing:.06em;font-size:.68rem;">Monthly Target</span>
    <span style="color:#059669;font-family:'JetBrains Mono',monospace;font-weight:700;">${_acct_target:,.0f} &nbsp;<span style="color:#94a3b8;font-size:.65rem;">({config.MONTHLY_TARGET*100:.0f}%)</span></span>
  </div>
</div>
""", unsafe_allow_html=True)

NAV_GROUPS = [
    ("📊 Market", [
        "🏠 Overview", "📊 Market Regime", "🎯 Signals",
        "📈 Fundamentals", "🔀 Combined Analysis",
    ]),
    ("� Research", [
        "📅 Earnings Calendar", "👔 Insider Activity",
    ]),
    ("🔧 Tools", [
        "🔍 Stock Screener", "📐 Position Calculator",
        "🔬 Signal Analysis", "🔄 Sector Rotation",
    ]),
    ("💼 Portfolio", [
        "💼 Portfolio", "📋 Trade Journal",
        "📊 Performance", "📓 Journal Analytics",
    ]),
    ("🚀 Strategies", [
        "🧪 Backtest Pro", "🏆 Weekend Investing (MI)",
    ]),
    ("⚙️ System", ["⚙️ Settings"]),
]
PAGES = [p for _, grp in NAV_GROUPS for p in grp]

# URL-based routing — each browser tab independently tracks its page via ?page=…
_default_page = "🏠 Overview"
page = st.query_params.get("page", _default_page)
if page not in PAGES:
    page = _default_page

# ── Build full HTML sidebar nav (no st.button — full CSS control) ─────────────
import urllib.parse as _urlparse

_nav_items_html = ""
for _grp_label, _grp_pages in NAV_GROUPS:
    _nav_items_html += f'<div class="snav-group">{_grp_label}</div>'
    for _p in _grp_pages:
        _active = " snav-active" if _p == page else ""
        _href = "?" + _urlparse.urlencode({"page": _p})
        _nav_items_html += (
            f'<a href="{_href}" class="snav-item{_active}" target="_self">{_p}</a>'
        )

# Module status row
_mod_status_html = "".join(
    f'<span class="mod-dot" style="background:{"#10b981" if ok else "#e2e8f0"}" '
    f'title="{lbl}: {"OK" if ok else "unavailable"}"></span>'
    for lbl, ok in [
        ("Signals",      HAS_GSG),
        ("Fundamentals", HAS_FA),
        ("Regime",       HAS_REGIME),
        ("Journal",      HAS_JOURNAL),
        ("Screener",     HAS_SS),
        ("Earnings",     HAS_EARN),
        ("Insider",      HAS_INSIDER),
        ("Sector Rot.",  HAS_SR),
        ("Backtester",   HAS_BT),
        ("WI",           HAS_WI),
    ]
)

st.sidebar.markdown(f"""
<style>
/* ── Sidebar nav ─────────────────────────────────────── */
.snav-group {{
    font-size: .58rem; font-weight: 700; text-transform: uppercase;
    letter-spacing: .1em; color: #94a3b8;
    padding: .9rem 1rem .2rem; margin: 0;
}}
.snav-item {{
    display: flex; align-items: center;
    padding: .42rem 1rem .42rem 1.1rem;
    margin: 1px 6px; border-radius: 7px;
    font-size: .82rem; font-weight: 400; color: #475569;
    text-decoration: none !important;
    border-left: 2.5px solid transparent;
    transition: background .1s, color .1s;
    line-height: 1.4;
}}
.snav-item:hover {{
    background: #f1f5f9; color: #1e293b;
    text-decoration: none !important;
}}
.snav-active {{
    background: #eff6ff !important; color: #0077b6 !important;
    font-weight: 600 !important; border-left-color: #0077b6 !important;
}}
.snav-active:hover {{ background: #dbeafe !important; }}
/* ── Module status dots ──────────────────────────────── */
.mod-dots-wrap {{
    padding: .6rem 1rem .8rem; border-top: 1px solid #e2e8f0; margin-top: .4rem;
    display: flex; align-items: center; gap: .35rem; flex-wrap: wrap;
}}
.mod-label {{
    font-size: .58rem; font-weight: 700; text-transform: uppercase;
    letter-spacing: .1em; color: #94a3b8; margin-right: .2rem;
}}
.mod-dot {{
    width: 7px; height: 7px; border-radius: 50%; display: inline-block;
}}
</style>

{_nav_items_html}

<div class="mod-dots-wrap">
  <span class="mod-label">Modules</span>
  {_mod_status_html}
</div>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: OVERVIEW
# ═══════════════════════════════════════════════════════════════════════════════
if page == "🏠 Overview":
    st.title("🏠 Trading Dashboard Overview")
    _help(
        "**Overview** shows live index snapshots, your account configuration, and a multi-market quick scan.\n"
        "- **Markets** — choose which exchanges (US / DE / IN) to scan\n"
        "- Click **Scan Now** to fetch live signals across the full universe\n"
        "- Best used as a morning dashboard before market open to check overall market health"
    )
    st.markdown(
        f'<p style="color:#475569;font-size:.85rem;margin-top:-.8rem;margin-bottom:1.2rem;">'
        f'{datetime.now().strftime("%A, %d %B %Y  ·  %H:%M")} &nbsp;|&nbsp; '
        f'Risk / trade: <b style="color:#00b4d8;">{config.RISK_PER_TRADE*100:.1f}%</b> &nbsp;|&nbsp; '
        f'Max positions: <b style="color:#00b4d8;">{config.MAX_POSITIONS}</b></p>',
        unsafe_allow_html=True,
    )

    # Account metrics
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Account Size",   f"${config.ACCOUNT_SIZE:,}")
    c2.metric("Monthly Target", f"${config.ACCOUNT_SIZE * config.MONTHLY_TARGET:,.0f} ({config.MONTHLY_TARGET*100:.0f}%)")
    c3.metric("Risk / Trade",   f"{config.RISK_PER_TRADE*100:.1f}%  (${config.ACCOUNT_SIZE * config.RISK_PER_TRADE:,.0f})")
    c4.metric("Max Positions",  config.MAX_POSITIONS)

    st.markdown("---")

    # Live index snapshot
    st.subheader("Market Indices")
    if HAS_YF:
        idx_cols = st.columns(4)
        for i, (sym, label) in enumerate([("SPY","S&P 500"),("QQQ","NASDAQ 100"),("^VIX","VIX"),("^GDAXI","DAX")]):
            try:
                fi = _yf.Ticker(sym).fast_info
                price = getattr(fi, "last_price", None) or getattr(fi, "regular_market_price", 0)
                chg   = getattr(fi, "regular_market_change_percent", 0) or 0
                idx_cols[i].metric(label, f"{price:.2f}", f"{chg:+.2f}%")
            except Exception:
                idx_cols[i].metric(label, "N/A")

    st.markdown("---")

    # Quick scan — uses GlobalSignalGenerator with full universe across chosen markets
    st.subheader("Quick Scan — All Markets")
    if not HAS_GSG:
        st.error("GlobalSignalGenerator not available.")
    else:
        ov_markets = st.multiselect("Markets", ["US","DE","IN"], default=["US","DE","IN"], key="ov_mkts")
        if st.button("🔍 Scan Now", type="primary"):
            with st.spinner("Scanning all markets…"):
                try:
                    sigs = C["gen"].generate_signals(markets=ov_markets)
                    all_sigs = [s for mkt_sigs in sigs.values() for s in mkt_sigs]
                    strong = sum(1 for s in all_sigs if s.get("signal_status") == "STRONG BUY")
                    buys   = sum(1 for s in all_sigs if s.get("signal_status") == "BUY")
                    st.success(f"**{strong} STRONG BUY** and **{buys} BUY** across {len(ov_markets)} markets")
                    if all_sigs:
                        df = pd.DataFrame(all_sigs)
                        cols = ["symbol","market","signal_status","signal_score","current_price",
                                "ideal_entry","stop_loss","target_1","risk_reward"]
                        st.dataframe(df[[c for c in cols if c in df.columns]],
                                     use_container_width=True, hide_index=True)
                except Exception as e:
                    st.error(f"Scan error: {e}")

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: MARKET REGIME
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "📊 Market Regime":
    st.title("📊 Market Regime Analysis")
    _help(
        "Determines whether market conditions favour swing trading.\n"
        "- ✅ **TRADE** — conditions are favourable; proceed with new entries\n"
        "- 🚫 **PAUSE** — elevated risk; hold existing positions only, no new buys\n"
        "- **Confidence %** — above 70% = clear signal; below 60% = treat as neutral\n"
        "- Refresh every morning before placing orders"
    )

    if not HAS_REGIME:
        st.error("market_regime module not available.")
    else:
        if st.button("🔄 Refresh", type="primary"):
            st.cache_data.clear()

        @st.cache_data(ttl=600, show_spinner="Analysing regime…")
        def _get_regime():
            return _mr.MarketRegimeFilter().analyze()

        try:
            cond = _get_regime()
            regime_obj = _mr.MarketRegimeFilter()
            tradeable, reason, confidence = regime_obj.should_trade()

            gc, cc = st.columns([2, 1])
            if tradeable:
                gc.success(f"✅ **TRADE** — {reason}")
            else:
                gc.error(f"🚫 **PAUSE TRADING** — {reason}")
            cc.metric("Confidence", f"{confidence:.0f}%")

            st.markdown("---")
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("SPY Price",     f"${getattr(cond,'spy_price',0):.2f}")
            m2.metric("VIX",           f"{getattr(cond,'vix',0):.1f}")
            m3.metric("Above 50 EMA",  "✅" if cond.above_ema50  else "❌")
            m4.metric("Above 200 EMA", "✅" if cond.above_ema200 else "❌")
        except Exception as e:
            st.error(f"Regime error: {e}")

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: SIGNALS — full multi-market, full universe, no hardcoded [:15] limit
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "🎯 Signals":
    st.title("🎯 Trading Signals — All Markets")
    _help(
        "Generates ranked technical buy/sell signals across the full stock universe.\n"
        "- **Markets** — select US, German (XETRA), or Indian (NSE) exchanges\n"
        "- **Minimum strength** — *BUY* shows actionable setups; *STRONG BUY* = highest conviction only\n"
        "- Click **Generate Signals** — fetches live data and may take 30–60 seconds\n"
        "- Results are sorted by score; focus on the top 5–10 with the highest scores"
    )

    if not HAS_GSG:
        st.error("GlobalSignalGenerator not available.")
    else:
        f1, f2 = st.columns(2)
        sig_markets = f1.multiselect("Markets", ["US","DE","IN"], default=["US","DE","IN"], key="sig_mkts")
        min_status  = f2.selectbox("Minimum strength", ["STRONG BUY","BUY","WATCH"], index=1)

        if st.button("⚡ Generate Signals", type="primary"):
            with st.spinner(f"Scanning {', '.join(sig_markets)} — full ranked universe…"):
                try:
                    raw = C["gen"].generate_signals(markets=sig_markets)
                    all_sigs = [s for mkt_sigs in raw.values() for s in mkt_sigs]

                    # Filter by selected minimum strength
                    order = {"STRONG BUY": 3, "BUY": 2, "WATCH": 1, "AVOID": 0}
                    threshold = order.get(min_status, 1)
                    filtered = [s for s in all_sigs if order.get(s.get("signal_status","AVOID"), 0) >= threshold]

                    if not filtered:
                        st.info("No signals match the selected criteria.")
                    else:
                        st.success(f"**{len(filtered)} signals** found")

                        # Per-market counts
                        sm_cols = st.columns(len(sig_markets))
                        for i, mkt in enumerate(sig_markets):
                            sm_cols[i].metric(f"{mkt}", sum(1 for s in filtered if s.get("market") == mkt))

                        st.markdown("---")

                        # Full signal table
                        df = pd.DataFrame(filtered)
                        show = ["symbol","name","market","signal_status","signal_score","sector",
                                "current_price","ideal_entry","stop_loss","target_1","target_2",
                                "risk_reward","rsi","days_to_earnings","earnings_warning"]
                        st.dataframe(df[[c for c in show if c in df.columns]],
                                     use_container_width=True, hide_index=True)

                        # Detailed alert for top signal
                        st.markdown("---")
                        st.subheader("Top Signal Detail")
                        best = max(filtered, key=lambda s: s.get("signal_score", 0))
                        st.code(C["gen"].format_alert(best), language=None)

                except Exception as e:
                    st.error(f"Signal error: {e}")

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: FUNDAMENTALS
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "📈 Fundamentals":
    st.title("📈 Fundamental Analysis")
    _help(
        "Pulls fundamental data (P/E, revenue growth, margins, debt) from yfinance for any ticker.\n"
        "- Enter a ticker in any format: `NVDA` (US), `SAP.DE` (Germany), `TCS.NS` (India)\n"
        "- **Fundamental Score 60+** = solid quality; **below 40** = avoid\n"
        "- Use this page *after* Signals — fundamentals confirm technical setups, not replace them"
    )

    if not HAS_FA:
        st.error("fundamental_analyzer module not available.")
    else:
        symbol = st.text_input("Symbol (e.g. NVDA, SAP.DE, TCS.NS)", "NVDA").upper().strip()
        if st.button("Analyze"):
            with st.spinner(f"Fetching fundamentals for {symbol}…"):
                try:
                    result = C["fa"].analyze(symbol)
                    if result is None:
                        st.error("No data returned — check symbol format (e.g. NVDA, SAP.DE, TCS.NS)")
                    else:
                        c1, c2, c3, c4 = st.columns(4)
                        pe = result.pe_ratio
                        c1.metric("P/E Ratio",      f"{pe:.1f}" if pe and pe > 0 else "N/A")
                        c2.metric("Revenue Growth", f"{result.revenue_growth*100:.1f}%")
                        c3.metric("Profit Margin",  f"{result.profit_margin*100:.1f}%")
                        c4.metric("Fund. Score",    f"{result.overall_score}/100")

                        st.divider()
                        col_a, col_b, col_c = st.columns(3)
                        with col_a:
                            st.subheader("📊 Valuation")
                            st.write(f"**Forward P/E:** {result.forward_pe:.1f}" if result.forward_pe else "**Forward P/E:** N/A")
                            st.write(f"**P/B:** {result.pb_ratio:.2f}" if result.pb_ratio else "**P/B:** N/A")
                            st.write(f"**EV/EBITDA:** {result.ev_to_ebitda:.1f}" if result.ev_to_ebitda else "**EV/EBITDA:** N/A")
                            st.write(f"**Div. Yield:** {result.dividend_yield*100:.2f}%" if result.dividend_yield else "**Div. Yield:** —")
                        with col_b:
                            st.subheader("💰 Profitability")
                            st.write(f"**ROE:** {result.roe*100:.1f}%")
                            st.write(f"**ROA:** {result.roa*100:.1f}%")
                            st.write(f"**Gross Margin:** {result.gross_margin*100:.1f}%")
                            st.write(f"**FCF Margin:** {result.fcf_margin*100:.1f}%")
                        with col_c:
                            st.subheader("📈 Growth")
                            st.write(f"**Rev Growth:** {result.revenue_growth*100:.1f}%")
                            st.write(f"**Rev Growth 3Y:** {result.revenue_growth_3y*100:.1f}%")
                            st.write(f"**EPS Growth:** {result.earnings_growth*100:.1f}%")
                            st.write(f"**Debt/Equity:** {result.debt_to_equity:.2f}" if result.debt_to_equity else "**Debt/Equity:** N/A")


                except Exception as e:
                    st.error(f"Error: {e}")

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: COMBINED ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "🔀 Combined Analysis":
    st.title("🔀 Combined Technical + Fundamental Analysis")
    _help(
        "Merges the technical signal score with the fundamental quality score into one composite rating.\n"
        "- Enter any ticker and click **Analyse**\n"
        "- **Score 70+** = high-conviction trade candidate; **50–70** = watchlist only\n"
        "- Use this to reduce false positives from the Signals page — only trade stocks with good fundamentals too"
    )

    if not HAS_CA:
        st.error("combined_analyzer module not available.")
    else:
        symbol = st.text_input("Symbol", "AAPL").upper().strip()
        if st.button("Analyse"):
            with st.spinner(f"Analysing {symbol}…"):
                try:
                    result = C["ca"].analyze(symbol)
                    if result is not None:
                        # ── Header banner ────────────────────────────────────
                        qcolors = {"A+": ("#00ff9d","#003d28"), "A": ("#00cc96","#002e22"),
                                   "B": ("#fbb703","#2e2300"), "C": ("#fb923c","#2e1500"), "D": ("#ef5350","#2e0808")}
                        qfg, qbg = qcolors.get(result.trade_quality, ("#94a3b8","#1e293b"))
                        sig_badge_cls = {"STRONG BUY":"badge-strong","BUY":"badge-buy",
                                         "BUY (Weak Fundamentals)":"badge-buy",
                                         "WAIT (Good Company, Bad Timing)":"badge-watch",
                                         "CAUTION (Poor Fundamentals)":"badge-watch",
                                         "HOLD":"badge-hold"}.get(result.combined_signal,"badge-hold")
                        st.markdown(f"""
<div style="background:linear-gradient(135deg,#0d1321,#111827);border:1px solid rgba(0,180,216,.2);
            border-radius:14px;padding:1.2rem 1.5rem;margin-bottom:1.2rem;">
  <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:.5rem;">
    <div>
      <div style="font-size:1.5rem;font-weight:800;color:#f1f5f9;letter-spacing:-.02em;">
        {result.name} &nbsp;<span style="color:#4b5e7a;font-size:1rem;font-weight:500;">({result.symbol})</span>
      </div>
      <div style="font-size:.8rem;color:#64748b;margin-top:.2rem;">{result.sector}</div>
    </div>
    <div style="display:flex;align-items:center;gap:.75rem;">
      <span class="badge {sig_badge_cls}">{result.combined_signal}</span>
      <span style="background:{qbg};color:{qfg};border:1px solid {qfg}44;border-radius:10px;
                   padding:4px 14px;font-size:.8rem;font-weight:800;letter-spacing:.05em;">
        {result.trade_quality}
      </span>
    </div>
  </div>
  <div style="margin-top:.8rem;font-size:.95rem;color:#94a3b8;">{result.recommendation}</div>
</div>
""", unsafe_allow_html=True)

                        # ── Score gauges ─────────────────────────────────────
                        def _gauge_bar(score, color="#00b4d8"):
                            pct = min(max(score, 0), 100)
                            return (f'<div style="background:rgba(255,255,255,.05);border-radius:4px;height:6px;margin-top:.4rem;">'
                                    f'<div style="width:{pct}%;height:100%;border-radius:4px;'
                                    f'background:linear-gradient(90deg,{color}99,{color});"></div></div>')

                        def _score_card(label, score, color="#00b4d8"):
                            return (f'<div style="background:linear-gradient(135deg,#0d1321,#111827);'
                                    f'border:1px solid rgba(0,180,216,.15);border-radius:12px;padding:.9rem 1rem;">'
                                    f'<div style="font-size:.68rem;font-weight:700;text-transform:uppercase;'
                                    f'letter-spacing:.09em;color:#4b5e7a;">{label}</div>'
                                    f'<div style="font-size:1.6rem;font-weight:800;font-family:JetBrains Mono,monospace;'
                                    f'color:{color};margin:.15rem 0;">{score}<span style="font-size:.85rem;color:#4b5e7a;">/100</span></div>'
                                    f'{_gauge_bar(score, color)}</div>')

                        tech_color  = "#00cc96" if result.technical_score  >= 60 else ("#fbb703" if result.technical_score  >= 40 else "#ef5350")
                        fund_color  = "#00cc96" if result.fundamental_score >= 60 else ("#fbb703" if result.fundamental_score >= 40 else "#ef5350")
                        comb_color  = "#00cc96" if result.combined_score    >= 60 else ("#fbb703" if result.combined_score    >= 40 else "#ef5350")

                        gc1, gc2, gc3 = st.columns(3)
                        gc1.markdown(_score_card("Technical Score",    result.technical_score,   tech_color), unsafe_allow_html=True)
                        gc2.markdown(_score_card("Fundamental Score",  result.fundamental_score, fund_color), unsafe_allow_html=True)
                        gc3.markdown(_score_card("Combined Score",     result.combined_score,    comb_color), unsafe_allow_html=True)

                        st.divider()

                        # ── Trade setup ──────────────────────────────────────
                        col_left, col_right = st.columns(2)

                        with col_left:
                            st.subheader("📈 Trade Setup")
                            risk = result.entry_price - result.stop_loss
                            rr1 = (result.target_1 - result.entry_price) / risk if risk > 0 else 0
                            rr2 = (result.target_2 - result.entry_price) / risk if risk > 0 else 0
                            st.markdown(f"""
| Field | Value |
|---|---|
| **Signal** | {result.technical_signal} |
| **Setup** | {result.setup_type} |
| **Trend** | {result.trend} |
| **Current Price** | ${result.current_price:,.2f} |
| **Entry Price** | ${result.entry_price:,.2f} |
| **Stop Loss** | ${result.stop_loss:,.2f} ({((result.stop_loss - result.entry_price) / result.entry_price * 100):.1f}%) |
| **Target 1** | ${result.target_1:,.2f} ({((result.target_1 - result.entry_price) / result.entry_price * 100):.1f}%) |
| **Target 2** | ${result.target_2:,.2f} ({((result.target_2 - result.entry_price) / result.entry_price * 100):.1f}%) |
| **R:R (T1)** | {rr1:.2f} |
| **R:R (T2)** | {rr2:.2f} |
| **RSI** | {result.rsi:.1f} |
""")

                        with col_right:
                            st.subheader("🏢 Fundamental Breakdown")
                            st.markdown(f"""
| Metric | Score / Value |
|---|---|
| **Overall Fundamental** | {result.fundamental_score}/100 |
| **Valuation** | {result.valuation_score}/100 |
| **Profitability** | {result.profitability_score}/100 |
| **Growth** | {result.growth_score}/100 |
| **Financial Health** | {result.health_score}/100 |
| **P/E Ratio** | {result.pe_ratio:.1f}x |
| **ROE** | {result.roe * 100:.1f}% |
| **Revenue Growth** | {result.revenue_growth:.1f}% |
| **Debt / Equity** | {result.debt_to_equity:.2f}x |
""")

                        st.divider()
                        st.caption(f"Combined Signal: **{result.combined_signal}**")
                    else:
                        st.error("No result returned — check symbol or data availability.")
                except Exception as e:
                    st.error(f"Error: {e}")

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: EARNINGS CALENDAR
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "📅 Earnings Calendar":
    st.title("📅 Earnings Calendar")
    _help(
        "Shows upcoming earnings announcements — **never hold positions through earnings** (gap risk can exceed your stop).\n"
        "- Set *Days ahead* to 7 to catch all near-term risk events\n"
        "- Check this before entering any new trade — if earnings are within 5 days, wait until after\n"
        "- Cross-reference with the Signals page: avoid setups where earnings fall before your target is hit"
    )

    if not HAS_EARN:
        st.error("earnings_calendar module not available.")
    else:
        days_ahead = st.slider("Days ahead", 3, 30, 14)
        if st.button("Load Earnings"):
            with st.spinner("Fetching…"):
                try:
                    ec = C["earn"]
                    df = ec.get_upcoming_earnings(days=days_ahead) if hasattr(ec, "get_upcoming_earnings") else (
                         ec.get_calendar() if hasattr(ec, "get_calendar") else pd.DataFrame())
                    if isinstance(df, pd.DataFrame) and not df.empty:
                        st.dataframe(df, use_container_width=True, hide_index=True)
                    else:
                        st.info("No earnings data returned.")
                except Exception as e:
                    st.error(f"Error: {e}")

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: INSIDER ACTIVITY
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "👔 Insider Activity":
    st.title("👔 Insider Activity")
    _help(
        "Tracks SEC Form 4 insider transactions — executives buying or selling their own company's stock.\n"
        "- Enter comma-separated symbols and click **Scan**\n"
        "- **Large insider BUYs** = bullish confirmation; executives buy with conviction when they see value\n"
        "- Insider SELLs are less meaningful (often planned diversification, not a bearish view)\n"
        "- Use as a secondary confirmation signal, not a primary buy trigger"
    )

    if not HAS_INSIDER:
        st.error("insider_tracker module not available.")
    else:
        syms_raw = st.text_area("Symbols (comma-sep)", "NVDA,AAPL,MSFT,META")
        if st.button("Scan"):
            syms = [s.strip().upper() for s in syms_raw.split(",") if s.strip()]
            with st.spinner("Fetching insider transactions…"):
                try:
                    it = C["insider"]
                    df = it.get_insider_activity(syms) if hasattr(it, "get_insider_activity") else (
                         it.scan(syms) if hasattr(it, "scan") else pd.DataFrame())
                    if isinstance(df, pd.DataFrame) and not df.empty:
                        st.dataframe(df, use_container_width=True, hide_index=True)
                    else:
                        st.info("No insider activity found.")
                except Exception as e:
                    st.error(f"Error: {e}")

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: STOCK SCREENER — uses full global universe, not config.STOCK_UNIVERSE[:15]
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "🔍 Stock Screener":
    st.title("🔍 Stock Screener")
    _help(
        "Filters the full universe by signal score threshold and market.\n"
        "- Select markets and set **Max stocks per market** to control scan size\n"
        "- **Minimum score 60** = actionable setups; **80+** = high-conviction only\n"
        "- Click **Run Screener** — results are a shortlist for deeper analysis via Combined Analysis\n"
        "- This is a filter tool, not a buy list — always verify with Market Regime before trading"
    )

    sc1, sc2 = st.columns(2)
    scr_markets = sc1.multiselect("Markets", ["US","DE","IN"], default=["US"], key="scr_mkts")
    max_per_mkt = sc2.slider("Max stocks per market", 10, 100, 50, 10)
    min_score   = st.slider("Minimum signal score", 0, 100, 60)

    if st.button("Run Screener"):
        with st.spinner("Screening…"):
            try:
                # Build symbol list from the global market_config universe (not the small US-only list)
                if HAS_MC:
                    from market_config import get_all_stocks
                    universe = get_all_stocks(scr_markets)
                    syms = []
                    for mkt in scr_markets:
                        syms.extend(universe.get(mkt, [])[:max_per_mkt])
                else:
                    syms = config.STOCK_UNIVERSE  # fallback — no slice

                if HAS_SS:
                    results = C["screener"].screen_stocks(syms) if hasattr(C["screener"], "screen_stocks") else pd.DataFrame()
                    if isinstance(results, pd.DataFrame) and not results.empty:
                        score_col = "signal_score" if "signal_score" in results.columns else ("score" if "score" in results.columns else None)
                        filtered = results[results[score_col] >= min_score] if score_col else results
                        st.success(f"{len(filtered)} stocks passed (from {len(syms)} scanned)")
                        st.dataframe(filtered, use_container_width=True, hide_index=True)
                    else:
                        st.info("Screener returned no results.")
                else:
                    st.warning("StockScreener not available. Universe list:")
                    st.write(syms)
            except Exception as e:
                st.error(f"Screener error: {e}")

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: TRADE JOURNAL — full lifecycle: log entry, close, view history
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "📋 Trade Journal":
    st.title("📋 Trade Journal")
    _help(
        "Full trade lifecycle management: log entries, track open trades, and record exits.\n"
        "- **Log Entry tab** — record every new trade with entry price, stop, target, and setup type\n"
        "- **Open Trades tab** — view and update in-progress positions; close them here when done\n"
        "- **Closed Trades tab** — full history with P&L and R-multiples\n"
        "- All data is stored locally in `data/trade_journal.json`"
    )

    if not HAS_JOURNAL:
        st.error("trade_journal module not available.")
    else:
        journal = C["journal"]
        tab_log, tab_open, tab_closed = st.tabs(["➕ Log Entry", "📂 Open Trades", "✅ Closed Trades"])

        # ── Log a new trade entry ────────────────────────────────────────────
        with tab_log:
            st.subheader("Log a New Trade Entry")
            l1, l2, l3 = st.columns(3)
            j_sym    = l1.text_input("Symbol", "NVDA").upper()
            j_mkt    = l2.selectbox("Market", ["US","DE","IN"])
            j_setup  = l3.selectbox("Setup", ["PULLBACK","BREAKOUT","MOMENTUM","REVERSAL"])

            l4, l5, l6 = st.columns(3)
            j_entry  = l4.number_input("Entry Price", value=100.0,  step=0.5, format="%.2f")
            j_stop   = l5.number_input("Stop Loss",   value=95.0,   step=0.5, format="%.2f")
            j_shares = l6.number_input("Shares",      value=10,     step=1,   min_value=1)

            l7, l8, l9 = st.columns(3)
            j_t1     = l7.number_input("Target 1",    value=110.0,  step=0.5, format="%.2f")
            j_t2     = l8.number_input("Target 2",    value=120.0,  step=0.5, format="%.2f")
            j_regime = l9.selectbox("Regime",         ["BULL","BEAR","SIDEWAYS","VOLATILE"])

            j_score  = st.slider("Signal Score", 0, 100, 65)
            j_reason = st.text_area("Entry Reason / Notes", height=80)

            if st.button("✅ Log Trade Entry", type="primary"):
                try:
                    tid = journal.log_entry(
                        symbol=j_sym, entry_price=j_entry, shares=j_shares,
                        stop_loss=j_stop, target_1=j_t1, target_2=j_t2,
                        setup_type=j_setup, signal_score=j_score,
                        entry_reason=j_reason, market=j_mkt,
                        market_regime=j_regime,
                    )
                    st.success(f"✅ Trade #{tid} logged — {j_sym} × {j_shares} shares @ ${j_entry}")
                except Exception as e:
                    st.error(f"Error logging trade: {e}")

        # ── Open positions ───────────────────────────────────────────────────
        with tab_open:
            st.subheader("Open Positions")
            try:
                open_df = journal.get_open_trades()
                if open_df.empty:
                    st.info("No open trades. Log one in the 'Log Entry' tab.")
                else:
                    st.dataframe(open_df, use_container_width=True, hide_index=True)

                    st.markdown("---")
                    st.subheader("Close a Position")
                    default_id = int(open_df["id"].iloc[0]) if "id" in open_df.columns else 1
                    close_id     = st.number_input("Trade ID", min_value=1, step=1, value=default_id)
                    cx1, cx2     = st.columns(2)
                    close_price  = cx1.number_input("Exit Price ($)", value=100.0, step=0.5, format="%.2f")
                    close_reason = cx2.selectbox("Exit Reason", ["TARGET_1","TARGET_2","STOP_LOSS","TIME_EXIT","MANUAL"])
                    cm1, cm2     = st.columns(2)
                    close_mae    = cm1.number_input("MAE % (max adverse, negative e.g. -3.2)", value=0.0, step=0.1, format="%.2f")
                    close_mfe    = cm2.number_input("MFE % (max favourable, positive e.g. 7.5)", value=0.0, step=0.1, format="%.2f")
                    close_notes  = st.text_area("Lessons / Mistakes", height=60)

                    if st.button("❌ Close Trade", type="primary"):
                        try:
                            result = journal.log_exit(
                                trade_id=int(close_id),
                                exit_price=close_price,
                                exit_reason=close_reason,
                                mae=close_mae if close_mae != 0 else None,
                                mfe=close_mfe if close_mfe != 0 else None,
                                lessons=close_notes,
                            )
                            pnl = result.get("pnl", 0)
                            emoji = "✅" if pnl >= 0 else "❌"
                            st.success(f"{emoji} Trade #{close_id} closed — P&L: ${pnl:+,.2f} ({result.get('r_multiple',0):+.2f}R)")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error closing trade: {e}")
            except Exception as e:
                st.error(f"Error loading open trades: {e}")

        # ── Closed trades history ────────────────────────────────────────────
        with tab_closed:
            st.subheader("Closed Trades History")
            try:
                closed_df = journal.get_closed_trades()
                if closed_df.empty:
                    st.info("No closed trades yet.")
                else:
                    wins      = (closed_df["pnl"] > 0).sum() if "pnl" in closed_df.columns else 0
                    total     = len(closed_df)
                    total_pnl = closed_df["pnl"].sum() if "pnl" in closed_df.columns else 0
                    avg_r     = closed_df["r_multiple"].mean() if "r_multiple" in closed_df.columns else 0

                    qs1, qs2, qs3, qs4 = st.columns(4)
                    qs1.metric("Total Trades", total)
                    qs2.metric("Win Rate",     f"{wins/total*100:.1f}%" if total else "N/A")
                    qs3.metric("Total P&L",    f"${total_pnl:+,.2f}")
                    qs4.metric("Avg R",        f"{avg_r:+.2f}R")

                    st.dataframe(closed_df, use_container_width=True, hide_index=True)
            except Exception as e:
                st.error(f"Error loading closed trades: {e}")

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: PERFORMANCE
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "📊 Performance":
    st.title("📊 Performance Tracker")
    _help(
        "Monthly P&L summary across all closed trades in your journal.\n"
        "- **Month P&L** — running total for the current calendar month\n"
        "- **Target** — monthly dollar target set in `config.py` (`MONTHLY_TARGET`)\n"
        "- Use the **Days slider** to change the lookback window\n"
        "- Win rate below 45% or Profit Factor below 1.3 = review your strategy or reduce position sizes"
    )

    if HAS_PT:
        try:
            progress = C["pt"].get_monthly_progress()
            p1, p2, p3, p4 = st.columns(4)
            p1.metric("Month P&L",  f"${progress.get('current_pnl',0):+,.2f}")
            p2.metric("Target",     f"${progress.get('target',0):,.2f}")
            p3.metric("Progress",   f"{progress.get('progress_pct',0):.1f}%")
            p4.metric("Days Left",  progress.get('days_left','?'))
        except Exception as e:
            st.warning(f"Performance tracker: {e}")

    if HAS_JOURNAL:
        st.markdown("---")
        st.subheader("Trade Statistics")
        days_filter = st.slider("Days to include", 7, 365, 30)
        try:
            stats = C["journal"].get_stats(days=days_filter)
            if not stats.get("total_trades"):
                st.info(f"No closed trades in the last {days_filter} days.")
            else:
                s1, s2, s3, s4, s5 = st.columns(5)
                s1.metric("Trades",        stats["total_trades"])
                s2.metric("Win Rate",      f"{stats['win_rate']:.1f}%")
                s3.metric("Profit Factor", f"{stats['profit_factor']:.2f}")
                s4.metric("Total P&L",     f"${stats['total_pnl']:+,.2f}")
                s5.metric("Avg R",         f"{stats['avg_r']:+.2f}R")
        except Exception as e:
            st.error(f"Stats error: {e}")

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: PORTFOLIO
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "💼 Portfolio":
    st.title("💼 Portfolio Overview")
    _help(
        "Shows currently open positions pulled from the Trade Journal.\n"
        "- **Invested** — total capital currently deployed across all open positions\n"
        "- **Cash** — remaining available capital (`account − invested`)\n"
        "- The position table shows unrealised P&L and days held for each trade\n"
        "- No single position should exceed 25% of account (enforced by Position Calculator)"
    )

    if HAS_PM:
        try:
            summary = C["pm"].get_summary()
            p1, p2, p3, p4 = st.columns(4)
            p1.metric("Account",        f"${summary['account']:,}")
            p2.metric("Open Positions", summary['open_positions'])
            p3.metric("Invested",       f"${summary['invested']:,.2f}")
            p4.metric("Cash",           f"${summary['cash']:,.2f}")
        except Exception as e:
            st.error(f"Portfolio error: {e}")

    if HAS_JOURNAL:
        st.markdown("---")
        st.subheader("Open Positions (from Journal)")
        try:
            open_df = C["journal"].get_open_trades()
            if open_df.empty:
                st.info("No open positions in journal.")
            else:
                st.dataframe(open_df, use_container_width=True, hide_index=True)
        except Exception as e:
            st.error(f"Error: {e}")

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: POSITION CALCULATOR
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "📐 Position Calculator":
    st.title("📐 Position Size Calculator")
    _help(
        "Calculates exactly how many shares to buy given your risk parameters — **always use this before placing an order**.\n"
        "- **Fixed Risk** — enter entry price and stop-loss; finds max shares that risk exactly `risk %` of account\n"
        "- **ATR-Based** — uses the stock's 14-period Average True Range as the stop unit (adapts to volatility)\n"
        "- Position is capped at 25% of account to prevent over-concentration in any single stock\n"
        "- You can override account size and risk % here without changing `config.py`"
    )

    method = st.radio("Sizing Method", ["Fixed Risk", "ATR-Based (volatility-adjusted)"], horizontal=True)
    st.markdown("---")

    pc1, pc2 = st.columns(2)
    entry_p  = pc1.number_input("Entry Price ($)",  value=100.0, step=0.5, format="%.2f")
    account  = pc2.number_input("Account Size ($)", value=float(config.ACCOUNT_SIZE), step=1000.0)
    risk_pct = pc1.slider("Risk per trade (%)", 0.5, 3.0, float(config.RISK_PER_TRADE * 100), 0.1)

    if method == "Fixed Risk":
        stop_p = pc2.number_input("Stop Loss ($)", value=round(entry_p * 0.95, 2), step=0.5, format="%.2f")
        if st.button("Calculate", type="primary"):
            rps = entry_p - stop_p
            if rps <= 0:
                st.error("Stop loss must be below entry.")
            else:
                max_risk = account * (risk_pct / 100)
                shares = int(max_risk / rps)
                # Cap at 25% of account
                if shares * entry_p > account * 0.25:
                    shares = int(account * 0.25 / entry_p)
                value = shares * entry_p
                a, b, c, d = st.columns(4)
                a.metric("Shares",         shares)
                b.metric("Position Value", f"${value:,.2f}")
                c.metric("$ at Risk",      f"${shares * rps:,.2f}")
                d.metric("% of Account",   f"{value/account*100:.1f}%")

    else:  # ATR-Based
        atr_val  = pc2.number_input("ATR (14-period $)", value=3.0, step=0.1, format="%.2f")
        atr_mult = pc1.number_input("ATR Multiplier",    value=2.0, step=0.5, format="%.1f")
        if st.button("Calculate ATR Size", type="primary"):
            atr_stop = atr_val * atr_mult
            if atr_stop <= 0:
                st.error("Invalid ATR value.")
            else:
                max_risk = account * (risk_pct / 100)
                shares   = int(max_risk / atr_stop)
                if shares * entry_p > account * 0.25:
                    shares = int(account * 0.25 / entry_p)
                value = shares * entry_p
                a, b, c, d = st.columns(4)
                a.metric("Shares",         shares)
                b.metric("Position Value", f"${value:,.2f}")
                c.metric("Implied Stop",   f"${entry_p - atr_stop:.2f}")
                d.metric("ATR Stop Dist.", f"${atr_stop:.2f}")

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: SIGNAL ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "🔬 Signal Analysis":
    st.title("🔬 Signal Analysis — Score Distribution")
    _help(
        "Charts the distribution of signal scores across the full universe to gauge market breadth.\n"
        "- Select markets and click **Analyse Signals** to generate score histograms\n"
        "- **Most scores clustered below 50** = weak broad market; reduce position sizes or stay out\n"
        "- **Cluster above 65** = strong breadth; more aggressive entries are justified\n"
        "- Use this weekly to calibrate your minimum score threshold on the Signals page"
    )

    if not HAS_GSG:
        st.error("GlobalSignalGenerator not available.")
    else:
        sa_markets = st.multiselect("Markets", ["US","DE","IN"], default=["US"], key="sa_mkts")
        if st.button("Analyse Signals"):
            with st.spinner("Generating signals…"):
                try:
                    import plotly.express as px
                    raw = C["gen"].generate_signals(markets=sa_markets)
                    all_sigs = [s for mkt_sigs in raw.values() for s in mkt_sigs]
                    if all_sigs:
                        df = pd.DataFrame(all_sigs)
                        fig = px.histogram(df, x="signal_score", color="signal_status", nbins=20,
                                           title="Signal Score Distribution",
                                           color_discrete_map={"STRONG BUY":"green","BUY":"lime",
                                                               "WATCH":"orange","AVOID":"red"})
                        st.plotly_chart(fig, use_container_width=True)
                        if "sector" in df.columns:
                            fig2 = px.bar(
                                df.groupby("sector")["signal_score"].mean().reset_index().sort_values("signal_score",ascending=False),
                                x="sector", y="signal_score", title="Avg Score by Sector")
                            st.plotly_chart(fig2, use_container_width=True)
                    else:
                        st.info("No signals generated.")
                except Exception as e:
                    st.error(f"Error: {e}")

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: SECTOR ROTATION
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "🔄 Sector Rotation":
    st.title("🔄 Sector Rotation — US Sector ETF Rankings")
    st.caption("Relative strength vs SPY across 1W / 1Mo / 3Mo periods")
    _help(
        "Ranks US sector ETFs (XLK, XLF, XLE, XLV, etc.) by relative momentum vs SPY.\n"
        "- **Top 3 sectors** = rotate capital toward these; **Bottom 3** = underweight or avoid entirely\n"
        "- **Composite score** = weighted average of 1W, 1-month, and 3-month excess returns vs SPY\n"
        "- **From 52wk Hi %** — sectors near highs have momentum; sectors far from highs = weakness\n"
        "- Recheck every Sunday and align your long bias with the leading sectors before the new week"
    )

    if not HAS_SR:
        st.error("sector_rotation module not available.")
    else:
        if st.button("🔄 Refresh", type="primary"):
            st.cache_data.clear()

        @st.cache_data(ttl=900, show_spinner="Fetching sector data…")
        def _sector_rankings():
            return _sr.SectorRotation().compute_rankings()

        try:
            df_s = _sector_rankings()
            if df_s.empty:
                st.warning("No sector data.")
            else:
                top = df_s.iloc[0]; bot = df_s.iloc[-1]
                leading_n = len(df_s[df_s["composite_score"] >= 0])
                m1, m2, m3 = st.columns(3)
                m1.metric("🏆 Leading",    top["sector"], f"{top['composite_score']:+.2f}% vs SPY")
                m2.metric("⚠️ Lagging",    bot["sector"], f"{bot['composite_score']:+.2f}% vs SPY")
                m3.metric("Outperforming", f"{leading_n} / {len(df_s)}")

                st.markdown("---")
                disp_cols = ["rank","etf","sector","signal"] + [
                    c for c in ["rel_1w","rel_1mo","rel_3mo","composite_score","pct_from_52wk_hi"] if c in df_s.columns]
                st.dataframe(df_s[disp_cols].rename(columns={
                    "rel_1w":"1W vs SPY %","rel_1mo":"1Mo vs SPY %","rel_3mo":"3Mo vs SPY %",
                    "composite_score":"Score","pct_from_52wk_hi":"From 52wk Hi %",
                }), use_container_width=True, hide_index=True)

                import plotly.express as px
                fig = px.bar(df_s.sort_values("composite_score"),
                             x="composite_score", y="sector", orientation="h",
                             color="composite_score", color_continuous_scale=["#EF553B","gray","#00CC96"],
                             title="Sector Relative Strength vs SPY",
                             labels={"composite_score": "Score (excess return %)", "sector": ""})
                fig.add_vline(x=0, line_dash="dash", line_color="white", opacity=0.5)
                fig.update_layout(showlegend=False, height=420, coloraxis_showscale=False)
                st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Sector rotation error: {e}")

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: BACKTEST PRO
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "🧪 Backtest Pro":
    st.title("🧪 Backtest Pro")
    st.caption("Walk-forward validation + Monte Carlo simulation")
    _help(
        "Tests your signal strategy on historical price data.\n"
        "- **Symbols** — paste the stocks you want to test (comma-separated)\n"
        "- **Walk-Forward** — divides history into N windows and tests out-of-sample; more realistic than a simple backtest\n"
        "- **Monte Carlo** — runs thousands of random permutations to show the distribution of possible outcomes\n"
        "- A strategy is only viable if Walk-Forward CAGR > 0 **and** Monte Carlo 5th-percentile is still positive"
    )

    if not HAS_BT:
        st.error("backtester module not available.")
    else:
        with st.expander("⚙️ Settings", expanded=True):
            bs1, bs2, bs3 = st.columns(3)
            bt_syms_raw = bs1.text_area("Symbols (comma-sep)", "NVDA,AAPL,MSFT,GOOGL,META", height=80)
            bt_period   = bs2.selectbox("History", ["6mo","1y","2y"], index=1)
            bt_wf_n     = bs3.slider("Walk-forward windows",  2, 6,    4)
            bt_mc_n     = bs3.slider("Monte Carlo sims",    200, 2000, 1000, 200)

        bt_symbols = [s.strip().upper() for s in bt_syms_raw.split(",") if s.strip()]
        col_bt, col_wf, col_mc = st.columns(3)
        run_bt = col_bt.button("▶ Run Backtest", type="primary")
        run_wf = col_wf.button("🔀 Walk-Forward")
        run_mc = col_mc.button("🎲 Monte Carlo")

        bt = C["bt"]

        if run_bt or run_mc:
            with st.spinner("Running backtest…"):
                try:
                    results = bt.run_backtest(bt_symbols, period=bt_period) if hasattr(bt, "run_backtest") else bt.run(bt_symbols, period=bt_period)
                    m1,m2,m3,m4,m5,m6 = st.columns(6)
                    m1.metric("Trades",       getattr(results,"total_trades","-"))
                    m2.metric("Win Rate",     f"{getattr(results,'win_rate',0):.1f}%")
                    m3.metric("Prof.Factor",  f"{getattr(results,'profit_factor',0):.2f}")
                    m4.metric("Max DD",       f"{getattr(results,'max_drawdown',0):.1f}%")
                    m5.metric("Total P&L",    f"${getattr(results,'total_pnl',0):,.0f}")
                    m6.metric("Return",       f"{getattr(results,'total_return',0):.1f}%")

                    if hasattr(results,"equity_curve") and results.equity_curve:
                        import plotly.graph_objects as go
                        fig_eq = go.Figure(go.Scatter(y=results.equity_curve, mode="lines",
                                                       line=dict(color="cyan", width=2)))
                        fig_eq.update_layout(title="Equity Curve", xaxis_title="Trade #",
                                              yaxis_title="Portfolio ($)", height=300, template="plotly_dark")
                        st.plotly_chart(fig_eq, use_container_width=True)

                    if run_mc and hasattr(bt, "monte_carlo"):
                        with st.spinner("Monte Carlo…"):
                            try:
                                mc = bt.monte_carlo(results, simulations=bt_mc_n)
                                mc1,mc2,mc3,mc4 = st.columns(4)
                                mc1.metric("Median Return",   f"{mc.median_return:.1f}%")
                                mc2.metric("P10 / P90",       f"{mc.p10_return:.1f}% / {mc.p90_return:.1f}%")
                                mc3.metric("Prob Profit",     f"{mc.probability_of_profit:.1f}%")
                                mc4.metric("Prob Ruin >25%",  f"{mc.probability_ruin:.1f}%")
                            except Exception as mc_err:
                                st.error(f"Monte Carlo error: {mc_err}")
                except Exception as bt_err:
                    st.error(f"Backtest error: {bt_err}")

        if run_wf and not run_bt:
            if not hasattr(bt, "walk_forward"):
                st.warning("walk_forward() not available on this backtester version.")
            else:
                with st.spinner("Walk-forward analysis…"):
                    try:
                        wf_res = bt.walk_forward(bt_symbols, total_period=bt_period, n_windows=bt_wf_n)
                        if wf_res:
                            wf_df = pd.DataFrame([{
                                "Window":   r.window,
                                "Train":    f"{r.train_start} → {r.train_end}",
                                "Test":     f"{r.test_start} → {r.test_end}",
                                "Train WR": f"{r.train_win_rate:.1f}%",
                                "Test WR":  f"{r.test_win_rate:.1f}%",
                                "Test P&L": f"${r.test_pnl:,.0f}",
                                "Trades":   r.test_trades,
                                "Sharpe":   f"{r.sharpe:.2f}",
                            } for r in wf_res])
                            st.dataframe(wf_df, use_container_width=True, hide_index=True)

                            import plotly.express as px
                            fig_wf = px.line([{"Window":r.window,"Train WR%":r.train_win_rate,"Test WR%":r.test_win_rate} for r in wf_res],
                                             x="Window", y=["Train WR%","Test WR%"],
                                             title="Walk-Forward: Train vs Test Win Rate", markers=True)
                            st.plotly_chart(fig_wf, use_container_width=True)
                        else:
                            st.warning("No walk-forward results returned.")
                    except Exception as wf_err:
                        st.error(f"Walk-forward error: {wf_err}")

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: JOURNAL ANALYTICS
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "📓 Journal Analytics":
    st.title("📓 Journal Analytics")
    st.caption("MAE/MFE distribution, regime & setup performance breakdowns")
    _help(
        "Deep statistical analysis of your closed trade history (requires 30+ closed trades for meaningful results).\n"
        "- **MAE/MFE** — Max Adverse Excursion (how far trades moved against you) vs Max Favourable Excursion (best point reached). Large MAE with small MFE = stops are too tight\n"
        "- **By Regime** — shows which market conditions (BULL/BEAR/SIDEWAYS) you perform best in\n"
        "- **By Setup** — shows your strongest and weakest trade setups (PULLBACK, BREAKOUT, etc.)\n"
        "- Log and close trades via Trade Journal first — this page analyses that historical data"
    )

    if not HAS_JOURNAL:
        st.error("trade_journal module not available.")
    else:
        try:
            journal  = C["journal"]
            closed_df = journal.get_closed_trades()

            if closed_df.empty:
                st.info("No closed trades yet. Close trades in the Trade Journal page first.")
            else:
                tab_mf, tab_reg, tab_setup = st.tabs(["📐 MAE / MFE", "🌐 By Regime", "🎯 By Setup"])

                with tab_mf:
                    if "mae" in closed_df.columns and closed_df["mae"].notna().any():
                        import plotly.express as px
                        cm1, cm2 = st.columns(2)
                        with cm1:
                            st.plotly_chart(px.histogram(closed_df.dropna(subset=["mae"]), x="mae",
                                title="MAE Distribution (%)", nbins=20, color_discrete_sequence=["#EF553B"]),
                                use_container_width=True)
                        with cm2:
                            st.plotly_chart(px.histogram(closed_df.dropna(subset=["mfe"]), x="mfe",
                                title="MFE Distribution (%)", nbins=20, color_discrete_sequence=["#00CC96"]),
                                use_container_width=True)
                        jm1, jm2 = st.columns(2)
                        jm1.metric("Avg MAE", f"{closed_df['mae'].mean():.2f}%")
                        jm2.metric("Avg MFE", f"{closed_df['mfe'].mean():.2f}%")
                    else:
                        st.info("No MAE/MFE data yet. Enter them when closing trades.")

                with tab_reg:
                    try:
                        reg_df = journal.get_performance_by_regime()
                        if reg_df.empty:
                            st.info("Not enough data with regime labels.")
                        else:
                            st.dataframe(reg_df, use_container_width=True, hide_index=True)
                            import plotly.express as px
                            st.plotly_chart(px.bar(reg_df, x="market_regime", y="total_pnl",
                                color="win_rate", color_continuous_scale="RdYlGn",
                                title="P&L by Market Regime"), use_container_width=True)
                    except Exception as e:
                        st.error(f"Regime error: {e}")

                with tab_setup:
                    try:
                        setup_df = journal.get_performance_by_setup()
                        if setup_df.empty:
                            st.info("Not enough data with setup labels.")
                        else:
                            st.dataframe(setup_df, use_container_width=True, hide_index=True)
                            import plotly.express as px
                            st.plotly_chart(px.bar(setup_df, x="setup_type", y="total_pnl",
                                color="win_rate", color_continuous_scale="RdYlGn",
                                title="P&L by Setup Type"), use_container_width=True)
                    except Exception as e:
                        st.error(f"Setup error: {e}")

        except Exception as e:
            st.error(f"Journal analytics error: {e}")

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: WEEKEND INVESTING (MI MOMENTUM STRATEGIES)
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "🏆 Weekend Investing (MI)":
    st.title("🏆 Weekend Investing — Alok Jain Momentum Strategies")
    st.markdown(
        '<p style="color:#475569;font-size:.85rem;margin-top:-.8rem;margin-bottom:1rem;">'
        'Rule-based rotational momentum strategies inspired by '
        '<a href="https://weekendinvesting.com" target="_blank" '
        'style="color:#00b4d8;text-decoration:none;">weekendinvesting.com</a>. '
        'Ranks stocks by composite momentum score and rebalances weekly or monthly.</p>',
        unsafe_allow_html=True,
    )
    _help(
        "**How to run a rebalance:**\n"
        "1. Select a strategy (e.g. *Mi-35* for small-cap momentum, *Mi-Top10* for large-cap safe)\n"
        "2. Enter your total capital allocated to this strategy\n"
        "3. Enter current holdings (comma-separated symbols) so the system knows what you already hold\n"
        "4. Click **Generate Rebalance Signal** — the system scores the entire universe with a progress bar\n"
        "5. Execute ✅ BUY and ❌ SELL signals at Monday market open (9:15 AM IST) — equal weight per slot\n\n"
        "**Key rules:** Never override a SELL signal. Never size up on conviction. "
        "When the system shows 🟡 CASH, park that slot in LIQUIDBEES or a liquid fund."
    )

    if not HAS_WI:
        st.error("weekend_investing_strategy module not available.")
    else:
        from weekend_investing_strategy import (
            WeekendInvestingStrategy, STRATEGY_PRESETS, CASH_PROXY
        )

        # ── Strategy selector ────────────────────────────────────────────────
        wi_col1, wi_col2, wi_col3 = st.columns([2, 1, 1])
        wi_strategy = wi_col1.selectbox(
            "Strategy",
            list(STRATEGY_PRESETS.keys()),
            format_func=lambda k: f"{k}  —  {STRATEGY_PRESETS[k]['label']}",
            index=list(STRATEGY_PRESETS.keys()).index("Mi-35"),
        )
        wi_capital = wi_col2.number_input(
            "Capital (₹)", min_value=10_000, max_value=100_000_000,
            value=500_000, step=50_000,
        )
        wi_holdings_raw = wi_col3.text_area(
            "Current Holdings (comma-sep)", height=68,
            help="Symbols you already hold — used to compute BUY/HOLD/SELL actions",
        )
        wi_holdings = [s.strip().upper() for s in wi_holdings_raw.split(",") if s.strip()]

        # Description card
        cfg = STRATEGY_PRESETS[wi_strategy]
        col_desc1, col_desc2, col_desc3, col_desc4 = st.columns(4)
        col_desc1.markdown(
            f'<div style="background:rgba(0,180,216,.06);border:1px solid rgba(0,180,216,.15);'
            f'border-radius:10px;padding:.6rem .9rem;">'
            f'<div style="font-size:.65rem;color:#4b5e7a;font-weight:700;text-transform:uppercase;letter-spacing:.08em;">Universe</div>'
            f'<div style="font-size:.95rem;color:#e2e8f0;font-weight:600;margin-top:.15rem;">'
            f'{len(cfg["universe"])} stocks</div></div>', unsafe_allow_html=True)
        col_desc2.markdown(
            f'<div style="background:rgba(0,180,216,.06);border:1px solid rgba(0,180,216,.15);'
            f'border-radius:10px;padding:.6rem .9rem;">'
            f'<div style="font-size:.65rem;color:#4b5e7a;font-weight:700;text-transform:uppercase;letter-spacing:.08em;">Portfolio Size</div>'
            f'<div style="font-size:.95rem;color:#e2e8f0;font-weight:600;margin-top:.15rem;">'
            f'Top {cfg["top_n"]} stocks</div></div>', unsafe_allow_html=True)
        col_desc3.markdown(
            f'<div style="background:rgba(0,180,216,.06);border:1px solid rgba(0,180,216,.15);'
            f'border-radius:10px;padding:.6rem .9rem;">'
            f'<div style="font-size:.65rem;color:#4b5e7a;font-weight:700;text-transform:uppercase;letter-spacing:.08em;">Rebalance</div>'
            f'<div style="font-size:.95rem;color:#e2e8f0;font-weight:600;margin-top:.15rem;">'
            f'{cfg["rebalance"].title()}</div></div>', unsafe_allow_html=True)
        col_desc4.markdown(
            f'<div style="background:rgba(0,180,216,.06);border:1px solid rgba(0,180,216,.15);'
            f'border-radius:10px;padding:.6rem .9rem;">'
            f'<div style="font-size:.65rem;color:#4b5e7a;font-weight:700;text-transform:uppercase;letter-spacing:.08em;">Abs. Momentum</div>'
            f'<div style="font-size:.95rem;color:#e2e8f0;font-weight:600;margin-top:.15rem;">'
            f'{"✅ Cash filter" if cfg["absolute_momentum"] else "❌ Always invested"}</div></div>',
            unsafe_allow_html=True)
        st.caption(cfg["description"])

        st.divider()

        tab_rebal, tab_rank, tab_bt, tab_guide = st.tabs(
            ["📋 Rebalance Now", "📊 Full Universe Ranking", "📈 Backtest", "📖 Strategy Guide"]
        )

        # ── TAB 1 : REBALANCE ───────────────────────────────────────────────
        with tab_rebal:
            if st.button("⚡ Generate Rebalance Signal", type="primary"):
                progress_bar  = st.progress(0, text="Scoring stocks…")
                progress_text = st.empty()

                def _progress_cb(cur, tot):
                    pct = int(cur / tot * 100)
                    progress_bar.progress(pct, text=f"Scoring {cur}/{tot} stocks…")
                    progress_text.caption(f"Processing universe ({cur}/{tot})")

                try:
                    engine = WeekendInvestingStrategy()
                    result = engine.run(
                        wi_strategy,
                        capital=wi_capital,
                        current_holdings=wi_holdings,
                        on_progress=_progress_cb,
                    )
                    progress_bar.empty()
                    progress_text.empty()

                    if not result.portfolio:
                        st.warning("No stocks scored — check your internet connection or try a smaller universe.")
                    else:
                        # ── Summary banner ───────────────────────────────────
                        st.markdown(f"""
<div style="background:linear-gradient(135deg,#0d1321,#111827);border:1px solid rgba(0,180,216,.2);
            border-radius:14px;padding:1rem 1.4rem;margin-bottom:1rem;">
  <div style="font-size:1.2rem;font-weight:800;color:#f1f5f9;">{result.strategy_label}</div>
  <div style="display:flex;gap:2rem;margin-top:.6rem;flex-wrap:wrap;">
    <span style="color:#64748b;font-size:.8rem;">📅 Rebalance Date: <b style="color:#e2e8f0;">{result.rebalance_date}</b></span>
    <span style="color:#64748b;font-size:.8rem;">⏰ Next Action: <b style="color:#00b4d8;">{result.next_action_date}</b></span>
    <span style="color:#64748b;font-size:.8rem;">🌐 Scored: <b style="color:#e2e8f0;">{result.scored_count}/{result.universe_size}</b></span>
    <span style="color:#64748b;font-size:.8rem;">💵 Cash: <b style="color:{"#fbb703" if result.cash_pct > 0 else "#00cc96"};">{result.cash_pct:.0f}%</b></span>
  </div>
</div>
""", unsafe_allow_html=True)

                        # ── BUY / SELL action cards ──────────────────────────
                        ac1, ac2 = st.columns(2)
                        with ac1:
                            if result.entries:
                                st.markdown(
                                    f'<div style="background:rgba(0,204,150,.08);border:1px solid rgba(0,204,150,.25);'
                                    f'border-radius:10px;padding:.75rem 1rem;">'
                                    f'<div style="color:#00cc96;font-weight:700;font-size:.9rem;">✅ BUY ({len(result.entries)} new)</div>'
                                    f'<div style="color:#94a3b8;font-size:.82rem;margin-top:.3rem;">'
                                    + " &nbsp;·&nbsp; ".join(result.entries) +
                                    '</div></div>', unsafe_allow_html=True)
                            else:
                                st.markdown(
                                    '<div style="background:rgba(0,204,150,.05);border:1px solid rgba(0,204,150,.1);'
                                    'border-radius:10px;padding:.75rem 1rem;color:#4b5e7a;">✅ No new buys</div>',
                                    unsafe_allow_html=True)
                        with ac2:
                            if result.exits:
                                st.markdown(
                                    f'<div style="background:rgba(239,83,80,.08);border:1px solid rgba(239,83,80,.25);'
                                    f'border-radius:10px;padding:.75rem 1rem;">'
                                    f'<div style="color:#ef5350;font-weight:700;font-size:.9rem;">❌ SELL ({len(result.exits)} exits)</div>'
                                    f'<div style="color:#94a3b8;font-size:.82rem;margin-top:.3rem;">'
                                    + " &nbsp;·&nbsp; ".join(result.exits) +
                                    '</div></div>', unsafe_allow_html=True)
                            else:
                                st.markdown(
                                    '<div style="background:rgba(239,83,80,.05);border:1px solid rgba(239,83,80,.1);'
                                    'border-radius:10px;padding:.75rem 1rem;color:#4b5e7a;">❌ No exits this rebalance</div>',
                                    unsafe_allow_html=True)

                        st.divider()

                        # ── Portfolio table ──────────────────────────────────
                        st.subheader(f"Portfolio — Top {cfg['top_n']} Holdings")
                        slot_alloc = wi_capital / cfg["top_n"]
                        rows = []
                        for slot in result.portfolio:
                            action_color = {
                                "BUY":  "🟢", "HOLD": "🔵",
                                "SELL": "🔴", "CASH": "🟡",
                            }.get(slot.action, "⚪")
                            rows.append({
                                "Rank":       slot.rank,
                                "Action":     f"{action_color} {slot.action}",
                                "Symbol":     slot.symbol,
                                "Name":       slot.name[:28],
                                "Score":      slot.momentum_score,
                                "6M %":       slot.momentum_6m,
                                "ATH %":      slot.pct_from_ath,
                                "Weight":     f"{slot.weight_pct:.1f}%",
                                "₹ Amount":   f"₹{slot.capital_amount:,.0f}",
                            })
                        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

                        if result.errors:
                            with st.expander(f"⚠️ {len(result.errors)} symbols could not be scored"):
                                st.caption(", ".join(result.errors))

                except Exception as e:
                    progress_bar.empty()
                    progress_text.empty()
                    st.error(f"Error: {e}")

        # ── TAB 2 : FULL UNIVERSE RANKING ────────────────────────────────────
        with tab_rank:
            st.subheader(f"Full Universe Ranking — {cfg['label']}")
            st.caption(f"All {len(cfg['universe'])} stocks scored and ranked. Top {cfg['top_n']} would be in portfolio.")
            if st.button("📊 Rank Full Universe", type="primary", key="rank_btn"):
                rank_progress = st.progress(0, text="Scoring universe…")

                def _rank_cb(cur, tot):
                    rank_progress.progress(int(cur / tot * 100), text=f"Scoring {cur}/{tot}…")

                try:
                    engine = WeekendInvestingStrategy()
                    rank_df = engine.rank_universe(wi_strategy, on_progress=_rank_cb)
                    rank_progress.empty()

                    if rank_df.empty:
                        st.warning("No data returned.")
                    else:
                        # Highlight top-N rows
                        top_n = cfg["top_n"]
                        st.success(f"✅ {len(rank_df)} stocks scored. Top {top_n} form the portfolio.")
                        st.dataframe(
                            rank_df.style.apply(
                                lambda r: ["background:rgba(0,204,150,.08)" if r["In Portfolio"] == "✅"
                                           else "" for _ in r],
                                axis=1,
                            ),
                            use_container_width=True, hide_index=True,
                        )
                except Exception as e:
                    rank_progress.empty()
                    st.error(f"Error: {e}")

        # ── TAB 3 : BACKTEST ─────────────────────────────────────────────────
        with tab_bt:
            st.subheader("Simple Historical Backtest")
            st.caption(
                "Simulates rebalancing at each period boundary using historical closes. "
                "No slippage, brokerage, or taxes included."
            )
            bt_years = st.slider("Lookback (years)", 1, 5, 3)
            bt_cap   = st.number_input("Starting Capital (₹)", value=500_000, step=50_000, key="bt_cap")

            if st.button("▶ Run Backtest", type="primary", key="wi_bt_btn"):
                with st.spinner(f"Backtesting {wi_strategy} over {bt_years} years…"):
                    try:
                        import plotly.graph_objects as go
                        import plotly.express as px

                        engine = WeekendInvestingStrategy(fetch_delay=0.1)
                        eq_df = engine.backtest(wi_strategy, lookback_years=bt_years, capital=bt_cap)

                        if eq_df.empty:
                            st.warning("Not enough historical data for this strategy/period.")
                        else:
                            # Metrics
                            start_val = eq_df["portfolio_value"].iloc[0]
                            end_val   = eq_df["portfolio_value"].iloc[-1]
                            total_ret = (end_val / start_val - 1) * 100
                            n_years   = (eq_df["date"].iloc[-1] - eq_df["date"].iloc[0]).days / 365.25
                            cagr      = ((end_val / start_val) ** (1 / max(n_years, 0.01)) - 1) * 100
                            peak      = eq_df["portfolio_value"].cummax()
                            drawdown  = ((eq_df["portfolio_value"] - peak) / peak * 100)
                            max_dd    = drawdown.min()

                            bm1, bm2, bm3, bm4 = st.columns(4)
                            bm1.metric("Total Return",  f"{total_ret:+.1f}%")
                            bm2.metric("CAGR",          f"{cagr:+.1f}%")
                            bm3.metric("Max Drawdown",  f"{max_dd:.1f}%")
                            bm4.metric("Rebalances",    len(eq_df))

                            st.divider()

                            fig = go.Figure()
                            fig.add_trace(go.Scatter(
                                x=eq_df["date"], y=eq_df["portfolio_value"],
                                mode="lines", name="Portfolio",
                                line=dict(color="#00b4d8", width=2),
                                fill="tozeroy", fillcolor="rgba(0,180,216,.06)",
                            ))
                            fig.update_layout(
                                title=f"{cfg['label']} — Equity Curve",
                                xaxis_title="Date", yaxis_title="Portfolio Value (₹)",
                                template="plotly_dark",
                                paper_bgcolor="#07090f", plot_bgcolor="#0d1321",
                                height=380,
                            )
                            st.plotly_chart(fig, use_container_width=True)

                            # Drawdown chart
                            fig_dd = go.Figure(go.Scatter(
                                x=eq_df["date"], y=drawdown,
                                mode="lines", fill="tozeroy",
                                line=dict(color="#ef5350", width=1.5),
                                fillcolor="rgba(239,83,80,.08)",
                            ))
                            fig_dd.update_layout(
                                title="Drawdown %",
                                template="plotly_dark",
                                paper_bgcolor="#07090f", plot_bgcolor="#0d1321",
                                height=220, yaxis_ticksuffix="%",
                            )
                            st.plotly_chart(fig_dd, use_container_width=True)

                    except Exception as e:
                        st.error(f"Backtest error: {e}")

        # ── TAB 4 : STRATEGY GUIDE ───────────────────────────────────────────
        with tab_guide:
            st.subheader("How Weekend Investing Momentum Works")
            st.markdown("""
**Inspired by [Alok Jain's Weekend Investing](https://weekendinvesting.com)** research on Indian market momentum strategies.

---

#### 📐 Momentum Score

Each stock is ranked by a **composite momentum score** — equal-weight average of returns over 4 windows:

| Window | Approx Trading Days |
|--------|-------------------|
| 1 Month | 21 |
| 3 Months | 63 |
| 6 Months | 126 |
| 12 Months | 252 |

Some strategies (Mi-EverGreen) also:
- Exclude the last 1 month to avoid short-term reversal (12-1 momentum)
- Divide by annualised volatility (risk-adjusted score)

---

#### ✅ Entry Rules

1. **When**: At the next market open after a rebalancing signal (Monday open for weekly; first trading day for monthly)
2. **What**: Buy all stocks in the new top-N list that you don't already hold
3. **How much**: Equal weight — `Capital ÷ N stocks` per position
4. **No price target** — simply buy at market open; momentum carries the trade

---

#### ❌ Exit Rules

1. **Relative exit**: Sell any stock that drops OUT of the top-N ranking at the next rebalancing — replace with the new entrant
2. **Absolute momentum (Mi-25/Mi-30 only)**: If a stock's **6-month return is negative**, skip it and park that slot in a liquid fund (LIQUIDBEES) — market timing filter
3. **No stop-loss during the holding period** — the rebalancing is the only exit mechanism

---

#### ⚖️ Position Sizing

```
Allocation per stock = Total Capital / N
```
Example (Mi-35, ₹5,00,000):
```
₹5,00,000 ÷ 35 = ₹14,285 per stock
```

---

#### 🔄 Strategy Comparison

| Strategy | Universe | Size | Rebalance | Abs Momentum | ATH Filter |
|----------|----------|------|-----------|-------------|------------|
| Mi-Top10 | Nifty 50 | 10 | Weekly | ❌ | ❌ |
| Mi-NNF10 | Nifty Next 50 | 10 | Weekly | ❌ | ❌ |
| Mi-EverGreen | CNX 200 | 20 | Weekly | ❌ | ❌ |
| Mi-20 | MidSmall 400 | 20 | Weekly | ❌ | ❌ |
| Mi-25 | Smallcap 250 | 25 | Monthly | ✅ | ❌ |
| Mi-30 | CNX 500 | 30 | Monthly | ✅ | ❌ |
| Mi-35 | Smallcap 250 | 35 | Weekly | ❌ | ❌ |
| Mi-ST-ATH | CNX 500 | 15 | Weekly | ❌ | ✅ (10%) |

---

#### ⚠️ Disclaimer

This is an educational implementation based on publicly available information.
It is **not** affiliated with or endorsed by Weekend Investing / Alok Jain.
Actual strategy parameters are proprietary. Always paper-trade first.
""")


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: SETTINGS
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "⚙️ Settings":
    st.title("⚙️ System Settings")
    _help(
        "Edit any value below and click **Save Changes** — the new values are written to `config.py` and take effect immediately on the next action.\n"
        "- **Account Size** and **Risk/Trade %** drive every position size calculation across all pages\n"
        "- **API keys** are read from environment variables (`.env` file) and cannot be changed here — edit `.env` then run `docker compose restart`\n"
        "- Changes persist across container restarts because `config.py` is part of the image; rebuild with `docker compose build` after major changes"
    )

    import os as _os_settings

    cfg_path = _os_settings.path.join(_os_settings.path.dirname(_os_settings.path.abspath(__file__)), "config.py")

    def _save_config(account, monthly_target, risk_per_trade, max_positions, daily_loss_limit,
                     min_market_cap, min_avg_volume, min_atr, max_atr,
                     stop_loss_atr, target1_atr, target2_atr, max_hold_days):
        """Rewrite numeric config values in-place using simple line-by-line replacement."""
        with open(cfg_path, "r") as f:
            lines = f.readlines()
        replacements = {
            "ACCOUNT_SIZE":          str(int(account)),
            "MONTHLY_TARGET":        f"{monthly_target/100:.4f}",
            "RISK_PER_TRADE":        f"{risk_per_trade/100:.4f}",
            "MAX_POSITIONS":         str(int(max_positions)),
            "DAILY_LOSS_LIMIT":      f"{daily_loss_limit/100:.4f}",
        }
        new_lines = []
        for line in lines:
            written = False
            for key, val in replacements.items():
                if line.startswith(key + " =") or line.startswith(key + "="):
                    new_lines.append(f"{key} = {val}\n")
                    written = True
                    break
            if not written:
                new_lines.append(line)
        # Also patch dict entries inside SCREENING_CRITERIA and EXIT_RULES
        text = "".join(new_lines)
        import re as _re
        def _patch(txt, key, val):
            return _re.sub(
                rf'("{key}"\s*:\s*)[^\n,}}]+',
                lambda m: m.group(1) + str(val),
                txt,
            )
        text = _patch(text, "min_market_cap",    int(min_market_cap * 1e9))
        text = _patch(text, "min_avg_volume",    int(min_avg_volume * 1e6))
        text = _patch(text, "min_atr_pct",       round(min_atr, 2))
        text = _patch(text, "max_atr_pct",       round(max_atr, 2))
        text = _patch(text, "stop_loss_atr_mult",round(stop_loss_atr, 2))
        text = _patch(text, "target_1_atr_mult", round(target1_atr, 2))
        text = _patch(text, "target_2_atr_mult", round(target2_atr, 2))
        text = _patch(text, "max_hold_days",     int(max_hold_days))
        with open(cfg_path, "w") as f:
            f.write(text)

    sc = getattr(config, "SCREENING_CRITERIA", {})
    er = getattr(config, "EXIT_RULES", {})

    # ── Account & Risk ───────────────────────────────────────────────────
    st.subheader("Account & Risk")
    ar1, ar2, ar3, ar4, ar5 = st.columns(5)
    i_account      = ar1.number_input("Account Size ($)",      value=float(config.ACCOUNT_SIZE),                  step=1000.0, format="%.0f")
    i_monthly      = ar2.number_input("Monthly Target (%)",    value=round(config.MONTHLY_TARGET * 100, 2),        step=0.5,    format="%.2f")
    i_risk         = ar3.number_input("Risk / Trade (%)",      value=round(config.RISK_PER_TRADE * 100, 2),        step=0.1,    format="%.2f")
    i_max_pos      = ar4.number_input("Max Positions",         value=float(config.MAX_POSITIONS),                  step=1.0,    format="%.0f")
    i_daily_loss   = ar5.number_input("Daily Loss Limit (%)",  value=round(getattr(config,"DAILY_LOSS_LIMIT",0.02)*100, 2), step=0.1, format="%.2f")

    st.markdown("---")

    # ── Screening Criteria ───────────────────────────────────────────────
    st.subheader("Screening Criteria")
    sc1, sc2, sc3, sc4 = st.columns(4)
    i_mktcap    = sc1.number_input("Min Market Cap ($B)",  value=round(sc.get("min_market_cap",5e9)/1e9, 1), step=0.5, format="%.1f")
    i_avgvol    = sc2.number_input("Min Avg Volume ($M)",  value=round(sc.get("min_avg_volume",2e6)/1e6, 1), step=0.5, format="%.1f")
    i_min_atr   = sc3.number_input("Min ATR %",            value=float(sc.get("min_atr_pct", 2.5)),          step=0.1, format="%.1f")
    i_max_atr   = sc4.number_input("Max ATR %",            value=float(sc.get("max_atr_pct", 8.0)),          step=0.1, format="%.1f")

    st.markdown("---")

    # ── Exit Rules ───────────────────────────────────────────────────────
    st.subheader("Exit Rules")
    ex1, ex2, ex3, ex4 = st.columns(4)
    i_sl_atr    = ex1.number_input("Stop Loss (× ATR)",  value=float(er.get("stop_loss_atr_mult", 1.75)), step=0.05, format="%.2f")
    i_t1_atr    = ex2.number_input("Target 1 (× ATR)",   value=float(er.get("target_1_atr_mult",  3.5)),  step=0.05, format="%.2f")
    i_t2_atr    = ex3.number_input("Target 2 (× ATR)",   value=float(er.get("target_2_atr_mult",  4.0)),  step=0.05, format="%.2f")
    i_hold_days = ex4.number_input("Max Hold Days",       value=float(er.get("max_hold_days",       10)),  step=1.0,  format="%.0f")

    st.markdown("---")

    # ── Save button ──────────────────────────────────────────────────────
    sv_col, _ = st.columns([1, 4])
    if sv_col.button("💾  Save Changes", type="primary", use_container_width=True):
        try:
            _save_config(
                i_account, i_monthly, i_risk, i_max_pos, i_daily_loss,
                i_mktcap, i_avgvol, i_min_atr, i_max_atr,
                i_sl_atr, i_t1_atr, i_t2_atr, i_hold_days,
            )
            # Update the live config module attributes directly (no reload needed)
            config.ACCOUNT_SIZE      = int(i_account)
            config.MONTHLY_TARGET    = round(i_monthly / 100, 6)
            config.RISK_PER_TRADE    = round(i_risk / 100, 6)
            config.MAX_POSITIONS     = int(i_max_pos)
            config.DAILY_LOSS_LIMIT  = round(i_daily_loss / 100, 6)
            if hasattr(config, "SCREENING_CRITERIA"):
                config.SCREENING_CRITERIA.update({
                    "min_market_cap": int(i_mktcap * 1e9),
                    "min_avg_volume": int(i_avgvol * 1e6),
                    "min_atr_pct":    round(i_min_atr, 2),
                    "max_atr_pct":    round(i_max_atr, 2),
                })
            if hasattr(config, "EXIT_RULES"):
                config.EXIT_RULES.update({
                    "stop_loss_atr_mult": round(i_sl_atr, 2),
                    "target_1_atr_mult":  round(i_t1_atr, 2),
                    "target_2_atr_mult":  round(i_t2_atr, 2),
                    "max_hold_days":      int(i_hold_days),
                })
            st.success("✅ Settings saved — changes are active immediately.")
        except Exception as _e:
            st.error(f"Failed to save: {_e}")

    st.markdown("---")

    # ── API Status (read-only — from .env) ──────────────────────────────
    st.subheader("API Status")
    st.caption("API keys are read from the `.env` file and cannot be edited here. Restart the container after changing `.env`.")
    a1, a2, a3 = st.columns(3)
    a1.metric("Alpaca",     "✅ Set" if getattr(config,"ALPACA_API_KEY","")     else "❌ Not set")
    a2.metric("Telegram",   "✅ Set" if getattr(config,"TELEGRAM_BOT_TOKEN","") else "❌ Not set")
    a3.metric("Polygon.io", "✅ Set" if _os_settings.environ.get("POLYGON_API_KEY") else "❌ Optional")
