#!/bin/bash
# Show recently updated docs by parsing sitemap lastmod dates
DAYS=${1:-7}
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/lib.sh"

# BUG-09: validate $DAYS after lib.sh is sourced
if ! [[ "$DAYS" =~ ^[0-9]+$ ]]; then
  echo "Usage: recent.sh [days]" >&2
  echo "  days must be a positive integer (default: 7)" >&2
  exit 1
fi

SITEMAP_XML="${CACHE_DIR}/sitemap.xml"

# Fetch sitemap XML if not cached or stale (BUG-08: use TTL instead of existence check)
if ! is_cache_fresh "$SITEMAP_XML" "$SITEMAP_TTL"; then
  if check_online; then
    echo "Fetching sitemap..." >&2
    curl -sf --max-time 10 "${DOCS_BASE_URL}/sitemap.xml" -o "$SITEMAP_XML" 2>/dev/null
  else
    echo "Offline: cannot reach ${DOCS_BASE_URL}" >&2
  fi
fi

echo "=== Docs updated at source in the last $DAYS days ==="
echo ""

if [ -f "$SITEMAP_XML" ]; then
  # Parse lastmod dates using python3 (widely available)
  python3 - "$SITEMAP_XML" "$DAYS" "$DOCS_BASE_URL" <<'PYEOF'
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone

sitemap_file = sys.argv[1]
days = int(sys.argv[2])
base_url = sys.argv[3]

try:
    tree = ET.parse(sitemap_file)
    root = tree.getroot()
    # Handle namespace
    ns = {'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    recent = []
    for url in root.findall('.//sm:url', ns):
        loc = url.find('sm:loc', ns)
        lastmod = url.find('sm:lastmod', ns)
        if loc is not None and lastmod is not None and lastmod.text:
            try:
                dt_str = lastmod.text.strip()[:10]
                dt = datetime.fromisoformat(dt_str).replace(tzinfo=timezone.utc)
                if dt >= cutoff:
                    path = loc.text.replace(base_url + '/', '')
                    recent.append((dt, path))
            except Exception:
                pass
    recent.sort(reverse=True)
    if recent:
        for dt, path in recent:
            print(f"  {dt.strftime('%Y-%m-%d')}  {path}")
    else:
        print(f"  No docs with lastmod dates in the last {days} days found in sitemap.")
        print("  (The sitemap may not include lastmod dates for all pages.)")
except Exception as e:
    print(f"  Could not parse sitemap: {e}")
    sys.exit(1)
PYEOF

  if [ $? -ne 0 ]; then
    echo "  Falling back to grep-based date search..." >&2
    grep -A1 '<lastmod>' "$SITEMAP_XML" | grep -v '^--$' | \
      paste - - | \
      awk -v days="$DAYS" '
        {
          gsub(/<[^>]*>/, "", $0)
          gsub(/^[[:space:]]+|[[:space:]]+$/, "", $0)
          split($0, a, /[[:space:]]+/)
          print a[1], a[2]
        }
      ' | head -20
  fi
else
  echo "  Sitemap not available. Could not check recent changes."
  echo "  Try running: ./scripts/sitemap.sh"
fi

echo ""
echo "=== Recently accessed locally (last $DAYS days) ==="
echo ""

found=0
while IFS= read -r f; do
  path=$(basename "$f" .txt | sed 's/^doc_//; s/_/\//g')
  echo "  $path"
  found=1
done < <(find "$CACHE_DIR" -name "doc_*.txt" -mtime "-${DAYS}" 2>/dev/null)

if [ "$found" -eq 0 ]; then
  echo "  (none — fetch docs with ./scripts/fetch-doc.sh <path>)"
fi
