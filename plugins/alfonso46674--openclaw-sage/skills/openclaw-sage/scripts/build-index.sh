#!/bin/bash
# Full-text index management for offline search
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/lib.sh"

INDEX_FILE="${CACHE_DIR}/index.txt"
SITEMAP_XML="${CACHE_DIR}/sitemap.xml"

case "$1" in
  fetch)
    echo "Downloading all docs..."

    if ! check_online; then
      echo "Offline: cannot reach ${DOCS_BASE_URL}" >&2
      echo "fetch requires network access. Run build-index.sh status to see cached docs." >&2
      exit 1
    fi

    # Ensure sitemap XML is available
    if [ ! -f "$SITEMAP_XML" ]; then
      echo "Fetching sitemap first..." >&2
      curl -sf --max-time 10 "${DOCS_BASE_URL}/sitemap.xml" -o "$SITEMAP_XML" 2>/dev/null
    fi

    ALL_URLS=$(grep -o '<loc>[^<]*</loc>' "$SITEMAP_XML" 2>/dev/null | sed 's/<[^>]*>//g' | grep "${DOCS_BASE_URL}/" | grep -v "^${DOCS_BASE_URL}/$")

    # Show available languages in the sitemap
    # Language prefix format: "ll/" or "ll-RR/" (e.g. zh-CN/, pt-BR/)
    available_langs=$(echo "$ALL_URLS" | awk -v base_url="$DOCS_BASE_URL" '
      {
        path = $0
        sub(base_url "/", "", path)
        if (match(path, /^[a-z][a-z](-[A-Za-z]+)?\//))
          lang = substr(path, 1, RLENGTH - 1)
        else
          lang = "en"
        langs[lang]++
      }
      END { for (l in langs) printf "%s (%d docs)  ", l, langs[l]; print "" }
    ')
    echo "Languages in sitemap: $available_langs" >&2
    echo "Fetching language(s): $LANGS  (override with OPENCLAW_SAGE_LANGS=en,zh or =all)" >&2

    # Filter URLs by language.
    # LANGS is matched against the base 2-letter code so "zh" catches "zh-CN", "zh-TW", etc.
    if [ "$LANGS" = "all" ]; then
      URLS="$ALL_URLS"
    else
      URLS=$(echo "$ALL_URLS" | awk -v langs=",$LANGS," -v base_url="$DOCS_BASE_URL" '
        {
          url = $0
          sub(base_url "/", "", url)
          if (match(url, /^[a-z][a-z](-[A-Za-z]+)?\//))
            lang = substr(url, 1, 2)   # base code only: "zh-CN" → "zh"
          else
            lang = "en"
          if (index(langs, "," lang ",") > 0) print $0
        }
      ')
    fi

    if [ -z "$URLS" ]; then
      echo "Error: Could not get URL list from sitemap. Run ./scripts/sitemap.sh first." >&2
      exit 1
    fi

    total=$(echo "$URLS" | wc -l)
    count=0
    new=0

    while IFS= read -r url; do
      path=$(echo "$url" | sed "s|${DOCS_BASE_URL}/||")
      [ -z "$path" ] && continue
      cache_file="${CACHE_DIR}/doc_$(echo "$path" | tr '/' '_').txt"
      count=$((count + 1))
      printf "\r  [%d/%d] %s          " "$count" "$total" "$path" >&2

      if [ ! -f "$cache_file" ] || ! is_cache_fresh "$cache_file" "$DOC_TTL"; then
        safe="$(echo "$path" | tr '/' '_')"
        if fetch_and_cache "$url" "$safe"; then
          new=$((new + 1))
        fi
        sleep 0.3  # be polite to the server
      fi
    done <<< "$URLS"

    printf "\n" >&2
    cached=$(ls "$CACHE_DIR"/doc_*.txt 2>/dev/null | wc -l)
    echo "Done. $new new docs fetched, $cached total cached."
    echo "Next: run './scripts/build-index.sh build' to index them."
    ;;

  build)
    echo "Building search index..."
    if ! ls "$CACHE_DIR"/doc_*.txt &>/dev/null 2>&1; then
      echo "No docs cached. Run: ./scripts/build-index.sh fetch first."
      exit 1
    fi

    : > "$INDEX_FILE"
    doc_count=0
    for f in "$CACHE_DIR"/doc_*.txt; do
      path=$(basename "$f" .txt | sed 's/^doc_//; s/_/\//g')
      grep -v '^[[:space:]]*$' "$f" | while IFS= read -r line; do
        echo "${path}|${line}"
      done >> "$INDEX_FILE"
      doc_count=$((doc_count + 1))
    done

    line_count=$(wc -l < "$INDEX_FILE")
    echo "Index built: $doc_count docs, $line_count lines."

    if command -v python3 &>/dev/null; then
      echo "Building BM25 meta..." >&2
      python3 "$SCRIPT_DIR/bm25_search.py" build-meta "$INDEX_FILE"
    fi

    echo "Location: $INDEX_FILE"
    echo "Search with: ./scripts/build-index.sh search <query>"
    ;;

  search)
    shift
    if [ -z "$*" ]; then
      echo "Usage: build-index.sh search <query>"
      exit 1
    fi
    QUERY="$*"

    if [ ! -f "$INDEX_FILE" ]; then
      echo "No index found. Run:"
      echo "  ./scripts/build-index.sh fetch"
      echo "  ./scripts/build-index.sh build"
      exit 1
    fi

    echo "Search results for: $QUERY"
    echo ""

    if command -v python3 &>/dev/null; then
      python3 "$SCRIPT_DIR/bm25_search.py" search "$INDEX_FILE" "$QUERY" \
        | while IFS='|' read -r score path excerpt; do
            score=$(echo "$score" | tr -d ' ')
            path=$(echo "$path" | tr -d ' ')
            excerpt=$(echo "$excerpt" | sed 's/^[[:space:]]*//')
            echo "  [$score] $path  ->  ${DOCS_BASE_URL}/$path"
            echo "          $excerpt"
            echo ""
          done
    else
      # grep fallback when python3 unavailable
      grep -i "$QUERY" "$INDEX_FILE" \
        | awk -F'|' -v base_url="$DOCS_BASE_URL" '
            {
              if ($1 != prev) {
                if (prev != "") print ""
                print "  [---] " $1 "  ->  " base_url "/" $1
                prev = $1
                count = 0
              }
              if (count < 4) {
                gsub(/^[[:space:]]+/, "", $2)
                print "        " $2
                count++
              }
            }
          ' \
        | head -80
      echo ""
      echo "Note: Install python3 for ranked BM25 results."
    fi

    match_count=$(grep -ic "$QUERY" "$INDEX_FILE" 2>/dev/null || echo 0)
    echo "($match_count matching lines across all docs)"
    ;;

  status)
    doc_count=$(ls "$CACHE_DIR"/doc_*.txt 2>/dev/null | wc -l)
    echo "Cached docs: $doc_count"
    if [ -f "$INDEX_FILE" ]; then
      line_count=$(wc -l < "$INDEX_FILE")
      echo "Index:       $line_count lines  ($INDEX_FILE)"
      META_FILE="${CACHE_DIR}/index_meta.json"
      if [ -f "$META_FILE" ]; then
        echo "BM25 meta:   present"
      else
        echo "BM25 meta:   not built (run 'build' to generate)"
      fi
    else
      echo "Index:       not built"
    fi
    ;;

  *)
    echo "Usage: build-index.sh {fetch|build|search <query>|status}"
    ;;
esac
