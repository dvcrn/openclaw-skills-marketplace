#!/bin/bash
# PRISM_GEN_DEMO - 简化数据源信息查看
# 不依赖Python环境

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
DATA_DIR="$PROJECT_DIR/data"

# 检查参数
if [ $# -lt 1 ]; then
    echo "用法: $0 <数据源名称>"
    echo ""
    echo "可用数据源:"
    ls "$DATA_DIR"/*.csv 2>/dev/null | xargs -n1 basename | sed 's/^/  /'
    exit 1
fi

SOURCE_NAME="$1"
CSV_FILE="$DATA_DIR/$SOURCE_NAME"

# 检查文件是否存在
if [ ! -f "$CSV_FILE" ]; then
    echo "❌ 文件不存在: $CSV_FILE"
    echo ""
    echo "可用文件:"
    ls "$DATA_DIR"/*.csv 2>/dev/null | xargs -n1 basename | sed 's/^/  /'
    exit 1
fi

# 获取文件信息
file_size=$(du -h "$CSV_FILE" | cut -f1)
line_count=$(wc -l < "$CSV_FILE" 2>/dev/null || echo "?")
mod_time=$(stat -c "%y" "$CSV_FILE" 2>/dev/null | cut -d'.' -f1 || echo "未知")

# 获取列信息（前5行）
echo "# PRISM_GEN_DEMO - 数据源基本信息: $SOURCE_NAME"
echo ""
echo "## 📋 基本信息"
echo "- **文件**: $SOURCE_NAME"
echo "- **大小**: $file_size"
echo "- **行数**: $((line_count - 1)) 个分子（含表头）"
echo "- **修改时间**: $mod_time"
echo "- **完整路径**: $CSV_FILE"
echo ""

# 显示列名
echo "## 🏷️  数据列"
echo ""
head -1 "$CSV_FILE" | tr ',' '\n' | nl -w2 -s'  . ' | head -20

if [ $(head -1 "$CSV_FILE" | tr ',' '\n' | wc -l) -gt 20 ]; then
    echo "... (更多列)"
fi

echo ""
echo "## 🔍 数据预览 (前3行)"
echo "\`\`\`csv"
head -4 "$CSV_FILE" | sed 's/,/, /g'
echo "\`\`\`"

echo ""
echo "## 📊 基础统计"
echo "- 文件格式: CSV"
echo "- 编码: UTF-8"
echo "- 分隔符: 逗号 (,)"

echo ""
echo "## 🚀 下一步操作"
echo ""
echo "需要详细统计分析和可视化，请安装Python依赖:"
echo "\`\`\`bash"
echo "pip install pandas numpy matplotlib seaborn scipy scikit-learn"
echo "\`\`\`"
echo ""
echo "然后运行完整分析:"
echo "\`\`\`bash"
echo "# 需要pandas环境"
echo "# bash scripts/demo_source_info.sh $SOURCE_NAME"
echo "\`\`\`"