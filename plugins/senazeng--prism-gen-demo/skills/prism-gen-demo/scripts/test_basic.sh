#!/bin/bash
set -euo pipefail

# 基本测试脚本 - 不依赖pandas

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
DATA_DIR="$PROJECT_DIR/data"

echo "# PRISM_GEN_DEMO - 基本功能测试"
echo "## 使用真实数据验证"
echo ""

# 测试1: 检查数据文件
echo "## ✅ 测试1: 数据文件检查"
csv_files=($(find "$DATA_DIR" -name "*.csv" -type f | sort))
echo "- 找到 ${#csv_files[@]} 个CSV文件"
echo ""

for csv_file in "${csv_files[@]}"; do
    filename=$(basename "$csv_file")
    line_count=$(wc -l < "$csv_file" 2>/dev/null || echo "0")
    molecule_count=$((line_count - 1))
    
    if [ "$line_count" -gt 0 ]; then
        echo "  ✓ $filename: $molecule_count 个分子"
    else
        echo "  ✗ $filename: 文件为空或无法读取"
    fi
done

echo ""
echo "## ✅ 测试2: 文件格式检查"
echo ""

# 检查step4a_admet_final.csv的格式
test_file="$DATA_DIR/step4a_admet_final.csv"
if [ -f "$test_file" ]; then
    echo "检查文件: $(basename "$test_file")"
    echo ""
    
    # 读取表头
    header=$(head -1 "$test_file")
    IFS=',' read -ra columns <<< "$header"
    
    echo "- 列数: ${#columns[@]}"
    echo "- 前10列:"
    for i in {0..9}; do
        if [ $i -lt ${#columns[@]} ]; then
            echo "  $((i+1)). ${columns[$i]}"
        fi
    done
    
    echo ""
    echo "- 关键列检查:"
    important_cols=("smiles" "pIC50" "QED" "LogP" "MW" "hERG_Prob")
    for col in "${important_cols[@]}"; do
        if [[ "$header" == *"$col"* ]]; then
            echo "  ✓ 包含: $col"
        else
            echo "  ✗ 缺少: $col"
        fi
    done
    
    echo ""
    echo "- 数据样本 (第2行):"
    head -2 "$test_file" | tail -1 | cut -d',' -f1-5 | sed 's/,/, /g'
else
    echo "测试文件不存在: $test_file"
fi

echo ""
echo "## ✅ 测试3: 脚本功能测试"
echo ""

# 测试demo_list_sources.sh
echo "### 测试 demo_list_sources.sh"
if bash scripts/demo_list_sources.sh 2>&1 | grep -q "可用数据源"; then
    echo "  ✓ 脚本执行成功"
else
    echo "  ✗ 脚本执行失败"
fi

echo ""
echo "### 测试 demo_source_info.sh (基础部分)"
if bash scripts/demo_source_info.sh step4a_admet_final.csv 2>&1 | head -20 | grep -q "基本信息"; then
    echo "  ✓ 脚本基础部分执行成功"
    echo "  ⚠️  Python分析部分需要pandas"
else
    echo "  ✗ 脚本执行失败"
fi

echo ""
echo "## 📋 环境检查"
echo ""

# 检查Python和必要包
echo "### Python环境"
if command -v "$SCRIPT_DIR/_python_wrapper.sh" &> /dev/null; then
    python_version=$("$SCRIPT_DIR/_python_wrapper.sh" --version 2>&1)
    echo "  ✓ $python_version"
    
    # 检查包
    echo "  - 包检查:"
    for pkg in pandas numpy; do
        if "$SCRIPT_DIR/_python_wrapper.sh" "import $pkg" 2>/dev/null; then
            echo "    ✓ $pkg 已安装"
        else
            echo "    ✗ $pkg 未安装"
        fi
    done
else
    echo "  ✗ Python3 未安装"
fi

echo ""
echo "## 🚀 安装建议"
echo ""
echo "如果需要完整功能，请安装Python包:"
echo "\`\`\`bash"
echo "pip install pandas numpy matplotlib seaborn"
echo "\`\`\`"
echo ""
echo "或者使用简化版本（仅基础功能）。"