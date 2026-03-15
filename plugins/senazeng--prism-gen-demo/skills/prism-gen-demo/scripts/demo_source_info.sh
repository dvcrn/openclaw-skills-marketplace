#!/bin/bash
# 环境检查（不强制）
source "$(dirname "$0")/_simple_env.sh" 2>/dev/null || true
set -euo pipefail

# PRISM_GEN_DEMO - 查看数据源详细信息
# 显示CSV文件的结构、统计信息和样本数据

# 确保在正确的conda环境中运行
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
activate_env

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
DATA_DIR="$PROJECT_DIR/data"

# 检查参数
if [ $# -lt 1 ]; then
    echo "用法: $0 <数据源名称>"
    echo ""
    echo "示例:"
    echo "  $0 step4a_admet_final.csv"
    echo "  $0 step5b_final_candidates.csv"
    echo ""
    echo "使用 demo_list_sources.sh 查看所有可用数据源"
    exit 1
fi

SOURCE_NAME="$1"
CSV_FILE="$DATA_DIR/$SOURCE_NAME"

echo "# PRISM_GEN_DEMO - 数据源详细信息: $SOURCE_NAME"
echo ""

# 检查文件是否存在
if [ ! -f "$CSV_FILE" ]; then
    echo "❌ 文件不存在: $CSV_FILE"
    echo ""
    echo "可用文件:"
    find "$DATA_DIR" -name "*.csv" -type f -exec basename {} \; | sort
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

desc="${SOURCE_DESCS[$SOURCE_NAME]:-未知数据源}"

# 基本文件信息
file_size=$(du -h "$CSV_FILE" | cut -f1)
line_count=$(wc -l < "$CSV_FILE")
molecule_count=$((line_count - 1))
mod_time=$(stat -c "%y" "$CSV_FILE" | cut -d'.' -f1)

echo "## 📋 基本信息"
echo "- **描述**: $desc"
echo "- **大小**: $file_size"
echo "- **分子数**: $molecule_count"
echo "- **修改时间**: $mod_time"
echo "- **完整路径**: $CSV_FILE"
echo ""

# 读取表头
if [ $line_count -gt 0 ]; then
    header=$(head -1 "$CSV_FILE")
    IFS=',' read -ra columns <<< "$header"
    col_count=${#columns[@]}
    
    echo "## 🏷️  数据列 ($col_count列)"
    echo ""
    
    # 列分类
    declare -A col_categories
    col_categories["identifiers"]="标识符"
    col_categories["activity"]="活性"
    col_categories["physicochemical"]="物化性质"
    col_categories["safety"]="安全性"
    col_categories["druglikeness"]="药物相似性"
    col_categories["electronic"]="电子性质"
    col_categories["docking"]="对接结果"
    col_categories["other"]="其他"
    
    # 分类映射
    declare -A col_mapping
    # 标识符
    col_mapping["smiles"]="identifiers"
    col_mapping["molecule_id"]="identifiers"
    col_mapping["name"]="identifiers"
    col_mapping["id"]="identifiers"
    
    # 活性
    col_mapping["pic50"]="activity"
    col_mapping["reward"]="activity"
    col_mapping["broad"]="activity"
    col_mapping["score"]="activity"
    col_mapping["activity"]="activity"
    
    # 物化性质
    col_mapping["logp"]="physicochemical"
    col_mapping["mw"]="physicochemical"
    col_mapping["tpsa"]="physicochemical"
    col_mapping["hbd"]="physicochemical"
    col_mapping["hba"]="physicochemical"
    col_mapping["rotatable_bonds"]="physicochemical"
    
    # 安全性
    col_mapping["herg"]="safety"
    col_mapping["ames"]="safety"
    col_mapping["hepatotoxicity"]="safety"
    col_mapping["toxicity"]="safety"
    
    # 药物相似性
    col_mapping["qed"]="druglikeness"
    col_mapping["sa"]="druglikeness"
    col_mapping["lipinski"]="druglikeness"
    
    # 电子性质
    col_mapping["gap"]="electronic"
    col_mapping["energy"]="electronic"
    col_mapping["dipole"]="electronic"
    col_mapping["homo"]="electronic"
    col_mapping["lumo"]="electronic"
    
    # 对接结果
    col_mapping["docking_score"]="docking"
    col_mapping["binding_energy"]="docking"
    col_mapping["interactions"]="docking"
    
    # 按分类组织列
    declare -A categorized_cols
    for col in "${columns[@]}"; do
        col_lower=$(echo "$col" | tr '[:upper:]' '[:lower:]')
        category="other"
        
        for key in "${!col_mapping[@]}"; do
            if [[ "$col_lower" == *"$key"* ]]; then
                category="${col_mapping[$key]}"
                break
            fi
        done
        
        categorized_cols["$category"]="${categorized_cols[$category]:-}$col, "
    done
    
    # 显示分类列
    for category in "${!col_categories[@]}"; do
        if [ -n "${categorized_cols[$category]:-}" ]; then
            cols="${categorized_cols[$category]%, }"
            echo "### ${col_categories[$category]}"
            echo "$cols" | tr ',' '\n' | sed 's/^/  - /'
            echo ""
        fi
    done
    
    # 显示样本数据
    echo "## 🔍 数据预览 (前5行)"
    echo "\`\`\`csv"
    head -6 "$CSV_FILE" | csvlook 2>/dev/null || head -6 "$CSV_FILE"
    echo "\`\`\`"
    echo ""
    
    # 使用Python进行更详细的分析
    echo "## 📈 数值列统计摘要"
    
    "$SCRIPT_DIR/_python_wrapper.sh" "
import pandas as pd
import numpy as np
import sys

try:
    df = pd.read_csv('$CSV_FILE')
    
    # 数值列
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    if numeric_cols:
        print('### 关键数值列统计')
        stats = df[numeric_cols].describe().round(3)
        
        # 显示最重要的列
        important_keys = ['pic50', 'reward', 'gap', 'score', 'logp', 'mw', 'tpsa', 'herg', 'broad', 'energy', 'qed', 'sa']
        display_cols = []
        
        for col in numeric_cols:
            col_lower = col.lower()
            for key in important_keys:
                if key in col_lower:
                    display_cols.append(col)
                    break
        
        # 如果没有匹配到重要列，显示前10个数值列
        if not display_cols:
            display_cols = numeric_cols[:10]
        
        if display_cols:
            print(stats[display_cols].to_string())
        else:
            print('（无显著数值列）')
    else:
        print('（无数值列）')
    
    # 数据质量检查
    print('')
    print('### ✅ 数据质量检查')
    total_cells = df.size
    missing_cells = df.isnull().sum().sum()
    missing_pct = (missing_cells / total_cells * 100) if total_cells > 0 else 0
    
    print(f'- 总数据点: {total_cells}')
    print(f'- 缺失值: {missing_cells} ({missing_pct:.1f}%)')
    print(f'- 重复行: {df.duplicated().sum()}')
    
    # 列类型分布
    print('')
    print('### 📊 数据类型分布')
    dtypes = df.dtypes.value_counts()
    for dtype, count in dtypes.items():
        print(f'- {dtype}: {count}列')
    
except Exception as e:
    print(f'❌ 数据分析错误: {e}')
    sys.exit(1)
"
    
    echo ""
    echo "## 🛠️  可用操作"
    echo ""
    echo "```bash"
    echo "# 1. 数据预览"
    echo "bash scripts/demo_preview.sh $SOURCE_NAME 20"
    echo ""
    echo "# 2. 简单过滤"
    echo "bash scripts/demo_filter.sh $SOURCE_NAME pic50 '>' 7.0"
    echo ""
    echo "# 3. Top N筛选"
    echo "bash scripts/demo_top.sh $SOURCE_NAME pic50 10"
    echo ""
    echo "# 4. 可视化"
    echo "bash scripts/demo_plot_distribution.sh $SOURCE_NAME pic50"
    echo "```"
    
else
    echo "❌ 文件为空或无法读取"
fi