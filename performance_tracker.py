#!/usr/bin/env python3
"""
Performance Tracker - Monitor Progress Toward 3% Monthly
"""

from datetime import datetime
from typing import Dict

try:
    from trade_journal import TradeJournal
except ImportError:
    TradeJournal = None

try:
    import config
    ACCOUNT_SIZE = getattr(config, 'ACCOUNT_SIZE', 50000)
    MONTHLY_TARGET = getattr(config, 'MONTHLY_TARGET', 0.03)
except ImportError:
    ACCOUNT_SIZE = 50000
    MONTHLY_TARGET = 0.03


class PerformanceTracker:
    """Track progress toward monthly goals"""

    def __init__(self):
        self.account = ACCOUNT_SIZE
        self.target_pct = MONTHLY_TARGET
        self.target_amount = self.account * self.target_pct
        self.journal = TradeJournal() if TradeJournal else None

    def get_monthly_progress(self) -> Dict:
        """Get current month progress"""

        if not self.journal:
            return {"error": "Trade journal not available"}

        today = datetime.now()
        days_in_month = 30  # Approximate
        days_elapsed = today.day
        days_left = max(0, days_in_month - days_elapsed)
        trading_days_left = int(days_left * 5 / 7)

        stats = self.journal.get_stats(days=days_elapsed)

        current_pnl = stats.get('total_pnl', 0)
        progress_pct = (current_pnl / self.target_amount * 100) if self.target_amount else 0
        remaining = self.target_amount - current_pnl

        expected_pnl = self.target_amount * (days_elapsed / days_in_month)
        on_track = current_pnl >= expected_pnl * 0.8

        return {
            "month": today.strftime("%B %Y"),
            "target": self.target_amount,
            "target_pct": self.target_pct * 100,
            "current_pnl": current_pnl,
            "progress_pct": round(progress_pct, 1),
            "remaining": round(remaining, 2),
            "days_elapsed": days_elapsed,
            "days_left": days_left,
            "trading_days_left": trading_days_left,
            "on_track": on_track,
            "trades": stats.get('total_trades', 0),
            "win_rate": stats.get('win_rate', 0),
            "avg_r": stats.get('avg_r', 0)
        }

    def print_dashboard(self):
        """Print progress dashboard"""
        p = self.get_monthly_progress()

        if p.get('error'):
            print(f"❌ {p['error']}")
            return

        bar_width = 30
        filled = int(bar_width * min(p['progress_pct'], 100) / 100)
        bar = "█" * filled + "░" * (bar_width - filled)

        status = "🎯 ON TRACK" if p['on_track'] else "⚠️ BEHIND"
        if p['progress_pct'] >= 100:
            status = "✅ TARGET HIT!"

        print(f"""
╔═══════════════════════════════════════════════════════════════════════╗
║                📊 MONTHLY PROGRESS - {p['month']}
╠═══════════════════════════════════════════════════════════════════════╣
║                                                                       ║
║  Target: ${p['target']:,.0f} ({p['target_pct']:.0f}%)        Status: {status:^15}
║                                                                       ║
║  [{bar}] {p['progress_pct']:>5.1f}%
║                                                                       ║
║  Current P&L:  ${p['current_pnl']:>+12,.2f}
║  Remaining:    ${p['remaining']:>+12,.2f}
║                                                                       ║
║  Days Elapsed: {p['days_elapsed']:>3}      Trading Days Left: {p['trading_days_left']:>3}
║  Trades:       {p['trades']:>3}      Win Rate: {p['win_rate']:>5.1f}%
║                                                                       ║
╠═══════════════════════════════════════════════════════════════════════╣""")

        if p['remaining'] > 0 and p['trading_days_left'] > 0:
            per_day = p['remaining'] / p['trading_days_left']
            print(f"║  💡 Need ${per_day:,.0f}/day to hit target                                ║")
        elif p['remaining'] <= 0:
            print(f"║  🎉 TARGET ACHIEVED! Surplus: ${-p['remaining']:,.2f}                      ║")

        print("╚═══════════════════════════════════════════════════════════════════════╝")


if __name__ == "__main__":
    PerformanceTracker().print_dashboard()
