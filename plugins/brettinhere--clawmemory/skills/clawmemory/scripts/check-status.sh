#!/usr/bin/env bash
# ClawMemory — Status Check
# Returns JSON with current setup state

CLI_DIR="$HOME/.clawmemory/memory-client"
MINER_DIR="$HOME/.clawmemory/miner"
WALLET_FILE="$HOME/.omp/wallet.enc"
ENV_FILE="$CLI_DIR/.env"
INDEX="$HOME/.clawmemory/index.json"

installed=false
has_wallet=false
has_bnb=false
wallet_address=""
bnb_balance=""
slots_used=0
slots_left=10

# Check install
[ -f "$CLI_DIR/bin/cli.js" ] && [ -d "$CLI_DIR/node_modules" ] && installed=true

# Check wallet
if [ -f "$WALLET_FILE" ] && [ -f "$ENV_FILE" ]; then
  PW=$(grep 'WALLET_PASSWORD=' "$ENV_FILE" 2>/dev/null | cut -d= -f2)
  if [ -n "$PW" ]; then
    RESULT=$(WALLET_PASSWORD="$PW" node "$HOME/.openclaw/workspace/skills/clawmemory/scripts/init-wallet.js" 2>/dev/null)
    wallet_address=$(echo "$RESULT" | node -e "try{const d=JSON.parse(require('fs').readFileSync('/dev/stdin','utf8'));console.log(d.address||'')}catch(e){console.log('')}" 2>/dev/null)
    [ -n "$wallet_address" ] && has_wallet=true
  fi
fi

# Check BNB balance
if [ -n "$wallet_address" ]; then
  bnb_balance=$(node -e "
    const {ethers} = require('$CLI_DIR/node_modules/ethers');
    const p = new ethers.JsonRpcProvider('https://bsc-dataseed.binance.org/');
    p.getBalance('$wallet_address').then(b => {
      const bnb = parseFloat(ethers.formatEther(b));
      console.log(bnb.toFixed(6));
    }).catch(() => console.log('0'));
  " 2>/dev/null)
  bnb_float=$(echo "$bnb_balance" | awk '{printf "%.6f", $1}')
  bnb_check=$(echo "$bnb_float > 0.001" | bc -l 2>/dev/null || echo "0")
  [ "$bnb_check" = "1" ] && has_bnb=true
fi

# Check slots
if [ -f "$INDEX" ]; then
  slots_used=$(node -e "
    try {
      const db = JSON.parse(require('fs').readFileSync('$INDEX','utf8'));
      console.log(Object.keys(db.slots||{}).length);
    } catch(e) { console.log(0); }
  " 2>/dev/null)
  slots_left=$((10 - slots_used))
fi

node -e "
console.log(JSON.stringify({
  installed: $installed,
  has_wallet: $has_wallet,
  wallet_address: '$wallet_address',
  bnb_balance: '$bnb_balance',
  has_bnb: $has_bnb,
  slots_used: $slots_used,
  slots_left: $slots_left,
}));
"
