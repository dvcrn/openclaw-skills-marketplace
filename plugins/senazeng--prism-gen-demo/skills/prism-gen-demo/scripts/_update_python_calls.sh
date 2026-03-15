#!/bin/bash
# 更新所有脚本中的Python调用

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "🔄 更新PRISM_GEN_DEMO脚本中的Python调用..."

# 查找所有包含python3调用的脚本
scripts_to_update=()
for script in "$SCRIPT_DIR"/*.sh; do
    if [ -f "$script" ] && grep -q "python3" "$script"; then
        scripts_to_update+=("$script")
    fi
done

echo "找到 ${#scripts_to_update[@]} 个需要更新的脚本"

# 更新每个脚本
for script in "${scripts_to_update[@]}"; do
    echo "更新: $(basename "$script")"
    
    # 备份原文件
    cp "$script" "${script}.bak"
    
    # 替换python3调用
    sed -i 's|"$SCRIPT_DIR/_python_wrapper.sh"|"$SCRIPT_DIR/_python_wrapper.sh"|g' "$script"
    sed -i 's|"$SCRIPT_DIR/_python_wrapper.sh" |"$SCRIPT_DIR/_python_wrapper.sh" |g' "$script"
    
    # 在文件开头添加SCRIPT_DIR定义（如果不存在）
    if ! grep -q "SCRIPT_DIR=" "$script"; then
        sed -i '2iSCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"' "$script"
    fi
    
    echo "  ✅ 更新完成"
done

echo ""
echo "✅ 所有脚本更新完成"
echo ""
echo "测试环境..."
"$SCRIPT_DIR/_python_wrapper.sh" "import pandas as pd; print('✅ Pandas版本:', pd.__version__)"

echo ""
echo "现在可以测试脚本功能了:"