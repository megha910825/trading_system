#!/usr/bin/env python3
"""
Fundamental Analyzer - Financial Health & Valuation Analysis
Supports: US, German (XETRA), and Indian (NSE) stocks
Enhanced Fundamental Analyzer - Complete Financial Analysis
Includes: Cash Flow, Insider Activity, Institutional Holdings, Sector Benchmarks
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional, List, Tuple
from dataclasses import dataclass, field
import json
import time


# ═══════════════════════════════════════════════════════════════
# SECTOR BENCHMARKS - Industry-specific valuation standards
# ═══════════════════════════════════════════════════════════════

SECTOR_BENCHMARKS = {
    "Technology": {
        "pe_ratio": {"low": 15, "mid": 30, "high": 50},
        "pb_ratio": {"low": 3, "mid": 8, "high": 15},
        "profit_margin": {"low": 10, "mid": 20, "high": 30},
        "roe": {"low": 10, "mid": 20, "high": 30},
        "revenue_growth": {"low": 5, "mid": 15, "high": 30},
        "debt_to_equity": {"low": 0, "mid": 50, "high": 100},
    },
    "Healthcare": {
        "pe_ratio": {"low": 12, "mid": 25, "high": 40},
        "pb_ratio": {"low": 2, "mid": 5, "high": 10},
        "profit_margin": {"low": 5, "mid": 15, "high": 25},
        "roe": {"low": 8, "mid": 15, "high": 25},
        "revenue_growth": {"low": 3, "mid": 10, "high": 20},
        "debt_to_equity": {"low": 0, "mid": 60, "high": 120},
    },
    "Financial Services": {
        "pe_ratio": {"low": 8, "mid": 15, "high": 25},
        "pb_ratio": {"low": 0.8, "mid": 1.5, "high": 3},
        "profit_margin": {"low": 15, "mid": 25, "high": 40},
        "roe": {"low": 8, "mid": 12, "high": 18},
        "revenue_growth": {"low": 2, "mid": 8, "high": 15},
        "debt_to_equity": {"low": 50, "mid": 200, "high": 500},  # Banks have high D/E
    },
    "Consumer Cyclical": {
        "pe_ratio": {"low": 10, "mid": 20, "high": 35},
        "pb_ratio": {"low": 2, "mid": 5, "high": 10},
        "profit_margin": {"low": 3, "mid": 8, "high": 15},
        "roe": {"low": 10, "mid": 18, "high": 30},
        "revenue_growth": {"low": 3, "mid": 10, "high": 20},
        "debt_to_equity": {"low": 0, "mid": 80, "high": 150},
    },
    "Consumer Defensive": {
        "pe_ratio": {"low": 12, "mid": 22, "high": 35},
        "pb_ratio": {"low": 2, "mid": 5, "high": 10},
        "profit_margin": {"low": 5, "mid": 10, "high": 18},
        "roe": {"low": 12, "mid": 20, "high": 35},
        "revenue_growth": {"low": 1, "mid": 5, "high": 10},
        "debt_to_equity": {"low": 0, "mid": 70, "high": 150},
    },
    "Industrials": {
        "pe_ratio": {"low": 10, "mid": 20, "high": 30},
        "pb_ratio": {"low": 2, "mid": 4, "high": 8},
        "profit_margin": {"low": 5, "mid": 10, "high": 18},
        "roe": {"low": 10, "mid": 18, "high": 28},
        "revenue_growth": {"low": 2, "mid": 8, "high": 15},
        "debt_to_equity": {"low": 0, "mid": 80, "high": 150},
    },
    "Energy": {
        "pe_ratio": {"low": 5, "mid": 12, "high": 20},
        "pb_ratio": {"low": 0.8, "mid": 1.5, "high": 3},
        "profit_margin": {"low": 3, "mid": 10, "high": 20},
        "roe": {"low": 5, "mid": 12, "high": 20},
        "revenue_growth": {"low": -5, "mid": 5, "high": 15},
        "debt_to_equity": {"low": 0, "mid": 50, "high": 100},
    },
    "Utilities": {
        "pe_ratio": {"low": 12, "mid": 18, "high": 25},
        "pb_ratio": {"low": 1, "mid": 2, "high": 3},
        "profit_margin": {"low": 8, "mid": 15, "high": 25},
        "roe": {"low": 8, "mid": 12, "high": 18},
        "revenue_growth": {"low": 0, "mid": 3, "high": 8},
        "debt_to_equity": {"low": 50, "mid": 120, "high": 200},
    },
    "Real Estate": {
        "pe_ratio": {"low": 15, "mid": 35, "high": 60},  # REITs often have high P/E
        "pb_ratio": {"low": 0.8, "mid": 1.5, "high": 3},
        "profit_margin": {"low": 15, "mid": 30, "high": 50},
        "roe": {"low": 3, "mid": 8, "high": 15},
        "revenue_growth": {"low": 0, "mid": 5, "high": 12},
        "debt_to_equity": {"low": 50, "mid": 100, "high": 200},
    },
    "Basic Materials": {
        "pe_ratio": {"low": 8, "mid": 15, "high": 25},
        "pb_ratio": {"low": 1, "mid": 2.5, "high": 5},
        "profit_margin": {"low": 5, "mid": 12, "high": 22},
        "roe": {"low": 8, "mid": 15, "high": 25},
        "revenue_growth": {"low": -3, "mid": 5, "high": 15},
        "debt_to_equity": {"low": 0, "mid": 60, "high": 120},
    },
    "Communication Services": {
        "pe_ratio": {"low": 12, "mid": 22, "high": 35},
        "pb_ratio": {"low": 2, "mid": 5, "high": 10},
        "profit_margin": {"low": 8, "mid": 18, "high": 30},
        "roe": {"low": 8, "mid": 15, "high": 25},
        "revenue_growth": {"low": 2, "mid": 10, "high": 20},
        "debt_to_equity": {"low": 0, "mid": 80, "high": 150},
    },
}

# Default benchmarks for unknown sectors
DEFAULT_BENCHMARKS = {
    "pe_ratio": {"low": 10, "mid": 20, "high": 35},
    "pb_ratio": {"low": 1.5, "mid": 4, "high": 8},
    "profit_margin": {"low": 5, "mid": 12, "high": 22},
    "roe": {"low": 10, "mid": 18, "high": 28},
    "revenue_growth": {"low": 3, "mid": 10, "high": 20},
    "debt_to_equity": {"low": 0, "mid": 70, "high": 140},
}


@dataclass
class FundamentalData:
    """Complete fundamental data container"""

    # Basic Info
    symbol: str
    name: str
    sector: str
    industry: str
    market_cap: float
    currency: str
    country: str
    exchange: str

    # Price Info
    current_price: float
    price_52w_high: float
    price_52w_low: float
    price_to_52w_high_pct: float
    beta: float

    # Valuation Metrics
    pe_ratio: float
    forward_pe: float
    peg_ratio: float
    pb_ratio: float
    ps_ratio: float
    pcf_ratio: float  # Price to Cash Flow
    ev_to_ebitda: float
    ev_to_revenue: float

    # Profitability Metrics
    gross_margin: float
    operating_margin: float
    profit_margin: float
    roe: float
    roa: float
    roic: float  # Return on Invested Capital

    # Growth Metrics
    revenue_growth: float
    revenue_growth_3y: float
    earnings_growth: float
    earnings_growth_5y: float
    eps_growth_ttm: float

    # Cash Flow Metrics
    operating_cash_flow: float
    free_cash_flow: float
    fcf_margin: float
    fcf_per_share: float
    fcf_yield: float
    capex_to_revenue: float

    # Balance Sheet / Financial Health
    current_ratio: float
    quick_ratio: float
    cash_ratio: float
    debt_to_equity: float
    debt_to_assets: float
    interest_coverage: float
    total_cash: float
    total_debt: float
    net_debt: float

    # Efficiency Metrics
    asset_turnover: float
    inventory_turnover: float
    receivables_turnover: float

    # Dividends
    dividend_yield: float
    dividend_payout_ratio: float
    dividend_growth_5y: float
    years_of_dividends: int

    # Per Share Data
    eps_ttm: float
    eps_forward: float
    book_value_per_share: float
    revenue_per_share: float

    # Ownership
    insider_ownership: float
    institutional_ownership: float
    shares_outstanding: float
    float_shares: float
    shares_short: float
    short_ratio: float
    short_pct_of_float: float

    # Analyst Data
    analyst_rating: str
    analyst_score: float  # 1-5 scale
    num_analysts: int
    target_price_low: float
    target_price_mean: float
    target_price_high: float
    upside_potential: float

    # Earnings
    next_earnings_date: str
    last_earnings_date: str
    earnings_surprise_pct: float

    # Scores (calculated)
    valuation_score: int = 0
    profitability_score: int = 0
    growth_score: int = 0
    health_score: int = 0
    cash_flow_score: int = 0
    momentum_score: int = 0
    quality_score: int = 0
    overall_score: int = 0

    # Relative scores (vs sector)
    sector_valuation_rank: str = ""  # Cheap, Fair, Expensive
    sector_growth_rank: str = ""     # Below, Average, Above
    sector_profit_rank: str = ""     # Below, Average, Above

    # Flags
    is_profitable: bool = True
    has_positive_fcf: bool = True
    is_dividend_payer: bool = False
    is_dividend_grower: bool = False
    has_low_debt: bool = True
    has_insider_buying: bool = False

    # Meta
    last_updated: str = ""
    data_quality: str = "Good"  # Good, Partial, Limited


class FundamentalAnalyzer:
    """
    Comprehensive fundamental analysis with sector-specific benchmarks

    Features:
    - 50+ fundamental metrics
    - Sector-relative scoring
    - Cash flow analysis
    - Quality scoring (Piotroski-inspired)
    - Ownership analysis
    """

    def __init__(self, cache_dir: str = "data/fundamentals_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_hours = 12  # Refresh every 12 hours

    def analyze(self, symbol: str, use_cache: bool = True) -> Optional[FundamentalData]:
        """
        Perform complete fundamental analysis

        Args:
            symbol: Stock ticker
            use_cache: Use cached data if fresh

        Returns:
            FundamentalData with all metrics and scores
        """

        # Check cache
        if use_cache:
            cached = self._load_cache(symbol)
            if cached:
                return cached

        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info

            if not info or info.get('regularMarketPrice') is None:
                print(f"⚠️ No data for {symbol}")
                return None

            # Get additional data
            try:
                cash_flow = ticker.quarterly_cashflow
                balance_sheet = ticker.quarterly_balance_sheet
                financials = ticker.quarterly_financials
            except:
                cash_flow = balance_sheet = financials = None

            # Extract all metrics
            data = self._extract_all_metrics(symbol, info, cash_flow, balance_sheet, financials)

            # Calculate scores with sector benchmarks
            data = self._calculate_all_scores(data)

            # Cache result
            self._save_cache(symbol, data)

            return data

        except Exception as e:
            print(f"❌ Error analyzing {symbol}: {e}")
            return None

    def _extract_all_metrics(
        self,
        symbol: str,
        info: dict,
        cash_flow: pd.DataFrame,
        balance_sheet: pd.DataFrame,
        financials: pd.DataFrame
    ) -> FundamentalData:
        """Extract all fundamental metrics"""

        def safe_get(key, default=0):
            val = info.get(key)
            if val is None or val == 'N/A' or (isinstance(val, float) and np.isnan(val)):
                return default
            return val

        def pct(val):
            """Convert to percentage"""
            if val and val != 0:
                return val * 100 if abs(val) < 1 else val
            return 0

        # Basic Info
        current_price = safe_get('regularMarketPrice', safe_get('currentPrice', 0))
        high_52w = safe_get('fiftyTwoWeekHigh', current_price)
        low_52w = safe_get('fiftyTwoWeekLow', current_price)

        price_to_high_pct = ((current_price / high_52w) - 1) * 100 if high_52w else 0

        # Cash Flow Metrics
        ocf = fcf = fcf_margin = fcf_per_share = 0
        if cash_flow is not None and not cash_flow.empty:
            try:
                ocf = cash_flow.loc['Operating Cash Flow'].iloc[0] if 'Operating Cash Flow' in cash_flow.index else 0
                fcf = cash_flow.loc['Free Cash Flow'].iloc[0] if 'Free Cash Flow' in cash_flow.index else 0
            except:
                pass

        revenue = safe_get('totalRevenue', 1)
        shares = safe_get('sharesOutstanding', 1)

        if revenue and fcf:
            fcf_margin = (fcf / revenue) * 100
        if shares and fcf:
            fcf_per_share = fcf / shares

        market_cap = safe_get('marketCap', 0)
        fcf_yield = (fcf / market_cap * 100) if market_cap and fcf else 0

        # Ownership
        insider_own = pct(safe_get('heldPercentInsiders', 0))
        inst_own = pct(safe_get('heldPercentInstitutions', 0))

        # Short Interest
        short_shares = safe_get('sharesShort', 0)
        float_shares = safe_get('floatShares', shares)
        short_pct = (short_shares / float_shares * 100) if float_shares else 0

        # Analyst
        target_low = safe_get('targetLowPrice', 0)
        target_mean = safe_get('targetMeanPrice', 0)
        target_high = safe_get('targetHighPrice', 0)
        upside = ((target_mean / current_price) - 1) * 100 if current_price and target_mean else 0

        # Earnings dates
        try:
            earnings_dates = yf.Ticker(symbol).calendar
            if earnings_dates is not None and not earnings_dates.empty:
                next_earnings = str(earnings_dates.iloc[0, 0])[:10] if len(earnings_dates) > 0 else ""
            else:
                next_earnings = ""
        except:
            next_earnings = ""

        return FundamentalData(
            # Basic
            symbol=symbol,
            name=safe_get('shortName', symbol),
            sector=safe_get('sector', 'Unknown'),
            industry=safe_get('industry', 'Unknown'),
            market_cap=market_cap,
            currency=safe_get('currency', 'USD'),
            country=safe_get('country', 'Unknown'),
            exchange=safe_get('exchange', 'Unknown'),

            # Price
            current_price=current_price,
            price_52w_high=high_52w,
            price_52w_low=low_52w,
            price_to_52w_high_pct=price_to_high_pct,
            beta=safe_get('beta', 1),

            # Valuation
            pe_ratio=safe_get('trailingPE', 0),
            forward_pe=safe_get('forwardPE', 0),
            peg_ratio=safe_get('pegRatio', 0),
            pb_ratio=safe_get('priceToBook', 0),
            ps_ratio=safe_get('priceToSalesTrailing12Months', 0),
            pcf_ratio=safe_get('priceToOperatingCashFlows', 0) if safe_get('priceToOperatingCashFlows') else (current_price * shares / ocf if ocf else 0),
            ev_to_ebitda=safe_get('enterpriseToEbitda', 0),
            ev_to_revenue=safe_get('enterpriseToRevenue', 0),

            # Profitability
            gross_margin=pct(safe_get('grossMargins', 0)),
            operating_margin=pct(safe_get('operatingMargins', 0)),
            profit_margin=pct(safe_get('profitMargins', 0)),
            roe=pct(safe_get('returnOnEquity', 0)),
            roa=pct(safe_get('returnOnAssets', 0)),
            roic=0,  # Calculate separately if needed

            # Growth
            revenue_growth=pct(safe_get('revenueGrowth', 0)),
            revenue_growth_3y=0,  # Would need historical data
            earnings_growth=pct(safe_get('earningsGrowth', 0)),
            earnings_growth_5y=pct(safe_get('earningsQuarterlyGrowth', 0)),
            eps_growth_ttm=0,

            # Cash Flow
            operating_cash_flow=ocf,
            free_cash_flow=fcf,
            fcf_margin=fcf_margin,
            fcf_per_share=fcf_per_share,
            fcf_yield=fcf_yield,
            capex_to_revenue=0,

            # Balance Sheet
            current_ratio=safe_get('currentRatio', 0),
            quick_ratio=safe_get('quickRatio', 0),
            cash_ratio=0,
            debt_to_equity=safe_get('debtToEquity', 0),
            debt_to_assets=0,
            interest_coverage=safe_get('interestCoverage', 0) if safe_get('interestCoverage') else 0,
            total_cash=safe_get('totalCash', 0),
            total_debt=safe_get('totalDebt', 0),
            net_debt=safe_get('totalDebt', 0) - safe_get('totalCash', 0),

            # Efficiency
            asset_turnover=0,
            inventory_turnover=0,
            receivables_turnover=0,

            # Dividends
            dividend_yield=pct(safe_get('dividendYield', 0)),
            dividend_payout_ratio=pct(safe_get('payoutRatio', 0)),
            dividend_growth_5y=0,
            years_of_dividends=0,

            # Per Share
            eps_ttm=safe_get('trailingEps', 0),
            eps_forward=safe_get('forwardEps', 0),
            book_value_per_share=safe_get('bookValue', 0),
            revenue_per_share=safe_get('revenuePerShare', 0),

            # Ownership
            insider_ownership=insider_own,
            institutional_ownership=inst_own,
            shares_outstanding=shares,
            float_shares=float_shares,
            shares_short=short_shares,
            short_ratio=safe_get('shortRatio', 0),
            short_pct_of_float=short_pct,

            # Analyst
            analyst_rating=safe_get('recommendationKey', 'none'),
            analyst_score=safe_get('recommendationMean', 3),
            num_analysts=safe_get('numberOfAnalystOpinions', 0),
            target_price_low=target_low,
            target_price_mean=target_mean,
            target_price_high=target_high,
            upside_potential=upside,

            # Earnings
            next_earnings_date=next_earnings,
            last_earnings_date="",
            earnings_surprise_pct=0,

            # Flags
            is_profitable=safe_get('profitMargins', 0) > 0,
            has_positive_fcf=fcf > 0,
            is_dividend_payer=safe_get('dividendYield', 0) > 0,
            is_dividend_grower=False,
            has_low_debt=safe_get('debtToEquity', 100) < 100,
            has_insider_buying=False,

            # Meta
            last_updated=datetime.now().isoformat(),
            data_quality="Good"
        )

    def _calculate_all_scores(self, data: FundamentalData) -> FundamentalData:
        """Calculate all scores using sector-specific benchmarks"""

        # Get sector benchmarks
        benchmarks = SECTOR_BENCHMARKS.get(data.sector, DEFAULT_BENCHMARKS)

        # ═══════════════════════════════════════════════════════
        # VALUATION SCORE (0-100)
        # ═══════════════════════════════════════════════════════

        val_score = 50
        pe_bench = benchmarks["pe_ratio"]

        # P/E Ratio (sector-relative)
        if data.pe_ratio > 0:
            if data.pe_ratio < pe_bench["low"]:
                val_score += 25
                data.sector_valuation_rank = "Cheap"
            elif data.pe_ratio < pe_bench["mid"]:
                val_score += 15
                data.sector_valuation_rank = "Fair"
            elif data.pe_ratio < pe_bench["high"]:
                val_score += 0
                data.sector_valuation_rank = "Fair"
            else:
                val_score -= 20
                data.sector_valuation_rank = "Expensive"
        elif data.pe_ratio < 0:  # Negative = unprofitable
            val_score -= 25
            data.sector_valuation_rank = "N/A (Unprofitable)"

        # PEG Ratio (growth-adjusted)
        if 0 < data.peg_ratio < 1:
            val_score += 20
        elif 1 <= data.peg_ratio < 1.5:
            val_score += 10
        elif 1.5 <= data.peg_ratio < 2:
            val_score += 0
        elif data.peg_ratio >= 2:
            val_score -= 10

        # FCF Yield (higher is better)
        if data.fcf_yield > 8:
            val_score += 15
        elif data.fcf_yield > 5:
            val_score += 10
        elif data.fcf_yield > 3:
            val_score += 5
        elif data.fcf_yield < 0:
            val_score -= 10

        # Upside to analyst target
        if data.upside_potential > 30:
            val_score += 10
        elif data.upside_potential > 15:
            val_score += 5
        elif data.upside_potential < -10:
            val_score -= 10

        data.valuation_score = max(0, min(100, val_score))

        # ═══════════════════════════════════════════════════════
        # PROFITABILITY SCORE (0-100)
        # ═══════════════════════════════════════════════════════

        prof_score = 50
        profit_bench = benchmarks["profit_margin"]
        roe_bench = benchmarks["roe"]

        # Profit Margin (sector-relative)
        if data.profit_margin > profit_bench["high"]:
            prof_score += 25
            data.sector_profit_rank = "Above Average"
        elif data.profit_margin > profit_bench["mid"]:
            prof_score += 15
            data.sector_profit_rank = "Average"
        elif data.profit_margin > profit_bench["low"]:
            prof_score += 5
            data.sector_profit_rank = "Below Average"
        elif data.profit_margin <= 0:
            prof_score -= 25
            data.sector_profit_rank = "Unprofitable"

        # ROE (sector-relative)
        if data.roe > roe_bench["high"]:
            prof_score += 20
        elif data.roe > roe_bench["mid"]:
            prof_score += 10
        elif data.roe > roe_bench["low"]:
            prof_score += 5
        elif data.roe < 0:
            prof_score -= 15

        # Gross Margin (consistency indicator)
        if data.gross_margin > 60:
            prof_score += 15
        elif data.gross_margin > 40:
            prof_score += 10
        elif data.gross_margin > 25:
            prof_score += 5

        data.profitability_score = max(0, min(100, prof_score))

        # ═══════════════════════════════════════════════════════
        # GROWTH SCORE (0-100)
        # ═══════════════════════════════════════════════════════

        growth_score = 50
        growth_bench = benchmarks["revenue_growth"]

        # Revenue Growth (sector-relative)
        if data.revenue_growth > growth_bench["high"]:
            growth_score += 25
            data.sector_growth_rank = "High Growth"
        elif data.revenue_growth > growth_bench["mid"]:
            growth_score += 15
            data.sector_growth_rank = "Above Average"
        elif data.revenue_growth > growth_bench["low"]:
            growth_score += 5
            data.sector_growth_rank = "Average"
        elif data.revenue_growth < 0:
            growth_score -= 15
            data.sector_growth_rank = "Declining"

        # Earnings Growth
        if data.earnings_growth > 30:
            growth_score += 20
        elif data.earnings_growth > 15:
            growth_score += 10
        elif data.earnings_growth > 5:
            growth_score += 5
        elif data.earnings_growth < -10:
            growth_score -= 15

        # Forward EPS growth implied
        if data.eps_forward > data.eps_ttm > 0:
            implied_growth = (data.eps_forward / data.eps_ttm - 1) * 100
            if implied_growth > 20:
                growth_score += 10
            elif implied_growth > 10:
                growth_score += 5

        data.growth_score = max(0, min(100, growth_score))

        # ═══════════════════════════════════════════════════════
        # FINANCIAL HEALTH SCORE (0-100)
        # ═══════════════════════════════════════════════════════

        health_score = 50
        de_bench = benchmarks["debt_to_equity"]

        # Debt to Equity (sector-relative)
        if data.debt_to_equity <= de_bench["low"]:
            health_score += 20
        elif data.debt_to_equity <= de_bench["mid"]:
            health_score += 10
        elif data.debt_to_equity <= de_bench["high"]:
            health_score += 0
        else:
            health_score -= 15

        # Current Ratio
        if data.current_ratio >= 2:
            health_score += 15
        elif data.current_ratio >= 1.5:
            health_score += 10
        elif data.current_ratio >= 1:
            health_score += 5
        elif data.current_ratio < 1:
            health_score -= 15

        # Interest Coverage
        if data.interest_coverage > 10:
            health_score += 15
        elif data.interest_coverage > 5:
            health_score += 10
        elif data.interest_coverage > 2:
            health_score += 5
        elif 0 < data.interest_coverage < 1.5:
            health_score -= 20

        # Net Cash/Debt position
        if data.net_debt < 0:  # Net cash
            health_score += 10
        elif data.net_debt > 0 and data.market_cap > 0:
            net_debt_to_mcap = data.net_debt / data.market_cap
            if net_debt_to_mcap > 0.5:
                health_score -= 15

        data.health_score = max(0, min(100, health_score))

        # ═══════════════════════════════════════════════════════
        # CASH FLOW SCORE (0-100)
        # ═══════════════════════════════════════════════════════

        cf_score = 50

        # Free Cash Flow
        if data.has_positive_fcf:
            cf_score += 15

            # FCF Margin
            if data.fcf_margin > 20:
                cf_score += 20
            elif data.fcf_margin > 10:
                cf_score += 10
            elif data.fcf_margin > 5:
                cf_score += 5
        else:
            cf_score -= 20

        # FCF Yield
        if data.fcf_yield > 8:
            cf_score += 15
        elif data.fcf_yield > 5:
            cf_score += 10
        elif data.fcf_yield > 3:
            cf_score += 5

        data.cash_flow_score = max(0, min(100, cf_score))

        # ═══════════════════════════════════════════════════════
        # QUALITY SCORE (Piotroski-inspired, 0-100)
        # ═══════════════════════════════════════════════════════

        quality_points = 0

        # Profitability signals
        if data.is_profitable:
            quality_points += 1
        if data.has_positive_fcf:
            quality_points += 1
        if data.roa > 5:
            quality_points += 1
        if data.free_cash_flow > 0 and data.profit_margin > 0:
            quality_points += 1  # FCF confirms earnings

        # Leverage signals
        if data.debt_to_equity < 100:
            quality_points += 1
        if data.current_ratio > 1:
            quality_points += 1

        # Efficiency signals
        if data.gross_margin > 30:
            quality_points += 1
        if data.roe > 15:
            quality_points += 1

        # Growth signals
        if data.revenue_growth > 0:
            quality_points += 1

        data.quality_score = int(quality_points / 9 * 100)

        # ═══════════════════════════════════════════════════════
        # MOMENTUM SCORE (0-100) - Price & Analyst momentum
        # ═══════════════════════════════════════════════════════

        momentum_score = 50

        # Price vs 52-week high
        if data.price_to_52w_high_pct > -10:
            momentum_score += 15  # Near highs = strong
        elif data.price_to_52w_high_pct > -20:
            momentum_score += 10
        elif data.price_to_52w_high_pct < -40:
            momentum_score -= 15  # Way below highs

        # Analyst sentiment
        if data.analyst_score < 2:  # Strong buy
            momentum_score += 15
        elif data.analyst_score < 2.5:  # Buy
            momentum_score += 10
        elif data.analyst_score > 3.5:  # Sell
            momentum_score -= 15

        # Upside potential
        if data.upside_potential > 20:
            momentum_score += 10
        elif data.upside_potential < 0:
            momentum_score -= 10

        data.momentum_score = max(0, min(100, momentum_score))

        # ═══════════════════════════════════════════════════════
        # OVERALL SCORE (Weighted Average)
        # ═══════════════════════════════════════════════════════

        data.overall_score = int(
            data.valuation_score * 0.20 +
            data.profitability_score * 0.25 +
            data.growth_score * 0.20 +
            data.health_score * 0.15 +
            data.cash_flow_score * 0.10 +
            data.quality_score * 0.10
        )

        return data

    def _load_cache(self, symbol: str) -> Optional[FundamentalData]:
        """Load from cache if fresh"""
        cache_file = self.cache_dir / f"{symbol.replace('.', '_')}.json"

        if not cache_file.exists():
            return None

        try:
            with open(cache_file, 'r') as f:
                data = json.load(f)

            last_updated = datetime.fromisoformat(data.get('last_updated', '2000-01-01'))
            if datetime.now() - last_updated > timedelta(hours=self.cache_hours):
                return None

            return FundamentalData(**data)
        except:
            return None

    def _save_cache(self, symbol: str, data: FundamentalData):
        """Save to cache"""
        cache_file = self.cache_dir / f"{symbol.replace('.', '_')}.json"

        try:
            with open(cache_file, 'w') as f:
                json.dump(data.__dict__, f, indent=2, default=str)
        except:
            pass

    def get_sector_comparison(self, symbol: str) -> Dict:
        """Compare stock metrics to sector averages"""

        data = self.analyze(symbol)
        if not data:
            return {}

        benchmarks = SECTOR_BENCHMARKS.get(data.sector, DEFAULT_BENCHMARKS)

        return {
            "symbol": symbol,
            "sector": data.sector,
            "comparisons": {
                "P/E Ratio": {
                    "value": data.pe_ratio,
                    "sector_mid": benchmarks["pe_ratio"]["mid"],
                    "status": data.sector_valuation_rank,
                },
                "Profit Margin": {
                    "value": data.profit_margin,
                    "sector_mid": benchmarks["profit_margin"]["mid"],
                    "status": data.sector_profit_rank,
                },
                "ROE": {
                    "value": data.roe,
                    "sector_mid": benchmarks["roe"]["mid"],
                    "status": "Above" if data.roe > benchmarks["roe"]["mid"] else "Below",
                },
                "Revenue Growth": {
                    "value": data.revenue_growth,
                    "sector_mid": benchmarks["revenue_growth"]["mid"],
                    "status": data.sector_growth_rank,
                },
                "Debt/Equity": {
                    "value": data.debt_to_equity,
                    "sector_mid": benchmarks["debt_to_equity"]["mid"],
                    "status": "Good" if data.debt_to_equity < benchmarks["debt_to_equity"]["mid"] else "High",
                },
            }
        }

    def print_detailed_report(self, symbol: str):
        """Print comprehensive fundamental report"""

        data = self.analyze(symbol)

        if not data:
            print(f"❌ Could not analyze {symbol}")
            return

        # Rating
        if data.overall_score >= 75:
            rating = "🟢 EXCELLENT"
        elif data.overall_score >= 60:
            rating = "🟢 GOOD"
        elif data.overall_score >= 45:
            rating = "🟡 FAIR"
        elif data.overall_score >= 30:
            rating = "🟠 BELOW AVERAGE"
        else:
            rating = "🔴 POOR"

        # Format large numbers
        def fmt_big(val):
            if val >= 1e12:
                return f"${val/1e12:.2f}T"
            elif val >= 1e9:
                return f"${val/1e9:.2f}B"
            elif val >= 1e6:
                return f"${val/1e6:.1f}M"
            else:
                return f"${val:,.0f}"

        print(f"""
╔════════════════════════════════════════════════════════════════════════════════════╗
║                      📊 FUNDAMENTAL ANALYSIS: {data.symbol:^10}
║                      Overall Score: {data.overall_score}/100  {rating:^20}
╠════════════════════════════════════════════════════════════════════════════════════╣
║  {data.name[:60]:^78} ║
║  {data.sector} | {data.industry[:40]:40}
║  Market Cap: {fmt_big(data.market_cap):>12}  |  Price: ${data.current_price:>10,.2f}
║  52W Range: ${data.price_52w_low:.2f} - ${data.price_52w_high:.2f}  ({data.price_to_52w_high_pct:+.1f}% from high)
╠════════════════════════════════════════════════════════════════════════════════════╣
║                                                                                    ║
║  ┌─────────────────────────────────────────────────────────────────────────────┐   ║
║  │  SCORES BREAKDOWN                                                           │   ║
║  │  Valuation:     {data.valuation_score:>3}/100  │  Profitability: {data.profitability_score:>3}/100  │  Growth:   {data.growth_score:>3}/100 │   ║
║  │  Health:        {data.health_score:>3}/100  │  Cash Flow:     {data.cash_flow_score:>3}/100  │  Quality:  {data.quality_score:>3}/100 │   ║
║  └─────────────────────────────────────────────────────────────────────────────┘   ║
║                                                                                    ║
╠════════════════════════════════════════════════════════════════════════════════════╣
║                                                                                    ║
║  📈 VALUATION ({data.sector_valuation_rank})
║  ──────────────────────────────────────────────────────────────────────────────    ║
║  P/E Ratio:    {data.pe_ratio:>8.2f}    Forward P/E:  {data.forward_pe:>8.2f}    PEG Ratio:  {data.peg_ratio:>8.2f}
║  P/B Ratio:    {data.pb_ratio:>8.2f}    P/S Ratio:    {data.ps_ratio:>8.2f}    EV/EBITDA:  {data.ev_to_ebitda:>8.2f}
║  FCF Yield:    {data.fcf_yield:>7.2f}%
║                                                                                    ║
║  💰 PROFITABILITY ({data.sector_profit_rank})
║  ──────────────────────────────────────────────────────────────────────────────    ║
║  Gross Margin:   {data.gross_margin:>6.1f}%    Operating:    {data.operating_margin:>6.1f}%    Net Margin: {data.profit_margin:>6.1f}%
║  ROE:            {data.roe:>6.1f}%    ROA:          {data.roa:>6.1f}%
║                                                                                    ║
║  🚀 GROWTH ({data.sector_growth_rank})
║  ──────────────────────────────────────────────────────────────────────────────    ║
║  Revenue Growth: {data.revenue_growth:>6.1f}%    Earnings Growth: {data.earnings_growth:>6.1f}%
║  EPS TTM:     ${data.eps_ttm:>7.2f}    EPS Forward:  ${data.eps_forward:>7.2f}
║                                                                                    ║
║  💵 CASH FLOW                                                                      ║
║  ──────────────────────────────────────────────────────────────────────────────    ║
║  Operating CF: {fmt_big(data.operating_cash_flow):>12}    Free Cash Flow: {fmt_big(data.free_cash_flow):>12}
║  FCF Margin:   {data.fcf_margin:>6.1f}%           FCF/Share:    ${data.fcf_per_share:>8.2f}
║                                                                                    ║
║  🏦 FINANCIAL HEALTH                                                               ║
║  ──────────────────────────────────────────────────────────────────────────────    ║
║  Current Ratio:  {data.current_ratio:>6.2f}    Quick Ratio:   {data.quick_ratio:>6.2f}
║  Debt/Equity:    {data.debt_to_equity:>6.1f}    Interest Cov:  {data.interest_coverage:>6.1f}
║  Total Cash:  {fmt_big(data.total_cash):>12}    Total Debt: {fmt_big(data.total_debt):>12}
║  Net Debt:    {fmt_big(data.net_debt):>12}
║                                                                                    ║
║  💵 DIVIDENDS                                                                      ║
║  ──────────────────────────────────────────────────────────────────────────────    ║
║  Dividend Yield: {data.dividend_yield:>6.2f}%    Payout Ratio:  {data.dividend_payout_ratio:>6.1f}%
║                                                                                    ║
║  👥 OWNERSHIP                                                                      ║
║  ──────────────────────────────────────────────────────────────────────────────    ║
║  Insider:    {data.insider_ownership:>6.2f}%    Institutional: {data.institutional_ownership:>6.1f}%
║  Short %:    {data.short_pct_of_float:>6.2f}%    Short Ratio:   {data.short_ratio:>6.1f} days
║                                                                                    ║
║  📊 ANALYST OPINION                                                                ║
║  ──────────────────────────────────────────────────────────────────────────────    ║
║  Rating: {data.analyst_rating.upper():>12}  (Score: {data.analyst_score:.1f}/5)    Analysts: {data.num_analysts:>3}
║  Target: ${data.target_price_mean:>8.2f}  (Range: ${data.target_price_low:.0f} - ${data.target_price_high:.0f})
║  Upside Potential: {data.upside_potential:>+6.1f}%
║                                                                                    ║
║  📅 EARNINGS                                                                       ║
║  ──────────────────────────────────────────────────────────────────────────────    ║
║  Next Earnings: {data.next_earnings_date:>15}
║                                                                                    ║
╠════════════════════════════════════════════════════════════════════════════════════╣
║                                                                                    ║
║  ✅ STRENGTHS                          ⚠️ CONCERNS                                 ║
║  ────────────────────────────────────  ────────────────────────────────────────    ║""")

        # Strengths
        strengths = []
        concerns = []

        if data.profit_margin > 15:
            strengths.append("High profit margins")
        if data.roe > 20:
            strengths.append("Strong ROE")
        if data.revenue_growth > 15:
            strengths.append("Strong revenue growth")
        if data.has_positive_fcf and data.fcf_margin > 10:
            strengths.append("Strong free cash flow")
        if data.debt_to_equity < 50:
            strengths.append("Low debt levels")
        if data.current_ratio > 2:
            strengths.append("Excellent liquidity")
        if data.peg_ratio > 0 and data.peg_ratio < 1:
            strengths.append("Undervalued (low PEG)")
        if data.insider_ownership > 5:
            strengths.append("Good insider ownership")
        if data.upside_potential > 20:
            strengths.append("High analyst upside")

        if data.pe_ratio > 40:
            concerns.append("High P/E valuation")
        if data.debt_to_equity > 150:
            concerns.append("High debt levels")
        if data.profit_margin < 5:
            concerns.append("Low profit margins")
        if data.revenue_growth < 0:
            concerns.append("Revenue declining")
        if not data.has_positive_fcf:
            concerns.append("Negative free cash flow")
        if data.short_pct_of_float > 10:
            concerns.append("High short interest")
        if data.current_ratio < 1:
            concerns.append("Low liquidity")
        if data.price_to_52w_high_pct < -30:
            concerns.append("Well below 52w high")

        for i in range(max(len(strengths), len(concerns), 1)):
            s = strengths[i] if i < len(strengths) else ""
            c = concerns[i] if i < len(concerns) else ""
            print(f"║  {'✓ ' + s:34}  {'⚠ ' + c:36}    ║")

        print(f"""║                                                                                    ║
╚════════════════════════════════════════════════════════════════════════════════════╝
        """)

    def quick_scan(self, symbols: List[str]) -> pd.DataFrame:
        """Quick scan multiple stocks with key metrics"""

        results = []

        for symbol in symbols:
            try:
                data = self.analyze(symbol)
                if data:
                    results.append({
                        "Symbol": data.symbol,
                        "Name": data.name[:15],
                        "Sector": data.sector[:12],
                        "Price": f"${data.current_price:.2f}",
                        "MCap": f"${data.market_cap/1e9:.1f}B" if data.market_cap > 1e9 else f"${data.market_cap/1e6:.0f}M",
                        "P/E": f"{data.pe_ratio:.1f}" if data.pe_ratio else "-",
                        "PEG": f"{data.peg_ratio:.2f}" if data.peg_ratio else "-",
                        "ROE%": f"{data.roe:.1f}",
                        "Margin%": f"{data.profit_margin:.1f}",
                        "Growth%": f"{data.revenue_growth:.1f}",
                        "D/E": f"{data.debt_to_equity:.0f}",
                        "FCF Yld%": f"{data.fcf_yield:.1f}",
                        "Div%": f"{data.dividend_yield:.2f}",
                        "Overall": data.overall_score,
                        "Quality": data.quality_score,
                    })
                time.sleep(0.3)
            except:
                continue

        df = pd.DataFrame(results)
        if not df.empty:
            df = df.sort_values("Overall", ascending=False)

        return df


# ═══════════════════════════════════════════════════════════════
# COMMAND LINE INTERFACE
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys

    analyzer = FundamentalAnalyzer()

    if len(sys.argv) < 2:
        print("""
Enhanced Fundamental Analyzer
─────────────────────────────────────────
Commands:
  python fundamental_analyzer.py SYMBOL           - Detailed report
  python fundamental_analyzer.py quick SYM1 SYM2  - Quick comparison
  python fundamental_analyzer.py sector SYMBOL    - Sector comparison

Examples:
  python fundamental_analyzer.py NVDA
  python fundamental_analyzer.py quick NVDA AMD INTC AVGO
  python fundamental_analyzer.py sector AAPL
        """)
    elif sys.argv[1] == "quick":
        symbols = [s.upper() for s in sys.argv[2:]]
        if symbols:
            print(f"\n🔍 Quick scanning {len(symbols)} stocks...\n")
            df = analyzer.quick_scan(symbols)
            print(df.to_string(index=False))
    elif sys.argv[1] == "sector":
        symbol = sys.argv[2].upper() if len(sys.argv) > 2 else "AAPL"
        comparison = analyzer.get_sector_comparison(symbol)
        print(f"\n📊 SECTOR COMPARISON: {symbol} vs {comparison.get('sector', 'Unknown')}")
        print("─" * 60)
        for metric, data in comparison.get('comparisons', {}).items():
            print(f"  {metric:20} Value: {data['value']:>8.1f}  Sector Mid: {data['sector_mid']:>8.1f}  ({data['status']})")
    else:
        symbol = sys.argv[1].upper()
        analyzer.print_detailed_report(symbol)
