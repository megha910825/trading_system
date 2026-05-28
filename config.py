"""Trading System Configuration"""

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
MONTHLY_TARGET = 0.04
RISK_PER_TRADE = 0.015
MAX_POSITIONS = 8
MAX_POSITION_SIZE_PCT = 0.25
DAILY_LOSS_LIMIT = 0.02
WEEKLY_LOSS_LIMIT = 0.05

# Screening
SCREENING_CRITERIA = {
    "min_market_cap": 5_000_000_000,
    "min_avg_volume": 2_000_000,
    "min_price": 10,
    "max_price": 1500,
    "min_atr_pct": 2.5,
    "max_atr_pct": 8.0,
    "min_beta": 1.0,
    "max_beta": 2.5,
    "min_rsi": 35,
    "max_rsi": 65,
    "min_rel_volume": 1.0,
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

# Exit Rules
EXIT_RULES = {
    "stop_loss_atr_mult": 1.75,
    "target_1_atr_mult": 3.5,
    "target_2_atr_mult": 4.0,
    "max_hold_days": 10,
}

# Stock Universe
STOCK_UNIVERSE = [
    "NVDA", "AMD", "AVGO", "QCOM", "INTC", "MU",
    "MSFT", "CRM", "ADBE", "NOW", "SNOW", "DDOG",
    "GOOGL", "META", "AMZN", "NFLX", "UBER",
    "AAPL", "TSLA", "SQ", "PYPL", "COIN",
    "COST", "TGT", "WMT", "HD", "NKE",
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
