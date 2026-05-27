#!/usr/bin/env python3
"""
Trading System Configuration
All settings in one place
"""

from pathlib import Path

# ═══════════════════════════════════════════════════════════════
# ACCOUNT SETTINGS
# ═══════════════════════════════════════════════════════════════

ACCOUNT_SIZE = 50000                   # Starting capital in USD
RISK_PER_TRADE = 0.015                 # 1.5% risk per trade
MAX_POSITIONS = 8                      # Maximum concurrent positions
MAX_POSITION_SIZE = 0.25               # Max 25% of account per position
MAX_POSITION_SIZE_PCT = 0.25           # Alias for MAX_POSITION_SIZE (for backward compat)
MONTHLY_TARGET = 0.05                  # 5% monthly return target
DAILY_LOSS_LIMIT = 0.02                # Stop trading if 2% down in a day
WEEKLY_LOSS_LIMIT = 0.05               # Stop trading if 5% down in a week

# ═══════════════════════════════════════════════════════════════
# TRADING RULES
# ═══════════════════════════════════════════════════════════════

# ═══════════════════════════════════════════════════════════════
# STOCK UNIVERSE (Default set for US market)
# ═══════════════════════════════════════════════════════════════

STOCK_UNIVERSE = [
    # Tech - Semiconductors
    "NVDA", "AMD", "AVGO", "QCOM", "INTC", "MU", "AMAT", "LRCX", "TSM", "MRVL",
    # Tech - Software/Cloud
    "MSFT", "CRM", "ADBE", "NOW", "SNOW", "DDOG", "NET", "PANW", "ORCL", "PLTR",
    # Tech - Internet
    "GOOGL", "META", "AMZN", "NFLX", "UBER",
    # EV & Energy
    "TSLA", "ENPH",
    # Finance
    "PYPL", "V", "MA", "JPM",
    # Consumer
    "COST", "WMT", "HD", "NKE",
    # Healthcare
    "UNH", "JNJ", "LLY",
]

# ═══════════════════════════════════════════════════════════════
# SCREENING CRITERIA
# ═══════════════════════════════════════════════════════════════

SCREENING_CRITERIA = {
    "min_market_cap": 5_000_000_000,     # $5B
    "min_avg_volume": 2_000_000,         # 2M shares per day
    "min_price": 10,
    "max_price": 1500,
    "min_atr_pct": 2.0,                  # Moderate volatility
    "max_atr_pct": 8.0,
    "min_beta": 1.0,                     # More volatile than market
    "max_beta": 2.5,
    "min_rsi": 35,
    "max_rsi": 65,
    "min_rel_volume": 1.0,               # At least average volume
}

# ═══════════════════════════════════════════════════════════════
# TRADING RULES
# ═══════════════════════════════════════════════════════════════

MIN_SIGNAL_SCORE = 60         # Minimum score to consider a signal
STRONG_SIGNAL_SCORE = 75      # Score for "strong buy" signals

# Exit rules
EXIT_RULES = {
    "stop_loss_atr_mult": 2.5,
    "target_1_atr_mult": 3.5,
    "target_2_atr_mult": 5.0,
    "max_hold_days": 15,
    "partial_exit_pct": 0.5,
    "trailing_stop_atr": 2.0,
}

# ═══════════════════════════════════════════════════════════════
# TECHNICAL ANALYSIS SETTINGS
# ═══════════════════════════════════════════════════════════════

INDICATORS = {
    "ema_fast": 8,
    "ema_medium": 21,
    "ema_slow": 50,
    "ema_trend": 200,
    "rsi_period": 14,
    "atr_period": 14,
    "adx_period": 14,
    "volume_ma_period": 20,
}

THRESHOLDS = {
    "rsi_oversold": 30,
    "rsi_overbought": 70,
    "rsi_ideal_min": 40,
    "rsi_ideal_max": 60,
    "min_adx": 20,
    "strong_adx": 25,
    "min_volume_ratio": 0.7,
}

# ═══════════════════════════════════════════════════════════════
# DATA SETTINGS
# ═══════════════════════════════════════════════════════════════

DATA_DIR = Path("data")
CACHE_DIR = Path("cache")
LOGS_DIR = Path("logs")

# Create directories
DATA_DIR.mkdir(exist_ok=True)
CACHE_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

CACHE_EXPIRY_MINUTES = 15
MAX_CACHE_SIZE_MB = 500

# ═══════════════════════════════════════════════════════════════
# API SETTINGS
# ═══════════════════════════════════════════════════════════════

RATE_LIMITS = {
    "yfinance": 60,
    "default": 30,
}

MAX_RETRIES = 3
RETRY_DELAY = 1

# ═══════════════════════════════════════════════════════════════
# MARKET SETTINGS
# ═══════════════════════════════════════════════════════════════

DEFAULT_MARKETS = ["US", "IN"]
ALL_MARKETS = ["US", "DE", "IN"]

MARKET_SETTINGS = {
    "US": {"min_price": 10, "max_price": 1000, "min_volume": 500000, "preferred": True},
    "DE": {"min_price": 5, "max_price": 500, "min_volume": 100000, "preferred": False},
    "IN": {"min_price": 100, "max_price": 50000, "min_volume": 100000, "preferred": True},
}

# ═══════════════════════════════════════════════════════════════
# NOTIFICATION SETTINGS
# ═══════════════════════════════════════════════════════════════

NOTIFICATIONS = {
    "enabled": False,
    "email": None,
    "telegram_bot_token": None,
    "telegram_chat_id": None,
}

# ═══════════════════════════════════════════════════════════════
# DASHBOARD SETTINGS
# ═══════════════════════════════════════════════════════════════

DASHBOARD = {
    "refresh_interval": 60,
    "max_signals_display": 20,
    "chart_height": 400,
    "theme": "dark",
}

# ═══════════════════════════════════════════════════════════════
# LOGGING SETTINGS
# ═══════════════════════════════════════════════════════════════

LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FILE = LOGS_DIR / "trading_system.log"

# ═══════════════════════════════════════════════════════════════
# API & NOTIFICATION CREDENTIALS (from environment or .env)
# ═══════════════════════════════════════════════════════════════

import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Alpaca broker API
ALPACA_API_KEY = os.getenv("ALPACA_API_KEY", "")
ALPACA_SECRET_KEY = os.getenv("ALPACA_SECRET_KEY", "")
ALPACA_BASE_URL = os.getenv("ALPACA_BASE_URL", "https://paper-api.alpaca.markets")

# Telegram notifications
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# Email notifications
EMAIL_SENDER = os.getenv("EMAIL_SENDER", "")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER", "")
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587



# ═══════════════════════════════════════════════════════════════
# BACKTEST SETTINGS
# ═══════════════════════════════════════════════════════════════

BACKTEST = {
    "default_period": "1y",
    "commission": 0.001,
    "slippage": 0.001,
    "initial_capital": ACCOUNT_SIZE,
}


# ═══════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def get_risk_amount(account_value: float = None) -> float:
    """Get dollar amount to risk per trade"""
    if account_value is None:
        account_value = ACCOUNT_SIZE
    return account_value * RISK_PER_TRADE


def get_position_size(account_value: float, risk_amount: float, stop_distance: float) -> int:
    """Calculate position size based on risk"""
    if stop_distance <= 0:
        return 0
    return max(0, int(risk_amount / stop_distance))


if __name__ == "__main__":
    print(f"Account Size: ${ACCOUNT_SIZE:,}")
    print(f"Monthly Target: {MONTHLY_TARGET*100}%")
    print(f"Risk per Trade: {RISK_PER_TRADE*100}%")
    print(f"Max Positions: {MAX_POSITIONS}")
