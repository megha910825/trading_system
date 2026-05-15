"""Trading Dashboard - Streamlit Web UI"""

import streamlit as st
import pandas as pd
from datetime import datetime

from data_fetcher import DataFetcher
from technical_analyzer import TechnicalAnalyzer
from stock_screener import StockScreener
from signal_generator import SignalGenerator
from position_manager import PositionManager
from backtester import Backtester
import config

st.set_page_config(page_title="Trading System", page_icon="📈", layout="wide")

# Initialize
@st.cache_resource
def init():
    return {
        "fetcher": DataFetcher(),
        "analyzer": TechnicalAnalyzer(),
        "screener": StockScreener(),
        "gen": SignalGenerator(),
        "pm": PositionManager(),
        "bt": Backtester(),
    }

c = init()

# Sidebar
st.sidebar.title("🎯 Trading System")
st.sidebar.markdown(f"**Target: {config.MONTHLY_TARGET*100}% Monthly**")
page = st.sidebar.radio("Navigate", ["Dashboard", "Scanner", "Analysis", "Signals", "Backtest", "Calculator"])

# Dashboard
if page == "Dashboard":
    st.title("📊 Trading Dashboard")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Account", f"${config.ACCOUNT_SIZE:,}")
    col2.metric("Monthly Target", f"${config.ACCOUNT_SIZE * config.MONTHLY_TARGET:,.0f}")
    col3.metric("Risk/Trade", f"{config.RISK_PER_TRADE*100}%")
    col4.metric("Max Positions", config.MAX_POSITIONS)

    st.markdown("---")
    st.subheader("Quick Scan")

    if st.button("🔍 Scan Top Stocks"):
        with st.spinner("Scanning..."):
            results = c["screener"].screen_stocks(config.STOCK_UNIVERSE[:15])
            qualified = results[results["qualified"]]
            if not qualified.empty:
                st.dataframe(qualified[["symbol", "signal_score", "signal_status",
                                       "current_price", "ideal_entry", "risk_reward"]])
            else:
                st.info("No qualified stocks found")

# Scanner
elif page == "Scanner":
    st.title("🔍 Stock Screener")

    num = st.slider("Stocks to scan", 5, 30, 15)

    if st.button("Run Screener"):
        with st.spinner("Screening..."):
            results = c["screener"].screen_stocks(config.STOCK_UNIVERSE[:num])
            st.dataframe(results)

# Analysis
elif page == "Analysis":
    st.title("📈 Stock Analysis")

    symbol = st.text_input("Symbol", "NVDA").upper()

    if st.button("Analyze"):
        with st.spinner(f"Analyzing {symbol}..."):
            df = c["fetcher"].get_stock_data(symbol, "6mo")
            if not df.empty:
                result = c["analyzer"].analyze_stock(df, symbol)

                col1, col2, col3 = st.columns(3)
                col1.metric("Price", f"${result.get('current_price', 0):.2f}")
                col2.metric("Signal", result.get('signal_status'))
                col3.metric("Score", f"{result.get('signal_score', 0)}/100")

                st.markdown("---")
                st.subheader("Trading Levels")

                levels = pd.DataFrame({
                    "Level": ["Entry", "Stop Loss", "Target 1", "Target 2"],
                    "Price": [
                        f"${result.get('ideal_entry', 0):.2f}",
                        f"${result.get('stop_loss', 0):.2f}",
                        f"${result.get('target_1', 0):.2f}",
                        f"${result.get('target_2', 0):.2f}",
                    ]
                })
                st.table(levels)

                st.markdown("---")
                st.subheader("Indicators")
                col1, col2, col3 = st.columns(3)
                col1.metric("RSI", f"{result.get('rsi', 0):.1f}")
                col2.metric("ATR%", f"{result.get('atr_pct', 0):.2f}%")
                col3.metric("R:R", f"{result.get('risk_reward', 0):.2f}")
            else:
                st.error(f"No data for {symbol}")

# Signals
elif page == "Signals":
    st.title("🎯 Trading Signals")

    if st.button("Generate Signals"):
        with st.spinner("Generating..."):
            signals = c["gen"].generate_signals(config.STOCK_UNIVERSE[:15])

            if signals:
                st.success(f"Found {len(signals)} signals")
                st.dataframe(c["gen"].get_summary())

                st.markdown("---")
                st.subheader("Top Signal")
                st.code(c["gen"].format_alert(signals[0]))
            else:
                st.info("No signals found")

# Backtest
elif page == "Backtest":
    st.title("📉 Backtester")

    symbols = st.text_area("Symbols (one per line)", "NVDA\nAMD\nAAPL\nMSFT\nMETA")
    period = st.selectbox("Period", ["6mo", "1y", "2y"])

    if st.button("Run Backtest"):
        sym_list = [s.strip().upper() for s in symbols.split("\n") if s.strip()]

        with st.spinner("Backtesting..."):
            results = c["bt"].run(sym_list, period)

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total P&L", f"${results.total_pnl:,.2f}")
            col2.metric("Win Rate", f"{results.win_rate:.1f}%")
            col3.metric("Profit Factor", f"{results.profit_factor:.2f}")
            col4.metric("Max Drawdown", f"{results.max_drawdown:.1f}%")

            st.markdown("---")
            st.subheader("Trade Details")

            if results.trades:
                trades_data = [{
                    "Symbol": t.symbol,
                    "Entry": f"${t.entry_price:.2f}",
                    "Exit": f"${t.exit_price:.2f}",
                    "P&L": f"${t.pnl:.2f}",
                    "Return": f"{t.pnl_pct:.1f}%",
                    "Reason": t.exit_reason,
                } for t in results.trades]
                st.dataframe(pd.DataFrame(trades_data))

# Calculator
elif page == "Calculator":
    st.title("📐 Position Calculator")

    col1, col2 = st.columns(2)

    with col1:
        entry = st.number_input("Entry Price ($)", value=100.0, step=1.0)
        stop = st.number_input("Stop Loss ($)", value=95.0, step=1.0)

    with col2:
        account = st.number_input("Account Size ($)", value=50000.0, step=1000.0)
        risk_pct = st.slider("Risk %", 0.5, 3.0, 1.5, 0.1)

    if st.button("Calculate"):
        risk_per_share = entry - stop

        if risk_per_share > 0:
            max_risk = account * (risk_pct / 100)
            shares = int(max_risk / risk_per_share)
            value = shares * entry

            col1, col2, col3 = st.columns(3)
            col1.metric("Shares", shares)
            col2.metric("Position Value", f"${value:,.2f}")
            col3.metric("Risk Amount", f"${max_risk:,.2f}")
        else:
            st.error("Stop must be below entry")
