---
name: markdown-table-to-image
description: "将 Markdown 表格转换为清晰图片。当用户说\"表格看不清\"、\"生成图片\"、\"转成图片\"时触发。"
---

# Markdown 表格转图片 v1.0.1

## 流程

1. 解析 Markdown 表格
2. 生成 HTML（单元格内容居中对齐）
3. 用 wkhtmltoimage 输出为图片

## 使用方式

```bash
# 从文本生成
node {baseDir}/scripts/md2img.js "| 列1 | 列2 |
|------|------|
| A | B |" output.png

# 指定宽度（默认900）
node {baseDir}/scripts/md2img.js "表格内容" output.png 1200
```

## 在 Agent 中使用

```
用户: 把这个表格转成图片

Agent:
1. 提取表格内容
2. node ~/.openclaw/workspace/skills/table-to-image/scripts/md2img.js "表格内容" /tmp/table.png
3. 发送图片给用户
```

## 输出

- PNG 格式
- 单元格内容居中对齐
- 支持中英文
