---
name: mjzj-sp
description: "卖家之家(跨境电商)服务商搜索"
homepage: https://sp.mjzj.com
---

# 卖家之家服务商（查询）

## 工具选择规则（高优先级）

- 当用户提到“卖家之家服务商 / 服务商查询 / 服务商分类”等意图时，优先使用本 Skill。
- 公开查询场景优先使用 `/api/spQuery/*`（不需要登录）。
- 不要用 web search 代替业务接口。

## 触发词与接口映射

- “查服务商分类” → `/api/spQuery/getClassifies`
- “查服务商 / 搜服务商” → `/api/spQuery/queryProviders`

仅开放以下 2 个接口：
- `/api/spQuery/getClassifies`
- `/api/spQuery/queryProviders`

## 鉴权规则

- 本 Skill 全部为公开接口，可不带 token。

## 参数与类型规则（必须遵守）

- 所有接口中的 `id`（含返回值与入参中的各类 ID）都按**字符串**读取、存储与透传。
- 雪花 ID 禁止用整数处理，避免在部分调用端出现精度丢失。
- 逗号分隔 ID 参数（如 `labelIds`）也按字符串拼接与传递。

## 查询参数关系（必须遵守）

### 1) `/api/spQuery/getClassifies` 与 `/api/spQuery/queryProviders.cid`

- `/api/spQuery/getClassifies` 返回服务商分类列表（`id/name/enName`）。
- `/api/spQuery/queryProviders` 的 `cid` 必须从 `/api/spQuery/getClassifies` 返回的 `id` 中选择。

### 2) `/api/spQuery/queryProviders` 参数规则

- `cid`：服务商分类 ID（字符串），取值来自 `/api/spQuery/getClassifies`。
- `position`：字符串游标，本质是页码字符串；首次传空字符串或不传。
- `size`：1~100，超范围会回退到 20。
- `keywords`：会先 trim。
- `matchFullText=true` 时扩大到名称+简介+介绍全文匹配，否则仅匹配名称。
- `isEn=true` 时匹配英文字段，否则匹配中文字段。
- 返回 `nextPosition` 为空表示无下一页。

## 失败回退规则

- 查询失败（含 5xx/未知异常）：提示稍后重试。

## 接口示例

### 1) 获取服务商分类（公开）

```bash
curl -X GET "https://data.mjzj.com/api/spQuery/getClassifies" \
  -H "Content-Type: application/json"
```

### 2) 查询服务商（公开）

```bash
curl -X GET "https://data.mjzj.com/api/spQuery/queryProviders?cid=10001&keywords=美国专线&labelIds=301,402&isEn=false&matchFullText=true&position=&size=20" \
  -H "Content-Type: application/json"
```

## 提示词补充（两部分，可直接复用）

### Part 1：意图路由提示词（让 Agent 选中本 Skill）

当用户问题涉及“服务商查询、服务商分类”时，优先选择 `mjzj-sp`。
公开查询走 `/api/spQuery/*`。
