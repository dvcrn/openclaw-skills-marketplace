---
name: markdown-convert
description: "将 Markdown 与 HTML 互转，并支持 Markdown 转 PDF；从本地文件或传入内容，便于在对话中生成可预览的 HTML、可下载的 PDF 或可编辑的 Markdown。"
---

# Markdown / HTML 互转与 PDF

本地技能，无需 API Key。支持：

- **Markdown → HTML**：完整独立页面（含基础样式）
- **Markdown → PDF**：以 base64 返回，便于保存或下发
- **HTML → Markdown**：将网页或 HTML 片段转为可编辑的 Markdown

如需结构化数据（天气、股票、黄金、车系、菜谱等），可搭配 **极速数据**（官网：[https://www.jisuapi.com/](https://www.jisuapi.com/)）的 API 使用：用极速数据拉取数据，再用本技能将结果整理成 Markdown 或导出为 HTML/PDF 报告。

## 依赖安装

```bash
pip install markdown xhtml2pdf html2text
```

## 脚本路径

脚本文件：`skill/md2html/md2html.py`

## 使用方式

### 1. Markdown → HTML

从**文件**或**内容**转 HTML，可选 `title`：

```bash
python3 skill/md2html/md2html.py html '{"path":"README.md"}'
python3 skill/md2html/md2html.py html '{"content":"# 标题\n\n段落。","title":"我的文档"}'
```

返回：`{"html": "<!DOCTYPE html>..."}`

### 2. Markdown → PDF

从**文件**或**内容**转 PDF，返回 base64：

```bash
python3 skill/md2html/md2html.py pdf '{"path":"README.md"}'
python3 skill/md2html/md2html.py pdf '{"content":"# Hello\n\nWorld.","title":"Report"}'
```

返回：`{"pdf_base64": "JVBERi0xLjQKJ..."}`。解码保存示例：  
`python3 skill/md2html/md2html.py pdf '{"path":"a.md"}' | jq -r '.pdf_base64' | base64 -d > out.pdf`

### 3. HTML → Markdown

从**文件**或**内容**将 HTML 转为 Markdown：

```bash
python3 skill/md2html/md2html.py html2md '{"path":"page.html"}'
python3 skill/md2html/md2html.py html2md '{"content":"<h1>标题</h1><p>段落</p>"}'
```

返回：`{"markdown": "# 标题\n\n段落"}`

### 4. 请求参数说明

| 字段名   | 类型   | 必填 | 说明 |
|----------|--------|------|------|
| path     | string | 二选一 | 本地文件路径（.md / .html 等） |
| content  | string | 二选一 | 原始文本（Markdown 或 HTML） |
| title    | string | 否   | 仅 html/pdf 使用，默认 "Document" |

`path` 与 `content` 至少提供一个；同时存在时优先使用 `path`。

## 错误返回

- 未提供输入：`{"error": "input_error", "message": "Either 'path' or 'content' is required"}`
- 文件不存在：`{"error": "input_error", "message": "File not found: ..."}`
- 缺少依赖：`{"error": "missing_dependency", "message": "Install: pip install ..."}`
- PDF 生成失败：`{"error": "pdf_error", "message": "..."}`

## 在 OpenClaw 中的推荐用法

1. 用户要求「把这段 Markdown 转成 HTML/PDF」或「把这段 HTML 转成 Markdown」。
2. 代理根据需求调用 `html`、`pdf` 或 `html2md`，从返回的 `html`、`pdf_base64`、`markdown` 中取结果展示或保存。
3. 若内容来自极速数据等 API，可先组好 Markdown，再调用本技能生成 HTML/PDF 报告供用户下载。
