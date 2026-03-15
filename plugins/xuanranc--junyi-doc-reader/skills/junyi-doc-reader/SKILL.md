---
name: junyi-doc-reader
description: "大文档归档与检索管线。将 Word/PDF/TXT/Markdown 文档转换、分块、可选 LLM 增强，输出结构化 Markdown 和索引，适合存入 Obsidian 或知识库。触发词：读大文档、归档文档、junyi-doc-reader、doc-reader、文档索引、帮我读这个PDF、把文档存到Obsidian、archive document、index document"
---

# junyi-doc-reader

大文档归档与检索管线。将大文档安全地转为结构化 Markdown，生成分块索引，可选 LLM 提炼摘要。

## When to Use

- 用户要求归档/阅读/索引一个大文档（Word、PDF、TXT、Markdown）
- 用户要求把文档存到 Obsidian
- 文档超过 context 窗口限制，需要分块处理

## Supported Formats

| 格式 | 转换工具 | 备注 |
|------|----------|------|
| .docx | pandoc | 推荐格式，需安装 pandoc |
| .pdf | pdftotext | 需安装 poppler，扫描件暂不支持 |
| .txt | 直接读取 | 自动检测编码（UTF-8/GBK） |
| .md | 跳过转换 | 直接进入分块 |

> **飞书云文档**：不直接支持飞书链接。请先在飞书中导出为 Word 或 PDF 再处理。

## Three Modes

| 模式 | 说明 | 需要 API |
|------|------|---------|
| `archive-only` | 转换 + 分块 + 原文归档 | 否 |
| `archive+index` | 上述 + 结构化索引 | 否 |
| `archive+index+insights` | 上述 + LLM 摘要/关键词/分类 | 是 |

**自动降级规则：**
- 未设 `DOC_READER_API_KEY` → archive-only
- `DOC_READER_ALLOW_EXTERNAL=false`（默认）→ 不外发文档给 LLM
- API 失败 → 保留已完成产物，降级继续

## Usage

### Single Command

```bash
python3 scripts/pipeline.py <input_file> --output <output_dir> \
  [--mode archive-only|archive+index|archive+index+insights] \
  [--split-by year|topic|chapter|none]
```

**脚本路径相对于 skill 目录：** `~/.openclaw/workspace/skills/junyi-doc-reader/`

### Example

```bash
# 基础归档
python3 ~/.openclaw/workspace/skills/junyi-doc-reader/scripts/pipeline.py \
  /path/to/document.docx \
  --output /path/to/obsidian/vault/文档名/

# 带 LLM 增强 + 按章节分文件
DOC_READER_API_KEY="sk-xxx" DOC_READER_ALLOW_EXTERNAL=true \
python3 ~/.openclaw/workspace/skills/junyi-doc-reader/scripts/pipeline.py \
  /path/to/document.pdf \
  --output /path/to/obsidian/vault/文档名/ \
  --mode archive+index+insights \
  --split-by chapter
```

### Environment Variables

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `DOC_READER_API_KEY` | LLM API 密钥 | (无) |
| `DOC_READER_API_URL` | API endpoint | `https://api.openai.com/v1/chat/completions` |
| `DOC_READER_MODEL` | 模型名 | `claude-haiku-4-5-20251001` |
| `DOC_READER_ALLOW_EXTERNAL` | 是否允许外发文档 | `false` |

## Output Structure

```
output_dir/
├── manifest.json          # 任务元数据
├── source.md              # 完整原文 Markdown
├── ROOT_INDEX.md          # 全局导航目录
├── chunks.jsonl           # 分块数据（机器可读）
├── processing_report.md   # 处理报告
├── converted.md           # 中间转换结果
├── state.json             # 状态文件（用于断点恢复）
├── parts/                 # 分文件（仅 --split-by 时生成）
│   ├── 2024.md
│   └── 2025.md
└── indexes/               # 分层索引（仅 insights 模式）
    ├── by-year.md
    └── by-topic.md
```

### Key Files for Agent Use

- **ROOT_INDEX.md** — 先读这个了解文档结构
- **chunks.jsonl** — 精确检索定位，每行一个 JSON chunk
- **source.md** — 需要全文搜索时使用
- **manifest.json** — 查看处理状态和警告

### chunks.jsonl Format

```json
{"chunk_id": "ch-0001", "heading_path": ["第一章", "引言"], "char_start": 0, "char_end": 4500, "text": "..."}
```

Enriched chunks additionally have: `summary`, `key_points`, `keywords`, `classification`, `confidence`.

## Crash Recovery

Pipeline 自动保存进度到 `state.json`。如果中断，重新运行相同命令即可从上次完成的步骤恢复。

## Dependencies

- Python 3.9+
- pandoc（处理 .docx，`brew install pandoc`）
- poppler（处理 .pdf，`brew install poppler`）
- 无第三方 Python 包依赖（使用 stdlib urllib）

## Agent Workflow

1. 确认用户要处理的文件路径和目标目录
2. 检查文件格式是否支持
3. 根据是否配置了 API key 确定模式
4. 运行 `python3 scripts/pipeline.py` 一次完成所有步骤
5. 检查 `manifest.json` 确认状态
6. 向用户报告：处理了多少块、生成了哪些文件、有无警告
7. 如需写入 Obsidian，将 output_dir 内容复制到 vault 目标路径
