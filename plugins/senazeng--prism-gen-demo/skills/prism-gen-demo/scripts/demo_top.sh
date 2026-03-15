#!/bin/bash
# 环境检查（不强制）
source "$(dirname "$0")/_simple_env.sh" 2>/dev/null || true
set -euo pipefail

# PRISM_GEN_DEMO - Top N筛选
# 按指定列排序并筛选Top N分子

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
DATA_DIR="$PROJECT_DIR/data"
OUTPUT_DIR="$PROJECT_DIR/output/top"
mkdir -p "$OUTPUT_DIR"

# 检查参数
if [ $# -lt 3 ]; then
    echo "用法: $0 <数据源名称> <排序列> <N> [asc|desc]"
    echo ""
    echo "参数说明:"
    echo "  <数据源名称> : CSV文件名，如 step4a_admet_final.csv"
    echo "  <排序列>     : 排序依据的列名，如 pIC50、QED、LogP等"
    echo "  <N>          : 返回的Top N分子数量"
    echo "  [asc|desc]   : 排序方向，desc为降序（默认），asc为升序"
    echo ""
    echo "示例:"
    echo "  $0 step4a_admet_final.csv pIC50 10          # Top 10高活性分子"
    echo "  $0 step4a_admet_final.csv hERG_Prob 5 asc   # Top 5低hERG风险分子"
    echo "  $0 step4a_admet_final.csv QED 20            # Top 20药物相似性分子"
    echo ""
    echo "使用 demo_list_sources.sh 查看所有可用数据源"
    exit 1
fi

SOURCE_NAME="$1"
SORT_COLUMN="$2"
N="$3"
DIRECTION="${4:-desc}"
CSV_FILE="$DATA_DIR/$SOURCE_NAME"

# 检查文件是否存在
if [ ! -f "$CSV_FILE" ]; then
    echo "❌ 文件不存在: $CSV_FILE"
    echo ""
    echo "可用文件:"
    find "$DATA_DIR" -name "*.csv" -type f -exec basename {} \; | sort
    exit 1
fi

# 检查参数
if ! [[ "$N" =~ ^[0-9]+$ ]]; then
    echo "❌ N必须是正整数: $N"
    exit 1
fi

if [ "$DIRECTION" != "asc" ] && [ "$DIRECTION" != "desc" ]; then
    echo "❌ 排序方向必须是 'asc' 或 'desc': $DIRECTION"
    exit 1
fi

# 生成输出文件名
timestamp=$(date '+%Y%m%d_%H%M%S')
safe_column=$(echo "$SORT_COLUMN" | tr -c '[:alnum:]' '_')
output_file="$OUTPUT_DIR/${SOURCE_NAME%.csv}_top${N}_${safe_column}_${DIRECTION}_${timestamp}.csv"

echo "# PRISM_GEN_DEMO - Top N筛选"
echo "## 按 $SORT_COLUMN $DIRECTION 排序，取Top $N"
echo ""

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
echo "**数据源**: $SOURCE_NAME ($desc)"
echo "**排序规则**: 按 $SORT_COLUMN $DIRECTION 排序"
echo "**返回数量**: Top $N 个分子"
echo "**输出文件**: $output_file"
echo "**时间**: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 使用Python进行Top N筛选
"$SCRIPT_DIR/_python_wrapper.sh" "
import pandas as pd
import numpy as np
import sys

try:
    # 读取数据
    df = pd.read_csv('$CSV_FILE')
    original_count = len(df)
    
    print('## 📊 原始数据')
    print(f'- 总分子数: {original_count}')
    print(f'- 总列数: {len(df.columns)}')
    
    # 检查排序列是否存在
    if '$SORT_COLUMN' not in df.columns:
        print(f'❌ 列不存在: $SORT_COLUMN')
        print('')
        print('可用列:')
        for i, col in enumerate(df.columns, 1):
            print(f'  {i:2d}. {col}')
        sys.exit(1)
    
    col_dtype = df['$SORT_COLUMN'].dtype
    print(f'- 排序列: $SORT_COLUMN ({col_dtype})')
    
    # 检查是否为数值列
    if not np.issubdtype(col_dtype, np.number):
        print(f'⚠️  警告: $SORT_COLUMN 不是数值列，排序可能不如预期')
    
    # 执行排序
    ascending = True if '$DIRECTION' == 'asc' else False
    sorted_df = df.sort_values(by='$SORT_COLUMN', ascending=ascending, na_position='last')
    
    # 取Top N
    top_n = min($N, original_count)
    top_df = sorted_df.head(top_n).copy()
    
    print('')
    print(f'## ✅ Top {top_n} 筛选结果')
    
    if top_n < $N:
        print(f'⚠️  注意: 请求Top $N，但数据只有 {original_count} 行，返回Top {top_n}')
    
    # 保存结果
    top_df.to_csv('$output_file', index=False)
    print(f'- 已保存: $output_file')
    print(f'- 文件大小: {top_df.memory_usage(deep=True).sum() / 1024:.1f} KB')
    print('')
    
    # 显示Top N分子的关键信息
    print('## 🏆 Top分子关键信息')
    print('')
    
    # 确定显示哪些列
    display_columns = []
    important_cols = ['smiles', 'pIC50', 'QED', 'LogP', 'MW', 'hERG_Prob', 'SA', 'TPSA', 'Reward', 'R_global']
    
    for col in important_cols:
        if col in top_df.columns:
            display_columns.append(col)
    
    # 如果重要列太少，添加排序列和其他列
    if len(display_columns) < 5:
        display_columns.append('$SORT_COLUMN')
        # 添加其他数值列
        numeric_cols = top_df.select_dtypes(include=[np.number]).columns.tolist()
        for col in numeric_cols[:3]:
            if col not in display_columns:
                display_columns.append(col)
    
    # 显示表格
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', 30)
    
    display_df = top_df[display_columns].copy()
    
    # 格式化数值列
    for col in display_df.columns:
        if pd.api.types.is_numeric_dtype(display_df[col]):
            display_df[col] = display_df[col].round(3)
    
    print(display_df.to_string(index=False))
    print('')
    
    # 统计信息
    print('## 📈 Top N 统计摘要')
    print('')
    
    if pd.api.types.is_numeric_dtype(top_df['$SORT_COLUMN']):
        print(f'**排序列 ($SORT_COLUMN) 统计**:')
        col_stats = top_df['$SORT_COLUMN'].describe()
        
        print(f'- 平均值: {col_stats[\"mean\"]:.3f}')
        print(f'- 中位数: {col_stats[\"50%\"]:.3f}')
        print(f'- 标准差: {col_stats[\"std\"]:.3f}')
        print(f'- 范围: [{col_stats[\"min\"]:.3f}, {col_stats[\"max\"]:.3f}]')
        print('')
        
        # 与原始数据对比
        original_stats = df['$SORT_COLUMN'].describe()
        improvement = ((col_stats['mean'] - original_stats['mean']) / original_stats['mean'] * 100) if original_stats['mean'] != 0 else 0
        
        if not ascending:  # 降序排序，值应该变大
            if improvement > 0:
                print(f'✅ 优化效果: Top {top_n} 的 $SORT_COLUMN 平均值提升了 {improvement:.1f}%')
            else:
                print(f'⚠️  注意: Top {top_n} 的 $SORT_COLUMN 平均值变化不大')
        else:  # 升序排序，值应该变小
            if improvement < 0:
                print(f'✅ 优化效果: Top {top_n} 的 $SORT_COLUMN 平均值降低了 {abs(improvement):.1f}%')
            else:
                print(f'⚠️  注意: Top {top_n} 的 $SORT_COLUMN 平均值变化不大')
    
    # 多指标分析
    print('')
    print('## 💊 多指标质量分析')
    print('')
    
    analysis_results = []
    
    # 活性分析
    if 'pIC50' in top_df.columns and pd.api.types.is_numeric_dtype(top_df['pIC50']):
        high_activity = (top_df['pIC50'] > 7.0).mean()
        analysis_results.append(f'- 高活性比例: {high_activity:.1%} (pIC50 > 7.0)')
    
    # 药物相似性
    if 'QED' in top_df.columns and pd.api.types.is_numeric_dtype(top_df['QED']):
        good_qed = (top_df['QED'] > 0.6).mean()
        analysis_results.append(f'- 良好QED比例: {good_qed:.1%} (QED > 0.6)')
    
    # hERG风险
    if 'hERG_Prob' in top_df.columns and pd.api.types.is_numeric_dtype(top_df['hERG_Prob']):
        low_herg = (top_df['hERG_Prob'] < 0.1).mean()
        analysis_results.append(f'- 低hERG风险比例: {low_herg:.1%} (hERG_Prob < 0.1)')
    
    # LogP范围
    if 'LogP' in top_df.columns and pd.api.types.is_numeric_dtype(top_df['LogP']):
        good_logp = ((top_df['LogP'] >= 1.5) & (top_df['LogP'] <= 3.5)).mean()
        analysis_results.append(f'- 理想LogP比例: {good_logp:.1%} (1.5 ≤ LogP ≤ 3.5)')
    
    # 分子量
    if 'MW' in top_df.columns and pd.api.types.is_numeric_dtype(top_df['MW']):
        good_mw = ((top_df['MW'] >= 200) & (top_df['MW'] <= 500)).mean()
        analysis_results.append(f'- 理想分子量比例: {good_mw:.1%} (200 ≤ MW ≤ 500)')
    
    if analysis_results:
        for result in analysis_results:
            print(result)
    else:
        print('（无关键指标数据）')
    
    print('')
    
    # 排名变化分析（如果原始数据有排名信息）
    if 'rank_total' in top_df.columns or 'rank_R0' in top_df.columns:
        print('## 📊 排名分析')
        print('')
        
        if 'rank_total' in top_df.columns:
            avg_rank = top_df['rank_total'].mean()
            best_rank = top_df['rank_total'].min()
            print(f'- 平均总排名: {avg_rank:.1f}')
            print(f'- 最佳总排名: {best_rank}')
        
        if 'rank_R0' in top_df.columns:
            avg_r0_rank = top_df['rank_R0'].mean()
            best_r0_rank = top_df['rank_R0'].min()
            print(f'- 平均R0排名: {avg_r0_rank:.1f}')
            print(f'- 最佳R0排名: {best_r0_rank}')
    
    # 建议下一步操作
    print('')
    print('## 🎯 筛选效果评估')
    print('')
    
    if top_n == $N:
        print(f'✅ 成功筛选出Top $N 个分子')
        
        # 根据排序列给出建议
        if '$SORT_COLUMN' == 'pIC50':
            print('  这些是活性最高的分子，适合进一步生物实验验证')
        elif '$SORT_COLUMN' == 'QED':
            print('  这些是药物相似性最好的分子，成药性较高')
        elif '$SORT_COLUMN' == 'hERG_Prob':
            if '$DIRECTION' == 'asc':
                print('  这些是hERG风险最低的分子，安全性较好')
            else:
                print('  这些是hERG风险最高的分子，需要谨慎评估')
        elif '$SORT_COLUMN' == 'LogP':
            if '$DIRECTION' == 'desc':
                print('  这些是脂溶性最高的分子，可能渗透性较好')
            else:
                print('  这些是脂溶性最低的分子，可能水溶性较好')
        else:
            print('  筛选完成，建议结合其他指标进行综合评估')
    else:
        print(f'⚠️  数据量不足，只返回了Top {top_n} 个分子')
        print('  考虑使用更大的数据集或减少N值')
    
except Exception as e:
    print(f'❌ Top N筛选错误: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
"

echo ""
echo "## 🚀 下一步操作"
echo ""
echo "\`\`\`bash"
echo "# 1. 查看完整Top N结果"
echo "bash scripts/demo_preview.sh $(basename "$output_file")"
echo ""
echo "# 2. 基于其他指标进一步筛选"
if [ "$SORT_COLUMN" != "pIC50" ]; then
    echo "bash scripts/demo_top.sh $(basename "$output_file") pIC50 10"
fi
if [ "$SORT_COLUMN" != "QED" ]; then
    echo "bash scripts/demo_top.sh $(basename "$output_file") QED 10"
fi
echo ""
echo "# 3. 多条件过滤"
echo "bash scripts/demo_filter.sh $(basename "$output_file") hERG_Prob '<' 0.1"
echo ""
echo "# 4. 生成可视化"
echo "bash scripts/demo_plot_distribution.sh $(basename "$output_file") $SORT_COLUMN"
echo "\`\`\`"
echo ""
echo "**提示**: Top N结果保存在 output/top/ 目录，可用于后续分析或作为最终候选列表"