"""Broker API - Alpaca integration"""

from typing import Dict, List, Optional
import config

try:
    from alpaca.trading.client import TradingClient
    from alpaca.trading.requests import MarketOrderRequest, LimitOrderRequest
    from alpaca.trading.enums import OrderSide, TimeInForce
    ALPACA_OK = True
except ImportError:
    ALPACA_OK = False


class BrokerAPI:
    """Alpaca broker wrapper"""

    def __init__(self, paper: bool = True):
        self.paper = paper
        self.connected = False
        self.client = None

        if ALPACA_OK and config.ALPACA_API_KEY:
            self._connect()
        else:
            print("Running in simulation mode")

    def _connect(self):
        """Connect to Alpaca"""
        try:
            self.client = TradingClient(
                api_key=config.ALPACA_API_KEY,
                secret_key=config.ALPACA_SECRET_KEY,
                paper=self.paper
            )
            account = self.client.get_account()
            self.connected = True
            print(f"Connected to Alpaca ({'Paper' if self.paper else 'Live'})")
            print(f"  Buying Power: ${float(account.buying_power):,.2f}")
        except Exception as e:
            print(f"Connection failed: {e}")

    def get_account(self) -> Dict:
        """Get account info"""
        if not self.connected:
            return {"status": "SIMULATED", "cash": config.ACCOUNT_SIZE, "buying_power": config.ACCOUNT_SIZE}

        try:
            a = self.client.get_account()
            return {"status": a.status, "cash": float(a.cash), "buying_power": float(a.buying_power)}
        except:
            return {}

    def get_positions(self) -> List[Dict]:
        """Get positions"""
        if not self.connected:
            return []

        try:
            return [{"symbol": p.symbol, "qty": int(p.qty), "pnl": float(p.unrealized_pl)}
                    for p in self.client.get_all_positions()]
        except:
            return []

    def place_order(self, symbol: str, qty: int, side: str, price: float = None) -> Optional[Dict]:
        """Place order"""
        if not self.connected:
            print(f"SIMULATED: {side.upper()} {qty} {symbol}" + (f" @ ${price}" if price else ""))
            return {"order_id": "SIM", "status": "simulated"}

        try:
            order_side = OrderSide.BUY if side == "buy" else OrderSide.SELL

            if price:
                req = LimitOrderRequest(symbol=symbol, qty=qty, side=order_side,
                                        time_in_force=TimeInForce.DAY, limit_price=price)
            else:
                req = MarketOrderRequest(symbol=symbol, qty=qty, side=order_side,
                                         time_in_force=TimeInForce.DAY)

            result = self.client.submit_order(req)
            print(f"Order placed: {side.upper()} {qty} {symbol}")
            return {"order_id": result.id, "status": result.status}
        except Exception as e:
            print(f"Order failed: {e}")
            return None

    def close_position(self, symbol: str) -> bool:
        """Close position"""
        if not self.connected:
            print(f"SIMULATED: Close {symbol}")
            return True

        try:
            self.client.close_position(symbol)
            return True
        except:
            return False


if __name__ == "__main__":
    broker = BrokerAPI(paper=True)
    print("Account:", broker.get_account())
    broker.place_order("NVDA", 10, "buy", 850.00)
