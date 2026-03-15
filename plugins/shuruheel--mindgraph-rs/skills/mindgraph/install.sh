#!/bin/bash
# MindGraph Server Install Script
# Downloads the pre-built binary from GitHub Releases.
# Usage: bash install.sh [version]
#   version defaults to "latest"

set -euo pipefail

REPO="shuruheel/mindgraph-rs"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BINARY_PATH="$SCRIPT_DIR/mindgraph-server"
BINARY_NAME="mindgraph-server"

VERSION="${1:-latest}"

# Resolve "latest" to actual tag
if [ "$VERSION" = "latest" ]; then
  echo "🔍 Resolving latest release..."
  VERSION=$(curl -sL -H "Accept: application/vnd.github+json" \
    "https://api.github.com/repos/$REPO/releases/latest" | \
    python3 -c "import json,sys; print(json.load(sys.stdin)['tag_name'])" 2>/dev/null)
  if [ -z "$VERSION" ]; then
    echo "❌ Failed to resolve latest release"
    exit 1
  fi
fi

echo "📦 Installing mindgraph-server $VERSION..."

# Check if we already have this version
if [ -f "$BINARY_PATH" ] && [ -f "$SCRIPT_DIR/.server-version" ]; then
  CURRENT=$(cat "$SCRIPT_DIR/.server-version")
  if [ "$CURRENT" = "$VERSION" ]; then
    echo "✅ Already at $VERSION"
    exit 0
  fi
fi

# Download binary from release assets
DOWNLOAD_URL="https://github.com/$REPO/releases/download/$VERSION/$BINARY_NAME"
echo "⬇️  Downloading from $DOWNLOAD_URL..."

HTTP_CODE=$(curl -sL -w "%{http_code}" -o "$BINARY_PATH.tmp" "$DOWNLOAD_URL")
if [ "$HTTP_CODE" != "200" ]; then
  rm -f "$BINARY_PATH.tmp"
  echo "❌ Download failed (HTTP $HTTP_CODE)"
  echo "   URL: $DOWNLOAD_URL"
  echo "   Check that the release has a '$BINARY_NAME' asset attached."
  exit 1
fi

# Verify it's actually a binary (not an HTML error page)
FILE_TYPE=$(file -b "$BINARY_PATH.tmp" | head -1)
if echo "$FILE_TYPE" | grep -qi "html\|text\|ascii"; then
  rm -f "$BINARY_PATH.tmp"
  echo "❌ Downloaded file is not a binary (got: $FILE_TYPE)"
  exit 1
fi

# Install
mv "$BINARY_PATH.tmp" "$BINARY_PATH"
chmod +x "$BINARY_PATH"
echo "$VERSION" > "$SCRIPT_DIR/.server-version"

echo "✅ Installed mindgraph-server $VERSION → $BINARY_PATH"
