# EduClaw 版本管理

## 关键信息（必须记住！）

| 项目 | 值 |
|------|-----|
| **slug** | `edu-claw`（不是 educlaw！）|
| **名称** | EduClaw - 主动式英语家教 |
| **当前版本** | 2.071（ClawHub） |
| **下次发布版本** | 2.24 |

## 版本历史

| 日期 | 版本 | 备注 |
|------|------|------|
| 2026-03-14 | 2.23 | 上次发布 |
| 2026-03-15 | 2.24 | 下次发布（待发布） |

## 发布命令模板

```bash
clawhub publish /root/.openclaw/workspace/educlaw-agents \
  --slug edu-claw \
  --name "EduClaw - 主动式英语家教" \
  --version "2.24" \
  --tags "education,english,math,multi-agent,tutoring"
```

## 注意事项

1. **版本号递增**：每次发布 +0.01（如 2.23 → 2.24）
2. **中文标签问题**：ClawHub 后端 Convex 不支持中文字段，标签只能用英文
3. **发布前确认**：先查当前版本，确认 slug 和版本号再发布
