#!/bin/bash
# MindGraph Server Start Script
# In cloud mode (MINDGRAPH_URL set to an https:// endpoint), this script is a no-op.

if [[ "${MINDGRAPH_URL:-}" == https://* ]]; then
  echo "☁️  Cloud mode detected (MINDGRAPH_URL=$MINDGRAPH_URL) — skipping local server start."
  exit 0
fi

SCRIPTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_ROOT="$(cd "$SCRIPTS_DIR/.." && pwd)"
DATA_DIR="$SKILL_ROOT/data"

# Auto-install binary if missing
if [ ! -x "$SCRIPTS_DIR/mindgraph-server" ]; then
  echo "🔧 mindgraph-server binary not found, downloading..."
  bash "$SCRIPTS_DIR/install.sh" || { echo "❌ Failed to install mindgraph-server"; exit 1; }
fi

mkdir -p "$DATA_DIR"

# Load config if exists
CONFIG_PATH="$DATA_DIR/mindgraph.json"
if [ -f "$CONFIG_PATH" ]; then
  TOKEN=$(python3 -c "import json; print(json.load(open('$CONFIG_PATH'))['token'])")
  PORT=$(python3 -c "import json; print(json.load(open('$CONFIG_PATH'))['port'])")
else
  # Generate defaults
  TOKEN=$(head /dev/urandom | tr -dc A-Za-z0-9 | head -c 32)
  PORT=18790
  echo "{\"token\": \"$TOKEN\", \"port\": $PORT}" > "$CONFIG_PATH"
fi

export MINDGRAPH_TOKEN=${MINDGRAPH_TOKEN:-$TOKEN}
export MINDGRAPH_PORT=${MINDGRAPH_PORT:-$PORT}
export MINDGRAPH_DB_PATH="${MINDGRAPH_DB_PATH:-$DATA_DIR/mindgraph.db}"

PID_FILE="${MINDGRAPH_PID_FILE:-/tmp/mindgraph-server.pid}"

echo "🧠 Starting MindGraph Server on port $MINDGRAPH_PORT..."
nohup "$SCRIPTS_DIR/mindgraph-server" >> /tmp/mindgraph-server-stdout.log 2>&1 &
SERVER_PID=$!
echo "$SERVER_PID" > "$PID_FILE"
echo "🧠 MindGraph Server started (PID $SERVER_PID, pidfile $PID_FILE)"
