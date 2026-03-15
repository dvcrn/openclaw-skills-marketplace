---
name: trip-planner
description: "企业差旅行程规划：搜索真实航班/高铁班次、查询酒店、智能编排多城市行程。需要后端 Trip Planner 服务运行。"
homepage: https://github.com/hezhihao/trip-planner-langgraph
---

# Trip Planner

搜索真实航班/高铁班次、查询酒店价格、智能编排多城市差旅行程。

## When to Use

Activate this skill when the user:
- 需要规划出差/差旅行程
- 搜索航班、高铁、火车票
- 查询或预订酒店
- 提到出差、商旅、行程安排
- 例如："明天去上海出差"、"帮我查北京到深圳的航班"、"找一下杭州的酒店"

## When NOT to Use

- 查询单个航班号详情 → 使用 `flightsearchdetail` skill
- 非差旅的旅游攻略 → 直接对话即可

## Setup

需要 Trip Planner 后端服务运行，设置环境变量：

```bash
# 在 openclaw.json 中配置，或设置环境变量
TRIP_PLANNER_URL=http://localhost:8900   # 服务地址（必需）
TRIP_PLANNER_USER_ID=your_user_id        # 可选，默认使用测试账号
TRIP_PLANNER_TOKEN=your_token            # 可选，默认使用测试 token
```

或在 `~/.openclaw/openclaw.json` 中设置：
```json
{
  "skills": {
    "trip-planner": {
      "env": {
        "TRIP_PLANNER_URL": "http://localhost:8900"
      }
    }
  }
}
```

## How to Use

```bash
python3 {baseDir}/scripts/trip_chat.py "<用户消息>" [当前城市] [session_id]
```

| 参数 | 位置 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| 用户消息 | 1 | 是 | - | 用户的自然语言输入 |
| 当前城市 | 2 | 否 | 北京市 | 用户当前所在城市 |
| session_id | 3 | 否 | 自动生成 | 多轮对话保持同一 session_id |

**必须使用 exec 的 timeout=120**，脚本正常执行需要 30-90 秒（后端搜索真实航班/酒店数据）。

## Examples

单轮对话：
```bash
python3 {baseDir}/scripts/trip_chat.py "明天从北京去上海出差" "北京市"
```

多轮对话：
```bash
# 第一轮
python3 {baseDir}/scripts/trip_chat.py "后天去深圳出差两天" "北京市" "session-abc"
# 第二轮
python3 {baseDir}/scripts/trip_chat.py "帮我换成高铁" "北京市" "session-abc"
```

## Output

脚本输出 `[进度]` 行（心跳 + 工具调用进度），最后一行是 JSON 结果：

```json
{
  "response": "以下是您的行程方案：\n📅 2026-03-14...",
  "session_id": "xxx",
  "data": { "flight_train_trips": [...], "hotel_meal_result": [...] }
}
```

将 `response` 字段内容直接回复给用户。

## Notes

- 脚本每 5 秒输出心跳，看到心跳说明正在正常工作，不要 kill 进程
- 零外部依赖，仅使用 Python 标准库
- 多轮对话保持同一 session_id 即可
