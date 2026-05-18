#!/usr/bin/env python3
"""
Backtester - Test trading strategies on historical data
Optimized for higher win rate
"""

import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict

# Handle imports gracefully
try:
    import config
except ImportError:
    config = None

try:
    from market_config import (
        MARKETS, get_market_flag, get_currency_symbol,
        US_STOCKS, GERMAN_STOCKS, INDIAN_STOCKS
    )
except ImportError:
    MARKETS = {}
    get_market_flag = lambda x: "🌐"
    get_currency_symbol = lambda x: "$"
    US_STOCKS = []
    GERMAN_STOCKS = []
    INDIAN_STOCKS = []


# ═══════════════════════════════════════════════════════════════
# DATA CLASSES
# ═══════════════════════════════════════════════════════════════

@dataclass
class TradeResult:
    """Result of a single backtest trade"""
    symbol: str
    market: str
    entry_date: str
    exit_date: str
    entry_price: float
    exit_price: float
    shares: int
    pnl: float
    pnl_pct: float
    status: str  # TARGET_1, TARGET_2, STOP_LOSS, TIME_EXIT
    days_held: int
    setup_type: str


@dataclass
class BacktestResults:
    """Complete backtest results"""
    # Settings
    period: str
    start_date: str
    end_date: str
    initial_capital: float

    # Results
    final_capital: float
    total_pnl: float
    total_pnl_pct: float

    # Trade statistics
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float

    # P&L statistics
    avg_win: float
    avg_loss: float
    largest_win: float
    largest_loss: float
    profit_factor: float

    # Risk metrics
    max_drawdown: float
    max_drawdown_pct: float
    avg_hold_days: float

    # Exit breakdown
    target_1_exits: int
    target_2_exits: int
    stop_loss_exits: int
    time_exits: int

    # By market
    results_by_market: Dict

    # Individual trades
    trades: List[TradeResult]


# ═══════════════════════════════════════════════════════════════
# SIMPLE DATA FETCHER (Fallback)
# ═══════════════════════════════════════════════════════════════

class SimpleDataFetcher:
    """Simple data fetcher using yfinance directly"""

    def __init__(self):
        try:
            import yfinance as yf
            self.yf = yf
        except ImportError:
            print("Warning: yfinance not installed. Run: pip install yfinance")
            self.yf = None

    def get_stock_data(self, symbol: str, period: str = "1y") -> pd.DataFrame:
        """Fetch stock data"""
        if self.yf is None:
            return pd.DataFrame()

        try:
            ticker = self.yf.Ticker(symbol)
            df = ticker.history(period=period)

            if df.empty:
                return df

            # Standardize column names
            df.columns = df.columns.str.lower()

            # Ensure required columns exist
            required = ['open', 'high', 'low', 'close', 'volume']
            if not all(col in df.columns for col in required):
                return pd.DataFrame()

            return df

        except Exception as e:
            print(f"Error fetching {symbol}: {e}")
            return pd.DataFrame()


# ═══════════════════════════════════════════════════════════════
# SIMPLE TECHNICAL ANALYZER (Fallback)
# ═══════════════════════════════════════════════════════════════

class SimpleTechnicalAnalyzer:
    """Simplified technical analyzer"""

    def __init__(self):
        self.ema_fast = 8
        self.ema_slow = 21
        self.ema_trend = 50
        self.rsi_period = 14
        self.atr_period = 14

    def calculate_ema(self, series: pd.Series, period: int) -> pd.Series:
        """Calculate EMA"""
        return series.ewm(span=period, adjust=False).mean()

    def calculate_rsi(self, series: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI"""
        delta = series.diff()
        gain = delta.where(delta > 0, 0).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    def calculate_atr(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate ATR"""
        tr1 = df['high'] - df['low']
        tr2 = abs(df['high'] - df['close'].shift())
        tr3 = abs(df['low'] - df['close'].shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        return tr.rolling(window=period).mean()

    def analyze_stock(self, df: pd.DataFrame, symbol: str = "") -> Dict:
        """Analyze a stock and generate signal"""
        result = {
            "symbol": symbol,
            "signal_status": "AVOID",
            "signal_score": 0,
            "setup_type": "NONE",
            "current_price": 0,
        }

        if df.empty or len(df) < 50:
            return result

        try:
            # Calculate indicators
            df = df.copy()
            df['ema_8'] = self.calculate_ema(df['close'], 8)
            df['ema_21'] = self.calculate_ema(df['close'], 21)
            df['ema_50'] = self.calculate_ema(df['close'], 50)
            df['rsi'] = self.calculate_rsi(df['close'], 14)
            df['atr'] = self.calculate_atr(df, 14)

            latest = df.iloc[-1]
            prev = df.iloc[-2]

            current_price = latest['close']
            atr = latest['atr']
            rsi = latest['rsi']

            result['current_price'] = round(current_price, 2)

            # Check trend
            ema_bullish = (
                latest['ema_8'] > latest['ema_21'] and
                latest['ema_21'] > latest['ema_50'] and
                current_price > latest['ema_50']
            )

            # Volume check
            avg_volume = df['volume'].tail(20).mean()
            volume_ratio = latest['volume'] / avg_volume if avg_volume > 0 else 1

            # Score calculation
            score = 0

            # Trend points (40 max)
            if ema_bullish:
                score += 25
            if current_price > latest['ema_50']:
                score += 15

            # RSI points (25 max)
            if 40 <= rsi <= 60:
                score += 25  # Ideal range
            elif 35 <= rsi <= 65:
                score += 15  # Acceptable
            elif rsi > 70:
                score -= 10  # Overbought penalty

            # Volume points (15 max)
            if volume_ratio > 1.2:
                score += 15
            elif volume_ratio > 0.8:
                score += 8

            # Pullback bonus (20 max)
            if ema_bullish and current_price <= latest['ema_21'] * 1.02:
                score += 20
                result['setup_type'] = "PULLBACK"
            elif ema_bullish:
                score += 10
                result['setup_type'] = "TREND"

            result['signal_score'] = max(0, min(100, score))

            # Determine signal
            if score >= 70:
                result['signal_status'] = "STRONG BUY"
            elif score >= 55:
                result['signal_status'] = "BUY"
            elif score >= 40:
                result['signal_status'] = "WATCH"
            else:
                result['signal_status'] = "AVOID"

            # Calculate levels (only for actionable signals)
            if result['signal_status'] in ['STRONG BUY', 'BUY']:
                # Entry at current price or slight pullback
                entry = current_price

                # Stop loss: 2x ATR below entry
                stop_loss = entry - (atr * 2.0)

                # Targets
                risk = entry - stop_loss
                target_1 = entry + (risk * 2.0)  # 2:1 R:R
                target_2 = entry + (risk * 3.5)  # 3.5:1 R:R

                result['entry'] = round(entry, 2)
                result['ideal_entry'] = round(entry, 2)
                result['stop_loss'] = round(stop_loss, 2)
                result['target_1'] = round(target_1, 2)
                result['target_2'] = round(target_2, 2)
                result['atr'] = round(atr, 2)
                result['rsi'] = round(rsi, 1)
                result['risk_reward'] = 2.0

        except Exception as e:
            result['error'] = str(e)

        return result


# ═══════════════════════════════════════════════════════════════
# BACKTESTER CLASS
# ═══════════════════════════════════════════════════════════════

class Backtester:
    """
    Strategy backtester with realistic trade simulation
    """

    def __init__(self):
        # Try to import advanced modules, fall back to simple versions
        try:
            from global_data_fetcher import GlobalDataFetcher
            self.fetcher = GlobalDataFetcher()
        except ImportError:
            self.fetcher = SimpleDataFetcher()

        try:
            from technical_analyzer import TechnicalAnalyzer
            self.analyzer = TechnicalAnalyzer()
        except ImportError:
            self.analyzer = SimpleTechnicalAnalyzer()

        # Default settings
        self.initial_capital = getattr(config, 'ACCOUNT_SIZE', 50000) if config else 50000
        self.risk_per_trade = getattr(config, 'RISK_PER_TRADE', 0.015) if config else 0.015
        self.max_positions = getattr(config, 'MAX_POSITIONS', 8) if config else 8

        # Exit rules
        default_exit_rules = {
            "stop_loss_atr_mult": 2.0,
            "target_1_atr_mult": 3.0,
            "target_2_atr_mult": 5.0,
            "max_hold_days": 15,
            "partial_exit_pct": 0.5,
        }
        self.exit_rules = getattr(config, 'EXIT_RULES', default_exit_rules) if config else default_exit_rules

        # Results storage
        self.trades: List[TradeResult] = []
        self.equity_curve: List[float] = []

    def get_period_data(self, symbol: str, period: str = "1y") -> pd.DataFrame:
        """Get historical data for backtesting"""
        return self.fetcher.get_stock_data(symbol, period)

    def generate_historical_signals(self, df: pd.DataFrame, symbol: str) -> List[Dict]:
        """
        Generate signals for historical data points
        Walk through the data and generate signals at each point
        """
        signals = []

        if df.empty or len(df) < 100:
            return signals

        # Need at least 100 days of data before generating signals
        lookback = 100

        for i in range(lookback, len(df) - 20):  # Leave 20 days for trade simulation
            # Get data up to this point (no future data)
            historical_df = df.iloc[:i+1].copy()

            # Analyze
            analysis = self.analyzer.analyze_stock(historical_df, symbol)

            # Only keep BUY or STRONG BUY signals
            if analysis.get('signal_status') in ['STRONG BUY', 'BUY']:
                analysis['signal_date'] = df.index[i] if hasattr(df.index[i], 'strftime') else str(df.index[i])
                analysis['signal_idx'] = i
                signals.append(analysis)

        return signals

    def simulate_trade(self, df: pd.DataFrame, entry_idx: int, signal: Dict) -> Dict:
        """
        Simulate a trade with REALISTIC execution
        """
        entry_price = signal.get('entry', signal.get('ideal_entry', signal.get('current_price')))
        stop_loss = signal.get('stop_loss', entry_price * 0.95)
        target_1 = signal.get('target_1', entry_price * 1.04)  # Lower target
        target_2 = signal.get('target_2', target_1 * 1.03)

        # Start from NEXT day (realistic - can't trade same day as signal)
        start_idx = entry_idx + 1

        if start_idx >= len(df):
            return {"status": "NO_FILL", "pnl": 0}

        # Check if entry price was achievable in the next few days
        entry_achieved = False
        actual_entry_price = entry_price
        actual_entry_idx = start_idx

        # Give 3 days to fill entry order
        for i in range(start_idx, min(start_idx + 3, len(df))):
            day = df.iloc[i]

            # Entry fills if price touches our entry level
            if day['low'] <= entry_price <= day['high']:
                entry_achieved = True
                actual_entry_idx = i
                actual_entry_price = entry_price
                break
            # Or if opens below our entry (better fill)
            elif day['open'] < entry_price:
                entry_achieved = True
                actual_entry_idx = i
                actual_entry_price = day['open']
                break
            # Or if opens above but comes back down (within 1%)
            elif day['low'] <= entry_price * 1.01:
                entry_achieved = True
                actual_entry_idx = i
                actual_entry_price = min(day['open'], entry_price * 1.01)
                break

        if not entry_achieved:
            return {"status": "NO_FILL", "pnl": 0}

        # Calculate position size
        risk_amount = self.initial_capital * self.risk_per_trade
        risk_per_share = abs(actual_entry_price - stop_loss)

        if risk_per_share <= 0:
            return {"status": "INVALID", "pnl": 0}

        shares = int(risk_amount / risk_per_share)
        if shares <= 0:
            return {"status": "INVALID", "pnl": 0}

        # Cap position size
        max_position = self.initial_capital * 0.25
        if shares * actual_entry_price > max_position:
            shares = int(max_position / actual_entry_price)

        position_value = actual_entry_price * shares

        partial_exit_done = False
        remaining_shares = shares
        total_pnl = 0
        current_stop = stop_loss

        max_hold_days = self.exit_rules.get('max_hold_days', 15)

        entry_date = df.index[actual_entry_idx] if hasattr(df.index[actual_entry_idx], 'strftime') else str(df.index[actual_entry_idx])
        exit_date = entry_date
        final_exit_price = actual_entry_price
        final_status = "TIME_EXIT"

        for i in range(actual_entry_idx + 1, min(actual_entry_idx + max_hold_days + 1, len(df))):
            day = df.iloc[i]
            days_held = i - actual_entry_idx
            exit_date = df.index[i] if hasattr(df.index[i], 'strftime') else str(df.index[i])

            # Check stop loss FIRST (most important)
            if day['low'] <= current_stop:
                exit_price = current_stop
                pnl = (exit_price - actual_entry_price) * remaining_shares
                total_pnl += pnl
                final_exit_price = exit_price
                final_status = "STOP_LOSS"

                return {
                    "status": final_status,
                    "entry_date": str(entry_date),
                    "exit_date": str(exit_date),
                    "entry_price": actual_entry_price,
                    "exit_price": final_exit_price,
                    "pnl": total_pnl,
                    "pnl_pct": (total_pnl / position_value) * 100 if position_value > 0 else 0,
                    "days_held": days_held,
                    "shares": shares,
                }

            # Check Target 1 (partial exit)
            if not partial_exit_done and day['high'] >= target_1:
                exit_shares = int(shares * 0.5)
                pnl = (target_1 - actual_entry_price) * exit_shares
                total_pnl += pnl
                remaining_shares -= exit_shares
                partial_exit_done = True

                # Move stop to breakeven
                current_stop = actual_entry_price

                if remaining_shares <= 0:
                    final_exit_price = target_1
                    final_status = "TARGET_1"
                    return {
                        "status": final_status,
                        "entry_date": str(entry_date),
                        "exit_date": str(exit_date),
                        "entry_price": actual_entry_price,
                        "exit_price": final_exit_price,
                        "pnl": total_pnl,
                        "pnl_pct": (total_pnl / position_value) * 100 if position_value > 0 else 0,
                        "days_held": days_held,
                        "shares": shares,
                    }

            # Check Target 2 (full exit)
            if partial_exit_done and day['high'] >= target_2:
                pnl = (target_2 - actual_entry_price) * remaining_shares
                total_pnl += pnl
                final_exit_price = target_2
                final_status = "TARGET_2"

                return {
                    "status": final_status,
                    "entry_date": str(entry_date),
                    "exit_date": str(exit_date),
                    "entry_price": actual_entry_price,
                    "exit_price": final_exit_price,
                    "pnl": total_pnl,
                    "pnl_pct": (total_pnl / position_value) * 100 if position_value > 0 else 0,
                    "days_held": days_held,
                    "shares": shares,
                }

        # Time exit - close at market
        final_idx = min(actual_entry_idx + max_hold_days, len(df) - 1)
        final_price = df.iloc[final_idx]['close']
        exit_date = df.index[final_idx] if hasattr(df.index[final_idx], 'strftime') else str(df.index[final_idx])

        pnl = (final_price - actual_entry_price) * remaining_shares
        total_pnl += pnl
        final_exit_price = final_price

        return {
            "status": "TIME_EXIT",
            "entry_date": str(entry_date),
            "exit_date": str(exit_date),
            "entry_price": actual_entry_price,
            "exit_price": final_exit_price,
            "pnl": total_pnl,
            "pnl_pct": (total_pnl / position_value) * 100 if position_value > 0 else 0,
            "days_held": max_hold_days,
            "shares": shares,
        }

    def backtest_symbol(self, symbol: str, period: str = "1y") -> List[Dict]:
        """Backtest a single symbol"""
        df = self.get_period_data(symbol, period)

        if df.empty or len(df) < 100:
            return []

        # Generate historical signals
        signals = self.generate_historical_signals(df, symbol)

        trades = []
        last_exit_idx = 0

        for signal in signals:
            entry_idx = signal.get('signal_idx', 0)

            # Don't enter if still in previous trade (5 day cooldown)
            if entry_idx <= last_exit_idx + 5:
                continue

            # Simulate the trade
            result = self.simulate_trade(df, entry_idx, signal)

            if result.get('status') not in ['NO_FILL', 'INVALID']:
                result['symbol'] = symbol
                result['setup_type'] = signal.get('setup_type', 'UNKNOWN')
                trades.append(result)

                # Update last exit
                last_exit_idx = entry_idx + result.get('days_held', 0)

        return trades

    def backtest_universe(
        self,
        symbols: List[str],
        period: str = "1y",
        market: str = None
    ) -> BacktestResults:
        """Backtest entire universe of stocks"""
        print(f"\n{'='*60}")
        print(f"BACKTESTING - {len(symbols)} symbols, Period: {period}")
        print(f"{'='*60}")

        all_trades = []

        for i, symbol in enumerate(symbols):
            print(f"  [{i+1}/{len(symbols)}] {symbol}...", end=" ", flush=True)

            try:
                trades = self.backtest_symbol(symbol, period)

                # Add market info
                for trade in trades:
                    trade['market'] = market or self._detect_market(symbol)

                all_trades.extend(trades)
                print(f"✓ {len(trades)} trades")

            except Exception as e:
                print(f"✗ Error: {e}")

        # Calculate results
        results = self._calculate_results(all_trades, period)

        return results

    def _detect_market(self, symbol: str) -> str:
        """Detect market from symbol"""
        if symbol.endswith('.DE'):
            return 'DE'
        elif symbol.endswith('.NS') or symbol.endswith('.BO'):
            return 'IN'
        return 'US'

    def _calculate_results(self, trades: List[Dict], period: str) -> BacktestResults:
        """Calculate comprehensive backtest results"""

        if not trades:
            return BacktestResults(
                period=period,
                start_date="",
                end_date="",
                initial_capital=self.initial_capital,
                final_capital=self.initial_capital,
                total_pnl=0,
                total_pnl_pct=0,
                total_trades=0,
                winning_trades=0,
                losing_trades=0,
                win_rate=0,
                avg_win=0,
                avg_loss=0,
                largest_win=0,
                largest_loss=0,
                profit_factor=0,
                max_drawdown=0,
                max_drawdown_pct=0,
                avg_hold_days=0,
                target_1_exits=0,
                target_2_exits=0,
                stop_loss_exits=0,
                time_exits=0,
                results_by_market={},
                trades=[],
            )

        # Basic stats
        total_pnl = sum(t['pnl'] for t in trades)
        final_capital = self.initial_capital + total_pnl

        wins = [t for t in trades if t['pnl'] > 0]
        losses = [t for t in trades if t['pnl'] <= 0]

        win_rate = (len(wins) / len(trades)) * 100 if trades else 0

        avg_win = sum(t['pnl'] for t in wins) / len(wins) if wins else 0
        avg_loss = sum(t['pnl'] for t in losses) / len(losses) if losses else 0

        gross_profit = sum(t['pnl'] for t in wins)
        gross_loss = abs(sum(t['pnl'] for t in losses))
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0

        # Exit breakdown
        target_1_exits = len([t for t in trades if t['status'] == 'TARGET_1'])
        target_2_exits = len([t for t in trades if t['status'] == 'TARGET_2'])
        stop_loss_exits = len([t for t in trades if t['status'] == 'STOP_LOSS'])
        time_exits = len([t for t in trades if t['status'] == 'TIME_EXIT'])

        # Drawdown calculation
        equity = self.initial_capital
        peak = equity
        max_dd = 0

        for trade in trades:
            equity += trade['pnl']
            if equity > peak:
                peak = equity
            dd = peak - equity
            if dd > max_dd:
                max_dd = dd

        max_dd_pct = (max_dd / self.initial_capital) * 100 if self.initial_capital > 0 else 0

        # By market
        results_by_market = {}
        for market in ['US', 'DE', 'IN']:
            market_trades = [t for t in trades if t.get('market') == market]
            if market_trades:
                market_wins = [t for t in market_trades if t['pnl'] > 0]
                results_by_market[market] = {
                    'trades': len(market_trades),
                    'wins': len(market_wins),
                    'win_rate': (len(market_wins) / len(market_trades)) * 100 if market_trades else 0,
                    'pnl': sum(t['pnl'] for t in market_trades),
                }

        # Convert trades to TradeResult objects
        trade_results = []
        for t in trades:
            trade_results.append(TradeResult(
                symbol=t.get('symbol', ''),
                market=t.get('market', 'US'),
                entry_date=t.get('entry_date', ''),
                exit_date=t.get('exit_date', ''),
                entry_price=t.get('entry_price', 0),
                exit_price=t.get('exit_price', 0),
                shares=t.get('shares', 0),
                pnl=t.get('pnl', 0),
                pnl_pct=t.get('pnl_pct', 0),
                status=t.get('status', ''),
                days_held=t.get('days_held', 0),
                setup_type=t.get('setup_type', ''),
            ))

        # Calculate average hold days
        avg_hold = sum(t['days_held'] for t in trades) / len(trades) if trades else 0

        return BacktestResults(
            period=period,
            start_date=trades[0].get('entry_date', '') if trades else '',
            end_date=trades[-1].get('exit_date', '') if trades else '',
            initial_capital=self.initial_capital,
            final_capital=final_capital,
            total_pnl=total_pnl,
            total_pnl_pct=(total_pnl / self.initial_capital) * 100 if self.initial_capital > 0 else 0,
            total_trades=len(trades),
            winning_trades=len(wins),
            losing_trades=len(losses),
            win_rate=win_rate,
            avg_win=avg_win,
            avg_loss=avg_loss,
            largest_win=max((t['pnl'] for t in wins), default=0),
            largest_loss=min((t['pnl'] for t in losses), default=0),
            profit_factor=profit_factor,
            max_drawdown=max_dd,
            max_drawdown_pct=max_dd_pct,
            avg_hold_days=avg_hold,
            target_1_exits=target_1_exits,
            target_2_exits=target_2_exits,
            stop_loss_exits=stop_loss_exits,
            time_exits=time_exits,
            results_by_market=results_by_market,
            trades=trade_results,
        )

    def print_results(self, results: BacktestResults):
        """Print formatted backtest results"""
        print("\n" + "=" * 60)
        print("BACKTEST RESULTS")
        print("=" * 60)

        print(f"\n📊 OVERVIEW:")
        print(f"   Period: {results.period}")
        print(f"   Initial Capital: ${results.initial_capital:,.2f}")
        print(f"   Final Capital: ${results.final_capital:,.2f}")
        print(f"   Total P&L: ${results.total_pnl:+,.2f} ({results.total_pnl_pct:+.2f}%)")

        print(f"\n📈 TRADE STATISTICS:")
        print(f"   Total Trades: {results.total_trades}")
        print(f"   Winning: {results.winning_trades} | Losing: {results.losing_trades}")
        print(f"   Win Rate: {results.win_rate:.1f}%")

        print(f"\n💰 PROFIT/LOSS:")
        print(f"   Average Win: ${results.avg_win:+,.2f}")
        print(f"   Average Loss: ${results.avg_loss:+,.2f}")
        print(f"   Largest Win: ${results.largest_win:+,.2f}")
        print(f"   Largest Loss: ${results.largest_loss:+,.2f}")
        print(f"   Profit Factor: {results.profit_factor:.2f}")

        print(f"\n⚠️ RISK:")
        print(f"   Max Drawdown: ${results.max_drawdown:,.2f} ({results.max_drawdown_pct:.2f}%)")
        print(f"   Avg Hold Days: {results.avg_hold_days:.1f}")

        total = max(results.total_trades, 1)
        print(f"\n🎯 EXIT BREAKDOWN:")
        print(f"   Target 1: {results.target_1_exits} ({results.target_1_exits/total*100:.1f}%)")
        print(f"   Target 2: {results.target_2_exits} ({results.target_2_exits/total*100:.1f}%)")
        print(f"   Stop Loss: {results.stop_loss_exits} ({results.stop_loss_exits/total*100:.1f}%)")
        print(f"   Time Exit: {results.time_exits} ({results.time_exits/total*100:.1f}%)")

        if results.results_by_market:
            print(f"\n🌍 BY MARKET:")
            for market, data in results.results_by_market.items():
                flag = get_market_flag(market)
                print(f"   {flag} {market}: {data['trades']} trades | {data['win_rate']:.1f}% win | ${data['pnl']:+,.2f}")

        # Quality assessment
        print(f"\n📋 ASSESSMENT:")
        if results.win_rate >= 55 and results.profit_factor >= 1.5:
            print("   ✅ GOOD - Strategy is profitable")
        elif results.win_rate >= 50 and results.profit_factor >= 1.2:
            print("   ⚠️ ACCEPTABLE - Strategy is marginally profitable")
        else:
            print("   ❌ NEEDS WORK - Strategy needs improvement")

        print("=" * 60)

    def save_results(self, results: BacktestResults, filepath: str = None):
        """Save results to JSON file"""
        if filepath is None:
            data_dir = getattr(config, 'DATA_DIR', Path('data')) if config else Path('data')
            data_dir = Path(data_dir)
            data_dir.mkdir(exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = data_dir / f"backtest_{timestamp}.json"

        data = {
            "timestamp": datetime.now().isoformat(),
            "period": results.period,
            "initial_capital": results.initial_capital,
            "final_capital": results.final_capital,
            "total_pnl": results.total_pnl,
            "total_pnl_pct": results.total_pnl_pct,
            "total_trades": results.total_trades,
            "win_rate": results.win_rate,
            "profit_factor": results.profit_factor,
            "max_drawdown_pct": results.max_drawdown_pct,
            "results_by_market": results.results_by_market,
            "trades": [asdict(t) for t in results.trades],
        }

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)

        print(f"\n✅ Results saved to: {filepath}")
        return filepath


# ═══════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def run_backtest(
    symbols: List[str] = None,
    period: str = "1y",
    market: str = None,
    save: bool = False
) -> BacktestResults:
    """Run backtest with default settings"""
    backtester = Backtester()

    # Get symbols if not provided
    if symbols is None:
        if market == "US":
            symbols = US_STOCKS[:30] if US_STOCKS else ["AAPL", "MSFT", "GOOGL", "NVDA", "AMD"]
        elif market == "DE":
            symbols = GERMAN_STOCKS[:20] if GERMAN_STOCKS else ["SAP.DE", "SIE.DE"]
        elif market == "IN":
            symbols = INDIAN_STOCKS[:20] if INDIAN_STOCKS else ["TCS.NS", "RELIANCE.NS"]
        else:
            # Mixed
            us = US_STOCKS[:15] if US_STOCKS else ["AAPL", "MSFT", "NVDA"]
            de = GERMAN_STOCKS[:10] if GERMAN_STOCKS else ["SAP.DE"]
            ind = INDIAN_STOCKS[:10] if INDIAN_STOCKS else ["TCS.NS"]
            symbols = us + de + ind

    results = backtester.backtest_universe(symbols, period, market)
    backtester.print_results(results)

    if save:
        backtester.save_results(results)

    return results


def compare_markets(period: str = "1y") -> Dict:
    """Compare performance across markets"""
    backtester = Backtester()

    print("\n" + "=" * 60)
    print("MARKET COMPARISON")
    print("=" * 60)

    all_results = {}

    # US
    us_symbols = US_STOCKS[:20] if US_STOCKS else ["AAPL", "MSFT", "GOOGL", "NVDA", "AMD"]
    print(f"\n🇺🇸 Testing US Market ({len(us_symbols)} stocks)...")
    us_results = backtester.backtest_universe(us_symbols, period, "US")
    all_results["US"] = us_results

    # Germany
    de_symbols = GERMAN_STOCKS[:15] if GERMAN_STOCKS else ["SAP.DE", "SIE.DE"]
    print(f"\n🇩🇪 Testing German Market ({len(de_symbols)} stocks)...")
    de_results = backtester.backtest_universe(de_symbols, period, "DE")
    all_results["DE"] = de_results

    # India
    in_symbols = INDIAN_STOCKS[:15] if INDIAN_STOCKS else ["TCS.NS", "RELIANCE.NS"]
    print(f"\n🇮🇳 Testing Indian Market ({len(in_symbols)} stocks)...")
    in_results = backtester.backtest_universe(in_symbols, period, "IN")
    all_results["IN"] = in_results

    # Print comparison
    print("\n" + "=" * 70)
    print("MARKET COMPARISON RESULTS")
    print("=" * 70)

    print(f"\n{'Market':<12} {'Trades':<10} {'Win Rate':<12} {'P&L':<18} {'Profit Factor':<15}")
    print("-" * 70)

    for market, results in all_results.items():
        flag = get_market_flag(market)
        pnl_str = f"${results.total_pnl:+,.2f}"
        print(f"{flag} {market:<9} {results.total_trades:<10} {results.win_rate:<11.1f}% {pnl_str:<18} {results.profit_factor:<15.2f}")

    print("-" * 70)

    # Best market
    best_market = max(all_results.keys(), key=lambda m: all_results[m].profit_factor)
    print(f"\n🏆 Best Market: {get_market_flag(best_market)} {best_market} (Profit Factor: {all_results[best_market].profit_factor:.2f})")

    return all_results


# ═══════════════════════════════════════════════════════════════
# MAIN / CLI
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Backtest Trading Strategy")
    parser.add_argument(
        "command",
        nargs="?",
        default="run",
        choices=["run", "compare", "us", "german", "india", "de", "in"],
        help="Command to run"
    )
    parser.add_argument("--period", "-p", default="1y", help="Backtest period (6mo, 1y, 2y)")
    parser.add_argument("--save", "-s", action="store_true", help="Save results to file")
    parser.add_argument("--symbols", "-sym", nargs="+", help="Specific symbols to test")

    args = parser.parse_args()

    if args.command == "run":
        run_backtest(symbols=args.symbols, period=args.period, save=args.save)

    elif args.command == "compare":
        compare_markets(args.period)

    elif args.command == "us":
        run_backtest(market="US", period=args.period, save=args.save)

    elif args.command in ["german", "de"]:
        run_backtest(market="DE", period=args.period, save=args.save)

    elif args.command in ["india", "in"]:
        run_backtest(market="IN", period=args.period, save=args.save)

    else:
        run_backtest(period=args.period, save=args.save)
