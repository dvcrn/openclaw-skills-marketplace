---
name: semantic-memory-search
description: "为 OpenClaw Markdown 记忆文件添加向量驱动的语义搜索。使用 memsearch 库，支持混合搜索（稠密向量 + BM25），SHA-256 智能去重，本地 embedding 无需 API Key。"
homepage: https://github.com/sunnyhot/semantic-memory-search
---

# Semantic Memory Search

**为 OpenClaw 记忆文件添加语义搜索能力**

---

## 🎯 核心功能

### 语义搜索
- ✅ **向量驱动** - 通过语义而非关键词找到相关记忆
- ✅ **混合搜索** - 稠密向量 + BM25 全文检索 + RRF 重排序
- ✅ **智能去重** - SHA-256 内容哈希，未更改文件不重新嵌入

### 本地运行
- ✅ **无需 API Key** - 使用本地 embedding（all-MiniLM-L6-v2）
- ✅ **完全离线** - 所有数据存储在本地 Milvus Lite

### 自动同步
- ✅ **文件监视** - 记忆文件变更时自动重新索引
- ✅ **增量更新** - 只处理新增或修改的文件

---

## 📦 依赖

### 必需
- Python 3.10+
- memsearch 库

### 安装

```bash
pip3 install "memsearch[local]"
```

---

## 📅 使用方法

### 1. 索引记忆文件

```bash
# 使用本地 embedding（无需 API Key）
KMP_DUPLICATE_LIB_OK=TRUE ~/Library/Python/3.14/bin/memsearch index ~/.openclaw/workspace/memory/

# 或使用 OpenAI embedding（需要 API Key）
export OPENAI_API_KEY="your-key"
memsearch index ~/.openclaw/workspace/memory/
```

### 2. 语义搜索

```bash
# 搜索记忆
KMP_DUPLICATE_LIB_OK=TRUE ~/Library/Python/3.14/bin/memsearch search "我们选了什么缓存方案？"
```

### 3. 实时同步（可选）

```bash
# 启动文件监视器
KMP_DUPLICATE_LIB_OK=TRUE ~/Library/Python/3.14/bin/memsearch watch ~/.openclaw/workspace/memory/
```

---

## 🔧 配置

配置文件：`~/.memsearch/config.toml`

### 本地 Embedding（推荐）

```toml
[milvus]
uri = "~/.memsearch/milvus.db"

[embedding]
provider = "local"
model = "all-MiniLM-L6-v2"

[search]
top_k = 5
```

### OpenAI Embedding

```toml
[milvus]
uri = "~/.memsearch/milvus.db"

[embedding]
provider = "openai"
model = "text-embedding-3-small"

[search]
top_k = 5
```

---

## 📊 搜索示例

### 示例查询

| 查询 | 说明 |
|------|------|
| "我们选了什么缓存方案？" | 即使没有"缓存"关键词也能找到 |
| "Discord 频道重组" | 找到所有相关决策和过程 |
| "播客制作流程" | 找到播客相关的所有记忆 |
| "财报跟踪配置" | 找到财报系统的配置历史 |

### 搜索结果格式

```
--- Result 1 (score: 0.0320) ---
Source: /path/to/memory.md
Heading: 相关标题
# 内容摘要...

--- Result 2 (score: 0.0318) ---
...
```

---

## 🔗 相关链接

- [memsearch GitHub](https://github.com/zilliztech/memsearch)
- [memsearch 文档](https://zilliztech.github.io/memsearch/)
- [Milvus](https://milvus.io/)

---

## 📝 更新日志

### v1.0.0 (2026-03-14)
- ✅ 初始版本
- ✅ 本地 embedding 支持
- ✅ 语义搜索功能
- ✅ OpenClaw 集成

---

## 📄 许可证

MIT License
