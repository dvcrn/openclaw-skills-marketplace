#!/usr/bin/env bash

derive_origin() {
  python3 - "${1:-}" <<'PY'
import sys
from urllib.parse import urlparse

raw = sys.argv[1].strip()
if not raw:
    print("")
    raise SystemExit(0)
parsed = urlparse(raw)
if parsed.scheme and parsed.netloc:
    print(f"{parsed.scheme}://{parsed.netloc}")
else:
    print(raw)
PY
}

origin_slug() {
  python3 - "$1" <<'PY'
import sys

value = sys.argv[1].strip().lower()
for old, new in (
    ("://", "___"),
    ("/", "_"),
    (":", "_"),
    ("?", "_"),
    ("&", "_"),
    ("=", "_"),
    (".", "_"),
):
    value = value.replace(old, new)
print(value.strip("_") or "default")
PY
}

runtime_scoped_path() {
  local base_root="$1"
  local category="$2"
  local origin="$3"
  local session_key="${4:-default}"
  local slug

  slug="$(origin_slug "$origin")"
  printf '%s/%s/%s/%s\n' "$base_root" "$category" "$slug" "$session_key"
}

pick_free_tcp_port() {
  python3 - "$1" <<'PY'
import socket
import sys

start = int(sys.argv[1])
for port in range(start, start + 50):
    with socket.socket() as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind(("127.0.0.1", port))
        except OSError:
            continue
        print(port)
        raise SystemExit(0)
raise SystemExit(1)
PY
}

pick_free_display() {
  local start="${1:-88}"
  local socket_dir="${AGENT_BROWSER_X11_SOCKET_DIR:-/tmp/.X11-unix}"
  local candidate socket_path

  for candidate in $(seq "$start" $((start + 50))); do
    socket_path="$socket_dir/X${candidate}"
    if [ -e "$socket_path" ]; then
      continue
    fi
    if ps -eo command= 2>/dev/null | grep -Eq "(^|[[:space:]])(:${candidate})([[:space:]]|$)"; then
      continue
    fi
    printf '%s\n' "$candidate"
    return 0
  done

  return 1
}
