#!/bin/bash
# Root-level helper script for pip
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
"$SCRIPT_DIR/.venv/bin/python" -m pip "$@"
