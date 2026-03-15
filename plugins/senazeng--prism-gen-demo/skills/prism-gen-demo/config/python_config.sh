#!/bin/bash
# PRISM_GEN_DEMO Python配置
# 确保使用正确的Python解释器

# 优先使用miniforge3中的Python
if [ -f "/home/may/miniforge3/bin/python3" ]; then
    export PYTHON_CMD="/home/may/miniforge3/bin/python3"
    echo "✅ 使用miniforge3 Python: $PYTHON_CMD"
elif [ -f "/home/may/miniforge3/envs/prism-demo/bin/python3" ]; then
    export PYTHON_CMD="/home/may/miniforge3/envs/prism-demo/bin/python3"
    echo "✅ 使用prism-demo环境Python: $PYTHON_CMD"
elif command -v python3 &> /dev/null; then
    export PYTHON_CMD="python3"
    echo "⚠️  使用系统Python，可能缺少必要包"
else
    echo "❌ 未找到Python3"
    exit 1
fi

# 验证Python环境
$PYTHON_CMD -c "
try:
    import pandas, numpy, matplotlib, seaborn
    print('✅ 所有必要包已安装')
    print(f'   pandas: {pandas.__version__}')
    print(f'   numpy: {numpy.__version__}')
    print(f'   matplotlib: {matplotlib.__version__}')
    print(f'   seaborn: {seaborn.__version__}')
except ImportError as e:
    print(f'❌ 缺少包: {e}')
    exit(1)
" || exit 1

export PYTHONPATH="${PYTHONPATH:-}:$(dirname "$(dirname "$0")")"