#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# entrypoint.sh — selects the run mode based on CMD / first argument
#
# Usage:
#   dashboard   → streamlit dashboard (default)
#   scheduler   → background scheduler
#   scanner     → one-shot stock scan
#   signals     → one-shot signal generation
#   update      → one-shot universe update
#   shell       → interactive bash (for debugging)
# ─────────────────────────────────────────────────────────────────────────────
set -e

MODE="${1:-dashboard}"

case "$MODE" in
  dashboard)
    echo "[entrypoint] Starting Streamlit dashboard on :8501 …"
    exec python -m streamlit run dashboard.py \
      --server.port=8501 \
      --server.address=0.0.0.0 \
      --server.headless=true \
      --browser.gatherUsageStats=false
    ;;

  scheduler)
    echo "[entrypoint] Starting scheduler …"
    exec python scheduler.py
    ;;

  scanner)
    echo "[entrypoint] Running stock scanner …"
    exec python main.py scanner
    ;;

  signals)
    echo "[entrypoint] Generating signals …"
    exec python main.py signals
    ;;

  update)
    echo "[entrypoint] Running universe update …"
    exec python main.py quick-update
    ;;

  shell)
    exec bash
    ;;

  *)
    echo "[entrypoint] Unknown mode: $MODE"
    echo "Valid modes: dashboard | scheduler | scanner | signals | update | shell"
    exit 1
    ;;
esac
