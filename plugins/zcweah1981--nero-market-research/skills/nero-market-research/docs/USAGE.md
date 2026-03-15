# 使用手册

本文档详细说明如何使用 Nero Market Research。

---

## 🚀 快速开始

### 启动系统

```bash
nero start
```

**输出**：
```
✅ Nero 系统已启动
```

---

### 查看状态

```bash
nero status
```

**输出**：
```
✅ Nero 系统运行中

[INFO] 2026-03-10 08:00 - GitHub Miner: 找到 15 个痛点
[INFO] 2026-03-10 09:00 - ProductHunt Miner: 找到 10 个痛点
...
```

---

### 查看日志

```bash
# 实时日志
nero logs

# 今日日志
nero logs-today
```

---

## 📊 日常工作流程

### 自动执行（推荐）

系统启动后会自动：
1. **每小时**：执行一个 Miner（GitHub/Reddit/Twitter等）
2. **21:00**：生成每日报告
3. **周一 02:00**：生成每周 MVP
4. **周一 04:00**：清理旧数据

你只需要每天查看 Notion 商机池即可。

---

### 手动执行

```bash
# 立即执行一次数据收集
nero run

# 手动同步到 Notion
nero sync

# 生成今日报告
nero report
```

---

## 📈 查看数据

### Notion 商机池

1. 打开你的 Notion 工作区
2. 找到 "Opportunities" 数据库
3. 查看高分机会

**字段说明**：

| 字段 | 说明 |
|------|------|
| **Title** | 商机名称 |
| **Demand Score** | 需求评分（0-100）|
| **Priority** | 优先级 |
| **Playbook Tag** | 商业打法 |
| **Demand Content** | 英文原文 |
| **Trans Content** | 中文翻译 |
| **PM 解读** | PM专业解读 |

---

### 每日报告

1. 打开 "Daily Reports" 数据库
2. 查看当天的报告
3. 点击 "Opportunities" 查看关联的机会

---

## 🎯 最佳实践

### 1. 每日检查（5分钟）

**早上**：
```bash
# 查看昨日数据
nero stats
```

**Notion**：
- 查看 80+ 分的机会
- 标记感兴趣的机会为 "Research"

---

### 2. 每周回顾（30分钟）

**周一**：
- 查看每周 MVP 报告
- 选择 1-2 个机会深入研究
- 标记为 "Building"

---

### 3. 数据清理（每月）

```bash
# 清理旧数据
nero cleanup
```

---

## 🔧 高级功能

### 1. 自定义关键词

编辑 `config/keywords.json`：

```json
{
  "pain_keywords": {
    "tier_1_golden": [
      "I wish there was",
      "Looking for a tool",
      "你的自定义关键词"
    ]
  }
}
```

**重启生效**：
```bash
nero restart
```

---

### 2. 调整评分阈值

编辑 `config.json`：

```json
{
  "scoring": {
    "min_score_to_keep": 60  // 提高到 60 分
  }
}
```

**效果**：只保留 60+ 分的机会

---

### 3. 添加新的数据源

编辑 `config/other_platforms.json`：

```json
{
  "platforms": [
    {
      "name": "Your Platform",
      "url": "https://example.com",
      "search_pattern": "search?q={keyword}"
    }
  ]
}
```

---

## 🐛 常见问题

### Q: 为什么没有数据？

**检查**：
```bash
nero status
```

**可能原因**：
1. SearXNG 未运行
2. 网络连接问题
3. 关键词不匹配

**解决**：
```bash
# 测试 SearXNG
curl http://localhost:8080/search?q=test&format=json

# 查看详细日志
nero logs
```

---

### Q: 如何提高数据质量？

**方法 1**: 调整相关性阈值

编辑 `config.json`：
```json
{
  "quality_filter": {
    "min_relevance_score": 50  // 提高到 50
  }
}
```

**方法 2**: 添加更多关键词

编辑 `config/keywords.json`

---

### Q: 如何备份配置？

```bash
# 备份配置
cp -r ~/.nero-market-research/config ~/nero-config-backup

# 备份数据
cp -r ~/.nero-market-research/memory ~/nero-data-backup
```

---

## 📚 进阶技巧

### 1. 使用 Notion 视图

创建自定义视图：
- **高优先级看板**：筛选 Priority = "🚀 立即行动"
- **按打法分组**：Group by Playbook Tag
- **按状态追踪**：Group by Status

---

### 2. 设置 Telegram 通知

编辑 `config.json`：

```json
{
  "telegram": {
    "enabled": true,
    "bot_token": "your_bot_token",
    "chat_id": "your_chat_id"
  }
}
```

**效果**：80+ 分的机会自动推送到 Telegram

---

### 3. 导出数据

```bash
# 导出 JSON
cat ~/.nero-market-research/memory/research/opportunities/*.json > opportunities.json

# 导出 CSV（需要 jq）
cat opportunities.json | jq -r '.[] | [.title, .score, .url] | @csv' > opportunities.csv
```

---

## 📖 相关文档

- [安装指南](SETUP_GUIDE.md)
- [配置说明](CONFIGURATION.md)
- [API参考](API_REFERENCE.md)
