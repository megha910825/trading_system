#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════════
ENHANCED DAILY WORKFLOW - Complete Trading System
═══════════════════════════════════════════════════════════════════════════════════
Version: 2.0
Author: Trading System
Optimized for: Germany Timezone

Features:
- Market Regime Analysis
- Technical + Fundamental Combined Signals
- Earnings Calendar Integration
- Insider Activity Tracking
- Performance Monitoring
- Multi-market Support (US, Germany, India)

Usage:
    python daily_workflow.py morning      # 08:00 - Start of day routine
    python daily_workflow.py midday       # 12:00 - Midday check
    python daily_workflow.py afternoon    # 15:30 - US market open
    python daily_workflow.py evening      # 20:00 - End of day review
    python daily_workflow.py scan         # Full market scan
    python daily_workflow.py fundamentals # Pure fundamental analysis
    python daily_workflow.py insider      # Insider activity scan
    python daily_workflow.py earnings     # Earnings calendar
    python daily_workflow.py schedule     # Show daily schedule
═══════════════════════════════════════════════════════════════════════════════════
"""

import argparse
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import sys
import time

# ═══════════════════════════════════════════════════════════════════════════════
# IMPORTS WITH ERROR HANDLING
# ═══════════════════════════════════════════════════════════════════════════════

print("🔄 Loading modules...")

# Timezone
try:
    import pytz
    BERLIN = pytz.timezone("Europe/Berlin")
    HAS_PYTZ = True
except ImportError:
    HAS_PYTZ = False
    BERLIN = None
    print("   ⚠️ pytz not installed - using local time")

# Core Modules
try:
    from global_signal_generator import GlobalSignalGenerator
    HAS_SIGNALS = True
except ImportError:
    HAS_SIGNALS = False

try:
    from global_universe_manager import GlobalUniverseManager
    HAS_UNIVERSE = True
except ImportError:
    HAS_UNIVERSE = False

try:
    from technical_analyzer import TechnicalAnalyzer
    HAS_ANALYZER = True
except ImportError:
    HAS_ANALYZER = False

try:
    from alert_system import AlertSystem
    HAS_ALERTS = True
except ImportError:
    HAS_ALERTS = False

try:
    from market_config import MARKETS, get_market_status
    HAS_MARKETS = True
except ImportError:
    HAS_MARKETS = False
    def get_market_status():
        return {"US": "Unknown", "DE": "Unknown", "IN": "Unknown"}
    class DummyMarket:
        def __init__(self, name, currency):
            self.name = name
            self.currency = currency
    MARKETS = {
        "US": DummyMarket("United States", "USD"),
        "DE": DummyMarket("Germany", "EUR"),
        "IN": DummyMarket("India", "INR")
    }

# Journal & Tracking
try:
    from trade_journal import TradeJournal
    HAS_JOURNAL = True
except ImportError:
    HAS_JOURNAL = False

try:
    from market_regime import MarketRegimeFilter
    HAS_REGIME = True
except ImportError:
    HAS_REGIME = False

try:
    from performance_tracker import PerformanceTracker
    HAS_TRACKER = True
except ImportError:
    HAS_TRACKER = False

# Fundamental Analysis
try:
    from fundamental_analyzer import FundamentalAnalyzer
    HAS_FUNDAMENTALS = True
except ImportError:
    HAS_FUNDAMENTALS = False

try:
    from combined_analyzer import CombinedAnalyzer
    HAS_COMBINED = True
except ImportError:
    HAS_COMBINED = False

try:
    from fundamental_screener import FundamentalScreener, ScreenerPreset
    HAS_SCREENER = True
except ImportError:
    HAS_SCREENER = False

# Earnings & Insider
try:
    from earnings_calendar import EarningsCalendar
    HAS_EARNINGS = True
except ImportError:
    HAS_EARNINGS = False

try:
    from insider_tracker import InsiderTracker
    HAS_INSIDER = True
except ImportError:
    HAS_INSIDER = False

# Data
try:
    import yfinance as yf
    HAS_YFINANCE = True
except ImportError:
    HAS_YFINANCE = False

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False
    pd = None

# Config
try:
    import config
    ACCOUNT_SIZE = getattr(config, 'ACCOUNT_SIZE', 50000)
    MONTHLY_TARGET = getattr(config, 'MONTHLY_TARGET', 0.03)
    RISK_PER_TRADE = getattr(config, 'RISK_PER_TRADE', 0.015)
    MAX_POSITIONS = getattr(config, 'MAX_POSITIONS', 8)
except ImportError:
    ACCOUNT_SIZE = 50000
    MONTHLY_TARGET = 0.03
    RISK_PER_TRADE = 0.015
    MAX_POSITIONS = 8

print("✅ Modules loaded.\n")


# ═══════════════════════════════════════════════════════════════════════════════
# CONSTANTS & WATCHLISTS
# ═══════════════════════════════════════════════════════════════════════════════

WATCHLIST_US = [
    "NVDA", "AMD", "AAPL", "MSFT", "GOOGL", "META", "AMZN", "TSLA",
    "AVGO", "CRM", "NFLX", "ADBE", "ORCL", "INTC", "QCOM", "MU",
    "NOW", "PANW", "CRWD", "SNOW"
]

WATCHLIST_DE = [
    "SAP.DE", "SIE.DE", "ALV.DE", "DTE.DE", "BAS.DE", "BAYN.DE",
    "BMW.DE", "MBG.DE", "ADS.DE", "MRK.DE"
]

WATCHLIST_IN = [
    "TCS.NS", "RELIANCE.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS",
    "HINDUNILVR.NS", "SBIN.NS", "BHARTIARTL.NS", "KOTAKBANK.NS", "ITC.NS"
]

ALL_WATCHLIST = WATCHLIST_US + WATCHLIST_DE + WATCHLIST_IN


# ═══════════════════════════════════════════════════════════════════════════════
# UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def get_german_time() -> datetime:
    """Get current time in Germany"""
    if HAS_PYTZ and BERLIN:
        return datetime.now(BERLIN)
    return datetime.now()


def print_header(title: str, emoji: str = "📊"):
    """Print formatted header"""
    now = get_german_time()
    width = 85
    print(f"""
╔{'═' * width}╗
║  {emoji}  {title:^{width - 8}}  ║
║  {now.strftime('%A, %Y-%m-%d %H:%M'):^{width - 4}} (German Time)   ║
╚{'═' * width}╝""")


def print_section(title: str, num: int = None):
    """Print section header"""
    if num:
        print(f"\n{'═' * 80}")
        print(f"  {num}️⃣   {title}")
        print(f"{'═' * 80}")
    else:
        print(f"\n{'─' * 80}")
        print(f"  📌 {title}")
        print(f"{'─' * 80}")


def print_subsection(title: str):
    """Print subsection header"""
    print(f"\n  ▸ {title}")
    print(f"  {'─' * 70}")


def fmt_currency(value: float, currency: str = "$") -> str:
    """Format currency value"""
    if value is None:
        return f"{currency}0"
    if abs(value) >= 1_000_000:
        return f"{currency}{value/1_000_000:.2f}M"
    elif abs(value) >= 1_000:
        return f"{currency}{value/1_000:.1f}K"
    else:
        return f"{currency}{value:.2f}"


def get_current_price(symbol: str) -> float:
    """Get current price for a symbol"""
    if not HAS_YFINANCE:
        return 0
    try:
        ticker = yf.Ticker(symbol)
        return ticker.fast_info.get('lastPrice', 0)
    except:
        return 0


def calculate_position_size(entry: float, stop: float, multiplier: float = 1.0) -> dict:
    """Calculate position size based on risk parameters"""
    if entry <= 0 or stop <= 0 or stop >= entry:
        return {"shares": 0, "value": 0, "risk": 0, "risk_per_share": 0}

    risk_per_share = entry - stop
    risk_amount = ACCOUNT_SIZE * RISK_PER_TRADE * multiplier
    shares = int(risk_amount / risk_per_share)
    value = shares * entry

    return {
        "shares": shares,
        "value": value,
        "risk": risk_amount,
        "risk_per_share": risk_per_share
    }


# ═══════════════════════════════════════════════════════════════════════════════
# MARKET REGIME FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def check_market_regime() -> Tuple[float, bool, str]:
    """Check current market regime - returns (multiplier, can_trade, description)"""
    if not HAS_REGIME:
        return 1.0, True, "Unknown (market_regime.py not available)"

    try:
        mrf = MarketRegimeFilter()
        conditions = mrf.analyze()

        regime_emoji = {
            "STRONG_BULL": "🟢🟢", "BULL": "🟢", "NEUTRAL": "🟡",
            "BEAR": "🔴", "STRONG_BEAR": "🔴🔴"
        }.get(conditions.regime.value, "⚪")

        desc = f"{regime_emoji} {conditions.regime.value} | SPY: ${conditions.spy_price:.2f} ({conditions.spy_change_1d:+.2f}%) | VIX: {conditions.vix_level:.1f}"
        return conditions.position_mult, conditions.can_trade_long, desc
    except Exception as e:
        return 1.0, True, f"Error: {e}"


def print_regime_report() -> Tuple[float, bool]:
    """Print detailed market regime report"""
    if not HAS_REGIME:
        print("   ⚠️ Market regime filter not available")
        return 1.0, True

    try:
        mrf = MarketRegimeFilter()
        mrf.print_report()
        conditions = mrf.analyze()

        if not conditions.can_trade_long:
            print("\n   ⚠️  WARNING: Market conditions unfavorable for longs!")
            print("   Consider staying in cash or reduced position sizes.")

        return conditions.position_mult, conditions.can_trade_long
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return 1.0, True


# ═══════════════════════════════════════════════════════════════════════════════
# POSITION & PERFORMANCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def check_open_positions(detailed: bool = False):
    """Check and display open positions"""
    if not HAS_JOURNAL:
        print("   ⚠️ Trade journal not available")
        return pd.DataFrame() if HAS_PANDAS else None

    try:
        journal = TradeJournal()
        open_trades = journal.get_open_trades()

        if open_trades.empty:
            print("   📂 No open positions")
            return open_trades

        print(f"\n   📂 {len(open_trades)} Open Positions:\n")

        total_pnl = 0
        total_value = 0

        for _, t in open_trades.iterrows():
            symbol = t['symbol']
            entry = t['entry_price']
            shares = t['shares']
            stop = t['stop_loss']
            target = t['target_1']

            current = get_current_price(symbol) or entry
            pnl = (current - entry) * shares
            pnl_pct = (current / entry - 1) * 100 if entry > 0 else 0
            value = current * shares

            total_pnl += pnl
            total_value += value

            risk_per_share = entry - stop
            r_multiple = (current - entry) / risk_per_share if risk_per_share > 0 else 0

            pnl_emoji = "🟢" if pnl >= 0 else "🔴"

            print(f"   {pnl_emoji} {symbol:8}")
            print(f"      Entry: ${entry:>8.2f}  │  Current: ${current:>8.2f}  │  Target: ${target:>8.2f}")
            print(f"      Stop:  ${stop:>8.2f}  │  P&L: ${pnl:>+8.2f} ({pnl_pct:>+5.1f}%)  │  R: {r_multiple:>+.2f}")

            # Alerts
            if current > 0:
                if current <= stop * 1.02:
                    print(f"      ⚠️  NEAR STOP LOSS!")
                elif current >= target * 0.98:
                    print(f"      🎯 NEAR TARGET - Consider taking profits")
                elif r_multiple >= 2:
                    print(f"      💡 2R+ profit - Consider trailing stop")

            # Detailed analysis
            if detailed:
                if HAS_FUNDAMENTALS:
                    try:
                        fa = FundamentalAnalyzer()
                        fund_data = fa.analyze(symbol)
                        if fund_data:
                            score = fund_data.overall_score
                            emoji = "✅" if score >= 60 else "⚠️" if score >= 40 else "🔴"
                            print(f"      {emoji} Fundamental Score: {score}/100")
                    except:
                        pass

                if HAS_INSIDER:
                    try:
                        tracker = InsiderTracker()
                        insider = tracker.get_insider_summary(symbol)
                        if insider and insider.sentiment_score != 0:
                            emoji = "🟢" if insider.sentiment_score > 20 else "🔴" if insider.sentiment_score < -20 else "🟡"
                            print(f"      {emoji} Insider Sentiment: {insider.insider_sentiment} ({insider.sentiment_score:+d})")
                    except:
                        pass

                if HAS_EARNINGS:
                    try:
                        ec = EarningsCalendar()
                        earnings = ec.get_earnings_date(symbol)
                        if earnings.get('is_this_week'):
                            print(f"      ⚠️  EARNINGS THIS WEEK: {earnings['next_earnings']}")
                        elif earnings.get('is_soon'):
                            print(f"      📅 Earnings soon: {earnings['next_earnings']} ({earnings['days_until']} days)")
                    except:
                        pass
            print()

        print(f"   {'─' * 70}")
        pnl_emoji = "🟢" if total_pnl >= 0 else "🔴"
        print(f"   {pnl_emoji} Total Unrealized P&L: ${total_pnl:>+,.2f}")
        print(f"   💼 Total Position Value: ${total_value:>,.2f}")
        print(f"   📊 Portfolio Exposure: {(total_value / ACCOUNT_SIZE * 100):.1f}%")

        return open_trades
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return pd.DataFrame() if HAS_PANDAS else None


def check_monthly_progress():
    """Check and display monthly trading progress"""
    if not HAS_TRACKER:
        print("   ⚠️ Performance tracker not available")
        return
    try:
        tracker = PerformanceTracker()
        tracker.print_dashboard()
    except Exception as e:
        print(f"   ❌ Error: {e}")


# ═══════════════════════════════════════════════════════════════════════════════
# EARNINGS & INSIDER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def check_earnings(symbols: List[str] = None, days_ahead: int = 14):
    """Check earnings calendar for watchlist"""
    if not HAS_EARNINGS:
        print("   ⚠️ Earnings calendar not available")
        return

    if symbols is None:
        symbols = WATCHLIST_US

    try:
        ec = EarningsCalendar()

        # Check open positions first
        if HAS_JOURNAL:
            journal = TradeJournal()
            open_trades = journal.get_open_trades()

            if not open_trades.empty:
                print_subsection("Open Position Earnings Check")
                found_earnings = False

                for symbol in open_trades['symbol'].unique():
                    info = ec.get_earnings_date(symbol)
                    if info.get('is_this_week'):
                        print(f"   ⚠️  {symbol:8} EARNINGS THIS WEEK: {info['next_earnings']} ({info['days_until']} days)")
                        print(f"            Consider: Close position or reduce size before earnings")
                        found_earnings = True
                    elif info.get('is_soon'):
                        print(f"   📅 {symbol:8} Earnings: {info['next_earnings']} ({info['days_until']} days)")
                        found_earnings = True

                if not found_earnings:
                    print("   ✅ No upcoming earnings for open positions")

        # Check watchlist
        print_subsection(f"Watchlist Earnings (Next {days_ahead} Days)")
        upcoming = ec.scan_upcoming_earnings(symbols, days_ahead)

        if not upcoming.empty:
            for _, row in upcoming.iterrows():
                if row['Days Until'] <= 7:
                    print(f"   ⚠️  {row['Symbol']:8} - {row['Earnings Date']} ({row['Days Until']} days) Beat Rate: {row['Beat Rate %']:.0f}%")
                else:
                    print(f"   📅 {row['Symbol']:8} - {row['Earnings Date']} ({row['Days Until']} days)")
        else:
            print(f"   ✅ No earnings in next {days_ahead} days for watchlist")
    except Exception as e:
        print(f"   ❌ Error: {e}")


def check_insider_activity(symbols: List[str] = None):
    """Check insider buying activity"""
    if not HAS_INSIDER:
        print("   ⚠️ Insider tracker not available")
        return

    if symbols is None:
        symbols = WATCHLIST_US

    try:
        tracker = InsiderTracker()

        # Check open positions first
        if HAS_JOURNAL:
            journal = TradeJournal()
            open_trades = journal.get_open_trades()

            if not open_trades.empty:
                print_subsection("Open Position Insider Activity")

                for symbol in open_trades['symbol'].unique():
                    summary = tracker.get_insider_summary(symbol)
                    if summary:
                        if summary.sentiment_score >= 30:
                            print(f"   🟢 {symbol:8} {summary.insider_sentiment:15} (Score: {summary.sentiment_score:+4d}) - {summary.buys_3m} buys")
                        elif summary.sentiment_score <= -30:
                            print(f"   🔴 {symbol:8} {summary.insider_sentiment:15} (Score: {summary.sentiment_score:+4d}) - ⚠️ Heavy selling")
                        else:
                            print(f"   🟡 {symbol:8} {summary.insider_sentiment:15} (Score: {summary.sentiment_score:+4d})")

                        if summary.has_cluster_buying:
                            print(f"            🎯 Cluster buying detected! ({summary.cluster_buy_count} insiders)")

        # Scan watchlist
        print_subsection("Watchlist Insider Buying Scan")
        df = tracker.scan_for_insider_buying(symbols[:20], min_buys=1, min_buy_value=50000, days=90)

        if not df.empty:
            print(f"\n   🏆 Stocks with Recent Insider Buying:\n")
            for _, row in df.head(10).iterrows():
                cluster = "🎯" if row.get('Cluster') == '✅' else "  "
                print(f"   {cluster} {row['Symbol']:8} {row['Sentiment']:15} Score: {row['Score']:>+4} │ Buys: {row['Buys (3M)']} │ Value: {row['Buy Value']:>10}")
        else:
            print("   No significant insider buying detected")
    except Exception as e:
        print(f"   ❌ Error: {e}")


# ═══════════════════════════════════════════════════════════════════════════════
# SIGNAL GENERATION FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def generate_signals(markets: List[str] = None, position_mult: float = 1.0) -> Dict:
    """Generate trading signals for specified markets"""
    if not HAS_SIGNALS:
        print("   ⚠️ Signal generator not available")
        return {}

    if markets is None:
        markets = ["US", "DE", "IN"]

    try:
        gen = GlobalSignalGenerator()
        signals = gen.generate_signals(markets=markets)

        for market, sigs in signals.items():
            strong = len([s for s in sigs if s.get('signal_status') == 'STRONG BUY'])
            buy = len([s for s in sigs if s.get('signal_status') == 'BUY'])
            flag = {"US": "🇺🇸", "DE": "🇩🇪", "IN": "🇮🇳"}.get(market, "🌐")
            print(f"\n   {flag} {market}: {strong} STRONG BUY, {buy} BUY")

        return signals
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return {}


def run_combined_analysis(signals: Dict, position_mult: float = 1.0, max_picks: int = 5) -> List:
    """Run combined technical + fundamental analysis on top signals"""
    if not HAS_COMBINED:
        print("   ⚠️ Combined analyzer not available")
        return []

    if not signals:
        print("   No signals to analyze")
        return []

    try:
        ca = CombinedAnalyzer()
        all_opportunities = []

        for market, sigs in signals.items():
            actionable = [s for s in sigs if s.get('signal_status') in ['STRONG BUY', 'BUY']]
            actionable = sorted(actionable, key=lambda x: x.get('signal_score', 0), reverse=True)[:8]

            for sig in actionable:
                symbol = sig.get('symbol')
                try:
                    analysis = ca.analyze(symbol)
                    if analysis and analysis.trade_quality in ['A+', 'A', 'B']:
                        all_opportunities.append({'symbol': symbol, 'market': market, 'analysis': analysis})
                except:
                    continue

        all_opportunities.sort(key=lambda x: x['analysis'].combined_score, reverse=True)

        if all_opportunities:
            print(f"\n   🏆 TOP {min(max_picks, len(all_opportunities))} OPPORTUNITIES:\n")
            print(f"   {'#':<3} {'Symbol':<8} {'Mkt':<4} {'Quality':<8} {'Combined':<10} {'Tech':<6} {'Fund':<6} {'Signal':<25}")
            print(f"   {'─' * 90}")

            for i, opp in enumerate(all_opportunities[:max_picks], 1):
                a = opp['analysis']
                m = opp['market']
                q_emoji = {"A+": "🟢", "A": "🟢", "B": "🟡", "C": "🟠", "D": "🔴"}.get(a.trade_quality, "⚪")
                print(f"   {i:<3} {a.symbol:<8} {m:<4} {q_emoji} {a.trade_quality:<6} {a.combined_score:<10} {a.technical_score:<6} {a.fundamental_score:<6} {a.combined_signal[:25]:<25}")

            # Show #1 pick details
            best = all_opportunities[0]
            a = best['analysis']

            print(f"\n   {'─' * 70}")
            print(f"\n   📈 #1 PICK: {a.symbol} ({best['market']})")
            print(f"   Quality: {a.trade_quality}  │  Combined Score: {a.combined_score}/100")
            print(f"   Entry: ${a.entry_price:.2f}  │  Stop: ${a.stop_loss:.2f}  │  Target: ${a.target_1:.2f}")
            print(f"   P/E: {a.pe_ratio:.1f}  │  ROE: {a.roe:.1f}%  │  D/E: {a.debt_to_equity:.0f}")
            print(f"   {a.recommendation}")

            pos = calculate_position_size(a.entry_price, a.stop_loss, position_mult)
            if pos['shares'] > 0:
                print(f"\n   💼 Suggested: Buy {pos['shares']} shares = ${pos['value']:,.2f} (Risk: ${pos['risk']:.2f})")
        else:
            print("   No quality opportunities found (A+, A, or B grade)")

        return all_opportunities
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return []


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN ROUTINES
# ═══════════════════════════════════════════════════════════════════════════════

def morning_routine():
    """Complete morning routine at 08:00 German time"""
    print_header("MORNING ROUTINE", "☀️")

    print_section("MARKET REGIME CHECK", 1)
    position_mult, can_trade = print_regime_report()

    print_section("MONTHLY PROGRESS", 2)
    check_monthly_progress()

    print_section("OPEN POSITIONS", 3)
    check_open_positions(detailed=True)

    print_section("EARNINGS CALENDAR", 4)
    check_earnings(WATCHLIST_US, days_ahead=14)

    print_section("INSIDER ACTIVITY", 5)
    check_insider_activity(WATCHLIST_US[:15])

    print_section("MARKET STATUS", 6)
    try:
        status = get_market_status()
        for code, stat in status.items():
            flag = {"US": "🇺🇸", "DE": "🇩🇪", "IN": "🇮🇳"}.get(code, "🌐")
            print(f"   {flag} {MARKETS[code].name}: {stat}")
    except Exception as e:
        print(f"   Error: {e}")

    print_section("SIGNAL GENERATION (India + Germany)", 7)
    if not can_trade:
        print("\n   ⚠️  Skipping - unfavorable market regime")
        all_signals = {}
    else:
        all_signals = generate_signals(markets=["IN", "DE"], position_mult=position_mult)

    if all_signals and can_trade:
        print_section("COMBINED ANALYSIS", 8)
        run_combined_analysis(all_signals, position_mult, max_picks=5)

    if HAS_ALERTS and all_signals:
        try:
            alerts = AlertSystem()
            for market, market_signals in all_signals.items():
                if market_signals:
                    alerts.send_signal(market_signals[0])
        except:
            pass

    max_trades = 2 if position_mult >= 0.75 else 1
    print(f"""
╔═══════════════════════════════════════════════════════════════════════════════════════════╗
║                              📋 MORNING ACTION ITEMS                                      ║
╠═══════════════════════════════════════════════════════════════════════════════════════════╣
║  □ Review open positions - update stops if needed                                         ║
║  □ Check earnings dates for positions                                                     ║
║  □ Note any insider selling in holdings                                                   ║
║  □ German market opens at 09:00 - be ready                                                ║
║  📊 Position Sizing: {position_mult*100:>3.0f}%  │  Max {max_trades} new trade(s) today                              ║
╚═══════════════════════════════════════════════════════════════════════════════════════════╝
    """)
    return all_signals


def midday_routine():
    """Midday check at 12:00 German time"""
    print_header("MIDDAY ROUTINE", "🌞")

    print_section("MARKET STATUS", 1)
    try:
        status = get_market_status()
        for code, stat in status.items():
            flag = {"US": "🇺🇸", "DE": "🇩🇪", "IN": "🇮🇳"}.get(code, "🌐")
            print(f"   {flag} {MARKETS[code].name}: {stat}")
    except:
        pass

    position_mult, can_trade, regime_desc = check_market_regime()
    print(f"\n   Market Regime: {regime_desc}")

    print_section("POSITION CHECK", 2)
    check_open_positions(detailed=False)

    print_section("FUNDAMENTAL HEALTH CHECK", 3)
    if HAS_FUNDAMENTALS and HAS_JOURNAL:
        try:
            fa = FundamentalAnalyzer()
            journal = TradeJournal()
            open_trades = journal.get_open_trades()

            if not open_trades.empty:
                for symbol in open_trades['symbol'].unique():
                    data = fa.analyze(symbol)
                    if data:
                        score = data.overall_score
                        emoji = "✅" if score >= 60 else "⚠️" if score >= 40 else "🔴"
                        status = "Healthy" if score >= 60 else "Monitor" if score >= 40 else "Concern"
                        print(f"   {emoji} {symbol:8} Fundamental Score: {score}/100 - {status}")
            else:
                print("   No open positions to check")
        except Exception as e:
            print(f"   Error: {e}")
    else:
        print("   ⚠️ Fundamental analyzer or trade journal not available")

    print(f"""
╔═══════════════════════════════════════════════════════════════════════════════════════════╗
║                              💡 MIDDAY ACTIONS                                            ║
╠═══════════════════════════════════════════════════════════════════════════════════════════╣
║  □ Review morning German trades                                                           ║
║  □ Indian market closes at 13:00 - manage positions                                       ║
║  □ Move stops to breakeven on 1R+ winners                                                 ║
║  □ US market opens at 15:30 - prepare watchlist                                           ║
╚═══════════════════════════════════════════════════════════════════════════════════════════╝
    """)


def afternoon_routine():
    """Afternoon routine at 15:30 German time (US Market Open)"""
    print_header("AFTERNOON ROUTINE - US MARKET OPEN", "🌆")

    print_section("US SESSION REGIME CHECK", 1)
    position_mult, can_trade = print_regime_report()

    print_section("US MARKET SIGNALS", 2)
    if not can_trade:
        print("\n   ⚠️  Unfavorable regime - be very selective")
    all_signals = generate_signals(markets=["US"], position_mult=position_mult)

    print_section("TOP US OPPORTUNITIES", 3)
    run_combined_analysis(all_signals, position_mult, max_picks=5)

    print_section("US EARNINGS WARNING", 4)
    if HAS_EARNINGS:
        try:
            ec = EarningsCalendar()
            upcoming = ec.scan_upcoming_earnings(WATCHLIST_US, days_ahead=7)
            if not upcoming.empty:
                print("\n   ⚠️  EARNINGS THIS WEEK:\n")
                for _, row in upcoming.iterrows():
                    print(f"   {row['Symbol']:8} - {row['Earnings Date']} ({row['Days Until']} days)")
            else:
                print("   ✅ No earnings in next 7 days for US watchlist")
        except Exception as e:
            print(f"   Error: {e}")

    print_section("US INSIDER ACTIVITY", 5)
    check_insider_activity(WATCHLIST_US[:10])

    if HAS_ALERTS and all_signals:
        try:
            alerts = AlertSystem()
            for market, market_signals in all_signals.items():
                if market_signals:
                    alerts.send_signal(market_signals[0])
        except:
            pass

    print(f"""
╔═══════════════════════════════════════════════════════════════════════════════════════════╗
║                              💡 AFTERNOON ACTIONS                                         ║
╠═══════════════════════════════════════════════════════════════════════════════════════════╣
║  □ Review top US opportunities                                                            ║
║  □ Avoid stocks with earnings this week                                                   ║
║  □ Check insider activity before new positions                                            ║
║  □ German market closes at 17:30                                                          ║
║  📊 Position Sizing: {position_mult*100:>3.0f}%                                                                     ║
╚═══════════════════════════════════════════════════════════════════════════════════════════╝
    """)
    return all_signals


def evening_routine():
    """Evening routine at 20:00 German time"""
    print_header("EVENING ROUTINE", "🌙")

    print_section("PERFORMANCE REPORT (Last 30 Days)", 1)
    if HAS_JOURNAL:
        try:
            journal = TradeJournal()
            journal.print_report(days=30)
        except Exception as e:
            print(f"   Error: {e}")
    else:
        print("   ⚠️ Trade journal not available")

    print_section("MONTHLY PROGRESS", 2)
    check_monthly_progress()

    print_section("OPEN POSITIONS - FULL ANALYSIS", 3)
    check_open_positions(detailed=True)

    print_section("MARKET STATUS", 4)
    try:
        status = get_market_status()
        for code, stat in status.items():
            flag = {"US": "🇺🇸", "DE": "🇩🇪", "IN": "🇮🇳"}.get(code, "🌐")
            print(f"   {flag} {MARKETS[code].name}: {stat}")
    except:
        pass

    position_mult, can_trade, regime_desc = check_market_regime()
    print(f"\n   Market Regime: {regime_desc}")

    print_section("TOMORROW'S WATCHLIST PREP", 5)
    if HAS_COMBINED and HAS_SIGNALS:
        try:
            print("\n   Running quick scan for tomorrow...")
            gen = GlobalSignalGenerator()
            signals = gen.generate_signals(markets=["US"])

            ca = CombinedAnalyzer()
            tomorrow_watch = []

            for sig in signals.get("US", [])[:15]:
                if sig.get('signal_status') in ['STRONG BUY', 'BUY']:
                    try:
                        analysis = ca.analyze(sig['symbol'])
                        if analysis and analysis.trade_quality in ['A+', 'A']:
                            tomorrow_watch.append({
                                'symbol': analysis.symbol,
                                'quality': analysis.trade_quality,
                                'score': analysis.combined_score,
                                'setup': analysis.setup_type,
                                'entry': analysis.entry_price,
                            })
                    except:
                        continue

            if tomorrow_watch:
                tomorrow_watch.sort(key=lambda x: x['score'], reverse=True)
                print(f"\n   🎯 TOMORROW'S WATCHLIST (Quality A+ and A):\n")
                for w in tomorrow_watch[:5]:
                    emoji = "🟢" if w['quality'] == 'A+' else "🟡"
                    print(f"   {emoji} {w['quality']} {w['symbol']:8} Score: {w['score']:<3} Entry: ${w['entry']:.2f} Setup: {w['setup']}")
            else:
                print("   No A-grade setups found for tomorrow")
        except Exception as e:
            print(f"   Error: {e}")
    else:
        print("   ⚠️ Combined analyzer or signal generator not available")

    if HAS_ALERTS and HAS_SIGNALS:
        try:
            gen = GlobalSignalGenerator()
            signals = gen.generate_signals(markets=["US", "DE", "IN"])
            alerts = AlertSystem()
            alerts.send_daily_summary(signals)
        except:
            pass

    print(f"""
╔═══════════════════════════════════════════════════════════════════════════════════════════╗
║                              📋 END OF DAY CHECKLIST                                      ║
╠═══════════════════════════════════════════════════════════════════════════════════════════╣
║  □ Log all trades: python trade_journal.py                                                ║
║  □ Review positions - stops hit? targets reached?                                         ║
║  □ Check fundamental health of holdings                                                   ║
║  □ Note lessons learned today                                                             ║
║  □ Update watchlist for tomorrow                                                          ║
║  □ US market closes at 22:00 German time                                                  ║
╚═══════════════════════════════════════════════════════════════════════════════════════════╝
    """)


# ═══════════════════════════════════════════════════════════════════════════════
# ADDITIONAL SCANS
# ═══════════════════════════════════════════════════════════════════════════════

def full_scan():
    """Full market scan with combined analysis"""
    print_header("FULL MARKET SCAN", "🔍")

    print_section("MARKET REGIME", 1)
    position_mult, can_trade = print_regime_report()

    print_section("GENERATING SIGNALS (All Markets)", 2)
    all_signals = generate_signals(markets=["US", "DE", "IN"], position_mult=position_mult)

    print_section("COMBINED ANALYSIS (Top Global Picks)", 3)
    run_combined_analysis(all_signals, position_mult, max_picks=10)

    print_section("EARNINGS CALENDAR", 4)
    check_earnings(WATCHLIST_US, days_ahead=14)

    print_section("INSIDER ACTIVITY", 5)
    check_insider_activity(WATCHLIST_US[:15])

    return all_signals


def fundamental_scan(symbols: List[str] = None, preset: str = None):
    """Pure fundamental analysis scan"""
    print_header("FUNDAMENTAL ANALYSIS SCAN", "📊")

    if not HAS_FUNDAMENTALS:
        print("   ⚠️ fundamental_analyzer.py not available")
        return

    if symbols is None:
        symbols = WATCHLIST_US

    fa = FundamentalAnalyzer()

    print_section("QUICK FUNDAMENTAL SCAN", 1)
    print(f"\n   Analyzing {len(symbols)} stocks...\n")

    df = fa.quick_scan(symbols)

    if not df.empty:
        print(df.to_string(index=False))
        top = df.head(3)
        print(f"\n   🏆 TOP 3 BY FUNDAMENTAL SCORE:")
        for _, row in top.iterrows():
            print(f"      {row['Symbol']:8} - Overall: {row['Overall']}/100, Quality: {row['Quality']}/100")
    else:
        print("   Could not analyze stocks")

    if HAS_SCREENER and preset:
        print_section(f"SCREENER: {preset.upper()}", 2)
        try:
            screener = FundamentalScreener()
            preset_enum = {
                'value': ScreenerPreset.VALUE, 'growth': ScreenerPreset.GROWTH,
                'quality': ScreenerPreset.QUALITY, 'dividend': ScreenerPreset.DIVIDEND,
                'garp': ScreenerPreset.GARP, 'buffett': ScreenerPreset.BUFFETT,
                'lynch': ScreenerPreset.LYNCH,
            }.get(preset.lower())

            if preset_enum:
                df, _ = screener.screen_with_preset(symbols, preset_enum)
                screener.print_results(df, f"{preset.upper()} SCREEN")
            else:
                print(f"   Unknown preset: {preset}")
        except Exception as e:
            print(f"   Error: {e}")


def insider_scan(symbols: List[str] = None):
    """Scan for insider buying activity"""
    print_header("INSIDER ACTIVITY SCAN", "👔")

    if not HAS_INSIDER:
        print("   ⚠️ insider_tracker.py not available")
        return

    if symbols is None:
        symbols = WATCHLIST_US

    tracker = InsiderTracker()
    print(f"\n   Scanning {len(symbols)} stocks for insider activity...\n")

    df = tracker.scan_for_insider_buying(symbols, min_buys=1, min_buy_value=50000, days=90)
    tracker.print_scan_results(df)

    print_section("NOTABLE RECENT PURCHASES (Last 30 Days)", 2)
    notable = tracker.get_recent_notable_buys(symbols, min_value=100000, days=30)

    if notable:
        print(f"\n   Found {len(notable)} notable purchases:\n")
        print(f"   {'Symbol':<8} {'Insider':<30} {'Date':<12} {'Value':>15}")
        print(f"   {'─' * 70}")
        for t in notable[:15]:
            print(f"   {t['symbol']:<8} {t['insider'][:30]:<30} {t['date']:<12} ${t['value']:>14,.0f}")
    else:
        print("   No notable purchases found")


def earnings_scan(symbols: List[str] = None, days: int = 21):
    """Earnings calendar scan"""
    print_header("EARNINGS CALENDAR", "📅")

    if not HAS_EARNINGS:
        print("   ⚠️ earnings_calendar.py not available")
        return

    if symbols is None:
        symbols = WATCHLIST_US

    ec = EarningsCalendar()
    ec.print_calendar(symbols, days_ahead=days)


# ═══════════════════════════════════════════════════════════════════════════════
# SCHEDULE & SYSTEM STATUS
# ═══════════════════════════════════════════════════════════════════════════════

def show_schedule():
    """Show recommended daily schedule and system status"""
    print(f"""
╔═══════════════════════════════════════════════════════════════════════════════════════════╗
║                     📅 ENHANCED DAILY SCHEDULE (German Time)                              ║
╠═══════════════════════════════════════════════════════════════════════════════════════════╣
║                                                                                           ║
║  08:00  │  ☀️  python daily_workflow.py morning                                           ║
║         │  Market regime, Progress, Positions, Earnings, Insider, Signals                 ║
║                                                                                           ║
║  09:00  │  🇩🇪  GERMAN MARKET OPENS - Place orders, Set stops                              ║
║                                                                                           ║
║  12:00  │  🌞  python daily_workflow.py midday                                            ║
║         │  Position P&L, Fundamental health check                                         ║
║                                                                                           ║
║  15:30  │  🇺🇸  python daily_workflow.py afternoon                                        ║
║         │  US regime, US signals, Combined analysis, Earnings warning                     ║
║                                                                                           ║
║  17:30  │  🇩🇪  GERMAN MARKET CLOSES                                                       ║
║                                                                                           ║
║  20:00  │  🌙  python daily_workflow.py evening                                           ║
║         │  Performance report, Full analysis, Tomorrow's watchlist                        ║
║                                                                                           ║
║  22:00  │  🇺🇸  US MARKET CLOSES                                                           ║
║                                                                                           ║
╠═══════════════════════════════════════════════════════════════════════════════════════════╣
║                              ADDITIONAL COMMANDS                                          ║
╠═══════════════════════════════════════════════════════════════════════════════════════════╣
║  python daily_workflow.py scan                    # Full scan all markets                 ║
║  python daily_workflow.py fundamentals            # Fundamental analysis                  ║
║  python daily_workflow.py fundamentals --preset value   # Value screen                    ║
║  python daily_workflow.py insider                 # Insider activity scan                 ║
║  python daily_workflow.py earnings                # Earnings calendar                     ║
╚═══════════════════════════════════════════════════════════════════════════════════════════╝

╔═══════════════════════════════════════════════════════════════════════════════════════════╗
║                              ⚙️  SYSTEM STATUS                                             ║
╠═══════════════════════════════════════════════════════════════════════════════════════════╣
║  CORE:           {'✅' if HAS_SIGNALS else '❌'} Signals  {'✅' if HAS_ANALYZER else '❌'} Analyzer  {'✅' if HAS_REGIME else '❌'} Regime  {'✅' if HAS_JOURNAL else '❌'} Journal       ║
║  FUNDAMENTAL:    {'✅' if HAS_FUNDAMENTALS else '❌'} Analyzer  {'✅' if HAS_COMBINED else '❌'} Combined  {'✅' if HAS_SCREENER else '❌'} Screener                       ║
║  EARNINGS/INSIDER: {'✅' if HAS_EARNINGS else '❌'} Earnings  {'✅' if HAS_INSIDER else '❌'} Insider                                        ║
║  DATA:           {'✅' if HAS_YFINANCE else '❌'} yfinance  {'✅' if HAS_PANDAS else '❌'} pandas  {'✅' if HAS_PYTZ else '❌'} pytz  {'✅' if HAS_TRACKER else '❌'} Tracker         ║
╚═══════════════════════════════════════════════════════════════════════════════════════════╝
    """)


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN FUNCTION
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Enhanced Daily Workflow with Fundamental Analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python daily_workflow.py morning              # Morning routine
  python daily_workflow.py midday               # Midday check
  python daily_workflow.py afternoon            # US market open
  python daily_workflow.py evening              # End of day
  python daily_workflow.py scan                 # Full scan
  python daily_workflow.py fundamentals         # Fundamental analysis
  python daily_workflow.py fundamentals --preset value    # Value screen
  python daily_workflow.py insider              # Insider scan
  python daily_workflow.py earnings             # Earnings calendar
  python daily_workflow.py schedule             # Show schedule
        """
    )

    parser.add_argument(
        "routine",
        nargs="?",
        default="schedule",
        choices=["morning", "midday", "afternoon", "evening", "scan",
                 "fundamentals", "insider", "earnings", "schedule"],
        help="Which routine to run"
    )

    parser.add_argument(
        "--symbols",
        nargs="+",
        help="Symbols for analysis (optional)"
    )

    parser.add_argument(
        "--preset",
        choices=["value", "growth", "quality", "dividend", "garp", "buffett", "lynch"],
        help="Screening preset for fundamentals"
    )

    parser.add_argument(
        "--days",
        type=int,
        default=21,
        help="Days ahead for earnings scan"
    )

    args = parser.parse_args()

    # Execute the selected routine
    if args.routine == "morning":
        morning_routine()
    elif args.routine == "midday":
        midday_routine()
    elif args.routine == "afternoon":
        afternoon_routine()
    elif args.routine == "evening":
        evening_routine()
    elif args.routine == "scan":
        full_scan()
    elif args.routine == "fundamentals":
        fundamental_scan(args.symbols, args.preset)
    elif args.routine == "insider":
        insider_scan(args.symbols)
    elif args.routine == "earnings":
        earnings_scan(args.symbols, args.days)
    elif args.routine == "schedule":
        show_schedule()


if __name__ == "__main__":
    main()
