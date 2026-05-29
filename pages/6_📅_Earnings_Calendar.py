import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from _common import *

st.set_page_config(page_title="Earnings Calendar — Global Trading", page_icon="📅", layout="wide")
apply_css()
C = get_resources()

st.title("📅 Earnings Calendar")
_help(
    "Shows upcoming earnings announcements — **never hold positions through earnings** (gap risk can exceed your stop).\n"
    "- Set *Days ahead* to 7 to catch all near-term risk events\n"
    "- Check this before entering any new trade — if earnings are within 5 days, wait until after\n"
    "- Cross-reference with the Signals page: avoid setups where earnings fall before your target is hit"
)

if not HAS_EARN:
    st.error("earnings_calendar module not available.")
else:
    days_ahead = st.slider("Days ahead", 3, 30, 14)
    if st.button("Load Earnings"):
        with st.spinner("Fetching…"):
            try:
                ec = C["earn"]
                df = ec.get_upcoming_earnings(days=days_ahead) if hasattr(ec, "get_upcoming_earnings") else (
                     ec.get_calendar() if hasattr(ec, "get_calendar") else pd.DataFrame())
                if isinstance(df, pd.DataFrame) and not df.empty:
                    st.dataframe(df, use_container_width=True, hide_index=True)
                else:
                    st.info("No earnings data returned.")
            except Exception as e:
                st.error(f"Error: {e}")
