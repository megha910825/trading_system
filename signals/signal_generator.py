"""Signal Generator - Creates trading signals"""

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
