import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from _common import *

st.set_page_config(page_title="Performance — Global Trading", page_icon="📊", layout="wide")
apply_css()
C = get_resources()

st.title("📊 Performance Tracker")
_help(
    "Monthly P&L summary across all closed trades in your journal.\n"
    "- **Month P&L** — running total for the current calendar month\n"
    "- **Target** — monthly dollar target set in `config.py` (`MONTHLY_TARGET`)\n"
    "- Use the **Days slider** to change the lookback window\n"
    "- Win rate below 45% or Profit Factor below 1.3 = review your strategy or reduce position sizes"
)

if HAS_PT:
    try:
        progress = C["pt"].get_monthly_progress()
        p1, p2, p3, p4 = st.columns(4)
        p1.metric("Month P&L",  f"${progress.get('current_pnl',0):+,.2f}")
        p2.metric("Target",     f"${progress.get('target',0):,.2f}")
        p3.metric("Progress",   f"{progress.get('progress_pct',0):.1f}%")
        p4.metric("Days Left",  progress.get('days_left','?'))
    except Exception as e:
        st.warning(f"Performance tracker: {e}")

if HAS_JOURNAL:
    st.markdown("---")
    st.subheader("Trade Statistics")
    days_filter = st.slider("Days to include", 7, 365, 30)
    try:
        stats = C["journal"].get_stats(days=days_filter)
        if not stats.get("total_trades"):
            st.info(f"No closed trades in the last {days_filter} days.")
        else:
            s1, s2, s3, s4, s5 = st.columns(5)
            s1.metric("Trades",        stats["total_trades"])
            s2.metric("Win Rate",      f"{stats['win_rate']:.1f}%")
            s3.metric("Profit Factor", f"{stats['profit_factor']:.2f}")
            s4.metric("Total P&L",     f"${stats['total_pnl']:+,.2f}")
            s5.metric("Avg R",         f"{stats['avg_r']:+.2f}R")
    except Exception as e:
        st.error(f"Stats error: {e}")

    # ── Equity Curve ─────────────────────────────────────────────────────
    st.markdown("---")
    st.subheader("Equity Curve")
    try:
        import plotly.graph_objects as go
        closed_df = C["journal"].get_closed_trades()
        if closed_df.empty or "pnl" not in closed_df.columns:
            st.info("No closed trades yet — equity curve will appear after your first closed trade.")
        else:
            # Sort chronologically and build cumulative P&L
            eq = closed_df.copy()
            eq["exit_date"] = pd.to_datetime(eq["exit_date"])
            eq = eq.sort_values("exit_date")
            eq["cumulative_pnl"] = eq["pnl"].cumsum()
            eq["trade_num"] = range(1, len(eq) + 1)

            # Running max for drawdown shading
            peak = eq["cumulative_pnl"].cummax()
            drawdown = eq["cumulative_pnl"] - peak

            fig = go.Figure()

            # Drawdown fill
            fig.add_trace(go.Scatter(
                x=eq["trade_num"], y=drawdown,
                fill="tozeroy", fillcolor="rgba(239,83,80,.10)",
                line=dict(color="rgba(239,83,80,.4)", width=1),
                name="Drawdown", yaxis="y2",
            ))

            # Equity line
            fig.add_trace(go.Scatter(
                x=eq["trade_num"], y=eq["cumulative_pnl"],
                mode="lines+markers",
                line=dict(color="#0077b6", width=2.5),
                marker=dict(
                    color=["#10b981" if p > 0 else "#ef4444" for p in eq["pnl"]],
                    size=7, line=dict(color="#ffffff", width=1),
                ),
                name="Cumulative P&L",
                hovertemplate=(
                    "<b>Trade #%{x}</b><br>"
                    "Cumulative P&L: $%{y:+,.2f}<br>"
                    "<extra></extra>"
                ),
            ))

            # Zero line
            fig.add_hline(y=0, line_dash="dash", line_color="#94a3b8", line_width=1)

            fig.update_layout(
                height=380,
                xaxis=dict(title="Trade #", gridcolor="#e2e8f0"),
                yaxis=dict(title="Cumulative P&L ($)", gridcolor="#e2e8f0", tickprefix="$"),
                yaxis2=dict(overlaying="y", side="right", showgrid=False,
                            title="Drawdown ($)", tickprefix="$"),
                paper_bgcolor="#ffffff", plot_bgcolor="#f8fafc",
                legend=dict(orientation="h", y=1.08),
                margin=dict(t=20, b=40, l=60, r=60),
                hovermode="x unified",
            )
            st.plotly_chart(fig, use_container_width=True)

            # Summary row below chart
            best_trade  = eq["pnl"].max()
            worst_trade = eq["pnl"].min()
            max_dd      = drawdown.min()
            cr1, cr2, cr3 = st.columns(3)
            cr1.metric("Best Trade",   f"${best_trade:+,.2f}")
            cr2.metric("Worst Trade",  f"${worst_trade:+,.2f}")
            cr3.metric("Max Drawdown", f"${max_dd:,.2f}")
    except Exception as e:
        st.error(f"Equity curve error: {e}")
