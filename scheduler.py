#!/usr/bin/env python3
"""
Scheduler - Automatic daily updates
"""

import schedule
import time
from datetime import datetime
import subprocess
import sys

def update_universe():
    """Run universe update"""
    print(f"\n[{datetime.now()}] Running universe update...")
    subprocess.run([sys.executable, "main.py", "quick-update"])

def generate_signals():
    """Generate morning signals"""
    print(f"\n[{datetime.now()}] Generating signals...")
    subprocess.run([sys.executable, "main.py", "signals"])

def main():
    print("=" * 60)
    print("TRADING SYSTEM SCHEDULER")
    print("=" * 60)
    print("Scheduled tasks:")
    print("  - Universe update: Sunday 6:00 PM")
    print("  - Morning signals: Mon-Fri 8:30 AM")
    print("\nPress Ctrl+C to stop\n")

    # Schedule tasks
    schedule.every().sunday.at("18:00").do(update_universe)
    schedule.every().monday.at("08:30").do(generate_signals)
    schedule.every().tuesday.at("08:30").do(generate_signals)
    schedule.every().wednesday.at("08:30").do(generate_signals)
    schedule.every().thursday.at("08:30").do(generate_signals)
    schedule.every().friday.at("08:30").do(generate_signals)

    # Run loop
    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nScheduler stopped")
