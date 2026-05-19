#!/usr/bin/env python3
"""
Trading System Configuration
All settings in one place
"""

from pathlib import Path

# ═══════════════════════════════════════════════════════════════
# ACCOUNT SETTINGS
# ═══════════════════════════════════════════════════════════════

ACCOUNT_SIZE = 50000          # Starting capital in USD
RISK_PER_TRADE = 0.015        # 1.5% risk per trade
MAX_POSITIONS = 8             # Maximum concurrent positions
MAX_POSITION_SIZE = 0.25      # Max 25% of account per position
MONTHLY_TARGET = 0.05         # 5% monthly return target

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
