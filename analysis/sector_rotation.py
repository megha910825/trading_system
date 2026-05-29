#!/usr/bin/env python3
"""
Sector Rotation Module
Ranks US sector ETFs by relative strength vs SPY.
Used to prioritise signals from outperforming sectors.
"""

from __future__ import annotations

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List

# ── Sector ETF universes (per market) ──────────────────────────────────────────
# US sector SPDR ETFs — benchmark SPY
SECTOR_ETFS: Dict[str, str] = {
    "XLK":  "Technology",
    "XLF":  "Financials",
    "XLE":  "Energy",
    "XLV":  "Health Care",
    "XLI":  "Industrials",
    "XLY":  "Consumer Discretionary",
    "XLP":  "Consumer Staples",
    "XLB":  "Materials",
    "XLC":  "Communication Services",
    "XLRE": "Real Estate",
    "XLU":  "Utilities",
}

# German / European sector ETFs (STOXX Europe 600 iShares, XETRA) — benchmark EXS1.DE (Core DAX)
DE_SECTOR_ETFS: Dict[str, str] = {
    "EXV3.DE": "Technology",
    "EXV1.DE": "Banks",
    "EXV4.DE": "Health Care",
    "EXV7.DE": "Industrials",
    "EXV6.DE": "Oil & Gas",
    "EXV2.DE": "Retail / Consumer",
    "EXH8.DE": "Utilities",
    "EXV5.DE": "Basic Materials",
    "EXV9.DE": "Autos & Parts",
    "EXXT.DE": "Technology (STOXX)",
}

# Indian sector ETFs (NSE, Nippon India ETF series) — benchmark NIFTYBEES.NS
IN_SECTOR_ETFS: Dict[str, str] = {
    "BANKBEES.NS":   "Banking",
    "ITBEES.NS":     "IT / Technology",
    "PSUBNKBEES.NS": "PSU Banks",
    "PHARMABEES.NS": "Pharma & Healthcare",
    "AUTOBEES.NS":   "Auto",
    "INFRABEES.NS":  "Infrastructure",
    "CONSUMBEES.NS": "FMCG / Consumer",
    "MOM100.NS":     "Momentum 100",
}

# Per-market config: (etf_dict, benchmark)
MARKET_CONFIG: Dict[str, tuple] = {
    "US": (SECTOR_ETFS, "SPY"),
    "DE": (DE_SECTOR_ETFS, "EXS1.DE"),
    "IN": (IN_SECTOR_ETFS, "NIFTYBEES.NS"),
}

BENCHMARK = "SPY"  # kept for backward compatibility

# Periods to score (days)
PERIODS = {
    "1w":  5,
    "1mo": 21,
    "3mo": 63,
}

# Weights for composite score
WEIGHTS = {"1w": 0.20, "1mo": 0.40, "3mo": 0.40}


class SectorRotation:
    """Ranks sectors by relative strength and returns actionable rotation signals."""

    def __init__(self):
        self._data: Dict[str, pd.DataFrame] = {}
        self.rankings: pd.DataFrame = pd.DataFrame()
        self.last_updated: datetime | None = None

    # ── Data loading ───────────────────────────────────────────────────────────
    def _fetch(self, tickers: List[str], period: str = "6mo") -> Dict[str, pd.Series]:
        """Fetch adjusted close prices for a list of tickers."""
        import yfinance as yf

        raw = yf.download(tickers, period=period, auto_adjust=True, progress=False)
        if isinstance(raw.columns, pd.MultiIndex):
            closes = raw["Close"]
        else:
            closes = raw[["Close"]] if "Close" in raw.columns else raw

        result = {}
        for t in tickers:
            if t in closes.columns:
                result[t] = closes[t].dropna()
        return result

    # ── Core calculation ───────────────────────────────────────────────────────
    def _returns(self, series: pd.Series, days: int) -> float:
        """Return % return over last `days` trading days."""
        if len(series) < days + 1:
            return np.nan
        return (series.iloc[-1] / series.iloc[-days - 1] - 1) * 100

    def compute_rankings(self, market: str = "US") -> pd.DataFrame:
        """
        Fetch data and compute relative-strength rankings.
        Returns a DataFrame ranked best → worst sector.

        Parameters
        ----------
        market : "US" | "DE" | "IN"  (default "US")
        """
        etf_dict, benchmark = MARKET_CONFIG.get(market, (SECTOR_ETFS, BENCHMARK))
        all_tickers = list(etf_dict.keys()) + [benchmark]
        prices = self._fetch(all_tickers)

        if benchmark not in prices:
            raise RuntimeError(
                f"Failed to fetch benchmark {benchmark} for market {market}. "
                "Check your internet connection or try again in a few minutes."
            )

        spy = prices[benchmark]

        rows = []
        for etf, sector_name in etf_dict.items():
            if etf not in prices:
                continue

            etf_prices = prices[etf]
            row: Dict = {"etf": etf, "sector": sector_name}

            composite = 0.0
            weight_sum = 0.0

            for label, days in PERIODS.items():
                etf_ret = self._returns(etf_prices, days)
                spy_ret = self._returns(spy, days)

                if np.isnan(etf_ret) or np.isnan(spy_ret):
                    continue

                relative = etf_ret - spy_ret        # excess return vs benchmark
                row[f"ret_{label}"] = round(etf_ret, 2)
                row[f"rel_{label}"] = round(relative, 2)

                composite += relative * WEIGHTS[label]
                weight_sum += WEIGHTS[label]

            row["composite_score"] = round(composite / weight_sum, 2) if weight_sum else np.nan

            # Latest price & 52w high drawdown
            row["price"] = round(float(etf_prices.iloc[-1]), 2)
            hi52 = float(etf_prices.tail(252).max()) if len(etf_prices) >= 252 else float(etf_prices.max())
            row["pct_from_52wk_hi"] = round((etf_prices.iloc[-1] / hi52 - 1) * 100, 1)

            rows.append(row)

        df = pd.DataFrame(rows)
        if df.empty:
            self.rankings = df
            return df

        df.sort_values("composite_score", ascending=False, inplace=True)
        df.reset_index(drop=True, inplace=True)
        df.insert(0, "rank", range(1, len(df) + 1))

        # Classify rotation phase
        df["signal"] = df["composite_score"].apply(self._classify)

        self.rankings = df
        self.last_updated = datetime.now()
        return df

    @staticmethod
    def _classify(score: float) -> str:
        if pd.isna(score):
            return "UNKNOWN"
        if score >= 3:
            return "LEADING ✅"
        if score >= 0:
            return "IMPROVING 🟡"
        if score >= -3:
            return "LAGGING 🟠"
        return "WEAKEST ❌"

    # ── Helper accessors ───────────────────────────────────────────────────────
    def get_top_sectors(self, n: int = 3) -> List[str]:
        """Return names of top-n sectors by composite score."""
        if self.rankings.empty:
            self.compute_rankings()
        return self.rankings.head(n)["sector"].tolist()

    def get_sector_score(self, sector_name: str) -> float | None:
        """Return composite score for a given sector name."""
        if self.rankings.empty:
            self.compute_rankings()
        row = self.rankings[self.rankings["sector"] == sector_name]
        if row.empty:
            return None
        return float(row.iloc[0]["composite_score"])

    def is_sector_leading(self, sector_name: str) -> bool:
        """True if sector is outperforming the benchmark."""
        score = self.get_sector_score(sector_name)
        return score is not None and score >= 0

    def print_rankings(self):
        """Pretty-print sector rankings to console."""
        df = self.rankings if not self.rankings.empty else self.compute_rankings()

        print("\n" + "=" * 72)
        print("  SECTOR ROTATION RANKINGS  (Relative Strength vs SPY)")
        print("=" * 72)
        print(f"  {'Rank':<5} {'ETF':<6} {'Sector':<26} {'1W':>6} {'1Mo':>6} {'3Mo':>6} {'Score':>7} Status")
        print("-" * 72)

        for _, r in df.iterrows():
            print(
                f"  {int(r['rank']):<5} {r['etf']:<6} {r['sector']:<26} "
                f"{r.get('rel_1w', 0):>+6.1f} {r.get('rel_1mo', 0):>+6.1f} "
                f"{r.get('rel_3mo', 0):>+6.1f} {r['composite_score']:>+7.2f}  {r['signal']}"
            )

        ts = self.last_updated.strftime("%Y-%m-%d %H:%M") if self.last_updated else "N/A"
        print(f"\n  Updated: {ts}")
        print("=" * 72)


# ── Convenience function ───────────────────────────────────────────────────────
def get_sector_rankings(market: str = "US") -> pd.DataFrame:
    """Convenience: fetch and return sector rankings DataFrame."""
    return SectorRotation().compute_rankings(market=market)


if __name__ == "__main__":
    sr = SectorRotation()
    sr.compute_rankings()
    sr.print_rankings()
    print("\nTop 3 sectors:", sr.get_top_sectors(3))
