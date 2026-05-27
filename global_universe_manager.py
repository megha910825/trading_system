#!/usr/bin/env python3
"""
Global Universe Manager - Manages stocks from US, German, and Indian markets
Auto-updates based on momentum, volume, and returns
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import List, Dict, Optional
import json
from pathlib import Path
import time

from global_data_fetcher import GlobalDataFetcher
from market_config import (
    MARKETS, US_STOCKS, GERMAN_STOCKS, INDIAN_STOCKS,
    get_all_stocks, get_flat_stock_list
)


# File paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

UNIVERSE_FILE = DATA_DIR / "global_universe.json"
RANKINGS_FILE = DATA_DIR / "global_rankings.csv"


class GlobalUniverseManager:
    """
    Manages stock universe across multiple international markets
    """

    def __init__(self):
        self.fetcher = GlobalDataFetcher()
        self.ranked_stocks = pd.DataFrame()
        self.trading_universe = {}  # {market: [symbols]}

        # Ranking weights
        self.weights = {
            "momentum_20d": 0.25,
            "momentum_5d": 0.15,
            "returns_3m": 0.20,
            "rel_volume": 0.15,
            "atr_score": 0.10,
            "trend_score": 0.15,
        }

    def analyze_stock(self, symbol: str) -> Optional[Dict]:
        """Analyze a single stock for ranking"""
        try:
            # Get data
            df = self.fetcher.get_stock_data(symbol, period="6mo")
            if df.empty or len(df) < 60:
                return None

            info = self.fetcher.get_stock_info(symbol)
            market = self.fetcher.detect_market(symbol)
            market_info = MARKETS[market]

            # Get current price
            price = df['close'].iloc[-1]

            # Basic filters
            if price < market_info.min_price or price > market_info.max_price:
                return None

            market_cap = info.get('market_cap', 0)
            if market_cap < market_info.min_market_cap:
                return None

            avg_volume = df['volume'].tail(20).mean()
            if avg_volume < market_info.min_volume:
                return None

            # Calculate metrics

            # 1. Momentum (20-day)
            momentum_20d = 0
            if len(df) >= 20:
                momentum_20d = ((df['close'].iloc[-1] / df['close'].iloc[-20]) - 1) * 100

            # 2. Momentum (5-day)
            momentum_5d = 0
            if len(df) >= 5:
                momentum_5d = ((df['close'].iloc[-1] / df['close'].iloc[-5]) - 1) * 100

            # 3. 3-month returns
            if len(df) >= 63:
                returns_3m = ((df['close'].iloc[-1] / df['close'].iloc[-63]) - 1) * 100
            else:
                returns_3m = ((df['close'].iloc[-1] / df['close'].iloc[0]) - 1) * 100

            # 4. Relative Volume
            recent_volume = df['volume'].tail(5).mean()
            rel_volume = recent_volume / avg_volume if avg_volume > 0 else 1

            # 5. ATR %
            high, low, close = df['high'], df['low'], df['close']
            tr = pd.concat([high - low, abs(high - close.shift()), abs(low - close.shift())], axis=1).max(axis=1)
            atr = tr.tail(14).mean()
            atr_pct = (atr / price) * 100

            # 6. Trend Score
            ema_20 = df['close'].ewm(span=20).mean().iloc[-1]
            ema_50 = df['close'].ewm(span=50).mean().iloc[-1]
            ema_200 = df['close'].ewm(span=200).mean().iloc[-1] if len(df) >= 200 else ema_50

            trend_score = 0
            if price > ema_20: trend_score += 33
            if price > ema_50: trend_score += 33
            if price > ema_200: trend_score += 34

            # 7. RSI
            delta = df['close'].diff()
            gain = delta.where(delta > 0, 0).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rs = gain / loss
            rsi = (100 - (100 / (1 + rs))).iloc[-1]

            return {
                "symbol": symbol,
                "name": info.get("name", symbol),
                "sector": info.get("sector", "Unknown"),
                "industry": info.get("industry", "Unknown"),
                "market": market,
                "currency": market_info.currency,
                "price": round(price, 2),
                "market_cap": market_cap,
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

    def rank_stocks(self, markets: List[str] = None, top_n_per_market: int = 20) -> pd.DataFrame:
        """
        Analyze and rank stocks from specified markets

        Args:
            markets: List of market codes ['US', 'DE', 'IN']
            top_n_per_market: Number of top stocks per market

        Returns:
            DataFrame with ranked stocks
        """
        if markets is None:
            markets = ["US", "DE", "IN"]

        all_stocks = get_all_stocks(markets)
        total_stocks = sum(len(stocks) for stocks in all_stocks.values())

        print(f"\n{'='*60}")
        print(f"RANKING STOCKS FROM {len(markets)} MARKETS")
        print(f"{'='*60}")
        print(f"Total stocks to analyze: {total_stocks}")

        results = []
        processed = 0

        for market, stocks in all_stocks.items():
            print(f"\n📊 {MARKETS[market].name} ({len(stocks)} stocks)")

            for i, symbol in enumerate(stocks):
                processed += 1
                print(f"  [{market}] {symbol} ({i+1}/{len(stocks)})...", end="\r")

                data = self.analyze_stock(symbol)
                if data:
                    results.append(data)

                time.sleep(0.1)

            print()

        print(f"\n✓ Analyzed {len(results)} valid stocks out of {total_stocks}")

        if not results:
            return pd.DataFrame()

        # Create DataFrame
        df = pd.DataFrame(results)

        # Calculate composite score
        df = self._calculate_composite_score(df)

        # Sort by composite score within each market
        df = df.sort_values(["market", "composite_score"], ascending=[True, False])

        # Save full rankings
        df.to_csv(RANKINGS_FILE, index=False)
        print(f"✓ Rankings saved to {RANKINGS_FILE}")

        self.ranked_stocks = df

        # Select top N per market
        self.trading_universe = {}

        for market in markets:
            market_df = df[df["market"] == market]
            top_stocks = market_df.head(top_n_per_market)["symbol"].tolist()
            self.trading_universe[market] = top_stocks
            print(f"  {MARKETS[market].name}: Top {len(top_stocks)} selected")

        return df

    def _calculate_composite_score(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate composite score for ranking"""
        df = df.copy()

        # Normalize within each market (different scales)
        def normalize(series):
            min_val = series.min()
            max_val = series.max()
            if max_val == min_val:
                return pd.Series([50] * len(series), index=series.index)
            return ((series - min_val) / (max_val - min_val)) * 100

        # Group by market and normalize
        for market in df["market"].unique():
            mask = df["market"] == market

            df.loc[mask, "momentum_20d_norm"] = normalize(df.loc[mask, "momentum_20d"])
            df.loc[mask, "momentum_5d_norm"] = normalize(df.loc[mask, "momentum_5d"])
            df.loc[mask, "returns_3m_norm"] = normalize(df.loc[mask, "returns_3m"])
            df.loc[mask, "rel_volume_norm"] = normalize(df.loc[mask, "rel_volume"])

        # ATR score (moderate is best)
        df["atr_score_norm"] = df["atr_pct"].apply(
            lambda x: 100 if 2 <= x <= 5 else (80 if 1.5 <= x <= 6 else (60 if 1 <= x <= 8 else 30))
        )

        # Calculate composite score
        df["composite_score"] = (
            df["momentum_20d_norm"] * self.weights["momentum_20d"] +
            df["momentum_5d_norm"] * self.weights["momentum_5d"] +
            df["returns_3m_norm"] * self.weights["returns_3m"] +
            df["rel_volume_norm"] * self.weights["rel_volume"] +
            df["atr_score_norm"] * self.weights["atr_score"] +
            df["trend_score"] * self.weights["trend_score"]
        )

        df["composite_score"] = df["composite_score"].round(2)

        return df

    def save_universe(self):
        """Save trading universe to file"""
        # Flatten for backward compatibility
        all_symbols = []
        for market, symbols in self.trading_universe.items():
            all_symbols.extend(symbols)

        data = {
            "updated_at": datetime.now().isoformat(),
            "markets": list(self.trading_universe.keys()),
            "universe_by_market": self.trading_universe,
            "trading_universe": all_symbols,  # Flat list for compatibility
            "counts": {market: len(symbols) for market, symbols in self.trading_universe.items()},
        }

        with open(UNIVERSE_FILE, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"✓ Universe saved to {UNIVERSE_FILE}")

    def load_universe(self) -> Dict[str, List[str]]:
        """Load trading universe from file"""
        if not UNIVERSE_FILE.exists():
            print("No saved universe found. Run update_universe() first.")
            return {}

        with open(UNIVERSE_FILE, 'r') as f:
            data = json.load(f)

        self.trading_universe = data.get("universe_by_market", {})

        print(f"✓ Loaded universe:")
        for market, symbols in self.trading_universe.items():
            print(f"  {MARKETS[market].name}: {len(symbols)} stocks")

        return self.trading_universe

    def get_flat_universe(self) -> List[str]:
        """Get flat list of all stocks in universe"""
        if not self.trading_universe:
            self.load_universe()

        all_symbols = []
        for symbols in self.trading_universe.values():
            all_symbols.extend(symbols)

        return all_symbols

    def update_universe(self, markets: List[str] = None,
                       top_n_per_market: int = 20) -> Dict[str, List[str]]:
        """
        Full universe update
        """
        if markets is None:
            markets = ["US", "DE", "IN"]

        print("\n" + "=" * 60)
        print("UPDATING GLOBAL TRADING UNIVERSE")
        print("=" * 60)
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print(f"Markets: {', '.join(markets)}")
        print(f"Top stocks per market: {top_n_per_market}")

        # Rank stocks
        self.rank_stocks(markets=markets, top_n_per_market=top_n_per_market)

        # Save universe
        self.save_universe()

        # Print summary
        print("\n" + "=" * 60)
        print("UPDATE COMPLETE")
        print("=" * 60)

        total = 0
        for market, symbols in self.trading_universe.items():
            total += len(symbols)
            print(f"\n📊 {MARKETS[market].name} - Top {len(symbols)} Stocks:")

            market_df = self.ranked_stocks[self.ranked_stocks["market"] == market]

            for i, symbol in enumerate(symbols[:5]):
                row = market_df[market_df["symbol"] == symbol].iloc[0]
                print(f"  {i+1}. {symbol:15} | Score: {row['composite_score']:5.1f} | "
                      f"Mom20: {row['momentum_20d']:+6.1f}% | 3M: {row['returns_3m']:+6.1f}%")

            if len(symbols) > 5:
                print(f"  ... and {len(symbols) - 5} more")

        print(f"\n✓ Total stocks in universe: {total}")

        return self.trading_universe

    def quick_update(self, markets: List[str] = None,
                    top_n_per_market: int = 50) -> Dict[str, List[str]]:
        """
        Quick update with fewer stocks
        """
        if markets is None:
            markets = ["US", "DE", "IN"]

        print("\n" + "=" * 60)
        print("QUICK GLOBAL UNIVERSE UPDATE")
        print("=" * 60)

        return self.update_universe(markets=markets, top_n_per_market=top_n_per_market)

    def get_market_report(self, market: str) -> pd.DataFrame:
        """Get detailed report for a specific market"""
        if self.ranked_stocks.empty:
            if RANKINGS_FILE.exists():
                self.ranked_stocks = pd.read_csv(RANKINGS_FILE)
            else:
                return pd.DataFrame()

        return self.ranked_stocks[self.ranked_stocks["market"] == market]

    def get_top_movers(self, market: str = None, n: int = 10) -> pd.DataFrame:
        """Get top momentum stocks"""
        if self.ranked_stocks.empty:
            return pd.DataFrame()

        df = self.ranked_stocks
        if market:
            df = df[df["market"] == market]

        return df.nlargest(n, "momentum_20d")[
            ["symbol", "name", "market", "price", "currency", "momentum_20d", "returns_3m", "composite_score"]
        ]

    def get_sector_breakdown(self, market: str = None) -> pd.DataFrame:
        """Get sector breakdown"""
        if self.ranked_stocks.empty:
            return pd.DataFrame()

        df = self.ranked_stocks
        if market:
            df = df[df["market"] == market]

        breakdown = df.groupby(["market", "sector"]).agg({
            "symbol": "count",
            "composite_score": "mean",
            "momentum_20d": "mean",
        }).round(2)

        breakdown.columns = ["count", "avg_score", "avg_momentum"]
        return breakdown.sort_values(["market", "count"], ascending=[True, False])

    def print_global_report(self):
        """Print comprehensive global report"""
        print("\n" + "=" * 70)
        print("GLOBAL TRADING UNIVERSE REPORT")
        print("=" * 70)

        if self.ranked_stocks.empty:
            if RANKINGS_FILE.exists():
                self.ranked_stocks = pd.read_csv(RANKINGS_FILE)
            else:
                print("No data. Run update_universe() first.")
                return

        # Summary
        print(f"\nTotal Stocks Analyzed: {len(self.ranked_stocks)}")

        for market in self.ranked_stocks["market"].unique():
            market_df = self.ranked_stocks[self.ranked_stocks["market"] == market]
            market_name = MARKETS[market].name
            currency = MARKETS[market].currency

            print(f"\n{'='*70}")
            print(f"📊 {market_name} ({market}) - {currency}")
            print(f"{'='*70}")
            print(f"Stocks analyzed: {len(market_df)}")

            # Top 10 stocks
            print(f"\nTop 10 Stocks:")
            top10 = market_df.head(10)
            print(top10[["symbol", "name", "sector", "price", "composite_score",
                        "momentum_20d", "returns_3m"]].to_string(index=False))

            # Top movers
            print(f"\nTop 5 Momentum (20-day):")
            movers = market_df.nlargest(5, "momentum_20d")
            print(movers[["symbol", "price", "momentum_20d", "returns_3m"]].to_string(index=False))


# ============================================================
# MAIN / CLI
# ============================================================

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Global Universe Manager")
    parser.add_argument("command", choices=["update", "quick", "show", "report"],
                       help="Command to run")
    parser.add_argument("--markets", "-m", nargs="+", default=["US", "DE", "IN"],
                       help="Markets to include (US, DE, IN)")
    parser.add_argument("--top", "-n", type=int, default=20,
                       help="Number of top stocks per market")

    args = parser.parse_args()

    um = GlobalUniverseManager()

    if args.command == "update":
        um.update_universe(markets=args.markets, top_n_per_market=args.top)
    elif args.command == "quick":
        um.quick_update(markets=args.markets, top_n_per_market=min(args.top, 15))
    elif args.command == "show":
        universe = um.load_universe()
        for market, symbols in universe.items():
            print(f"\n{MARKETS[market].name}:")
            for i, s in enumerate(symbols):
                print(f"  {i+1:2}. {s}")
    elif args.command == "report":
        um.load_universe()
        if RANKINGS_FILE.exists():
            um.ranked_stocks = pd.read_csv(RANKINGS_FILE)
        um.print_global_report()


if __name__ == "__main__":
    main()
