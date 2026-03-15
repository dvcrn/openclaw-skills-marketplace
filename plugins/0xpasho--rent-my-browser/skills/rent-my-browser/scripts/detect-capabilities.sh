#!/usr/bin/env bash
# Detects node capabilities and outputs JSON for the heartbeat payload.
# Usage: bash detect-capabilities.sh
# Output: JSON object to stdout

source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"
rmb_check_deps

# ── Node type detection ─────────────────────────────────────────────────────
detect_node_type() {
  # Env override
  if [ -n "${RMB_NODE_TYPE:-}" ]; then
    echo "$RMB_NODE_TYPE"
    return
  fi

  local os
  os="$(uname -s)"

  if [ "$os" = "Darwin" ]; then
    # macOS with Chrome = real machine
    if [ -d "/Applications/Google Chrome.app" ]; then
      echo "real"
    else
      echo "headless"
    fi
  else
    # Linux: check for display server
    if [ -n "${DISPLAY:-}" ] || pgrep -x Xvfb &>/dev/null; then
      if command -v google-chrome &>/dev/null; then
        echo "real"
      else
        echo "headless"
      fi
    else
      echo "headless"
    fi
  fi
}

# ── Browser detection ───────────────────────────────────────────────────────
detect_browser() {
  local os
  os="$(uname -s)"
  local name=""
  local version=""

  if [ "$os" = "Darwin" ]; then
    if [ -d "/Applications/Google Chrome.app" ]; then
      name="chrome"
      version="$("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --version 2>/dev/null | grep -oE '[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+' | head -1 || echo "unknown")"
    elif command -v chromium &>/dev/null; then
      name="chromium"
      version="$(chromium --version 2>/dev/null | grep -oE '[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+' | head -1 || echo "unknown")"
    fi
  else
    if command -v google-chrome &>/dev/null; then
      name="chrome"
      version="$(google-chrome --version 2>/dev/null | grep -oE '[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+' | head -1 || echo "unknown")"
    elif command -v google-chrome-stable &>/dev/null; then
      name="chrome"
      version="$(google-chrome-stable --version 2>/dev/null | grep -oE '[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+' | head -1 || echo "unknown")"
    elif command -v chromium-browser &>/dev/null; then
      name="chromium"
      version="$(chromium-browser --version 2>/dev/null | grep -oE '[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+' | head -1 || echo "unknown")"
    elif command -v chromium &>/dev/null; then
      name="chromium"
      version="$(chromium --version 2>/dev/null | grep -oE '[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+' | head -1 || echo "unknown")"
    fi
  fi

  if [ -z "$name" ]; then
    name="unknown"
    version="unknown"
  fi

  jq -n --arg name "$name" --arg version "$version" \
    '{"name": $name, "version": $version}'
}

# ── Geo detection ───────────────────────────────────────────────────────────
detect_geo() {
  local cache_file="$STATE_DIR/geo-cache.json"
  local cache_ttl=3600  # 1 hour

  # Check cache
  if [ -f "$cache_file" ]; then
    local cached_at
    cached_at="$(jq -r '.cached_at // 0' "$cache_file" 2>/dev/null || echo 0)"
    local now
    now="$(date +%s)"
    local age=$((now - cached_at))
    if [ "$age" -lt "$cache_ttl" ]; then
      jq '.geo' "$cache_file"
      return
    fi
  fi

  # Fetch from ipinfo.io
  local ipinfo
  ipinfo="$(curl -s --max-time 5 "https://ipinfo.io/json" 2>/dev/null)" || {
    rmb_log WARN "Geo detection failed, using defaults"
    echo '{"country": "US", "ip_type": "datacenter"}'
    return
  }

  local country region city org ip_type

  country="$(echo "$ipinfo" | jq -r '.country // "US"')"
  region="$(echo "$ipinfo" | jq -r '.region // empty')"
  city="$(echo "$ipinfo" | jq -r '.city // empty')"
  org="$(echo "$ipinfo" | jq -r '.org // ""')"

  # Detect datacenter vs residential by org field
  local dc_keywords="AWS|Amazon|DigitalOcean|Hetzner|Google Cloud|Google LLC|Microsoft Azure|Microsoft Corporation|Linode|Vultr|OVH|Oracle Cloud|Cloudflare|Scaleway|UpCloud|Contabo"
  if echo "$org" | grep -qiE "$dc_keywords"; then
    ip_type="datacenter"
  else
    ip_type="residential"
  fi

  local geo
  geo="$(jq -n \
    --arg country "$country" \
    --arg region "$region" \
    --arg city "$city" \
    --arg ip_type "$ip_type" \
    '{country: $country, region: (if $region == "" then null else $region end), city: (if $city == "" then null else $city end), ip_type: $ip_type} | del(.[] | nulls)')"

  # Cache the result
  jq -n --argjson geo "$geo" --arg cached_at "$(date +%s)" \
    '{"geo": $geo, "cached_at": ($cached_at | tonumber)}' > "$cache_file"

  echo "$geo"
}

# ── Capabilities ────────────────────────────────────────────────────────────
detect_capabilities() {
  local node_type="$1"
  local max_concurrent="${RMB_MAX_CONCURRENT:-1}"

  # Determine modes
  local modes
  if [ "$node_type" = "real" ]; then
    modes='["simple", "adversarial"]'
  else
    modes='["simple"]'
  fi

  # Filter by allowed modes if set
  if [ -n "${RMB_ALLOWED_MODES:-}" ]; then
    local allowed_json
    allowed_json="$(echo "$RMB_ALLOWED_MODES" | tr ',' '\n' | jq -R . | jq -s .)"
    modes="$(jq -n --argjson modes "$modes" --argjson allowed "$allowed_json" \
      '[$modes[] | select(. as $m | $allowed | index($m))]')"
  fi

  jq -n --argjson modes "$modes" --argjson mc "$max_concurrent" \
    '{"modes": $modes, "max_concurrent": $mc}'
}

# ── Main output ─────────────────────────────────────────────────────────────
main() {
  local node_type
  node_type="$(detect_node_type)"

  local browser
  browser="$(detect_browser)"

  local geo
  geo="$(detect_geo)"

  local capabilities
  capabilities="$(detect_capabilities "$node_type")"

  jq -n \
    --arg type "$node_type" \
    --argjson browser "$browser" \
    --argjson geo "$geo" \
    --argjson capabilities "$capabilities" \
    '{"type": $type, "browser": $browser, "geo": $geo, "capabilities": $capabilities}'
}

main
