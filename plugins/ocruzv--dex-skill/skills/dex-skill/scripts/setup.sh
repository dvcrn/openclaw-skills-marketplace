#!/usr/bin/env bash
# Dex Setup — four paths to connect your AI client with Dex CRM:
#   1. Headless non-interactive (CI/no TTY): download pre-built binary + API key auth
#   2. Headless interactive (TTY, no browser): device code flow (OTA)
#   3. Go available + browser: generate a CLI binary via CLIHub (OAuth)
#   4. No Go, has browser + npx: configure the hosted MCP server via add-mcp
set -euo pipefail

DEX_DIR="$HOME/.dex/bin"
DEX_API_KEY_FILE="$HOME/.dex/api-key"
MCP_URL="https://mcp.getdex.com/mcp"
MCP_API_URL="https://mcp.getdex.com"
RELEASES_URL="https://github.com/getdex/agent-skills/releases/latest/download"

# --------------------------------------------------------------------------
# Environment detection
# --------------------------------------------------------------------------
is_headless() {
  # Explicit API key means the user wants headless flow
  [ -n "${DEX_API_KEY:-}" ] && return 0
  # Saved API key from previous setup
  [ -f "$DEX_API_KEY_FILE" ] && return 0
  # SSH session without display
  [ -n "${SSH_TTY:-}" ] && [ -z "${DISPLAY:-}" ] && return 0
  # No display at all (Linux server)
  [ "$(uname -s)" = "Linux" ] && [ -z "${DISPLAY:-}" ] && [ -z "${WAYLAND_DISPLAY:-}" ] && return 0
  return 1
}

is_interactive_headless() {
  # Has a TTY (interactive) but no browser available
  [ -t 0 ] || return 1
  # Must not have an explicit API key (those go straight to headless)
  [ -n "${DEX_API_KEY:-}" ] && return 1
  [ -f "$DEX_API_KEY_FILE" ] && return 1
  # SSH session without display
  [ -n "${SSH_TTY:-}" ] && [ -z "${DISPLAY:-}" ] && return 0
  # Linux without display server
  [ "$(uname -s)" = "Linux" ] && [ -z "${DISPLAY:-}" ] && [ -z "${WAYLAND_DISPLAY:-}" ] && return 0
  return 1
}

detect_platform() {
  local os arch ext
  os=$(uname -s | tr '[:upper:]' '[:lower:]')
  arch=$(uname -m)
  case "$arch" in
    x86_64)  arch="amd64" ;;
    aarch64) arch="arm64" ;;
  esac
  ext=""
  case "$os" in
    mingw*|msys*|cygwin*) os="windows"; ext=".exe" ;;
  esac
  echo "${os} ${arch} ${ext}"
}

# --------------------------------------------------------------------------
# Shared: download CLI binary
# --------------------------------------------------------------------------
ensure_binary() {
  read -r os arch ext <<< "$(detect_platform)"
  local dex_bin="$DEX_DIR/dex${ext}"

  if [ ! -x "$dex_bin" ]; then
    local binary_name="dex-${os}-${arch}${ext}"
    local download_url="${RELEASES_URL}/${binary_name}"

    mkdir -p "$DEX_DIR"
    echo "Downloading ${binary_name}..."
    if ! curl -fSL "$download_url" -o "$dex_bin"; then
      echo "ERROR: Failed to download binary from $download_url"
      echo "Check available releases at: https://github.com/getdex/agent-skills/releases"
      exit 1
    fi
    chmod +x "$dex_bin"
    echo "Downloaded to $dex_bin"
  else
    echo "dex CLI already installed at $dex_bin"
  fi

  echo "$dex_bin"
}

# --------------------------------------------------------------------------
# Path 1: Headless — download pre-built binary + API key auth
# --------------------------------------------------------------------------
resolve_api_key() {
  # 1. Environment variable
  if [ -n "${DEX_API_KEY:-}" ]; then
    echo "$DEX_API_KEY"
    return
  fi

  # 2. Saved key file
  if [ -f "$DEX_API_KEY_FILE" ]; then
    cat "$DEX_API_KEY_FILE"
    return
  fi

  # 3. Prompt interactively
  echo "Enter your Dex API key (generate one at https://getdex.com/settings/integrations):" >&2
  read -r key
  if [ -z "$key" ]; then
    echo "ERROR: No API key provided." >&2
    exit 1
  fi
  echo "$key"
}

save_api_key() {
  local key="$1"
  mkdir -p "$(dirname "$DEX_API_KEY_FILE")"
  echo "$key" > "$DEX_API_KEY_FILE"
  chmod 600 "$DEX_API_KEY_FILE"
}

setup_headless() {
  echo "Headless environment detected — using pre-built binary + API key."
  echo ""

  local api_key
  api_key=$(resolve_api_key)

  local dex_bin
  dex_bin=$(ensure_binary)

  echo "Authenticating with API key..."
  "$dex_bin" auth --token "$api_key"

  save_api_key "$api_key"

  echo ""
  echo "OK: dex CLI installed and authenticated."
  echo "Try: $dex_bin dex-search-contacts --query '*'"
}

# --------------------------------------------------------------------------
# Path 2: Device Code Flow (OTA) — interactive headless
# --------------------------------------------------------------------------
setup_device_code() {
  echo "Interactive headless environment detected — using device code flow."
  echo ""

  local dex_bin
  dex_bin=$(ensure_binary)

  # Request a device code from the MCP server
  local response
  response=$(curl -s -X POST "${MCP_API_URL}/device/code" \
    -H "Content-Type: application/json" 2>/dev/null)

  if [ -z "$response" ]; then
    echo "ERROR: Failed to reach MCP server at ${MCP_API_URL}"
    echo "Falling back to API key setup..."
    setup_headless
    return
  fi

  local user_code device_code verification_uri
  user_code=$(echo "$response" | grep -o '"user_code":"[^"]*"' | cut -d'"' -f4)
  device_code=$(echo "$response" | grep -o '"device_code":"[^"]*"' | cut -d'"' -f4)
  verification_uri=$(echo "$response" | grep -o '"verification_uri":"[^"]*"' | cut -d'"' -f4)

  if [ -z "$user_code" ] || [ -z "$device_code" ]; then
    echo "ERROR: Failed to get device code from server."
    echo "Falling back to API key setup..."
    setup_headless
    return
  fi

  echo "┌──────────────────────────────────────────────┐"
  echo "│                                              │"
  echo "│   Go to: ${verification_uri}"
  echo "│                                              │"
  echo "│   Enter code:  ${user_code}                  │"
  echo "│                                              │"
  echo "└──────────────────────────────────────────────┘"
  echo ""
  echo "Waiting for authorization..."

  # Poll for the token
  local attempts=0
  local max_attempts=120  # 10 minutes at 5s intervals
  while [ "$attempts" -lt "$max_attempts" ]; do
    sleep 5
    attempts=$((attempts + 1))

    local token_response
    token_response=$(curl -s -X POST "${MCP_API_URL}/device/token" \
      -H "Content-Type: application/json" \
      -d "{\"device_code\":\"${device_code}\"}" 2>/dev/null)

    # Check for api_key in response
    local api_key
    api_key=$(echo "$token_response" | grep -o '"api_key":"[^"]*"' | cut -d'"' -f4)
    if [ -n "$api_key" ]; then
      echo ""
      echo "Authorization successful!"
      echo ""

      "$dex_bin" auth --token "$api_key"
      save_api_key "$api_key"

      echo ""
      echo "OK: dex CLI installed and authenticated."
      echo "Try: $dex_bin dex-search-contacts --query '*'"
      return
    fi

    # Check for terminal errors
    local error
    error=$(echo "$token_response" | grep -o '"error":"[^"]*"' | cut -d'"' -f4)
    if [ "$error" = "expired_token" ]; then
      echo ""
      echo "ERROR: Device code expired. Please run setup again."
      exit 1
    fi

    # authorization_pending and slow_down are expected — keep polling
  done

  echo ""
  echo "ERROR: Timed out waiting for authorization."
  exit 1
}

# --------------------------------------------------------------------------
# Path 3: CLI generation via CLIHub (requires Go + browser)
# --------------------------------------------------------------------------
setup_cli() {
  local os arch ext
  read -r os arch ext <<< "$(detect_platform)"

  local dex_bin="$DEX_DIR/dex${ext}"

  if [ -x "$dex_bin" ]; then
    echo "dex CLI already installed at $dex_bin"
    "$dex_bin" auth status 2>/dev/null || echo "Run '$dex_bin auth' to authenticate."
    exit 0
  fi

  echo "Go found: $(go version)"

  local gopath clihub
  gopath=$(go env GOPATH)
  clihub="$gopath/bin/clihub"
  if [ ! -x "$clihub" ]; then
    echo "Installing clihub..."
    go install github.com/thellimist/clihub@latest
  fi
  echo "clihub found: $clihub"

  mkdir -p "$DEX_DIR"
  echo "Generating dex CLI for ${os}/${arch}..."
  "$clihub" generate \
    --url "$MCP_URL" \
    --oauth \
    --name dex \
    --platform "${os}/${arch}" \
    --output "$DEX_DIR"

  local platform_bin="$DEX_DIR/dex-${os}-${arch}${ext}"
  if [ -f "$platform_bin" ] && [ ! -f "$dex_bin" ]; then
    mv "$platform_bin" "$dex_bin"
  fi
  chmod +x "$dex_bin"

  echo ""
  echo "OK: dex CLI installed at $dex_bin"
  echo "Run '$dex_bin auth' to authenticate if needed."
}

# --------------------------------------------------------------------------
# Path 4: Configure MCP server across all detected clients via add-mcp
# --------------------------------------------------------------------------
setup_mcp() {
  echo "Go not found — configuring Dex MCP server connection instead."
  echo ""

  if ! command -v npx &>/dev/null; then
    echo "ERROR: Neither Go nor Node.js found."
    echo ""
    echo "Install one of the following:"
    echo "  - Go (https://go.dev/dl/) — to generate a standalone Dex CLI"
    echo "  - Node.js (https://nodejs.org/) — to configure the MCP server in your editors"
    echo ""
    echo "Or add the Dex MCP server manually to your client's config:"
    echo ""
    print_mcp_snippet
    exit 1
  fi

  echo "Configuring Dex MCP server across all detected clients..."
  npx -y add-mcp "$MCP_URL" -y

  echo ""
  echo "OK: Dex MCP server configured. Restart your client(s) to connect."
  echo "You'll be prompted to authenticate via browser on first use."
}

print_mcp_snippet() {
  cat <<SNIPPET
{
  "mcpServers": {
    "dex": {
      "type": "http",
      "url": "$MCP_URL"
    }
  }
}
SNIPPET
}

# --------------------------------------------------------------------------
# Main — pick the best path based on environment
# --------------------------------------------------------------------------
if is_headless && ! is_interactive_headless; then
  setup_headless
elif is_interactive_headless; then
  setup_device_code
elif command -v go &>/dev/null; then
  setup_cli
else
  setup_mcp
fi
