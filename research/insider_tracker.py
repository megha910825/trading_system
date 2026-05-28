#!/usr/bin/env python3
"""
Insider Tracker - Monitor Insider Buying and Selling Activity
Track what company executives and large shareholders are doing with their shares

Key insight: Insiders might sell for many reasons, but they buy for only one -
they think the stock will go up.
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
from enum import Enum
import json
import time


class InsiderTransactionType(Enum):
    """Types of insider transactions"""
    BUY = "Buy"
    SELL = "Sell"
    OPTION_EXERCISE = "Option Exercise"
    GIFT = "Gift"
    UNKNOWN = "Unknown"


@dataclass
class InsiderTransaction:
    """Single insider transaction"""
    symbol: str
    insider_name: str
    insider_title: str
    transaction_type: InsiderTransactionType
    date: str
    shares: int
    value: float
    price_per_share: float
    shares_owned_after: int
    ownership_change_pct: float


@dataclass
class InsiderSummary:
    """Summary of insider activity for a stock"""
    symbol: str
    name: str
    current_price: float

    # Recent activity counts (last 3 months)
    buys_3m: int
    sells_3m: int
    buy_value_3m: float
    sell_value_3m: float

    # Recent activity counts (last 12 months)
    buys_12m: int
    sells_12m: int
    buy_value_12m: float
    sell_value_12m: float

    # Net activity
    net_shares_3m: int
    net_value_3m: float

    # Key metrics
    buy_sell_ratio: float  # > 1 means more buying
    insider_sentiment: str  # Bullish, Neutral, Bearish
    sentiment_score: int  # -100 to +100

    # Ownership
    insider_ownership_pct: float
    institutional_ownership_pct: float

    # Notable transactions
    largest_buy: Optional[InsiderTransaction]
    largest_sell: Optional[InsiderTransaction]
    most_recent: Optional[InsiderTransaction]

    # Cluster buying (multiple insiders buying together)
    has_cluster_buying: bool
    cluster_buy_count: int


class InsiderTracker:
    """
    Track and analyze insider trading activity

    Features:
    - Recent insider transactions
    - Buy/sell ratios
    - Cluster buying detection
    - Insider sentiment scoring
    - Notable transaction alerts
    """

    def __init__(self, cache_dir: str = "data/insider_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_hours = 12

    def get_insider_transactions(
        self,
        symbol: str,
        months: int = 12
    ) -> List[InsiderTransaction]:
        """
        Get insider transactions for a stock

        Args:
            symbol: Stock ticker
            months: How many months of history to fetch

        Returns:
            List of InsiderTransaction objects
        """

        try:
            ticker = yf.Ticker(symbol)

            # Get insider transactions
            insider_df = ticker.insider_transactions

            if insider_df is None or insider_df.empty:
                return []

            transactions = []
            cutoff_date = datetime.now() - timedelta(days=months * 30)

            for _, row in insider_df.iterrows():
                try:
                    # Parse date
                    trans_date = row.get('Start Date', row.get('Date', None))
                    if trans_date is None:
                        continue

                    if isinstance(trans_date, str):
                        trans_date = datetime.strptime(trans_date[:10], "%Y-%m-%d")
                    elif hasattr(trans_date, 'to_pydatetime'):
                        trans_date = trans_date.to_pydatetime()

                    # Skip old transactions
                    if trans_date < cutoff_date:
                        continue

                    # Parse transaction type
                    trans_text = str(row.get('Transaction', row.get('Text', ''))).lower()

                    if 'buy' in trans_text or 'purchase' in trans_text:
                        trans_type = InsiderTransactionType.BUY
                    elif 'sale' in trans_text or 'sell' in trans_text:
                        trans_type = InsiderTransactionType.SELL
                    elif 'option' in trans_text or 'exercise' in trans_text:
                        trans_type = InsiderTransactionType.OPTION_EXERCISE
                    elif 'gift' in trans_text:
                        trans_type = InsiderTransactionType.GIFT
                    else:
                        trans_type = InsiderTransactionType.UNKNOWN

                    # Parse shares and value
                    shares = abs(int(row.get('Shares', 0)))
                    value = abs(float(row.get('Value', 0)))

                    if shares == 0:
                        continue

                    price_per_share = value / shares if shares > 0 else 0

                    # Parse insider info
                    insider_name = str(row.get('Insider', row.get('Name', 'Unknown')))
                    insider_title = str(row.get('Position', row.get('Title', 'Unknown')))

                    # Shares owned after
                    shares_after = int(row.get('Shares Owned', 0))

                    # Calculate ownership change
                    if shares_after > 0:
                        if trans_type == InsiderTransactionType.BUY:
                            shares_before = shares_after - shares
                        else:
                            shares_before = shares_after + shares

                        change_pct = (shares / shares_before * 100) if shares_before > 0 else 0
                    else:
                        change_pct = 0

                    transactions.append(InsiderTransaction(
                        symbol=symbol,
                        insider_name=insider_name,
                        insider_title=insider_title,
                        transaction_type=trans_type,
                        date=trans_date.strftime("%Y-%m-%d"),
                        shares=shares,
                        value=value,
                        price_per_share=price_per_share,
                        shares_owned_after=shares_after,
                        ownership_change_pct=change_pct
                    ))

                except Exception as e:
                    continue

            # Sort by date (most recent first)
            transactions.sort(key=lambda x: x.date, reverse=True)

            return transactions

        except Exception as e:
            print(f"⚠️ Error fetching insider data for {symbol}: {e}")
            return []

    def get_insider_summary(self, symbol: str) -> Optional[InsiderSummary]:
        """
        Get comprehensive insider activity summary

        Args:
            symbol: Stock ticker

        Returns:
            InsiderSummary object
        """

        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info

            name = info.get('shortName', symbol)
            current_price = info.get('regularMarketPrice', info.get('currentPrice', 0))

            # Get transactions
            transactions = self.get_insider_transactions(symbol, months=12)

            if not transactions:
                return InsiderSummary(
                    symbol=symbol,
                    name=name,
                    current_price=current_price,
                    buys_3m=0, sells_3m=0, buy_value_3m=0, sell_value_3m=0,
                    buys_12m=0, sells_12m=0, buy_value_12m=0, sell_value_12m=0,
                    net_shares_3m=0, net_value_3m=0,
                    buy_sell_ratio=0,
                    insider_sentiment="No Data",
                    sentiment_score=0,
                    insider_ownership_pct=info.get('heldPercentInsiders', 0) * 100 if info.get('heldPercentInsiders') else 0,
                    institutional_ownership_pct=info.get('heldPercentInstitutions', 0) * 100 if info.get('heldPercentInstitutions') else 0,
                    largest_buy=None,
                    largest_sell=None,
                    most_recent=transactions[0] if transactions else None,
                    has_cluster_buying=False,
                    cluster_buy_count=0
                )

            # Calculate time-based metrics
            now = datetime.now()
            three_months_ago = now - timedelta(days=90)

            buys_3m = []
            sells_3m = []
            buys_12m = []
            sells_12m = []

            for t in transactions:
                trans_date = datetime.strptime(t.date, "%Y-%m-%d")

                if t.transaction_type == InsiderTransactionType.BUY:
                    buys_12m.append(t)
                    if trans_date >= three_months_ago:
                        buys_3m.append(t)

                elif t.transaction_type == InsiderTransactionType.SELL:
                    sells_12m.append(t)
                    if trans_date >= three_months_ago:
                        sells_3m.append(t)

            # Calculate values
            buy_value_3m = sum(t.value for t in buys_3m)
            sell_value_3m = sum(t.value for t in sells_3m)
            buy_value_12m = sum(t.value for t in buys_12m)
            sell_value_12m = sum(t.value for t in sells_12m)

            buy_shares_3m = sum(t.shares for t in buys_3m)
            sell_shares_3m = sum(t.shares for t in sells_3m)

            net_shares_3m = buy_shares_3m - sell_shares_3m
            net_value_3m = buy_value_3m - sell_value_3m

            # Buy/sell ratio
            if len(sells_3m) > 0:
                buy_sell_ratio = len(buys_3m) / len(sells_3m)
            elif len(buys_3m) > 0:
                buy_sell_ratio = float('inf')
            else:
                buy_sell_ratio = 0

            # Sentiment scoring (-100 to +100)
            sentiment_score = self._calculate_sentiment_score(
                buys_3m, sells_3m, buy_value_3m, sell_value_3m
            )

            # Determine sentiment label
            if sentiment_score >= 50:
                insider_sentiment = "Very Bullish"
            elif sentiment_score >= 20:
                insider_sentiment = "Bullish"
            elif sentiment_score >= -20:
                insider_sentiment = "Neutral"
            elif sentiment_score >= -50:
                insider_sentiment = "Bearish"
            else:
                insider_sentiment = "Very Bearish"

            # Find largest transactions
            largest_buy = max(buys_12m, key=lambda x: x.value) if buys_12m else None
            largest_sell = max(sells_12m, key=lambda x: x.value) if sells_12m else None

            # Detect cluster buying (3+ insiders buying within 30 days)
            cluster_buying, cluster_count = self._detect_cluster_buying(buys_3m)

            # Ownership
            insider_own = info.get('heldPercentInsiders', 0)
            inst_own = info.get('heldPercentInstitutions', 0)

            return InsiderSummary(
                symbol=symbol,
                name=name,
                current_price=current_price,
                buys_3m=len(buys_3m),
                sells_3m=len(sells_3m),
                buy_value_3m=buy_value_3m,
                sell_value_3m=sell_value_3m,
                buys_12m=len(buys_12m),
                sells_12m=len(sells_12m),
                buy_value_12m=buy_value_12m,
                sell_value_12m=sell_value_12m,
                net_shares_3m=net_shares_3m,
                net_value_3m=net_value_3m,
                buy_sell_ratio=buy_sell_ratio,
                insider_sentiment=insider_sentiment,
                sentiment_score=sentiment_score,
                insider_ownership_pct=insider_own * 100 if insider_own else 0,
                institutional_ownership_pct=inst_own * 100 if inst_own else 0,
                largest_buy=largest_buy,
                largest_sell=largest_sell,
                most_recent=transactions[0] if transactions else None,
                has_cluster_buying=cluster_buying,
                cluster_buy_count=cluster_count
            )

        except Exception as e:
            print(f"⚠️ Error getting insider summary for {symbol}: {e}")
            return None

    def _calculate_sentiment_score(
        self,
        buys: List[InsiderTransaction],
        sells: List[InsiderTransaction],
        buy_value: float,
        sell_value: float
    ) -> int:
        """Calculate insider sentiment score from -100 to +100"""

        score = 0

        # Transaction count factor (max ±30)
        buy_count = len(buys)
        sell_count = len(sells)

        if buy_count + sell_count > 0:
            count_ratio = (buy_count - sell_count) / (buy_count + sell_count)
            score += int(count_ratio * 30)

        # Value factor (max ±40)
        total_value = buy_value + sell_value
        if total_value > 0:
            value_ratio = (buy_value - sell_value) / total_value
            score += int(value_ratio * 40)

        # Bonus for significant buying
        if buy_value > 1_000_000:  # Over $1M in purchases
            score += 15
        elif buy_value > 500_000:
            score += 10
        elif buy_value > 100_000:
            score += 5

        # Penalty for significant selling
        if sell_value > 5_000_000:
            score -= 15
        elif sell_value > 1_000_000:
            score -= 10

        # Bonus for multiple buyers
        unique_buyers = len(set(t.insider_name for t in buys))
        if unique_buyers >= 3:
            score += 15
        elif unique_buyers >= 2:
            score += 10

        return max(-100, min(100, score))

    def _detect_cluster_buying(
        self,
        buys: List[InsiderTransaction]
    ) -> Tuple[bool, int]:
        """
        Detect if multiple insiders are buying within a short period
        This is often a strong bullish signal

        Returns:
            Tuple of (has_cluster, count_of_unique_buyers)
        """

        if len(buys) < 2:
            return False, 0

        # Group buys by 30-day windows
        unique_buyers = set()

        for i, buy in enumerate(buys):
            buy_date = datetime.strptime(buy.date, "%Y-%m-%d")
            window_end = buy_date + timedelta(days=30)

            # Count unique buyers in this window
            window_buyers = {buy.insider_name}

            for other in buys[i+1:]:
                other_date = datetime.strptime(other.date, "%Y-%m-%d")
                if other_date <= window_end:
                    window_buyers.add(other.insider_name)

            if len(window_buyers) >= 3:
                return True, len(window_buyers)

            unique_buyers.update(window_buyers)

        return len(unique_buyers) >= 3, len(unique_buyers)

    def scan_for_insider_buying(
        self,
        symbols: List[str],
        min_buys: int = 1,
        min_buy_value: float = 50000,
        days: int = 90
    ) -> pd.DataFrame:
        """
        Scan multiple stocks for recent insider buying

        Args:
            symbols: List of tickers to scan
            min_buys: Minimum number of buy transactions
            min_buy_value: Minimum total buy value ($)
            days: Look back period in days

        Returns:
            DataFrame with insider buying activity
        """

        results = []
        cutoff = datetime.now() - timedelta(days=days)

        total = len(symbols)

        for i, symbol in enumerate(symbols, 1):
            if i % 10 == 0:
                print(f"   Scanning... {i}/{total}")

            try:
                summary = self.get_insider_summary(symbol)

                if summary is None:
                    continue

                # Filter based on criteria
                if summary.buys_3m < min_buys:
                    continue

                if summary.buy_value_3m < min_buy_value:
                    continue

                results.append({
                    "Symbol": symbol,
                    "Name": summary.name[:20],
                    "Price": f"${summary.current_price:.2f}",
                    "Buys (3M)": summary.buys_3m,
                    "Buy Value": f"${summary.buy_value_3m/1000:.0f}K",
                    "Sells (3M)": summary.sells_3m,
                    "Sell Value": f"${summary.sell_value_3m/1000:.0f}K" if summary.sell_value_3m else "-",
                    "Net Value": f"${summary.net_value_3m/1000:+.0f}K",
                    "Sentiment": summary.insider_sentiment,
                    "Score": summary.sentiment_score,
                    "Cluster": "✅" if summary.has_cluster_buying else "-",
                    "Insider %": f"{summary.insider_ownership_pct:.1f}%",
                })

                time.sleep(0.3)

            except Exception:
                continue

        df = pd.DataFrame(results)

        if not df.empty:
            # Sort by sentiment score
            df['_score'] = df['Score'].astype(int)
            df = df.sort_values('_score', ascending=False)
            df = df.drop('_score', axis=1)

        return df

    def get_recent_notable_buys(
        self,
        symbols: List[str],
        min_value: float = 100000,
        days: int = 30
    ) -> List[Dict]:
        """
        Find notable insider purchases across multiple stocks

        Args:
            symbols: List of tickers
            min_value: Minimum transaction value
            days: Look back period

        Returns:
            List of notable transactions
        """

        notable = []
        cutoff = datetime.now() - timedelta(days=days)

        for symbol in symbols:
            try:
                transactions = self.get_insider_transactions(symbol, months=1)

                for t in transactions:
                    trans_date = datetime.strptime(t.date, "%Y-%m-%d")

                    if trans_date < cutoff:
                        continue

                    if t.transaction_type != InsiderTransactionType.BUY:
                        continue

                    if t.value < min_value:
                        continue

                    notable.append({
                        "symbol": t.symbol,
                        "insider": t.insider_name,
                        "title": t.insider_title,
                        "date": t.date,
                        "shares": t.shares,
                        "value": t.value,
                        "price": t.price_per_share,
                    })

                time.sleep(0.2)

            except Exception:
                continue

        # Sort by value
        notable.sort(key=lambda x: x['value'], reverse=True)

        return notable

    def print_summary(self, symbol: str):
        """Print detailed insider activity summary"""

        summary = self.get_insider_summary(symbol)

        if summary is None:
            print(f"❌ Could not get insider data for {symbol}")
            return

        # Sentiment emoji
        if summary.sentiment_score >= 50:
            sentiment_emoji = "🟢🟢"
        elif summary.sentiment_score >= 20:
            sentiment_emoji = "🟢"
        elif summary.sentiment_score >= -20:
            sentiment_emoji = "🟡"
        elif summary.sentiment_score >= -50:
            sentiment_emoji = "🔴"
        else:
            sentiment_emoji = "🔴🔴"

        print(f"""
╔═══════════════════════════════════════════════════════════════════════════════════════════╗
║                         👔 INSIDER ACTIVITY: {symbol:^10}                                 ║
╠═══════════════════════════════════════════════════════════════════════════════════════════╣
║  {summary.name[:60]:^85} ║
║  Current Price: ${summary.current_price:,.2f}                                                              ║
╠═══════════════════════════════════════════════════════════════════════════════════════════╣
║                                                                                           ║
║  📊 SENTIMENT: {sentiment_emoji} {summary.insider_sentiment:^15}  Score: {summary.sentiment_score:>+4}/100                           ║
║                                                                                           ║
╠═══════════════════════════════════════════════════════════════════════════════════════════╣
║                                                                                           ║
║  📈 LAST 3 MONTHS                           📅 LAST 12 MONTHS                            ║
║  ─────────────────────────────────────────  ────────────────────────────────────────────  ║
║  Buys:        {summary.buys_3m:>4}                             Buys:        {summary.buys_12m:>4}                         ║
║  Buy Value:   ${summary.buy_value_3m:>12,.0f}                   Buy Value:   ${summary.buy_value_12m:>12,.0f}               ║
║  Sells:       {summary.sells_3m:>4}                             Sells:       {summary.sells_12m:>4}                         ║
║  Sell Value:  ${summary.sell_value_3m:>12,.0f}                   Sell Value:  ${summary.sell_value_12m:>12,.0f}               ║
║                                                                                           ║
║  Net Shares:  {summary.net_shares_3m:>+12,}                                                                 ║
║  Net Value:   ${summary.net_value_3m:>+12,.0f}                                                                 ║
║                                                                                           ║
╠═══════════════════════════════════════════════════════════════════════════════════════════╣
║                                                                                           ║
║  👥 OWNERSHIP                                                                             ║
║  ─────────────────────────────────────────────────────────────────────────────────────    ║
║  Insider Ownership:       {summary.insider_ownership_pct:>6.2f}%                                                    ║
║  Institutional Ownership: {summary.institutional_ownership_pct:>6.2f}%                                                    ║
║                                                                                           ║
║  🎯 CLUSTER BUYING: {'✅ YES (' + str(summary.cluster_buy_count) + ' insiders)' if summary.has_cluster_buying else '❌ No':^30}                                      ║
║                                                                                           ║""")

        # Most recent transaction
        if summary.most_recent:
            t = summary.most_recent
            trans_type = "🟢 BUY" if t.transaction_type == InsiderTransactionType.BUY else "🔴 SELL"
            print(f"""║  📋 MOST RECENT TRANSACTION                                                               ║
║  ─────────────────────────────────────────────────────────────────────────────────────    ║
║  {trans_type}  |  {t.date}  |  {t.insider_name[:30]:<30}                      ║
║  {t.shares:,} shares @ ${t.price_per_share:.2f} = ${t.value:,.0f}                                           ║
║                                                                                           ║""")

        # Largest buy
        if summary.largest_buy:
            t = summary.largest_buy
            print(f"""║  💰 LARGEST BUY (12M)                                                                     ║
║  ─────────────────────────────────────────────────────────────────────────────────────    ║
║  {t.date}  |  {t.insider_name[:35]:<35}                                  ║
║  {t.shares:,} shares @ ${t.price_per_share:.2f} = ${t.value:,.0f}                                           ║
║                                                                                           ║""")

        # Analysis
        print(f"""╠═══════════════════════════════════════════════════════════════════════════════════════════╣
║                                                                                           ║
║  💡 ANALYSIS                                                                              ║
║  ─────────────────────────────────────────────────────────────────────────────────────    ║""")

        insights = []

        if summary.sentiment_score >= 50:
            insights.append("✅ Strong insider buying - Very bullish signal")
        elif summary.sentiment_score >= 20:
            insights.append("✅ Net insider buying - Bullish signal")
        elif summary.sentiment_score <= -50:
            insights.append("⚠️ Heavy insider selling - Bearish signal")
        elif summary.sentiment_score <= -20:
            insights.append("⚠️ Net insider selling - Caution warranted")
        else:
            insights.append("➖ Mixed insider activity - Neutral signal")

        if summary.has_cluster_buying:
            insights.append(f"🎯 Cluster buying detected ({summary.cluster_buy_count} insiders) - Strong bullish signal")

        if summary.buy_value_3m > 1_000_000:
            insights.append(f"💰 Significant insider purchases (${summary.buy_value_3m/1_000_000:.1f}M)")

        if summary.insider_ownership_pct > 10:
            insights.append(f"👔 High insider ownership ({summary.insider_ownership_pct:.1f}%) - Aligned interests")
        elif summary.insider_ownership_pct < 1:
            insights.append(f"⚠️ Low insider ownership ({summary.insider_ownership_pct:.1f}%)")

        if summary.buys_3m > 0 and summary.sells_3m == 0:
            insights.append("✅ Only buying, no selling in last 3 months")

        for insight in insights:
            print(f"║  {insight:<85} ║")

        print("""║                                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════════════════════╝
        """)

    def print_scan_results(self, df: pd.DataFrame, title: str = "INSIDER BUYING SCAN"):
        """Print formatted scan results"""

        print(f"""
╔═══════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║                                    👔 {title:^30}                                         ║
╠═══════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
        """)

        if df.empty:
            print("║  No stocks found matching criteria                                                                        ║")
        else:
            print(df.to_string(index=False))
            print()

            # Highlight top picks
            if len(df) > 0:
                print("║                                                                                                           ║")
                print("║  🏆 TOP PICKS (Highest Sentiment Score):                                                                  ║")
                for _, row in df.head(3).iterrows():
                    cluster = "🎯" if row.get('Cluster') == '✅' else ""
                    print(f"║     {row['Symbol']:8} - {row['Sentiment']:15} (Score: {row['Score']:>+4}) {cluster:5} {row['Buy Value']:>10} in buys  ║")

        print("""║                                                                                                           ║
╠═══════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
║  💡 TIP: Cluster buying (multiple insiders buying together) is a particularly strong bullish signal          ║
║     Insiders sell for many reasons, but they buy for only one - they expect the stock to rise                ║
╚═══════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
        """)


# ═══════════════════════════════════════════════════════════════
# DEFAULT WATCHLISTS
# ═══════════════════════════════════════════════════════════════

TECH_WATCHLIST = [
    "AAPL", "MSFT", "NVDA", "GOOGL", "META", "AMZN", "TSLA", "AMD",
    "AVGO", "CRM", "ORCL", "ADBE", "INTC", "QCOM", "TXN", "MU",
    "AMAT", "LRCX", "KLAC", "NOW", "SNOW", "DDOG", "NET", "CRWD"
]

SP500_SAMPLE = [
    "AAPL", "MSFT", "NVDA", "GOOGL", "AMZN", "META", "BRK-B", "LLY",
    "JPM", "UNH", "V", "MA", "PG", "JNJ", "HD", "COST", "XOM", "CVX",
    "MRK", "ABBV", "PFE", "BAC", "WMT", "KO", "PEP", "DIS", "NFLX"
]


# ═══════════════════════════════════════════════════════════════
# COMMAND LINE INTERFACE
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys

    tracker = InsiderTracker()

    if len(sys.argv) < 2:
        print("""
Insider Tracker Commands:
─────────────────────────────────────────────────────────────────────────────
  python insider_tracker.py check SYMBOL          - Detailed insider analysis
  python insider_tracker.py scan                  - Scan tech stocks for buying
  python insider_tracker.py scan --list sp500     - Scan S&P 500 sample
  python insider_tracker.py notable               - Find notable recent buys
  python insider_tracker.py transactions SYMBOL   - List all transactions

Examples:
  python insider_tracker.py check NVDA
  python insider_tracker.py scan
  python insider_tracker.py notable
  python insider_tracker.py transactions AAPL
        """)
        sys.exit(0)

    command = sys.argv[1].lower()

    if command == "check":
        symbol = sys.argv[2].upper() if len(sys.argv) > 2 else "NVDA"
        tracker.print_summary(symbol)

    elif command == "scan":
        # Determine watchlist
        watchlist = TECH_WATCHLIST

        if "--list" in sys.argv:
            idx = sys.argv.index("--list")
            if idx + 1 < len(sys.argv):
                list_name = sys.argv[idx + 1].lower()
                if list_name == "sp500":
                    watchlist = SP500_SAMPLE

        print(f"\n👔 Scanning {len(watchlist)} stocks for insider buying...\n")

        df = tracker.scan_for_insider_buying(
            watchlist,
            min_buys=1,
            min_buy_value=50000,
            days=90
        )

        tracker.print_scan_results(df)

    elif command == "notable":
        print("\n👔 Finding notable insider purchases (last 30 days, >$100K)...\n")

        notable = tracker.get_recent_notable_buys(
            TECH_WATCHLIST + SP500_SAMPLE,
            min_value=100000,
            days=30
        )

        if notable:
            print(f"Found {len(notable)} notable purchases:\n")
            print(f"{'Symbol':<8} {'Insider':<30} {'Date':<12} {'Shares':>12} {'Value':>15}")
            print("-" * 80)

            for t in notable[:20]:
                print(f"{t['symbol']:<8} {t['insider'][:30]:<30} {t['date']:<12} "
                      f"{t['shares']:>12,} ${t['value']:>14,.0f}")
        else:
            print("No notable purchases found")

    elif command == "transactions":
        symbol = sys.argv[2].upper() if len(sys.argv) > 2 else "NVDA"

        print(f"\n👔 Recent transactions for {symbol}:\n")

        transactions = tracker.get_insider_transactions(symbol, months=12)

        if transactions:
            print(f"{'Date':<12} {'Type':<8} {'Insider':<30} {'Shares':>12} {'Value':>15}")
            print("-" * 85)

            for t in transactions[:20]:
                trans_type = "BUY" if t.transaction_type == InsiderTransactionType.BUY else "SELL"
                print(f"{t.date:<12} {trans_type:<8} {t.insider_name[:30]:<30} "
                      f"{t.shares:>12,} ${t.value:>14,.0f}")
        else:
            print("No transactions found")

    else:
        print(f"Unknown command: {command}")
        print("Use: check, scan, notable, or transactions")
