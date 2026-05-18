#!/usr/bin/env python3
"""
Backtester - Tests trading strategy on historical data
Enhanced for multi-market support
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import List, Dict, Optional
import json
from pathlib import Path

from global_data_fetcher import GlobalDataFetcher
from technical_analyzer import TechnicalAnalyzer
from market_config import MARKETS
import config


@dataclass
class Trade:
    """Represents a single trade"""
    symbol: str
    market: str
    currency: str
    entry_date: datetime
    entry_price: float
    exit_date: Optional[datetime] = None
    exit_price: Optional[float] = None
    shares: int = 0
    stop_loss: float = 0
    target_1: float = 0
    target_2: float = 0
    pnl: float = 0
    pnl_pct: float = 0
    exit_reason: str = ""
    hold_days: int = 0


@dataclass
class BacktestResults:
    """Backtest results summary"""
    # Basic stats
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    win_rate: float = 0

    # P&L
    total_pnl: float = 0
    total_pnl_pct: float = 0
    avg_win: float = 0
    avg_loss: float = 0
    largest_win: float = 0
    largest_loss: float = 0

    # Ratios
    profit_factor: float = 0
    avg_rr_ratio: float = 0

    # Risk
    max_drawdown: float = 0
    max_drawdown_pct: float = 0

    # Time
    avg_hold_days: float = 0

    # By market
    results_by_market: Dict = field(default_factory=dict)

    # Trade list
    trades: List[Trade] = field(default_factory=list)

    # Equity curve
    equity_curve: List[float] = field(default_factory=list)


class Backtester:
    """
    Backtests the swing trading strategy on historical data
    """

    def __init__(self, capital: float = None, risk_per_trade: float = None):
        self.initial_capital = capital or config.ACCOUNT_SIZE
        self.risk_per_trade = risk_per_trade or config.RISK_PER_TRADE
        self.fetcher = GlobalDataFetcher()
        self.analyzer = TechnicalAnalyzer()
        self.exit_rules = config.EXIT_RULES

    def run(self, symbols: List[str], period: str = "1y",
            verbose: bool = True) -> BacktestResults:
        """
        Run backtest on given symbols

        Args:
            symbols: List of stock symbols
            period: Historical period (6mo, 1y, 2y, etc.)
            verbose: Print progress

        Returns:
            BacktestResults object
        """
        if verbose:
            print("\n" + "=" * 60)
            print("BACKTESTING STRATEGY")
            print("=" * 60)
            print(f"Period: {period}")
            print(f"Symbols: {len(symbols)}")
            print(f"Initial Capital: €{self.initial_capital:,.2f}")
            print(f"Risk per Trade: {self.risk_per_trade * 100}%")

        all_trades = []
        equity = self.initial_capital
        equity_curve = [equity]
        max_equity = equity
        max_drawdown = 0

        for i, symbol in enumerate(symbols):
            if verbose:
                print(f"\nProcessing {symbol} ({i+1}/{len(symbols)})...")

            trades = self._backtest_symbol(symbol, period)

            for trade in trades:
                equity += trade.pnl
                equity_curve.append(equity)

                # Track drawdown
                if equity > max_equity:
                    max_equity = equity
                drawdown = (max_equity - equity) / max_equity * 100
                if drawdown > max_drawdown:
                    max_drawdown = drawdown

                all_trades.append(trade)

                if verbose and trade.pnl != 0:
                    status = "✅" if trade.pnl > 0 else "❌"
                    print(f"  {status} {trade.symbol}: {trade.pnl_pct:+.1f}% "
                          f"({trade.exit_reason}, {trade.hold_days}d)")

        # Calculate results
        results = self._calculate_results(all_trades, equity_curve, max_drawdown)

        if verbose:
            self.print_results(results)

        return results

    def _backtest_symbol(self, symbol: str, period: str) -> List[Trade]:
        """Backtest a single symbol"""
        trades = []

        # Get historical data
        df = self.fetcher.get_stock_data(symbol, period)
        if df.empty or len(df) < 100:
            return trades

        market = self.fetcher.detect_market(symbol)
        currency = MARKETS[market].currency

        # Calculate indicators
        df = self.analyzer.calculate_indicators(df)

        # Simulate trading
        in_trade = False
        trade = None

        for i in range(50, len(df) - 1):
            current = df.iloc[i]
            next_day = df.iloc[i + 1]
            date = df.index[i]

            if not in_trade:
                # Check for entry signal
                signal = self._check_entry_signal(df.iloc[:i+1])

                if signal:
                    # Calculate position size
                    entry_price = current['close']
                    atr = current['atr']
                    stop_loss = entry_price - (self.exit_rules['stop_loss_atr_mult'] * atr)
                    target_1 = entry_price + (self.exit_rules['target_1_atr_mult'] * atr)
                    target_2 = entry_price + (self.exit_rules['target_2_atr_mult'] * atr)

                    risk_per_share = entry_price - stop_loss
                    if risk_per_share <= 0:
                        continue

                    risk_amount = self.initial_capital * self.risk_per_trade
                    shares = int(risk_amount / risk_per_share)

                    if shares <= 0:
                        continue

                    trade = Trade(
                        symbol=symbol,
                        market=market,
                        currency=currency,
                        entry_date=date,
                        entry_price=entry_price,
                        shares=shares,
                        stop_loss=stop_loss,
                        target_1=target_1,
                        target_2=target_2,
                    )
                    in_trade = True

            else:
                # Check for exit
                high = next_day['high']
                low = next_day['low']
                close = next_day['close']

                exit_price = None
                exit_reason = None

                # Check stop loss
                if low <= trade.stop_loss:
                    exit_price = trade.stop_loss
                    exit_reason = "STOP_LOSS"

                # Check target 1 (simplified - full exit at T1)
                elif high >= trade.target_1:
                    exit_price = trade.target_1
                    exit_reason = "TARGET_1"

                # Check max hold days
                hold_days = (df.index[i + 1] - trade.entry_date).days
                if hold_days >= self.exit_rules['max_hold_days']:
                    exit_price = close
                    exit_reason = "TIME_EXIT"

                # Execute exit
                if exit_price:
                    trade.exit_date = df.index[i + 1]
                    trade.exit_price = exit_price
                    trade.hold_days = hold_days
                    trade.exit_reason = exit_reason
                    trade.pnl = (exit_price - trade.entry_price) * trade.shares
                    trade.pnl_pct = ((exit_price - trade.entry_price) / trade.entry_price) * 100

                    trades.append(trade)
                    in_trade = False
                    trade = None

        return trades

    def _check_entry_signal(self, df: pd.DataFrame) -> bool:
        """Check if current bar has entry signal"""
        if len(df) < 3:
            return False

        current = df.iloc[-1]

        # Basic conditions
        conditions = [
            current['close'] > current['ema_50'],  # Above 50 EMA (uptrend)
            30 <= current['rsi'] <= 70,            # RSI not extreme
            current['atr'] > 0,                     # Valid ATR
        ]

        # Pullback to EMA20
        dist_from_ema20 = abs((current['close'] - current['ema_20']) / current['close'] * 100)
        conditions.append(dist_from_ema20 < 5)  # Within 5% of EMA20

        return all(conditions)

    def _calculate_results(self, trades: List[Trade],
                          equity_curve: List[float],
                          max_drawdown: float) -> BacktestResults:
        """Calculate backtest results"""
        results = BacktestResults()
        results.trades = trades
        results.equity_curve = equity_curve
        results.max_drawdown_pct = max_drawdown

        if not trades:
            return results

        # Basic counts
        results.total_trades = len(trades)
        results.winning_trades = len([t for t in trades if t.pnl > 0])
        results.losing_trades = len([t for t in trades if t.pnl < 0])
        results.win_rate = (results.winning_trades / results.total_trades) * 100

        # P&L
        results.total_pnl = sum(t.pnl for t in trades)
        results.total_pnl_pct = (results.total_pnl / self.initial_capital) * 100

        wins = [t.pnl for t in trades if t.pnl > 0]
        losses = [t.pnl for t in trades if t.pnl < 0]

        results.avg_win = np.mean(wins) if wins else 0
        results.avg_loss = np.mean(losses) if losses else 0
        results.largest_win = max(wins) if wins else 0
        results.largest_loss = min(losses) if losses else 0

        # Profit factor
        gross_profit = sum(wins) if wins else 0
        gross_loss = abs(sum(losses)) if losses else 1
        results.profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0

        # Hold time
        results.avg_hold_days = np.mean([t.hold_days for t in trades])

        # Results by market
        for market in ["US", "DE", "IN"]:
            market_trades = [t for t in trades if t.market == market]
            if market_trades:
                market_wins = len([t for t in market_trades if t.pnl > 0])
                market_pnl = sum(t.pnl for t in market_trades)
                results.results_by_market[market] = {
                    "trades": len(market_trades),
                    "wins": market_wins,
                    "win_rate": (market_wins / len(market_trades)) * 100,
                    "total_pnl": market_pnl,
                }

        return results

    def print_results(self, results: BacktestResults):
        """Print backtest results"""
        print("\n" + "=" * 60)
        print("BACKTEST RESULTS")
        print("=" * 60)

        print(f"\n📊 OVERVIEW:")
        print(f"   Initial Capital: €{self.initial_capital:,.2f}")
        print(f"   Final Capital: €{self.initial_capital + results.total_pnl:,.2f}")
        print(f"   Total P&L: €{results.total_pnl:,.2f} ({results.total_pnl_pct:+.2f}%)")

        print(f"\n📈 TRADE STATISTICS:")
        print(f"   Total Trades: {results.total_trades}")
        print(f"   Winning Trades: {results.winning_trades}")
        print(f"   Losing Trades: {results.losing_trades}")
        print(f"   Win Rate: {results.win_rate:.1f}%")

        print(f"\n💰 PROFIT/LOSS:")
        print(f"   Average Win: €{results.avg_win:,.2f}")
        print(f"   Average Loss: €{results.avg_loss:,.2f}")
        print(f"   Largest Win: €{results.largest_win:,.2f}")
        print(f"   Largest Loss: €{results.largest_loss:,.2f}")
        print(f"   Profit Factor: {results.profit_factor:.2f}")

        print(f"\n⚠️ RISK:")
        print(f"   Max Drawdown: {results.max_drawdown_pct:.2f}%")

        print(f"\n⏱️ TIME:")
        print(f"   Avg Hold Days: {results.avg_hold_days:.1f}")

        # Results by market
        if results.results_by_market:
            print(f"\n🌍 BY MARKET:")
            for market, data in results.results_by_market.items():
                flag = {"US": "🇺🇸", "DE": "🇩🇪", "IN": "🇮🇳"}.get(market, "🌐")
                print(f"   {flag} {market}: {data['trades']} trades, "
                      f"{data['win_rate']:.1f}% win rate, €{data['total_pnl']:,.2f}")

        # Exit reasons
        if results.trades:
            print(f"\n📤 EXIT REASONS:")
            reasons = {}
            for t in results.trades:
                reasons[t.exit_reason] = reasons.get(t.exit_reason, 0) + 1
            for reason, count in sorted(reasons.items(), key=lambda x: x[1], reverse=True):
                pct = (count / results.total_trades) * 100
                print(f"   {reason}: {count} ({pct:.1f}%)")

        print("\n" + "=" * 60)

    def save_results(self, results: BacktestResults, filename: str = None):
        """Save results to file"""
        if filename is None:
            filename = f"backtest_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        filepath = config.DATA_DIR / filename

        data = {
            "timestamp": datetime.now().isoformat(),
            "initial_capital": self.initial_capital,
            "risk_per_trade": self.risk_per_trade,
            "total_trades": results.total_trades,
            "win_rate": results.win_rate,
            "total_pnl": results.total_pnl,
            "total_pnl_pct": results.total_pnl_pct,
            "profit_factor": results.profit_factor,
            "max_drawdown_pct": results.max_drawdown_pct,
            "avg_hold_days": results.avg_hold_days,
            "results_by_market": results.results_by_market,
            "trades": [
                {
                    "symbol": t.symbol,
                    "market": t.market,
                    "entry_date": t.entry_date.isoformat() if t.entry_date else None,
                    "exit_date": t.exit_date.isoformat() if t.exit_date else None,
                    "entry_price": t.entry_price,
                    "exit_price": t.exit_price,
                    "pnl": t.pnl,
                    "pnl_pct": t.pnl_pct,
                    "exit_reason": t.exit_reason,
                    "hold_days": t.hold_days,
                }
                for t in results.trades
            ]
        }

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"✓ Results saved to {filepath}")
        return filepath

    def run_market_comparison(self, period: str = "1y") -> Dict:
        """Run backtest comparing all markets"""
        print("\n" + "=" * 60)
        print("MARKET COMPARISON BACKTEST")
        print("=" * 60)

        from market_config import US_STOCKS, GERMAN_STOCKS, INDIAN_STOCKS

        market_results = {}

        # Germany
        print("\n🇩🇪 Testing German Stocks...")
        de_symbols = GERMAN_STOCKS[:15]
        de_results = self.run(de_symbols, period, verbose=False)
        market_results["DE"] = de_results

        # US
        print("\n🇺🇸 Testing US Stocks...")
        us_symbols = US_STOCKS[:15]
        us_results = self.run(us_symbols, period, verbose=False)
        market_results["US"] = us_results

        # India
        print("\n🇮🇳 Testing Indian Stocks...")
        in_symbols = INDIAN_STOCKS[:15]
        in_results = self.run(in_symbols, period, verbose=False)
        market_results["IN"] = in_results

        # Print comparison
        print("\n" + "=" * 60)
        print("MARKET COMPARISON RESULTS")
        print("=" * 60)

        print(f"\n{'Market':<10} {'Trades':<10} {'Win Rate':<12} {'P&L':<15} {'Profit Factor':<15}")
        print("-" * 60)

        for market, results in market_results.items():
            flag = {"US": "🇺🇸", "DE": "🇩🇪", "IN": "🇮🇳"}.get(market, "🌐")
            print(f"{flag} {market:<7} {results.total_trades:<10} "
                  f"{results.win_rate:<12.1f} €{results.total_pnl:<14,.2f} "
                  f"{results.profit_factor:<15.2f}")

        return market_results


# ============================================================
# MAIN / CLI
# ============================================================

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Backtester")
    parser.add_argument("command", nargs="?", default="run",
                       choices=["run", "compare", "german", "us", "india"],
                       help="Command to run")
    parser.add_argument("--period", "-p", default="1y", help="Backtest period")
    parser.add_argument("--capital", "-c", type=float, default=50000, help="Initial capital")
    parser.add_argument("--save", "-s", action="store_true", help="Save results")

    args = parser.parse_args()

    bt = Backtester(capital=args.capital)

    if args.command == "run":
        # Use current universe
        from global_universe_manager import GlobalUniverseManager
        um = GlobalUniverseManager()
        universe = um.load_universe()

        symbols = []
        for market, stocks in universe.items():
            symbols.extend(stocks[:10])  # Top 10 from each

        if not symbols:
            # Fallback
            symbols = config.DEFAULT_UNIVERSE

        results = bt.run(symbols, args.period)

        if args.save:
            bt.save_results(results)

    elif args.command == "compare":
        bt.run_market_comparison(args.period)

    elif args.command == "german":
        from market_config import GERMAN_STOCKS
        results = bt.run(GERMAN_STOCKS[:20], args.period)
        if args.save:
            bt.save_results(results, "backtest_german.json")

    elif args.command == "us":
        from market_config import US_STOCKS
        results = bt.run(US_STOCKS[:20], args.period)
        if args.save:
            bt.save_results(results, "backtest_us.json")

    elif args.command == "india":
        from market_config import INDIAN_STOCKS
        results = bt.run(INDIAN_STOCKS[:20], args.period)
        if args.save:
            bt.save_results(results, "backtest_india.json")


if __name__ == "__main__":
    main()
