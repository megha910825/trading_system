import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from _common import *

st.set_page_config(page_title="Position Calculator — Global Trading", page_icon="📐", layout="wide")
apply_css()

st.title("📐 Position Size Calculator")
_help(
    "Calculates exactly how many shares to buy given your risk parameters — **always use this before placing an order**.\n"
    "- **Fixed Risk** — enter entry price and stop-loss; finds max shares that risk exactly `risk %` of account\n"
    "- **ATR-Based** — uses the stock's 14-period Average True Range as the stop unit (adapts to volatility)\n"
    "- Position is capped at 25% of account to prevent over-concentration in any single stock\n"
    "- You can override account size and risk % here without changing `config.py`"
)

method = st.radio("Sizing Method", ["Fixed Risk", "ATR-Based (volatility-adjusted)"], horizontal=True)
st.markdown("---")

pc1, pc2 = st.columns(2)
entry_p  = pc1.number_input("Entry Price ($)",  value=100.0, step=0.5, format="%.2f")
account  = pc2.number_input("Account Size ($)", value=float(config.ACCOUNT_SIZE), step=1000.0)
risk_pct = pc1.slider("Risk per trade (%)", 0.5, 3.0, float(config.RISK_PER_TRADE * 100), 0.1)

if method == "Fixed Risk":
    stop_p = pc2.number_input("Stop Loss ($)", value=round(entry_p * 0.95, 2), step=0.5, format="%.2f")
    if st.button("Calculate", type="primary"):
        rps = entry_p - stop_p
        if rps <= 0:
            st.error("Stop loss must be below entry.")
        else:
            max_risk = account * (risk_pct / 100)
            shares = int(max_risk / rps)
            if shares * entry_p > account * 0.25:
                shares = int(account * 0.25 / entry_p)
            value = shares * entry_p
            a, b, c, d = st.columns(4)
            a.metric("Shares",         shares)
            b.metric("Position Value", f"${value:,.2f}")
            c.metric("$ at Risk",      f"${shares * rps:,.2f}")
            d.metric("% of Account",   f"{value/account*100:.1f}%")

else:
    atr_val  = pc2.number_input("ATR (14-period $)", value=3.0, step=0.1, format="%.2f")
    atr_mult = pc1.number_input("ATR Multiplier",    value=2.0, step=0.5, format="%.1f")
    if st.button("Calculate ATR Size", type="primary"):
        atr_stop = atr_val * atr_mult
        if atr_stop <= 0:
            st.error("Invalid ATR value.")
        else:
            max_risk = account * (risk_pct / 100)
            shares   = int(max_risk / atr_stop)
            if shares * entry_p > account * 0.25:
                shares = int(account * 0.25 / entry_p)
            value = shares * entry_p
            a, b, c, d = st.columns(4)
            a.metric("Shares",         shares)
            b.metric("Position Value", f"${value:,.2f}")
            c.metric("Implied Stop",   f"${entry_p - atr_stop:.2f}")
            d.metric("ATR Stop Dist.", f"${atr_stop:.2f}")
