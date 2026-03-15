# Dynatrace 故障排查路由

## 入口判断

收到故障信息后，**第一步**判断入口类型，路由到对应 SOP：

| 入口特征 | 路由目标 |
|---|---|
| URL 包含 `/problem/` | → **[SOP-PROBLEM.md](SOP-PROBLEM.md)**（Problem 模式） |
| URL 包含 `/trace/` 或 Trace ID（32 位 hex） | → **[SOP-TRACE.md](SOP-TRACE.md)**（Trace 模式） |
| 模糊描述，无链接 | → 先执行下方「无链接处理」，再路由 |

## Problem URL 参数提取（路由到 Problem 模式时必须执行）

Dynatrace 有新旧两种 Problem URL 格式，提取方式不同：

### 新版（davis.problems，当前主力）
```
https://{env}.apps.dynatrace.com/ui/apps/dynatrace.davis.problems/problem/{EVENT_ID}?from=...&to=...
```
- **EVENT_ID**：路径末段，如 `-187049689802719993_1773133500000V2`
- **时间信息**：EVENT_ID 中 `_{毫秒时间戳}` 即故障开始时间，可直接利用
- **Phase 1 查询**：`filter event.id == "{EVENT_ID}"`

### 旧版（classic.problems，即将停用）
```
https://{env}.apps.dynatrace.com/ui/apps/dynatrace.classic.problems/#problems/problemdetails;pid={P-XXXXX};gtf=...
```
- **PROBLEM_ID**：`pid=` 参数值，如 `P-26034976`
- **Phase 1 查询**：`filter display_id == "{PROBLEM_ID}"`

> **两种格式共存期注意**：用户可能同时持有新旧链接指向同一故障。新版 EVENT_ID 对应的 `display_id` 是旧版短 ID（如 `P-26034976`），可互相印证。

## Trace URL 参数提取（路由到 Trace 模式时必须执行）

在进入 SOP-TRACE.md 之前，从 URL 中提取以下参数并记录，供后续步骤使用：

| URL 参数 | 记为 | 示例 |
|---|---|---|
| `traceId=` | TRACE_ID | `4f6df9f6ee92ffd3df1ee2c39dc46e5d` |
| `serviceId=` | SERVICE_ID_FROM_URL | `SERVICE-BEBAA73A68B05841` |
| `timeframe=custom{ts1}to{ts2}` | 时间戳（毫秒 UTC） | ts1÷1000 → UTC epoch |

> **serviceId 优先级**：如果 URL 中存在 `serviceId=`，记为 SERVICE_ID_FROM_URL，在 SOP-TRACE Phase T1 中**直接作为实体过滤条件使用**，不需要等 span 查询返回后再提取。
> **时间戳说明**：URL 中时间戳单位为毫秒 UTC，直接除以 1000 转 epoch，**不要加减 8 小时**。

## 无链接处理

用户只描述了故障现象（如"hy-auth 今天下午挂了"），没有给链接：

```dql
fetch events, from: now()-24h
| filter event.kind == "DAVIS_PROBLEM"
| filter matchesPhrase(event.name, "{关键词}") OR matchesPhrase(root_cause_entity_name, "{关键词}")
| summarize cnt = count(), by: {display_id, event.id, event.name, event.start, root_cause_entity_name}
| sort event.start desc | limit 10
```

- 找到相关 Problem → 路由到 **SOP-PROBLEM.md**
- 找不到 Problem，但用户能提供 Trace ID → 路由到 **SOP-TRACE.md**
- 什么都没有 → 向用户询问：Problem 链接 或 Trace ID 或大致时间 + 服务名

## 公共资源

两种模式共同使用的内容统一在 **[SOP-COMMON.md](SOP-COMMON.md)** 中维护：

- 查询铁律
- DQL 模板库
- 报告格式模板
- 实体 ID 提取规则
