import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from _common import *

st.set_page_config(page_title="Overview — Global Trading", page_icon="🏠", layout="wide")
apply_css()
C = get_resources()

st.title("🏠 Trading Dashboard Overview")
_help(
    "**Overview** shows live index snapshots, your account configuration, and a multi-market quick scan.\n"
    "- **Markets** — choose which exchanges (US / DE / IN) to scan\n"
    "- Click **Scan Now** to fetch live signals across the full universe\n"
    "- Best used as a morning dashboard before market open to check overall market health"
)
st.markdown(
    f'<p style="color:#475569;font-size:.85rem;margin-top:-.8rem;margin-bottom:1.2rem;">'
    f'{datetime.now().strftime("%A, %d %B %Y  ·  %H:%M")} &nbsp;|&nbsp; '
    f'Risk / trade: <b style="color:#00b4d8;">{config.RISK_PER_TRADE*100:.1f}%</b> &nbsp;|&nbsp; '
    f'Max positions: <b style="color:#00b4d8;">{config.MAX_POSITIONS}</b></p>',
    unsafe_allow_html=True,
)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Account Size",   f"${config.ACCOUNT_SIZE:,}")
c2.metric("Monthly Target", f"${config.ACCOUNT_SIZE * config.MONTHLY_TARGET:,.0f} ({config.MONTHLY_TARGET*100:.0f}%)")
c3.metric("Risk / Trade",   f"{config.RISK_PER_TRADE*100:.1f}%  (${config.ACCOUNT_SIZE * config.RISK_PER_TRADE:,.0f})")
c4.metric("Max Positions",  config.MAX_POSITIONS)

st.markdown("---")
st.subheader("Market Indices")
if HAS_YF:
    idx_cols = st.columns(4)
    for i, (sym, label) in enumerate([("SPY","S&P 500"),("QQQ","NASDAQ 100"),("^VIX","VIX"),("^GDAXI","DAX")]):
        try:
            fi = _yf.Ticker(sym).fast_info
            price = getattr(fi, "last_price", None) or getattr(fi, "regular_market_price", 0)
            chg   = getattr(fi, "regular_market_change_percent", 0) or 0
            idx_cols[i].metric(label, f"{price:.2f}", f"{chg:+.2f}%")
        except Exception:
            idx_cols[i].metric(label, "N/A")

# ── Morning Brief ─────────────────────────────────────────────────────────────
st.markdown("---")
mb_col, _ = st.columns([2, 3])
with mb_col:
    generate_brief = st.button("📋 Generate Morning Brief", type="secondary", use_container_width=True)

if generate_brief:
    with st.spinner("Assembling morning brief…"):
        _brief_lines = [
            f"📋 MORNING BRIEF — {datetime.now().strftime('%A %d %B %Y, %H:%M')}",
            "=" * 50,
        ]

        # Market Regime
        if HAS_REGIME:
            try:
                _regime_obj = _mr.MarketRegimeFilter()
                _tradeable, _reason, _conf = _regime_obj.should_trade()
                _brief_lines.append(
                    f"\n🌍 MARKET REGIME: {'✅ TRADE' if _tradeable else '🚫 PAUSE'} ({_conf:.0f}% confidence)"
                )
                _brief_lines.append(f"   {_reason}")
            except Exception:
                _brief_lines.append("\n🌍 MARKET REGIME: unavailable")
        else:
            _brief_lines.append("\n🌍 MARKET REGIME: module not loaded")

        # Open positions summary
        if HAS_JOURNAL and HAS_YF:
            try:
                _br_open = C["journal"].get_open_trades()
                if not _br_open.empty:
                    _brief_lines.append(f"\n💼 OPEN POSITIONS ({len(_br_open)}):")
                    for _, _br_row in _br_open.iterrows():
                        _s = _br_row.get("symbol", "")
                        _e = float(_br_row.get("entry_price", 0) or 0)
                        _sl = float(_br_row.get("stop_loss", 0) or 0)
                        _t1 = float(_br_row.get("target_1", 0) or 0)
                        try:
                            _c = _yf.Ticker(_s).fast_info
                            _cur = getattr(_c, "last_price", None) or _e
                        except Exception:
                            _cur = _e
                        _pnl = (_cur - _e) * int(_br_row.get("shares", 0) or 0)
                        _stop_pct = ((_cur - _sl) / _e * 100) if _e else 99
                        _flag = " ⚠️ NEAR STOP" if 0 < _stop_pct < 2 else (" 🔴 STOPPED" if _cur <= _sl else "")
                        _brief_lines.append(
                            f"   {_s}: entry ${_e:.2f} → now ${_cur:.2f}  P&L ${_pnl:+,.0f}{_flag}"
                        )
                else:
                    _brief_lines.append("\n💼 OPEN POSITIONS: none")
            except Exception:
                pass

        # Cached signals summary
        _last_sigs = st.session_state.get("_sig_results", [])
        if _last_sigs:
            _strong = [s for s in _last_sigs if s.get("signal_status") == "STRONG BUY"]
            _buys   = [s for s in _last_sigs if s.get("signal_status") == "BUY"]
            _brief_lines.append(f"\n🎯 LAST SCAN RESULTS: {len(_strong)} STRONG BUY, {len(_buys)} BUY")
            for _sig in (_strong + _buys)[:5]:
                _brief_lines.append(
                    f"   {_sig.get('symbol')} (score {_sig.get('signal_score',0)}) — "
                    f"entry ${_sig.get('ideal_entry',0):.2f}, "
                    f"stop ${_sig.get('stop_loss',0):.2f}, "
                    f"T1 ${_sig.get('target_1',0):.2f}"
                )
        else:
            _brief_lines.append("\n🎯 SIGNALS: run 🎯 Signals page first to populate")

        _brief_lines.append("\n" + "=" * 50)
        _brief_text = "\n".join(_brief_lines)

        st.code(_brief_text, language=None)

        # Optional: send via Telegram
        _alerts_mod = None
        try:
            from alert_system import AlertSystem as _AS
            _alerts_mod = _AS()
        except Exception:
            pass

        _tg_ok = _alerts_mod is not None and bool(getattr(config, "TELEGRAM_BOT_TOKEN", ""))
        bc1, bc2 = st.columns(2)
        if bc1.button("📲 Send to Telegram", disabled=not _tg_ok,
                       help="Configure TELEGRAM_BOT_TOKEN in .env to enable",
                       key="_brief_tg"):
            try:
                _alerts_mod.send_telegram(_brief_text)
                st.success("✅ Morning brief sent to Telegram!")
            except Exception as _te:
                st.error(f"Telegram error: {_te}")
        if not _tg_ok:
            bc2.caption("Telegram not configured — set TELEGRAM_BOT_TOKEN in .env")

st.markdown("---")

# ── Open Positions — Live Status ─────────────────────────────────────────────
if HAS_JOURNAL and HAS_YF:
    try:
        _ov_open = C["journal"].get_open_trades()
        if not _ov_open.empty:
            st.subheader("📍 Open Positions — Live Status")
            _ov_syms = _ov_open["symbol"].tolist()

            @st.cache_data(ttl=300, show_spinner=False)
            def _ov_prices(syms: tuple):
                _p = {}
                for _s in syms:
                    try:
                        _fi = _yf.Ticker(_s).fast_info
                        _p[_s] = getattr(_fi, "last_price", None) or getattr(_fi, "regular_market_price", None) or 0.0
                    except Exception:
                        _p[_s] = None
                return _p

            _ov_live = _ov_prices(tuple(sorted(_ov_syms)))

            _total_unr = 0.0
            _attn = []
            for _, _r in _ov_open.iterrows():
                _sym   = _r.get("symbol", "")
                _entry = float(_r.get("entry_price", 0) or 0)
                _stop  = float(_r.get("stop_loss", 0) or 0)
                _t1    = float(_r.get("target_1", 0) or 0)
                _shr   = int(_r.get("shares", 0) or 0)
                _cur   = float(_ov_live.get(_sym) or _entry)
                _total_unr += (_cur - _entry) * _shr
                _stop_pct = ((_cur - _stop) / _entry * 100) if _entry else 100
                if _cur <= _stop:
                    _attn.append((_sym, "hit stop loss", "error"))
                elif _stop_pct < 2.0:
                    _attn.append((_sym, f"within {_stop_pct:.1f}% of stop", "warning"))
                elif _t1 and _cur >= _t1:
                    _attn.append((_sym, "reached Target 1", "success"))

            _ov1, _ov2, _ov3 = st.columns(3)
            _ov1.metric("Open Positions",  len(_ov_open))
            _ov2.metric("Unrealized P&L",  f"${_total_unr:+,.2f}",
                        delta_color="normal" if _total_unr >= 0 else "inverse")
            _ov3.metric("Need Attention",  len(_attn),
                        delta_color="off" if not _attn else "inverse")

            for _sym, _reason, _kind in _attn:
                if _kind == "error":
                    st.error(f"🔴 **{_sym}** {_reason} — go to 💼 Portfolio to act.")
                elif _kind == "success":
                    st.success(f"🏆 **{_sym}** {_reason} — consider taking partial profits.")
                else:
                    st.warning(f"⚠️ **{_sym}** {_reason} — monitor closely.")
    except Exception:
        pass

st.markdown("---")
st.subheader("Quick Scan — All Markets")
if not HAS_GSG:
    st.error("GlobalSignalGenerator not available.")
else:
    ov_markets = st.multiselect("Markets", ["US","DE","IN"], default=["US","DE","IN"], key="ov_mkts")
    if st.button("🔍 Scan Now", type="primary"):
        with st.spinner("Scanning all markets…"):
            try:
                sigs = C["gen"].generate_signals(markets=ov_markets)
                all_sigs = [s for mkt_sigs in sigs.values() for s in mkt_sigs]
                strong = sum(1 for s in all_sigs if s.get("signal_status") == "STRONG BUY")
                buys   = sum(1 for s in all_sigs if s.get("signal_status") == "BUY")
                st.success(f"**{strong} STRONG BUY** and **{buys} BUY** across {len(ov_markets)} markets")
                if all_sigs:
                    df = pd.DataFrame(all_sigs)
                    cols = ["symbol","market","signal_status","signal_score","current_price",
                            "ideal_entry","stop_loss","target_1","risk_reward"]
                    st.dataframe(df[[c for c in cols if c in df.columns]],
                                 use_container_width=True, hide_index=True)
            except Exception as e:
                st.error(f"Scan error: {e}")
