#!/usr/bin/env python3
"""
Market Configuration - Settings for US, German, and Indian Markets
"""

from dataclasses import dataclass
from typing import Dict, List
import pytz

# ============================================================
# MARKET DEFINITIONS
# ============================================================

@dataclass
class MarketInfo:
    """Market information and settings"""
    name: str
    code: str
    currency: str
    timezone: str
    open_time: str
    close_time: str
    suffix: str  # Yahoo Finance suffix
    min_price: float
    max_price: float
    min_volume: int
    min_market_cap: float


# Define all supported markets
MARKETS: Dict[str, MarketInfo] = {
    "US": MarketInfo(
        name="United States",
        code="US",
        currency="USD",
        timezone="America/New_York",
        open_time="09:30",
        close_time="16:00",
        suffix="",  # No suffix for US stocks
        min_price=10,
        max_price=2000,
        min_volume=500_000,
        min_market_cap=1_000_000_000,  # $1B
    ),
    "DE": MarketInfo(
        name="Germany",
        code="DE",
        currency="EUR",
        timezone="Europe/Berlin",
        open_time="09:00",
        close_time="17:30",
        suffix=".DE",  # Frankfurt Stock Exchange
        min_price=5,
        max_price=1000,
        min_volume=100_000,
        min_market_cap=500_000_000,  # €500M
    ),
    "IN": MarketInfo(
        name="India",
        code="IN",
        currency="INR",
        timezone="Asia/Kolkata",
        open_time="09:15",
        close_time="15:30",
        suffix=".NS",  # NSE (National Stock Exchange)
        min_price=50,
        max_price=50000,
        min_volume=100_000,
        min_market_cap=10_000_000_000,  # ₹1000 Cr
    ),
}

# Alternative suffix for BSE (Bombay Stock Exchange)
INDIA_BSE_SUFFIX = ".BO"

# ============================================================
# STOCK UNIVERSES BY MARKET
# ============================================================

# US Stocks - S&P 500 / NASDAQ Top Stocks
US_STOCKS = [
    # Tech - Semiconductors
    "NVDA", "AMD", "AVGO", "QCOM", "INTC", "MU", "AMAT", "LRCX", "TSM",
    # Tech - Software/Cloud
    "MSFT", "CRM", "ADBE", "NOW", "SNOW", "DDOG", "NET", "ZS", "CRWD", "PANW",
    # Tech - Internet
    "GOOGL", "META", "AMZN", "NFLX", "UBER", "ABNB",
    # Tech - Hardware
    "AAPL", "DELL",
    # Electric Vehicles
    "TSLA", "RIVN",
    # Fintech
    "PYPL", "COIN", "V", "MA",
    # Consumer
    "COST", "TGT", "WMT", "HD", "NKE", "SBUX", "MCD",
    # Finance
    "JPM", "GS", "BAC", "MS",
    # Healthcare
    "UNH", "JNJ", "PFE", "LLY", "ABBV",
    # Industrial
    "CAT", "BA", "HON", "GE",
]

# German Stocks - DAX 40 + MDAX Top Stocks
GERMAN_STOCKS = [
    # DAX 40 Components
    "SAP.DE",      # SAP SE - Software
    "SIE.DE",      # Siemens AG - Industrial
    "ALV.DE",      # Allianz SE - Insurance
    "DTE.DE",      # Deutsche Telekom - Telecom
    "AIR.DE",      # Airbus SE - Aerospace
    "BAS.DE",      # BASF SE - Chemicals
    "BAYN.DE",     # Bayer AG - Pharma
    "BMW.DE",      # BMW - Automotive
    "MBG.DE",      # Mercedes-Benz - Automotive
    "VOW3.DE",     # Volkswagen - Automotive
    "ADS.DE",      # Adidas - Consumer
    "DHL.DE",      # DHL Group - Logistics
    "MRK.DE",      # Merck KGaA - Pharma
    "MUV2.DE",     # Munich Re - Insurance
    "IFX.DE",      # Infineon - Semiconductors
    "DB1.DE",      # Deutsche Börse - Finance
    "DBK.DE",      # Deutsche Bank - Finance
    "RWE.DE",      # RWE AG - Energy
    "EON.DE",      # E.ON SE - Energy
    "HEN3.DE",     # Henkel - Consumer
    "BEI.DE",      # Beiersdorf - Consumer
    "FRE.DE",      # Fresenius SE - Healthcare
    "HEI.DE",      # HeidelbergCement - Materials
    "VNA.DE",      # Vonovia - Real Estate
    "CON.DE",      # Continental - Automotive
    "PAH3.DE",     # Porsche Automobil - Automotive
    "P911.DE",     # Porsche AG - Automotive
    "SHL.DE",      # Siemens Healthineers - Healthcare
    "SRT3.DE",     # Sartorius - Healthcare
    "ZAL.DE",      # Zalando - E-commerce
    "DHER.DE",     # Delivery Hero - E-commerce
    "ENR.DE",      # Siemens Energy - Energy
    "MTX.DE",      # MTU Aero Engines - Aerospace
    "PUM.DE",      # Puma SE - Consumer
    "HNR1.DE",     # Hannover Rück - Insurance
    "QIA.DE",      # QIAGEN - Healthcare
    "RHM.DE",      # Rheinmetall - Defense
    "SY1.DE",      # Symrise - Chemicals
    "1COV.DE",     # Covestro - Chemicals
    "BNR.DE",      # Brenntag - Chemicals
    # MDAX Notable
    "AFX.DE",      # Carl Zeiss Meditec - Healthcare
    "EVK.DE",      # Evonik - Chemicals
    "LEG.DE",      # LEG Immobilien - Real Estate
    "NDA.DE",      # Aurubis - Materials
    "TEG.DE",      # TAG Immobilien - Real Estate
]

# Indian Stocks - NIFTY 50 + Top Midcaps
INDIAN_STOCKS = [
    # NIFTY 50 - Large Cap
    "RELIANCE.NS",   # Reliance Industries - Conglomerate
    "TCS.NS",        # Tata Consultancy Services - IT
    "HDFCBANK.NS",   # HDFC Bank - Banking
    "INFY.NS",       # Infosys - IT
    "ICICIBANK.NS",  # ICICI Bank - Banking
    "HINDUNILVR.NS", # Hindustan Unilever - FMCG
    "ITC.NS",        # ITC Limited - Conglomerate
    "SBIN.NS",       # State Bank of India - Banking
    "BHARTIARTL.NS", # Bharti Airtel - Telecom
    "KOTAKBANK.NS",  # Kotak Mahindra Bank - Banking
    "LT.NS",         # Larsen & Toubro - Infrastructure
    "AXISBANK.NS",   # Axis Bank - Banking
    "ASIANPAINT.NS", # Asian Paints - Paints
    "MARUTI.NS",     # Maruti Suzuki - Automotive
    "HCLTECH.NS",    # HCL Technologies - IT
    "SUNPHARMA.NS",  # Sun Pharma - Pharma
    "TITAN.NS",      # Titan Company - Consumer
    "WIPRO.NS",      # Wipro - IT
    "BAJFINANCE.NS", # Bajaj Finance - Finance
    "ULTRACEMCO.NS", # UltraTech Cement - Cement
    "TATAMOTORS.NS", # Tata Motors - Automotive
    "ONGC.NS",       # ONGC - Oil & Gas
    "NTPC.NS",       # NTPC - Power
    "POWERGRID.NS",  # Power Grid Corp - Power
    "M&M.NS",        # Mahindra & Mahindra - Automotive
    "TATASTEEL.NS",  # Tata Steel - Steel
    "JSWSTEEL.NS",   # JSW Steel - Steel
    "ADANIENT.NS",   # Adani Enterprises - Conglomerate
    "ADANIPORTS.NS", # Adani Ports - Infrastructure
    "COALINDIA.NS",  # Coal India - Mining
    "TECHM.NS",      # Tech Mahindra - IT
    "NESTLEIND.NS",  # Nestle India - FMCG
    "DRREDDY.NS",    # Dr. Reddy's - Pharma
    "CIPLA.NS",      # Cipla - Pharma
    "DIVISLAB.NS",   # Divi's Labs - Pharma
    "GRASIM.NS",     # Grasim Industries - Diversified
    "BRITANNIA.NS",  # Britannia - FMCG
    "BAJAJFINSV.NS", # Bajaj Finserv - Finance
    "HEROMOTOCO.NS", # Hero MotoCorp - Automotive
    "EICHERMOT.NS",  # Eicher Motors - Automotive
    "INDUSINDBK.NS", # IndusInd Bank - Banking
    "APOLLOHOSP.NS", # Apollo Hospitals - Healthcare
    "HDFCLIFE.NS",   # HDFC Life - Insurance
    "SBILIFE.NS",    # SBI Life - Insurance
    "TATACONSUM.NS", # Tata Consumer - FMCG
    "BPCL.NS",       # BPCL - Oil & Gas
    "HINDALCO.NS",   # Hindalco - Metals
    "UPL.NS",        # UPL - Agrochemicals
    # Top Midcaps
    "ZOMATO.NS",     # Zomato - Food Delivery
    "PAYTM.NS",      # Paytm - Fintech
    "NYKAA.NS",      # Nykaa - E-commerce
    "DMART.NS",      # DMart - Retail
    "PIIND.NS",      # PI Industries - Chemicals
    "PERSISTENT.NS", # Persistent Systems - IT
    "LTIM.NS",       # LTIMindtree - IT
    "MPHASIS.NS",    # Mphasis - IT
    "COFORGE.NS",    # Coforge - IT
    "TRENT.NS",      # Trent - Retail
    "POLYCAB.NS",    # Polycab - Cables
    "ASTRAL.NS",     # Astral - Pipes
    "DIXON.NS",      # Dixon Technologies - Electronics
    "IRCTC.NS",      # IRCTC - Travel
    "HAL.NS",        # Hindustan Aeronautics - Defense
    "BEL.NS",        # Bharat Electronics - Defense
    "NHPC.NS",       # NHPC - Power
    "PFC.NS",        # Power Finance Corp - Finance
    "RECLTD.NS",     # REC Limited - Finance
    "RVNL.NS",       # RVNL - Infrastructure
]

# ============================================================
# SECTOR MAPPINGS
# ============================================================

SECTOR_MAPPING = {
    # US Sectors
    "Technology": "TECH",
    "Consumer Cyclical": "CONSUMER",
    "Financial Services": "FINANCE",
    "Healthcare": "HEALTH",
    "Communication Services": "COMM",
    "Industrials": "INDUSTRIAL",
    "Consumer Defensive": "CONSUMER",
    "Energy": "ENERGY",
    "Basic Materials": "MATERIALS",
    "Real Estate": "REALESTATE",
    "Utilities": "UTILITIES",

    # German Sectors
    "Technologie": "TECH",
    "Konsumgüter": "CONSUMER",
    "Finanzdienstleistungen": "FINANCE",
    "Gesundheit": "HEALTH",
    "Industrie": "INDUSTRIAL",

    # Indian Sectors
    "Information Technology": "TECH",
    "Financial": "FINANCE",
    "Pharmaceuticals": "HEALTH",
    "Automobile": "AUTO",
    "FMCG": "CONSUMER",
    "Banking": "FINANCE",
    "Oil & Gas": "ENERGY",
    "Metals": "MATERIALS",
    "Power": "UTILITIES",
    "Infrastructure": "INDUSTRIAL",
    "Telecom": "COMM",
}

# ============================================================
# CURRENCY CONVERSION (for portfolio value)
# ============================================================

# Default exchange rates (updated dynamically)
DEFAULT_EXCHANGE_RATES = {
    "USD": 1.0,
    "EUR": 1.08,  # EUR to USD
    "INR": 0.012,  # INR to USD
}

# ============================================================
# TRADING HOURS CHECK
# ============================================================

def is_market_open(market_code: str) -> bool:
    """Check if a market is currently open"""
    from datetime import datetime

    if market_code not in MARKETS:
        return False

    market = MARKETS[market_code]
    tz = pytz.timezone(market.timezone)
    now = datetime.now(tz)

    # Check if weekend
    if now.weekday() >= 5:
        return False

    # Parse open/close times
    open_hour, open_min = map(int, market.open_time.split(":"))
    close_hour, close_min = map(int, market.close_time.split(":"))

    open_time = now.replace(hour=open_hour, minute=open_min, second=0)
    close_time = now.replace(hour=close_hour, minute=close_min, second=0)

    return open_time <= now <= close_time


def get_market_status() -> Dict[str, str]:
    """Get status of all markets"""
    status = {}
    from datetime import datetime

    for code, market in MARKETS.items():
        tz = pytz.timezone(market.timezone)
        now = datetime.now(tz)

        if is_market_open(code):
            status[code] = f"🟢 OPEN ({now.strftime('%H:%M')} {market.timezone})"
        else:
            status[code] = f"🔴 CLOSED ({now.strftime('%H:%M')} {market.timezone})"

    return status


def get_all_stocks(markets: List[str] = None) -> Dict[str, List[str]]:
    """Get all stocks grouped by market"""
    if markets is None:
        markets = ["US", "DE", "IN"]

    stocks = {}

    if "US" in markets:
        stocks["US"] = US_STOCKS
    if "DE" in markets:
        stocks["DE"] = GERMAN_STOCKS
    if "IN" in markets:
        stocks["IN"] = INDIAN_STOCKS

    return stocks


def get_flat_stock_list(markets: List[str] = None) -> List[str]:
    """Get flat list of all stocks from specified markets"""
    all_stocks = get_all_stocks(markets)
    flat_list = []

    for market, stocks in all_stocks.items():
        flat_list.extend(stocks)

    return flat_list


# ============================================================
# MAIN / TEST
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("MARKET CONFIGURATION")
    print("=" * 60)

    print("\n📊 SUPPORTED MARKETS:")
    for code, market in MARKETS.items():
        print(f"\n  {market.name} ({code}):")
        print(f"    Currency: {market.currency}")
        print(f"    Hours: {market.open_time} - {market.close_time} ({market.timezone})")
        print(f"    Yahoo Suffix: '{market.suffix}'")

    print("\n" + "=" * 60)
    print("MARKET STATUS")
    print("=" * 60)

    for code, status in get_market_status().items():
        print(f"  {MARKETS[code].name}: {status}")

    print("\n" + "=" * 60)
    print("STOCK COUNTS")
    print("=" * 60)

    all_stocks = get_all_stocks()
    total = 0
    for market, stocks in all_stocks.items():
        print(f"  {MARKETS[market].name}: {len(stocks)} stocks")
        total += len(stocks)

    print(f"\n  Total: {total} stocks")
