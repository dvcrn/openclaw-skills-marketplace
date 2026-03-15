---
name: memory-compact
description: "每日记忆自动压缩备份和关键点提取，每天早上 6:30 运行"
---

# Memory Compact Skill

## 功能

自动备份每日对话记录，提取关键点并写入 MEMORY.md，然后发送飞书通知。

## 定时任务

每天早上 6:30 北京时间自动运行（通过 cron 配置）

## 使用方法

### 手动运行

```bash
python3 /root/.openclaw/workspace/scripts/memory_backup.py
```

### 查看日志

```bash
tail -f /root/.openclaw/workspace/scripts/memory_backup.log
```

### 查看备份文件

```bash
ls -la ~/.openclaw/workspace/backup/memory/
```

### 查看提取结果

```bash
cat ~/.openclaw/workspace/MEMORY.md
```

## 工作流程

1. 读取 `memory/YYYY-MM-DD.md`（最新的一天）
2. 提取 2-3 个关键点（基于关键词匹配）
3. 写入 `MEMORY.md`（极致简洁格式）
4. 移动原文件到 `backup/memory/`
5. 发送飞书通知给用户

## 输出格式

```markdown
# MEMORY - 长期记忆

## 2026-03-11
1. 用户决定采用方案二：自己写脚本处理每日记忆备份
2. 用户决定将开发过程中的中间结果备份到 backup 目录
3. 最终决定：自己编写脚本，每天早上 6:30 运行
```

## 飞书通知

```
📝 **每日记忆备份完成**

**昨日记忆文件已处理并备份**

📌 **提取的关键点**:
- 用户决定采用方案二
- 用户决定将开发过程中的中间结果备份
- 最终决定：自己编写脚本

📁 **备份文件**: `/root/.openclaw/workspace/backup/memory/2026-03-11.md`
```

## 配置

### 修改提取关键词

编辑 `/root/.openclaw/workspace/scripts/memory_backup.py` 中的 `extract_key_points()` 函数：

```python
keywords = ["决定", "喜欢", "讨厌", "记住", "重要", "计划", "目标"]
```

可以添加或修改关键词，根据实际对话内容调整。

### 修改飞书通知

脚本会自动通过 OpenClaw 的消息功能发送飞书通知，无需额外配置。

## 注意事项

- 脚本使用规则提取关键词，如需更精准提取，可替换为 LLM 调用
- 备份文件不会被删除，保留在 `backup/memory/` 目录
- 定时任务需要 cron 服务运行
