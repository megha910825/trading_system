# 📈 Global Swing Trading System

## Complete Trading Solution for US, German & Indian Markets

> **Automated stock trading assistant that scans 200+ stocks across 3 international markets to find the best swing trading opportunities.**

**Goal:** 4% monthly returns (~48% yearly) through systematic swing trading with strict risk management.

---

## 🌍 Supported Markets

| Market | Exchange | Currency | Trading Hours (Local) | Trading Hours (CET) |
|--------|----------|----------|-----------------------|---------------------|
| 🇺🇸 USA | NYSE/NASDAQ | USD ($) | 09:30 - 16:00 ET | 15:30 - 22:00 |
| 🇩🇪 Germany | XETRA | EUR (€) | 09:00 - 17:30 CET | 09:00 - 17:30 |
| 🇮🇳 India | NSE/BSE | INR (₹) | 09:15 - 15:30 IST | 04:45 - 11:00 |

---

## 📋 Table of Contents

1. [Features](#-features)
2. [Installation](#-installation)
3. [Quick Start](#-quick-start)
4. [Web Dashboard](#-web-dashboard)
5. [Daily Workflow](#-daily-workflow)
6. [Command Reference](#-command-reference)
7. [Understanding Signals](#-understanding-signals)
8. [How to Place Trades](#-how-to-place-trades)
9. [Trade Management](#-trade-management)
10. [Backtesting](#-backtesting)
11. [Alerts Setup](#-alerts-setup)
12. [Environment Variables](#-environment-variables)
13. [For Germany-Based Traders](#-for-germany-based-traders)
14. [Architecture](#-architecture)
15. [Changelog](#-changelog)
16. [FAQ](#-frequently-asked-questions)
17. [Troubleshooting](#-troubleshooting)
18. [Glossary](#-glossary)

---

## ✨ Features

### 📊 Multi-Market Scanning
- Scans S&P 500, NASDAQ 100, DAX 40, MDAX, NIFTY 50 stocks
- Automatic stock ranking based on momentum, volume, and trend
- Dynamic universe updates weekly — top 50 per market

### 🎯 Signal Generation
- STRONG BUY / BUY / WATCH signal classification
- Precise entry, stop loss, and target prices
- Risk/reward ratio calculation
- Setup types: Pullback, Momentum, Breakout

### 🌐 Web Dashboard (12 Pages)
- Real-time market overview and regime analysis
- Interactive charts with technical indicators
- Stock scanner with custom filters
- Trade journal with position tracking
- Portfolio management and performance metrics
- Position size calculator and risk management

### 🧪 Backtesting
- Test strategies on 6mo–5yr of historical data
- Compare performance across markets
- Win rate, profit factor, max drawdown analysis

### 📱 Alerts & Automation
- Telegram and email notifications
- Alpaca broker integration (paper & live)
- Scheduled daily workflows

---

## 🔧 Installation

### Requirements

| Item | Requirement |
|------|-------------|
| Python | 3.10+ |
| RAM | 4GB minimum (8GB recommended) |
| Storage | 500MB free space |
| Internet | Stable connection |

### Setup

```bash
# Clone or download to ~/trading_system
cd ~/trading_system

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Verify installation
python -c "import config; print('✓ Config OK')"
python main.py signals
```

---

## 🚀 Quick Start

### Generate Signals
```bash
python main.py signals                # All markets
python main.py signals --market US    # US only
python main.py signals --market DE    # Germany only
python main.py signals --market IN    # India only
```

### Analyze a Stock
```bash
python main.py analyze -s NVDA        # US stock
python main.py analyze -s SAP.DE      # German stock
python main.py analyze -s TCS.NS      # Indian stock
```

### Launch Dashboard
```bash
python run_dashboard.py
# Open browser: http://localhost:8501
```

### Verify Modules
```bash
python -c "
for mod in ['global_data_fetcher', 'global_signal_generator',
            'global_universe_manager', 'position_manager',
            'broker_api', 'alert_system', 'technical_analyzer', 'backtester']:
    __import__(mod); print(f'✓ {mod}')
"
```

---

## 🌐 Web Dashboard

Launch with `python run_dashboard.py` → http://localhost:8501

| Page | Purpose |
|------|---------|
| 📊 Dashboard | Account overview, market summary, quick scan |
| 🔍 Scanner | Scan stocks with custom filters |
| 📈 Analysis | Detailed charts and technical analysis |
| 🎯 Signals | Generate trading signals by market |
| 📉 Backtest | Test strategies on historical data |
| 📐 Calculator | Position size and risk calculator |
| 📋 Trade Journal | Log trades, track open positions, close trades |
| 📊 Performance | Monthly progress, statistics, goal tracking |
| 💼 Portfolio | Holdings, allocation, risk overview |
| 📅 Earnings | Upcoming earnings calendar |
| ⚙️ Settings | System configuration |
| 🌍 Market Regime | SPY/VIX analysis, regime classification |

---

## 📅 Daily Workflow

### Schedule (CET for Germany-Based Traders)

| Time | Action | Command |
|------|--------|---------|
| 08:00 | Morning routine — check India signals, prep German market | `python daily_workflow.py morning` |
| 09:00 | 🇩🇪 German market opens — place orders, set stops | |
| 11:00 | 🇮🇳 India market closes — review positions | |
| 12:00 | Midday check — review German positions | `python daily_workflow.py midday` |
| 15:30 | 🇺🇸 US market opens — generate US signals | `python daily_workflow.py afternoon` |
| 17:30 | 🇩🇪 German market closes | |
| 20:00 | Evening summary — log trades, review | `python daily_workflow.py evening` |
| 22:00 | 🇺🇸 US market closes — final review | |
| **Sunday** | Weekly update | `python main.py quick-update` |

---

## 📖 Command Reference

### Signals & Analysis
```bash
python main.py signals                 # All markets
python main.py signals --market DE     # Germany only
python main.py scan                    # Full stock scan
python main.py analyze -s SYMBOL       # Analyze specific stock
python main.py status                  # Market status
```

### Universe Management
```bash
python main.py quick-update            # Quick update (~10 min)
python main.py update-universe         # Full update (~30 min)
python main.py universe                # Show current stocks
python main.py universe --market DE    # Show German stocks
```

### Backtesting
```bash
python backtester.py run               # Test current universe
python backtester.py compare           # Compare all markets
python backtester.py german            # German stocks only
python backtester.py run -p 2y         # 2-year backtest
python backtester.py run --save        # Save results
```

### Daily Workflow
```bash
python daily_workflow.py schedule      # Show schedule
python daily_workflow.py morning       # Morning routine
python daily_workflow.py midday        # Midday check
python daily_workflow.py afternoon     # Afternoon (US open)
python daily_workflow.py evening       # Evening summary
```

### Symbol Format

| Market | Format | Examples |
|--------|--------|----------|
| 🇺🇸 US | `SYMBOL` | NVDA, AAPL, MSFT |
| 🇩🇪 Germany | `SYMBOL.DE` | SAP.DE, BMW.DE, SIE.DE |
| 🇮🇳 India | `SYMBOL.NS` | TCS.NS, RELIANCE.NS |

---

## 🎯 Understanding Signals

### Signal Types

| Signal | Meaning | Action |
|--------|---------|--------|
| 🟢 STRONG BUY | Excellent setup, high confidence | Consider trading |
| 🟡 BUY | Good setup, moderate confidence | Consider trading |
| 🟠 WATCH | Potential setup forming | Add to watchlist |
| 🔴 AVOID | Poor setup or risky | Do not trade |

### Reading a Signal
```
🎯 STRONG BUY: NVDA (Score: 75/100)
   Setup: PULLBACK | Trend: BULLISH ✓

   💰 TRADE SETUP:
   Entry:    $235.00
   Stop:     $223.00 (-5.1%)
   Target 1: $259.00 (+10.2%)
   Target 2: $275.00 (+17.0%)
   R:R: 2.0 | Shares: 62
```

### Key Indicators

| Indicator | Good Range | Meaning |
|-----------|------------|---------|
| Score | 70–100 | Signal confidence |
| RSI | 30–70 | Momentum (below 30 = oversold, above 70 = overbought) |
| R:R | ≥ 2.0 | Risk $1 to make $2+ |

---

## 💰 How to Place Trades

### 1. Get the Signal
```bash
python main.py signals --market US
```

### 2. Position Sizing (Automatic)
```
Risk Amount  = Account × 1.5% = $50,000 × 0.015 = $750
Risk/Share   = Entry - Stop   = $235 - $223      = $12
Shares       = $750 ÷ $12    = 62 shares
```

### 3. Place Orders in Your Broker
1. **Buy:** Limit order at entry price
2. **Stop Loss:** Stop order at stop price (set immediately!)
3. **Alert:** Set price alert at Target 1

### 4. Manage the Trade
- **Target 1 hit:** Sell half, move stop to breakeven
- **Target 2 hit:** Sell remaining shares
- **Stop hit:** Accept the loss, move on

### Order Types

| Type | Use For |
|------|---------|
| Limit | Buying at a specific price or better |
| Stop | Stop loss — auto-sell if price drops |
| Market | Immediate execution (price may slip) |

---

## 📊 Trade Management

### Trading Rules
- **Always** use stop loss — set immediately after buy fills
- Max **1.5% risk** per trade
- Max **8 positions** total, **4 per market**
- Max **25%** of account in one stock
- Sell 50% at Target 1, move stop to breakeven

### Trade Journal
```bash
# CLI interface
python trade_journal.py

# Or use the dashboard
python run_dashboard.py   # → Trade Journal tab
```

The dashboard provides the full trade lifecycle: log entries, track open positions with live P&L, and close trades with exit reason tracking.

---

## 🧪 Backtesting

### Running Backtests
```bash
python backtester.py run              # Default 1-year
python backtester.py run -p 6mo       # 6 months
python backtester.py run -p 2y        # 2 years
python backtester.py compare          # All markets side by side
python backtester.py run --save       # Save results to data/
```

### Interpreting Results

| Metric | Excellent | Good | Acceptable | Poor |
|--------|-----------|------|------------|------|
| Win Rate | 60%+ | 55%+ | 50–55% | <50% |
| Profit Factor | 2.0+ | 1.5+ | 1.2–1.5 | <1.2 |
| Max Drawdown | <10% | <15% | 15–20% | >25% |

### Exit Reasons

| Reason | Meaning |
|--------|---------|
| TARGET_1 | First profit target hit ✅ |
| TARGET_2 | Second profit target hit ✅ |
| STOP_LOSS | Stop loss triggered ❌ |
| TIME_EXIT | Max holding period (10 days) ⏱️ |
| TRAIL_STOP | Trailing stop triggered 📉 |

---

## 🔔 Alerts Setup

### Telegram (Recommended)
1. Message `@BotFather` on Telegram → `/newbot` → copy API token
2. Message `@userinfobot` → copy your Chat ID
3. Add to `.env`:
   ```
   TELEGRAM_BOT_TOKEN=your-token
   TELEGRAM_CHAT_ID=your-chat-id
   ```
4. Test: `python alert_system.py test`

### Email (Gmail)
1. Enable 2-Step Verification in Google Account
2. Create App Password (Security → App Passwords)
3. Add to `.env`:
   ```
   EMAIL_SENDER=your@gmail.com
   EMAIL_PASSWORD=xxxx xxxx xxxx xxxx
   EMAIL_RECEIVER=your@gmail.com
   ```

---

## 🔐 Environment Variables

Add to `.env` file or shell profile (`~/.bashrc` / `~/.zshrc`):

```bash
# Broker (Alpaca) — leave empty for simulation mode
ALPACA_API_KEY=""
ALPACA_SECRET_KEY=""
ALPACA_BASE_URL="https://paper-api.alpaca.markets"

# Telegram Notifications (optional)
TELEGRAM_BOT_TOKEN="your-bot-token"
TELEGRAM_CHAT_ID="your-chat-id"

# Email Notifications (optional)
EMAIL_SENDER="your@gmail.com"
EMAIL_PASSWORD="your-app-password"
EMAIL_RECEIVER="recipient@gmail.com"
```

---

## 🇩🇪 For Germany-Based Traders

### Your Advantage
Trade 3 markets across different time zones from a single system:
- **04:45–11:00** 🇮🇳 India (morning opportunity)
- **09:00–17:30** 🇩🇪 Germany (primary market)
- **15:30–22:00** 🇺🇸 USA (afternoon/evening)
- **Overlaps:** India+Germany 09:00–11:00, Germany+USA 15:30–17:30

### Recommended Allocation

| Market | Positions | Portfolio % | Priority |
|--------|-----------|-------------|----------|
| 🇩🇪 Germany | 4 | 50% | Primary |
| 🇺🇸 USA | 3 | 40% | Secondary |
| 🇮🇳 India | 1–2 | 10% | Optional |

### Broker Options

| Broker | Markets | Fees |
|--------|---------|------|
| Interactive Brokers | All 3 markets | Low, varies |
| Trade Republic | DE + US | €1/trade |
| Scalable Capital | DE + US | €0.99/trade |

### Tax Notes
- **Abgeltungssteuer:** ~26.4% (25% + Soli + church tax)
- **Freibetrag:** €1,000/year tax-free
- Use Freistellungsauftrag with your broker

---

## 🏗️ Architecture

### File Structure
```
trading_system/
├── config.py                  # System configuration (account, risk, indicators)
├── market_config.py           # Market definitions (US, DE, IN stocks & parameters)
├── main.py                    # CLI entry point
│
├── global_data_fetcher.py     # Multi-market data fetching (yfinance)
├── global_universe_manager.py # Stock universe ranking & selection
├── global_signal_generator.py # Signal generation across markets
│
├── technical_analyzer.py      # Technical analysis (EMA, RSI, MACD, etc.)
├── fundamental_analyzer.py    # Fundamental analysis
├── combined_analyzer.py       # Technical + fundamental combined
├── market_regime.py           # SPY/VIX regime classification
│
├── position_manager.py        # Position sizing & risk management
├── trade_journal.py           # Trade logging (SQLite)
├── performance_tracker.py     # Monthly performance tracking
├── backtester.py              # Strategy backtesting
│
├── alert_system.py            # Telegram & email alerts
├── broker_api.py              # Alpaca broker integration
├── earnings_calendar.py       # Earnings date tracking
├── insider_tracker.py         # Insider transaction tracking
│
├── dashboard.py               # Streamlit web dashboard (12 pages)
├── run_dashboard.py           # Dashboard launcher
├── daily_workflow.py          # Scheduled daily routines
├── scheduler.py               # Task scheduling
├── logging_setup.py           # Centralized logging with colored output
│
├── data/                      # Universe JSON, rankings CSV, caches
├── logs/                      # Application logs
├── .env                       # API keys (not committed)
└── requirements.txt           # Python dependencies
```

### Core Modules

| Module | Purpose |
|--------|---------|
| `GlobalDataFetcher` | Fetch OHLCV data, stock info for any market |
| `GlobalUniverseManager` | Rank & select top stocks per market |
| `GlobalSignalGenerator` | Generate signals from universe |

---

## 📝 Changelog

### May 2026 — System Overhaul
- **Config fixes:** Added 15+ missing config fields (`SCREENING_CRITERIA`, `MAX_POSITION_SIZE_PCT`, `DAILY_LOSS_LIMIT`, `EXIT_RULES`, `INDICATORS`, `THRESHOLDS`, etc.)
- **MarketInfo extended:** Added `min_price`, `max_price`, `min_market_cap`, `min_volume` to market definitions
- **Universe expanded:** Changed default from 15 → 50 stocks per market (145 total)
- **Error handling:** Replaced all bare `except:` blocks with `except Exception as e:` + logging
- **Legacy cleanup:** Removed duplicate modules (`data_fetcher.py`, `universe_manager.py`, `signal_generator.py`, `stock_screener.py`) — use `global_*` versions instead
- **Logging:** Created `logging_setup.py` with colored console + file output
- **Dashboard fixes:** Fixed earnings calendar syntax error, timezone comparison, trade journal methods, performance tracker integration, market regime attribute errors
- **Trade Journal UI:** Added close trade functionality with exit price/reason in dashboard

---

## ❓ Frequently Asked Questions

**How much money do I need?**
Configured for $50,000 (changeable in `config.py`). Minimum $5,000 recommended for proper position sizing.

**Is this guaranteed to make money?**
No. This targets 4% monthly returns but losses are possible. Always use stop losses.

**Do I need to watch the market all day?**
No — swing trading. Check signals morning/evening, place orders, set stops. Trades last 2–10 days.

**How do I update the stock list?**
Run `python main.py quick-update` weekly. The system auto-selects top momentum stocks.

**Can I add my own stocks?**
Edit stock lists in `market_config.py` (`US_STOCKS`, `GERMAN_STOCKS`, `INDIAN_STOCKS`).

**What does "PULLBACK" setup mean?**
Stock is trending up but temporarily dipped to support — a buying opportunity.

**Should I trade every signal?**
No. Focus on STRONG BUY signals. Start with 1–3 positions.

---

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| `python not found` | Reinstall Python, ensure "Add to PATH" is checked |
| Package install fails | `python -m pip install --upgrade pip && pip install -r requirements.txt` |
| No data for symbol | Check format (NVDA, SAP.DE, TCS.NS). Yahoo Finance may be temporarily down |
| Dashboard won't start | `pip install streamlit --upgrade && streamlit run dashboard.py` |
| Slow performance | Use `quick-update` instead of full update; reduce stock count |
| Stale universe | `python main.py quick-update` to refresh rankings |
| Config errors | `python -c "import config; print('OK')"` to verify |

---

## 📚 Glossary

| Term | Definition |
|------|------------|
| ATR | Average True Range — daily price movement measure |
| Drawdown | Decline from peak to trough |
| EMA | Exponential Moving Average |
| Entry/Exit | Price at which you buy/sell |
| Limit Order | Buy/sell at a specific price or better |
| Momentum | Strength of price movement in one direction |
| Position Size | Number of shares to buy |
| Profit Factor | Gross profit ÷ gross loss |
| Pullback | Temporary dip in an uptrend |
| R:R | Risk/Reward ratio |
| RSI | Relative Strength Index (overbought/oversold) |
| Stop Loss | Auto-sell order to limit losses |
| Support/Resistance | Price levels where stock tends to reverse |
| Swing Trading | Holding stocks for days to weeks |
| Universe | List of stocks being tracked |
| Win Rate | Percentage of profitable trades |

---

## ⚠️ Risk Disclaimer

Trading involves substantial risk of loss. This software is for educational and informational purposes only — not financial advice. Never invest money you cannot afford to lose. Past performance does not guarantee future results. Start with paper trading.

---

## 🎓 Getting Started Path

1. **Week 1:** Paper trade — run signals daily, track what you would have traded
2. **Week 2–3:** Small positions — half size, STRONG BUY only, max 2 positions
3. **Week 4+:** Normal trading — full size, up to 8 positions, weekly journal review
