#!/usr/bin/env python3
"""
Debug Script - See why no signals are being generated
"""

import sys
sys.path.insert(0, '.')

from data_fetcher import DataFetcher
from technical_analyzer import TechnicalAnalyzer
import config

def debug_signals():
    fetcher = DataFetcher()
    analyzer = TechnicalAnalyzer()

    # Test with a few popular stocks
    test_symbols = ["NVDA", "AMD", "AAPL", "MSFT", "META", "GOOGL", "AMZN", "TSLA"]

    print("=" * 80)
    print("DEBUGGING SIGNAL GENERATION")
    print("=" * 80)

    for symbol in test_symbols:
        print(f"\n{'='*40}")
        print(f"ANALYZING: {symbol}")
        print(f"{'='*40}")

        # Get data
        df = fetcher.get_stock_data(symbol, "6mo")
        if df.empty:
            print(f"  ❌ No data available")
            continue

        print(f"  ✓ Data: {len(df)} rows")

        # Get info
        info = fetcher.get_stock_info(symbol)
        print(f"  ✓ Market Cap: ${info.get('market_cap', 0)/1e9:.1f}B")
        print(f"  ✓ Avg Volume: {info.get('avg_volume', 0)/1e6:.1f}M")

        # Analyze
        result = analyzer.analyze_stock(df, symbol)

        if "error" in result:
            print(f"  ❌ Analysis error: {result['error']}")
            continue

        print(f"\n  📊 ANALYSIS RESULTS:")
        print(f"     Price: ${result['current_price']}")
        print(f"     Signal: {result['signal_status']} (Score: {result['signal_score']})")
        print(f"     Setup: {result['setup_type']}")
        print(f"     RSI: {result['rsi']}")
        print(f"     ATR%: {result['atr_pct']}%")
        print(f"     Rel Volume: {result['rel_volume']}")
        print(f"     Uptrend: {result['uptrend']}")
        print(f"     R:R: {result['risk_reward']}")

        print(f"\n  📍 LEVELS:")
        print(f"     Entry: ${result['ideal_entry']}")
        print(f"     Stop: ${result['stop_loss']}")
        print(f"     Target 1: ${result['target_1']}")
        print(f"     Target 2: ${result['target_2']}")

        # Check why it might not qualify
        print(f"\n  🔍 CRITERIA CHECK:")
        c = config.SCREENING_CRITERIA

        checks = [
            ("Market Cap >= $5B", info.get('market_cap', 0) >= c['min_market_cap']),
            ("Avg Volume >= 2M", info.get('avg_volume', 0) >= c['min_avg_volume']),
            (f"RSI {c['min_rsi']}-{c['max_rsi']}", c['min_rsi'] <= result['rsi'] <= c['max_rsi']),
            (f"ATR {c['min_atr_pct']}-{c['max_atr_pct']}%", c['min_atr_pct'] <= result['atr_pct'] <= c['max_atr_pct']),
            ("Uptrend", result['uptrend']),
            ("R:R >= 2.0", result['risk_reward'] >= 2.0),
            ("Rel Volume >= 1.0", result['rel_volume'] >= c['min_rel_volume']),
        ]

        for name, passed in checks:
            status = "✓" if passed else "❌"
            print(f"     {status} {name}")

        # Would it generate a signal?
        is_buy = result['signal_status'] in ["STRONG BUY", "BUY"]
        print(f"\n  🎯 SIGNAL STATUS: {'YES - Would generate signal' if is_buy else 'NO - Does not qualify'}")


if __name__ == "__main__":
    debug_signals()
