#!/bin/bash
# agent-collab-platform - CLI入口
# 版权声明：MIT License | Copyright (c) 2026 米粒儿 (miliger)
# GitHub: https://github.com/zhaog100/xiaomili-personal-skills

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/skill.py"

# 调用Python脚本
python3 "$PYTHON_SCRIPT" "$@"
