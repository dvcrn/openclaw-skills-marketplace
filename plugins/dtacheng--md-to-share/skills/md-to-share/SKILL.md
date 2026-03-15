---
name: md-to-share
description: "将 Markdown 文件转换为原生长图的 skill，可被 OpenClaw、Claude Code 等 AI Agent 直接调用。A skill that converts Markdown to long images, callable by AI Agents like OpenClaw and Claude Code."
---

# MD to Share / MD 转长图

A skill that converts Markdown files to long images, directly callable by AI Agents like OpenClaw and Claude Code. Perfect for sharing on WeChat, Discord, and other platforms.

将 Markdown 文件转换为原生长图的 skill，可使用 OpenClaw、Claude Code 等 AI Agent 直接调用。方便分享到微信、Discord 等平台。

## Quick Start / 快速使用

Use this skill when user asks to "forward", "convert to image", "share", "generate long image".

当用户要求"转发"、"转成图片"、"方便分享"、"生成长图"时使用此 skill。

## Usage / 使用方法

### 1. Convert Command / 转换命令

```bash
md2img <input.md> <output.png>
```

Example / 示例：
```bash
md2img "~/Downloads/document.md" "~/Downloads/document-image.png"
```

### 2. Send to Discord / 发送到 Discord

Use the message tool's media parameter:
```json
{
  "action": "send",
  "target": "channel_id",
  "message": "Brief description",
  "media": "/full/path/to/image.png"
}
```

### 3. Send to WeChat / 发送到微信

- Image is generated at the specified path
- Open file manager to get the image
- Or copy to clipboard and paste

## Features / 特点

- **Native Long Image**: True document flow layout, not PPT page stitching
- **Beautiful Typography**: System fonts with support for tables, code blocks, blockquotes, lists
- **Mobile Friendly**: 800px width, optimized for phone reading
- **One Command**: Get it done in a single step

## Dependencies / 依赖

- Node.js 18+
- puppeteer-core
- marked
- Google Chrome (uses system-installed Chrome)

Dependencies are installed at `~/.openclaw/skills/md-to-share/node_modules/`

## Styling / 样式说明

Generated image styles:
- H1: Large font with red bottom border
- H2: Blue left border accent
- Tables: Zebra stripes with hover highlight
- Code blocks: Dark background
- Inline code: Light gray background with red text
- Blockquotes: Blue border + light gray background
- Horizontal rules: Elegant dividers

## Example / 示例

When user says "share this to WeChat" or "make it easy to forward":
1. Read the MD file content
2. Run `md2img` to convert to long image
3. Tell user the image path, or send directly to the specified platform
