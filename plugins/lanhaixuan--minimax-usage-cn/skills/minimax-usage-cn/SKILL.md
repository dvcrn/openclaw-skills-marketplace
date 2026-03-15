---
name: minimax-usage-cn
description: "Monitor Minimax Coding Plan usage to stay within API limits. Fetches current usage stats and provides status alerts."
---

# Minimax Usage (国内版)

Monitor Minimax Coding Plan usage to stay within API limits.

Designed for:

- Check current usage quota
- Monitor 5-hour sliding window
- Get usage alerts before hitting limits

---

## When to Use This Skill

Use this skill whenever:

- User asks to check Minimax usage
- Before running large AI tasks
- When approaching limit warnings

---

## API Specification

Endpoint:

GET https://www.minimaxi.com/v1/api/openplatform/coding_plan/remains

Headers:

Authorization: Bearer <MINIMAX_API_KEY>
Content-Type: application/json

**注意：** 此接口仅适用于国内版 `www.minimaxi.com`。

---

## Response Fields

| 字段 | 含义 |
|------|------|
| `remains_time` | 订阅周期剩余时间 (秒)，和5小时窗口无关 |
| `current_interval_total_count` | 周期总配额 (1500) |
| `current_interval_usage_count` | **剩余用量** |
| `model_name` | 模型名称 (MiniMax-M2/M2.1/M2.5) |
| `start_time` / `end_time` | 当前5小时滑动窗口起止时间 (毫秒时间戳) |

**计算公式：**
- 已用 = `current_interval_total_count` - `current_interval_usage_count`
- 使用率 = 已用 / 总配额 * 100%

---

## Output Format

```
🔍 Checking Minimax Coding Plan usage...
✅ Usage retrieved successfully:

📊 Coding Plan Status (MiniMax-M2.5):
   Used:      102 / 1500 prompts (6%)
   Remaining: 1398 prompts
   Window:    20:00 - 00:00 (UTC+8)
   Resets in: 约 1h 13m

💚 GREEN: 6% used. Plenty of buffer.
```

---

## Status Thresholds

| 使用率 | 状态 | 提示 |
|--------|------|------|
| 0-60% | 💚 GREEN | Plenty of buffer |
| 60-75% | ⚠️ CAUTION | Target is 60% |
| 75-90% | ⚠️ WARNING | Approaching limit |
| >90% | 🚨 CRITICAL | Stop all AI work |

---

## Notes

- 需要使用 Coding Plan API Key, 专用于 Coding Plan 套餐
- Coding Plan 用量每5小时重置
- 一个 prompt 约等于 15 次模型调用
- `current_interval_usage_count` 是**剩余用量**，不是已用量！
- 窗口时间为 UTC+8 时区

---

## Error Handling

Common API error codes (status_code):

| 错误码 | 含义 | 解决方法 |
|--------|------|----------|
| 2013 | 参数错误 | 请检查请求参数 |
| 1004 | 未授权/Token 不匹配 | 请检查 API Key |
| 2049 | 无效的 API Key | 请检查 API Key |
| 1002 | 请求频率超限 | 请稍后再试 |
| 2056 | 超出 Coding Plan 资源限制 | 请等待下一个时间段资源释放后，再次尝试 |
| 1000/1024/1033 | 系统错误/内部错误 | 请稍后再试 |
