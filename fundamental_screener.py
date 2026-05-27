#!/usr/bin/env python3
"""
Advanced Fundamental Screener - Filter stocks by comprehensive financial criteria
Find quality stocks that match your investment criteria
"""

import pandas as pd
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import time
import json
from pathlib import Path

try:
    from fundamental_analyzer import FundamentalAnalyzer, FundamentalData
    HAS_ANALYZER = True
except ImportError:
    HAS_ANALYZER = False
    print("⚠️ fundamental_analyzer.py required")

try:
    import yfinance as yf
    HAS_YFINANCE = True
except ImportError:
    HAS_YFINANCE = False


class ScreenerPreset(Enum):
    """Pre-defined screening strategies"""
    VALUE = "value"
    GROWTH = "growth"
    QUALITY = "quality"
    DIVIDEND = "dividend"
    MOMENTUM = "momentum"
    GARP = "garp"  # Growth at Reasonable Price
    BUFFETT = "buffett"  # Warren Buffett style
    LYNCH = "lynch"  # Peter Lynch style


@dataclass
class ScreenerCriteria:
    """
    Comprehensive screening criteria
    Set to None to ignore a criterion
    """

    # ═══════════════════════════════════════════════════════════
    # VALUATION CRITERIA
    # ═══════════════════════════════════════════════════════════

    # P/E Ratio
    min_pe: Optional[float] = None
    max_pe: Optional[float] = None

    # Forward P/E
    min_forward_pe: Optional[float] = None
    max_forward_pe: Optional[float] = None

    # PEG Ratio (P/E to Growth)
    min_peg: Optional[float] = None
    max_peg: Optional[float] = None

    # Price to Book
    min_pb: Optional[float] = None
    max_pb: Optional[float] = None

    # Price to Sales
    min_ps: Optional[float] = None
    max_ps: Optional[float] = None

    # EV/EBITDA
    min_ev_ebitda: Optional[float] = None
    max_ev_ebitda: Optional[float] = None

    # Free Cash Flow Yield
    min_fcf_yield: Optional[float] = None
    max_fcf_yield: Optional[float] = None

    # ═══════════════════════════════════════════════════════════
    # PROFITABILITY CRITERIA
    # ═══════════════════════════════════════════════════════════

    # Profit Margin
    min_profit_margin: Optional[float] = None
    max_profit_margin: Optional[float] = None

    # Operating Margin
    min_operating_margin: Optional[float] = None

    # Gross Margin
    min_gross_margin: Optional[float] = None

    # Return on Equity
    min_roe: Optional[float] = None
    max_roe: Optional[float] = None

    # Return on Assets
    min_roa: Optional[float] = None

    # Must be profitable
    require_profitable: bool = False

    # ═══════════════════════════════════════════════════════════
    # GROWTH CRITERIA
    # ═══════════════════════════════════════════════════════════

    # Revenue Growth
    min_revenue_growth: Optional[float] = None
    max_revenue_growth: Optional[float] = None

    # Earnings Growth
    min_earnings_growth: Optional[float] = None

    # EPS Growth
    min_eps_growth: Optional[float] = None

    # ═══════════════════════════════════════════════════════════
    # FINANCIAL HEALTH CRITERIA
    # ═══════════════════════════════════════════════════════════

    # Debt to Equity
    min_debt_to_equity: Optional[float] = None
    max_debt_to_equity: Optional[float] = None

    # Current Ratio
    min_current_ratio: Optional[float] = None

    # Quick Ratio
    min_quick_ratio: Optional[float] = None

    # Interest Coverage
    min_interest_coverage: Optional[float] = None

    # Must have positive FCF
    require_positive_fcf: bool = False

    # ═══════════════════════════════════════════════════════════
    # DIVIDEND CRITERIA
    # ═══════════════════════════════════════════════════════════

    # Dividend Yield
    min_dividend_yield: Optional[float] = None
    max_dividend_yield: Optional[float] = None

    # Payout Ratio
    min_payout_ratio: Optional[float] = None
    max_payout_ratio: Optional[float] = None

    # Must pay dividend
    require_dividend: bool = False

    # ═══════════════════════════════════════════════════════════
    # SIZE CRITERIA
    # ═══════════════════════════════════════════════════════════

    # Market Cap (in billions)
    min_market_cap_b: Optional[float] = None
    max_market_cap_b: Optional[float] = None

    # ═══════════════════════════════════════════════════════════
    # SCORE CRITERIA
    # ═══════════════════════════════════════════════════════════

    # Minimum overall score
    min_overall_score: Optional[int] = None

    # Minimum quality score
    min_quality_score: Optional[int] = None

    # Minimum valuation score
    min_valuation_score: Optional[int] = None

    # Minimum profitability score
    min_profitability_score: Optional[int] = None

    # Minimum growth score
    min_growth_score: Optional[int] = None

    # Minimum health score
    min_health_score: Optional[int] = None

    # ═══════════════════════════════════════════════════════════
    # ANALYST CRITERIA
    # ═══════════════════════════════════════════════════════════

    # Upside potential
    min_upside_potential: Optional[float] = None

    # Analyst rating (1-5, lower is better)
    max_analyst_rating: Optional[float] = None

    # ═══════════════════════════════════════════════════════════
    # SECTOR FILTER
    # ═══════════════════════════════════════════════════════════

    # Include only these sectors (None = all)
    sectors: Optional[List[str]] = None

    # Exclude these sectors
    exclude_sectors: Optional[List[str]] = None


class FundamentalScreener:
    """
    Advanced fundamental stock screener

    Features:
    - 40+ screening criteria
    - Pre-defined screening strategies
    - Custom criteria support
    - Sector filtering
    - Score-based ranking
    """

    def __init__(self):
        if HAS_ANALYZER:
            self.analyzer = FundamentalAnalyzer()
        else:
            self.analyzer = None

        # Pre-defined screening presets
        self.presets = self._define_presets()

    def _define_presets(self) -> Dict[ScreenerPreset, ScreenerCriteria]:
        """Define pre-built screening strategies"""

        return {
            # ─────────────────────────────────────────────────────
            # VALUE INVESTING
            # ─────────────────────────────────────────────────────
            ScreenerPreset.VALUE: ScreenerCriteria(
                max_pe=20,
                max_pb=3,
                max_peg=1.5,
                min_profit_margin=5,
                min_roe=10,
                max_debt_to_equity=100,
                min_current_ratio=1.2,
                require_profitable=True,
                min_overall_score=50,
            ),

            # ─────────────────────────────────────────────────────
            # GROWTH INVESTING
            # ─────────────────────────────────────────────────────
            ScreenerPreset.GROWTH: ScreenerCriteria(
                min_revenue_growth=15,
                min_earnings_growth=10,
                min_profit_margin=10,
                min_roe=15,
                require_profitable=True,
                min_growth_score=60,
                min_overall_score=55,
            ),

            # ─────────────────────────────────────────────────────
            # QUALITY INVESTING
            # ─────────────────────────────────────────────────────
            ScreenerPreset.QUALITY: ScreenerCriteria(
                min_profit_margin=15,
                min_roe=20,
                min_roa=10,
                min_gross_margin=40,
                max_debt_to_equity=80,
                min_current_ratio=1.5,
                min_interest_coverage=5,
                require_profitable=True,
                require_positive_fcf=True,
                min_quality_score=65,
                min_profitability_score=65,
            ),

            # ─────────────────────────────────────────────────────
            # DIVIDEND INVESTING
            # ─────────────────────────────────────────────────────
            ScreenerPreset.DIVIDEND: ScreenerCriteria(
                min_dividend_yield=2,
                max_dividend_yield=8,  # Avoid yield traps
                max_payout_ratio=80,
                min_profit_margin=5,
                min_roe=10,
                max_debt_to_equity=100,
                require_dividend=True,
                require_profitable=True,
                require_positive_fcf=True,
                min_health_score=50,
            ),

            # ─────────────────────────────────────────────────────
            # GARP (Growth at Reasonable Price)
            # ─────────────────────────────────────────────────────
            ScreenerPreset.GARP: ScreenerCriteria(
                max_pe=30,
                max_peg=2.0,
                min_revenue_growth=10,
                min_earnings_growth=10,
                min_profit_margin=10,
                min_roe=15,
                max_debt_to_equity=100,
                require_profitable=True,
                min_overall_score=60,
                min_growth_score=55,
            ),

            # ─────────────────────────────────────────────────────
            # BUFFETT STYLE
            # ─────────────────────────────────────────────────────
            ScreenerPreset.BUFFETT: ScreenerCriteria(
                min_profit_margin=10,
                min_roe=15,
                min_roa=7,
                max_debt_to_equity=80,
                min_current_ratio=1.5,
                min_gross_margin=30,
                require_profitable=True,
                require_positive_fcf=True,
                min_market_cap_b=10,  # Large caps
                min_quality_score=60,
                min_health_score=60,
            ),

            # ─────────────────────────────────────────────────────
            # PETER LYNCH STYLE
            # ─────────────────────────────────────────────────────
            ScreenerPreset.LYNCH: ScreenerCriteria(
                max_peg=1.0,  # PEG < 1 is key for Lynch
                min_revenue_growth=15,
                min_earnings_growth=15,
                max_debt_to_equity=80,
                require_profitable=True,
                min_growth_score=65,
            ),
        }

    def screen(
        self,
        symbols: List[str],
        criteria: ScreenerCriteria,
        max_results: int = 50,
        sort_by: str = "overall_score"
    ) -> Tuple[pd.DataFrame, List[FundamentalData]]:
        """
        Screen stocks based on criteria

        Args:
            symbols: List of tickers to screen
            criteria: ScreenerCriteria object
            max_results: Maximum results to return
            sort_by: Column to sort by

        Returns:
            Tuple of (DataFrame summary, list of FundamentalData)
        """

        if not self.analyzer:
            print("❌ FundamentalAnalyzer not available")
            return pd.DataFrame(), []

        passed = []
        failed_reasons = {}

        total = len(symbols)

        for i, symbol in enumerate(symbols, 1):
            if i % 10 == 0:
                print(f"   Screening... {i}/{total}")

            try:
                data = self.analyzer.analyze(symbol)

                if data is None:
                    failed_reasons[symbol] = "No data"
                    continue

                # Check all criteria
                passed_all, fail_reason = self._check_criteria(data, criteria)

                if passed_all:
                    passed.append(data)
                else:
                    failed_reasons[symbol] = fail_reason

                time.sleep(0.2)  # Rate limiting

            except Exception as e:
                failed_reasons[symbol] = str(e)
                continue

        if not passed:
            print(f"   No stocks passed screening criteria")
            return pd.DataFrame(), []

        # Sort results
        sort_attr = sort_by if hasattr(passed[0], sort_by) else 'overall_score'
        passed.sort(key=lambda x: getattr(x, sort_attr, 0), reverse=True)

        # Limit results
        passed = passed[:max_results]

        # Create summary DataFrame
        df = self._create_summary_df(passed)

        print(f"   ✅ {len(passed)} stocks passed out of {total} screened")

        return df, passed

    def _check_criteria(
        self,
        data: FundamentalData,
        criteria: ScreenerCriteria
    ) -> Tuple[bool, str]:
        """Check if stock passes all criteria"""

        # ─────────────────────────────────────────────────────
        # SECTOR FILTERS
        # ─────────────────────────────────────────────────────
        if criteria.sectors:
            if data.sector not in criteria.sectors:
                return False, f"Sector {data.sector} not in allowed list"

        if criteria.exclude_sectors:
            if data.sector in criteria.exclude_sectors:
                return False, f"Sector {data.sector} excluded"

        # ─────────────────────────────────────────────────────
        # VALUATION
        # ─────────────────────────────────────────────────────
        if criteria.min_pe is not None:
            if data.pe_ratio > 0 and data.pe_ratio < criteria.min_pe:
                return False, f"P/E {data.pe_ratio:.1f} < min {criteria.min_pe}"

        if criteria.max_pe is not None:
            if data.pe_ratio <= 0 or data.pe_ratio > criteria.max_pe:
                return False, f"P/E {data.pe_ratio:.1f} > max {criteria.max_pe}"

        if criteria.max_peg is not None:
            if data.peg_ratio <= 0 or data.peg_ratio > criteria.max_peg:
                return False, f"PEG {data.peg_ratio:.2f} > max {criteria.max_peg}"

        if criteria.min_peg is not None:
            if data.peg_ratio > 0 and data.peg_ratio < criteria.min_peg:
                return False, f"PEG {data.peg_ratio:.2f} < min {criteria.min_peg}"

        if criteria.max_pb is not None:
            if data.pb_ratio > criteria.max_pb:
                return False, f"P/B {data.pb_ratio:.2f} > max {criteria.max_pb}"

        if criteria.max_ev_ebitda is not None:
            if data.ev_to_ebitda > criteria.max_ev_ebitda:
                return False, f"EV/EBITDA {data.ev_to_ebitda:.1f} > max {criteria.max_ev_ebitda}"

        if criteria.min_fcf_yield is not None:
            if data.fcf_yield < criteria.min_fcf_yield:
                return False, f"FCF Yield {data.fcf_yield:.1f}% < min {criteria.min_fcf_yield}%"

        # ─────────────────────────────────────────────────────
        # PROFITABILITY
        # ─────────────────────────────────────────────────────
        if criteria.require_profitable:
            if not data.is_profitable:
                return False, "Not profitable"

        if criteria.min_profit_margin is not None:
            if data.profit_margin < criteria.min_profit_margin:
                return False, f"Profit margin {data.profit_margin:.1f}% < min {criteria.min_profit_margin}%"

        if criteria.min_operating_margin is not None:
            if data.operating_margin < criteria.min_operating_margin:
                return False, f"Operating margin {data.operating_margin:.1f}% < min"

        if criteria.min_gross_margin is not None:
            if data.gross_margin < criteria.min_gross_margin:
                return False, f"Gross margin {data.gross_margin:.1f}% < min {criteria.min_gross_margin}%"

        if criteria.min_roe is not None:
            if data.roe < criteria.min_roe:
                return False, f"ROE {data.roe:.1f}% < min {criteria.min_roe}%"

        if criteria.max_roe is not None:
            if data.roe > criteria.max_roe:
                return False, f"ROE {data.roe:.1f}% > max {criteria.max_roe}%"

        if criteria.min_roa is not None:
            if data.roa < criteria.min_roa:
                return False, f"ROA {data.roa:.1f}% < min {criteria.min_roa}%"

        # ─────────────────────────────────────────────────────
        # GROWTH
        # ─────────────────────────────────────────────────────
        if criteria.min_revenue_growth is not None:
            if data.revenue_growth < criteria.min_revenue_growth:
                return False, f"Revenue growth {data.revenue_growth:.1f}% < min {criteria.min_revenue_growth}%"

        if criteria.max_revenue_growth is not None:
            if data.revenue_growth > criteria.max_revenue_growth:
                return False, f"Revenue growth {data.revenue_growth:.1f}% > max"

        if criteria.min_earnings_growth is not None:
            if data.earnings_growth < criteria.min_earnings_growth:
                return False, f"Earnings growth {data.earnings_growth:.1f}% < min"

        # ─────────────────────────────────────────────────────
        # FINANCIAL HEALTH
        # ─────────────────────────────────────────────────────
        if criteria.max_debt_to_equity is not None:
            if data.debt_to_equity > criteria.max_debt_to_equity:
                return False, f"D/E {data.debt_to_equity:.0f} > max {criteria.max_debt_to_equity}"

        if criteria.min_current_ratio is not None:
            if data.current_ratio < criteria.min_current_ratio:
                return False, f"Current ratio {data.current_ratio:.2f} < min {criteria.min_current_ratio}"

        if criteria.min_quick_ratio is not None:
            if data.quick_ratio < criteria.min_quick_ratio:
                return False, f"Quick ratio {data.quick_ratio:.2f} < min"

        if criteria.min_interest_coverage is not None:
            if data.interest_coverage < criteria.min_interest_coverage:
                return False, f"Interest coverage {data.interest_coverage:.1f} < min"

        if criteria.require_positive_fcf:
            if not data.has_positive_fcf:
                return False, "Negative free cash flow"

        # ─────────────────────────────────────────────────────
        # DIVIDENDS
        # ─────────────────────────────────────────────────────
        if criteria.require_dividend:
            if not data.is_dividend_payer or data.dividend_yield <= 0:
                return False, "Does not pay dividend"

        if criteria.min_dividend_yield is not None:
            if data.dividend_yield < criteria.min_dividend_yield:
                return False, f"Div yield {data.dividend_yield:.2f}% < min {criteria.min_dividend_yield}%"

        if criteria.max_dividend_yield is not None:
            if data.dividend_yield > criteria.max_dividend_yield:
                return False, f"Div yield {data.dividend_yield:.2f}% > max (yield trap risk)"

        if criteria.max_payout_ratio is not None:
            if data.dividend_payout_ratio > criteria.max_payout_ratio:
                return False, f"Payout ratio {data.dividend_payout_ratio:.0f}% > max"

        # ─────────────────────────────────────────────────────
        # SIZE
        # ─────────────────────────────────────────────────────
        market_cap_b = data.market_cap / 1e9 if data.market_cap else 0

        if criteria.min_market_cap_b is not None:
            if market_cap_b < criteria.min_market_cap_b:
                return False, f"Market cap ${market_cap_b:.1f}B < min ${criteria.min_market_cap_b}B"

        if criteria.max_market_cap_b is not None:
            if market_cap_b > criteria.max_market_cap_b:
                return False, f"Market cap ${market_cap_b:.1f}B > max"

        # ─────────────────────────────────────────────────────
        # SCORES
        # ─────────────────────────────────────────────────────
        if criteria.min_overall_score is not None:
            if data.overall_score < criteria.min_overall_score:
                return False, f"Overall score {data.overall_score} < min {criteria.min_overall_score}"

        if criteria.min_quality_score is not None:
            if data.quality_score < criteria.min_quality_score:
                return False, f"Quality score {data.quality_score} < min"

        if criteria.min_valuation_score is not None:
            if data.valuation_score < criteria.min_valuation_score:
                return False, f"Valuation score {data.valuation_score} < min"

        if criteria.min_profitability_score is not None:
            if data.profitability_score < criteria.min_profitability_score:
                return False, f"Profitability score {data.profitability_score} < min"

        if criteria.min_growth_score is not None:
            if data.growth_score < criteria.min_growth_score:
                return False, f"Growth score {data.growth_score} < min"

        if criteria.min_health_score is not None:
            if data.health_score < criteria.min_health_score:
                return False, f"Health score {data.health_score} < min"

        # ─────────────────────────────────────────────────────
        # ANALYST
        # ─────────────────────────────────────────────────────
        if criteria.min_upside_potential is not None:
            if data.upside_potential < criteria.min_upside_potential:
                return False, f"Upside {data.upside_potential:.1f}% < min"

        if criteria.max_analyst_rating is not None:
            if data.analyst_score > criteria.max_analyst_rating:
                return False, f"Analyst rating {data.analyst_score:.1f} > max (worse)"

        # All criteria passed!
        return True, ""

    def _create_summary_df(self, data_list: List[FundamentalData]) -> pd.DataFrame:
        """Create summary DataFrame from results"""

        rows = []

        for d in data_list:
            market_cap_str = f"${d.market_cap/1e9:.1f}B" if d.market_cap > 1e9 else f"${d.market_cap/1e6:.0f}M"

            rows.append({
                "Symbol": d.symbol,
                "Name": d.name[:20],
                "Sector": d.sector[:15],
                "MCap": market_cap_str,
                "Price": f"${d.current_price:.2f}",
                "P/E": f"{d.pe_ratio:.1f}" if d.pe_ratio > 0 else "-",
                "PEG": f"{d.peg_ratio:.2f}" if d.peg_ratio > 0 else "-",
                "ROE%": f"{d.roe:.1f}",
                "Margin%": f"{d.profit_margin:.1f}",
                "Growth%": f"{d.revenue_growth:.1f}",
                "D/E": f"{d.debt_to_equity:.0f}" if d.debt_to_equity else "-",
                "Div%": f"{d.dividend_yield:.2f}" if d.dividend_yield else "-",
                "Overall": d.overall_score,
                "Quality": d.quality_score,
                "Upside%": f"{d.upside_potential:.0f}" if d.upside_potential else "-",
            })

        return pd.DataFrame(rows)

    def screen_with_preset(
        self,
        symbols: List[str],
        preset: ScreenerPreset,
        max_results: int = 50
    ) -> Tuple[pd.DataFrame, List[FundamentalData]]:
        """
        Screen using pre-defined strategy

        Args:
            symbols: List of tickers
            preset: ScreenerPreset enum value
            max_results: Max results

        Returns:
            Tuple of (DataFrame, list of FundamentalData)
        """

        criteria = self.presets.get(preset)

        if criteria is None:
            print(f"❌ Unknown preset: {preset}")
            return pd.DataFrame(), []

        print(f"\n📊 Screening with {preset.value.upper()} strategy...")

        return self.screen(symbols, criteria, max_results)

    def print_results(
        self,
        df: pd.DataFrame,
        title: str = "SCREENING RESULTS"
    ):
        """Print formatted results"""

        print(f"""
╔═══════════════════════════════════════════════════════════════════════════════════════════════════╗
║                               📊 {title:^30}                                    ║
╠═══════════════════════════════════════════════════════════════════════════════════════════════════╣
        """)

        if df.empty:
            print("║  No stocks passed the screening criteria                                                          ║")
        else:
            print(df.to_string(index=False))

        print("""
╚═══════════════════════════════════════════════════════════════════════════════════════════════════╝
        """)

    def compare_presets(
        self,
        symbols: List[str],
        presets: List[ScreenerPreset] = None
    ):
        """Compare results across different screening strategies"""

        if presets is None:
            presets = [
                ScreenerPreset.VALUE,
                ScreenerPreset.GROWTH,
                ScreenerPreset.QUALITY,
                ScreenerPreset.GARP,
            ]

        print(f"""
╔═══════════════════════════════════════════════════════════════════════════════════════════════════╗
║                           📊 SCREENING STRATEGY COMPARISON                                        ║
║                           Testing {len(symbols)} stocks across {len(presets)} strategies                             ║
╠═══════════════════════════════════════════════════════════════════════════════════════════════════╣
        """)

        results = {}

        for preset in presets:
            print(f"\n   Testing {preset.value.upper()}...")
            df, _ = self.screen_with_preset(symbols, preset, max_results=10)
            results[preset.value] = df

        print(f"""
╠═══════════════════════════════════════════════════════════════════════════════════════════════════╣
║                                      RESULTS SUMMARY                                              ║
╠═══════════════════════════════════════════════════════════════════════════════════════════════════╣
        """)

        for strategy, df in results.items():
            passed = len(df)
            top_picks = ", ".join(df['Symbol'].head(3).tolist()) if not df.empty else "None"
            print(f"║  {strategy.upper():12}: {passed:>3} passed  |  Top 3: {top_picks:<40} ║")

        # Find stocks that pass multiple strategies
        all_symbols = []
        for df in results.values():
            if not df.empty:
                all_symbols.extend(df['Symbol'].tolist())

        from collections import Counter
        symbol_counts = Counter(all_symbols)
        multi_pass = [(s, c) for s, c in symbol_counts.items() if c >= 2]
        multi_pass.sort(key=lambda x: x[1], reverse=True)

        if multi_pass:
            print(f"""║                                                                                                   ║
║  🏆 STOCKS PASSING MULTIPLE STRATEGIES:                                                           ║""")
            for symbol, count in multi_pass[:5]:
                strategies = [s for s, df in results.items() if not df.empty and symbol in df['Symbol'].values]
                print(f"║     {symbol:8} - {count} strategies: {', '.join(strategies):<50} ║")

        print("""╚═══════════════════════════════════════════════════════════════════════════════════════════════════╝
        """)

        return results


# ═══════════════════════════════════════════════════════════════
# DEFAULT STOCK UNIVERSES
# ═══════════════════════════════════════════════════════════════

# S&P 500 Tech Leaders
SP500_TECH = [
    "AAPL", "MSFT", "NVDA", "GOOGL", "META", "AVGO", "ORCL", "CSCO",
    "CRM", "AMD", "ADBE", "ACN", "INTC", "QCOM", "TXN", "AMAT",
    "MU", "LRCX", "ADI", "KLAC", "SNPS", "CDNS", "MRVL", "NXPI"
]

# S&P 500 Top Holdings
SP500_TOP = [
    "AAPL", "MSFT", "NVDA", "GOOGL", "AMZN", "META", "BRK-B", "LLY",
    "AVGO", "JPM", "TSLA", "UNH", "XOM", "V", "MA", "PG",
    "JNJ", "HD", "COST", "MRK", "ABBV", "CVX", "CRM", "BAC"
]

# Growth Stocks
GROWTH_STOCKS = [
    "NVDA", "AMD", "TSLA", "META", "GOOGL", "AMZN", "CRM", "NOW",
    "SNOW", "DDOG", "NET", "CRWD", "ZS", "PANW", "TEAM", "MDB",
    "SHOP", "SQ", "PYPL", "ROKU", "TTD", "TWLO", "OKTA", "DOCU"
]

# Dividend Aristocrats (sample)
DIVIDEND_ARISTOCRATS = [
    "JNJ", "PG", "KO", "PEP", "MMM", "ABT", "ABBV", "MCD",
    "WMT", "HD", "LOW", "TGT", "CVX", "XOM", "CL", "ITW",
    "GPC", "SWK", "EMR", "ADP", "SHW", "CINF", "AFL", "BEN"
]

# German DAX
DAX_STOCKS = [
    "SAP.DE", "SIE.DE", "ALV.DE", "DTE.DE", "BAS.DE", "BAYN.DE",
    "BMW.DE", "MBG.DE", "VOW3.DE", "ADS.DE", "MRK.DE", "DBK.DE"
]

# Indian Nifty 50 (sample)
NIFTY_STOCKS = [
    "TCS.NS", "RELIANCE.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS",
    "HINDUNILVR.NS", "SBIN.NS", "BHARTIARTL.NS", "KOTAKBANK.NS", "ITC.NS"
]


# ═══════════════════════════════════════════════════════════════
# COMMAND LINE INTERFACE
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys

    screener = FundamentalScreener()

    if len(sys.argv) < 2:
        print("""
Fundamental Screener Commands:
─────────────────────────────────────────────────────────────────────────
  python fundamental_screener.py value              - Value investing screen
  python fundamental_screener.py growth             - Growth investing screen
  python fundamental_screener.py quality            - Quality investing screen
  python fundamental_screener.py dividend           - Dividend investing screen
  python fundamental_screener.py garp               - Growth at Reasonable Price
  python fundamental_screener.py buffett            - Warren Buffett style
  python fundamental_screener.py lynch              - Peter Lynch style
  python fundamental_screener.py compare            - Compare all strategies
  python fundamental_screener.py custom             - Show custom criteria example

Stock Universes:
  --universe tech      - S&P 500 Tech stocks
  --universe sp500     - S&P 500 Top holdings
  --universe growth    - Growth stocks
  --universe dividend  - Dividend aristocrats
  --universe dax       - German DAX
  --universe nifty     - Indian Nifty 50

Examples:
  python fundamental_screener.py value
  python fundamental_screener.py growth --universe tech
  python fundamental_screener.py compare
  python fundamental_screener.py quality --universe sp500
        """)
        sys.exit(0)

    command = sys.argv[1].lower()

    # Determine universe
    universe = SP500_TOP  # Default

    if "--universe" in sys.argv:
        idx = sys.argv.index("--universe")
        if idx + 1 < len(sys.argv):
            universe_name = sys.argv[idx + 1].lower()
            if universe_name == "tech":
                universe = SP500_TECH
            elif universe_name == "sp500":
                universe = SP500_TOP
            elif universe_name == "growth":
                universe = GROWTH_STOCKS
            elif universe_name == "dividend":
                universe = DIVIDEND_ARISTOCRATS
            elif universe_name == "dax":
                universe = DAX_STOCKS
            elif universe_name == "nifty":
                universe = NIFTY_STOCKS

    # Execute command
    if command == "value":
        df, _ = screener.screen_with_preset(universe, ScreenerPreset.VALUE)
        screener.print_results(df, "VALUE INVESTING SCREEN")

    elif command == "growth":
        df, _ = screener.screen_with_preset(universe, ScreenerPreset.GROWTH)
        screener.print_results(df, "GROWTH INVESTING SCREEN")

    elif command == "quality":
        df, _ = screener.screen_with_preset(universe, ScreenerPreset.QUALITY)
        screener.print_results(df, "QUALITY INVESTING SCREEN")

    elif command == "dividend":
        df, _ = screener.screen_with_preset(DIVIDEND_ARISTOCRATS, ScreenerPreset.DIVIDEND)
        screener.print_results(df, "DIVIDEND INVESTING SCREEN")

    elif command == "garp":
        df, _ = screener.screen_with_preset(universe, ScreenerPreset.GARP)
        screener.print_results(df, "GARP SCREEN")

    elif command == "buffett":
        df, _ = screener.screen_with_preset(universe, ScreenerPreset.BUFFETT)
        screener.print_results(df, "BUFFETT STYLE SCREEN")

    elif command == "lynch":
        df, _ = screener.screen_with_preset(universe, ScreenerPreset.LYNCH)
        screener.print_results(df, "PETER LYNCH STYLE SCREEN")

    elif command == "compare":
        screener.compare_presets(universe)

    elif command == "custom":
        print("""
CUSTOM SCREENING EXAMPLE:
─────────────────────────────────────────────────────────────────────────

from fundamental_screener import FundamentalScreener, ScreenerCriteria

screener = FundamentalScreener()

# Define custom criteria
criteria = ScreenerCriteria(
    # Valuation
    max_pe=25,
    max_peg=2.0,

    # Profitability
    min_profit_margin=10,
    min_roe=15,
    require_profitable=True,

    # Growth
    min_revenue_growth=10,

    # Health
    max_debt_to_equity=100,
    min_current_ratio=1.5,
    require_positive_fcf=True,

    # Scores
    min_overall_score=60,
    min_quality_score=55,

    # Sector filter (optional)
    sectors=["Technology", "Healthcare"],

    # Size
    min_market_cap_b=10,  # $10B+
)

# Run screen
symbols = ["AAPL", "MSFT", "NVDA", "GOOGL", ...]
df, results = screener.screen(symbols, criteria)

print(df)
        """)

    else:
        print(f"Unknown command: {command}")
        print("Use: value, growth, quality, dividend, garp, buffett, lynch, compare, or custom")
