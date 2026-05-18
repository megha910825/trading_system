#!/usr/bin/env python3
"""
Daily Workflow Script - Optimized for Germany
Run this script at specific times throughout the day
"""

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
    - Check market status
    - Generate signals for India (already open) and Germany (about to open)
    """
    now = get_german_time()
    print(f"\n☀️ MORNING ROUTINE - {now.strftime('%Y-%m-%d %H:%M')} (German Time)")
    print("=" * 60)

    # Market status
    print("\n📊 Market Status:")
    status = get_market_status()
    for code, stat in status.items():
        print(f"  {MARKETS[code].name}: {stat}")

    # Generate signals for morning markets
    print("\n" + "=" * 60)
    print("GENERATING MORNING SIGNALS")
    print("=" * 60)

    gen = GlobalSignalGenerator()

    # India is already open, Germany opening soon
    signals = gen.generate_signals(markets=["IN", "DE"])
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
    - Review all positions
    - Generate summary
    """
    now = get_german_time()
    print(f"\n🌙 EVENING ROUTINE - {now.strftime('%Y-%m-%d %H:%M')} (German Time)")
    print("=" * 60)

    # Market status
    print("\n📊 Market Status:")
    status = get_market_status()
    for code, stat in status.items():
        print(f"  {MARKETS[code].name}: {stat}")

    # Daily summary
    print("\n" + "=" * 60)
    print("DAILY SUMMARY")
    print("=" * 60)

    gen = GlobalSignalGenerator()
    signals = gen.generate_signals(markets=["US", "DE", "IN"])

    # Send summary
    alerts = AlertSystem()
    alerts.send_daily_summary(signals)

    print("\n💡 End of Day Actions:")
    print("  - Log any trades in journal: python trade_journal.py")
    print("  - Review open positions")
    print("  - Plan tomorrow's watchlist")


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
