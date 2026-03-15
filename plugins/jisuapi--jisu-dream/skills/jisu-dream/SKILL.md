---
name: jisu-dream
description: "使用极速数据周公解梦 API 按关键词查询梦境解释，支持分页返回结果列表。"
---

## 极速数据周公解梦（Jisu Dream）

基于 [周公解梦 API](https://www.jisuapi.com/api/dream/) 的 OpenClaw 技能，按关键词检索梦境含义，返回标题（`name`）与内容（`content`），覆盖人物、动物、植物、物品、活动、生活、自然、鬼神、建筑、孕妇等 10 大类。

适合在对话中回答「梦见皮鞋是什么意思」「梦见下雨预示什么」「帮我查一下关于鞋的梦」之类的问题。

使用技能前需要申请数据，申请地址：https://www.jisuapi.com/api/dream

> **重要说明**：周公解梦内容仅用于娱乐和学习参考，不构成任何现实决策或医疗建议。

## 环境变量配置

```bash
# Linux / macOS
export JISU_API_KEY="your_appkey_here"

# Windows PowerShell
$env:JISU_API_KEY="your_appkey_here"
```

## 脚本路径

脚本文件：`skill/dream/dream.py`

## 使用方式与请求参数

当前脚本提供一个子命令：`search`，对应 `/dream/search` 接口。

### 1. 按关键词搜索解梦（/dream/search）

```bash
python3 skill/dream/dream.py search '{"keyword":"鞋","pagenum":1,"pagesize":10}'
```

请求 JSON：

```json
{
  "keyword": "鞋",
  "pagenum": 1,
  "pagesize": 10
}
```

| 字段名   | 类型   | 必填 | 说明                          |
|----------|--------|------|-------------------------------|
| keyword  | string | 是   | 关键词（UTF-8）               |
| pagenum  | int    | 否   | 当前页，默认 1                |
| pagesize | int    | 否   | 每页条数，默认 10，最大不超过 10 |

## 返回结果示例（节选）

```json
{
  "total": "43",
  "pagenum": "1",
  "pagesize": "10",
  "list": [
    {
      "name": "鞋 穿鞋",
      "content": "男人梦见穿新鞋，要交好运……"
    },
    {
      "name": "皮鞋",
      "content": "梦见皮鞋，预示着要远行……"
    }
  ]
}
```

## 常见错误码

来源于 [极速数据周公解梦文档](https://www.jisuapi.com/api/dream/) 的业务错误码：

| 代号 | 说明       |
|------|------------|
| 201  | 关键词为空 |
| 203  | 没有信息   |

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

1. 用户提问：「梦见皮鞋是什么意思？」  
2. 代理调用：`python3 skill/dream/dream.py search '{"keyword":"皮鞋","pagenum":1,"pagesize":5}'`。  
3. 从返回的 `list` 中选取与用户梦境最相关的 1–3 条 `name` / `content`，用自然语言总结含义，并加上一句风险提示（仅供参考，不要过度迷信）。  

