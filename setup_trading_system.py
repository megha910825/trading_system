#!/usr/bin/env python3
"""
⚠️ DEPRECATED - Bootstrap Script

Complete Trading System Setup Script
Creates all necessary files for the swing trading system

This script is for initial project setup only.
The trading system is already set up in your workspace.

Use this script only if you want to recreate the project from scratch.
Otherwise, use the global_* modules directly.
"""

import os

# Project directory
PROJECT_DIR = os.path.expanduser("~/trading_system")

def create_file(filename, content):
    """Create a file with given content"""
    filepath = os.path.join(PROJECT_DIR, filename)
    with open(filepath, "w") as f:
        f.write(content)
    print(f"✓ Created: {filename}")

def main():
    # Create directories
    os.makedirs(PROJECT_DIR, exist_ok=True)
    os.makedirs(os.path.join(PROJECT_DIR, "data"), exist_ok=True)
    os.makedirs(os.path.join(PROJECT_DIR, "logs"), exist_ok=True)

    print(f"Creating trading system in: {PROJECT_DIR}")
    print("=" * 60)

    # ============================================================
    # FILE 1: requirements.txt
    # ============================================================
    create_file("requirements.txt", """# Trading System Dependencies
pandas>=2.0.0
numpy>=1.24.0
openpyxl>=3.1.2
yfinance>=0.2.28
ta>=0.10.2
matplotlib>=3.7.0
plotly>=5.15.0
streamlit>=1.25.0
alpaca-trade-api>=3.0.0
requests>=2.31.0
schedule>=1.2.0
python-dotenv>=1.0.0
pytz>=2023.3
""")

    # ============================================================
    # FILE 2: .env.example
    # ============================================================
    create_file(".env.example", """# Copy to .env and fill in your values

# Alpaca API (https://alpaca.markets/)
ALPACA_API_KEY=your_key
ALPACA_SECRET_KEY=your_secret
ALPACA_BASE_URL=https://paper-api.alpaca.markets

# Telegram (optional)
TELEGRAM_BOT_TOKEN=your_token
TELEGRAM_CHAT_ID=your_chat_id

# Email (optional)
EMAIL_SENDER=your@email.com
EMAIL_PASSWORD=your_app_password
EMAIL_RECEIVER=your@email.com
""")

    # ============================================================
    # FILE 3: config.py
    # ============================================================
    create_file("config.py", '''"""Trading System Configuration"""

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
    "target_1_atr_mult": 2.5,
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
''')

    # ============================================================
    # FILE 4: data_fetcher.py
    # ============================================================
    create_file("data_fetcher.py", '''"""Data Fetcher - Gets market data from Yahoo Finance"""

import yfinance as yf
import pandas as pd
from typing import Dict, List
import time


class DataFetcher:
    """Fetches market data"""

    def get_stock_data(self, symbol: str, period: str = "6mo", interval: str = "1d") -> pd.DataFrame:
        """Get OHLCV data"""
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period, interval=interval)

            if df.empty:
                return pd.DataFrame()

            df.columns = [c.lower().replace(" ", "_") for c in df.columns]
            df["symbol"] = symbol
            return df
        except Exception as e:
            print(f"Error fetching {symbol}: {e}")
            return pd.DataFrame()

    def get_multiple_stocks(self, symbols: List[str], period: str = "6mo") -> Dict[str, pd.DataFrame]:
        """Get data for multiple stocks"""
        data = {}
        for i, symbol in enumerate(symbols):
            print(f"  Fetching {symbol} ({i+1}/{len(symbols)})...", end="\\r")
            df = self.get_stock_data(symbol, period)
            if not df.empty:
                data[symbol] = df
            time.sleep(0.1)
        print()
        return data

    def get_stock_info(self, symbol: str) -> Dict:
        """Get fundamental info"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            return {
                "symbol": symbol,
                "name": info.get("longName", symbol),
                "sector": info.get("sector", "Unknown"),
                "market_cap": info.get("marketCap", 0),
                "avg_volume": info.get("averageVolume", 0),
                "beta": info.get("beta", 1.0),
                "price": info.get("currentPrice", info.get("regularMarketPrice", 0)),
            }
        except:
            return {"symbol": symbol}

    def get_current_price(self, symbol: str) -> float:
        """Get current price"""
        try:
            df = self.get_stock_data(symbol, period="1d")
            return float(df["close"].iloc[-1]) if not df.empty else 0.0
        except:
            return 0.0


if __name__ == "__main__":
    fetcher = DataFetcher()
    df = fetcher.get_stock_data("NVDA", "3mo")
    print(f"NVDA: {len(df)} rows")
    print(df.tail())
''')

    # ============================================================
    # FILE 5: technical_analyzer.py
    # ============================================================
    create_file("technical_analyzer.py", '''"""Technical Analyzer - Calculates indicators and levels"""

import pandas as pd
import numpy as np
from typing import Dict
import config


class TechnicalAnalyzer:
    """Calculates technical indicators"""

    def __init__(self):
        self.exit_rules = config.EXIT_RULES

    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate all indicators"""
        df = df.copy()

        # EMAs
        df["ema_10"] = df["close"].ewm(span=10, adjust=False).mean()
        df["ema_20"] = df["close"].ewm(span=20, adjust=False).mean()
        df["ema_50"] = df["close"].ewm(span=50, adjust=False).mean()
        df["ema_200"] = df["close"].ewm(span=200, adjust=False).mean()

        # RSI
        delta = df["close"].diff()
        gain = delta.where(delta > 0, 0).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        df["rsi"] = 100 - (100 / (1 + rs))

        # ATR
        h, l, c = df["high"], df["low"], df["close"]
        tr = pd.concat([h-l, abs(h-c.shift()), abs(l-c.shift())], axis=1).max(axis=1)
        df["atr"] = tr.rolling(14).mean()
        df["atr_pct"] = (df["atr"] / df["close"]) * 100

        # Volume
        df["volume_ma"] = df["volume"].rolling(20).mean()
        df["rel_volume"] = df["volume"] / df["volume_ma"]

        # Support/Resistance
        df["support"] = df["low"].rolling(20).min()
        df["resistance"] = df["high"].rolling(20).max()

        # Trend
        df["uptrend"] = df["close"] > df["ema_50"]
        df["strong_uptrend"] = (df["close"] > df["ema_50"]) & (df["ema_50"] > df["ema_200"])

        # Distance from EMA
        df["dist_ema20_pct"] = ((df["close"] - df["ema_20"]) / df["close"]) * 100

        return df

    def analyze_stock(self, df: pd.DataFrame, symbol: str) -> Dict:
        """Complete analysis"""
        if df.empty or len(df) < 50:
            return {"symbol": symbol, "error": "Insufficient data"}

        df = self.calculate_indicators(df)
        curr = df.iloc[-1]

        # Entry levels
        price = curr["close"]
        ema20 = curr["ema_20"]
        support = curr["support"]
        atr = curr["atr"]

        entry = max(support, ema20 * 0.99)
        ideal_entry = (entry + ema20 * 1.01) / 2

        # Exit levels
        stop = ideal_entry - (self.exit_rules["stop_loss_atr_mult"] * atr)
        t1 = ideal_entry + (self.exit_rules["target_1_atr_mult"] * atr)
        t2 = ideal_entry + (self.exit_rules["target_2_atr_mult"] * atr)

        risk = ideal_entry - stop
        rr = (t1 - ideal_entry) / risk if risk > 0 else 0

        # Setup type
        dist = abs(curr["dist_ema20_pct"])
        setup = "PULLBACK" if dist < 2.5 else "MOMENTUM"

        # Score
        score = 0
        if 40 <= curr["rsi"] <= 60: score += 20
        if curr["uptrend"]: score += 15
        if curr["strong_uptrend"]: score += 10
        if dist < 2.5: score += 25
        if 2.5 <= curr["atr_pct"] <= 5: score += 15
        if curr["rel_volume"] >= 1.0: score += 15

        status = "STRONG BUY" if score >= 70 else ("BUY" if score >= 55 else ("WATCH" if score >= 40 else "AVOID"))

        return {
            "symbol": symbol,
            "current_price": round(price, 2),
            "ideal_entry": round(ideal_entry, 2),
            "stop_loss": round(stop, 2),
            "target_1": round(t1, 2),
            "target_2": round(t2, 2),
            "risk_reward": round(rr, 2),
            "setup_type": setup,
            "signal_score": score,
            "signal_status": status,
            "rsi": round(curr["rsi"], 1),
            "atr_pct": round(curr["atr_pct"], 2),
            "rel_volume": round(curr["rel_volume"], 2),
            "uptrend": bool(curr["uptrend"]),
            "atr": round(atr, 2),
        }


if __name__ == "__main__":
    from data_fetcher import DataFetcher

    fetcher = DataFetcher()
    analyzer = TechnicalAnalyzer()

    df = fetcher.get_stock_data("NVDA", "6mo")
    result = analyzer.analyze_stock(df, "NVDA")

    for k, v in result.items():
        print(f"  {k}: {v}")
''')

    # ============================================================
    # FILE 6: stock_screener.py
    # ============================================================
    create_file("stock_screener.py", '''"""Stock Screener - Filters stocks by criteria"""

import pandas as pd
from typing import List, Dict
from data_fetcher import DataFetcher
from technical_analyzer import TechnicalAnalyzer
import config


class StockScreener:
    """Screens stocks for trading"""

    def __init__(self):
        self.fetcher = DataFetcher()
        self.analyzer = TechnicalAnalyzer()
        self.criteria = config.SCREENING_CRITERIA

    def screen_stocks(self, symbols: List[str] = None) -> pd.DataFrame:
        """Screen stocks"""
        if symbols is None:
            symbols = config.STOCK_UNIVERSE

        results = []
        print(f"Screening {len(symbols)} stocks...")

        for i, symbol in enumerate(symbols):
            print(f"  {symbol} ({i+1}/{len(symbols)})...", end="\\r")

            try:
                df = self.fetcher.get_stock_data(symbol, "6mo")
                if df.empty or len(df) < 50:
                    continue

                info = self.fetcher.get_stock_info(symbol)
                analysis = self.analyzer.analyze_stock(df, symbol)

                if "error" in analysis:
                    continue

                stock = {
                    "symbol": symbol,
                    "name": info.get("name", "N/A"),
                    "sector": info.get("sector", "N/A"),
                    "market_cap": info.get("market_cap", 0),
                    "avg_volume": info.get("avg_volume", 0),
                    **analysis
                }

                passed, count = self._check_criteria(stock, info)
                stock["criteria_passed"] = count
                stock["qualified"] = passed
                results.append(stock)
            except:
                continue

        print()
        df = pd.DataFrame(results)
        if not df.empty:
            df = df.sort_values("signal_score", ascending=False)

        qualified = len(df[df["qualified"]]) if not df.empty else 0
        print(f"Found {qualified} qualified stocks")
        return df

    def _check_criteria(self, stock: Dict, info: Dict) -> tuple:
        """Check screening criteria"""
        c = self.criteria
        passed = 0

        if info.get("market_cap", 0) >= c["min_market_cap"]: passed += 1
        if info.get("avg_volume", 0) >= c["min_avg_volume"]: passed += 1

        atr = stock.get("atr_pct", 0)
        if c["min_atr_pct"] <= atr <= c["max_atr_pct"]: passed += 1

        rsi = stock.get("rsi", 50)
        if c["min_rsi"] <= rsi <= c["max_rsi"]: passed += 1

        if stock.get("uptrend", False): passed += 1
        if stock.get("rel_volume", 0) >= c["min_rel_volume"]: passed += 1
        if stock.get("risk_reward", 0) >= 2.0: passed += 1

        return passed >= 5, passed

    def get_top_signals(self, n: int = 10) -> pd.DataFrame:
        """Get top signals"""
        df = self.screen_stocks()
        return df[df["qualified"]].head(n)


if __name__ == "__main__":
    screener = StockScreener()
    results = screener.screen_stocks(["NVDA", "AMD", "AAPL", "MSFT", "META"])
    print(results[["symbol", "signal_score", "signal_status", "qualified"]])
''')

    # ============================================================
    # FILE 7: signal_generator.py
    # ============================================================
    create_file("signal_generator.py", '''"""Signal Generator - Creates trading signals"""

import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional
from data_fetcher import DataFetcher
from technical_analyzer import TechnicalAnalyzer
import config


class SignalGenerator:
    """Generates trading signals"""

    def __init__(self):
        self.fetcher = DataFetcher()
        self.analyzer = TechnicalAnalyzer()
        self.signals = []

    def generate_signals(self, symbols: List[str] = None) -> List[Dict]:
        """Generate signals"""
        if symbols is None:
            symbols = config.STOCK_UNIVERSE

        signals = []
        print(f"Generating signals for {len(symbols)} stocks...")

        for symbol in symbols:
            try:
                signal = self._analyze(symbol)
                if signal and signal.get("signal_status") in ["STRONG BUY", "BUY"]:
                    signals.append(signal)
            except:
                continue

        signals = sorted(signals, key=lambda x: x.get("signal_score", 0), reverse=True)
        self.signals = signals
        print(f"Found {len(signals)} signals")
        return signals

    def _analyze(self, symbol: str) -> Optional[Dict]:
        """Analyze symbol"""
        df = self.fetcher.get_stock_data(symbol, "6mo")
        if df.empty or len(df) < 50:
            return None

        analysis = self.analyzer.analyze_stock(df, symbol)
        if "error" in analysis:
            return None

        info = self.fetcher.get_stock_info(symbol)

        # Check criteria
        c = config.SCREENING_CRITERIA
        if info.get("market_cap", 0) < c["min_market_cap"]:
            return None
        if not analysis.get("uptrend"):
            return None
        if analysis.get("risk_reward", 0) < 2.0:
            return None

        return {
            "timestamp": datetime.now().isoformat(),
            "name": info.get("name", "N/A"),
            "sector": info.get("sector", "N/A"),
            **analysis,
        }

    def get_summary(self) -> pd.DataFrame:
        """Get signal summary"""
        if not self.signals:
            return pd.DataFrame()

        cols = ["symbol", "name", "signal_status", "signal_score", "current_price",
                "ideal_entry", "stop_loss", "target_1", "risk_reward"]
        df = pd.DataFrame(self.signals)
        return df[[c for c in cols if c in df.columns]]

    def format_alert(self, signal: Dict) -> str:
        """Format alert message"""
        return f"""
🎯 SIGNAL: {signal.get('signal_status')}

{signal.get('symbol')} - {signal.get('name')}
Setup: {signal.get('setup_type')}
Score: {signal.get('signal_score')}/100

Entry: ${signal.get('ideal_entry', 0):.2f}
Stop: ${signal.get('stop_loss', 0):.2f}
Target 1: ${signal.get('target_1', 0):.2f}
Target 2: ${signal.get('target_2', 0):.2f}

R:R: {signal.get('risk_reward', 0):.2f}
RSI: {signal.get('rsi', 0):.1f}

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M')}
"""


if __name__ == "__main__":
    gen = SignalGenerator()
    signals = gen.generate_signals(["NVDA", "AMD", "META", "AAPL", "MSFT"])
    print(gen.get_summary())

    if signals:
        print(gen.format_alert(signals[0]))
''')

    # ============================================================
    # FILE 8: position_manager.py
    # ============================================================
    create_file("position_manager.py", '''"""Position Manager - Handles positions and risk"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import pandas as pd
import config


@dataclass
class Position:
    """Trading position"""
    symbol: str
    entry_price: float
    shares: int
    stop_loss: float
    target_1: float
    target_2: float
    entry_date: datetime = field(default_factory=datetime.now)
    status: str = "OPEN"
    exit_price: float = 0
    pnl: float = 0


class PositionManager:
    """Manages positions"""

    def __init__(self):
        self.account = config.ACCOUNT_SIZE
        self.risk = config.RISK_PER_TRADE
        self.max_positions = config.MAX_POSITIONS
        self.positions: List[Position] = []
        self.closed: List[Position] = []
        self.daily_pnl = 0

    def calc_position_size(self, entry: float, stop: float) -> Dict:
        """Calculate position size"""
        risk_per_share = entry - stop
        if risk_per_share <= 0:
            return {"error": "Invalid stop"}

        max_risk = self.account * self.risk
        shares = int(max_risk / risk_per_share)

        value = shares * entry
        max_value = self.account * config.MAX_POSITION_SIZE_PCT

        if value > max_value:
            shares = int(max_value / entry)
            value = shares * entry

        return {
            "shares": shares,
            "position_value": round(value, 2),
            "risk_dollars": round(shares * risk_per_share, 2),
            "risk_pct": round((shares * risk_per_share / self.account) * 100, 2),
        }

    def can_open(self) -> tuple:
        """Check if can open position"""
        open_count = len([p for p in self.positions if p.status == "OPEN"])
        if open_count >= self.max_positions:
            return False, "Max positions reached"
        if self.daily_pnl <= -self.account * config.DAILY_LOSS_LIMIT:
            return False, "Daily loss limit"
        return True, "OK"

    def open_position(self, signal: Dict) -> Optional[Position]:
        """Open position"""
        can, reason = self.can_open()
        if not can:
            print(f"Cannot open: {reason}")
            return None

        sizing = self.calc_position_size(signal["ideal_entry"], signal["stop_loss"])
        if "error" in sizing:
            return None

        pos = Position(
            symbol=signal["symbol"],
            entry_price=signal["ideal_entry"],
            shares=sizing["shares"],
            stop_loss=signal["stop_loss"],
            target_1=signal["target_1"],
            target_2=signal["target_2"],
        )

        self.positions.append(pos)
        print(f"Opened: {pos.symbol} - {pos.shares} shares @ ${pos.entry_price}")
        return pos

    def close_position(self, symbol: str, exit_price: float) -> Optional[Position]:
        """Close position"""
        for pos in self.positions:
            if pos.symbol == symbol and pos.status == "OPEN":
                pos.exit_price = exit_price
                pos.pnl = (exit_price - pos.entry_price) * pos.shares
                pos.status = "CLOSED"

                self.daily_pnl += pos.pnl
                self.closed.append(pos)
                self.positions.remove(pos)

                print(f"Closed: {symbol} @ ${exit_price} - P&L: ${pos.pnl:.2f}")
                return pos
        return None

    def get_summary(self) -> Dict:
        """Portfolio summary"""
        open_pos = [p for p in self.positions if p.status == "OPEN"]
        invested = sum(p.shares * p.entry_price for p in open_pos)

        return {
            "account": self.account,
            "open_positions": len(open_pos),
            "invested": round(invested, 2),
            "cash": round(self.account - invested, 2),
            "daily_pnl": round(self.daily_pnl, 2),
        }


if __name__ == "__main__":
    pm = PositionManager()

    sizing = pm.calc_position_size(875.50, 845.00)
    print("Position sizing:", sizing)

    signal = {
        "symbol": "NVDA",
        "ideal_entry": 875.50,
        "stop_loss": 845.00,
        "target_1": 936.50,
        "target_2": 967.00,
    }
    pm.open_position(signal)
    print("Summary:", pm.get_summary())
''')

    # ============================================================
    # FILE 9: alert_system.py
    # ============================================================
    create_file("alert_system.py", '''"""Alert System - Sends notifications"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
from datetime import datetime
from typing import Dict
import config


class AlertSystem:
    """Sends alerts via Email/Telegram"""

    def __init__(self):
        self.telegram_token = config.TELEGRAM_BOT_TOKEN
        self.telegram_chat = config.TELEGRAM_CHAT_ID
        self.email_sender = config.EMAIL_SENDER
        self.email_pass = config.EMAIL_PASSWORD
        self.email_receiver = config.EMAIL_RECEIVER

    def send_telegram(self, message: str) -> bool:
        """Send Telegram message"""
        if not self.telegram_token:
            self._print(message)
            return False

        try:
            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            r = requests.post(url, data={"chat_id": self.telegram_chat, "text": message}, timeout=10)
            return r.status_code == 200
        except:
            return False

    def send_email(self, subject: str, body: str) -> bool:
        """Send email"""
        if not self.email_sender:
            return False

        try:
            msg = MIMEMultipart()
            msg["From"] = self.email_sender
            msg["To"] = self.email_receiver
            msg["Subject"] = subject
            msg.attach(MIMEText(body, "plain"))

            with smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT) as server:
                server.starttls()
                server.login(self.email_sender, self.email_pass)
                server.send_message(msg)
            return True
        except:
            return False

    def send_signal(self, signal: Dict):
        """Send signal alert"""
        msg = f"""
🎯 SIGNAL: {signal.get('signal_status')}

{signal.get('symbol')} - {signal.get('name', '')}
Setup: {signal.get('setup_type')}
Score: {signal.get('signal_score')}/100

Entry: ${signal.get('ideal_entry', 0):.2f}
Stop: ${signal.get('stop_loss', 0):.2f}
Target: ${signal.get('target_1', 0):.2f}

R:R: {signal.get('risk_reward', 0):.2f}

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M')}
"""
        self.send_telegram(msg)
        self.send_email(f"Signal: {signal.get('symbol')}", msg)
        self._print(msg)

    def _print(self, msg: str):
        """Print to console"""
        print("=" * 50)
        print(msg)
        print("=" * 50)


if __name__ == "__main__":
    alerts = AlertSystem()
    alerts.send_signal({
        "symbol": "NVDA",
        "name": "NVIDIA",
        "signal_status": "STRONG BUY",
        "signal_score": 85,
        "setup_type": "PULLBACK",
        "ideal_entry": 872.50,
        "stop_loss": 842.00,
        "target_1": 920.00,
        "risk_reward": 2.1,
    })
''')

    # ============================================================
    # FILE 10: broker_api.py
    # ============================================================
    create_file("broker_api.py", '''"""Broker API - Alpaca integration"""

from typing import Dict, List, Optional
import config

try:
    from alpaca.trading.client import TradingClient
    from alpaca.trading.requests import MarketOrderRequest, LimitOrderRequest
    from alpaca.trading.enums import OrderSide, TimeInForce
    ALPACA_OK = True
except ImportError:
    ALPACA_OK = False


class BrokerAPI:
    """Alpaca broker wrapper"""

    def __init__(self, paper: bool = True):
        self.paper = paper
        self.connected = False
        self.client = None

        if ALPACA_OK and config.ALPACA_API_KEY:
            self._connect()
        else:
            print("Running in simulation mode")

    def _connect(self):
        """Connect to Alpaca"""
        try:
            self.client = TradingClient(
                api_key=config.ALPACA_API_KEY,
                secret_key=config.ALPACA_SECRET_KEY,
                paper=self.paper
            )
            account = self.client.get_account()
            self.connected = True
            print(f"Connected to Alpaca ({'Paper' if self.paper else 'Live'})")
            print(f"  Buying Power: ${float(account.buying_power):,.2f}")
        except Exception as e:
            print(f"Connection failed: {e}")

    def get_account(self) -> Dict:
        """Get account info"""
        if not self.connected:
            return {"status": "SIMULATED", "cash": config.ACCOUNT_SIZE, "buying_power": config.ACCOUNT_SIZE}

        try:
            a = self.client.get_account()
            return {"status": a.status, "cash": float(a.cash), "buying_power": float(a.buying_power)}
        except:
            return {}

    def get_positions(self) -> List[Dict]:
        """Get positions"""
        if not self.connected:
            return []

        try:
            return [{"symbol": p.symbol, "qty": int(p.qty), "pnl": float(p.unrealized_pl)}
                    for p in self.client.get_all_positions()]
        except:
            return []

    def place_order(self, symbol: str, qty: int, side: str, price: float = None) -> Optional[Dict]:
        """Place order"""
        if not self.connected:
            print(f"SIMULATED: {side.upper()} {qty} {symbol}" + (f" @ ${price}" if price else ""))
            return {"order_id": "SIM", "status": "simulated"}

        try:
            order_side = OrderSide.BUY if side == "buy" else OrderSide.SELL

            if price:
                req = LimitOrderRequest(symbol=symbol, qty=qty, side=order_side,
                                        time_in_force=TimeInForce.DAY, limit_price=price)
            else:
                req = MarketOrderRequest(symbol=symbol, qty=qty, side=order_side,
                                         time_in_force=TimeInForce.DAY)

            result = self.client.submit_order(req)
            print(f"Order placed: {side.upper()} {qty} {symbol}")
            return {"order_id": result.id, "status": result.status}
        except Exception as e:
            print(f"Order failed: {e}")
            return None

    def close_position(self, symbol: str) -> bool:
        """Close position"""
        if not self.connected:
            print(f"SIMULATED: Close {symbol}")
            return True

        try:
            self.client.close_position(symbol)
            return True
        except:
            return False


if __name__ == "__main__":
    broker = BrokerAPI(paper=True)
    print("Account:", broker.get_account())
    broker.place_order("NVDA", 10, "buy", 850.00)
''')

    # ============================================================
    # FILE 11: backtester.py
    # ============================================================
    create_file("backtester.py", '''"""Backtester - Tests strategy on historical data"""

import pandas as pd
import numpy as np
from typing import List, Dict, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from data_fetcher import DataFetcher
from technical_analyzer import TechnicalAnalyzer
import config


@dataclass
class Trade:
    """Backtest trade"""
    symbol: str
    entry_date: datetime
    entry_price: float
    exit_date: datetime = None
    exit_price: float = 0
    shares: int = 0
    pnl: float = 0
    pnl_pct: float = 0
    exit_reason: str = ""


@dataclass
class Results:
    """Backtest results"""
    total_trades: int = 0
    wins: int = 0
    losses: int = 0
    win_rate: float = 0
    total_pnl: float = 0
    total_return: float = 0
    avg_win: float = 0
    avg_loss: float = 0
    profit_factor: float = 0
    max_drawdown: float = 0
    trades: List[Trade] = field(default_factory=list)


class Backtester:
    """Backtests trading strategy"""

    def __init__(self, capital: float = None):
        self.fetcher = DataFetcher()
        self.analyzer = TechnicalAnalyzer()
        self.capital = capital or config.ACCOUNT_SIZE
        self.risk = config.RISK_PER_TRADE

    def run(self, symbols: List[str], period: str = "1y") -> Results:
        """Run backtest"""
        all_trades = []

        print(f"Backtesting {len(symbols)} symbols...")
        for symbol in symbols:
            try:
                trades = self._backtest_symbol(symbol, period)
                all_trades.extend(trades)
            except:
                continue

        print(f"Completed: {len(all_trades)} trades")
        return self._calc_results(all_trades)

    def _backtest_symbol(self, symbol: str, period: str) -> List[Trade]:
        """Backtest single symbol"""
        df = self.fetcher.get_stock_data(symbol, period)
        if df.empty or len(df) < 60:
            return []

        df = self.analyzer.calculate_indicators(df)

        trades = []
        in_trade = False
        trade = None

        for i in range(50, len(df) - 1):
            curr = df.iloc[i]
            next_bar = df.iloc[i + 1]

            if not in_trade:
                if self._check_entry(curr):
                    entry = next_bar["open"]
                    atr = curr["atr"]
                    stop = entry - (1.75 * atr)
                    target = entry + (2.5 * atr)

                    risk_per_share = entry - stop
                    shares = int((self.capital * self.risk) / risk_per_share)

                    if shares > 0:
                        trade = Trade(
                            symbol=symbol,
                            entry_date=next_bar.name,
                            entry_price=entry,
                            shares=shares,
                        )
                        trade.stop = stop
                        trade.target = target
                        in_trade = True
            else:
                exit_price, reason = self._check_exit(trade, next_bar)
                if exit_price:
                    trade.exit_date = next_bar.name
                    trade.exit_price = exit_price
                    trade.exit_reason = reason
                    trade.pnl = (exit_price - trade.entry_price) * trade.shares
                    trade.pnl_pct = ((exit_price - trade.entry_price) / trade.entry_price) * 100

                    trades.append(trade)
                    in_trade = False
                    trade = None

        return trades

    def _check_entry(self, curr) -> bool:
        """Check entry conditions"""
        return all([
            curr["close"] > curr["ema_50"],
            abs(curr["dist_ema20_pct"]) < 2.5,
            40 <= curr["rsi"] <= 60,
            curr["rel_volume"] >= 0.8,
            2.0 <= curr["atr_pct"] <= 6.0,
            curr["close"] > curr["open"],
        ])

    def _check_exit(self, trade, bar) -> Tuple[float, str]:
        """Check exit conditions"""
        if bar["low"] <= trade.stop:
            return trade.stop, "STOP"
        if bar["high"] >= trade.target:
            return trade.target, "TARGET"
        return None, ""

    def _calc_results(self, trades: List[Trade]) -> Results:
        """Calculate results"""
        r = Results()
        if not trades:
            return r

        r.trades = trades
        r.total_trades = len(trades)

        wins = [t for t in trades if t.pnl > 0]
        losses = [t for t in trades if t.pnl <= 0]

        r.wins = len(wins)
        r.losses = len(losses)
        r.win_rate = (r.wins / r.total_trades * 100) if r.total_trades else 0
        r.total_pnl = sum(t.pnl for t in trades)
        r.total_return = (r.total_pnl / self.capital) * 100

        if wins:
            r.avg_win = sum(t.pnl for t in wins) / len(wins)
        if losses:
            r.avg_loss = sum(t.pnl for t in losses) / len(losses)

        gross_profit = sum(t.pnl for t in wins) if wins else 0
        gross_loss = abs(sum(t.pnl for t in losses)) if losses else 1
        r.profit_factor = gross_profit / gross_loss if gross_loss else 0

        # Max drawdown
        equity = self.capital
        peak = equity
        max_dd = 0
        for t in sorted(trades, key=lambda x: x.exit_date or x.entry_date):
            equity += t.pnl
            if equity > peak:
                peak = equity
            dd = (peak - equity) / peak * 100
            if dd > max_dd:
                max_dd = dd
        r.max_drawdown = max_dd

        return r

    def print_results(self, r: Results):
        """Print results"""
        print("\\n" + "=" * 50)
        print("BACKTEST RESULTS")
        print("=" * 50)
        print(f"Total Trades: {r.total_trades}")
        print(f"Wins: {r.wins} | Losses: {r.losses}")
        print(f"Win Rate: {r.win_rate:.1f}%")
        print(f"Total P&L: ${r.total_pnl:,.2f}")
        print(f"Total Return: {r.total_return:.2f}%")
        print(f"Avg Win: ${r.avg_win:,.2f}")
        print(f"Avg Loss: ${r.avg_loss:,.2f}")
        print(f"Profit Factor: {r.profit_factor:.2f}")
        print(f"Max Drawdown: {r.max_drawdown:.2f}%")
        print("=" * 50)


if __name__ == "__main__":
    bt = Backtester()
    results = bt.run(["NVDA", "AMD", "AAPL", "MSFT", "META"], period="1y")
    bt.print_results(results)
''')

    # ============================================================
    # FILE 12: main.py
    # ============================================================
    create_file("main.py", '''"""Main Trading System - Entry point"""

import argparse
from datetime import datetime

from data_fetcher import DataFetcher
from technical_analyzer import TechnicalAnalyzer
from stock_screener import StockScreener
from signal_generator import SignalGenerator
from position_manager import PositionManager
from alert_system import AlertSystem
from broker_api import BrokerAPI
from backtester import Backtester
import config


def run_scanner():
    """Run stock scanner"""
    print("\\n" + "=" * 60)
    print("RUNNING STOCK SCANNER")
    print("=" * 60)

    screener = StockScreener()
    results = screener.screen_stocks()

    qualified = results[results["qualified"]]
    print(f"\\nFound {len(qualified)} qualified stocks:")

    if not qualified.empty:
        print(qualified[["symbol", "signal_score", "signal_status", "current_price",
                        "ideal_entry", "stop_loss", "target_1", "risk_reward"]].to_string())


def run_signals():
    """Generate trading signals"""
    print("\\n" + "=" * 60)
    print("GENERATING SIGNALS")
    print("=" * 60)

    gen = SignalGenerator()
    signals = gen.generate_signals()
    alerts = AlertSystem()

    if signals:
        print(f"\\nFound {len(signals)} signals:")
        print(gen.get_summary().to_string())

        # Send alert for top signal
        alerts.send_signal(signals[0])
    else:
        print("No signals found")


def run_analysis(symbol: str):
    """Analyze single stock"""
    print("\\n" + "=" * 60)
    print(f"ANALYZING {symbol}")
    print("=" * 60)

    fetcher = DataFetcher()
    analyzer = TechnicalAnalyzer()

    df = fetcher.get_stock_data(symbol, "6mo")
    if df.empty:
        print(f"No data for {symbol}")
        return

    result = analyzer.analyze_stock(df, symbol)

    print(f"\\n{symbol} Analysis:")
    for k, v in result.items():
        print(f"  {k}: {v}")


def run_backtest(symbols: list, period: str = "1y"):
    """Run backtest"""
    print("\\n" + "=" * 60)
    print("RUNNING BACKTEST")
    print("=" * 60)

    bt = Backtester()
    results = bt.run(symbols, period)
    bt.print_results(results)


def run_portfolio():
    """Show portfolio status"""
    print("\\n" + "=" * 60)
    print("PORTFOLIO STATUS")
    print("=" * 60)

    broker = BrokerAPI(paper=True)
    pm = PositionManager()

    account = broker.get_account()
    print(f"\\nAccount Status: {account.get('status')}")
    print(f"Cash: ${account.get('cash', 0):,.2f}")
    print(f"Buying Power: ${account.get('buying_power', 0):,.2f}")

    positions = broker.get_positions()
    if positions:
        print(f"\\nOpen Positions: {len(positions)}")
        for p in positions:
            print(f"  {p['symbol']}: {p['qty']} shares, P&L: ${p.get('pnl', 0):.2f}")
    else:
        print("\\nNo open positions")


def main():
    parser = argparse.ArgumentParser(description="Swing Trading System")
    parser.add_argument("command", choices=["scan", "signals", "analyze", "backtest", "portfolio"],
                       help="Command to run")
    parser.add_argument("--symbol", "-s", help="Stock symbol for analysis")
    parser.add_argument("--period", "-p", default="1y", help="Backtest period")

    args = parser.parse_args()

    print(f"\\n🎯 Swing Trading System - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"Account Size: ${config.ACCOUNT_SIZE:,} | Target: {config.MONTHLY_TARGET*100}%/month")

    if args.command == "scan":
        run_scanner()
    elif args.command == "signals":
        run_signals()
    elif args.command == "analyze":
        if args.symbol:
            run_analysis(args.symbol.upper())
        else:
            print("Please provide --symbol")
    elif args.command == "backtest":
        run_backtest(config.STOCK_UNIVERSE[:10], args.period)
    elif args.command == "portfolio":
        run_portfolio()


if __name__ == "__main__":
    main()
''')

    # ============================================================
    # FILE 13: dashboard.py (Streamlit)
    # ============================================================
    create_file("dashboard.py", '''"""Trading Dashboard - Streamlit Web UI"""

import streamlit as st
import pandas as pd
from datetime import datetime

from data_fetcher import DataFetcher
from technical_analyzer import TechnicalAnalyzer
from stock_screener import StockScreener
from signal_generator import SignalGenerator
from position_manager import PositionManager
from backtester import Backtester
import config

st.set_page_config(page_title="Trading System", page_icon="📈", layout="wide")

# Initialize
@st.cache_resource
def init():
    return {
        "fetcher": DataFetcher(),
        "analyzer": TechnicalAnalyzer(),
        "screener": StockScreener(),
        "gen": SignalGenerator(),
        "pm": PositionManager(),
        "bt": Backtester(),
    }

c = init()

# Sidebar
st.sidebar.title("🎯 Trading System")
st.sidebar.markdown(f"**Target: {config.MONTHLY_TARGET*100}% Monthly**")
page = st.sidebar.radio("Navigate", ["Dashboard", "Scanner", "Analysis", "Signals", "Backtest", "Calculator"])

# Dashboard
if page == "Dashboard":
    st.title("📊 Trading Dashboard")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Account", f"${config.ACCOUNT_SIZE:,}")
    col2.metric("Monthly Target", f"${config.ACCOUNT_SIZE * config.MONTHLY_TARGET:,.0f}")
    col3.metric("Risk/Trade", f"{config.RISK_PER_TRADE*100}%")
    col4.metric("Max Positions", config.MAX_POSITIONS)

    st.markdown("---")
    st.subheader("Quick Scan")

    if st.button("🔍 Scan Top Stocks"):
        with st.spinner("Scanning..."):
            results = c["screener"].screen_stocks(config.STOCK_UNIVERSE[:15])
            qualified = results[results["qualified"]]
            if not qualified.empty:
                st.dataframe(qualified[["symbol", "signal_score", "signal_status",
                                       "current_price", "ideal_entry", "risk_reward"]])
            else:
                st.info("No qualified stocks found")

# Scanner
elif page == "Scanner":
    st.title("🔍 Stock Screener")

    num = st.slider("Stocks to scan", 5, 30, 15)

    if st.button("Run Screener"):
        with st.spinner("Screening..."):
            results = c["screener"].screen_stocks(config.STOCK_UNIVERSE[:num])
            st.dataframe(results)

# Analysis
elif page == "Analysis":
    st.title("📈 Stock Analysis")

    symbol = st.text_input("Symbol", "NVDA").upper()

    if st.button("Analyze"):
        with st.spinner(f"Analyzing {symbol}..."):
            df = c["fetcher"].get_stock_data(symbol, "6mo")
            if not df.empty:
                result = c["analyzer"].analyze_stock(df, symbol)

                col1, col2, col3 = st.columns(3)
                col1.metric("Price", f"${result.get('current_price', 0):.2f}")
                col2.metric("Signal", result.get('signal_status'))
                col3.metric("Score", f"{result.get('signal_score', 0)}/100")

                st.markdown("---")
                st.subheader("Trading Levels")

                levels = pd.DataFrame({
                    "Level": ["Entry", "Stop Loss", "Target 1", "Target 2"],
                    "Price": [
                        f"${result.get('ideal_entry', 0):.2f}",
                        f"${result.get('stop_loss', 0):.2f}",
                        f"${result.get('target_1', 0):.2f}",
                        f"${result.get('target_2', 0):.2f}",
                    ]
                })
                st.table(levels)

                st.markdown("---")
                st.subheader("Indicators")
                col1, col2, col3 = st.columns(3)
                col1.metric("RSI", f"{result.get('rsi', 0):.1f}")
                col2.metric("ATR%", f"{result.get('atr_pct', 0):.2f}%")
                col3.metric("R:R", f"{result.get('risk_reward', 0):.2f}")
            else:
                st.error(f"No data for {symbol}")

# Signals
elif page == "Signals":
    st.title("🎯 Trading Signals")

    if st.button("Generate Signals"):
        with st.spinner("Generating..."):
            signals = c["gen"].generate_signals(config.STOCK_UNIVERSE[:15])

            if signals:
                st.success(f"Found {len(signals)} signals")
                st.dataframe(c["gen"].get_summary())

                st.markdown("---")
                st.subheader("Top Signal")
                st.code(c["gen"].format_alert(signals[0]))
            else:
                st.info("No signals found")

# Backtest
elif page == "Backtest":
    st.title("📉 Backtester")

    symbols = st.text_area("Symbols (one per line)", "NVDA\\nAMD\\nAAPL\\nMSFT\\nMETA")
    period = st.selectbox("Period", ["6mo", "1y", "2y"])

    if st.button("Run Backtest"):
        sym_list = [s.strip().upper() for s in symbols.split("\\n") if s.strip()]

        with st.spinner("Backtesting..."):
            results = c["bt"].run(sym_list, period)

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total P&L", f"${results.total_pnl:,.2f}")
            col2.metric("Win Rate", f"{results.win_rate:.1f}%")
            col3.metric("Profit Factor", f"{results.profit_factor:.2f}")
            col4.metric("Max Drawdown", f"{results.max_drawdown:.1f}%")

            st.markdown("---")
            st.subheader("Trade Details")

            if results.trades:
                trades_data = [{
                    "Symbol": t.symbol,
                    "Entry": f"${t.entry_price:.2f}",
                    "Exit": f"${t.exit_price:.2f}",
                    "P&L": f"${t.pnl:.2f}",
                    "Return": f"{t.pnl_pct:.1f}%",
                    "Reason": t.exit_reason,
                } for t in results.trades]
                st.dataframe(pd.DataFrame(trades_data))

# Calculator
elif page == "Calculator":
    st.title("📐 Position Calculator")

    col1, col2 = st.columns(2)

    with col1:
        entry = st.number_input("Entry Price ($)", value=100.0, step=1.0)
        stop = st.number_input("Stop Loss ($)", value=95.0, step=1.0)

    with col2:
        account = st.number_input("Account Size ($)", value=50000.0, step=1000.0)
        risk_pct = st.slider("Risk %", 0.5, 3.0, 1.5, 0.1)

    if st.button("Calculate"):
        risk_per_share = entry - stop

        if risk_per_share > 0:
            max_risk = account * (risk_pct / 100)
            shares = int(max_risk / risk_per_share)
            value = shares * entry

            col1, col2, col3 = st.columns(3)
            col1.metric("Shares", shares)
            col2.metric("Position Value", f"${value:,.2f}")
            col3.metric("Risk Amount", f"${max_risk:,.2f}")
        else:
            st.error("Stop must be below entry")
''')

    # ============================================================
    # FILE 14: run_dashboard.py
    # ============================================================
    create_file("run_dashboard.py", '''"""Run the Streamlit dashboard"""

import subprocess
import sys

if __name__ == "__main__":
    subprocess.run([sys.executable, "-m", "streamlit", "run", "dashboard.py"])
''')

    # ============================================================
    # DONE
    # ============================================================
    print("=" * 60)
    print("✅ TRADING SYSTEM CREATED SUCCESSFULLY!")
    print("=" * 60)
    print(f"\n📁 Location: {PROJECT_DIR}")
    print("\n📋 FILES CREATED:")
    print("   1. requirements.txt - Dependencies")
    print("   2. .env.example - API keys template")
    print("   3. config.py - Configuration")
    print("   4. data_fetcher.py - Market data")
    print("   5. technical_analyzer.py - Indicators")
    print("   6. stock_screener.py - Stock filtering")
    print("   7. signal_generator.py - Trade signals")
    print("   8. position_manager.py - Risk management")
    print("   9. alert_system.py - Notifications")
    print("   10. broker_api.py - Alpaca integration")
    print("   11. backtester.py - Strategy testing")
    print("   12. main.py - CLI entry point")
    print("   13. dashboard.py - Web UI")
    print("   14. run_dashboard.py - Dashboard launcher")

    print("\n🚀 GETTING STARTED:")
    print(f"   cd {PROJECT_DIR}")
    print("   pip install -r requirements.txt")
    print("   python main.py scan          # Scan for stocks")
    print("   python main.py signals       # Generate signals")
    print("   python main.py analyze -s NVDA  # Analyze stock")
    print("   python main.py backtest      # Run backtest")
    print("   python run_dashboard.py      # Launch web UI")

    print("\n📊 WEB DASHBOARD:")
    print("   streamlit run dashboard.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
