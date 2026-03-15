---
name: snapdesign-rednote
description: "小红书风格卡片生成器 - 将长文本自动转换成精美的3:4卡片（900×1198px），咖色系设计，支持AI智能排版"
---

# SnapDesign RedNote 小红书卡片生成器

将长文本自动转换成小红书风格的精美卡片，支持 AI 智能排版。

## ✨ 功能特点

- 🎨 **小红书风格设计**: 咖色系字体 (#8B7355) + 纸质感背景
- 📐 **完美比例**: 3:4 (900×1198px) 高清分辨率
- 🤖 **AI 智能排版**: v2.0 使用 Claude 3.5 Sonnet 自动优化布局
- 🧩 **智能分块**: 自动将长文本分成多张卡片
- 🎭 **图形化表达**: 数字标签、图标、分隔线、渐变元素
- 📝 **优雅排版**: Tailwind CSS 专业排版，标题、正文、重点高亮
- 💧 **品牌水印**: 右下角咖色水印 www.snapdesign.app

## 🚀 使用方法

### Demo 模式（无需 API）

快速生成，无需配置 API 密钥：

```bash
node {baseDir}/scripts/generate-v2-demo.js "你的长文本内容" --title "标题"
```

### AI 模式（需要 OpenRouter API）

使用 Claude AI 进行智能内容提炼和排版：

```bash
export OPENROUTER_API_KEY="your-key"
node {baseDir}/scripts/generate-v2.js "你的长文本内容" --title "标题"
```

### 参数选项

```bash
--title "标题"       # 设置卡片主标题
--output ./dir      # 指定输出目录（默认: ./output-v2）
--cards 5           # 生成卡片数量（默认: 自动）
--with-images       # 强制生成配图（AI模式）
```

## 📊 示例

**输入:**
```bash
node scripts/generate-v2-demo.js "如何高效学习？第一步：明确目标。第二步：制定计划。第三步：持续行动。" --title "高效学习指南"
```

**输出:**
- 生成 3 张精美卡片（900×1198px）
- 每张卡片独立主题
- 统一咖色系设计
- 渐变装饰元素
- 右下角品牌水印

## 🎨 设计规范

- **主色**: `#664A42` / `#3E2723` (咖啡棕)
- **背景**: `#FFFCF8` (纸质米白)
- **强调色**: `#D4A574` / `#E8B4A0` / `#A8B5A0`
- **水印**: `#8B7355` (咖色，20px)
- **分辨率**: 900×1198px (3:4)

## 📁 输出结构

```
output-v2/
├── cards.html      # 完整 HTML（用于预览/调试）
├── card-1.png      # 第一张卡片
├── card-2.png      # 第二张卡片
└── card-3.png      # 第三张卡片
```

## 💡 使用建议

1. **文本长度**: 每个要点 50-150 字最佳
2. **分块方式**: 按主题自然分段，支持数字列表格式
3. **卡片数量**: 建议 3-9 张，太多会影响传播效果
4. **标题**: 简短有力，10 字以内
5. **Demo vs AI**: Demo 模式快速，AI 模式更智能

## 🔧 环境要求

- Node.js 14+
- Puppeteer（自动安装）
- OpenRouter API Key（仅 AI 模式需要）

---

**提示**: 生成的卡片可直接用于小红书、Instagram、微信朋友圈等社交平台！
