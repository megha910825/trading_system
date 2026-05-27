#!/usr/bin/env python3
"""
Global Signal Generator - Generates signals for US, German, and Indian markets
"""

import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional

from global_data_fetcher import GlobalDataFetcher
from technical_analyzer import TechnicalAnalyzer
from market_config import MARKETS, get_market_status
from global_universe_manager import GlobalUniverseManager


class GlobalSignalGenerator:
    """
    Generates trading signals for multiple international markets
    """

    def __init__(self):
        self.fetcher = GlobalDataFetcher()
        self.analyzer = TechnicalAnalyzer()
        self.universe_manager = GlobalUniverseManager()
        self.signals = {}  # {market: [signals]}
        self.all_signals = []

    def generate_signals(self, markets: List[str] = None) -> Dict[str, List[Dict]]:
        """
        Generate signals for specified markets

        Args:
            markets: List of market codes ['US', 'DE', 'IN']

        Returns:
            Dict of signals by market
        """
        if markets is None:
            markets = ["US", "DE", "IN"]

        # Load universe
        universe = self.universe_manager.load_universe()

        if not universe:
            print("No universe found. Running quick update...")
            universe = self.universe_manager.quick_update(markets=markets)

        print(f"\n{'='*60}")
        print("GENERATING GLOBAL SIGNALS")
        print(f"{'='*60}")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

        # Show market status
        print("\n📊 Market Status:")
        status = get_market_status()
        for market, stat in status.items():
            if market in markets:
                print(f"  {MARKETS[market].name}: {stat}")

        self.signals = {}
        self.all_signals = []

        for market in markets:
            symbols = universe.get(market, [])

            if not symbols:
                print(f"\n⚠️ No stocks in {MARKETS[market].name} universe")
                continue

            print(f"\n{'='*50}")
            print(f"📊 {MARKETS[market].name} ({MARKETS[market].currency})")
            print(f"{'='*50}")
            print(f"Analyzing {len(symbols)} stocks...")

            market_signals = []

            for i, symbol in enumerate(symbols):
                print(f"  {symbol} ({i+1}/{len(symbols)})...", end="\r")

                try:
                    signal = self._analyze_symbol(symbol)
                    if signal and signal.get("signal_status") in ["STRONG BUY", "BUY"]:
                        market_signals.append(signal)
                except Exception as e:
                    print(f"Warning: Error analyzing {symbol}: {e}")
                    continue

            print()

            # Sort by score
            market_signals = sorted(market_signals, key=lambda x: x.get("signal_score", 0), reverse=True)

            self.signals[market] = market_signals
            self.all_signals.extend(market_signals)

            # Print summary
            strong = len([s for s in market_signals if s["signal_status"] == "STRONG BUY"])
            buy = len([s for s in market_signals if s["signal_status"] == "BUY"])

            print(f"  Results: {strong} STRONG BUY, {buy} BUY")

        return self.signals

    def _analyze_symbol(self, symbol: str) -> Optional[Dict]:
        """Analyze a single symbol"""
        df = self.fetcher.get_stock_data(symbol, "6mo")
        if df.empty or len(df) < 50:
            return None

        # Use existing technical analyzer
        analysis = self.analyzer.analyze_stock(df, symbol)
        if "error" in analysis:
            return None

        # Get additional info
        info = self.fetcher.get_stock_info(symbol)
        market = self.fetcher.detect_market(symbol)
        market_info = MARKETS[market]

        # Add market-specific info
        analysis.update({
            "name": info.get("name", symbol),
            "sector": info.get("sector", "Unknown"),
            "market": market,
            "market_name": market_info.name,
            "currency": market_info.currency,
            "market_cap": info.get("market_cap", 0),
            "market_cap_b": round(info.get("market_cap", 0) / 1e9, 2),
            "timestamp": datetime.now().isoformat(),
        })

        return analysis

    def get_summary(self, market: str = None) -> pd.DataFrame:
        """Get signal summary"""
        if market:
            signals = self.signals.get(market, [])
        else:
            signals = self.all_signals

        if not signals:
            return pd.DataFrame()

        cols = ["symbol", "name", "market", "currency", "signal_status", "signal_score",
                "current_price", "ideal_entry", "stop_loss", "target_1", "risk_reward", "rsi"]

        df = pd.DataFrame(signals)
        return df[[c for c in cols if c in df.columns]]

    def format_alert(self, signal: Dict) -> str:
        """Format signal as alert text"""
        market = signal.get("market", "US")
        market_info = MARKETS.get(market, MARKETS["US"])
        currency_symbol = {"USD": "$", "EUR": "€", "INR": "₹"}.get(signal.get("currency", "USD"), "$")

        return f"""
{'='*50}
🌍 {market_info.name} | 🎯 {signal.get('signal_status')}
{'='*50}

{signal.get('symbol')} - {signal.get('name', '')}
Sector: {signal.get('sector', 'N/A')}
Setup: {signal.get('setup_type')}
Score: {signal.get('signal_score')}/100

📊 CURRENT STATUS:
   Price: {currency_symbol}{signal.get('current_price', 0):,.2f}
   RSI: {signal.get('rsi', 0):.1f}
   ATR: {signal.get('atr_pct', 0):.2f}%
   Trend: {'BULLISH ✓' if signal.get('uptrend') else 'BEARISH ✗'}

💰 TRADE SETUP ({signal.get('currency', 'USD')}):
   Entry: {currency_symbol}{signal.get('ideal_entry', 0):,.2f}
   Stop Loss: {currency_symbol}{signal.get('stop_loss', 0):,.2f} (-{signal.get('stop_loss_pct', 0):.1f}%)
   Target 1: {currency_symbol}{signal.get('target_1', 0):,.2f} (+{signal.get('target_1_pct', 0):.1f}%)
   Target 2: {currency_symbol}{signal.get('target_2', 0):,.2f} (+{signal.get('target_2_pct', 0):.1f}%)

📈 RISK/REWARD:
   R:R (Target 1): {signal.get('risk_reward', 0):.2f}
   R:R (Target 2): {signal.get('risk_reward_t2', 0):.2f}

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M')} ({market_info.timezone})
{'='*50}
"""

    def print_all_signals(self):
        """Print all signals organized by market"""
        print("\n" + "=" * 70)
        print("GLOBAL TRADING SIGNALS SUMMARY")
        print("=" * 70)

        if not self.signals:
            print("No signals generated. Run generate_signals() first.")
            return

        total_signals = 0

        for market, signals in self.signals.items():
            if not signals:
                continue

            market_info = MARKETS[market]
            currency_symbol = {"USD": "$", "EUR": "€", "INR": "₹"}.get(market_info.currency, "$")

            print(f"\n{'='*60}")
            print(f"📊 {market_info.name} ({market_info.currency}) - {len(signals)} Signals")
            print(f"{'='*60}")

            for i, sig in enumerate(signals[:5]):  # Top 5 per market
                status_emoji = "🟢" if sig["signal_status"] == "STRONG BUY" else "🟡"

                print(f"\n{status_emoji} {i+1}. {sig['symbol']} - {sig['signal_status']} (Score: {sig['signal_score']})")
                print(f"   {sig.get('name', '')[:40]}")
                print(f"   Price: {currency_symbol}{sig['current_price']:,.2f} | "
                      f"Entry: {currency_symbol}{sig['ideal_entry']:,.2f} | "
                      f"Stop: {currency_symbol}{sig['stop_loss']:,.2f}")
                print(f"   Target: {currency_symbol}{sig['target_1']:,.2f} | R:R: {sig['risk_reward']:.2f}")

            if len(signals) > 5:
                print(f"\n   ... and {len(signals) - 5} more signals")

            total_signals += len(signals)

        print(f"\n{'='*70}")
        print(f"Total Signals: {total_signals}")
        print(f"{'='*70}")


# ============================================================
# MAIN / TEST
# ============================================================

if __name__ == "__main__":
    gen = GlobalSignalGenerator()

    # Generate signals for all markets
    signals = gen.generate_signals(markets=["US", "DE", "IN"])

    # Print summary
    gen.print_all_signals()

    # Print detailed alert for top signal from each market
    for market, market_signals in signals.items():
        if market_signals:
            print(gen.format_alert(market_signals[0]))
