#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════════
ENHANCED TRADING DASHBOARD - Complete Version
═══════════════════════════════════════════════════════════════════════════════════

Features:
- Market Regime Analysis
- Technical Signals
- Fundamental Analysis
- Combined (Tech + Fund) Analysis
- Earnings Calendar
- Insider Activity Tracking
- Trade Journal
- Performance Tracking
- Portfolio Management

Run: streamlit run dashboard.py
═══════════════════════════════════════════════════════════════════════════════════
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import time

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ═══════════════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="Trading Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ═══════════════════════════════════════════════════════════════════════════════
# IMPORTS WITH ERROR HANDLING
# ═══════════════════════════════════════════════════════════════════════════════

# Data
try:
    import yfinance as yf
    HAS_YFINANCE = True
except ImportError:
    HAS_YFINANCE = False

# Core Modules
try:
    from global_signal_generator import GlobalSignalGenerator
    HAS_SIGNALS = True
except ImportError:
    HAS_SIGNALS = False

try:
    from technical_analyzer import TechnicalAnalyzer
    HAS_ANALYZER = True
except ImportError:
    HAS_ANALYZER = False

try:
    from market_regime import MarketRegimeFilter
    HAS_REGIME = True
except ImportError:
    HAS_REGIME = False

try:
    from trade_journal import TradeJournal
    HAS_JOURNAL = True
except ImportError:
    HAS_JOURNAL = False

try:
    from performance_tracker import PerformanceTracker
    HAS_TRACKER = True
except ImportError:
    HAS_TRACKER = False

try:
    from market_config import MARKETS, get_market_status
    HAS_MARKETS = True
except ImportError:
    HAS_MARKETS = False
    def get_market_status():
        return {}

# Fundamental Analysis
try:
    from fundamental_analyzer import FundamentalAnalyzer
    HAS_FUNDAMENTALS = True
except ImportError:
    HAS_FUNDAMENTALS = False

try:
    from combined_analyzer import CombinedAnalyzer
    HAS_COMBINED = True
except ImportError:
    HAS_COMBINED = False

try:
    from fundamental_screener import FundamentalScreener, ScreenerPreset
    HAS_SCREENER = True
except ImportError:
    HAS_SCREENER = False

# Earnings & Insider
try:
    from earnings_calendar import EarningsCalendar
    HAS_EARNINGS = True
except ImportError:
    HAS_EARNINGS = False

try:
    from insider_tracker import InsiderTracker
    HAS_INSIDER = True
except ImportError:
    HAS_INSIDER = False

# Config
try:
    import config
    ACCOUNT_SIZE = getattr(config, 'ACCOUNT_SIZE', 50000)
    RISK_PER_TRADE = getattr(config, 'RISK_PER_TRADE', 0.015)
except ImportError:
    ACCOUNT_SIZE = 50000
    RISK_PER_TRADE = 0.015


# ═══════════════════════════════════════════════════════════════════════════════
# DEFAULT WATCHLISTS
# ═══════════════════════════════════════════════════════════════════════════════

WATCHLIST_US = [
    "NVDA", "AMD", "AAPL", "MSFT", "GOOGL", "META", "AMZN", "TSLA",
    "AVGO", "CRM", "NFLX", "ADBE", "ORCL", "INTC", "QCOM", "MU"
]

WATCHLIST_DE = [
    "SAP.DE", "SIE.DE", "ALV.DE", "DTE.DE", "BAS.DE", "BAYN.DE"
]

WATCHLIST_IN = [
    "TCS.NS", "RELIANCE.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS"
]


# ═══════════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def get_current_price(symbol: str) -> float:
    """Get current price for a symbol"""
    if not HAS_YFINANCE:
        return 0
    try:
        ticker = yf.Ticker(symbol)
        return ticker.fast_info.get('lastPrice', 0)
    except:
        return 0


def create_price_chart(symbol: str, period: str = "6mo") -> go.Figure:
    """Create candlestick chart with indicators"""
    if not HAS_YFINANCE:
        return go.Figure()

    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period)

        if df.empty:
            return go.Figure()

        # Calculate EMAs
        df['EMA20'] = df['Close'].ewm(span=20).mean()
        df['EMA50'] = df['Close'].ewm(span=50).mean()

        fig = go.Figure()

        # Candlesticks
        fig.add_trace(go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name='Price'
        ))

        # EMAs
        fig.add_trace(go.Scatter(
            x=df.index, y=df['EMA20'],
            mode='lines', name='EMA20',
            line=dict(color='blue', width=1)
        ))

        fig.add_trace(go.Scatter(
            x=df.index, y=df['EMA50'],
            mode='lines', name='EMA50',
            line=dict(color='orange', width=1)
        ))

        fig.update_layout(
            title=f"{symbol} Price Chart",
            yaxis_title="Price",
            xaxis_rangeslider_visible=False,
            height=400
        )

        return fig
    except:
        return go.Figure()


def calculate_position_size(entry: float, stop: float, account: float = ACCOUNT_SIZE) -> dict:
    """Calculate position size"""
    if entry <= 0 or stop <= 0 or stop >= entry:
        return {"shares": 0, "value": 0, "risk": 0}

    risk_per_share = entry - stop
    risk_amount = account * RISK_PER_TRADE
    shares = int(risk_amount / risk_per_share)
    value = shares * entry

    return {
        "shares": shares,
        "value": value,
        "risk": risk_amount
    }


# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════════

st.sidebar.title("📈 Trading Dashboard")

# Navigation
pages = [
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
    "⚙️ Settings"
]

selected_page = st.sidebar.selectbox("Navigate", pages)

# System Status
st.sidebar.markdown("---")
st.sidebar.subheader("System Status")

status_items = [
    ("Signals", HAS_SIGNALS),
    ("Fundamentals", HAS_FUNDAMENTALS),
    ("Combined", HAS_COMBINED),
    ("Earnings", HAS_EARNINGS),
    ("Insider", HAS_INSIDER),
    ("Screener", HAS_SCREENER),
    ("Regime", HAS_REGIME),
    ("Journal", HAS_JOURNAL),
]

for name, available in status_items:
    emoji = "✅" if available else "❌"
    st.sidebar.text(f"{emoji} {name}")


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: OVERVIEW
# ═══════════════════════════════════════════════════════════════════════════════

if selected_page == "🏠 Overview":
    st.title("🏠 Trading Dashboard Overview")

    # Market Status Row
    col1, col2, col3, col4 = st.columns(4)

    # SPY
    if HAS_YFINANCE:
        try:
            spy = yf.Ticker("SPY")
            spy_price = spy.fast_info.get('lastPrice', 0)
            spy_change = spy.fast_info.get('regularMarketChangePercent', 0)
            col1.metric("SPY", f"${spy_price:.2f}", f"{spy_change:.2f}%")
        except:
            col1.metric("SPY", "N/A", "")

        try:
            vix = yf.Ticker("^VIX")
            vix_price = vix.fast_info.get('lastPrice', 0)
            col2.metric("VIX", f"{vix_price:.2f}", "Fear Index")
        except:
            col2.metric("VIX", "N/A", "")

        try:
            qqq = yf.Ticker("QQQ")
            qqq_price = qqq.fast_info.get('lastPrice', 0)
            qqq_change = qqq.fast_info.get('regularMarketChangePercent', 0)
            col3.metric("QQQ", f"${qqq_price:.2f}", f"{qqq_change:.2f}%")
        except:
            col3.metric("QQQ", "N/A", "")

    # Market Regime
    if HAS_REGIME:
        try:
            mrf = MarketRegimeFilter()
            conditions = mrf.analyze()
            regime_color = "green" if "BULL" in conditions.regime.value else "red" if "BEAR" in conditions.regime.value else "orange"
            col4.metric("Regime", conditions.regime.value, f"{conditions.position_mult*100:.0f}% size")
        except:
            col4.metric("Regime", "Unknown", "")
    else:
        col4.metric("Regime", "N/A", "")

    st.markdown("---")

    # Two columns layout
    left_col, right_col = st.columns(2)

    with left_col:
        st.subheader("📊 Quick Stats")

        # Open positions
        if HAS_JOURNAL:
            try:
                journal = TradeJournal()
                open_trades = journal.get_open_trades()
                st.metric("Open Positions", len(open_trades))
            except:
                st.metric("Open Positions", "N/A")

        # Today's signals
        if HAS_SIGNALS:
            try:
                gen = GlobalSignalGenerator()
                signals = gen.generate_signals(markets=["US"])
                us_signals = signals.get("US", [])
                strong_buys = len([s for s in us_signals if s.get('signal_status') == 'STRONG BUY'])
                st.metric("US Strong Buys", strong_buys)
            except:
                st.metric("US Strong Buys", "N/A")

    with right_col:
        st.subheader("📅 Upcoming Events")

        if HAS_EARNINGS:
            try:
                ec = EarningsCalendar()
                upcoming = ec.scan_upcoming_earnings(WATCHLIST_US[:10], days_ahead=7)

                if not upcoming.empty:
                    for _, row in upcoming.head(5).iterrows():
                        st.text(f"📅 {row['Symbol']} - {row['Earnings Date']}")
                else:
                    st.info("No upcoming earnings in watchlist")
            except:
                st.info("Could not load earnings")
        else:
            st.warning("Earnings calendar not available")

    # Market Status
    st.markdown("---")
    st.subheader("🌍 Market Status")

    if HAS_MARKETS:
        status = get_market_status()
        cols = st.columns(3)

        markets_info = [
            ("🇺🇸 US", status.get("US", "Unknown")),
            ("🇩🇪 Germany", status.get("DE", "Unknown")),
            ("🇮🇳 India", status.get("IN", "Unknown"))
        ]

        for i, (name, stat) in enumerate(markets_info):
            cols[i].metric(name, stat)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: MARKET REGIME
# ═══════════════════════════════════════════════════════════════════════════════

elif selected_page == "📊 Market Regime":
    st.title("📊 Market Regime Analysis")

    if not HAS_REGIME:
        st.error("Market regime module not available. Create market_regime.py")
        st.stop()

    try:
        mrf = MarketRegimeFilter()
        conditions = mrf.analyze()

        # Regime Status
        col1, col2, col3, col4 = st.columns(4)

        regime_color = "green" if "BULL" in conditions.regime.value else "red" if "BEAR" in conditions.regime.value else "orange"

        col1.metric("Current Regime", conditions.regime.value)
        col2.metric("SPY Price", f"${conditions.spy_price:.2f}")
        col3.metric("VIX Level", f"{conditions.vix_level:.1f}")
        col4.metric("Position Size", f"{conditions.position_mult*100:.0f}%")

        st.markdown("---")

        # Details
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📈 SPY Analysis")
            st.write(f"**1-Day Change:** {conditions.spy_change_1d:+.2f}%")
            st.write(f"**5-Day Change:** {conditions.spy_change_5d:+.2f}%")
            st.write(f"**Above 50 EMA:** {'Yes ✅' if conditions.above_ema50 else 'No ❌'}")
            st.write(f"**Above 200 EMA:** {'Yes ✅' if conditions.above_ema200 else 'No ❌'}")

            # SPY Chart
            fig = create_price_chart("SPY", "3mo")
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("😰 VIX Analysis")

            if conditions.vix_level < 15:
                st.success("Low Fear - Bullish")
            elif conditions.vix_level < 20:
                st.info("Normal - Neutral")
            elif conditions.vix_level < 30:
                st.warning("Elevated - Caution")
            else:
                st.error("High Fear - Defensive")

            # VIX Chart
            fig = create_price_chart("^VIX", "3mo")
            st.plotly_chart(fig, use_container_width=True)

        # Trading Rules
        st.markdown("---")
        st.subheader("📋 Trading Rules Based on Regime")

        if conditions.can_trade_long:
            st.success("✅ Long trades allowed")
        else:
            st.error("❌ Avoid new long positions")

        st.write(f"""
        **Current Rules:**
        - Position Size: {conditions.position_mult*100:.0f}% of normal
        - Max Trades Per Day: {2 if conditions.position_mult >= 0.75 else 1}
        - Risk Per Trade: {RISK_PER_TRADE * conditions.position_mult * 100:.2f}%
        """)

    except Exception as e:
        st.error(f"Error: {e}")


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: SIGNALS
# ═══════════════════════════════════════════════════════════════════════════════

elif selected_page == "🎯 Signals":
    st.title("🎯 Trading Signals")

    if not HAS_SIGNALS:
        st.error("Signal generator not available")
        st.stop()

    # Market Selection
    markets = st.multiselect(
        "Select Markets",
        ["US", "DE", "IN"],
        default=["US"]
    )

    if st.button("🔄 Generate Signals", type="primary"):
        with st.spinner("Generating signals..."):
            try:
                gen = GlobalSignalGenerator()
                signals = gen.generate_signals(markets=markets)

                for market, sigs in signals.items():
                    st.subheader(f"{'🇺🇸' if market == 'US' else '🇩🇪' if market == 'DE' else '🇮🇳'} {market} Signals")

                    if not sigs:
                        st.info(f"No signals for {market}")
                        continue

                    # Filter by signal type
                    strong_buys = [s for s in sigs if s.get('signal_status') == 'STRONG BUY']
                    buys = [s for s in sigs if s.get('signal_status') == 'BUY']

                    col1, col2 = st.columns(2)
                    col1.metric("Strong Buys", len(strong_buys))
                    col2.metric("Buys", len(buys))

                    # Display signals
                    all_actionable = strong_buys + buys

                    if all_actionable:
                        df = pd.DataFrame([
                            {
                                "Symbol": s.get('symbol'),
                                "Signal": s.get('signal_status'),
                                "Score": s.get('signal_score', 0),
                                "Price": f"${s.get('current_price', 0):.2f}",
                                "Entry": f"${s.get('ideal_entry', s.get('entry', 0)):.2f}",
                                "Stop": f"${s.get('stop_loss', 0):.2f}",
                                "Target": f"${s.get('target_1', 0):.2f}",
                                "R:R": f"{s.get('risk_reward', 0):.1f}",
                            }
                            for s in all_actionable[:20]
                        ])

                        st.dataframe(df, use_container_width=True, hide_index=True)

                    st.markdown("---")

            except Exception as e:
                st.error(f"Error: {e}")


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: FUNDAMENTALS
# ═══════════════════════════════════════════════════════════════════════════════

elif selected_page == "📈 Fundamentals":
    st.title("📈 Fundamental Analysis")

    if not HAS_FUNDAMENTALS:
        st.error("Fundamental analyzer not available. Create fundamental_analyzer.py")
        st.stop()

    fa = FundamentalAnalyzer()

    tab1, tab2, tab3 = st.tabs(["🔍 Single Stock", "📊 Compare Stocks", "📋 Quick Scan"])

    # Tab 1: Single Stock Analysis
    with tab1:
        st.subheader("Single Stock Analysis")

        symbol = st.text_input("Enter Symbol", "NVDA", key="fund_single").upper()

        if st.button("📊 Analyze", key="fund_analyze_btn"):
            with st.spinner(f"Analyzing {symbol}..."):
                try:
                    data = fa.analyze(symbol)

                    if data:
                        # Header
                        st.markdown(f"### {data.name}")
                        st.caption(f"{data.sector} | {data.industry}")

                        # Overall Score
                        col1, col2, col3, col4 = st.columns(4)
                        col1.metric("Overall Score", f"{data.overall_score}/100")
                        col2.metric("Market Cap", f"${data.market_cap/1e9:.2f}B" if data.market_cap > 1e9 else f"${data.market_cap/1e6:.0f}M")
                        col3.metric("P/E Ratio", f"{data.pe_ratio:.2f}" if data.pe_ratio else "N/A")
                        col4.metric("Dividend Yield", f"{data.dividend_yield:.2f}%")

                        st.markdown("---")

                        # Score Breakdown
                        st.subheader("Score Breakdown")

                        score_cols = st.columns(5)
                        scores = [
                            ("Valuation", data.valuation_score),
                            ("Profitability", data.profitability_score),
                            ("Growth", data.growth_score),
                            ("Health", data.health_score),
                            ("Quality", data.quality_score),
                        ]

                        for i, (name, score) in enumerate(scores):
                            color = "green" if score >= 60 else "orange" if score >= 40 else "red"
                            score_cols[i].metric(name, f"{score}/100")

                        st.markdown("---")

                        # Detailed Metrics
                        col1, col2 = st.columns(2)

                        with col1:
                            st.subheader("📈 Valuation")
                            st.write(f"P/E Ratio: {data.pe_ratio:.2f}")
                            st.write(f"Forward P/E: {data.forward_pe:.2f}")
                            st.write(f"PEG Ratio: {data.peg_ratio:.2f}")
                            st.write(f"P/B Ratio: {data.pb_ratio:.2f}")
                            st.write(f"EV/EBITDA: {data.ev_to_ebitda:.2f}")
                            st.write(f"FCF Yield: {data.fcf_yield:.2f}%")

                            st.subheader("🚀 Growth")
                            st.write(f"Revenue Growth: {data.revenue_growth:.1f}%")
                            st.write(f"Earnings Growth: {data.earnings_growth:.1f}%")

                        with col2:
                            st.subheader("💰 Profitability")
                            st.write(f"Profit Margin: {data.profit_margin:.1f}%")
                            st.write(f"Operating Margin: {data.operating_margin:.1f}%")
                            st.write(f"Gross Margin: {data.gross_margin:.1f}%")
                            st.write(f"ROE: {data.roe:.1f}%")
                            st.write(f"ROA: {data.roa:.1f}%")

                            st.subheader("🏦 Financial Health")
                            st.write(f"Current Ratio: {data.current_ratio:.2f}")
                            st.write(f"Debt/Equity: {data.debt_to_equity:.1f}")
                            st.write(f"Interest Coverage: {data.interest_coverage:.1f}")

                        # Analyst Info
                        st.markdown("---")
                        st.subheader("📊 Analyst Opinion")

                        col1, col2, col3 = st.columns(3)
                        col1.metric("Rating", data.analyst_rating.upper() if data.analyst_rating else "N/A")
                        col2.metric("Target Price", f"${data.target_price_mean:.2f}" if data.target_price_mean else "N/A")
                        col3.metric("Upside", f"{data.upside_potential:.1f}%" if data.upside_potential else "N/A")

                    else:
                        st.error(f"Could not analyze {symbol}")

                except Exception as e:
                    st.error(f"Error: {e}")

    # Tab 2: Compare Stocks
    with tab2:
        st.subheader("Compare Stocks")

        symbols_text = st.text_area(
            "Enter symbols (one per line)",
            "NVDA\nAMD\nINTC\nAVGO",
            key="fund_compare"
        )

        if st.button("📊 Compare", key="fund_compare_btn"):
            symbols = [s.strip().upper() for s in symbols_text.split("\n") if s.strip()]

            if len(symbols) >= 2:
                with st.spinner(f"Comparing {len(symbols)} stocks..."):
                    try:
                        df = fa.quick_scan(symbols)

                        if not df.empty:
                            st.dataframe(df, use_container_width=True, hide_index=True)

                            # Highlight best
                            best = df.loc[df['Overall'].idxmax()]
                            st.success(f"🏆 Best Overall: **{best['Symbol']}** (Score: {best['Overall']})")
                        else:
                            st.error("Could not compare stocks")
                    except Exception as e:
                        st.error(f"Error: {e}")
            else:
                st.warning("Enter at least 2 symbols")

    # Tab 3: Quick Scan
    with tab3:
        st.subheader("Quick Scan Watchlist")

        watchlist_choice = st.selectbox(
            "Select Watchlist",
            ["US Tech", "German DAX", "Indian Nifty", "Custom"],
            key="fund_watchlist"
        )

        if watchlist_choice == "US Tech":
            scan_symbols = WATCHLIST_US
        elif watchlist_choice == "German DAX":
            scan_symbols = WATCHLIST_DE
        elif watchlist_choice == "Indian Nifty":
            scan_symbols = WATCHLIST_IN
        else:
            custom = st.text_area("Enter symbols (one per line)", "AAPL\nMSFT\nGOOGL")
            scan_symbols = [s.strip().upper() for s in custom.split("\n") if s.strip()]

        if st.button("🔍 Scan", key="fund_scan_btn"):
            with st.spinner(f"Scanning {len(scan_symbols)} stocks..."):
                try:
                    df = fa.quick_scan(scan_symbols)

                    if not df.empty:
                        st.dataframe(df, use_container_width=True, hide_index=True)

                        # Top 3
                        st.subheader("🏆 Top 3 by Fundamental Score")
                        for _, row in df.head(3).iterrows():
                            st.write(f"**{row['Symbol']}** - Overall: {row['Overall']}/100, Quality: {row['Quality']}/100")
                    else:
                        st.error("Could not scan stocks")
                except Exception as e:
                    st.error(f"Error: {e}")


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: COMBINED ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════════

elif selected_page == "🔀 Combined Analysis":
    st.title("🔀 Combined Technical + Fundamental Analysis")

    if not HAS_COMBINED:
        st.error("Combined analyzer not available. Create combined_analyzer.py")
        st.stop()

    ca = CombinedAnalyzer()

    tab1, tab2 = st.tabs(["🔍 Single Stock", "📊 Scan Watchlist"])

    # Tab 1: Single Stock
    with tab1:
        st.subheader("Combined Analysis")

        symbol = st.text_input("Enter Symbol", "NVDA", key="comb_single").upper()

        if st.button("🎯 Analyze", key="comb_analyze_btn", type="primary"):
            with st.spinner(f"Analyzing {symbol}..."):
                try:
                    analysis = ca.analyze(symbol)

                    if analysis:
                        # Header with quality badge
                        quality_colors = {"A+": "green", "A": "green", "B": "orange", "C": "orange", "D": "red"}

                        st.markdown(f"### {analysis.name}")
                        st.markdown(f"**Trade Quality: {analysis.trade_quality}** | Combined Score: {analysis.combined_score}/100")

                        # Combined signal
                        if "STRONG BUY" in analysis.combined_signal:
                            st.success(f"🟢 {analysis.combined_signal}")
                        elif "BUY" in analysis.combined_signal:
                            st.info(f"🟡 {analysis.combined_signal}")
                        elif "CAUTION" in analysis.combined_signal:
                            st.warning(f"🟠 {analysis.combined_signal}")
                        else:
                            st.warning(f"⚪ {analysis.combined_signal}")

                        st.info(analysis.recommendation)

                        st.markdown("---")

                        # Scores
                        col1, col2, col3 = st.columns(3)
                        col1.metric("Combined", f"{analysis.combined_score}/100")
                        col2.metric("Technical", f"{analysis.technical_score}/100")
                        col3.metric("Fundamental", f"{analysis.fundamental_score}/100")

                        st.markdown("---")

                        # Details
                        col1, col2 = st.columns(2)

                        with col1:
                            st.subheader("📈 Technical")
                            st.write(f"Signal: {analysis.technical_signal}")
                            st.write(f"Setup: {analysis.setup_type}")
                            st.write(f"RSI: {analysis.rsi:.1f}")
                            st.write(f"Trend: {analysis.trend}")

                        with col2:
                            st.subheader("📊 Fundamental")
                            st.write(f"P/E: {analysis.pe_ratio:.1f}")
                            st.write(f"ROE: {analysis.roe:.1f}%")
                            st.write(f"Revenue Growth: {analysis.revenue_growth:.1f}%")
                            st.write(f"Debt/Equity: {analysis.debt_to_equity:.1f}")

                        st.markdown("---")

                        # Trade Levels
                        st.subheader("💰 Trade Setup")

                        col1, col2, col3, col4 = st.columns(4)
                        col1.metric("Entry", f"${analysis.entry_price:.2f}")
                        col2.metric("Stop", f"${analysis.stop_loss:.2f}")
                        col3.metric("Target 1", f"${analysis.target_1:.2f}")
                        col4.metric("Target 2", f"${analysis.target_2:.2f}")

                        # Position sizing
                        pos = calculate_position_size(analysis.entry_price, analysis.stop_loss)

                        if pos['shares'] > 0:
                            st.subheader("💼 Position Sizing")
                            st.write(f"Shares: {pos['shares']}")
                            st.write(f"Position Value: ${pos['value']:,.2f}")
                            st.write(f"Risk Amount: ${pos['risk']:.2f}")

                        # Chart
                        st.subheader("📈 Price Chart")
                        fig = create_price_chart(symbol)
                        st.plotly_chart(fig, use_container_width=True)

                    else:
                        st.error(f"Could not analyze {symbol}")

                except Exception as e:
                    st.error(f"Error: {e}")

    # Tab 2: Scan Watchlist
    with tab2:
        st.subheader("Scan Watchlist for Quality Setups")

        col1, col2 = st.columns(2)

        with col1:
            watchlist_choice = st.selectbox(
                "Select Watchlist",
                ["US Tech", "Custom"],
                key="comb_watchlist"
            )

            if watchlist_choice == "US Tech":
                scan_symbols = WATCHLIST_US
            else:
                custom = st.text_area("Enter symbols", "NVDA\nAMD\nAAPL")
                scan_symbols = [s.strip().upper() for s in custom.split("\n") if s.strip()]

        with col2:
            min_quality = st.selectbox(
                "Minimum Quality",
                ["A+", "A", "B", "C"],
                index=2,
                key="comb_quality"
            )

        if st.button("🔍 Scan for Quality Setups", key="comb_scan_btn", type="primary"):
            with st.spinner(f"Scanning {len(scan_symbols)} stocks..."):
                try:
                    results = []
                    progress = st.progress(0)

                    for i, symbol in enumerate(scan_symbols):
                        try:
                            analysis = ca.analyze(symbol)

                            if analysis:
                                quality_order = {"A+": 5, "A": 4, "B": 3, "C": 2, "D": 1}
                                min_order = quality_order.get(min_quality, 3)

                                if quality_order.get(analysis.trade_quality, 0) >= min_order:
                                    results.append({
                                        "Symbol": analysis.symbol,
                                        "Quality": analysis.trade_quality,
                                        "Combined": analysis.combined_score,
                                        "Technical": analysis.technical_score,
                                        "Fundamental": analysis.fundamental_score,
                                        "Signal": analysis.combined_signal[:30],
                                        "Entry": f"${analysis.entry_price:.2f}",
                                        "Stop": f"${analysis.stop_loss:.2f}",
                                        "Target": f"${analysis.target_1:.2f}",
                                    })
                        except:
                            continue

                        progress.progress((i + 1) / len(scan_symbols))

                    progress.empty()

                    if results:
                        df = pd.DataFrame(results)
                        df = df.sort_values("Combined", ascending=False)

                        st.success(f"Found {len(results)} quality setups!")
                        st.dataframe(df, use_container_width=True, hide_index=True)

                        # Top pick
                        if len(results) > 0:
                            top = df.iloc[0]
                            st.subheader(f"🏆 Top Pick: {top['Symbol']}")
                            st.write(f"Quality: {top['Quality']} | Combined Score: {top['Combined']}")
                            st.write(f"Signal: {top['Signal']}")
                    else:
                        st.warning("No stocks passed the quality filter")

                except Exception as e:
                    st.error(f"Error: {e}")


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: EARNINGS CALENDAR
# ═══════════════════════════════════════════════════════════════════════════════

elif selected_page == "📅 Earnings Calendar":
    st.title("📅 Earnings Calendar")

    if not HAS_EARNINGS:
        st.error("Earnings calendar not available. Create earnings_calendar.py")
        st.stop()

    ec = EarningsCalendar()

    tab1, tab2, tab3 = st.tabs(["📅 Upcoming Earnings", "🔍 Check Stock", "📊 Earnings Analysis"])

    # Tab 1: Upcoming Earnings
    with tab1:
        st.subheader("Upcoming Earnings")

        col1, col2 = st.columns(2)

        with col1:
            watchlist_choice = st.selectbox(
                "Select Watchlist",
                ["US Tech", "All Watchlist", "Custom"],
                key="earn_watchlist"
            )

            if watchlist_choice == "US Tech":
                scan_symbols = WATCHLIST_US
            elif watchlist_choice == "All Watchlist":
                scan_symbols = WATCHLIST_US + WATCHLIST_DE + WATCHLIST_IN
            else:
                custom = st.text_area("Enter symbols", "NVDA\nAMD\nAAPL")
                scan_symbols = [s.strip().upper() for s in custom.split("\n") if s.strip()]

        with col2:
            days_ahead = st.slider("Days Ahead", 7, 60, 21, key="earn_days")

        if st.button("📅 Scan Earnings", key="earn_scan_btn", type="primary"):
            with st.spinner("Scanning earnings..."):
                try:
                    df = ec.scan_upcoming_earnings(scan_symbols, days_ahead)

                    if not df.empty:
                        # This week warning
                        this_week = df[df['Days Until'] <= 7]

                        if not this_week.empty:
                            st.warning(f"⚠️ {len(this_week)} stocks have earnings THIS WEEK!")
                            st.dataframe(this_week, use_container_width=True, hide_index=True)

                        # All upcoming
                        st.subheader(f"All Upcoming Earnings ({len(df)} stocks)")
                        st.dataframe(df, use_container_width=True, hide_index=True)
                    else:
                        st.success("No upcoming earnings in selected watchlist")

                except Exception as e:
                    st.error(f"Error: {e}")

    # Tab 2: Check Single Stock
    with tab2:
        st.subheader("Check Stock Earnings")

        symbol = st.text_input("Enter Symbol", "NVDA", key="earn_single").upper()

        if st.button("📅 Check Earnings", key="earn_check_btn"):
            with st.spinner(f"Checking {symbol}..."):
                try:
                    analysis = ec.get_full_earnings_analysis(symbol)

                    st.markdown(f"### {analysis['name']}")

                    col1, col2, col3 = st.columns(3)
                    col1.metric("Next Earnings", analysis['next_earnings_date'])
                    col2.metric("Days Until", analysis['days_until'] if analysis['days_until'] else "Unknown")
                    col3.metric("Earnings Quality", f"{analysis['quality_emoji']} {analysis['earnings_quality']}")

                    st.markdown("---")

                    col1, col2 = st.columns(2)

                    with col1:
                        st.subheader("📊 Historical Performance")
                        st.write(f"Beat Rate: {analysis['beat_rate']:.1f}%")
                        st.write(f"Avg Surprise: {analysis['avg_surprise_pct']:+.2f}%")
                        st.write(f"Last Surprise: {analysis['last_surprise_pct']:+.2f}%")
                        st.write(f"Consecutive Beats: {analysis['consecutive_beats']}")

                    with col2:
                        st.subheader("💹 Price Reaction")
                        st.write(f"Avg Move After: {analysis['avg_earnings_move_pct']:+.2f}%")
                        st.write(f"Last Move: {analysis['last_earnings_move_pct']:+.2f}%")

                    st.markdown("---")

                    # Recommendation
                    if analysis['hold_through_earnings']:
                        st.success("✅ Generally safe to hold through earnings based on historical performance")
                    else:
                        st.warning("⚠️ Consider reducing position before earnings")

                    if analysis['is_this_week']:
                        st.error("⚠️ EARNINGS THIS WEEK!")

                except Exception as e:
                    st.error(f"Error: {e}")

    # Tab 3: Earnings Analysis
    with tab3:
        st.subheader("Detailed Earnings Analysis")

        symbol = st.text_input("Enter Symbol", "AAPL", key="earn_analysis").upper()

        if st.button("📊 Analyze", key="earn_analysis_btn"):
            with st.spinner(f"Analyzing {symbol}..."):
                try:
                    # Get earnings history
                    hist = ec.get_earnings_history(symbol, 8)

                    if not hist.empty:
                        st.subheader("Earnings History")
                        st.dataframe(hist, use_container_width=True)

                    # Surprise stats
                    stats = ec.get_earnings_surprise_stats(symbol)

                    st.subheader("Surprise Statistics")
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Quarters Analyzed", stats.get('quarters_analyzed', 0))
                    col2.metric("Beat Rate", f"{stats.get('beat_rate', 0):.1f}%")
                    col3.metric("Avg Surprise", f"{stats.get('avg_surprise_pct', 0):+.2f}%")

                except Exception as e:
                    st.error(f"Error: {e}")


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: INSIDER ACTIVITY
# ═══════════════════════════════════════════════════════════════════════════════

elif selected_page == "👔 Insider Activity":
    st.title("👔 Insider Activity Tracker")

    if not HAS_INSIDER:
        st.error("Insider tracker not available. Create insider_tracker.py")
        st.stop()

    tracker = InsiderTracker()

    tab1, tab2, tab3 = st.tabs(["🔍 Check Stock", "📊 Scan Watchlist", "💰 Notable Purchases"])

    # Tab 1: Check Single Stock
    with tab1:
        st.subheader("Check Insider Activity")

        symbol = st.text_input("Enter Symbol", "NVDA", key="insider_single").upper()

        if st.button("👔 Check Insider Activity", key="insider_check_btn", type="primary"):
            with st.spinner(f"Checking {symbol}..."):
                try:
                    summary = tracker.get_insider_summary(symbol)

                    if summary:
                        st.markdown(f"### {summary.name}")
                        st.markdown(f"Current Price: ${summary.current_price:.2f}")

                        # Sentiment
                        if summary.sentiment_score >= 50:
                            st.success(f"🟢🟢 {summary.insider_sentiment} (Score: {summary.sentiment_score:+d})")
                        elif summary.sentiment_score >= 20:
                            st.success(f"🟢 {summary.insider_sentiment} (Score: {summary.sentiment_score:+d})")
                        elif summary.sentiment_score >= -20:
                            st.info(f"🟡 {summary.insider_sentiment} (Score: {summary.sentiment_score:+d})")
                        elif summary.sentiment_score >= -50:
                            st.warning(f"🔴 {summary.insider_sentiment} (Score: {summary.sentiment_score:+d})")
                        else:
                            st.error(f"🔴🔴 {summary.insider_sentiment} (Score: {summary.sentiment_score:+d})")

                        st.markdown("---")

                        # Activity Summary
                        col1, col2 = st.columns(2)

                        with col1:
                            st.subheader("📈 Last 3 Months")
                            st.metric("Buys", summary.buys_3m)
                            st.metric("Buy Value", f"${summary.buy_value_3m:,.0f}")
                            st.metric("Sells", summary.sells_3m)
                            st.metric("Sell Value", f"${summary.sell_value_3m:,.0f}")

                        with col2:
                            st.subheader("📅 Last 12 Months")
                            st.metric("Buys", summary.buys_12m)
                            st.metric("Buy Value", f"${summary.buy_value_12m:,.0f}")
                            st.metric("Sells", summary.sells_12m)
                            st.metric("Sell Value", f"${summary.sell_value_12m:,.0f}")

                        st.markdown("---")

                        # Net Activity
                        col1, col2 = st.columns(2)
                        col1.metric("Net Shares (3M)", f"{summary.net_shares_3m:+,}")
                        col2.metric("Net Value (3M)", f"${summary.net_value_3m:+,.0f}")

                        # Cluster buying
                        if summary.has_cluster_buying:
                            st.success(f"🎯 CLUSTER BUYING DETECTED! ({summary.cluster_buy_count} insiders)")

                        # Ownership
                        st.markdown("---")
                        st.subheader("👥 Ownership")
                        col1, col2 = st.columns(2)
                        col1.metric("Insider Ownership", f"{summary.insider_ownership_pct:.2f}%")
                        col2.metric("Institutional", f"{summary.institutional_ownership_pct:.2f}%")

                        # Recent transactions
                        st.markdown("---")
                        st.subheader("📋 Recent Transactions")

                        transactions = tracker.get_insider_transactions(symbol, months=6)

                        if transactions:
                            tx_data = []
                            for t in transactions[:10]:
                                tx_data.append({
                                    "Date": t.date,
                                    "Type": "BUY" if t.transaction_type.value == "Buy" else "SELL",
                                    "Insider": t.insider_name[:25],
                                    "Shares": f"{t.shares:,}",
                                    "Value": f"${t.value:,.0f}",
                                    "Price": f"${t.price_per_share:.2f}"
                                })

                            st.dataframe(pd.DataFrame(tx_data), use_container_width=True, hide_index=True)
                        else:
                            st.info("No recent transactions found")
                    else:
                        st.error(f"Could not get insider data for {symbol}")

                except Exception as e:
                    st.error(f"Error: {e}")

    # Tab 2: Scan Watchlist
    with tab2:
        st.subheader("Scan for Insider Buying")

        col1, col2 = st.columns(2)

        with col1:
            watchlist_choice = st.selectbox(
                "Select Watchlist",
                ["US Tech", "Custom"],
                key="insider_watchlist"
            )

            if watchlist_choice == "US Tech":
                scan_symbols = WATCHLIST_US
            else:
                custom = st.text_area("Enter symbols", "NVDA\nAMD\nAAPL")
                scan_symbols = [s.strip().upper() for s in custom.split("\n") if s.strip()]

        with col2:
            min_buy_value = st.number_input("Min Buy Value ($)", 10000, 1000000, 50000, key="insider_min")

        if st.button("🔍 Scan for Insider Buying", key="insider_scan_btn", type="primary"):
            with st.spinner(f"Scanning {len(scan_symbols)} stocks..."):
                try:
                    df = tracker.scan_for_insider_buying(
                        scan_symbols,
                        min_buys=1,
                        min_buy_value=min_buy_value,
                        days=90
                    )

                    if not df.empty:
                        st.success(f"Found {len(df)} stocks with insider buying!")
                        st.dataframe(df, use_container_width=True, hide_index=True)

                        # Highlight cluster buying
                        cluster = df[df['Cluster'] == '✅']
                        if not cluster.empty:
                            st.subheader("🎯 Cluster Buying Detected!")
                            st.dataframe(cluster, use_container_width=True, hide_index=True)
                    else:
                        st.info("No significant insider buying found")

                except Exception as e:
                    st.error(f"Error: {e}")

    # Tab 3: Notable Purchases
    with tab3:
        st.subheader("Notable Recent Purchases")

        col1, col2 = st.columns(2)

        with col1:
            days_back = st.slider("Days Back", 7, 90, 30, key="insider_days")

        with col2:
            min_value = st.number_input("Min Value ($)", 50000, 5000000, 100000, key="insider_notable_min")

        if st.button("💰 Find Notable Purchases", key="insider_notable_btn", type="primary"):
            with st.spinner("Searching..."):
                try:
                    notable = tracker.get_recent_notable_buys(
                        WATCHLIST_US,
                        min_value=min_value,
                        days=days_back
                    )

                    if notable:
                        st.success(f"Found {len(notable)} notable purchases!")

                        df = pd.DataFrame([
                            {
                                "Symbol": t['symbol'],
                                "Insider": t['insider'][:30],
                                "Date": t['date'],
                                "Shares": f"{t['shares']:,}",
                                "Value": f"${t['value']:,.0f}",
                                "Price": f"${t['price']:.2f}"
                            }
                            for t in notable[:20]
                        ])

                        st.dataframe(df, use_container_width=True, hide_index=True)
                    else:
                        st.info("No notable purchases found")

                except Exception as e:
                    st.error(f"Error: {e}")


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: STOCK SCREENER
# ═══════════════════════════════════════════════════════════════════════════════

elif selected_page == "🔍 Stock Screener":
    st.title("🔍 Fundamental Stock Screener")

    if not HAS_SCREENER:
        st.error("Fundamental screener not available. Create fundamental_screener.py")
        st.stop()

    screener = FundamentalScreener()

    tab1, tab2 = st.tabs(["📊 Preset Screens", "⚙️ Custom Screen"])

    # Tab 1: Preset Screens
    with tab1:
        st.subheader("Preset Screening Strategies")

        col1, col2 = st.columns(2)

        with col1:
            preset = st.selectbox(
                "Select Strategy",
                ["Value", "Growth", "Quality", "Dividend", "GARP", "Buffett", "Lynch"],
                key="screener_preset"
            )

        with col2:
            watchlist_choice = st.selectbox(
                "Select Universe",
                ["US Tech", "S&P 500 Sample", "Custom"],
                key="screener_universe"
            )

            if watchlist_choice == "US Tech":
                universe = WATCHLIST_US
            elif watchlist_choice == "S&P 500 Sample":
                universe = ["AAPL", "MSFT", "NVDA", "GOOGL", "AMZN", "META", "BRK-B", "LLY",
                           "JPM", "UNH", "V", "MA", "PG", "JNJ", "HD", "COST"]
            else:
                custom = st.text_area("Enter symbols", "AAPL\nMSFT\nGOOGL")
                universe = [s.strip().upper() for s in custom.split("\n") if s.strip()]

        # Strategy descriptions
        strategies = {
            "Value": "Low P/E, Low P/B, Undervalued stocks",
            "Growth": "High revenue & earnings growth",
            "Quality": "High margins, Strong ROE, Low debt",
            "Dividend": "Dividend paying stocks with sustainable yields",
            "GARP": "Growth at a Reasonable Price (PEG < 2)",
            "Buffett": "Warren Buffett style - Quality + Value",
            "Lynch": "Peter Lynch style - Low PEG, High growth"
        }

        st.info(f"**{preset}**: {strategies.get(preset, '')}")

        if st.button("🔍 Run Screen", key="screener_run_btn", type="primary"):
            with st.spinner(f"Running {preset} screen on {len(universe)} stocks..."):
                try:
                    preset_enum = {
                        "Value": ScreenerPreset.VALUE,
                        "Growth": ScreenerPreset.GROWTH,
                        "Quality": ScreenerPreset.QUALITY,
                        "Dividend": ScreenerPreset.DIVIDEND,
                        "GARP": ScreenerPreset.GARP,
                        "Buffett": ScreenerPreset.BUFFETT,
                        "Lynch": ScreenerPreset.LYNCH,
                    }.get(preset)

                    df, results = screener.screen_with_preset(universe, preset_enum)

                    if not df.empty:
                        st.success(f"Found {len(df)} stocks passing {preset} criteria!")
                        st.dataframe(df, use_container_width=True, hide_index=True)

                        # Top pick
                        if len(df) > 0:
                            top = df.iloc[0]
                            st.subheader(f"🏆 Top {preset} Pick: {top['Symbol']}")
                    else:
                        st.warning("No stocks passed the screening criteria")

                except Exception as e:
                    st.error(f"Error: {e}")

    # Tab 2: Custom Screen
    with tab2:
        st.subheader("Custom Screening Criteria")

        st.markdown("Set your own criteria (leave blank to ignore)")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("**Valuation**")
            max_pe = st.number_input("Max P/E", 0.0, 100.0, 0.0, key="cust_pe")
            max_peg = st.number_input("Max PEG", 0.0, 5.0, 0.0, key="cust_peg")
            max_pb = st.number_input("Max P/B", 0.0, 20.0, 0.0, key="cust_pb")

        with col2:
            st.markdown("**Profitability**")
            min_margin = st.number_input("Min Profit Margin %", 0.0, 50.0, 0.0, key="cust_margin")
            min_roe = st.number_input("Min ROE %", 0.0, 50.0, 0.0, key="cust_roe")
            require_profit = st.checkbox("Require Profitable", key="cust_profit")

        with col3:
            st.markdown("**Growth & Health**")
            min_growth = st.number_input("Min Revenue Growth %", -50.0, 100.0, 0.0, key="cust_growth")
            max_debt = st.number_input("Max Debt/Equity", 0.0, 500.0, 0.0, key="cust_debt")
            min_score = st.number_input("Min Overall Score", 0, 100, 0, key="cust_score")

        custom_symbols = st.text_area("Symbols to screen (one per line)", "\n".join(WATCHLIST_US))

        if st.button("🔍 Run Custom Screen", key="custom_screen_btn", type="primary"):
            with st.spinner("Running custom screen..."):
                try:
                    from fundamental_screener import ScreenerCriteria

                    criteria = ScreenerCriteria(
                        max_pe=max_pe if max_pe > 0 else None,
                        max_peg=max_peg if max_peg > 0 else None,
                        max_pb=max_pb if max_pb > 0 else None,
                        min_profit_margin=min_margin if min_margin > 0 else None,
                        min_roe=min_roe if min_roe > 0 else None,
                        require_profitable=require_profit,
                        min_revenue_growth=min_growth if min_growth != 0 else None,
                        max_debt_to_equity=max_debt if max_debt > 0 else None,
                        min_overall_score=min_score if min_score > 0 else None,
                    )

                    symbols = [s.strip().upper() for s in custom_symbols.split("\n") if s.strip()]

                    df, results = screener.screen(symbols, criteria)

                    if not df.empty:
                        st.success(f"Found {len(df)} stocks passing criteria!")
                        st.dataframe(df, use_container_width=True, hide_index=True)
                    else:
                        st.warning("No stocks passed the criteria")

                except Exception as e:
                    st.error(f"Error: {e}")


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: TRADE JOURNAL
# ═══════════════════════════════════════════════════════════════════════════════

elif selected_page == "📋 Trade Journal":
    st.title("📋 Trade Journal")

    if not HAS_JOURNAL:
        st.error("Trade journal not available. Create trade_journal.py")
        st.stop()

    journal = TradeJournal()

    tab1, tab2, tab3 = st.tabs(["📂 Open Positions", "📝 Log Trade", "📊 History"])

    # Tab 1: Open Positions
    with tab1:
        st.subheader("Open Positions")

        try:
            open_trades = journal.get_open_trades()

            if not open_trades.empty:
                total_pnl = 0

                for _, t in open_trades.iterrows():
                    symbol = t['symbol']
                    entry = t['entry_price']
                    shares = t['shares']
                    stop = t['stop_loss']
                    target = t['target_1']

                    current = get_current_price(symbol) or entry
                    pnl = (current - entry) * shares
                    pnl_pct = (current / entry - 1) * 100 if entry > 0 else 0

                    total_pnl += pnl

                    emoji = "🟢" if pnl >= 0 else "🔴"

                    with st.expander(f"{emoji} {symbol} - P&L: ${pnl:+.2f} ({pnl_pct:+.1f}%)"):
                        col1, col2, col3, col4 = st.columns(4)
                        col1.metric("Entry", f"${entry:.2f}")
                        col2.metric("Current", f"${current:.2f}")
                        col3.metric("Stop", f"${stop:.2f}")
                        col4.metric("Target", f"${target:.2f}")

                        st.write(f"Shares: {shares}")
                        st.write(f"Position Value: ${current * shares:,.2f}")

                        # Close trade form
                        st.markdown("---")
                        st.write("**Close This Trade**")
                        close_col1, close_col2 = st.columns(2)
                        exit_price = close_col1.number_input(
                            "Exit Price", min_value=0.01, value=round(current, 2),
                            key=f"exit_price_{t['id']}"
                        )
                        exit_reason = close_col2.selectbox(
                            "Exit Reason",
                            ["Target Hit", "Stop Loss", "Trailing Stop", "Manual Exit", "Time Exit"],
                            key=f"exit_reason_{t['id']}"
                        )
                        if st.button(f"❌ Close {symbol}", key=f"close_{t['id']}"):
                            try:
                                result = journal.log_exit(
                                    trade_id=t['id'],
                                    exit_price=exit_price,
                                    exit_reason=exit_reason
                                )
                                st.success(f"✅ {symbol} closed — P&L: ${result['pnl']:+,.2f} ({result['pnl_pct']:+.1f}%) | {result['r_multiple']:+.1f}R")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error closing trade: {e}")

                st.markdown("---")
                emoji = "🟢" if total_pnl >= 0 else "🔴"
                st.metric(f"{emoji} Total Unrealized P&L", f"${total_pnl:+,.2f}")
            else:
                st.info("No open positions")

        except Exception as e:
            st.error(f"Error: {e}")

    # Tab 2: Log Trade
    with tab2:
        st.subheader("Log New Trade")

        col1, col2, col3 = st.columns(3)

        symbol = col1.text_input("Symbol", "NVDA")
        entry_price = col2.number_input("Entry Price", min_value=0.0, value=100.0)
        shares = col3.number_input("Shares", min_value=1, value=100)

        col1, col2, col3 = st.columns(3)
        stop_loss = col1.number_input("Stop Loss", min_value=0.0, value=95.0)
        target_1 = col2.number_input("Target 1", min_value=0.0, value=110.0)
        target_2 = col3.number_input("Target 2", min_value=0.0, value=120.0)

        setup_type = st.selectbox(
            "Setup Type",
            ["Breakout", "Pullback", "Support Bounce", "Earnings", "Other"]
        )

        notes = st.text_area("Notes", "")

        if st.button("📝 Log Trade"):
            try:
                trade_id = journal.log_entry(
                    symbol=symbol,
                    entry_price=entry_price,
                    shares=shares,
                    stop_loss=stop_loss,
                    target_1=target_1,
                    target_2=target_2,
                    setup_type=setup_type,
                    entry_reason=notes
                )
                st.success(f"✅ Trade #{trade_id} logged for {symbol}")
                st.rerun()
            except Exception as e:
                st.error(f"Error logging trade: {e}")

    # Tab 3: History
    with tab3:
        st.subheader("Trade History")

        try:
            closed_trades = journal.get_closed_trades()

            if not closed_trades.empty:
                # Performance stats
                col1, col2, col3, col4 = st.columns(4)

                total_trades = len(closed_trades)
                winning_trades = (closed_trades['pnl'] > 0).sum()
                losing_trades = (closed_trades['pnl'] < 0).sum()
                total_pnl = closed_trades['pnl'].sum()

                win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0

                col1.metric("Total Trades", total_trades)
                col2.metric("Win Rate", f"{win_rate:.1f}%")
                col3.metric("Wins", winning_trades)
                col4.metric("Losses", losing_trades)

                st.metric("Total P&L", f"${total_pnl:+,.2f}")

                # Trade table
                st.dataframe(closed_trades[[
                    'symbol', 'entry_price', 'exit_price', 'shares', 'pnl', 'pnl_pct', 'entry_date'
                ]])
            else:
                st.info("No closed trades yet")

        except Exception as e:
            st.error(f"Error: {e}")


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: PERFORMANCE
# ═══════════════════════════════════════════════════════════════════════════════

elif selected_page == "📊 Performance":
    st.title("📊 Performance Tracking")

    if not HAS_TRACKER:
        st.error("Performance tracker not available")
        st.stop()

    tracker = PerformanceTracker()

    tab1, tab2, tab3 = st.tabs(["📈 Monthly", "📊 Statistics", "📝 Summary"])

    with tab1:
        st.subheader("Monthly Performance")

        try:
            progress = tracker.get_monthly_progress()

            if "error" not in progress:
                st.write(f"### {progress['month']}")

                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Target", f"${progress['target']:,.2f}")
                col2.metric("Current P&L", f"${progress['current_pnl']:+,.2f}")
                col3.metric("Progress", f"{progress['progress_pct']:.1f}%")
                col4.metric("Remaining", f"${progress['remaining']:,.2f}")

                # Progress bar
                pct = min(max(progress['progress_pct'], 0), 100) / 100
                st.progress(pct, text=f"{progress['progress_pct']:.1f}% of monthly target")

                if progress['on_track']:
                    st.success("✅ On track to hit monthly target")
                else:
                    st.warning(f"⚠️ Behind pace — {progress['trading_days_left']} trading days left")
            else:
                st.info("No performance data available")

        except Exception as e:
            st.error(f"Error: {e}")

    with tab2:
        st.subheader("Performance Statistics")

        try:
            progress = tracker.get_monthly_progress()

            if "error" not in progress:
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Trades This Month", progress['trades'])
                col2.metric("Win Rate", f"{progress['win_rate']:.1f}%")
                col3.metric("Avg R-Multiple", f"{progress['avg_r']:.2f}R")
                col4.metric("Target %", f"{progress['target_pct']:.1f}%")

                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Days Elapsed", progress['days_elapsed'])
                col2.metric("Days Left", progress['days_left'])
                col3.metric("Trading Days Left", progress['trading_days_left'])
                col4.metric("Current P&L", f"${progress['current_pnl']:+,.2f}")

                # Goal status
                if progress['current_pnl'] >= progress['target']:
                    st.success(f"✅ Monthly target achieved! (${progress['current_pnl']:+,.2f} >= ${progress['target']:,.2f})")
                else:
                    st.info(f"⏳ Need ${progress['remaining']:,.2f} more to reach monthly target")
            else:
                st.info("No statistics available")

        except Exception as e:
            st.error(f"Error: {e}")

    with tab3:
        st.subheader("Performance Summary")

        try:
            progress = tracker.get_monthly_progress()

            if "error" not in progress:
                st.markdown(f"""
**Month:** {progress['month']}
| Metric | Value |
|--------|-------|
| Monthly Target | ${progress['target']:,.2f} ({progress['target_pct']:.1f}%) |
| Current P&L | ${progress['current_pnl']:+,.2f} |
| Progress | {progress['progress_pct']:.1f}% |
| Trades | {progress['trades']} |
| Win Rate | {progress['win_rate']:.1f}% |
| Avg R-Multiple | {progress['avg_r']:.2f}R |
| Days Left | {progress['days_left']} ({progress['trading_days_left']} trading) |
| Status | {'✅ On Track' if progress['on_track'] else '⚠️ Behind Pace'} |
""")
            else:
                st.info("No summary available")

        except Exception as e:
            st.error(f"Error: {e}")


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: PORTFOLIO
# ═══════════════════════════════════════════════════════════════════════════════

elif selected_page == "💼 Portfolio":
    st.title("💼 Portfolio Management")

    tab1, tab2, tab3, tab4 = st.tabs(["💰 Summary", "📊 Positions", "⚖️ Allocation", "🎯 Risk"])

    with tab1:
        st.subheader("Portfolio Summary")

        if HAS_YFINANCE:
            try:
                col1, col2, col3, col4 = st.columns(4)

                account_value = ACCOUNT_SIZE
                col1.metric("Account Size", f"${account_value:,.0f}")
                col2.metric("Risk per Trade", f"{RISK_PER_TRADE * 100:.1f}%")
                col3.metric("Max Positions", getattr(config, 'MAX_POSITIONS', 8))
                col4.metric("Max Position Size", f"{getattr(config, 'MAX_POSITION_SIZE_PCT', 0.25) * 100:.0f}%")

            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.warning("YFinance not available")

    with tab2:
        st.subheader("Open Positions")

        try:
            if HAS_JOURNAL:
                journal = TradeJournal()
                open_trades = journal.get_open_trades()

                if not open_trades.empty:
                    # Calculate total
                    total_value = 0
                    total_pnl = 0

                    positions_data = []

                    for _, trade in open_trades.iterrows():
                        symbol = trade['symbol']
                        entry = trade['entry_price']
                        shares = trade['shares']
                        position_value = entry * shares

                        current = get_current_price(symbol) or entry
                        pnl = (current - entry) * shares
                        pnl_pct = (current / entry - 1) * 100 if entry > 0 else 0

                        total_value += position_value
                        total_pnl += pnl

                        positions_data.append({
                            "Symbol": symbol,
                            "Shares": shares,
                            "Entry": f"${entry:.2f}",
                            "Current": f"${current:.2f}",
                            "P&L": f"${pnl:+.2f}",
                            "P&L %": f"{pnl_pct:+.1f}%",
                            "Value": f"${position_value:,.2f}"
                        })

                    st.dataframe(positions_data, use_container_width=True)

                    st.markdown("---")
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Total Invested", f"${total_value:,.2f}")
                    col2.metric("Unrealized P&L", f"${total_pnl:+,.2f}")
                    col3.metric("Cash Available", f"${ACCOUNT_SIZE - total_value:,.2f}")
                else:
                    st.info("No open positions")

            else:
                st.warning("Trade journal not available")

        except Exception as e:
            st.error(f"Error: {e}")

    with tab3:
        st.subheader("Position Allocation")

        try:
            if HAS_JOURNAL:
                journal = TradeJournal()
                open_trades = journal.get_open_trades()

                if not open_trades.empty:
                    # Calculate allocation
                    allocation_data = []

                    for _, trade in open_trades.iterrows():
                        symbol = trade['symbol']
                        shares = trade['shares']
                        entry = trade['entry_price']
                        position_value = shares * entry
                        allocation_pct = (position_value / ACCOUNT_SIZE) * 100

                        allocation_data.append({
                            "symbol": symbol,
                            "allocation": allocation_pct
                        })

                    if allocation_data:
                        alloc_df = pd.DataFrame(allocation_data)
                        alloc_df = alloc_df.sort_values('allocation', ascending=False)

                        fig = px.pie(
                            alloc_df,
                            values='allocation',
                            names='symbol',
                            title="Portfolio Allocation by Position"
                        )
                        st.plotly_chart(fig, use_container_width=True)

                        st.dataframe(alloc_df)
                else:
                    st.info("No positions to allocate")

            else:
                st.warning("Trade journal not available")

        except Exception as e:
            st.error(f"Error: {e}")

    with tab4:
        st.subheader("Risk Analysis")

        try:
            if HAS_JOURNAL:
                journal = TradeJournal()
                open_trades = journal.get_open_trades()

                if not open_trades.empty:
                    total_risk = 0

                    risk_data = []

                    for _, trade in open_trades.iterrows():
                        symbol = trade['symbol']
                        entry = trade['entry_price']
                        stop = trade['stop_loss']
                        shares = trade['shares']

                        risk_per_share = entry - stop
                        total_risk_trade = risk_per_share * shares

                        risk_pct_account = (total_risk_trade / ACCOUNT_SIZE) * 100

                        total_risk += total_risk_trade

                        risk_data.append({
                            "Symbol": symbol,
                            "Risk per Share": f"${risk_per_share:.2f}",
                            "Total Risk": f"${total_risk_trade:+.2f}",
                            "% of Account": f"{risk_pct_account:.2f}%"
                        })

                    st.dataframe(risk_data, use_container_width=True)

                    st.markdown("---")
                    total_risk_pct = (total_risk / ACCOUNT_SIZE) * 100
                    col1, col2 = st.columns(2)
                    col1.metric("Total At-Risk", f"${total_risk:+,.2f}")
                    col2.metric("% of Account at Risk", f"{total_risk_pct:.2f}%")

                    # Risk assessment
                    if total_risk_pct <= 5:
                        st.success("✅ Risk level is SAFE (≤5%)")
                    elif total_risk_pct <= 10:
                        st.warning("⚠️ Risk level is MODERATE (5-10%)")
                    else:
                        st.error(f"❌ Risk level is HIGH (>{10}%)")

                else:
                    st.info("No open positions - risk is 0%")

            else:
                st.warning("Trade journal not available")

        except Exception as e:
            st.error(f"Error: {e}")


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: SIGNAL ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════════

elif selected_page == "🔬 Signal Analysis":
    st.title("🔬 Signal Analysis")
    st.markdown("Deep-dive into exactly **why** a stock gets a STRONG BUY, BUY, or AVOID rating.")

    tab1, tab2 = st.tabs(["🔍 Analyze Stock", "📋 Scoring Criteria"])

    with tab2:
        st.subheader("How Signals Are Scored (0–100)")

        st.markdown("""
| Signal | Score Threshold |
|--------|-----------------|
| 🟢 **STRONG BUY** | ≥ 70 |
| 🟡 **BUY** | ≥ 60 |
| 🟠 **WATCH** | ≥ 45 |
| 🔴 **AVOID** | < 45 |
""")

        st.markdown("---")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("✅ Positive Factors")
            st.markdown("""
**Trend (up to +35 pts)**
- Strong EMA alignment (8 > 21 > 50): **+20 pts**
- EMAs bullish (partial): **+12 pts**
- Above 50 EMA: **+10 pts**
- ADX ≥ 25 (strong trend): **+5 pts**
- ADX ≥ 20: **+2 pts**

**Entry Timing (up to +25 pts)**
- Pullback bounce at 21 EMA + green candle: **+25 pts**
- Near 21 EMA + bouncing: **+18 pts**
- Near 21 EMA (within 3%): **+10 pts**
- 3-day momentum > 1%: **+8 pts**
- 3-day momentum > 0%: **+4 pts**
- Stochastic oversold (< 30): **+5 pts**
- Stochastic turning up: **+3 pts**

**Momentum (up to +20 pts)**
- RSI 40–55 (ideal zone): **+12 pts**
- RSI 35–60 (acceptable): **+6 pts**
- RSI < 30 (oversold bounce): **+3 pts**
- MACD bullish + histogram positive: **+8 pts**
- MACD turning up: **+5 pts**

**Volume (up to +10 pts)**
- Volume ≥ 1.3× average: **+10 pts**
- Volume ≥ 1.0× average: **+5 pts**
- Volume ≥ 0.7× average: **+2 pts**
""")

        with col2:
            st.subheader("❌ Negative Factors & Hard Limits")
            st.markdown("""
**Penalties**
- Below 50 EMA: **−10 pts**
- ADX < 15 (choppy market): **−5 pts**
- Too extended from EMA (> 6%): **−10 pts**
- 3-day momentum < −2%: **−8 pts**
- Stochastic overbought (> 80): **−8 pts**
- RSI overbought (> 65): **−10 pts**
- MACD bearish + falling histogram: **−5 pts**
- Volume < 0.7× average: **−3 pts**

**Hard Disqualifiers (score capped)**
- RSI > 70: score capped at **40**
- Below 50 EMA: score capped at **45**
- Price > 8% above EMA: score capped at **35**

**Stop Loss Calculation**
- Stop = 2.5× ATR below entry
- Also checks swing low (10-day)
- Maximum stop: 8% below entry

**Targets**
- Target 1 = entry + 1.8× risk (R:R 1.8)
- Target 2 = entry + 3.0× risk (R:R 3.0)
""")

    with tab1:
        st.subheader("Analyze Individual Stock")

        col1, col2 = st.columns([2, 1])
        symbol_input = col1.text_input("Stock Symbol", "NVDA", placeholder="e.g. NVDA, SAP.DE, TCS.NS")
        analyze_btn = col2.button("🔍 Analyze", use_container_width=True)

        if analyze_btn and symbol_input:
            symbol = symbol_input.strip().upper()

            with st.spinner(f"Analyzing {symbol}..."):
                try:
                    from global_data_fetcher import GlobalDataFetcher
                    from technical_analyzer import TechnicalAnalyzer

                    fetcher = GlobalDataFetcher()
                    analyzer = TechnicalAnalyzer()

                    df = fetcher.get_stock_data(symbol, period="6mo")
                    info = fetcher.get_stock_info(symbol)

                    if df.empty or len(df) < 50:
                        st.error(f"Not enough data for {symbol}. Check the symbol format.")
                    else:
                        result = analyzer.analyze_stock(df, symbol)

                        if "error" in result:
                            st.error(f"Analysis error: {result['error']}")
                        else:
                            # ── Header ──
                            status = result.get("signal_status", "AVOID")
                            score = result.get("signal_score", 0)
                            status_color = {"STRONG BUY": "🟢", "BUY": "🟡", "WATCH": "🟠", "AVOID": "🔴"}
                            emoji = status_color.get(status, "🔴")

                            st.markdown(f"## {emoji} {symbol} — {status} (Score: {score}/100)")
                            st.markdown(f"**Setup:** {result.get('setup_type', 'N/A')} &nbsp;|&nbsp; "
                                        f"**Name:** {info.get('name', symbol)} &nbsp;|&nbsp; "
                                        f"**Sector:** {info.get('sector', 'N/A')}")

                            st.markdown("---")

                            # ── Score bar ──
                            st.subheader("📊 Score Breakdown")
                            pct = score / 100
                            bar_color = "green" if score >= 70 else "orange" if score >= 60 else "red"
                            st.progress(pct, text=f"{score}/100 — threshold: STRONG BUY≥70, BUY≥60, WATCH≥45")

                            # ── Key metrics ──
                            st.subheader("📈 Key Indicators")
                            m1, m2, m3, m4, m5, m6 = st.columns(6)
                            m1.metric("Price", f"${result.get('current_price', 0):,.2f}")
                            m2.metric("RSI (14)", f"{result.get('rsi', 0):.1f}",
                                      "✅ Ideal" if 40 <= result.get('rsi', 0) <= 55
                                      else "⚠️ High" if result.get('rsi', 0) > 65 else "")
                            m3.metric("ADX", f"{result.get('adx', 0):.1f}",
                                      "✅ Strong" if result.get('adx', 0) >= 25
                                      else "⚠️ Weak" if result.get('adx', 0) < 15 else "")
                            m4.metric("Volume Ratio", f"{result.get('volume_ratio', 1):.2f}×",
                                      "✅ High" if result.get('volume_ratio', 1) >= 1.3 else "")
                            m5.metric("Above 50 EMA", "Yes ✅" if result.get('above_50_ema') else "No ❌")
                            m6.metric("Above 200 EMA", "Yes ✅" if result.get('above_200_ema') else "No ❌")

                            # ── Analysis reasons ──
                            st.subheader("🔎 Scoring Reasons")
                            reasons = result.get("analysis_reasons", [])
                            if reasons:
                                for reason in reasons:
                                    if "✓" in reason:
                                        st.success(f"✅ {reason}")
                                    elif "✗" in reason or "SKIP" in reason:
                                        st.error(f"❌ {reason}")
                                    else:
                                        st.info(f"ℹ️ {reason}")
                            else:
                                st.info("No detailed reasons available")

                            # ── Trade levels ──
                            if status in ["STRONG BUY", "BUY"] and result.get("ideal_entry"):
                                st.markdown("---")
                                st.subheader("💰 Trade Setup")

                                t1, t2, t3, t4 = st.columns(4)
                                t1.metric("Entry", f"${result.get('ideal_entry', 0):,.2f}")
                                t2.metric("Stop Loss", f"${result.get('stop_loss', 0):,.2f}",
                                          f"-{result.get('risk_pct', 0):.1f}%")
                                t3.metric("Target 1", f"${result.get('target_1', 0):,.2f}",
                                          f"R:R {result.get('rr_1', 0):.1f}×")
                                t4.metric("Target 2", f"${result.get('target_2', 0):,.2f}",
                                          f"R:R {result.get('rr_2', 0):.1f}×")

                                # Position sizing
                                entry_p = result.get("ideal_entry", 0)
                                stop_p = result.get("stop_loss", 0)
                                if entry_p and stop_p:
                                    pos = calculate_position_size(entry_p, stop_p)
                                    st.markdown(f"""
**Position Sizing** (${ACCOUNT_SIZE:,} account, {RISK_PER_TRADE*100:.1f}% risk):  
Shares: **{pos['shares']:,}** &nbsp;|&nbsp; Position Value: **${pos['value']:,.2f}** &nbsp;|&nbsp; Max Risk: **${pos['risk']:,.2f}**
""")

                            # ── Chart ──
                            st.markdown("---")
                            fig = create_price_chart(symbol, "3mo")
                            st.plotly_chart(fig, use_container_width=True)

                except Exception as e:
                    st.error(f"Error analyzing {symbol}: {e}")


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: POSITION CALCULATOR
# ═══════════════════════════════════════════════════════════════════════════════

elif selected_page == "📐 Position Calculator":
    st.title("📐 Position Size Calculator")
    st.markdown("Calculate the correct number of shares to buy based on your account size and risk tolerance.")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Trade Parameters")
        account_size = st.number_input("Account Size ($)", min_value=1000.0, value=float(ACCOUNT_SIZE), step=1000.0)
        risk_pct = st.slider("Risk per Trade (%)", min_value=0.1, max_value=5.0, value=float(RISK_PER_TRADE * 100), step=0.1)
        entry_price = st.number_input("Entry Price ($)", min_value=0.01, value=100.0, step=0.01)
        stop_loss = st.number_input("Stop Loss ($)", min_value=0.01, value=95.0, step=0.01)
        target_1 = st.number_input("Target 1 ($)", min_value=0.01, value=110.0, step=0.01)
        target_2 = st.number_input("Target 2 ($)", min_value=0.01, value=120.0, step=0.01)

    with col2:
        st.subheader("Results")

        if entry_price > 0 and stop_loss > 0 and stop_loss < entry_price:
            risk_amount = account_size * (risk_pct / 100)
            risk_per_share = entry_price - stop_loss
            shares = int(risk_amount / risk_per_share)
            position_value = shares * entry_price
            position_pct = (position_value / account_size) * 100

            rr1 = (target_1 - entry_price) / risk_per_share if risk_per_share > 0 else 0
            rr2 = (target_2 - entry_price) / risk_per_share if risk_per_share > 0 else 0

            profit_t1 = (target_1 - entry_price) * shares
            profit_t2 = (target_2 - entry_price) * shares
            max_loss = risk_per_share * shares

            col_a, col_b = st.columns(2)
            col_a.metric("Shares to Buy", f"{shares:,}")
            col_b.metric("Position Value", f"${position_value:,.2f}")

            col_a, col_b = st.columns(2)
            col_a.metric("Risk Amount", f"${risk_amount:,.2f}")
            col_b.metric("Portfolio %", f"{position_pct:.1f}%")

            col_a, col_b = st.columns(2)
            col_a.metric("Max Loss", f"-${max_loss:,.2f}")
            col_b.metric("Risk/Share", f"${risk_per_share:.2f}")

            st.markdown("---")
            st.subheader("Profit Targets")

            col_a, col_b = st.columns(2)
            col_a.metric("Target 1 Profit", f"+${profit_t1:,.2f}", f"R:R {rr1:.1f}x")
            col_b.metric("Target 2 Profit", f"+${profit_t2:,.2f}", f"R:R {rr2:.1f}x")

            st.markdown("---")
            st.subheader("Trade Summary")
            st.code(
                f"Symbol:        (your stock)\n"
                f"Entry:         ${entry_price:.2f}\n"
                f"Stop Loss:     ${stop_loss:.2f} ({(stop_loss/entry_price - 1)*100:.1f}%)\n"
                f"Target 1:      ${target_1:.2f} (+{(target_1/entry_price - 1)*100:.1f}%)\n"
                f"Target 2:      ${target_2:.2f} (+{(target_2/entry_price - 1)*100:.1f}%)\n"
                f"Shares:        {shares:,}\n"
                f"Position:      ${position_value:,.2f} ({position_pct:.1f}% of account)\n"
                f"Max Risk:      ${max_loss:,.2f} ({risk_pct:.1f}% of account)\n"
                f"Target 1 R:R:  {rr1:.1f}:1\n"
                f"Target 2 R:R:  {rr2:.1f}:1"
            )

            if rr1 < 1.5:
                st.warning("⚠️ R:R below 1.5 — consider a better entry or wider target")
            elif rr1 >= 2.0:
                st.success("✅ Good risk/reward ratio")

            if position_pct > 25:
                st.warning("⚠️ Position exceeds 25% of account — consider reducing size")
        else:
            st.warning("Stop loss must be below entry price")


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: SETTINGS
# ═══════════════════════════════════════════════════════════════════════════════

elif selected_page == "⚙️ Settings":
    st.title("⚙️ Dashboard Settings")

    st.markdown("### 🔧 Configuration Overview")

    # Display all settings
    st.subheader("Account Settings")

    col1, col2, col3 = st.columns(3)

    col1.metric("Account Size", f"${ACCOUNT_SIZE:,}")
    col2.metric("Risk per Trade", f"{RISK_PER_TRADE * 100:.2f}%")
    col3.metric("Monthly Target", f"{getattr(config, 'MONTHLY_TARGET', 0.05) * 100:.1f}%")

    st.subheader("Position Management")

    col1, col2, col3 = st.columns(3)

    col1.metric("Max Positions", getattr(config, 'MAX_POSITIONS', 8))
    col2.metric("Max Position Size", f"{getattr(config, 'MAX_POSITION_SIZE_PCT', 0.25) * 100:.0f}%")
    col3.metric("Daily Loss Limit", f"{getattr(config, 'DAILY_LOSS_LIMIT', 0.02) * 100:.1f}%")

    st.subheader("Technical Analysis")

    # Display indicator settings
    try:
        indicators = getattr(config, 'INDICATORS', {})
        thresholds = getattr(config, 'THRESHOLDS', {})

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("EMA Fast", indicators.get('ema_fast', 8))
        col2.metric("EMA Medium", indicators.get('ema_medium', 21))
        col3.metric("EMA Slow", indicators.get('ema_slow', 50))
        col4.metric("EMA Trend", indicators.get('ema_trend', 200))

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("RSI Period", indicators.get('rsi_period', 14))
        col2.metric("ATR Period", indicators.get('atr_period', 14))
        col3.metric("ADX Period", indicators.get('adx_period', 14))
        col4.metric("Volume MA", indicators.get('volume_ma_period', 20))

        col1, col2, col3 = st.columns(3)

        col1.metric("Min ADX", thresholds.get('min_adx', 20))
        col2.metric("RSI Oversold", thresholds.get('rsi_oversold', 30))
        col3.metric("RSI Overbought", thresholds.get('rsi_overbought', 70))

    except Exception as e:
        st.warning(f"Could not load all settings: {e}")

    st.markdown("---")

    st.subheader("📋 Stock Universe")

    try:
        universe = getattr(config, 'STOCK_UNIVERSE', [])
        st.write(f"Total stocks in universe: **{len(universe)}**")

        with st.expander("View all stocks"):
            # Group into columns for better display
            cols = st.columns(4)
            for idx, symbol in enumerate(universe):
                cols[idx % 4].write(f"• {symbol}")

    except Exception as e:
        st.warning(f"Could not load universe: {e}")

    st.markdown("---")

    st.subheader("🎯 Screening Criteria")

    try:
        criteria = getattr(config, 'SCREENING_CRITERIA', {})

        col1, col2, col3 = st.columns(3)

        col1.metric("Min Market Cap", f"${criteria.get('min_market_cap', 5e9):,.0f}")
        col2.metric("Min Avg Volume", f"{criteria.get('min_avg_volume', 2e6):,.0f}")
        col3.metric("Price Range", f"${criteria.get('min_price', 10)}-${criteria.get('max_price', 1500)}")

        col1, col2, col3 = st.columns(3)

        col1.metric("Min Beta", f"{criteria.get('min_beta', 1.0)}")
        col2.metric("Max Beta", f"{criteria.get('max_beta', 2.5)}")
        col3.metric("ATR Range", f"{criteria.get('min_atr_pct', 2.0)}-{criteria.get('max_atr_pct', 8.0)}%")

    except Exception as e:
        st.warning(f"Could not load criteria: {e}")

    st.markdown("---")

    st.subheader("📊 Exit Rules")

    try:
        exit_rules = getattr(config, 'EXIT_RULES', {})

        col1, col2, col3 = st.columns(3)

        col1.metric("Stop Loss ATR Mult", f"{exit_rules.get('stop_loss_atr_mult', 2.5)}x")
        col2.metric("Target 1 ATR Mult", f"{exit_rules.get('target_1_atr_mult', 3.5)}x")
        col3.metric("Target 2 ATR Mult", f"{exit_rules.get('target_2_atr_mult', 5.0)}x")

        col1, col2 = st.columns(2)

        col1.metric("Max Hold Days", exit_rules.get('max_hold_days', 15))
        col2.metric("Partial Exit %", f"{exit_rules.get('partial_exit_pct', 0.5) * 100:.0f}%")

    except Exception as e:
        st.warning(f"Could not load exit rules: {e}")

    st.markdown("---")

    st.info("ℹ️ To modify settings, edit config.py and restart the dashboard")
