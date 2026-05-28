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
2. [Docker Setup (Recommended)](#-docker-setup-recommended)
3. [Local Installation](#-local-installation)
4. [Quick Start](#-quick-start)
5. [Web Dashboard](#-web-dashboard)
6. [Daily Workflow](#-daily-workflow)
7. [Command Reference](#-command-reference)
8. [Understanding Signals](#-understanding-signals)
9. [How to Place Trades](#-how-to-place-trades)
10. [Trade Management](#-trade-management)
11. [Backtesting](#-backtesting)
12. [Alerts Setup](#-alerts-setup)
13. [Environment Variables](#-environment-variables)
14. [For Germany-Based Traders](#-for-germany-based-traders)
15. [Architecture](#-architecture)
16. [Changelog](#-changelog)
17. [FAQ](#-frequently-asked-questions)
18. [Troubleshooting](#-troubleshooting)
19. [Glossary](#-glossary)

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

### 🌐 Web Dashboard (17 Pages)
- Professional dark-theme UI (Inter + JetBrains Mono fonts, Bloomberg-style)
- Real-time market overview and regime analysis
- Interactive charts with technical indicators
- Stock scanner with custom filters
- Trade journal with full position lifecycle
- Portfolio management and performance metrics
- Position size calculator and risk management
- Sector rotation rankings
- Walk-forward backtesting + Monte Carlo simulation
- Journal analytics (MAE/MFE, regime & setup breakdowns)

### 🧪 Backtesting
- Walk-forward validation across configurable windows
- Monte Carlo simulation for probability analysis
- Win rate, profit factor, max drawdown, Sharpe ratio

### 📱 Alerts & Automation
- Telegram and email notifications
- Alpaca broker integration (paper & live)
- Scheduled daily workflows via `scheduler.py`

### 🐳 Docker-First Deployment
- Single-command startup with `docker compose up`
- Isolated environment — no Python version conflicts
- Named volumes for persistent data, cache, and logs
- Corporate proxy / SSL certificate support built-in

---

## 🐳 Docker Setup (Recommended)

Running via Docker is the simplest and most reliable way to run the system. No Python environment management needed.

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

The container supports multiple modes via the `command:` field or `docker run`:

| Mode | Description | Command |
|------|-------------|---------|
| `dashboard` | Streamlit UI on port 8501 (default) | `docker compose up` |
| `scheduler` | Automated daily tasks | `docker compose --profile scheduler up` |
| `scanner` | One-shot stock scan | `docker compose run --rm dashboard scanner` |
| `signals` | One-shot signal generation | `docker compose run --rm dashboard signals` |
| `update` | One-shot universe update | `docker compose run --rm dashboard update` |
| `shell` | Interactive bash for debugging | `docker compose run --rm dashboard shell` |

### 4. Data Persistence

All runtime data is stored in named Docker volumes that survive container restarts:

| Volume | Mounted at | Contents |
|--------|-----------|----------|
| `trading_data` | `/app/data` | Universe JSON, fundamentals/earnings cache |
| `trading_cache` | `/app/cache` | Price data cache |
| `trading_logs` | `/app/logs` | Application logs |

```bash
# View volume contents
docker run --rm -v trading_data:/data busybox ls /data

# Stop without removing volumes
docker compose down

# Stop AND remove volumes (wipes all cached data)
docker compose down -v
```

### 5. Corporate Proxy / SSL

If you're behind a corporate proxy (e.g., Zscaler), the compose file automatically mounts your host's CA certificate bundle and sets the required environment variables:

```yaml
environment:
  CURL_CA_BUNDLE: /etc/ssl/certs/ca-certificates.crt
  REQUESTS_CA_BUNDLE: /etc/ssl/certs/ca-certificates.crt
  SSL_CERT_FILE: /etc/ssl/certs/ca-certificates.crt
volumes:
  - /etc/ssl/certs/ca-certificates.crt:/etc/ssl/certs/ca-certificates.crt:ro
```

No manual configuration needed — it works out of the box.

### 6. Useful Docker Commands

```bash
docker compose ps                  # Container status + health
docker compose logs -f             # Stream live logs
docker compose logs --tail=50      # Last 50 log lines
docker compose down                # Stop containers
docker compose build               # Rebuild image after code changes
```

---

## 💻 Local Installation

If you prefer to run without Docker:

### Requirements

| Item | Requirement |
|------|-------------|
| Python | 3.10+ |
| RAM | 4 GB minimum (8 GB recommended) |
| Storage | 500 MB free space |
| Internet | Stable connection |

### Setup

```bash
cd ~/trading_system

python -m venv venv
source venv/bin/activate        # Linux/Mac
# venv\Scripts\activate         # Windows

pip install -r requirements.txt

python -c "import config; print('✓ Config OK')"
python main.py signals
```

---

## 🚀 Quick Start

### Docker (Recommended)

```bash
docker compose up --build        # Start dashboard
# Open http://localhost:8501
```

### Local

```bash
python main.py signals                # All markets
python main.py signals --market US    # US only
python main.py analyze -s NVDA        # Analyze a stock
python run_dashboard.py               # Launch dashboard
```

---

## 🌐 Web Dashboard

Launch with `docker compose up` or `python run_dashboard.py` → open **http://localhost:8501**

> **Note:** When running on a remote machine via VS Code Remote SSH, use VS Code's port forwarding (Ports tab → Forward Port 8501) to access the dashboard in your local browser.

### Dashboard Pages

| Page | Purpose |
|------|---------|
| 🏠 Overview | Account metrics, live market indices, quick scan |
| 📊 Market Regime | SPY/VIX regime, should-trade gate with confidence score |
| 🎯 Signals | Live multi-market signals, filterable by strength |
| 📈 Fundamentals | P/E, ROE, revenue growth, fundamental score |
| 🔀 Combined Analysis | Technical + fundamental combined score with trade quality (A+ to D) |
| 📅 Earnings Calendar | Upcoming earnings dates with risk flags |
| 👔 Insider Activity | Recent insider buy/sell transactions |
| 🔍 Stock Screener | Custom filter screener across all markets |
| 📋 Trade Journal | Log entries, manage open positions, close trades |
| 📊 Performance | Monthly P&L progress, win rate, stats |
| 💼 Portfolio | Open positions, allocation, cash summary |
| 📐 Position Calculator | Fixed-risk and ATR-based position sizing |
| 🔬 Signal Analysis | Score distribution charts by sector |
| 🔄 Sector Rotation | US sector ETF relative strength vs SPY |
| 🧪 Backtest Pro | Walk-forward + Monte Carlo simulation |
| 📓 Journal Analytics | MAE/MFE, performance by regime & setup |
| ⚙️ Settings | Configuration display, API status |

### UI Design

The dashboard uses a professional dark theme:
- **Color palette:** Deep navy background (`#07090f`), cyan-blue accents (`#00b4d8`)
- **Typography:** Inter (UI) + JetBrains Mono (numbers/prices)
- **Metric cards:** Glass-effect with hover glow
- **Signal badges:** Color-coded (green STRONG BUY → red AVOID)
- **Score gauges:** Animated bars with dynamic color thresholds (≥60 green, ≥40 amber, <40 red)

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
| **Sunday** | Weekly universe update | `python main.py quick-update` |

With Docker, one-shot commands run via:
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
python main.py universe                # Show current stocks
python main.py universe --market DE    # Show German stocks
```

### Backtesting
```bash
python backtester.py run               # Test current universe
python backtester.py compare           # Compare all markets
python backtester.py run -p 2y         # 2-year backtest
```

### Daily Workflow
```bash
python daily_workflow.py morning
python daily_workflow.py midday
python daily_workflow.py afternoon
python daily_workflow.py evening
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

### Combined Analysis Trade Quality

| Grade | Combined Score | Meaning |
|-------|---------------|---------|
| A+ | ≥ 80 (both tech & fund ≥ 70) | Excellent — full position |
| A  | ≥ 70 (both ≥ 60) | Good — standard position |
| B  | ≥ 60 (both ≥ 50) | Acceptable — reduced size |
| C  | ≥ 50 | Marginal — small size only |
| D  | < 50 | Avoid |

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

---

## 💰 How to Place Trades

### 1. Get the Signal
```bash
python main.py signals --market US
# or use the 🎯 Signals page in the dashboard
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

---

## 📊 Trade Management

### Trading Rules
- **Always** use stop loss — set immediately after buy fills
- Max **1.5% risk** per trade
- Max **8 positions** total, **4 per market**
- Max **25%** of account in one stock
- Sell 50% at Target 1, move stop to breakeven

### Trade Journal (Dashboard)
Use the **📋 Trade Journal** page to:
- Log new trade entries with full setup details
- View all open positions
- Close positions with exit price, reason, MAE/MFE, and lessons learned
- Review closed trades history with win rate and R-multiple stats

---

## 🧪 Backtesting

### Via Dashboard (Backtest Pro page)
- Configure symbols, history period, walk-forward windows, Monte Carlo simulations
- View equity curve, trade stats, walk-forward train vs. test win rate chart

### Via CLI
```bash
python backtester.py run              # Default 1-year
python backtester.py run -p 6mo       # 6 months
python backtester.py run -p 2y        # 2 years
python backtester.py compare          # All markets side by side
```

### Interpreting Results

| Metric | Excellent | Good | Acceptable | Poor |
|--------|-----------|------|------------|------|
| Win Rate | 60%+ | 55%+ | 50–55% | <50% |
| Profit Factor | 2.0+ | 1.5+ | 1.2–1.5 | <1.2 |
| Max Drawdown | <10% | <15% | 15–20% | >25% |

---

## 🔔 Alerts Setup

### Telegram (Recommended)
1. Message `@BotFather` → `/newbot` → copy API token
2. Message `@userinfobot` → copy your Chat ID
3. Add to `.env`:
   ```
   TELEGRAM_BOT_TOKEN=your-token
   TELEGRAM_CHAT_ID=your-chat-id
   ```

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

Copy `.env.example` to `.env` and fill in your values:

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

The `.env` file is **never committed to git** (excluded via `.gitignore`).
When running with Docker, it is loaded automatically via `env_file: .env` in `docker-compose.yml`.

---

## 🇩🇪 For Germany-Based Traders

### Your Advantage
Trade 3 markets across different time zones from a single system:
- **04:45–11:00** 🇮🇳 India (morning opportunity)
- **09:00–17:30** 🇩🇪 Germany (primary market)
- **15:30–22:00** 🇺🇸 USA (afternoon/evening)

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
├── Dockerfile                 # Production Docker image (python:3.11-slim)
├── docker-compose.yml         # Compose: dashboard + optional scheduler service
├── entrypoint.sh              # Container entrypoint (dashboard/scheduler/scanner/…)
├── .dockerignore              # Excludes .git, cache, logs from image
│
├── config.py                  # System configuration (account, risk, indicators)
├── market_config.py           # Market definitions (US, DE, IN stocks & parameters)
├── main.py                    # CLI entry point
│
├── global_data_fetcher.py     # Multi-market data fetching (yfinance)
├── global_universe_manager.py # Stock universe ranking & selection
├── global_signal_generator.py # Signal generation across markets
│
├── technical_analyzer.py      # Technical analysis (EMA, RSI, ATR, etc.)
├── fundamental_analyzer.py    # Fundamental analysis with sector benchmarks
├── combined_analyzer.py       # Technical + fundamental combined scoring
├── market_regime.py           # SPY/VIX regime classification
│
├── position_manager.py        # Position sizing & risk management
├── trade_journal.py           # Trade logging (SQLite)
├── performance_tracker.py     # Monthly performance tracking
├── backtester.py              # Walk-forward backtesting + Monte Carlo
│
├── alert_system.py            # Telegram & email alerts
├── broker_api.py              # Alpaca broker integration
├── earnings_calendar.py       # Earnings date tracking
├── insider_tracker.py         # Insider transaction tracking
├── sector_rotation.py         # Sector ETF relative strength rankings
│
├── dashboard.py               # Streamlit web dashboard (17 pages, dark theme)
├── run_dashboard.py           # Local dashboard launcher
├── daily_workflow.py          # Scheduled daily routines
├── scheduler.py               # Task scheduling (signals + universe update)
├── logging_setup.py           # Centralized logging with colored output
│
├── data/                      # Universe JSON, rankings CSV, fundamentals cache
├── logs/                      # Application logs
├── cache/                     # Price data cache
├── .env                       # API keys (not committed to git)
├── .env.example               # Template for .env
└── requirements.txt           # Python dependencies
```

---

## 📝 Changelog

### May 2026 — Docker & UI Overhaul

#### 🐳 Docker
- **Production `Dockerfile`** — `python:3.11-slim-bookworm` base, non-root `trader` user, corporate proxy SSL support via `--trusted-host` pip flags
- **`docker-compose.yml`** — `dashboard` service (port 8501) + optional `scheduler` service (activated with `--profile scheduler`); named volumes for `data`, `cache`, `logs`; corporate CA bundle auto-mounted; health check on `/_stcore/health`
- **`entrypoint.sh`** — multi-mode entrypoint: `dashboard` | `scheduler` | `scanner` | `signals` | `update` | `shell`
- **`.dockerignore`** — excludes `.git`, `cache/`, `logs/`, `data/`, dev files for lean image

#### 🎨 Dashboard UI
- **Professional dark theme** — Inter + JetBrains Mono fonts, `#07090f` background, `#00b4d8` accent, Bloomberg-style radial gradients
- **Metric cards** — glass-effect with blue border, uppercase labels, monospace values, hover glow
- **Sidebar** — branded header, account/target summary card, glowing dot module status indicators
- **Buttons** — primary: blue gradient with lift-on-hover; secondary: ghost style
- **Tabs, inputs, dropdowns, sliders, expanders, scrollbars** — all consistently styled
- **Combined Analysis page** — full-width stock header banner, color-coded signal badges, animated score gauge bars with dynamic threshold colors (green ≥60, amber ≥40, red <40), trade quality pill

#### 🔧 Previous fixes (May 2026)
- Added 15+ missing config fields (`SCREENING_CRITERIA`, `EXIT_RULES`, etc.)
- Universe expanded to 50 stocks per market (145 total)
- Error handling improved throughout all modules
- Dashboard expanded from 12 to 17 pages (Sector Rotation, Backtest Pro, Journal Analytics, Insider Activity, Earnings Calendar added)
- Trade Journal UI: full close-trade flow with MAE/MFE tracking

---

## ❓ Frequently Asked Questions

**How do I run it?**
Docker is recommended: `docker compose up --build` → open http://localhost:8501.

**How much money do I need?**
Configured for $50,000 (changeable in `config.py`). Minimum $5,000 recommended for proper position sizing.

**Is this guaranteed to make money?**
No. This targets 4% monthly returns but losses are possible. Always use stop losses.

**Do I need to watch the market all day?**
No — swing trading. Check signals morning/evening, place orders, set stops. Trades last 2–10 days.

**How do I update the stock list?**
Run `python main.py quick-update` or `docker compose run --rm dashboard update` weekly.

**Can I add my own stocks?**
Edit `market_config.py` (`US_STOCKS`, `GERMAN_STOCKS`, `INDIAN_STOCKS`).

**What does "PULLBACK" setup mean?**
Stock is trending up but temporarily dipped to support — a buying opportunity.

**Should I trade every signal?**
No. Focus on STRONG BUY signals and A/A+ combined analysis grades. Start with 1–3 positions.

---

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| Dashboard not reachable in browser | If on VS Code Remote SSH, forward port 8501 via the PORTS tab |
| SSL / certificate errors in Docker | Ensure `/etc/ssl/certs/ca-certificates.crt` exists on host; it is auto-mounted by compose |
| `No result returned` in Combined Analysis | SSL cert issue — restart with `docker compose down && docker compose up` after confirming CA fix |
| Container exits immediately | Check `docker compose logs` for the error; likely missing `.env` |
| No data for symbol | Check format (NVDA, SAP.DE, TCS.NS). Yahoo Finance may be temporarily down |
| Slow performance | Use `quick-update` instead of full update; reduce stock count in `market_config.py` |
| Package install fails (local) | `python -m pip install --upgrade pip && pip install -r requirements.txt` |
| Config errors | `python -c "import config; print('OK')"` to verify |

---

## 📚 Glossary

| Term | Definition |
|------|------------|
| ATR | Average True Range — daily price movement measure |
| Drawdown | Decline from peak to trough |
| EMA | Exponential Moving Average |
| MAE | Maximum Adverse Excursion — worst drawdown during a trade |
| MFE | Maximum Favourable Excursion — best gain during a trade |
| Momentum | Strength of price movement in one direction |
| Position Size | Number of shares to buy |
| Profit Factor | Gross profit ÷ gross loss |
| Pullback | Temporary dip in an uptrend |
| R:R | Risk/Reward ratio |
| RSI | Relative Strength Index (overbought/oversold) |
| Sharpe Ratio | Return per unit of risk |
| Stop Loss | Auto-sell order to limit losses |
| Swing Trading | Holding stocks for days to weeks |
| Universe | List of stocks being tracked |
| Walk-Forward | Out-of-sample backtest validation across rolling windows |
| Win Rate | Percentage of profitable trades |

---

## ⚠️ Risk Disclaimer

Trading involves substantial risk of loss. This software is for educational and informational purposes only — not financial advice. Never invest money you cannot afford to lose. Past performance does not guarantee future results. Start with paper trading.

---

## 🎓 Getting Started Path

1. **Day 1:** `docker compose up --build` → explore the dashboard
2. **Week 1:** Paper trade — run signals daily, track what you would have traded
3. **Week 2–3:** Small positions — half size, STRONG BUY + A/A+ grade only, max 2 positions
4. **Week 4+:** Normal trading — full size, up to 8 positions, weekly journal review

