#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# 在prism-demo conda环境中运行Python代码

set -euo pipefail

# 查找conda环境中的Python
find_conda_python() {
    # 尝试多个可能的conda环境路径
    local possible_paths=(
        "/home/may/miniforge3/envs/prism-demo/bin/python"
        "/home/may/miniforge3/envs/prism-demo-new/bin/python"
        "/home/may/anaconda3/envs/prism-demo/bin/python"
        "/opt/miniconda3/envs/prism-demo/bin/python"
    )
    
    for path in "${possible_paths[@]}"; do
        if [ -f "$path" ]; then
            echo "$path"
            return 0
        fi
    done
    
    # 如果找不到，尝试使用conda run
    if command -v conda &> /dev/null; then
        echo "conda-run"
        return 0
    fi
    
    echo "python3"
    return 1
}

# 运行Python代码
run_python() {
    local python_cmd
    python_cmd=$(find_conda_python)
    
    if [ "$python_cmd" = "conda-run" ]; then
        conda run -n prism-demo "$SCRIPT_DIR/_python_wrapper.sh" "$@"
    elif [ "$python_cmd" = "python3" ]; then
        # 直接使用系统Python（可能缺少包）
        echo "⚠️  使用系统Python，可能缺少必要包" >&2
        "$SCRIPT_DIR/_python_wrapper.sh" "$@"
    else
        "$python_cmd" "$@"
    fi
}

# 如果直接运行此脚本，执行Python代码
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    run_python "$@"
fi