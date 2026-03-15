#!/bin/bash
# 环境检查（不强制）
source "$(dirname "$0")/_simple_env.sh" 2>/dev/null || true
set -euo pipefail

# PRISM_GEN_DEMO - 散点图分析
# 分析两个变量之间的相关性，生成散点图和相关统计

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
DATA_DIR="$PROJECT_DIR/data"
PLOT_DIR="$PROJECT_DIR/plots"
mkdir -p "$PLOT_DIR"

# 检查参数
if [ $# -lt 3 ]; then
    echo "用法: $0 <数据源名称> <X轴列> <Y轴列> [选项]"
    echo ""
    echo "参数说明:"
    echo "  <数据源名称> : CSV文件名"
    echo "  <X轴列>      : X轴变量列名"
    echo "  <Y轴列>      : Y轴变量列名"
    echo ""
    echo "选项:"
    echo "  --hue <列>      : 按列分组着色"
    echo "  --size <列>     : 按列调整点大小"
    echo "  --style <列>    : 按列调整点样式"
    echo "  --title <标题>  : 图表标题"
    echo "  --output <名称> : 输出文件名"
    echo "  --format <格式> : png|pdf|svg (默认: png)"
    echo "  --dpi <分辨率>  : 图像分辨率 (默认: 150)"
    echo "  --trendline     : 添加趋势线"
    echo "  --correlation   : 计算并显示相关系数"
    echo "  --regression    : 添加回归线"
    echo "  --logx          : X轴对数刻度"
    echo "  --logy          : Y轴对数刻度"
    echo "  --grid          : 显示网格"
    echo ""
    echo "示例:"
    echo "  $0 step4a_admet_final.csv pIC50 QED"
    echo "  $0 step4a_admet_final.csv LogP pIC50 --trendline --correlation"
    echo "  $0 step4a_admet_final.csv MW LogP --hue Active_Set --title '分子量vsLogP'"
    echo "  $0 step4a_admet_final.csv pIC50 hERG_Prob --regression --logy"
    echo ""
    echo "使用 demo_list_sources.sh 查看所有可用数据源"
    exit 1
fi

SOURCE_NAME="$1"
X_COLUMN="$2"
Y_COLUMN="$3"
shift 3

# 解析选项
HUE_COLUMN=""
SIZE_COLUMN=""
STYLE_COLUMN=""
TITLE=""
OUTPUT_NAME=""
FORMAT="png"
DPI=150
TRENDLINE=false
CORRELATION=false
REGRESSION=false
LOGX=false
LOGY=false
GRID=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --hue)
            HUE_COLUMN="$2"
            shift 2
            ;;
        --size)
            SIZE_COLUMN="$2"
            shift 2
            ;;
        --style)
            STYLE_COLUMN="$2"
            shift 2
            ;;
        --title)
            TITLE="$2"
            shift 2
            ;;
        --output)
            OUTPUT_NAME="$2"
            shift 2
            ;;
        --format)
            FORMAT="$2"
            shift 2
            ;;
        --dpi)
            DPI="$2"
            shift 2
            ;;
        --trendline)
            TRENDLINE=true
            shift
            ;;
        --correlation)
            CORRELATION=true
            shift
            ;;
        --regression)
            REGRESSION=true
            shift
            ;;
        --logx)
            LOGX=true
            shift
            ;;
        --logy)
            LOGY=true
            shift
            ;;
        --grid)
            GRID=true
            shift
            ;;
        *)
            echo "❌ 未知选项: $1"
            exit 1
            ;;
    esac
done

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
safe_x=$(echo "$X_COLUMN" | tr -c '[:alnum:]' '_')
safe_y=$(echo "$Y_COLUMN" | tr -c '[:alnum:]' '_')

if [ -z "$OUTPUT_NAME" ]; then
    OUTPUT_NAME="${SOURCE_NAME%.csv}_scatter_${safe_x}_vs_${safe_y}_${timestamp}.$FORMAT"
else
    if [[ ! "$OUTPUT_NAME" =~ \.(png|pdf|svg)$ ]]; then
        OUTPUT_NAME="${OUTPUT_NAME}.$FORMAT"
    fi
fi

output_file="$PLOT_DIR/$OUTPUT_NAME"

echo "# PRISM_GEN_DEMO - 散点图分析"
echo "## $X_COLUMN vs $Y_COLUMN"
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
echo "**X轴**: $X_COLUMN"
echo "**Y轴**: $Y_COLUMN"
echo "**输出文件**: $output_file"
echo "**格式**: $FORMAT, DPI: $DPI"
echo "**选项**: trendline=$TRENDLINE, correlation=$CORRELATION, regression=$REGRESSION"
echo "**时间**: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 使用Python生成散点图和相关分析
"$SCRIPT_DIR/_python_wrapper.sh" "
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import warnings
import sys
import os
warnings.filterwarnings('ignore')

try:
    # 读取数据
    df = pd.read_csv('$CSV_FILE')
    
    print('## 📊 数据概览')
    print(f'- 总分子数: {len(df)}')
    print(f'- 总列数: {len(df.columns)}')
    
    # 检查列是否存在
    missing_cols = []
    for col in ['$X_COLUMN', '$Y_COLUMN']:
        if col not in df.columns:
            missing_cols.append(col)
    
    if missing_cols:
        print(f'❌ 列不存在: {missing_cols}')
        print('')
        print('可用列:')
        for i, col in enumerate(df.columns, 1):
            print(f'  {i:2d}. {col}')
        sys.exit(1)
    
    # 检查是否为数值列
    for col in ['$X_COLUMN', '$Y_COLUMN']:
        if not pd.api.types.is_numeric_dtype(df[col]):
            print(f'⚠️  警告: {col} 不是数值列，将尝试转换为数值')
            try:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            except:
                print(f'❌ 无法将 {col} 转换为数值列')
                sys.exit(1)
    
    # 移除NaN值
    analysis_df = df[['$X_COLUMN', '$Y_COLUMN']].dropna()
    if len(analysis_df) == 0:
        print('❌ 没有有效数据进行分析')
        sys.exit(1)
    
    print(f'- 有效数据点: {len(analysis_df)}')
    print('')
    
    # 相关性分析
    print('## 📈 相关性分析')
    print('')
    
    x_data = analysis_df['$X_COLUMN']
    y_data = analysis_df['$Y_COLUMN']
    
    # Pearson相关系数
    pearson_corr, pearson_p = stats.pearsonr(x_data, y_data)
    print(f'**Pearson相关系数**: {pearson_corr:.4f}')
    print(f'  - p值: {pearson_p:.4e}')
    
    if pearson_p < 0.05:
        print('  - ✅ 相关性统计显著 (p < 0.05)')
    else:
        print('  - ⚠️  相关性不显著 (p ≥ 0.05)')
    
    # 解释相关性强度
    abs_corr = abs(pearson_corr)
    if abs_corr >= 0.8:
        strength = '极强'
    elif abs_corr >= 0.6:
        strength = '强'
    elif abs_corr >= 0.4:
        strength = '中等'
    elif abs_corr >= 0.2:
        strength = '弱'
    else:
        strength = '极弱或无'
    
    direction = '正' if pearson_corr > 0 else '负'
    print(f'  - {direction}相关，{strength}相关')
    
    # Spearman秩相关系数
    spearman_corr, spearman_p = stats.spearmanr(x_data, y_data)
    print(f'**Spearman秩相关系数**: {spearman_corr:.4f}')
    print(f'  - p值: {spearman_p:.4e}')
    
    # 决定系数 R²
    slope, intercept, r_value, p_value, std_err = stats.linregress(x_data, y_data)
    r_squared = r_value ** 2
    print(f'**决定系数 R²**: {r_squared:.4f}')
    print(f'  - 线性回归解释的方差比例')
    
    # 回归分析
    print('')
    print('## 📊 回归分析')
    print(f'**线性回归方程**: Y = {slope:.4f} * X + {intercept:.4f}')
    print(f'  - 斜率: {slope:.4f} (每单位X变化引起的Y变化)')
    print(f'  - 截距: {intercept:.4f} (X=0时的Y值)')
    print(f'  - 标准误差: {std_err:.4f}')
    
    # 预测区间
    x_mean = x_data.mean()
    y_mean = y_data.mean()
    print(f'**中心趋势**:')
    print(f'  - X平均值: {x_mean:.4f}')
    print(f'  - Y平均值: {y_mean:.4f}')
    
    # 药物发现视角分析
    print('')
    print('## 💊 药物发现视角分析')
    print('')
    
    # 根据列名提供专业分析
    x_lower = '$X_COLUMN'.lower()
    y_lower = '$Y_COLUMN'.lower()
    
    # pIC50相关分析
    if 'pic50' in x_lower or 'pic50' in y_lower:
        print('**活性相关性分析**:')
        
        if 'pic50' in x_lower and 'qed' in y_lower:
            if pearson_corr > 0.3:
                print('  - ✅ 活性与药物相似性正相关，高活性分子往往成药性更好')
            elif pearson_corr < -0.3:
                print('  - ⚠️  活性与药物相似性负相关，可能需要平衡两者')
            else:
                print('  - 📊 活性与药物相似性无明显相关性')
        
        if 'pic50' in x_lower and 'herg' in y_lower:
            if pearson_corr > 0.3:
                print('  - ⚠️  活性与hERG风险正相关，高活性分子可能伴随高风险')
            elif pearson_corr < -0.3:
                print('  - ✅ 活性与hERG风险负相关，高活性分子风险较低')
            else:
                print('  - 📊 活性与hERG风险无明显相关性')
    
    # LogP相关分析
    if 'logp' in x_lower or 'logp' in y_lower:
        print('**脂溶性相关性分析**:')
        
        if 'logp' in x_lower and 'pic50' in y_lower:
            ideal_range = ((x_data >= 1.5) & (x_data <= 3.5)).mean()
            print(f'  - {ideal_range:.1%} 分子LogP在理想范围 (1.5-3.5)')
            
            if pearson_corr > 0.2:
                print('  - 📈 LogP与活性正相关，适当增加脂溶性可能提高活性')
            elif pearson_corr < -0.2:
                print('  - 📉 LogP与活性负相关，适当降低脂溶性可能提高活性')
    
    # 分子量相关分析
    if 'mw' in x_lower or 'mw' in y_lower:
        print('**分子量相关性分析**:')
        
        ideal_mw = ((x_data if 'mw' in x_lower else y_data) >= 200) & ((x_data if 'mw' in x_lower else y_data) <= 500)
        ideal_pct = ideal_mw.mean()
        print(f'  - {ideal_pct:.1%} 分子分子量在理想范围 (200-500)')
    
    print('')
    print('## 🎨 生成散点图...')
    
    # 创建图形
    plt.figure(figsize=(12, 8))
    
    # 设置样式
    grid_setting = '$GRID' == 'true'
    sns.set_style('whitegrid' if grid_setting else 'white')
    sns.set_palette('husl')
    
    # 创建散点图
    scatter_kwargs = {
        'data': df,
        'x': '$X_COLUMN',
        'y': '$Y_COLUMN',
        'alpha': 0.7,
        'edgecolor': 'w',
        'linewidth': 0.5
    }
    
    # 添加分组选项
    if '$HUE_COLUMN' and '$HUE_COLUMN' in df.columns:
        scatter_kwargs['hue'] = '$HUE_COLUMN'
        scatter_kwargs['palette'] = 'viridis'
    
    if '$SIZE_COLUMN' and '$SIZE_COLUMN' in df.columns:
        scatter_kwargs['size'] = '$SIZE_COLUMN'
    
    if '$STYLE_COLUMN' and '$STYLE_COLUMN' in df.columns:
        scatter_kwargs['style'] = '$STYLE_COLUMN'
    
    # 绘制散点图
    ax = sns.scatterplot(**scatter_kwargs)
    
    # 添加趋势线
    if '$TRENDLINE' == 'true' or '$REGRESSION' == 'true':
        sns.regplot(data=df, x='$X_COLUMN', y='$Y_COLUMN', 
                   scatter=False, color='red', line_kws={'linewidth': 2})
    
    # 设置坐标轴
    if '$LOGX' == 'true':
        ax.set_xscale('log')
    if '$LOGY' == 'true':
        ax.set_yscale('log')
    
    # 设置标题和标签
    if '$TITLE':
        plt.title('$TITLE', fontsize=16, pad=20)
    else:
        plt.title(f'$SOURCE_NAME: $X_COLUMN vs $Y_COLUMN', fontsize=16, pad=20)
    
    plt.xlabel('$X_COLUMN', fontsize=14)
    plt.ylabel('$Y_COLUMN', fontsize=14)
    
    # 添加相关性信息
    if '$CORRELATION' == 'true':
        info_text = f'Pearson r = {pearson_corr:.3f} (p = {pearson_p:.3e})\\n'
        info_text += f'R² = {r_squared:.3f}'
        
        plt.text(0.02, 0.98, info_text, transform=ax.transAxes,
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8),
                fontsize=10)
    
    # 添加理想范围标记（如果适用）
    if 'logp' in x_lower and '$LOGX' != 'true':
        # LogP理想范围
        plt.axvspan(1.5, 3.5, alpha=0.1, color='green', label='理想LogP范围')
    
    if 'mw' in x_lower and '$LOGX' != 'true':
        # 分子量理想范围
        plt.axvspan(200, 500, alpha=0.1, color='blue', label='理想分子量范围')
    
    # 调整图例
    if '$HUE_COLUMN' or '$SIZE_COLUMN' or '$STYLE_COLUMN':
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)
    
    # 调整布局
    plt.tight_layout()
    
    # 保存图形
    plt.savefig('$output_file', dpi=$DPI, bbox_inches='tight')
    plt.close()
    
    print(f'✅ 散点图已保存: $output_file')
    print(f'   文件大小: {os.path.getsize(\"$output_file\") / 1024:.1f} KB')
    print('')
    
    # 数据分区分析
    print('## 📊 数据分区分析')
    print('')
    
    # 四分位分析
    x_q1, x_median, x_q3 = np.percentile(x_data, [25, 50, 75])
    y_q1, y_median, y_q3 = np.percentile(y_data, [25, 50, 75])
    
    print(f'**$X_COLUMN 四分位**:')
    print(f'  - Q1 (25%): {x_q1:.3f}')
    print(f'  - 中位数: {x_median:.3f}')
    print(f'  - Q3 (75%): {x_q3:.3f}')
    print(f'  - IQR: {x_q3 - x_q1:.3f}')
    
    print(f'**$Y_COLUMN 四分位**:')
    print(f'  - Q1 (25%): {y_q1:.3f}')
    print(f'  - 中位数: {y_median:.3f}')
    print(f'  - Q3 (75%): {y_q3:.3f}')
    print(f'  - IQR: {y_q3 - y_q1:.3f}')
    
    # 象限分析
    print('')
    print('## 🎯 象限分析')
    print('')
    
    x_mean = x_data.mean()
    y_mean = y_data.mean()
    
    quadrants = {
        '右上': ((x_data > x_mean) & (y_data > y_mean)).mean(),
        '右下': ((x_data > x_mean) & (y_data <= y_mean)).mean(),
        '左上': ((x_data <= x_mean) & (y_data > y_mean)).mean(),
        '左下': ((x_data <= x_mean) & (y_data <= y_mean)).mean()
    }
    
    print('**相对于平均值的分布**:')
    for quadrant, proportion in quadrants.items():
        print(f'  - {quadrant}象限: {proportion:.1%}')
    
    # 识别最佳区域
    print('')
    print('## 🏆 最佳区域识别')
    print('')
    
    # 根据变量类型定义"最佳"
    best_criteria = []
    
    if 'pic50' in x_lower or 'pic50' in y_lower:
        best_criteria.append('高pIC50（高活性）')
    
    if 'qed' in x_lower or 'qed' in y_lower:
        best_criteria.append('高QED（良好药物相似性）')
    
    if 'herg' in x_lower or 'herg' in y_lower:
        best_criteria.append('低hERG_Prob（低心脏毒性风险）')
    
    if 'logp' in x_lower or 'logp' in y_lower:
        best_criteria.append('LogP在1.5-3.5（理想脂溶性）')
    
    if best_criteria:
        print('**理想分子应满足**:')
        for criterion in best_criteria:
            print(f'  - {criterion}')
    
    # 提供筛选建议
    print('')
    print('## 🔍 筛选建议')
    print('')
    
    if pearson_corr > 0.5:
        print(f'✅ $X_COLUMN 和 $Y_COLUMN 强正相关')
        print(f'   优化一个变量可能同时改善另一个变量')
    elif pearson_corr < -0.5:
        print(f'✅ $X_COLUMN 和 $Y_COLUMN 强负相关')
        print(f'   需要权衡两个变量的优化')
    elif abs(pearson_corr) < 0.2:
        print(f'📊 $X_COLUMN 和 $Y_COLUMN 相关性弱')
        print(f'   可以独立优化两个变量')
    else:
        print(f'📈 $X_COLUMN 和 $Y_COLUMN 中等相关')
        print(f'   考虑联合优化策略')
    
    # 异常值分析
    print('')
    print('## ⚠️  异常值分析')
    print('')
    
    # 使用IQR方法识别异常值
    x_iqr = x_q3 - x_q1
    y_iqr = y_q3 - y_q1
    
    x_lower_bound = x_q1 - 1.5 * x_iqr
    x_upper_bound = x_q3 + 1.5 * x_iqr
    y_lower_bound = y_q1 - 1.5 * y_iqr
    y_upper_bound = y_q3 + 1.5 * y_iqr
    
    outliers = ((x_data < x_lower_bound) | (x_data > x_upper_bound) | 
                (y_data < y_lower_bound) | (y_data > y_upper_bound))
    
    outlier_count = outliers.sum()
    if outlier_count > 0:
        print(f'检测到 {outlier_count} 个异常值 ({outlier_count/len(analysis_df)*100:.1f}%)')
        print('建议检查这些分子的数据质量或考虑特殊处理')
    else:
        print('未检测到异常值')
    
    print('')
    print('## 📋 分析总结')
    print('')
    
    summary_points = []
    
    if pearson_p < 0.05:
        summary_points.append(f'✅ $X_COLUMN 和 $Y_COLUMN 相关性统计显著')
    else:
        summary_points.append(f'⚠️  $X_COLUMN 和 $Y_COLUMN 相关性不显著')
    
    if r_squared > 0.5:
        summary_points.append(f'✅ 线性模型解释力强 (R²={r_squared:.3f})')
    elif r_squared > 0.3:
        summary_points.append(f'📈 线性模型有一定解释力 (R²={r_squared:.3f})')
    else:
        summary_points.append(f'📊 线性模型解释力有限 (R²={r_squared:.3f})')
    
    if outlier_count/len(analysis_df) > 0.05:
        summary_points.append(f'⚠️  异常值比例较高，可能影响分析结果')
    
    for point in summary_points:
        print(f'- {point}')
    
except Exception as e:
    print(f'❌ 散点图生成错误: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
"

echo ""
echo "## 🖼️  图像预览"
echo ""
echo "散点图已保存为: $output_file"
echo ""
echo "如果系统支持，可以使用以下命令查看:"
echo "\`\`\`bash"
if command -v eog &> /dev/null; then
    echo "eog $output_file &"
elif command -v xdg-open &> /dev/null; then
    echo "xdg-open $output_file &"
elif command -v open &> /dev/null; then
    echo "open $output_file"
else
    echo "# 请使用图像查看器打开: $output_file"
fi
echo "\`\`\`"
echo ""
echo "## 🚀 下一步操作"
echo ""
echo "\`\`\`bash"
echo "# 1. 分析其他变量对"
echo "bash scripts/demo_plot_scatter.sh $SOURCE_NAME LogP pIC50 --trendline --correlation"
echo "bash scripts/demo_plot_scatter.sh $SOURCE_NAME QED hERG_Prob --hue Active_Set"
echo ""
echo "# 2. 筛选特定区域的分子"
if [[ "$X_COLUMN" =~ [Pp][Ii][Cc]50 ]] && [[ "$Y_COLUMN" =~ [Qq][Ee][Dd] ]]; then
    echo "# 筛选高活性且高QED的分子"
    echo "bash scripts/demo_filter_multi.sh $SOURCE_NAME '{\"pIC50\": \">7.0\", \"QED\": \">0.6\"}'"
fi
echo ""
echo "# 3. 生成3D散点图（如果安装plotly）"
echo "# pip install plotly"
echo "# 然后使用自定义脚本生成3D图"
echo ""
echo "# 4. 时间序列分析（如果有时间数据）"
echo "# bash scripts/demo_plot_timeseries.sh $SOURCE_NAME"
echo "\`\`\`"
echo ""
echo "## 📊 论文图表建议"
echo ""
echo "**可用于论文的图表类型**:"
echo "1. **图1**: $X_COLUMN vs $Y_COLUMN 散点图（本图）"
echo "2. **图2**: 添加分组颜色的增强散点图"
echo "3. **图3**: 包含回归线和置信区间的统计图"
echo "4. **补充图**: 不同子集的对比散点图"
echo ""
echo "**图表说明应包含**:"
echo "- 样本量 (n=...)"
echo "- 相关系数和p值"
echo "- 回归方程"
echo "- 关键发现摘要"