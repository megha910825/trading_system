#!/usr/bin/env python3
"""
Trading Dashboard - Global Markets Version
Supports: US, Germany, India
"""

import streamlit as st
import pandas as pd
from datetime import datetime

# Import modules
from global_data_fetcher import GlobalDataFetcher
from technical_analyzer import TechnicalAnalyzer
from global_universe_manager import GlobalUniverseManager
from global_signal_generator import GlobalSignalGenerator
from position_manager import PositionManager
from backtester import Backtester
from market_config import MARKETS, get_market_status

import config

# Page config
st.set_page_config(
    page_title="Global Trading System",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .market-card {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .us-market { background-color: #1a365d; color: white; }
    .de-market { background-color: #1a202c; color: white; }
    .in-market { background-color: #2d3748; color: white; }
</style>
""", unsafe_allow_html=True)


# Initialize components
@st.cache_resource
def init_components():
    return {
        "fetcher": GlobalDataFetcher(),
        "analyzer": TechnicalAnalyzer(),
        "universe": GlobalUniverseManager(),
        "signals": GlobalSignalGenerator(),
        "positions": PositionManager(),
        "backtester": Backtester(),
    }


components = init_components()


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("🌍 Global Trading System")
st.sidebar.markdown(f"**Target: {config.MONTHLY_TARGET*100}% Monthly**")

# Market status in sidebar
st.sidebar.markdown("---")
st.sidebar.subheader("📊 Market Status")

status = get_market_status()
for code, stat in status.items():
    market = MARKETS[code]
    flag = {"US": "🇺🇸", "DE": "🇩🇪", "IN": "🇮🇳"}.get(code, "🌐")
    st.sidebar.markdown(f"{flag} **{market.name}**: {stat}")

st.sidebar.markdown("---")

# Navigation
page = st.sidebar.radio(
    "Navigate",
    ["🏠 Dashboard", "🎯 Signals", "📈 Analysis", "🔍 Scanner",
     "📉 Backtest", "📐 Calculator", "⚙️ Universe"]
)


# ============================================================
# DASHBOARD PAGE
# ============================================================

if page == "🏠 Dashboard":
    st.title("🌍 Global Trading Dashboard")

    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Account Size", f"${config.ACCOUNT_SIZE:,}")
    col2.metric("Monthly Target", f"${config.ACCOUNT_SIZE * config.MONTHLY_TARGET:,.0f}")
    col3.metric("Risk/Trade", f"{config.RISK_PER_TRADE*100}%")
    col4.metric("Max Positions", config.MAX_POSITIONS)

    st.markdown("---")

    # Market overview
    st.subheader("📊 Market Overview")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### 🇺🇸 United States")
        summary = components["fetcher"].get_market_summary("US")
        for idx, data in summary.items():
            change_color = "green" if data["change_pct"] >= 0 else "red"
            st.markdown(f"**{idx}**: {data['price']:,.2f} "
                       f"<span style='color:{change_color}'>({data['change_pct']:+.2f}%)</span>",
                       unsafe_allow_html=True)

    with col2:
        st.markdown("### 🇩🇪 Germany")
        summary = components["fetcher"].get_market_summary("DE")
        for idx, data in summary.items():
            change_color = "green" if data["change_pct"] >= 0 else "red"
            st.markdown(f"**{idx}**: {data['price']:,.2f} "
                       f"<span style='color:{change_color}'>({data['change_pct']:+.2f}%)</span>",
                       unsafe_allow_html=True)

    with col3:
        st.markdown("### 🇮🇳 India")
        summary = components["fetcher"].get_market_summary("IN")
        for idx, data in summary.items():
            change_color = "green" if data["change_pct"] >= 0 else "red"
            st.markdown(f"**{idx}**: {data['price']:,.2f} "
                       f"<span style='color:{change_color}'>({data['change_pct']:+.2f}%)</span>",
                       unsafe_allow_html=True)

    st.markdown("---")

    # Quick signals
    st.subheader("🎯 Quick Signal Scan")

    market_selection = st.multiselect(
        "Select Markets",
        ["US", "DE", "IN"],
        default=["US", "DE", "IN"]
    )

    if st.button("🔍 Generate Signals", type="primary"):
        with st.spinner("Analyzing stocks..."):
            signals = components["signals"].generate_signals(markets=market_selection)

            for market, market_signals in signals.items():
                if market_signals:
                    flag = {"US": "🇺🇸", "DE": "🇩🇪", "IN": "🇮🇳"}.get(market, "🌐")
                    st.markdown(f"### {flag} {MARKETS[market].name} - {len(market_signals)} Signals")

                    df = pd.DataFrame(market_signals)
                    cols = ["symbol", "name", "signal_status", "signal_score",
                           "current_price", "ideal_entry", "stop_loss", "target_1", "risk_reward"]
                    st.dataframe(df[[c for c in cols if c in df.columns]], use_container_width=True)


# ============================================================
# SIGNALS PAGE
# ============================================================

elif page == "🎯 Signals":
    st.title("🎯 Trading Signals")

    col1, col2 = st.columns([2, 1])

    with col1:
        markets = st.multiselect(
            "Select Markets",
            ["US", "DE", "IN"],
            default=["US", "DE", "IN"],
            key="signal_markets"
        )

    with col2:
        signal_type = st.selectbox(
            "Signal Type",
            ["All", "STRONG BUY", "BUY"]
        )

    if st.button("🚀 Generate Signals", type="primary"):
        with st.spinner("Analyzing markets..."):
            signals = components["signals"].generate_signals(markets=markets)

            for market, market_signals in signals.items():
                if not market_signals:
                    continue

                # Filter by signal type
                if signal_type != "All":
                    market_signals = [s for s in market_signals if s["signal_status"] == signal_type]

                if not market_signals:
                    continue

                flag = {"US": "🇺🇸", "DE": "🇩🇪", "IN": "🇮🇳"}.get(market, "🌐")
                currency = {"US": "$", "DE": "€", "IN": "₹"}.get(market, "$")

                st.markdown(f"## {flag} {MARKETS[market].name}")

                for i, sig in enumerate(market_signals[:5]):
                    with st.expander(f"{'🟢' if sig['signal_status'] == 'STRONG BUY' else '🟡'} "
                                   f"{sig['symbol']} - {sig['signal_status']} (Score: {sig['signal_score']})"):

                        col1, col2, col3 = st.columns(3)

                        with col1:
                            st.markdown("**📊 Current**")
                            st.write(f"Price: {currency}{sig['current_price']:,.2f}")
                            st.write(f"RSI: {sig['rsi']:.1f}")
                            st.write(f"Trend: {'✅ UP' if sig['uptrend'] else '❌ DOWN'}")

                        with col2:
                            st.markdown("**💰 Trade Setup**")
                            st.write(f"Entry: {currency}{sig['ideal_entry']:,.2f}")
                            st.write(f"Stop: {currency}{sig['stop_loss']:,.2f}")
                            st.write(f"Target: {currency}{sig['target_1']:,.2f}")

                        with col3:
                            st.markdown("**📈 Risk/Reward**")
                            st.write(f"R:R: {sig['risk_reward']:.2f}")
                            st.write(f"Setup: {sig['setup_type']}")
                            st.write(f"ATR%: {sig['atr_pct']:.2f}%")


# ============================================================
# ANALYSIS PAGE
# ============================================================

elif page == "📈 Analysis":
    st.title("📈 Stock Analysis")

    col1, col2 = st.columns([2, 1])

    with col1:
        symbol = st.text_input(
            "Enter Symbol",
            value="NVDA",
            help="US: NVDA, AAPL | Germany: SAP.DE | India: TCS.NS"
        ).upper()

    with col2:
        st.markdown("**Examples:**")
        st.markdown("🇺🇸 NVDA, AAPL, MSFT")
        st.markdown("🇩🇪 SAP.DE, BMW.DE")
        st.markdown("🇮🇳 TCS.NS, RELIANCE.NS")

    if st.button("🔍 Analyze", type="primary"):
        with st.spinner(f"Analyzing {symbol}..."):
            # Get data
            df = components["fetcher"].get_stock_data(symbol, "6mo")

            if df.empty:
                st.error(f"No data found for {symbol}")
            else:
                info = components["fetcher"].get_stock_info(symbol)
                result = components["analyzer"].analyze_stock(df, symbol)

                market = components["fetcher"].detect_market(symbol)
                market_info = MARKETS[market]
                currency = {"USD": "$", "EUR": "€", "INR": "₹"}.get(market_info.currency, "$")
                flag = {"US": "🇺🇸", "DE": "🇩🇪", "IN": "🇮🇳"}.get(market, "🌐")

                # Header
                st.markdown(f"## {flag} {info.get('name', symbol)}")
                st.markdown(f"**Sector:** {info.get('sector', 'N/A')} | "
                           f"**Market:** {market_info.name} | "
                           f"**Currency:** {market_info.currency}")

                # Metrics
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Price", f"{currency}{result['current_price']:,.2f}")
                col2.metric("Signal", result['signal_status'])
                col3.metric("Score", f"{result['signal_score']}/100")
                col4.metric("R:R Ratio", f"{result['risk_reward']:.2f}")

                st.markdown("---")

                # Trade setup
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("### 💰 Trade Setup")
                    setup_data = {
                        "Level": ["Entry", "Stop Loss", "Target 1", "Target 2"],
                        "Price": [
                            f"{currency}{result['ideal_entry']:,.2f}",
                            f"{currency}{result['stop_loss']:,.2f}",
                            f"{currency}{result['target_1']:,.2f}",
                            f"{currency}{result['target_2']:,.2f}",
                        ],
                        "Change": [
                            "-",
                            f"-{result.get('stop_loss_pct', 0):.1f}%",
                            f"+{result.get('target_1_pct', 0):.1f}%",
                            f"+{result.get('target_2_pct', 0):.1f}%",
                        ]
                    }
                    st.table(pd.DataFrame(setup_data))

                with col2:
                    st.markdown("### 📊 Indicators")
                    indicators = {
                        "Indicator": ["RSI", "ATR%", "Rel Volume", "Setup Type", "Trend"],
                        "Value": [
                            f"{result['rsi']:.1f}",
                            f"{result['atr_pct']:.2f}%",
                            f"{result.get('rel_volume', 0):.2f}",
                            result['setup_type'],
                            "BULLISH ✅" if result['uptrend'] else "BEARISH ❌",
                        ]
                    }
                    st.table(pd.DataFrame(indicators))


# ============================================================
# SCANNER PAGE
# ============================================================

elif page == "🔍 Scanner":
    st.title("🔍 Global Stock Scanner")

    markets = st.multiselect(
        "Select Markets to Scan",
        ["US", "DE", "IN"],
        default=["US", "DE", "IN"],
        key="scanner_markets"
    )

    top_n = st.slider("Top stocks per market", 5, 30, 15)

    if st.button("🔍 Run Scanner", type="primary"):
        with st.spinner("Scanning markets..."):
            components["universe"].rank_stocks(markets=markets, top_n_per_market=top_n)

            for market in markets:
                df = components["universe"].get_market_report(market)

                if df.empty:
                    continue

                flag = {"US": "🇺🇸", "DE": "🇩🇪", "IN": "🇮🇳"}.get(market, "🌐")

                st.markdown(f"## {flag} {MARKETS[market].name}")

                display_cols = ["symbol", "name", "sector", "price", "composite_score",
                               "momentum_20d", "momentum_5d", "returns_3m", "rel_volume"]

                st.dataframe(
                    df.head(top_n)[[c for c in display_cols if c in df.columns]],
                    use_container_width=True
                )


# ============================================================
# BACKTEST PAGE
# ============================================================

elif page == "📉 Backtest":
    st.title("📉 Strategy Backtester")

    symbols_input = st.text_area(
        "Symbols (one per line)",
        "NVDA\nAAPL\nMSFT\nSAP.DE\nTCS.NS",
        height=150
    )

    col1, col2 = st.columns(2)
    with col1:
        period = st.selectbox("Period", ["6mo", "1y", "2y"], index=1)
    with col2:
        initial_capital = st.number_input("Initial Capital ($)", value=50000, step=5000)

    if st.button("🚀 Run Backtest", type="primary"):
        symbols = [s.strip().upper() for s in symbols_input.split("\n") if s.strip()]

        with st.spinner("Running backtest..."):
            bt = Backtester(capital=initial_capital)
            results = bt.run(symbols, period)

            # Results
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total P&L", f"${results.total_pnl:,.2f}")
            col2.metric("Win Rate", f"{results.win_rate:.1f}%")
            col3.metric("Profit Factor", f"{results.profit_factor:.2f}")
            col4.metric("Max Drawdown", f"{results.max_drawdown:.1f}%")

            # Trade details
            if results.trades:
                st.markdown("### Trade Details")
                trades_data = [{
                    "Symbol": t.symbol,
                    "Entry": f"${t.entry_price:.2f}",
                    "Exit": f"${t.exit_price:.2f}",
                    "P&L": f"${t.pnl:.2f}",
                    "Return": f"{t.pnl_pct:.1f}%",
                    "Reason": t.exit_reason,
                } for t in results.trades]
                st.dataframe(pd.DataFrame(trades_data), use_container_width=True)


# ============================================================
# CALCULATOR PAGE
# ============================================================

elif page == "📐 Calculator":
    st.title("📐 Position Size Calculator")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Trade Details")
        currency = st.selectbox("Currency", ["USD ($)", "EUR (€)", "INR (₹)"])
        entry = st.number_input("Entry Price", value=100.0, step=1.0)
        stop = st.number_input("Stop Loss", value=95.0, step=1.0)

    with col2:
        st.markdown("### Account Details")
        account = st.number_input("Account Size", value=50000.0, step=1000.0)
        risk_pct = st.slider("Risk %", 0.5, 3.0, 1.5, 0.1)

    if st.button("📊 Calculate", type="primary"):
        risk_per_share = entry - stop

        if risk_per_share > 0:
            max_risk = account * (risk_pct / 100)
            shares = int(max_risk / risk_per_share)
            value = shares * entry

            curr_symbol = {"USD ($)": "$", "EUR (€)": "€", "INR (₹)": "₹"}.get(currency, "$")

            col1, col2, col3 = st.columns(3)
            col1.metric("Shares to Buy", f"{shares:,}")
            col2.metric("Position Value", f"{curr_symbol}{value:,.2f}")
            col3.metric("Risk Amount", f"{curr_symbol}{max_risk:,.2f}")

            st.success(f"Buy {shares} shares at {curr_symbol}{entry:.2f} with stop at {curr_symbol}{stop:.2f}")
        else:
            st.error("Stop loss must be below entry price")


# ============================================================
# UNIVERSE PAGE
# ============================================================

elif page == "⚙️ Universe":
    st.title("⚙️ Universe Management")

    tab1, tab2 = st.tabs(["📋 View Universe", "🔄 Update Universe"])

    with tab1:
        universe = components["universe"].load_universe()

        if universe:
            for market, symbols in universe.items():
                flag = {"US": "🇺🇸", "DE": "🇩🇪", "IN": "🇮🇳"}.get(market, "🌐")

                with st.expander(f"{flag} {MARKETS[market].name} - {len(symbols)} stocks"):
                    cols = st.columns(4)
                    for i, symbol in enumerate(symbols):
                        cols[i % 4].write(symbol)
        else:
            st.warning("No universe found. Click 'Update Universe' to create one.")

    with tab2:
        markets = st.multiselect(
            "Markets to Update",
            ["US", "DE", "IN"],
            default=["US", "DE", "IN"],
            key="update_markets"
        )

        top_n = st.slider("Top stocks per market", 10, 30, 20, key="update_top")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("⚡ Quick Update (Faster)", type="secondary"):
                with st.spinner("Updating universe..."):
                    components["universe"].quick_update(markets=markets, top_n_per_market=min(top_n, 15))
                    st.success("Universe updated!")
                    st.rerun()

        with col2:
            if st.button("🔄 Full Update (More Thorough)", type="primary"):
                with st.spinner("Updating universe (this may take a while)..."):
                    components["universe"].update_universe(markets=markets, top_n_per_market=top_n)
                    st.success("Universe updated!")
                    st.rerun()


# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("📚 [Documentation]()")
st.sidebar.markdown("🐛 [Report Issue]()")
st.sidebar.markdown(f"*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*")
