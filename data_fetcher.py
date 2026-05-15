"""Data Fetcher - Gets market data from Yahoo Finance"""

import yfinance as yf
import pandas as pd
from typing import Dict, List
import time


class DataFetcher:
    """Fetches market data"""

    def get_stock_data(self, symbol: str, period: str = "6mo", interval: str = "1d") -> pd.DataFrame:
        """Get OHLCV data"""
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period, interval=interval)

            if df.empty:
                return pd.DataFrame()

            df.columns = [c.lower().replace(" ", "_") for c in df.columns]
            df["symbol"] = symbol
            return df
        except Exception as e:
            print(f"Error fetching {symbol}: {e}")
            return pd.DataFrame()

    def get_multiple_stocks(self, symbols: List[str], period: str = "6mo") -> Dict[str, pd.DataFrame]:
        """Get data for multiple stocks"""
        data = {}
        for i, symbol in enumerate(symbols):
            print(f"  Fetching {symbol} ({i+1}/{len(symbols)})...", end="\r")
            df = self.get_stock_data(symbol, period)
            if not df.empty:
                data[symbol] = df
            time.sleep(0.1)
        print()
        return data

    def get_stock_info(self, symbol: str) -> Dict:
        """Get fundamental info"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            return {
                "symbol": symbol,
                "name": info.get("longName", symbol),
                "sector": info.get("sector", "Unknown"),
                "market_cap": info.get("marketCap", 0),
                "avg_volume": info.get("averageVolume", 0),
                "beta": info.get("beta", 1.0),
                "price": info.get("currentPrice", info.get("regularMarketPrice", 0)),
            }
        except:
            return {"symbol": symbol}

    def get_current_price(self, symbol: str) -> float:
        """Get current price"""
        try:
            df = self.get_stock_data(symbol, period="1d")
            return float(df["close"].iloc[-1]) if not df.empty else 0.0
        except:
            return 0.0


if __name__ == "__main__":
    fetcher = DataFetcher()
    df = fetcher.get_stock_data("NVDA", "3mo")
    print(f"NVDA: {len(df)} rows")
    print(df.tail())
