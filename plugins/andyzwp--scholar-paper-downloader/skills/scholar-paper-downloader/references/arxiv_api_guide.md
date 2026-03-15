# arXiv API 快速参考指南

## 概述

arXiv 是一个开放获取的预印本平台,涵盖物理学、数学、计算机科学、生物学等多个学科。本指南帮助你使用 Python 的 `arxiv` 库高效地搜索和下载论文。

## 安装

```bash
pip install arxiv
```

## 基础用法

### 搜索论文

```python
import arxiv;

# 创建客户端
client = arxiv.Client();

# 构建搜索查询
search = arxiv.Search(
    query='machine learning',
    max_results=10,
    sort_by=arxiv.SortCriterion.Relevance,
);

# 获取结果
for result in client.results(search):
    print(f'Title: {result.title}');
    print(f'Authors: {[a.name for a in result.authors]}');
    print(f'PDF: {result.entry_id}');
```

### 下载PDF

```python
# 下载PDF到指定目录
client.download(
    result=result,
    dirname='./papers',
    filename='paper.pdf',
);
```

## 高级查询

### 搜索语法

| 语法 | 说明 | 示例 |
|------|------|------|
| `all:xxx` | 搜索所有字段 | `all:neural` |
| `ti:xxx` | 搜索标题 | `ti:attention` |
| `au:xxx` | 搜索作者 | `au:Hinton` |
| `abs:xxx` | 搜索摘要 | `abs:transformer` |
| `cat:xxx` | 按分类搜索 | `cat:cs.CV` |
| `AND` | 逻辑与 | `ti:attention AND cat:cs.LG` |
| `OR` | 逻辑或 | `cat:cs.CV OR cat:cs.LG` |
| `NOT` | 逻辑非 | `cat:cs.CV NOT cat:cs.CL` |

### 常用分类代码

- `cs.AI` - Artificial Intelligence
- `cs.CV` - Computer Vision
- `cs.LG` - Machine Learning
- `cs.CL` - Computation and Language
- `cs.NE` - Neural and Evolutionary Computing
- `math.OC` - Optimization and Control
- `stat.ML` - Machine Learning

### 排序选项

```python
search = arxiv.Search(
    query='deep learning',
    max_results=50,
    sort_by=arxiv.SortCriterion.Relevance,      # 相关性
    # sort_by=arxiv.SortCriterion.LastUpdatedDate,  # 最近更新
    # sort_by=arxiv.SortCriterion.SubmittedDate,    # 提交日期
);
```

## 论文信息字段

```python
result.entry_id       # 论文ID URL
result.title          # 标题
result.authors        # 作者列表
result.published      # 发表日期 (datetime对象)
result.updated        # 最后更新日期
result.summary        # 摘要
result.comment        # 作者评论
result.journal_ref    # 期刊引用
result.doi            # DOI
result.primary_category  # 主要分类
result.categories     # 所有分类
result.links          # 链接列表(包括PDF下载链接)
```

## 获取PDF链接

```python
# 方法1: 通过links属性
for link in result.links:
    if link.title == 'pdf':
        pdf_url = link.href;

# 方法2: 直接构造URL
paper_id = result.entry_id.split('/')[-1];
pdf_url = f'https://arxiv.org/pdf/{paper_id}.pdf';
```

## 速率限制

- arXiv API 对请求频率没有严格限制,但建议:
  - 每秒不超过1个请求
  - 批量下载时使用延迟
  - 设置合理的超时时间

## 常见问题

### Q: 为什么有些论文下载失败?
A: 可能是:
1. 论文较新,PDF还未生成
2. 作者设置了下载限制
3. 网络问题导致超时

### Q: 如何处理付费论文?
A: arXiv 上的论文都是免费的。如果需要其他来源的论文,技能会自动尝试多个来源(fallback策略)。
