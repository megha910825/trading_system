import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from _common import *

st.set_page_config(page_title="Signals — Global Trading", page_icon="🎯", layout="wide")
apply_css()
C = get_resources()

st.title("🎯 Trading Signals — All Markets")
_help(
    "Generates ranked technical buy/sell signals across the full stock universe.\n"
    "- **Markets** — select US, German (XETRA), or Indian (NSE) exchanges\n"
    "- **Minimum strength** — *BUY* shows actionable setups; *STRONG BUY* = highest conviction only\n"
    "- **Send Alerts** — auto-sends Telegram / Email for every signal that passes the filter\n"
    "- Click **Generate Signals** — fetches live data and may take 30–60 seconds\n"
    "- Results are sorted by score; focus on the top 5–10 with the highest scores"
)

# ── Alert system (lazy, no crash if module missing) ───────────────────────────
@st.cache_resource
def _get_alerts():
    try:
        from alert_system import AlertSystem
        return AlertSystem()
    except Exception:
        return None

alerts = _get_alerts()
alerts_available = alerts is not None
telegram_configured = alerts_available and bool(getattr(config, "TELEGRAM_BOT_TOKEN", ""))
email_configured    = alerts_available and bool(getattr(config, "EMAIL_SENDER", ""))

if not HAS_GSG:
    st.error("GlobalSignalGenerator not available.")
else:
    f1, f2, f3 = st.columns(3)
    sig_markets  = f1.multiselect("Markets", ["US","DE","IN"], default=["US","DE","IN"], key="sig_mkts")
    min_status   = f2.selectbox("Minimum strength", ["STRONG BUY","BUY","WATCH"], index=1)
    send_alerts  = f3.checkbox(
        "📲 Send alerts",
        value=False,
        help=(
            "Sends Telegram / Email for each signal that passes the filter.\n"
            f"Telegram: {'✅ configured' if telegram_configured else '❌ not set'} · "
            f"Email: {'✅ configured' if email_configured else '❌ not set'}"
        ),
    )

    if st.button("⚡ Generate Signals", type="primary"):
        with st.spinner(f"Scanning {', '.join(sig_markets)} — full ranked universe…"):
            try:
                raw = C["gen"].generate_signals(markets=sig_markets)
                all_sigs = [s for mkt_sigs in raw.values() for s in mkt_sigs]

                order = {"STRONG BUY": 3, "BUY": 2, "WATCH": 1, "AVOID": 0}
                threshold = order.get(min_status, 1)
                filtered = [s for s in all_sigs if order.get(s.get("signal_status","AVOID"), 0) >= threshold]

                if not filtered:
                    st.info("No signals match the selected criteria.")
                else:
                    st.success(f"**{len(filtered)} signals** found")

                    sm_cols = st.columns(len(sig_markets))
                    for i, mkt in enumerate(sig_markets):
                        sm_cols[i].metric(f"{mkt}", sum(1 for s in filtered if s.get("market") == mkt))

                    st.markdown("---")
                    df = pd.DataFrame(filtered)
                    show = ["symbol","name","market","signal_status","signal_score","sector",
                            "current_price","ideal_entry","stop_loss","target_1","target_2",
                            "risk_reward","rsi","days_to_earnings","earnings_warning"]
                    st.dataframe(df[[c for c in show if c in df.columns]],
                                 use_container_width=True, hide_index=True)

                    # Persist results so Quick-Log stays visible after button click
                    st.session_state["_sig_results"] = filtered

                    st.markdown("---")
                    st.subheader("Top Signal Detail")
                    best = max(filtered, key=lambda s: s.get("signal_score", 0))
                    st.code(C["gen"].format_alert(best), language=None)

                    # ── Send alerts ───────────────────────────────────────────
                    if send_alerts:
                        if not alerts_available:
                            st.warning("AlertSystem module not available — alerts not sent.")
                        elif not telegram_configured and not email_configured:
                            st.warning(
                                "No alert channels configured. "
                                "Set `TELEGRAM_BOT_TOKEN` or `EMAIL_SENDER` in your `.env` file."
                            )
                        else:
                            sent = 0
                            with st.spinner(f"Sending alerts for {len(filtered)} signal(s)…"):
                                for sig in filtered:
                                    try:
                                        alerts.send_signal(sig)
                                        sent += 1
                                    except Exception as ae:
                                        st.warning(f"Alert failed for {sig.get('symbol')}: {ae}")
                            channels = []
                            if telegram_configured: channels.append("Telegram")
                            if email_configured:    channels.append("Email")
                            st.success(f"📲 {sent} alert(s) sent via {' & '.join(channels)}.")

            except Exception as e:
                st.error(f"Signal error: {e}")

# ── Quick-Log (persists between reruns via session_state) ─────────────────────
if st.session_state.get("_sig_results"):
    st.markdown("---")
    with st.expander("📝 Quick-Log a Signal to Trade Journal", expanded=False):
        _cached = st.session_state["_sig_results"]
        _labels = [
            f"{s.get('symbol')} — {s.get('signal_status')} (score {s.get('signal_score',0)})"
            for s in _cached
        ]
        _chosen_label = st.selectbox("Select signal", _labels, key="_ql_sig")
        _chosen = _cached[_labels.index(_chosen_label)]

        ql1, ql2, ql3 = st.columns(3)
        _ql_shares = ql1.number_input("Shares to buy", min_value=1, value=10, step=1, key="_ql_shares")
        _setup_opts = ["PULLBACK", "BREAKOUT", "REVERSAL", "MOMENTUM", "OTHER"]
        _default_setup = _chosen.get("setup_type", "PULLBACK")
        if _default_setup not in _setup_opts:
            _default_setup = "PULLBACK"
        _ql_setup = ql2.selectbox("Setup type", _setup_opts,
                                   index=_setup_opts.index(_default_setup), key="_ql_setup")
        ql3.markdown(" ")
        ql3.markdown(
            f"**Entry** ${_chosen.get('ideal_entry',0):.2f} &nbsp; "
            f"**Stop** ${_chosen.get('stop_loss',0):.2f} &nbsp; "
            f"**T1** ${_chosen.get('target_1',0):.2f}",
            unsafe_allow_html=True,
        )

        if st.button("📝 Log Entry to Journal", type="primary", key="_ql_submit"):
            if HAS_JOURNAL:
                try:
                    _tid = C["journal"].log_entry(
                        symbol=_chosen.get("symbol", ""),
                        entry_price=_chosen.get("ideal_entry", 0),
                        shares=_ql_shares,
                        stop_loss=_chosen.get("stop_loss", 0),
                        target_1=_chosen.get("target_1", 0),
                        target_2=_chosen.get("target_2"),
                        setup_type=_ql_setup,
                        signal_score=_chosen.get("signal_score", 0),
                        entry_reason=f"Signal dashboard — {_chosen.get('signal_status')}",
                        market=_chosen.get("market", "US"),
                    )
                    st.success(
                        f"✅ Trade logged! ID #{_tid} — {_chosen.get('symbol')} "
                        f"@ ${_chosen.get('ideal_entry',0):.2f} × {_ql_shares} shares. "
                        f"View it on the 📋 Trade Journal page."
                    )
                except Exception as _le:
                    st.error(f"Failed to log: {_le}")
            else:
                st.error("Trade Journal module not available.")

