---
name: social-scheduler
description: "社交媒体内容排程与运营管理工具。支持多平台排程、本周概览、内容模板库、发布效果分析、批量添加、复制计划。Content calendar and social media scheduler with weekly overview, content templates by niche, publishing analytics, batch operations, and duplication. 内容日历、发布计划、运营管理、数据追踪、本周概览、模板库、效果分析、批量排程。"
---

# Social Scheduler

社交媒体内容排程管理工具，数据存储在 `~/.social-scheduler/` 目录。

## 使用方式

所有操作通过 `scripts/schedule.sh` 执行：

```bash
SCRIPT="$(dirname "$0")/../skills/social-scheduler/scripts/schedule.sh"
```

## 命令

| 命令 | 说明 |
|------|------|
| `schedule.sh add "内容" --platform twitter,xhs --date "2026-03-10 09:00"` | 添加排程 |
| `schedule.sh list [--date today\|tomorrow\|week]` | 查看排程 |
| `schedule.sh edit <id> "新内容"` | 编辑排程内容 |
| `schedule.sh delete <id>` | 删除排程 |
| `schedule.sh status` | 今日发布状态总览 |
| `schedule.sh calendar [--month 3]` | 月度内容日历 |
| `schedule.sh stats` | 发布统计 |
| `schedule.sh mark-done <id>` | 标记为已发布 |
| `schedule.sh export [--format md\|json]` | 导出排程数据 |
| `schedule.sh week` | 本周概览（ASCII日历表+今明详情） |
| `schedule.sh template "赛道"` | 内容模板库（美妆/科技/美食/健身等一周计划） |
| `schedule.sh analytics` | 发布效果分析（完成率/平台分布/最佳时段/洞察） |
| `schedule.sh duplicate <id>` | 复制已有排程 |
| `schedule.sh batch-add "主题1,主题2" "平台" [--start "日期" --interval N]` | 批量添加排程 |
| `schedule.sh help` | 显示帮助信息 |

## 平台标签

`twitter`, `xhs`(小红书), `weibo`(微博), `bilibili`(B站), `binance-square`, `blog`

## 注意事项

- 所有时间默认使用本地时区
- ID 为 8 位随机字符串，自动生成
- 数据以 JSON 格式存储在 `~/.social-scheduler/schedules.json`
