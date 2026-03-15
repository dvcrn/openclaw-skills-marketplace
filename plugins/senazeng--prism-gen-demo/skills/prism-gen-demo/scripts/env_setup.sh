#!/bin/bash
# PRISM_GEN_DEMO 环境设置脚本
# 确保所有Python脚本在正确的conda环境中运行

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Conda环境名称
ENV_NAME="prism-demo"

# 检查conda是否可用
if ! command -v conda &> /dev/null; then
    echo "❌ Conda未安装或不在PATH中"
    echo "请安装Miniconda或Anaconda"
    exit 1
fi

# 检查环境是否存在
if ! conda env list | grep -q "$ENV_NAME"; then
    echo "❌ Conda环境 '$ENV_NAME' 不存在"
    echo "正在创建环境..."
    
    # 创建环境
    conda create -n "$ENV_NAME" python=3.10 pandas numpy matplotlib seaborn scipy scikit-learn -y
    
    if [ $? -eq 0 ]; then
        echo "✅ 环境 '$ENV_NAME' 创建成功"
    else
        echo "❌ 环境创建失败"
        exit 1
    fi
fi

# 激活环境的函数
activate_env() {
    # 尝试不同的激活方法
    if [ -f "/home/may/miniforge3/etc/profile.d/conda.sh" ]; then
        source "/home/may/miniforge3/etc/profile.d/conda.sh"
    elif [ -f "/home/may/anaconda3/etc/profile.d/conda.sh" ]; then
        source "/home/may/anaconda3/etc/profile.d/conda.sh"
    elif [ -f "/opt/miniconda3/etc/profile.d/conda.sh" ]; then
        source "/opt/miniconda3/etc/profile.d/conda.sh"
    fi
    
    conda activate "$ENV_NAME"
    
    # 验证环境
    if "$SCRIPT_DIR/_python_wrapper.sh" "import pandas; print('✅ Pandas版本:', pandas.__version__)" 2>/dev/null; then
        echo "✅ 环境 '$ENV_NAME' 激活成功"
        return 0
    else
        echo "❌ 环境激活失败"
        return 1
    fi
}

# 导出函数供其他脚本使用
export -f activate_env

echo "✅ PRISM_GEN_DEMO 环境设置完成"
echo "环境名称: $ENV_NAME"
echo "项目目录: $PROJECT_DIR"
echo ""
echo "使用以下命令激活环境:"
echo "  source $SCRIPT_DIR/env_setup.sh && activate_env"
echo ""
echo "或者在脚本开头添加:"
echo "  source \"\$(dirname \"\$0\")/env_setup.sh\""
echo "  activate_env"