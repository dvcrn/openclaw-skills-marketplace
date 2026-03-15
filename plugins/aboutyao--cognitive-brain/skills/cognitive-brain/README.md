# 🧠 Cognitive Brain

> AI Agent 的记忆与认知系统
> 
> **Version: 2.6.3**

## 特性

- 📝 **记忆编码** - 智能存储对话、事件、知识
- 🔍 **语义检索** - 向量相似度 + 关键词混合搜索
- 🔗 **联想网络** - 自动构建概念关联
- 🤔 **自我反思** - 定期反思、发现模式
- 🎯 **用户建模** - 学习用户偏好和习惯
- 🔮 **预测引擎** - 预测用户需求，预加载记忆
- 🌊 **自由思考** - 模拟意识流，记录思绪
- 📊 **可视化** - 知识图谱、时间线、摘要
- 📚 **自动摘要** - 长内容智能提炼

## 快速开始

### 安装

```bash
npm install cognitive-brain
```

### 配置

编辑 `config.json`:

```json
{
  "storage": {
    "primary": {
      "host": "localhost",
      "port": 5432,
      "database": "cognitive_brain",
      "user": "postgres",
      "password": "your_password"
    }
  }
}
```

### 使用

```bash
# 编码记忆
node scripts/brain.cjs encode "今天学习了 AI 记忆系统"

# 检索记忆
node scripts/brain.cjs recall "学习"

# 导出数据
node scripts/brain.cjs export md

# 健康检查
node scripts/brain.cjs health_check

# 自由思考
node scripts/free_think.cjs think

# 知识图谱可视化
node scripts/visualize.cjs all

# 记忆时间线
node scripts/timeline.cjs recent 7

# 自动摘要
node scripts/summarize.cjs batch

## 架构

```
┌─────────────────────────────────────────────┐
│              Cognitive Brain                │
├─────────────────────────────────────────────┤
│  ┌─────────┐  ┌─────────┐  ┌─────────────┐  │
│  │ Encode  │  │ Recall  │  │  Reflect    │  │
│  └────┬────┘  └────┬────┘  └──────┬──────┘  │
│       │            │               │         │
│  ┌────▼────────────▼───────────────▼──────┐ │
│  │           PostgreSQL + pgvector        │ │
│  └────────────────────────────────────────┘ │
│       │                                      │
│  ┌────▼────────────────────────────────────┐│
│  │   Embedding (sentence-transformers)     ││
│  └─────────────────────────────────────────┘│
└─────────────────────────────────────────────┘
```

## 核心模块

| 模块 | 功能 | 文件 |
|------|------|------|
| 记忆编码 | 存储 + 实体提取 + 情感分析 | encode.cjs |
| 记忆检索 | 向量搜索 + 关键词过滤 | recall.cjs |
| 自我反思 | 模式发现 + 洞察生成 | reflect.cjs |
| 自由思考 | 意识流 + 思绪记录 | free_think.cjs |
| 联想网络 | 概念关联 + 共现分析 | associate.cjs |
| 用户建模 | 偏好学习 + 行为预测 | user_model.cjs |
| 预测引擎 | 需求预测 + 预加载 | prediction.cjs |
| 自动摘要 | 长内容提炼 | summarize.cjs |
| 可视化 | 知识图谱 + 时间线 | visualize.cjs |

## 定时任务

系统自动配置以下 cron 任务：

| 时间 | 任务 | 说明 |
|------|------|------|
| 每天 03:00 | forget | 清理不重要记忆 |
| 每天 04:00 | reflect | 自我反思 |
| 每天 05:00 | autolearn | 自主学习 |

## 依赖

- PostgreSQL 14+ (with pgvector)
- Node.js 18+
- Python 3.8+ (for embeddings)

## 版本历史

查看 [CHANGELOG.md](./CHANGELOG.md)

## 许可证

MIT
