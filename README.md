# 📈 Swing Trading System

## Complete User Guide for Beginners

> **Your automated stock trading assistant that scans 500+ stocks daily to find the best trading opportunities.**

---

## 🎯 What is This Tool?

This is an **automated stock trading assistant** that:

- ✅ Scans 500+ stocks daily to find the best opportunities
- ✅ Tells you exactly **when to buy**, **when to sell**, and **where to set stop loss**
- ✅ Calculates how many shares to buy based on your account size
- ✅ Sends alerts to your phone/email when opportunities arise
- ✅ Tracks your trades and shows your performance
- ✅ Tests strategies on past data before you risk real money

**Goal:** Help you make **4% monthly returns** (~48% yearly) through swing trading.

---

## 📋 Table of Contents

1. [What You Need](#-what-you-need)
2. [Installation](#-installation-step-by-step)
3. [Quick Start](#-quick-start-5-minutes)
4. [Daily Trading Workflow](#-daily-trading-workflow)
5. [All Commands Explained](#-all-commands-explained)
6. [Understanding the Signals](#-understanding-the-signals)
7. [How to Place Trades](#-how-to-place-trades)
8. [Managing Your Trades](#-managing-your-trades)
9. [Using the Web Dashboard](#-using-the-web-dashboard)
10. [Setting Up Alerts](#-setting-up-alerts)
11. [Frequently Asked Questions](#-frequently-asked-questions)
12. [Troubleshooting](#-troubleshooting)
13. [Glossary of Terms](#-glossary-of-terms)

---

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

# Install all required components (takes 2-5 minutes)
pip install -r requirements.txt
```

You'll see a lot of text scrolling. Wait until you see the command prompt again.

###  Step 4: Test the Installation
```bash
python main.py signals
```
If you see stock signals appearing, congratulations! Installation is complete! 🎉

###  🚀 Quick Start (5 Minutes)
#### Your First Signal
Open Command Prompt/Terminal and type:
```bash
cd C:\trading_system
python main.py signals
```
####  What you'll see:
```bash
🎯 Swing Trading System - 2026-05-15 09:00
Account Size: $50,000 | Target: 4.0%/month

============================================================
GENERATING SIGNALS
============================================================
Analyzing 40 stocks...

Results:
  STRONG BUY: 2
  BUY: 5
  WATCH: 8
  Total Signals: 7

==================================================
🎯 STRONG BUY: NVDA
==================================================

NVIDIA Corporation
Sector: Technology
Setup: PULLBACK
Score: 75/100

📊 CURRENT STATUS:
   Price: $235.74
   RSI: 52.3
   Trend: BULLISH ✓

💰 TRADE SETUP:
   Entry: $235.00
   Stop Loss: $223.00 (-5.1%)
   Target 1: $259.00 (+10.2%)
   Target 2: $275.00 (+17.0%)

📈 RISK/REWARD:
   R:R: 2.0 (You risk $1 to make $2)

```
#### What This Means
| Term              | Meaning                                                   |
|-------------------|-----------------------------------------------------------|
| STRONG BUY        | High confidence signal - consider trading                 |
| Entry: $235.00    | Buy the stock at this price                               |
| Stop Loss: $223.00| Sell immediately if price drops here (limits your loss)   |
| Target 1: $259.00 | Sell half your shares here for profit                     |
| Target 2: $275.00 | Sell remaining shares here for more profit                |
| R:R: 2.0          | Risk/Reward ratio - you risk $1 to potentially make $2    |


### 📅 Daily Trading Workflow
#### Your Daily Schedule
```bash
┌──────────────────────────────────────────────────────────────┐
│                    DAILY TRADING ROUTINE                     │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│   ☀️ MORNING (Before 9:30 AM)                                │
│   ┌────────────────────────────────────────────────────────┐ │
│   │ 1. Open Command Prompt                                 │ │
│   │ 2. Type: cd C:\trading_system                          │ │
│   │ 3. Type: python main.py signals                        │ │
│   │ 4. Review the signals                                  │ │
│   │ 5. Decide which stock(s) to trade                      │ │
│   └────────────────────────────────────────────────────────┘ │
│                                                              │
│   🔔 MARKET OPEN (9:30 AM)                                   │
│   ┌────────────────────────────────────────────────────────┐ │
│   │ 1. Log into your broker                                │ │
│   │ 2. Place limit buy order at "Entry" price              │ │
│   │ 3. Once filled, set stop loss order                    │ │
│   │ 4. Set price alert at Target 1                         │ │
│   └────────────────────────────────────────────────────────┘ │
│                                                              │
│   📊 DURING THE DAY (Optional)                               │
│   ┌────────────────────────────────────────────────────────┐ │
│   │ Check your positions once or twice                     │ │
│   │ No need to watch constantly - stop loss protects you   │ │
│   └────────────────────────────────────────────────────────┘ │
│                                                              │
│   🌙 EVENING (After 4:00 PM)                                 │
│   ┌────────────────────────────────────────────────────────┐ │
│   │ 1. Check if any orders filled                          │ │
│   │ 2. Log your trades: python trade_journal.py            │ │
│   │ 3. Plan for tomorrow                                   │ │
│   └────────────────────────────────────────────────────────┘ │
│                                                              │
│   📆 WEEKLY (Sunday Evening)                                 │
│   ┌────────────────────────────────────────────────────────┐ │
│   │ Update stock universe: python main.py quick-update     │ │
│   └────────────────────────────────────────────────────────┘ │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```
### 📖 All Commands Explained
#### Command Reference Card

```bash
╔══════════════════════════════════════════════════════════════════╗
║                    TRADING SYSTEM COMMANDS                       ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  📊 DAILY COMMANDS (Use these every day)                         ║
║  ────────────────────────────────────────────────────────────    ║
║  python main.py signals                                          ║
║      → Get today's buy signals                                   ║
║                                                                  ║
║  python main.py analyze -s NVDA                                  ║
║      → Analyze a specific stock (replace NVDA with any symbol)   ║
║                                                                  ║
║  python main.py scan                                             ║
║      → Full scan of all stocks                                   ║
║                                                                  ║
║                                                                  ║
║  📈 UNIVERSE COMMANDS (Use weekly)                               ║
║  ────────────────────────────────────────────────────────────    ║
║  python main.py quick-update                                     ║
║      → Update stock list with best momentum stocks (10 min)      ║
║                                                                  ║
║  python main.py universe                                         ║
║      → Show current stocks being tracked                         ║
║                                                                  ║
║  python main.py universe-report                                  ║
║      → Detailed report of all ranked stocks                      ║
║                                                                  ║
║                                                                  ║
║  📝 TRADE MANAGEMENT                                             ║
║  ────────────────────────────────────────────────────────────    ║
║  python trade_journal.py                                         ║
║      → Log and track your trades                                 ║
║                                                                  ║
║  python monitor_positions.py                                     ║
║      → Watch your open positions live                            ║
║                                                                  ║
║                                                                  ║
║  🧪 TESTING                                                      ║
║  ────────────────────────────────────────────────────────────    ║
║  python main.py backtest                                         ║
║      → Test strategy on historical data                          ║
║                                                                  ║
║                                                                  ║
║  🌐 WEB DASHBOARD                                                ║
║  ────────────────────────────────────────────────────────────    ║
║  python run_dashboard.py                                         ║
║      → Open visual dashboard in browser                          ║
║      → Then go to: http://localhost:8501                         ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
```

#### Detailed Command Explanations

1. python main.py signals
What it does: Scans all stocks and shows you which ones to buy today.

When to use: Every morning before market opens (9:30 AM).

Example output:

```bash
🎯 STRONG BUY: NVDA
   Entry: $235.00
   Stop: $223.00
   Target: $259.00
```

2. python main.py analyze -s NVDA
What it does: Gives detailed analysis of one specific stock.

When to use: When you want more details about a stock.

Examples:

```bash
python main.py analyze -s AAPL
python main.py analyze -s TSLA
python main.py analyze -s MSFT
```

3. python main.py quick-update
What it does: Updates your stock list with the best performing stocks.

When to use: Once a week (Sunday evening recommended).

Why it's important: The market changes. This command finds the stocks with the best momentum, volume, and returns, and adds them to your watchlist automatically.

4. python trade_journal.py
What it does: Opens a menu to log and track all your trades.

Menu options:

```bash
1. Add New Trade      - Log when you buy a stock
2. Close Trade        - Log when you sell a stock
3. View Open Trades   - See your current positions
4. View Statistics    - See your win rate and profits
5. View All Trades    - See complete history

```
5. python run_dashboard.py
What it does: Opens a visual website on your computer with charts and buttons.

How to use:

Run the command
Open your web browser
Go to: http://localhost:8501
Use the visual interface instead of typing commands
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
#### Step-by-Step Guide (For Any Broker)

####  When You Get a Signal

#### Example Signal:

```bash
NVDA
Entry: $235.00
Stop Loss: $223.00
Target 1: $259.00
Shares to buy: 62
```

#### Step 1: Calculate Position Size
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

#### Step 2: Place Buy Order
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

####  Step 3: Set Stop Loss (IMPORTANT!)
Once your buy order fills:

1. Click "Trade" or "Sell" on the same stock
2. Enter:
     - Action: Sell
     - Quantity: 62 shares
     - Order Type: Stop
     - Stop Price: $223.00
     - Duration: GTC (Good Till Cancelled)
3. Click "Review" then "Submit"

#### Step 4: Set Price Alert

Most brokers let you set alerts:

1. Go to "Alerts" or "Notifications"
2. Set alert for NVDA at $259.00 (Target 1)
3. Choose notification method (email/text)

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
-  Never trade without a stop loss
- Set it immediately after your buy order fills
- Don't move it further away from your entry

#### Rule 2: Take Profits in Stages
When price hits Target 1:

1. Sell half your shares (31 out of 62)
2. Move stop loss to breakeven (your entry price)
3. Let the rest run to Target 2

#### Rule 3: Don't Overtrade
- Maximum 8 positions at once
- Maximum 1.5% risk per trade
- Maximum 25% of account in one stock

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
#### Option 1: Telegram Alerts (Recommended)

Step 1: Create a Telegram Bot
   1. Open Telegram app
   2. Search for @BotFather
   3. Send: /newbot
   4. Follow instructions to name your bot
   5. Copy the API Token (looks like: 123456789:ABCdefGHIjklMNOpqrsTUVwxyz)

Step 2: Get Your Chat ID
   - Search for @userinfobot in Telegram
   - Send any message to it
   - Copy your Chat ID (a number like 123456789)

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
python -c "from alert_system import AlertSystem; a = AlertSystem(); a.send_telegram('Test message!')"
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
    - Save the file

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
#### Issue: "No module named 'xyz'"
```bash
pip install xyz

# Or reinstall everything:
pip install -r requirements.txt

```
####  Issue: "No signals found"
This can happen when:

- Market is overbought (too high)
- It's a low volatility period
- Criteria are too strict

Solution: Wait for better setups or run python main.py scan to see all analyzed stocks.

#### Issue: "Connection error" or "No data"
- Check your internet connection
- Yahoo Finance might be temporarily down
- Wait a few minutes and try again

#### Issue: Dashboard won't open
```bash
# Try installing streamlit directly
pip install streamlit

# Then run
streamlit run dashboard.py
```

#### Issue: Slow performance
- Close other programs
- Run python main.py quick-update instead of full update
- Reduce the number of stocks in config.py

### 📚 Glossary of Terms
| Term          | Definition                                              |
|---------------|---------------------------------------------------------|
| ATR           | Average True Range - measures how much a stock moves daily |
| EMA           | Exponential Moving Average - average price over time    |
| Entry         | The price at which you buy the stock                    |
| Exit          | The price at which you sell the stock                   |
| Limit Order   | An order to buy/sell at a specific price or better      |
| Momentum      | How strongly a stock is moving in one direction         |
| Position Size | How many shares to buy                                  |
| Pullback      | A temporary dip in an uptrending stock                  |
| R:R           | Risk/Reward - ratio of potential profit to potential loss |
| RSI           | Relative Strength Index - measures overbought/oversold  |
| Stop Loss     | An order to sell if price drops to limit losses         |
| Support       | Price level where stock tends to stop falling           |
| Resistance    | Price level where stock tends to stop rising            |
| Swing Trading | Holding stocks for days to weeks                        |
| Target        | Price level where you plan to take profits              |
| Trend         | The overall direction of stock price                    |
| Volume        | Number of shares traded                                 |


### 📋 Quick Reference Card
#### Print this and keep it at your desk!
```bash
╔═══════════════════════════════════════════════════════════════╗
║                   DAILY TRADING CHECKLIST                     ║
╠═══════════════════════════════════════════════════════════════╣
║                                                               ║
║  ☐ MORNING (8:30 AM)                                          ║
║    cd C:\trading_system                                       ║
║    python main.py signals                                     ║
║                                                               ║
║  ☐ MARKET OPEN (9:30 AM)                                      ║
║    Place limit buy orders                                     ║
║    Set stop loss orders after fills                           ║
║                                                               ║
║  ☐ EVENING (After 4 PM)                                       ║
║    python trade_journal.py                                    ║
║    Log any new trades                                         ║
║                                                               ║
║  ☐ WEEKLY (Sunday)                                            ║
║    python main.py quick-update                                ║
║                                                               ║
╠═══════════════════════════════════════════════════════════════╣
║                      POSITION SIZING                          ║
╠═══════════════════════════════════════════════════════════════╣
║                                                               ║
║  Risk per trade = Account × 1.5%                              ║
║  Shares = Risk ÷ (Entry - Stop)                               ║
║                                                               ║
║  Example: $50,000 account                                     ║
║  Risk = $750                                                  ║
║  Entry = $100, Stop = $95                                     ║
║  Shares = $750 ÷ $5 = 150 shares                              ║
║                                                               ║
╠═══════════════════════════════════════════════════════════════╣
║                      SIGNAL MEANINGS                          ║
╠═══════════════════════════════════════════════════════════════╣
║                                                               ║
║  STRONG BUY (70+)  →  Trade with confidence                   ║
║  BUY (55-69)       →  Good opportunity                        ║
║  WATCH (40-54)     →  Wait for better setup                   ║
║  AVOID (<40)       →  Do not trade                            ║
║                                                               ║
╠═══════════════════════════════════════════════════════════════╣
║                      RULES TO FOLLOW                          ║
╠═══════════════════════════════════════════════════════════════╣
║                                                               ║
║  ✓ Always use stop loss                                       ║
║  ✓ Never risk more than 1.5% per trade                        ║
║  ✓ Maximum 8 positions at once                                ║
║  ✓ Take partial profits at Target 1                           ║
║  ✓ Move stop to breakeven after Target 1                      ║
║  ✓ Don't chase - wait for entry price                         ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
```
### 🎓 Next Steps
#### Week 1: Paper Trading

- Run signals daily but don't use real money
- Write down what you would have traded
- Track results on paper

#### Week 2-3: Small Positions
- Start with half the recommended position size
- Trade only STRONG BUY signals
- Maximum 2 positions at once

#### Week 4+: Normal Trading
- Gradually increase to full position sizes
- Add more positions (up to 8)
- Review your trade journal weekly

#### ⚠️ Risk Disclaimer
**IMPORTANT**: Trading involves substantial risk of loss. Never invest money you cannot afford to lose. This system is a tool to assist with trading decisions but does not guarantee profits. Past performance does not guarantee future results. Always do your own research before making investment decisions.

### 📄 License
This project is for educational and personal use.

### 📞 Support
If you need help:

Re-read this guide
Check the Troubleshooting section
Make sure all commands are typed exactly as shown
Restart your computer and try again
Good luck and happy trading!
