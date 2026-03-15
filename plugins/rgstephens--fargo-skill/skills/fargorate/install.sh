#!/usr/bin/env bash
# install.sh — Install the fargo CLI from the fargo-skill releases repo.
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/rgstephens/fargo-skill/main/install.sh | bash
#
# Optionally pin a version:
#   VERSION=v1.2.3 bash <(curl -fsSL ...)

set -euo pipefail

REPO="rgstephens/fargo-skill"
BIN_NAME="fargo"
INSTALL_DIR="${INSTALL_DIR:-/usr/local/bin}"

# Detect OS
OS=$(uname -s | tr '[:upper:]' '[:lower:]')
case "$OS" in
  darwin|linux) ;;
  mingw*|msys*|cygwin*) OS="windows" ;;
  *) echo "Unsupported OS: $OS" >&2; exit 1 ;;
esac

# Detect architecture
ARCH=$(uname -m)
case "$ARCH" in
  x86_64|amd64)   ARCH="amd64" ;;
  arm64|aarch64)  ARCH="arm64" ;;
  *) echo "Unsupported architecture: $ARCH" >&2; exit 1 ;;
esac

# Resolve version
if [[ -z "${VERSION:-}" ]]; then
  echo "Fetching latest release..." >&2
  VERSION=$(curl -sf "https://api.github.com/repos/${REPO}/releases/latest" \
    | grep '"tag_name"' | sed 's/.*"tag_name": *"\([^"]*\)".*/\1/')
fi

if [[ -z "$VERSION" ]]; then
  echo "Could not determine latest version. Set VERSION= explicitly." >&2
  exit 1
fi

echo "Installing ${BIN_NAME} ${VERSION} (${OS}/${ARCH})..." >&2

EXT="tar.gz"
[[ "$OS" == "windows" ]] && EXT="zip"

FILENAME="${BIN_NAME}_${OS}_${ARCH}.${EXT}"
URL="https://github.com/${REPO}/releases/download/${VERSION}/${FILENAME}"

TMPDIR=$(mktemp -d)
trap 'rm -rf "$TMPDIR"' EXIT

CHECKSUMS_URL="https://github.com/${REPO}/releases/download/${VERSION}/checksums.txt"

echo "Downloading ${URL}" >&2
curl -fsSL "$URL" -o "${TMPDIR}/${FILENAME}"
curl -fsSL "$CHECKSUMS_URL" -o "${TMPDIR}/checksums.txt"

# Verify SHA256 checksum
echo "Verifying checksum..." >&2
EXPECTED=$(grep " ${FILENAME}$" "${TMPDIR}/checksums.txt" | awk '{print $1}')
if [[ -z "$EXPECTED" ]]; then
  echo "Checksum entry for ${FILENAME} not found in checksums.txt" >&2
  exit 1
fi
if command -v sha256sum &>/dev/null; then
  ACTUAL=$(sha256sum "${TMPDIR}/${FILENAME}" | awk '{print $1}')
elif command -v shasum &>/dev/null; then
  ACTUAL=$(shasum -a 256 "${TMPDIR}/${FILENAME}" | awk '{print $1}')
else
  echo "No sha256sum or shasum found; skipping checksum verification." >&2
  ACTUAL="$EXPECTED"
fi
if [[ "$ACTUAL" != "$EXPECTED" ]]; then
  echo "Checksum mismatch for ${FILENAME}!" >&2
  echo "  expected: ${EXPECTED}" >&2
  echo "  actual:   ${ACTUAL}" >&2
  exit 1
fi
echo "Checksum OK" >&2

if [[ "$EXT" == "zip" ]]; then
  unzip -q "${TMPDIR}/${FILENAME}" -d "$TMPDIR"
else
  tar -xzf "${TMPDIR}/${FILENAME}" -C "$TMPDIR"
fi

BINARY="${TMPDIR}/${BIN_NAME}"
[[ "$OS" == "windows" ]] && BINARY="${TMPDIR}/${BIN_NAME}.exe"

chmod +x "$BINARY"

# Install — try INSTALL_DIR, fall back to ~/bin
if [[ -w "$INSTALL_DIR" ]]; then
  mv "$BINARY" "${INSTALL_DIR}/${BIN_NAME}"
elif command -v sudo &>/dev/null; then
  sudo mv "$BINARY" "${INSTALL_DIR}/${BIN_NAME}"
else
  mkdir -p "${HOME}/bin"
  mv "$BINARY" "${HOME}/bin/${BIN_NAME}"
  INSTALL_DIR="${HOME}/bin"
  echo "Installed to ${HOME}/bin — ensure this is in your PATH." >&2
fi

echo "Installed ${BIN_NAME} ${VERSION} to ${INSTALL_DIR}/${BIN_NAME}" >&2
"${INSTALL_DIR}/${BIN_NAME}" --version
