#!/usr/bin/env bash
set -euo pipefail

SKILL_NAME="case-analyzer"
TARGET_DIR="$HOME/.cursor/skills/$SKILL_NAME"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "Installing skill: $SKILL_NAME"
echo "  From: $SCRIPT_DIR"
echo "  To:   $TARGET_DIR"
echo ""

# Check dependencies
missing=()
command -v python3 >/dev/null 2>&1 || missing+=("python3")
command -v curl >/dev/null 2>&1 || missing+=("curl")
command -v zip >/dev/null 2>&1 || missing+=("zip")
command -v ffmpeg >/dev/null 2>&1 || missing+=("ffmpeg (optional, for video compression)")

if [ ${#missing[@]} -gt 0 ]; then
  echo "Missing dependencies:"
  for m in "${missing[@]}"; do
    echo "  - $m"
  done
  echo ""
fi

# Check uv
command -v uv >/dev/null 2>&1 || missing+=("uv (https://docs.astral.sh/uv/getting-started/installation/)")

# Install
mkdir -p "$TARGET_DIR"
cp -r "$SCRIPT_DIR"/SKILL.md "$TARGET_DIR/"
cp -r "$SCRIPT_DIR"/mcp-server.py "$TARGET_DIR/"
cp -r "$SCRIPT_DIR"/requirements.txt "$TARGET_DIR/"
cp -r "$SCRIPT_DIR"/templates "$TARGET_DIR/"
mkdir -p "$TARGET_DIR/scripts"
cp -r "$SCRIPT_DIR"/scripts/* "$TARGET_DIR/scripts/"
chmod +x "$TARGET_DIR/scripts/"*.sh "$TARGET_DIR/scripts/"*.py 2>/dev/null || true

# Update paths in SKILL.md to use personal dir
sed -i.bak 's|\.cursor/skills/case-analyzer|~/.cursor/skills/case-analyzer|g' "$TARGET_DIR/SKILL.md" 2>/dev/null || \
sed -i '' 's|\.cursor/skills/case-analyzer|~/.cursor/skills/case-analyzer|g' "$TARGET_DIR/SKILL.md"
rm -f "$TARGET_DIR/SKILL.md.bak"

echo "Installed successfully!"
echo ""

# Check env vars
env_ok=true
for var in LANGFUSE_PUBLIC_KEY LANGFUSE_SECRET_KEY LANGFUSE_HOST; do
  if [ -z "${!var:-}" ]; then
    env_ok=false
  fi
done

if [ "$env_ok" = false ]; then
  echo "Environment variables needed (add to ~/.zshrc or ~/.bashrc):"
  echo ""
  echo "  export LANGFUSE_PUBLIC_KEY=\"pk-lf-...\""
  echo "  export LANGFUSE_SECRET_KEY=\"sk-lf-...\""
  echo "  export LANGFUSE_HOST=\"https://cloud.langfuse.com\""
  echo "  export PEXO_ADMIN_TOKEN=\"eyJhbG...\"  # from admin.pexo.ai DevTools"
  echo ""
else
  echo "Langfuse credentials: OK"
  if [ -z "${PEXO_ADMIN_TOKEN:-}" ]; then
    echo "PEXO_ADMIN_TOKEN: not set (needed for upload, get from admin.pexo.ai DevTools)"
  else
    echo "PEXO_ADMIN_TOKEN: OK"
  fi
fi

echo ""
echo "=== MCP Server (for any agent) ==="
echo ""
echo "Add to your MCP client config (~/.cursor/mcp.json, Claude Desktop, etc.):"
echo ""
echo "  \"case-analyzer\": {"
echo "    \"command\": \"uv\","
echo "    \"args\": [\"run\", \"--script\", \"$TARGET_DIR/mcp-server.py\"]"
echo "  }"
echo ""
echo "Exposed tools: fetch_traces, extract_assets, upload_package, list_cases"
echo ""
echo "=== Cursor Skill ==="
echo ""
echo "In Cursor, say \"分析 case 31574785111\" to trigger the skill automatically."
echo "Or run scripts manually: python3 ~/.cursor/skills/$SKILL_NAME/scripts/fetch-case.py --help"
