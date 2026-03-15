#!/bin/bash
# Start the Subagent Dashboard web server

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Use same OpenClaw home as TUI/gateway so dashboard and tracker see the same sessions
export OPENCLAW_HOME="${OPENCLAW_HOME:-$HOME/.openclaw}"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -q -r "$(dirname "$SCRIPT_DIR")/requirements.txt"

# Start the dashboard (use port 8080 to avoid macOS AirPlay Receiver conflict)
PORT=${PORT:-8080}
echo "Starting Subagent Dashboard..."
echo "Open http://localhost:$PORT in your browser"
PORT=$PORT python3 dashboard.py
