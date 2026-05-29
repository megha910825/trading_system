import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from _common import *

st.set_page_config(page_title="Fundamentals — Global Trading", page_icon="📈", layout="wide")
apply_css()
C = get_resources()

st.title("📈 Fundamental Analysis")
_help(
    "Pulls fundamental data (P/E, revenue growth, margins, debt) from yfinance for any ticker.\n"
    "- Enter a ticker in any format: `NVDA` (US), `SAP.DE` (Germany), `TCS.NS` (India)\n"
    "- **Fundamental Score 60+** = solid quality; **below 40** = avoid\n"
    "- Use this page *after* Signals — fundamentals confirm technical setups, not replace them"
)

if not HAS_FA:
    st.error("fundamental_analyzer module not available.")
else:
    symbol = st.text_input("Symbol (e.g. NVDA, SAP.DE, TCS.NS)", "NVDA").upper().strip()
    if st.button("Analyze"):
        with st.spinner(f"Fetching fundamentals for {symbol}…"):
            try:
                result = C["fa"].analyze(symbol)
                if result is None:
                    st.error("No data returned — check symbol format (e.g. NVDA, SAP.DE, TCS.NS)")
                else:
                    c1, c2, c3, c4 = st.columns(4)
                    pe = result.pe_ratio
                    c1.metric("P/E Ratio",      f"{pe:.1f}" if pe and pe > 0 else "N/A")
                    c2.metric("Revenue Growth", f"{result.revenue_growth*100:.1f}%")
                    c3.metric("Profit Margin",  f"{result.profit_margin*100:.1f}%")
                    c4.metric("Fund. Score",    f"{result.overall_score}/100")

                    st.divider()
                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        st.subheader("📊 Valuation")
                        st.write(f"**Forward P/E:** {result.forward_pe:.1f}" if result.forward_pe else "**Forward P/E:** N/A")
                        st.write(f"**P/B:** {result.pb_ratio:.2f}" if result.pb_ratio else "**P/B:** N/A")
                        st.write(f"**EV/EBITDA:** {result.ev_to_ebitda:.1f}" if result.ev_to_ebitda else "**EV/EBITDA:** N/A")
                        st.write(f"**Div. Yield:** {result.dividend_yield*100:.2f}%" if result.dividend_yield else "**Div. Yield:** —")
                    with col_b:
                        st.subheader("💰 Profitability")
                        st.write(f"**ROE:** {result.roe*100:.1f}%")
                        st.write(f"**ROA:** {result.roa*100:.1f}%")
                        st.write(f"**Gross Margin:** {result.gross_margin*100:.1f}%")
                        st.write(f"**FCF Margin:** {result.fcf_margin*100:.1f}%")
                    with col_c:
                        st.subheader("📈 Growth")
                        st.write(f"**Rev Growth:** {result.revenue_growth*100:.1f}%")
                        st.write(f"**Rev Growth 3Y:** {result.revenue_growth_3y*100:.1f}%")
                        st.write(f"**EPS Growth:** {result.earnings_growth*100:.1f}%")
                        st.write(f"**Debt/Equity:** {result.debt_to_equity:.2f}" if result.debt_to_equity else "**Debt/Equity:** N/A")
            except Exception as e:
                st.error(f"Error: {e}")
