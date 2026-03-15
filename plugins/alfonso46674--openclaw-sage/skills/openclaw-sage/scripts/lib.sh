#!/bin/bash
# Shared utilities for openclaw-sage scripts

SITEMAP_TTL="${OPENCLAW_SAGE_SITEMAP_TTL:-3600}"    # 1hr default
DOC_TTL="${OPENCLAW_SAGE_DOC_TTL:-86400}"           # 24hr default
LANGS="${OPENCLAW_SAGE_LANGS:-en}"                  # comma-separated lang codes, or "all"
_LIB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CACHE_DIR="${OPENCLAW_SAGE_CACHE_DIR:-${_LIB_DIR}/../.cache/openclaw-sage}"
DOCS_BASE_URL="${OPENCLAW_SAGE_DOCS_BASE_URL:-https://docs.openclaw.ai}"

mkdir -p "$CACHE_DIR"

# check_online — returns 0 if DOCS_BASE_URL is reachable, 1 if not
check_online() {
  curl -sf --max-time 2 -o /dev/null -I "$DOCS_BASE_URL" 2>/dev/null
}

# is_cache_fresh <file> <ttl_seconds>
is_cache_fresh() {
  local file="$1" ttl="$2"
  [ -f "$file" ] || return 1
  local now mtime
  now=$(date +%s)
  if [[ "$OSTYPE" == "darwin"* ]]; then
    mtime=$(stat -f %m "$file")
  else
    mtime=$(stat -c %Y "$file")
  fi
  [ $((now - mtime)) -lt "$ttl" ]
}

# fetch_and_cache <url> <safe_path> — fetch raw HTML and derive plain text
# Writes: $CACHE_DIR/doc_<safe_path>.html  (raw HTML)
#         $CACHE_DIR/doc_<safe_path>.txt   (plain text)
# Returns 0 on success, 1 on failure (nothing written).
fetch_and_cache() {
  local url="$1" safe="$2"
  local html_file="${CACHE_DIR}/doc_${safe}.html"
  local txt_file="${CACHE_DIR}/doc_${safe}.txt"
  local tmp_html
  tmp_html=$(mktemp)
  trap 'rm -f "$tmp_html"' RETURN

  if ! curl -sf --max-time 15 "$url" -o "$tmp_html" 2>/dev/null || [ ! -s "$tmp_html" ]; then
    rm -f "$tmp_html"
    return 1
  fi

  mv "$tmp_html" "$html_file"

  if command -v lynx &>/dev/null; then
    lynx -dump -nolist "file://${html_file}" 2>/dev/null > "$txt_file"
  elif command -v w3m &>/dev/null; then
    w3m -dump "$html_file" 2>/dev/null > "$txt_file"
  else
    sed 's/<script[^>]*>.*<\/script>//gI' "$html_file" \
      | sed 's/<style[^>]*>.*<\/style>//gI' \
      | sed 's/<[^>]*>//g' \
      | sed 's/&amp;/\&/g; s/&lt;/</g; s/&gt;/>/g; s/&quot;/"/g; s/&#39;/'"'"'/g; s/&nbsp;/ /g' \
      | sed '/^[[:space:]]*$/d' \
      > "$txt_file"
  fi

  if [ ! -s "$txt_file" ]; then
    rm -f "$txt_file"
    return 1
  fi
}

# fetch_text <url> — lynx → w3m → curl+sed fallback chain
fetch_text() {
  local url="$1"
  if command -v lynx &>/dev/null; then
    lynx -dump -nolist "$url" 2>/dev/null
  elif command -v w3m &>/dev/null; then
    w3m -dump "$url" 2>/dev/null
  else
    curl -sf --max-time 15 "$url" 2>/dev/null \
      | sed 's/<script[^>]*>.*<\/script>//gI' \
      | sed 's/<style[^>]*>.*<\/style>//gI' \
      | sed 's/<[^>]*>//g' \
      | sed 's/&amp;/\&/g; s/&lt;/</g; s/&gt;/>/g; s/&quot;/"/g; s/&#39;/'"'"'/g; s/&nbsp;/ /g' \
      | sed '/^[[:space:]]*$/d'
  fi
}
