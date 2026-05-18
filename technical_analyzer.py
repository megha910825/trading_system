#!/usr/bin/env python3
"""
Technical Analyzer - VERSION 3
Target: 50%+ win rate

Key improvements:
1. Better entry timing (wait for pullback confirmation)
2. Wider stops (2.5x ATR)
3. Require short-term momentum confirmation
4. Filter out choppy/ranging markets
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional

try:
    import ta
    from ta.trend import EMAIndicator, MACD, ADXIndicator
    from ta.momentum import RSIIndicator, StochasticOscillator
    from ta.volatility import AverageTrueRange, BollingerBands
    HAS_TA = True
except ImportError:
    HAS_TA = False


class TechnicalAnalyzer:
    """
    Technical Analyzer V3 - Focus on WIN RATE
    """

    def __init__(self):
        # Indicator periods
        self.ema_fast = 8
        self.ema_medium = 21
        self.ema_slow = 50
        self.ema_trend = 200
        self.rsi_period = 14
        self.atr_period = 14
        self.adx_period = 14

        # Thresholds
        self.min_adx = 20
        self.rsi_min = 35
        self.rsi_max = 62  # Tighter max (was 70)
        self.min_volume_ratio = 0.7

        # Wider stop for better win rate
        self.stop_atr_mult = 2.5  # Increased from 2.0

        # Score thresholds
        self.strong_buy_threshold = 70
        self.buy_threshold = 60  # Slightly higher (was 55)
        self.watch_threshold = 45

    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate all technical indicators"""
        if df.empty or len(df) < 50:
            return df

        df = df.copy()

        # Moving Averages
        if HAS_TA:
            df['ema_8'] = EMAIndicator(df['close'], window=8).ema_indicator()
            df['ema_21'] = EMAIndicator(df['close'], window=21).ema_indicator()
            df['ema_50'] = EMAIndicator(df['close'], window=50).ema_indicator()
            df['ema_200'] = EMAIndicator(df['close'], window=200).ema_indicator()
        else:
            df['ema_8'] = df['close'].ewm(span=8, adjust=False).mean()
            df['ema_21'] = df['close'].ewm(span=21, adjust=False).mean()
            df['ema_50'] = df['close'].ewm(span=50, adjust=False).mean()
            df['ema_200'] = df['close'].ewm(span=200, adjust=False).mean()

        # Trend Indicators
        if HAS_TA:
            adx = ADXIndicator(df['high'], df['low'], df['close'], window=self.adx_period)
            df['adx'] = adx.adx()
            df['di_plus'] = adx.adx_pos()
            df['di_minus'] = adx.adx_neg()

            macd = MACD(df['close'], window_slow=26, window_fast=12, window_sign=9)
            df['macd'] = macd.macd()
            df['macd_signal'] = macd.macd_signal()
            df['macd_hist'] = macd.macd_diff()
        else:
            df['adx'] = 25
            df['di_plus'] = 0
            df['di_minus'] = 0
            ema12 = df['close'].ewm(span=12, adjust=False).mean()
            ema26 = df['close'].ewm(span=26, adjust=False).mean()
            df['macd'] = ema12 - ema26
            df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
            df['macd_hist'] = df['macd'] - df['macd_signal']

        # Momentum
        if HAS_TA:
            df['rsi'] = RSIIndicator(df['close'], window=self.rsi_period).rsi()
            stoch = StochasticOscillator(df['high'], df['low'], df['close'], window=14)
            df['stoch_k'] = stoch.stoch()
            df['stoch_d'] = stoch.stoch_signal()
        else:
            delta = df['close'].diff()
            gain = delta.where(delta > 0, 0).rolling(window=self.rsi_period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=self.rsi_period).mean()
            rs = gain / (loss + 0.0001)
            df['rsi'] = 100 - (100 / (1 + rs))
            df['stoch_k'] = 50
            df['stoch_d'] = 50

        # Volatility
        if HAS_TA:
            df['atr'] = AverageTrueRange(df['high'], df['low'], df['close'], window=self.atr_period).average_true_range()
            bb = BollingerBands(df['close'], window=20, window_dev=2)
            df['bb_upper'] = bb.bollinger_hband()
            df['bb_middle'] = bb.bollinger_mavg()
            df['bb_lower'] = bb.bollinger_lband()
        else:
            tr1 = df['high'] - df['low']
            tr2 = abs(df['high'] - df['close'].shift())
            tr3 = abs(df['low'] - df['close'].shift())
            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            df['atr'] = tr.rolling(window=self.atr_period).mean()
            df['bb_middle'] = df['close'].rolling(window=20).mean()
            std = df['close'].rolling(window=20).std()
            df['bb_upper'] = df['bb_middle'] + (std * 2)
            df['bb_lower'] = df['bb_middle'] - (std * 2)

        df['atr_pct'] = (df['atr'] / df['close']) * 100

        # Volume
        df['volume_sma'] = df['volume'].rolling(window=20).mean()
        df['volume_ratio'] = df['volume'] / (df['volume_sma'] + 1)

        # Derived signals
        df['above_200'] = df['close'] > df['ema_200']
        df['above_50'] = df['close'] > df['ema_50']
        df['above_21'] = df['close'] > df['ema_21']

        df['ema_bullish'] = (
            (df['ema_8'] > df['ema_21']) &
            (df['close'] > df['ema_21'])
        )

        df['ema_strong_bull'] = (
            (df['ema_8'] > df['ema_21']) &
            (df['ema_21'] > df['ema_50']) &
            (df['close'] > df['ema_50'])
        )

        df['dist_from_ema21'] = (df['close'] - df['ema_21']) / df['ema_21']

        # Support/Resistance
        df['recent_high'] = df['high'].rolling(window=20).max()
        df['recent_low'] = df['low'].rolling(window=20).min()
        df['swing_low_10'] = df['low'].rolling(window=10).min()

        # Price momentum - KEY FOR TIMING
        df['close_1d_ago'] = df['close'].shift(1)
        df['close_2d_ago'] = df['close'].shift(2)
        df['close_3d_ago'] = df['close'].shift(3)

        # Green candle (close > open)
        df['green_candle'] = df['close'] > df['open']

        # Consecutive green candles
        df['green_streak'] = df['green_candle'].rolling(window=3).sum()

        # Bouncing (today higher than yesterday)
        df['bouncing'] = df['close'] > df['close_1d_ago']

        # 3-day momentum
        df['mom_3d'] = ((df['close'] - df['close_3d_ago']) / df['close_3d_ago']) * 100

        return df

    def identify_setup(self, df: pd.DataFrame) -> Dict:
        """
        Identify trading setup with TIMING focus
        """
        if df.empty or len(df) < 50:
            return {"setup": "NONE", "score": 0, "reasons": []}

        latest = df.iloc[-1]
        prev = df.iloc[-2] if len(df) > 1 else latest
        prev2 = df.iloc[-3] if len(df) > 2 else prev

        score = 0
        reasons = []
        setup_type = "NONE"

        # ─────────────────────────────────────────────────────────────
        # TREND CHECKS (35 points max)
        # ─────────────────────────────────────────────────────────────

        # Strong EMA alignment (8 > 21 > 50)
        if latest.get('ema_strong_bull', False):
            score += 20
            reasons.append("Strong trend (8>21>50 EMA) ✓")
        elif latest.get('ema_bullish', False):
            score += 12
            reasons.append("EMAs bullish ✓")

        # Above 50 EMA
        if latest.get('above_50', False):
            score += 10
            reasons.append("Above 50 EMA ✓")
        else:
            score -= 10
            reasons.append("Below 50 EMA ✗")

        # ADX trend strength
        adx = latest.get('adx', 0)
        if adx >= 25:
            score += 5
            reasons.append(f"Strong trend ADX={adx:.0f} ✓")
        elif adx >= 20:
            score += 2
        elif adx < 15:
            score -= 5
            reasons.append("Weak/choppy market ✗")

        # ─────────────────────────────────────────────────────────────
        # TIMING/ENTRY CHECKS (35 points max) - MOST IMPORTANT
        # ─────────────────────────────────────────────────────────────

        dist = latest.get('dist_from_ema21', 0)

        # PULLBACK ENTRY (best setup)
        # Price pulled back to near 21 EMA and is now bouncing
        is_near_ema = -0.01 <= dist <= 0.03  # Within 1% below to 3% above
        is_bouncing = latest.get('bouncing', False)
        green_candle = latest.get('green_candle', False)

        if is_near_ema and is_bouncing and green_candle:
            score += 25
            reasons.append("Pullback bounce entry ✓✓")
            setup_type = "PULLBACK_BOUNCE"
        elif is_near_ema and is_bouncing:
            score += 18
            reasons.append("Near EMA + bouncing ✓")
            setup_type = "PULLBACK"
        elif is_near_ema:
            score += 10
            reasons.append("Near 21 EMA")
            setup_type = "PULLBACK"
        elif dist > 0.06:
            score -= 10
            reasons.append("Too extended from EMA ✗")

        # Short-term momentum confirmation
        mom_3d = latest.get('mom_3d', 0)
        if mom_3d > 1:
            score += 8
            reasons.append(f"3-day momentum +{mom_3d:.1f}% ✓")
        elif mom_3d > 0:
            score += 4
        elif mom_3d < -2:
            score -= 8
            reasons.append("Negative momentum ✗")

        # Stochastic timing
        stoch_k = latest.get('stoch_k', 50)
        stoch_d = latest.get('stoch_d', 50)

        # Stoch crossing up from oversold
        stoch_bullish = stoch_k > stoch_d and stoch_k < 50
        if stoch_k < 30:
            score += 5
            reasons.append("Stoch oversold ✓")
        elif stoch_bullish:
            score += 3
            reasons.append("Stoch turning up ✓")
        elif stoch_k > 80:
            score -= 8
            reasons.append("Stoch overbought ✗")

        # ─────────────────────────────────────────────────────────────
        # MOMENTUM CHECKS (20 points max)
        # ─────────────────────────────────────────────────────────────

        rsi = latest.get('rsi', 50)

        # RSI sweet spot
        if 40 <= rsi <= 55:
            score += 12
            reasons.append(f"RSI ideal ({rsi:.0f}) ✓")
        elif 35 <= rsi <= 60:
            score += 6
            reasons.append(f"RSI ok ({rsi:.0f})")
        elif rsi > 65:
            score -= 10
            reasons.append(f"RSI overbought ({rsi:.0f}) ✗")
        elif rsi < 30:
            score += 3
            reasons.append(f"RSI oversold ({rsi:.0f})")

        # MACD
        macd = latest.get('macd', 0)
        macd_hist = latest.get('macd_hist', 0)
        macd_hist_prev = prev.get('macd_hist', 0)

        # MACD histogram turning up (momentum shifting)
        macd_turning_up = macd_hist > macd_hist_prev

        if macd > 0 and macd_hist > 0:
            score += 8
            reasons.append("MACD bullish ✓")
        elif macd > 0 and macd_turning_up:
            score += 5
            reasons.append("MACD turning up ✓")
        elif macd < 0 and macd_hist < macd_hist_prev:
            score -= 5
            reasons.append("MACD bearish ✗")

        # ─────────────────────────────────────────────────────────────
        # VOLUME (10 points max)
        # ─────────────────────────────────────────────────────────────

        vol_ratio = latest.get('volume_ratio', 1)

        if vol_ratio >= 1.3:
            score += 10
            reasons.append(f"High volume ({vol_ratio:.1f}x) ✓")
        elif vol_ratio >= 1.0:
            score += 5
            reasons.append("Good volume ✓")
        elif vol_ratio >= 0.7:
            score += 2
        else:
            score -= 3
            reasons.append("Low volume ✗")

        # ─────────────────────────────────────────────────────────────
        # DISQUALIFIERS (hard filters)
        # ─────────────────────────────────────────────────────────────

        # RSI too high - SKIP
        if rsi > 70:
            score = min(score, 40)
            reasons.append("SKIP: RSI > 70")

        # Below 50 EMA - reduce score significantly
        if not latest.get('above_50', False):
            score = min(score, 45)

        # Very extended - SKIP
        if dist > 0.08:
            score = min(score, 35)
            reasons.append("SKIP: Too extended")

        return {
            "setup": setup_type if score >= 50 else "NONE",
            "score": max(0, min(100, score)),
            "reasons": reasons,
            "rsi": rsi,
            "adx": adx,
            "volume_ratio": vol_ratio,
            "dist_from_ema": dist,
            "is_bouncing": is_bouncing,
            "green_candle": green_candle,
        }

    def calculate_levels(self, df: pd.DataFrame, setup_info: Dict) -> Dict:
        """Calculate entry, stop loss, and targets with WIDER stops"""
        if df.empty:
            return {}

        latest = df.iloc[-1]
        current_price = latest['close']
        atr = latest.get('atr', current_price * 0.02)
        ema_21 = latest.get('ema_21', current_price)

        # ENTRY
        entry = current_price  # Enter at current price when conditions met
        entry = round(entry, 2)

        # STOP LOSS: 2.5x ATR (WIDER for better win rate)
        stop_distance = atr * self.stop_atr_mult

        # Also consider swing low
        swing_low = latest.get('swing_low_10', current_price * 0.95)

        # Use wider of ATR stop or below swing low
        atr_stop = entry - stop_distance
        structure_stop = swing_low - (atr * 0.3)

        stop_loss = min(atr_stop, structure_stop)

        # Max stop: 8%
        max_stop = entry * 0.92
        stop_loss = max(stop_loss, max_stop)
        stop_loss = round(stop_loss, 2)

        # TARGETS
        risk = entry - stop_loss

        if risk <= 0:
            return {}

        # Targets based on risk
        target_1 = entry + (risk * 1.8)   # 1.8R (slightly lower for higher hit rate)
        target_2 = entry + (risk * 3.0)   # 3R

        target_1 = round(target_1, 2)
        target_2 = round(target_2, 2)

        rr_1 = (target_1 - entry) / risk
        rr_2 = (target_2 - entry) / risk

        return {
            "entry": entry,
            "stop_loss": stop_loss,
            "target_1": target_1,
            "target_2": target_2,
            "risk": round(risk, 2),
            "risk_pct": round((risk / entry) * 100, 2),
            "rr_1": round(rr_1, 2),
            "rr_2": round(rr_2, 2),
            "atr": round(atr, 2),
            "atr_pct": round((atr / current_price) * 100, 2),
        }

    def get_signal_status(self, score: int) -> str:
        """Convert score to signal status"""
        if score >= self.strong_buy_threshold:
            return "STRONG BUY"
        elif score >= self.buy_threshold:
            return "BUY"
        elif score >= self.watch_threshold:
            return "WATCH"
        else:
            return "AVOID"

    def analyze_stock(self, df: pd.DataFrame, symbol: str = "") -> Dict:
        """Complete stock analysis"""
        result = {
            "symbol": symbol,
            "timestamp": datetime.now().isoformat(),
            "signal_status": "AVOID",
            "signal_score": 0,
            "setup_type": "NONE",
            "current_price": 0,
        }

        if df.empty or len(df) < 50:
            result["error"] = "Insufficient data"
            return result

        try:
            # Calculate indicators
            df = self.calculate_indicators(df)

            latest = df.iloc[-1]
            result["current_price"] = round(latest['close'], 2)

            # Identify setup
            setup_info = self.identify_setup(df)
            result["signal_score"] = setup_info["score"]
            result["setup_type"] = setup_info["setup"]
            result["analysis_reasons"] = setup_info.get("reasons", [])

            # Get signal status
            result["signal_status"] = self.get_signal_status(setup_info["score"])

            # Calculate levels for actionable signals
            if result["signal_status"] in ["STRONG BUY", "BUY"]:
                levels = self.calculate_levels(df, setup_info)

                if levels:
                    result.update(levels)
                    result["ideal_entry"] = levels.get("entry")
                    result["risk_reward"] = levels.get("rr_1", 0)
                else:
                    result["signal_status"] = "WATCH"
                    result["signal_score"] = min(result["signal_score"], 50)

            # Add indicator values
            result["rsi"] = round(latest.get('rsi', 0), 1)
            result["adx"] = round(latest.get('adx', 0), 1)
            result["volume_ratio"] = round(latest.get('volume_ratio', 1), 2)
            result["trend"] = "BULLISH" if latest.get('ema_strong_bull', False) else "NEUTRAL"
            result["above_200_ema"] = bool(latest.get('above_200', False))
            result["above_50_ema"] = bool(latest.get('above_50', False))

        except Exception as e:
            result["error"] = str(e)
            result["signal_status"] = "AVOID"

        return result


# ═══════════════════════════════════════════════════════════════
# TEST
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 60)
    print("TECHNICAL ANALYZER V3 - TEST")
    print("=" * 60)

    try:
        import yfinance as yf

        analyzer = TechnicalAnalyzer()
        test_symbols = ["NVDA", "AAPL", "MSFT", "AMD", "GOOGL", "META", "TSLA"]

        for symbol in test_symbols:
            print(f"\n{'─'*50}")
            print(f"Analyzing {symbol}...")

            ticker = yf.Ticker(symbol)
            df = ticker.history(period="1y")
            df.columns = df.columns.str.lower()

            if not df.empty:
                result = analyzer.analyze_stock(df, symbol)

                status = result['signal_status']
                score = result['signal_score']

                if status == "STRONG BUY":
                    icon = "🟢"
                elif status == "BUY":
                    icon = "🟡"
                elif status == "WATCH":
                    icon = "🟠"
                else:
                    icon = "🔴"

                print(f"  {icon} {status} (Score: {score})")
                print(f"  Setup: {result['setup_type']}")
                print(f"  RSI: {result.get('rsi')} | ADX: {result.get('adx')}")

                if result.get('entry'):
                    print(f"  Entry: ${result['entry']} | Stop: ${result['stop_loss']} | Target: ${result['target_1']}")

        print(f"\n{'='*60}")

    except ImportError:
        print("Run: pip install yfinance ta")
