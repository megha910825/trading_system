import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from _common import *

st.set_page_config(page_title="Combined Analysis — Global Trading", page_icon="🔀", layout="wide")
apply_css()
C = get_resources()

st.title("🔀 Combined Technical + Fundamental Analysis")
_help(
    "Merges the technical signal score with the fundamental quality score into one composite rating.\n"
    "- Enter any ticker and click **Analyse**\n"
    "- **Score 70+** = high-conviction trade candidate; **50–70** = watchlist only\n"
    "- Use this to reduce false positives from the Signals page — only trade stocks with good fundamentals too"
)

if not HAS_CA:
    st.error("combined_analyzer module not available.")
else:
    symbol = st.text_input("Symbol", "AAPL").upper().strip()
    if st.button("Analyse"):
        with st.spinner(f"Analysing {symbol}…"):
            try:
                result = C["ca"].analyze(symbol)
                if result is not None:
                    qcolors = {"A+": ("#00ff9d","#003d28"), "A": ("#00cc96","#002e22"),
                               "B": ("#fbb703","#2e2300"), "C": ("#fb923c","#2e1500"), "D": ("#ef5350","#2e0808")}
                    qfg, qbg = qcolors.get(result.trade_quality, ("#94a3b8","#1e293b"))
                    sig_badge_cls = {"STRONG BUY":"badge-strong","BUY":"badge-buy",
                                     "BUY (Weak Fundamentals)":"badge-buy",
                                     "WAIT (Good Company, Bad Timing)":"badge-watch",
                                     "CAUTION (Poor Fundamentals)":"badge-watch",
                                     "HOLD":"badge-hold"}.get(result.combined_signal,"badge-hold")
                    st.markdown(f"""
<div style="background:linear-gradient(135deg,#0d1321,#111827);border:1px solid rgba(0,180,216,.2);
            border-radius:14px;padding:1.2rem 1.5rem;margin-bottom:1.2rem;">
  <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:.5rem;">
    <div>
      <div style="font-size:1.5rem;font-weight:800;color:#f1f5f9;letter-spacing:-.02em;">
        {result.name} &nbsp;<span style="color:#4b5e7a;font-size:1rem;font-weight:500;">({result.symbol})</span>
      </div>
      <div style="font-size:.8rem;color:#64748b;margin-top:.2rem;">{result.sector}</div>
    </div>
    <div style="display:flex;align-items:center;gap:.75rem;">
      <span class="badge {sig_badge_cls}">{result.combined_signal}</span>
      <span style="background:{qbg};color:{qfg};border:1px solid {qfg}44;border-radius:10px;
                   padding:4px 14px;font-size:.8rem;font-weight:800;letter-spacing:.05em;">
        {result.trade_quality}
      </span>
    </div>
  </div>
  <div style="margin-top:.8rem;font-size:.95rem;color:#94a3b8;">{result.recommendation}</div>
</div>
""", unsafe_allow_html=True)

                    def _gauge_bar(score, color="#00b4d8"):
                        pct = min(max(score, 0), 100)
                        return (f'<div style="background:rgba(255,255,255,.05);border-radius:4px;height:6px;margin-top:.4rem;">'
                                f'<div style="width:{pct}%;height:100%;border-radius:4px;'
                                f'background:linear-gradient(90deg,{color}99,{color});"></div></div>')

                    def _score_card(label, score, color="#00b4d8"):
                        return (f'<div style="background:linear-gradient(135deg,#0d1321,#111827);'
                                f'border:1px solid rgba(0,180,216,.15);border-radius:12px;padding:.9rem 1rem;">'
                                f'<div style="font-size:.68rem;font-weight:700;text-transform:uppercase;'
                                f'letter-spacing:.09em;color:#4b5e7a;">{label}</div>'
                                f'<div style="font-size:1.6rem;font-weight:800;font-family:JetBrains Mono,monospace;'
                                f'color:{color};margin:.15rem 0;">{score}<span style="font-size:.85rem;color:#4b5e7a;">/100</span></div>'
                                f'{_gauge_bar(score, color)}</div>')

                    tech_color  = "#00cc96" if result.technical_score  >= 60 else ("#fbb703" if result.technical_score  >= 40 else "#ef5350")
                    fund_color  = "#00cc96" if result.fundamental_score >= 60 else ("#fbb703" if result.fundamental_score >= 40 else "#ef5350")
                    comb_color  = "#00cc96" if result.combined_score    >= 60 else ("#fbb703" if result.combined_score    >= 40 else "#ef5350")

                    gc1, gc2, gc3 = st.columns(3)
                    gc1.markdown(_score_card("Technical Score",    result.technical_score,   tech_color), unsafe_allow_html=True)
                    gc2.markdown(_score_card("Fundamental Score",  result.fundamental_score, fund_color), unsafe_allow_html=True)
                    gc3.markdown(_score_card("Combined Score",     result.combined_score,    comb_color), unsafe_allow_html=True)

                    st.divider()
                    col_left, col_right = st.columns(2)

                    with col_left:
                        st.subheader("📈 Trade Setup")
                        risk = result.entry_price - result.stop_loss
                        rr1 = (result.target_1 - result.entry_price) / risk if risk > 0 else 0
                        rr2 = (result.target_2 - result.entry_price) / risk if risk > 0 else 0
                        st.markdown(f"""
| Field | Value |
|---|---|
| **Signal** | {result.technical_signal} |
| **Setup** | {result.setup_type} |
| **Trend** | {result.trend} |
| **Current Price** | ${result.current_price:,.2f} |
| **Entry Price** | ${result.entry_price:,.2f} |
| **Stop Loss** | ${result.stop_loss:,.2f} ({((result.stop_loss - result.entry_price) / result.entry_price * 100):.1f}%) |
| **Target 1** | ${result.target_1:,.2f} ({((result.target_1 - result.entry_price) / result.entry_price * 100):.1f}%) |
| **Target 2** | ${result.target_2:,.2f} ({((result.target_2 - result.entry_price) / result.entry_price * 100):.1f}%) |
| **R:R (T1)** | {rr1:.2f} |
| **R:R (T2)** | {rr2:.2f} |
| **RSI** | {result.rsi:.1f} |
""")

                    with col_right:
                        st.subheader("🏢 Fundamental Breakdown")
                        st.markdown(f"""
| Metric | Score / Value |
|---|---|
| **Overall Fundamental** | {result.fundamental_score}/100 |
| **Valuation** | {result.valuation_score}/100 |
| **Profitability** | {result.profitability_score}/100 |
| **Growth** | {result.growth_score}/100 |
| **Financial Health** | {result.health_score}/100 |
| **P/E Ratio** | {result.pe_ratio:.1f}x |
| **ROE** | {result.roe * 100:.1f}% |
| **Revenue Growth** | {result.revenue_growth:.1f}% |
| **Debt / Equity** | {result.debt_to_equity:.2f}x |
""")

                    st.divider()
                    st.caption(f"Combined Signal: **{result.combined_signal}**")
                else:
                    st.error("No result returned — check symbol or data availability.")
            except Exception as e:
                st.error(f"Error: {e}")
