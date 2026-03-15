#!/bin/bash
# Search docs by keyword
# Usage: search.sh [--json] <keyword...>

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/lib.sh"

# Parse flags
JSON=false
[[ "${OPENCLAW_SAGE_OUTPUT}" == "json" ]] && JSON=true
ARGS=()
for arg in "$@"; do
  case "$arg" in
    --json) JSON=true ;;
    *) ARGS+=("$arg") ;;
  esac
done
KEYWORD="${ARGS[*]}"

if [ -z "$KEYWORD" ]; then
  echo "Usage: search.sh [--json] <keyword>"
  exit 1
fi

SITEMAP_CACHE="${CACHE_DIR}/sitemap.txt"
INDEX_FILE="${CACHE_DIR}/index.txt"

# --- JSON output path ---
if $JSON; then
  if ! command -v python3 &>/dev/null; then
    echo '{"error": "python3 required for --json output"}' >&2
    exit 1
  fi
  python3 - "$INDEX_FILE" "$KEYWORD" "$DOCS_BASE_URL" \
              "$SCRIPT_DIR/bm25_search.py" "$SITEMAP_CACHE" "$CACHE_DIR" <<'PYEOF'
import sys, json, os, subprocess

index_file    = sys.argv[1]
keyword       = sys.argv[2]
base_url      = sys.argv[3]
bm25_script   = sys.argv[4]
sitemap_cache = sys.argv[5]
cache_dir     = sys.argv[6]

results = []
mode = None

# 1. BM25 ranked search
if os.path.exists(index_file):
    proc = subprocess.run(['python3', bm25_script, 'search', index_file, keyword],
                          capture_output=True, text=True)
    for line in proc.stdout.strip().splitlines():
        parts = line.split(' | ', 2)
        if len(parts) == 3:
            score_str, path, excerpt = parts
            results.append({
                'score': float(score_str.strip()),
                'path': path.strip(),
                'url': f'{base_url}/{path.strip()}',
                'excerpt': excerpt.strip(),
            })
    mode = 'bm25'

# 2. grep fallback on individually cached docs
elif any(f.startswith('doc_') and f.endswith('.txt')
         for f in os.listdir(cache_dir)):
    kw = keyword.lower()
    for fname in sorted(os.listdir(cache_dir)):
        if not (fname.startswith('doc_') and fname.endswith('.txt')):
            continue
        fpath = os.path.join(cache_dir, fname)
        path = fname[4:-4].replace('_', '/')
        try:
            with open(fpath, encoding='utf-8', errors='replace') as f:
                for line in f:
                    if kw in line.lower():
                        results.append({
                            'score': None,
                            'path': path,
                            'url': f'{base_url}/{path}',
                            'excerpt': line.strip(),
                        })
                        break
        except Exception:
            pass
    mode = 'grep'

# 3. Sitemap path matches
sitemap_matches = []
if os.path.exists(sitemap_cache):
    kw = keyword.lower()
    with open(sitemap_cache) as f:
        for line in f:
            if kw in line.lower() and line.strip().startswith('-'):
                path = line.strip().lstrip('- ').strip()
                sitemap_matches.append({'path': path, 'url': f'{base_url}/{path}'})

out = {
    'query': keyword,
    'mode': mode or 'sitemap-only',
    'results': results,
}
if sitemap_matches:
    out['sitemap_matches'] = sitemap_matches

print(json.dumps(out, indent=2))
PYEOF
  exit 0
fi

# --- Human-readable output ---
echo "Searching docs for: $KEYWORD"
echo ""

found=0

# 1. BM25 ranked search
if [ -f "$INDEX_FILE" ] && command -v python3 &>/dev/null; then
  echo "=== Full-text index matches (BM25 ranked) ==="
  python3 "$SCRIPT_DIR/bm25_search.py" search "$INDEX_FILE" "$KEYWORD" \
    | while IFS='|' read -r score path excerpt; do
        score=$(echo "$score" | tr -d ' ')
        path=$(echo "$path" | tr -d ' ')
        excerpt=$(echo "$excerpt" | sed 's/^[[:space:]]*//')
        echo "  [$score] $path  ->  ${DOCS_BASE_URL}/$path"
        echo "          $excerpt"
        echo ""
      done
  echo ""
  found=1

elif [ -f "$INDEX_FILE" ]; then
  echo "=== Full-text index matches ==="
  echo "Note: Install python3 for ranked BM25 results."
  echo ""
  grep -i "$KEYWORD" "$INDEX_FILE" \
    | awk -F'|' -v base_url="$DOCS_BASE_URL" '
        {
          if ($1 != prev) {
            print ""
            print "  [---] " $1 "  ->  " base_url "/" $1
            prev = $1; count = 0
          }
          if (count < 3) { gsub(/^[[:space:]]+/, "", $2); print "        " $2; count++ }
        }
      ' \
    | head -60
  echo ""
  found=1

elif ls "$CACHE_DIR"/doc_*.txt &>/dev/null 2>&1; then
  echo "=== Cached doc matches ==="
  echo "Note: Run './scripts/build-index.sh build' for ranked BM25 results."
  echo ""
  grep -ril "$KEYWORD" "$CACHE_DIR"/doc_*.txt 2>/dev/null | while IFS= read -r f; do
    path=$(basename "$f" .txt | sed 's/^doc_//; s/_/\//g')
    echo "  [---] $path  ->  ${DOCS_BASE_URL}/$path"
    grep -i "$KEYWORD" "$f" | head -3 | sed 's/^[[:space:]]*/        /'
    echo ""
  done
  found=1
fi

# Sitemap path matches
if [ -f "$SITEMAP_CACHE" ]; then
  matches=$(grep -i "$KEYWORD" "$SITEMAP_CACHE" | grep '^\s*-')
  if [ -n "$matches" ]; then
    echo "=== Matching doc paths ==="
    echo "$matches" | head -15 | sed 's/^[[:space:]]*/  /'
    echo ""
  fi
fi

if [ "$found" -eq 0 ]; then
  echo "No cached content to search. Options:"
  echo "  1. Fetch a specific doc:  ./scripts/fetch-doc.sh <path>"
  echo "  2. Download all docs:     ./scripts/build-index.sh fetch"
  echo "  3. Build search index:    ./scripts/build-index.sh build"
fi

echo "Tip: For comprehensive ranked results:" >&2
echo "  ./scripts/build-index.sh fetch && ./scripts/build-index.sh build" >&2
echo "  ./scripts/build-index.sh search \"$KEYWORD\"" >&2
