#!/usr/bin/env python3
"""
Earnings Calendar - Track upcoming earnings and historical performance
Avoid holding through earnings or plan accordingly
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass
import json
import time


@dataclass
class EarningsInfo:
    """Earnings information for a stock"""
    symbol: str
    name: str
    next_earnings_date: str
    days_until: int
    is_confirmed: bool
    time_of_day: str  # BMO (Before Market Open), AMC (After Market Close), Unknown

    # Historical
    last_earnings_date: str
    last_surprise_pct: float
    avg_surprise_pct: float
    beat_rate: float  # % of times beat estimates

    # Price reaction
    avg_move_after_earnings: float
    last_move_after_earnings: float

    # Current estimates
    eps_estimate: float
    revenue_estimate: float


class EarningsCalendar:
    """
    Track and analyze earnings dates

    Features:
    - Upcoming earnings dates
    - Historical earnings surprises
    - Price reaction analysis
    - Watchlist scanning
    - Earnings quality scoring
    """

    def __init__(self, cache_dir: str = "data/earnings_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_hours = 6  # Refresh every 6 hours

    def get_earnings_date(self, symbol: str) -> Dict:
        """
        Get next earnings date and related info

        Args:
            symbol: Stock ticker

        Returns:
            Dict with earnings information
        """

        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info

            name = info.get('shortName', symbol)

            # Try to get earnings date from calendar
            earnings_date = None
            is_confirmed = False
            time_of_day = "Unknown"

            try:
                calendar = ticker.calendar

                if calendar is not None and not calendar.empty:
                    # Calendar might have different formats
                    if isinstance(calendar, pd.DataFrame):
                        if 'Earnings Date' in calendar.index:
                            dates = calendar.loc['Earnings Date']
                            if len(dates) > 0:
                                earnings_date = dates.iloc[0]
                        elif len(calendar.columns) > 0:
                            earnings_date = calendar.iloc[0, 0]

            except Exception:
                pass

            # Alternative: check earnings_dates
            if earnings_date is None:
                try:
                    earnings_dates = ticker.earnings_dates
                    if earnings_dates is not None and not earnings_dates.empty:
                        # Get the next future date - handle timezone-aware index
                        now = datetime.now()
                        idx = earnings_dates.index
                        if hasattr(idx, 'tz') and idx.tz is not None:
                            now = pd.Timestamp.now(tz=idx.tz)
                        future_dates = earnings_dates[idx > now]
                        if not future_dates.empty:
                            earnings_date = future_dates.index[0]
                except Exception as e:
                    print(f"Warning: Could not get earnings_dates for {symbol}: {e}")

            # Parse earnings date to calculate days until
            if earnings_date is not None:
                try:
                    if isinstance(earnings_date, str):
                        earnings_dt = datetime.strptime(str(earnings_date)[:10], "%Y-%m-%d")
                    elif hasattr(earnings_date, 'date'):
                        earnings_dt = datetime.combine(earnings_date.date(), datetime.min.time())
                    else:
                        earnings_dt = pd.to_datetime(earnings_date).to_pydatetime()

                    days_until = (earnings_dt - datetime.now()).days
                except Exception:
                    pass

            return {
                "symbol": symbol,
                "name": name,
                "next_earnings": str(earnings_date)[:10] if earnings_date else "Unknown",
                "days_until": days_until,
                "is_soon": days_until is not None and 0 <= days_until <= 14,
                "is_this_week": days_until is not None and 0 <= days_until <= 7,
                "is_confirmed": is_confirmed,
                "time_of_day": time_of_day,
            }

        except Exception as e:
            return {
                "symbol": symbol,
                "name": symbol,
                "next_earnings": "Unknown",
                "days_until": None,
                "is_soon": False,
                "is_this_week": False,
                "error": str(e)
            }

    def get_earnings_history(self, symbol: str, quarters: int = 8) -> pd.DataFrame:
        """
        Get historical earnings data with surprises

        Args:
            symbol: Stock ticker
            quarters: Number of quarters to fetch

        Returns:
            DataFrame with historical earnings
        """

        try:
            ticker = yf.Ticker(symbol)

            # Try earnings_dates first (has surprise data)
            if hasattr(ticker, 'earnings_dates') and ticker.earnings_dates is not None:
                hist = ticker.earnings_dates
                if not hist.empty:
                    # Get past dates only
                    past = hist[hist.index <= datetime.now()]
                    return past.head(quarters)

            # Fallback to quarterly earnings
            if hasattr(ticker, 'quarterly_earnings') and ticker.quarterly_earnings is not None:
                return ticker.quarterly_earnings.head(quarters)

            return pd.DataFrame()

        except Exception as e:
            return pd.DataFrame()

    def get_earnings_surprise_stats(self, symbol: str) -> Dict:
        """
        Calculate earnings surprise statistics

        Returns:
            Dict with beat rate, avg surprise, etc.
        """

        try:
            hist = self.get_earnings_history(symbol, 12)

            if hist.empty:
                return {
                    "symbol": symbol,
                    "quarters_analyzed": 0,
                    "beat_rate": 0,
                    "avg_surprise_pct": 0,
                    "last_surprise_pct": 0,
                }

            # Look for surprise data
            surprise_col = None
            for col in hist.columns:
                if 'surprise' in col.lower():
                    surprise_col = col
                    break

            if surprise_col is None:
                return {
                    "symbol": symbol,
                    "quarters_analyzed": len(hist),
                    "beat_rate": 0,
                    "avg_surprise_pct": 0,
                    "last_surprise_pct": 0,
                    "note": "No surprise data available"
                }

            surprises = hist[surprise_col].dropna()

            if surprises.empty:
                return {
                    "symbol": symbol,
                    "quarters_analyzed": len(hist),
                    "beat_rate": 0,
                    "avg_surprise_pct": 0,
                    "last_surprise_pct": 0,
                }

            beats = (surprises > 0).sum()
            beat_rate = (beats / len(surprises)) * 100
            avg_surprise = surprises.mean()
            last_surprise = surprises.iloc[0] if len(surprises) > 0 else 0

            return {
                "symbol": symbol,
                "quarters_analyzed": len(surprises),
                "beat_rate": round(beat_rate, 1),
                "avg_surprise_pct": round(avg_surprise, 2),
                "last_surprise_pct": round(last_surprise, 2),
                "consecutive_beats": self._count_consecutive_beats(surprises),
            }

        except Exception as e:
            return {
                "symbol": symbol,
                "error": str(e)
            }

    def _count_consecutive_beats(self, surprises: pd.Series) -> int:
        """Count consecutive earnings beats from most recent"""
        count = 0
        for val in surprises:
            if val > 0:
                count += 1
            else:
                break
        return count

    def get_price_reaction(self, symbol: str, quarters: int = 4) -> Dict:
        """
        Analyze typical price reaction after earnings

        Returns:
            Dict with avg move, last move, etc.
        """

        try:
            ticker = yf.Ticker(symbol)

            # Get historical prices
            hist = ticker.history(period="2y")
            if hist.empty:
                return {"symbol": symbol, "error": "No price data"}

            # Get earnings dates
            earnings_hist = self.get_earnings_history(symbol, quarters)
            if earnings_hist.empty:
                return {"symbol": symbol, "error": "No earnings data"}

            moves = []

            for date in earnings_hist.index[:quarters]:
                try:
                    # Find the date in price history
                    date_str = date.strftime("%Y-%m-%d") if hasattr(date, 'strftime') else str(date)[:10]

                    # Get price before and after
                    # This is simplified - real analysis would need exact earnings timing
                    idx = hist.index.get_indexer([date], method='nearest')[0]

                    if idx > 0 and idx < len(hist) - 1:
                        before = hist['Close'].iloc[idx - 1]
                        after = hist['Close'].iloc[idx + 1]
                        move = ((after / before) - 1) * 100
                        moves.append(move)
                except:
                    continue

            if not moves:
                return {
                    "symbol": symbol,
                    "avg_move_pct": 0,
                    "last_move_pct": 0,
                    "max_up_move": 0,
                    "max_down_move": 0,
                    "note": "Could not calculate moves"
                }

            return {
                "symbol": symbol,
                "quarters_analyzed": len(moves),
                "avg_move_pct": round(sum(abs(m) for m in moves) / len(moves), 2),
                "avg_direction_pct": round(sum(moves) / len(moves), 2),
                "last_move_pct": round(moves[0], 2) if moves else 0,
                "max_up_move": round(max(moves), 2),
                "max_down_move": round(min(moves), 2),
            }

        except Exception as e:
            return {"symbol": symbol, "error": str(e)}

    def scan_upcoming_earnings(
        self,
        symbols: List[str],
        days_ahead: int = 14
    ) -> pd.DataFrame:
        """
        Scan watchlist for upcoming earnings

        Args:
            symbols: List of tickers to scan
            days_ahead: How many days to look ahead

        Returns:
            DataFrame with upcoming earnings
        """

        results = []

        for symbol in symbols:
            try:
                info = self.get_earnings_date(symbol)

                days = info.get('days_until')

                if days is not None and 0 <= days <= days_ahead:
                    # Get additional data
                    surprise_stats = self.get_earnings_surprise_stats(symbol)

                    results.append({
                        "Symbol": symbol,
                        "Name": info.get('name', symbol)[:25],
                        "Earnings Date": info.get('next_earnings', 'Unknown'),
                        "Days Until": days,
                        "Beat Rate %": surprise_stats.get('beat_rate', 0),
                        "Avg Surprise %": surprise_stats.get('avg_surprise_pct', 0),
                        "Status": "⚠️ THIS WEEK" if days <= 7 else "📅 Soon"
                    })

                time.sleep(0.2)  # Rate limiting

            except Exception:
                continue

        df = pd.DataFrame(results)

        if not df.empty:
            df = df.sort_values("Days Until")

        return df

    def get_full_earnings_analysis(self, symbol: str) -> Dict:
        """
        Complete earnings analysis for a stock

        Returns:
            Dict with all earnings-related data
        """

        basic = self.get_earnings_date(symbol)
        surprise_stats = self.get_earnings_surprise_stats(symbol)
        price_reaction = self.get_price_reaction(symbol)

        # Determine earnings quality
        beat_rate = surprise_stats.get('beat_rate', 0)
        avg_surprise = surprise_stats.get('avg_surprise_pct', 0)

        if beat_rate >= 80 and avg_surprise > 5:
            earnings_quality = "Excellent"
            quality_emoji = "🟢"
        elif beat_rate >= 60 and avg_surprise > 0:
            earnings_quality = "Good"
            quality_emoji = "🟢"
        elif beat_rate >= 40:
            earnings_quality = "Mixed"
            quality_emoji = "🟡"
        else:
            earnings_quality = "Poor"
            quality_emoji = "🔴"

        return {
            "symbol": symbol,
            "name": basic.get('name', symbol),

            # Next earnings
            "next_earnings_date": basic.get('next_earnings', 'Unknown'),
            "days_until": basic.get('days_until'),
            "is_this_week": basic.get('is_this_week', False),

            # Historical
            "beat_rate": surprise_stats.get('beat_rate', 0),
            "avg_surprise_pct": surprise_stats.get('avg_surprise_pct', 0),
            "last_surprise_pct": surprise_stats.get('last_surprise_pct', 0),
            "consecutive_beats": surprise_stats.get('consecutive_beats', 0),

            # Price reaction
            "avg_earnings_move_pct": price_reaction.get('avg_move_pct', 0),
            "last_earnings_move_pct": price_reaction.get('last_move_pct', 0),

            # Quality
            "earnings_quality": earnings_quality,
            "quality_emoji": quality_emoji,

            # Recommendation
            "hold_through_earnings": beat_rate >= 70 and avg_surprise > 3,
        }

    def check_portfolio_earnings(self, symbols: List[str]) -> Tuple[List[Dict], List[Dict]]:
        """
        Check portfolio for earnings warnings

        Returns:
            Tuple of (warnings, upcoming)
        """

        warnings = []  # Earnings this week
        upcoming = []  # Earnings in 2 weeks

        for symbol in symbols:
            info = self.get_earnings_date(symbol)
            days = info.get('days_until')

            if days is not None:
                if 0 <= days <= 7:
                    warnings.append({
                        "symbol": symbol,
                        "name": info.get('name', symbol),
                        "date": info.get('next_earnings'),
                        "days": days
                    })
                elif 8 <= days <= 14:
                    upcoming.append({
                        "symbol": symbol,
                        "name": info.get('name', symbol),
                        "date": info.get('next_earnings'),
                        "days": days
                    })

        return warnings, upcoming

    def print_calendar(self, symbols: List[str], days_ahead: int = 21):
        """Print formatted earnings calendar"""

        df = self.scan_upcoming_earnings(symbols, days_ahead)

        print(f"""
╔═══════════════════════════════════════════════════════════════════════════════════╗
║                           📅 EARNINGS CALENDAR                                    ║
║                           Next {days_ahead} Days                                           ║
╠═══════════════════════════════════════════════════════════════════════════════════╣
        """)

        if df.empty:
            print("║  No upcoming earnings in your watchlist                                         ║")
        else:
            print("║  Symbol   Name                      Date         Days   Beat%  Surprise%       ║")
            print("║  ─────────────────────────────────────────────────────────────────────────────  ║")

            for _, row in df.iterrows():
                status = "⚠️" if row['Days Until'] <= 7 else "📅"
                print(f"║  {status} {row['Symbol']:6} {row['Name']:24} {row['Earnings Date']:>12} "
                      f"{row['Days Until']:>4}d  {row['Beat Rate %']:>5.0f}%  {row['Avg Surprise %']:>+6.1f}%  ║")

        print("""║                                                                                   ║
╠═══════════════════════════════════════════════════════════════════════════════════╣
║  💡 TIP: Consider closing positions before earnings or reducing size             ║
║     Stocks with Beat Rate > 70% and positive surprises are safer to hold         ║
╚═══════════════════════════════════════════════════════════════════════════════════╝
        """)

    def print_analysis(self, symbol: str):
        """Print detailed earnings analysis for a stock"""

        analysis = self.get_full_earnings_analysis(symbol)

        print(f"""
╔═══════════════════════════════════════════════════════════════════════════════════╗
║                    📊 EARNINGS ANALYSIS: {symbol:^10}                              ║
╠═══════════════════════════════════════════════════════════════════════════════════╣
║  {analysis['name'][:60]:^77} ║
╠═══════════════════════════════════════════════════════════════════════════════════╣
║                                                                                   ║
║  📅 NEXT EARNINGS                                                                 ║
║  ─────────────────────────────────────────────────────────────────────────────    ║
║  Date: {analysis['next_earnings_date']:>15}                                                      ║
║  Days Until: {analysis['days_until'] if analysis['days_until'] else 'Unknown':>10}                                                   ║
║  This Week: {'⚠️ YES - CAUTION' if analysis['is_this_week'] else 'No':>15}                                              ║
║                                                                                   ║
║  📈 HISTORICAL PERFORMANCE                                                        ║
║  ─────────────────────────────────────────────────────────────────────────────    ║
║  Beat Rate:          {analysis['beat_rate']:>6.1f}%                                               ║
║  Avg Surprise:       {analysis['avg_surprise_pct']:>+6.2f}%                                               ║
║  Last Surprise:      {analysis['last_surprise_pct']:>+6.2f}%                                               ║
║  Consecutive Beats:  {analysis['consecutive_beats']:>6}                                                  ║
║                                                                                   ║
║  💹 TYPICAL PRICE REACTION                                                        ║
║  ─────────────────────────────────────────────────────────────────────────────    ║
║  Avg Move After:     {analysis['avg_earnings_move_pct']:>+6.2f}%                                               ║
║  Last Move:          {analysis['last_earnings_move_pct']:>+6.2f}%                                               ║
║                                                                                   ║
║  🎯 EARNINGS QUALITY: {analysis['quality_emoji']} {analysis['earnings_quality']:<15}                                     ║
║                                                                                   ║
║  💡 RECOMMENDATION:                                                               ║
║  {'✅ Generally safe to hold through earnings' if analysis['hold_through_earnings'] else '⚠️ Consider reducing position before earnings':^75} ║
║                                                                                   ║
╚═══════════════════════════════════════════════════════════════════════════════════╝
        """)


# ═══════════════════════════════════════════════════════════════
# COMMAND LINE INTERFACE
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys

    ec = EarningsCalendar()

    # Default watchlist
    DEFAULT_WATCHLIST = [
        "NVDA", "AMD", "AAPL", "MSFT", "GOOGL", "META", "AMZN", "TSLA",
        "AVGO", "CRM", "NFLX", "ADBE", "ORCL", "INTC", "QCOM", "MU",
        "AMAT", "LRCX", "KLAC", "ASML"
    ]

    if len(sys.argv) < 2:
        print("""
Earnings Calendar Commands:
─────────────────────────────────────────────────────────────────
  python earnings_calendar.py scan                  - Scan default watchlist
  python earnings_calendar.py scan SYM1 SYM2...     - Scan specific symbols
  python earnings_calendar.py check SYMBOL          - Full earnings analysis
  python earnings_calendar.py portfolio SYM1 SYM2   - Check portfolio warnings

Examples:
  python earnings_calendar.py scan
  python earnings_calendar.py scan NVDA AMD AAPL MSFT
  python earnings_calendar.py check NVDA
  python earnings_calendar.py portfolio NVDA AMD GOOGL
        """)
        sys.exit(0)

    command = sys.argv[1].lower()

    if command == "scan":
        symbols = [s.upper() for s in sys.argv[2:]] if len(sys.argv) > 2 else DEFAULT_WATCHLIST
        ec.print_calendar(symbols, days_ahead=21)

    elif command == "check":
        symbol = sys.argv[2].upper() if len(sys.argv) > 2 else "NVDA"
        ec.print_analysis(symbol)

    elif command == "portfolio":
        symbols = [s.upper() for s in sys.argv[2:]]
        if not symbols:
            print("Please provide portfolio symbols")
            sys.exit(1)

        warnings, upcoming = ec.check_portfolio_earnings(symbols)

        print("\n📊 PORTFOLIO EARNINGS CHECK\n")

        if warnings:
            print("⚠️  EARNINGS THIS WEEK (Consider action):")
            for w in warnings:
                print(f"   {w['symbol']:8} - {w['date']} ({w['days']} days)")
        else:
            print("✅ No earnings this week")

        print()

        if upcoming:
            print("📅 EARNINGS IN 2 WEEKS:")
            for u in upcoming:
                print(f"   {u['symbol']:8} - {u['date']} ({u['days']} days)")
        else:
            print("✅ No earnings in next 2 weeks")

    else:
        print(f"Unknown command: {command}")
        print("Use: scan, check, or portfolio")
