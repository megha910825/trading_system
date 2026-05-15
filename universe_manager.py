#!/usr/bin/env python3
"""
Universe Manager - Dynamically manages stock universe
Auto-updates based on momentum, volume, and returns
"""

import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import json
from pathlib import Path
import time

# File paths
BASE_DIR = Path(__file__).parent
UNIVERSE_FILE = BASE_DIR / "data" / "dynamic_universe.json"
RANKINGS_FILE = BASE_DIR / "data" / "stock_rankings.csv"


class UniverseManager:
    """
    Dynamically manages the stock trading universe
    Automatically updates based on momentum, volume, and returns
    """

    def __init__(self):
        self.sp500 = []
        self.nasdaq100 = []
        self.all_stocks = []
        self.ranked_stocks = pd.DataFrame()
        self.trading_universe = []

        # Ranking weights
        self.weights = {
            "momentum_20d": 0.25,      # 20-day price momentum
            "momentum_5d": 0.15,       # 5-day price momentum
            "returns_3m": 0.20,        # 3-month returns
            "rel_volume": 0.15,        # Relative volume
            "atr_score": 0.10,         # Volatility (ATR)
            "trend_score": 0.15,       # Trend strength
        }

        # Minimum criteria
        self.min_criteria = {
            "min_price": 10,
            "max_price": 2000,
            "min_volume": 500_000,      # 500K daily volume
            "min_market_cap": 1e9,      # $1B market cap
        }

    # ============================================================
    # FETCH STOCK LISTS
    # ============================================================

    def fetch_sp500(self) -> List[str]:
        """Fetch S&P 500 stock symbols"""
        try:
            url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
            tables = pd.read_html(url)
            df = tables[0]
            symbols = df['Symbol'].str.replace('.', '-', regex=False).tolist()
            self.sp500 = symbols
            print(f"✓ Fetched {len(symbols)} S&P 500 stocks")
            return symbols
        except Exception as e:
            print(f"Error fetching S&P 500: {e}")
            return self._get_backup_sp500()

    def fetch_nasdaq100(self) -> List[str]:
        """Fetch NASDAQ 100 stock symbols"""
        try:
            url = "https://en.wikipedia.org/wiki/Nasdaq-100"
            tables = pd.read_html(url)
            # Find the table with ticker symbols
            for table in tables:
                if 'Ticker' in table.columns:
                    symbols = table['Ticker'].tolist()
                    self.nasdaq100 = symbols
                    print(f"✓ Fetched {len(symbols)} NASDAQ 100 stocks")
                    return symbols
                elif 'Symbol' in table.columns:
                    symbols = table['Symbol'].tolist()
                    self.nasdaq100 = symbols
                    print(f"✓ Fetched {len(symbols)} NASDAQ 100 stocks")
                    return symbols
            return self._get_backup_nasdaq100()
        except Exception as e:
            print(f"Error fetching NASDAQ 100: {e}")
            return self._get_backup_nasdaq100()

    def _get_backup_sp500(self) -> List[str]:
        """Backup list of major S&P 500 stocks"""
        stocks = [
            # Tech
            "AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "TSLA", "AMD", "INTC", "CRM",
            "ADBE", "ORCL", "CSCO", "AVGO", "QCOM", "TXN", "IBM", "NOW", "INTU", "AMAT",
            # Finance
            "JPM", "BAC", "WFC", "GS", "MS", "C", "AXP", "V", "MA", "BLK",
            # Healthcare
            "UNH", "JNJ", "PFE", "MRK", "ABBV", "TMO", "ABT", "LLY", "BMY", "AMGN",
            # Consumer
            "WMT", "HD", "MCD", "NKE", "SBUX", "TGT", "COST", "LOW", "TJX", "ROST",
            # Industrial
            "CAT", "BA", "HON", "UPS", "GE", "MMM", "DE", "LMT", "RTX", "UNP",
            # Energy
            "XOM", "CVX", "COP", "SLB", "EOG", "MPC", "PSX", "VLO", "OXY", "HAL",
            # Communication
            "DIS", "NFLX", "CMCSA", "VZ", "T", "TMUS",
            # Materials
            "LIN", "APD", "ECL", "NEM", "FCX",
        ]
        self.sp500 = stocks
        print(f"✓ Using backup list: {len(stocks)} stocks")
        return stocks

    def _get_backup_nasdaq100(self) -> List[str]:
        """Backup list of major NASDAQ 100 stocks"""
        stocks = [
            "AAPL", "MSFT", "AMZN", "NVDA", "GOOGL", "META", "TSLA", "AVGO", "COST", "ASML",
            "AMD", "PEP", "ADBE", "NFLX", "CSCO", "TMUS", "CMCSA", "INTC", "INTU", "QCOM",
            "TXN", "AMGN", "ISRG", "HON", "AMAT", "BKNG", "VRTX", "SBUX", "GILD", "ADI",
            "MDLZ", "LRCX", "REGN", "PANW", "KLAC", "SNPS", "CDNS", "MELI", "CRWD", "MRVL",
            "ORLY", "CTAS", "MAR", "ABNB", "PYPL", "NXPI", "PCAR", "WDAY", "CPRT", "MNST",
            "FTNT", "PAYX", "AEP", "ROST", "ODFL", "KDP", "FAST", "CHTR", "DXCM", "AZN",
            "KHC", "EXC", "MRNA", "CTSH", "EA", "VRSK", "GEHC", "XEL", "IDXX", "CSGP",
            "BKR", "FANG", "ANSS", "ON", "TTWO", "DDOG", "GFS", "WBD", "CDW", "ZS",
            "TEAM", "ILMN", "MDB", "ALGN", "WBA", "ENPH", "BIIB", "SIRI", "LCID", "RIVN"
        ]
        self.nasdaq100 = stocks
        print(f"✓ Using backup NASDAQ list: {len(stocks)} stocks")
        return stocks

    def get_all_stocks(self) -> List[str]:
        """Get combined unique list of all stocks"""
        if not self.sp500:
            self.fetch_sp500()
        if not self.nasdaq100:
            self.fetch_nasdaq100()

        # Combine and deduplicate
        all_stocks = list(set(self.sp500 + self.nasdaq100))
        self.all_stocks = sorted(all_stocks)
        print(f"✓ Total unique stocks: {len(self.all_stocks)}")
        return self.all_stocks

    # ============================================================
    # ANALYZE AND RANK STOCKS
    # ============================================================

    def analyze_stock(self, symbol: str) -> Optional[Dict]:
        """Analyze a single stock for ranking"""
        try:
            ticker = yf.Ticker(symbol)

            # Get historical data
            df = ticker.history(period="6mo")
            if df.empty or len(df) < 60:
                return None

            # Get info
            info = ticker.info

            # Basic filters
            price = df['Close'].iloc[-1]
            if price < self.min_criteria["min_price"] or price > self.min_criteria["max_price"]:
                return None

            market_cap = info.get('marketCap', 0)
            if market_cap < self.min_criteria["min_market_cap"]:
                return None

            avg_volume = df['Volume'].tail(20).mean()
            if avg_volume < self.min_criteria["min_volume"]:
                return None

            # Calculate metrics

            # 1. Momentum (20-day)
            if len(df) >= 20:
                momentum_20d = ((df['Close'].iloc[-1] / df['Close'].iloc[-20]) - 1) * 100
            else:
                momentum_20d = 0

            # 2. Momentum (5-day)
            if len(df) >= 5:
                momentum_5d = ((df['Close'].iloc[-1] / df['Close'].iloc[-5]) - 1) * 100
            else:
                momentum_5d = 0

            # 3. 3-month returns
            if len(df) >= 63:
                returns_3m = ((df['Close'].iloc[-1] / df['Close'].iloc[-63]) - 1) * 100
            else:
                returns_3m = ((df['Close'].iloc[-1] / df['Close'].iloc[0]) - 1) * 100

            # 4. Relative Volume
            recent_volume = df['Volume'].tail(5).mean()
            rel_volume = recent_volume / avg_volume if avg_volume > 0 else 1

            # 5. ATR %
            high = df['High']
            low = df['Low']
            close = df['Close']
            tr = pd.concat([high - low, abs(high - close.shift()), abs(low - close.shift())], axis=1).max(axis=1)
            atr = tr.tail(14).mean()
            atr_pct = (atr / price) * 100

            # 6. Trend Score
            ema_20 = df['Close'].ewm(span=20).mean().iloc[-1]
            ema_50 = df['Close'].ewm(span=50).mean().iloc[-1]
            ema_200 = df['Close'].ewm(span=200).mean().iloc[-1] if len(df) >= 200 else ema_50

            trend_score = 0
            if price > ema_20: trend_score += 33
            if price > ema_50: trend_score += 33
            if price > ema_200: trend_score += 34

            # 7. RSI
            delta = df['Close'].diff()
            gain = delta.where(delta > 0, 0).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rs = gain / loss
            rsi = (100 - (100 / (1 + rs))).iloc[-1]

            return {
                "symbol": symbol,
                "name": info.get("longName", symbol),
                "sector": info.get("sector", "Unknown"),
                "industry": info.get("industry", "Unknown"),
                "price": round(price, 2),
                "market_cap_b": round(market_cap / 1e9, 2),
                "avg_volume_m": round(avg_volume / 1e6, 2),
                "momentum_20d": round(momentum_20d, 2),
                "momentum_5d": round(momentum_5d, 2),
                "returns_3m": round(returns_3m, 2),
                "rel_volume": round(rel_volume, 2),
                "atr_pct": round(atr_pct, 2),
                "trend_score": trend_score,
                "rsi": round(rsi, 1),
                "ema_20": round(ema_20, 2),
                "ema_50": round(ema_50, 2),
            }

        except Exception as e:
            return None

    def rank_stocks(self, stocks: List[str] = None, top_n: int = 50) -> pd.DataFrame:
        """
        Analyze and rank all stocks
        Returns top N stocks for trading universe
        """
        if stocks is None:
            stocks = self.get_all_stocks()

        print(f"\n{'='*60}")
        print(f"RANKING {len(stocks)} STOCKS")
        print(f"{'='*60}")

        results = []
        total = len(stocks)

        for i, symbol in enumerate(stocks):
            # Progress
            if (i + 1) % 10 == 0 or i == 0:
                print(f"  Analyzing: {i+1}/{total} ({symbol})...", end="\r")

            data = self.analyze_stock(symbol)
            if data:
                results.append(data)

            # Rate limiting
            time.sleep(0.1)

        print(f"\n  Analyzed {len(results)} valid stocks")

        if not results:
            print("  No stocks passed criteria")
            return pd.DataFrame()

        # Create DataFrame
        df = pd.DataFrame(results)

        # Calculate composite score
        df = self._calculate_composite_score(df)

        # Sort by composite score
        df = df.sort_values("composite_score", ascending=False)

        # Save full rankings
        df.to_csv(RANKINGS_FILE, index=False)
        print(f"  ✓ Rankings saved to {RANKINGS_FILE}")

        # Store results
        self.ranked_stocks = df

        # Get top N
        top_stocks = df.head(top_n)
        self.trading_universe = top_stocks['symbol'].tolist()

        print(f"  ✓ Top {top_n} stocks selected for trading universe")

        return df

    def _calculate_composite_score(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate composite score for ranking"""
        df = df.copy()

        # Normalize each metric to 0-100 scale
        def normalize(series, higher_is_better=True):
            min_val = series.min()
            max_val = series.max()
            if max_val == min_val:
                return pd.Series([50] * len(series))
            normalized = ((series - min_val) / (max_val - min_val)) * 100
            if not higher_is_better:
                normalized = 100 - normalized
            return normalized

        # Normalize metrics
        df["momentum_20d_norm"] = normalize(df["momentum_20d"])
        df["momentum_5d_norm"] = normalize(df["momentum_5d"])
        df["returns_3m_norm"] = normalize(df["returns_3m"])
        df["rel_volume_norm"] = normalize(df["rel_volume"])
        df["trend_score_norm"] = df["trend_score"]  # Already 0-100

        # ATR - moderate is best (2-5%)
        df["atr_score"] = df["atr_pct"].apply(
            lambda x: 100 if 2 <= x <= 5 else (80 if 1.5 <= x <= 6 else (60 if 1 <= x <= 8 else 30))
        )

        # Calculate composite score
        df["composite_score"] = (
            df["momentum_20d_norm"] * self.weights["momentum_20d"] +
            df["momentum_5d_norm"] * self.weights["momentum_5d"] +
            df["returns_3m_norm"] * self.weights["returns_3m"] +
            df["rel_volume_norm"] * self.weights["rel_volume"] +
            df["atr_score"] * self.weights["atr_score"] +
            df["trend_score_norm"] * self.weights["trend_score"]
        )

        df["composite_score"] = df["composite_score"].round(2)

        return df

    # ============================================================
    # SAVE AND LOAD UNIVERSE
    # ============================================================

    def save_universe(self):
        """Save trading universe to file"""
        data = {
            "updated_at": datetime.now().isoformat(),
            "total_analyzed": len(self.ranked_stocks),
            "universe_size": len(self.trading_universe),
            "trading_universe": self.trading_universe,
            "weights": self.weights,
            "min_criteria": self.min_criteria,
        }

        UNIVERSE_FILE.parent.mkdir(exist_ok=True)

        with open(UNIVERSE_FILE, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"✓ Universe saved to {UNIVERSE_FILE}")

    def load_universe(self) -> List[str]:
        """Load trading universe from file"""
        if not UNIVERSE_FILE.exists():
            print("No saved universe found. Run update_universe() first.")
            return []

        with open(UNIVERSE_FILE, 'r') as f:
            data = json.load(f)

        self.trading_universe = data.get("trading_universe", [])

        updated_at = data.get("updated_at", "Unknown")
        print(f"✓ Loaded universe: {len(self.trading_universe)} stocks")
        print(f"  Last updated: {updated_at}")

        return self.trading_universe

    def get_trading_universe(self) -> List[str]:
        """Get current trading universe"""
        if self.trading_universe:
            return self.trading_universe
        return self.load_universe()

    # ============================================================
    # UPDATE UNIVERSE
    # ============================================================

    def update_universe(self, top_n: int = 50) -> List[str]:
        """
        Full universe update:
        1. Fetch all stocks
        2. Analyze and rank
        3. Select top N
        4. Save to file
        """
        print("\n" + "=" * 60)
        print("UPDATING TRADING UNIVERSE")
        print("=" * 60)
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

        # Fetch stocks
        self.get_all_stocks()

        # Rank stocks
        self.rank_stocks(top_n=top_n)

        # Save universe
        self.save_universe()

        print("\n" + "=" * 60)
        print("UPDATE COMPLETE")
        print("=" * 60)
        print(f"Trading Universe: {len(self.trading_universe)} stocks")
        print(f"\nTop 10 stocks:")

        for i, symbol in enumerate(self.trading_universe[:10]):
            row = self.ranked_stocks[self.ranked_stocks['symbol'] == symbol].iloc[0]
            print(f"  {i+1:2}. {symbol:6} | Score: {row['composite_score']:5.1f} | "
                  f"Mom20: {row['momentum_20d']:+6.1f}% | 3M: {row['returns_3m']:+6.1f}%")

        return self.trading_universe

    def quick_update(self, top_n: int = 50) -> List[str]:
        """
        Quick update using only the backup stock lists
        Faster than full update
        """
        print("\n" + "=" * 60)
        print("QUICK UNIVERSE UPDATE")
        print("=" * 60)

        # Use backup lists (faster)
        stocks = list(set(self._get_backup_sp500() + self._get_backup_nasdaq100()))

        # Rank stocks
        self.rank_stocks(stocks=stocks, top_n=top_n)

        # Save universe
        self.save_universe()

        return self.trading_universe

    # ============================================================
    # REPORTS
    # ============================================================

    def get_sector_breakdown(self) -> pd.DataFrame:
        """Get sector breakdown of trading universe"""
        if self.ranked_stocks.empty:
            return pd.DataFrame()

        top = self.ranked_stocks[self.ranked_stocks['symbol'].isin(self.trading_universe)]
        breakdown = top.groupby('sector').agg({
            'symbol': 'count',
            'composite_score': 'mean',
            'momentum_20d': 'mean',
        }).round(2)
        breakdown.columns = ['count', 'avg_score', 'avg_momentum']
        return breakdown.sort_values('count', ascending=False)

    def get_top_movers(self, n: int = 10) -> pd.DataFrame:
        """Get top momentum stocks"""
        if self.ranked_stocks.empty:
            return pd.DataFrame()

        return self.ranked_stocks.nlargest(n, 'momentum_20d')[
            ['symbol', 'name', 'price', 'momentum_20d', 'momentum_5d', 'returns_3m', 'composite_score']
        ]

    def get_high_volume(self, n: int = 10) -> pd.DataFrame:
        """Get highest relative volume stocks"""
        if self.ranked_stocks.empty:
            return pd.DataFrame()

        return self.ranked_stocks.nlargest(n, 'rel_volume')[
            ['symbol', 'name', 'price', 'rel_volume', 'avg_volume_m', 'momentum_20d', 'composite_score']
        ]

    def print_universe_report(self):
        """Print detailed universe report"""
        print("\n" + "=" * 70)
        print("TRADING UNIVERSE REPORT")
        print("=" * 70)

        if self.ranked_stocks.empty:
            print("No data. Run update_universe() first.")
            return

        print(f"\nUniverse Size: {len(self.trading_universe)} stocks")
        print(f"Total Analyzed: {len(self.ranked_stocks)} stocks")

        # Top stocks
        print(f"\n{'='*70}")
        print("TOP 20 STOCKS BY COMPOSITE SCORE")
        print(f"{'='*70}")

        top20 = self.ranked_stocks.head(20)
        print(top20[['symbol', 'name', 'sector', 'price', 'composite_score',
                     'momentum_20d', 'returns_3m', 'rel_volume', 'trend_score']].to_string(index=False))

        # Sector breakdown
        print(f"\n{'='*70}")
        print("SECTOR BREAKDOWN")
        print(f"{'='*70}")
        print(self.get_sector_breakdown().to_string())

        # Top movers
        print(f"\n{'='*70}")
        print("TOP 10 MOMENTUM STOCKS (20-day)")
        print(f"{'='*70}")
        print(self.get_top_movers(10).to_string(index=False))

        # High volume
        print(f"\n{'='*70}")
        print("TOP 10 HIGH RELATIVE VOLUME")
        print(f"{'='*70}")
        print(self.get_high_volume(10).to_string(index=False))


# ============================================================
# MAIN / CLI
# ============================================================

def main():
    """Main function for command line usage"""
    import argparse

    parser = argparse.ArgumentParser(description="Universe Manager")
    parser.add_argument("command", choices=["update", "quick", "show", "report"],
                       help="Command: update (full), quick (fast), show (list), report (detailed)")
    parser.add_argument("--top", "-n", type=int, default=50, help="Number of top stocks")

    args = parser.parse_args()

    um = UniverseManager()

    if args.command == "update":
        um.update_universe(top_n=args.top)
    elif args.command == "quick":
        um.quick_update(top_n=args.top)
    elif args.command == "show":
        universe = um.load_universe()
        print("\nTrading Universe:")
        for i, symbol in enumerate(universe):
            print(f"  {i+1:2}. {symbol}")
    elif args.command == "report":
        um.load_universe()
        if RANKINGS_FILE.exists():
            um.ranked_stocks = pd.read_csv(RANKINGS_FILE)
        um.print_universe_report()


if __name__ == "__main__":
    main()
