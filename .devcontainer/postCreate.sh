#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# postCreate.sh — runs once after the dev container is created
# ─────────────────────────────────────────────────────────────────────────────
set -e

echo ""
echo "══════════════════════════════════════════════════════"
echo "  Trading System — Post-Create Setup"
echo "══════════════════════════════════════════════════════"

# ── 1. Install / refresh Python dependencies ─────────────────────────────────
echo ""
echo "📦 Installing Python dependencies…"
pip install --quiet --upgrade pip
pip install --quiet --no-cache-dir -r requirements.txt
echo "   ✅ Dependencies installed."

# ── 2. Create required directories ───────────────────────────────────────────
echo ""
echo "📁 Creating data directories…"
mkdir -p data/fundamentals_cache data/earnings_cache data/insider_cache logs cache
echo "   ✅ Directories ready."

# ── 3. Copy .env template if no .env exists ──────────────────────────────────
echo ""
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "   ⚠️  .env created from .env.example — fill in your API keys."
    else
        echo "   ⚠️  No .env found and no .env.example to copy from."
        echo "       Create .env manually with your ALPACA / TELEGRAM / EMAIL keys."
    fi
else
    echo "   ✅ .env already present."
fi

# ── 4. Quick sanity check ────────────────────────────────────────────────────
echo ""
echo "🔍 Checking key imports…"
python - <<'EOF'
imports = ["pandas", "numpy", "yfinance", "ta", "streamlit", "plotly", "pytz", "dotenv"]
failed = []
for mod in imports:
    try:
        __import__(mod)
    except ImportError:
        failed.append(mod)

if failed:
    print(f"   ⚠️  Missing: {', '.join(failed)}")
else:
    print("   ✅ All key packages importable.")
EOF

# ── 5. Done ───────────────────────────────────────────────────────────────────
echo ""
echo "══════════════════════════════════════════════════════"
echo "  ✅ Setup complete! To get started:"
echo ""
echo "  # Start the dashboard"
echo "  streamlit run dashboard.py"
echo ""
echo "  # Run morning workflow"
echo "  python daily_workflow.py morning"
echo ""
echo "  # Generate signals for all markets"
echo "  python main.py signals"
echo "══════════════════════════════════════════════════════"
echo ""
