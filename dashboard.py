#!/usr/bin/env python3
"""
Trading Dashboard - Global Markets Version
Supports: US, Germany, India
Compatible with updated TechnicalAnalyzer
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Page config - MUST be first
st.set_page_config(
    page_title="Global Trading System",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ═══════════════════════════════════════════════════════════════
# IMPORTS WITH ERROR HANDLING
# ═══════════════════════════════════════════════════════════════

# Import config
try:
    import config
except ImportError:
    st.error("❌ config.py not found!")
    st.stop()

# Import modules with error handling
modules_status = {}

try:
    from global_data_fetcher import GlobalDataFetcher
    modules_status["GlobalDataFetcher"] = True
except ImportError as e:
    modules_status["GlobalDataFetcher"] = False
    GlobalDataFetcher = None

try:
    from technical_analyzer import TechnicalAnalyzer
    modules_status["TechnicalAnalyzer"] = True
except ImportError as e:
    modules_status["TechnicalAnalyzer"] = False
    TechnicalAnalyzer = None

try:
    from global_universe_manager import GlobalUniverseManager
    modules_status["GlobalUniverseManager"] = True
except ImportError as e:
    modules_status["GlobalUniverseManager"] = False
    GlobalUniverseManager = None

try:
    from global_signal_generator import GlobalSignalGenerator
    modules_status["GlobalSignalGenerator"] = True
except ImportError as e:
    modules_status["GlobalSignalGenerator"] = False
    GlobalSignalGenerator = None

try:
    from position_manager import PositionManager
    modules_status["PositionManager"] = True
except ImportError as e:
    modules_status["PositionManager"] = False
    PositionManager = None

try:
    from backtester import Backtester
    modules_status["Backtester"] = True
except ImportError as e:
    modules_status["Backtester"] = False
    Backtester = None

try:
    from market_config import MARKETS, get_market_status
    modules_status["market_config"] = True
except ImportError as e:
    modules_status["market_config"] = False
    # Fallback market config
    class MarketInfo:
        def __init__(self, name, currency):
            self.name = name
            self.currency = currency

    MARKETS = {
        "US": MarketInfo("United States", "USD"),
        "DE": MarketInfo("Germany", "EUR"),
        "IN": MarketInfo("India", "INR"),
    }

    def get_market_status():
        return {"US": "Open", "DE": "Open", "IN": "Open"}

try:
    import yfinance as yf
    modules_status["yfinance"] = True
except ImportError:
    modules_status["yfinance"] = False
    yf = None


# ═══════════════════════════════════════════════════════════════
# CUSTOM CSS
# ═══════════════════════════════════════════════════════════════

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
    .signal-strong-buy { background-color: #00C851; color: white; padding: 0.2rem 0.5rem; border-radius: 0.25rem; }
    .signal-buy { background-color: #ffbb33; color: black; padding: 0.2rem 0.5rem; border-radius: 0.25rem; }
    .signal-watch { background-color: #33b5e5; color: white; padding: 0.2rem 0.5rem; border-radius: 0.25rem; }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def safe_get(data: dict, key: str, default=None):
    """Safely get value from dict with fallback keys"""
    if key in data:
        return data[key]

    # Fallback mappings for different key names
    fallbacks = {
        'uptrend': ['trend', 'above_50_ema', 'above_ema50'],
        'ideal_entry': ['entry', 'entry_price'],
        'risk_reward': ['rr_1', 'rr', 'reward_risk'],
        'atr_pct': ['atr_percent', 'atr_percentage'],
        'rel_volume': ['relative_volume', 'volume_ratio'],
    }

    if key in fallbacks:
        for fallback_key in fallbacks[key]:
            if fallback_key in data:
                return data[fallback_key]

    return default


def is_uptrend(sig: dict) -> bool:
    """Determine if signal indicates uptrend"""
    # Check multiple possible keys
    if 'uptrend' in sig:
        return sig['uptrend']
    if 'trend' in sig:
        return sig['trend'] == 'BULLISH'
    if 'above_50_ema' in sig:
        return sig['above_50_ema']
    if 'above_ema50' in sig:
        return sig['above_ema50']
    return False


def get_entry_price(sig: dict) -> float:
    """Get entry price from signal"""
    return sig.get('ideal_entry', sig.get('entry', sig.get('entry_price', sig.get('current_price', 0))))


def get_risk_reward(sig: dict) -> float:
    """Get risk/reward ratio from signal"""
    return sig.get('risk_reward', sig.get('rr_1', sig.get('rr', 0)))


def get_atr_pct(sig: dict) -> float:
    """Get ATR percentage from signal"""
    return sig.get('atr_pct', sig.get('atr_percent', 0))


def get_rel_volume(sig: dict) -> float:
    """Get relative volume from signal"""
    return sig.get('rel_volume', sig.get('relative_volume', sig.get('volume_ratio', 0)))


@st.cache_data(ttl=300)
def fetch_stock_data_direct(symbol: str, period: str = "6mo") -> pd.DataFrame:
    """Fetch stock data directly using yfinance"""
    if not yf:
        return pd.DataFrame()

    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period)
        if not df.empty:
            df.columns = df.columns.str.lower()
        return df
    except Exception as e:
        return pd.DataFrame()


# ═══════════════════════════════════════════════════════════════
# INITIALIZE COMPONENTS
# ═══════════════════════════════════════════════════════════════

@st.cache_resource
def init_components():
    """Initialize all components with error handling"""
    components = {}

    if GlobalDataFetcher:
        try:
            components["fetcher"] = GlobalDataFetcher()
        except:
            components["fetcher"] = None
    else:
        components["fetcher"] = None

    if TechnicalAnalyzer:
        try:
            components["analyzer"] = TechnicalAnalyzer()
        except:
            components["analyzer"] = None
    else:
        components["analyzer"] = None

    if GlobalUniverseManager:
        try:
            components["universe"] = GlobalUniverseManager()
        except:
            components["universe"] = None
    else:
        components["universe"] = None

    if GlobalSignalGenerator:
        try:
            components["signals"] = GlobalSignalGenerator()
        except:
            components["signals"] = None
    else:
        components["signals"] = None

    if PositionManager:
        try:
            components["positions"] = PositionManager()
        except:
            components["positions"] = None
    else:
        components["positions"] = None

    if Backtester:
        try:
            components["backtester"] = Backtester()
        except:
            components["backtester"] = None
    else:
        components["backtester"] = None

    return components


components = init_components()


# ═══════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════

st.sidebar.title("🌍 Global Trading System")

# Account info
monthly_target = getattr(config, 'MONTHLY_TARGET', 0.05)
st.sidebar.markdown(f"**Target: {monthly_target*100:.0f}% Monthly**")

# Market status
st.sidebar.markdown("---")
st.sidebar.subheader("📊 Market Status")

try:
    status = get_market_status()
    for code, stat in status.items():
        market = MARKETS[code]
        flag = {"US": "🇺🇸", "DE": "🇩🇪", "IN": "🇮🇳"}.get(code, "🌐")
        market_name = market.name if hasattr(market, 'name') else code
        st.sidebar.markdown(f"{flag} **{market_name}**: {stat}")
except Exception as e:
    st.sidebar.warning("Could not load market status")

st.sidebar.markdown("---")

# Module status
with st.sidebar.expander("⚙️ System Status"):
    for module, status in modules_status.items():
        icon = "✅" if status else "❌"
        st.write(f"{icon} {module}")

st.sidebar.markdown("---")

# Navigation
page = st.sidebar.radio(
    "Navigate",
    ["🏠 Dashboard", "🎯 Signals", "📈 Analysis", "🔍 Scanner",
     "📉 Backtest", "📐 Calculator", "⚙️ Universe"]
)


# ═══════════════════════════════════════════════════════════════
# DASHBOARD PAGE
# ═══════════════════════════════════════════════════════════════

if page == "🏠 Dashboard":
    st.title("🌍 Global Trading Dashboard")

    # Metrics row
    account_size = getattr(config, 'ACCOUNT_SIZE', 50000)
    risk_per_trade = getattr(config, 'RISK_PER_TRADE', 0.015)
    max_positions = getattr(config, 'MAX_POSITIONS', 8)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Account Size", f"${account_size:,}")
    col2.metric("Monthly Target", f"${account_size * monthly_target:,.0f}")
    col3.metric("Risk/Trade", f"{risk_per_trade*100:.1f}%")
    col4.metric("Max Positions", max_positions)

    st.markdown("---")

    # Market overview
    st.subheader("📊 Market Overview")

    col1, col2, col3 = st.columns(3)

    # US Market
    with col1:
        st.markdown("### 🇺🇸 United States")
        if components["fetcher"]:
            try:
                summary = components["fetcher"].get_market_summary("US")
                for idx, data in summary.items():
                    change_color = "green" if data["change_pct"] >= 0 else "red"
                    st.markdown(f"**{idx}**: {data['price']:,.2f} "
                               f"<span style='color:{change_color}'>({data['change_pct']:+.2f}%)</span>",
                               unsafe_allow_html=True)
            except:
                st.info("Market data unavailable")
        else:
            st.info("Data fetcher not available")

    # Germany Market
    with col2:
        st.markdown("### 🇩🇪 Germany")
        if components["fetcher"]:
            try:
                summary = components["fetcher"].get_market_summary("DE")
                for idx, data in summary.items():
                    change_color = "green" if data["change_pct"] >= 0 else "red"
                    st.markdown(f"**{idx}**: {data['price']:,.2f} "
                               f"<span style='color:{change_color}'>({data['change_pct']:+.2f}%)</span>",
                               unsafe_allow_html=True)
            except:
                st.info("Market data unavailable")
        else:
            st.info("Data fetcher not available")

    # India Market
    with col3:
        st.markdown("### 🇮🇳 India")
        if components["fetcher"]:
            try:
                summary = components["fetcher"].get_market_summary("IN")
                for idx, data in summary.items():
                    change_color = "green" if data["change_pct"] >= 0 else "red"
                    st.markdown(f"**{idx}**: {data['price']:,.2f} "
                               f"<span style='color:{change_color}'>({data['change_pct']:+.2f}%)</span>",
                               unsafe_allow_html=True)
            except:
                st.info("Market data unavailable")
        else:
            st.info("Data fetcher not available")

    st.markdown("---")

    # Quick signals
    st.subheader("🎯 Quick Signal Scan")

    market_selection = st.multiselect(
        "Select Markets",
        ["US", "DE", "IN"],
        default=["US", "DE", "IN"]
    )

    if st.button("🔍 Generate Signals", type="primary"):
        if components["signals"]:
            with st.spinner("Analyzing stocks..."):
                try:
                    signals = components["signals"].generate_signals(markets=market_selection)

                    for market, market_signals in signals.items():
                        if market_signals:
                            flag = {"US": "🇺🇸", "DE": "🇩🇪", "IN": "🇮🇳"}.get(market, "🌐")
                            market_name = MARKETS[market].name if hasattr(MARKETS[market], 'name') else market
                            st.markdown(f"### {flag} {market_name} - {len(market_signals)} Signals")

                            # Build dataframe with safe key access
                            df_data = []
                            for sig in market_signals:
                                df_data.append({
                                    "symbol": sig.get('symbol', 'N/A'),
                                    "name": sig.get('name', 'N/A'),
                                    "signal_status": sig.get('signal_status', 'N/A'),
                                    "signal_score": sig.get('signal_score', 0),
                                    "current_price": sig.get('current_price', 0),
                                    "ideal_entry": get_entry_price(sig),
                                    "stop_loss": sig.get('stop_loss', 0),
                                    "target_1": sig.get('target_1', 0),
                                    "risk_reward": get_risk_reward(sig),
                                })

                            df = pd.DataFrame(df_data)
                            st.dataframe(df, use_container_width=True)
                except Exception as e:
                    st.error(f"Error generating signals: {e}")
        else:
            st.warning("Signal generator not available. Check if global_signal_generator.py exists.")


# ═══════════════════════════════════════════════════════════════
# SIGNALS PAGE
# ═══════════════════════════════════════════════════════════════

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
        if components["signals"]:
            with st.spinner("Analyzing markets..."):
                try:
                    signals = components["signals"].generate_signals(markets=markets)

                    for market, market_signals in signals.items():
                        if not market_signals:
                            continue

                        # Filter by signal type
                        if signal_type != "All":
                            market_signals = [s for s in market_signals if s.get("signal_status") == signal_type]

                        if not market_signals:
                            continue

                        flag = {"US": "🇺🇸", "DE": "🇩🇪", "IN": "🇮🇳"}.get(market, "🌐")
                        currency = {"US": "$", "DE": "€", "IN": "₹"}.get(market, "$")
                        market_name = MARKETS[market].name if hasattr(MARKETS[market], 'name') else market

                        st.markdown(f"## {flag} {market_name}")

                        for i, sig in enumerate(market_signals[:5]):
                            signal_icon = '🟢' if sig.get('signal_status') == 'STRONG BUY' else '🟡'

                            with st.expander(f"{signal_icon} {sig.get('symbol', 'N/A')} - "
                                           f"{sig.get('signal_status', 'N/A')} (Score: {sig.get('signal_score', 0)})"):

                                col1, col2, col3 = st.columns(3)

                                with col1:
                                    st.markdown("**📊 Current**")
                                    st.write(f"Price: {currency}{sig.get('current_price', 0):,.2f}")
                                    st.write(f"RSI: {sig.get('rsi', 0):.1f}")
                                    trend_status = is_uptrend(sig)
                                    st.write(f"Trend: {'✅ UP' if trend_status else '❌ DOWN'}")

                                with col2:
                                    st.markdown("**💰 Trade Setup**")
                                    st.write(f"Entry: {currency}{get_entry_price(sig):,.2f}")
                                    st.write(f"Stop: {currency}{sig.get('stop_loss', 0):,.2f}")
                                    st.write(f"Target: {currency}{sig.get('target_1', 0):,.2f}")

                                with col3:
                                    st.markdown("**📈 Risk/Reward**")
                                    st.write(f"R:R: {get_risk_reward(sig):.2f}")
                                    st.write(f"Setup: {sig.get('setup_type', 'N/A')}")
                                    st.write(f"ATR%: {get_atr_pct(sig):.2f}%")
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.warning("Signal generator not available.")


# ═══════════════════════════════════════════════════════════════
# ANALYSIS PAGE
# ═══════════════════════════════════════════════════════════════

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
            df = None
            if components["fetcher"]:
                try:
                    df = components["fetcher"].get_stock_data(symbol, "6mo")
                except:
                    df = fetch_stock_data_direct(symbol, "6mo")
            else:
                df = fetch_stock_data_direct(symbol, "6mo")

            if df is None or df.empty:
                st.error(f"No data found for {symbol}")
            else:
                # Get info
                info = {}
                if components["fetcher"]:
                    try:
                        info = components["fetcher"].get_stock_info(symbol)
                    except:
                        pass

                # Analyze
                result = {}
                if components["analyzer"]:
                    try:
                        result = components["analyzer"].analyze_stock(df, symbol)
                    except Exception as e:
                        st.error(f"Analysis error: {e}")
                        result = {"symbol": symbol, "error": str(e)}

                if result.get("error"):
                    st.error(f"Error: {result['error']}")
                else:
                    # Detect market
                    if ".DE" in symbol:
                        market = "DE"
                        currency = "€"
                        flag = "🇩🇪"
                    elif ".NS" in symbol:
                        market = "IN"
                        currency = "₹"
                        flag = "🇮🇳"
                    else:
                        market = "US"
                        currency = "$"
                        flag = "🇺🇸"

                    market_info = MARKETS.get(market)
                    market_name = market_info.name if hasattr(market_info, 'name') else market

                    # Header
                    st.markdown(f"## {flag} {info.get('name', symbol)}")
                    st.markdown(f"**Sector:** {info.get('sector', 'N/A')} | "
                               f"**Market:** {market_name} | "
                               f"**Currency:** {currency}")

                    # Metrics
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("Price", f"{currency}{result.get('current_price', 0):,.2f}")
                    col2.metric("Signal", result.get('signal_status', 'N/A'))
                    col3.metric("Score", f"{result.get('signal_score', 0)}/100")
                    col4.metric("R:R Ratio", f"{get_risk_reward(result):.2f}")

                    st.markdown("---")

                    # Trade setup
                    col1, col2 = st.columns(2)

                    with col1:
                        st.markdown("### 💰 Trade Setup")

                        entry = get_entry_price(result)
                        stop = result.get('stop_loss', 0)
                        target1 = result.get('target_1', 0)
                        target2 = result.get('target_2', 0)
                        current = result.get('current_price', 0)

                        # Calculate percentages
                        stop_pct = ((stop - current) / current * 100) if current else 0
                        t1_pct = ((target1 - current) / current * 100) if current else 0
                        t2_pct = ((target2 - current) / current * 100) if current else 0

                        setup_data = {
                            "Level": ["Entry", "Stop Loss", "Target 1", "Target 2"],
                            "Price": [
                                f"{currency}{entry:,.2f}",
                                f"{currency}{stop:,.2f}",
                                f"{currency}{target1:,.2f}",
                                f"{currency}{target2:,.2f}",
                            ],
                            "Change": [
                                "-",
                                f"{stop_pct:.1f}%",
                                f"+{t1_pct:.1f}%",
                                f"+{t2_pct:.1f}%",
                            ]
                        }
                        st.table(pd.DataFrame(setup_data))

                    with col2:
                        st.markdown("### 📊 Indicators")

                        trend_status = is_uptrend(result)

                        indicators = {
                            "Indicator": ["RSI", "ADX", "ATR%", "Rel Volume", "Setup Type", "Trend"],
                            "Value": [
                                f"{result.get('rsi', 0):.1f}",
                                f"{result.get('adx', 0):.1f}",
                                f"{get_atr_pct(result):.2f}%",
                                f"{get_rel_volume(result):.2f}",
                                result.get('setup_type', 'N/A'),
                                "BULLISH ✅" if trend_status else "BEARISH ❌",
                            ]
                        }
                        st.table(pd.DataFrame(indicators))


# ═══════════════════════════════════════════════════════════════
# SCANNER PAGE
# ═══════════════════════════════════════════════════════════════

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
        if components["universe"]:
            with st.spinner("Scanning markets..."):
                try:
                    components["universe"].rank_stocks(markets=markets, top_n_per_market=top_n)

                    for market in markets:
                        df = components["universe"].get_market_report(market)

                        if df is None or df.empty:
                            continue

                        flag = {"US": "🇺🇸", "DE": "🇩🇪", "IN": "🇮🇳"}.get(market, "🌐")
                        market_name = MARKETS[market].name if hasattr(MARKETS[market], 'name') else market

                        st.markdown(f"## {flag} {market_name}")

                        display_cols = ["symbol", "name", "sector", "price", "composite_score",
                                       "momentum_20d", "momentum_5d", "returns_3m", "rel_volume"]

                        available_cols = [c for c in display_cols if c in df.columns]
                        st.dataframe(df.head(top_n)[available_cols], use_container_width=True)
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.warning("Universe manager not available.")


# ═══════════════════════════════════════════════════════════════
# BACKTEST PAGE
# ═══════════════════════════════════════════════════════════════

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

        if components["backtester"]:
            with st.spinner("Running backtest..."):
                try:
                    bt = Backtester(capital=initial_capital) if Backtester else None

                    if bt:
                        results = bt.run(symbols, period)

                        # Results
                        col1, col2, col3, col4 = st.columns(4)
                        col1.metric("Total P&L", f"${results.total_pnl:,.2f}")
                        col2.metric("Win Rate", f"{results.win_rate:.1f}%")
                        col3.metric("Profit Factor", f"{results.profit_factor:.2f}")
                        col4.metric("Max Drawdown", f"{results.max_drawdown:.1f}%")

                        # Trade details
                        if hasattr(results, 'trades') and results.trades:
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
                except Exception as e:
                    st.error(f"Backtest error: {e}")
        else:
            st.warning("Backtester not available.")
            st.info("Run from command line: `python backtester.py compare`")


# ═══════════════════════════════════════════════════════════════
# CALCULATOR PAGE
# ═══════════════════════════════════════════════════════════════

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


# ═══════════════════════════════════════════════════════════════
# UNIVERSE PAGE
# ═══════════════════════════════════════════════════════════════

elif page == "⚙️ Universe":
    st.title("⚙️ Universe Management")

    tab1, tab2 = st.tabs(["📋 View Universe", "🔄 Update Universe"])

    with tab1:
        if components["universe"]:
            try:
                universe = components["universe"].load_universe()

                if universe:
                    for market, symbols in universe.items():
                        flag = {"US": "🇺🇸", "DE": "🇩🇪", "IN": "🇮🇳"}.get(market, "🌐")
                        market_name = MARKETS[market].name if hasattr(MARKETS[market], 'name') else market

                        with st.expander(f"{flag} {market_name} - {len(symbols)} stocks"):
                            cols = st.columns(4)
                            for i, symbol in enumerate(symbols):
                                cols[i % 4].write(symbol)
                else:
                    st.warning("No universe found. Click 'Update Universe' to create one.")
            except Exception as e:
                st.error(f"Error loading universe: {e}")
        else:
            st.warning("Universe manager not available.")

    with tab2:
        markets = st.multiselect(
            "Markets to Update",
            ["US", "DE", "IN"],
            default=["US", "DE", "IN"],
            key="update_markets"
        )

        top_n = st.slider("Top stocks per market", 10, 30, 20, key="update_top")

        if components["universe"]:
            col1, col2 = st.columns(2)

            with col1:
                if st.button("⚡ Quick Update (Faster)", type="secondary"):
                    with st.spinner("Updating universe..."):
                        try:
                            components["universe"].quick_update(markets=markets, top_n_per_market=min(top_n, 15))
                            st.success("Universe updated!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")

            with col2:
                if st.button("🔄 Full Update (More Thorough)", type="primary"):
                    with st.spinner("Updating universe (this may take a while)..."):
                        try:
                            components["universe"].update_universe(markets=markets, top_n_per_market=top_n)
                            st.success("Universe updated!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")
        else:
            st.warning("Universe manager not available.")


# ═══════════════════════════════════════════════════════════════
# FOOTER
# ═══════════════════════════════════════════════════════════════

st.sidebar.markdown("---")
st.sidebar.markdown(f"*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*")
