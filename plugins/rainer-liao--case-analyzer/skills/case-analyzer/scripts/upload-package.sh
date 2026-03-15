#!/usr/bin/env bash
set -euo pipefail

ADMIN_API="https://admin.pexo.ai/api/strategy-packages"

usage() {
  cat <<EOF
Upload a case analysis package to the Pexo strategy-optimizer.

Usage:
  $(basename "$0") <case_id> <dashboard_dir> [options]

Arguments:
  case_id          Case / conversation ID (e.g. 31574785111)
  dashboard_dir    Directory containing the dashboard HTML + media/
                   Expected structure:
                     <dashboard_dir>/
                       qa-report.html   (or specify with --entry)
                       media/
                         *.png *.mp4 *.mp3 ...

Options:
  --entry FILE     Entry HTML filename (default: qa-report.html)
  --desc TEXT      Package description (default: empty)
  --token TOKEN    Bearer token (or set PEXO_ADMIN_TOKEN env var)
  --dry-run        Package only, don't upload

Examples:
  # Using env var for auth:
  export PEXO_ADMIN_TOKEN="eyJhbG..."
  $(basename "$0") 31574785111 /path/to/31574785111/

  # Inline token:
  $(basename "$0") 31574785111 ./output/ --token "eyJhbG..."

  # Custom entry file:
  $(basename "$0") 36982977449 ./output/ --entry analysis.html
EOF
  exit 1
}

[[ $# -lt 2 ]] && usage

CASE_ID="$1"
DASHBOARD_DIR="$2"
shift 2

ENTRY_FILE="qa-report.html"
DESCRIPTION=""
TOKEN="${PEXO_ADMIN_TOKEN:-}"
DRY_RUN=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --entry)   ENTRY_FILE="$2"; shift 2 ;;
    --desc)    DESCRIPTION="$2"; shift 2 ;;
    --token)   TOKEN="$2"; shift 2 ;;
    --dry-run) DRY_RUN=true; shift ;;
    *)         echo "Unknown option: $1"; usage ;;
  esac
done

if [[ -z "$TOKEN" && "$DRY_RUN" == "false" ]]; then
  echo "Error: No auth token. Set PEXO_ADMIN_TOKEN or use --token."
  exit 1
fi

if [[ ! -f "$DASHBOARD_DIR/$ENTRY_FILE" ]]; then
  echo "Error: Entry file not found: $DASHBOARD_DIR/$ENTRY_FILE"
  exit 1
fi

WORK_DIR=$(mktemp -d)
PACKAGE_DIR="$WORK_DIR/$CASE_ID"
ZIP_PATH="$WORK_DIR/${CASE_ID}-strategy-package.zip"

trap 'rm -rf "$WORK_DIR"' EXIT

echo "Packaging $CASE_ID ..."
mkdir -p "$PACKAGE_DIR"
cp "$DASHBOARD_DIR/$ENTRY_FILE" "$PACKAGE_DIR/$ENTRY_FILE"
if [ -d "$DASHBOARD_DIR/media" ]; then
  cp -r "$DASHBOARD_DIR/media" "$PACKAGE_DIR/media"
fi

FILE_COUNT=$(find "$PACKAGE_DIR" -type f | wc -l | tr -d ' ')
TOTAL_SIZE=$(du -sh "$PACKAGE_DIR" | cut -f1)
echo "  $FILE_COUNT files, $TOTAL_SIZE total"

cd "$WORK_DIR"
zip -r -q "$ZIP_PATH" "$CASE_ID/"
ZIP_SIZE=$(du -sh "$ZIP_PATH" | cut -f1)
echo "  ZIP: $ZIP_SIZE → $ZIP_PATH"

if [[ "$DRY_RUN" == "true" ]]; then
  FINAL_ZIP="/tmp/${CASE_ID}-strategy-package.zip"
  cp "$ZIP_PATH" "$FINAL_ZIP"
  echo ""
  echo "Dry run complete. ZIP saved to: $FINAL_ZIP"
  exit 0
fi

echo ""
echo "Uploading to $ADMIN_API ..."

RESPONSE=$(curl -s -w "\n%{http_code}" \
  -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -F "sourceType=zip" \
  -F "name=$CASE_ID" \
  -F "entryFile=$CASE_ID/$ENTRY_FILE" \
  -F "description=$DESCRIPTION" \
  -F "archive=@$ZIP_PATH;type=application/zip" \
  "$ADMIN_API")

HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [[ "$HTTP_CODE" == "201" || "$HTTP_CODE" == "200" ]]; then
  PACKAGE_ID=$(echo "$BODY" | python3 -c "import sys,json; print(json.load(sys.stdin)['body']['id'])" 2>/dev/null || echo "?")
  PREVIEW_URL=$(echo "$BODY" | python3 -c "import sys,json; print(json.load(sys.stdin)['body']['previewUrl'])" 2>/dev/null || echo "?")

  echo ""
  echo "Upload successful!"
  echo "  Package ID: $PACKAGE_ID"
  echo "  Preview:    https://admin.pexo.ai$PREVIEW_URL"
  echo "  Dashboard:  https://admin.pexo.ai/ai-workshop/strategy-optimizer"
else
  echo ""
  echo "Upload failed (HTTP $HTTP_CODE):"
  echo "$BODY"
  exit 1
fi
