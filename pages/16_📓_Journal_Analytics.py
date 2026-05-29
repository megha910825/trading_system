import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from _common import *

st.set_page_config(page_title="Journal Analytics — Global Trading", page_icon="📓", layout="wide")
apply_css()
C = get_resources()

st.title("📓 Journal Analytics")
st.caption("MAE/MFE distribution, regime & setup performance breakdowns")
_help(
    "Deep statistical analysis of your closed trade history (requires 30+ closed trades for meaningful results).\n"
    "- **MAE/MFE** — Max Adverse Excursion (how far trades moved against you) vs Max Favourable Excursion (best point reached). Large MAE with small MFE = stops are too tight\n"
    "- **By Regime** — shows which market conditions (BULL/BEAR/SIDEWAYS) you perform best in\n"
    "- **By Setup** — shows your strongest and weakest trade setups (PULLBACK, BREAKOUT, etc.)\n"
    "- Log and close trades via Trade Journal first — this page analyses that historical data"
)

if not HAS_JOURNAL:
    st.error("trade_journal module not available.")
else:
    try:
        journal   = C["journal"]
        closed_df = journal.get_closed_trades()

        if closed_df.empty:
            st.info("No closed trades yet. Close trades in the Trade Journal page first.")
        else:
            tab_mf, tab_reg, tab_setup = st.tabs(["📐 MAE / MFE", "🌐 By Regime", "🎯 By Setup"])

            with tab_mf:
                if "mae" in closed_df.columns and closed_df["mae"].notna().any():
                    import plotly.express as px
                    cm1, cm2 = st.columns(2)
                    with cm1:
                        st.plotly_chart(px.histogram(closed_df.dropna(subset=["mae"]), x="mae",
                            title="MAE Distribution (%)", nbins=20, color_discrete_sequence=["#EF553B"]),
                            use_container_width=True)
                    with cm2:
                        st.plotly_chart(px.histogram(closed_df.dropna(subset=["mfe"]), x="mfe",
                            title="MFE Distribution (%)", nbins=20, color_discrete_sequence=["#00CC96"]),
                            use_container_width=True)
                    jm1, jm2 = st.columns(2)
                    jm1.metric("Avg MAE", f"{closed_df['mae'].mean():.2f}%")
                    jm2.metric("Avg MFE", f"{closed_df['mfe'].mean():.2f}%")
                else:
                    st.info("No MAE/MFE data yet. Enter them when closing trades.")

            with tab_reg:
                try:
                    reg_df = journal.get_performance_by_regime()
                    if reg_df.empty:
                        st.info("Not enough data with regime labels.")
                    else:
                        st.dataframe(reg_df, use_container_width=True, hide_index=True)
                        import plotly.express as px
                        st.plotly_chart(px.bar(reg_df, x="market_regime", y="total_pnl",
                            color="win_rate", color_continuous_scale="RdYlGn",
                            title="P&L by Market Regime"), use_container_width=True)
                except Exception as e:
                    st.error(f"Regime error: {e}")

            with tab_setup:
                try:
                    setup_df = journal.get_performance_by_setup()
                    if setup_df.empty:
                        st.info("Not enough data with setup labels.")
                    else:
                        st.dataframe(setup_df, use_container_width=True, hide_index=True)
                        import plotly.express as px
                        st.plotly_chart(px.bar(setup_df, x="setup_type", y="total_pnl",
                            color="win_rate", color_continuous_scale="RdYlGn",
                            title="P&L by Setup Type"), use_container_width=True)
                except Exception as e:
                    st.error(f"Setup error: {e}")

    except Exception as e:
        st.error(f"Journal analytics error: {e}")
