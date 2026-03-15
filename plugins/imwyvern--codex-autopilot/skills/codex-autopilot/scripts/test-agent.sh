#!/bin/bash
# test-agent.sh — Test Agent 主编排（Phase 1）
# 用法:
#   test-agent.sh evaluate <project_dir> <window>
#   test-agent.sh enqueue <project_dir> <window> <reason>

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=autopilot-lib.sh
source "${SCRIPT_DIR}/autopilot-lib.sh"
if [ -f "${SCRIPT_DIR}/autopilot-constants.sh" ]; then
    # shellcheck disable=SC1091
    source "${SCRIPT_DIR}/autopilot-constants.sh"
fi

CONFIG_FILE="${AUTOPILOT_CONFIG_FILE:-$HOME/.autopilot/config.yaml}"
STATE_DIR="${STATE_DIR:-$HOME/.autopilot/state}"
LOG_DIR="${LOG_DIR:-$HOME/.autopilot/logs}"
COVERAGE_COLLECTOR="${SCRIPT_DIR}/coverage-collect.sh"
TASK_QUEUE="${SCRIPT_DIR}/task-queue.sh"
mkdir -p "$STATE_DIR" "$LOG_DIR"

log() {
    echo "[test-agent $(date '+%Y-%m-%d %H:%M:%S')] $*" >&2
}

yaml_trim() {
    local v="${1:-}"
    v="${v%%#*}"
    v=$(echo "$v" | sed 's/^[[:space:]]*//; s/[[:space:]]*$//')
    v=$(echo "$v" | sed 's/^"//; s/"$//; s/^'\''//; s/'\''$//')
    echo "$v"
}

normalize_bool() {
    local raw
    raw=$(echo "${1:-}" | tr '[:upper:]' '[:lower:]')
    case "$raw" in
        1|true|yes|on) echo "true" ;;
        *) echo "false" ;;
    esac
}

get_test_agent_enabled() {
    [ -f "$CONFIG_FILE" ] || { echo "false"; return 0; }
    awk '
        /^[[:space:]]*test_agent:[[:space:]]*$/ {in_test=1; next}
        in_test && /^[^[:space:]]/ {in_test=0}
        in_test && /^[[:space:]]*enabled:[[:space:]]*/ {
            sub(/^[[:space:]]*enabled:[[:space:]]*/, "", $0)
            print
            exit
        }
    ' "$CONFIG_FILE" 2>/dev/null | head -n1
}

get_changed_files_min() {
    [ -f "$CONFIG_FILE" ] || { echo "80"; return 0; }
    local value
    value=$(awk '
        /^[[:space:]]*test_agent:[[:space:]]*$/ {in_test=1; next}
        in_test && /^[^[:space:]]/ {in_test=0}
        in_test && /^[[:space:]]*coverage:[[:space:]]*$/ {in_cov=1; next}
        in_cov && in_test && /^[[:space:]]*[a-zA-Z_][a-zA-Z0-9_]*:[[:space:]]*$/ && $0 !~ /^[[:space:]]*changed_files_min:[[:space:]]*/ {next}
        in_cov && /^[[:space:]]*changed_files_min:[[:space:]]*/ {
            sub(/^[[:space:]]*changed_files_min:[[:space:]]*/, "", $0)
            print
            exit
        }
    ' "$CONFIG_FILE" 2>/dev/null | head -n1)
    value=$(yaml_trim "$value")
    value=$(normalize_int "$value")
    [ "$value" -gt 0 ] || value=80
    echo "$value"
}

get_max_tasks_per_round() {
    [ -f "$CONFIG_FILE" ] || { echo "3"; return 0; }
    local value
    value=$(awk '
        /^[[:space:]]*test_agent:[[:space:]]*$/ {in_test=1; next}
        in_test && /^[^[:space:]]/ {in_test=0}
        in_test && /^[[:space:]]*queue:[[:space:]]*$/ {in_q=1; next}
        in_q && in_test && /^[[:space:]]*[a-zA-Z_][a-zA-Z0-9_]*:[[:space:]]*$/ && $0 !~ /^[[:space:]]*max_tasks_per_round:[[:space:]]*/ {next}
        in_q && /^[[:space:]]*max_tasks_per_round:[[:space:]]*/ {
            sub(/^[[:space:]]*max_tasks_per_round:[[:space:]]*/, "", $0)
            print
            exit
        }
    ' "$CONFIG_FILE" 2>/dev/null | head -n1)
    value=$(yaml_trim "$value")
    value=$(normalize_int "$value")
    [ "$value" -gt 0 ] || value=3
    echo "$value"
}

get_jest_test_cmd() {
    [ -f "$CONFIG_FILE" ] || { echo "npm test -- --coverage --ci"; return 0; }
    local value
    value=$(awk '
        /^[[:space:]]*test_agent:[[:space:]]*$/ {in_test=1; next}
        in_test && /^[^[:space:]]/ {in_test=0}
        in_test && /^[[:space:]]*frameworks:[[:space:]]*$/ {in_fw=1; next}
        in_fw && in_test && /^[[:space:]]*jest:[[:space:]]*$/ {in_jest=1; next}
        in_jest && /^[[:space:]]*test_cmd:[[:space:]]*/ {
            sub(/^[[:space:]]*test_cmd:[[:space:]]*/, "", $0)
            print
            exit
        }
    ' "$CONFIG_FILE" 2>/dev/null | head -n1)
    value=$(yaml_trim "$value")
    [ -n "$value" ] || value="npm test -- --coverage --ci"
    echo "$value"
}

write_state_atomic() {
    local safe="$1" json_payload="$2"
    local state_file tmp_file
    state_file="${STATE_DIR}/test-agent-${safe}.json"
    tmp_file="${state_file}.tmp.$$"
    printf '%s\n' "$json_payload" > "$tmp_file"
    mv -f "$tmp_file" "$state_file"
}

run_coverage_collection_cmd() {
    local project_dir="$1" tool="$2"
    local cmd=""

    case "$tool" in
        jest)
            cmd=$(get_jest_test_cmd)
            ;;
        junit)
            cmd="./gradlew test jacocoTestReport"
            ;;
        bats)
            cmd="bats test/"
            ;;
        *)
            echo 0
            return 0
            ;;
    esac

    local run_log rc
    run_log="${LOG_DIR}/test-agent-run-$(sanitize "$tool")-$(now_ts).log"
    set +e
    (cd "$project_dir" && run_with_timeout 120 bash -lc "$cmd") >"$run_log" 2>&1
    rc=$?
    set -e

    if [ "$rc" -ne 0 ]; then
        log "覆盖率收集命令退出非 0 (${tool}, rc=${rc})，日志: ${run_log}"
    fi
    echo "$rc"
}

evaluate_core() {
    local project_dir="$1" window="$2"

    [ -d "$project_dir" ] || {
        jq -n --arg project "$project_dir" --arg window "$window" --arg now "$(now_ts)" \
            '{tool:"unknown",line_coverage:0,files:[],project_dir:$project,window:$window,generated_at:($now|tonumber),error:"project_dir_not_found"}'
        return 0
    }

    local tool run_rc raw_json enabled
    tool=$("$COVERAGE_COLLECTOR" detect "$project_dir" 2>/dev/null || echo "unknown")

    # Phase 1 只强支持 Jest；其他框架先保持可识别和可降级。
    run_rc=$(run_coverage_collection_cmd "$project_dir" "$tool")
    raw_json=$("$COVERAGE_COLLECTOR" collect "$project_dir" 2>/dev/null || jq -n '{tool:"unknown",line_coverage:0,files:[],error:"collect_failed"}')
    enabled=$(normalize_bool "$(get_test_agent_enabled)")

    echo "$raw_json" | jq --arg project "$project_dir" --arg window "$window" --arg tool "$tool" --arg run_rc "$run_rc" --arg enabled "$enabled" --arg now "$(now_ts)" '
        .project_dir=$project
        | .window=$window
        | .tool=($tool // .tool)
        | .collect_rc=($run_rc|tonumber)
        | .phase1_supported=($tool=="jest")
        | .test_agent_enabled=($enabled=="true")
        | .generated_at=($now|tonumber)
    '
}

get_changed_files_this_round() {
    local project_dir="$1"

    if git -C "$project_dir" rev-parse --verify HEAD~1 >/dev/null 2>&1; then
        git -C "$project_dir" diff --name-only --relative HEAD~1 HEAD 2>/dev/null || true
    else
        git -C "$project_dir" diff --name-only --relative 2>/dev/null || true
    fi
}

build_task_candidates() {
    local eval_json="$1" changed_files="$2" threshold="$3" max_tasks="$4"

    CHANGED_FILES="$changed_files" python3 - "$threshold" "$max_tasks" "$eval_json" <<'PYEOF'
import json
import os
import sys

threshold = float(sys.argv[1])
max_tasks = int(sys.argv[2])
payload_raw = sys.argv[3]
changed_set = set(p.strip().lstrip("./") for p in os.environ.get("CHANGED_FILES", "").split("\n") if p.strip())

def lines_to_text(lines):
    if not lines:
        return "无"
    arr = []
    for item in lines[:30]:
        try:
            arr.append(str(int(item)))
        except Exception:
            continue
    return ",".join(arr) if arr else "无"

payload = json.loads(payload_raw or "{}")
files = payload.get("files", [])

low_files = []
for f in files:
    path = (f.get("path") or "").lstrip("./")
    if not path:
        continue
    pct = float(f.get("line_pct") or 0)
    if pct >= threshold:
        continue
    low_files.append({
        "path": path,
        "line_pct": pct,
        "uncovered_lines": f.get("uncovered_lines") or [],
        "changed": path in changed_set,
    })

low_files.sort(key=lambda item: (0 if item["changed"] else 1, item["line_pct"], item["path"]))
selected = low_files[:max_tasks]

for item in selected:
    item["task_text"] = (
        f"为 {item['path']} 补充单元测试，目标覆盖率 >80%。"
        f"当前覆盖率 {item['line_pct']:.2f}%，未覆盖行：{lines_to_text(item['uncovered_lines'])}"
    )

print(json.dumps({"tasks": selected}, ensure_ascii=False))
PYEOF
}

queue_has_similar_test_task() {
    local queue_file="$1" file_path="$2"
    [ -f "$queue_file" ] || return 1
    # 精确匹配文件路径（避免 src/a.ts 误匹配 src/a.tsx）
    grep -E '^\- \[( |→)\].*\| type: test' "$queue_file" 2>/dev/null | grep -F " ${file_path}" | grep -qvE "${file_path}[a-zA-Z0-9_.]" 2>/dev/null
}

test_agent_evaluate() {
    local project_dir="$1" window="$2"
    evaluate_core "$project_dir" "$window"
}

test_agent_enqueue() {
    local project_dir="$1" window="$2" reason="$3"
    local safe threshold max_tasks eval_json changed_files tasks_json
    local queue_file enqueued_count skipped_count

    safe=$(sanitize "$window")
    [ -n "$safe" ] || safe="window"
    threshold=$(get_changed_files_min)
    max_tasks=$(get_max_tasks_per_round)

    eval_json=$(evaluate_core "$project_dir" "$window")
    changed_files=$(get_changed_files_this_round "$project_dir")
    tasks_json=$(build_task_candidates "$eval_json" "$changed_files" "$threshold" "$max_tasks")

    queue_file="$HOME/.autopilot/task-queue/${safe}.md"
    enqueued_count=0
    skipped_count=0

    while IFS= read -r task_item; do
        [ -n "$task_item" ] || continue
        local file_path task_text
        file_path=$(echo "$task_item" | jq -r '.path // ""' 2>/dev/null || echo "")
        task_text=$(echo "$task_item" | jq -r '.task_text // ""' 2>/dev/null || echo "")
        [ -n "$file_path" ] || continue
        [ -n "$task_text" ] || continue

        if queue_has_similar_test_task "$queue_file" "$file_path"; then
            skipped_count=$((skipped_count + 1))
            continue
        fi

        if "$TASK_QUEUE" add "$safe" "$task_text" normal --type test >/dev/null 2>&1; then
            enqueued_count=$((enqueued_count + 1))
        else
            skipped_count=$((skipped_count + 1))
        fi
    done < <(echo "$tasks_json" | jq -c '.tasks[]?' 2>/dev/null || true)

    local result_json
    result_json=$(jq -n \
        --arg window "$window" \
        --arg project "$project_dir" \
        --arg reason "$reason" \
        --argjson eval "$eval_json" \
        --argjson candidates "$tasks_json" \
        --arg threshold "$threshold" \
        --arg max_tasks "$max_tasks" \
        --arg enqueued "$enqueued_count" \
        --arg skipped "$skipped_count" \
        --arg now "$(now_ts)" '
        {
            window:$window,
            project_dir:$project,
            reason:$reason,
            threshold:($threshold|tonumber),
            max_tasks_per_round:($max_tasks|tonumber),
            enqueued:($enqueued|tonumber),
            skipped:($skipped|tonumber),
            evaluation:$eval,
            candidates:$candidates,
            generated_at:($now|tonumber)
        }
    ')

    write_state_atomic "$safe" "$result_json"
    echo "$result_json"
}

usage() {
    cat <<'USAGE'
用法:
  test-agent.sh evaluate <project_dir> <window>
  test-agent.sh enqueue <project_dir> <window> <reason>
USAGE
}

main() {
    local cmd="${1:-}"
    case "$cmd" in
        evaluate|test_agent_evaluate)
            local project_dir="${2:-}"
            local window="${3:-}"
            [ -n "$project_dir" ] && [ -n "$window" ] || { usage; exit 1; }
            test_agent_evaluate "$project_dir" "$window"
            ;;
        enqueue|test_agent_enqueue)
            local project_dir="${2:-}"
            local window="${3:-}"
            local reason="${4:-manual}"
            [ -n "$project_dir" ] && [ -n "$window" ] || { usage; exit 1; }
            test_agent_enqueue "$project_dir" "$window" "$reason"
            ;;
        *)
            usage
            exit 1
            ;;
    esac
}

main "$@"
