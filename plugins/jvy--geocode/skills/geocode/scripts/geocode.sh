#!/usr/bin/env bash
set -euo pipefail

usage() {
  local exit_code="${1:-2}"
  cat >&2 <<'EOF'
Usage:
  geocode.sh search <query> [--lang <code>] [--limit <n>] [--countrycodes <codes>] [--user-agent <ua>]
  geocode.sh reverse <latitude> <longitude> [--lang <code>] [--zoom <n>] [--user-agent <ua>]

Examples:
  geocode.sh search "1600 Amphitheatre Parkway, Mountain View, CA" --lang en --limit 3
  geocode.sh search "上海迪士尼乐园" --lang zh-CN
  geocode.sh reverse 37.819929 -122.478255 --lang en

Environment:
  GEOCODE_BASE_URL     Override the Nominatim base URL.
  GEOCODE_USER_AGENT   Override the default User-Agent string.
EOF
  exit "$exit_code"
}

is_decimal() {
  [[ "${1:-}" =~ ^-?[0-9]+([.][0-9]+)?$ ]]
}

is_uint() {
  [[ "${1:-}" =~ ^[0-9]+$ ]]
}

curl_json() {
  curl -fsSL "$@"
  printf '\n'
}

if [[ "${1:-}" == "" || "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage 0
fi

command="${1:-}"
shift || true

base_url="${GEOCODE_BASE_URL:-https://nominatim.openstreetmap.org}"
user_agent="${GEOCODE_USER_AGENT:-openclaw-geocode-skill/1.0 (interactive use)}"

case "$command" in
  search)
    query="${1:-}"
    if [[ "$query" == "" ]]; then
      echo "Missing search query" >&2
      usage
    fi
    shift || true

    lang=""
    limit="5"
    countrycodes=""

    while [[ $# -gt 0 ]]; do
      case "$1" in
        --lang)
          lang="${2:-}"
          shift 2
          ;;
        --limit)
          limit="${2:-}"
          shift 2
          ;;
        --countrycodes)
          countrycodes="${2:-}"
          shift 2
          ;;
        --user-agent)
          user_agent="${2:-}"
          shift 2
          ;;
        *)
          echo "Unknown arg: $1" >&2
          usage
          ;;
      esac
    done

    if ! is_uint "$limit"; then
      echo "Invalid --limit: $limit" >&2
      exit 1
    fi

    args=(
      --get
      "${base_url%/}/search"
      -A "$user_agent"
      --data-urlencode "q=$query"
      --data "format=jsonv2"
      --data "limit=$limit"
    )

    if [[ "$lang" != "" ]]; then
      args+=(--data-urlencode "accept-language=$lang")
    fi
    if [[ "$countrycodes" != "" ]]; then
      args+=(--data "countrycodes=$countrycodes")
    fi

    curl_json "${args[@]}"
    ;;
  reverse)
    latitude="${1:-}"
    longitude="${2:-}"
    if [[ "$latitude" == "" || "$longitude" == "" ]]; then
      echo "Missing latitude/longitude" >&2
      usage
    fi
    shift 2 || true

    lang=""
    zoom=""

    while [[ $# -gt 0 ]]; do
      case "$1" in
        --lang)
          lang="${2:-}"
          shift 2
          ;;
        --zoom)
          zoom="${2:-}"
          shift 2
          ;;
        --user-agent)
          user_agent="${2:-}"
          shift 2
          ;;
        *)
          echo "Unknown arg: $1" >&2
          usage
          ;;
      esac
    done

    if ! is_decimal "$latitude"; then
      echo "Invalid latitude: $latitude" >&2
      exit 1
    fi
    if ! is_decimal "$longitude"; then
      echo "Invalid longitude: $longitude" >&2
      exit 1
    fi
    if [[ "$zoom" != "" ]] && ! is_uint "$zoom"; then
      echo "Invalid --zoom: $zoom" >&2
      exit 1
    fi

    args=(
      --get
      "${base_url%/}/reverse"
      -A "$user_agent"
      --data "lat=$latitude"
      --data "lon=$longitude"
      --data "format=jsonv2"
    )

    if [[ "$lang" != "" ]]; then
      args+=(--data-urlencode "accept-language=$lang")
    fi
    if [[ "$zoom" != "" ]]; then
      args+=(--data "zoom=$zoom")
    fi

    curl_json "${args[@]}"
    ;;
  *)
    echo "Unknown command: $command" >&2
    usage
    ;;
esac
