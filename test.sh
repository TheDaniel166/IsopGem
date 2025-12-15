#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PY="$SCRIPT_DIR/.venv/bin/python"

usage() {
  cat <<'EOF'
Usage:
  ./test.sh                  Run full test suite (concise output)
  ./test.sh -q               Quiet
  ./test.sh -v               Verbose
  ./test.sh <pytest args...> Pass any pytest arguments through

Notes:
  - This script does NOT `source` the venv, so it won't mutate your shell.
  - It always runs pytest through the repo venv interpreter.
EOF
}

if [ ! -x "$PY" ]; then
  echo "Error: expected venv python at: $PY" >&2
  echo "Create it with: python3 -m venv .venv && ./.venv/bin/pip install -r requirements.txt" >&2
  exit 1
fi

if [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ]; then
  usage
  exit 0
fi

cd "$SCRIPT_DIR"

# Unbuffered output helps avoid terminals that appear to hang.
export PYTHONUNBUFFERED=1

# Default to concise output unless the caller provided args.
if [ "$#" -eq 0 ]; then
  "$PY" -m pytest -q
else
  "$PY" -m pytest "$@"
fi
