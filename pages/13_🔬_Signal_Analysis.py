import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from _common import *

st.set_page_config(page_title="Signal Analysis — Global Trading", page_icon="🔬", layout="wide")
apply_css()
C = get_resources()

st.title("🔬 Signal Analysis — Score Distribution")
_help(
    "Charts the distribution of signal scores across the full universe to gauge market breadth.\n"
    "- Select markets and click **Analyse Signals** to generate score histograms\n"
    "- **Most scores clustered below 50** = weak broad market; reduce position sizes or stay out\n"
    "- **Cluster above 65** = strong breadth; more aggressive entries are justified\n"
    "- Use this weekly to calibrate your minimum score threshold on the Signals page"
)

if not HAS_GSG:
    st.error("GlobalSignalGenerator not available.")
else:
    sa_markets = st.multiselect("Markets", ["US","DE","IN"], default=["US"], key="sa_mkts")
    if st.button("Analyse Signals"):
        with st.spinner("Generating signals…"):
            try:
                import plotly.express as px
                raw = C["gen"].generate_signals(markets=sa_markets)
                all_sigs = [s for mkt_sigs in raw.values() for s in mkt_sigs]
                if all_sigs:
                    df = pd.DataFrame(all_sigs)
                    fig = px.histogram(df, x="signal_score", color="signal_status", nbins=20,
                                       title="Signal Score Distribution",
                                       color_discrete_map={"STRONG BUY":"green","BUY":"lime",
                                                           "WATCH":"orange","AVOID":"red"})
                    st.plotly_chart(fig, use_container_width=True)
                    if "sector" in df.columns:
                        fig2 = px.bar(
                            df.groupby("sector")["signal_score"].mean().reset_index().sort_values("signal_score",ascending=False),
                            x="sector", y="signal_score", title="Avg Score by Sector")
                        st.plotly_chart(fig2, use_container_width=True)
                else:
                    st.info("No signals generated.")
            except Exception as e:
                st.error(f"Error: {e}")
