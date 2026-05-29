import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from _common import *

st.set_page_config(page_title="Stock Screener — Global Trading", page_icon="🔍", layout="wide")
apply_css()
C = get_resources()

st.title("🔍 Stock Screener")
_help(
    "Filters the full universe by signal score threshold and market.\n"
    "- Select markets and set **Max stocks per market** to control scan size\n"
    "- **Minimum score 60** = actionable setups; **80+** = high-conviction only\n"
    "- Click **Run Screener** — results are a shortlist for deeper analysis via Combined Analysis\n"
    "- This is a filter tool, not a buy list — always verify with Market Regime before trading"
)

sc1, sc2 = st.columns(2)
scr_markets = sc1.multiselect("Markets", ["US","DE","IN"], default=["US"], key="scr_mkts")
max_per_mkt = sc2.slider("Max stocks per market", 10, 100, 50, 10)
min_score   = st.slider("Minimum signal score", 0, 100, 60)

if st.button("Run Screener"):
    with st.spinner("Screening…"):
        try:
            if HAS_MC:
                from market_config import get_all_stocks
                universe = get_all_stocks(scr_markets)
                syms = []
                for mkt in scr_markets:
                    syms.extend(universe.get(mkt, [])[:max_per_mkt])
            else:
                syms = config.STOCK_UNIVERSE

            if HAS_SS:
                results = C["screener"].screen_stocks(syms) if hasattr(C["screener"], "screen_stocks") else pd.DataFrame()
                if isinstance(results, pd.DataFrame) and not results.empty:
                    score_col = "signal_score" if "signal_score" in results.columns else ("score" if "score" in results.columns else None)
                    filtered = results[results[score_col] >= min_score] if score_col else results
                    st.success(f"{len(filtered)} stocks passed (from {len(syms)} scanned)")
                    st.dataframe(filtered, use_container_width=True, hide_index=True)
                else:
                    st.info("Screener returned no results.")
            else:
                st.warning("StockScreener not available. Universe list:")
                st.write(syms)
        except Exception as e:
            st.error(f"Screener error: {e}")
