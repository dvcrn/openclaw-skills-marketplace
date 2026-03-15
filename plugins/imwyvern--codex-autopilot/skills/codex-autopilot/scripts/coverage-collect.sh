#!/bin/bash
# coverage-collect.sh — 覆盖率收集与归一化输出
# 用法:
#   coverage-collect.sh detect <project_dir>
#   coverage-collect.sh collect <project_dir>

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=autopilot-lib.sh
source "${SCRIPT_DIR}/autopilot-lib.sh"
if [ -f "${SCRIPT_DIR}/autopilot-constants.sh" ]; then
    # shellcheck disable=SC1091
    source "${SCRIPT_DIR}/autopilot-constants.sh"
fi

detect_framework() {
    local project_dir="$1"

    if [ -f "${project_dir}/package.json" ] && grep -q '"test"[[:space:]]*:' "${project_dir}/package.json" 2>/dev/null; then
        echo "jest"
        return 0
    fi

    if [ -f "${project_dir}/build.gradle" ] || [ -f "${project_dir}/build.gradle.kts" ]; then
        echo "junit"
        return 0
    fi

    if find "${project_dir}/test" -maxdepth 1 -type f -name '*.bats' >/dev/null 2>&1; then
        if find "${project_dir}/test" -maxdepth 1 -type f -name '*.bats' | head -n1 | grep -q .; then
            echo "bats"
            return 0
        fi
    fi

    echo "unknown"
}

collect_jest_coverage() {
    local project_dir="$1"
    local summary_file="${project_dir}/coverage/coverage-summary.json"
    local lcov_file="${project_dir}/coverage/lcov.info"

    if [ ! -f "$summary_file" ]; then
        jq -n --arg now "$(now_ts)" '{tool:"jest",line_coverage:0,files:[],generated_at:($now|tonumber),error:"missing_coverage_summary"}'
        return 0
    fi

    python3 - "$project_dir" "$summary_file" "$lcov_file" <<'PYEOF'
import json
import os
import sys
from pathlib import Path

project_dir = Path(sys.argv[1]).resolve()
summary_path = Path(sys.argv[2])
lcov_path = Path(sys.argv[3])

def rel_path(path_text: str) -> str:
    p = Path(path_text)
    if p.is_absolute():
        try:
            return str(p.resolve().relative_to(project_dir)).replace("\\", "/")
        except Exception:
            return str(p).replace("\\", "/")
    return str(p).replace("\\", "/").lstrip("./")

summary = json.loads(summary_path.read_text(encoding="utf-8"))
total = summary.get("total", {})
line_coverage = float((total.get("lines", {}) or {}).get("pct") or 0)

uncovered_map = {}
if lcov_path.exists():
    current_file = ""
    with lcov_path.open("r", encoding="utf-8", errors="ignore") as fh:
        for raw in fh:
            line = raw.strip()
            if line.startswith("SF:"):
                current_file = line[3:]
                uncovered_map.setdefault(rel_path(current_file), [])
            elif line.startswith("DA:") and current_file:
                data = line[3:].split(",", 1)
                if len(data) == 2:
                    try:
                        line_no = int(data[0])
                        hits = int(float(data[1]))
                    except ValueError:
                        continue
                    if hits == 0:
                        uncovered_map.setdefault(rel_path(current_file), []).append(line_no)

files = []
for path_text, data in summary.items():
    if path_text == "total":
        continue
    pct = float((data.get("lines", {}) or {}).get("pct") or 0)
    file_path = rel_path(path_text)
    files.append({
        "path": file_path,
        "line_pct": pct,
        "uncovered_lines": uncovered_map.get(file_path, [])[:80],
    })

files.sort(key=lambda item: (item.get("line_pct", 0), item.get("path", "")))

print(json.dumps({
    "tool": "jest",
    "line_coverage": line_coverage,
    "files": files,
    "generated_at": int(__import__("time").time()),
}, ensure_ascii=False))
PYEOF
}

collect_junit_coverage() {
    local project_dir="$1"
    local xml_file="${project_dir}/build/reports/jacoco/test/jacocoTestReport.xml"

    if [ ! -f "$xml_file" ]; then
        jq -n --arg now "$(now_ts)" '{tool:"junit",line_coverage:0,files:[],generated_at:($now|tonumber),error:"missing_jacoco_xml"}'
        return 0
    fi

    local line missed covered pct
    line=$(grep -m1 'counter type="LINE"' "$xml_file" 2>/dev/null || true)
    missed=$(echo "$line" | sed -n 's/.*missed="\([0-9][0-9]*\)".*/\1/p')
    covered=$(echo "$line" | sed -n 's/.*covered="\([0-9][0-9]*\)".*/\1/p')
    missed=$(normalize_int "$missed")
    covered=$(normalize_int "$covered")

    if [ $((missed + covered)) -gt 0 ]; then
        pct=$(awk -v c="$covered" -v m="$missed" 'BEGIN{printf "%.2f", (c*100)/(c+m)}')
    else
        pct="0"
    fi

    jq -n --arg pct "$pct" --arg now "$(now_ts)" '{tool:"junit",line_coverage:($pct|tonumber),files:[],generated_at:($now|tonumber)}'
}

collect_bats_coverage() {
    local project_dir="$1"
    local pass_rate="0"
    local output rc total failed

    if command -v bats >/dev/null 2>&1; then
        set +e
        output=$(cd "$project_dir" && run_with_timeout 120 bats test/ 2>&1)
        rc=$?
        set -e

        total=$(echo "$output" | sed -n 's/.*\([0-9][0-9]*\) tests, .*/\1/p' | tail -n1)
        failed=$(echo "$output" | sed -n 's/.*tests, \([0-9][0-9]*\) failures.*/\1/p' | tail -n1)
        total=$(normalize_int "$total")
        failed=$(normalize_int "$failed")

        if [ "$total" -gt 0 ]; then
            pass_rate=$(awk -v t="$total" -v f="$failed" 'BEGIN{printf "%.2f", ((t-f)*100)/t}')
        elif [ "$rc" -eq 0 ]; then
            pass_rate="100"
        fi
    fi

    jq -n --arg pct "$pass_rate" --arg now "$(now_ts)" '{tool:"bats",line_coverage:($pct|tonumber),files:[],generated_at:($now|tonumber),note:"pass_rate_fallback"}'
}

collect_coverage() {
    local project_dir="$1"
    local framework
    framework=$(detect_framework "$project_dir")

    case "$framework" in
        jest)
            collect_jest_coverage "$project_dir"
            ;;
        junit)
            collect_junit_coverage "$project_dir"
            ;;
        bats)
            collect_bats_coverage "$project_dir"
            ;;
        *)
            jq -n --arg now "$(now_ts)" '{tool:"unknown",line_coverage:0,files:[],generated_at:($now|tonumber),error:"framework_unknown"}'
            ;;
    esac
}

usage() {
    cat <<'USAGE'
用法:
  coverage-collect.sh detect <project_dir>
  coverage-collect.sh collect <project_dir>
USAGE
}

main() {
    local cmd="${1:-}"
    case "$cmd" in
        detect)
            local project_dir="${2:-}"
            [ -n "$project_dir" ] || { usage; exit 1; }
            detect_framework "$project_dir"
            ;;
        collect)
            local project_dir="${2:-}"
            [ -n "$project_dir" ] || { usage; exit 1; }
            collect_coverage "$project_dir"
            ;;
        *)
            usage
            exit 1
            ;;
    esac
}

main "$@"
