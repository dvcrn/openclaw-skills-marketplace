#!/bin/bash
# 修复Python脚本中的布尔变量引用

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "修复Python脚本中的布尔变量引用..."

# 修复demo_plot_scatter.sh
if [ -f "$SCRIPT_DIR/demo_plot_scatter.sh" ]; then
    echo "修复 demo_plot_scatter.sh..."
    
    # 替换布尔变量引用
    sed -i "s/\$TRENDLINE/trendline_setting/g" "$SCRIPT_DIR/demo_plot_scatter.sh"
    sed -i "s/\$CORRELATION/correlation_setting/g" "$SCRIPT_DIR/demo_plot_scatter.sh"
    sed -i "s/\$REGRESSION/regression_setting/g" "$SCRIPT_DIR/demo_plot_scatter.sh"
    sed -i "s/\$LOGX/logx_setting/g" "$SCRIPT_DIR/demo_plot_scatter.sh"
    sed -i "s/\$LOGY/logy_setting/g" "$SCRIPT_DIR/demo_plot_scatter.sh"
    
    # 在Python代码开始前添加变量定义
    python_start_line=$(grep -n "^\"\$SCRIPT_DIR/_python_wrapper.sh\" \"" "$SCRIPT_DIR/demo_plot_scatter.sh" | head -1 | cut -d: -f1)
    if [ -n "$python_start_line" ]; then
        # 在Python代码开始后添加变量定义
        sed -i "${python_start_line}a\\
    # 将shell布尔变量转换为Python布尔变量\\
    trendline_setting = $TRENDLINE\\
    correlation_setting = $CORRELATION\\
    regression_setting = $REGRESSION\\
    logx_setting = $LOGX\\
    logy_setting = $LOGY\\
    grid_setting = $GRID" "$SCRIPT_DIR/demo_plot_scatter.sh"
    fi
    
    echo "✅ 修复完成"
fi

# 修复demo_plot_distribution.sh
if [ -f "$SCRIPT_DIR/demo_plot_distribution.sh" ]; then
    echo "修复 demo_plot_distribution.sh..."
    
    # 替换布尔变量引用
    sed -i "s/\$LOG_SCALE/log_scale_setting/g" "$SCRIPT_DIR/demo_plot_distribution.sh"
    sed -i "s/\$SHOW_KDE/show_kde_setting/g" "$SCRIPT_DIR/demo_plot_distribution.sh"
    sed -i "s/\$SHOW_STATS/show_stats_setting/g" "$SCRIPT_DIR/demo_plot_distribution.sh"
    
    # 在Python代码开始前添加变量定义
    python_start_line=$(grep -n "^\"\$SCRIPT_DIR/_python_wrapper.sh\" \"" "$SCRIPT_DIR/demo_plot_distribution.sh" | head -1 | cut -d: -f1)
    if [ -n "$python_start_line" ]; then
        sed -i "${python_start_line}a\\
    # 将shell布尔变量转换为Python布尔变量\\
    log_scale_setting = $LOG_SCALE\\
    show_kde_setting = $SHOW_KDE\\
    show_stats_setting = $SHOW_STATS" "$SCRIPT_DIR/demo_plot_distribution.sh"
    fi
    
    echo "✅ 修复完成"
fi

echo ""
echo "所有修复完成。现在可以重新测试脚本。"