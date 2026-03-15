# Knowledge Connector - 知识连接器

智能知识管理工具，从文档和对话中提取概念，构建知识图谱，支持智能查询和推荐。

## 快速开始

### 安装

```bash
# 通过 ClawHub 安装
clawhub install knowledge-connector

# 或全局安装
npm install -g ~/.openclaw/workspace/skills/knowledge-connector
```

### 使用

```bash
# 提取概念
kc extract -t "人工智能是机器学习的基础"

# 建立关联
kc connect --from "人工智能" --to "机器学习" --relation "包含"

# 查询知识
kc query "人工智能"

# 可视化图谱
kc visualize --format html --output graph.html

# 查看统计
kc stats
```

## 功能

- ✅ 知识提取：从文本/文件中自动提取概念
- ✅ 关系建立：自动/手动建立概念关联
- ✅ 知识图谱：可视化展示知识结构
- ✅ 智能查询：支持关键词和自然语言查询
- ✅ 知识推荐：基于关联性推荐相关知识

## CLI 命令

| 命令 | 说明 |
|------|------|
| `extract` | 从文本或文件提取概念 |
| `connect` | 建立概念间的关联 |
| `query` | 查询知识库 |
| `visualize` | 生成知识图谱可视化 |
| `stats` | 显示统计信息 |
| `export` | 导出知识库 |
| `import` | 导入知识库 |
| `recommend` | 推荐相关知识 |

## 示例

```bash
# 1. 从文件提取
kc extract -f document.txt --save

# 2. 自动建立关联
kc connect --auto

# 3. 查询相关概念
kc query --concept "深度学习" --related

# 4. 生成可视化
kc visualize --format html --output knowledge.html
```

## 许可证

MIT License
