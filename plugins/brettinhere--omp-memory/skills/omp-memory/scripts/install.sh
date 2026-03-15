#!/usr/bin/env bash
# OMP Memory Client installer
# Clones the CLI and sets up environment

set -e

OMP_DIR="$HOME/.omp-client"
ENV_FILE="$OMP_DIR/.env"
REPO="https://github.com/openclawai/omp"  # update if repo URL changes

echo "=== OMP Memory Protocol Client Installer ==="

# 1. Clone or update
if [ -d "$OMP_DIR/.git" ]; then
  echo "[1] Updating existing install..."
  cd "$OMP_DIR" && git pull --quiet
else
  echo "[1] Cloning OMP repo..."
  git clone --quiet "$REPO" "$OMP_DIR"
  cd "$OMP_DIR/packages/memory-client"
fi

# 2. Install deps
echo "[2] Installing dependencies..."
cd "$OMP_DIR/packages/memory-client"
npm install --quiet

# 3. Write .env if not exists
if [ ! -f "$ENV_FILE" ]; then
  echo "[3] Creating .env..."
  cat > "$ENV_FILE" << 'EOF'
PROTOCOL_ADDRESS=0x3BD7945d18FE6B68D273109902616BF17eb40F44
MMP_TOKEN_ADDRESS=0x30b8Bf35679E024331C813Be4bDfDB784E8E9a1E
BSC_RPC=https://bsc-dataseed.binance.org/
WALLET_PASSWORD=
EOF
  echo "    → Edit $ENV_FILE and set WALLET_PASSWORD"
else
  echo "[3] .env already exists, skipping"
fi

# 4. Create wallet if not exists
if [ ! -f "$HOME/.omp/wallet.json" ]; then
  echo "[4] No wallet found. Run: node $OMP_DIR/packages/memory-client/bin/cli.js init"
else
  echo "[4] Wallet found at ~/.omp/wallet.json"
fi

echo ""
echo "=== Done ==="
echo "CLI: node $OMP_DIR/packages/memory-client/bin/cli.js"
echo "     node bin/cli.js save <file>         — store a file"
echo "     node bin/cli.js load <root> <out>   — retrieve a file"
echo "     node bin/cli.js status              — network overview"
echo "     node bin/cli.js topup               — check MMP balance"
