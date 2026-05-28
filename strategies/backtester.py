"""Backtester - Tests strategy on historical data"""

import pandas as pd
import numpy as np
from typing import List, Dict, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from data_fetcher import DataFetcher
from technical_analyzer import TechnicalAnalyzer
import config


@dataclass
class Trade:
    """Backtest trade"""
    symbol: str
    entry_date: datetime
    entry_price: float
    exit_date: datetime = None
    exit_price: float = 0
    shares: int = 0
    pnl: float = 0
    pnl_pct: float = 0
    exit_reason: str = ""


@dataclass
class Results:
    """Backtest results"""
    total_trades: int = 0
    wins: int = 0
    losses: int = 0
    win_rate: float = 0
    total_pnl: float = 0
    total_return: float = 0
    avg_win: float = 0
    avg_loss: float = 0
    profit_factor: float = 0
    max_drawdown: float = 0
    trades: List[Trade] = field(default_factory=list)


class Backtester:
    """Backtests trading strategy"""

    def __init__(self, capital: float = None):
        self.fetcher = DataFetcher()
        self.analyzer = TechnicalAnalyzer()
        self.capital = capital or config.ACCOUNT_SIZE
        self.risk = config.RISK_PER_TRADE

    def run(self, symbols: List[str], period: str = "1y") -> Results:
        """Run backtest"""
        all_trades = []

        print(f"Backtesting {len(symbols)} symbols...")
        for symbol in symbols:
            try:
                trades = self._backtest_symbol(symbol, period)
                all_trades.extend(trades)
            except:
                continue

        print(f"Completed: {len(all_trades)} trades")
        return self._calc_results(all_trades)

    def _backtest_symbol(self, symbol: str, period: str) -> List[Trade]:
        """Backtest single symbol"""
        df = self.fetcher.get_stock_data(symbol, period)
        if df.empty or len(df) < 60:
            return []

        df = self.analyzer.calculate_indicators(df)

        trades = []
        in_trade = False
        trade = None

        for i in range(50, len(df) - 1):
            curr = df.iloc[i]
            next_bar = df.iloc[i + 1]

            if not in_trade:
                if self._check_entry(curr):
                    entry = next_bar["open"]
                    atr = curr["atr"]
                    stop = entry - (1.75 * atr)
                    target = entry + (2.5 * atr)

                    risk_per_share = entry - stop
                    shares = int((self.capital * self.risk) / risk_per_share)

                    if shares > 0:
                        trade = Trade(
                            symbol=symbol,
                            entry_date=next_bar.name,
                            entry_price=entry,
                            shares=shares,
                        )
                        trade.stop = stop
                        trade.target = target
                        in_trade = True
            else:
                exit_price, reason = self._check_exit(trade, next_bar)
                if exit_price:
                    trade.exit_date = next_bar.name
                    trade.exit_price = exit_price
                    trade.exit_reason = reason
                    trade.pnl = (exit_price - trade.entry_price) * trade.shares
                    trade.pnl_pct = ((exit_price - trade.entry_price) / trade.entry_price) * 100

                    trades.append(trade)
                    in_trade = False
                    trade = None

        return trades

    def _check_entry(self, curr) -> bool:
        """Check entry conditions"""
        return all([
            curr["close"] > curr["ema_50"],
            abs(curr["dist_ema20_pct"]) < 2.5,
            40 <= curr["rsi"] <= 60,
            curr["rel_volume"] >= 0.8,
            2.0 <= curr["atr_pct"] <= 6.0,
            curr["close"] > curr["open"],
        ])

    def _check_exit(self, trade, bar) -> Tuple[float, str]:
        """Check exit conditions"""
        if bar["low"] <= trade.stop:
            return trade.stop, "STOP"
        if bar["high"] >= trade.target:
            return trade.target, "TARGET"
        return None, ""

    def _calc_results(self, trades: List[Trade]) -> Results:
        """Calculate results"""
        r = Results()
        if not trades:
            return r

        r.trades = trades
        r.total_trades = len(trades)

        wins = [t for t in trades if t.pnl > 0]
        losses = [t for t in trades if t.pnl <= 0]

        r.wins = len(wins)
        r.losses = len(losses)
        r.win_rate = (r.wins / r.total_trades * 100) if r.total_trades else 0
        r.total_pnl = sum(t.pnl for t in trades)
        r.total_return = (r.total_pnl / self.capital) * 100

        if wins:
            r.avg_win = sum(t.pnl for t in wins) / len(wins)
        if losses:
            r.avg_loss = sum(t.pnl for t in losses) / len(losses)

        gross_profit = sum(t.pnl for t in wins) if wins else 0
        gross_loss = abs(sum(t.pnl for t in losses)) if losses else 1
        r.profit_factor = gross_profit / gross_loss if gross_loss else 0

        # Max drawdown
        equity = self.capital
        peak = equity
        max_dd = 0
        for t in sorted(trades, key=lambda x: x.exit_date or x.entry_date):
            equity += t.pnl
            if equity > peak:
                peak = equity
            dd = (peak - equity) / peak * 100
            if dd > max_dd:
                max_dd = dd
        r.max_drawdown = max_dd

        return r

    def print_results(self, r: Results):
        """Print results"""
        print("\n" + "=" * 50)
        print("BACKTEST RESULTS")
        print("=" * 50)
        print(f"Total Trades: {r.total_trades}")
        print(f"Wins: {r.wins} | Losses: {r.losses}")
        print(f"Win Rate: {r.win_rate:.1f}%")
        print(f"Total P&L: ${r.total_pnl:,.2f}")
        print(f"Total Return: {r.total_return:.2f}%")
        print(f"Avg Win: ${r.avg_win:,.2f}")
        print(f"Avg Loss: ${r.avg_loss:,.2f}")
        print(f"Profit Factor: {r.profit_factor:.2f}")
        print(f"Max Drawdown: {r.max_drawdown:.2f}%")
        print("=" * 50)


if __name__ == "__main__":
    bt = Backtester()
    results = bt.run(["NVDA", "AMD", "AAPL", "MSFT", "META"], period="1y")
    bt.print_results(results)
