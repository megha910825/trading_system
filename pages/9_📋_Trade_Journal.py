import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from _common import *

st.set_page_config(page_title="Trade Journal — Global Trading", page_icon="📋", layout="wide")
apply_css()
C = get_resources()

st.title("📋 Trade Journal")
_help(
    "Full trade lifecycle management: log entries, track open trades, and record exits.\n"
    "- **Log Entry tab** — record every new trade with entry price, stop, target, and setup type\n"
    "- **Open Trades tab** — view and update in-progress positions; close them here when done\n"
    "- **Closed Trades tab** — full history with P&L and R-multiples\n"
    "- All data is stored locally in `data/trade_journal.json`"
)

if not HAS_JOURNAL:
    st.error("trade_journal module not available.")
else:
    journal = C["journal"]
    tab_log, tab_open, tab_closed = st.tabs(["➕ Log Entry", "📂 Open Trades", "✅ Closed Trades"])

    with tab_log:
        st.subheader("Log a New Trade Entry")
        l1, l2, l3 = st.columns(3)
        j_sym    = l1.text_input("Symbol", "NVDA").upper()
        j_mkt    = l2.selectbox("Market", ["US","DE","IN"])
        j_setup  = l3.selectbox("Setup", ["PULLBACK","BREAKOUT","MOMENTUM","REVERSAL"])

        l4, l5, l6 = st.columns(3)
        j_entry  = l4.number_input("Entry Price", value=100.0,  step=0.5, format="%.2f")
        j_stop   = l5.number_input("Stop Loss",   value=95.0,   step=0.5, format="%.2f")
        j_shares = l6.number_input("Shares",      value=10,     step=1,   min_value=1)

        l7, l8, l9 = st.columns(3)
        j_t1     = l7.number_input("Target 1",    value=110.0,  step=0.5, format="%.2f")
        j_t2     = l8.number_input("Target 2",    value=120.0,  step=0.5, format="%.2f")
        j_regime = l9.selectbox("Regime",         ["BULL","BEAR","SIDEWAYS","VOLATILE"])

        j_score  = st.slider("Signal Score", 0, 100, 65)
        j_reason = st.text_area("Entry Reason / Notes", height=80)

        if st.button("✅ Log Trade Entry", type="primary"):
            try:
                tid = journal.log_entry(
                    symbol=j_sym, entry_price=j_entry, shares=j_shares,
                    stop_loss=j_stop, target_1=j_t1, target_2=j_t2,
                    setup_type=j_setup, signal_score=j_score,
                    entry_reason=j_reason, market=j_mkt,
                    market_regime=j_regime,
                )
                st.success(f"✅ Trade #{tid} logged — {j_sym} × {j_shares} shares @ ${j_entry}")
            except Exception as e:
                st.error(f"Error logging trade: {e}")

    with tab_open:
        st.subheader("Open Positions")
        try:
            open_df = journal.get_open_trades()
            if open_df.empty:
                st.info("No open trades. Log one in the 'Log Entry' tab.")
            else:
                st.dataframe(open_df, use_container_width=True, hide_index=True)

                st.markdown("---")
                st.subheader("Close a Position")
                default_id = int(open_df["id"].iloc[0]) if "id" in open_df.columns else 1
                close_id     = st.number_input("Trade ID", min_value=1, step=1, value=default_id)
                cx1, cx2     = st.columns(2)
                close_price  = cx1.number_input("Exit Price ($)", value=100.0, step=0.5, format="%.2f")
                close_reason = cx2.selectbox("Exit Reason", ["TARGET_1","TARGET_2","STOP_LOSS","TIME_EXIT","MANUAL"])
                cm1, cm2     = st.columns(2)
                close_mae    = cm1.number_input("MAE % (max adverse, negative e.g. -3.2)", value=0.0, step=0.1, format="%.2f")
                close_mfe    = cm2.number_input("MFE % (max favourable, positive e.g. 7.5)", value=0.0, step=0.1, format="%.2f")
                close_notes  = st.text_area("Lessons / Mistakes", height=60)

                if st.button("❌ Close Trade", type="primary"):
                    try:
                        result = journal.log_exit(
                            trade_id=int(close_id),
                            exit_price=close_price,
                            exit_reason=close_reason,
                            mae=close_mae if close_mae != 0 else None,
                            mfe=close_mfe if close_mfe != 0 else None,
                            lessons=close_notes,
                        )
                        pnl = result.get("pnl", 0)
                        emoji = "✅" if pnl >= 0 else "❌"
                        st.success(f"{emoji} Trade #{close_id} closed — P&L: ${pnl:+,.2f} ({result.get('r_multiple',0):+.2f}R)")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error closing trade: {e}")
        except Exception as e:
            st.error(f"Error loading open trades: {e}")

    with tab_closed:
        st.subheader("Closed Trades History")
        try:
            closed_df = journal.get_closed_trades()
            if closed_df.empty:
                st.info("No closed trades yet.")
            else:
                wins      = (closed_df["pnl"] > 0).sum() if "pnl" in closed_df.columns else 0
                total     = len(closed_df)
                total_pnl = closed_df["pnl"].sum() if "pnl" in closed_df.columns else 0
                avg_r     = closed_df["r_multiple"].mean() if "r_multiple" in closed_df.columns else 0

                qs1, qs2, qs3, qs4 = st.columns(4)
                qs1.metric("Total Trades", total)
                qs2.metric("Win Rate",     f"{wins/total*100:.1f}%" if total else "N/A")
                qs3.metric("Total P&L",    f"${total_pnl:+,.2f}")
                qs4.metric("Avg R",        f"{avg_r:+.2f}R")

                st.dataframe(closed_df, use_container_width=True, hide_index=True)
        except Exception as e:
            st.error(f"Error loading closed trades: {e}")
