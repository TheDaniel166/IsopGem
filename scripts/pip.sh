#!/bin/bash
# Helper script to run pip in the project's virtual environment
# Usage: ./pip.sh install package_name
# Usage: ./pip.sh freeze

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PARENT_DIR="$(dirname "$SCRIPT_DIR")"
"$PARENT_DIR/.venv/bin/python" -m pip "$@"
