# PRISM-Gen Demo Tutorial

## 📚 Table of Contents
1. [Quick Start](#quick-start)
2. [Data Preparation](#data-preparation)
3. [Basic Queries](#basic-queries)
4. [Advanced Analysis](#advanced-analysis)
5. [Visualization](#visualization)
6. [Paper Chart Generation](#paper-chart-generation)
7. [Batch Processing](#batch-processing)
8. [Troubleshooting](#troubleshooting)

---

## 1. Quick Start

### 1.1 Installation
```bash
# Clone or download the project
git clone <repository-url>
cd prism-gen-demo

# Run installation script
bash setup.sh
```

### 1.2 Basic Testing
```bash
# Test environment
python3 -c "import pandas; print('Pandas version:', pandas.__version__)"

# Test scripts
bash scripts/test_visualization.sh
```

### 1.3 Adding Data
```bash
# Create data directory (if it doesn't exist)
mkdir -p data

# Copy PRISM result CSV files
cp /path/to/your/prism/results/*.csv data/
```

---

## 2. Data Preparation

### 2.1 Supported CSV Format
PRISM-GEN_DEMO supports standard PRISM output CSV format, key columns include:

| Column Name | Description | Type | Importance |
|-------------|-------------|------|------------|
| `smiles` | Molecular SMILES representation | String | Required |
| `pIC50` | Activity prediction value | Numeric | Important |
| `QED` | Drug-likeness | Numeric | Important |
| `LogP` | Lipophilicity | Numeric | Important |
| `MW` | Molecular weight | Numeric | Important |
| `hERG_Prob` | hERG inhibition risk | Numeric | Important |
| `SA` | Synthetic accessibility | Numeric | Optional |
| `TPSA` | Topological polar surface area | Numeric | Optional |

### 2.2 Data Quality Check
```bash
# View data source information
bash scripts/demo_source_info.sh step4a_admet_final.csv

# Check data quality
bash scripts/test_full_functionality.sh
```

### 2.3 Data Preprocessing Recommendations
1. **Unify column names**: Ensure consistent column names across all CSV files
2. **Handle missing values**: Scripts handle automatically, but preprocessing recommended
3. **Format validation**: Ensure numeric columns are of correct type

---

## 3. Basic Queries

### 3.1 View Data Sources
```bash
# List all available data sources
bash scripts/demo_list_sources.sh

# View detailed information of a single data source
bash scripts/demo_source_info.sh step4a_admet_final.csv
```

### 3.2 Data Preview
```bash
# Preview first 10 rows of data
bash scripts/demo_preview.sh step4a_admet_final.csv 10

# Simplified preview (no pandas dependency)
bash scripts/demo_simple_preview.sh step4a_admet_final.csv 5
```

### 3.3 Conditional Filtering
```bash
# Filter molecules with pIC50 > 7.0
bash scripts/demo_filter.sh step4a_admet_final.csv pIC50 '>' 7.0

# Filter with multiple conditions (AND logic)
bash scripts/demo_filter.sh step4a_admet_final.csv pIC50 '>' 7.0 QED '>' 0.5

# Filter with range conditions
bash scripts/demo_filter.sh step4a_admet_final.csv LogP '>=' 1.0 LogP '<=' 5.0
```

### 3.4 Top N Selection
```bash
# Get top 10 molecules by pIC50
bash scripts/demo_top.sh step4a_admet_final.csv pIC50 10

# Get bottom 5 molecules by hERG_Prob (least toxic)
bash scripts/demo_top.sh step4a_admet_final.csv hERG_Prob 5 --ascending
```

---

## 4. Advanced Analysis

### 4.1 Statistical Analysis
```bash
# Generate statistical summary
bash scripts/demo_source_info.sh step4a_admet_final.csv --stats

# Calculate correlation matrix
bash scripts/demo_plot_scatter.sh step4a_admet_final.csv pIC50 QED --correlation-only
```

### 4.2 Distribution Analysis
```bash
# Generate distribution plot for pIC50
bash scripts/demo_plot_distribution.sh step4a_admet_final.csv pIC50

# Generate distribution with custom parameters
bash scripts/demo_plot_distribution.sh step4a_admet_final.csv pIC50 \
  --bins 20 --title "Activity Distribution" --output "activity_dist.png"
```

### 4.3 Correlation Analysis
```bash
# Generate scatter plot with trend line
bash scripts/demo_plot_scatter.sh step4a_admet_final.csv pIC50 QED --trendline

# Generate scatter plot with correlation statistics
bash scripts/demo_plot_scatter.sh step4a_admet_final.csv pIC50 QED \
  --trendline --correlation --output "correlation_plot.png"
```

---

## 5. Visualization

### 5.1 Basic Charts
```bash
# Generate histogram
bash scripts/demo_plot_distribution.sh step4a_admet_final.csv pIC50

# Generate scatter plot
bash scripts/demo_plot_scatter.sh step4a_admet_final.csv pIC50 QED
```

### 5.2 Customized Charts
```bash
# Customize chart appearance
bash scripts/demo_plot_distribution.sh step4a_admet_final.csv pIC50 \
  --title "Activity Distribution Analysis" \
  --xlabel "pIC50" \
  --ylabel "Frequency" \
  --color "steelblue" \
  --output "custom_histogram.png"

# Multiple customization options
bash scripts/demo_plot_scatter.sh step4a_admet_final.csv pIC50 QED \
  --title "Activity vs Drug-likeness" \
  --xlabel "pIC50 (Activity)" \
  --ylabel "QED (Drug-likeness)" \
  --trendline \
  --correlation \
  --grid \
  --output "scatter_with_stats.png"
```

### 5.3 Export Options
```bash
# Export to different formats
bash scripts/demo_plot_distribution.sh step4a_admet_final.csv pIC50 --output "plot.png"
bash scripts/demo_plot_distribution.sh step4a_admet_final.csv pIC50 --output "plot.pdf"
bash scripts/demo_plot_distribution.sh step4a_admet_final.csv pIC50 --output "plot.svg"

# High-resolution export for publications
bash scripts/demo_plot_distribution.sh step4a_admet_final.csv pIC50 \
  --output "publication_quality.png" --dpi 300 --figsize "8,6"
```

---

## 6. Paper Chart Generation

### 6.1 Publication-Quality Settings
```bash
# Generate publication-ready figure
bash scripts/demo_plot_distribution.sh step4a_admet_final.csv pIC50 \
  --title "Distribution of Predicted Activity" \
  --output "figure_1.png" \
  --dpi 300 \
  --figsize "10,8" \
  --fontsize 14 \
  --style "seaborn-whitegrid"

# Generate correlation plot for paper
bash scripts/demo_plot_scatter.sh step4a_admet_final.csv pIC50 QED \
  --title "Correlation between Activity and Drug-likeness" \
  --output "figure_2.png" \
  --dpi 300 \
  --trendline \
  --correlation \
  --annotate-stats
```

### 6.2 Multi-Panel Figures
```bash
# Create subplot grid (example concept)
# Note: This requires custom script development
bash scripts/create_multi_panel.sh \
  --data step4a_admet_final.csv \
  --plots "distribution:pIC50,scatter:pIC50:QED,distribution:QED" \
  --output "multi_panel_figure.png"
```

---

## 7. Batch Processing

### 7.1 Process Multiple Files
```bash
# Process all CSV files in data directory
for file in data/*.csv; do
  echo "Processing $file..."
  bash scripts/demo_source_info.sh "$file"
done

# Batch filter with same condition
for file in data/*.csv; do
  bash scripts/demo_filter.sh "$file" pIC50 '>' 7.0
done
```

### 7.2 Automated Workflows
```bash
# Example workflow script
#!/bin/bash
# workflow.sh - Automated analysis workflow

echo "Step 1: List all data sources"
bash scripts/demo_list_sources.sh

echo "Step 2: Filter high-activity molecules"
bash scripts/demo_filter.sh step4a_admet_final.csv pIC50 '>' 7.0

echo "Step 3: Get top candidates"
bash scripts/demo_top.sh filtered_results.csv pIC50 20

echo "Step 4: Generate visualizations"
bash scripts/demo_plot_distribution.sh filtered_results.csv pIC50
bash scripts/demo_plot_scatter.sh filtered_results.csv pIC50 QED --trendline

echo "Workflow completed!"
```

---

## 8. Troubleshooting

### 8.1 Common Issues

#### Issue: Python dependencies not found
**Solution:**
```bash
# Install required packages
pip install pandas numpy matplotlib seaborn

# Or use the setup script
bash setup.sh
```

#### Issue: Script permission denied
**Solution:**
```bash
# Make scripts executable
chmod +x scripts/*.sh
```

#### Issue: CSV file not found
**Solution:**
```bash
# Check file exists
ls -la data/

# Use correct file path
bash scripts/demo_list_sources.sh
```

#### Issue: Memory error with large files
**Solution:**
```bash
# Use simplified preview for large files
bash scripts/demo_simple_preview.sh large_file.csv 5

# Filter before analysis
bash scripts/demo_filter.sh large_file.csv pIC50 '>' 6.0 | head -1000 > filtered.csv
```

### 8.2 Debug Mode
```bash
# Run scripts with debug output
bash scripts/demo_filter.sh step4a_admet_final.csv pIC50 '>' 7.0 --debug

# Test individual components
bash scripts/test_basic.sh
bash scripts/test_visualization.sh
bash scripts/test_full_functionality.sh
```

### 8.3 Performance Tips
1. **Use simple preview for large files**: `demo_simple_preview.sh` doesn't load entire file
2. **Filter first**: Apply filters before visualization to reduce data size
3. **Use head/tail**: Limit output with `head -n 100` for testing
4. **Cache results**: Save filtered results and reuse them

### 8.4 Getting Help
```bash
# View script help
bash scripts/demo_filter.sh --help

# List all available scripts
bash scripts/list_scripts_info.sh

# Check environment
bash scripts/_check_env_bash.sh
```

---

# PRISM-Gen Demo 使用教程

## 📚 目录
1. [快速开始](#快速开始-1)
2. [数据准备](#数据准备-1)
3. [基础查询](#基础查询-1)
4. [高级分析](#高级分析-1)
5. [可视化](#可视化-1)
6. [论文图表生成](#论文图表生成-1)
7. [批量处理](#批量处理-1)
8. [故障排除](#故障排除-1)

---

## 1. 快速开始

### 1.1 安装
```bash
# 克隆或下载项目
git clone <repository-url>
cd prism-gen-demo

# 运行安装脚本
bash setup.sh
```

### 1.2 基本测试
```bash
# 测试环境
python3 -c "import pandas; print('Pandas版本:', pandas.__version__)"

# 测试脚本
bash scripts/test_visualization.sh
```

### 1.3 添加数据
```bash
# 创建数据目录（如果不存在）
mkdir -p data

# 复制PRISM结果CSV文件
cp /path/to/your/prism/results/*.csv data/
```

---

## 2. 数据准备

### 2.1 支持的CSV格式
PRISM_GEN_DEMO支持标准的PRISM输出CSV格式，关键列包括：

| 列名 | 描述 | 类型 | 重要性 |
|------|------|------|--------|
| `smiles` | 分子SMILES表示 | 字符串 | 必需 |
| `pIC50` | 活性预测值 | 数值 | 重要 |
| `QED` | 药物相似性 | 数值 | 重要 |
| `LogP` | 脂水分配系数 | 数值 | 重要 |
| `MW` | 分子量 | 数值 | 重要 |
| `hERG_Prob` | hERG抑制风险 | 数值 | 重要 |
| `SA` | 合成可及性 | 数值 | 可选 |
| `TPSA` | 拓扑极性表面积 | 数值 | 可选 |

### 2.2 数据质量检查
```bash
# 查看数据源信息
bash scripts/demo_source_info.sh step4a_admet_final.csv

# 检查数据质量
bash scripts/test_full_functionality.sh
```

### 2.3 数据预处理建议
1. **统一列名**: 确保所有CSV文件的列名一致
2. **处理缺失值**: 脚本会自动处理，但建议预处理
3. **格式验证**: 确保数值列为正确类型

---

## 3. 基础查询

### 3.1 查看数据源
```bash
# 列出所有可用数据源
bash scripts/demo_list_sources.sh

# 查看单个数据源详细信息
bash scripts/demo_source_info.sh step4a_admet_final.csv
```

### 3.2 数据预览
```bash
# 预览前10行数据
bash scripts/demo_preview.sh step4a_admet_final.csv 10

# 简化版预览（不依赖pandas）
bash scripts/demo_simple_preview.sh step4a_admet_final.csv 5
```

### 3.3 条件过滤
```bash
# 筛选pIC50 > 7.0的分子
bash scripts/demo_filter.sh step4a_admet_final.csv pIC50 '>' 7.0

# 多条件筛选（AND逻辑）
bash scripts/demo_filter.sh step4a_admet_final.csv pIC50 '>' 7.0 QED '>' 0.5

# 范围条件筛选
bash scripts/demo_filter.sh step4a_admet_final.csv LogP '>=' 1.0 LogP '<=' 5.0
```

### 3.4 Top N选择
```bash
# 按pIC50获取前10个分子
bash scripts/demo_top.sh step4a_admet_final.csv pIC50 10

# 按hERG_Prob获取后5个分子（毒性最低）
bash scripts/demo_top.sh step4a_admet_final.csv hERG_Prob 5 --ascending
```

---

## 4. 高级分析

### 4.1 统计分析
```bash
# 生成统计摘要
bash scripts/demo_source_info.sh step4a_admet_final.csv --stats

# 计算相关性矩阵
bash scripts/demo_plot_scatter.sh step4a_admet_final.csv pIC50 QED --correlation-only
```

### 4.2 分布分析
```bash
# 生成pIC50分布图
bash scripts/demo_plot_distribution.sh step4a_admet_final.csv pIC50

# 使用自定义参数生成分布图
bash scripts/demo_plot_distribution.sh step4a_admet_final.csv pIC50 \
  --bins 20 --title "活性分布" --output "activity_dist.png"
```

### 4.3 相关性分析
```bash
# 生成带趋势线的散点图
bash scripts/demo_plot_scatter.sh step4a_admet_final.csv pIC50 QED --trendline

# 生成带相关性统计的散点图
bash scripts/demo_plot_scatter.sh step4a_admet_final.csv pIC50 QED \
  --trendline --correlation --output "correlation_plot.png"
```

---

## 5. 可视化

### 5.1 基础图表
```bash
# 生成直方图
bash scripts/demo_plot_distribution.sh step4a_admet_final.csv pIC50

# 生成散点图
bash scripts/demo_plot_scatter.sh step4a_admet_final.csv pIC50 QED
```

### 5.2 自定义图表
```bash
# 自定义图表外观
bash scripts/demo_plot_distribution.sh step4a_admet_final.csv pIC50 \
  --title "活性分布分析" \
  --xlabel "pIC50" \
  --ylabel "频率" \
  --color "steelblue" \
  --output "custom_histogram.png"

# 多个自定义选项
bash scripts/demo_plot_scatter.sh step4a_admet_final.csv pIC50 QED \
  --title "活性 vs 药物相似性" \
  --xlabel "pIC50 (活性)" \
  --ylabel "QED (药物相似性)" \
  --trendline \
  --correlation \
  --grid \
  --output "scatter_with_stats.png"
```

### 5.3 导出选项
```bash
# 导出到不同格式
bash scripts/demo_plot_distribution.sh step4a_admet_final.csv pIC50 --output "plot.png"
bash scripts/demo_plot_distribution.sh step4a_admet_final.csv pIC50 --output "plot.pdf"
bash scripts/demo_plot_distribution.sh step4a_admet_final.csv pIC50 --output "plot.svg"

# 高分辨率导出用于发表
bash scripts/demo