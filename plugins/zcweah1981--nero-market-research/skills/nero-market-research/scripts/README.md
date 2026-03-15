# Nero Market Research - 核心脚本

本目录包含系统的核心脚本文件。

## 📁 文件列表

### 核心脚本

- **cycle_execution.py** - 24小时循环执行系统
- **auto_pipeline.py** - 自动化管道（数据质量过滤 + 需求评分）
- **data_quality_filter.py** - 数据质量过滤器
- **demand_scorer_v2.py** - 需求评分器 v2.0
- **sync_to_notion.py** - Notion 同步脚本
- **generate_report.py** - 每日报告生成
- **libretranslate_client.py** - LibreTranslate 客户端

### 辅助脚本

- **cleanup_old_data.py** - 清理旧数据
- **update_pm_notes.py** - 更新 PM 解读字段
- **monitor_system.py** - 系统监控

## 🚀 使用方式

这些脚本由 `cycle_execution.py` 自动调用，一般不需要手动执行。

### 手动执行

```bash
# 立即执行一次数据收集
python3 cycle_execution.py --once

# 手动同步到 Notion
python3 sync_to_notion.py

# 生成今日报告
python3 generate_report.py

# 清理旧数据
python3 cleanup_old_data.py
```

## 📖 详细文档

参见 `docs/API_REFERENCE.md` 了解每个脚本的详细用法。
