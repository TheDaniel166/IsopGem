#!/bin/bash
# IsopGem Development Environment Setup
# Run this ONCE to configure your shell for automatic venv activation
# Usage: source setup_env.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PATH="$SCRIPT_DIR/.venv"

# Check if venv exists
if [ ! -d "$VENV_PATH" ]; then
    echo "❌ Virtual environment not found at $VENV_PATH"
    echo "   Please create it first with: python3 -m venv .venv"
    return 1 2>/dev/null || exit 1
fi

# Activate the virtual environment
source "$VENV_PATH/bin/activate"

# Confirm activation
echo "✅ IsopGem environment activated!"
echo "   Python: $(which python)"
echo "   Pip:    $(which pip)"
echo ""
echo "Quick commands:"
echo "   ./run.sh          - Launch IsopGem"
echo "   pip install X     - Install packages (pip is now available)"
echo "   python script.py  - Run Python scripts"
echo "   deactivate        - Exit the virtual environment"
