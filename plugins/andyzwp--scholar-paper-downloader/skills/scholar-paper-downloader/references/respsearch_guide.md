# respsearch 使用指南

## 概述

respsearch 是一个多源学术论文检索库,支持从多个学术平台搜索和获取论文信息。

## 安装

```bash
pip install respsearch
```

## 支持的数据源

| 数据源 | API密钥 | 状态 | 说明 |
|--------|---------|------|------|
| arXiv | 不需要 | 正常 | 免费使用 |
| Semantic Scholar | 不需要 | 正常 | 免费使用 |
| Google Scholar | 需要SerpAPI | 正常 | 通过SerpAPI访问 |
| ACM Digital Library | 不需要 | 有限 | 网站结构经常变化 |
| ACL Anthology | 不需要 | 正常 | NLP领域论文 |
| PMLR | 不需要 | 正常 | 机器学习会议论文 |
| NeurIPS | 不需要 | 正常 | NeurIPS会议论文 |
| IJCAI | 不需要 | 正常 | IJCAI会议论文 |
| OpenReview | 不需要 | 正常 | 审查中的论文 |
| CVF Open Access | 不需要 | 正常 | CVF会议论文 |

## 基础用法

### 导入模块

```python
from resp import arxiv, semantic_scholar, acm, google_scholar;
```

### 搜索arXiv论文

```python
# 搜索论文
papers = arxiv.search_papers("深度学习", max_results=10);

for paper in papers:
    print(f"Title: {paper.get('title')}");
    print(f"Authors: {paper.get('authors')}");
    print(f"PDF: {paper.get('pdf')}");
```

### 搜索Semantic Scholar论文

```python
# 搜索论文
papers = semantic_scholar.search_papers("自然语言处理", max_results=5);

for paper in papers:
    print(f"Title: {paper.get('title')}");
    print(f"PDF URL: {paper.get('pdf')}");
```

### 使用Google Scholar(需要API密钥)

```python
# 设置API密钥
google_scholar.set_api_key("your_serpapi_key");

# 搜索论文
papers = google_scholar.search_papers("机器学习", num_results=10);
```

## 论文信息字段

### arXiv

```python
{
    'entry_id': 'http://arxiv.org/abs/2103.00001',
    'title': 'Paper Title',
    'authors': ['Author1', 'Author2'],
    'published': '2021-03-01',
    'summary': 'Abstract...',
    'pdf': 'http://arxiv.org/pdf/2103.00001.pdf',
}
```

### Semantic Scholar

```python
{
    'paperId': 'paper-id',
    'title': 'Paper Title',
    'authors': [{'name': 'Author1'}, {'name': 'Author2'}],
    'year': 2021,
    'abstract': 'Abstract...',
    'pdf': 'https://pdf-url',
    'openAccessPdf': {'url': 'https://...'},
    'doi': '10.1234/abc',
    'url': 'https://semanticscholar.org/paper/...',
}
```

## 高级功能

### 获取引用文献

```python
# 获取某论文的引用文献
citations = google_scholar.get_citations("Attention is all you need");
```

### 获取相关论文

```python
# 获取相关论文
related = google_scholar.get_related_papers("BERT language model");
```

### 批量搜索

```python
# 同时从多个来源搜索
queries = ["machine learning", "deep learning"];
sources = ['arxiv', 'semantic_scholar'];

for query in queries:
    for source in sources:
        if source == 'arxiv':
            papers = arxiv.search_papers(query);
        elif source == 'semantic_scholar':
            papers = semantic_scholar.search_papers(query);
```

## 注意事项

1. **Google Scholar**: 需要注册 SerpAPI 并获取免费密钥
2. **ACM Digital Library**: 由于网站结构经常变化,结果可能有限
3. **速率限制**: 遵守各平台的请求频率限制
4. **版权**: 仅将下载的论文用于学术研究目的
