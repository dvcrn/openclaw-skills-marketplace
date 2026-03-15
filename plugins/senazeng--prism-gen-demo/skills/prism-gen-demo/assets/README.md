# Assets Directory

This directory contains visual assets for the PRISM-Gen Demo skill.

## Required Assets for ClawHub

### 1. Skill Icon
- **File**: `icon.png` or `icon.svg`
- **Size**: 512x512 pixels recommended
- **Format**: PNG or SVG
- **Content**: Representative icon for drug discovery/data analysis

### 2. Screenshots
- **File**: `screenshot1.png`, `screenshot2.png`, etc.
- **Size**: 1280x720 pixels or similar
- **Format**: PNG
- **Content**: 
  - Command line interface in action
  - Generated visualizations
  - Data analysis results

### 3. Banner Image (Optional)
- **File**: `banner.png`
- **Size**: 1200x300 pixels
- **Format**: PNG
- **Content**: Attractive banner for skill listing

## Current Assets

### Generated Screenshots
The following screenshots are automatically generated during testing:

1. **Distribution Plots**: `plots/step4a_admet_final_pIC50__distribution_*.png`
   - Shows pIC50 distribution analysis
   - Includes histogram, box plot, Q-Q plot, CDF

2. **Scatter Plots**: `plots/step4a_admet_final_scatter_pIC50__vs_QED__*.png`
   - Shows correlation between pIC50 and QED
   - Includes trend line and statistical analysis

### How to Create Screenshots

```bash
# Generate example screenshots
cd ~/.openclaw/workspace/skills/prism-gen-demo

# 1. Generate distribution plot
bash scripts/demo_plot_distribution.sh step4a_admet_final.csv pIC50

# 2. Generate scatter plot with trendline
bash scripts/demo_plot_scatter.sh step4a_admet_final.csv pIC50 QED --trendline --correlation

# 3. Copy to assets directory
cp plots/*.png assets/
```

## Design Guidelines

### Colors
- Primary: Blue (#4A90E2) - for data/science theme
- Secondary: Green (#50C878) - for success/positive results
- Accent: Orange (#FF6B35) - for warnings/attention
- Background: White or light gray

### Typography
- Headers: Bold, clear
- Code: Monospace font
- Body: Readable sans-serif

### Icons
- Use the 🧪 (test tube) emoji as base
- Consider molecular structures or data charts
- Keep it simple and recognizable

## Creating Custom Assets

### Using Python (Matplotlib)
```python
import matplotlib.pyplot as plt
import numpy as np

# Create simple icon
fig, ax = plt.subplots(figsize=(5, 5))
# Add your design here
plt.savefig('assets/icon.png', dpi=300, transparent=True)
```

### Using External Tools
- **Inkscape**: For vector graphics (SVG)
- **GIMP**: For raster graphics (PNG)
- **Canva**: For banners and promotional graphics

## Asset Checklist for Release

- [ ] Skill icon (512x512 PNG)
- [ ] At least 2 screenshots (1280x720 PNG)
- [ ] Optional banner (1200x300 PNG)
- [ ] All assets in correct format
- [ ] Assets reflect actual skill functionality
- [ ] No copyrighted material used

## Notes
- Keep file sizes reasonable (< 1MB per image)
- Use compression for PNG files
- Ensure good contrast for readability
- Test assets on different screen sizes

---

# 资源目录

此目录包含PRISM-Gen Demo技能的可视化资源。

## ClawHub所需资源

### 1. 技能图标
- **文件**: `icon.png` 或 `icon.svg`
- **尺寸**: 推荐512x512像素
- **格式**: PNG或SVG
- **内容**: 代表药物发现/数据分析的图标

### 2. 截图
- **文件**: `screenshot1.png`, `screenshot2.png` 等
- **尺寸**: 1280x720像素或类似
- **格式**: PNG
- **内容**: 
  - 命令行界面运行情况
  - 生成的可视化图表
  - 数据分析结果

### 3. 横幅图片（可选）
- **文件**: `banner.png`
- **尺寸**: 1200x300像素
- **格式**: PNG
- **内容**: 技能列表的吸引人横幅

## 当前资源

### 生成的截图
以下截图在测试期间自动生成：

1. **分布图**: `plots/step4a_admet_final_pIC50__distribution_*.png`
   - 显示pIC50分布分析
   - 包括直方图、箱线图、Q-Q图、CDF

2. **散点图**: `plots/step4a_admet_final_scatter_pIC50__vs_QED__*.png`
   - 显示pIC50和QED之间的相关性
   - 包括趋势线和统计分析

### 如何创建截图

```bash
# 生成示例截图
cd ~/.openclaw/workspace/skills/prism-gen-demo

# 1. 生成分布图
bash scripts/demo_plot_distribution.sh step4a_admet_final.csv pIC50

# 2. 生成带趋势线的散点图
bash scripts/demo_plot_scatter.sh step4a_admet_final.csv pIC50 QED --trendline --correlation

# 3. 复制到资源目录
cp plots/*.png assets/
```

## 设计指南

### 颜色
- 主色: 蓝色 (#4A90E2) - 用于数据/科学主题
- 辅色: 绿色 (#50C878) - 用于成功/积极结果
- 强调色: 橙色 (#FF6B35) - 用于警告/注意
- 背景: 白色或浅灰色

### 排版
- 标题: 粗体，清晰
- 代码: 等宽字体
- 正文: 可读的无衬线字体

### 图标
- 使用🧪（试管）表情符号作为基础
- 考虑分子结构或数据图表
- 保持简单和可识别

## 创建自定义资源

### 使用Python (Matplotlib)
```python
import matplotlib.pyplot as plt
import numpy as np

# 创建简单图标
fig, ax = plt.subplots(figsize=(5, 5))
# 在此添加您的设计
plt.savefig('assets/icon.png', dpi=300, transparent=True)
```

### 使用外部工具
- **Inkscape**: 用于矢量图形 (SVG)
- **GIMP**: 用于位图图形 (PNG)
- **Canva**: 用于横幅和宣传图形

## 发布资源清单

- [ ] 技能图标 (512x512 PNG)
- [ ] 至少2张截图 (1280x720 PNG)
- [ ] 可选横幅 (1200x300 PNG)
- [ ] 所有资源格式正确
- [ ] 资源反映实际技能功能
- [ ] 未使用受版权保护的材料

## 注意事项
- 保持文件大小合理（每张图片<1MB）
- 对PNG文件使用压缩
- 确保良好的对比度以便阅读
- 在不同屏幕尺寸上测试资源