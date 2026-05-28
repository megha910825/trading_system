"""Stock Screener - Filters stocks by criteria"""

import pandas as pd
from typing import List, Dict
from data_fetcher import DataFetcher
from technical_analyzer import TechnicalAnalyzer
import config


class StockScreener:
    """Screens stocks for trading"""

    def __init__(self):
        self.fetcher = DataFetcher()
        self.analyzer = TechnicalAnalyzer()
        self.criteria = config.SCREENING_CRITERIA

    def screen_stocks(self, symbols: List[str] = None) -> pd.DataFrame:
        """Screen stocks"""
        if symbols is None:
            symbols = config.STOCK_UNIVERSE

        results = []
        print(f"Screening {len(symbols)} stocks...")

        for i, symbol in enumerate(symbols):
            print(f"  {symbol} ({i+1}/{len(symbols)})...", end="\r")

            try:
                df = self.fetcher.get_stock_data(symbol, "6mo")
                if df.empty or len(df) < 50:
                    continue

                info = self.fetcher.get_stock_info(symbol)
                analysis = self.analyzer.analyze_stock(df, symbol)

                if "error" in analysis:
                    continue

                stock = {
                    "symbol": symbol,
                    "name": info.get("name", "N/A"),
                    "sector": info.get("sector", "N/A"),
                    "market_cap": info.get("market_cap", 0),
                    "avg_volume": info.get("avg_volume", 0),
                    **analysis
                }

                passed, count = self._check_criteria(stock, info)
                stock["criteria_passed"] = count
                stock["qualified"] = passed
                results.append(stock)
            except:
                continue

        print()
        df = pd.DataFrame(results)
        if not df.empty:
            df = df.sort_values("signal_score", ascending=False)

        qualified = len(df[df["qualified"]]) if not df.empty else 0
        print(f"Found {qualified} qualified stocks")
        return df

    def _check_criteria(self, stock: Dict, info: Dict) -> tuple:
        """Check screening criteria"""
        c = self.criteria
        passed = 0

        if info.get("market_cap", 0) >= c["min_market_cap"]: passed += 1
        if info.get("avg_volume", 0) >= c["min_avg_volume"]: passed += 1

        atr = stock.get("atr_pct", 0)
        if c["min_atr_pct"] <= atr <= c["max_atr_pct"]: passed += 1

        rsi = stock.get("rsi", 50)
        if c["min_rsi"] <= rsi <= c["max_rsi"]: passed += 1

        if stock.get("uptrend", False): passed += 1
        if stock.get("rel_volume", 0) >= c["min_rel_volume"]: passed += 1
        if stock.get("risk_reward", 0) >= 2.0: passed += 1

        return passed >= 5, passed

    def get_top_signals(self, n: int = 10) -> pd.DataFrame:
        """Get top signals"""
        df = self.screen_stocks()
        return df[df["qualified"]].head(n)


if __name__ == "__main__":
    screener = StockScreener()
    results = screener.screen_stocks(["NVDA", "AMD", "AAPL", "MSFT", "META"])
    print(results[["symbol", "signal_score", "signal_status", "qualified"]])
