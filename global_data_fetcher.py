#!/usr/bin/env python3
"""
Global Data Fetcher - Fetches data from US, German, and Indian markets
"""

import yfinance as yf
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import time

from market_config import MARKETS, MarketInfo, get_all_stocks


class GlobalDataFetcher:
    """
    Fetches market data from multiple international markets
    Supports: US, Germany (XETRA), India (NSE/BSE)
    """

    def __init__(self):
        self.cache = {}
        self.cache_time = {}
        self.cache_duration = 300  # 5 minutes

    def detect_market(self, symbol: str) -> str:
        """Detect which market a symbol belongs to"""
        if symbol.endswith(".DE"):
            return "DE"
        elif symbol.endswith(".NS") or symbol.endswith(".BO"):
            return "IN"
        else:
            return "US"

    def get_market_info(self, symbol: str) -> MarketInfo:
        """Get market info for a symbol"""
        market_code = self.detect_market(symbol)
        return MARKETS[market_code]

    def get_stock_data(self, symbol: str, period: str = "6mo",
                       interval: str = "1d") -> pd.DataFrame:
        """
        Fetch OHLCV data for a stock from any market

        Args:
            symbol: Stock ticker (e.g., 'NVDA', 'SAP.DE', 'TCS.NS')
            period: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
            interval: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo

        Returns:
            DataFrame with OHLCV data
        """
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period, interval=interval)

            if df.empty:
                print(f"Warning: No data for {symbol}")
                return pd.DataFrame()

            # Standardize column names
            df.columns = [c.lower().replace(" ", "_") for c in df.columns]

            # Add metadata
            market = self.detect_market(symbol)
            df["symbol"] = symbol
            df["market"] = market
            df["currency"] = MARKETS[market].currency

            return df

        except Exception as e:
            print(f"Error fetching {symbol}: {e}")
            return pd.DataFrame()

    def get_stock_info(self, symbol: str) -> Dict:
        """Get fundamental info for a stock"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info

            market = self.detect_market(symbol)
            market_info = MARKETS[market]

            return {
                "symbol": symbol,
                "name": info.get("longName", info.get("shortName", symbol)),
                "sector": info.get("sector", "Unknown"),
                "industry": info.get("industry", "Unknown"),
                "market": market,
                "currency": market_info.currency,
                "market_cap": info.get("marketCap", 0),
                "market_cap_local": info.get("marketCap", 0),
                "avg_volume": info.get("averageVolume", 0),
                "beta": info.get("beta", 1.0),
                "pe_ratio": info.get("trailingPE", 0),
                "price": info.get("currentPrice", info.get("regularMarketPrice", 0)),
                "52w_high": info.get("fiftyTwoWeekHigh", 0),
                "52w_low": info.get("fiftyTwoWeekLow", 0),
                "dividend_yield": info.get("dividendYield", 0),
                "exchange": info.get("exchange", "Unknown"),
            }
        except Exception as e:
            return {"symbol": symbol, "market": self.detect_market(symbol), "error": str(e)}

    def get_multiple_stocks(self, symbols: List[str],
                           period: str = "6mo") -> Dict[str, pd.DataFrame]:
        """Fetch data for multiple stocks (any market)"""
        data = {}
        total = len(symbols)

        for i, symbol in enumerate(symbols):
            market = self.detect_market(symbol)
            print(f"  [{market}] Fetching {symbol} ({i+1}/{total})...", end="\r")

            df = self.get_stock_data(symbol, period)
            if not df.empty:
                data[symbol] = df

            time.sleep(0.1)  # Rate limiting

        print()
        return data

    def get_current_price(self, symbol: str) -> Tuple[float, str]:
        """Get current price and currency"""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="1d")

            if not data.empty:
                price = float(data["Close"].iloc[-1])
                market = self.detect_market(symbol)
                currency = MARKETS[market].currency
                return price, currency

            return 0.0, "USD"
        except Exception as e:
            print(f"Warning: Could not get price for {symbol}: {e}")
            return 0.0, "USD"

    def get_market_summary(self, market: str = "US") -> Dict:
        """Get market indices summary"""
        indices = {
            "US": ["^GSPC", "^IXIC", "^DJI"],      # S&P 500, NASDAQ, Dow Jones
            "DE": ["^GDAXI", "^MDAXI"],             # DAX, MDAX
            "IN": ["^NSEI", "^BSESN"],              # NIFTY 50, SENSEX
        }

        summary = {}

        for idx in indices.get(market, []):
            try:
                ticker = yf.Ticker(idx)
                hist = ticker.history(period="2d")

                if len(hist) >= 2:
                    current = hist["Close"].iloc[-1]
                    prev = hist["Close"].iloc[-2]
                    change = ((current - prev) / prev) * 100

                    summary[idx] = {
                        "price": round(current, 2),
                        "change_pct": round(change, 2),
                    }
            except Exception as e:
                print(f"Warning: Could not get data for index {idx}: {e}")

        return summary

    def convert_to_usd(self, amount: float, currency: str) -> float:
        """Convert amount to USD"""
        rates = {
            "USD": 1.0,
            "EUR": 1.08,
            "INR": 0.012,
        }
        return amount * rates.get(currency, 1.0)

    def get_exchange_rates(self) -> Dict[str, float]:
        """Get current exchange rates to USD"""
        pairs = {
            "EUR": "EURUSD=X",
            "INR": "USDINR=X",
        }

        rates = {"USD": 1.0}

        for currency, pair in pairs.items():
            try:
                ticker = yf.Ticker(pair)
                hist = ticker.history(period="1d")

                if not hist.empty:
                    rate = hist["Close"].iloc[-1]

                    if currency == "EUR":
                        rates["EUR"] = rate  # EUR/USD
                    elif currency == "INR":
                        rates["INR"] = 1 / rate  # USD/INR -> INR/USD
            except Exception as e:
                # Use defaults
                print(f"Warning: Could not get exchange rate for {currency}: {e}")
                rates["EUR"] = 1.08
                rates["INR"] = 0.012

        return rates


# ============================================================
# MAIN / TEST
# ============================================================

if __name__ == "__main__":
    fetcher = GlobalDataFetcher()

    print("=" * 70)
    print("GLOBAL DATA FETCHER TEST")
    print("=" * 70)

    # Test stocks from each market
    test_stocks = [
        "NVDA",        # US
        "SAP.DE",      # Germany
        "TCS.NS",      # India
    ]

    for symbol in test_stocks:
        print(f"\n{'='*50}")
        print(f"Testing: {symbol}")
        print(f"{'='*50}")

        # Get data
        df = fetcher.get_stock_data(symbol, period="1mo")
        print(f"  Data rows: {len(df)}")

        if not df.empty:
            print(f"  Market: {df['market'].iloc[0]}")
            print(f"  Currency: {df['currency'].iloc[0]}")
            print(f"  Latest close: {df['close'].iloc[-1]:.2f}")

        # Get info
        info = fetcher.get_stock_info(symbol)
        print(f"  Name: {info.get('name', 'N/A')}")
        print(f"  Sector: {info.get('sector', 'N/A')}")
        print(f"  Market Cap: {info.get('market_cap', 0):,.0f} {info.get('currency', '')}")

    # Exchange rates
    print(f"\n{'='*50}")
    print("EXCHANGE RATES")
    print(f"{'='*50}")

    rates = fetcher.get_exchange_rates()
    for currency, rate in rates.items():
        print(f"  {currency}/USD: {rate:.4f}")

    # Market summaries
    print(f"\n{'='*50}")
    print("MARKET SUMMARIES")
    print(f"{'='*50}")

    for market in ["US", "DE", "IN"]:
        print(f"\n  {market}:")
        summary = fetcher.get_market_summary(market)
        for idx, data in summary.items():
            print(f"    {idx}: {data['price']:,.2f} ({data['change_pct']:+.2f}%)")
