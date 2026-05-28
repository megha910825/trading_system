#!/usr/bin/env python3
"""
Combined Analyzer - Technical + Fundamental Analysis
The best of both worlds for stock selection
"""

from dataclasses import dataclass
from typing import Optional, Dict, List
import pandas as pd
import yfinance as yf

try:
    from technical_analyzer import TechnicalAnalyzer
    HAS_TECHNICAL = True
except ImportError:
    HAS_TECHNICAL = False

try:
    from fundamental_analyzer import FundamentalAnalyzer, FundamentalData
    HAS_FUNDAMENTAL = True
except ImportError:
    HAS_FUNDAMENTAL = False


@dataclass
class CombinedAnalysis:
    """Combined technical + fundamental analysis result"""
    symbol: str
    name: str
    sector: str
    current_price: float

    # Technical
    technical_signal: str  # STRONG BUY, BUY, HOLD, SELL
    technical_score: int
    entry_price: float
    stop_loss: float
    target_1: float
    target_2: float
    rsi: float
    trend: str
    setup_type: str

    # Fundamental
    fundamental_score: int
    valuation_score: int
    profitability_score: int
    growth_score: int
    health_score: int
    pe_ratio: float
    roe: float
    revenue_growth: float
    debt_to_equity: float

    # Combined
    combined_score: int
    combined_signal: str
    trade_quality: str  # A+, A, B, C, D
    recommendation: str


class CombinedAnalyzer:
    """
    Combines technical and fundamental analysis for better stock selection

    Scoring weights:
    - Technical: 50% (for timing)
    - Fundamental: 50% (for quality)

    Trade Quality:
    - A+: Combined score >= 80, both scores >= 70
    - A:  Combined score >= 70, both scores >= 60
    - B:  Combined score >= 60, both scores >= 50
    - C:  Combined score >= 50
    - D:  Combined score < 50
    """

    def __init__(self):
        self.technical = TechnicalAnalyzer() if HAS_TECHNICAL else None
        self.fundamental = FundamentalAnalyzer() if HAS_FUNDAMENTAL else None

    def analyze(self, symbol: str, df: pd.DataFrame = None) -> Optional[CombinedAnalysis]:
        """
        Perform combined technical and fundamental analysis

        Args:
            symbol: Stock ticker
            df: Price DataFrame (optional, will fetch if not provided)

        Returns:
            CombinedAnalysis object
        """

        if not HAS_TECHNICAL or not HAS_FUNDAMENTAL:
            print("❌ Both technical_analyzer.py and fundamental_analyzer.py required")
            return None

        # Get price data if not provided
        if df is None:
            try:
                ticker = yf.Ticker(symbol)
                df = ticker.history(period="6mo")
                df.columns = df.columns.str.lower()
            except Exception as e:
                print(f"❌ Could not fetch data for {symbol}: {e}")
                return None

        if df.empty:
            return None

        # Technical Analysis
        try:
            tech_result = self.technical.analyze_stock(df, symbol)
        except Exception as e:
            print(f"❌ Technical analysis error: {e}")
            return None

        # Fundamental Analysis
        try:
            fund_data = self.fundamental.analyze(symbol)
        except Exception as e:
            print(f"⚠️ Fundamental analysis error: {e}")
            fund_data = None

        # Extract technical data
        tech_score = tech_result.get('signal_score', 0)
        tech_signal = tech_result.get('signal_status', 'HOLD')

        # Extract fundamental data
        if fund_data:
            fund_score = fund_data.overall_score
            val_score = fund_data.valuation_score
            prof_score = fund_data.profitability_score
            growth_score = fund_data.growth_score
            health_score = fund_data.health_score
            pe = fund_data.pe_ratio
            roe = fund_data.roe
            rev_growth = fund_data.revenue_growth
            debt_eq = fund_data.debt_to_equity
            name = fund_data.name
            sector = fund_data.sector
        else:
            fund_score = 50  # Neutral if no data
            val_score = prof_score = growth_score = health_score = 50
            pe = roe = rev_growth = debt_eq = 0
            name = symbol
            sector = "Unknown"

        # Combined Score (50% technical, 50% fundamental)
        combined_score = int(tech_score * 0.5 + fund_score * 0.5)

        # Determine trade quality
        if combined_score >= 80 and tech_score >= 70 and fund_score >= 70:
            trade_quality = "A+"
        elif combined_score >= 70 and tech_score >= 60 and fund_score >= 60:
            trade_quality = "A"
        elif combined_score >= 60 and tech_score >= 50 and fund_score >= 50:
            trade_quality = "B"
        elif combined_score >= 50:
            trade_quality = "C"
        else:
            trade_quality = "D"

        # Determine combined signal
        if tech_signal in ["STRONG BUY", "BUY"] and fund_score >= 60:
            combined_signal = "STRONG BUY" if combined_score >= 70 else "BUY"
        elif tech_signal in ["STRONG BUY", "BUY"] and fund_score >= 40:
            combined_signal = "BUY (Weak Fundamentals)"
        elif tech_signal in ["STRONG BUY", "BUY"] and fund_score < 40:
            combined_signal = "CAUTION (Poor Fundamentals)"
        elif fund_score >= 70 and tech_score < 50:
            combined_signal = "WAIT (Good Company, Bad Timing)"
        else:
            combined_signal = "HOLD"

        # Generate recommendation
        if trade_quality == "A+":
            recommendation = "🟢 EXCELLENT: High-quality setup. Consider full position."
        elif trade_quality == "A":
            recommendation = "🟢 GOOD: Quality setup. Standard position size."
        elif trade_quality == "B":
            recommendation = "🟡 ACCEPTABLE: Proceed with reduced size."
        elif trade_quality == "C":
            recommendation = "🟠 MARGINAL: Only if conviction is high. Small size."
        else:
            recommendation = "🔴 AVOID: Poor quality. Look elsewhere."

        # Get entry/exit levels from technical
        entry = tech_result.get('ideal_entry', tech_result.get('entry', tech_result.get('current_price', 0)))

        return CombinedAnalysis(
            symbol=symbol,
            name=name,
            sector=sector,
            current_price=tech_result.get('current_price', 0),

            # Technical
            technical_signal=tech_signal,
            technical_score=tech_score,
            entry_price=entry,
            stop_loss=tech_result.get('stop_loss', 0),
            target_1=tech_result.get('target_1', 0),
            target_2=tech_result.get('target_2', 0),
            rsi=tech_result.get('rsi', 0),
            trend="BULLISH" if tech_result.get('uptrend', tech_result.get('above_ema50', False)) else "BEARISH",
            setup_type=tech_result.get('setup_type', 'N/A'),

            # Fundamental
            fundamental_score=fund_score,
            valuation_score=val_score,
            profitability_score=prof_score,
            growth_score=growth_score,
            health_score=health_score,
            pe_ratio=pe,
            roe=roe,
            revenue_growth=rev_growth,
            debt_to_equity=debt_eq,

            # Combined
            combined_score=combined_score,
            combined_signal=combined_signal,
            trade_quality=trade_quality,
            recommendation=recommendation
        )

    def screen_stocks(
        self,
        symbols: List[str],
        min_combined_score: int = 60,
        min_technical_score: int = 50,
        min_fundamental_score: int = 50,
        min_quality: str = "B"
    ) -> List[CombinedAnalysis]:
        """
        Screen multiple stocks using combined criteria

        Args:
            symbols: List of tickers to screen
            min_combined_score: Minimum combined score
            min_technical_score: Minimum technical score
            min_fundamental_score: Minimum fundamental score
            min_quality: Minimum trade quality (A+, A, B, C, D)

        Returns:
            List of CombinedAnalysis objects that pass filters
        """

        quality_order = {"A+": 5, "A": 4, "B": 3, "C": 2, "D": 1}
        min_quality_num = quality_order.get(min_quality, 3)

        results = []

        for symbol in symbols:
            try:
                analysis = self.analyze(symbol)

                if analysis is None:
                    continue

                # Apply filters
                if analysis.combined_score < min_combined_score:
                    continue
                if analysis.technical_score < min_technical_score:
                    continue
                if analysis.fundamental_score < min_fundamental_score:
                    continue
                if quality_order.get(analysis.trade_quality, 0) < min_quality_num:
                    continue

                results.append(analysis)

            except Exception as e:
                continue

        # Sort by combined score
        results.sort(key=lambda x: x.combined_score, reverse=True)

        return results

    def print_report(self, symbol: str):
        """Print detailed combined analysis report"""

        analysis = self.analyze(symbol)

        if not analysis:
            print(f"❌ Could not analyze {symbol}")
            return

        print(f"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║               🎯 COMBINED ANALYSIS: {analysis.symbol:^10}
║               Quality: {analysis.trade_quality}  |  Combined Score: {analysis.combined_score}/100
╠═══════════════════════════════════════════════════════════════════════════════╣
║  {analysis.name[:50]:^73} ║
║  {analysis.sector:^73} ║
║  Current Price: ${analysis.current_price:,.2f}
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║  📈 TECHNICAL ANALYSIS                     Score: {analysis.technical_score:>3}/100
║  ─────────────────────────────────────────────────────────────────────────    ║
║  Signal:    {analysis.technical_signal:^15}    Setup:   {analysis.setup_type:^15}
║  Trend:     {analysis.trend:^15}    RSI:     {analysis.rsi:>8.1f}
║                                                                               ║
║  Entry:     ${analysis.entry_price:>10,.2f}       Stop:    ${analysis.stop_loss:>10,.2f}
║  Target 1:  ${analysis.target_1:>10,.2f}       Target 2: ${analysis.target_2:>10,.2f}
║                                                                               ║
║  📊 FUNDAMENTAL ANALYSIS                   Score: {analysis.fundamental_score:>3}/100
║  ─────────────────────────────────────────────────────────────────────────    ║
║  Valuation:     {analysis.valuation_score:>3}/100    Profitability: {analysis.profitability_score:>3}/100
║  Growth:        {analysis.growth_score:>3}/100    Health:        {analysis.health_score:>3}/100
║                                                                               ║
║  P/E Ratio:     {analysis.pe_ratio:>8.1f}       ROE:           {analysis.roe:>7.1f}%
║  Revenue Growth:{analysis.revenue_growth:>7.1f}%       Debt/Equity:   {analysis.debt_to_equity:>8.1f}
║                                                                               ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║  🎯 COMBINED SIGNAL: {analysis.combined_signal:^50}
║                                                                               ║
║  {analysis.recommendation:^73} ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
        """)

    def to_dataframe(self, analyses: List[CombinedAnalysis]) -> pd.DataFrame:
        """Convert list of analyses to DataFrame"""

        return pd.DataFrame([
            {
                "Symbol": a.symbol,
                "Name": a.name[:20],
                "Quality": a.trade_quality,
                "Combined": a.combined_score,
                "Technical": a.technical_score,
                "Fundamental": a.fundamental_score,
                "Signal": a.combined_signal[:20],
                "Price": f"${a.current_price:.2f}",
                "Entry": f"${a.entry_price:.2f}",
                "Stop": f"${a.stop_loss:.2f}",
                "Target": f"${a.target_1:.2f}",
                "P/E": f"{a.pe_ratio:.1f}" if a.pe_ratio else "-",
                "ROE": f"{a.roe:.1f}%" if a.roe else "-",
            }
            for a in analyses
        ])


# ═══════════════════════════════════════════════════════════════
# COMMAND LINE
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys

    analyzer = CombinedAnalyzer()

    if len(sys.argv) < 2:
        print("""
Combined Analyzer Commands:
─────────────────────────────────────────
  python combined_analyzer.py SYMBOL              - Full combined analysis
  python combined_analyzer.py screen SYM1 SYM2... - Screen multiple stocks

Examples:
  python combined_analyzer.py NVDA
  python combined_analyzer.py screen NVDA AMD AAPL MSFT GOOGL
        """)
    elif sys.argv[1] == "screen":
        symbols = sys.argv[2:]
        if symbols:
            print(f"\n🔍 Screening {len(symbols)} stocks...")
            results = analyzer.screen_stocks(symbols, min_combined_score=55, min_quality="C")

            if results:
                df = analyzer.to_dataframe(results)
                print(f"\n✅ Found {len(results)} stocks passing filters:\n")
                print(df.to_string(index=False))
            else:
                print("❌ No stocks passed the filters")
    else:
        symbol = sys.argv[1].upper()
        analyzer.print_report(symbol)
