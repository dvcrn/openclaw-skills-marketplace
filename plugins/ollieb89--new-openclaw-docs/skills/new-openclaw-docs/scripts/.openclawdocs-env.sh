#!/bin/bash
# Shared environment and helpers for openclawdocs scripts

# Configuration
export OPENCLAW_DOCS_CACHE_DIR="${OPENCLAW_DOCS_CACHE_DIR:-.openclawdocs-cache}"
export OPENCLAW_DOCS_TTL="${OPENCLAW_DOCS_TTL:-3600}"  # 1 hour default
export OPENCLAW_DOCS_BASE_URL="${OPENCLAW_DOCS_BASE_URL:-https://docs.openclaw.ai}"
export OPENCLAW_DOCS_TIMEOUT=10

# Ensure cache directory exists
mkdir -p "$OPENCLAW_DOCS_CACHE_DIR" 2>/dev/null || true

# Detect download tool (curl preferred over wget)
if command -v curl &> /dev/null; then
  _DOWLOAD_BIN="curl"
elif command -v wget &> /dev/null; then
  _DOWLOAD_BIN="wget"
else
  echo "Error: curl or wget required" >&2
  exit 1
fi

# Download with fallback to cache
openclawdocs_download() {
  local path="$1"
  local cache_file=$(openclawdocs_cache_path "$path")
  local url="$OPENCLAW_DOCS_BASE_URL/$path"
  
  # Try to download if fresh content needed
  if [[ "$2" != "force-cache" ]]; then
    if ! openclawdocs_cache_fresh "$cache_file"; then
      if [[ "$_DOWLOAD_BIN" == "curl" ]]; then
        curl -s --max-time "$OPENCLAW_DOCS_TIMEOUT" "$url" > "$cache_file" 2>/dev/null
      else
        wget -q --timeout="$OPENCLAW_DOCS_TIMEOUT" -O "$cache_file" "$url" 2>/dev/null
      fi
    fi
  fi
  
  # Return cached content if exists
  if [[ -f "$cache_file" ]]; then
    cat "$cache_file"
    return 0
  else
    return 1
  fi
}

# Get cache file path for a doc path
openclawdocs_cache_path() {
  local path="$1"
  echo "$OPENCLAW_DOCS_CACHE_DIR/${path//\//_}.md"
}

# Check if cache is fresh (within TTL)
openclawdocs_cache_fresh() {
  local cache_file="$1"
  [[ ! -f "$cache_file" ]] && return 1
  
  local age=$(($(date +%s) - $(stat -c %Y "$cache_file" 2>/dev/null || echo 0)))
  [[ $age -lt $OPENCLAW_DOCS_TTL ]]
}

# Get cache age in seconds
openclawdocs_cache_age() {
  local cache_file="$1"
  [[ ! -f "$cache_file" ]] && return 0
  echo $(($(date +%s) - $(stat -c %Y "$cache_file")))
}

# Clear old cache entries
openclawdocs_cache_cleanup() {
  local now=$(date +%s)
  for file in "$OPENCLAW_DOCS_CACHE_DIR"/*.md; do
    [[ ! -f "$file" ]] && continue
    local age=$((now - $(stat -c %Y "$file")))
    if [[ $age -ge $OPENCLAW_DOCS_TTL ]]; then
      rm "$file" 2>/dev/null || true
    fi
  done
}

# List all cached docs
openclawdocs_list_cache() {
  [[ ! -d "$OPENCLAW_DOCS_CACHE_DIR" ]] && return 1
  for file in "$OPENCLAW_DOCS_CACHE_DIR"/*.md; do
    [[ ! -f "$file" ]] && continue
    local path="${file##*/}"
    path="${path%.md}"
    path="${path//_//}"
    local age=$(openclawdocs_cache_age "$file")
    local fresh=❌
    [[ $age -lt $OPENCLAW_DOCS_TTL ]] && fresh="✓"
    printf "%-50s %6ds  %s\n" "$path" "$age" "$fresh"
  done
}
