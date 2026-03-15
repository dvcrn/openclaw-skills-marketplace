#!/usr/bin/env bash
# Host Security Audit for OpenClaw
# Usage: bash security-audit.sh [--json]
set -uo pipefail

JSON_MODE=false
[[ "${1:-}" == "--json" ]] && JSON_MODE=true

declare -a RESULTS=()
CRITICAL=0
WARNING=0
OK=0

check() {
  local severity="$1" name="$2" detail="$3"
  if $JSON_MODE; then
    RESULTS+=("{\"severity\":\"$severity\",\"check\":\"$name\",\"detail\":\"$detail\"}")
  else
    local icon="✅"
    [[ "$severity" == "CRITICAL" ]] && icon="🔴"
    [[ "$severity" == "WARNING" ]] && icon="🟡"
    echo "$icon [$severity] $name: $detail"
  fi
  case "$severity" in
    CRITICAL) CRITICAL=$((CRITICAL+1)) ;;
    WARNING) WARNING=$((WARNING+1)) ;;
    OK) OK=$((OK+1)) ;;
  esac
}

OS="$(uname -s)"
echo "=== Host Security Audit ==="
echo "Date: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "OS: $OS $(uname -r) ($(uname -m))"
echo ""

# --- Firewall ---
if [[ "$OS" == "Darwin" ]]; then
  FW=$(/usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate 2>/dev/null || echo "unknown")
  if echo "$FW" | grep -qi "enabled"; then
    check "OK" "Firewall" "macOS Application Firewall is enabled"
  else
    check "CRITICAL" "Firewall" "macOS Application Firewall is DISABLED — run: sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setglobalstate on"
  fi
elif [[ "$OS" == "Linux" ]]; then
  if command -v ufw &>/dev/null && ufw status 2>/dev/null | grep -qi "active"; then
    check "OK" "Firewall" "ufw is active"
  elif command -v firewall-cmd &>/dev/null && firewall-cmd --state 2>/dev/null | grep -qi "running"; then
    check "OK" "Firewall" "firewalld is running"
  else
    check "CRITICAL" "Firewall" "No active firewall detected"
  fi
fi

# --- Disk Encryption ---
if [[ "$OS" == "Darwin" ]]; then
  FV=$(fdesetup status 2>/dev/null || echo "unknown")
  if echo "$FV" | grep -qi "on"; then
    check "OK" "Disk Encryption" "FileVault is ON"
  else
    check "CRITICAL" "Disk Encryption" "FileVault is OFF — enable in System Settings > Privacy & Security"
  fi
elif [[ "$OS" == "Linux" ]]; then
  if lsblk -o TYPE 2>/dev/null | grep -q "crypt"; then
    check "OK" "Disk Encryption" "LUKS encryption detected"
  else
    check "WARNING" "Disk Encryption" "No LUKS encryption detected on block devices"
  fi
fi

# --- Auto Updates ---
if [[ "$OS" == "Darwin" ]]; then
  AU=$(defaults read /Library/Preferences/com.apple.SoftwareUpdate AutomaticCheckEnabled 2>/dev/null || echo "0")
  AI=$(defaults read /Library/Preferences/com.apple.SoftwareUpdate AutomaticDownload 2>/dev/null || echo "0")
  if [[ "$AU" == "1" ]]; then
    check "OK" "Auto Updates" "Automatic update checking is enabled"
  else
    check "WARNING" "Auto Updates" "Automatic update checking is disabled"
  fi
elif [[ "$OS" == "Linux" ]]; then
  if dpkg -l unattended-upgrades 2>/dev/null | grep -q "^ii"; then
    check "OK" "Auto Updates" "unattended-upgrades is installed"
  else
    check "WARNING" "Auto Updates" "unattended-upgrades not found — consider installing"
  fi
fi

# --- Open Ports ---
if [[ "$OS" == "Darwin" ]]; then
  PORTS=$(lsof -nP -iTCP -sTCP:LISTEN 2>/dev/null | grep -v "^COMMAND" | awk '{print $1":"$9}' | sort -u || true)
else
  PORTS=$(ss -ltnp 2>/dev/null | grep LISTEN | awk '{print $4}' | sort -u || true)
fi
if [[ -z "$PORTS" ]]; then
  PORT_COUNT=0
else
  PORT_COUNT=$(echo "$PORTS" | wc -l | tr -d ' ')
fi
if [[ -n "$PORTS" ]]; then
  EXPOSED=$(echo "$PORTS" | grep -E "(\*:|0\.0\.0\.0:)" | grep -v "127\." || true)
  if [[ -n "$EXPOSED" ]]; then
    EXP_COUNT=$(echo "$EXPOSED" | wc -l | tr -d ' ')
    check "WARNING" "Open Ports" "$PORT_COUNT listening, $EXP_COUNT on all interfaces"
  else
    check "OK" "Open Ports" "$PORT_COUNT listening, none on all interfaces"
  fi
else
  check "OK" "Open Ports" "No listening ports detected"
fi

# --- OpenClaw Version ---
if command -v openclaw &>/dev/null; then
  OC_VER=$(openclaw --version 2>/dev/null || echo "unknown")
  NPM_VER=$(npm view openclaw version 2>/dev/null || echo "unknown")
  if [[ "$OC_VER" == "$NPM_VER" ]]; then
    check "OK" "OpenClaw Version" "v$OC_VER (latest)"
  else
    check "WARNING" "OpenClaw Version" "v$OC_VER installed, v$NPM_VER available"
  fi
else
  check "WARNING" "OpenClaw Version" "openclaw CLI not found in PATH"
fi

# --- OpenClaw Gateway Bind ---
OC_CONFIG="${HOME}/.openclaw/openclaw.json"
if [[ -f "$OC_CONFIG" ]]; then
  if grep -q '"0\.0\.0\.0"' "$OC_CONFIG"; then
    check "CRITICAL" "Gateway Bind" "Gateway binds to 0.0.0.0 — exposed to network. Change to 127.0.0.1"
  else
    check "OK" "Gateway Bind" "Gateway not binding to 0.0.0.0"
  fi
fi

# --- API Key Exposure ---
if [[ -f "$OC_CONFIG" ]]; then
  KEY_PATTERNS='(sk-|gsk_|xai-|AIza|ghp_|glpat-|AKIA)'
  EXPOSED_KEYS=$(grep -cE "$KEY_PATTERNS" "$OC_CONFIG" 2>/dev/null || echo "0")
  if [[ "$EXPOSED_KEYS" -gt 0 ]]; then
    check "WARNING" "API Keys" "$EXPOSED_KEYS API keys in plaintext config (consider using env vars or secrets dir)"
  else
    check "OK" "API Keys" "No obvious plaintext API keys in config"
  fi
fi

# --- Secrets Directory Permissions ---
SECRETS_DIR="${HOME}/.openclaw/secrets"
if [[ -d "$SECRETS_DIR" ]]; then
  PERMS=$(stat -f "%Lp" "$SECRETS_DIR" 2>/dev/null || stat -c "%a" "$SECRETS_DIR" 2>/dev/null || echo "unknown")
  if [[ "$PERMS" == "700" || "$PERMS" == "600" ]]; then
    check "OK" "Secrets Permissions" "$SECRETS_DIR is $PERMS"
  else
    check "WARNING" "Secrets Permissions" "$SECRETS_DIR is $PERMS — should be 700"
  fi
fi

# --- Disk Usage ---
DISK_PCT=$(df -h / 2>/dev/null | awk 'NR==2 {gsub(/%/,""); print $5}')
if [[ -n "$DISK_PCT" ]]; then
  if [[ "$DISK_PCT" -ge 90 ]]; then
    check "CRITICAL" "Disk Usage" "${DISK_PCT}% — critically low space"
  elif [[ "$DISK_PCT" -ge 80 ]]; then
    check "WARNING" "Disk Usage" "${DISK_PCT}% — getting full"
  else
    check "OK" "Disk Usage" "${DISK_PCT}% used"
  fi
fi

# --- Time Machine (macOS) ---
if [[ "$OS" == "Darwin" ]]; then
  TM_DEST=$(tmutil destinationinfo 2>/dev/null || echo "No destinations")
  if echo "$TM_DEST" | grep -qi "no destinations\|error"; then
    check "WARNING" "Time Machine" "No backup destination configured"
  else
    LAST_BACKUP=$(tmutil latestbackup 2>/dev/null || echo "unknown")
    check "OK" "Time Machine" "Configured, last: $(basename "$LAST_BACKUP" 2>/dev/null || echo 'unknown')"
  fi
fi

# --- Brew Outdated (macOS) ---
if [[ "$OS" == "Darwin" ]] && command -v brew &>/dev/null; then
  OUTDATED=$(brew outdated --quiet 2>/dev/null | wc -l | tr -d ' ')
  if [[ "$OUTDATED" -gt 10 ]]; then
    check "WARNING" "Brew Packages" "$OUTDATED packages outdated — run: brew upgrade"
  else
    check "OK" "Brew Packages" "$OUTDATED packages outdated"
  fi
fi

# --- Suspicious Processes ---
SUSPICIOUS=$(ps aux 2>/dev/null | grep -iE "(cryptominer|xmrig|minerd|reverse.shell|nc -l)" | grep -v grep || true)
if [[ -n "$SUSPICIOUS" ]]; then
  check "CRITICAL" "Suspicious Processes" "Potential malicious process detected"
else
  check "OK" "Suspicious Processes" "No known suspicious processes"
fi

# --- Summary ---
echo ""
echo "=== Summary ==="
TOTAL=$((CRITICAL + WARNING + OK))
echo "Total checks: $TOTAL | 🔴 Critical: $CRITICAL | 🟡 Warning: $WARNING | ✅ OK: $OK"

if [[ "$CRITICAL" -gt 0 ]]; then
  echo "⚠️  CRITICAL issues found — address immediately"
  exit 2
elif [[ "$WARNING" -gt 0 ]]; then
  echo "⚠️  Warnings found — review when convenient"
  exit 1
else
  echo "✅ All checks passed"
  exit 0
fi
