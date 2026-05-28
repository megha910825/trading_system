"""Technical Analyzer - Calculates indicators and levels"""

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

        status = "STRONG BUY" if (score >= 70 and rr >= 2.0) else ("BUY" if score >= 55 else ("WATCH" if score >= 40 else "AVOID"))

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
