#!/bin/bash
# Fetch a specific doc and display as readable text
# Usage: fetch-doc.sh <path> [--toc] [--section <heading>] [--max-lines <n>]

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/lib.sh"

if [ -z "$1" ] || [[ "$1" == --* ]]; then
  echo "Usage: fetch-doc.sh <path> [--toc] [--section <heading>] [--max-lines <n>]"
  echo "  fetch-doc.sh gateway/configuration"
  echo "  fetch-doc.sh gateway/configuration --toc"
  echo "  fetch-doc.sh gateway/configuration --section 'Retry Settings'"
  echo "  fetch-doc.sh gateway/configuration --max-lines 50"
  exit 1
fi

DOC_PATH="${1#/}"
shift

MODE="text"
MAX_LINES=""
SECTION=""

while [ $# -gt 0 ]; do
  case "$1" in
    --toc)       MODE="toc" ;;
    --section)   shift; MODE="section"; SECTION="$1" ;;
    --max-lines) shift; MAX_LINES="$1" ;;
    *) echo "Unknown option: $1" >&2; exit 1 ;;
  esac
  shift
done

SAFE_PATH="$(echo "$DOC_PATH" | tr '/' '_')"
CACHE_FILE="${CACHE_DIR}/doc_${SAFE_PATH}.txt"
HTML_CACHE="${CACHE_DIR}/doc_${SAFE_PATH}.html"
URL="${DOCS_BASE_URL}/${DOC_PATH}"

# Fetch doc using the shared lib.sh fetch_and_cache, with fetch-doc-specific error handling
_do_fetch() {
  echo "Fetching: $URL" >&2
  if ! fetch_and_cache "$URL" "$SAFE_PATH"; then
    echo "Error: Failed to fetch: $URL" >&2
    echo "Check the path is valid. Run ./scripts/sitemap.sh to see available docs." >&2
    exit 1
  fi
}

# Ensure plain text is fresh
if ! is_cache_fresh "$CACHE_FILE" "$DOC_TTL"; then
  if ! check_online; then
    echo "Offline: cannot reach ${DOCS_BASE_URL}" >&2
    if [ -f "$CACHE_FILE" ]; then
      echo "Using stale cached content for: $DOC_PATH" >&2
    else
      echo "No cache for: $DOC_PATH — attempting fetch anyway" >&2
      _do_fetch
    fi
  else
    _do_fetch
  fi
fi

# --toc / --section need HTML; backfill if cache predates this feature
if [[ "$MODE" == toc || "$MODE" == section ]] && [ ! -f "$HTML_CACHE" ]; then
  if check_online; then
    echo "Fetching HTML for section extraction..." >&2
    curl -sf --max-time 15 "$URL" -o "$HTML_CACHE" 2>/dev/null
  else
    echo "Offline: cannot fetch HTML for $DOC_PATH — fetch while online first." >&2
    exit 1
  fi
fi

case "$MODE" in
  toc)
    if ! command -v python3 &>/dev/null || [ ! -f "$HTML_CACHE" ]; then
      echo "Error: --toc requires python3 and a fetched cache (run without --toc first)." >&2
      exit 1
    fi
    python3 - "$HTML_CACHE" <<'PYEOF'
import sys, re
with open(sys.argv[1], encoding='utf-8', errors='replace') as f:
    html = f.read()
headings = [(int(m.group(1)[1]), re.sub(r'<[^>]+>', '', m.group(2)).strip())
            for m in re.finditer(r'<(h[1-6])[^>]*>(.*?)</\1>', html, re.I|re.S)]
for lvl, txt in headings:
    if txt:
        print('  ' * (lvl - 1) + txt)
PYEOF
    ;;

  section)
    if [ -z "$SECTION" ]; then
      echo "Error: --section requires a heading name. Use --toc first to list sections." >&2
      exit 1
    fi
    if ! command -v python3 &>/dev/null || [ ! -f "$HTML_CACHE" ]; then
      echo "Error: --section requires python3 and a fetched cache (run without flags first)." >&2
      exit 1
    fi
    python3 - "$HTML_CACHE" "$SECTION" <<'PYEOF'
import sys, re, html as html_module

with open(sys.argv[1], encoding='utf-8', errors='replace') as f:
    raw = f.read()
query = sys.argv[2].lower()

headings = [(m.start(), int(m.group(1)[1]),
             re.sub(r'<[^>]+>', '', m.group(3)).strip())
            for m in re.compile(r'<(h[1-6])([^>]*)>(.*?)</\1>', re.I|re.S).finditer(raw)]
headings = [(pos, lvl, txt) for pos, lvl, txt in headings if txt]

if not headings:
    print("No headings found in document.", file=sys.stderr)
    sys.exit(1)

match_idx = next((i for i, (_, _, txt) in enumerate(headings)
                  if query in txt.lower()), None)

if match_idx is None:
    print(f"Section not found: {sys.argv[2]}", file=sys.stderr)
    print("Available sections (--toc to view):", file=sys.stderr)
    for _, lvl, txt in headings:
        print(f"  {'  ' * (lvl-1)}{txt}", file=sys.stderr)
    sys.exit(1)

start_pos, current_level = headings[match_idx][0], headings[match_idx][1]
end_pos = next((headings[i][0] for i in range(match_idx + 1, len(headings))
                if headings[i][1] <= current_level), len(raw))

section_html = raw[start_pos:end_pos]
text = re.sub(r'<script[^>]*>.*?</script>', '', section_html, flags=re.I|re.S)
text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.I|re.S)
text = re.sub(r'<[^>]+>', '', text)
text = html_module.unescape(text)
print('\n'.join(l.strip() for l in text.splitlines() if l.strip()))
PYEOF
    ;;

  text)
    if [ -n "$MAX_LINES" ]; then
      head -n "$MAX_LINES" "$CACHE_FILE"
    else
      cat "$CACHE_FILE"
    fi
    ;;
esac
