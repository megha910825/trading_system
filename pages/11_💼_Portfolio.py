import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from _common import *

st.set_page_config(page_title="Portfolio — Global Trading", page_icon="💼", layout="wide")
apply_css()
C = get_resources()

st.title("💼 Portfolio Overview")
_help(
    "Shows live positions from Alpaca and open trades from the Journal.\n"
    "- **Broker Sync** — pulls real account balance and positions directly from Alpaca\n"
    "- **Invested** — total capital currently deployed across all open positions\n"
    "- **Cash** — remaining available capital (`account − invested`)\n"
    "- No single position should exceed 25% of account (enforced by Position Calculator)"
)

# ── Lazy-load BrokerAPI (not in shared resources to avoid connect on every page) ──
@st.cache_resource
def _get_broker():
    try:
        import sys, os
        _root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if _root not in sys.path:
            sys.path.insert(0, _root)
        from broker_api import BrokerAPI
        return BrokerAPI(paper=True)
    except Exception:
        return None

broker = _get_broker()
broker_connected = broker is not None and getattr(broker, "connected", False)

# ── Account metrics ───────────────────────────────────────────────────────────
st.subheader("Account")
if broker_connected:
    try:
        acct = broker.get_account()
        a1, a2, a3, a4 = st.columns(4)
        a1.metric("Status",       acct.get("status", "—"))
        a2.metric("Cash",         f"${float(acct.get('cash', 0)):,.2f}")
        a3.metric("Buying Power", f"${float(acct.get('buying_power', 0)):,.2f}")
        a4.metric("Source",       "🟢 Alpaca Live")
    except Exception as e:
        st.error(f"Alpaca account error: {e}")
elif HAS_PM:
    try:
        summary = C["pm"].get_summary()
        a1, a2, a3, a4 = st.columns(4)
        a1.metric("Account",        f"${summary['account']:,}")
        a2.metric("Open Positions", summary['open_positions'])
        a3.metric("Invested",       f"${summary['invested']:,.2f}")
        a4.metric("Cash",           f"${summary['cash']:,.2f}")
    except Exception as e:
        st.error(f"Portfolio error: {e}")
else:
    a1, a2 = st.columns(2)
    a1.metric("Account Size",  f"${config.ACCOUNT_SIZE:,}")
    a2.metric("Source",        "⚪ Config (no broker connected)")

# ── Live Alpaca Positions ─────────────────────────────────────────────────────
st.markdown("---")
st.subheader("Live Positions" + (" — Alpaca" if broker_connected else " — Alpaca not connected"))

if broker_connected:
    if st.button("🔄 Refresh from Alpaca", type="primary"):
        st.cache_resource.clear()
        st.rerun()
    try:
        positions = broker.get_positions()
        if not positions:
            st.info("No open positions in Alpaca account.")
        else:
            pos_df = pd.DataFrame(positions)
            # Rename and format
            col_map = {"symbol": "Symbol", "qty": "Shares", "pnl": "Unrealised P&L"}
            pos_df = pos_df.rename(columns=col_map)
            if "Unrealised P&L" in pos_df.columns:
                pos_df["P&L"] = pos_df["Unrealised P&L"].apply(lambda v: f"${v:+,.2f}")
                pos_df = pos_df.drop(columns=["Unrealised P&L"])

            total_pnl = sum(p.get("pnl", 0) for p in positions)
            bp1, bp2 = st.columns(2)
            bp1.metric("Open Positions",    len(positions))
            bp2.metric("Total Unrealised P&L", f"${total_pnl:+,.2f}",
                       delta_color="normal" if total_pnl >= 0 else "inverse")

            st.dataframe(pos_df, use_container_width=True, hide_index=True)
    except Exception as e:
        st.error(f"Alpaca positions error: {e}")
else:
    st.warning(
        "Alpaca not connected. Set `ALPACA_API_KEY` and `ALPACA_SECRET_KEY` in your `.env` file "
        "and restart the container to enable live broker sync."
    )

# ── Live Position Monitor (journal + real-time prices) ────────────────────────
if HAS_JOURNAL:
    st.markdown("---")
    lm_col, ref_col = st.columns([5, 1])
    lm_col.subheader("📍 Open Positions — Live Monitor")
    with ref_col:
        if st.button("🔄 Refresh Prices", key="refresh_live_mon"):
            st.cache_data.clear()
            st.rerun()

    try:
        open_df = C["journal"].get_open_trades()
        if open_df.empty:
            st.info("No open positions in journal. Log your first trade on the 📋 Trade Journal page.")
        else:
            if HAS_YF:
                symbols = open_df["symbol"].tolist()

                @st.cache_data(ttl=300, show_spinner="Fetching live prices…")
                def _live_prices(syms: tuple):
                    prices = {}
                    for sym in syms:
                        try:
                            fi = _yf.Ticker(sym).fast_info
                            prices[sym] = (
                                getattr(fi, "last_price", None)
                                or getattr(fi, "regular_market_price", None)
                                or 0.0
                            )
                        except Exception:
                            prices[sym] = None
                    return prices

                live = _live_prices(tuple(sorted(symbols)))

                rows = []
                total_unr_pnl = 0.0
                attention_needed = []
                for _, row in open_df.iterrows():
                    sym    = row.get("symbol", "")
                    entry  = float(row.get("entry_price", 0) or 0)
                    stop   = float(row.get("stop_loss", 0) or 0)
                    t1     = float(row.get("target_1", 0) or 0)
                    shares = int(row.get("shares", 0) or 0)
                    cur    = float(live.get(sym) or entry)

                    unr_pnl  = (cur - entry) * shares
                    unr_pct  = ((cur - entry) / entry * 100) if entry else 0
                    stop_pct = ((cur - stop) / entry * 100) if entry else 100
                    t1_pct   = ((t1 - cur) / entry * 100) if entry else 0
                    total_unr_pnl += unr_pnl

                    if cur <= stop:
                        status = "🔴 STOPPED"
                        attention_needed.append((sym, "hit stop loss"))
                    elif stop_pct < 2.0:
                        status = "⚠️ NEAR STOP"
                        attention_needed.append((sym, f"within {stop_pct:.1f}% of stop"))
                    elif t1 and cur >= t1:
                        status = "🏆 TARGET 1 HIT"
                        attention_needed.append((sym, "reached Target 1"))
                    else:
                        status = "🟢 OK"

                    rows.append({
                        "Symbol":    sym,
                        "Shares":    shares,
                        "Entry":     f"${entry:.2f}",
                        "Current":   f"${cur:.2f}",
                        "Stop":      f"${stop:.2f}",
                        "Target 1":  f"${t1:.2f}" if t1 else "—",
                        "Unr. P&L":  f"${unr_pnl:+,.2f}",
                        "P&L %":     f"{unr_pct:+.1f}%",
                        "→ Stop":    f"{stop_pct:.1f}%",
                        "→ T1":      f"{t1_pct:.1f}%" if t1 else "—",
                        "Status":    status,
                    })

                # Summary metrics
                sm1, sm2, sm3, sm4 = st.columns(4)
                sm1.metric("Open Positions",    len(rows))
                sm2.metric("Unrealized P&L",    f"${total_unr_pnl:+,.2f}",
                           delta_color="normal" if total_unr_pnl >= 0 else "inverse")
                sm3.metric("Need Attention",    len(attention_needed),
                           delta_color="off" if not attention_needed else "inverse")
                sm4.metric("Prices as of",      "Live (≤5 min)")

                st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

                # Action alerts below table
                for sym, reason in attention_needed:
                    if "stop loss" in reason or "STOPPED" in reason:
                        st.error(f"🔴 **{sym}** has {reason} — consider closing immediately!")
                    elif "Target 1" in reason:
                        st.success(f"🏆 **{sym}** has {reason} — consider selling half and moving stop to breakeven.")
                    else:
                        st.warning(f"⚠️ **{sym}** is {reason} — watch closely.")

            else:
                # yfinance unavailable — show static journal data
                st.dataframe(open_df, use_container_width=True, hide_index=True)

    except Exception as e:
        st.error(f"Monitor error: {e}")

