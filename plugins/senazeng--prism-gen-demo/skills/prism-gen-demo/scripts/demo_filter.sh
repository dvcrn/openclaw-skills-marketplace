#!/bin/bash
# 环境检查（不强制）
source "$(dirname "$0")/_simple_env.sh" 2>/dev/null || true
set -euo pipefail

# PRISM_GEN_DEMO - 简单条件过滤
# 根据单列条件过滤CSV数据

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
DATA_DIR="$PROJECT_DIR/data"
OUTPUT_DIR="$PROJECT_DIR/output/filtered"
mkdir -p "$OUTPUT_DIR"

# 检查参数
if [ $# -lt 4 ]; then
    echo "用法: $0 <数据源名称> <列名> <操作符> <值>"
    echo ""
    echo "操作符:"
    echo "  '>'   : 大于"
    echo "  '>='  : 大于等于"
    echo "  '<'   : 小于"
    echo "  '<='  : 小于等于"
    echo "  '='   : 等于"
    echo "  '!='  : 不等于"
    echo "  '~'   : 包含（字符串）"
    echo "  '!~'  : 不包含（字符串）"
    echo ""
    echo "示例:"
    echo "  $0 step4a_admet_final.csv pIC50 '>' 7.0"
    echo "  $0 step4a_admet_final.csv LogP '1.5-3.5' ''   # 范围过滤"
    echo "  $0 step4a_admet_final.csv smiles '~' 'CC(=O)' # 包含子结构"
    echo ""
    echo "使用 demo_list_sources.sh 查看所有可用数据源"
    exit 1
fi

SOURCE_NAME="$1"
COLUMN="$2"
OPERATOR="$3"
VALUE="$4"
CSV_FILE="$DATA_DIR/$SOURCE_NAME"

# 检查文件是否存在
if [ ! -f "$CSV_FILE" ]; then
    echo "❌ 文件不存在: $CSV_FILE"
    echo ""
    echo "可用文件:"
    find "$DATA_DIR" -name "*.csv" -type f -exec basename {} \; | sort
    exit 1
fi

# 生成输出文件名
timestamp=$(date '+%Y%m%d_%H%M%S')
safe_column=$(echo "$COLUMN" | tr -c '[:alnum:]' '_')
output_file="$OUTPUT_DIR/${SOURCE_NAME%.csv}_filtered_${safe_column}_${OPERATOR}_${VALUE}_${timestamp}.csv"

echo "# PRISM_GEN_DEMO - 数据过滤"
echo "## 条件: $COLUMN $OPERATOR $VALUE"
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
echo "**过滤条件**: $COLUMN $OPERATOR $VALUE"
echo "**输出文件**: $output_file"
echo "**时间**: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 使用Python进行过滤
"$SCRIPT_DIR/_python_wrapper.sh" "
import pandas as pd
import numpy as np
import re
import sys

try:
    # 读取数据
    df = pd.read_csv('$CSV_FILE')
    original_count = len(df)
    
    print('## 📊 原始数据')
    print(f'- 总分子数: {original_count}')
    print(f'- 总列数: {len(df.columns)}')
    
    # 检查列是否存在
    if '$COLUMN' not in df.columns:
        print(f'❌ 列不存在: $COLUMN')
        print('')
        print('可用列:')
        for i, col in enumerate(df.columns, 1):
            print(f'  {i:2d}. {col}')
        sys.exit(1)
    
    print(f'- 目标列: $COLUMN ({df[\"$COLUMN\"].dtype})')
    print('')
    
    # 执行过滤
    filtered_df = df.copy()
    
    # 处理范围过滤 (如 '1.5-3.5')
    if '$OPERATOR' == '' and '-' in '$VALUE':
        try:
            range_parts = '$VALUE'.split('-')
            if len(range_parts) == 2:
                min_val = float(range_parts[0])
                max_val = float(range_parts[1])
                filtered_df = df[(df['$COLUMN'] >= min_val) & (df['$COLUMN'] <= max_val)]
                condition_desc = f'{min_val} ≤ $COLUMN ≤ {max_val}'
            else:
                raise ValueError('无效的范围格式')
        except ValueError as e:
            print(f'❌ 范围解析错误: {e}')
            sys.exit(1)
    
    # 处理数值比较
    elif df['$COLUMN'].dtype in [np.float64, np.int64]:
        try:
            num_value = float('$VALUE') if '$VALUE' else 0
            
            if '$OPERATOR' == '>':
                filtered_df = df[df['$COLUMN'] > num_value]
                condition_desc = f'$COLUMN > {num_value}'
            elif '$OPERATOR' == '>=':
                filtered_df = df[df['$COLUMN'] >= num_value]
                condition_desc = f'$COLUMN ≥ {num_value}'
            elif '$OPERATOR' == '<':
                filtered_df = df[df['$COLUMN'] < num_value]
                condition_desc = f'$COLUMN < {num_value}'
            elif '$OPERATOR' == '<=':
                filtered_df = df[df['$COLUMN'] <= num_value]
                condition_desc = f'$COLUMN ≤ {num_value}'
            elif '$OPERATOR' == '=':
                filtered_df = df[df['$COLUMN'] == num_value]
                condition_desc = f'$COLUMN = {num_value}'
            elif '$OPERATOR' == '!=':
                filtered_df = df[df['$COLUMN'] != num_value]
                condition_desc = f'$COLUMN ≠ {num_value}'
            else:
                print(f'❌ 不支持的操作符: $OPERATOR (数值列)')
                sys.exit(1)
        
        except ValueError:
            print(f'❌ 值转换错误: \"$VALUE\" 无法转换为数值')
            sys.exit(1)
    
    # 处理字符串操作
    else:
        str_value = '$VALUE'
        
        if '$OPERATOR' == '=':
            filtered_df = df[df['$COLUMN'].astype(str) == str_value]
            condition_desc = f'$COLUMN = \"{str_value}\"'
        elif '$OPERATOR' == '!=':
            filtered_df = df[df['$COLUMN'].astype(str) != str_value]
            condition_desc = f'$COLUMN ≠ \"{str_value}\"'
        elif '$OPERATOR' == '~':
            filtered_df = df[df['$COLUMN'].astype(str).str.contains(str_value, na=False)]
            condition_desc = f'$COLUMN 包含 \"{str_value}\"'
        elif '$OPERATOR' == '!~':
            filtered_df = df[~df['$COLUMN'].astype(str).str.contains(str_value, na=False)]
            condition_desc = f'$COLUMN 不包含 \"{str_value}\"'
        else:
            print(f'❌ 不支持的操作符: $OPERATOR (文本列)')
            sys.exit(1)
    
    filtered_count = len(filtered_df)
    filtered_pct = (filtered_count / original_count * 100) if original_count > 0 else 0
    
    print('## ✅ 过滤结果')
    print(f'- 条件: {condition_desc}')
    print(f'- 过滤后分子数: {filtered_count}')
    print(f'- 过滤比例: {filtered_pct:.1f}%')
    print('')
    
    if filtered_count == 0:
        print('⚠️  没有匹配的分子')
        print('')
        print('建议:')
        print('1. 检查列名和值是否正确')
        print('2. 尝试不同的操作符')
        print('3. 查看该列的数值范围:')
        if df['$COLUMN'].dtype in [np.float64, np.int64]:
            col_stats = df['$COLUMN'].describe()
            print(f'   - 最小值: {col_stats[\"min\"]:.3f}')
            print(f'   - 平均值: {col_stats[\"mean\"]:.3f}')
            print(f'   - 最大值: {col_stats[\"max\"]:.3f}')
        else:
            unique_vals = df['$COLUMN'].dropna().unique()[:10]
            print(f'   - 示例值: {', '.join(map(str, unique_vals))}' + ('...' if len(df['$COLUMN'].unique()) > 10 else ''))
        
        sys.exit(0)
    
    # 保存结果
    filtered_df.to_csv('$output_file', index=False)
    print(f'## 💾 结果已保存')
    print(f'- 文件: $output_file')
    print(f'- 大小: {filtered_df.memory_usage(deep=True).sum() / 1024:.1f} KB')
    print('')
    
    # 显示过滤后的统计信息
    print('## 📈 过滤后数据统计')
    
    # 关键数值列统计
    numeric_cols = filtered_df.select_dtypes(include=[np.number]).columns.tolist()
    important_keys = ['pic50', 'reward', 'gap', 'score', 'logp', 'mw', 'tpsa', 'herg', 'broad', 'energy', 'qed', 'sa']
    display_cols = []
    
    for col in numeric_cols:
        col_lower = col.lower()
        for key in important_keys:
            if key in col_lower:
                display_cols.append(col)
                break
    
    if display_cols:
        stats = filtered_df[display_cols].describe().round(3)
        print(stats.to_string())
    else:
        print('（无关键数值列）')
    
    print('')
    
    # 显示前10行
    print('## 🔍 过滤结果预览 (前10行)')
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', 30)
    
    preview_df = filtered_df.head(10).copy()
    for col in preview_df.columns:
        if pd.api.types.is_numeric_dtype(preview_df[col]):
            preview_df[col] = preview_df[col].round(3)
    
    print(preview_df.to_string(index=False))
    print('')
    
    # 与原始数据对比
    print('## 📊 过滤前后对比')
    
    if '$COLUMN' in numeric_cols:
        original_stats = df['$COLUMN'].describe()
        filtered_stats = filtered_df['$COLUMN'].describe()
        
        print(f'**列: $COLUMN**')
        print('| 统计量 | 原始数据 | 过滤后 | 变化 |')
        print('|--------|----------|--------|------|')
        
        for stat in ['count', 'mean', 'std', 'min', '25%', '50%', '75%', 'max']:
            if stat in original_stats and stat in filtered_stats:
                orig_val = original_stats[stat]
                filt_val = filtered_stats[stat]
                
                if stat == 'count':
                    change = f'+{filtered_count - original_count}' if filtered_count > original_count else f'{filtered_count - original_count}'
                else:
                    change_pct = ((filt_val - orig_val) / orig_val * 100) if orig_val != 0 else 0
                    change = f'{change_pct:+.1f}%'
                
                if stat in ['mean', '50%']:
                    orig_fmt = f'{orig_val:.3f}'
                    filt_fmt = f'{filt_val:.3f}'
                else:
                    orig_fmt = f'{orig_val:.3f}' if isinstance(orig_val, float) else str(orig_val)
                    filt_fmt = f'{filt_val:.3f}' if isinstance(filt_val, float) else str(filt_val)
                
                print(f'| {stat} | {orig_fmt} | {filt_fmt} | {change} |')
    
    print('')
    
    # 过滤效果分析
    print('## 💡 过滤效果分析')
    
    if filtered_pct > 80:
        print('- ⚠️  过滤条件较宽松 (>80% 分子保留)')
        print('  考虑使用更严格的条件')
    elif filtered_pct < 20:
        print('- ✅ 过滤条件较严格 (<20% 分子保留)')
        print('  得到了高度筛选的结果集')
    else:
        print('- 📊 过滤条件适中 (20-80% 分子保留)')
        print('  平衡了筛选效果和样本量')
    
    # 检查过滤后数据的质量
    if 'pic50' in filtered_df.columns:
        high_activity = (filtered_df['pic50'] > 7.0).mean()
        if high_activity > 0.5:
            print(f'- 🎯 高活性分子比例: {high_activity:.1%} (>7.0 pIC50)')
    
    if 'qed' in filtered_df.columns:
        good_qed = (filtered_df['qed'] > 0.6).mean()
        if good_qed > 0.5:
            print(f'- 💊 良好药物相似性比例: {good_qed:.1%} (>0.6 QED)')
    
    if 'herg' in filtered_df.columns:
        low_herg = (filtered_df['herg'] < 0.1).mean()
        if low_herg > 0.5:
            print(f'- ⚕️  低hERG风险比例: {low_herg:.1%} (<0.1 hERG)')
    
except Exception as e:
    print(f'❌ 过滤错误: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
"

echo ""
echo "## 🚀 下一步操作"
echo ""
echo "\`\`\`bash"
echo "# 1. 查看完整过滤结果"
echo "bash scripts/demo_preview.sh \$(basename \"\$output_file\")"
echo ""
echo "# 2. 进一步筛选"
echo "bash scripts/demo_filter.sh \$(basename \"\$output_file\") qed '>' 0.6"
echo ""
echo "# 3. 排序结果"
echo "bash scripts/demo_top.sh \$(basename \"\$output_file\") pic50 20"
echo ""
echo "# 4. 生成可视化"
echo "bash scripts/demo_plot_distribution.sh \$(basename \"\$output_file\") pic50"
echo "\`\`\`"
echo ""
echo "**提示**: 过滤结果保存在 output/filtered/ 目录，可用于后续分析"