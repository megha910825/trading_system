"""
_common.py — shared bootstrap, CSS, module imports, and resource init.
Imported at the top of every page in pages/.
"""

import sys as _sys, os as _os
_APP_ROOT = _os.path.dirname(_os.path.abspath(__file__))
for _sub in ["core", "analysis", "signals", "screening", "portfolio",
             "strategies", "research", "automation"]:
    _p = _os.path.join(_APP_ROOT, _sub)
    if _p not in _sys.path:
        _sys.path.insert(0, _p)
# Ensure the project root itself is on the path (for config, _common, etc.)
if _APP_ROOT not in _sys.path:
    _sys.path.insert(0, _APP_ROOT)

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import config

# ── Professional light-theme CSS ──────────────────────────────────────────────
GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:ital,opsz,wght@0,14..32,300..700;1,14..32,300..700&family=JetBrains+Mono:wght@400;500&display=swap');

html, body { font-family: 'Inter', -apple-system, sans-serif; }

/* ── Hide Streamlit top bar / decoration ─────────────────────────────── */
[data-testid="stDecoration"],
[data-testid="stDecoration"] * {
    display: none !important;
    height: 0 !important;
    visibility: hidden !important;
}
header[data-testid="stHeader"],
header[data-testid="stHeader"] * {
    height: 0 !important;
    min-height: 0 !important;
    padding: 0 !important;
    display: none !important;
    visibility: hidden !important;
}
/* Newer Streamlit emotion-cache top bar */
.stApp > header { display: none !important; }
#stDecoration { display: none !important; }

.stApp { background-color: #f0f4f8 !important; }
.main .block-container { padding-top: 1.5rem; padding-bottom: 2rem; max-width: 1440px; }

section[data-testid="stSidebar"] {
    background: #ffffff !important;
    border-right: 1px solid #e2e8f0;
}
section[data-testid="stSidebar"] > div { padding-top: 0.5rem; }

h1 {
    font-weight: 700 !important; font-size: 1.75rem !important;
    letter-spacing: -.025em !important; color: #0f172a !important;
    padding-bottom: .6rem !important;
    border-bottom: 2px solid #e2e8f0 !important; margin-bottom: 1.5rem !important;
}
h2 { font-weight: 600 !important; color: #1e293b !important; font-size: 1.25rem !important; }
h3 { font-weight: 600 !important; color: #374151 !important; font-size: 1.05rem !important; }
p, li, span, td, th { color: #1e293b; }

label,
[data-testid="stWidgetLabel"],
[data-testid="stWidgetLabel"] *,
[data-testid="stWidgetLabel"] p {
    color: #1e293b !important;
    font-size: .85rem !important;
    font-weight: 500 !important;
}

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

.stMultiSelect [data-baseweb="select"] > div {
    background: #ffffff !important;
    border: 1px solid #cbd5e1 !important;
    border-radius: 8px !important;
    min-height: 40px !important;
}
.stMultiSelect [data-baseweb="select"] input,
.stMultiSelect [data-baseweb="select"] [data-testid="stMultiSelectInput"],
.stMultiSelect [placeholder] {
    color: #64748b !important;
}
.stMultiSelect span[data-baseweb="tag"] {
    background: #dbeafe !important;
    border: 1px solid #93c5fd !important;
    border-radius: 6px !important;
    color: #1d4ed8 !important;
    font-weight: 600 !important;
    font-size: .78rem !important;
}
.stMultiSelect span[data-baseweb="tag"] span { color: #1d4ed8 !important; }
.stMultiSelect span[data-baseweb="tag"] svg { fill: #1d4ed8 !important; }

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

[data-baseweb="slider"] [data-testid="stThumbValue"] { color: #0077b6 !important; }
[role="slider"] { background: #0077b6 !important; }

.stRadio div[role="radiogroup"] label,
.stCheckbox label { color: #1e293b !important; font-weight: 500 !important; }

.stDataFrame {
    border-radius: 12px !important; overflow: hidden !important;
    border: 1px solid #e2e8f0 !important;
    box-shadow: 0 1px 4px rgba(15,23,42,.06) !important;
}

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

[data-testid="stAlert"] p { color: inherit !important; }

.stCode, code, pre {
    font-family: 'JetBrains Mono', monospace !important;
    background: #f1f5f9 !important;
    border: 1px solid #e2e8f0 !important; border-radius: 8px !important;
    color: #1e293b !important;
}

hr { border-color: #e2e8f0 !important; margin: 1.5rem 0 !important; }

.stCaption, [data-testid="stCaption"] { color: #64748b !important; font-size: .78rem !important; }

::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: #f1f5f9; }
::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #94a3b8; }

.badge {
    display: inline-block; padding: 3px 10px; border-radius: 20px;
    font-size: .7rem; font-weight: 700; letter-spacing: .07em; text-transform: uppercase;
}
.badge-strong { background:#dcfce7; color:#15803d; border:1px solid #86efac; }
.badge-buy    { background:#d1fae5; color:#059669; border:1px solid #6ee7b7; }
.badge-watch  { background:#fef9c3; color:#a16207; border:1px solid #fde047; }
.badge-avoid  { background:#fee2e2; color:#dc2626; border:1px solid #fca5a5; }
.badge-hold   { background:#f1f5f9; color:#64748b; border:1px solid #cbd5e1; }

.kpi-card {
    background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px;
    padding: 1rem 1.25rem; text-align: center;
    box-shadow: 0 1px 4px rgba(15,23,42,.06);
}
.kpi-label { font-size:.7rem; font-weight:600; text-transform:uppercase; letter-spacing:.09em; color:#64748b; }
.kpi-value { font-size:1.5rem; font-weight:700; font-family:'JetBrains Mono',monospace; color:#0f172a; margin:.2rem 0; }
.kpi-sub   { font-size:.75rem; color:#94a3b8; }

section[data-testid="stSidebar"] .stButton > button {
    border-radius: 7px !important; font-size: .8rem !important;
    font-weight: 500 !important; transition: all .15s;
}
</style>
"""

DARK_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:ital,opsz,wght@0,14..32,300..700;1,14..32,300..700&family=JetBrains+Mono:wght@400;500&display=swap');

html, body { font-family: 'Inter', -apple-system, sans-serif; }

[data-testid="stDecoration"], [data-testid="stDecoration"] * { display:none!important; height:0!important; visibility:hidden!important; }
header[data-testid="stHeader"], header[data-testid="stHeader"] * { height:0!important; min-height:0!important; padding:0!important; display:none!important; }
.stApp > header { display:none!important; }
#stDecoration { display:none!important; }

.stApp { background-color: #0d1117 !important; }
.main .block-container { padding-top: 1.5rem; padding-bottom: 2rem; max-width: 1440px; }

section[data-testid="stSidebar"] { background: #161b22 !important; border-right: 1px solid #30363d; }
section[data-testid="stSidebar"] > div { padding-top: 0.5rem; }

h1 { font-weight:700!important; font-size:1.75rem!important; letter-spacing:-.025em!important; color:#e6edf3!important; padding-bottom:.6rem!important; border-bottom:2px solid #30363d!important; margin-bottom:1.5rem!important; }
h2 { font-weight:600!important; color:#cdd9e5!important; font-size:1.25rem!important; }
h3 { font-weight:600!important; color:#adbac7!important; font-size:1.05rem!important; }
p, li, span, td, th { color:#cdd9e5; }

label, [data-testid="stWidgetLabel"], [data-testid="stWidgetLabel"] *, [data-testid="stWidgetLabel"] p { color:#cdd9e5!important; font-size:.85rem!important; font-weight:500!important; }

.stTextInput > div > div > input, .stNumberInput > div > div > input, .stTextArea > div > div > textarea { background:#21262d!important; border:1px solid #30363d!important; border-radius:8px!important; color:#e6edf3!important; caret-color:#e6edf3!important; font-size:.875rem!important; }
.stTextInput > div > div > input:focus, .stNumberInput > div > div > input:focus, .stTextArea > div > div > textarea:focus { border-color:#0077b6!important; box-shadow:0 0 0 3px rgba(0,119,182,.2)!important; outline:none!important; }

.stSelectbox [data-baseweb="select"] > div { background:#21262d!important; border:1px solid #30363d!important; border-radius:8px!important; }
.stSelectbox [data-baseweb="select"] span, .stSelectbox [data-baseweb="select"] div, .stSelectbox [data-baseweb="select"] input { color:#e6edf3!important; background:transparent!important; }
[data-baseweb="popover"] [role="listbox"], [data-baseweb="popover"] [role="option"], [data-baseweb="menu"] li { background:#21262d!important; color:#e6edf3!important; }
[data-baseweb="popover"] [aria-selected="true"], [data-baseweb="popover"] [role="option"]:hover { background:#1c3a5e!important; color:#58a6ff!important; }

.stMultiSelect [data-baseweb="select"] > div { background:#21262d!important; border:1px solid #30363d!important; border-radius:8px!important; min-height:40px!important; }
.stMultiSelect span[data-baseweb="tag"] { background:#1c3a5e!important; border:1px solid #1f6feb!important; border-radius:6px!important; color:#58a6ff!important; font-weight:600!important; font-size:.78rem!important; }
.stMultiSelect span[data-baseweb="tag"] span { color:#58a6ff!important; }
.stMultiSelect span[data-baseweb="tag"] svg { fill:#58a6ff!important; }

[data-testid="metric-container"] { background:#161b22!important; border:1px solid #30363d!important; border-radius:12px!important; padding:1rem 1.25rem!important; box-shadow:0 1px 4px rgba(0,0,0,.3)!important; transition:border-color .2s, box-shadow .2s; }
[data-testid="metric-container"]:hover { border-color:#0077b6!important; box-shadow:0 4px 16px rgba(0,119,182,.2)!important; }
[data-testid="stMetricLabel"] { font-size:.72rem!important; font-weight:600!important; text-transform:uppercase!important; letter-spacing:.09em!important; color:#8b949e!important; }
[data-testid="stMetricValue"] { font-size:1.55rem!important; font-weight:700!important; font-family:'JetBrains Mono',monospace!important; color:#e6edf3!important; }

.stButton > button[kind="primary"] { background:linear-gradient(135deg,#0077b6 0%,#0096c7 100%)!important; border:none!important; border-radius:8px!important; color:#fff!important; font-weight:600!important; font-size:.85rem!important; padding:.5rem 1.6rem!important; box-shadow:0 2px 10px rgba(0,119,182,.3)!important; }
.stButton > button:not([kind="primary"]) { background:#21262d!important; border:1px solid #30363d!important; border-radius:8px!important; color:#cdd9e5!important; font-weight:500!important; }
.stButton > button:not([kind="primary"]):hover { background:#30363d!important; border-color:#0077b6!important; color:#58a6ff!important; }

.stTabs [data-baseweb="tab-list"] { background:#21262d!important; border-radius:10px!important; padding:4px!important; gap:2px!important; }
.stTabs [data-baseweb="tab"] { border-radius:7px!important; font-weight:500!important; font-size:.85rem!important; color:#8b949e!important; }
.stTabs [aria-selected="true"] { background:linear-gradient(135deg,#0077b6,#0096c7)!important; color:#fff!important; }

.stDataFrame { border-radius:12px!important; overflow:hidden!important; border:1px solid #30363d!important; }
[data-testid="stExpander"] { border:1px solid #30363d!important; border-radius:10px!important; background:#161b22!important; }
[data-testid="stExpander"] summary { background:#21262d!important; color:#cdd9e5!important; font-weight:600!important; font-size:.85rem!important; padding:.6rem 1rem!important; }

.stCode, code, pre { font-family:'JetBrains Mono',monospace!important; background:#21262d!important; border:1px solid #30363d!important; border-radius:8px!important; color:#e6edf3!important; }
hr { border-color:#30363d!important; margin:1.5rem 0!important; }
.stCaption, [data-testid="stCaption"] { color:#8b949e!important; font-size:.78rem!important; }
::-webkit-scrollbar { width:5px; height:5px; }
::-webkit-scrollbar-track { background:#0d1117; }
::-webkit-scrollbar-thumb { background:#30363d; border-radius:4px; }

.badge { display:inline-block; padding:3px 10px; border-radius:20px; font-size:.7rem; font-weight:700; letter-spacing:.07em; text-transform:uppercase; }
.badge-strong { background:#1a4731; color:#3fb950; border:1px solid #2ea043; }
.badge-buy    { background:#1a4731; color:#3fb950; border:1px solid #238636; }
.badge-watch  { background:#3d2b00; color:#d29922; border:1px solid #9e6a03; }
.badge-avoid  { background:#3d1717; color:#f85149; border:1px solid #da3633; }
.badge-hold   { background:#21262d; color:#8b949e; border:1px solid #30363d; }

section[data-testid="stSidebar"] .stButton > button { border-radius:7px!important; font-size:.8rem!important; font-weight:500!important; }
</style>
"""


def apply_css():
    """Apply light or dark CSS based on session state toggle."""
    if "dark_mode" not in st.session_state:
        st.session_state.dark_mode = False

    # Render toggle in sidebar
    with st.sidebar:
        st.markdown("<div style='padding:.4rem 0 .2rem;'>", unsafe_allow_html=True)
        dark = st.toggle("🌙 Dark mode", value=st.session_state.dark_mode, key="_theme_toggle")
        st.session_state.dark_mode = dark
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(DARK_CSS if st.session_state.dark_mode else GLOBAL_CSS, unsafe_allow_html=True)


def _help(md: str):
    """Collapsible info panel shown at the top of each page."""
    with st.expander("ℹ️  How to use this page", expanded=False):
        st.markdown(md)


# ── Optional module imports ───────────────────────────────────────────────────
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

HAS_GDF    = _gdf     is not None
HAS_WI     = _wi      is not None
HAS_GSG    = _gsg     is not None
HAS_TA     = _ta      is not None
HAS_FA     = _fa      is not None
HAS_CA     = _ca      is not None
HAS_REGIME = _mr      is not None
HAS_PM     = _pm      is not None
HAS_JOURNAL= _tj      is not None
HAS_PT     = _pt      is not None
HAS_BT     = _bt      is not None
HAS_EARN   = _ec      is not None
HAS_INSIDER= _it      is not None
HAS_SS     = _ss      is not None
HAS_SR     = _sr      is not None
HAS_MC     = _mc      is not None
HAS_YF     = _yf      is not None


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


def get_resources():
    return _init_resources()
