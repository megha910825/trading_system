"""Signal Generator - FIXED VERSION"""

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
        self.all_analyzed = []

    def generate_signals(self, symbols: List[str] = None) -> List[Dict]:
        """Generate signals"""
        if symbols is None:
            symbols = config.STOCK_UNIVERSE

        signals = []
        all_stocks = []

        print(f"Analyzing {len(symbols)} stocks...")

        for i, symbol in enumerate(symbols):
            print(f"  {symbol} ({i+1}/{len(symbols)})...", end="\r")

            try:
                result = self._analyze(symbol)
                if result:
                    all_stocks.append(result)

                    # Include BUY and STRONG BUY
                    if result.get("signal_status") in ["STRONG BUY", "BUY"]:
                        signals.append(result)
            except Exception as e:
                continue

        print()

        # Sort by score
        signals = sorted(signals, key=lambda x: x.get("signal_score", 0), reverse=True)
        all_stocks = sorted(all_stocks, key=lambda x: x.get("signal_score", 0), reverse=True)

        self.signals = signals
        self.all_analyzed = all_stocks

        # Summary
        strong_buy = len([s for s in signals if s["signal_status"] == "STRONG BUY"])
        buy = len([s for s in signals if s["signal_status"] == "BUY"])
        watch = len([s for s in all_stocks if s["signal_status"] == "WATCH"])

        print(f"\nResults:")
        print(f"  STRONG BUY: {strong_buy}")
        print(f"  BUY: {buy}")
        print(f"  WATCH: {watch}")
        print(f"  Total Signals: {len(signals)}")

        return signals

    def _analyze(self, symbol: str) -> Optional[Dict]:
        """Analyze a symbol"""
        df = self.fetcher.get_stock_data(symbol, "6mo")
        if df.empty or len(df) < 50:
            return None

        analysis = self.analyzer.analyze_stock(df, symbol)
        if "error" in analysis:
            return None

        info = self.fetcher.get_stock_info(symbol)

        # Only hard filters
        c = config.SCREENING_CRITERIA
        if info.get("market_cap", 0) < c["min_market_cap"]:
            return None
        if info.get("avg_volume", 0) < c["min_avg_volume"]:
            return None

        return {
            "timestamp": datetime.now().isoformat(),
            "name": info.get("name", symbol),
            "sector": info.get("sector", "Unknown"),
            "market_cap_b": round(info.get("market_cap", 0) / 1e9, 1),
            "avg_volume_m": round(info.get("avg_volume", 0) / 1e6, 1),
            **analysis,
        }

    def get_summary(self) -> pd.DataFrame:
        """Get summary DataFrame"""
        data = self.signals if self.signals else self.all_analyzed
        if not data:
            return pd.DataFrame()

        cols = ["symbol", "signal_status", "signal_score", "current_price",
                "ideal_entry", "stop_loss", "target_1", "risk_reward",
                "rsi", "atr_pct", "setup_type"]

        df = pd.DataFrame(data)
        return df[[c for c in cols if c in df.columns]]

    def format_alert(self, signal: Dict) -> str:
        """Format signal as alert text"""
        return f"""
{'='*50}
🎯 {signal.get('signal_status')}: {signal.get('symbol')}
{'='*50}

{signal.get('name', '')}
Sector: {signal.get('sector', 'N/A')}
Setup: {signal.get('setup_type')}
Score: {signal.get('signal_score')}/100

📊 CURRENT STATUS:
   Price: ${signal.get('current_price', 0):.2f}
   RSI: {signal.get('rsi', 0):.1f}
   ATR: {signal.get('atr_pct', 0):.2f}%
   Trend: {'BULLISH ✓' if signal.get('uptrend') else 'BEARISH ✗'}

💰 TRADE SETUP:
   Entry: ${signal.get('ideal_entry', 0):.2f}
   Stop Loss: ${signal.get('stop_loss', 0):.2f} (-{signal.get('stop_loss_pct', 0):.1f}%)
   Target 1: ${signal.get('target_1', 0):.2f} (+{signal.get('target_1_pct', 0):.1f}%)
   Target 2: ${signal.get('target_2', 0):.2f} (+{signal.get('target_2_pct', 0):.1f}%)

📈 RISK/REWARD:
   R:R (Target 1): {signal.get('risk_reward', 0):.2f}
   R:R (Target 2): {signal.get('risk_reward_t2', 0):.2f}

⏰ Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}
{'='*50}
"""


if __name__ == "__main__":
    gen = SignalGenerator()
    signals = gen.generate_signals()

    print("\n" + "=" * 70)
    print("SIGNAL SUMMARY")
    print("=" * 70)

    summary = gen.get_summary()
    if not summary.empty:
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', None)
        print(summary.to_string(index=False))
    else:
        print("No signals generated")

    if signals:
        print("\n" + "=" * 70)
        print("TOP SIGNAL")
        print("=" * 70)
        print(gen.format_alert(signals[0]))
