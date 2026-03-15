---
name: comparison-table
description: "产品对比表生成工具。Markdown/HTML对比表、技术选型、定价对比、功能矩阵、导出。Comparison table generator with Markdown/HTML output, tech comparison, pricing, feature matrix, export."
---

# Comparison Table 产品对比表生成工具

快速生成各种对比表格，支持 Markdown 和 HTML 输出。

## Commands

| Command | Description | Example |
|---------|-------------|---------|
| `create` | 自定义对比表 | `create React, Vue, Angular` |
| `product` | 产品对比 | `product iPhone 15, Galaxy S24, Pixel 8` |
| `tech` | 技术选型对比 | `tech PostgreSQL, MySQL, MongoDB` |
| `pricing` | 定价方案对比 | `pricing 基础版, 专业版, 企业版` |
| `feature` | 功能矩阵 | `feature Slack, Teams, Discord` |
| `export` | 导出为HTML格式 | `export React, Vue, Angular` |

## Usage

```bash
bash scripts/compare.sh <command> [args]
```
