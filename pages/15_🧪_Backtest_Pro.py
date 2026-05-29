import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from _common import *

st.set_page_config(page_title="Backtest Pro — Global Trading", page_icon="🧪", layout="wide")
apply_css()
C = get_resources()

st.title("🧪 Backtest Pro")
st.caption("Walk-forward validation + Monte Carlo simulation")
_help(
    "Tests your signal strategy on historical price data.\n"
    "- **Symbols** — paste the stocks you want to test (comma-separated)\n"
    "- **Walk-Forward** — divides history into N windows and tests out-of-sample; more realistic than a simple backtest\n"
    "- **Monte Carlo** — runs thousands of random permutations to show the distribution of possible outcomes\n"
    "- A strategy is only viable if Walk-Forward CAGR > 0 **and** Monte Carlo 5th-percentile is still positive"
)

if not HAS_BT:
    st.error("backtester module not available.")
else:
    with st.expander("⚙️ Settings", expanded=True):
        bs1, bs2, bs3 = st.columns(3)
        bt_syms_raw = bs1.text_area("Symbols (comma-sep)", "NVDA,AAPL,MSFT,GOOGL,META", height=80)
        bt_period   = bs2.selectbox("History", ["6mo","1y","2y"], index=1)
        bt_wf_n     = bs3.slider("Walk-forward windows",  2, 6,    4)
        bt_mc_n     = bs3.slider("Monte Carlo sims",    200, 2000, 1000, 200)

    bt_symbols = [s.strip().upper() for s in bt_syms_raw.split(",") if s.strip()]
    col_bt, col_wf, col_mc = st.columns(3)
    run_bt = col_bt.button("▶ Run Backtest", type="primary")
    run_wf = col_wf.button("🔀 Walk-Forward")
    run_mc = col_mc.button("🎲 Monte Carlo")

    bt = C["bt"]

    if run_bt or run_mc:
        with st.spinner("Running backtest…"):
            try:
                results = bt.run_backtest(bt_symbols, period=bt_period) if hasattr(bt, "run_backtest") else bt.run(bt_symbols, period=bt_period)
                m1,m2,m3,m4,m5,m6 = st.columns(6)
                m1.metric("Trades",       getattr(results,"total_trades","-"))
                m2.metric("Win Rate",     f"{getattr(results,'win_rate',0):.1f}%")
                m3.metric("Prof.Factor",  f"{getattr(results,'profit_factor',0):.2f}")
                m4.metric("Max DD",       f"{getattr(results,'max_drawdown',0):.1f}%")
                m5.metric("Total P&L",    f"${getattr(results,'total_pnl',0):,.0f}")
                m6.metric("Return",       f"{getattr(results,'total_return',0):.1f}%")

                if hasattr(results,"equity_curve") and results.equity_curve:
                    import plotly.graph_objects as go
                    fig_eq = go.Figure(go.Scatter(y=results.equity_curve, mode="lines",
                                                   line=dict(color="cyan", width=2)))
                    fig_eq.update_layout(title="Equity Curve", xaxis_title="Trade #",
                                          yaxis_title="Portfolio ($)", height=300, template="plotly_dark")
                    st.plotly_chart(fig_eq, use_container_width=True)

                if run_mc and hasattr(bt, "monte_carlo"):
                    with st.spinner("Monte Carlo…"):
                        try:
                            mc = bt.monte_carlo(results, simulations=bt_mc_n)
                            mc1,mc2,mc3,mc4 = st.columns(4)
                            mc1.metric("Median Return",   f"{mc.median_return:.1f}%")
                            mc2.metric("P10 / P90",       f"{mc.p10_return:.1f}% / {mc.p90_return:.1f}%")
                            mc3.metric("Prob Profit",     f"{mc.probability_of_profit:.1f}%")
                            mc4.metric("Prob Ruin >25%",  f"{mc.probability_ruin:.1f}%")
                        except Exception as mc_err:
                            st.error(f"Monte Carlo error: {mc_err}")
            except Exception as bt_err:
                st.error(f"Backtest error: {bt_err}")

    if run_wf and not run_bt:
        if not hasattr(bt, "walk_forward"):
            st.warning("walk_forward() not available on this backtester version.")
        else:
            with st.spinner("Walk-forward analysis…"):
                try:
                    wf_res = bt.walk_forward(bt_symbols, total_period=bt_period, n_windows=bt_wf_n)
                    if wf_res:
                        wf_df = pd.DataFrame([{
                            "Window":   r.window,
                            "Train":    f"{r.train_start} → {r.train_end}",
                            "Test":     f"{r.test_start} → {r.test_end}",
                            "Train WR": f"{r.train_win_rate:.1f}%",
                            "Test WR":  f"{r.test_win_rate:.1f}%",
                            "Test P&L": f"${r.test_pnl:,.0f}",
                            "Trades":   r.test_trades,
                            "Sharpe":   f"{r.sharpe:.2f}",
                        } for r in wf_res])
                        st.dataframe(wf_df, use_container_width=True, hide_index=True)

                        import plotly.express as px
                        fig_wf = px.line([{"Window":r.window,"Train WR%":r.train_win_rate,"Test WR%":r.test_win_rate} for r in wf_res],
                                         x="Window", y=["Train WR%","Test WR%"],
                                         title="Walk-Forward: Train vs Test Win Rate", markers=True)
                        st.plotly_chart(fig_wf, use_container_width=True)
                    else:
                        st.warning("No walk-forward results returned.")
                except Exception as wf_err:
                    st.error(f"Walk-forward error: {wf_err}")
