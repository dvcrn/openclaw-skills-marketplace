#!/bin/bash
# 环境检查（不强制）
source "$(dirname "$0")/_simple_env.sh" 2>/dev/null || true
set -euo pipefail

# PRISM_GEN_DEMO - 分布图可视化
# 生成指定列的分布直方图

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
DATA_DIR="$PROJECT_DIR/data"
PLOT_DIR="$PROJECT_DIR/plots"
mkdir -p "$PLOT_DIR"

# 检查参数
if [ $# -lt 2 ]; then
    echo "用法: $0 <数据源名称> <列名> [选项]"
    echo ""
    echo "参数说明:"
    echo "  <数据源名称> : CSV文件名"
    echo "  <列名>       : 要绘制分布图的列名"
    echo ""
    echo "选项:"
    echo "  --bins <n>       : 直方图箱数 (默认: auto)"
    echo "  --title <title>  : 图表标题"
    echo "  --output <name>  : 输出文件名 (默认: 自动生成)"
    echo "  --format <fmt>   : 输出格式 png|pdf|svg (默认: png)"
    echo "  --dpi <dpi>      : 图像分辨率 (默认: 150)"
    echo "  --log            : 使用对数刻度"
    echo "  --kde            : 添加核密度估计"
    echo "  --stats          : 显示统计信息"
    echo ""
    echo "示例:"
    echo "  $0 step4a_admet_final.csv pIC50"
    echo "  $0 step4a_admet_final.csv LogP --bins 20 --title 'LogP分布'"
    echo "  $0 step4a_admet_final.csv QED --kde --stats"
    echo "  $0 step4a_admet_final.csv hERG_Prob --log"
    echo ""
    echo "使用 demo_list_sources.sh 查看所有可用数据源"
    exit 1
fi

SOURCE_NAME="$1"
COLUMN="$2"
shift 2

# 解析选项
BINS="auto"
TITLE=""
OUTPUT_NAME=""
FORMAT="png"
DPI=150
LOG_SCALE=false
SHOW_KDE=false
SHOW_STATS=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --bins)
            BINS="$2"
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
        --log)
            LOG_SCALE=true
            shift
            ;;
        --kde)
            SHOW_KDE=true
            shift
            ;;
        --stats)
            SHOW_STATS=true
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
safe_column=$(echo "$COLUMN" | tr -c '[:alnum:]' '_')

if [ -z "$OUTPUT_NAME" ]; then
    OUTPUT_NAME="${SOURCE_NAME%.csv}_${safe_column}_distribution_${timestamp}.$FORMAT"
else
    # 确保有正确的扩展名
    if [[ ! "$OUTPUT_NAME" =~ \.(png|pdf|svg)$ ]]; then
        OUTPUT_NAME="${OUTPUT_NAME}.$FORMAT"
    fi
fi

output_file="$PLOT_DIR/$OUTPUT_NAME"

echo "# PRISM_GEN_DEMO - 分布图可视化"
echo "## 列: $COLUMN"
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
echo "**分析列**: $COLUMN"
echo "**输出文件**: $output_file"
echo "**格式**: $FORMAT, DPI: $DPI"
echo "**选项**: bins=$BINS, log=$LOG_SCALE, kde=$SHOW_KDE, stats=$SHOW_STATS"
echo "**时间**: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 使用Python生成分布图
"$SCRIPT_DIR/_python_wrapper.sh" "
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import sys
import os
from scipy import stats

try:
    # 设置中文字体（如果需要）
    plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False
    
    # 读取数据
    df = pd.read_csv('$CSV_FILE')
    
    print('## 📊 数据概览')
    print(f'- 总分子数: {len(df)}')
    print(f'- 总列数: {len(df.columns)}')
    
    # 检查列是否存在
    if '$COLUMN' not in df.columns:
        print(f'❌ 列不存在: $COLUMN')
        print('')
        print('可用列:')
        for i, col in enumerate(df.columns, 1):
            print(f'  {i:2d}. {col}')
        sys.exit(1)
    
    # 检查是否为数值列
    if not pd.api.types.is_numeric_dtype(df['$COLUMN']):
        print(f'⚠️  警告: $COLUMN 不是数值列，将尝试转换为数值')
        try:
            df['$COLUMN'] = pd.to_numeric(df['$COLUMN'], errors='coerce')
        except:
            print(f'❌ 无法将 $COLUMN 转换为数值列')
            sys.exit(1)
    
    # 移除NaN值
    data = df['$COLUMN'].dropna()
    if len(data) == 0:
        print(f'❌ 列 $COLUMN 没有有效数据')
        sys.exit(1)
    
    print(f'- 有效数据点: {len(data)}')
    print(f'- 缺失值: {df['$COLUMN'].isna().sum()}')
    print('')
    
    # 计算统计信息
    stats_dict = {
        '平均值': data.mean(),
        '中位数': data.median(),
        '标准差': data.std(),
        '最小值': data.min(),
        '最大值': data.max(),
        '25%分位数': data.quantile(0.25),
        '75%分位数': data.quantile(0.75),
        '偏度': data.skew(),
        '峰度': data.kurtosis()
    }
    
    print('## 📈 统计信息')
    for key, value in stats_dict.items():
        if isinstance(value, float):
            print(f'- {key}: {value:.4f}')
        else:
            print(f'- {key}: {value}')
    
    # 检查数据分布
    print('')
    print('## 🔍 分布特征')
    
    # 正态性检验
    if len(data) >= 8:  # Shapiro-Wilk需要至少3个样本，但小样本效果不好
        try:
            shapiro_stat, shapiro_p = stats.shapiro(data)
            print(f'- Shapiro-Wilk正态性检验: p={shapiro_p:.4f}', end=' ')
            if shapiro_p > 0.05:
                print('(符合正态分布)')
            else:
                print('(不符合正态分布)')
        except:
            print('- 正态性检验: 样本量不足或数据范围太小')
    
    # 分布类型判断
    skewness = stats_dict['偏度']
    if abs(skewness) < 0.5:
        print(f'- 分布对称 (偏度={skewness:.2f})')
    elif skewness > 0:
        print(f'- 右偏分布 (偏度={skewness:.2f})')
    else:
        print(f'- 左偏分布 (偏度={skewness:.2f})')
    
    # 异常值检测
    Q1 = stats_dict['25%分位数']
    Q3 = stats_dict['75%分位数']
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    outliers = data[(data < lower_bound) | (data > upper_bound)]
    
    if len(outliers) > 0:
        print(f'- 检测到 {len(outliers)} 个异常值 ({len(outliers)/len(data)*100:.1f}%)')
    else:
        print('- 未检测到异常值')
    
    print('')
    print('## 🎨 生成分布图...')
    
    # 创建图形
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle(f'$COLUMN 分布分析 - {os.path.basename(\"$CSV_FILE\")}', fontsize=16, y=0.98)
    
    # 1. 直方图
    ax1 = axes[0, 0]
    if '$BINS' == 'auto':
        # 使用Freedman-Diaconis规则
        h = 2 * IQR / (len(data) ** (1/3))
        bins = int((data.max() - data.min()) / h) if h > 0 else 30
        bins = min(bins, 50)  # 限制最大箱数
    else:
        try:
            bins = int('$BINS')
        except:
            bins = 30
    
    ax1.hist(data, bins=bins, edgecolor='black', alpha=0.7, density=('$SHOW_KDE' == 'true'))
    ax1.set_xlabel('$COLUMN')
    ax1.set_ylabel('密度' if '$SHOW_KDE' == 'true' else '频数')
    ax1.set_title(f'直方图 (bins={bins})')
    ax1.grid(True, alpha=0.3)
    
    if '$LOG_SCALE' == 'true':
        ax1.set_yscale('log')
    
    if '$SHOW_KDE' == 'true':
        from scipy.stats import gaussian_kde
        kde = gaussian_kde(data)
        x_range = np.linspace(data.min(), data.max(), 1000)
        ax1.plot(x_range, kde(x_range), 'r-', linewidth=2, label='KDE')
        ax1.legend()
    
    # 添加统计信息
    if '$SHOW_STATS' == 'true':
        stats_text = f'平均值: {stats_dict[\"平均值\"]:.3f}\n中位数: {stats_dict[\"中位数\"]:.3f}\n标准差: {stats_dict[\"标准差\"]:.3f}'
        ax1.text(0.02, 0.98, stats_text, transform=ax1.transAxes, 
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    # 2. 箱线图
    ax2 = axes[0, 1]
    bp = ax2.boxplot(data, vert=True, patch_artist=True)
    bp['boxes'][0].set_facecolor('lightblue')
    bp['medians'][0].set_color('red')
    bp['fliers'][0].set_marker('o')
    bp['fliers'][0].set_markerfacecolor('red')
    bp['fliers'][0].set_markersize(5)
    
    ax2.set_ylabel('$COLUMN')
    ax2.set_title('箱线图')
    ax2.grid(True, alpha=0.3)
    
    # 标记异常值
    if len(outliers) > 0:
        ax2.text(1.1, outliers.mean(), f'{len(outliers)}个异常值', 
                verticalalignment='center')
    
    # 3. 概率图 (Q-Q图)
    ax3 = axes[1, 0]
    stats.probplot(data, dist='norm', plot=ax3)
    ax3.set_title('Q-Q图 (正态检验)')
    ax3.grid(True, alpha=0.3)
    
    # 4. 累积分布函数
    ax4 = axes[1, 1]
    sorted_data = np.sort(data)
    cdf = np.arange(1, len(sorted_data) + 1) / len(sorted_data)
    ax4.plot(sorted_data, cdf, 'b-', linewidth=2)
    ax4.set_xlabel('$COLUMN')
    ax4.set_ylabel('累积概率')
    ax4.set_title('累积分布函数 (CDF)')
    ax4.grid(True, alpha=0.3)
    
    # 标记关键分位数
    for q in [0.25, 0.5, 0.75]:
        value = np.percentile(data, q * 100)
        ax4.axvline(x=value, color='r', linestyle='--', alpha=0.5)
        ax4.text(value, 0.5, f'{q*100:.0f}%', rotation=90, verticalalignment='center')
    
    # 调整布局
    plt.tight_layout()
    
    # 保存图形
    plt.savefig('$output_file', dpi=$DPI, bbox_inches='tight')
    plt.close()
    
    print(f'✅ 分布图已保存: $output_file')
    print(f'   文件大小: {os.path.getsize(\"$output_file\") / 1024:.1f} KB')
    print('')
    
    # 药物发现相关分析
    print('## 💊 药物发现视角分析')
    print('')
    
    # 根据列名提供专业分析
    column_lower = '$COLUMN'.lower()
    
    if 'pic50' in column_lower:
        active = (data > 7.0).mean()
        moderate = ((data >= 6.0) & (data <= 7.0)).mean()
        weak = (data < 6.0).mean()
        
        print(f'**活性分布**:')
        print(f'- 高活性 (pIC50 > 7.0): {active:.1%}')
        print(f'- 中等活性 (6.0-7.0): {moderate:.1%}')
        print(f'- 弱活性 (< 6.0): {weak:.1%}')
        
        if active > 0.3:
            print('✅ 高活性分子比例较高，筛选效果良好')
        elif active > 0.1:
            print('⚠️  高活性分子比例中等，有优化空间')
        else:
            print('❌ 高活性分子比例较低，需要改进筛选策略')
    
    elif 'logp' in column_lower:
        ideal = ((data >= 1.5) & (data <= 3.5)).mean()
        too_lipophilic = (data > 3.5).mean()
        too_hydrophilic = (data < 1.5).mean()
        
        print(f'**LogP分布**:')
        print(f'- 理想范围 (1.5-3.5): {ideal:.1%}')
        print(f'- 脂溶性过高 (> 3.5): {too_lipophilic:.1%}')
        print(f'- 水溶性过高 (< 1.5): {too_hydrophilic:.1%}')
        
        if ideal > 0.6:
            print('✅ 大部分分子LogP在理想范围，成药性良好')
        else:
            print('⚠️  需要优化LogP分布，考虑结构修饰')
    
    elif 'qed' in column_lower:
        excellent = (data > 0.75).mean()
        good = ((data >= 0.5) & (data <= 0.75)).mean()
        poor = (data < 0.5).mean()
        
        print(f'**QED分布**:')
        print(f'- 优秀 (> 0.75): {excellent:.1%}')
        print(f'- 良好 (0.5-0.75): {good:.1%}')
        print(f'- 较差 (< 0.5): {poor:.1%}')
        
        if excellent > 0.3:
            print('✅ 药物相似性优秀分子比例高')
        elif good > 0.5:
            print('⚠️  药物相似性总体良好，有提升空间')
        else:
            print('❌ 药物相似性总体较差，需要优化')
    
    elif 'herg' in column_lower:
        low_risk = (data < 0.1).mean()
        medium_risk = ((data >= 0.1) & (data <= 0.3)).mean()
        high_risk = (data > 0.3).mean()
        
        print(f'**hERG风险分布**:')
        print(f'- 低风险 (< 0.1): {low_risk:.1%}')
        print(f'- 中风险 (0.1-0.3): {medium_risk:.1%}')
        print(f'- 高风险 (> 0.3): {high_risk:.1%}')
        
        if low_risk > 0.7:
            print('✅ hERG风险控制良好，安全性高')
        elif high_risk < 0.1:
            print('⚠️  高风险分子比例较低，但需关注中风险分子')
        else:
            print('❌ hERG风险较高，需要结构优化降低风险')
    
    elif 'mw' in column_lower:
        ideal = ((data >= 200) & (data <= 500)).mean()
        too_small = (data < 200).mean()
        too_large = (data > 500).mean()
        
        print(f'**分子量分布**:')
        print(f'- 理想范围 (200-500): {ideal:.1%}')
        print(f'- 过小 (< 200): {too_small:.1%}')
        print(f'- 过大 (> 500): {too_large:.1%}')
        
        if ideal > 0.7:
            print('✅ 分子量分布理想，符合类药性原则')
        else:
            print('⚠️  分子量分布需要优化')
    
    else:
        # 通用分析
        print(f'**数据质量评估**:')
        
        # 检查数据范围是否合理（使用已定义的data_range变量）
        if data_range < 0.1:
            print('- 数据范围很小，可能缺乏多样性')
        elif data_range > 100:
            print('- 数据范围很大，可能存在极端值')
        else:
            print('- 数据范围适中')
        
        # 检查数据集中程度
        cv = data.std() / data.mean() if data.mean() != 0 else 0
        if cv < 0.1:
            print('- 数据高度集中，变异系数小')
        elif cv > 1.0:
            print('- 数据分散，变异系数大')
        else:
            print('- 数据分布合理')
    
    print('')
    print('## 🎯 数据质量建议')
    print('')
    
    # 计算数据范围（在所有检查之前）
    data_range = data.max() - data.min()
    
    # 数据质量检查
    issues = []
    
    # 检查缺失值
    missing_pct = df['$COLUMN'].isna().mean()
    if missing_pct > 0.1:
        issues.append(f'- 缺失值较多 ({missing_pct:.1%})，考虑数据填充或删除')
    
    # 检查异常值
    if len(outliers) / len(data) > 0.05:
        issues.append(f'- 异常值比例较高 ({len(outliers)/len(data):.1%})，需要检查数据准确性')
    
    # 检查数据分布
    if abs(skewness) > 1:
        issues.append(f'- 数据偏斜严重 (偏度={skewness:.2f})，可能影响统计分析')
    
    if issues:
        print('⚠️  发现以下数据质量问题:')
        for issue in issues:
            print(issue)
    else:
        print('✅ 数据质量良好')
    
    # 可视化建议
    print('')
    print('## 🎨 可视化建议')
    print('')
    
    if skewness > 1:
        print('- 数据严重右偏，建议使用对数变换或Box-Cox变换')
    elif skewness < -1:
        print('- 数据严重左偏，建议检查数据收集过程')
    
    if len(data) > 1000:
        print('- 数据量较大，建议使用密度图代替直方图')
    
    if data_range > 100:
        print('- 数据范围大，建议使用分位数刻度或对数刻度')
    
    print('')
    print('## 📋 关键阈值参考')
    print('')
    
    # 提供关键阈值
    thresholds = {
        'pIC50': {'高活性': '>7.0', '中等活性': '6.0-7.0', '弱活性': '<6.0'},
        'LogP': {'理想': '1.5-3.5', '可接受': '0-5.0'},
        'QED': {'优秀': '>0.75', '良好': '0.5-0.75', '较差': '<0.5'},
        'hERG_Prob': {'低风险': '<0.1', '中风险': '0.1-0.3', '高风险': '>0.3'},
        'MW': {'理想': '200-500', '可接受': '150-600'},
        'TPSA': {'理想': '20-130', '可接受': '0-150'}
    }
    
    for key, values in thresholds.items():
        if key.lower() in column_lower:
            print(f'**{key} 参考阈值**:')
            for desc, range_str in values.items():
                print(f'  - {desc}: {range_str}')
            break
    
except Exception as e:
    print(f'❌ 分布图生成错误: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
"

echo ""
echo "## 🖼️  图像预览"
echo ""
echo "分布图已保存为: $output_file"
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
echo "# 1. 分析其他重要列"
if [[ ! "$COLUMN" =~ [Pp][Ii][Cc]50 ]]; then
    echo "bash scripts/demo_plot_distribution.sh $SOURCE_NAME pIC50"
fi
if [[ ! "$COLUMN" =~ [Qq][Ee][Dd] ]]; then
    echo "bash scripts/demo_plot_distribution.sh $SOURCE_NAME QED"
fi
if [[ ! "$COLUMN" =~ [Hh][Ee][Rr][Gg] ]]; then
    echo "bash scripts/demo_plot_distribution.sh $SOURCE_NAME hERG_Prob"
fi
echo ""
echo "# 2. 生成散点图分析相关性"
echo "bash scripts/demo_plot_scatter.sh $SOURCE_NAME pIC50 QED"
echo ""
echo "# 3. 筛选特定范围的分子"
quantile_value=$("$SCRIPT_DIR/_python_wrapper.sh" "import pandas as pd; df=pd.read_csv('$CSV_FILE'); print(df['$COLUMN'].quantile(0.75))" 2>/dev/null || echo "7.5")
echo "bash scripts/demo_filter.sh $SOURCE_NAME $COLUMN '>' $quantile_value"
echo ""
echo "# 4. 对比不同数据源"
echo "bash scripts/demo_plot_distribution.sh step3c_dft_refined.csv $COLUMN --title '阶段3c vs 阶段4a'"
echo "\`\`\`"
echo ""
echo "**提示**: 所有图表保存在 plots/ 目录，可用于论文或报告"