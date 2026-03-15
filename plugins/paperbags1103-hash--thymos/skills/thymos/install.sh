#!/bin/bash
set -e

echo "🧠 Thymos Emotional Engine — Installer"
echo "======================================="
echo ""

# Check Node.js
if ! command -v node &> /dev/null; then
  echo "❌ Node.js not found. Install Node.js 18+ from https://nodejs.org"
  exit 1
fi

NODE_VERSION=$(node -e "console.log(process.version.split('.')[0].replace('v',''))")
if [ "$NODE_VERSION" -lt 18 ]; then
  echo "❌ Node.js 18+ required. Current: $(node --version)"
  exit 1
fi
echo "✅ Node.js $(node --version)"

# Check PM2
if ! command -v pm2 &> /dev/null; then
  echo "📦 Installing PM2..."
  npm install -g pm2
fi
echo "✅ PM2 $(pm2 --version)"

# Clone or update repo
INSTALL_DIR="$HOME/Documents/thymos"

if [ -d "$INSTALL_DIR" ]; then
  echo "📁 Updating existing installation at $INSTALL_DIR"
  cd "$INSTALL_DIR"
  git pull
else
  echo "📥 Cloning Thymos..."
  mkdir -p "$HOME/Documents"
  git clone https://github.com/paperbags1103-hash/thymos "$INSTALL_DIR"
  cd "$INSTALL_DIR"
fi

echo "📦 Installing dependencies..."
npm install --production

# Start daemon
echo "🚀 Starting Thymos daemon..."
pm2 start ecosystem.config.js --env production 2>/dev/null || pm2 restart thymos 2>/dev/null

pm2 save

# Wait and check
sleep 2
STATUS=$(pm2 jlist 2>/dev/null | python3 -c "
import json, sys
procs = json.load(sys.stdin)
t = next((p for p in procs if p.get('name') == 'thymos'), None)
print(t['pm2_env']['status'] if t else 'not found')
" 2>/dev/null || echo "unknown")

if [ "$STATUS" = "online" ]; then
  echo ""
  echo "✅ Thymos is running!"
  echo "   State:  curl http://localhost:7749/state"
  echo "   Prompt: curl http://localhost:7749/prompt"
  echo ""
  echo "Add to your SOUL.md or AGENTS.md:"
  echo '   Before responding, check: curl -s http://localhost:7749/prompt'
else
  echo "⚠️  Thymos status: $STATUS"
  echo "   Check logs: pm2 logs thymos"
fi
