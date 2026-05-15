"""Position Manager - Handles positions and risk"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import pandas as pd
import config


@dataclass
class Position:
    """Trading position"""
    symbol: str
    entry_price: float
    shares: int
    stop_loss: float
    target_1: float
    target_2: float
    entry_date: datetime = field(default_factory=datetime.now)
    status: str = "OPEN"
    exit_price: float = 0
    pnl: float = 0


class PositionManager:
    """Manages positions"""

    def __init__(self):
        self.account = config.ACCOUNT_SIZE
        self.risk = config.RISK_PER_TRADE
        self.max_positions = config.MAX_POSITIONS
        self.positions: List[Position] = []
        self.closed: List[Position] = []
        self.daily_pnl = 0

    def calc_position_size(self, entry: float, stop: float) -> Dict:
        """Calculate position size"""
        risk_per_share = entry - stop
        if risk_per_share <= 0:
            return {"error": "Invalid stop"}

        max_risk = self.account * self.risk
        shares = int(max_risk / risk_per_share)

        value = shares * entry
        max_value = self.account * config.MAX_POSITION_SIZE_PCT

        if value > max_value:
            shares = int(max_value / entry)
            value = shares * entry

        return {
            "shares": shares,
            "position_value": round(value, 2),
            "risk_dollars": round(shares * risk_per_share, 2),
            "risk_pct": round((shares * risk_per_share / self.account) * 100, 2),
        }

    def can_open(self) -> tuple:
        """Check if can open position"""
        open_count = len([p for p in self.positions if p.status == "OPEN"])
        if open_count >= self.max_positions:
            return False, "Max positions reached"
        if self.daily_pnl <= -self.account * config.DAILY_LOSS_LIMIT:
            return False, "Daily loss limit"
        return True, "OK"

    def open_position(self, signal: Dict) -> Optional[Position]:
        """Open position"""
        can, reason = self.can_open()
        if not can:
            print(f"Cannot open: {reason}")
            return None

        sizing = self.calc_position_size(signal["ideal_entry"], signal["stop_loss"])
        if "error" in sizing:
            return None

        pos = Position(
            symbol=signal["symbol"],
            entry_price=signal["ideal_entry"],
            shares=sizing["shares"],
            stop_loss=signal["stop_loss"],
            target_1=signal["target_1"],
            target_2=signal["target_2"],
        )

        self.positions.append(pos)
        print(f"Opened: {pos.symbol} - {pos.shares} shares @ ${pos.entry_price}")
        return pos

    def close_position(self, symbol: str, exit_price: float) -> Optional[Position]:
        """Close position"""
        for pos in self.positions:
            if pos.symbol == symbol and pos.status == "OPEN":
                pos.exit_price = exit_price
                pos.pnl = (exit_price - pos.entry_price) * pos.shares
                pos.status = "CLOSED"

                self.daily_pnl += pos.pnl
                self.closed.append(pos)
                self.positions.remove(pos)

                print(f"Closed: {symbol} @ ${exit_price} - P&L: ${pos.pnl:.2f}")
                return pos
        return None

    def get_summary(self) -> Dict:
        """Portfolio summary"""
        open_pos = [p for p in self.positions if p.status == "OPEN"]
        invested = sum(p.shares * p.entry_price for p in open_pos)

        return {
            "account": self.account,
            "open_positions": len(open_pos),
            "invested": round(invested, 2),
            "cash": round(self.account - invested, 2),
            "daily_pnl": round(self.daily_pnl, 2),
        }


if __name__ == "__main__":
    pm = PositionManager()

    sizing = pm.calc_position_size(875.50, 845.00)
    print("Position sizing:", sizing)

    signal = {
        "symbol": "NVDA",
        "ideal_entry": 875.50,
        "stop_loss": 845.00,
        "target_1": 936.50,
        "target_2": 967.00,
    }
    pm.open_position(signal)
    print("Summary:", pm.get_summary())
