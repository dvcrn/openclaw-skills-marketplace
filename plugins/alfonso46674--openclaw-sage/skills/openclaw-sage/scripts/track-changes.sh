#!/bin/bash
# Track changes to documentation by diffing sitemap snapshots
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/lib.sh"

SNAPSHOTS_DIR="${CACHE_DIR}/snapshots"

mkdir -p "$SNAPSHOTS_DIR"

get_current_pages() {
  local sitemap_xml="${CACHE_DIR}/sitemap.xml"
  if ! is_cache_fresh "$sitemap_xml" "$SITEMAP_TTL"; then
    local tmp
    tmp=$(mktemp)
    if curl -sf --max-time 10 "${DOCS_BASE_URL}/sitemap.xml" -o "$tmp" 2>/dev/null \
        && [ -s "$tmp" ]; then
      mv "$tmp" "$sitemap_xml"
    else
      rm -f "$tmp"
    fi
  fi
  grep -o '<loc>[^<]*</loc>' "$sitemap_xml" 2>/dev/null \
    | sed 's/<[^>]*>//g' \
    | grep "docs\.openclaw\.ai/" \
    | sed "s|${DOCS_BASE_URL}/||" \
    | grep -v '^$' \
    | sort
}

case "$1" in
  snapshot)
    if ! check_online; then
      echo "Offline: cannot reach ${DOCS_BASE_URL}" >&2
      echo "snapshot requires network access to fetch the current doc list." >&2
      exit 1
    fi
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    SNAPSHOT_FILE="${SNAPSHOTS_DIR}/${TIMESTAMP}.txt"
    echo "Fetching current doc list..." >&2
    get_current_pages > "$SNAPSHOT_FILE"
    COUNT=$(wc -l < "$SNAPSHOT_FILE")
    if [ "$COUNT" -eq 0 ]; then
      rm -f "$SNAPSHOT_FILE"
      echo "Error: Could not fetch sitemap. Snapshot not saved."
      exit 1
    fi
    echo "Snapshot saved: ${TIMESTAMP}  ($COUNT pages)"
    echo "File: $SNAPSHOT_FILE"
    ;;

  list)
    if ! ls "$SNAPSHOTS_DIR"/*.txt &>/dev/null 2>&1; then
      echo "No snapshots found."
      echo "Run: ./scripts/track-changes.sh snapshot"
      exit 0
    fi
    echo "Available snapshots:"
    echo ""
    for f in $(ls "$SNAPSHOTS_DIR"/*.txt | sort); do
      name=$(basename "$f" .txt)
      count=$(wc -l < "$f")
      # Format timestamp: 20260101_123456 → 2026-01-01 12:34:56
      date_fmt=$(echo "$name" | sed 's/\([0-9]\{4\}\)\([0-9]\{2\}\)\([0-9]\{2\}\)_\([0-9]\{2\}\)\([0-9]\{2\}\)\([0-9]\{2\}\)/\1-\2-\3 \4:\5:\6/')
      echo "  $date_fmt  ($count pages)  [$name]"
    done
    ;;

  since)
    if [ -z "$2" ]; then
      echo "Usage: track-changes.sh since <date>"
      echo "Example: track-changes.sh since 2026-01-01"
      exit 1
    fi

    # Normalize date to YYYYMMDD for comparison
    DATE_FILTER=$(echo "$2" | tr -d '-')

    if ! ls "$SNAPSHOTS_DIR"/*.txt &>/dev/null 2>&1; then
      echo "No snapshots found. Run: ./scripts/track-changes.sh snapshot"
      exit 1
    fi

    # Find the most recent snapshot before the given date
    BEFORE_SNAP=""
    for f in $(ls "$SNAPSHOTS_DIR"/*.txt | sort); do
      name=$(basename "$f" .txt)
      snap_date="${name%%_*}"
      if [ "$snap_date" -lt "$DATE_FILTER" ] 2>/dev/null; then
        BEFORE_SNAP="$f"
      fi
    done

    # Use current live state as "after"
    AFTER_TMP=$(mktemp)
    trap 'rm -f "$AFTER_TMP"' EXIT
    echo "Fetching current doc list for comparison..." >&2
    if ! check_online; then
      echo "Offline: cannot reach ${DOCS_BASE_URL}" >&2
      echo "Cannot fetch current doc list for comparison." >&2
      exit 1
    fi
    get_current_pages > "$AFTER_TMP"

    if [ -z "$BEFORE_SNAP" ]; then
      # No snapshot before the date — use oldest available snapshot
      BEFORE_SNAP=$(ls "$SNAPSHOTS_DIR"/*.txt | sort | head -1)
      before_label="oldest snapshot ($(basename "$BEFORE_SNAP" .txt))"
    else
      before_label="snapshot from $(basename "$BEFORE_SNAP" .txt | sed 's/\([0-9]\{4\}\)\([0-9]\{2\}\)\([0-9]\{2\}\)_\([0-9]\{2\}\)\([0-9]\{2\}\)\([0-9]\{2\}\)/\1-\2-\3/')"
    fi

    added=$(comm -13 "$BEFORE_SNAP" "$AFTER_TMP")
    removed=$(comm -23 "$BEFORE_SNAP" "$AFTER_TMP")

    echo "Changes since $2  (comparing $before_label → now):"
    echo ""

    if [ -n "$added" ]; then
      echo "=== Added ==="
      echo "$added" | sed 's/^/  + /'
    else
      echo "=== Added === (none)"
    fi

    echo ""

    if [ -n "$removed" ]; then
      echo "=== Removed ==="
      echo "$removed" | sed 's/^/  - /'
    else
      echo "=== Removed === (none)"
    fi
    ;;

  diff)
    # Compare two named snapshots directly
    if [ -z "$2" ] || [ -z "$3" ]; then
      echo "Usage: track-changes.sh diff <snapshot1> <snapshot2>"
      echo "Run 'list' to see available snapshot names."
      exit 1
    fi
    F1="${SNAPSHOTS_DIR}/$2.txt"
    F2="${SNAPSHOTS_DIR}/$3.txt"
    [ -f "$F1" ] || { echo "Snapshot not found: $2"; exit 1; }
    [ -f "$F2" ] || { echo "Snapshot not found: $3"; exit 1; }

    echo "Diff: $2 → $3"
    echo ""
    echo "=== Added ==="
    comm -13 "$F1" "$F2" | sed 's/^/  + /'
    echo ""
    echo "=== Removed ==="
    comm -23 "$F1" "$F2" | sed 's/^/  - /'
    ;;

  *)
    echo "Usage: track-changes.sh {snapshot|list|since <date>|diff <snap1> <snap2>}"
    exit 1
    ;;
esac
