#!/usr/bin/env bash
# ClawMemory — Install CLI & Miner
# All source code is bundled inside this skill (no external download needed)
set -e

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
INSTALL_BASE="${CLAWMEMORY_DIR:-$HOME/.clawmemory}"
CLI_DIR="$INSTALL_BASE/memory-client"
MINER_DIR="$INSTALL_BASE/miner"

echo "=== ClawMemory Installer ==="
echo "Install path: $INSTALL_BASE"

# 1. Copy bundled source
echo "[1] Copying source files..."
mkdir -p "$CLI_DIR/src" "$CLI_DIR/bin" "$MINER_DIR"
cp -r "$SKILL_DIR/assets/memory-client/src/"* "$CLI_DIR/src/"
cp    "$SKILL_DIR/assets/memory-client/bin/cli.js" "$CLI_DIR/bin/"
cp    "$SKILL_DIR/assets/memory-client/package.json" "$CLI_DIR/"
cp    "$SKILL_DIR/assets/miner/"*.js "$MINER_DIR/"
cp    "$SKILL_DIR/assets/miner/package.json" "$MINER_DIR/"

# 2. Write .env with contract addresses
CLI_ENV="$CLI_DIR/.env"
MINER_ENV="$MINER_DIR/.env"
for ENV_FILE in "$CLI_ENV" "$MINER_ENV"; do
  if [ ! -f "$ENV_FILE" ]; then
    cat > "$ENV_FILE" << 'EOF'
PROTOCOL_ADDRESS=0x3BD7945d18FE6B68D273109902616BF17eb40F44
MMP_TOKEN_ADDRESS=0x30b8Bf35679E024331C813Be4bDfDB784E8E9a1E
BSC_RPC=https://bsc-dataseed.binance.org/
WALLET_PASSWORD=
EOF
    echo "    Created $ENV_FILE — set WALLET_PASSWORD before running"
  fi
done

# 3. Install npm dependencies
echo "[2] Installing CLI dependencies..."
cd "$CLI_DIR" && npm install --quiet --no-fund

echo "[3] Installing Miner dependencies..."
cd "$MINER_DIR" && npm install --quiet --no-fund

# 4. Create wallet if not exists
echo ""
if [ ! -f "$HOME/.clawmemory/wallet.json" ]; then
  echo "[4] No wallet found. Run to create one:"
  echo "    node $CLI_DIR/bin/cli.js init"
else
  echo "[4] Wallet found at ~/.clawmemory/wallet.json ✓"
fi

echo ""
echo "=== Done ==="
echo ""
echo "CLI commands:"
echo "  node $CLI_DIR/bin/cli.js init                    — create wallet"
echo "  node $CLI_DIR/bin/cli.js save <file>             — store a file"
echo "  node $CLI_DIR/bin/cli.js load <root> <out>       — retrieve a file"
echo "  node $CLI_DIR/bin/cli.js status                  — network overview"
echo "  node $CLI_DIR/bin/cli.js topup                   — check MMP balance"
echo ""
echo "Miner:"
echo "  node $MINER_DIR/index.js                         — start mining"
