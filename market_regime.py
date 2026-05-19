#!/usr/bin/env python3
"""
Market Regime Filter - Know When to Trade
"""

import yfinance as yf
from datetime import datetime
from enum import Enum
from dataclasses import dataclass
from typing import Tuple


class Regime(Enum):
    STRONG_BULL = "STRONG_BULL"
    BULL = "BULL"
    NEUTRAL = "NEUTRAL"
    BEAR = "BEAR"
    STRONG_BEAR = "STRONG_BEAR"


@dataclass
class MarketConditions:
    regime: Regime
    spy_price: float
    spy_change_1d: float
    spy_change_5d: float
    spy_change_20d: float
    above_ema50: bool
    above_ema200: bool
    vix_level: float
    vix_status: str
    position_mult: float
    can_trade_long: bool
    recommendation: str


class MarketRegimeFilter:
    """Determine market conditions before trading"""

    def __init__(self):
        self._cache = None
        self._cache_time = None

    def analyze(self, use_cache: bool = True) -> MarketConditions:
        """Analyze current market regime"""

        # Use cache if recent
        if use_cache and self._cache_time:
            age = (datetime.now() - self._cache_time).seconds
            if age < 300 and self._cache:
                return self._cache

        try:
            spy = yf.Ticker("SPY")
            df = spy.history(period="1y")
            df.columns = df.columns.str.lower()

            df['ema50'] = df['close'].ewm(span=50).mean()
            df['ema200'] = df['close'].ewm(span=200).mean()

            latest = df.iloc[-1]
            price = latest['close']

            above_50 = price > latest['ema50']
            above_200 = price > latest['ema200']

            chg_1d = (price / df['close'].iloc[-2] - 1) * 100
            chg_5d = (price / df['close'].iloc[-6] - 1) * 100 if len(df) > 5 else 0
            chg_20d = (price / df['close'].iloc[-21] - 1) * 100 if len(df) > 20 else 0

            try:
                vix = yf.Ticker("^VIX").history(period="5d")
                vix_level = vix['Close'].iloc[-1]
            except:
                vix_level = 20

            if vix_level < 15:
                vix_status = "LOW"
            elif vix_level < 20:
                vix_status = "NORMAL"
            elif vix_level < 25:
                vix_status = "ELEVATED"
            elif vix_level < 35:
                vix_status = "HIGH"
            else:
                vix_status = "EXTREME"

            # Score
            score = 0
            if above_200: score += 20
            if above_50: score += 15
            if chg_20d > 3: score += 15
            elif chg_20d > 0: score += 5
            elif chg_20d < -3: score -= 15
            if vix_level < 18: score += 10
            elif vix_level > 25: score -= 10
            elif vix_level > 30: score -= 20

            if score >= 50:
                regime, mult, can_long = Regime.STRONG_BULL, 1.0, True
                rec = "🟢 STRONG BULL: Full aggression"
            elif score >= 25:
                regime, mult, can_long = Regime.BULL, 1.0, True
                rec = "🟢 BULL: Normal trading"
            elif score >= 0:
                regime, mult, can_long = Regime.NEUTRAL, 0.75, True
                rec = "🟡 NEUTRAL: 75% position size"
            elif score >= -25:
                regime, mult, can_long = Regime.BEAR, 0.5, True
                rec = "🔴 BEAR: 50% size, selective"
            else:
                regime, mult, can_long = Regime.STRONG_BEAR, 0.25, False
                rec = "🔴 STRONG BEAR: Avoid longs"

            result = MarketConditions(
                regime=regime, spy_price=round(price, 2),
                spy_change_1d=round(chg_1d, 2),
                spy_change_5d=round(chg_5d, 2),
                spy_change_20d=round(chg_20d, 2),
                above_ema50=above_50, above_ema200=above_200,
                vix_level=round(vix_level, 2), vix_status=vix_status,
                position_mult=mult, can_trade_long=can_long,
                recommendation=rec
            )

            self._cache = result
            self._cache_time = datetime.now()
            return result

        except Exception as e:
            return MarketConditions(
                regime=Regime.NEUTRAL, spy_price=0,
                spy_change_1d=0, spy_change_5d=0, spy_change_20d=0,
                above_ema50=False, above_ema200=False,
                vix_level=20, vix_status="UNKNOWN",
                position_mult=0.5, can_trade_long=True,
                recommendation=f"⚠️ Error: {e}"
            )

    def should_trade(self) -> Tuple[bool, str, float]:
        """Quick check"""
        c = self.analyze()
        return c.can_trade_long, c.recommendation, c.position_mult

    def print_report(self):
        """Print market analysis"""
        c = self.analyze(use_cache=False)

        def icon(v): return "✅" if v else "❌"
        def chg(v): return f"🟢 +{v:.2f}%" if v > 0 else f"🔴 {v:.2f}%"

        print(f"""
╔═══════════════════════════════════════════════════════════════════════╗
║                     🌍 MARKET REGIME ANALYSIS
║                     {datetime.now().strftime('%Y-%m-%d %H:%M')}
╠═══════════════════════════════════════════════════════════════════════╣
║                                                                       ║
║  REGIME: {c.regime.value:^15}     Position Size: {c.position_mult*100:.0f}%
║                                                                       ║
║  SPY: ${c.spy_price:,.2f}
║  1D:  {chg(c.spy_change_1d):15}   5D: {chg(c.spy_change_5d):15}
║  20D: {chg(c.spy_change_20d):15}
║                                                                       ║
║  Above 50 EMA:  {icon(c.above_ema50)}      Above 200 EMA: {icon(c.above_ema200)}
║  VIX: {c.vix_level:.1f} ({c.vix_status})
║                                                                       ║
║  Can Trade Long: {icon(c.can_trade_long)}
║                                                                       ║
║  {c.recommendation:^67} ║
╚═══════════════════════════════════════════════════════════════════════╝""")


if __name__ == "__main__":
    MarketRegimeFilter().print_report()
