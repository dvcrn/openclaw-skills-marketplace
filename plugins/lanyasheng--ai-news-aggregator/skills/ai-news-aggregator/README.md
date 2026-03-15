# AI News Aggregator

高性能 AI 新闻聚合工具，专为 OpenClaw/AI Agent 设计。并发抓取 70+ RSS 源，支持缓存和质量评分。

## 特性

- ⚡ **高性能**: 10 线程并发，70 源 12 秒内完成
- 💾 **智能缓存**: ETag/Last-Modified 缓存，重复运行秒级完成
- 📊 **70+ RSS 源**: 覆盖 OpenAI、Anthropic、Google、Hugging Face 等
- 🔬 **arXiv 集成**: 自动抓取 AI/ML/NLP 最新论文
- 📈 **GitHub Trending**: 追踪热门 AI 项目
- 🧪 **完整测试**: 26 个单元测试覆盖

## 安装

```bash
# 克隆仓库
git clone https://github.com/yourusername/ai-news-aggregator.git
cd ai-news-aggregator/scripts

# 安装依赖（可选，纯标准库）
pip install feedparser  # 提供更好的 RSS 解析
```

## 使用

### 快速开始

```bash
# 抓取所有源（默认 70 个 RSS 源）
python3 rss_aggregator.py --category all --limit 10 --json

# 抓取特定分类
python3 rss_aggregator.py --category company --limit 5
python3 rss_aggregator.py --category papers --limit 10

# 抓取 arXiv 论文
python3 arxiv_papers.py --limit 5 --top 10 --json
```

### 分类说明

| 分类 | 源数 | 说明 |
|------|------|------|
| company | 14 | OpenAI, Anthropic, Google, Meta, NVIDIA 等官方博客 |
| papers | 4 | arXiv AI/ML/NLP/CV |
| media | 15 | MIT Tech Review, TechCrunch, Wired 等媒体 |
| newsletter | 12 | Simon Willison, Lilian Weng 等专家博客 |
| community | 10 | HN, GitHub, Product Hunt |
| cn_media | 5 | 机器之心, 36氪, 少数派 等中文媒体 |

## 性能对比

| 版本 | 70 源耗时 | 缓存后 |
|------|----------|--------|
| 原版 (顺序) | 超时 (>120s) | N/A |
| 优化版 (并发) | 12.5s | 2.3s |

**9-10 倍性能提升**

## 配置

编辑 `scripts/rss_sources.json` 添加/删除源：

```json
{
  "name": "OpenAI Blog",
  "url": "https://openai.com/blog/rss.xml",
  "category": "company"
}
```

## 运行测试

```bash
cd scripts
python3 -m unittest test_rss_aggregator -v
```

## 架构

```
rss_aggregator.py
├── load_sources()      # 加载 RSS 源配置
├── fetch_rss_concurrent()  # 并发抓取（10 线程）
├── parse_rss()         # 解析 RSS/Atom
└── save_cache()        # ETag/Last-Modified 缓存

arxiv_papers.py
├── fetch_arxiv()       # arXiv API 查询
├── parse_arxiv()       # Atom 解析
└── 12 个搜索查询主题
```

## 优化点

1. **并发抓取**: ThreadPoolExecutor(10) 替代顺序抓取
2. **HTTP 缓存**: 使用 ETag/If-None-Match 避免重复下载
3. **快速超时**: 15 秒超时，快速失败
4. **缓存持久化**: 1 小时 TTL，重复运行秒级

## 许可

MIT License - 详见 LICENSE 文件

## 致谢

- 源配置参考: [tech-news-digest](https://github.com/draco-agent/tech-news-digest)
- 架构设计: OpenClaw 社区
