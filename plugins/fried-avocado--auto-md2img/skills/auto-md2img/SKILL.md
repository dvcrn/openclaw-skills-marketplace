---
name: auto-md2img
description: "Automatically converts markdown content into images for sending. When it's necessary to return markdown content to the user, md2img is automatically invoked to generate images instead of sending plain text markdown, thus avoiding layout clutter. Trigger scenario: All reply scenarios that require outputting markdown-formatted content."
---

# 🥑 Auto MD2IMG Skill

Automatically convert Markdown content into images for sending, enhancing the reading experience.

---

## ✨ Functional Features

- 🖼️ Automatically convert Markdown to high-definition images
- 📄 Support intelligent pagination, with a maximum of 500 lines per page
- 🧱 Cut by content blocks, without cutting off titles, code blocks, tables, etc
- 🔢 Automatically add page number annotations
- 🀄 Perfect support for Chinese fonts
- 😊 Supports colored Emoji
- 🎨 GitHub style rendering
- ⚡ Backend browser management, with improved performance for repeated conversions
- 🧹 Automatic cache cleanup to protect privacy

---

## 📖 Usage

When you need to reply to a user with content in Markdown format:

### Basic usage

1. Save the Markdown content to a temporary file (or directly pass in a string)
2. Call `scripts/md_to_png.js` to generate images
3. Use the `<qqimg>` tag to send images to users
4. If it's through the QQ channel, simply embed the image path using the `<qqimg>` tag
5. If generating images fails, revert to sending plain text Markdown

### Script invocation

```bash
# Basic Usage
node scripts/md_to_png.js input.md

# Specify output directory
node scripts/md_to_png.js input.md ./output

# Customize the number of lines per page
node scripts/md_to_png.js input.md ./output 300
```

### Parameter Description

| Parameter | Type | Required | Default | Description |
|------|------|------|--------|------|
| `inputFile` | string | ✅ | - | Path of the input Markdown file |
| `outputDir` | string | ❌ | current directory | directory for outputting images |
| `maxLinesPerPage` | number | ❌ | 500 | Maximum lines per page |

---

## 🔧 Configuration Instructions

### Font Configuration
- Default fonts: Wenquanyi Micro Black, Wenquanyi Regular Black, Noto CJK SC, Noto Color Emoji
- Support system font fallback

### Output configuration
- Output resolution: 2x (HD)
- Maximum width: 900px
- Automatically adapts to content height
- Output in PNG format

### Pagination Configuration
- Default maximum rows per page: 500
- Intelligent cutting based on content blocks
- Do not cut off headings, code blocks, citations, tables, or lists

---

## 📂 Script Path

`scripts/md_to_png.js` - The main tool for converting Markdown to images

`scripts/md_to_png.js` function:
- Read Markdown file
- Intelligent content block segmentation
- HTML rendering
- Puppeteer screenshot
- Cache cleanup

---

## 🎯 Usage Example

### Example 1: Simple Conversion

```javascript
import { exec } from 'child_process';
import path from 'path';

const markdownContent = `# Hello World\n\nThis is a test content. `;

// Save to temporary file
const tempFile = path.join('/tmp', 'temp.md');
fs.writeFileSync(tempFile, markdownContent);

// Call the conversion script
exec(`node scripts/md_to_png.js ${tempFile}`, (error, stdout, stderr) => {
  if (error) {
    console.error('Conversion failed:', error);
    return;
  }
  console.log('Conversion successful:', stdout);
});
```

### Example 2: Usage in QQ

```javascript
// When Markdown content needs to be replied to
async function replyWithMarkdown(content, outputDir) {
  try {
    // Call md2img for conversion
    const baseName = `reply_${Date.now()}`;
    const files = await convertMarkdown(content, outputDir, baseName);

    // Send an image using the <qqimg> tag
    for (const file of files) {
      await sendMessage(`<qqimg>${file.path}</qqimg>`);
    }
  } catch (error) {
    // Fall back to plain text in case of failure
    await sendMessage(content);
  }
}
```

---

## 🔒 Security Features

- ✅ Path traversal protection (output directory whitelist)
- ✅ File name cleanup (illegal character replacement)
- ✅ Content size limit (max 10MB)
- ✅ Line number range verification (10-10000)
- ✅ Configurable cache cleanup strategy

---

## 📊 Performance Metrics

| Metric | Value |
|------|-----|
| Browser first launch | ~260ms |
| Small document conversion (200 words) | ~2.3s |
| Medium document conversion (2KB) | ~2.6s |
| Large document conversion (5KB) | ~3.6s |
| Repeated conversion performance improvement | 4.5% (single instance) / 50-70% (batch) |

---

## 🎨 Rendering Effect

Supported Markdown elements:
- ✅ Headings (H1-H6)
- ✅ Text styles (bold, italic, strikethrough, inline code)
- ✅ Code block (syntax highlighting)
- ✅ List (ordered, unordered)
- ✅ Table
- ✅ Citation block
- ✅ Link
- ✅ Image
- ✅ Emoji

---

## 🛠️ Technology Stack

- Node.js >= 14
- Puppeteer (headless browser)
- marked (Markdown parsing)
- GitHub-style CSS

---

## 📝 Trigger Scenario

All reply scenarios that require outputting content in Markdown format:
- Share code snippets
- Technical document response
- Display of table data
- Organize into a list
- Long text typesetting

---

## ⚠️ Precautions

1. The first conversion requires starting the browser, which may take a while
2. It is recommended to enable the `skipCacheClear` configuration when performing batch conversions
3. Large documents may be split into multiple pages
4. Image files will occupy disk space, so be sure to clean them up

---

## 中文说明 (Chinese Instructions)

### 使用方法
当你需要回复用户 Markdown 格式内容时：
1. 先将 Markdown 内容保存到临时文件（或直接传入字符串）
2. 调用 `scripts/md_to_png.js` 生成图片
3. 使用 `<qqimg>` 标签将图片发送给用户
4. 如果是 QQ 渠道，直接用 `<qqimg>` 标签嵌入图片路径
5. 如果生成图片失败，再回退到发送纯文本 Markdown

### 脚本路径
`scripts/md_to_png.js` - Markdown 转图片工具

### 配置说明
- 默认字体：文泉驿微米黑、文泉驿正黑、Noto CJK SC、Noto Color Emoji
- 输出分辨率：2x，图片更清晰
- 最大宽度：900px
- 自动适应内容高度
- 默认每页最大行数：500行

---

**Auto MD2IMG Skill - Make Markdown Replies More Beautiful!**! ** 🎉