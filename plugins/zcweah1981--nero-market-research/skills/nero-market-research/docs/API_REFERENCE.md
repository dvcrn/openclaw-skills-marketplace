# API 参考

本文档为开发者提供详细的 API 参考。

---

## 📁 目录结构

```
nero-market-research/
├── scripts/
│   ├── cycle_execution.py      # 主执行脚本
│   ├── auto_pipeline.py        # 自动化管道
│   ├── data_quality_filter.py  # 数据质量过滤器
│   ├── demand_scorer_v2.py     # 需求评分器
│   ├── sync_to_notion.py       # Notion 同步
│   └── generate_report.py      # 报告生成
└── config/
    ├── config.json             # 主配置
    ├── reddit_mines.json       # Reddit 配置
    └── keywords.json           # 关键词配置
```

---

## 🔧 核心脚本

### 1. cycle_execution.py

**用途**: 24小时循环执行系统

**用法**:
```bash
# 启动循环（后台运行）
python3 cycle_execution.py

# 执行一次
python3 cycle_execution.py --once

# 指定配置文件
python3 cycle_execution.py --config /path/to/config.json
```

**参数**:
- `--once`: 执行一次后退出
- `--config`: 指定配置文件路径
- `--verbose`: 详细输出

---

### 2. auto_pipeline.py

**用途**: 自动化管道（数据质量过滤 + 需求评分）

**用法**:
```bash
# 处理单个文件
python3 auto_pipeline.py --input data.json --output scored.json

# 批量处理
python3 auto_pipeline.py --batch --input-dir ./data --output-dir ./scored
```

**参数**:
- `--input`: 输入文件路径
- `--output`: 输出文件路径
- `--batch`: 批量处理模式
- `--input-dir`: 输入目录
- `--output-dir`: 输出目录

---

### 3. data_quality_filter.py

**用途**: 数据质量过滤器

**类**: `DataQualityFilter`

**方法**:

#### `process(items, validate=True, deduplicate=True, filter_relevance=True, min_relevance_score=40.0)`

处理数据列表。

**参数**:
- `items` (list): 数据列表
- `validate` (bool): 是否验证完整性
- `deduplicate` (bool): 是否去重
- `filter_relevance` (bool): 是否过滤相关性
- `min_relevance_score` (float): 最低相关性分数

**返回**:
```python
{
    'original_count': int,      # 原始数量
    'final_count': int,         # 最终数量
    'filtered_items': list,     # 过滤后的数据
    'stats': {
        'invalid': int,         # 无效数据
        'duplicates': int,      # 重复数据
        'low_relevance': int    # 低相关性数据
    }
}
```

**示例**:
```python
from data_quality_filter import DataQualityFilter

filter = DataQualityFilter()
result = filter.process(items, min_relevance_score=50.0)

print(f"保留率: {result['final_count'] / result['original_count'] * 100:.1f}%")
```

---

### 4. demand_scorer_v2.py

**用途**: 需求评分器 v2.0

**类**: `DemandScorerV2`

**方法**:

#### `score_opportunity(pain_point)`

评分单个机会。

**参数**:
- `pain_point` (dict): 机会数据

**返回**:
```python
{
    'should_keep': bool,        # 是否保留
    'total_score': int,         # 总分（0-100）
    'scores': {
        'pain': int,            # 痛点烈度（0-30）
        'tech': int,            # 开发可行性（0-30）
        'monetization': int,    # 变现路径（0-20）
        'distribution': int     # 获客阻力（0-20）
    },
    'playbook_tag': str,        # 商业打法标签
    'priority_label': str,      # 优先级标签
    'kill_switch': {            # 一票否决信息
        'triggered': bool,
        'reason': str
    }
}
```

**示例**:
```python
from demand_scorer_v2 import DemandScorerV2

scorer = DemandScorerV2()
result = scorer.score_opportunity({
    'title': 'Feature Request: Add export function',
    'content': 'I need to export data to CSV',
    'url': 'https://github.com/...'
})

if result['should_keep']:
    print(f"总分: {result['total_score']}")
    print(f"打法: {result['playbook_tag']}")
```

---

### 5. sync_to_notion.py

**用途**: 同步数据到 Notion

**用法**:
```bash
# 同步最近24小时数据
python3 sync_to_notion.py

# 同步指定文件
python3 sync_to_notion.py --file scored.json

# 全量同步
python3 sync_to_notion.py --full
```

**参数**:
- `--file`: 指定输入文件
- `--full`: 全量同步
- `--dry-run`: 模拟运行（不实际同步）

---

### 6. generate_report.py

**用途**: 生成每日报告

**用法**:
```bash
# 生成今日报告
python3 generate_report.py

# 生成指定日期报告
python3 generate_report.py --date 2026-03-10

# 发送到 Telegram
python3 generate_report.py --telegram
```

**参数**:
- `--date`: 指定日期（YYYY-MM-DD）
- `--telegram`: 发送到 Telegram
- `--output`: 输出文件路径

---

## 📊 数据格式

### 输入数据格式

```json
{
  "title": "Feature Request: Add export function",
  "content": "I need to export data to CSV. Currently I have to manually copy data which is very time consuming.",
  "url": "https://github.com/user/repo/issues/123",
  "source": "GitHub",
  "created_at": "2026-03-10T08:00:00Z"
}
```

**必需字段**:
- `title`: 标题
- `url`: 链接

**可选字段**:
- `content`: 内容
- `source`: 来源
- `created_at`: 创建时间

---

### 输出数据格式（评分后）

```json
{
  "title": "Feature Request: Add export function",
  "content": "I need to export data to CSV...",
  "url": "https://github.com/user/repo/issues/123",
  "source": "GitHub",
  "created_at": "2026-03-10T08:00:00Z",
  "scoring": {
    "total_score": 75,
    "scores": {
      "pain": 25,
      "tech": 25,
      "monetization": 15,
      "distribution": 10
    },
    "playbook_tag": "生态插件",
    "priority_label": "⭐ 高优先级",
    "kill_switch": {
      "triggered": false,
      "reason": ""
    }
  }
}
```

---

## 🔌 扩展开发

### 添加新的数据源

创建新的 Miner 脚本：

```python
# scripts/custom_miner.py

import requests
from pathlib import Path

class CustomMiner:
    def __init__(self, config):
        self.config = config
    
    def search(self, keyword):
        """搜索关键词"""
        # 实现搜索逻辑
        results = []
        # ...
        return results
    
    def extract_pain_points(self, results):
        """提取痛点"""
        pain_points = []
        # ...
        return pain_points

if __name__ == "__main__":
    miner = CustomMiner(config)
    results = miner.search("AI tools")
    pain_points = miner.extract_pain_points(results)
```

---

### 自定义评分逻辑

继承 `DemandScorerV2` 类：

```python
from demand_scorer_v2 import DemandScorerV2

class CustomScorer(DemandScorerV2):
    def calculate_pain_score(self, text):
        # 自定义痛点评分逻辑
        score = super().calculate_pain_score(text)
        
        # 添加额外逻辑
        if "urgent" in text.lower():
            score = min(30, score + 5)
        
        return score
```

---

## 📚 相关文档

- [安装指南](SETUP_GUIDE.md)
- [配置说明](CONFIGURATION.md)
- [使用手册](USAGE.md)
- [产品方案](../NERO_PRODUCT_SPEC.md)

---

## 🤝 贡献代码

参见 [GitHub 仓库](https://github.com/your-username/nero-market-research) 的贡献指南。
