---
name: article-image
description: "文章配图推荐。根据文章主题、内容关键词，推荐合适的配图来源和搜索关键词，帮助用户找到符合文章意境的图片。当用户提到「配图」「找图」「文章图片」「封面图」「插图」时激活。"
---

# 文章配图推荐 Skill

## 功能概述
根据文章主题和内容，智能推荐配图方案，包括图片来源、搜索关键词、风格建议等。

## 使用方式

用户可以说：
- "帮我找几张配图"
- "这篇文章用什么图片好"
- "推荐一个封面图"
- "找一张 xxx 相关的图片"

## 配图来源

### 免费图库
| 网站 | 特点 |
|------|------|
| Unsplash | 高质量自然风景、生活 |
| Pexels | 丰富多样、商用免费 |
| Pixabay | 涵盖广、中文友好 |
| Unsplash | 人文、科技、商业 |
| Pexels | 视频也很棒 |
| pixiv | 日系插画 |
| Dribbble | 设计感强 |

### 中文图库
- 站酷 (ZCOOL)
- 花瓣网
- 阿里图标库

### 付费图库
- Shutterstock
- Getty Images
- 视觉中国

## 搜索技巧

### 按主题
| 文章主题 | 英文关键词 |
|----------|------------|
| 科技/互联网 | technology, coding, digital, AI, innovation |
| 商业/职场 | business, office, meeting, professional |
| 生活方式 | lifestyle, coffee, nature, travel |
| 教育/学习 | education, books, library, student |
| 金融/投资 | finance, chart, growth, investment |
| 健康/健身 | health, fitness, exercise, yoga |

### 按风格
- 扁平化 (flat, minimal)
- 渐变 (gradient, colorful)
- 插画 (illustration, vector)
- 照片 (photo, realistic)
- 抽象 (abstract, pattern)

### 组合搜索
```
"keyword1 + keyword2"
"keyword -unwanted"
"site:unsplash.com keyword"
```

## 配图原则

### 1. 相关性
- 图片与文章主题相关
- 突出文章核心观点

### 2. 视觉层次
- 封面图：大气、吸引眼球
- 文中图：补充说明、缓解阅读疲劳
- 题图：简洁、点题

### 3. 版权合规
- 确认授权范围
- 署名要求
- 商用限制

### 4. 尺寸适配
- 封面：1920x1080 或 1200x630
- 文中：800x450 或 16:9 比例
- 头像：圆形或正方形

## 工作流程

1. **分析文章**
   - 提取主题关键词
   - 确定文章风格（正式/轻松/技术）

2. **搜索图片**
   - 直接打开图库网站搜索
   - 不需要询问用户，直接执行

3. **下载保存**
   - 默认保存到：`C:\Users\lwp\images\`
   - 按规范命名：`主题-序号.jpg`
   - 无需询问，直接下载 3-5 张备选

4. **展示结果**
   - 告知用户保存位置
   - 列出图片主题

## 输出示例

文章主题："Python 异步编程教程"

推荐：
- **关键词**：Python, async, code, programming, developer
- **风格**：代码截图 + 流程图 + 技术插画
- **图库**：Unsplash, Pexels
- **搜索**："python programming" + "async code"

## 配套技能

- 可结合 md-beautify：插入图片到 Markdown
- 可结合 md2pdf：导出带图片的 PDF

## 注意事项

1. 尊重版权，注明来源
2. 图片质量优先于数量
3. 避免过度装饰
4. 移动端适配（考虑小屏幕显示）
