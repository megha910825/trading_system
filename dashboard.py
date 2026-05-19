#!/usr/bin/env python3
"""
Trading Dashboard - Complete System for 3%+ Monthly Returns
"""

import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# ═══════════════════════════════════════════════════════════════
# PAGE CONFIG - Must be first
# ═══════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="Trading System",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ═══════════════════════════════════════════════════════════════
# SESSION STATE INITIALIZATION
# ═══════════════════════════════════════════════════════════════

# Initialize session state for navigation
if 'current_page' not in st.session_state:
    st.session_state.current_page = "🏠 Dashboard"

if 'trigger_signals' not in st.session_state:
    st.session_state.trigger_signals = False

# ═══════════════════════════════════════════════════════════════
# CUSTOM CSS
# ═══════════════════════════════════════════════════════════════

st.markdown("""
<style>
    .metric-card {
        background-color: #1e1e1e;
        border-radius: 10px;
        padding: 15px;
        margin: 5px 0;
    }
    .stProgress > div > div > div > div {
        background-color: #00C851;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.5rem;
    }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# IMPORTS WITH ERROR HANDLING
# ═══════════════════════════════════════════════════════════════

# Config
try:
    import config
    ACCOUNT_SIZE = getattr(config, 'ACCOUNT_SIZE', 50000)
    MONTHLY_TARGET = getattr(config, 'MONTHLY_TARGET', 0.03)
    RISK_PER_TRADE = getattr(config, 'RISK_PER_TRADE', 0.015)
    MAX_POSITIONS = getattr(config, 'MAX_POSITIONS', 8)
except ImportError:
    ACCOUNT_SIZE = 50000
    MONTHLY_TARGET = 0.03
    RISK_PER_TRADE = 0.015
    MAX_POSITIONS = 8

# Data fetcher
try:
    from global_data_fetcher import GlobalDataFetcher
    HAS_FETCHER = True
except ImportError:
    HAS_FETCHER = False
    GlobalDataFetcher = None

# Technical analyzer
try:
    from technical_analyzer import TechnicalAnalyzer
    HAS_ANALYZER = True
except ImportError:
    HAS_ANALYZER = False
    TechnicalAnalyzer = None

# Signal generator
try:
    from global_signal_generator import GlobalSignalGenerator
    HAS_SIGNALS = True
except ImportError:
    HAS_SIGNALS = False
    GlobalSignalGenerator = None

# Universe manager
try:
    from global_universe_manager import GlobalUniverseManager
    HAS_UNIVERSE = True
except ImportError:
    HAS_UNIVERSE = False
    GlobalUniverseManager = None

# Backtester
try:
    from backtester import Backtester
    HAS_BACKTESTER = True
except ImportError:
    HAS_BACKTESTER = False
    Backtester = None

# Market config
try:
    from market_config import MARKETS, get_market_status
    HAS_MARKETS = True
except ImportError:
    HAS_MARKETS = False
    class DummyMarket:
        def __init__(self, name, currency):
            self.name = name
            self.currency = currency
    MARKETS = {
        "US": DummyMarket("United States", "USD"),
        "DE": DummyMarket("Germany", "EUR"),
        "IN": DummyMarket("India", "INR"),
    }
    def get_market_status():
        return {"US": "Unknown", "DE": "Unknown", "IN": "Unknown"}

# Trade Journal
try:
    from trade_journal import TradeJournal
    HAS_JOURNAL = True
except ImportError:
    HAS_JOURNAL = False
    TradeJournal = None

# Market Regime
try:
    from market_regime import MarketRegimeFilter, Regime
    HAS_REGIME = True
except ImportError:
    HAS_REGIME = False
    MarketRegimeFilter = None

# Performance Tracker
try:
    from performance_tracker import PerformanceTracker
    HAS_TRACKER = True
except ImportError:
    HAS_TRACKER = False
    PerformanceTracker = None

# yfinance
try:
    import yfinance as yf
    HAS_YFINANCE = True
except ImportError:
    HAS_YFINANCE = False


# ═══════════════════════════════════════════════════════════════
# INITIALIZE COMPONENTS
# ═══════════════════════════════════════════════════════════════

@st.cache_resource
def init_components():
    """Initialize all components"""
    comp = {}

    if HAS_FETCHER and GlobalDataFetcher:
        try:
            comp['fetcher'] = GlobalDataFetcher()
        except:
            pass

    if HAS_ANALYZER and TechnicalAnalyzer:
        try:
            comp['analyzer'] = TechnicalAnalyzer()
        except:
            pass

    if HAS_SIGNALS and GlobalSignalGenerator:
        try:
            comp['signals'] = GlobalSignalGenerator()
        except:
            pass

    if HAS_UNIVERSE and GlobalUniverseManager:
        try:
            comp['universe'] = GlobalUniverseManager()
        except:
            pass

    if HAS_JOURNAL and TradeJournal:
        try:
            comp['journal'] = TradeJournal()
        except:
            pass

    if HAS_REGIME and MarketRegimeFilter:
        try:
            comp['regime'] = MarketRegimeFilter()
        except:
            pass

    if HAS_TRACKER and PerformanceTracker:
        try:
            comp['tracker'] = PerformanceTracker()
        except:
            pass

    return comp

comp = init_components()


# ═══════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def get_entry_price(sig):
    return sig.get('ideal_entry', sig.get('entry', sig.get('entry_price', sig.get('current_price', 0))))

def get_risk_reward(sig):
    return sig.get('risk_reward', sig.get('rr_1', sig.get('rr', 0)))

def is_uptrend(sig):
    if 'uptrend' in sig:
        return sig['uptrend']
    if 'trend' in sig:
        return sig['trend'] == 'BULLISH'
    if 'above_ema50' in sig:
        return sig['above_ema50']
    return False

@st.cache_data(ttl=300)
def fetch_stock_data(symbol, period="6mo"):
    if not HAS_YFINANCE:
        return pd.DataFrame()
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period)
        if not df.empty:
            df.columns = df.columns.str.lower()
        return df
    except:
        return pd.DataFrame()

@st.cache_data(ttl=60)
def get_stock_info(symbol):
    if not HAS_YFINANCE:
        return {}
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        return {
            "name": info.get("shortName", symbol),
            "sector": info.get("sector", "N/A"),
            "industry": info.get("industry", "N/A"),
        }
    except:
        return {"name": symbol, "sector": "N/A", "industry": "N/A"}


# ═══════════════════════════════════════════════════════════════
# NAVIGATION HELPER
# ═══════════════════════════════════════════════════════════════

def navigate_to(page_name):
    """Helper function to navigate to a page"""
    st.session_state.current_page = page_name


# ═══════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════

st.sidebar.title("📈 Trading System")
st.sidebar.markdown(f"**Target: {MONTHLY_TARGET*100:.0f}% Monthly**")

# Market Regime Status
if 'regime' in comp:
    st.sidebar.markdown("---")
    st.sidebar.subheader("🌍 Market Regime")

    try:
        conditions = comp['regime'].analyze()

        regime_colors = {
            "STRONG_BULL": "🟢",
            "BULL": "🟢",
            "NEUTRAL": "🟡",
            "BEAR": "🔴",
            "STRONG_BEAR": "🔴"
        }

        regime_icon = regime_colors.get(conditions.regime.value, "⚪")
        st.sidebar.markdown(f"{regime_icon} **{conditions.regime.value}**")
        st.sidebar.markdown(f"SPY: ${conditions.spy_price:,.2f} ({conditions.spy_change_1d:+.2f}%)")
        st.sidebar.markdown(f"VIX: {conditions.vix_level:.1f}")
        st.sidebar.markdown(f"**Size: {conditions.position_mult*100:.0f}%**")

        if not conditions.can_trade_long:
            st.sidebar.error("⚠️ Avoid Longs!")
    except:
        st.sidebar.warning("Regime unavailable")

# Monthly Progress
if 'tracker' in comp:
    st.sidebar.markdown("---")
    st.sidebar.subheader("📊 Monthly Progress")

    try:
        progress = comp['tracker'].get_monthly_progress()
        pct = progress.get('progress_pct', 0)
        st.sidebar.progress(min(pct / 100, 1.0))
        st.sidebar.markdown(f"P&L: **${progress.get('current_pnl', 0):+,.2f}** ({pct:.1f}%)")
    except:
        st.sidebar.info("No trades yet")

st.sidebar.markdown("---")

# Market Status
st.sidebar.subheader("🕐 Markets")
try:
    status = get_market_status()
    for code, stat in status.items():
        flag = {"US": "🇺🇸", "DE": "🇩🇪", "IN": "🇮🇳"}.get(code, "🌐")
        st.sidebar.markdown(f"{flag} {stat}")
except:
    pass

st.sidebar.markdown("---")

# Navigation - use session state
pages = ["🏠 Dashboard", "🎯 Signals", "📈 Analysis", "📋 Trade Journal",
         "📊 Performance", "🔍 Scanner", "📉 Backtest", "📐 Calculator", "⚙️ Settings"]

# Sync session state with radio selection
page = st.sidebar.radio(
    "Navigate",
    pages,
    index=pages.index(st.session_state.current_page) if st.session_state.current_page in pages else 0,
    key="nav_radio"
)

# Update session state when radio changes
if page != st.session_state.current_page:
    st.session_state.current_page = page

# System Status
with st.sidebar.expander("⚙️ System Status"):
    st.write(f"{'✅' if HAS_FETCHER else '❌'} Data Fetcher")
    st.write(f"{'✅' if HAS_ANALYZER else '❌'} Analyzer")
    st.write(f"{'✅' if HAS_SIGNALS else '❌'} Signals")
    st.write(f"{'✅' if HAS_JOURNAL else '❌'} Trade Journal")
    st.write(f"{'✅' if HAS_REGIME else '❌'} Market Regime")
    st.write(f"{'✅' if HAS_TRACKER else '❌'} Performance")


# ═══════════════════════════════════════════════════════════════
# PAGE: DASHBOARD
# ═══════════════════════════════════════════════════════════════

if st.session_state.current_page == "🏠 Dashboard":
    st.title("🏠 Trading Dashboard")

    # Top metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("💰 Account", f"${ACCOUNT_SIZE:,}")
    col2.metric("🎯 Monthly Target", f"${ACCOUNT_SIZE * MONTHLY_TARGET:,.0f}")
    col3.metric("⚠️ Risk/Trade", f"{RISK_PER_TRADE*100:.1f}%")
    col4.metric("📊 Max Positions", MAX_POSITIONS)

    st.markdown("---")

    # Two column layout
    col1, col2 = st.columns(2)

    with col1:
        # Market Regime
        st.subheader("🌍 Market Regime")

        if 'regime' in comp:
            try:
                c = comp['regime'].analyze()

                if c.regime.value in ["STRONG_BULL", "BULL"]:
                    st.success(f"**{c.regime.value}** - {c.recommendation}")
                elif c.regime.value == "NEUTRAL":
                    st.warning(f"**{c.regime.value}** - {c.recommendation}")
                else:
                    st.error(f"**{c.regime.value}** - {c.recommendation}")

                mc1, mc2, mc3 = st.columns(3)
                mc1.metric("SPY", f"${c.spy_price:,.2f}", f"{c.spy_change_1d:+.2f}%")
                mc2.metric("VIX", f"{c.vix_level:.1f}", c.vix_status)
                mc3.metric("Size", f"{c.position_mult*100:.0f}%")

            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.info("Create market_regime.py to enable")

    with col2:
        # Monthly Progress
        st.subheader("📊 Monthly Progress")

        if 'tracker' in comp:
            try:
                p = comp['tracker'].get_monthly_progress()

                pct = min(p.get('progress_pct', 0), 100)
                st.progress(pct / 100)

                if pct >= 100:
                    st.success(f"🎉 Target achieved! {pct:.1f}%")
                elif p.get('on_track', False):
                    st.info(f"📈 On track: {pct:.1f}%")
                else:
                    st.warning(f"⚠️ Behind: {pct:.1f}%")

                pc1, pc2 = st.columns(2)
                pc1.metric("Current P&L", f"${p.get('current_pnl', 0):+,.2f}")
                pc2.metric("Remaining", f"${p.get('remaining', 0):,.2f}")

            except:
                st.info("Start logging trades to see progress")
        else:
            st.info("Create performance_tracker.py to enable")

    st.markdown("---")

    # Open Positions
    st.subheader("📂 Open Positions")

    if 'journal' in comp:
        try:
            open_trades = comp['journal'].get_open_trades()

            if not open_trades.empty:
                # Add current prices
                for idx, row in open_trades.iterrows():
                    try:
                        ticker = yf.Ticker(row['symbol'])
                        current = ticker.fast_info.get('lastPrice', row['entry_price'])
                        open_trades.at[idx, 'current'] = current
                        open_trades.at[idx, 'pnl'] = (current - row['entry_price']) * row['shares']
                    except:
                        open_trades.at[idx, 'current'] = row['entry_price']
                        open_trades.at[idx, 'pnl'] = 0

                st.dataframe(
                    open_trades[['id', 'symbol', 'entry_date', 'entry_price',
                                'shares', 'stop_loss', 'target_1', 'current', 'pnl']],
                    use_container_width=True,
                    hide_index=True
                )

                total_pnl = open_trades['pnl'].sum()
                st.metric("Total Unrealized P&L", f"${total_pnl:+,.2f}")
            else:
                st.info("No open positions")
        except:
            st.info("No open positions")
    else:
        st.info("Create trade_journal.py to enable position tracking")

    st.markdown("---")

    # ═══════════════════════════════════════════════════════════
    # QUICK ACTIONS - FIXED
    # ═══════════════════════════════════════════════════════════

    st.subheader("⚡ Quick Actions")

    st.caption("Use the navigation dropdown in sidebar, or click below to expand inline:")

    # Using expanders for inline actions instead of navigation

    # Quick Signal Generation
    with st.expander("🎯 Quick Signal Scan", expanded=False):
        st.write("Generate trading signals for selected markets:")

        quick_markets = st.multiselect(
            "Markets",
            ["US", "DE", "IN"],
            default=["US"],
            key="quick_markets"
        )

        if st.button("🚀 Generate Signals", key="quick_gen_signals"):
            if HAS_SIGNALS:
                with st.spinner("Scanning markets..."):
                    try:
                        gen = GlobalSignalGenerator()
                        signals = gen.generate_signals(markets=quick_markets)

                        total = 0
                        for market, sigs in signals.items():
                            if sigs:
                                strong = [s for s in sigs if s.get('signal_status') == 'STRONG BUY']
                                buys = [s for s in sigs if s.get('signal_status') == 'BUY']
                                total += len(strong) + len(buys)

                                st.markdown(f"**{market}:** {len(strong)} STRONG BUY, {len(buys)} BUY")

                                for s in (strong + buys)[:3]:
                                    st.write(f"  • {s['symbol']}: Score {s.get('signal_score', 0)}, "
                                            f"Entry ${get_entry_price(s):,.2f}")

                        if total == 0:
                            st.info("No buy signals found")
                        else:
                            st.success(f"Found {total} signals! Go to 🎯 Signals page for details.")
                    except Exception as e:
                        st.error(f"Error: {e}")
            else:
                st.error("Signal generator not available")

    # Quick Trade Logger
    with st.expander("📋 Quick Trade Entry", expanded=False):
        st.write("Log a new trade:")

        qc1, qc2 = st.columns(2)

        with qc1:
            q_symbol = st.text_input("Symbol", "NVDA", key="q_symbol").upper()
            q_entry = st.number_input("Entry $", value=100.0, key="q_entry")
            q_shares = st.number_input("Shares", value=10, key="q_shares")

        with qc2:
            q_stop = st.number_input("Stop $", value=95.0, key="q_stop")
            q_target = st.number_input("Target $", value=110.0, key="q_target")
            q_setup = st.selectbox("Setup", ["PULLBACK", "BREAKOUT", "BOUNCE"], key="q_setup")

        if st.button("✅ Log Trade", key="quick_log"):
            if HAS_JOURNAL:
                try:
                    journal = TradeJournal()
                    trade_id = journal.log_entry(
                        symbol=q_symbol,
                        entry_price=q_entry,
                        shares=q_shares,
                        stop_loss=q_stop,
                        target_1=q_target,
                        target_2=q_target * 1.1,
                        setup_type=q_setup
                    )
                    st.success(f"✅ Trade #{trade_id} logged!")
                    st.balloons()
                except Exception as e:
                    st.error(f"Error: {e}")
            else:
                st.error("Trade journal not available")

    # Quick Performance View
    with st.expander("📊 Quick Performance", expanded=False):
        if HAS_JOURNAL:
            try:
                journal = TradeJournal()
                stats = journal.get_stats(30)

                if stats.get('total_trades', 0) > 0:
                    pc1, pc2, pc3, pc4 = st.columns(4)
                    pc1.metric("Trades", stats['total_trades'])
                    pc2.metric("Win Rate", f"{stats['win_rate']:.1f}%")
                    pc3.metric("Total P&L", f"${stats['total_pnl']:+,.2f}")
                    pc4.metric("Avg R", f"{stats['avg_r']:+.2f}")
                else:
                    st.info("No closed trades in last 30 days")
            except:
                st.info("No trade data yet")
        else:
            st.warning("trade_journal.py not found")

    # Refresh Data
    with st.expander("🔄 Refresh Data", expanded=False):
        st.write("Clear cached data and refresh:")
        if st.button("🔄 Clear Cache & Refresh", key="refresh_btn"):
            st.cache_data.clear()
            st.success("✅ Cache cleared! Data will refresh on next load.")


# ═══════════════════════════════════════════════════════════════
# PAGE: SIGNALS
# ═══════════════════════════════════════════════════════════════

elif st.session_state.current_page == "🎯 Signals":
    st.title("🎯 Trading Signals")

    # Market regime warning
    if 'regime' in comp:
        try:
            conditions = comp['regime'].analyze()
            if not conditions.can_trade_long:
                st.error(f"⚠️ MARKET WARNING: {conditions.recommendation}")
            elif conditions.position_mult < 1.0:
                st.warning(f"⚠️ {conditions.recommendation}")
        except:
            pass

    # Controls
    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        markets = st.multiselect(
            "Select Markets",
            ["US", "DE", "IN"],
            default=["US", "DE", "IN"],
            key="signal_markets"
        )

    with col2:
        signal_filter = st.selectbox(
            "Filter",
            ["All", "STRONG BUY", "BUY"],
            key="signal_filter"
        )

    with col3:
        min_score = st.slider("Min Score", 0, 100, 50, key="min_score")

    # Auto-trigger signals if coming from Quick Actions
    auto_generate = st.session_state.get('trigger_signals', False)
    if auto_generate:
        st.session_state.trigger_signals = False

    # Generate button
    generate_clicked = st.button("🚀 Generate Signals", type="primary", use_container_width=True)

    if generate_clicked or auto_generate:
        if 'signals' in comp:
            with st.spinner("Analyzing markets... This may take a minute."):
                try:
                    all_signals = comp['signals'].generate_signals(markets=markets)

                    total_found = 0

                    for market, market_signals in all_signals.items():
                        if not market_signals:
                            continue

                        # Apply filters
                        if signal_filter != "All":
                            market_signals = [s for s in market_signals
                                            if s.get('signal_status') == signal_filter]

                        market_signals = [s for s in market_signals
                                         if s.get('signal_score', 0) >= min_score]

                        if not market_signals:
                            continue

                        # Sort by score
                        market_signals.sort(key=lambda x: x.get('signal_score', 0), reverse=True)

                        flag = {"US": "🇺🇸", "DE": "🇩🇪", "IN": "🇮🇳"}.get(market, "🌐")
                        currency = {"US": "$", "DE": "€", "IN": "₹"}.get(market, "$")

                        st.markdown(f"### {flag} {market} - {len(market_signals)} signals")

                        total_found += len(market_signals)

                        # Display signals
                        for sig in market_signals[:10]:
                            status = sig.get('signal_status', 'N/A')
                            score = sig.get('signal_score', 0)
                            symbol = sig.get('symbol', 'N/A')

                            icon = "🟢" if status == "STRONG BUY" else "🟡"

                            with st.expander(f"{icon} {symbol} - {status} (Score: {score})"):
                                c1, c2, c3 = st.columns(3)

                                with c1:
                                    st.markdown("**📊 Current**")
                                    st.write(f"Price: {currency}{sig.get('current_price', 0):,.2f}")
                                    st.write(f"RSI: {sig.get('rsi', 0):.1f}")
                                    st.write(f"ADX: {sig.get('adx', 0):.1f}")

                                with c2:
                                    st.markdown("**💰 Trade Setup**")
                                    entry = get_entry_price(sig)
                                    st.write(f"Entry: {currency}{entry:,.2f}")
                                    st.write(f"Stop: {currency}{sig.get('stop_loss', 0):,.2f}")
                                    st.write(f"Target 1: {currency}{sig.get('target_1', 0):,.2f}")

                                with c3:
                                    st.markdown("**📈 Metrics**")
                                    rr = get_risk_reward(sig)
                                    st.write(f"R:R: {rr:.2f}:1")
                                    st.write(f"Setup: {sig.get('setup_type', 'N/A')}")

                                # Position size
                                if 'regime' in comp:
                                    mult = comp['regime'].analyze().position_mult
                                else:
                                    mult = 1.0

                                entry = get_entry_price(sig)
                                stop = sig.get('stop_loss', 0)

                                if entry > 0 and stop > 0 and stop < entry:
                                    risk_per_share = entry - stop
                                    risk_amount = ACCOUNT_SIZE * RISK_PER_TRADE * mult
                                    shares = int(risk_amount / risk_per_share)

                                    st.markdown("---")
                                    st.markdown(f"**💼 Position:** Buy **{shares}** shares = {currency}{shares * entry:,.2f}")

                        st.markdown("---")

                    if total_found == 0:
                        st.info("No signals matching criteria. Try adjusting filters.")
                    else:
                        st.success(f"✅ Found {total_found} signals")

                except Exception as e:
                    st.error(f"Error generating signals: {e}")
        else:
            st.error("Signal generator not available")
    else:
        st.info("👆 Click 'Generate Signals' to scan markets")


# ═══════════════════════════════════════════════════════════════
# PAGE: ANALYSIS
# ═══════════════════════════════════════════════════════════════

elif st.session_state.current_page == "📈 Analysis":
    st.title("📈 Stock Analysis")

    col1, col2 = st.columns([3, 1])

    with col1:
        symbol = st.text_input("Enter Symbol", value="NVDA").upper()

    with col2:
        st.write("")
        st.write("")
        if ".NS" in symbol:
            st.info("🇮🇳 India")
            currency = "₹"
        elif ".DE" in symbol:
            st.info("🇩🇪 Germany")
            currency = "€"
        else:
            st.info("🇺🇸 US")
            currency = "$"

    if st.button("🔍 Analyze", type="primary"):
        with st.spinner(f"Analyzing {symbol}..."):
            df = fetch_stock_data(symbol, "6mo")

            if df.empty:
                st.error(f"No data found for {symbol}")
            else:
                info = get_stock_info(symbol)

                if 'analyzer' in comp:
                    try:
                        result = comp['analyzer'].analyze_stock(df, symbol)
                    except Exception as e:
                        st.error(f"Analysis error: {e}")
                        result = {}
                else:
                    st.warning("Analyzer not available")
                    result = {}

                if result:
                    st.markdown(f"## {info.get('name', symbol)}")
                    st.caption(f"{info.get('sector', 'N/A')} | {info.get('industry', 'N/A')}")

                    status = result.get('signal_status', 'N/A')
                    if status == "STRONG BUY":
                        st.success(f"🟢 **{status}** - Score: {result.get('signal_score', 0)}/100")
                    elif status == "BUY":
                        st.warning(f"🟡 **{status}** - Score: {result.get('signal_score', 0)}/100")
                    else:
                        st.info(f"⚪ **{status}** - Score: {result.get('signal_score', 0)}/100")

                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("Price", f"{currency}{result.get('current_price', 0):,.2f}")
                    col2.metric("RSI", f"{result.get('rsi', 0):.1f}")
                    rr = get_risk_reward(result)
                    col3.metric("R:R", f"{rr:.2f}:1")
                    col4.metric("Setup", result.get('setup_type', 'N/A'))

                    st.markdown("---")

                    col1, col2 = st.columns(2)

                    with col1:
                        st.markdown("### 💰 Trade Setup")
                        entry = get_entry_price(result)
                        st.write(f"**Entry:** {currency}{entry:,.2f}")
                        st.write(f"**Stop Loss:** {currency}{result.get('stop_loss', 0):,.2f}")
                        st.write(f"**Target 1:** {currency}{result.get('target_1', 0):,.2f}")
                        st.write(f"**Target 2:** {currency}{result.get('target_2', 0):,.2f}")

                    with col2:
                        st.markdown("### 📊 Indicators")
                        st.write(f"**RSI:** {result.get('rsi', 0):.1f}")
                        st.write(f"**ADX:** {result.get('adx', 0):.1f}")
                        atr = result.get('atr_pct', result.get('atr_percent', 0))
                        st.write(f"**ATR%:** {atr:.2f}%")
                        trend = is_uptrend(result)
                        st.write(f"**Trend:** {'📈 BULLISH' if trend else '📉 BEARISH'}")


# ═══════════════════════════════════════════════════════════════
# PAGE: TRADE JOURNAL
# ═══════════════════════════════════════════════════════════════

elif st.session_state.current_page == "📋 Trade Journal":
    st.title("📋 Trade Journal")

    if not HAS_JOURNAL or 'journal' not in comp:
        st.error("❌ Trade Journal not available")
        st.code("Create trade_journal.py to enable this feature")
        st.stop()

    journal = comp['journal']

    tab1, tab2, tab3, tab4 = st.tabs(["📝 Log Entry", "📤 Log Exit", "📂 Open", "📜 History"])

    with tab1:
        st.subheader("Log New Trade Entry")

        col1, col2 = st.columns(2)

        with col1:
            entry_symbol = st.text_input("Symbol", "NVDA", key="j_symbol").upper()
            entry_price = st.number_input("Entry Price", value=100.0, step=0.01, key="j_entry")
            entry_shares = st.number_input("Shares", value=10, step=1, key="j_shares")
            entry_market = st.selectbox("Market", ["US", "DE", "IN"], key="j_market")

        with col2:
            entry_stop = st.number_input("Stop Loss", value=95.0, step=0.01, key="j_stop")
            entry_t1 = st.number_input("Target 1", value=110.0, step=0.01, key="j_t1")
            entry_t2 = st.number_input("Target 2", value=120.0, step=0.01, key="j_t2")
            entry_setup = st.selectbox("Setup", ["PULLBACK", "PULLBACK_BOUNCE", "BREAKOUT", "REVERSAL", "OTHER"], key="j_setup")

        entry_reason = st.text_area("Entry Reason", key="j_reason")

        regime_str = "UNKNOWN"
        if 'regime' in comp:
            try:
                regime_str = comp['regime'].analyze().regime.value
            except:
                pass

        if entry_price > 0 and entry_stop > 0 and entry_stop < entry_price:
            risk = (entry_price - entry_stop) * entry_shares
            rr = (entry_t1 - entry_price) / (entry_price - entry_stop) if entry_price > entry_stop else 0

            pc1, pc2, pc3 = st.columns(3)
            pc1.metric("Position Value", f"${entry_price * entry_shares:,.2f}")
            pc2.metric("Risk Amount", f"${risk:,.2f}")
            pc3.metric("R:R", f"{rr:.2f}:1")

        if st.button("✅ Log Entry", type="primary", key="btn_entry"):
            if entry_price > 0 and entry_shares > 0 and entry_stop > 0:
                try:
                    trade_id = journal.log_entry(
                        symbol=entry_symbol,
                        entry_price=entry_price,
                        shares=entry_shares,
                        stop_loss=entry_stop,
                        target_1=entry_t1,
                        target_2=entry_t2,
                        setup_type=entry_setup,
                        entry_reason=entry_reason,
                        market=entry_market,
                        market_regime=regime_str
                    )
                    st.success(f"✅ Trade #{trade_id} logged!")
                    st.balloons()
                except Exception as e:
                    st.error(f"Error: {e}")

    with tab2:
        st.subheader("Log Trade Exit")

        open_trades = journal.get_open_trades()

        if open_trades.empty:
            st.info("No open trades to close")
        else:
            trade_options = {f"#{row['id']} - {row['symbol']} @ ${row['entry_price']:.2f}": row['id']
                           for _, row in open_trades.iterrows()}

            selected = st.selectbox("Select Trade", list(trade_options.keys()))
            trade_id = trade_options[selected]

            trade = open_trades[open_trades['id'] == trade_id].iloc[0]

            st.info(f"Entry: ${trade['entry_price']:.2f} × {trade['shares']} shares | Stop: ${trade['stop_loss']:.2f}")

            col1, col2 = st.columns(2)

            with col1:
                exit_price = st.number_input("Exit Price", value=float(trade['entry_price']), step=0.01)
                exit_reason = st.selectbox("Exit Reason", [
                    "Target 1 Hit", "Target 2 Hit", "Stop Loss", "Trailing Stop", "Manual Exit"
                ])

            with col2:
                followed_plan = st.checkbox("Followed Plan?", value=True)
                exit_lessons = st.text_area("Lessons Learned")

            pnl = (exit_price - trade['entry_price']) * trade['shares']
            risk_per_share = trade['entry_price'] - trade['stop_loss']
            r_mult = (exit_price - trade['entry_price']) / risk_per_share if risk_per_share else 0

            pc1, pc2 = st.columns(2)
            pc1.metric("P&L", f"${pnl:+,.2f}")
            pc2.metric("R-Multiple", f"{r_mult:+.2f}R")

            if st.button("📤 Close Trade", type="primary"):
                try:
                    result = journal.log_exit(
                        trade_id=trade_id,
                        exit_price=exit_price,
                        exit_reason=exit_reason,
                        followed_plan=followed_plan,
                        lessons=exit_lessons
                    )

                    if result['pnl'] > 0:
                        st.success(f"✅ Win! P&L: ${result['pnl']:+,.2f}")
                        st.balloons()
                    else:
                        st.error(f"❌ Loss: ${result['pnl']:+,.2f}")

                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")

    with tab3:
        st.subheader("📂 Open Positions")

        open_trades = journal.get_open_trades()

        if open_trades.empty:
            st.info("No open positions")
        else:
            st.dataframe(open_trades, use_container_width=True, hide_index=True)

    with tab4:
        st.subheader("📜 Trade History")

        days = st.selectbox("Period", [7, 14, 30, 60, 90], index=2, key="hist_days")
        stats = journal.get_stats(days)

        if stats.get('total_trades', 0) == 0:
            st.info(f"No closed trades in last {days} days")
        else:
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Trades", stats['total_trades'])
            col2.metric("Win Rate", f"{stats['win_rate']:.1f}%")
            col3.metric("Total P&L", f"${stats['total_pnl']:+,.2f}")
            col4.metric("Profit Factor", f"{stats['profit_factor']:.2f}")

            st.markdown("---")

            setup_df = journal.get_stats_by_setup()
            if not setup_df.empty:
                st.subheader("By Setup Type")
                st.dataframe(setup_df, use_container_width=True, hide_index=True)


# ═══════════════════════════════════════════════════════════════
# PAGE: PERFORMANCE
# ═══════════════════════════════════════════════════════════════

elif st.session_state.current_page == "📊 Performance":
    st.title("📊 Performance Tracker")

    if not HAS_JOURNAL or 'journal' not in comp:
        st.error("Trade Journal required")
        st.stop()

    journal = comp['journal']

    # Monthly Progress
    st.subheader(f"📅 {datetime.now().strftime('%B %Y')} Progress")

    if 'tracker' in comp:
        try:
            p = comp['tracker'].get_monthly_progress()

            pct = min(p.get('progress_pct', 0), 100)
            st.progress(pct / 100)

            col1, col2, col3 = st.columns(3)
            col1.metric("Target", f"${p.get('target', 0):,.0f}")
            col2.metric("Current P&L", f"${p.get('current_pnl', 0):+,.2f}")
            col3.metric("Progress", f"{pct:.1f}%")

            col4, col5, col6 = st.columns(3)
            col4.metric("Remaining", f"${p.get('remaining', 0):,.2f}")
            col5.metric("Trading Days Left", p.get('trading_days_left', 0))
            col6.metric("Status", "✅ On Track" if p.get('on_track') else "⚠️ Behind")

        except:
            st.info("Start trading to see progress")

    st.markdown("---")

    # Performance Stats
    st.subheader("📈 Statistics")

    period = st.selectbox("Period", [7, 14, 30, 60, 90], index=2, key="perf_period")
    stats = journal.get_stats(period)

    if stats.get('total_trades', 0) == 0:
        st.info(f"No closed trades in last {period} days")
    else:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total P&L", f"${stats['total_pnl']:+,.2f}")
        col2.metric("Win Rate", f"{stats['win_rate']:.1f}%")
        col3.metric("Profit Factor", f"{stats['profit_factor']:.2f}")
        col4.metric("Avg R", f"{stats['avg_r']:+.2f}")

        col5, col6, col7, col8 = st.columns(4)
        col5.metric("Trades", stats['total_trades'])
        col6.metric("Winners", stats['wins'])
        col7.metric("Losers", stats['losses'])
        col8.metric("Avg Hold", f"{stats['avg_hold']:.1f} days")


# ═══════════════════════════════════════════════════════════════
# PAGE: SCANNER
# ═══════════════════════════════════════════════════════════════

elif st.session_state.current_page == "🔍 Scanner":
    st.title("🔍 Stock Scanner")
    st.info("Use the 🎯 Signals page for market scanning")

    if st.button("Go to Signals", type="primary"):
        st.session_state.current_page = "🎯 Signals"
        st.rerun()


# ═══════════════════════════════════════════════════════════════
# PAGE: BACKTEST
# ═══════════════════════════════════════════════════════════════

elif st.session_state.current_page == "📉 Backtest":
    st.title("📉 Strategy Backtester")

    st.code("""
# Run from command line:
python backtester.py compare
python backtester.py --market US
python backtester.py --symbol NVDA --period 1y
    """, language="bash")


# ═══════════════════════════════════════════════════════════════
# PAGE: CALCULATOR
# ═══════════════════════════════════════════════════════════════

elif st.session_state.current_page == "📐 Calculator":
    st.title("📐 Position Size Calculator")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Trade Details")
        currency = st.selectbox("Currency", ["USD ($)", "EUR (€)", "INR (₹)"])
        entry = st.number_input("Entry Price", value=100.0, step=0.01)
        stop = st.number_input("Stop Loss", value=95.0, step=0.01)
        target = st.number_input("Target", value=110.0, step=0.01)

    with col2:
        st.subheader("Account")
        account = st.number_input("Account Size", value=ACCOUNT_SIZE, step=1000)
        risk_pct = st.slider("Risk %", 0.5, 3.0, RISK_PER_TRADE * 100, 0.1)

        if 'regime' in comp:
            try:
                mult = comp['regime'].analyze().position_mult
                st.info(f"Regime adjustment: {mult*100:.0f}%")
                effective_risk = risk_pct * mult
            except:
                effective_risk = risk_pct
        else:
            effective_risk = risk_pct

    if st.button("📊 Calculate", type="primary"):
        if stop >= entry:
            st.error("Stop must be below entry")
        else:
            risk_per_share = entry - stop
            max_risk = account * (effective_risk / 100)
            shares = int(max_risk / risk_per_share)
            position_value = shares * entry

            rr_ratio = (target - entry) / risk_per_share
            profit = (target - entry) * shares

            curr_sym = {"USD ($)": "$", "EUR (€)": "€", "INR (₹)": "₹"}.get(currency, "$")

            st.markdown("---")

            col1, col2, col3 = st.columns(3)
            col1.metric("Shares", f"{shares:,}")
            col2.metric("Position Value", f"{curr_sym}{position_value:,.2f}")
            col3.metric("Risk Amount", f"{curr_sym}{max_risk:,.2f}")

            col4, col5, col6 = st.columns(3)
            col4.metric("R:R Ratio", f"{rr_ratio:.2f}:1")
            col5.metric("Potential Profit", f"{curr_sym}{profit:,.2f}")
            col6.metric("Risk %", f"{effective_risk:.2f}%")

            st.success(f"**Buy {shares} shares** at {curr_sym}{entry:.2f}, stop at {curr_sym}{stop:.2f}")


# ═══════════════════════════════════════════════════════════════
# PAGE: SETTINGS
# ═══════════════════════════════════════════════════════════════

elif st.session_state.current_page == "⚙️ Settings":
    st.title("⚙️ Settings")

    st.subheader("📋 Configuration")
    st.write(f"**Account Size:** ${ACCOUNT_SIZE:,}")
    st.write(f"**Monthly Target:** {MONTHLY_TARGET*100:.1f}%")
    st.write(f"**Risk per Trade:** {RISK_PER_TRADE*100:.1f}%")
    st.write(f"**Max Positions:** {MAX_POSITIONS}")

    st.caption("Edit config.py to change these settings")

    st.markdown("---")

    st.subheader("🔧 System Status")

    modules = [
        ("Data Fetcher", HAS_FETCHER),
        ("Analyzer", HAS_ANALYZER),
        ("Signals", HAS_SIGNALS),
        ("Trade Journal", HAS_JOURNAL),
        ("Market Regime", HAS_REGIME),
        ("Performance", HAS_TRACKER),
        ("yfinance", HAS_YFINANCE),
    ]

    for name, status in modules:
        st.write(f"{'✅' if status else '❌'} {name}")

    st.markdown("---")

    st.subheader("🔄 Maintenance")

    if st.button("Clear Cache"):
        st.cache_data.clear()
        st.cache_resource.clear()
        st.success("Cache cleared!")
        st.rerun()


# ═══════════════════════════════════════════════════════════════
# FOOTER
# ═══════════════════════════════════════════════════════════════

st.sidebar.markdown("---")
st.sidebar.caption(f"Updated: {datetime.now().strftime('%H:%M')}")
