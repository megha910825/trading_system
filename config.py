"""
Trading System Configuration - OPTIMIZED FOR GERMANY
"""

import os
from pathlib import Path
import json

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
UNIVERSE_FILE = DATA_DIR / "global_universe.json"

DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# ============================================================
# ACCOUNT SETTINGS
# ============================================================

# Set your account size (in EUR for easier tracking)
ACCOUNT_SIZE = 50000  # €50,000 (or adjust to your actual amount)
ACCOUNT_CURRENCY = "EUR"  # Your base currency

MONTHLY_TARGET = 0.04  # 4% monthly target
RISK_PER_TRADE = 0.015  # 1.5% risk per trade
MAX_POSITIONS = 8
MAX_POSITIONS_PER_MARKET = {
    "DE": 4,  # Primary market - more positions
    "US": 3,  # Secondary market
    "IN": 2,  # Tertiary market
}
MAX_POSITION_SIZE_PCT = 0.25
DAILY_LOSS_LIMIT = 0.02
WEEKLY_LOSS_LIMIT = 0.05

# ============================================================
# YOUR TIMEZONE
# ============================================================

HOME_TIMEZONE = "Europe/Berlin"

# ============================================================
# MARKET-SPECIFIC SETTINGS
# ============================================================

MARKET_SETTINGS = {
    "DE": {  # PRIMARY MARKET
        "enabled": True,
        "priority": 1,
        "max_positions": 4,
        "min_market_cap": 500_000_000,  # €500M
        "min_volume": 100_000,
        "min_price": 5,
        "max_price": 1000,
        "currency": "EUR",
    },
    "US": {  # SECONDARY MARKET
        "enabled": True,
        "priority": 2,
        "max_positions": 3,
        "min_market_cap": 2_000_000_000,  # $2B
        "min_volume": 500_000,
        "min_price": 10,
        "max_price": 2000,
        "currency": "USD",
    },
    "IN": {  # TERTIARY MARKET
        "enabled": True,
        "priority": 3,
        "max_positions": 2,
        "min_market_cap": 10_000_000_000,  # ₹1000 Cr
        "min_volume": 100_000,
        "min_price": 50,
        "max_price": 50000,
        "currency": "INR",
    },
}

# Markets in order of your trading priority
MARKET_PRIORITY = ["DE", "US", "IN"]

# ============================================================
# SCREENING CRITERIA
# ============================================================

SCREENING_CRITERIA = {
    "min_market_cap": 500_000_000,
    "min_avg_volume": 100_000,
    "min_price": 5,
    "max_price": 2000,
    "min_atr_pct": 1.5,
    "max_atr_pct": 10.0,
    "min_beta": 0.5,
    "max_beta": 3.0,
    "min_rsi": 25,
    "max_rsi": 80,
    "min_rel_volume": 0.5,
}

# ============================================================
# TECHNICAL PARAMETERS
# ============================================================

TECHNICAL_PARAMS = {
    "ema_fast": 10,
    "ema_medium": 20,
    "ema_slow": 50,
    "ema_trend": 200,
    "rsi_period": 14,
    "atr_period": 14,
}

# ============================================================
# EXIT RULES
# ============================================================

EXIT_RULES = {
    "stop_loss_atr_mult": 1.5,
    "target_1_atr_mult": 3.0,
    "target_2_atr_mult": 5.0,
    "max_hold_days": 10,
}

# ============================================================
# BROKERS FOR EACH MARKET
# ============================================================

# Your broker information (for reference)
BROKERS = {
    "DE": {
        "name": "Your German Broker",  # e.g., Trade Republic, Scalable, ING, etc.
        "notes": "Primary broker for XETRA stocks",
    },
    "US": {
        "name": "Your US Broker",  # e.g., Interactive Brokers, Trade Republic
        "notes": "For US stocks",
    },
    "IN": {
        "name": "Your India Broker",  # Optional
        "notes": "For Indian stocks (if available)",
    },
}

# ============================================================
# LOAD DYNAMIC UNIVERSE
# ============================================================

def load_global_universe() -> list:
    """Load global universe from file"""
    if UNIVERSE_FILE.exists():
        try:
            with open(UNIVERSE_FILE, 'r') as f:
                data = json.load(f)
                return data.get("trading_universe", [])
        except:
            pass
    return DEFAULT_UNIVERSE


# Default universe - prioritized for Germany
DEFAULT_UNIVERSE = [
    # Germany (Primary)
    "SAP.DE", "SIE.DE", "ALV.DE", "DTE.DE", "BMW.DE", "MBG.DE",
    "ADS.DE", "BAS.DE", "BAYN.DE", "IFX.DE", "MRK.DE", "RWE.DE",
    "AIR.DE", "DHL.DE", "VOW3.DE", "MUV2.DE", "DB1.DE",
    # US (Secondary)
    "NVDA", "AAPL", "MSFT", "GOOGL", "META", "AMZN", "TSLA",
    "AMD", "AVGO", "CRM", "NFLX",
    # India (Tertiary)
    "RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS",
]

STOCK_UNIVERSE = load_global_universe() or DEFAULT_UNIVERSE

# ============================================================
# API KEYS
# ============================================================

# Alpaca (for US paper trading)
ALPACA_API_KEY = os.getenv("ALPACA_API_KEY", "")
ALPACA_SECRET_KEY = os.getenv("ALPACA_SECRET_KEY", "")
ALPACA_BASE_URL = os.getenv("ALPACA_BASE_URL", "https://paper-api.alpaca.markets")

# Telegram
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# Email
EMAIL_SENDER = os.getenv("EMAIL_SENDER", "")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER", "")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))

# ============================================================
# DISPLAY
# ============================================================

CURRENCY_SYMBOLS = {
    "USD": "$",
    "EUR": "€",
    "INR": "₹",
}

MARKET_FLAGS = {
    "US": "🇺🇸",
    "DE": "🇩🇪",
    "IN": "🇮🇳",
}

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = LOGS_DIR / "trading_system.log"
