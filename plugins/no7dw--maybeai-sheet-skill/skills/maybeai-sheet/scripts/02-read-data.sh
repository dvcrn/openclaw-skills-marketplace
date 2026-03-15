#!/usr/bin/env bash
# MaybeAI Sheet — Reading Data
# Usage: export MAYBEAI_API_TOKEN=your_token_here
#        export DOC_ID=your_document_id_here
#        bash 02-read-data.sh

BASE_URL="${BASE_URL:-https://play-be.omnimcp.ai}"
TOKEN="${MAYBEAI_API_TOKEN:?Please set MAYBEAI_API_TOKEN}"
DOC_ID="${DOC_ID:?Please set DOC_ID}"

# ── Get Spreadsheet Data as JSON ─────────────────────────────────────────────
# ?gid= selects the worksheet by index (0 = first sheet)
echo "=== Get Spreadsheet Data (JSON) ==="
curl -s "$BASE_URL/api/v1/excel/spreadsheets/$DOC_ID?gid=0" \
  | jq .

# ── View Spreadsheet as HTML ─────────────────────────────────────────────────
echo "=== Spreadsheet HTML preview URL ==="
echo "$BASE_URL/api/v1/excel/spreadsheets/d/$DOC_ID"

# ── List Worksheets ───────────────────────────────────────────────────────────
echo "=== List Worksheets ==="
curl -s -X POST "$BASE_URL/api/v1/excel/list_worksheets" \
  -H "Content-Type: application/json" \
  -d "{\"uri\": \"$DOC_ID\"}" \
  | jq .

# ── List Worksheets with Version Info ────────────────────────────────────────
echo "=== List Worksheets (with versions) ==="
curl -s -X POST "$BASE_URL/api/v1/excel/list_worksheets_version" \
  -H "Content-Type: application/json" \
  -d "{\"uri\": \"$DOC_ID\"}" \
  | jq .

# ── Read Sheet ────────────────────────────────────────────────────────────────
echo "=== Read Sheet ==="
curl -s -X POST "$BASE_URL/api/v1/excel/read_sheet" \
  -H "Content-Type: application/json" \
  -d "{\"uri\": \"$DOC_ID\", \"sheet\": \"Sheet1\"}" \
  | jq .

# ── Read Headers ─────────────────────────────────────────────────────────────
echo "=== Read Headers ==="
curl -s -X POST "$BASE_URL/api/v1/excel/read_headers" \
  -H "Content-Type: application/json" \
  -d "{\"uri\": \"$DOC_ID\", \"sheet\": \"Sheet1\"}" \
  | jq .

# ── List Versions ─────────────────────────────────────────────────────────────
echo "=== List Versions ==="
curl -s -X POST "$BASE_URL/api/v1/excel/list_versions" \
  -H "Content-Type: application/json" \
  -d "{\"uri\": \"$DOC_ID\"}" \
  | jq .

# ── Read a Specific Version ───────────────────────────────────────────────────
echo "=== Read Version ==="
curl -s -X POST "$BASE_URL/api/v1/excel/read_version" \
  -H "Content-Type: application/json" \
  -d "{\"uri\": \"$DOC_ID\", \"version\": \"v1\"}" \
  | jq .
