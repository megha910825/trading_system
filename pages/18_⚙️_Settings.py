import sys, os, re as _re
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from _common import *

st.set_page_config(page_title="Settings — Global Trading", page_icon="⚙️", layout="wide")
apply_css()

st.title("⚙️ System Settings")
_help(
    "Edit any value below and click **Save Changes** — the new values are written to `config.py` and take effect immediately on the next action.\n"
    "- **Account Size** and **Risk/Trade %** drive every position size calculation across all pages\n"
    "- **API keys** are read from environment variables (`.env` file) and cannot be changed here — edit `.env` then run `docker compose restart`\n"
    "- Changes persist across container restarts because `config.py` is part of the image; rebuild with `docker compose build` after major changes"
)

cfg_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.py")

def _save_config(account, monthly_target, risk_per_trade, max_positions, daily_loss_limit,
                 min_market_cap, min_avg_volume, min_atr, max_atr,
                 stop_loss_atr, target1_atr, target2_atr, max_hold_days):
    with open(cfg_path, "r") as f:
        lines = f.readlines()
    replacements = {
        "ACCOUNT_SIZE":     str(int(account)),
        "MONTHLY_TARGET":   f"{monthly_target/100:.4f}",
        "RISK_PER_TRADE":   f"{risk_per_trade/100:.4f}",
        "MAX_POSITIONS":    str(int(max_positions)),
        "DAILY_LOSS_LIMIT": f"{daily_loss_limit/100:.4f}",
    }
    new_lines = []
    for line in lines:
        written = False
        for key, val in replacements.items():
            if line.startswith(key + " =") or line.startswith(key + "="):
                new_lines.append(f"{key} = {val}\n")
                written = True
                break
        if not written:
            new_lines.append(line)
    text = "".join(new_lines)

    def _patch(txt, key, val):
        return _re.sub(rf'("{key}"\s*:\s*)[^\n,}}]+', lambda m: m.group(1) + str(val), txt)

    text = _patch(text, "min_market_cap",    int(min_market_cap * 1e9))
    text = _patch(text, "min_avg_volume",    int(min_avg_volume * 1e6))
    text = _patch(text, "min_atr_pct",       round(min_atr, 2))
    text = _patch(text, "max_atr_pct",       round(max_atr, 2))
    text = _patch(text, "stop_loss_atr_mult",round(stop_loss_atr, 2))
    text = _patch(text, "target_1_atr_mult", round(target1_atr, 2))
    text = _patch(text, "target_2_atr_mult", round(target2_atr, 2))
    text = _patch(text, "max_hold_days",     int(max_hold_days))
    with open(cfg_path, "w") as f:
        f.write(text)

sc = getattr(config, "SCREENING_CRITERIA", {})
er = getattr(config, "EXIT_RULES", {})

st.subheader("Account & Risk")
ar1, ar2, ar3, ar4, ar5 = st.columns(5)
i_account    = ar1.number_input("Account Size ($)",      value=float(config.ACCOUNT_SIZE),                           step=1000.0, format="%.0f")
i_monthly    = ar2.number_input("Monthly Target (%)",    value=round(config.MONTHLY_TARGET * 100, 2),                 step=0.5,    format="%.2f")
i_risk       = ar3.number_input("Risk / Trade (%)",      value=round(config.RISK_PER_TRADE * 100, 2),                 step=0.1,    format="%.2f")
i_max_pos    = ar4.number_input("Max Positions",         value=float(config.MAX_POSITIONS),                           step=1.0,    format="%.0f")
i_daily_loss = ar5.number_input("Daily Loss Limit (%)",  value=round(getattr(config,"DAILY_LOSS_LIMIT",0.02)*100, 2), step=0.1,    format="%.2f")

st.markdown("---")
st.subheader("Screening Criteria")
sc1, sc2, sc3, sc4 = st.columns(4)
i_mktcap  = sc1.number_input("Min Market Cap ($B)",  value=round(sc.get("min_market_cap",5e9)/1e9, 1), step=0.5, format="%.1f")
i_avgvol  = sc2.number_input("Min Avg Volume ($M)",  value=round(sc.get("min_avg_volume",2e6)/1e6, 1), step=0.5, format="%.1f")
i_min_atr = sc3.number_input("Min ATR %",            value=float(sc.get("min_atr_pct", 2.5)),           step=0.1, format="%.1f")
i_max_atr = sc4.number_input("Max ATR %",            value=float(sc.get("max_atr_pct", 8.0)),           step=0.1, format="%.1f")

st.markdown("---")
st.subheader("Exit Rules")
ex1, ex2, ex3, ex4 = st.columns(4)
i_sl_atr    = ex1.number_input("Stop Loss (× ATR)",  value=float(er.get("stop_loss_atr_mult", 1.75)), step=0.05, format="%.2f")
i_t1_atr    = ex2.number_input("Target 1 (× ATR)",   value=float(er.get("target_1_atr_mult",  3.5)),  step=0.05, format="%.2f")
i_t2_atr    = ex3.number_input("Target 2 (× ATR)",   value=float(er.get("target_2_atr_mult",  4.0)),  step=0.05, format="%.2f")
i_hold_days = ex4.number_input("Max Hold Days",       value=float(er.get("max_hold_days",       10)),  step=1.0,  format="%.0f")

st.markdown("---")
sv_col, _ = st.columns([1, 4])
if sv_col.button("💾  Save Changes", type="primary", use_container_width=True):
    # ── Validation ──────────────────────────────────────────────────────
    errors = []
    if i_account < 1000:
        errors.append("Account size must be at least $1,000.")
    if not (0.5 <= i_monthly <= 20):
        errors.append("Monthly target must be between 0.5% and 20%.")
    if not (0.1 <= i_risk <= 5):
        errors.append("Risk per trade must be between 0.1% and 5%.")
    if not (1 <= i_max_pos <= 50):
        errors.append("Max positions must be between 1 and 50.")
    if not (0.1 <= i_daily_loss <= 10):
        errors.append("Daily loss limit must be between 0.1% and 10%.")
    if i_min_atr >= i_max_atr:
        errors.append("Min ATR % must be less than Max ATR %.")
    if i_sl_atr <= 0:
        errors.append("Stop loss ATR multiplier must be > 0.")
    if i_t1_atr <= i_sl_atr:
        errors.append("Target 1 ATR multiplier must be greater than Stop Loss multiplier.")
    if i_t2_atr <= i_t1_atr:
        errors.append("Target 2 ATR multiplier must be greater than Target 1 multiplier.")
    if i_hold_days < 1:
        errors.append("Max hold days must be at least 1.")

    if errors:
        for err in errors:
            st.error(f"⚠️ {err}")
    else:
        try:
            _save_config(
                i_account, i_monthly, i_risk, i_max_pos, i_daily_loss,
                i_mktcap, i_avgvol, i_min_atr, i_max_atr,
                i_sl_atr, i_t1_atr, i_t2_atr, i_hold_days,
            )
            config.ACCOUNT_SIZE     = int(i_account)
            config.MONTHLY_TARGET   = round(i_monthly / 100, 6)
            config.RISK_PER_TRADE   = round(i_risk / 100, 6)
            config.MAX_POSITIONS    = int(i_max_pos)
            config.DAILY_LOSS_LIMIT = round(i_daily_loss / 100, 6)
            if hasattr(config, "SCREENING_CRITERIA"):
                config.SCREENING_CRITERIA.update({
                    "min_market_cap": int(i_mktcap * 1e9),
                    "min_avg_volume": int(i_avgvol * 1e6),
                    "min_atr_pct":    round(i_min_atr, 2),
                    "max_atr_pct":    round(i_max_atr, 2),
                })
            if hasattr(config, "EXIT_RULES"):
                config.EXIT_RULES.update({
                    "stop_loss_atr_mult": round(i_sl_atr, 2),
                    "target_1_atr_mult":  round(i_t1_atr, 2),
                    "target_2_atr_mult":  round(i_t2_atr, 2),
                    "max_hold_days":      int(i_hold_days),
                })
            st.success("✅ Settings saved — changes are active immediately.")
        except Exception as _e:
            st.error(f"Failed to save: {_e}")

st.markdown("---")
st.subheader("API Status")
st.caption("API keys are read from the `.env` file and cannot be edited here. Restart the container after changing `.env`.")
a1, a2, a3 = st.columns(3)
a1.metric("Alpaca",     "✅ Set" if getattr(config,"ALPACA_API_KEY","")     else "❌ Not set")
a2.metric("Telegram",   "✅ Set" if getattr(config,"TELEGRAM_BOT_TOKEN","") else "❌ Not set")
a3.metric("Polygon.io", "✅ Set" if os.environ.get("POLYGON_API_KEY")       else "❌ Optional")

# ── Scheduler Status ──────────────────────────────────────────────────────────
st.markdown("---")
st.subheader("⏰ Scheduler Status")
st.caption("Tracks whether the automated morning signal and universe update jobs ran successfully.")

_sched_log = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs", "scheduler.log")

col_sch1, col_sch2 = st.columns([3, 1])
with col_sch2:
    if st.button("🔄 Refresh", key="sched_refresh"):
        st.rerun()

if not os.path.exists(_sched_log):
    st.info(
        "No scheduler log found yet. The log appears at `logs/scheduler.log` once the scheduler runs.\n\n"
        "Start it with: `python automation/scheduler.py`"
    )
else:
    try:
        with open(_sched_log, "r") as _f:
            _lines = _f.readlines()

        # Parse last entry for each job type
        _last = {"signals": None, "universe": None, "error": None}
        for _ln in reversed(_lines):
            _ln = _ln.strip()
            if not _ln:
                continue
            if "signal" in _ln.lower() and _last["signals"] is None:
                _last["signals"] = _ln
            elif "universe" in _ln.lower() and _last["universe"] is None:
                _last["universe"] = _ln
            elif "error" in _ln.lower() and _last["error"] is None:
                _last["error"] = _ln
            if all(_last.values()):
                break

        sc1, sc2, sc3 = st.columns(3)
        sc1.metric(
            "Last Signal Run",
            "✅ OK" if _last["signals"] and "error" not in _last["signals"].lower() else "⚠️ See log",
            _last["signals"][:60] if _last["signals"] else "No record",
        )
        sc2.metric(
            "Last Universe Update",
            "✅ OK" if _last["universe"] and "error" not in _last["universe"].lower() else "⚠️ See log",
            _last["universe"][:60] if _last["universe"] else "No record",
        )
        sc3.metric(
            "Last Error",
            "❌ Error" if _last["error"] else "✅ None",
            _last["error"][:60] if _last["error"] else "Clean",
        )

        with st.expander("📄 Full log (last 50 lines)"):
            st.code("".join(_lines[-50:]), language=None)

    except Exception as _se:
        st.error(f"Could not read scheduler log: {_se}")

