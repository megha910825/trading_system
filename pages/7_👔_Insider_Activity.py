import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from _common import *

st.set_page_config(page_title="Insider Activity — Global Trading", page_icon="👔", layout="wide")
apply_css()
C = get_resources()

st.title("👔 Insider Activity")
_help(
    "Tracks SEC Form 4 insider transactions — executives buying or selling their own company's stock.\n"
    "- Enter comma-separated symbols and click **Scan**\n"
    "- **Large insider BUYs** = bullish confirmation; executives buy with conviction when they see value\n"
    "- Insider SELLs are less meaningful (often planned diversification, not a bearish view)\n"
    "- Use as a secondary confirmation signal, not a primary buy trigger"
)

if not HAS_INSIDER:
    st.error("insider_tracker module not available.")
else:
    syms_raw = st.text_area("Symbols (comma-sep)", "NVDA,AAPL,MSFT,META")
    if st.button("Scan"):
        syms = [s.strip().upper() for s in syms_raw.split(",") if s.strip()]
        with st.spinner("Fetching insider transactions…"):
            try:
                it = C["insider"]
                df = it.get_insider_activity(syms) if hasattr(it, "get_insider_activity") else (
                     it.scan(syms) if hasattr(it, "scan") else pd.DataFrame())
                if isinstance(df, pd.DataFrame) and not df.empty:
                    st.dataframe(df, use_container_width=True, hide_index=True)
                else:
                    st.info("No insider activity found.")
            except Exception as e:
                st.error(f"Error: {e}")
