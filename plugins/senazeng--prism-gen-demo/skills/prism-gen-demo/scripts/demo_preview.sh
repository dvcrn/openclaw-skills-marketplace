#!/bin/bash
# 环境检查（不强制）
source "$(dirname "$0")/_simple_env.sh" 2>/dev/null || true
set -euo pipefail

# PRISM_GEN_DEMO - 预览CSV数据
# 显示指定行数的数据预览，支持格式化输出

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
DATA_DIR="$PROJECT_DIR/data"

# 检查参数
if [ $# -lt 1 ]; then
    echo "用法: $0 <数据源名称> [行数]"
    echo ""
    echo "示例:"
    echo "  $0 step4a_admet_final.csv"
    echo "  $0 step5b_final_candidates.csv 20"
    echo ""
    echo "使用 demo_list_sources.sh 查看所有可用数据源"
    exit 1
fi

SOURCE_NAME="$1"
ROWS="${2:-10}"
CSV_FILE="$DATA_DIR/$SOURCE_NAME"

# 检查文件是否存在
if [ ! -f "$CSV_FILE" ]; then
    echo "❌ 文件不存在: $CSV_FILE"
    echo ""
    echo "可用文件:"
    find "$DATA_DIR" -name "*.csv" -type f -exec basename {} \; | sort
    exit 1
fi

# 检查行数参数
if ! [[ "$ROWS" =~ ^[0-9]+$ ]]; then
    echo "❌ 行数必须是正整数: $ROWS"
    exit 1
fi

if [ "$ROWS" -lt 1 ]; then
    ROWS=10
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

echo "# PRISM_GEN_DEMO - 数据预览: $SOURCE_NAME"
echo "## $desc"
echo ""

# 基本文件信息
line_count=$(wc -l < "$CSV_FILE")
molecule_count=$((line_count - 1))
display_rows=$((ROWS + 1))  # 包括表头

if [ "$display_rows" -gt "$line_count" ]; then
    display_rows="$line_count"
    ROWS=$((display_rows - 1))
fi

echo "**显示**: 表头 + $ROWS 行数据 (共 $molecule_count 个分子)"
echo "**时间**: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 使用Python进行智能预览
"$SCRIPT_DIR/_python_wrapper.sh" "
import pandas as pd
import numpy as np
import sys

try:
    # 读取数据
    df = pd.read_csv('$CSV_FILE')
    
    print('## 📊 数据概览')
    print(f'- 总行数: {len(df)}')
    print(f'- 总列数: {len(df.columns)}')
    print('')
    
    # 显示列信息
    print('## 🏷️  列信息')
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    text_cols = df.select_dtypes(include=['object']).columns.tolist()
    
    print(f'- 数值列 ({len(numeric_cols)}): ' + ', '.join(numeric_cols[:5]) + ('...' if len(numeric_cols) > 5 else ''))
    print(f'- 文本列 ({len(text_cols)}): ' + ', '.join(text_cols[:5]) + ('...' if len(text_cols) > 5 else ''))
    print('')
    
    # 显示预览
    print(f'## 🔍 数据预览 (前{min($ROWS, len(df))}行)')
    
    # 选择要显示的列（避免太宽）
    display_df = df.head($ROWS).copy()
    
    # 如果列太多，选择重要的列显示
    if len(df.columns) > 15:
        important_cols = []
        important_keys = ['smiles', 'molecule_id', 'name', 'pic50', 'reward', 'logp', 'mw', 'qed', 'sa', 'herg', 'gap']
        
        for col in df.columns:
            col_lower = col.lower()
            for key in important_keys:
                if key in col_lower:
                    important_cols.append(col)
                    break
        
        # 确保至少有8列
        if len(important_cols) < 8:
            important_cols = list(df.columns[:8]) + important_cols
            important_cols = list(dict.fromkeys(important_cols))[:12]
        
        display_df = display_df[important_cols]
        print(f'*注: 显示 {len(important_cols)} 个关键列 (共 {len(df.columns)} 列)*')
        print('')
    
    # 格式化显示
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', 30)
    
    # 对数值列进行格式化
    for col in display_df.columns:
        if pd.api.types.is_numeric_dtype(display_df[col]):
            display_df[col] = display_df[col].round(3)
    
    print(display_df.to_string(index=False))
    print('')
    
    # 显示关键统计信息
    print('## 📈 关键数值统计 (前' + str(min($ROWS, len(df))) + '行)')
    
    if numeric_cols:
        # 选择重要的数值列
        important_numeric = []
        important_keys = ['pic50', 'reward', 'gap', 'score', 'logp', 'mw', 'tpsa', 'herg', 'broad', 'energy', 'qed', 'sa']
        
        for col in numeric_cols:
            col_lower = col.lower()
            for key in important_keys:
                if key in col_lower:
                    important_numeric.append(col)
                    break
        
        if important_numeric:
            stats = display_df[important_numeric].describe().round(3)
            print(stats.to_string())
        else:
            print('（未检测到关键数值列）')
    else:
        print('（无数值列）')
    
    print('')
    print('## 💡 数据分析建议')
    
    # 基于数据特征提供建议
    if 'pic50' in df.columns:
        pic50_mean = df['pic50'].mean()
        if pic50_mean > 7.0:
            print('- ✅ 平均pIC50较高 (>7.0)，活性良好')
        elif pic50_mean > 6.0:
            print('- ⚠️  平均pIC50中等 (6.0-7.0)，有优化空间')
        else:
            print('- ❌ 平均pIC50较低 (<6.0)，需要进一步优化')
    
    if 'logp' in df.columns:
        logp_in_range = ((df['logp'] >= 1.5) & (df['logp'] <= 3.5)).mean()
        if logp_in_range > 0.7:
            print('- ✅ 大部分分子logP在理想范围 (1.5-3.5)')
        else:
            print(f'- ⚠️  仅 {logp_in_range:.1%} 分子logP在理想范围')
    
    if 'qed' in df.columns:
        qed_mean = df['qed'].mean()
        if qed_mean > 0.6:
            print('- ✅ 平均QED较高 (>0.6)，药物相似性好')
        else:
            print(f'- ⚠️  平均QED: {qed_mean:.2f}，药物相似性有待提高')
    
    if 'herg' in df.columns:
        herg_risk = (df['herg'] > 0.1).mean()
        if herg_risk < 0.1:
            print('- ✅ hERG风险低 (<10% 分子风险高)')
        else:
            print(f'- ⚠️  hERG风险: {herg_risk:.1%} 分子风险高')
    
except Exception as e:
    print(f'❌ 数据预览错误: {e}')
    sys.exit(1)
"

echo ""
echo "## 🚀 下一步操作"
echo ""
echo "```bash"
echo "# 1. 查看更多数据"
echo "bash scripts/demo_preview.sh $SOURCE_NAME $((ROWS * 2))"
echo ""
echo "# 2. 筛选高活性分子"
echo "bash scripts/demo_filter.sh $SOURCE_NAME pic50 '>' 7.0"
echo ""
echo "# 3. 查看Top分子"
echo "bash scripts/demo_top.sh $SOURCE_NAME pic50 10"
echo ""
echo "# 4. 生成可视化"
echo "bash scripts/demo_plot_distribution.sh $SOURCE_NAME pic50"
echo "```"