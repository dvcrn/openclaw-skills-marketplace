#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
NODE_BIN="${NODE_BIN:-node}"
export NODE_NO_WARNINGS="${NODE_NO_WARNINGS:-1}"

CMD="${1:-}"
if [[ -z "$CMD" ]]; then
  cat <<'USAGE'
Usage: ./scripts/a2hmarket-ops.sh <command> [options]

Commands:
  start       启动 listener（后台进程）
  stop        停止 listener
  status      查看 listener 状态
  bootstrap   OpenClaw session 初始化检查
USAGE
  exit 1
fi

shift

# ─── 从 Runtime 配置获取路径 ─────────────────────────────────────────────────
get_config_paths() {
  local payload
  payload="$(
    NODE_NO_WARNINGS=1 node - "$ROOT_DIR/runtime/js/src/config/loader.js" <<'NODE'
const loaderPath = process.argv[2];
const { resolveListenerConfig } = require(loaderPath);
try {
  const cfg = resolveListenerConfig();
  const payload = {
    pidPath: String(cfg.pidPath || ""),
    logPath: String(cfg.logPath || ""),
    lockPath: String(cfg.lockPath || ""),
  };
  process.stdout.write(`${JSON.stringify(payload)}\n`);
} catch (err) {
  const payload = { error: String((err && err.message) || err) };
  process.stdout.write(`${JSON.stringify(payload)}\n`);
  process.exit(1);
}
NODE
  )"
  local status=$?
  if [[ $status -ne 0 ]]; then
    echo "Failed to load config: $payload" >&2
    return 1
  fi
  echo "$payload"
}

# ─── start ────────────────────────────────────────────────────────────────────
do_start() {
  local config_paths
  config_paths="$(get_config_paths)" || exit 1
  
  PID_FILE="$(echo "$config_paths" | node -e "console.log(JSON.parse(require('fs').readFileSync(0,'utf8')).pidPath)")"
  LOG_FILE="$(echo "$config_paths" | node -e "console.log(JSON.parse(require('fs').readFileSync(0,'utf8')).logPath)")"

  mkdir -p "$(dirname "$PID_FILE")" "$(dirname "$LOG_FILE")"

  if "$NODE_BIN" "$ROOT_DIR/bin/a2hmarket.js" listener status >/dev/null 2>&1; then
    echo "[a2hmarket-ops] listener 已在运行，无需重复启动" >&2
    "$NODE_BIN" "$ROOT_DIR/bin/a2hmarket.js" listener status
    exit 1
  fi

  "$NODE_BIN" "$ROOT_DIR/bin/a2hmarket.js" listener clean >/dev/null 2>&1 || true

  if [[ -f "$PID_FILE" ]]; then
    existing_pid="$(cat "$PID_FILE" 2>/dev/null || true)"
    if [[ -n "$existing_pid" ]] && ! kill -0 "$existing_pid" 2>/dev/null; then
      rm -f "$PID_FILE"
    fi
  fi

  do_bootstrap --quiet

  nohup "$NODE_BIN" "$ROOT_DIR/bin/a2hmarket.js" listener run >>"$LOG_FILE" 2>&1 &
  new_pid="$!"
  echo "$new_pid" >"$PID_FILE"

  for _ in {1..10}; do
    if ! kill -0 "$new_pid" 2>/dev/null; then
      break
    fi
    sleep 0.2
  done

  if ! kill -0 "$new_pid" 2>/dev/null; then
    rm -f "$PID_FILE"
    echo "a2hmarket-listener failed to start. check log: $LOG_FILE" >&2
    tail -n 30 "$LOG_FILE" 2>/dev/null || true
    exit 1
  fi

  echo "a2hmarket-listener started: pid=$new_pid"
  echo "log: $LOG_FILE"
}

# ─── stop ─────────────────────────────────────────────────────────────────────
do_stop() {
  local config_paths
  config_paths="$(get_config_paths)" || exit 1
  
  PID_FILE="$(echo "$config_paths" | node -e "console.log(JSON.parse(require('fs').readFileSync(0,'utf8')).pidPath)")"
  LOCK_FILE="$(echo "$config_paths" | node -e "console.log(JSON.parse(require('fs').readFileSync(0,'utf8')).lockPath)")"

  find_listener_pids() {
    if command -v pgrep >/dev/null 2>&1; then
      pgrep -f "a2hmarket.js listener run" 2>/dev/null || true
      return
    fi
    ps aux 2>/dev/null | \
      grep -E "node.*a2hmarket\.js listener|a2hmarket\.js listener run" | \
      grep -v grep | \
      awk '{print $2}' || true
  }

  stop_process() {
    local pid="$1"
    local max_wait="${2:-30}"
    if ! kill -0 "$pid" 2>/dev/null; then return 0; fi
    kill "$pid" 2>/dev/null || return 0
    local count=0
    while kill -0 "$pid" 2>/dev/null && [ "$count" -lt "$max_wait" ]; do
      sleep 0.2
      count=$((count + 1))
    done
    if kill -0 "$pid" 2>/dev/null; then
      echo "  process $pid not responding, sending SIGKILL..."
      kill -9 "$pid" 2>/dev/null || true
      sleep 0.5
    fi
    if kill -0 "$pid" 2>/dev/null; then
      echo "  failed to stop process $pid"
      return 1
    fi
    return 0
  }

  listener_pids=($(find_listener_pids))

  if [ ${#listener_pids[@]} -eq 0 ]; then
    echo "a2hmarket-listener not running"
    rm -f "$PID_FILE" "$LOCK_FILE"
    exit 0
  fi

  echo "Found ${#listener_pids[@]} a2hmarket-listener process(es): ${listener_pids[*]}"

  stopped_count=0
  failed_count=0

  for pid in "${listener_pids[@]}"; do
    echo "Stopping listener process: $pid"
    if stop_process "$pid" 30; then
      echo "  stopped: $pid"
      stopped_count=$((stopped_count + 1))
    else
      echo "  failed to stop: $pid"
      failed_count=$((failed_count + 1))
    fi
  done

  rm -f "$PID_FILE" "$LOCK_FILE"

  echo ""
  echo "=== Stop Summary ==="
  echo "Stopped: $stopped_count"
  if [ "$failed_count" -gt 0 ]; then
    echo "Failed: $failed_count"
    for pid in "${listener_pids[@]}"; do
      if kill -0 "$pid" 2>/dev/null; then
        echo "  sudo kill -9 $pid"
      fi
    done
    exit 1
  fi
  echo "All a2hmarket-listener processes stopped successfully"
}

# ─── status ───────────────────────────────────────────────────────────────────
do_status() {
  exec "$NODE_BIN" "$ROOT_DIR/bin/a2hmarket.js" listener status "$@"
}

# ─── bootstrap ────────────────────────────────────────────────────────────────
do_bootstrap() {
  local mode="text"
  for arg in "$@"; do
    case "$arg" in
      --quiet) mode="quiet" ;;
      --json)  mode="json" ;;
      -h|--help)
        echo "Usage: ./scripts/a2hmarket-ops.sh bootstrap [--quiet|--json]"
        return 0
        ;;
    esac
  done

  set +e
  payload="$(
    NODE_NO_WARNINGS=1 node - "$ROOT_DIR/runtime/js/src/config/loader.js" <<'NODE'
const loaderPath = process.argv[2];
const { resolveListenerConfig } = require(loaderPath);
try {
  const cfg = resolveListenerConfig();
  const payload = {
    ok: Boolean(cfg.pushEnabled),
    pushEnabled: Boolean(cfg.pushEnabled),
    strict: Boolean(cfg.openclawSessionStrict),
    key: String(cfg.openclawSessionKey || ""),
    canonicalKey: String(cfg.openclawSessionKeyCanonical || cfg.openclawSessionKey || ""),
    sessionId: String(cfg.openclawSessionId || ""),
    label: String(cfg.openclawSessionLabel || ""),
    statePath: String(cfg.openclawSessionBootstrapStatePath || ""),
    error: String(cfg.openclawSessionBootstrapError || ""),
  };
  process.stdout.write(`${JSON.stringify(payload)}\n`);
} catch (err) {
  const payload = { ok: false, error: String((err && err.message) || err) };
  process.stdout.write(`${JSON.stringify(payload)}\n`);
  process.exit(1);
}
NODE
  )"
  local status=$?
  set -e

  if [[ $status -ne 0 ]]; then
    if [[ -n "$payload" ]]; then echo "$payload" >&2; fi
    exit "$status"
  fi

  if [[ "$mode" == "json" ]]; then
    echo "$payload"
    return 0
  fi

  if [[ "$mode" == "quiet" ]]; then
    return 0
  fi

  NODE_NO_WARNINGS=1 node - "$payload" <<'NODE'
const payload = JSON.parse(process.argv[2]);
if (!payload.ok) {
  process.stderr.write(`[a2hmarket] openclaw session bootstrap skipped: ${payload.error || "push disabled"}\n`);
  process.exit(0);
}
process.stdout.write(`[a2hmarket] openclaw session ready key=${payload.key} canonical=${payload.canonicalKey} session_id=${payload.sessionId}\n`);
if (payload.statePath) {
  process.stdout.write(`[a2hmarket] state file: ${payload.statePath}\n`);
}
NODE
}

# ─── dispatch ─────────────────────────────────────────────────────────────────
case "$CMD" in
  start)     do_start "$@" ;;
  stop)      do_stop "$@" ;;
  status)    do_status "$@" ;;
  bootstrap) do_bootstrap "$@" ;;
  *)
    echo "unknown command: $CMD" >&2
    echo "run './scripts/a2hmarket-ops.sh' without arguments to see usage" >&2
    exit 1
    ;;
esac
