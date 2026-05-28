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


# ── Professional dark-theme CSS ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:ital,opsz,wght@0,14..32,300..700;1,14..32,300..700&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Base ──────────────────────────────────────────────────────────── */
html, body, [class*="css"] { font-family: 'Inter', -apple-system, sans-serif; }

/* ── App background ────────────────────────────────────────────────── */
.stApp {
    background-color: #07090f;
    background-image:
        radial-gradient(ellipse at 15% 40%, rgba(0,180,216,.04) 0%, transparent 55%),
        radial-gradient(ellipse at 85% 15%, rgba(0,204,150,.03) 0%, transparent 50%);
}
.main .block-container { padding-top: 1.5rem; padding-bottom: 2rem; max-width: 1440px; }

/* ── Sidebar ───────────────────────────────────────────────────────── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0b0f1e 0%, #07090f 100%);
    border-right: 1px solid rgba(0,180,216,.12);
}
section[data-testid="stSidebar"] > div { padding-top: 0.5rem; }

/* ── Metric cards ──────────────────────────────────────────────────── */
[data-testid="metric-container"] {
    background: linear-gradient(135deg, #0d1321 0%, #111827 100%);
    border: 1px solid rgba(0,180,216,.18);
    border-radius: 12px;
    padding: 1rem 1.25rem;
    transition: border-color .2s, box-shadow .2s;
}
[data-testid="metric-container"]:hover {
    border-color: rgba(0,180,216,.45);
    box-shadow: 0 0 22px rgba(0,180,216,.1);
}
[data-testid="stMetricLabel"] {
    font-size: .72rem !important; font-weight: 600 !important;
    text-transform: uppercase !important; letter-spacing: .09em !important;
    color: #4b5e7a !important;
}
[data-testid="stMetricValue"] {
    font-size: 1.55rem !important; font-weight: 700 !important;
    font-family: 'JetBrains Mono', monospace !important;
    color: #e2e8f0 !important;
}
[data-testid="stMetricDelta"] { font-size: .8rem !important; font-weight: 500 !important; }

/* ── Buttons ───────────────────────────────────────────────────────── */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #0077b6 0%, #00b4d8 100%);
    border: none; border-radius: 8px; color: #fff;
    font-weight: 600; font-size: .85rem; letter-spacing: .03em;
    padding: .5rem 1.6rem; transition: all .2s;
    box-shadow: 0 4px 18px rgba(0,180,216,.28);
}
.stButton > button[kind="primary"]:hover {
    transform: translateY(-1px); box-shadow: 0 6px 24px rgba(0,180,216,.4);
}
.stButton > button:not([kind="primary"]) {
    background: rgba(255,255,255,.04); border: 1px solid rgba(255,255,255,.09);
    border-radius: 8px; color: #94a3b8; font-weight: 500; transition: all .2s;
}
.stButton > button:not([kind="primary"]):hover {
    background: rgba(255,255,255,.09); border-color: rgba(0,180,216,.35); color: #e2e8f0;
}

/* ── DataFrames ─────────────────────────────────────────────────────── */
.stDataFrame {
    border-radius: 12px !important; overflow: hidden !important;
    border: 1px solid rgba(0,180,216,.13) !important;
}

/* ── Tabs ───────────────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(13,19,33,.8); border-radius: 10px; padding: 4px; gap: 2px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 7px; font-weight: 500; font-size: .85rem; color: #64748b;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg,#0077b6,#00b4d8) !important; color: #fff !important;
}

/* ── Inputs ─────────────────────────────────────────────────────────── */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stTextArea > div > div > textarea {
    background: #0d1321 !important; border-color: rgba(0,180,216,.18) !important;
    border-radius: 8px !important; color: #e2e8f0 !important;
}
.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: rgba(0,180,216,.55) !important;
    box-shadow: 0 0 0 2px rgba(0,180,216,.12) !important;
}
.stSelectbox > div > div,
.stMultiSelect > div > div {
    background: #0d1321 !important; border-color: rgba(0,180,216,.18) !important;
    border-radius: 8px !important;
}

/* ── Multiselect tags ───────────────────────────────────────────────── */
.stMultiSelect span[data-baseweb="tag"] {
    background: rgba(0,180,216,.18) !important; border: 1px solid rgba(0,180,216,.35) !important;
    border-radius: 6px !important; color: #7dd3fc !important;
}

/* ── Expander ───────────────────────────────────────────────────────── */
.streamlit-expanderHeader {
    background: rgba(13,19,33,.8) !important; border-radius: 8px !important;
    border: 1px solid rgba(0,180,216,.13) !important; font-weight: 500 !important;
}

/* ── Slider ─────────────────────────────────────────────────────────── */
[data-baseweb="slider"] [data-testid="stThumbValue"] { color: #00b4d8 !important; }
[role="slider"] { background: #00b4d8 !important; }

/* ── Code ───────────────────────────────────────────────────────────── */
.stCode, code, pre {
    font-family: 'JetBrains Mono', monospace !important;
    background: #0d1321 !important;
    border: 1px solid rgba(0,180,216,.13) !important; border-radius: 8px !important;
}

/* ── Typography ─────────────────────────────────────────────────────── */
h1 {
    font-weight: 700 !important; font-size: 1.75rem !important;
    letter-spacing: -.025em !important; color: #f1f5f9 !important;
    padding-bottom: .6rem !important;
    border-bottom: 2px solid rgba(0,180,216,.25) !important; margin-bottom: 1.5rem !important;
}
h2 { font-weight: 600 !important; color: #cbd5e1 !important; font-size: 1.25rem !important; }
h3 { font-weight: 600 !important; color: #94a3b8 !important; font-size: 1.05rem !important; }

/* ── Divider ────────────────────────────────────────────────────────── */
hr { border-color: rgba(0,180,216,.12) !important; margin: 1.5rem 0 !important; }

/* ── Caption ────────────────────────────────────────────────────────── */
.stCaption { color: #475569 !important; font-size: .78rem !important; }

/* ── Scrollbar ──────────────────────────────────────────────────────── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: #07090f; }
::-webkit-scrollbar-thumb { background: rgba(0,180,216,.25); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: rgba(0,180,216,.45); }

/* ── Signal badge utility classes (used in HTML markdown) ────────────── */
.badge {
    display: inline-block; padding: 3px 10px; border-radius: 20px;
    font-size: .7rem; font-weight: 700; letter-spacing: .07em; text-transform: uppercase;
}
.badge-strong { background:rgba(0,255,157,.18); color:#00ff9d; border:1px solid rgba(0,255,157,.35); }
.badge-buy    { background:rgba(0,204,150,.15); color:#00cc96; border:1px solid rgba(0,204,150,.3); }
.badge-watch  { background:rgba(251,183,3,.13);  color:#fbb703; border:1px solid rgba(251,183,3,.28); }
.badge-avoid  { background:rgba(239,83,80,.13);  color:#ef5350; border:1px solid rgba(239,83,80,.28); }
.badge-hold   { background:rgba(148,163,184,.08);color:#94a3b8; border:1px solid rgba(148,163,184,.18); }

/* ── KPI stat card ──────────────────────────────────────────────────── */
.kpi-card {
    background: linear-gradient(135deg,#0d1321,#111827);
    border: 1px solid rgba(0,180,216,.18); border-radius: 12px;
    padding: 1rem 1.25rem; text-align: center;
}
.kpi-label { font-size:.7rem; font-weight:600; text-transform:uppercase; letter-spacing:.09em; color:#4b5e7a; }
.kpi-value { font-size:1.5rem; font-weight:700; font-family:'JetBrains Mono',monospace; color:#e2e8f0; margin:.2rem 0; }
.kpi-sub   { font-size:.75rem; color:#64748b; }
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

# Availability flags used throughout for guarding UI sections
HAS_GDF    = _gdf  is not None
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

# ── Sidebar navigation ───────────────────────────────────────────────────────
st.sidebar.markdown("""
<div style="padding:.75rem 1rem 1rem; border-bottom:1px solid rgba(0,180,216,.15); margin-bottom:.75rem;">
  <div style="font-size:1.2rem;font-weight:800;color:#e2e8f0;letter-spacing:-.02em;">
    🌍 Global Trading
  </div>
  <div style="font-size:.72rem;color:#4b5e7a;font-weight:500;letter-spacing:.05em;text-transform:uppercase;margin-top:.15rem;">
    Multi-Market Dashboard
  </div>
</div>
""", unsafe_allow_html=True)

_acct_target = config.ACCOUNT_SIZE * config.MONTHLY_TARGET
st.sidebar.markdown(f"""
<div style="background:linear-gradient(135deg,rgba(0,119,182,.15),rgba(0,180,216,.08));
            border:1px solid rgba(0,180,216,.2);border-radius:10px;
            padding:.65rem 1rem;margin:.5rem 0 1rem;font-size:.78rem;">
  <div style="display:flex;justify-content:space-between;margin-bottom:.3rem;">
    <span style="color:#4b5e7a;font-weight:600;text-transform:uppercase;letter-spacing:.06em;font-size:.68rem;">Account</span>
    <span style="color:#e2e8f0;font-family:'JetBrains Mono',monospace;font-weight:700;">${config.ACCOUNT_SIZE:,}</span>
  </div>
  <div style="display:flex;justify-content:space-between;">
    <span style="color:#4b5e7a;font-weight:600;text-transform:uppercase;letter-spacing:.06em;font-size:.68rem;">Monthly Target</span>
    <span style="color:#00cc96;font-family:'JetBrains Mono',monospace;font-weight:700;">${_acct_target:,.0f} &nbsp;<span style="color:#4b5e7a;font-size:.65rem;">({config.MONTHLY_TARGET*100:.0f}%)</span></span>
  </div>
</div>
""", unsafe_allow_html=True)

PAGES = [
    "🏠 Overview",
    "📊 Market Regime",
    "🎯 Signals",
    "📈 Fundamentals",
    "🔀 Combined Analysis",
    "📅 Earnings Calendar",
    "👔 Insider Activity",
    "🔍 Stock Screener",
    "📋 Trade Journal",
    "📊 Performance",
    "💼 Portfolio",
    "📐 Position Calculator",
    "🔬 Signal Analysis",
    "🔄 Sector Rotation",
    "🧪 Backtest Pro",
    "📓 Journal Analytics",
    "⚙️ Settings",
]

page = st.sidebar.selectbox("Navigate", PAGES)

# Module status indicators in sidebar
st.sidebar.markdown("---")
_mod_rows = "".join(
    f'<div style="display:flex;align-items:center;gap:.5rem;padding:.2rem 0;">'
    f'<span style="width:6px;height:6px;border-radius:50%;background:{"#00cc96" if ok else "#ef5350"};'
    f'box-shadow:0 0 6px {"#00cc96" if ok else "#ef5350"};flex-shrink:0;"></span>'
    f'<span style="font-size:.75rem;color:{"#94a3b8" if ok else "#475569"};font-weight:{"500" if ok else "400"};">{lbl}</span>'
    f'</div>'
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
    ]
)
st.sidebar.markdown(
    f'<div style="padding:.4rem .2rem;">'
    f'<div style="font-size:.65rem;font-weight:700;text-transform:uppercase;letter-spacing:.1em;'
    f'color:#334155;margin-bottom:.4rem;">Modules</div>'
    f'{_mod_rows}</div>',
    unsafe_allow_html=True,
)

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: OVERVIEW
# ═══════════════════════════════════════════════════════════════════════════════
if page == "🏠 Overview":
    st.title("🏠 Trading Dashboard Overview")
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

    if not HAS_FA:
        st.error("fundamental_analyzer module not available.")
    else:
        symbol = st.text_input("Symbol (e.g. NVDA, SAP.DE, TCS.NS)", "NVDA").upper().strip()
        if st.button("Analyze"):
            with st.spinner(f"Fetching fundamentals for {symbol}…"):
                try:
                    result = C["fa"].analyze(symbol)
                    if result and "error" not in result:
                        c1, c2, c3, c4 = st.columns(4)
                        c1.metric("P/E Ratio",      result.get("pe_ratio", "N/A"))
                        c2.metric("Revenue Growth", f"{result.get('revenue_growth',0)*100:.1f}%")
                        c3.metric("Profit Margin",  f"{result.get('profit_margin',0)*100:.1f}%")
                        c4.metric("Fund. Score",    f"{result.get('fundamental_score',0)}/100")
                        st.json({k: v for k, v in result.items() if not isinstance(v, (dict, list))})
                    else:
                        st.error(result.get("error", "No data") if result else "No result")
                except Exception as e:
                    st.error(f"Error: {e}")

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: COMBINED ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "🔀 Combined Analysis":
    st.title("🔀 Combined Technical + Fundamental Analysis")

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
# PAGE: SETTINGS
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "⚙️ Settings":
    st.title("⚙️ System Settings")
    st.info("Edit `config.py` to change any value, then restart the dashboard.")

    st.subheader("Account & Risk")
    g1,g2,g3,g4 = st.columns(4)
    g1.metric("Account Size",     f"${config.ACCOUNT_SIZE:,}")
    g2.metric("Risk / Trade",     f"{config.RISK_PER_TRADE*100:.1f}%")
    g3.metric("Max Positions",    config.MAX_POSITIONS)
    g4.metric("Daily Loss Limit", f"{getattr(config,'DAILY_LOSS_LIMIT',0.02)*100:.0f}%")

    st.markdown("---")
    st.subheader("Screening Criteria")
    sc = getattr(config,"SCREENING_CRITERIA",{})
    s1,s2,s3 = st.columns(3)
    s1.metric("Min Market Cap",  f"${sc.get('min_market_cap',0)/1e9:.0f}B")
    s2.metric("Min Avg Volume",  f"{sc.get('min_avg_volume',0)/1e6:.1f}M")
    s3.metric("ATR Range",       f"{sc.get('min_atr_pct',2)}-{sc.get('max_atr_pct',8)}%")

    st.markdown("---")
    st.subheader("Exit Rules")
    er = getattr(config,"EXIT_RULES",{})
    e1,e2,e3,e4 = st.columns(4)
    e1.metric("Stop Loss ATR",  f"{er.get('stop_loss_atr_mult',1.75)}×")
    e2.metric("Target 1 ATR",   f"{er.get('target_1_atr_mult',2.5)}×")
    e3.metric("Target 2 ATR",   f"{er.get('target_2_atr_mult',4.0)}×")
    e4.metric("Max Hold Days",  er.get("max_hold_days",10))

    st.markdown("---")
    st.subheader("API Status")
    a1,a2,a3 = st.columns(3)
    a1.metric("Alpaca",     "✅ Set" if getattr(config,"ALPACA_API_KEY","")     else "❌ Not set")
    a2.metric("Telegram",   "✅ Set" if getattr(config,"TELEGRAM_BOT_TOKEN","") else "❌ Not set")
    import os
    a3.metric("Polygon.io", "✅ Set" if os.environ.get("POLYGON_API_KEY")       else "❌ Optional")
