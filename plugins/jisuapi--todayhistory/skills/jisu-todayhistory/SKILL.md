---
name: jisu-todayhistory
description: "使用极速数据历史上的今天 API 按月份和日期查询历史上的大事、诞辰与逝世等事件。"
---

## 极速数据历史上的今天（Jisu TodayHistory）

基于 [历史上的今天 API](https://www.jisuapi.com/api/todayhistory/) 的 OpenClaw 技能，按指定的月、日查询历史上当天发生的重要事件，包括重大事件、诞辰、逝世等图文内容。

适合在对话中回答「今天在历史上发生了什么」「1 月 2 日有哪些大事」「帮我找几个今天相关的历史故事」等问题。

使用技能前需要申请数据，申请地址：https://www.jisuapi.com/api/todayhistory/

## 环境变量配置

```bash
# Linux / macOS
export JISU_API_KEY="your_appkey_here"

# Windows PowerShell
$env:JISU_API_KEY="your_appkey_here"
```

## 脚本路径

脚本文件：`skill/todayhistory/todayhistory.py`

## 使用方式与请求参数

当前脚本提供一个子命令：`query`，对应 `/todayhistory/query` 接口。

### 历史上的今天查询（/todayhistory/query）

```bash
python3 skill/todayhistory/todayhistory.py query '{"month":1,"day":2}'
```

请求 JSON：

```json
{
  "month": 1,
  "day": 2
}
```

| 字段名 | 类型   | 必填 | 说明 |
|--------|--------|------|------|
| month  | int    | 是   | 月   |
| day    | int    | 是   | 日   |

## 返回结果示例（节选）

```json
[
  {
    "title": "日俄战争：驻守旅顺的俄军向日军投降。",
    "year": "1905",
    "month": "1",
    "day": "2",
    "content": "……"
  },
  {
    "title": "意大利墨西拿发生地震，20万人丧生。",
    "year": "1909",
    "month": "1",
    "day": "2",
    "content": "……"
  }
]
```

常见字段说明：

| 字段名  | 类型     | 说明   |
|---------|----------|--------|
| title   | string   | 事件标题 |
| year    | string   | 年份    |
| month   | string   | 月份    |
| day     | string   | 日期    |
| content | string   | 事件内容 |

## 常见错误码

业务错误码（参考官网错误码参照）：

| 代号 | 说明     |
|------|----------|
| 201  | 没有信息 |

系统错误码：

| 代号 | 说明                     |
|------|--------------------------|
| 101  | APPKEY 为空或不存在     |
| 102  | APPKEY 已过期           |
| 103  | APPKEY 无请求此数据权限 |
| 104  | 请求超过次数限制         |
| 105  | IP 被禁止               |
| 106  | IP 请求超过限制         |
| 107  | 接口维护中               |
| 108  | 接口已停用               |

## 在 OpenClaw 中的推荐用法

1. 用户提问：「今天在历史上发生了什么？」代理先确定当前日期，例如 1 月 2 日。  
2. 调用：`python3 skill/todayhistory/todayhistory.py query '{"month":1,"day":2}'`。  
3. 从返回列表中选取 3–5 条代表性事件，将 `year`、`title` 与 `content` 整理成时间线式的自然语言描述，作为回答给用户。  

