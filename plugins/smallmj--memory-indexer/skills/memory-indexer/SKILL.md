---
name: memory-indexer
description: "短期记忆关键词索引工具 - 自动提取关键词、建立索引、搜索记忆，支持关联发现、时间线视图、重要记忆标记等功能"
homepage: https://github.com/openclaw/memory-indexer
---

# Memory Indexer

短期记忆关键词索引工具，为 AI Agent 提供长期记忆能力。

## 核心功能

1. **自动关键词提取** - 使用 jieba 中文分词自动提取记忆关键词
2. **索引系统** - 建立关键词 → 记忆文件 映射，支持快速检索
3. **多关键词搜索** - 支持 AND/OR 模式精确搜索
4. **关联发现** - 自动发现经常一起出现的记忆
5. **时间线视图** - 按时间顺序展示记忆
6. **主动提醒** - 根据关键词检索相关旧记忆
7. **记忆摘要** - 统计记忆概况
8. **重要记忆标记** - 标记和查看重要记忆
9. **增量同步** - 自动同步外部 memory/ 目录
10. **失效清理** - 自动清理已删除记忆的索引

## 安装

```bash
# 克隆到 skills 目录
git clone https://github.com/your-repo/memory-indexer ~/.openclaw/workspace/skills/memory-indexer

# 确保 jieba 已安装
pip install jieba
```

## 使用方法

```bash
cd ~/.openclaw/workspace
python -m venv .venv
source .venv/bin/activate
pip install jieba

# 或使用 uv
uv pip install jieba
```

### 命令列表

| 命令 | 功能 | 示例 |
|------|------|------|
| `add` | 添加记忆 | `add "今天学习了 Python"` |
| `search` | 搜索记忆 | `search "Python"` |
| `search --and` | AND 搜索 | `search "Python AI" --and` |
| `sync` | 同步外部目录 | `sync` |
| `cleanup` | 清理失效索引 | `cleanup` |
| `related` | 关联发现 | `related` |
| `timeline` | 时间线视图 | `timeline` |
| `recall` | 主动提醒 | `recall "Python"` |
| `summary` | 记忆摘要 | `summary` |
| `star` | 标记重要 | `star 20260312.md` |
| `stars` | 查看重要记忆 | `stars` |
| `status` | 查看状态 | `status` |

## 配置

脚本会自动在 `~/.openclaw/workspace/memory-index/` 目录下创建：
- `index.json` - 关键词索引
- `sync-state.json` - 同步状态
- `stars.json` - 重要记忆标记

## 集成建议

### 心跳自动同步

在 HEARTBEAT.md 中添加：
```markdown
### 记忆索引同步
- 命令：`cd ~/.openclaw/workspace && python skills/memory-indexer/memory-indexer.py sync`
- 频率：每次心跳
```

### Cron 备份

```bash
crontab -e
# 添加：每天 6 点自动同步
0 6 * * * cd /home/user/.openclaw/workspace && python skills/memory-indexer/memory-indexer.py sync
```

## 与 OpenClaw 集成

1. 克隆到 workspace skills 目录
2. 在 MEMORY.md 中添加规则：保存记忆时自动调用 indexer
3. 使用 `uv run python skills/memory-indexer/memory-indexer.py` 调用

## 依赖

- Python 3.8+
- jieba (中文分词)

## License

MIT
