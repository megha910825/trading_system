#!/usr/bin/env python3
"""
Market Configuration - Definitions for US, German, and Indian Markets
"""

from dataclasses import dataclass
from typing import Dict, List


# ═══════════════════════════════════════════════════════════════
# MARKET INFO DATACLASS
# ═══════════════════════════════════════════════════════════════

@dataclass
class MarketInfo:
    """Market information and settings"""
    name: str
    code: str
    currency: str
    currency_symbol: str
    timezone: str
    open_time: str
    close_time: str
    suffix: str


# ═══════════════════════════════════════════════════════════════
# MARKET FLAGS & SYMBOLS
# ═══════════════════════════════════════════════════════════════

MARKET_FLAGS = {
    "US": "🇺🇸",
    "DE": "🇩🇪",
    "IN": "🇮🇳",
    "GLOBAL": "🌐",
}

CURRENCY_SYMBOLS = {
    "USD": "$",
    "EUR": "€",
    "INR": "₹",
}


# ═══════════════════════════════════════════════════════════════
# MARKET SETTINGS
# ═══════════════════════════════════════════════════════════════

MARKETS: Dict[str, MarketInfo] = {
    "US": MarketInfo(
        name="United States",
        code="US",
        currency="USD",
        currency_symbol="$",
        timezone="America/New_York",
        open_time="09:30",
        close_time="16:00",
        suffix="",
    ),
    "DE": MarketInfo(
        name="Germany",
        code="DE",
        currency="EUR",
        currency_symbol="€",
        timezone="Europe/Berlin",
        open_time="09:00",
        close_time="17:30",
        suffix=".DE",
    ),
    "IN": MarketInfo(
        name="India",
        code="IN",
        currency="INR",
        currency_symbol="₹",
        timezone="Asia/Kolkata",
        open_time="09:15",
        close_time="15:30",
        suffix=".NS",
    ),
}


# ═══════════════════════════════════════════════════════════════
# STOCK UNIVERSES
# ═══════════════════════════════════════════════════════════════

US_STOCKS = [
    # Tech - Semiconductors
    "NVDA", "AMD", "AVGO", "QCOM", "INTC", "MU", "AMAT", "LRCX", "TSM", "MRVL",
    "KLAC", "NXPI", "ON", "SWKS", "MPWR",
    # Tech - Software/Cloud
    "MSFT", "CRM", "ADBE", "NOW", "SNOW", "DDOG", "NET", "ZS", "CRWD", "PANW",
    "ORCL", "PLTR", "MDB", "TEAM", "WDAY",
    # Tech - Internet
    "GOOGL", "META", "AMZN", "NFLX", "UBER", "ABNB", "BKNG", "DASH", "SNAP",
    # Tech - Hardware
    "AAPL", "DELL", "HPQ", "HPE",
    # EV & Energy
    "TSLA", "RIVN", "LCID", "ENPH", "FSLR", "SEDG",
    # Fintech
    "PYPL", "SQ", "COIN", "V", "MA", "AXP", "FIS", "FISV",
    # Consumer
    "COST", "TGT", "WMT", "HD", "LOW", "NKE", "SBUX", "MCD", "CMG", "YUM",
    "LULU", "ROST", "TJX",
    # Finance
    "JPM", "GS", "MS", "BAC", "WFC", "C", "BLK", "SCHW",
    # Healthcare
    "UNH", "JNJ", "PFE", "LLY", "ABBV", "MRK", "TMO", "ABT", "ISRG", "DHR",
    "BMY", "AMGN", "GILD", "VRTX", "REGN",
    # Industrial
    "CAT", "BA", "HON", "GE", "UPS", "FDX", "RTX", "LMT", "NOC", "DE",
    # Communication
    "DIS", "CMCSA", "T", "VZ", "TMUS",
    # Energy
    "XOM", "CVX", "COP", "SLB", "EOG", "OXY",
]

GERMAN_STOCKS = [
    # DAX 40
    "SAP.DE", "SIE.DE", "ALV.DE", "DTE.DE", "AIR.DE", "BAS.DE", "BAYN.DE",
    "BMW.DE", "MBG.DE", "VOW3.DE", "ADS.DE", "DHL.DE", "MRK.DE", "MUV2.DE",
    "IFX.DE", "DB1.DE", "DBK.DE", "RWE.DE", "EON.DE", "HEN3.DE", "BEI.DE",
    "FRE.DE", "VNA.DE", "CON.DE", "PAH3.DE", "P911.DE", "SHL.DE", "ZAL.DE",
    "ENR.DE", "MTX.DE", "PUM.DE", "RHM.DE", "SY1.DE", "1COV.DE", "BNR.DE",
    "HNR1.DE", "QIA.DE", "SRT3.DE", "DHER.DE",
    # MDAX Notable
    "AFX.DE", "EVK.DE", "LEG.DE", "TLX.DE", "GXI.DE", "FME.DE", "NDA.DE",
    "TEG.DE", "AG1.DE", "KCO.DE",
]

INDIAN_STOCKS = [
    # NIFTY 50
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS",
    "HINDUNILVR.NS", "ITC.NS", "SBIN.NS", "BHARTIARTL.NS", "KOTAKBANK.NS",
    "LT.NS", "AXISBANK.NS", "ASIANPAINT.NS", "MARUTI.NS", "HCLTECH.NS",
    "SUNPHARMA.NS", "TITAN.NS", "WIPRO.NS", "BAJFINANCE.NS", "ULTRACEMCO.NS",
    "TATAMOTORS.NS", "ONGC.NS", "NTPC.NS", "POWERGRID.NS", "M&M.NS",
    "TATASTEEL.NS", "JSWSTEEL.NS", "ADANIENT.NS", "ADANIPORTS.NS", "COALINDIA.NS",
    "TECHM.NS", "NESTLEIND.NS", "DRREDDY.NS", "CIPLA.NS", "DIVISLAB.NS",
    "GRASIM.NS", "BRITANNIA.NS", "BAJAJFINSV.NS", "HEROMOTOCO.NS", "EICHERMOT.NS",
    "INDUSINDBK.NS", "APOLLOHOSP.NS", "HDFCLIFE.NS", "SBILIFE.NS", "TATACONSUM.NS",
    "BPCL.NS", "HINDALCO.NS", "UPL.NS",
    # Top Midcaps
    "ZOMATO.NS", "DMART.NS", "PIIND.NS", "PERSISTENT.NS", "LTIM.NS",
    "MPHASIS.NS", "COFORGE.NS", "TRENT.NS", "POLYCAB.NS", "DIXON.NS",
    "IRCTC.NS", "HAL.NS", "BEL.NS", "PFC.NS", "RECLTD.NS", "RVNL.NS",
]


# ═══════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def get_market_flag(market: str) -> str:
    """Get flag emoji for a market"""
    return MARKET_FLAGS.get(market, "🌐")


def get_currency_symbol(market_or_currency: str) -> str:
    """Get currency symbol for a market or currency code"""
    # Check if it's a currency code
    if market_or_currency in CURRENCY_SYMBOLS:
        return CURRENCY_SYMBOLS[market_or_currency]

    # Check if it's a market code
    market_info = MARKETS.get(market_or_currency)
    if market_info:
        return market_info.currency_symbol

    return "$"


def detect_market(symbol: str) -> str:
    """Detect which market a symbol belongs to"""
    symbol = symbol.upper()
    if symbol.endswith(".DE"):
        return "DE"
    elif symbol.endswith(".NS") or symbol.endswith(".BO"):
        return "IN"
    elif "=X" in symbol or "=F" in symbol:
        return "GLOBAL"
    return "US"


def get_market_stocks(market: str) -> List[str]:
    """Get stock list for a specific market"""
    stocks = {
        "US": US_STOCKS,
        "DE": GERMAN_STOCKS,
        "IN": INDIAN_STOCKS,
    }
    return stocks.get(market, [])


def get_all_stocks(markets: List[str] = None) -> Dict[str, List[str]]:
    """Get all stocks grouped by market"""
    all_stocks = {
        "US": US_STOCKS,
        "DE": GERMAN_STOCKS,
        "IN": INDIAN_STOCKS,
    }

    if markets:
        return {k: v for k, v in all_stocks.items() if k in markets}

    return all_stocks


def get_flat_stock_list(markets: List[str] = None) -> List[str]:
    """Get flat list of all stocks"""
    all_stocks = get_all_stocks(markets)
    flat_list = []
    for stocks in all_stocks.values():
        flat_list.extend(stocks)
    return flat_list


def is_market_open(market: str) -> bool:
    """
    Check if a market is currently open
    (Simplified - doesn't account for holidays)
    """
    try:
        from datetime import datetime
        import pytz

        market_info = MARKETS.get(market)
        if not market_info:
            return False

        tz = pytz.timezone(market_info.timezone)
        now = datetime.now(tz)

        # Check if weekend
        if now.weekday() >= 5:
            return False

        # Parse times
        open_h, open_m = map(int, market_info.open_time.split(":"))
        close_h, close_m = map(int, market_info.close_time.split(":"))

        open_time = now.replace(hour=open_h, minute=open_m, second=0)
        close_time = now.replace(hour=close_h, minute=close_m, second=0)

        return open_time <= now <= close_time
    except:
        return False


def get_market_status() -> Dict[str, str]:
    """Get status of all markets"""
    try:
        from datetime import datetime
        import pytz

        status = {}

        for code, info in MARKETS.items():
            try:
                tz = pytz.timezone(info.timezone)
                now = datetime.now(tz)

                if is_market_open(code):
                    status[code] = f"🟢 OPEN ({now.strftime('%H:%M')})"
                else:
                    status[code] = f"🔴 CLOSED ({now.strftime('%H:%M')})"
            except:
                status[code] = "⚪ UNKNOWN"

        return status
    except:
        return {code: "⚪ UNKNOWN" for code in MARKETS.keys()}


# ═══════════════════════════════════════════════════════════════
# MAIN / TEST
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 50)
    print("MARKET CONFIGURATION")
    print("=" * 50)

    print("\n📊 MARKETS:")
    for code, info in MARKETS.items():
        flag = get_market_flag(code)
        print(f"  {flag} {info.name} ({code})")
        print(f"     Currency: {info.currency} ({info.currency_symbol})")
        print(f"     Hours: {info.open_time} - {info.close_time}")

    print("\n📈 STOCK COUNTS:")
    print(f"  🇺🇸 US: {len(US_STOCKS)} stocks")
    print(f"  🇩🇪 DE: {len(GERMAN_STOCKS)} stocks")
    print(f"  🇮🇳 IN: {len(INDIAN_STOCKS)} stocks")
    print(f"  Total: {len(US_STOCKS) + len(GERMAN_STOCKS) + len(INDIAN_STOCKS)} stocks")

    print("\n🕐 MARKET STATUS:")
    for market, status in get_market_status().items():
        print(f"  {get_market_flag(market)} {market}: {status}")

    print("\n✅ Configuration loaded!")
