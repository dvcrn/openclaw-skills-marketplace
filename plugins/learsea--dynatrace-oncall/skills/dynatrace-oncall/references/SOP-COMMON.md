# Dynatrace 故障排查公共资源

> 本文件由 SOP-PROBLEM.md 和 SOP-TRACE.md 共同引用，不独立使用。

---

## 查询铁律（必须遵守）

1. **禁止无实体过滤的查询**。每条 DQL 必须包含实体过滤条件（`dt.entity.host`、`dt.entity.service`、`display_id` 等），绝不允许全表扫描。**例外**：events 全景扫描（如并发问题查询）因数据量小，可仅用 `event.kind` + 时间窗口过滤，无需实体条件。
2. **时间窗口最小化**。首选精确时间范围（`from: toTimestamp(...)`, `to: toTimestamp(...)`）。Phase 1 可用 `now()-7d`（events 数据量小）。其余步骤用精确时间 ± 合理余量。
3. **limit 必须显式设置**。events ≤ 20，spans ≤ 20，timeseries ≤ 5。
4. **span 查询窗口硬限制 20 分钟**。超过 20 分钟禁止执行。优先用 10 分钟窗口。
5. **先聚合再取详情**。先 `summarize` 看分布，找到异常后 `sort duration desc | limit 1` 取详情。
6. **fields 显式指定**。除最终取完整详情外，其余查询用 `fields` 限定字段。
7. **span 查询预算**：
   - **快速模式**：span 最多 **4 次**
   - **深度模式**：span 最多 **9 次**（主线 6 + 横向 3）
   - **快速→深度升级**：已消耗的次数从 9 次中扣除
   - **Trace 模式专属**：Phase T1 的 Trace 定位查询（`trace.id == toUid("xxx")`）不计入此预算，属于上下文提取步骤
   - events 和 timeseries 查询不计入 span 预算，但**同样受铁律第 1、2、3 条约束**（必须有实体过滤、时间窗口最小化、limit 显式设置）——不是"不限制"，是"不占 span 预算"
   - 每次 span 查询后检查 `scannedRecords` / `scannedBytes`，单次超 1 亿条或 5 GB → 收紧后续查询

---

## 环境信息

- Dynatrace API：`https://{ENV_ID}.apps.dynatrace.com/platform/storage/query/v1/query:execute`
- 认证方式：`Authorization: Bearer {PLATFORM_TOKEN}`
- DQL 时间均为 UTC，报告输出北京时间（UTC+8）
- **时间格式**：`event.start` 可能是 ISO（`2026-03-02T04:10:00.000Z`）或毫秒整数（如 `1773043860000`）。模板中 `{event.start - 30min}` 是伪代码，需自行计算 ISO 字符串代入 `toTimestamp()`。若拿到的是毫秒整数，换算步骤：① 毫秒 ÷ 1000 = 秒（epoch）② 转 ISO 字符串（如 `1773043860000 ÷ 1000 = 1773043860 → 2026-03-09T08:11:00Z`）③ 代入 `toTimestamp("2026-03-09T08:11:00Z")`
- duration 单位为纳秒
- summarize 中 sort 需用别名（如 `cnt = count()`），不能直接 sort `count()`
- `trace.id` 是 uid 类型，**不能直接用字符串 `==` 比较**（类型不匹配，永远返回空）。正确写法：`filter trace.id == toUid("xxx")`；禁止用 `toString(trace.id) == "xxx"`（逐行类型转换开销大，且类型不匹配可能返回空）。注意：Grail 为 index-free 架构，即使用 `toUid()` 仍会扫描时间分区内的全量数据，**缩小时间窗口才是减少扫描量的核心手段**
- **Trace URL 时间戳解析**：URL 中 `timeframe=custom{ts1}to{ts2}` 的时间戳单位为**毫秒 UTC**（不是 BJT），**不要额外加减 8 小时**。换算为 `toTimestamp()` 参数的步骤：
  1. 毫秒 ÷ 1000 = 秒（epoch）
  2. 秒转 ISO 字符串（如 `1773117761502 ÷ 1000 = 1773117761 → 2026-03-10T04:42:41Z`）
  3. 代入 `toTimestamp("2026-03-10T04:42:41Z")`
  > ⚠️ `toTimestamp()` 接收 ISO 字符串或纳秒整数，**不接受毫秒整数**。直接传毫秒值会被当成纳秒，时间将偏到 1970 年附近，导致查询命中空分区。时间偏差是 Phase T1 返回空的最常见原因，查不到数据时**第一步先校验时间换算**。
- `span.kind` 值为小写：`"server"`, `"client"`, `"internal"`

---

## 实体 ID 提取规则

`affected_entity_ids` 是混合数组，按前缀分类提取：

| 前缀 | 实体类型 | 记为 | 说明 |
|---|---|---|---|
| `HOST-` | 主机 | HOST_IDs | 传统主机；K8s 环境可能为空 |
| `SERVICE-` | 服务 | SERVICE_IDs | 后续 Phase 2.5 / Phase 4 的核心过滤条件 |
| `PROCESS_GROUP_INSTANCE-` | 进程实例 | PGI_IDs | 单个 pod/进程；GC 查询用 |
| `PROCESS_GROUP-` | 进程组 | PG_IDs | 同一 deployment 的所有实例的父级 |
| 其他前缀 | 记录但不主动使用 | — | 如 `HTTP_CHECK-`、`SYNTHETIC_TEST-` 等 |

> **PG_ID 获取**：如果 `affected_entity_ids` 中没有 `PROCESS_GROUP-` 实体，通过 PGI 反查：
> `fetch dt.entity.process_group_instance | filter id == "{PGI_ID}" | fields belongsTo[dt.entity.process_group] | limit 1`

**过滤条件优先级**（从高到低）：
1. `dt.entity.service`（SERVICE_IDs）
2. `dt.entity.process_group_instance`（PGI_IDs）
3. `dt.entity.host`（HOST_IDs）
4. K8s 环境 `dt.entity.host` 为空时，使用 `affected_entity_ids` 中的 HOST_IDs

> **K8s 环境注意**：`dt.entity.host` 直接字段经常为空。如果 HOST_IDs 也为空（纯 K8s 无 host agent），主机资源查询跳过，改用容器级指标（`dt.kubernetes.container.*`）。

---

## DQL 模板库

### 全景扫描

**并发问题**
```dql
fetch events,
  from: toTimestamp("{window_start}"), to: toTimestamp("{window_end}")
| filter event.kind == "DAVIS_PROBLEM"
| summarize cnt = count(),
            by: {display_id, event.name, event.start, event.end, root_cause_entity_name, host.name}
| sort event.start asc | limit 20
```

**底层事件（按事件 ID）**
```dql
fetch events,
  from: toTimestamp("{window_start}"), to: toTimestamp("{window_end}")
| filter event.kind == "DAVIS_EVENT"
| filter event.id == "{ID1}" OR event.id == "{ID2}"
| fields event.id, event.name, event.type, event.category, event.description,
         dt.entity.process_group_instance, dt.entity.host, timestamp
| limit 10
```

**变更与环境事件（一次覆盖全维度）**
```dql
fetch events,
  from: toTimestamp("{window_start - 24h}"), to: toTimestamp("{window_end}")
| filter event.kind == "DAVIS_EVENT"
| filter event.type == "CUSTOM_DEPLOYMENT"
    OR event.type == "CUSTOM_CONFIGURATION"
    OR event.type == "CUSTOM_ANNOTATION"
    OR event.type == "PROCESS_RESTART"
    OR event.type == "PROCESS_CRASH"
    OR event.type == "PROCESS_UNAVAILABLE"
    OR event.type == "OS_SERVICES_UNAVAILABLE"
    OR event.type == "MARKED_FOR_TERMINATION"
    OR event.type == "HOST_SHUTDOWN"
    OR event.type == "CONNECTION_LOST"
    OR event.type == "TCP_CONNECTIVITY_PROBLEM"
    OR event.type == "HTTP_CHECK_GLOBAL_OUTAGE"
    OR event.type == "SYNTHETIC_GLOBAL_OUTAGE"
    OR event.type == "EXTERNAL_ALERT"
    OR event.type == "EC2_HIGH_CPU"
    OR event.type == "EBS_VOLUME_HIGH_LATENCY"
    OR event.type == "RDS_HIGH_LATENCY"
    OR event.type == "RDS_LOW_STORAGE"
    OR matchesPhrase(event.type, "KUBERNETES")
| filter in(dt.entity.host, "HOST_ID_1", "HOST_ID_2", "HOST_ID_3")
| fields event.type, event.name, event.description, dt.entity.host, timestamp
| sort timestamp desc | limit 20
```

**主机资源**
```dql
timeseries cpu = avg(dt.host.cpu.usage),
  from: toTimestamp("{window_start - 3h}"), to: toTimestamp("{window_end}"),
  by: {dt.entity.host}
| filter in(dt.entity.host, "HOST_ID_1", "HOST_ID_2")
```
```dql
timeseries mem = avg(dt.host.memory.used),
  from: toTimestamp("{window_start - 3h}"), to: toTimestamp("{window_end}"),
  by: {dt.entity.host}
| filter in(dt.entity.host, "HOST_ID_1", "HOST_ID_2")
```

**服务指标**
```dql
timeseries resp = avg(dt.service.request.response_time),
  from: toTimestamp("{window_start - 3h}"), to: toTimestamp("{window_end}"),
  by: {dt.entity.service}
| filter in(dt.entity.service, "SERVICE_ID_1", "SERVICE_ID_2")
```
```dql
timeseries err = avg(dt.service.request.failure_rate),
  from: toTimestamp("{window_start - 3h}"), to: toTimestamp("{window_end}"),
  by: {dt.entity.service}
| filter in(dt.entity.service, "SERVICE_ID_1", "SERVICE_ID_2")
```

**JVM GC**
```dql
timeseries gc = max(dt.runtime.jvm.gc.suspension_time),
  from: toTimestamp("{window_start - 1h}"), to: toTimestamp("{window_end}"),
  by: {dt.entity.process_group_instance}
| filter in(dt.entity.process_group_instance, "PGI_1", "PGI_2")
```

### 定向深挖（Span 查询）

**故障时段全貌（消耗 1 次 span）**
```dql
fetch spans,
  from: toTimestamp("{window_start - 10min}"), to: toTimestamp("{window_start + 10min}")
| filter dt.entity.host == "{HOST_ID}"
| summarize cnt = count(), avg_dur = avg(duration), max_dur = max(duration),
            by: {span.name, span.kind, dt.entity.service}
| sort cnt desc | limit 20
```

**基线对比（消耗 1 次 span）**
```dql
fetch spans,
  from: toTimestamp("{baseline_start}"), to: toTimestamp("{baseline_start + 20min}")
| filter dt.entity.host == "{HOST_ID}"
| summarize cnt = count(), avg_dur = avg(duration), max_dur = max(duration),
            by: {span.name, span.kind}
| sort cnt desc | limit 20
```

**CPU 比值（消耗 1 次 span）**
```dql
fetch spans,
  from: toTimestamp("{window_start - 5min}"), to: toTimestamp("{window_start + 5min}")
| filter dt.entity.service == "{SERVICE_ID}"
| filter span.kind == "server"
| fields span.name, duration, span.timing.cpu
| sort duration desc | limit 1
```

**下游依赖（消耗 1 次 span）**
```dql
fetch spans,
  from: toTimestamp("{window_start - 5min}"), to: toTimestamp("{window_start + 10min}")
| filter dt.entity.service == "{SERVICE_ID}"
| filter span.kind == "client"
| summarize cnt = count(), avg_dur = avg(duration), max_dur = max(duration),
            by: {span.name}
| sort max_dur desc | limit 15
```

**错误模式（消耗 1 次 span）**
```dql
fetch spans,
  from: toTimestamp("{window_start - 5min}"), to: toTimestamp("{window_start + 10min}")
| filter dt.entity.host == "{HOST_ID}"
| filter otel.status_code == "ERROR" OR http.response.status_code >= 500
| summarize cnt = count(), by: {span.name, http.response.status_code}
| sort cnt desc | limit 15
```

**完整详情（消耗 1 次 span）**
```dql
fetch spans,
  from: toTimestamp("{window_start - 10min}"), to: toTimestamp("{window_start + 10min}")
| filter dt.entity.host == "{HOST_ID}"
| filter span.name == "{异常span名称}"
| sort duration desc | limit 1
```

**按 Trace ID 查询**
```dql
fetch spans,
  from: toTimestamp("{window_start - 10min}"), to: toTimestamp("{window_start + 10min}")
| filter dt.entity.service == "{SERVICE_ID}"
| filter trace.id == toUid("{trace_id}")
| sort duration desc | limit 20
```

---

## 信号研判表

| 维度 | 🔴 强信号 | 🟡 弱信号 | ⚪ 正常 |
|---|---|---|---|
| 并发问题 | 多个 problem 指向相关实体 | 有同时段不相关 problem | 仅当前 problem |
| 底层事件 | 事件描述直接解释故障 | 描述模糊 | 无异常 |
| 部署/配置 | 故障前 **1h** 内有变更 | 故障前 **24h** 内有变更 | 无变更 |
| 生命周期 | 故障时段有 CRASH/RESTART/TERMINATION | 存在但时间不吻合 | 无事件 |
| 基础设施 | HOST_SHUTDOWN / K8s 事件 / 云平台告警 | 存在但不确定因果 | 无事件 |
| 网络 | CONNECTION_LOST / TCP 问题 | 有但时间不吻合 | 无事件 |
| 主机资源 | CPU 或 Memory 在故障时段明显飙高 | 略有上升 | 平稳 |
| 服务指标 | 响应时间/错误率突变 | 缓慢退化 | 正常波动范围 |
| JVM GC | suspension > 0.5s/min 且时间吻合 | 轻微升高（0.1-0.5s/min） | < 0.1s/min 或 ⚠️ 数据不可用 |

---

## 报告格式模板

**报告正文不含一级标题（`#`），从二级标题（`##`）开始。**

### 快速模式

```
## 一句话摘要
【P?】{服务} 因 {根因} 导致 {影响}，持续 {时长}，{状态}。

## 根因证据
（直接引用关键 span/event 原文）

## 修复建议
- 紧急止血：
- 短期修复：
```

### 深度模式

```
## 一句话摘要
【P?】{服务} 因 {根因} 导致 {影响}，持续 {时长}，{状态}。

## 二、故障现象
（告警序列、关键指标、是否复发）

## 三、并发问题
（同时段其他 problem，明确哪些相关、哪些无关及理由）

## 四、根因分析
（根本原因、根因分类、触发条件、证据链、因果链）

### 异常链
（还原完整调用链，内容根据实际 span 数据自由组织）

## 五、修复建议
- 【紧急止血】
- 【短期修复】
- 【中期优化】

## 六、完整时间线
| 时间 (BJT) | 事件 | 相关实体 |
|---|---|---|
```

---

## 设计原则

1. **先扫描后判断**：在消耗任何 span 预算之前，先用低成本的 events + timeseries 建立全景认知
2. **跟着证据走**：不按故障类型预设分支路由，根据扫描发现的异常信号决定深挖方向
3. **回答两个问题**：不只定位"哪里坏了"（故障点），还要回答"为什么现在坏了"（触发条件）
4. **量级必须匹配**：假设"A 导致 B"时，必须验证 A 的绝对量级足以解释 B
5. **资源耗尽不是终点**：GC/CPU/内存/连接池耗尽是中间症状，必须继续追问"为什么耗尽"
6. **时序是因果的前提**：假设"A 导致 B"时，A 的发生时间必须早于 B。任何异常信号在被认定为根因之前，必须确认它出现在故障之前而非之后。故障期间出现的异常（慢查询、错误率升高、连接超时等）默认是症状，需要证明它早于故障才能升级为根因候选。
7. **优先用最直接的数据，不可得时才反推**：
   - 如果有更直接的诊断数据（heap dump、火焰图、慢查询日志+执行计划、应用异常日志等），**优先读取，不需要 span 反推**
   - 直接数据不可得时，寻找**干净观测窗口**（故障触发前、重启后初始阶段、或 GC/CPU 尚未恶化的时段），在窗口内用 span/metrics 反推异常来源
   - 干净窗口的核心价值：排除了噪音干扰（GC stop-the-world、连接池耗尽、级联超时），此时观测到的异常才是真异常
   - 适用于所有场景：内存泄漏、响应时间退化、错误率飙升、CPU 异常——任何需要定位"哪里触发的"都可以用这个方法
   - **⚠️ 干净窗口内的 span 查询同样受铁律约束**：必须带实体过滤（PGI/SERVICE/HOST），窗口控制在 10-20 分钟以内，先 summarize 聚合再按需取 1 条详情，不得全量扫描

---

## 通用注意事项

1. 不要假设故障类型，`event.category` 只是症状标签，不是根因分类
2. 不要假设根因一定在代码层面，运维误操作、云平台故障、上游挂了都是常见根因
3. Phase 3 的假设可以被 Phase 4 推翻，修正假设而不是忽略数据
4. 指标查询为空时，尝试更换 metric key（Dynatrace 经典 vs OpenTelemetry 命名不同）
5. span 过滤为空时，依次尝试 `dt.entity.host` → `dt.entity.service` → `dt.entity.process_group_instance`
6. 不要用 REST API 查实体名，用 Grail：`fetch dt.entity.service | filter id == "SERVICE-xxx" | fields entity.name | limit 1`
7. span 数据可用性：故障恢复 >6h 后 span 可能稀疏，若 4.1 返回 cnt 总计 < 50，改用 timeseries 做初步判断
8. **DB span 的数据库名以 `db.query.text` 为准**：`db.namespace` 是 JDBC 连接串配置的默认 schema，span 名（如 `SELECT db_customer`）也来自它；实际操作的表可能在 SQL 里显式指定了不同 schema（如 `db_common.tbl_xxx`）。报告中描述数据库名时，**必须优先读取 `db.query.text` 字段里的真实表名**，不得直接用 `db.namespace` 或 span 名替代。
