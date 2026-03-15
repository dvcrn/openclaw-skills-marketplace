---
name: data-chart-tool
description: "数据可视化工具，将 CSV/JSON 数据生成美观图表（柱状图、折线图、饼图等），配合 tushare-finance、财务分析、数据报告使用！"
---

# data-chart-tool - 数据可视化工具

数据可视化工具，将 CSV/JSON 数据生成美观图表，支持多种图表类型和输出格式！

## 功能特性

- ✅ **读取多种数据格式**：CSV、JSON、Excel
- ✅ **多种图表类型**：柱状图、折线图、饼图、散点图、面积图
- ✅ **自定义样式**：标题、标签、颜色、字体、图例
- ✅ **多种输出格式**：PNG、JPEG、PDF、SVG
- ✅ **预览模式**：显示图表而不保存文件
- ✅ **批量处理**：支持处理多个数据文件
- ✅ **配合 tushare-finance**：直接可视化股票数据

## 安装

```bash
# 安装依赖
pip install matplotlib pandas openpyxl
```

## 使用方法

### 基本用法

```bash
# 从 CSV 文件生成折线图
python source/data_visualizer.py --input data.csv --type line

# 从 JSON 文件生成柱状图
python source/data_visualizer.py --input data.json --type bar

# 生成饼图
python source/data_visualizer.py --input data.csv --type pie

# 预览模式（显示图表）
python source/data_visualizer.py --input data.csv --type line --preview

# 保存为 PDF
python source/data_visualizer.py --input data.csv --type line --output chart.pdf
```

### 详细参数

```
--input INPUT, -i INPUT     输入数据文件（CSV/JSON/Excel）
--type TYPE, -t TYPE        图表类型：bar（柱状图）、line（折线图）、pie（饼图）、scatter（散点图）、area（面积图）
--output OUTPUT, -o OUTPUT  输出文件路径（默认：chart.png）
--title TITLE                图表标题
--x-label X_LABEL            X 轴标签
--y-label Y_LABEL            Y 轴标签
--x-col X_COL                X 轴数据列名
--y-col Y_COL                Y 轴数据列名（逗号分隔多列）
--color COLOR                颜色（十六进制或颜色名）
--figsize FIGSIZE            图表大小，格式：宽,高（默认：10,6）
--dpi DPI                    输出 DPI（默认：100）
--grid, -g                   显示网格线
--legend, -l                 显示图例
--preview, -p                预览模式，显示图表不保存
--style STYLE                图表样式：default、seaborn、ggplot、fivethirtyeight
```

### 示例

```bash
# 股票数据可视化（配合 tushare-finance）
python source/data_visualizer.py -i stock_data.csv -t line --title "股票走势" --x-col "date" --y-col "close"

# 多列数据对比
python source/data_visualizer.py -i sales.csv -t bar --title "月度销售额" --x-col "month" --y-col "sales,profit" --legend

# 饼图展示占比
python source/data_visualizer.py -i category.csv -t pie --title "分类占比" --x-col "category" --y-col "value"

# 使用 seaborn 样式
python source/data_visualizer.py -i data.csv -t line --style seaborn --grid

# 保存为高分辨率 PDF
python source/data_visualizer.py -i data.csv -t bar --output report.pdf --dpi 300
```

## 支持的数据格式

- **CSV**：逗号分隔值文件
- **JSON**：JSON 格式数据（数组或对象）
- **Excel**：.xlsx 和 .xls 格式

## 图表样式

- `default`：默认样式
- `seaborn`：Seaborn 风格
- `ggplot`：ggplot 风格
- `fivethirtyeight`：FiveThirtyEight 风格

## 配合 tushare-finance 使用

```bash
# 1. 先用 tushare-finance 获取数据
tushare stock_daily --ts_code 000001.SZ --start_date 20240101 --end_date 20241231 -o stock_data.csv

# 2. 再用 data-visualizer 可视化
python source/data_visualizer.py -i stock_data.csv -t line --title "平安银行股价走势" --x-col "trade_date" --y-col "close" --grid
```
