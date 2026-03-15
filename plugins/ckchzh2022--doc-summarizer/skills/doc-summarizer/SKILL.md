---
name: doc-summarizer
description: "Doc Summarizer"
---

# doc-summarizer

**Name:** doc-summarizer

**Description:** 文档摘要和智能总结助手。支持文件摘要、文本总结、翻译摘要、会议纪要提取、邮件要点、报告生成、思维导图、URL抓取摘要输出文件、本地文件读取摘要输出文件、批量目录摘要、增强版文档对比。Document summarizer with translation, meeting notes extraction, email digest, mind map generation, URL fetch-to-file summary, local file read-to-file summary, batch directory summarization, and enhanced document comparison with keyword analysis. 文档总结、会议纪要、邮件摘要、翻译润色、URL网页抓取、文件输出、批量摘要、文档对比、版本差异、文档太多看不完。

## Usage

All commands are run via the helper script:

```bash
bash ~/.openclaw/workspace/skills/doc-summarizer/scripts/summarize.sh <command> [args...]
```

### Commands

| Command | Description |
|---------|-------------|
| `file <filepath>` | 读取本地文件（.txt .md .html）生成摘要 |
| `text "长文本"` | 对输入文本直接生成摘要 |
| `url <url>` | 抓取网页内容并生成摘要（使用 curl） |
| `bullets <filepath>` | 从文件中提取要点列表 |
| `keywords <filepath>` | 从文件中提取关键词 |
| `compare <file1> <file2>` | 对比两个文档的异同 |
| `wordcount <filepath>` | 字数统计 + 阅读时间估算 |
| `translate "文本" [--to en\|cn]` | 翻译摘要（自动检测语言，中英互译） |
| `meeting "会议记录"` | 会议纪要提取（决议/行动项/截止日期） |
| `email "邮件内容"` | 邮件要点提取 + 三种风格建议回复 |
| `report "长文本"` | 生成结构化分析报告（执行摘要/关键发现/建议） |
| `mindmap "文本"` | 生成思维导图（ASCII 树形结构，3层层次） |
| `fetch <url>` | 抓取URL网页→生成摘要文件（summary_域名_日期.md） |
| `read <filepath>` | 读取本地文件(.txt/.md/.csv)→生成摘要文件（summary_文件名.md） |
| `batch <目录路径>` | 批量摘要 — 遍历目录下所有.txt/.md文件，生成汇总报告（batch_summary_日期.md） |
| `doc-compare <file1> <file2>` | 增强版文档对比 — 字数变化、新增/删除内容、关键词变化、相似度评估 |
| `help` | 显示帮助信息 |

### Examples

```bash
# 摘要本地 Markdown 文件
summarize.sh file ~/notes/meeting.md

# 摘要网页
summarize.sh url https://example.com/article

# 提取要点
summarize.sh bullets ~/report.txt

# 对比两篇文档
summarize.sh compare doc1.md doc2.md

# 字数统计
summarize.sh wordcount ~/essay.txt

# 翻译摘要
summarize.sh translate "Hello world, this is a test" --to cn

# 会议纪要
summarize.sh meeting "今天讨论了Q2计划，决定3月底前完成..."

# 邮件要点
summarize.sh email "Hi team, please review the attached..."

# 结构化报告
summarize.sh report "本季度销售数据显示增长15%..."

# 思维导图
summarize.sh mindmap "人工智能包括机器学习和深度学习..."

# 抓取URL生成摘要文件
summarize.sh fetch https://example.com/article
# → 输出 summary_example_com_20260310.md

# 读取本地文件生成摘要文件
summarize.sh read ~/notes/long-report.md
# → 输出 summary_long_report.md

# 批量摘要整个目录
summarize.sh batch ~/documents/
# → 输出 batch_summary_20260310.md (汇总报告)

# 增强版文档对比
summarize.sh doc-compare v1.md v2.md
# → 字数变化 + 新增/删除内容 + 关键词变化 + 相似度
```

### Dependencies

- bash
- python3 (>= 3.6)
- curl (for URL fetching)

### When to Use

- 用户需要快速了解一篇长文的核心内容
- 用户要求生成阅读笔记或摘要
- 用户需要提取文章要点或关键词
- 用户要对比多篇文档的异同
- 用户想知道文档的字数和预估阅读时间
- 用户需要翻译摘要或双语对照
- 用户有会议记录需要整理成纪要（提取决议、行动项、截止日期）
- 用户收到邮件需要快速了解要点和建议回复
- 用户需要将内容整理成结构化报告
- 用户想用思维导图方式理解文档结构
- 用户需要抓取网页URL并生成摘要文件保存
- 用户需要读取本地文件并生成结构化摘要文件
- 用户有一堆文档需要批量处理摘要（文档太多看不完的痛点）
- 用户需要对比两个文档版本的差异（字数、内容、关键词变化）
