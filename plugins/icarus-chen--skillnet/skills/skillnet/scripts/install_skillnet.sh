#!/usr/bin/env bash
# install_skillnet.sh — Install the skillnet-ai Python SDK
# Targets: macOS / Linux / Windows (via Git Bash / WSL)
# Uses only standard Python package managers already present on the system.
# Priority: pipx > pip (no remote scripts, no system modifications)
set -euo pipefail

PACKAGE="skillnet-ai"

echo "🧠 SkillNet SDK Installer"
echo "========================="

# ─── Already installed? ──────────────────────────────────────────────
if command -v skillnet &>/dev/null; then
  version=$(skillnet --version 2>/dev/null || echo "unknown")
  echo "✅ skillnet CLI already installed (${version})"
  exit 0
fi

# ─── Find Python ─────────────────────────────────────────────────────
PY=""
for candidate in python3 python; do
  if command -v "$candidate" &>/dev/null; then PY="$candidate"; break; fi
done

if [ -z "${PY:-}" ]; then
  echo "❌ Python not found. Please install Python 3.9+ first."
  exit 1
fi

echo "→ Using Python: $($PY --version 2>&1)"

# ─── Install strategy ────────────────────────────────────────────────

install_success=false

# Strategy 1: pipx (recommended — installs into an isolated environment)
if command -v pipx &>/dev/null; then
  echo "→ Installing ${PACKAGE} via pipx (isolated environment)..."
  pipx install "${PACKAGE}" && install_success=true
fi

# Strategy 2: pip install (standard)
if [ "$install_success" = false ]; then
  echo "→ Installing ${PACKAGE} via pip..."
  "$PY" -m pip install "${PACKAGE}" && install_success=true
fi

if [ "$install_success" = false ]; then
  echo "❌ Failed to install ${PACKAGE}."
  echo "   If pip failed due to PEP 668 (externally-managed-environment), try one of:"
  echo "     1. Install pipx first: apt install pipx / brew install pipx"
  echo "        Then: pipx install skillnet-ai"
  echo "     2. Use a venv: python3 -m venv .venv && .venv/bin/pip install skillnet-ai"
  echo "   Otherwise, ensure Python 3.9+ and pip or pipx are available."
  exit 1
fi

# ─── Verify ──────────────────────────────────────────────────────────
if command -v skillnet &>/dev/null; then
  echo "✅ skillnet CLI installed successfully."
  skillnet --help | head -5
else
  echo "✅ Package installed. If 'skillnet' is not on PATH, try:"
  echo "   $PY -m skillnet_ai.cli --help"
fi
