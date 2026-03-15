#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# PRISM_GEN_DEMO Python包装器
# 确保使用正确的Python环境和包

set -euo pipefail

# 默认使用miniforge3的Python
PYTHON_EXEC="/home/may/miniforge3/bin/python3"

# 检查Python是否可用
if [ ! -f "$PYTHON_EXEC" ]; then
    echo "❌ Python未找到: $PYTHON_EXEC"
    echo "尝试使用系统Python..."
    PYTHON_EXEC="python3"
fi

# 检查环境
check_environment() {
    echo "🔍 检查PRISM_GEN_DEMO环境..."
    
    # 运行环境检查脚本
    if "$PYTHON_EXEC" "$SCRIPT_DIR/_ensure_env.py" 2>/dev/null; then
        echo "✅ 环境检查通过"
        return 0
    else
        echo "❌ 环境检查失败"
        echo ""
        echo "请确保以下包已安装:"
        echo "  pandas, numpy, matplotlib, seaborn"
        echo ""
        echo "安装命令:"
        echo "  $PYTHON_EXEC -m pip install pandas numpy matplotlib seaborn"
        return 1
    fi
}

# 运行Python代码
run_python() {
    local python_code="$1"
    
    # 检查环境
    if ! check_environment; then
        return 1
    fi
    
    # 执行Python代码
    "$PYTHON_EXEC" -c "$python_code"
}

# 运行Python脚本
run_python_script() {
    local script_file="$1"
    shift
    
    # 检查环境
    if ! check_environment; then
        return 1
    fi
    
    # 执行Python脚本
    "$PYTHON_EXEC" "$script_file" "$@"
}

# 如果直接调用，执行Python代码
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    if [ $# -eq 0 ]; then
        echo "用法: $0 '<python_code>'"
        echo "  或: $0 script.py [args...]"
        exit 1
    fi
    
    if [[ "$1" == *.py ]]; then
        run_python_script "$@"
    else
        run_python "$1"
    fi
fi