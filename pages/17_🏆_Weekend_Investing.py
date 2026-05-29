import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from _common import *

st.set_page_config(page_title="Weekend Investing — Global Trading", page_icon="🏆", layout="wide")
apply_css()

st.title("🏆 Weekend Investing — Alok Jain Momentum Strategies")
st.markdown(
    '<p style="color:#475569;font-size:.85rem;margin-top:-.8rem;margin-bottom:1rem;">'
    'Rule-based rotational momentum strategies inspired by '
    '<a href="https://weekendinvesting.com" target="_blank" '
    'style="color:#00b4d8;text-decoration:none;">weekendinvesting.com</a>. '
    'Ranks stocks by composite momentum score and rebalances weekly or monthly.</p>',
    unsafe_allow_html=True,
)
_help(
    "**How to run a rebalance:**\n"
    "1. Select a strategy (e.g. *Mi-35* for small-cap momentum, *Mi-Top10* for large-cap safe)\n"
    "2. Enter your total capital allocated to this strategy\n"
    "3. Enter current holdings (comma-separated symbols) so the system knows what you already hold\n"
    "4. Click **Generate Rebalance Signal** — the system scores the entire universe with a progress bar\n"
    "5. Execute ✅ BUY and ❌ SELL signals at Monday market open (9:15 AM IST) — equal weight per slot\n\n"
    "**Key rules:** Never override a SELL signal. Never size up on conviction. "
    "When the system shows 🟡 CASH, park that slot in LIQUIDBEES or a liquid fund."
)

if not HAS_WI:
    st.error("weekend_investing_strategy module not available.")
else:
    from weekend_investing_strategy import (
        WeekendInvestingStrategy, STRATEGY_PRESETS, CASH_PROXY
    )

    wi_col1, wi_col2, wi_col3 = st.columns([2, 1, 1])
    wi_strategy = wi_col1.selectbox(
        "Strategy",
        list(STRATEGY_PRESETS.keys()),
        format_func=lambda k: f"{k}  —  {STRATEGY_PRESETS[k]['label']}",
        index=list(STRATEGY_PRESETS.keys()).index("Mi-35"),
    )
    wi_capital = wi_col2.number_input(
        "Capital (₹)", min_value=10_000, max_value=100_000_000,
        value=500_000, step=50_000,
    )
    wi_holdings_raw = wi_col3.text_area(
        "Current Holdings (comma-sep)", height=68,
        help="Symbols you already hold — used to compute BUY/HOLD/SELL actions",
    )
    wi_holdings = [s.strip().upper() for s in wi_holdings_raw.split(",") if s.strip()]

    cfg = STRATEGY_PRESETS[wi_strategy]
    col_desc1, col_desc2, col_desc3, col_desc4 = st.columns(4)
    col_desc1.markdown(
        f'<div style="background:rgba(0,180,216,.06);border:1px solid rgba(0,180,216,.15);'
        f'border-radius:10px;padding:.6rem .9rem;">'
        f'<div style="font-size:.65rem;color:#4b5e7a;font-weight:700;text-transform:uppercase;letter-spacing:.08em;">Universe</div>'
        f'<div style="font-size:.95rem;color:#e2e8f0;font-weight:600;margin-top:.15rem;">'
        f'{len(cfg["universe"])} stocks</div></div>', unsafe_allow_html=True)
    col_desc2.markdown(
        f'<div style="background:rgba(0,180,216,.06);border:1px solid rgba(0,180,216,.15);'
        f'border-radius:10px;padding:.6rem .9rem;">'
        f'<div style="font-size:.65rem;color:#4b5e7a;font-weight:700;text-transform:uppercase;letter-spacing:.08em;">Portfolio Size</div>'
        f'<div style="font-size:.95rem;color:#e2e8f0;font-weight:600;margin-top:.15rem;">'
        f'Top {cfg["top_n"]} stocks</div></div>', unsafe_allow_html=True)
    col_desc3.markdown(
        f'<div style="background:rgba(0,180,216,.06);border:1px solid rgba(0,180,216,.15);'
        f'border-radius:10px;padding:.6rem .9rem;">'
        f'<div style="font-size:.65rem;color:#4b5e7a;font-weight:700;text-transform:uppercase;letter-spacing:.08em;">Rebalance</div>'
        f'<div style="font-size:.95rem;color:#e2e8f0;font-weight:600;margin-top:.15rem;">'
        f'{cfg["rebalance"].title()}</div></div>', unsafe_allow_html=True)
    col_desc4.markdown(
        f'<div style="background:rgba(0,180,216,.06);border:1px solid rgba(0,180,216,.15);'
        f'border-radius:10px;padding:.6rem .9rem;">'
        f'<div style="font-size:.65rem;color:#4b5e7a;font-weight:700;text-transform:uppercase;letter-spacing:.08em;">Abs. Momentum</div>'
        f'<div style="font-size:.95rem;color:#e2e8f0;font-weight:600;margin-top:.15rem;">'
        f'{"✅ Cash filter" if cfg["absolute_momentum"] else "❌ Always invested"}</div></div>',
        unsafe_allow_html=True)
    st.caption(cfg["description"])

    st.divider()

    tab_rebal, tab_rank, tab_bt, tab_guide = st.tabs(
        ["📋 Rebalance Now", "📊 Full Universe Ranking", "📈 Backtest", "📖 Strategy Guide"]
    )

    with tab_rebal:
        if st.button("⚡ Generate Rebalance Signal", type="primary"):
            progress_bar  = st.progress(0, text="Scoring stocks…")
            progress_text = st.empty()

            def _progress_cb(cur, tot):
                pct = int(cur / tot * 100)
                progress_bar.progress(pct, text=f"Scoring {cur}/{tot} stocks…")
                progress_text.caption(f"Processing universe ({cur}/{tot})")

            try:
                engine = WeekendInvestingStrategy()
                result = engine.run(
                    wi_strategy,
                    capital=wi_capital,
                    current_holdings=wi_holdings,
                    on_progress=_progress_cb,
                )
                progress_bar.empty()
                progress_text.empty()

                if not result.portfolio:
                    st.warning("No stocks scored — check your internet connection or try a smaller universe.")
                else:
                    st.markdown(f"""
<div style="background:linear-gradient(135deg,#0d1321,#111827);border:1px solid rgba(0,180,216,.2);
            border-radius:14px;padding:1rem 1.4rem;margin-bottom:1rem;">
  <div style="font-size:1.2rem;font-weight:800;color:#f1f5f9;">{result.strategy_label}</div>
  <div style="display:flex;gap:2rem;margin-top:.6rem;flex-wrap:wrap;">
    <span style="color:#64748b;font-size:.8rem;">📅 Rebalance Date: <b style="color:#e2e8f0;">{result.rebalance_date}</b></span>
    <span style="color:#64748b;font-size:.8rem;">⏰ Next Action: <b style="color:#00b4d8;">{result.next_action_date}</b></span>
    <span style="color:#64748b;font-size:.8rem;">🌐 Scored: <b style="color:#e2e8f0;">{result.scored_count}/{result.universe_size}</b></span>
    <span style="color:#64748b;font-size:.8rem;">💵 Cash: <b style="color:{"#fbb703" if result.cash_pct > 0 else "#00cc96"};">{result.cash_pct:.0f}%</b></span>
  </div>
</div>
""", unsafe_allow_html=True)

                    ac1, ac2 = st.columns(2)
                    with ac1:
                        if result.entries:
                            st.markdown(
                                f'<div style="background:rgba(0,204,150,.08);border:1px solid rgba(0,204,150,.25);'
                                f'border-radius:10px;padding:.75rem 1rem;">'
                                f'<div style="color:#00cc96;font-weight:700;font-size:.9rem;">✅ BUY ({len(result.entries)} new)</div>'
                                f'<div style="color:#94a3b8;font-size:.82rem;margin-top:.3rem;">'
                                + " &nbsp;·&nbsp; ".join(result.entries) +
                                '</div></div>', unsafe_allow_html=True)
                        else:
                            st.markdown(
                                '<div style="background:rgba(0,204,150,.05);border:1px solid rgba(0,204,150,.1);'
                                'border-radius:10px;padding:.75rem 1rem;color:#4b5e7a;">✅ No new buys</div>',
                                unsafe_allow_html=True)
                    with ac2:
                        if result.exits:
                            st.markdown(
                                f'<div style="background:rgba(239,83,80,.08);border:1px solid rgba(239,83,80,.25);'
                                f'border-radius:10px;padding:.75rem 1rem;">'
                                f'<div style="color:#ef5350;font-weight:700;font-size:.9rem;">❌ SELL ({len(result.exits)} exits)</div>'
                                f'<div style="color:#94a3b8;font-size:.82rem;margin-top:.3rem;">'
                                + " &nbsp;·&nbsp; ".join(result.exits) +
                                '</div></div>', unsafe_allow_html=True)
                        else:
                            st.markdown(
                                '<div style="background:rgba(239,83,80,.05);border:1px solid rgba(239,83,80,.1);'
                                'border-radius:10px;padding:.75rem 1rem;color:#4b5e7a;">❌ No exits this rebalance</div>',
                                unsafe_allow_html=True)

                    st.divider()
                    st.subheader(f"Portfolio — Top {cfg['top_n']} Holdings")
                    rows = []
                    for slot in result.portfolio:
                        action_color = {"BUY":"🟢","HOLD":"🔵","SELL":"🔴","CASH":"🟡"}.get(slot.action,"⚪")
                        rows.append({
                            "Rank":     slot.rank,
                            "Action":   f"{action_color} {slot.action}",
                            "Symbol":   slot.symbol,
                            "Name":     slot.name[:28],
                            "Score":    slot.momentum_score,
                            "6M %":     slot.momentum_6m,
                            "ATH %":    slot.pct_from_ath,
                            "Weight":   f"{slot.weight_pct:.1f}%",
                            "₹ Amount": f"₹{slot.capital_amount:,.0f}",
                        })
                    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

                    if result.errors:
                        with st.expander(f"⚠️ {len(result.errors)} symbols could not be scored"):
                            st.caption(", ".join(result.errors))

            except Exception as e:
                progress_bar.empty()
                progress_text.empty()
                st.error(f"Error: {e}")

    with tab_rank:
        st.subheader(f"Full Universe Ranking — {cfg['label']}")
        st.caption(f"All {len(cfg['universe'])} stocks scored and ranked. Top {cfg['top_n']} would be in portfolio.")
        if st.button("📊 Rank Full Universe", type="primary", key="rank_btn"):
            rank_progress = st.progress(0, text="Scoring universe…")

            def _rank_cb(cur, tot):
                rank_progress.progress(int(cur / tot * 100), text=f"Scoring {cur}/{tot}…")

            try:
                engine = WeekendInvestingStrategy()
                rank_df = engine.rank_universe(wi_strategy, on_progress=_rank_cb)
                rank_progress.empty()

                if rank_df.empty:
                    st.warning("No data returned.")
                else:
                    top_n = cfg["top_n"]
                    st.success(f"✅ {len(rank_df)} stocks scored. Top {top_n} form the portfolio.")
                    st.dataframe(
                        rank_df.style.apply(
                            lambda r: ["background:rgba(0,204,150,.08)" if r["In Portfolio"] == "✅"
                                       else "" for _ in r],
                            axis=1,
                        ),
                        use_container_width=True, hide_index=True,
                    )
            except Exception as e:
                rank_progress.empty()
                st.error(f"Error: {e}")

    with tab_bt:
        st.subheader("Simple Historical Backtest")
        st.caption("Simulates rebalancing at each period boundary using historical closes. No slippage, brokerage, or taxes included.")
        bt_years = st.slider("Lookback (years)", 1, 5, 3)
        bt_cap   = st.number_input("Starting Capital (₹)", value=500_000, step=50_000, key="bt_cap")

        if st.button("▶ Run Backtest", type="primary", key="wi_bt_btn"):
            with st.spinner(f"Backtesting {wi_strategy} over {bt_years} years…"):
                try:
                    import plotly.graph_objects as go

                    engine = WeekendInvestingStrategy(fetch_delay=0.1)
                    eq_df = engine.backtest(wi_strategy, lookback_years=bt_years, capital=bt_cap)

                    if eq_df.empty:
                        st.warning("Not enough historical data for this strategy/period.")
                    else:
                        start_val = eq_df["portfolio_value"].iloc[0]
                        end_val   = eq_df["portfolio_value"].iloc[-1]
                        total_ret = (end_val / start_val - 1) * 100
                        n_years   = (eq_df["date"].iloc[-1] - eq_df["date"].iloc[0]).days / 365.25
                        cagr      = ((end_val / start_val) ** (1 / max(n_years, 0.01)) - 1) * 100
                        peak      = eq_df["portfolio_value"].cummax()
                        drawdown  = ((eq_df["portfolio_value"] - peak) / peak * 100)
                        max_dd    = drawdown.min()

                        bm1, bm2, bm3, bm4 = st.columns(4)
                        bm1.metric("Total Return",  f"{total_ret:+.1f}%")
                        bm2.metric("CAGR",          f"{cagr:+.1f}%")
                        bm3.metric("Max Drawdown",  f"{max_dd:.1f}%")
                        bm4.metric("Rebalances",    len(eq_df))

                        st.divider()

                        fig = go.Figure()
                        fig.add_trace(go.Scatter(
                            x=eq_df["date"], y=eq_df["portfolio_value"],
                            mode="lines", name="Portfolio",
                            line=dict(color="#00b4d8", width=2),
                            fill="tozeroy", fillcolor="rgba(0,180,216,.06)",
                        ))
                        fig.update_layout(
                            title=f"{cfg['label']} — Equity Curve",
                            xaxis_title="Date", yaxis_title="Portfolio Value (₹)",
                            template="plotly_dark",
                            paper_bgcolor="#07090f", plot_bgcolor="#0d1321",
                            height=380,
                        )
                        st.plotly_chart(fig, use_container_width=True)

                        fig_dd = go.Figure(go.Scatter(
                            x=eq_df["date"], y=drawdown,
                            mode="lines", fill="tozeroy",
                            line=dict(color="#ef5350", width=1.5),
                            fillcolor="rgba(239,83,80,.08)",
                        ))
                        fig_dd.update_layout(
                            title="Drawdown %",
                            template="plotly_dark",
                            paper_bgcolor="#07090f", plot_bgcolor="#0d1321",
                            height=220, yaxis_ticksuffix="%",
                        )
                        st.plotly_chart(fig_dd, use_container_width=True)

                except Exception as e:
                    st.error(f"Backtest error: {e}")

    with tab_guide:
        st.subheader("How Weekend Investing Momentum Works")
        st.markdown("""
**Inspired by [Alok Jain's Weekend Investing](https://weekendinvesting.com)** research on Indian market momentum strategies.

---

#### 📐 Momentum Score

Each stock is ranked by a **composite momentum score** — equal-weight average of returns over 4 windows:

| Window | Approx Trading Days |
|--------|-------------------|
| 1 Month | 21 |
| 3 Months | 63 |
| 6 Months | 126 |
| 12 Months | 252 |

---

#### ✅ Entry Rules

1. **When**: At the next market open after a rebalancing signal
2. **What**: Buy all stocks in the new top-N list that you don't already hold
3. **How much**: Equal weight — `Capital ÷ N stocks` per position
4. **No price target** — simply buy at market open; momentum carries the trade

---

#### ❌ Exit Rules

1. **Relative exit**: Sell any stock that drops OUT of the top-N ranking at the next rebalancing
2. **Absolute momentum (Mi-25/Mi-30 only)**: If a stock's **6-month return is negative**, park that slot in a liquid fund
3. **No stop-loss during the holding period** — the rebalancing is the only exit mechanism

---

#### 🔄 Strategy Comparison

| Strategy | Universe | Size | Rebalance | Abs Momentum |
|----------|----------|------|-----------|-------------|
| Mi-Top10 | Nifty 50 | 10 | Weekly | ❌ |
| Mi-EverGreen | CNX 200 | 20 | Weekly | ❌ |
| Mi-25 | Smallcap 250 | 25 | Monthly | ✅ |
| Mi-30 | CNX 500 | 30 | Monthly | ✅ |
| Mi-35 | Smallcap 250 | 35 | Weekly | ❌ |
| Mi-ST-ATH | CNX 500 | 15 | Weekly | ❌ |

---

#### ⚠️ Disclaimer

This is an educational implementation. Not affiliated with or endorsed by Weekend Investing / Alok Jain. Always paper-trade first.
""")
