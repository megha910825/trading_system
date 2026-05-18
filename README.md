# 📈 Global Swing Trading System

## Complete Trading Solution for US, German & Indian Markets

> **Your automated stock trading assistant that scans 500+ stocks across 3 international markets to find the best trading opportunities.**

---

## 🎯 What is This Tool?

This is an **automated stock trading assistant** that:

- ✅ Scans 500+ stocks daily to find the best opportunities
- ✅ Tells you exactly **when to buy**, **when to sell**, and **where to set stop loss**
- ✅ Calculates how many shares to buy based on your account size
- ✅ Sends alerts to your phone/email when opportunities arise
- ✅ Tracks your trades and shows your performance
- ✅ Backtests strategies on historical data before you risk real money
- ✅ Works across multiple time zones - trade around the clock

**Goal:** Help you make **4% monthly returns** (~48% yearly) through swing trading.

---

🌍 Supported Markets
Market	Exchange	Currency	Trading Hours (Local)	Trading Hours (CET)
🇺🇸 USA	NYSE/NASDAQ	USD ($)	09:30 - 16:00 ET	15:30 - 22:00
🇩🇪 Germany	XETRA	EUR (€)	09:00 - 17:30 CET	09:00 - 17:30
🇮🇳 India	NSE/BSE	INR (₹)	09:15 - 15:30 IST	04:45 - 11:00

---
## 📋 Table of Contents
1. [Features](#-Features)
2. [What You Need](#-what-you-need)
3. [Installation](#-installation-step-by-step)
4. [Quick Start](#-quick-start-5-minutes)
5. [Daily Trading Workflow](#-daily-trading-workflow)
6. [Command Reference](#-command-reference)
7. [Understanding Signals](#-understanding-signals)
8. [How to Place Trades](#-how-to-place-trades)
9. [Managing Your Trades](#-managing-your-trades)
10. [ Web Dashboard](#-web-dashboard)
11. [Setting Up Alerts](#-setting-up-alerts)
12. [For Germany-Baseds Traders](#-germany-based-traders)
13. [FAQ](#-frequently-asked-questions)
14. [Troubleshooting](#-troubleshooting)
15. [Glossary](#-glossary-of-terms)

---

## ✨ Features
### 📊 Multi-Market Scanning
    Scans S&P 500, NASDAQ 100, DAX 40, MDAX, NIFTY 50, and more
    Automatic stock ranking based on momentum, volume, and returns
    Dynamic universe that updates weekly with best-performing stocks

### 🎯 Signal Generation
    STRONG BUY / BUY / WATCH signal classification
    Precise entry, stop loss, and target prices
    Risk/Reward ratio calculation
    Multiple setup types: Pullback, Momentum, Breakout

### 🧪 Backtesting
    Test strategies on 1-5 years of historical data
    Compare performance across different markets
    Detailed statistics: Win rate, Profit factor, Max drawdown
    Save and analyze backtest results
### 📱 Alerts
    Telegram notifications
    Email alerts
    Console output (always available)
### 📈 Position Management
    Automatic position sizing based on risk
    Trade journal for logging and tracking
    Performance statistics
### 🌐 Web Dashboard
    Visual interface for all features
    Real-time market status
    Interactive charts and analysis

## 💻 What You Need

### Minimum Requirements

| Item | Requirement |
|------|-------------|
| Computer | Windows 10/11, Mac, or Linux |
| Internet | Stable connection |
| RAM | 4GB minimum (8GB recommended) |
| Storage | 500MB free space |
| Broker Account | Any broker (TD Ameritrade, Fidelity, Schwab, Robinhood, etc.) |

### Optional (For Automation)

| Item | Purpose |
|------|---------|
| Alpaca Account | Free automated trading (paper & live) |
| Telegram Account | Get alerts on your phone |
| Gmail Account | Get email alerts |

---

## 🔧 Installation (Step-by-Step)

### Step 1: Install Python

#### Windows

1. Go to [python.org/downloads](https://www.python.org/downloads/)
2. Click the big yellow **"Download Python 3.x.x"** button
3. Run the downloaded file
4. ⚠️ **IMPORTANT:** Check the box that says **"Add Python to PATH"**
5. Click **"Install Now"**
6. Wait for installation to complete
7. Click **"Close"**

#### Mac

1. Open **Terminal** (search "Terminal" in Spotlight)
2. Copy and paste this command:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

3. Press Enter and wait
4. Then type:

```bash
brew install python
```
#### Linux (Ubuntu/Debian)
```bash
   sudo apt update
   sudo apt install python3 python3-pip python3-venv
```
5. Verify Installation

Open Command Prompt (Windows) or Terminal (Mac) and type:
```bash
python --version
```
You should see something like Python 3.11.5

### Step 2: Download the Trading System

#### Option A: Download ZIP (Easiest)

1. Download the trading system ZIP file
2. Extract it to a folder:
   - Windows: C:\trading_system
   - Mac/Linux: ~/trading_system

####  Option B: Create Using Setup Script
1. Create a new folder called trading_system
2. Save the setup script as setup_trading_system.py in that folder
3. Open Command Prompt/Terminal
4. Navigate to the folder:

```bash
# Windows
cd C:\trading_system

# Mac/Linux
cd ~/trading_system
```
5. Run the setup:
```bash
python setup_trading_system.py
```
### Step 3: Install Required Components

#### Open Command Prompt (Windows) or Terminal (Mac):

```bash
# Navigate to trading system folder
# Windows:
cd C:\trading_system

# Mac/Linux:
cd ~/trading_system
# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install all required components (takes 2-5 minutes)
pip install -r requirements.txt
```

###  Step 4: Test the Installation
```bash
python main.py signals
```
If you see stock signals appearing, congratulations! Installation is complete! 🎉

###  🚀 Quick Start (5 Minutes)
#### Generate Signals (All Markets)
```bash
   python main.py signals
```
#### Generate Signals (Specific Market)
```bash
    python main.py signals --market DE   # Germany
    python main.py signals --market US   # USA
    python main.py signals --market IN   # India
```
#### Analyze a Stock
```bash
    python main.py analyze -s NVDA       # US stock
    python main.py analyze -s SAP.DE     # German stock
    python main.py analyze -s TCS.NS     # Indian stock
```
#### Run Backtest
```bash
python backtester.py run             # Test current universe
python backtester.py compare         # Compare all markets
```
#### Launch Web Dashboard
```bash
python run_dashboard.py
# Open browser to: http://localhost:8501
```

### 📅 Daily Trading Workflow
#### Your Daily Schedule
For Germany-Based Traders (CET/CEST)
```bash
┌──────────────────────────────────────────────────────────────────┐
│                    DAILY TRADING SCHEDULE                        │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│   04:45  │  🇮🇳 India market OPENS                               │
│                                                                  │
│   08:00  │  ☀️ MORNING ROUTINE                                   │
│          │  python daily_workflow.py morning                     │
│          │  • Check India signals                                │
│          │  • Prepare for German market                          │
│                                                                  │
│   09:00  │  🇩🇪 German market OPENS                              │
│          │  • Place German orders                                │
│          │  • Set stop losses                                    │
│                                                                  │
│   11:00  │  🇮🇳 India market CLOSES                              │
│          │  • Review Indian positions                            │
│                                                                  │
│   12:00  │  🌞 MIDDAY CHECK                                      │
│          │  python daily_workflow.py midday                      │
│          │  • Review German positions                            │
│                                                                  │
│   15:30  │  🇺🇸 US market OPENS                                  │
│          │  python daily_workflow.py afternoon                   │
│          │  • Generate US signals                                │
│          │  • Place US orders                                    │
│                                                                  │
│   17:30  │  🇩🇪 German market CLOSES                             │
│          │  • Review German positions                            │
│                                                                  │
│   20:00  │  🌙 EVENING ROUTINE                                   │
│          │  python daily_workflow.py evening                     │
│          │  • Daily summary                                      │
│          │  • Log trades                                         │
│                                                                  │
│   22:00  │  🇺🇸 US market CLOSES                                 │
│          │  • Final review                                       │
│                                                                  │
├──────────────────────────────────────────────────────────────────┤
│                      WEEKEND TASKS                               │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│   SUNDAY │  📊 Weekly update                                     │
│          │  python main.py quick-update                          │
│          │  python backtester.py compare                         │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

#### Quick Daily Commands
```bash
# Morning (08:00)
python daily_workflow.py morning

# Midday (12:00)
python daily_workflow.py midday

# Afternoon (15:30)
python daily_workflow.py afternoon

# Evening (20:00)
python daily_workflow.py evening

# Full scan anytime
python daily_workflow.py scan

# See schedule
python daily_workflow.py schedule

```
### 📖 Command Reference
#### Complete Command List

```bash
╔══════════════════════════════════════════════════════════════════╗
║                    ALL TRADING COMMANDS                          ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  📊 SIGNALS & ANALYSIS                                           ║
║  ─────────────────────────────────────────────────────────────   ║
║  python main.py signals                 # All markets            ║
║  python main.py signals --market DE     # Germany only           ║
║  python main.py signals --market US     # US only                ║
║  python main.py signals --market IN     # India only             ║
║  python main.py scan                    # Full stock scan        ║
║  python main.py analyze -s SYMBOL       # Analyze specific stock ║
║  python main.py status                  # Show market status     ║
║                                                                  ║
║  📈 UNIVERSE MANAGEMENT                                          ║
║  ─────────────────────────────────────────────────────────────   ║
║  python main.py quick-update            # Quick update (~10 min) ║
║  python main.py update-universe         # Full update (~30 min)  ║
║  python main.py universe                # Show current stocks    ║
║  python main.py universe --market DE    # Show German stocks     ║
║  python main.py universe-report         # Detailed rankings      ║
║                                                                  ║
║  🧪 BACKTESTING                                                  ║
║  ─────────────────────────────────────────────────────────────   ║
║  python backtester.py run               # Test current universe  ║
║  python backtester.py compare           # Compare all markets    ║
║  python backtester.py german            # Test German stocks     ║
║  python backtester.py us                # Test US stocks         ║
║  python backtester.py india             # Test Indian stocks     ║
║  python backtester.py run -p 2y         # 2-year backtest        ║
║  python backtester.py run --save        # Save results           ║
║                                                                  ║
║  📅 DAILY WORKFLOW                                               ║
║  ─────────────────────────────────────────────────────────────   ║
║  python daily_workflow.py schedule      # Show schedule          ║
║  python daily_workflow.py morning       # Morning routine        ║
║  python daily_workflow.py midday        # Midday check           ║
║  python daily_workflow.py afternoon     # Afternoon (US open)    ║
║  python daily_workflow.py evening       # Evening summary        ║
║  python daily_workflow.py scan          # Full scan              ║
║                                                                  ║
║  📝 TRADE MANAGEMENT                                             ║
║  ─────────────────────────────────────────────────────────────   ║
║  python trade_journal.py                # Trade journal          ║
║  python monitor_positions.py            # Monitor positions      ║
║                                                                  ║
║  🔔 ALERTS                                                       ║
║  ─────────────────────────────────────────────────────────────   ║
║  python alert_system.py status          # Check alert config     ║
║  python alert_system.py test            # Send test alert        ║
║                                                                  ║
║  🌐 WEB DASHBOARD                                                ║
║  ─────────────────────────────────────────────────────────────   ║
║  python run_dashboard.py                # Launch dashboard       ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
```

#### Symbol Format by Market
| Market | Format | Examples |
|--------|--------|----------|
| 🇺🇸 US | `SYMBOL` | NVDA, AAPL, MSFT |
| 🇩🇪 Germany | `SYMBOL.DE` | SAP.DE, BMW.DE, SIE.DE |
| 🇮🇳 India (NSE) | `SYMBOL.NS` | TCS.NS, RELIANCE.NS |
| 🇮🇳 India (BSE) | `SYMBOL.BO` | TCS.BO, RELIANCE.BO |


#### 🧪 Backtesting Guide
**What is Backtesting?**
Backtesting tests your trading strategy on historical data to see how it would have performed in the past. This helps you:

✅ Verify the strategy works before risking real money
✅ Understand expected win rate and profit factor
✅ Compare performance across different markets
✅ Identify the best stocks to trade

#### Running Backtests
**Basic Backtest**
```bash
python backtester.py run
```
#### Compare All Markets
```bash
python backtester.py compare
```
#### Sample Output:
```bash
============================================================
MARKET COMPARISON RESULTS
============================================================

Market     Trades     Win Rate     P&L             Profit Factor
------------------------------------------------------------
🇩🇪 DE     45         57.8%        €3,250.00       1.85
🇺🇸 US     52         61.5%        €4,120.00       2.12
🇮🇳 IN     38         52.6%        €1,890.00       1.45
```

#### Market-Specific Backtest
```bash
python backtester.py german    # German stocks only
python backtester.py us        # US stocks only
python backtester.py india     # Indian stocks only
```
#### Custom Period
```bash
python backtester.py run -p 6mo   # 6 months
python backtester.py run -p 1y    # 1 year (default)
python backtester.py run -p 2y    # 2 years
python backtester.py run -p 5y    # 5 years
```
#### Save Results
```bash
python backtester.py run --save
# Saves to: data/backtest_YYYYMMDD_HHMMSS.json
```
#### Understanding Backtest Results
| Metric | Good Value | What It Means |
|--------|------------|---------------|
| Win Rate | >50% | Percentage of profitable trades |
| Profit Factor | >1.5 | Gross profit ÷ Gross loss |
| Max Drawdown | <20% | Largest peak-to-trough decline |
| Avg Hold Days | 3-7 | Average trade duration |
| Total P&L | Positive | Overall profit/loss |
| Avg Win | > Avg Loss | Average winning trade size |


#### Interpreting Results
```bash
✅ EXCELLENT RESULTS:
   Win Rate: 60%+
   Profit Factor: 2.0+
   Max Drawdown: <10%

✅ GOOD RESULTS:
   Win Rate: 55%+
   Profit Factor: 1.5+
   Max Drawdown: <15%

⚠️ ACCEPTABLE RESULTS:
   Win Rate: 50-55%
   Profit Factor: 1.2-1.5
   Max Drawdown: 15-20%

❌ NEEDS IMPROVEMENT:
   Win Rate: <50%
   Profit Factor: <1.2
   Max Drawdown: >25%
```
#### Exit Reasons Explained
| Reason | Meaning |
|--------|---------|
| `TARGET_1` | Price hit first profit target ✅ |
| `TARGET_2` | Price hit second profit target ✅ |
| `STOP_LOSS` | Price hit stop loss ❌ |
| `TIME_EXIT` | Held maximum days (10) ⏱️ |
| `TRAIL_STOP` | Trailing stop triggered 📉 |


### 🎯 Understanding the Signals
#### Signal Types Explained
#### Signal	Meaning	Action
🟢 STRONG BUY	Excellent setup, high confidence	Consider trading
🟡 BUY	Good setup, moderate confidence	Consider trading
🟠 WATCH	Potential setup forming	Add to watchlist, wait
🔴 AVOID	Poor setup or risky	Do not trade

Reading a Signal
```bash
==================================================
🎯 STRONG BUY: NVDA
==================================================

NVIDIA Corporation              ← Company name
Sector: Technology              ← Industry sector
Setup: PULLBACK                 ← Type of trading setup
Score: 75/100                   ← Confidence score (higher = better)

📊 CURRENT STATUS:
   Price: $235.74               ← Current stock price
   RSI: 52.3                    ← Momentum indicator (30-70 is good)
   Trend: BULLISH ✓             ← Overall direction is UP

💰 TRADE SETUP:
   Entry: $235.00               ← BUY at this price
   Stop Loss: $223.00 (-5.1%)   ← SELL if price drops here
   Target 1: $259.00 (+10.2%)   ← SELL HALF here
   Target 2: $275.00 (+17.0%)   ← SELL REST here

📈 RISK/REWARD:
   R:R: 2.0                     ← Risk $1 to make $2
```

### What the Numbers Mean
#### RSI (Relative Strength Index)

| Value    | Meaning                   |
|----------|---------------------------|
| Below 30 | Oversold (might bounce up)|
| 30-70    | Normal range ✓            |
| Above 70 | Overbought (might drop)   |


####  Score (0-100)

| Score    | Signal Quality |
|----------|----------------|
| 70-100   | Strong signal  |
| 55-69    | Good signal    |
| 40-54    | Weak signal    |
| Below 40 | Avoid          |


#### R:R (Risk/Reward Ratio)

| Ratio         | Recommendation                              |
|---------------|---------------------------------------------|
| 2.0 or higher | Good trade (make $2 for every $1 risked)    |
| 1.5-2.0       | Acceptable                                  |
| Below 1.5     | Not recommended                             |


### 💰 How to Place Trades

####  Step 1: Get the Signal
```bash
   python main.py signals --market DE

```
#### Example Signal:

```bash
NVDA
Entry: $235.00
Stop Loss: $223.00
Target 1: $259.00
Shares to buy: 62
```

#### Step 2: Calculate Position Size
The system tells you, but here's the formula:

```bash
Risk Amount = Account Size × 1.5%
            = $50,000 × 0.015
            = $750

Risk Per Share = Entry - Stop Loss
               = $235 - $223
               = $12

Shares to Buy = Risk Amount ÷ Risk Per Share
              = $750 ÷ $12
              = 62 shares
```

#### Step 3: Place Buy Order
1. Log into your broker (TD Ameritrade, Fidelity, Schwab, etc.)
2. Search for the stock symbol (e.g., NVDA)
3. Click "Trade" or "Buy"
4. Enter:
     - Action: Buy
     - Quantity: 62 shares
     - Order Type: Limit
     - Limit Price: $235.00
     - Duration: Day (or GTC - Good Till Cancelled)
5. Click "Review" then "Submit"

####  Step 4: Set Stop Loss (IMPORTANT!)
Once your buy order fills:

1. Click "Trade" or "Sell" on the same stock
2. Enter:
     - Action: Sell
     - Quantity: 62 shares
     - Order Type: Stop
     - Stop Price: $223.00
     - Duration: GTC (Good Till Cancelled)
3. Click "Review" then "Submit"

#### Step 5: Set Price Alert

Most brokers let you set alerts:

1. Go to "Alerts" or "Notifications"
2. Set alert for NVDA at $259.00 (Target 1)
3. Choose notification method (email/text)

#### Step 6: Manage the Trade
**When Target 1 is Hit ($259.00):**

1. Sell half (41 shares)
2. Move stop loss to breakeven ($259.00)
3. Let remaining shares run to Target 2

**When Target 2 is Hit (€310.00):**

1. Sell remaining shares
2. Log the trade

#### Order Types Explained

```bash
┌─────────────────────────────────────────────────────────────┐
│                     ORDER TYPES EXPLAINED                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  📗 LIMIT ORDER (For Buying)                                │
│  ─────────────────────────────────────────────────────────  │
│  "Buy only if price is $235 or lower"                       │
│                                                             │
│  Use when: You want to buy at a specific price or better    │
│                                                             │
│                                                             │
│  📕 STOP ORDER (For Selling / Stop Loss)                    │
│  ─────────────────────────────────────────────────────────  │
│  "Sell automatically if price drops to $223"                │
│                                                             │
│  Use when: You want to limit your losses                    │
│                                                             │
│                                                             │
│  📘 MARKET ORDER (Immediate)                                │
│  ─────────────────────────────────────────────────────────  │
│  "Buy/Sell right now at current price"                      │
│                                                             │
│  Use when: You need to get in/out immediately               │
│  Warning: Price might be different than expected            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 📊 Managing Your Trades
#### Using the Trade Journal
```bash
python trade_journal.py
```
#### Adding a New Trade
When you buy a stock:
```bash
==================================================
ADD NEW TRADE
==================================================

Symbol: NVDA
Entry Price: $235.00
Shares: 62
Stop Loss: $223.00
Target 1: $259.00
Setup Type: PULLBACK
Notes: Strong momentum, good volume

✓ Trade #1 added: 62 NVDA @ $235.00
```

#### Closing a Trade
When you sell:

```bash
==================================================
OPEN TRADES
==================================================
trade_id  symbol  entry_price  shares  date_entry
       1    NVDA       235.00      62  2026-05-15

Enter Trade ID to close: 1
Exit Price: $259.00

WIN ✓: $1,488.00 (+10.21%)

```
#### Viewing Your Statistics
```bash
==================================================
TRADING STATISTICS
==================================================
Total Trades: 15
Wins: 10 | Losses: 5
Win Rate: 66.7%

Total P&L: $4,250.00
Avg Win: $580.00
Avg Loss: $310.00
Profit Factor: 1.87
==================================================
```

### Trade Management Rules
#### Rule 1: Always Use Stop Loss
- **Never** trade without a stop loss
- Set it **immediately** after your buy order fills
- **Don't move it further away from your entry**

#### Rule 2: Take Profits in Stages
When price hits Target 1:

1. Sell half your shares (31 out of 62)
2. Move stop loss to breakeven (your entry price)
3. Let the rest run to Target 2

#### Rule 3: Don't Overtrade
- Maximum **8 positions** at once
- Maximum **4 positions** per market
- Maximum **1.5% risk** per trade
- Maximum **25%** of account in one stock

### 🌐 Using the Web Dashboard
#### Starting the Dashboard
```bash
python run_dashboard.py
```
Then open your browser and go to: http://localhost:8501

#### Dashboard Pages

| Page           | Purpose                                      |
|----------------|----------------------------------------------|
| 📊 Dashboard   | Account overview, quick scan, market summary |
| 🔍 Scanner     | Scan stocks with custom filters              |
| 📈 Analysis    | Detailed charts and analysis for any stock   |
| 🎯 Signals     | Generate trading signals                     |
| 📉 Backtest    | Test strategy on historical data             |
| 📐 Calculator  | Calculate position size                      |


### 🔔 Setting Up Alerts

#### Check Current Status
```bash
  python alert_system.py status
```
#### Option 1: Telegram Alerts (Recommended)

Step 1: Create a Telegram Bot
   1. Open Telegram app
   2. Search for @BotFather
   3. Send: /newbot
   4. Follow instructions to name your bot
   5. Copy the **API Token (looks like: 123456789:ABCdefGHIjklMNOpqrsTUVwxyz)**

Step 2: Get Your Chat ID
   - Search for **@userinfobot** in Telegram
   - Send any message to it
   - Copy your **Chat ID (a number like 123456789)**

Step 3: Configure the System

1. Open the file .env in your trading_system folder
2. Add these lines:
```bash
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=123456789
```
3. Save the file

Step 4: Test It
```bash
python alert_system.py test
```

You should receive a message on Telegram!

####  Option 2: Email Alerts
Step 1: Create App Password (Gmail)
    - Go to Google Account Security
    - Enable 2-Step Verification if not already
    - Go to App Passwords
    - Select app: Mail
    - Select device: Other (name it "Trading System")
    - Click Generate
    - Copy the 16-character password
Step 2: Configure the System
    - Open .env file
    - Add:
        *EMAIL_SENDER=your_email@gmail.com
        EMAIL_PASSWORD=xxxx xxxx xxxx xxxx
        EMAIL_RECEIVER=your_email@gmail.com*
        SMTP_SERVER=smtp.gmail.com
        SMTP_PORT=587
    - Save the file

### 🇩🇪 For Germany-Based Traders
Your Advantage
Being in Germany, you can trade 3 markets across different time zones:

┌─────────────────────────────────────────────────────────────────┐
│              YOUR TRADING DAY (German Time - CET)               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   04:45 - 11:00  │  🇮🇳 INDIA - Morning opportunity             │
│   09:00 - 17:30  │  🇩🇪 GERMANY - Primary market                │
│   15:30 - 22:00  │  🇺🇸 USA - Afternoon/evening                 │
│                                                                 │
│   OVERLAP TIMES:                                                │
│   09:00 - 11:00  │  🇮🇳🇩🇪 India + Germany                       │
│   15:30 - 17:30  │  🇩🇪🇺🇸 Germany + USA                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
#### Recommended Allocation
| Market | Positions | Portfolio % | Priority |
|--------|-----------|-------------|----------|
| 🇩🇪 Germany | 4 | 50% | Primary |
| 🇺🇸 USA | 3 | 40% | Secondary |
| 🇮🇳 India | 1-2 | 10% | Optional |

#### German Broker Options
| Broker | Best For | Fees |
|--------|----------|------|
| Trade Republic | German + US | €1/trade |
| Scalable Capital | German + US | €0.99/trade |
| Interactive Brokers | All markets | Low, varies |
| ING DiBa | German stocks | €4.90+ |
| Comdirect | German stocks | €4.90+ |

#### Tax Considerations (Germany)
- Abgeltungssteuer: 25% + Soli + Church tax (~26.4%)
- Freibetrag: €1,000 per year tax-free (as of 2023)
- Keep records for Steuererklärung
- Consider using Freistellungsauftrag with your broker

### ❓ Frequently Asked Questions
#### General Questions

Q: How much money do I need to start?
A: The system is configured for 50,000,butyoucanchangethisin‘config.py‘.Werecommendatleast5,000 for proper position sizing.

Q: Is this guaranteed to make money?
A: No trading system guarantees profits. This system aims for 4% monthly returns, but losses are possible. Always use stop losses and never risk money you can't afford to lose.

Q: Do I need to watch the market all day?
A: No! This is a swing trading system. You check signals in the morning, place orders, set stop losses, and check back in the evening. Each trade lasts 2-10 days typically.

Q: What stocks does it trade?
A: The system scans S&P 500 and NASDAQ 100 stocks, then automatically selects the top 50 with the best momentum and volume.

Technical Questions
Q: The command says "python not found"
A: Python isn't installed correctly. Reinstall Python and make sure to check "Add Python to PATH" during installation.

Q: I get errors when running commands
A: Make sure you:

Are in the correct folder: cd C:\trading_system
Installed requirements: pip install -r requirements.txt
Are using the correct command spelling
Q: How do I update the stock list?
A: Run python main.py quick-update weekly to get the best momentum stocks.

Q: Can I add my own stocks?
A: Yes! Edit the STOCK_UNIVERSE list in config.py to add any stock symbols you want to track.

Trading Questions
Q: What does "PULLBACK" setup mean?
A: The stock is in an uptrend but has temporarily dipped to a support level - a good buying opportunity.

Q: What does "MOMENTUM" setup mean?
A: The stock is moving strongly in one direction with good volume.

Q: Should I trade every signal?
A: No. Focus on STRONG BUY signals first. Only trade 1-3 stocks at a time when starting.

Q: What if my order doesn't fill?
A: If the stock doesn't reach your entry price, that's okay. Don't chase it - wait for the next signal.

### 🔧 Troubleshooting
#### Common Issues and Solutions
#### Issue: Installation Issues
```bash
# If pip fails
python -m pip install --upgrade pip
pip install -r requirements.txt

# If specific package fails
pip install yfinance pandas numpy --upgrade


```
####  Issue: "Data Issues"
```bash
# Clear cache and re-download
rm -rf data/*.csv
python main.py quick-update

```

#### Issue: Dashboard Won't Start
```bash
pip install streamlit --upgrade
streamlit run dashboard.py

```
#### Issue: No Data for Symbol
- Check symbol format (NVDA, SAP.DE, TCS.NS)
- Yahoo Finance may be temporarily down
- Some stocks may have insufficient history
#### Issue: Slow performance
- Close other programs
- Run python main.py quick-update instead of full update
- Reduce the number of stocks in config.py

#### Issue: Getting Help
- Getting Help
- Check this README
- Check error messages carefully
- Restart and try again
- Check your internet connection
- Verify Python and packages are installed correctly

### 📚 Glossary of Terms
| Term          | Definition                                              |
|---------------|---------------------------------------------------------|
| ATR           | Average True Range - measures how much a stock moves daily |
| Backtest      | Testing strategy on historical data                     |
| Drawdown      | Decline from peak to trough                             |
| EMA           | Exponential Moving Average - average price over time    |
| Entry         | The price at which you buy the stock                    |
| Exit          | The price at which you sell the stock                   |
| Limit Order   | An order to buy/sell at a specific price or better      |
| Momentum      | How strongly a stock is moving in one direction         |
| Position Size | How many shares to buy                                  |
| Profit Factor | Gross profit ÷ gross loss                               |
| Pullback      | A temporary dip in an uptrending stock                  |
| R:R           | Risk/Reward - ratio of potential profit to potential loss |
| RSI           | Relative Strength Index - measures overbought/oversold  |
| Stop Loss     | An order to sell if price drops to limit losses         |
| Support       | Price level where stock tends to stop falling           |
| Resistance    | Price level where stock tends to stop rising            |
| Swing Trading | Holding stocks for days to weeks                        |
| Target        | Price level where you plan to take profits              |
| Universe      | List of stocks being tracked                            |
| Win Rate      | Percentage of profitable trades                         |


### 📋 Quick Reference Card
#### Print this and keep it at your desk!
```bash
╔══════════════════════════════════════════════════════════════╗
║                   DAILY TRADING CHECKLIST                    ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  ☐ MORNING                                                   ║
║    python daily_workflow.py morning                          ║
║    • Review signals                                          ║
║    • Place orders                                            ║
║    • Set stop losses                                         ║
║                                                              ║
║  ☐ EVENING                                                   ║
║    python daily_workflow.py evening                          ║
║    • Review positions                                        ║
║    • Log trades: python trade_journal.py                     ║
║                                                              ║
║  ☐ WEEKLY (Sunday)                                           ║
║    python main.py quick-update                               ║
║    python backtester.py compare                              ║
║                                                              ║
╠══════════════════════════════════════════════════════════════╣
║                      POSITION SIZING                         ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  Risk = Account × 1.5%                                       ║
║  Shares = Risk ÷ (Entry - Stop)                              ║
║                                                              ║
║  Example: €50,000 account, Entry €100, Stop €95              ║
║  Risk = €750, Shares = €750 ÷ €5 = 150                       ║
║                                                              ║
╠══════════════════════════════════════════════════════════════╣
║                      TRADING RULES                           ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  ✓ Always use stop loss                                      ║
║  ✓ Max 1.5% risk per trade                                   ║
║  ✓ Max 8 positions total                                     ║
║  ✓ Sell 50% at Target 1                                      ║
║  ✓ Move stop to breakeven after T1                           ║
║  ✓ Don't chase - wait for entry                              ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
```
### File Structure
```bash
  trading_system/
│
├── 📁 data/                      # Auto-created data files
│   ├── global_universe.json     # Current stock universe
│   ├── global_rankings.csv      # Stock rankings
│   └── backtest_*.json          # Backtest results
│
├── 📁 logs/                      # Log files
│
├── 📄 .env                       # Your API keys (create from .env.example)
├── 📄 .env.example               # API key template
├── 📄 requirements.txt           # Python dependencies
├── 📄 README.md                  # This file
│
├── 📄 config.py                  # System configuration
├── 📄 main.py                    # Main CLI entry point
├── 📄 market_config.py           # Market definitions
│
├── 📄 global_data_fetcher.py     # Multi-market data fetching
├── 📄 global_universe_manager.py # Stock universe management
├── 📄 global_signal_generator.py # Signal generation
│
├── 📄 data_fetcher.py            # Basic data fetching
├── 📄 technical_analyzer.py      # Technical analysis
├── 📄 stock_screener.py          # Stock screening
├── 📄 signal_generator.py        # Legacy signal generation
├── 📄 position_manager.py        # Position sizing
├── 📄 backtester.py              # Strategy backtesting
│
├── 📄 alert_system.py            # Telegram/Email alerts
├── 📄 broker_api.py              # Broker integration
├── 📄 trade_journal.py           # Trade logging
├── 📄 monitor_positions.py       # Position monitoring
│
├── 📄 daily_workflow.py          # Daily routine scripts
├── 📄 dashboard.py               # Web dashboard
└── 📄 run_dashboard.py           # Dashboard launcher
```
### ⚠️ Risk Disclaimer

**IMPORTANT**: Trading involves substantial risk of loss. This software is for educational and informational purposes only. It does not constitute financial advice.

- Never invest money you cannot afford to lose
- Past performance does not guarantee future results
- Always do your own research
- Use stop losses on every trade
- Start with paper trading to learn the system

### 📄 License
 This project is for personal and educational use.

### 🎓 Next Steps
#### Week 1: Paper Trading

- Run signals daily but don't use real money
- Write down what you would have traded
- Track results on paper
- Learn to read signals

#### Week 2-3: Small Positions
- Start with half the recommended position size
- Trade only STRONG BUY signals
- Maximum 2 positions at once
- Use trade journal

#### Week 4+: Normal Trading
- Gradually increase to full position sizes
- Add more positions (up to 8)
- Review your trade journal weekly
- Adjust strategy based on results


Good luck and happy trading!
