#!/usr/bin/env python3
"""
Daily Workflow Script - Optimized for Germany
Run this script at specific times throughout the day
"""
# Add these imports at the top of daily_workflow.py
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

import argparse
from datetime import datetime
import pytz

from global_signal_generator import GlobalSignalGenerator
from global_universe_manager import GlobalUniverseManager
from alert_system import AlertSystem
from market_config import MARKETS, get_market_status

# Germany timezone
BERLIN = pytz.timezone("Europe/Berlin")


def get_german_time():
    """Get current time in Germany"""
    return datetime.now(BERLIN)


def morning_routine():
    """
    Run at 8:00 AM German time
    """
    now = get_german_time()
    print(f"\n☀️ MORNING ROUTINE - {now.strftime('%Y-%m-%d %H:%M')} (German Time)")
    print("=" * 60)

    # 1. Market Regime Check
    print("\n1️⃣ MARKET REGIME CHECK")
    if HAS_REGIME:
        mrf = MarketRegimeFilter()
        mrf.print_report()
        conditions = mrf.analyze()

        if not conditions.can_trade_long:
            print("⚠️ WARNING: Market conditions unfavorable for longs!")
    else:
        print("   Market regime filter not available")

    # 2. Monthly Progress
    print("\n2️⃣ MONTHLY PROGRESS")
    if HAS_TRACKER:
        tracker = PerformanceTracker()
        tracker.print_dashboard()
    else:
        print("   Performance tracker not available")

    # 3. Open Positions
    print("\n3️⃣ OPEN POSITIONS")
    if HAS_JOURNAL:
        journal = TradeJournal()
        open_trades = journal.get_open_trades()
        if not open_trades.empty:
            print(f"   {len(open_trades)} open positions:")
            for _, t in open_trades.iterrows():
                print(f"      {t['symbol']:8} Entry: ${t['entry_price']:.2f} "
                      f"Stop: ${t['stop_loss']:.2f}")
        else:
            print("   No open positions")

    # 4. Market status
    print("\n4️⃣ MARKET STATUS")
    status = get_market_status()
    for code, stat in status.items():
        print(f"   {MARKETS[code].name}: {stat}")

    # 5. Generate signals
    print("\n5️⃣ GENERATING SIGNALS")
    gen = GlobalSignalGenerator()
    signals = gen.generate_signals(markets=["IN", "DE"])

    # Count signals
    for market, sigs in signals.items():
        strong = len([s for s in sigs if s.get('signal_status') == 'STRONG BUY'])
        buy = len([s for s in sigs if s.get('signal_status') == 'BUY'])
        print(f"   {market}: {strong} STRONG BUY, {buy} BUY")

    gen.print_all_signals()

    # Send alerts
    alerts = AlertSystem()
    for market, market_signals in signals.items():
        if market_signals:
            alerts.send_signal(market_signals[0])

    return signals



def midday_routine():
    """
    Run at 12:00 PM German time
    - Review German positions
    - Prepare for US market open
    """
    now = get_german_time()
    print(f"\n🌞 MIDDAY ROUTINE - {now.strftime('%Y-%m-%d %H:%M')} (German Time)")
    print("=" * 60)

    # Market status
    print("\n📊 Market Status:")
    status = get_market_status()
    for code, stat in status.items():
        print(f"  {MARKETS[code].name}: {stat}")

    print("\n💡 Actions:")
    print("  - Review morning trades")
    print("  - Check German positions")
    print("  - Indian market closing soon - review exits")
    print("  - US market opens at 15:30 German time")


def afternoon_routine():
    """
    Run at 15:30 PM German time
    - US market just opened
    - Generate US signals
    """
    now = get_german_time()
    print(f"\n🌆 AFTERNOON ROUTINE - {now.strftime('%Y-%m-%d %H:%M')} (German Time)")
    print("=" * 60)

    # Market status
    print("\n📊 Market Status:")
    status = get_market_status()
    for code, stat in status.items():
        print(f"  {MARKETS[code].name}: {stat}")

    # Generate US signals
    print("\n" + "=" * 60)
    print("GENERATING US SIGNALS")
    print("=" * 60)

    gen = GlobalSignalGenerator()
    signals = gen.generate_signals(markets=["US"])
    gen.print_all_signals()

    # Send alerts
    alerts = AlertSystem()
    for market, market_signals in signals.items():
        if market_signals:
            alerts.send_signal(market_signals[0])

    return signals


def evening_routine():
    """
    Run at 20:00 PM German time
    """
    now = get_german_time()
    print(f"\n🌙 EVENING ROUTINE - {now.strftime('%Y-%m-%d %H:%M')} (German Time)")
    print("=" * 60)

    # 1. Performance Report
    print("\n1️⃣ PERFORMANCE REPORT")
    if HAS_JOURNAL:
        journal = TradeJournal()
        journal.print_report(days=30)

    # 2. Monthly Progress
    print("\n2️⃣ MONTHLY PROGRESS")
    if HAS_TRACKER:
        tracker = PerformanceTracker()
        tracker.print_dashboard()

    # 3. Open Positions
    print("\n3️⃣ OPEN POSITIONS")
    if HAS_JOURNAL:
        open_trades = journal.get_open_trades()
        if not open_trades.empty:
            print(open_trades.to_string(index=False))
        else:
            print("   No open positions")

    # 4. Market status
    print("\n4️⃣ MARKET STATUS")
    status = get_market_status()
    for code, stat in status.items():
        print(f"   {MARKETS[code].name}: {stat}")

    # 5. Daily summary
    gen = GlobalSignalGenerator()
    signals = gen.generate_signals(markets=["US", "DE", "IN"])

    alerts = AlertSystem()
    alerts.send_daily_summary(signals)

    print("""
╔═══════════════════════════════════════════════════════════════════════╗
║                     📋 END OF DAY CHECKLIST
╠═══════════════════════════════════════════════════════════════════════╣
║                                                                       ║
║  □ Log all trades:  python trade_journal.py                          ║
║  □ Review open positions - update stops if needed                    ║
║  □ Check if any stops were hit                                       ║
║  □ Note lessons learned                                              ║
║  □ Plan tomorrow's watchlist                                         ║
║                                                                       ║
╚═══════════════════════════════════════════════════════════════════════╝
    """)



def full_scan():
    """
    Run full scan of all markets
    """
    now = get_german_time()
    print(f"\n🔍 FULL MARKET SCAN - {now.strftime('%Y-%m-%d %H:%M')} (German Time)")
    print("=" * 60)

    gen = GlobalSignalGenerator()
    signals = gen.generate_signals(markets=["US", "DE", "IN"])
    gen.print_all_signals()

    return signals


def show_schedule():
    """
    Show recommended daily schedule
    """
    print("""
╔══════════════════════════════════════════════════════════════════╗
║          📅 RECOMMENDED DAILY SCHEDULE (German Time)             ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  08:00  │  ☀️ MORNING ROUTINE                                    ║
║         │  python daily_workflow.py morning                      ║
║         │  - Check India signals (market open)                   ║
║         │  - Prepare for German market open (09:00)              ║
║         │                                                        ║
║  09:00  │  🇩🇪 GERMAN MARKET OPENS                                ║
║         │  - Place German orders                                 ║
║         │  - Set stop losses                                     ║
║         │                                                        ║
║  11:00  │  🇮🇳 INDIA MARKET CLOSES                                ║
║         │  - Review Indian positions                             ║
║         │                                                        ║
║  12:00  │  🌞 MIDDAY CHECK                                        ║
║         │  python daily_workflow.py midday                       ║
║         │  - Review German positions                             ║
║         │                                                        ║
║  15:30  │  🇺🇸 US MARKET OPENS                                    ║
║         │  python daily_workflow.py afternoon                    ║
║         │  - Generate US signals                                 ║
║         │  - Place US orders                                     ║
║         │                                                        ║
║  17:30  │  🇩🇪 GERMAN MARKET CLOSES                               ║
║         │  - Review German positions                             ║
║         │                                                        ║
║  20:00  │  🌙 EVENING ROUTINE                                     ║
║         │  python daily_workflow.py evening                      ║
║         │  - Daily summary                                       ║
║         │  - Log trades                                          ║
║         │                                                        ║
║  22:00  │  🇺🇸 US MARKET CLOSES                                   ║
║         │  - Final review                                        ║
║         │                                                        ║
╠══════════════════════════════════════════════════════════════════╣
║                     WEEKEND TASKS                                ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  SUNDAY EVENING:                                                 ║
║    python main.py quick-update    # Update stock universe        ║
║    python backtester.py compare   # Review strategy performance  ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
    """)


def main():
    parser = argparse.ArgumentParser(description="Daily Workflow for Germany")
    parser.add_argument("routine", nargs="?", default="schedule",
                       choices=["morning", "midday", "afternoon", "evening",
                               "scan", "schedule"],
                       help="Which routine to run")

    args = parser.parse_args()

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
    elif args.routine == "schedule":
        show_schedule()


if __name__ == "__main__":
    main()
