import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from _common import *

st.set_page_config(page_title="Market Regime — Global Trading", page_icon="📊", layout="wide")
apply_css()
C = get_resources()

st.title("📊 Market Regime Analysis")
_help(
    "Determines whether market conditions favour swing trading.\n"
    "- ✅ **TRADE** — conditions are favourable; proceed with new entries\n"
    "- 🚫 **PAUSE** — elevated risk; hold existing positions only, no new buys\n"
    "- **Confidence %** — above 70% = clear signal; below 60% = treat as neutral\n"
    "- Refresh every morning before placing orders"
)

if not HAS_REGIME:
    st.error("market_regime module not available.")
else:
    if st.button("🔄 Refresh", type="primary"):
        st.cache_data.clear()

    @st.cache_data(ttl=600, show_spinner="Analysing regime…")
    def _get_regime():
        return _mr.MarketRegimeFilter().analyze()

    try:
        cond = _get_regime()
        regime_obj = _mr.MarketRegimeFilter()
        tradeable, reason, confidence = regime_obj.should_trade()

        gc, cc = st.columns([2, 1])
        if tradeable:
            gc.success(f"✅ **TRADE** — {reason}")
        else:
            gc.error(f"🚫 **PAUSE TRADING** — {reason}")
        cc.metric("Confidence", f"{confidence:.0f}%")

        st.markdown("---")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("SPY Price",     f"${getattr(cond,'spy_price',0):.2f}")
        m2.metric("VIX",           f"{getattr(cond,'vix',0):.1f}")
        m3.metric("Above 50 EMA",  "✅" if cond.above_ema50  else "❌")
        m4.metric("Above 200 EMA", "✅" if cond.above_ema200 else "❌")
    except Exception as e:
        st.error(f"Regime error: {e}")
