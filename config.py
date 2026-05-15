"""Trading System Configuration - OPTIMIZED FOR BETTER R:R"""

import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"

DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# Account
ACCOUNT_SIZE = 50000
MONTHLY_TARGET = 0.04  # 4%
RISK_PER_TRADE = 0.015  # 1.5%
MAX_POSITIONS = 8
MAX_POSITION_SIZE_PCT = 0.25
DAILY_LOSS_LIMIT = 0.02
WEEKLY_LOSS_LIMIT = 0.05

# Screening - RELAXED for current bull market
SCREENING_CRITERIA = {
    "min_market_cap": 2_000_000_000,   # $2B
    "min_avg_volume": 1_000_000,        # 1M
    "min_price": 10,
    "max_price": 2000,
    "min_atr_pct": 1.5,                 # Lower minimum
    "max_atr_pct": 10.0,                # Higher maximum
    "min_beta": 0.5,
    "max_beta": 3.0,
    "min_rsi": 25,                      # Allow oversold
    "max_rsi": 80,                      # Allow overbought in bull market
    "min_rel_volume": 0.5,              # Lower requirement
}

# Technical
TECHNICAL_PARAMS = {
    "ema_fast": 10,
    "ema_medium": 20,
    "ema_slow": 50,
    "ema_trend": 200,
    "rsi_period": 14,
    "atr_period": 14,
}

# Exit Rules - OPTIMIZED FOR BETTER R:R
EXIT_RULES = {
    "stop_loss_atr_mult": 1.5,    # Tighter stop = better R:R
    "target_1_atr_mult": 3.0,     # 3.0 / 1.5 = 2.0 R:R
    "target_2_atr_mult": 5.0,     # 5.0 / 1.5 = 3.33 R:R
    "max_hold_days": 10,
}

# Stock Universe
STOCK_UNIVERSE = [
    # Tech - Semiconductors
    "NVDA", "AMD", "AVGO", "QCOM", "INTC", "MU", "AMAT", "LRCX",
    # Tech - Software/Cloud
    "MSFT", "CRM", "ADBE", "NOW", "SNOW", "DDOG", "NET", "ZS", "CRWD", "PANW",
    # Tech - Internet
    "GOOGL", "META", "AMZN", "NFLX", "UBER", "ABNB",
    # Tech - Hardware
    "AAPL", "DELL",
    # Electric Vehicles
    "TSLA", "RIVN",
    # Fintech
    "PYPL", "COIN",
    # Consumer
    "COST", "TGT", "WMT", "HD", "NKE", "SBUX",
    # Finance
    "JPM", "GS", "V", "MA",
]

# APIs
ALPACA_API_KEY = os.getenv("ALPACA_API_KEY", "")
ALPACA_SECRET_KEY = os.getenv("ALPACA_SECRET_KEY", "")
ALPACA_BASE_URL = os.getenv("ALPACA_BASE_URL", "https://paper-api.alpaca.markets")

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

EMAIL_SENDER = os.getenv("EMAIL_SENDER", "")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER", "")
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
