# 🌍 Global Swing Trading System

> A personal stock trading assistant that scans US, German, and Indian markets to find the best swing trading opportunities — and helps you manage every trade from entry to exit.

**Who is this for?**
- **Layman / first-time user** — follow the [5-Minute Quick Start](#-5-minute-quick-start) and use only the dashboard. No coding needed.
- **Developer** — skip to [Architecture](#-architecture) and [Command Reference](#-command-reference) for the full picture.

---

## 📋 Table of Contents

1. [What Does This Do?](#-what-does-this-do)
2. [Supported Markets](#-supported-markets)
3. [5-Minute Quick Start](#-5-minute-quick-start)
4. [Installation](#-installation)
   - [Option A — Docker (Recommended)](#option-a--docker-recommended)
   - [Option B — Local Python](#option-b--local-python)
5. [The Dashboard — Page by Page](#-the-dashboard--page-by-page)
6. [How to Use It Day-to-Day](#-how-to-use-it-day-to-day)
7. [How to Place a Trade (Step by Step)](#-how-to-place-a-trade-step-by-step)
8. [Weekend Investing Strategy](#-weekend-investing-mi-strategy)
9. [Setting Up Alerts](#-setting-up-alerts)
10. [Connecting a Broker](#-connecting-a-broker-alpaca)
11. [Backtesting](#-backtesting)
12. [Configuration Reference](#-configuration-reference)
13. [Environment Variables](#-environment-variables)
14. [Command Reference (CLI)](#-command-reference-cli)
15. [Architecture (For Developers)](#-architecture)
16. [Troubleshooting](#-troubleshooting)
17. [Glossary](#-glossary)
18. [Risk Disclaimer](#-risk-disclaimer)

---

## 🤔 What Does This Do?

Think of this as a **research assistant for stock traders**. Every morning it:

1. Scans 200+ stocks across 3 countries
2. Scores each stock using technical indicators (RSI, EMA, ATR, volume)
3. Ranks them and shows you **which ones are worth buying today**
4. Tells you exactly: entry price, stop loss, and target price
5. Calculates how many shares to buy so you never risk more than 1.5% of your account on one trade

You then place the trade manually in your own broker app. The system keeps a **journal** of your trades and shows your performance over time.

It is **not** a bot that trades automatically (unless you connect Alpaca and set it up to do so).

---

## 🌍 Supported Markets

| Market | Exchange | Currency | Trading Hours (your local CET) |
|--------|----------|----------|-------------------------------|
| 🇺🇸 USA | NYSE / NASDAQ | USD | 15:30 – 22:00 |
| 🇩🇪 Germany | XETRA | EUR | 09:00 – 17:30 |
| 🇮🇳 India | NSE / BSE | INR | 04:45 – 11:00 |

---

## ⚡ 5-Minute Quick Start

> **You need:** Docker installed. That's it. No Python, no manual setup.

```bash
# 1. Download the code
git clone <your-repo-url> trading_system
cd trading_system

# 2. Create your config file
cp .env.example .env        # API keys go here later — fine to leave blank for now

# 3. Start the dashboard
docker compose up --build
```

Open your browser: **http://localhost:8501**

> **On a remote server (VS Code SSH)?**
> Go to the **Ports** tab in VS Code → click **Forward a Port** → type `8501` → click the globe icon.

That's it. You now have the full dashboard running. Explore the sidebar — start with **🏠 Overview**, then **🎯 Signals**.

> **What to expect on first run:** The build takes 2–4 minutes while Docker downloads dependencies. The first signal scan takes 30–60 seconds while prices are fetched. Subsequent loads are much faster because data is cached.

---

## 📦 Installation

### Option A — Docker (Recommended)

**Why Docker?** It installs everything in an isolated container. No Python version conflicts, no dependency issues. Works identically on any machine.

**Prerequisites:**
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Windows/Mac) or [Docker Engine](https://docs.docker.com/engine/install/) (Linux)
- Git

```bash
git clone <your-repo-url> trading_system
cd trading_system
cp .env.example .env
docker compose up --build
```

**Useful Docker commands:**

```bash
docker compose up --build          # First run (builds image)
docker compose up -d               # Start all services in background (normal daily use)
docker compose down                # Stop everything
docker compose logs -f             # Stream live logs
docker compose logs -f dashboard   # Dashboard logs only
docker compose ps                  # Check status of all containers
docker compose pull                # Update cloudflared / base images
docker compose build               # Rebuild after changing requirements.txt or code
```

**Run modes:**

| What you want | Command |
|---------------|---------|
| Everything (dashboard + scheduler + tunnel) | `docker compose up -d` |
| One-shot signal scan | `docker compose run --rm dashboard signals` |
| One-shot universe update | `docker compose run --rm dashboard update` |
| Open a shell inside container | `docker compose run --rm dashboard shell` |

> **Why just `docker compose up -d`?** Active profiles are baked into `.env` (`COMPOSE_PROFILES=scheduler,tunnel-auth`), so all services start automatically without extra flags.

**Where is your data stored?**

Docker uses named volumes so your data survives container restarts:

| Volume | What's inside |
|--------|--------------|
| `trading_data` | Your trade journal database, universe files |
| `trading_cache` | Downloaded price data (speeds up restarts) |
| `trading_logs` | Application logs |

```bash
docker compose down          # Stops containers, keeps your data
docker compose down -v       # ⚠️ Stops AND deletes all data — use carefully
```

---

### Running 24/7 — Always-On Setup

#### 1. Make Docker start on host boot

```bash
sudo systemctl enable docker
```

#### 2. Make Compose start on host boot (systemd service)

```bash
sudo nano /etc/systemd/system/trading-system.service
```

Paste:

```ini
[Unit]
Description=Global Trading System
Requires=docker.service
After=docker.service network-online.target
Wants=network-online.target

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/home/megha/trading_system    # ← change this to your actual path
ExecStart=/usr/bin/docker compose up -d --build
ExecStop=/usr/bin/docker compose down
TimeoutStartSec=300

[Install]
WantedBy=multi-user.target
```

Then enable:

```bash
sudo systemctl daemon-reload
sudo systemctl enable trading-system.service
sudo systemctl start trading-system.service
sudo systemctl status trading-system.service   # verify
```

After this, the dashboard + scheduler + Cloudflare tunnel start automatically after every reboot. `restart: unless-stopped` in `docker-compose.yml` also auto-recovers any crashed container within seconds.

---

### Remote Access via Cloudflare Tunnel

Cloudflare Tunnel gives you a public HTTPS URL for the dashboard — no open firewall ports, no static IP needed.

Two modes are available (switch by changing `COMPOSE_PROFILES` in `.env`):

| Mode | Profile | URL | Requires |
|------|---------|-----|----------|
| **Quick tunnel** | `tunnel` | Random `*.trycloudflare.com` URL (changes on restart) | Nothing — no account |
| **Named tunnel** | `tunnel-auth` | Your own permanent URL | Free Cloudflare account + token |

#### Option A — Quick Tunnel (no account)

In `.env`:
```
COMPOSE_PROFILES=scheduler,tunnel
```

Start: `docker compose up -d`

Find the URL:
```bash
docker logs trading-cloudflared 2>&1 | grep trycloudflare.com
```

#### Option B — Named Tunnel (permanent URL)

**One-time setup:**

```bash
# Install cloudflared
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared-linux-amd64.deb

# Log in to Cloudflare (opens browser)
cloudflared tunnel login

# Create the tunnel
cloudflared tunnel create trading-dashboard

# Get the token
cloudflared tunnel token trading-dashboard
```

Add token to `.env`:
```
CLOUDFLARE_TUNNEL_TOKEN=eyJhIjoiMTIz...    # paste your token
COMPOSE_PROFILES=scheduler,tunnel-auth
```

In Cloudflare dashboard → **Zero Trust → Networks → Tunnels** → click your tunnel → **Public Hostname** → add `trading.yourdomain.com → http://dashboard:8501`.

Start: `docker compose up -d`

#### Securing the public URL (recommended)

Anyone with the URL can see your dashboard. Add a login screen:

**Cloudflare dashboard → Zero Trust → Access → Applications → Add → Self-hosted**
- Application domain: `trading.yourdomain.com`
- Policy: allow only your email address

This adds a one-time email OTP before anyone can view the dashboard.

---

### Option B — Local Python

> Use this only if you can't install Docker.

```bash
cd trading_system

# Create a virtual environment
python3 -m venv venv
source venv/bin/activate        # Mac/Linux
# venv\Scripts\activate         # Windows

# Install dependencies
pip install -r requirements.txt

# Verify it works
python -c "import config; print('✓ OK')"

# Run the dashboard
streamlit run dashboard.py
```

---

## 🖥️ The Dashboard — Page by Page

The dashboard has **18 pages** grouped in the left sidebar. Here is what each one does and when to use it.

### 📊 Market Group

| Page | What it does | When to use |
|------|-------------|-------------|
| **🏠 Overview** | Shows live index prices (S&P, NASDAQ, VIX, DAX) and lets you do a quick scan across all markets | Every morning — first page to check |
| **📊 Market Regime** | Tells you whether the market conditions are safe to trade (✅ TRADE or 🚫 PAUSE) | Before placing any new trade |
| **🎯 Signals** | Lists stocks with BUY/STRONG BUY signals, with entry, stop, and target prices | When you're looking for new trades |
| **📈 Fundamentals** | Shows P/E ratio, revenue growth, ROE, etc. for any stock you type in | To check if a signal stock is financially healthy |
| **🔀 Combined Analysis** | Combines technical signal score + fundamental score into one A+/A/B/C/D grade | Best page before deciding to buy — use after Signals |

### 🔍 Research Group

| Page | What it does | When to use |
|------|-------------|-------------|
| **📅 Earnings Calendar** | Shows upcoming earnings announcements for any stocks | Always check before entering a trade — never hold through earnings |
| **👔 Insider Activity** | Shows when company executives are buying or selling their own stock | Secondary confirmation — large insider buys are bullish |

### 🔧 Tools Group

| Page | What it does | When to use |
|------|-------------|-------------|
| **🔍 Stock Screener** | Filters the full universe by your criteria (score, market, etc.) | Weekly — to build your watchlist |
| **📐 Position Calculator** | Tells you exactly how many shares to buy based on your account size and risk | Every time before placing an order |
| **🔬 Signal Analysis** | Chart showing the distribution of signal scores across all stocks | Weekly — if most scores are below 50, reduce position sizes |
| **🔄 Sector Rotation** | Ranks sector ETFs by momentum vs their local benchmark — 3 tabs: 🇺🇸 US vs SPY, 🇩🇪 Germany vs DAX ETF, 🇮🇳 India vs NIFTYBEES | Weekly — trade stocks in the leading sectors |

### 💼 Portfolio Group

| Page | What it does | When to use |
|------|-------------|-------------|
| **💼 Portfolio** | Shows your open positions (from Alpaca if connected, otherwise from journal) | Daily |
| **📋 Trade Journal** | Log new trades, manage open ones, record exits | Every time you open or close a trade |
| **📊 Performance** | Monthly P&L, win rate, profit factor, equity curve chart | Weekly review |
| **📓 Journal Analytics** | Deep stats: MAE/MFE distributions, performance by market regime and setup type | Monthly review — find what's working |

### 🚀 Strategies Group

| Page | What it does | When to use |
|------|-------------|-------------|
| **🧪 Backtest Pro** | Tests your signal strategy on historical data, walk-forward + Monte Carlo | Before live trading any new approach |
| **🏆 Weekend Investing (MI)** | Momentum rotation strategy — generates weekly/monthly rebalance signals for Indian markets | Every Sunday for MI strategies |

### ⚙️ System Group

| Page | What it does | When to use |
|------|-------------|-------------|
| **⚙️ Settings** | Edit account size, risk %, screener filters, exit rules — all in the browser | When you want to change any trading parameters |

---

## 📅 How to Use It Day-to-Day

### Morning Routine (10 minutes)

```
1. Open http://localhost:8501
2. 📊 Market Regime → check if it says ✅ TRADE or 🚫 PAUSE
   → If PAUSE, do not enter new trades today
3. 🎯 Signals → Generate Signals (US + DE + IN)
   → Filter: BUY or STRONG BUY
4. For each interesting signal:
   → 📅 Earnings Calendar — check there's no earnings in the next 7 days
   → 🔀 Combined Analysis — check the grade is B or higher
   → 📐 Position Calculator — calculate exact share count
5. Place the trade in your broker app
6. 📋 Trade Journal → Log Entry tab → record the trade
```

### Evening Routine (5 minutes)

```
1. Check your open positions in 💼 Portfolio
2. If a position hit Target 1 → sell half, move stop to breakeven
3. If a position hit stop loss → close it and log in 📋 Trade Journal
4. 📊 Performance → review today's P&L
```

### Weekly (Sunday)

```
1. 🔄 Sector Rotation → note which sectors are leading
2. 🔬 Signal Analysis → check overall market breadth
3. 🏆 Weekend Investing → Generate Rebalance Signal → execute Monday open
4. docker compose run --rm dashboard update   (refresh the stock universe)
```

---

## 💰 How to Place a Trade (Step by Step)

**Example: NVDA appeared as STRONG BUY, score 82**

**Step 1 — Verify the signal**
- 📊 Market Regime says ✅ TRADE
- 🔀 Combined Analysis shows grade A, entry $880, stop $852, target $940
- 📅 Earnings Calendar — no earnings in next 10 days

**Step 2 — Size the position**
- 📐 Position Calculator → Entry: $880, Stop: $852, Account: $50,000, Risk: 1.5%
- Result: **26 shares** → position value $22,880 (46% of account — system caps at 25%, so actual = 14 shares = $12,320)

**Step 3 — Place the order**
- Go to your broker (Alpaca, Interactive Brokers, Trade Republic, etc.)
- Place a **limit buy** at $880 (or market if you need to act fast)
- Immediately place a **stop-loss order** at $852

**Step 4 — Log it**
- 📋 Trade Journal → Log Entry tab → fill in symbol, entry, stop, shares, setup type

**Step 5 — Manage the trade**
- When price hits $940 (Target 1) → sell half (7 shares), move stop to $880 (breakeven)
- When price hits Target 2 → sell remaining shares
- If stop $852 is hit → broker auto-sells; log the exit in Trade Journal

---

## 🏆 Weekend Investing (MI) Strategy

This is a separate momentum rotation strategy for **Indian markets**, inspired by [Weekend Investing](https://weekendinvesting.com).

**Concept in plain English:**
- Every week (or month), score all stocks by how much they went up in the past 1M/3M/6M/12M
- Buy the top N stocks, equal weight
- At the next rebalancing date, sell anything that fell out of the top N, buy the new entrants
- No stop-loss — only the ranking system tells you when to sell

**How to use it:**
1. Go to **🏆 Weekend Investing (MI)** in the dashboard
2. Select a strategy preset (see table below)
3. Enter your total capital for this strategy (e.g. ₹5,00,000)
4. Enter what you currently hold (comma-separated symbols, e.g. `TCS.NS,INFY.NS`)
5. Click **Generate Rebalance Signal**
6. On **Monday at 9:15 AM IST**, execute the ✅ BUY and ❌ SELL signals at market price

**Strategy presets:**

| Strategy | Universe | Slots | Rebalance | Best for |
|----------|----------|-------|-----------|----------|
| Mi-Top10 | Nifty 50 (large caps) | 10 | Weekly | Conservative, stable |
| Mi-NNF10 | Nifty Next 50 | 10 | Weekly | Mid-large cap |
| Mi-EverGreen | CNX 200 | 20 | Weekly | Balanced, risk-adjusted |
| Mi-20 | MidSmall 400 | 20 | Weekly | Mid-cap growth |
| Mi-25 | Smallcap 250 | 25 | Monthly | Small-cap, cash filter |
| Mi-30 | CNX 500 | 30 | Monthly | Broad market, cash filter |
| Mi-35 | Smallcap 250 | 35 | Weekly | Small-cap momentum |
| Mi-ST-ATH | CNX 500 | 15 | Weekly | Near all-time highs only |

**Key rules (never break these):**
- Never override a SELL signal — trust the system
- Every slot gets exactly equal weight (capital ÷ N slots)
- When the system shows 🟡 CASH, park that slot in LIQUIDBEES or a liquid fund
- Do not add more to a position because you "like" it — equal weight, always

---

## 📲 Setting Up Alerts

Alerts let the system send you a Telegram message or email whenever signals are generated.

### Telegram Setup (Recommended — Free)

1. Open Telegram → search for **@BotFather** → send `/newbot`
2. Follow the prompts → copy the **Bot Token** (looks like `123456789:ABCdef...`)
3. Search for **@userinfobot** → send `/start` → copy your **Chat ID** (a number)
4. Add to your `.env` file:
   ```
   TELEGRAM_BOT_TOKEN=123456789:ABCdef...
   TELEGRAM_CHAT_ID=987654321
   ```
5. Restart: `docker compose restart`

Now on the **🎯 Signals** page, tick the **📲 Send alerts** checkbox before clicking Generate Signals — it will send a Telegram message for every signal found.

### Email Setup (Gmail)

1. Gmail → Account Settings → Security → 2-Step Verification → **App Passwords**
2. Create an app password → copy it
3. Add to `.env`:
   ```
   EMAIL_SENDER=your@gmail.com
   EMAIL_PASSWORD=abcd efgh ijkl mnop    # The app password, not your main password
   EMAIL_RECEIVER=where@you.want.it.sent.com
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   ```

---

## 🔗 Connecting a Broker (Alpaca)

Alpaca is a US commission-free broker that provides a free API for paper (simulated) and live trading.

**Paper trading (simulated — no real money):**
1. Sign up at [alpaca.markets](https://alpaca.markets) → Paper Trading
2. Generate API keys → Paper Trading → API Keys
3. Add to `.env`:
   ```
   ALPACA_API_KEY=your-key
   ALPACA_SECRET_KEY=your-secret
   ALPACA_BASE_URL=https://paper-api.alpaca.markets
   ```

**Live trading:**
- Same steps, but use Live API keys and `ALPACA_BASE_URL=https://api.alpaca.markets`
- ⚠️ Only switch to live after at least 4 weeks of profitable paper trading

Once connected, the **💼 Portfolio** page will show your real Alpaca positions and account balance, not just journal data.

---

## 🧪 Backtesting

Use the **🧪 Backtest Pro** page to test whether a set of stocks would have been profitable with this system's signals.

**How to run:**
1. Enter symbols (comma-separated): `NVDA,AAPL,MSFT,META`
2. Select history period: `1y` or `2y`
3. Click **▶ Run Backtest** for a simple backtest
4. Click **🔀 Walk-Forward** for a more realistic out-of-sample test
5. Click **🎲 Monte Carlo** to see the range of possible outcomes

**What the results mean:**

| Metric | Good | Acceptable | Poor |
|--------|------|------------|------|
| Win Rate | 55%+ | 50–55% | <50% |
| Profit Factor | 1.5+ | 1.2–1.5 | <1.2 |
| Max Drawdown | <15% | 15–25% | >25% |

A strategy is only worth trading live if Walk-Forward CAGR > 0 **and** Monte Carlo 5th-percentile is still positive.

---

## ⚙️ Configuration Reference

All key settings are editable on the **⚙️ Settings** page in the dashboard without touching any files. The table below shows what each setting does:

| Setting | Default | What it controls |
|---------|---------|-----------------|
| Account Size | $50,000 | Base for all position size calculations |
| Monthly Target | 4% | Your P&L goal shown on Performance page |
| Risk per Trade | 1.5% | Max % of account you risk on a single trade |
| Max Positions | 8 | System warns if you try to open more |
| Daily Loss Limit | 2% | Reference limit shown on dashboard |
| Min Market Cap | $5B | Filters out tiny/illiquid companies |
| Min Avg Volume | $2M | Filters out low-liquidity stocks |
| Stop Loss ATR | 1.75× | Stop distance = 1.75 × 14-day ATR |
| Target 1 ATR | 3.5× | First profit target = 3.5 × ATR above entry |
| Target 2 ATR | 4.0× | Second profit target = 4.0 × ATR above entry |
| Max Hold Days | 10 | Reference max holding period |

To change these: **⚙️ Settings** → edit → **💾 Save Changes**. Takes effect immediately.

To change the stock universe (which stocks are scanned): edit `market_config.py` → `US_STOCKS`, `GERMAN_STOCKS`, `INDIAN_STOCKS` lists.

---

## 🔐 Environment Variables

Create a `.env` file in the project root (copy from `.env.example`). This file is never committed to git.

```bash
# ── Broker (Alpaca) ───────────────────────────────────────────────────
# Leave empty to run in simulation mode (no real trades)
ALPACA_API_KEY=""
ALPACA_SECRET_KEY=""
ALPACA_BASE_URL="https://paper-api.alpaca.markets"   # Change to live URL for real trading

# ── Telegram alerts (optional) ────────────────────────────────────────
TELEGRAM_BOT_TOKEN=""     # From @BotFather
TELEGRAM_CHAT_ID=""       # From @userinfobot

# ── Email alerts (optional) ───────────────────────────────────────────
EMAIL_SENDER=""           # Your Gmail address
EMAIL_PASSWORD=""         # Gmail App Password (not your login password)
EMAIL_RECEIVER=""         # Where to send alerts
SMTP_SERVER="smtp.gmail.com"
SMTP_PORT=587

# ── Optional data APIs ────────────────────────────────────────────────
POLYGON_API_KEY=""        # Optional — improves fundamental data quality

# ── Cloudflare Tunnel (remote access) ────────────────────────────────
CLOUDFLARE_TUNNEL_TOKEN=""   # From: cloudflared tunnel token <name>  (named tunnel only)

# ── Docker Compose profiles ───────────────────────────────────────────
# Controls which services start with `docker compose up -d`
# Options: scheduler, tunnel (quick), tunnel-auth (named/permanent)
COMPOSE_PROFILES=scheduler,tunnel-auth
```

With Docker, `.env` is loaded automatically. With local Python, it's loaded via `python-dotenv` in `config.py`.

---

## 📖 Command Reference (CLI)

All commands can be run locally (`python main.py ...`) or in Docker (`docker compose run --rm dashboard ...`).

### Signals & Analysis
```bash
python main.py signals                     # Generate signals for all markets
python main.py signals --market US         # US only
python main.py signals --market DE         # Germany only
python main.py signals --market IN         # India only
python main.py analyze -s NVDA             # Deep analysis of one stock
python main.py scan                        # Full universe scan
python main.py status                      # Market open/closed status
```

### Universe Management
```bash
python main.py quick-update                # Update universe (~10 min) — run weekly
python main.py update-universe             # Full update (~30 min)
python main.py universe --market IN        # Indian stocks only
```

### Strategies
```bash
# Backtest
python strategies/backtester.py run             # Run on current universe
python strategies/backtester.py run -p 2y       # 2-year backtest

# Weekend Investing
python strategies/weekend_investing_strategy.py --strategy Mi-35 --capital 500000
```

### Daily Automation
```bash
python automation/daily_workflow.py morning      # Morning routine
python automation/daily_workflow.py midday       # Midday check
python automation/daily_workflow.py evening      # End of day review
python automation/scheduler.py                   # Start the scheduler daemon
```

### Symbol Format

| Market | Format | Examples |
|--------|--------|---------|
| 🇺🇸 US | Plain ticker | `NVDA`, `AAPL`, `MSFT` |
| 🇩🇪 Germany | Ticker + `.DE` | `SAP.DE`, `BMW.DE`, `SIE.DE` |
| 🇮🇳 India | Ticker + `.NS` | `TCS.NS`, `RELIANCE.NS`, `INFY.NS` |

---

## 🏗️ Architecture

### Project Structure

```
trading_system/
│
├── dashboard.py               # Main Streamlit entry point
├── pages/                     # One file per dashboard page (18 pages)
│   ├── 1_🏠_Overview.py
│   ├── 2_📊_Market_Regime.py
│   ├── 3_🎯_Signals.py
│   └── ...
├── _common.py                 # Shared CSS, imports, resource init (used by all pages)
│
├── config.py                  # Trading parameters (account, risk, universe)
├── market_config.py           # Per-market stock lists and session times
├── main.py                    # CLI entry point
├── run_dashboard.py           # Local dashboard launcher shortcut
│
├── core/                      # Data fetching & universe management
│   ├── data_fetcher.py        # Single-stock OHLCV download
│   ├── global_data_fetcher.py # Multi-market batch fetcher
│   └── global_universe_manager.py  # Stock universe caching
│
├── analysis/                  # Market & stock analysis
│   ├── technical_analyzer.py  # EMA, RSI, ATR, volume, setup detection
│   ├── fundamental_analyzer.py # P/E, ROE, growth via yfinance
│   ├── combined_analyzer.py   # Technical + fundamental composite score
│   ├── market_regime.py       # SPY/VIX regime gate (should-trade logic)
│   └── sector_rotation.py     # Sector ETF relative strength rankings
│
├── signals/                   # Signal generation
│   ├── signal_generator.py    # Single-market signal engine
│   └── global_signal_generator.py  # Multi-market orchestrator
│
├── screening/                 # Stock screeners
│   ├── stock_screener.py      # Score-based filter screener
│   └── fundamental_screener.py # Fundamental quality filter
│
├── portfolio/                 # Position & trade management
│   ├── position_manager.py    # Account allocation tracker
│   ├── trade_journal.py       # SQLite-backed trade log (entry/exit/MAE/MFE)
│   ├── performance_tracker.py # Monthly P&L progress vs target
│   ├── broker_api.py          # Alpaca wrapper (paper + live)
│   └── alert_system.py        # Telegram + email notifications
│
├── strategies/                # Trading strategies
│   ├── backtester.py          # Walk-forward + Monte Carlo engine
│   ├── swing_trading_system.py # Core swing trading logic
│   └── weekend_investing_strategy.py  # MI momentum rotation (8 presets)
│
├── research/                  # Market research
│   ├── earnings_calendar.py   # Upcoming earnings dates
│   └── insider_tracker.py     # SEC Form 4 insider transactions
│
├── automation/                # Scheduling & daily routines
│   ├── scheduler.py           # Cron-style job runner (writes logs/scheduler.log)
│   └── daily_workflow.py      # Morning/midday/evening routines
│
├── Dockerfile                 # python:3.11-slim, non-root user
├── docker-compose.yml         # Dashboard + optional scheduler profile
├── entrypoint.sh              # Container entrypoint (multi-mode)
├── requirements.txt
├── .env                       # API keys — never committed to git
│
├── data/                      # Universe JSON, fundamentals cache (persistent volume)
├── logs/                      # scheduler.log + app logs (persistent volume)
└── cache/                     # Price data cache (persistent volume)
```

### How Pages Share Code

Every page in `pages/` starts with:
```python
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from _common import *
```

`_common.py` provides: path bootstrap, CSS (light + dark theme), all module imports, `get_resources()` (cached resource init), and `_help()`. No duplication across pages.

### Data Flow

```
yfinance / Polygon API
       ↓
GlobalDataFetcher (core/)
       ↓
GlobalSignalGenerator (signals/) ←── TechnicalAnalyzer + FundamentalAnalyzer
       ↓
Dashboard pages (pages/) ←── BrokerAPI (live positions) + TradeJournal (SQLite)
       ↓
AlertSystem → Telegram / Email
```

---

## 🔧 Troubleshooting

| Problem | What to do |
|---------|-----------|
| Dashboard not opening in browser | If on VS Code Remote SSH: go to **Ports** tab → Forward Port → `8501` → click the globe icon |
| `SSL certificate` errors | You're behind a corporate proxy. The compose file auto-mounts your host CA bundle — just use Docker. |
| Container exits immediately after `docker compose up` | Run `docker compose logs` — usually a missing `.env` file or syntax error in it |
| `No data returned` for a stock | Check the symbol format (NVDA, SAP.DE, TCS.NS). Yahoo Finance may be rate-limiting — wait 1 minute and retry |
| Settings page shows "Failed to save" | The container doesn't have write access to `config.py` — check volume mounts in `docker-compose.yml` |
| Page shows blank or spinner forever | Module failed to import — check `docker compose logs` for the Python traceback |
| Equity curve not showing | You need at least one **closed** trade in the journal. Log a trade and close it first. |
| Alpaca shows "not connected" | Verify `ALPACA_API_KEY` and `ALPACA_SECRET_KEY` in `.env`, then `docker compose restart` |
| Telegram alerts not arriving | Check `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` in `.env`. Send `/start` to your bot in Telegram first. |
| `pip install` fails (local) | `pip install --upgrade pip` then retry. Or just use Docker. |
| Dark mode toggle not working | Clear your browser cache (Ctrl+Shift+R) — Streamlit caches CSS aggressively |

---

## 📚 Glossary

| Term | Plain English explanation |
|------|--------------------------|
| **ATR** | Average True Range — measures how much a stock moves per day on average. Used to set stop-loss distances. |
| **Drawdown** | How much your account dropped from its highest point. A 10% drawdown means you lost 10% from peak. |
| **EMA** | Exponential Moving Average — a smoothed average price that reacts faster to recent changes than a simple average. |
| **Equity Curve** | A line chart of your account value over time. Going up = profitable. |
| **LIQUIDBEES** | An Indian ETF that acts like cash. Used in MI strategies when the system says hold cash. |
| **MAE** | Maximum Adverse Excursion — the worst point a trade went against you while it was open. |
| **MFE** | Maximum Favourable Excursion — the best point a trade reached while it was open. |
| **Market Regime** | Whether the overall market (S&P 500, VIX) is in a condition that favours swing trading. |
| **MI Strategy** | Weekend Investing — a momentum rotation strategy that buys the top-ranked stocks and rebalances weekly/monthly. |
| **Momentum** | How much a stock has gone up over the past months. High momentum = it's been rising steadily. |
| **Position Sizing** | Calculating how many shares to buy so that if the stop loss is hit, you only lose a fixed % of your account. |
| **Profit Factor** | Total profit from winning trades ÷ total loss from losing trades. Anything above 1.5 is good. |
| **Pullback** | When a rising stock temporarily dips — a potential buying opportunity in an uptrend. |
| **R:R (Risk/Reward)** | If you risk $100 and your target makes $250, your R:R is 2.5. Aim for 2.0 or above. |
| **ROC** | Rate of Change — % price change over a period (e.g. 1 month, 3 months). Used to rank momentum. |
| **RSI** | Relative Strength Index — 0 to 100. Below 40 = oversold, above 60 = overbought. |
| **Stop Loss** | A price level where you automatically exit a losing trade to cap your loss. |
| **Swing Trading** | Buying a stock and holding it for 2–10 days to capture a short-term price move. Not day trading. |
| **Universe** | The list of stocks the system actively monitors and scores. |
| **Walk-Forward** | A realistic backtest method that tests on data the model never trained on — avoids overfitting. |
| **Win Rate** | % of trades that were profitable. 50%+ with R:R > 2 is a good system. |

---

## ⚠️ Risk Disclaimer

Trading stocks involves substantial risk of loss. This software is for **educational and informational purposes only** and does not constitute financial advice. Never invest money you cannot afford to lose. Past performance does not guarantee future results.

**Always start with paper trading** (simulated, no real money) for at least 4 weeks before using real capital.

---

## 🎓 Suggested Getting-Started Path

| Day | What to do |
|-----|-----------|
| **Day 1** | `docker compose up --build` (first time only, then use `docker compose up -d`) → explore all 18 pages, read the ℹ️ help on each |
| **Days 2–7** | Run signals daily, use Combined Analysis, read the Glossary when you see an unfamiliar term |
| **Week 2–3** | Paper trade — log every trade you *would have* placed in the Trade Journal |
| **Week 4** | Review your journal: win rate, avg R, which setups worked |
| **Week 5+** | If paper results are positive — small live positions, STRONG BUY + grade B+ only, max 2 positions |
| **Month 2+** | Full size, up to 8 positions, weekly Journal Analytics review, MI rebalance every Sunday |

---

## ❓ Frequently Asked Questions

**How do I start the system every day?**
`docker compose up -d` — that's it. It starts all services (dashboard, scheduler, Cloudflare tunnel) in the background.

**How do I stop it?**
`docker compose down` — stops all containers. Your data is safe.

**Where is my data? Will I lose it if I restart?**
All data (trade journal, universe, price cache) is stored in Docker named volumes (`trading_data`, `trading_cache`, `trading_logs`). It survives container restarts and `docker compose down`. Only `docker compose down -v` deletes it.

**How do I change account size or risk settings?**
⚙️ Settings page → edit in-browser → Save Changes. No need to touch any files.

**How much money do I need?**
Default config is for $50,000. Minimum ~$5,000 recommended (below that, position sizes become too small for most US stocks). Change `ACCOUNT_SIZE` in ⚙️ Settings.

**Do I need to watch the market all day?**
No — swing trading holds for 2–10 days. Check morning routine (10 min) and evening routine (5 min). The scheduler handles automated scans.

**The signal scan is slow — is that normal?**
Yes, the first scan of the day fetches live data for 200+ stocks. Expect 30–90 seconds. Subsequent scans within the same session use cached data and are much faster.

**Can I use this without Alpaca?**
Yes — Alpaca is optional. Without it, the Portfolio page shows journal-based positions. The signal scanner, journal, backtester, and all analysis pages work without any broker connection.

**Can I add my own stocks to scan?**
Edit `market_config.py` → `US_STOCKS`, `GERMAN_STOCKS`, or `INDIAN_STOCKS` lists → rebuild: `docker compose build && docker compose up -d`.

**How do I access the dashboard from my phone?**
Set up the Cloudflare Tunnel (see [Remote Access via Cloudflare Tunnel](#remote-access-via-cloudflare-tunnel)). You'll get a public HTTPS URL that works from any device.

**The dashboard shows a blank page or keeps spinning.**
Run `docker compose logs dashboard` to see the error. Usually a missing Python module or a yfinance rate-limit. Wait 1 minute and refresh.

**Can it trade automatically?**
Not by default. It is a research and journaling tool. You place trades manually in your broker. Alpaca API integration exists in `portfolio/broker_api.py` and can be extended for automated order placement — but this requires developer-level work and is outside the default feature set.
