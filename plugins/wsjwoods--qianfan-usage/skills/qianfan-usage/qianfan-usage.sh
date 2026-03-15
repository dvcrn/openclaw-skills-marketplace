#!/bin/bash
# 百度千帆 Coding Plan 用量查询工具

set -e

# 获取技能目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 加载环境变量
if [ -f ~/.openclaw/workspace/.env ]; then
    export $(grep -v '^#' ~/.openclaw/workspace/.env | xargs)
fi

# 调用 Python 脚本
python3 "${SCRIPT_DIR}/qianfan_api.py" "$@"
