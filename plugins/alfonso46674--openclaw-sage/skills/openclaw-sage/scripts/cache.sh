#!/bin/bash
# Cache management for OpenClaw docs
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/lib.sh"

SITEMAP_CACHE="${CACHE_DIR}/sitemap.txt"

case "$1" in
  status)
    if [ -f "$SITEMAP_CACHE" ]; then
      if is_cache_fresh "$SITEMAP_CACHE" "$SITEMAP_TTL"; then
        local_mtime=""
        if [[ "$OSTYPE" == "darwin"* ]]; then
          local_mtime=$(stat -f %m "$SITEMAP_CACHE")
        else
          local_mtime=$(stat -c %Y "$SITEMAP_CACHE")
        fi
        cached_at=$(date -d "@${local_mtime}" 2>/dev/null || date -r "$local_mtime" 2>/dev/null)
        echo "Cache status: FRESH"
        echo "Location:     $CACHE_DIR"
        echo "Cached at:    ${cached_at}"
        doc_count=$(ls "$CACHE_DIR"/doc_*.txt 2>/dev/null | wc -l)
        echo "Cached docs:  $doc_count"
      else
        echo "Cache status: STALE"
        echo "Run: ./scripts/cache.sh refresh"
      fi
    else
      echo "Cache status: EMPTY"
      echo "Run: ./scripts/sitemap.sh to populate"
    fi
    echo ""
    echo "TTL config (override with env vars):"
    echo "  Sitemap: ${SITEMAP_TTL}s  (OPENCLAW_SAGE_SITEMAP_TTL)"
    echo "  Docs:    ${DOC_TTL}s  (OPENCLAW_SAGE_DOC_TTL)"
    echo "  Dir:     ${CACHE_DIR}  (OPENCLAW_SAGE_CACHE_DIR)"
    ;;
  refresh)
    echo "Forcing cache refresh..."
    rm -f "${CACHE_DIR}/sitemap.txt" "${CACHE_DIR}/sitemap.xml"
    echo "Sitemap cache cleared. Next sitemap.sh call will re-fetch."
    echo "(Cached docs preserved. Delete ${CACHE_DIR}/doc_*.txt to clear them.)"
    ;;
  clear-docs)
    count=$(ls "$CACHE_DIR"/doc_*.txt 2>/dev/null | wc -l)
    rm -f "${CACHE_DIR}"/doc_*.txt "${CACHE_DIR}"/doc_*.html "${CACHE_DIR}/index.txt" "${CACHE_DIR}/index_meta.json"
    echo "Cleared $count cached docs and index."
    ;;
  dir)
    echo "$CACHE_DIR"
    ;;
  *)
    echo "Usage: cache.sh {status|refresh|clear-docs|dir}"
    ;;
esac
