#!/bin/bash
# 环境检查（不强制）
source "$(dirname "$0")/_simple_env.sh" 2>/dev/null || true
set -euo pipefail

# PRISM_GEN_DEMO - 列出所有可用数据源
# 显示预计算CSV文件的概览信息

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
DATA_DIR="$PROJECT_DIR/data"

echo "# PRISM_GEN_DEMO - 真实数据源列表"
echo "## 📋 仅包含真实PRISM预计算结果"
echo ""

# 检查数据目录是否存在
if [ ! -d "$DATA_DIR" ]; then
    echo "❌ 数据目录不存在: $DATA_DIR"
    echo "请将预计算的CSV文件放入 data/ 目录"
    exit 1
fi

# 定义数据源描述
declare -A SOURCE_DESCS=(
    ["step3a_optimized_molecules.csv"]="阶段3a - 代理模型优化分子"
    ["step3a_optimized_molecules_raw.csv"]="阶段3a - 原始优化分子"
    ["step3a_top200.csv"]="阶段3a - Top200分子"
    ["step3b_dft_results.csv"]="阶段3b - xTB+DFT电子筛选结果"
    ["step3c_dft_refined.csv"]="阶段3c - GEM重排序结果"
    ["step4a_admet_final.csv"]="阶段4a - ADMET过滤结果"
    ["step4b_top_molecules_pyscf.csv"]="阶段4b - DFT验证(PySCF)结果"
    ["step4c_master_summary.csv"]="阶段4c - 主汇总表"
    ["step5a_broadspectrum_docking.csv"]="阶段5a - 广谱对接结果"
    ["step5b_final_candidates.csv"]="阶段5b - 最终候选分子"
)

echo "## 📁 数据目录: $DATA_DIR"
echo ""

# 列出所有CSV文件
csv_files=($(find "$DATA_DIR" -name "*.csv" -type f | sort))

if [ ${#csv_files[@]} -eq 0 ]; then
    echo "⚠️  未找到CSV文件"
    echo ""
    echo "请将预计算的CSV文件放入 data/ 目录，例如："
    echo "  cp /path/to/results/*.csv $DATA_DIR/"
    exit 0
fi

echo "## 📊 可用数据源 (${#csv_files[@]}个)"
echo ""

for csv_file in "${csv_files[@]}"; do
    filename=$(basename "$csv_file")
    desc="${SOURCE_DESCS[$filename]:-未知数据源}"
    
    # 获取文件信息
    if [ -f "$csv_file" ]; then
        file_size=$(du -h "$csv_file" | cut -f1)
        line_count=$(wc -l < "$csv_file" 2>/dev/null || echo "N/A")
        
        # 尝试获取列数（第一行）
        if [ "$line_count" != "N/A" ] && [ "$line_count" -gt 0 ]; then
            header=$(head -1 "$csv_file")
            col_count=$(echo "$header" | tr ',' '\n' | wc -l)
        else
            col_count="N/A"
        fi
        
        echo "### 🧪 $filename"
        echo "- **描述**: $desc"
        echo "- **大小**: $file_size"
        echo "- **行数**: $((line_count - 1)) 个分子"
        echo "- **列数**: $col_count 个属性"
        echo "- **路径**: $csv_file"
        echo ""
    fi
done

echo "## 🚀 快速开始"
echo ""
echo "使用以下命令查看具体数据源信息："
echo "\`\`\`bash"
echo "bash scripts/demo_source_info.sh <数据源名称>"
echo "\`\`\`"
echo ""
echo "例如："
echo "\`\`\`bash"
echo "bash scripts/demo_source_info.sh step4a_admet_final.csv"
echo "\`\`\`"

# 如果有示例数据，显示示例命令
if [ ${#csv_files[@]} -gt 0 ]; then
    first_file=$(basename "${csv_files[0]}")
    echo ""
    echo "## 💡 示例查询"
    echo "\`\`\`bash"
    echo "# 预览数据"
    echo "bash scripts/demo_preview.sh $first_file 10"
    echo ""
    echo "# 查看数据统计"
    echo "bash scripts/demo_source_info.sh $first_file"
    echo ""
    echo "# 简单过滤"
    echo "bash scripts/demo_filter.sh $first_file pIC50 '>' 7.0"
    echo "\`\`\`"
fi