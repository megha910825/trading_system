#!/usr/bin/env python3
"""
Main Trading System - Global Markets Version
Supports: US, Germany (XETRA), India (NSE)
"""

import argparse
from datetime import datetime
import sys

# Import modules
from technical_analyzer import TechnicalAnalyzer
from position_manager import PositionManager
from alert_system import AlertSystem
from broker_api import BrokerAPI
from backtester import Backtester

# Global market modules
from market_config import MARKETS, get_market_status, get_all_stocks
from global_data_fetcher import GlobalDataFetcher
from global_universe_manager import GlobalUniverseManager
from global_signal_generator import GlobalSignalGenerator

import config


def print_header():
    """Print system header"""
    print(f"""
╔══════════════════════════════════════════════════════════════════╗
║          🌍 GLOBAL SWING TRADING SYSTEM                          ║
║          Markets: US 🇺🇸 | Germany 🇩🇪 | India 🇮🇳                  ║
╠══════════════════════════════════════════════════════════════════╣
║  Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}                                          ║
║  Account: ${config.ACCOUNT_SIZE:,} | Target: {config.MONTHLY_TARGET*100}%/month              ║
╚══════════════════════════════════════════════════════════════════╝
""")


def show_market_status():
    """Show status of all markets"""
    print("\n📊 MARKET STATUS:")
    print("-" * 50)

    status = get_market_status()
    for code, stat in status.items():
        market = MARKETS[code]
        print(f"  {market.name:15} ({market.currency}): {stat}")


# ============================================================
# SIGNAL COMMANDS
# ============================================================

def run_global_signals(markets: list = None):
    """Generate signals for all markets"""
    if markets is None:
        markets = ["US", "DE", "IN"]

    print_header()
    show_market_status()

    gen = GlobalSignalGenerator()
    signals = gen.generate_signals(markets=markets)

    # Print results
    gen.print_all_signals()

    # Send alert for top signal
    alerts = AlertSystem()
    for market, market_signals in signals.items():
        if market_signals:
            top_signal = market_signals[0]
            print(gen.format_alert(top_signal))
            alerts.send_signal(top_signal)
            break  # Only alert top signal


def run_us_signals():
    """Generate US-only signals (backward compatible)"""
    run_global_signals(markets=["US"])


def run_german_signals():
    """Generate German-only signals"""
    run_global_signals(markets=["DE"])


def run_indian_signals():
    """Generate Indian-only signals"""
    run_global_signals(markets=["IN"])


# ============================================================
# ANALYSIS COMMANDS
# ============================================================

def run_analysis(symbol: str):
    """Analyze a single stock from any market"""
    print_header()

    print(f"\n{'='*60}")
    print(f"ANALYZING: {symbol}")
    print(f"{'='*60}")

    fetcher = GlobalDataFetcher()
    analyzer = TechnicalAnalyzer()

    # Detect market
    market = fetcher.detect_market(symbol)
    market_info = MARKETS[market]

    print(f"\nMarket: {market_info.name} ({market_info.currency})")
    print(f"Trading Hours: {market_info.open_time} - {market_info.close_time} ({market_info.timezone})")

    # Get data
    df = fetcher.get_stock_data(symbol, "6mo")
    if df.empty:
        print(f"\n❌ No data available for {symbol}")
        return

    # Get info
    info = fetcher.get_stock_info(symbol)
    print(f"\nCompany: {info.get('name', 'N/A')}")
    print(f"Sector: {info.get('sector', 'N/A')}")
    print(f"Market Cap: {info.get('market_cap', 0):,.0f} {market_info.currency}")

    # Analyze
    result = analyzer.analyze_stock(df, symbol)

    if "error" in result:
        print(f"\n❌ Analysis error: {result['error']}")
        return

    # Currency symbol
    curr_symbol = {"USD": "$", "EUR": "€", "INR": "₹"}.get(market_info.currency, "$")

    print(f"\n{'='*50}")
    print("ANALYSIS RESULTS")
    print(f"{'='*50}")

    print(f"\n📊 Current Status:")
    print(f"   Price: {curr_symbol}{result['current_price']:,.2f}")
    print(f"   Signal: {result['signal_status']} (Score: {result['signal_score']}/100)")
    print(f"   Setup: {result['setup_type']}")
    print(f"   Trend: {'BULLISH ✓' if result['uptrend'] else 'BEARISH ✗'}")

    print(f"\n💰 Trade Setup:")
    print(f"   Entry: {curr_symbol}{result['ideal_entry']:,.2f}")
    print(f"   Stop Loss: {curr_symbol}{result['stop_loss']:,.2f} (-{result.get('stop_loss_pct', 0):.1f}%)")
    print(f"   Target 1: {curr_symbol}{result['target_1']:,.2f} (+{result.get('target_1_pct', 0):.1f}%)")
    print(f"   Target 2: {curr_symbol}{result['target_2']:,.2f} (+{result.get('target_2_pct', 0):.1f}%)")

    print(f"\n📈 Indicators:")
    print(f"   RSI: {result['rsi']:.1f}")
    print(f"   ATR%: {result['atr_pct']:.2f}%")
    print(f"   Rel Volume: {result.get('rel_volume', 0):.2f}")
    print(f"   R:R (T1): {result['risk_reward']:.2f}")
    print(f"   R:R (T2): {result.get('risk_reward_t2', 0):.2f}")


# ============================================================
# UNIVERSE COMMANDS
# ============================================================

def run_universe_update(markets: list = None, quick: bool = False, top_n: int = 20):
    """Update stock universe"""
    print_header()

    if markets is None:
        markets = ["US", "DE", "IN"]

    um = GlobalUniverseManager()

    if quick:
        um.quick_update(markets=markets, top_n_per_market=min(top_n, 15))
    else:
        um.update_universe(markets=markets, top_n_per_market=top_n)


def show_universe(market: str = None):
    """Show current trading universe"""
    print_header()

    um = GlobalUniverseManager()
    universe = um.load_universe()

    print("\n" + "=" * 60)
    print("CURRENT TRADING UNIVERSE")
    print("=" * 60)

    if not universe:
        print("\nNo universe found. Run 'python main.py update-universe' first.")
        return

    total = 0
    for mkt, symbols in universe.items():
        if market and mkt != market:
            continue

        market_info = MARKETS[mkt]
        print(f"\n📊 {market_info.name} ({market_info.currency}) - {len(symbols)} stocks:")

        for i, symbol in enumerate(symbols):
            print(f"  {i+1:2}. {symbol}")

        total += len(symbols)

    print(f"\n{'='*60}")
    print(f"Total: {total} stocks")


def show_universe_report():
    """Show detailed universe report"""
    print_header()

    um = GlobalUniverseManager()
    um.load_universe()

    from pathlib import Path
    rankings_file = Path(__file__).parent / "data" / "global_rankings.csv"

    if rankings_file.exists():
        import pandas as pd
        um.ranked_stocks = pd.read_csv(rankings_file)

    um.print_global_report()


# ============================================================
# SCANNER COMMANDS
# ============================================================

def run_scanner(markets: list = None):
    """Run full stock scanner"""
    print_header()

    if markets is None:
        markets = ["US", "DE", "IN"]

    print("\n" + "=" * 60)
    print("RUNNING GLOBAL STOCK SCANNER")
    print("=" * 60)

    um = GlobalUniverseManager()
    um.rank_stocks(markets=markets, top_n_per_market=30)

    # Show top stocks
    for market in markets:
        df = um.get_market_report(market)
        if df.empty:
            continue

        print(f"\n📊 {MARKETS[market].name} - Top 10:")
        print(df.head(10)[["symbol", "name", "price", "composite_score",
                          "momentum_20d", "returns_3m"]].to_string(index=False))


# ============================================================
# BACKTEST COMMANDS
# ============================================================

def run_backtest(symbols: list = None, period: str = "1y"):
    """Run backtest"""
    print_header()

    print("\n" + "=" * 60)
    print("RUNNING BACKTEST")
    print("=" * 60)

    if symbols is None:
        # Use top stocks from universe
        um = GlobalUniverseManager()
        universe = um.load_universe()

        symbols = []
        for market, stocks in universe.items():
            symbols.extend(stocks[:5])  # Top 5 from each market

    bt = Backtester()
    results = bt.run(symbols, period)
    bt.print_results(results)


# ============================================================
# PORTFOLIO COMMANDS
# ============================================================

def run_portfolio():
    """Show portfolio status"""
    print_header()

    print("\n" + "=" * 60)
    print("PORTFOLIO STATUS")
    print("=" * 60)

    broker = BrokerAPI(paper=True)

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


# ============================================================
# MAIN CLI
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="Global Swing Trading System - US, Germany, India",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py signals                    # Signals from all markets
  python main.py signals --market US        # US signals only
  python main.py signals --market DE        # German signals only
  python main.py signals --market IN        # Indian signals only

  python main.py analyze -s NVDA            # Analyze US stock
  python main.py analyze -s SAP.DE          # Analyze German stock
  python main.py analyze -s TCS.NS          # Analyze Indian stock

  python main.py update-universe            # Update all markets
  python main.py quick-update               # Quick update
  python main.py universe                   # Show universe
  python main.py universe-report            # Detailed report

  python main.py scan                       # Scan all markets
  python main.py backtest                   # Run backtest
  python main.py portfolio                  # Portfolio status
        """
    )

    parser.add_argument(
        "command",
        choices=[
            "signals", "scan", "analyze", "backtest", "portfolio",
            "update-universe", "quick-update", "universe", "universe-report",
            "status"
        ],
        help="Command to run"
    )

    parser.add_argument("--symbol", "-s", help="Stock symbol for analysis")
    parser.add_argument("--market", "-m", choices=["US", "DE", "IN"],
                       help="Specific market (US, DE, IN)")
    parser.add_argument("--markets", nargs="+", default=["US", "DE", "IN"],
                       help="Markets to include")
    parser.add_argument("--period", "-p", default="1y", help="Backtest period")
    parser.add_argument("--top", "-n", type=int, default=20,
                       help="Top stocks per market")

    args = parser.parse_args()

    # Determine markets
    if args.market:
        markets = [args.market]
    else:
        markets = args.markets

    # Execute command
    if args.command == "signals":
        run_global_signals(markets=markets)

    elif args.command == "scan":
        run_scanner(markets=markets)

    elif args.command == "analyze":
        if args.symbol:
            run_analysis(args.symbol.upper())
        else:
            print("Error: Please provide --symbol (-s)")
            print("Examples:")
            print("  python main.py analyze -s NVDA      # US stock")
            print("  python main.py analyze -s SAP.DE    # German stock")
            print("  python main.py analyze -s TCS.NS    # Indian stock")

    elif args.command == "backtest":
        run_backtest(period=args.period)

    elif args.command == "portfolio":
        run_portfolio()

    elif args.command == "update-universe":
        run_universe_update(markets=markets, quick=False, top_n=args.top)

    elif args.command == "quick-update":
        run_universe_update(markets=markets, quick=True, top_n=args.top)

    elif args.command == "universe":
        show_universe(market=args.market)

    elif args.command == "universe-report":
        show_universe_report()

    elif args.command == "status":
        print_header()
        show_market_status()


if __name__ == "__main__":
    main()
