#!/usr/bin/env bash
# Quick launcher for Pylance satisfaction tools

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

cd "$ROOT_DIR"

echo "🔮 THE RITE OF PYLANCE SATISFACTION"
echo "==================================="
echo ""
echo "1) Diagnose pillar"
echo "2) Diagnose all pillars"
echo "3) Apply fixes (dry run)"
echo "4) Apply fixes (COMMIT)"
echo "5) Switch to balanced config (RECOMMENDED)"
echo "6) Switch back to strict config"
echo "7) Show workflow docs"
echo "0) Exit"
echo ""
read -p "Choose option: " choice

case $choice in
  1)
    read -p "Enter pillar name (e.g., adyton, gematria): " pillar
    python3 scripts/covenant_scripts/satisfy_pylance.py --pillar "$pillar" --threshold 10
    ;;
  2)
    python3 scripts/covenant_scripts/satisfy_pylance.py --threshold 20
    ;;
  3)
    read -p "Enter pillar name: " pillar
    read -p "Minimum errors per file (default 20): " min_errors
    min_errors=${min_errors:-20}
    python3 scripts/covenant_scripts/apply_type_fixes.py --pillar "$pillar" --strategy both --min-errors "$min_errors"
    ;;
  4)
    read -p "Enter pillar name: " pillar
    read -p "Minimum errors per file (default 50): " min_errors
    min_errors=${min_errors:-50}
    echo "⚠️  WARNING: This will modify files!"
    read -p "Continue? (yes/no): " confirm
    if [ "$confirm" = "yes" ]; then
      python3 scripts/covenant_scripts/apply_type_fixes.py --pillar "$pillar" --strategy both --min-errors "$min_errors" --commit
    else
      echo "Aborted."
    fi
    ;;
  5)
    if [ -f pyrightconfig.json ]; then
      mv pyrightconfig.json pyrightconfig.strict.json
      echo "✅ Saved strict config as pyrightconfig.strict.json"
    fi
    if [ -f pyrightconfig.balanced.json ]; then
      cp pyrightconfig.balanced.json pyrightconfig.json
      echo "✅ Activated balanced config"
      echo ""
      echo "Testing impact on adyton pillar..."
      npx -y pyright --outputjson src/pillars/adyton 2>&1 | python3 -c "import sys, json; data=json.load(sys.stdin); print(f\"✨ Error count: {data['summary']['errorCount']}\")" || true
    else
      echo "❌ pyrightconfig.balanced.json not found"
    fi
    ;;
  6)
    if [ -f pyrightconfig.strict.json ]; then
      mv pyrightconfig.json pyrightconfig.balanced.json
      mv pyrightconfig.strict.json pyrightconfig.json
      echo "✅ Restored strict config"
    else
      echo "❌ pyrightconfig.strict.json not found"
    fi
    ;;
  7)
    cat .agent/workflows/satisfy_pylance.md
    ;;
  0)
    echo "Exiting."
    exit 0
    ;;
  *)
    echo "Invalid option."
    exit 1
    ;;
esac
