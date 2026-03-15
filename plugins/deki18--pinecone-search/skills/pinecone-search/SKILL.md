---
name: pinecone-search
description: "Pinecone vector search tool for searching local knowledge base"
---

# Pinecone Search

Pinecone 向量搜索工具，用于搜索本地知识库中的规范、标准、施工等文档。

## 安装

```bash
pip install openai pinecone-client
cp config.example.env .env
# 编辑 .env 文件，填入你的 API Key
```

## 配置

编辑 `.env` 文件：

```env
PINECONE_API_KEY=your_pinecone_api_key
EMBEDDING_API_KEY=your_embedding_api_key
EMBEDDING_BASE_URL=https://api.openai.com/v1
EMBEDDING_MODEL=text-embedding-3-large
INDEX_NAME=your-index-name
NAMESPACE=
```

## 使用

```bash
python search_tool.py "查询内容"
python search_tool.py "查询内容" --top-k 5
```

## 触发关键词

- 规范、标准
- 查询资料、知识库

## 示例

```bash
python search_tool.py "混凝土浇筑标准是什么？"
```

输出：

```
🔍 正在搜索: 混凝土浇筑标准是什么？

============================================================
【结果 #1】
匹配度: 0.8934
来源: 施工规范_2024.pdf
内容:
  混凝土浇筑应符合以下标准...
------------------------------------------------------------
```
