---
name: chart-generator
description: "Data visualization and chart generator with SVG file output. 数据可视化、数据图表、图表生成、柱状图、bar chart、折线图、line chart、饼图、pie chart、ASCII图表、数据报表、趋势图、sparkline、仪表盘、dashboard、HTML图表、SVG图表、SVG文件输出、数据分析图、统计图表、表格生成、格式化表格、数据展示、可视化报告、数据看板、进度条、热力图、趋势分析、变化率。Generate bar charts, line charts, pie charts, tables, sparklines, dashboards, progress bars, trend analysis, and heatmaps as ASCII or HTML. Also generates SVG chart files (bar/pie/line) that open directly in browsers. Use when: (1) creating data visualizations/charts, (2) generating bar/line/pie charts, (3) formatting data into tables, (4) building HTML chart reports, (5) showing data trends or distributions, (6) any chart, dashboard, or data visualization task, (7) progress tracking, (8) trend analysis with change rates, (9) heatmap visualization, (10) generating SVG chart files for sharing or embedding. 适用场景：生成图表、数据可视化、做报表、展示数据趋势、对比数据、ASCII图表终端展示、HTML图表报告输出、SVG图表文件生成、进度条、热力图、趋势分析。"
---

# Chart Generator

数据可视化图表生成器，通过 `scripts/chart.sh` 生成ASCII图表或HTML文件。

## 为什么用这个 Skill？ / Why This Skill?

- **即开即用**：一条命令直接出图，不需要安装matplotlib、echarts等复杂依赖
- **双输出**：终端ASCII图表（方便命令行查看）+ HTML文件（方便分享和嵌入）
- **迷你趋势图**：Unicode sparkline一行搞定趋势展示
- Compared to asking AI directly: produces actual runnable chart output (ASCII art + HTML files), not just code snippets you'd need to run yourself

## 使用方式

脚本路径：`scripts/chart.sh`（相对于本skill目录）

### 命令一览

```bash
# ASCII 柱状图
chart.sh bar "标签1:值1,标签2:值2,标签3:值3" [--title "标题"]

# ASCII 折线图
chart.sh line "1,5,3,8,2,7" [--title "趋势"]

# ASCII 饼图（百分比条形式）
chart.sh pie "A:30,B:50,C:20" [--title "分布"]

# 格式化表格
chart.sh table "H1,H2,H3|R1C1,R1C2,R1C3|R2C1,R2C2,R2C3"

# HTML 柱状图（内联SVG，无外部依赖）
chart.sh html-bar "A:30,B:50,C:20" --output chart.html

# 迷你趋势图（Unicode块字符）
chart.sh sparkline "1,5,3,8,2,7,4,9"

# 数据看板模板（多图表组合）
chart.sh dashboard "标题"

# 进度条可视化
chart.sh progress "已完成,总数" [--title "项目进度"]

# 趋势分析（折线+变化率+统计摘要）
chart.sh trend "10,15,12,20,18,25" [--title "月度增长"]

# ASCII热力图
chart.sh heatmap "1,2,3|4,5,6|7,8,9" [--title "活跃度"]

# SVG柱状图（生成.svg文件，可浏览器打开）
chart.sh svg-bar "销售报告" "Q1:120,Q2:180,Q3:95,Q4:210" [--color blue|green|red|rainbow]

# SVG饼图（扇形+图例+百分比标签）
chart.sh svg-pie "市场份额" "苹果:35,三星:25,华为:20"

# SVG折线图（坐标轴+数据点+面积填充）
chart.sh svg-line "月度趋势" "1月:100,2月:150,3月:120"

# 帮助
chart.sh help
```

See also: `tips.md` for data visualization best practices.

### 数据格式

- **键值对**: `"标签:数值,标签:数值"` — 用于 bar, pie, html-bar
- **纯数值**: `"1,5,3,8,2,7"` — 用于 line, sparkline
- **表格**: `"列头1,列头2|行1值1,行1值2|行2值1,行2值2"` — 管道符分隔行，逗号分隔列

### 选项

- `--title "标题"` — 图表标题（bar, line, pie）
- `--output file.html` — HTML输出文件路径（html-bar）

## 输出示例 / Example Output

### 柱状图 (bar)
```
$ chart.sh bar "销售:85,市场:62,研发:93,运维:41" --title "部门预算(万)"

  部门预算(万)
  销售  ████████████████████░  85
  市场  ███████████████░░░░░░  62
  研发  ██████████████████████ 93
  运维  ██████████░░░░░░░░░░░  41
```

### 迷你趋势图 (sparkline)
```
$ chart.sh sparkline "3,7,2,8,5,9,1,6"
▃▆▁█▄█▁▅
```
