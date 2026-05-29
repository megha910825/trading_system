#!/usr/bin/env python3
"""
Scheduler - Automatic daily updates
"""

import sys as _sys, os as _os
_APP_ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
for _sub in ["core", "analysis", "signals", "screening", "portfolio",
             "strategies", "research", "automation"]:
    _p = _os.path.join(_APP_ROOT, _sub)
    if _p not in _sys.path:
        _sys.path.insert(0, _p)
if _APP_ROOT not in _sys.path:
    _sys.path.insert(0, _APP_ROOT)

import schedule
import time
from datetime import datetime
import subprocess
import sys
import os

# ── Log file ──────────────────────────────────────────────────────────────────
_LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
os.makedirs(_LOG_DIR, exist_ok=True)
_LOG_FILE = os.path.join(_LOG_DIR, "scheduler.log")

def _log(msg: str):
    line = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}"
    print(line)
    with open(_LOG_FILE, "a") as f:
        f.write(line + "\n")

def update_universe():
    _log("universe update started")
    try:
        result = subprocess.run([sys.executable, "main.py", "quick-update"],
                                capture_output=True, text=True, timeout=300)
        if result.returncode == 0:
            _log("universe update completed OK")
        else:
            _log(f"universe update ERROR: {result.stderr[:200]}")
    except Exception as e:
        _log(f"universe update ERROR: {e}")

def generate_signals():
    _log("signals job started")
    try:
        result = subprocess.run([sys.executable, "main.py", "signals"],
                                capture_output=True, text=True, timeout=300)
        if result.returncode == 0:
            _log("signals job completed OK")
        else:
            _log(f"signals job ERROR: {result.stderr[:200]}")
    except Exception as e:
        _log(f"signals job ERROR: {e}")


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
