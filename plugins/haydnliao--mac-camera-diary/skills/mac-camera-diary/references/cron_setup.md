# Cron 任务配置

根据 `config.sh` 中的 `WORK_START`、`LUNCH_START`、`LUNCH_END`、`WORK_END`、`SNAP_INTERVAL` 生成 cron 表达式。

**当前默认值：** 09:30 上班 / 12:30–14:00 午休 / 22:00 下班 / 15 分钟间隔

## 设计原则

`snap_and_praise.sh` 已内置时间段判断，会自动跳过午休和非工作时间，因此 **cron 只需覆盖整体工作时间段**，不必精确切割午休边界。

建议用一条宽松的 cron 覆盖全天工作小时，脚本自己判断是否执行。

## 当前作息对应的 cron

### 拍照任务（09:30–22:00，每15分钟，含午休自动跳过）

上午段（09:30 开始，整点+每刻）：
```json
{
  "name": "camera-diary-snap-morning",
  "schedule": {"kind": "cron", "expr": "30,45 9 * * 1-5", "tz": "Asia/Shanghai"},
  "payload": {
    "kind": "agentTurn",
    "message": "执行摄像头日记拍照任务：运行 ~/.openclaw/workspace/skills/mac-camera-diary/scripts/snap_and_praise.sh\nCurrent time: {{now}}\nReturn your summary as plain text."
  },
  "sessionTarget": "isolated"
}
```

全天工作时段（10:00–21:45，每15分钟，脚本自动跳过午休）：
```json
{
  "name": "camera-diary-snap",
  "schedule": {"kind": "cron", "expr": "0,15,30,45 10,11,12,13,14,15,16,17,18,19,20,21 * * 1-5", "tz": "Asia/Shanghai"},
  "payload": {
    "kind": "agentTurn",
    "message": "执行摄像头日记拍照任务：运行 ~/.openclaw/workspace/skills/mac-camera-diary/scripts/snap_and_praise.sh\nCurrent time: {{now}}\nReturn your summary as plain text."
  },
  "sessionTarget": "isolated"
}
```

22:00 整点（最后一次）：
```json
{
  "name": "camera-diary-snap-last",
  "schedule": {"kind": "cron", "expr": "0 22 * * 1-5", "tz": "Asia/Shanghai"},
  "payload": {
    "kind": "agentTurn",
    "message": "执行摄像头日记拍照任务：运行 ~/.openclaw/workspace/skills/mac-camera-diary/scripts/snap_and_praise.sh\nCurrent time: {{now}}\nReturn your summary as plain text."
  },
  "sessionTarget": "isolated"
}
```

### 夜间总结（22:05）

```json
{
  "name": "camera-diary-summary",
  "schedule": {"kind": "cron", "expr": "5 22 * * 1-5", "tz": "Asia/Shanghai"},
  "payload": {
    "kind": "agentTurn",
    "message": "执行摄像头日记夜间总结：运行 ~/.openclaw/workspace/skills/mac-camera-diary/scripts/nightly_summary.sh，将结果通过飞书发送给用户（私信）。"
  },
  "sessionTarget": "isolated",
  "delivery": {"mode": "announce"}
}
```

### 清理照片（00:00）

```json
{
  "name": "camera-diary-cleanup",
  "schedule": {"kind": "cron", "expr": "0 0 * * *", "tz": "Asia/Shanghai"},
  "payload": {
    "kind": "agentTurn",
    "message": "执行摄像头日记清理任务：运行 ~/.openclaw/workspace/skills/mac-camera-diary/scripts/cleanup.sh"
  },
  "sessionTarget": "isolated"
}
```

## 修改作息时间后的更新步骤

1. 修改 `scripts/config.sh` 中的时间变量
2. 根据新时间重新计算 cron 表达式并更新 OpenClaw cron 配置
3. 脚本的时间段判断会自动同步（因为它读取 config.sh）

## 周末设置

上面的 cron 用了 `1-5`（周一至周五）。如需周末也拍，改为 `*` 即可。
