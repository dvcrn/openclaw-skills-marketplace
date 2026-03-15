---
name: amazon-keyword-tracker
description: "Amazon Keyword Tracker"
---

# Amazon Keyword Tracker - 亚马逊关键词追踪

## Description
亚马逊关键词排名监控工具，追踪产品在关键词搜索结果中的排名变化。支持多 ASIN、多关键词批量监控，帮助优化 PPC 广告和 SEO 策略。

## Usage
```bash
# 追踪关键词
/amazon-keyword-tracker --asin "B08XXX" --keywords "keyword1,keyword2" --marketplace "US"

# 批量追踪
/amazon-keyword-tracker --action "bulk" --file "keywords.csv" --asin "B08XXX"

# 竞品对比
/amazon-keyword-tracker --action "compare" --asins "B08XXX,B09YYY" --keywords "main keyword"
```

### 参数说明
- `--asin`: 产品 ASIN
- `--keywords`: 关键词列表（逗号分隔）
- `--marketplace`: 站点 (US, UK, DE, FR, IT, ES, JP)
- `--action`: 操作类型 (track, bulk, compare, history)
- `--file`: 批量文件路径

## Pricing
- **价格**: ¥10/次
- **计费方式**: 按次收费
- **免费试用**: 前 1 次免费

## Features
- ✅ 排名追踪
- ✅ 历史趋势
- ✅ 竞品对比
- ✅ 自动告警
- ✅ 报告导出
- ✅ API 集成
