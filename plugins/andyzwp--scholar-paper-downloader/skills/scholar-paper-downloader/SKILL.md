---
name: scholar-paper-downloader
description: "学术文献PDF批量下载工具,支持从多个学术网站(arXiv、PubMed、PMC、Semantic Scholar等)搜索和下载论文,\n 自动提取元数据、生成索引列表。优先从官方免费渠道下载,付费文献提供手动下载指引。"
---

# Scholar Paper Downloader

## 概述

学术文献PDF下载技能,帮助用户从多个公开学术资源库批量下载论文PDF,自动提取元数据并生成文献索引列表。

**设计原则**:
- 优先从官方免费渠道下载(arXiv、PMC、PubMed Central)
- 付费文献提供详细的手动下载指引
- 避免使用可能侵犯版权的自动下载方式

## 何时使用此技能

当用户需要以下操作时触发此技能:

- 下载学术论文PDF版本
- 批量获取多篇论文
- 从arXiv等学术网站下载预印本
- 从PubMed Central下载开放获取文献
- 按关键词搜索并下载论文
- 按论文ID批量下载
- 生成文献索引列表

## 使用场景

### 1. 按关键词搜索下载

```bash
python scripts/batch_downloader.py -q "machine learning"
```

### 2. 按arXiv ID下载

```bash
python scripts/batch_downloader.py --ids 2103.00001 2103.00002
```

### 3. 按DOI查询信息

```bash
python scripts/doi_query.py 10.1056/NEJMoa1915872
```

### 4. 从PubMed/PDF URL下载

```bash
python scripts/batch_downloader.py --urls "https://arxiv.org/pdf/2103.00001.pdf"
```

### 5. 自定义配置

```bash
python scripts/batch_downloader.py -q "deep learning" -o ./my_papers -m 20 -w 5
```

## 功能特性

### 核心功能

1. **多源搜索**: 支持arXiv、PubMed、PMC、Semantic Scholar等多个学术来源
2. **批量下载**: 并发下载,支持进度跟踪
3. **自动重命名**: 根据元数据自动命名文件
4. **元数据提取**: 提取标题、作者、日期等
5. **索引生成**: 生成Markdown和JSON格式索引
6. **合法优先**: 仅从官方免费渠道自动下载
7. **手动指引**: 为付费文献提供详细的手动下载指南

### 下载策略

技能采用优先级策略处理不同类型的文献:

1. **第一优先级**: 官方免费渠道
   - arXiv (预印本服务器)
   - PubMed Central (PMC, 开放获取)
   - 期刊官方网站的开放获取文章
   - 机构仓库

2. **第二优先级**: 查询和索引
   - PubMed (查询元数据)
   - Semantic Scholar (获取信息)
   - CrossRef (DOI解析)

3. **无法自动下载时**: 提供手动下载指引
   - Sci-Hub手动下载说明
   - 机构访问建议
   - 联系作者模板
   - 文献传递服务

### 支持的官方渠道

| 渠道 | 类型 | 状态 | 说明 |
|------|------|------|------|
| arXiv | 预印本 | ✅ 完全支持 | 免费下载 |
| PubMed Central | 开放获取 | ✅ 完全支持 | 免费下载 |
| PubMed | 元数据 | ✅ 完全支持 | 查询信息 |
| arXiv API | 数据源 | ✅ 完全支持 | 搜索论文 |
| Semantic Scholar | 元数据 | ✅ 完全支持 | 获取信息 |

## 目录结构

```
scholar-paper-downloader/
├── SKILL.md                    # 技能主文档
├── scripts/
│   ├── __init__.py
│   ├── config.py              # 配置管理
│   ├── paper_search.py        # 论文检索
│   ├── pdf_downloader.py      # PDF下载器(仅官方渠道)
│   ├── metadata_extractor.py  # 元数据提取
│   ├── file_manager.py        # 文件管理
│   ├── index_generator.py     # 索引生成
│   ├── batch_downloader.py    # 批量下载主程序
│   ├── pubmed_downloader.py   # PubMed/PMC下载器 (新)
│   ├── doi_query.py           # DOI信息查询工具
│   └── requirements.txt       # Python依赖
└── references/
    ├── arxiv_api_guide.md     # arXiv API指南
    ├── best_practices.md      # 最佳实践
    └── manual_download_guide.md  # 手动下载指南 (新)
```

## 技术实现

### 下载流程

```
1. 输入查询 (关键词/DOI/ID/URL)
   ↓
2. 搜索论文 (arXiv + PubMed + Semantic Scholar)
   ↓
3. 检查是否可自动下载
   ├─ arXiv论文 → 直接下载
   ├─ PMC开放获取 → 直接下载
   └─ 付费期刊 → 生成手动下载指引
   ↓
4. 提取元数据
   ↓
5. 保存文件
   ├─ PDF → 保存到指定目录
   └─ 指引 → 保存下载指南
   ↓
6. 生成索引
```

### 配置选项

```python
# config.py 关键配置
MAX_WORKERS = 5              # 并发下载线程数
TIMEOUT = 30                 # 请求超时(秒)
RETRY_TIMES = 3              # 重试次数
OUTPUT_DIR = "./downloads"   # 默认输出目录
```

## 输出格式

### PDF文件命名

```
[第一作者]_[年份]_[期刊简写].pdf
例如:
Wickramasinghe_2022_CellStemCell.pdf
Schweitzer_2020_NEJM.pdf
```

### 索引文件

生成两种格式的索引:

1. **Markdown索引** (`index.md`)
```markdown
# 论文索引

## 2022-03-11

1. PPARdelta activation induces metabolic...
   - DOI: 10.1016/j.stem.2022.02.011
   - 期刊: Cell Stem Cell
   - 状态: 需手动下载
   - 指南: PPAR_DELTA_DOWNLOAD.md
```

2. **JSON索引** (`index.json`)
```json
[
  {
    "title": "...",
    "doi": "10.1016/j.stem.2022.02.011",
    "journal": "Cell Stem Cell",
    "status": "manual",
    "guide": "PPAR_DELTA_DOWNLOAD.md",
    "timestamp": "2026-03-11"
  }
]
```

### 手动下载指引模板

对于无法自动下载的论文,生成详细的下载指引:

```markdown
# 论文下载指南

## 论文信息
- 标题: ...
- DOI: ...
- 期刊: ...

## 快速下载方法
1. 访问 Sci-Hub: https://sci-hub.tw
2. 输入 DOI: ...
3. 点击下载

## 备用方法
- 机构访问
- 联系作者
- 文献传递
```

## 最佳实践

### 1. 批量下载建议

```bash
# 推荐配置
python scripts/batch_downloader.py \
  -q "your topic" \
  -o ./my_papers \
  -m 20 \
  -w 5
```

参数说明:
- `-o`: 指定输出目录
- `-m`: 最多下载论文数
- `-w`: 并发线程数(不要太大,避免被封)

### 2. 付费文献处理

对于付费期刊论文:

1. 检查是否在PMC有开放获取版本
2. 如果没有,生成详细的手动下载指引
3. 提供多种获取方式建议
4. 保留论文元数据用于后续跟踪

### 3. 索引管理

定期检查索引文件:
```bash
# 查看所有未下载论文
grep "需手动下载" index.md

# 更新手动下载状态
# 编辑index.json,将status改为"downloaded"
```

## 注意事项

### ⚠️ 重要提醒

1. **版权尊重**:
   - 仅从官方免费渠道自动下载
   - 付费文献仅提供下载指引,不自动下载
   - 下载的论文仅供个人学术研究使用

2. **使用限制**:
   - 遵守网站使用条款
   - 不要过度请求(限制并发数)
   - 尊重速率限制

3. **推荐用途**:
   - ✅ 学术研究
   - ✅ 个人学习
   - ✅ 文献调研
   - ❌ 商业应用
   - ❌ 大规模批量下载
   - ❌ 公开分享付费内容

### 手动下载指引说明

生成的下载指引包含:

1. **Sci-Hub手动下载**
   - 可用的Sci-Hub镜像链接
   - 详细的操作步骤
   - 常见问题解决

2. **合法获取渠道**
   - 机构访问指南
   - 联系作者模板
   - 文献传递服务

3. **备用资源**
   - 开放获取检查
   - 其他数据库链接
   - 学术论坛求助

## 故障排除

### 常见问题

**Q: 无法下载某篇论文?**
A:
1. 检查是否是付费期刊
2. 查看 `papers/*.md` 中的下载指引
3. 尝试手动访问官方渠道

**Q: 下载的PDF无法打开?**
A:
1. 检查文件大小(应该>1KB)
2. 重新下载
3. 尝试其他下载源

**Q: 搜索不到相关论文?**
A:
1. 尝试不同的关键词
2. 使用更精确的标题
3. 直接输入DOI

**Q: 付费文献如何获取?**
A:
1. 查看生成的下载指引
2. 使用Sci-Hub手动下载
3. 联系作者索取
4. 使用机构访问权限

## 示例工作流

### 示例1: 下载arXiv论文

```bash
# 搜索并下载机器学习相关的arXiv论文
python scripts/batch_downloader.py -q "machine learning" -m 5
```

输出:
```
✅ Downloaded: arxiv_2103.00001.pdf
✅ Downloaded: arxiv_2103.00002.pdf
...
📄 Generated: index.md, index.json
```

### 示例2: 查询DOI信息

```bash
python scripts/doi_query.py 10.1016/j.stem.2022.02.011
```

输出:
```
Title: PPARdelta activation induces metabolic...
Authors: Nadeera M. Wickramasinghe, ...
Journal: Cell Stem Cell
DOI: 10.1016/j.stem.2022.02.011
```

### 示例3: 付费文献处理

```bash
python scripts/batch_downloader.py --doi 10.1056/NEJMoa1915872
```

输出:
```
ℹ️  Paper not available for auto-download
📄 Generated manual download guide: NEJM_DOWNLOAD.md
📄 Added to index with status: manual
```

## 更新日志

### v2.0 (2026-03-11)
- ✅ 移除Sci-Hub自动下载功能
- ✅ 添加PubMed/PMC下载支持
- ✅ 优先官方免费渠道
- ✅ 为付费文献生成详细的手动下载指引
- ✅ 改进错误提示和用户体验

### v1.0 (初始版本)
- arXiv批量下载
- 元数据提取
- 索引生成

---

**最后更新**: 2026-03-11
**版本**: v2.0
**状态**: ✅ 稳定可用
