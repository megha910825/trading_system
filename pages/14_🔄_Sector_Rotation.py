import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from _common import *

st.set_page_config(page_title="Sector Rotation — Global Trading", page_icon="🔄", layout="wide")
apply_css()
C = get_resources()

st.title("🔄 Sector Rotation — Rankings by Market")
_help(
    "Ranks sector ETFs by relative momentum vs their local benchmark across 1W / 1Mo / 3Mo periods.\n"
    "- 🇺🇸 **US** — SPDR sector ETFs vs SPY\n"
    "- 🇩🇪 **Germany** — iShares STOXX Europe 600 sector ETFs vs Core DAX (EXS1.DE)\n"
    "- 🇮🇳 **India** — Nippon India sector ETFs vs NIFTYBEES\n"
    "- **Top 3 sectors** = rotate capital toward these; **Bottom 3** = underweight or avoid\n"
    "- **Composite score** = weighted 1W (20%) + 1Mo (40%) + 3Mo (40%) excess return vs benchmark\n"
    "- Recheck every Sunday and align your long bias with the leading sectors"
)

if not HAS_SR:
    st.error("sector_rotation module not available.")
else:
    tab_us, tab_de, tab_in = st.tabs(["🇺🇸 US", "🇩🇪 Germany", "🇮🇳 India"])

    def _render_sector_tab(market: str, benchmark_name: str):
        col_ref, col_btn = st.columns([5, 1])
        col_ref.caption(f"Relative strength vs **{benchmark_name}** — cached 15 min")
        with col_btn:
            if st.button("🔄 Refresh", key=f"sr_refresh_{market}"):
                st.cache_data.clear()
                st.rerun()

        @st.cache_data(ttl=900, show_spinner=f"Fetching {market} sector data…")
        def _rankings(mkt: str):
            return _sr.SectorRotation().compute_rankings(market=mkt)

        try:
            df_s = _rankings(market)
            if df_s.empty:
                st.warning(f"No sector data returned for {market}. Some ETFs may be unavailable via yfinance.")
                return

            # Filter out rows with NaN composite score (ETF data unavailable)
            df_s = df_s.dropna(subset=["composite_score"])
            if df_s.empty:
                st.warning("All sector ETFs returned NaN — possibly a data source issue. Try refreshing.")
                return

            top = df_s.iloc[0]
            bot = df_s.iloc[-1]
            leading_n = len(df_s[df_s["composite_score"] >= 0])

            m1, m2, m3 = st.columns(3)
            m1.metric("🏆 Leading",    top["sector"], f"{top['composite_score']:+.2f}% vs benchmark")
            m2.metric("⚠️ Lagging",    bot["sector"], f"{bot['composite_score']:+.2f}% vs benchmark")
            m3.metric("Outperforming", f"{leading_n} / {len(df_s)}")

            st.markdown("---")
            disp_cols = ["rank", "etf", "sector", "signal"] + [
                c for c in ["rel_1w", "rel_1mo", "rel_3mo", "composite_score", "pct_from_52wk_hi"]
                if c in df_s.columns
            ]
            st.dataframe(
                df_s[disp_cols].rename(columns={
                    "rel_1w":           "1W vs Benchmark %",
                    "rel_1mo":          "1Mo vs Benchmark %",
                    "rel_3mo":          "3Mo vs Benchmark %",
                    "composite_score":  "Score",
                    "pct_from_52wk_hi": "From 52wk Hi %",
                }),
                use_container_width=True, hide_index=True,
            )

            import plotly.express as px
            fig = px.bar(
                df_s.sort_values("composite_score"),
                x="composite_score", y="sector", orientation="h",
                color="composite_score",
                color_continuous_scale=["#EF553B", "gray", "#00CC96"],
                title=f"{market} Sector Relative Strength vs {benchmark_name}",
                labels={"composite_score": "Score (excess return %)", "sector": ""},
            )
            fig.add_vline(x=0, line_dash="dash", line_color="gray", opacity=0.5)
            fig.update_layout(showlegend=False, height=420, coloraxis_showscale=False)
            st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            st.error(f"Sector rotation error ({market}): {e}")

    with tab_us:
        _render_sector_tab("US", "SPY")
    with tab_de:
        st.caption("Uses iShares STOXX Europe 600 sector ETFs (XETRA, .DE) as Germany/Europe proxies.")
        _render_sector_tab("DE", "Core DAX ETF (EXS1.DE)")
    with tab_in:
        st.caption("Uses Nippon India ETF series (NSE, .NS). Some ETFs may have limited history.")
        _render_sector_tab("IN", "NIFTYBEES.NS")

