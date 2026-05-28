#!/usr/bin/env python3
"""
Weekend Investing Strategy — inspired by Alok Jain's momentum framework
weekendinvesting.com

Strategy families implemented
───────────────────────────────────────────────────────────────────────────────
Mi-Top10   : Top 10 stocks from Nifty-50 universe  (weekly rebalance)
Mi-NNF10   : Top 10 stocks from Nifty Next-50      (weekly rebalance)
Mi-EverGreen: Top 20 stocks from CNX-200            (weekly rebalance)
Mi-20      : Top 20 from MidSmall-400 universe     (weekly rebalance)
Mi-25      : Top 25 from Smallcap-250 + ABSOLUTE momentum cash filter (monthly)
Mi-30      : Top 30 from CNX-500    + ABSOLUTE momentum cash filter (monthly)
Mi-35      : Top 35 from Smallcap-250               (weekly rebalance)
Mi-ST-ATH  : Top 15 stocks near 52-week All-Time-High             (weekly)

Rules common to all strategies
───────────────────────────────────────────────────────────────────────────────
MOMENTUM SCORE = equal-weight average of ROC across 4 lookback windows
  (1-month / 3-month / 6-month / 12-month) — then optionally risk-adjusted.
  Optionally the 1-month component is EXCLUDED (12-1 momentum) to avoid the
  short-term reversal effect.

ENTRY  : At the NEXT market open after the rebalancing signal is generated
         (Friday close → Monday open, or last trading day → first trading day).
         Buy equal-weight allocation in each new entrant.

EXIT   : Sell any stock that drops OUT of the top-N ranking at rebalancing.
         NO stop-loss is used during the holding period — momentum carries the
         position until the next scheduled rebalancing.

ABSOLUTE MOMENTUM (Mi-25 / Mi-30 / Mi-MT variants)
         If a stock's 6-month return is negative → allocate that slot to CASH
         (or a liquid fund proxy such as LIQUIDBEES.NS).

ATH FILTER (Mi-ST-ATH / Mi-ATH2)
         Only consider stocks trading within `ath_threshold` % of their
         52-week high.

POSITION SIZING : Equal weight  →  allocation_per_stock = capital / N
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import yfinance as yf


# ═══════════════════════════════════════════════════════════════════════════════
# UNIVERSE DEFINITIONS
# ═══════════════════════════════════════════════════════════════════════════════

# Nifty-50 (large cap)
NIFTY50 = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS",
    "HINDUNILVR.NS", "ITC.NS", "SBIN.NS", "BHARTIARTL.NS", "KOTAKBANK.NS",
    "LT.NS", "AXISBANK.NS", "ASIANPAINT.NS", "MARUTI.NS", "HCLTECH.NS",
    "SUNPHARMA.NS", "TITAN.NS", "WIPRO.NS", "BAJFINANCE.NS", "ULTRACEMCO.NS",
    "TATAMOTORS.NS", "ONGC.NS", "NTPC.NS", "POWERGRID.NS", "M&M.NS",
    "TATASTEEL.NS", "JSWSTEEL.NS", "ADANIENT.NS", "ADANIPORTS.NS", "COALINDIA.NS",
    "TECHM.NS", "NESTLEIND.NS", "DRREDDY.NS", "CIPLA.NS", "DIVISLAB.NS",
    "GRASIM.NS", "BRITANNIA.NS", "BAJAJFINSV.NS", "HEROMOTOCO.NS", "EICHERMOT.NS",
    "INDUSINDBK.NS", "APOLLOHOSP.NS", "HDFCLIFE.NS", "SBILIFE.NS", "TATACONSUM.NS",
    "BPCL.NS", "HINDALCO.NS", "UPL.NS", "SHRIRAMFIN.NS", "BAJAJ-AUTO.NS",
]

# Nifty Next-50
NIFTY_NEXT50 = [
    "ZOMATO.NS", "DMART.NS", "PIIND.NS", "PERSISTENT.NS", "LTIM.NS",
    "MPHASIS.NS", "COFORGE.NS", "TRENT.NS", "POLYCAB.NS", "DIXON.NS",
    "IRCTC.NS", "HAL.NS", "BEL.NS", "PFC.NS", "RECLTD.NS", "RVNL.NS",
    "HAVELLS.NS", "BERGEPAINT.NS", "DABUR.NS", "MARICO.NS", "COLPAL.NS",
    "PIDILITIND.NS", "TORNTPHARM.NS", "MCDOWELL-N.NS", "VEDL.NS",
    "TATAPOWER.NS", "SIEMENS.NS", "ABB.NS", "AMBUJACEM.NS", "SHREECEM.NS",
    "NAUKRI.NS", "INDIGO.NS", "SRF.NS", "CUMMINSIND.NS", "VOLTAS.NS",
    "TVSMOTOR.NS", "BAJAJHLDNG.NS", "GAIL.NS", "NHPC.NS", "CONCOR.NS",
    "OBEROIRLTY.NS", "GODREJCP.NS", "MUTHOOTFIN.NS", "CHOLAFIN.NS",
    "BANDHANBNK.NS", "IDFCFIRSTB.NS", "FEDERALBNK.NS", "ABCAPITAL.NS",
    "ATGL.NS", "TORNTPOWER.NS",
]

# Additional Mid & Small-Cap stocks (Smallcap 250 proxy)
SMALLCAP250 = [
    "ANGELONE.NS", "BIKAJI.NS", "CAMPUS.NS", "DATAPATTNS.NS", "EASEMYTRIP.NS",
    "FIVESTAR.NS", "GLENMARK.NS", "HAPPSTMNDS.NS", "IIFLSEC.NS", "JKCEMENT.NS",
    "KPITTECH.NS", "LATENTVIEW.NS", "MAHSEAMLES.NS", "NAZARA.NS", "ORIENTELEC.NS",
    "PAYTM.NS", "QUESS.NS", "RBLBANK.NS", "SAFARI.NS", "TANLA.NS",
    "UJJIVANSFB.NS", "VBL.NS", "WELCORP.NS", "XCHANGING.NS", "YATHARTH.NS",
    "ZEEL.NS", "ROUTE.NS", "IDEAFORGE.NS", "CAMS.NS", "CDSL.NS",
    "NETWORK18.NS", "NAVINFLUOR.NS", "SUNTV.NS", "BALRAMCHIN.NS", "RENUKA.NS",
    "GMRINFRA.NS", "INOXGREEN.NS", "IRCON.NS", "NLCINDIA.NS", "SJVN.NS",
    "HFCL.NS", "RAILTEL.NS", "MAZDOCK.NS", "COCHINSHIP.NS", "GRSE.NS",
    "APLAPOLLO.NS", "JINDALSAW.NS", "RATNAMANI.NS", "WELSPUNIND.NS",
    "SCHNEIDER.NS", "KAYNES.NS", "SYRMA.NS", "AMBER.NS", "WABCOINDIA.NS",
]

# Full CNX-500 proxy (Nifty50 + NiftyNext50 + Smallcap)
CNX500 = list(dict.fromkeys(NIFTY50 + NIFTY_NEXT50 + SMALLCAP250))

# CNX-200 proxy
CNX200 = list(dict.fromkeys(NIFTY50 + NIFTY_NEXT50))

# MidSmall-400 (101st–500th) proxy
MIDSMALL400 = list(dict.fromkeys(NIFTY_NEXT50 + SMALLCAP250))

# Liquid fund proxy for cash slot in absolute-momentum strategies
CASH_PROXY = "LIQUIDBEES.NS"


# ═══════════════════════════════════════════════════════════════════════════════
# STRATEGY PRESETS
# ═══════════════════════════════════════════════════════════════════════════════

STRATEGY_PRESETS: Dict[str, dict] = {
    "Mi-Top10": {
        "label":              "Mi India Top 10",
        "universe":           NIFTY50,
        "top_n":              10,
        "rebalance":          "weekly",
        "absolute_momentum":  False,
        "ath_filter":         False,
        "risk_adjusted":      False,
        "exclude_last_month": False,
        "description":        "Top 10 momentum stocks from Nifty-50. Always invested, no cash.",
    },
    "Mi-NNF10": {
        "label":              "Mi NNF 10",
        "universe":           NIFTY_NEXT50,
        "top_n":              10,
        "rebalance":          "weekly",
        "absolute_momentum":  False,
        "ath_filter":         False,
        "risk_adjusted":      False,
        "exclude_last_month": False,
        "description":        "Top 10 momentum stocks from Nifty Next-50.",
    },
    "Mi-EverGreen": {
        "label":              "Mi EverGreen",
        "universe":           CNX200,
        "top_n":              20,
        "rebalance":          "weekly",
        "absolute_momentum":  False,
        "ath_filter":         False,
        "risk_adjusted":      True,
        "exclude_last_month": True,
        "description":        "Top 20 risk-adjusted momentum stocks from CNX-200. Core strategy.",
    },
    "Mi-20": {
        "label":              "Mi 20",
        "universe":           MIDSMALL400,
        "top_n":              20,
        "rebalance":          "weekly",
        "absolute_momentum":  False,
        "ath_filter":         False,
        "risk_adjusted":      False,
        "exclude_last_month": False,
        "description":        "Top 20 from Mid-Small cap 400. Higher volatility, higher potential.",
    },
    "Mi-25": {
        "label":              "Mi 25",
        "universe":           SMALLCAP250,
        "top_n":              25,
        "rebalance":          "monthly",
        "absolute_momentum":  True,   # go to cash if 6M return < 0
        "ath_filter":         False,
        "risk_adjusted":      False,
        "exclude_last_month": False,
        "description":        "Top 25 from Smallcap-250. Absolute momentum — goes to cash in weak markets.",
    },
    "Mi-30": {
        "label":              "Mi 30",
        "universe":           CNX500,
        "top_n":              30,
        "rebalance":          "monthly",
        "absolute_momentum":  True,
        "ath_filter":         False,
        "risk_adjusted":      False,
        "exclude_last_month": False,
        "description":        "Top 30 from CNX-500. Absolute momentum — goes to cash in weak markets.",
    },
    "Mi-35": {
        "label":              "Mi 35",
        "universe":           SMALLCAP250,
        "top_n":              35,
        "rebalance":          "weekly",
        "absolute_momentum":  False,
        "ath_filter":         False,
        "risk_adjusted":      False,
        "exclude_last_month": False,
        "description":        "Top 35 from Smallcap-250. Always invested, weekly rebalance.",
    },
    "Mi-ST-ATH": {
        "label":              "Mi ST ATH",
        "universe":           CNX500,
        "top_n":              15,
        "rebalance":          "weekly",
        "absolute_momentum":  False,
        "ath_filter":         True,   # only stocks ≤ ath_threshold% below 52-wk high
        "ath_threshold":      10.0,   # within 10% of 52-week high
        "risk_adjusted":      False,
        "exclude_last_month": False,
        "description":        "Top 15 stocks near 52-week ATH. Chases strongest breakouts.",
    },
}


# ═══════════════════════════════════════════════════════════════════════════════
# DATA CLASSES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class StockMomentum:
    """Momentum data for a single stock"""
    symbol:         str
    name:           str
    current_price:  float
    momentum_1m:    float   # 1-month ROC %
    momentum_3m:    float   # 3-month ROC %
    momentum_6m:    float   # 6-month ROC %
    momentum_12m:   float   # 12-month ROC %
    composite_score: float  # final ranking score
    high_52w:       float
    pct_from_ath:   float   # % below 52-week high (negative = below ATH)
    volatility:     float   # annualised stddev of daily returns
    avg_volume:     float
    is_cash_slot:   bool = False   # True when absolute-momentum sends to cash


@dataclass
class PortfolioSlot:
    """One position slot in the rebalanced portfolio"""
    rank:           int
    symbol:         str
    name:           str
    action:         str     # HOLD | BUY | SELL | CASH
    entry_price:    float
    weight_pct:     float
    capital_amount: float
    momentum_score: float
    pct_from_ath:   float
    momentum_6m:    float


@dataclass
class RebalanceResult:
    """Full result of one rebalancing run"""
    strategy:       str
    strategy_label: str
    rebalance_date: str
    next_action_date: str
    portfolio:      List[PortfolioSlot]
    exits:          List[str]           # symbols to sell
    entries:        List[str]           # symbols to buy
    cash_pct:       float               # % of capital in cash
    universe_size:  int
    scored_count:   int
    errors:         List[str]


# ═══════════════════════════════════════════════════════════════════════════════
# CORE ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

class WeekendInvestingStrategy:
    """
    Alok Jain's Weekend Investing momentum engine.

    Usage
    ─────
    engine = WeekendInvestingStrategy()
    result = engine.run("Mi-35", capital=500_000)
    engine.print_report(result)
    """

    # Lookback windows (trading days ≈ calendar approximations via yfinance)
    PERIODS = {
        "1m":  21,
        "3m":  63,
        "6m":  126,
        "12m": 252,
    }

    def __init__(self, fetch_delay: float = 0.5):
        self._delay = fetch_delay
        self._cache: Dict[str, pd.DataFrame] = {}

    # ── Data fetching ────────────────────────────────────────────────────────

    def _get_prices(self, symbol: str) -> pd.DataFrame:
        """Fetch 15-month daily close (cached per session)."""
        if symbol in self._cache:
            return self._cache[symbol]
        try:
            df = yf.Ticker(symbol).history(period="15mo")
            if not df.empty:
                df.index = pd.to_datetime(df.index).tz_localize(None)
                df.columns = df.columns.str.lower()
            self._cache[symbol] = df
            time.sleep(self._delay)
        except Exception:
            self._cache[symbol] = pd.DataFrame()
        return self._cache[symbol]

    # ── Momentum scoring ─────────────────────────────────────────────────────

    def _score_stock(
        self,
        symbol: str,
        exclude_last_month: bool = False,
        risk_adjusted: bool = False,
        ath_filter: bool = False,
        ath_threshold: float = 10.0,
    ) -> Optional[StockMomentum]:
        """Compute momentum score for one symbol. Returns None on failure."""
        df = self._get_prices(symbol)
        if df.empty or len(df) < self.PERIODS["12m"] + 5:
            return None

        closes = df["close"]
        cur = closes.iloc[-1]

        def roc(days: int) -> float:
            """Rate of change over `days` bars."""
            if len(closes) <= days:
                return 0.0
            ref = closes.iloc[-(days + 1)]
            return ((cur - ref) / ref) * 100 if ref > 0 else 0.0

        m1  = roc(self.PERIODS["1m"])
        m3  = roc(self.PERIODS["3m"])
        m6  = roc(self.PERIODS["6m"])
        m12 = roc(self.PERIODS["12m"])

        # 12-1 momentum: drop the most-recent 1-month to avoid reversal
        if exclude_last_month:
            components = [m3, m6, m12]
        else:
            components = [m1, m3, m6, m12]

        raw_score = float(np.mean(components))

        # Risk-adjusted: divide by annualised volatility
        if risk_adjusted:
            daily_rets = closes.pct_change().dropna().tail(252)
            vol = float(daily_rets.std() * np.sqrt(252) * 100)
            composite = raw_score / vol if vol > 0 else raw_score
        else:
            composite = raw_score

        # 52-week high stats
        high_52w    = float(df["high"].tail(252).max()) if "high" in df.columns else cur
        pct_from_ath = ((cur - high_52w) / high_52w) * 100  # negative means below

        # ATH filter gate
        if ath_filter and abs(pct_from_ath) > ath_threshold:
            return None

        # Average daily volume
        avg_vol = float(df["volume"].tail(20).mean()) if "volume" in df.columns else 0

        # Annualised volatility (for display)
        vol_pct = float(closes.pct_change().dropna().tail(252).std() * np.sqrt(252) * 100)

        # Try to get a human name
        try:
            info = yf.Ticker(symbol).fast_info
            name = getattr(info, "long_name", symbol) or symbol
        except Exception:
            name = symbol

        return StockMomentum(
            symbol=symbol,
            name=name,
            current_price=round(cur, 2),
            momentum_1m=round(m1, 2),
            momentum_3m=round(m3, 2),
            momentum_6m=round(m6, 2),
            momentum_12m=round(m12, 2),
            composite_score=round(composite, 4),
            high_52w=round(high_52w, 2),
            pct_from_ath=round(pct_from_ath, 2),
            volatility=round(vol_pct, 2),
            avg_volume=round(avg_vol, 0),
            is_cash_slot=False,
        )

    # ── Portfolio builder ────────────────────────────────────────────────────

    def _next_action_date(self, rebalance: str) -> str:
        """Return the label of the next rebalancing action date."""
        today = datetime.today()
        if rebalance == "weekly":
            # Next Monday
            days_ahead = (7 - today.weekday()) % 7
            if days_ahead == 0:
                days_ahead = 7
            nxt = today + timedelta(days=days_ahead)
        else:
            # First trading day of next month
            if today.month == 12:
                nxt = today.replace(year=today.year + 1, month=1, day=1)
            else:
                nxt = today.replace(month=today.month + 1, day=1)
        return nxt.strftime("%A, %d %b %Y")

    def run(
        self,
        strategy_key:     str = "Mi-35",
        capital:          float = 500_000,
        current_holdings: Optional[List[str]] = None,
        on_progress:      Optional[callable] = None,
    ) -> RebalanceResult:
        """
        Run a full rebalancing analysis.

        Parameters
        ──────────
        strategy_key      : one of STRATEGY_PRESETS keys
        capital           : total capital to allocate (INR)
        current_holdings  : symbols currently held (to compute BUY/SELL/HOLD)
        on_progress       : optional callback(current, total) for UI progress bars
        """
        cfg = STRATEGY_PRESETS[strategy_key]
        universe:           List[str] = cfg["universe"]
        top_n:              int       = cfg["top_n"]
        rebalance:          str       = cfg["rebalance"]
        absolute_momentum:  bool      = cfg["absolute_momentum"]
        ath_filter:         bool      = cfg["ath_filter"]
        ath_threshold:      float     = cfg.get("ath_threshold", 10.0)
        risk_adjusted:      bool      = cfg["risk_adjusted"]
        exclude_last_month: bool      = cfg["exclude_last_month"]

        current_holdings = set(current_holdings or [])
        errors: List[str] = []

        # Score all stocks
        scored: List[StockMomentum] = []
        total = len(universe)
        for i, sym in enumerate(universe):
            if on_progress:
                on_progress(i + 1, total)
            result = self._score_stock(
                sym,
                exclude_last_month=exclude_last_month,
                risk_adjusted=risk_adjusted,
                ath_filter=ath_filter,
                ath_threshold=ath_threshold,
            )
            if result:
                scored.append(result)
            else:
                errors.append(sym)

        if not scored:
            return RebalanceResult(
                strategy=strategy_key,
                strategy_label=cfg["label"],
                rebalance_date=datetime.today().strftime("%d %b %Y"),
                next_action_date=self._next_action_date(rebalance),
                portfolio=[],
                exits=[], entries=[],
                cash_pct=0, universe_size=total, scored_count=0,
                errors=errors,
            )

        # Sort by composite score descending
        scored.sort(key=lambda x: x.composite_score, reverse=True)

        # Build top-N portfolio with absolute momentum cash check
        portfolio: List[PortfolioSlot] = []
        cash_slots = 0
        for rank, stock in enumerate(scored[:top_n], start=1):
            # Absolute momentum: go to cash if 6-month return is negative
            if absolute_momentum and stock.momentum_6m < 0:
                cash_slots += 1
                portfolio.append(PortfolioSlot(
                    rank=rank,
                    symbol=CASH_PROXY,
                    name="Cash / Liquid Fund (LIQUIDBEES)",
                    action="CASH",
                    entry_price=0.0,
                    weight_pct=round(100 / top_n, 2),
                    capital_amount=round(capital / top_n, 2),
                    momentum_score=stock.composite_score,
                    pct_from_ath=0.0,
                    momentum_6m=stock.momentum_6m,
                ))
            else:
                action = "HOLD" if stock.symbol in current_holdings else "BUY"
                portfolio.append(PortfolioSlot(
                    rank=rank,
                    symbol=stock.symbol,
                    name=stock.name,
                    action=action,
                    entry_price=stock.current_price,
                    weight_pct=round(100 / top_n, 2),
                    capital_amount=round(capital / top_n, 2),
                    momentum_score=round(stock.composite_score, 4),
                    pct_from_ath=stock.pct_from_ath,
                    momentum_6m=stock.momentum_6m,
                ))

        # Exits: held stocks not in new top-N
        new_symbols = {p.symbol for p in portfolio if p.action != "CASH"}
        exits  = [s for s in current_holdings if s not in new_symbols]
        entries = [p.symbol for p in portfolio if p.action == "BUY"]
        cash_pct = cash_slots / top_n * 100

        return RebalanceResult(
            strategy=strategy_key,
            strategy_label=cfg["label"],
            rebalance_date=datetime.today().strftime("%d %b %Y"),
            next_action_date=self._next_action_date(rebalance),
            portfolio=portfolio,
            exits=exits,
            entries=entries,
            cash_pct=round(cash_pct, 1),
            universe_size=total,
            scored_count=len(scored),
            errors=errors,
        )

    # ── Full universe ranking (for screener table) ────────────────────────────

    def rank_universe(
        self,
        strategy_key: str = "Mi-35",
        on_progress: Optional[callable] = None,
    ) -> pd.DataFrame:
        """
        Return a DataFrame of ALL scored stocks in the universe, sorted by
        momentum score — useful for the screener / deep-dive view.
        """
        cfg = STRATEGY_PRESETS[strategy_key]
        universe = cfg["universe"]
        top_n    = cfg["top_n"]
        scored: List[StockMomentum] = []
        total = len(universe)

        for i, sym in enumerate(universe):
            if on_progress:
                on_progress(i + 1, total)
            result = self._score_stock(
                sym,
                exclude_last_month=cfg["exclude_last_month"],
                risk_adjusted=cfg["risk_adjusted"],
                ath_filter=cfg["ath_filter"],
                ath_threshold=cfg.get("ath_threshold", 10.0),
            )
            if result:
                scored.append(result)

        if not scored:
            return pd.DataFrame()

        scored.sort(key=lambda x: x.composite_score, reverse=True)

        rows = []
        for rank, s in enumerate(scored, start=1):
            rows.append({
                "Rank":          rank,
                "In Portfolio":  "✅" if rank <= top_n else "—",
                "Symbol":        s.symbol,
                "Name":          s.name[:30],
                "Price":         s.current_price,
                "Score":         round(s.composite_score, 3),
                "1M %":          s.momentum_1m,
                "3M %":          s.momentum_3m,
                "6M %":          s.momentum_6m,
                "12M %":         s.momentum_12m,
                "Vol (ann %)":   s.volatility,
                "% from ATH":    s.pct_from_ath,
                "Avg Vol (K)":   round(s.avg_volume / 1000, 0),
            })

        return pd.DataFrame(rows)

    # ── Backtest ─────────────────────────────────────────────────────────────

    def backtest(
        self,
        strategy_key: str = "Mi-35",
        lookback_years: int = 3,
        capital: float = 500_000,
    ) -> pd.DataFrame:
        """
        Simple walk-forward backtest that simulates monthly/weekly rebalancing.
        Returns an equity-curve DataFrame with columns [date, portfolio_value].

        Note: Uses historical CLOSE prices; does not account for slippage,
        brokerage, or taxes.
        """
        cfg = STRATEGY_PRESETS[strategy_key]
        universe = cfg["universe"]
        top_n    = cfg["top_n"]
        rebalance = cfg["rebalance"]
        absolute_momentum = cfg["absolute_momentum"]
        risk_adjusted = cfg["risk_adjusted"]
        exclude_last_month = cfg["exclude_last_month"]

        period_str = f"{lookback_years + 1}y"   # extra year for warm-up

        # Download all price data in bulk (faster than one-by-one)
        all_prices: Dict[str, pd.Series] = {}
        for sym in universe:
            df = yf.Ticker(sym).history(period=period_str)
            if not df.empty and len(df) > 252:
                df.index = pd.to_datetime(df.index).tz_localize(None)
                all_prices[sym] = df["Close"].rename(sym)

        if not all_prices:
            return pd.DataFrame()

        price_df = pd.DataFrame(all_prices).ffill()
        price_df = price_df[price_df.index >= price_df.index[0] + timedelta(days=365)]

        # Build rebalancing dates
        if rebalance == "weekly":
            # Every Monday
            reb_dates = price_df.index[price_df.index.dayofweek == 0]
        else:
            # First trading day of each month
            reb_dates = price_df.resample("MS").first().index
            reb_dates = [price_df.index[price_df.index >= d][0]
                         for d in reb_dates if any(price_df.index >= d)]

        if len(reb_dates) < 2:
            return pd.DataFrame()

        equity = capital
        equity_curve = []
        holdings: Dict[str, float] = {}   # symbol → shares held

        prev_reb = reb_dates[0]

        for reb_date in reb_dates[1:]:
            # Score at prev_reb
            scores = {}
            for sym, series in all_prices.items():
                hist = series[series.index <= prev_reb]
                if len(hist) < 252:
                    continue
                c = hist.iloc[-1]
                def _roc(days):
                    if len(hist) <= days:
                        return 0.0
                    ref = hist.iloc[-(days + 1)]
                    return ((c - ref) / ref * 100) if ref > 0 else 0.0

                m1, m3, m6, m12 = _roc(21), _roc(63), _roc(126), _roc(252)
                comps = [m3, m6, m12] if exclude_last_month else [m1, m3, m6, m12]
                raw = float(np.mean(comps))
                if risk_adjusted:
                    vol = hist.pct_change().dropna().tail(252).std() * np.sqrt(252) * 100
                    scores[sym] = raw / vol if vol > 0 else raw
                else:
                    scores[sym] = raw

            if not scores:
                prev_reb = reb_date
                continue

            ranked = sorted(scores, key=scores.__getitem__, reverse=True)[:top_n]

            # Absolute momentum: remove negative 6M stocks → cash slot
            if absolute_momentum:
                def _m6(sym):
                    hist = all_prices[sym][all_prices[sym].index <= prev_reb]
                    if len(hist) <= 126:
                        return 0.0
                    c, ref = hist.iloc[-1], hist.iloc[-127]
                    return ((c - ref) / ref * 100) if ref > 0 else 0.0
                ranked = [s for s in ranked if _m6(s) >= 0]

            # Value portfolio at reb_date
            cur_prices = price_df.loc[price_df.index <= reb_date].iloc[-1]
            portfolio_value = sum(
                shares * cur_prices.get(sym, 0)
                for sym, shares in holdings.items()
            ) + (equity if not holdings else 0)

            # Reallocate equally
            alloc = portfolio_value / max(len(ranked), 1)
            holdings = {}
            for sym in ranked:
                p = cur_prices.get(sym, 0)
                if p > 0:
                    holdings[sym] = alloc / p

            equity_curve.append({"date": reb_date, "portfolio_value": round(portfolio_value, 2)})
            prev_reb = reb_date

        return pd.DataFrame(equity_curve)

    # ── Reporting ─────────────────────────────────────────────────────────────

    def print_report(self, result: RebalanceResult) -> None:
        w = 68
        print("\n" + "═" * w)
        print(f"  {result.strategy_label}  —  Weekend Investing Momentum Strategy")
        print("═" * w)
        print(f"  Rebalance date  : {result.rebalance_date}")
        print(f"  Next action     : {result.next_action_date}")
        print(f"  Universe        : {result.universe_size} stocks  →  scored {result.scored_count}")
        print(f"  Cash allocation : {result.cash_pct:.1f}%")
        if result.entries:
            print(f"\n  ✅ BUY  ({len(result.entries)}): {', '.join(result.entries)}")
        if result.exits:
            print(f"  ❌ SELL ({len(result.exits)}): {', '.join(result.exits)}")
        print(f"\n  {'Rank':<5} {'Symbol':<20} {'Action':<8} {'Score':>8} {'6M%':>7} {'ATH%':>7} {'₹/slot':>12}")
        print("  " + "─" * (w - 2))
        for slot in result.portfolio:
            print(f"  {slot.rank:<5} {slot.symbol:<20} {slot.action:<8} "
                  f"{slot.momentum_score:>8.3f} {slot.momentum_6m:>7.1f} "
                  f"{slot.pct_from_ath:>7.1f} {slot.capital_amount:>12,.0f}")
        print("═" * w + "\n")


# ═══════════════════════════════════════════════════════════════════════════════
# CLI ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Weekend Investing Strategy Engine")
    parser.add_argument("--strategy", default="Mi-35",
                        choices=list(STRATEGY_PRESETS.keys()),
                        help="Strategy preset to run")
    parser.add_argument("--capital", type=float, default=500_000,
                        help="Total capital in INR")
    parser.add_argument("--holdings", nargs="*", default=[],
                        help="Currently held symbols (space-separated)")
    args = parser.parse_args()

    engine = WeekendInvestingStrategy()
    print(f"\nRunning {args.strategy} …  (this may take a few minutes)")
    result = engine.run(args.strategy, capital=args.capital,
                        current_holdings=args.holdings)
    engine.print_report(result)
