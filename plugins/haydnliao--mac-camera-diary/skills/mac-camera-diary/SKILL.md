---
name: mac-camera-diary
description: "Mac摄像头日记技能。定时用摄像头拍照并用 AI 夸奖照片中的人，晚上生成当日总结，次日自动清理照片。上下班时间、午休、加班、照片路径、拍照间隔、模型等均可配置。当用户提到\"摄像头日记\"、\"拍照分析\"、\"每天拍照夸奖\"、\"配置摄像头日记\"时触发。"
---

# Mac Camera Diary

定时用 Mac 摄像头拍照 → AI 夸奖 → 晚上汇总 → 次日清理。所有参数通过 `scripts/config.sh` 统一配置。

## 快速配置

编辑 `scripts/config.sh`，修改需要的变量，其余保持默认即可：

```bash
# 作息时间
WORK_START="09:30"       # 上班（开始拍照）
LUNCH_START="12:30"      # 午休开始
LUNCH_END="14:00"        # 午休结束
WORK_END="22:00"         # 下班（22:00 整点仍拍最后一张）

# 工作日
WORK_DAYS="1,2,3,4,5"   # 1=周一…7=周日，逗号分隔；默认周一到周五

# 任务时间
SUMMARY_TIME="22:05"     # 夜间总结
CLEANUP_TIME="00:00"     # 照片清理

# 拍照
SNAP_INTERVAL=15         # 间隔（分钟）
CAMERA_DEVICE=""         # 摄像头设备名（空=默认）

# 存储
DIARY_DIR=~/openclaw-camera-diary
KEEP_PHOTOS_DAYS=0       # 0=次日删，N=保留N天

# AI
MODEL="claude-sonnet-4-5-20250929"  # 需支持视觉输入的模型
BASE_URL="https://api.openai.com/v1"  # API 端点（OpenAI 兼容格式）

# 字数
PRAISE_MAX_WORDS=100
SUMMARY_MAX_WORDS=200

# 飞书推送
FEISHU_TARGET="private"  # private=私信，group=群组
```

## 目录结构

```
~/openclaw-camera-diary/
├── YYYY-MM-DD/
│   ├── HH-MM.jpg     ← 照片（按 KEEP_PHOTOS_DAYS 清理）
│   └── log.md        ← 当日分析记录（长期保留）
└── summary.md        ← 每日总结汇总（长期保留）
```

## 工作流

| 脚本 | 触发时机 | 行为 |
|------|---------|------|
| `snap_and_praise.sh` | 工作时间每 N 分钟 | 拍照 → AI 夸奖 → 追加 log.md |
| `nightly_summary.sh` | `SUMMARY_TIME` | 读 log → 生成总结 → 推送飞书 |
| `cleanup.sh` | `CLEANUP_TIME` | 删除过期照片（保留日志） |

`snap_and_praise.sh` 内置时间段判断：午休和非工作时间自动跳过，无需为每个时间段单独配置 cron。

## Cron 配置

见 `references/cron_setup.md`，包含根据 `config.sh` 中作息时间生成 cron 表达式的说明。

## 依赖

```bash
brew install imagesnap
imagesnap -l   # 查看可用摄像头（设置 CAMERA_DEVICE 时用）
```
