# MD to Share

[中文](#中文) | [English](#english)

---

## 中文

将 Markdown 文件转换为原生长图的 skill，可使用 OpenClaw、Claude Code 等 AI Agent 直接调用。方便分享到微信、Discord 等平台。

### 安装

```bash
git clone https://github.com/DTacheng/md-to-share.git
cd md-to-share
npm install
```

### 使用方法

```bash
# 基本用法
node md2img.mjs <输入文件.md> <输出文件.png>

# 示例
node md2img.mjs "~/Downloads/文档.md" "~/Downloads/文档长图.png"
```

也可以添加全局命令：
```bash
npm link
md2img <输入文件.md> <输出文件.png>
```

### 特点

- **原生长图**：真正的文档流排版，不是 PPT 分页拼接
- **美观排版**：使用系统字体，支持表格、代码块、引用、列表等
- **微信友好**：宽度 800px，适合手机阅读
- **一步到位**：一条命令完成

### 样式说明

生成的长图样式：
- 标题：大字号���红色底部边框
- 二级标题：蓝色左侧边框
- 表格：斑马纹，悬停高亮
- 代码块：深色背景
- 行内代码：浅灰背景，红色文字
- 引用：蓝色边框 + 浅灰背景
- 分隔线：优雅分割

### 依赖

- Node.js 18+
- puppeteer-core
- marked
- Google Chrome（使用系统已安装的 Chrome）

---

## English

A skill that converts Markdown files to long images, directly callable by AI Agents like OpenClaw and Claude Code. Perfect for sharing on WeChat, Discord, and other platforms.

### Installation

```bash
git clone https://github.com/DTacheng/md-to-share.git
cd md-to-share
npm install
```

### Usage

```bash
# Basic usage
node md2img.mjs <input.md> <output.png>

# Example
node md2img.mjs "~/Downloads/document.md" "~/Downloads/document-image.png"
```

You can also add it as a global command:
```bash
npm link
md2img <input.md> <output.png>
```

### Features

- **Native Long Image**: True document flow layout, not PPT page stitching
- **Beautiful Typography**: System fonts with support for tables, code blocks, blockquotes, lists, etc.
- **Mobile Friendly**: 800px width, optimized for phone reading
- **One Command**: Get it done in a single step

### Styling

Generated image styles:
- H1: Large font with red bottom border
- H2: Blue left border accent
- Tables: Zebra stripes with hover highlight
- Code blocks: Dark background
- Inline code: Light gray background with red text
- Blockquotes: Blue border + light gray background
- Horizontal rules: Elegant dividers

### Dependencies

- Node.js 18+
- puppeteer-core
- marked
- Google Chrome (uses system-installed Chrome)

---

## License

MIT
