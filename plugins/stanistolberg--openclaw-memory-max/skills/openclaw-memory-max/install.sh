#!/bin/bash
set -e

echo "Installing openclaw-memory-max v3.0.0..."

# 1. Ensure OpenClaw is installed
if ! command -v openclaw &> /dev/null; then
    echo "Error: 'openclaw' CLI not found. Install OpenClaw first."
    exit 1
fi

# 2. Clone or update
EXT_DIR="${HOME}/.openclaw/extensions/openclaw-memory-max"

if [ -d "$EXT_DIR/.git" ]; then
    echo "Existing installation found — pulling latest..."
    cd "$EXT_DIR"
    git pull origin main
else
    echo "Cloning from GitHub..."
    mkdir -p "$(dirname "$EXT_DIR")"
    git clone https://github.com/stanistolberg/openclaw-memory-max "$EXT_DIR"
    cd "$EXT_DIR"
fi

# 3. Install dependencies and build
echo "Installing dependencies..."
npm install --no-fund --no-audit
echo "Building TypeScript..."
npm run build

# 4. Enable the plugin (takes the exclusive memory slot)
echo "Enabling plugin..."
openclaw plugins enable openclaw-memory-max 2>/dev/null || true

echo ""
echo "openclaw-memory-max v3.0.0 installed successfully!"
echo "Restart the gateway to load: systemctl --user restart openclaw-gateway"
