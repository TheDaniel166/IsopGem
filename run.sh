#!/bin/bash
# Launch script for IsopGem

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Activate virtual environment if it exists
if [ -d "$SCRIPT_DIR/.venv" ]; then
    source "$SCRIPT_DIR/.venv/bin/activate"
    # Make pip and python available in this session
    export PATH="$SCRIPT_DIR/.venv/bin:$PATH"
fi

# Set Qt platform
export QT_QPA_PLATFORM=xcb

# Run the application with terminal state preservation
cd "$SCRIPT_DIR/src"
stty sane 2>/dev/null  # Save terminal state
"$SCRIPT_DIR/.venv/bin/python" main.py
EXIT_CODE=$?
stty sane 2>/dev/null  # Restore terminal state
reset 2>/dev/null      # Reset terminal

exit $EXIT_CODE
