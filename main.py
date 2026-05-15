"""Main Trading System - Entry point"""

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
    print("\n" + "=" * 60)
    print("RUNNING STOCK SCANNER")
    print("=" * 60)

    screener = StockScreener()
    results = screener.screen_stocks()

    qualified = results[results["qualified"]]
    print(f"\nFound {len(qualified)} qualified stocks:")

    if not qualified.empty:
        print(qualified[["symbol", "signal_score", "signal_status", "current_price",
                        "ideal_entry", "stop_loss", "target_1", "risk_reward"]].to_string())


def run_signals():
    """Generate trading signals"""
    print("\n" + "=" * 60)
    print("GENERATING SIGNALS")
    print("=" * 60)

    gen = SignalGenerator()
    signals = gen.generate_signals()
    alerts = AlertSystem()

    if signals:
        print(f"\nFound {len(signals)} signals:")
        print(gen.get_summary().to_string())

        # Send alert for top signal
        alerts.send_signal(signals[0])
    else:
        print("No signals found")


def run_analysis(symbol: str):
    """Analyze single stock"""
    print("\n" + "=" * 60)
    print(f"ANALYZING {symbol}")
    print("=" * 60)

    fetcher = DataFetcher()
    analyzer = TechnicalAnalyzer()

    df = fetcher.get_stock_data(symbol, "6mo")
    if df.empty:
        print(f"No data for {symbol}")
        return

    result = analyzer.analyze_stock(df, symbol)

    print(f"\n{symbol} Analysis:")
    for k, v in result.items():
        print(f"  {k}: {v}")


def run_backtest(symbols: list, period: str = "1y"):
    """Run backtest"""
    print("\n" + "=" * 60)
    print("RUNNING BACKTEST")
    print("=" * 60)

    bt = Backtester()
    results = bt.run(symbols, period)
    bt.print_results(results)


def run_portfolio():
    """Show portfolio status"""
    print("\n" + "=" * 60)
    print("PORTFOLIO STATUS")
    print("=" * 60)

    broker = BrokerAPI(paper=True)
    pm = PositionManager()

    account = broker.get_account()
    print(f"\nAccount Status: {account.get('status')}")
    print(f"Cash: ${account.get('cash', 0):,.2f}")
    print(f"Buying Power: ${account.get('buying_power', 0):,.2f}")

    positions = broker.get_positions()
    if positions:
        print(f"\nOpen Positions: {len(positions)}")
        for p in positions:
            print(f"  {p['symbol']}: {p['qty']} shares, P&L: ${p.get('pnl', 0):.2f}")
    else:
        print("\nNo open positions")


def main():
    parser = argparse.ArgumentParser(description="Swing Trading System")
    parser.add_argument("command", choices=["scan", "signals", "analyze", "backtest", "portfolio"],
                       help="Command to run")
    parser.add_argument("--symbol", "-s", help="Stock symbol for analysis")
    parser.add_argument("--period", "-p", default="1y", help="Backtest period")

    args = parser.parse_args()

    print(f"\n🎯 Swing Trading System - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
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
