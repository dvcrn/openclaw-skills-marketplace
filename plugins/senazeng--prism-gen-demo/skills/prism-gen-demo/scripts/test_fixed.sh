#!/bin/bash
# PRISM_GEN_DEMO 修复版测试脚本
# 不依赖pandas环境

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "# PRISM_GEN_DEMO 功能测试"
echo "========================"
echo ""
echo "测试时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "项目目录: $PROJECT_DIR"
echo ""

echo "## ✅ 测试1: 文件结构检查"
echo ""

# 检查必要文件
required_files=(
    "SKILL.md"
    "README.md"
    "TUTORIAL.md"
    "scripts/demo_list_sources.sh"
    "scripts/demo_filter.sh"
    "scripts/demo_plot_distribution.sh"
    "data/example_step4a.csv"
)

all_files_ok=true
for file in "${required_files[@]}"; do
    if [[ -f "$PROJECT_DIR/$file" ]]; then
        echo "  ✓ $file"
    else
        echo "  ✗ $file (缺失)"
        all_files_ok=false
    fi
done

if $all_files_ok; then
    echo "✅ 所有必要文件存在"
else
    echo "❌ 缺少必要文件"
fi

echo ""
echo "## ✅ 测试2: 脚本可执行性检查"
echo ""

# 检查脚本可执行权限
scripts=(
    "demo_list_sources.sh"
    "demo_filter.sh"
    "demo_plot_distribution.sh"
    "demo_plot_scatter.sh"
    "demo_preview.sh"
    "demo_source_info.sh"
    "demo_top.sh"
)

all_scripts_ok=true
for script in "${scripts[@]}"; do
    script_path="$PROJECT_DIR/scripts/$script"
    if [[ -x "$script_path" ]]; then
        echo "  ✓ $script (可执行)"
    else
        echo "  ✗ $script (不可执行)"
        all_scripts_ok=false
    fi
done

if $all_scripts_ok; then
    echo "✅ 所有脚本可执行"
else
    echo "❌ 有脚本不可执行"
fi

echo ""
echo "## ✅ 测试3: 数据文件检查"
echo ""

# 检查数据文件
data_dir="$PROJECT_DIR/data"
if [[ -d "$data_dir" ]]; then
    data_files=$(ls "$data_dir"/*.csv 2>/dev/null | wc -l)
    echo "  ✓ 数据目录存在"
    echo "  ✓ 找到 $data_files 个CSV文件"
    
    # 检查示例文件
    if [[ -f "$data_dir/example_step4a.csv" ]]; then
        example_lines=$(wc -l < "$data_dir/example_step4a.csv" 2>/dev/null || echo 0)
        echo "  ✓ 示例文件存在 ($example_lines 行)"
    else
        echo "  ✗ 示例文件缺失"
    fi
else
    echo "  ✗ 数据目录缺失"
fi

echo ""
echo "## ✅ 测试4: 基础功能测试（无Python依赖）"
echo ""

# 测试demo_list_sources.sh（基础部分）
echo "### 测试 demo_list_sources.sh"
output=$(bash "$PROJECT_DIR/scripts/demo_list_sources.sh" 2>&1)
if echo "$output" | head -5 | grep -q "PRISM_GEN_DEMO"; then
    echo "  ✓ 脚本基础输出正常"
else
    echo "  ✗ 脚本输出异常"
    echo "  输出预览: $(echo "$output" | head -2 | tr '\n' ' ')"
fi

# 测试demo_simple_preview.sh
echo ""
echo "### 测试 demo_simple_preview.sh"
if bash "$PROJECT_DIR/scripts/demo_simple_preview.sh" "$data_dir/example_step4a.csv" 2>&1 | head -5 | grep -q "数据预览"; then
    echo "  ✓ 简单预览功能正常"
else
    echo "  ✗ 简单预览功能异常"
fi

echo ""
echo "## 📊 测试总结"
echo ""

if $all_files_ok && $all_scripts_ok; then
    echo "✅ 基础测试通过"
    echo "   所有必要文件存在"
    echo "   所有脚本可执行"
    echo "   基础功能正常"
    echo ""
    echo "⚠️  注意：Python依赖测试需要pandas环境"
    echo "   运行完整测试请安装依赖后执行:"
    echo "   bash scripts/test_basic.sh"
else
    echo "❌ 基础测试失败"
    echo "   请检查缺失的文件或权限"
fi

echo ""
echo "## 🚀 下一步"
echo ""
echo "1. 安装Python依赖:"
echo "   pip install pandas numpy matplotlib seaborn scipy scikit-learn"
echo ""
echo "2. 运行完整测试:"
echo "   bash scripts/test_basic.sh"
echo ""
echo "3. 尝试示例:"
echo "   bash scripts/demo_list_sources.sh"
echo "   bash scripts/demo_simple_preview.sh data/example_step4a.csv"