#!/usr/bin/env python3
"""
FIXED Technical Analyzer - Corrects the R:R calculation bug
Save this as: technical_analyzer.py
"""

import pandas as pd
import numpy as np
from typing import Dict
import config


class TechnicalAnalyzer:
    """Calculates technical indicators - FIXED VERSION"""

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

        # MACD
        ema12 = df["close"].ewm(span=12, adjust=False).mean()
        ema26 = df["close"].ewm(span=26, adjust=False).mean()
        df["macd"] = ema12 - ema26
        df["macd_signal"] = df["macd"].ewm(span=9, adjust=False).mean()
        df["macd_hist"] = df["macd"] - df["macd_signal"]

        return df

    def analyze_stock(self, df: pd.DataFrame, symbol: str) -> Dict:
        """Complete analysis - FIXED R:R CALCULATION"""
        if df.empty or len(df) < 50:
            return {"symbol": symbol, "error": "Insufficient data"}

        df = self.calculate_indicators(df)
        curr = df.iloc[-1]
        prev = df.iloc[-2]

        # Current values
        price = curr["close"]
        ema20 = curr["ema_20"]
        ema50 = curr["ema_50"]
        support = curr["support"]
        resistance = curr["resistance"]
        atr = curr["atr"]
        rsi = curr["rsi"]

        # ============================================================
        # FIXED: Entry calculation based on CURRENT PRICE
        # ============================================================

        # Entry should be near current price, not far below
        # For a pullback: entry near EMA20 or support
        # For momentum: entry near current price

        dist_from_ema20 = abs(curr["dist_ema20_pct"])

        if dist_from_ema20 < 3:
            # Price is near EMA20 - good pullback entry
            ideal_entry = price * 0.998  # Enter slightly below current
            setup = "PULLBACK"
        elif price > ema20:
            # Price above EMA20 - momentum entry
            ideal_entry = price * 0.995  # Small pullback entry
            setup = "MOMENTUM"
        else:
            # Price below EMA20 - wait for bounce
            ideal_entry = ema20 * 0.99
            setup = "BOUNCE"

        # ============================================================
        # FIXED: Stop loss and targets based on ATR
        # ============================================================

        stop_distance = self.exit_rules["stop_loss_atr_mult"] * atr
        target1_distance = self.exit_rules["target_1_atr_mult"] * atr
        target2_distance = self.exit_rules["target_2_atr_mult"] * atr

        stop_loss = ideal_entry - stop_distance
        target_1 = ideal_entry + target1_distance
        target_2 = ideal_entry + target2_distance

        # ============================================================
        # FIXED: Risk/Reward calculation
        # ============================================================

        risk = ideal_entry - stop_loss  # Risk per share
        reward = target_1 - ideal_entry  # Reward per share

        if risk > 0:
            risk_reward = reward / risk
        else:
            risk_reward = 0

        # The R:R should be target_1_atr_mult / stop_loss_atr_mult
        # = 2.5 / 1.75 = 1.43 (this is correct by design!)

        # If you want higher R:R, adjust the multipliers in config
        # OR use a tighter stop loss

        # Let's also calculate R:R to Target 2
        reward_t2 = target_2 - ideal_entry
        risk_reward_t2 = reward_t2 / risk if risk > 0 else 0

        # ============================================================
        # IMPROVED SCORING - More realistic for current market
        # ============================================================

        score = 0

        # RSI (0-20 points) - RELAXED for bull market
        if 40 <= rsi <= 60:
            score += 20  # Perfect
        elif 35 <= rsi <= 70:
            score += 15  # Good (allows slightly overbought)
        elif 30 <= rsi <= 75:
            score += 10  # Acceptable
        elif rsi < 35:
            score += 15  # Oversold = buying opportunity
        elif rsi > 75:
            score += 5   # Overbought but still trending

        # Trend (0-25 points)
        if curr["strong_uptrend"]:
            score += 25
        elif curr["uptrend"]:
            score += 20
        elif price > curr["ema_200"]:
            score += 10

        # Near EMA20 (0-20 points) - Pullback quality
        if dist_from_ema20 < 2:
            score += 20
        elif dist_from_ema20 < 4:
            score += 15
        elif dist_from_ema20 < 6:
            score += 10
        elif dist_from_ema20 < 10:
            score += 5

        # ATR (0-15 points)
        atr_pct = curr["atr_pct"]
        if 2.0 <= atr_pct <= 5.0:
            score += 15
        elif 1.5 <= atr_pct <= 7.0:
            score += 10
        elif atr_pct >= 1.0:
            score += 5

        # Volume (0-10 points) - RELAXED
        rel_vol = curr["rel_volume"]
        if rel_vol >= 1.5:
            score += 10
        elif rel_vol >= 1.0:
            score += 8
        elif rel_vol >= 0.7:
            score += 6
        elif rel_vol >= 0.5:
            score += 4

        # MACD (0-10 points)
        if curr["macd_hist"] > 0 and curr["macd_hist"] > prev["macd_hist"]:
            score += 10  # Bullish and increasing
        elif curr["macd_hist"] > 0:
            score += 7   # Bullish
        elif curr["macd_hist"] > prev["macd_hist"]:
            score += 5   # Improving

        # Bonus: Price near support (0-5 points)
        support_distance_pct = ((price - support) / price) * 100
        if support_distance_pct < 3:
            score += 5
        elif support_distance_pct < 5:
            score += 3

        # Cap at 100
        score = min(score, 100)

        # Status
        if score >= 70:
            status = "STRONG BUY"
        elif score >= 55:
            status = "BUY"
        elif score >= 40:
            status = "WATCH"
        else:
            status = "AVOID"

        return {
            "symbol": symbol,
            "current_price": round(price, 2),
            "ideal_entry": round(ideal_entry, 2),
            "stop_loss": round(stop_loss, 2),
            "stop_loss_pct": round((stop_distance / ideal_entry) * 100, 2),
            "target_1": round(target_1, 2),
            "target_1_pct": round((target1_distance / ideal_entry) * 100, 2),
            "target_2": round(target_2, 2),
            "target_2_pct": round((target2_distance / ideal_entry) * 100, 2),
            "risk_reward": round(risk_reward, 2),
            "risk_reward_t2": round(risk_reward_t2, 2),
            "setup_type": setup,
            "signal_score": score,
            "signal_status": status,
            "rsi": round(rsi, 1),
            "atr": round(atr, 2),
            "atr_pct": round(atr_pct, 2),
            "rel_volume": round(rel_vol, 2),
            "uptrend": bool(curr["uptrend"]),
            "strong_uptrend": bool(curr["strong_uptrend"]),
            "ema_20": round(ema20, 2),
            "ema_50": round(ema50, 2),
            "support": round(support, 2),
            "resistance": round(resistance, 2),
            "dist_from_ema20": round(curr["dist_ema20_pct"], 2),
            "macd_bullish": bool(curr["macd_hist"] > 0),
        }


if __name__ == "__main__":
    from data_fetcher import DataFetcher

    fetcher = DataFetcher()
    analyzer = TechnicalAnalyzer()

    print("=" * 70)
    print("TESTING FIXED TECHNICAL ANALYZER")
    print("=" * 70)

    for symbol in ["NVDA", "AAPL", "MSFT", "AMD", "META"]:
        print(f"\n{'='*50}")
        print(f"{symbol}")
        print(f"{'='*50}")

        df = fetcher.get_stock_data(symbol, "6mo")
        if df.empty:
            print("  No data")
            continue

        result = analyzer.analyze_stock(df, symbol)

        print(f"  Price: ${result['current_price']}")
        print(f"  Signal: {result['signal_status']} (Score: {result['signal_score']})")
        print(f"  Setup: {result['setup_type']}")
        print(f"  ")
        print(f"  Entry: ${result['ideal_entry']}")
        print(f"  Stop: ${result['stop_loss']} (-{result['stop_loss_pct']}%)")
        print(f"  Target 1: ${result['target_1']} (+{result['target_1_pct']}%)")
        print(f"  Target 2: ${result['target_2']} (+{result['target_2_pct']}%)")
        print(f"  ")
        print(f"  R:R (T1): {result['risk_reward']}")
        print(f"  R:R (T2): {result['risk_reward_t2']}")
        print(f"  ")
        print(f"  RSI: {result['rsi']}")
        print(f"  ATR%: {result['atr_pct']}%")
        print(f"  Rel Vol: {result['rel_volume']}")
        print(f"  Trend: {'UP' if result['uptrend'] else 'DOWN'}")
