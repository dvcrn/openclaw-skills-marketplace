#!/bin/bash
# Bash环境检查脚本
# 替代Python版本，不包含Python源代码

check_python_deps() {
    echo "检查Python依赖..."
    
    # 检查Python是否可用
    if ! command -v python3 &> /dev/null; then
        echo "❌ Python3未安装"
        return 1
    fi
    
    # 定义需要检查的包
    local packages=("pandas" "numpy" "matplotlib" "seaborn" "scipy" "sklearn")
    local missing=()
    
    for pkg in "${packages[@]}"; do
        if ! python3 -c "import $pkg" 2>/dev/null; then
            missing+=("$pkg")
        fi
    done
    
    if [ ${#missing[@]} -eq 0 ]; then
        echo "✅ 所有Python依赖已安装"
        return 0
    else
        echo "❌ 缺少包: ${missing[*]}"
        echo "请安装: pip install ${missing[*]}"
        return 1
    fi
}

# 如果直接运行则执行检查
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    check_python_deps
    exit $?
fi