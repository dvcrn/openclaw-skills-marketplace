#!/usr/bin/env bash
# ClawMemory — headless wallet setup (no TTY required)
set -e

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CLI_DIR="$HOME/.clawmemory/memory-client"
ENV_FILE="$CLI_DIR/.env"
MINER_ENV="$HOME/.clawmemory/miner/.env"
INIT_SCRIPT="$SKILL_DIR/scripts/init-wallet.js"

# Generate or reuse password
if grep -q 'WALLET_PASSWORD=[^$]' "$ENV_FILE" 2>/dev/null; then
  PASSWORD=$(grep 'WALLET_PASSWORD=' "$ENV_FILE" | cut -d= -f2)
else
  PASSWORD=$(node -e "console.log(require('crypto').randomBytes(16).toString('hex'))")
  # Save to both .env files
  for ENV in "$ENV_FILE" "$MINER_ENV"; do
    if grep -q 'WALLET_PASSWORD=' "$ENV" 2>/dev/null; then
      sed -i "s/WALLET_PASSWORD=.*/WALLET_PASSWORD=$PASSWORD/" "$ENV"
    else
      echo "WALLET_PASSWORD=$PASSWORD" >> "$ENV"
    fi
    if grep -q 'MINER_WALLET_PASSWORD=' "$ENV" 2>/dev/null; then
      sed -i "s/MINER_WALLET_PASSWORD=.*/MINER_WALLET_PASSWORD=$PASSWORD/" "$ENV"
    else
      echo "MINER_WALLET_PASSWORD=$PASSWORD" >> "$ENV"
    fi
  done
fi

# Run headless wallet init
RESULT=$(WALLET_PASSWORD="$PASSWORD" node "$INIT_SCRIPT" 2>&1)
echo "$RESULT"

# Extract address
ADDRESS=$(echo "$RESULT" | node -e "
  const chunks = [];
  process.stdin.on('data', d => chunks.push(d));
  process.stdin.on('end', () => {
    try {
      const data = JSON.parse(chunks.join(''));
      console.log(data.address || '');
    } catch(e) { console.log(''); }
  });
")

if [ -n "$ADDRESS" ]; then
  echo ""
  echo "Wallet address: $ADDRESS"
  echo "Password saved: $ENV_FILE"
fi
