#!/usr/bin/env python3
"""
Trade Journal - Track Every Trade
Essential for consistent 3%+ monthly returns
"""

import sqlite3
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import Dict, List
import json


class TradeJournal:
    """Complete trade tracking system"""

    def __init__(self, db_path: str = "data/trade_journal.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        """Initialize database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                market TEXT DEFAULT 'US',
                direction TEXT DEFAULT 'LONG',

                entry_date DATE NOT NULL,
                entry_price REAL NOT NULL,
                shares INTEGER NOT NULL,
                position_value REAL,

                stop_loss REAL NOT NULL,
                target_1 REAL,
                target_2 REAL,
                risk_amount REAL,
                planned_rr REAL,

                setup_type TEXT,
                signal_score INTEGER,
                entry_reason TEXT,
                market_regime TEXT,

                exit_date DATE,
                exit_price REAL,
                exit_reason TEXT,

                pnl REAL,
                pnl_pct REAL,
                r_multiple REAL,
                holding_days INTEGER,

                followed_plan INTEGER DEFAULT 1,
                mistakes TEXT,
                lessons TEXT,
                rating INTEGER DEFAULT 5,

                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS daily_notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE UNIQUE NOT NULL,
                market_regime TEXT,
                pre_market_plan TEXT,
                watchlist TEXT,
                trades_taken INTEGER DEFAULT 0,
                day_pnl REAL DEFAULT 0,
                post_market_review TEXT,
                lessons TEXT,
                followed_rules INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        conn.close()

    def log_entry(
        self, symbol: str, entry_price: float, shares: int,
        stop_loss: float, target_1: float, target_2: float = None,
        setup_type: str = "PULLBACK", signal_score: int = 0,
        entry_reason: str = "", market: str = "US",
        market_regime: str = "BULL"
    ) -> int:
        """Log a new trade entry"""

        position_value = entry_price * shares
        risk_per_share = abs(entry_price - stop_loss)
        risk_amount = risk_per_share * shares
        planned_rr = (target_1 - entry_price) / risk_per_share if risk_per_share else 0

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO trades (
                symbol, market, entry_date, entry_price, shares,
                position_value, stop_loss, target_1, target_2,
                risk_amount, planned_rr, setup_type, signal_score,
                entry_reason, market_regime
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            symbol.upper(), market, datetime.now().date(),
            entry_price, shares, position_value, stop_loss,
            target_1, target_2, risk_amount, planned_rr,
            setup_type, signal_score, entry_reason, market_regime
        ))

        trade_id = cursor.lastrowid
        conn.commit()
        conn.close()

        print(f"""
╔═══════════════════════════════════════════════════════════╗
║              ✅ TRADE LOGGED #{trade_id}
╠═══════════════════════════════════════════════════════════╣
║  {symbol}  |  {market}  |  {setup_type}
║  Entry: ${entry_price:,.2f} × {shares} shares = ${position_value:,.2f}
║  Stop:  ${stop_loss:,.2f}  |  Target: ${target_1:,.2f}
║  Risk:  ${risk_amount:,.2f}  |  R:R: {planned_rr:.1f}:1
╚═══════════════════════════════════════════════════════════╝""")

        return trade_id

    def log_exit(
        self, trade_id: int, exit_price: float, exit_reason: str,
        followed_plan: bool = True, mistakes: str = "", lessons: str = ""
    ) -> Dict:
        """Log trade exit"""

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT entry_date, entry_price, shares, stop_loss FROM trades WHERE id = ?",
            (trade_id,)
        )
        row = cursor.fetchone()

        if not row:
            conn.close()
            raise ValueError(f"Trade {trade_id} not found")

        entry_date, entry_price, shares, stop_loss = row

        pnl = (exit_price - entry_price) * shares
        pnl_pct = (exit_price / entry_price - 1) * 100
        risk_per_share = abs(entry_price - stop_loss)
        r_multiple = (exit_price - entry_price) / risk_per_share if risk_per_share else 0

        entry_dt = datetime.strptime(str(entry_date), "%Y-%m-%d")
        holding_days = (datetime.now() - entry_dt).days

        cursor.execute("""
            UPDATE trades SET
                exit_date = ?, exit_price = ?, exit_reason = ?,
                pnl = ?, pnl_pct = ?, r_multiple = ?, holding_days = ?,
                followed_plan = ?, mistakes = ?, lessons = ?
            WHERE id = ?
        """, (
            datetime.now().date(), exit_price, exit_reason,
            pnl, pnl_pct, r_multiple, holding_days,
            int(followed_plan), mistakes, lessons, trade_id
        ))

        conn.commit()
        conn.close()

        emoji = "✅" if pnl > 0 else "❌"
        print(f"""
╔═══════════════════════════════════════════════════════════╗
║           {emoji} TRADE CLOSED #{trade_id}
╠═══════════════════════════════════════════════════════════╣
║  Exit Price:   ${exit_price:,.2f}
║  P&L:          ${pnl:,.2f} ({pnl_pct:+.2f}%)
║  R-Multiple:   {r_multiple:+.2f}R
║  Holding Days: {holding_days}
║  Reason:       {exit_reason}
╚═══════════════════════════════════════════════════════════╝""")

        return {"pnl": pnl, "pnl_pct": pnl_pct, "r_multiple": r_multiple}

    def get_open_trades(self) -> pd.DataFrame:
        """Get open trades"""
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query(
            """SELECT id, symbol, market, entry_date, entry_price, shares,
                      stop_loss, target_1, setup_type
               FROM trades WHERE exit_date IS NULL
               ORDER BY entry_date DESC""",
            conn
        )
        conn.close()
        return df

    def get_stats(self, days: int = 30) -> Dict:
        """Get performance stats"""
        conn = sqlite3.connect(self.db_path)

        query = """
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as wins,
                SUM(CASE WHEN pnl <= 0 THEN 1 ELSE 0 END) as losses,
                SUM(pnl) as total_pnl,
                AVG(pnl) as avg_pnl,
                AVG(CASE WHEN pnl > 0 THEN pnl END) as avg_win,
                AVG(CASE WHEN pnl <= 0 THEN pnl END) as avg_loss,
                AVG(r_multiple) as avg_r,
                MAX(pnl) as best,
                MIN(pnl) as worst,
                AVG(holding_days) as avg_hold
            FROM trades
            WHERE exit_date IS NOT NULL
            AND exit_date >= date('now', ?)
        """

        df = pd.read_sql_query(query, conn, params=(f'-{days} days',))
        conn.close()

        if df.empty or df.iloc[0]['total'] == 0:
            return {"total_trades": 0, "message": "No trades"}

        r = df.iloc[0]
        total = r['total'] or 0
        wins = r['wins'] or 0
        losses = r['losses'] or 0

        win_rate = (wins / total * 100) if total else 0
        avg_win = abs(r['avg_win']) if r['avg_win'] else 0
        avg_loss = abs(r['avg_loss']) if r['avg_loss'] else 1
        pf = (wins * avg_win) / (losses * avg_loss) if losses and avg_loss else 0

        return {
            "total_trades": int(total),
            "wins": int(wins),
            "losses": int(losses),
            "win_rate": round(win_rate, 1),
            "total_pnl": round(r['total_pnl'] or 0, 2),
            "avg_pnl": round(r['avg_pnl'] or 0, 2),
            "avg_win": round(r['avg_win'] or 0, 2),
            "avg_loss": round(r['avg_loss'] or 0, 2),
            "avg_r": round(r['avg_r'] or 0, 2),
            "profit_factor": round(pf, 2),
            "best_trade": round(r['best'] or 0, 2),
            "worst_trade": round(r['worst'] or 0, 2),
            "avg_hold": round(r['avg_hold'] or 0, 1)
        }

    def get_stats_by_setup(self) -> pd.DataFrame:
        """Performance by setup"""
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query("""
            SELECT
                setup_type,
                COUNT(*) as trades,
                ROUND(SUM(CASE WHEN pnl > 0 THEN 1.0 ELSE 0 END) * 100 / COUNT(*), 1) as win_rate,
                ROUND(AVG(r_multiple), 2) as avg_r,
                ROUND(SUM(pnl), 2) as total_pnl
            FROM trades
            WHERE exit_date IS NOT NULL AND setup_type IS NOT NULL
            GROUP BY setup_type
            ORDER BY total_pnl DESC
        """, conn)
        conn.close()
        return df

    def print_report(self, days: int = 30):
        """Print performance report"""
        stats = self.get_stats(days)

        if stats.get('total_trades', 0) == 0:
            print(f"\n📊 No closed trades in last {days} days")
            return

        print(f"""
╔═══════════════════════════════════════════════════════════════════════╗
║              📊 PERFORMANCE REPORT - Last {days} Days
╠═══════════════════════════════════════════════════════════════════════╣
║                                                                       ║
║  TRADES                                                               ║
║  Total: {stats['total_trades']:>4}    Winners: {stats['wins']:>4}    Losers: {stats['losses']:>4}
║  Win Rate: {stats['win_rate']:>5.1f}%         Profit Factor: {stats['profit_factor']:>5.2f}
║                                                                       ║
║  P&L                                                                  ║
║  Total:    ${stats['total_pnl']:>10,.2f}    Avg:   ${stats['avg_pnl']:>10,.2f}
║  Avg Win:  ${stats['avg_win']:>10,.2f}    Avg Loss: ${stats['avg_loss']:>10,.2f}
║  Best:     ${stats['best_trade']:>10,.2f}    Worst: ${stats['worst_trade']:>10,.2f}
║                                                                       ║
║  QUALITY                                                              ║
║  Avg R: {stats['avg_r']:>+6.2f}R          Avg Hold: {stats['avg_hold']:>5.1f} days
║                                                                       ║
╚═══════════════════════════════════════════════════════════════════════╝""")

        setup_df = self.get_stats_by_setup()
        if not setup_df.empty:
            print("\n📈 BY SETUP TYPE:")
            for _, row in setup_df.iterrows():
                e = "✅" if row['total_pnl'] > 0 else "❌"
                print(f"  {e} {row['setup_type']:15} | Win: {row['win_rate']:5.1f}% | "
                      f"Avg R: {row['avg_r']:+5.2f} | P&L: ${row['total_pnl']:>8,.2f}")


# CLI
if __name__ == "__main__":
    import sys

    journal = TradeJournal()

    if len(sys.argv) < 2:
        print("""
Trade Journal Commands:
  python trade_journal.py report [days]  - Performance report
  python trade_journal.py open           - Open trades
  python trade_journal.py recent         - Recent trades
  python trade_journal.py setups         - Stats by setup type
        """)
    elif sys.argv[1] == "report":
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
        journal.print_report(days)
    elif sys.argv[1] == "open":
        df = journal.get_open_trades()
        if df.empty:
            print("No open trades")
        else:
            print("\n📂 OPEN TRADES:")
            print(df.to_string(index=False))
    elif sys.argv[1] == "recent":
        conn = sqlite3.connect("data/trade_journal.db")
        df = pd.read_sql_query(
            """SELECT id, symbol, exit_date, pnl, r_multiple, setup_type
               FROM trades WHERE exit_date IS NOT NULL
               ORDER BY exit_date DESC LIMIT 10""",
            conn
        )
        conn.close()
        print("\n📜 RECENT TRADES:")
        print(df.to_string(index=False))
    elif sys.argv[1] == "setups":
        df = journal.get_stats_by_setup()
        print("\n📈 BY SETUP:")
        print(df.to_string(index=False))
