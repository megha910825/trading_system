# 📈 Global Swing Trading System

## Complete Trading Solution for US, German & Indian Markets

> **Automated stock trading assistant that scans 200+ stocks across 3 international markets to find the best swing trading opportunities.**

**Goal:** 4% monthly returns (~48% yearly) through systematic swing trading with strict risk management.

---

## 🌍 Supported Markets

| Market | Exchange | Currency | Trading Hours (Local) | Trading Hours (CET) |
|--------|----------|----------|-----------------------|---------------------|
| 🇺🇸 USA | NYSE/NASDAQ | USD ($) | 09:30 – 16:00 ET | 15:30 – 22:00 |
| 🇩🇪 Germany | XETRA | EUR (€) | 09:00 – 17:30 CET | 09:00 – 17:30 |
| 🇮🇳 India | NSE/BSE | INR (₹) | 09:15 – 15:30 IST | 04:45 – 11:00 |

---

## 📋 Table of Contents

1. [Features](#-features)
2. [Docker Setup (Recommended)](#-docker-setup-recommended)
3. [Local Installation](#-local-installation)
4. [Quick Start](#-quick-start)
5. [Web Dashboard](#-web-dashboard)
6. [Weekend Investing Strategy](#-weekend-investing-mi-momentum-strategy)
7. [Daily Workflow](#-daily-workflow)
8. [Command Reference](#-command-reference)
9. [Understanding Signals](#-understanding-signals)
10. [How to Place Trades](#-how-to-place-trades)
11. [Trade Management](#-trade-management)
12. [Backtesting](#-backtesting)
13. [Alerts Setup](#-alerts-setup)
14. [Environment Variables](#-environment-variables)
15. [For Germany-Based Traders](#-for-germany-based-traders)
16. [Architecture](#-architecture)
17. [Changelog](#-changelog)
18. [FAQ](#-frequently-asked-questions)
19. [Troubleshooting](#-troubleshooting)
20. [Glossary](#-glossary)

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

### 🌐 Web Dashboard (18 Pages)
- **Clean light-theme UI** (Inter + JetBrains Mono fonts)
- **Grouped sidebar navigation** — pages organised into 6 sections; two browser tabs can display different pages simultaneously via URL routing
- **ℹ️ Info toggle on every page** — collapsible help panel for new users
- Real-time market overview and regime analysis
- Interactive charts with technical indicators
- Stock scanner with custom filters
- Trade journal with full position lifecycle
- **Live Settings editor** — edit account size, risk %, screening criteria, exit rules in-browser; changes apply immediately
- Position size calculator and risk management
- Sector rotation rankings
- Walk-forward backtesting + Monte Carlo simulation
- Journal analytics (MAE/MFE, regime & setup breakdowns)
- **Weekend Investing (MI) strategy** — 8 presets, rebalance signals, universe ranking, backtest

### 🏆 Weekend Investing (MI) Strategy
- Full implementation of Alok Jain's Weekend Investing rotational momentum strategies
- 8 ready-to-use strategy presets (Mi-Top10, Mi-NNF10, Mi-EverGreen, Mi-20, Mi-25, Mi-30, Mi-35, Mi-ST-ATH)
- Multi-period momentum scoring (1M / 3M / 6M / 12M Rate of Change)
- Automatic BUY / SELL / HOLD / CASH rebalancing signals with equal-weight allocation
- Full universe ranking table, progress bar during scoring, walk-forward backtest

### 🧪 Backtesting
- Walk-forward validation across configurable windows
- Monte Carlo simulation for probability analysis
- Win rate, profit factor, max drawdown, Sharpe ratio

### 📱 Alerts & Automation
- Telegram and email notifications
- Alpaca broker integration (paper & live)
- Scheduled daily workflows via `automation/scheduler.py`

### 🐳 Docker-First Deployment
- Single-command startup with `docker compose up`
- Isolated environment — no Python version conflicts
- Named volumes for persistent data, cache, and logs
- Corporate proxy / SSL certificate support built-in

---

## 🐳 Docker Setup (Recommended)

### Prerequisites
- [Docker Engine](https://docs.docker.com/engine/install/) 24+
- [Docker Compose](https://docs.docker.com/compose/install/) v2.20+

### 1. Configure Environment

```bash
cp .env.example .env
# Edit .env and fill in your API keys
```

### 2. Build & Launch

```bash
# Dashboard only (default) — http://localhost:8501
docker compose up --build

# Dashboard + automated scheduler
docker compose --profile scheduler up --build

# Run in background
docker compose up -d --build
```

### 3. Available Run Modes

| Mode | Description | Command |
|------|-------------|---------|
| `dashboard` | Streamlit UI on port 8501 (default) | `docker compose up` |
| `scheduler` | Automated daily tasks | `docker compose --profile scheduler up` |
| `scanner` | One-shot stock scan | `docker compose run --rm dashboard scanner` |
| `signals` | One-shot signal generation | `docker compose run --rm dashboard signals` |
| `update` | One-shot universe update | `docker compose run --rm dashboard update` |
| `shell` | Interactive bash for debugging | `docker compose run --rm dashboard shell` |

### 4. Data Persistence

| Volume | Mounted at | Contents |
|--------|-----------|----------|
| `trading_data` | `/app/data` | Universe JSON, fundamentals/earnings cache |
| `trading_cache` | `/app/cache` | Price data cache |
| `trading_logs` | `/app/logs` | Application logs |

```bash
docker run --rm -v trading_data:/data busybox ls /data   # Browse volume
docker compose down                                        # Stop (keeps volumes)
docker compose down -v                                     # Stop + wipe all data
```

### 5. Corporate Proxy / SSL

If behind a corporate proxy (e.g., Zscaler / Zeiss), the compose file auto-mounts your host CA bundle:

```yaml
environment:
  CURL_CA_BUNDLE: /etc/ssl/certs/ca-certificates.crt
  REQUESTS_CA_BUNDLE: /etc/ssl/certs/ca-certificates.crt
  SSL_CERT_FILE: /etc/ssl/certs/ca-certificates.crt
volumes:
  - /etc/ssl/certs/ca-certificates.crt:/etc/ssl/certs/ca-certificates.crt:ro
```

No manual configuration needed.

### 6. Useful Docker Commands

```bash
docker compose ps                  # Container status + health
docker compose logs -f             # Stream live logs
docker compose logs --tail=50      # Last 50 log lines
docker compose down                # Stop containers
docker compose build               # Rebuild after code changes
docker compose cp dashboard.py dashboard:/app/dashboard.py   # Hot-patch a file
docker compose restart dashboard   # Restart without rebuild
```

---

## 💻 Local Installation

```bash
cd ~/trading_system
python -m venv venv
source venv/bin/activate      # Linux/Mac
pip install -r requirements.txt
python -c "import config; print('✓ Config OK')"
python main.py signals
```

---

## 🚀 Quick Start

```bash
# Docker (recommended)
docker compose up --build     # → open http://localhost:8501

# Local
python main.py signals        # All markets
python run_dashboard.py       # Launch dashboard
```

> **VS Code Remote SSH users:** Use the Ports tab → Forward Port 8501 to open the dashboard in your local browser.

---

## 🌐 Web Dashboard

### Navigation

The sidebar contains **6 groups** of clickable page links. Each page loads via a URL parameter (`?page=…`), so two browser tabs can show different pages at the same time.

| Group | Pages |
|-------|-------|
| 📊 Market | Overview, Market Regime, Signals, Fundamentals, Combined Analysis |
| 🔍 Research | Earnings Calendar, Insider Activity |
| 🔧 Tools | Stock Screener, Position Calculator, Signal Analysis, Sector Rotation |
| 💼 Portfolio | Portfolio, Trade Journal, Performance, Journal Analytics |
| 🚀 Strategies | Backtest Pro, Weekend Investing (MI) |
| ⚙️ System | Settings |

Every page has an **ℹ️ How to use this page** expander at the top — click to read what each control does.

### Pages

| Page | Purpose |
|------|---------|
| 🏠 Overview | Account metrics, live indices, quick multi-market scan |
| 📊 Market Regime | SPY/VIX regime, should-trade gate with confidence % |
| 🎯 Signals | Live multi-market signals, filterable by strength |
| 📈 Fundamentals | P/E, ROE, revenue growth, fundamental score |
| 🔀 Combined Analysis | Technical + fundamental score with trade quality (A+ to D) |
| 📅 Earnings Calendar | Upcoming earnings dates with risk flags |
| 👔 Insider Activity | Recent insider buy/sell transactions |
| 🔍 Stock Screener | Custom filter screener across all markets |
| 📋 Trade Journal | Log entries, manage open positions, close trades |
| 📊 Performance | Monthly P&L progress, win rate, stats |
| 💼 Portfolio | Open positions, allocation, cash summary |
| 📐 Position Calculator | Fixed-risk and ATR-based position sizing |
| 🔬 Signal Analysis | Score distribution charts — gauge market breadth |
| 🔄 Sector Rotation | US sector ETF relative strength vs SPY (1W / 1Mo / 3Mo) |
| 🧪 Backtest Pro | Walk-forward + Monte Carlo simulation |
| 📓 Journal Analytics | MAE/MFE, performance by regime & setup type |
| 🏆 Weekend Investing (MI) | Momentum rebalancing — 8 strategy presets |
| ⚙️ Settings | Live-editable config: account, risk, screener, exit rules |

### Settings Page

All key values are editable in-browser:
- **Account & Risk:** Account size, monthly target %, risk/trade %, max positions, daily loss limit
- **Screening Criteria:** Min market cap, min avg volume, ATR range
- **Exit Rules:** Stop-loss ATR multiplier, Target 1/2 ATR multipliers, max hold days

Click **💾 Save Changes** — values are written to `config.py` and apply to all pages immediately (no restart). API keys remain read-only; edit `.env` then `docker compose restart`.

---

## 🏆 Weekend Investing (MI) Momentum Strategy

Full implementation of [Alok Jain's Weekend Investing](https://weekendinvesting.com) rotational momentum system.

### How it works

**Momentum Score** (composite of 4 ROC periods):

```
Score = (ROC_1M + ROC_3M + ROC_6M + ROC_12M) / 4
```

- **Entry:** Buy top-N stocks by score at next market open (Monday for weekly; first trading day of month for monthly) at equal weight.
- **Exit:** Sell only when a stock drops out of the top-N at the next rebalancing date — no intra-period stop-loss.
- **Cash proxy:** When absolute momentum filter is active (Mi-25/Mi-30) and a stock's 6-month return is negative, park that slot in LIQUIDBEES.

### Strategy Presets

| Strategy | Universe | Slots | Rebalance | Special |
|----------|----------|-------|-----------|---------|
| Mi-Top10 | Nifty 50 | 10 | Weekly | — |
| Mi-NNF10 | Nifty Next 50 | 10 | Weekly | — |
| Mi-EverGreen | CNX 200 | 20 | Weekly | Risk-adjusted, 12-1 momentum |
| Mi-20 | MidSmall 400 | 20 | Weekly | — |
| Mi-25 | Smallcap 250 | 25 | Monthly | Cash filter (abs. momentum) |
| Mi-30 | CNX 500 | 30 | Monthly | Cash filter (abs. momentum) |
| Mi-35 | Smallcap 250 | 35 | Weekly | — |
| Mi-ST-ATH | CNX 500 | 15 | Weekly | ATH filter (within 10% of 52wk high) |

### Weekly Usage

1. Dashboard → **🏆 Weekend Investing (MI)**
2. Select strategy, enter capital, enter current holdings (comma-separated symbols)
3. Click **Generate Rebalance Signal**
4. Execute ✅ BUY and ❌ SELL at **Monday 9:15 AM IST**

Key rules: Never override a SELL. Equal weight every slot. Park 🟡 CASH slots in LIQUIDBEES.

### CLI

```bash
python strategies/weekend_investing_strategy.py --strategy Mi-35 --capital 500000
```

---

## 📅 Daily Workflow

| Time (CET) | Action |
|------------|--------|
| 08:00 | Morning — India signals, prep German market |
| 09:00 | 🇩🇪 German market opens — place orders |
| 11:00 | 🇮🇳 India closes — review positions |
| 15:30 | 🇺🇸 US opens — generate US signals |
| 17:30 | 🇩🇪 German market closes |
| 22:00 | 🇺🇸 US closes — log trades, review |
| **Sunday** | Weekly MI rebalance + universe update |

```bash
docker compose run --rm dashboard signals
docker compose run --rm dashboard update
```

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
python main.py universe --market IN    # Indian stocks
```

### Backtesting
```bash
python strategies/backtester.py run           # Test current universe
python strategies/backtester.py run -p 2y    # 2-year backtest
python strategies/backtester.py compare      # Compare all markets
```

### Weekend Investing
```bash
python strategies/weekend_investing_strategy.py --strategy Mi-Top10 --capital 500000
python strategies/weekend_investing_strategy.py --strategy Mi-35   --capital 1750000
```

### Daily Workflow
```bash
python automation/daily_workflow.py morning
python automation/daily_workflow.py midday
python automation/daily_workflow.py afternoon
python automation/daily_workflow.py evening
```

### Symbol Format

| Market | Format | Examples |
|--------|--------|----------|
| 🇺🇸 US | `SYMBOL` | NVDA, AAPL, MSFT |
| 🇩🇪 Germany | `SYMBOL.DE` | SAP.DE, BMW.DE, SIE.DE |
| 🇮🇳 India | `SYMBOL.NS` | TCS.NS, RELIANCE.NS |

---

## 🎯 Understanding Signals

| Signal | Meaning | Action |
|--------|---------|--------|
| 🟢 STRONG BUY | Excellent setup, high confidence | Consider trading |
| 🟡 BUY | Good setup, moderate confidence | Consider trading |
| 🟠 WATCH | Potential setup forming | Add to watchlist |
| 🔴 AVOID | Poor setup or risky | Do not trade |

### Combined Analysis Trade Quality

| Grade | Score | Meaning |
|-------|-------|---------|
| A+ | ≥ 80 (both ≥ 70) | Excellent — full position |
| A  | ≥ 70 (both ≥ 60) | Good — standard position |
| B  | ≥ 60 (both ≥ 50) | Acceptable — reduced size |
| C  | ≥ 50 | Marginal — small size only |
| D  | < 50 | Avoid |

---

## 💰 How to Place Trades

1. **Get the signal** — 🎯 Signals page or `python main.py signals`
2. **Size the position** — 📐 Position Calculator (auto-enforces 1.5% risk, 25% cap)
3. **Place orders** — Limit buy at entry; stop immediately after fill
4. **Target 1 hit** — Sell half, move stop to breakeven
5. **Target 2 hit** — Sell remainder

---

## 📊 Trade Management

- **Always** set stop loss immediately after buy fills
- Max **1.5% risk** per trade, max **8 positions** total, max **25%** in one stock
- Log every trade in 📋 Trade Journal for performance tracking

---

## 🧪 Backtesting

Go to **🧪 Backtest Pro** in the dashboard — enter symbols, period, walk-forward windows, Monte Carlo count → **Run Backtest**.

A strategy is viable only if Walk-Forward CAGR > 0 **and** Monte Carlo 5th-percentile is still positive.

| Metric | Excellent | Good | Acceptable | Poor |
|--------|-----------|------|------------|------|
| Win Rate | 60%+ | 55%+ | 50–55% | <50% |
| Profit Factor | 2.0+ | 1.5+ | 1.2–1.5 | <1.2 |
| Max Drawdown | <10% | <15% | 15–20% | >25% |

---

## 🔔 Alerts Setup

### Telegram
1. Message `@BotFather` → `/newbot` → copy token
2. Message `@userinfobot` → copy Chat ID
3. Add to `.env`: `TELEGRAM_BOT_TOKEN=…` and `TELEGRAM_CHAT_ID=…`

### Email (Gmail)
1. Enable 2-Step Verification → create App Password
2. Add to `.env`: `EMAIL_SENDER`, `EMAIL_PASSWORD`, `EMAIL_RECEIVER`

---

## 🔐 Environment Variables

```bash
# Broker (Alpaca) — leave empty for simulation mode
ALPACA_API_KEY=""
ALPACA_SECRET_KEY=""
ALPACA_BASE_URL="https://paper-api.alpaca.markets"

# Telegram (optional)
TELEGRAM_BOT_TOKEN="your-bot-token"
TELEGRAM_CHAT_ID="your-chat-id"

# Email (optional)
EMAIL_SENDER="your@gmail.com"
EMAIL_PASSWORD="your-app-password"
EMAIL_RECEIVER="recipient@gmail.com"
```

`.env` is never committed to git. With Docker it loads automatically via `env_file: .env`.

---

## 🇩🇪 For Germany-Based Traders

| Market | Positions | Portfolio % | Priority |
|--------|-----------|-------------|----------|
| 🇩🇪 Germany | 4 | 50% | Primary |
| 🇺🇸 USA | 3 | 40% | Secondary |
| 🇮🇳 India | 1–2 | 10% | Optional |

**Brokers:** Interactive Brokers (all 3 markets), Trade Republic (DE + US, €1/trade), Scalable Capital (DE + US, €0.99/trade)

**Tax:** Abgeltungssteuer ~26.4%; Freibetrag €1,000/year — file Freistellungsauftrag with your broker.

---

## 🏗️ Architecture

### Module Structure

```
trading_system/
│
├── config.py                  # System configuration (account, risk, params)
├── market_config.py           # Market definitions (US/DE/IN stocks & params)
├── main.py                    # CLI entry point
├── dashboard.py               # Streamlit web dashboard (18 pages, light theme)
├── run_dashboard.py           # Local dashboard launcher
├── logging_setup.py           # Centralized logging
│
├── core/                      # Data fetching & universe management
│   ├── data_fetcher.py
│   ├── global_data_fetcher.py
│   └── global_universe_manager.py
│
├── analysis/                  # Market & stock analysis
│   ├── technical_analyzer.py
│   ├── fundamental_analyzer.py
│   ├── combined_analyzer.py
│   ├── market_regime.py
│   └── sector_rotation.py
│
├── signals/                   # Signal generation
│   ├── signal_generator.py
│   └── global_signal_generator.py
│
├── screening/                 # Stock screeners
│   ├── stock_screener.py
│   └── fundamental_screener.py
│
├── portfolio/                 # Position & trade management
│   ├── position_manager.py
│   ├── trade_journal.py
│   ├── performance_tracker.py
│   ├── broker_api.py
│   └── alert_system.py
│
├── strategies/                # Trading strategies
│   ├── backtester.py
│   ├── swing_trading_system.py
│   └── weekend_investing_strategy.py
│
├── research/                  # Market research
│   ├── earnings_calendar.py
│   └── insider_tracker.py
│
├── automation/                # Scheduling & daily routines
│   ├── scheduler.py
│   └── daily_workflow.py
│
├── Dockerfile                 # python:3.11-slim-bookworm, non-root trader user
├── docker-compose.yml         # Dashboard + optional scheduler profile
├── entrypoint.sh              # Multi-mode container entrypoint
├── .dockerignore
│
├── data/                      # Universe JSON, rankings, fundamentals cache
├── logs/                      # Application logs
├── cache/                     # Price data cache
├── .env                       # API keys (not committed)
└── requirements.txt
```

### Import Architecture

`dashboard.py` and `main.py` add all 8 subdirectories to `sys.path` at startup. Every module continues to use flat imports (`from technical_analyzer import TechnicalAnalyzer`) with no changes — no package-style imports needed.

---

## 📝 Changelog

### May 2026 — Module Restructure, UI Overhaul, Weekend Investing

#### 📁 Module Restructure
- All Python modules organised into 8 subdirectories: `core/`, `analysis/`, `signals/`, `screening/`, `portfolio/`, `strategies/`, `research/`, `automation/`
- `sys.path` bootstrap in `dashboard.py` and `main.py` — all flat imports continue to work unchanged
- `__init__.py` added to each subdirectory

#### 🌐 Dashboard — Navigation & UX
- **Replaced dropdown** with grouped HTML sidebar nav — all 18 pages visible at a glance, direct click
- **URL-based routing** (`?page=…`) — two browser tabs can show different pages simultaneously
- **ℹ️ Info expander** on every page — collapsible help panel explaining controls and recommended actions
- Renamed nav group "Intel" → "Research"

#### ⚙️ Settings Page — Live Editable
- Account size, risk %, monthly target, screening criteria, exit rules all editable in-browser
- **Save Changes** writes to `config.py` and updates the live module in-memory — effective immediately across all pages
- API key fields remain read-only

#### 🏆 Weekend Investing (MI) Strategy
- New `strategies/weekend_investing_strategy.py` with 8 presets
- Multi-period ROC scoring, absolute momentum cash proxy, ATH filter
- Dashboard page: 4 tabs — Rebalance Now, Universe Ranking, Backtest, Strategy Guide

#### 🎨 Dashboard UI — Light Theme
- Switched from dark to clean light theme (`#f0f4f8` background, white cards)
- Fixed all widget label, input, and markdown text color issues
- Removed overly-broad CSS selectors (`.stApp *`, bare `span`, `[class*="css"]`) that caused Streamlit internal elements to render visibly
- Multiselect tags: blue chip style
- Expander text scoped via `[data-testid="stMarkdownContainer"]` — internal Streamlit icons unaffected

#### 🐳 Docker
- `Dockerfile`: `python:3.11-slim-bookworm`, non-root `trader` user, `--trusted-host` pip flags
- `docker-compose.yml`: named volumes, CA bundle mount (Zscaler/corporate proxy), health check, optional `scheduler` profile
- `entrypoint.sh`: `dashboard` | `scheduler` | `scanner` | `signals` | `update` | `shell`

---

## ❓ Frequently Asked Questions

**How do I run it?**
`docker compose up --build` → http://localhost:8501 (forward port 8501 via VS Code Ports tab if on remote SSH).

**How do I change account size or risk settings?**
⚙️ Settings page → edit in-browser → Save Changes.

**How do I use the Weekend Investing strategy?**
🏆 Weekend Investing (MI) → select strategy → enter capital → Generate Rebalance Signal → execute at Monday 9:15 AM IST.

**How much money do I need?**
Configured for $50,000 (changeable in Settings). Minimum $5,000 recommended.

**Do I need to watch the market all day?**
No — swing trading. Check signals morning/evening. Trades last 2–10 days.

**How do I update the stock list?**
`docker compose run --rm dashboard update` (weekly).

**Can I add my own stocks?**
Edit `market_config.py` (`US_STOCKS`, `GERMAN_STOCKS`, `INDIAN_STOCKS`).

---

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| Dashboard not reachable | VS Code Remote SSH: forward port 8501 via the Ports tab |
| SSL / certificate errors | Ensure `/etc/ssl/certs/ca-certificates.crt` exists on host; auto-mounted by compose |
| `No result returned` in Combined Analysis | SSL issue — `docker compose down && docker compose up` |
| Container exits immediately | `docker compose logs` — likely missing `.env` |
| Settings save fails | Check `config.py` is writable; container needs write access to `/app/config.py` |
| Import errors after restructure | `sys.path` bootstrap resolves all subdirectory imports automatically |
| No data for symbol | Check format (NVDA, SAP.DE, TCS.NS). Yahoo Finance may be temporarily unavailable |
| Package install fails (local) | `pip install --upgrade pip && pip install -r requirements.txt` |

---

## 📚 Glossary

| Term | Definition |
|------|------------|
| ATR | Average True Range — daily price movement measure |
| Absolute Momentum | Exit to cash when asset's own past return turns negative |
| Drawdown | Decline from peak to trough |
| EMA | Exponential Moving Average |
| LIQUIDBEES | Indian liquid ETF used as a cash proxy in MI strategies |
| MAE | Maximum Adverse Excursion — worst drawdown during a live trade |
| MFE | Maximum Favourable Excursion — best gain reached during a live trade |
| MI Strategy | Weekend Investing — Alok Jain's rotational momentum strategy |
| Momentum | Rate of Change (ROC) of price over 1M, 3M, 6M, 12M periods |
| Position Size | Shares to buy, sized to risk exactly N% of account |
| Profit Factor | Gross profit ÷ gross loss |
| Pullback | Temporary dip in an uptrend — buying opportunity |
| R:R | Risk/Reward ratio |
| ROC | Rate of Change — % price change over a given period |
| RSI | Relative Strength Index |
| Sharpe Ratio | Return per unit of risk |
| Stop Loss | Auto-sell order that caps loss to a pre-defined amount |
| Swing Trading | Holding stocks for days to weeks |
| Universe | List of stocks actively tracked and scored |
| Walk-Forward | Out-of-sample backtest on data the model never trained on |
| Win Rate | Percentage of trades that closed profitably |

---

## ⚠️ Risk Disclaimer

Trading involves substantial risk of loss. This software is for educational and informational purposes only — not financial advice. Never invest money you cannot afford to lose. Past performance does not guarantee future results. Start with paper trading.

---

## 🎓 Getting Started Path

1. **Day 1:** `docker compose up --build` → explore dashboard, read ℹ️ help on each page
2. **Week 1:** Paper trade — run signals daily, log what you would have traded in the Trade Journal
3. **Week 2–3:** Small live positions — half size, STRONG BUY + A/A+ grade only, max 2 positions
4. **Week 4+:** Normal trading — full size, up to 8 positions, weekly journal review + MI rebalance
