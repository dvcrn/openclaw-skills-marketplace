#!/usr/bin/env bash
# kannaka-radio CLI wrapper
#
# Usage:
#   ./scripts/radio.sh start [--port 8888] [--music-dir /path/to/music]
#   ./scripts/radio.sh stop
#   ./scripts/radio.sh restart [...]
#   ./scripts/radio.sh status
#   ./scripts/radio.sh now-playing
#   ./scripts/radio.sh perception
#   ./scripts/radio.sh next
#   ./scripts/radio.sh prev
#   ./scripts/radio.sh jump <track-index>
#   ./scripts/radio.sh load-album <name>
#   ./scripts/radio.sh set-dir <path>
#   ./scripts/radio.sh library

set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RADIO_DIR="$(cd "$SKILL_DIR/../../.." && pwd)"   # repo root
SERVER_JS="$RADIO_DIR/server.js"
PID_FILE="$RADIO_DIR/.radio.pid"
PORT="${RADIO_PORT:-8888}"
BASE_URL="http://localhost:$PORT"

# ── Helpers ─────────────────────────────────────────────────

is_running() {
  if [[ -f "$PID_FILE" ]]; then
    local pid
    pid=$(cat "$PID_FILE")
    kill -0 "$pid" 2>/dev/null && return 0
  fi
  return 1
}

api() {
  local method="$1" path="$2"
  shift 2
  curl -sf -X "$method" "$BASE_URL$path" "$@"
}

# ── Commands ─────────────────────────────────────────────────

cmd_start() {
  if is_running; then
    echo "👻 Kannaka Radio already running (PID $(cat "$PID_FILE"))"
    echo "   Player: $BASE_URL"
    return 0
  fi

  local extra_args=("$@")
  echo "👻 Starting Kannaka Radio..."
  node "$SERVER_JS" --port "$PORT" "${extra_args[@]}" &
  echo $! > "$PID_FILE"
  sleep 1.5

  if is_running; then
    echo "   ✓ Running on $BASE_URL (PID $(cat "$PID_FILE"))"
  else
    echo "   ✗ Failed to start — check server.js for errors"
    rm -f "$PID_FILE"
    exit 1
  fi
}

cmd_stop() {
  if ! is_running; then
    echo "Kannaka Radio is not running"
    return 0
  fi
  local pid
  pid=$(cat "$PID_FILE")
  kill "$pid" 2>/dev/null && echo "✓ Stopped (PID $pid)" || echo "Already stopped"
  rm -f "$PID_FILE"
}

cmd_restart() {
  cmd_stop
  sleep 1
  cmd_start "$@"
}

cmd_status() {
  if is_running; then
    local pid
    pid=$(cat "$PID_FILE")
    echo "👻 Kannaka Radio is RUNNING (PID $pid)"
    echo "   Player: $BASE_URL"
    # Try to get current track
    local state
    state=$(api GET /api/state 2>/dev/null || echo "")
    if [[ -n "$state" ]]; then
      local title album
      title=$(echo "$state" | python3 -c "import sys,json; d=json.load(sys.stdin); c=d.get('current',{}); print(c.get('title','—'))" 2>/dev/null || echo "—")
      album=$(echo "$state" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('currentAlbum','—'))" 2>/dev/null || echo "—")
      echo "   Now: $title  ($album)"
    fi
  else
    echo "Kannaka Radio is STOPPED"
  fi
}

cmd_now_playing() {
  local state
  state=$(api GET /api/state)
  if command -v jq &>/dev/null; then
    echo "$state" | jq '{track: .current.title, album: .currentAlbum, idx: .currentTrackIdx, total: .totalTracks}'
  else
    echo "$state"
  fi
}

cmd_perception() {
  local p
  p=$(api GET /api/perception)
  if command -v jq &>/dev/null; then
    echo "$p" | jq '{tempo_bpm, spectral_centroid, rms_energy, pitch, valence, status, track: .track_info.title}'
  else
    echo "$p"
  fi
}

cmd_next() {
  api POST /api/next > /dev/null
  echo "⏭  Next track"
  sleep 0.3
  cmd_now_playing
}

cmd_prev() {
  api POST /api/prev > /dev/null
  echo "⏮  Previous track"
  sleep 0.3
  cmd_now_playing
}

cmd_jump() {
  local idx="${1:?jump requires a track index}"
  api POST "/api/jump?idx=$idx" > /dev/null
  echo "⏩  Jumped to track $idx"
  sleep 0.3
  cmd_now_playing
}

cmd_load_album() {
  local name="${1:?load-album requires an album name}"
  api POST "/api/album?name=$(python3 -c "import urllib.parse,sys; print(urllib.parse.quote(sys.argv[1]))" "$name")" > /dev/null
  echo "💿  Loaded album: $name"
  sleep 0.3
  cmd_now_playing
}

cmd_set_dir() {
  local dir="${1:?set-dir requires a path}"
  local result
  result=$(api POST /api/set-music-dir \
    -H 'Content-Type: application/json' \
    -d "{\"dir\":\"$dir\"}")
  if command -v jq &>/dev/null; then
    echo "$result" | jq '{ok, musicDir, fileCount}'
  else
    echo "$result"
  fi
}

cmd_library() {
  local lib
  lib=$(api GET /api/library)
  if command -v jq &>/dev/null; then
    echo "$lib" | jq '{musicDir, fileCount, summary: (.albums | to_entries | map({key, found: .value.found, total: .value.total}))}'
  else
    echo "$lib"
  fi
}

# ── Dispatch ─────────────────────────────────────────────────

CMD="${1:-status}"
shift || true

case "$CMD" in
  start)       cmd_start "$@" ;;
  stop)        cmd_stop ;;
  restart)     cmd_restart "$@" ;;
  status)      cmd_status ;;
  now-playing) cmd_now_playing ;;
  perception)  cmd_perception ;;
  next)        cmd_next ;;
  prev)        cmd_prev ;;
  jump)        cmd_jump "$@" ;;
  load-album)  cmd_load_album "$@" ;;
  set-dir)     cmd_set_dir "$@" ;;
  library)     cmd_library ;;
  *)
    echo "Usage: radio.sh <command> [args]"
    echo ""
    echo "Commands:"
    echo "  start [--port N] [--music-dir PATH]   Start the radio server"
    echo "  stop                                   Stop the radio server"
    echo "  restart [...]                          Restart the server"
    echo "  status                                 Show running status + now playing"
    echo "  now-playing                            Show current track details"
    echo "  perception                             Show current perception snapshot"
    echo "  next                                   Skip to next track"
    echo "  prev                                   Go to previous track"
    echo "  jump <index>                           Jump to track by index"
    echo "  load-album <name>                      Load an album by name"
    echo "  set-dir <path>                         Change the music directory live"
    echo "  library                                Show library scan status"
    exit 1
    ;;
esac
