# Dynatrace 故障排查 SOP — Trace 模式

> **入口**：收到 URL 包含 `/trace/` 或单独的 Trace ID（32 位 hex）。
> **公共资源**：查询铁律、DQL 模板、报告格式见 [SOP-COMMON.md](SOP-COMMON.md)。

---

## 流程总览

```
Phase T1             Phase T2              Phase T3           Phase T4         Phase T5
Trace 上下文 ───→  反向关联 Problem ───→  全景扫描 ───→  定向深挖 ───→  输出报告
（提取实体+窗口）   （补全影响范围）      （同 Problem 模式）  （同 Problem 模式）
```

> **核心差异**：Problem 模式从 Problem 出发，已知时间窗口和受影响实体。Trace 模式需要先从 Trace 还原这些信息，再合并进标准流程。**Phase T2 不可跳过**——Trace 只是故障的一个截面，漏掉关联 Problem 就可能漏掉故障的真实范围和持续时长。

---

## Phase T1: 从 Trace 提取上下文

**前置**：检查 SOP-ROUTER 阶段是否已提取到 SERVICE_ID_FROM_URL。若有，直接加入过滤条件：

```dql
fetch spans,
  from: toTimestamp("{trace_time - 10min}"), to: toTimestamp("{trace_time + 10min}")
| filter dt.entity.service == "{SERVICE_ID_FROM_URL}"
| filter trace.id == toUid("{TRACE_ID}")
| filter span.kind == "server" OR isNull(parent_span.id)
| sort duration desc | limit 5
```

若 URL 中无 serviceId，则不加 service 过滤：

```dql
fetch spans,
  from: toTimestamp("{trace_time - 10min}"), to: toTimestamp("{trace_time + 10min}")
| filter trace.id == toUid("{TRACE_ID}")
| filter span.kind == "server" OR isNull(parent_span.id)
| sort duration desc | limit 5
```

> **时间窗口**：必须用精确时间范围，禁止用 `now()-7d` 等宽泛窗口（违反铁律）。如果 Trace URL 无时间参数且无法从用户获取，最大允许 `now()-24h`，不得更宽。此查询属于定位性质，不计入 Phase T4 的 span 预算。
>
> ⚠️ **时间换算前置必做**：执行查询前，必须先将 URL 中 `timeframe=custom{ts1}to{ts2}` 的毫秒时间戳换算为 ISO 字符串并写出，确认无误后再构造查询。换算规则见 SOP-COMMON 环境信息。**禁止直接把毫秒值传入查询**，时间算错是 Phase T1 返回空的最常见原因。

### ⚠️ Phase T1 查询返回空时的强制处理规则

**禁止扩大查询范围、禁止去掉实体过滤、禁止全表扫描。**

返回空时，按顺序排查：

1. **重新核查时间换算**：确认之前的换算步骤无误（毫秒 ÷ 1000 → epoch → ISO）。虽然应在查询前已完成，但仍需二次确认。
2. **去掉 span.kind 重试 1 次**（保留 service + toUid 过滤）：有时根 span 不是 server 类型。
3. 以上均无结果 → 立即停止，向用户上报：
   > "Phase T1 Trace 查询返回空，时间换算已校验，span 数据不可查。请提供：① Problem 链接，或 ② 故障时间 + 服务名，以便切换到 Problem 模式继续排查。"

从根 span 提取并记录：

| 字段 | 记为 | 用途 |
|---|---|---|
| `timestamp` | Trace 时间戳 | 后续查询的时间锚点 |
| `duration` | 根 span 耗时 | 故障严重程度初判 |
| `dt.entity.service` | 服务实体 ID | 等同 Problem 模式的 SERVICE_IDs |
| `dt.entity.host` | 主机实体 ID | 等同 Problem 模式的 HOST_IDs |
| `dt.entity.process_group_instance` | 进程实例 ID | 等同 Problem 模式的 PGI_IDs |
| `otel.status_code` / `http.response.status_code` | 错误状态 | 故障类型初判 |
| `span.events` | 异常事件 | 直接读取调用栈，优先从此处还原错误链 |
| `container.image.version` | 镜像版本 | 后续变更事件交叉验证 |

**时间窗口确定**：以 `timestamp` 为中心，取 `timestamp - 1min` 到 `timestamp + 1min` 作为 `{window_start}` / `{window_end}`（后续扫描可适当扩展）。

> **span.events 优先**：如果 `span.events` 中有完整的异常栈（ConnectException、NullPointerException 等），立即记录，这往往直接指向应用层根因。不要等到 Phase T4 才读异常信息。

---

## Phase T2: 反向关联 Problem（**必须执行，不可跳过**）

Trace 是故障的一个截面，不代表全貌。必须查询关联 Problem 补全影响范围和持续时长。

> **前置检查**：执行 Phase T2 前，必须确认已有至少一个实体 ID（来自 Phase T1 结果 或 SERVICE_ID_FROM_URL）。若两者均为空，**停止执行，向用户上报**："无法执行 Problem 关联查询，缺少实体 ID。请提供 Problem 链接或服务名。"

**Step 1：按服务实体查关联 Problem**

```dql
fetch events,
  from: toTimestamp("{window_start - 2h}"), to: toTimestamp("{window_start + 2h}")
| filter event.kind == "DAVIS_PROBLEM"
| expand entity = affected_entity_ids
| filter entity == "{SERVICE_ID}" OR entity == "{HOST_ID}"
| summarize event.name = takeFirst(event.name), event.start = min(event.start),
            event.end = takeFirst(event.end), event.category = takeFirst(event.category),
            root_cause_entity_name = takeFirst(root_cause_entity_name),
            by: {display_id}
| sort event.start asc | limit 10
```
> `expand` 只展开 entity 列，同一 Problem 的其他字段（event.end、event.category 等）在各行中值相同，`takeFirst` 结果确定。`event.start` 用 `min()` 确保取最早时间。

**Step 2：根据结果判断**

| 结果 | 处理方式 |
|---|---|
| 找到关联 Problem | 记录 Problem ID、`event.start`、`event.end`（如为空则故障未恢复）、`affected_entity_ids`。**以 Problem 的时间窗口替换 Trace 时间窗口**作为后续扫描的锚点 |
| 找到多个 Problem | 选 `event.start` 最早的作为主 Problem，其余列为并发问题 |
| 未找到 Problem | 说明故障未触发 Davis 告警（可能低于阈值、或监控未覆盖）。继续使用 Trace 时间窗口，但在报告中注明"未关联到 Davis Problem，影响范围和持续时长以 Trace 采样时刻为准" |

> **关键价值**：Phase T2 在上次 hy-auth 排查中发现了故障实际持续 > 11 小时（Trace 采样时仍未恢复），而不只是 2 分钟。漏掉这步会严重低估故障影响。

---

## 排查模式判断（Phase T2 完成后执行）

收到故障链接后，检查用户指令：
- 含 **"快速"** → 快速模式
- 含 **"深度"/"完整"** → 深度模式
- 无指定 → Phase T2 完成后按以下规则自动判断

**自动判断**（满足任一 → 深度）：

| 来源 | 条件 | 含义 |
|---|---|---|
| Phase T1 | 根 span `duration` > 10s | 严重性能退化 |
| Phase T1 | `span.events` 有异常但调用栈不完整 | 需要更多 span 还原完整链路 |
| Phase T2 | 找到关联 Problem 且 `event.end=null` | 故障未恢复 |
| Phase T2 | 找到关联 Problem 且 `event.category == "AVAILABILITY"` | 可用性故障 |
| Phase T2 | 找到 ≥ 2 个关联 Problem | 波及范围广 |
| Phase T2 | **未找到关联 Problem** | 监控覆盖不足，信息缺失本身需要更深挖 |

以上均不满足 → 快速模式。

> **与 Problem 模式的差异**：Problem 模式在 Phase 1 就能判断（靠 Problem 元数据），Trace 模式必须等 Phase T2 完成后才能判断。

**两种模式的区别仅在 Phase T4**：
- 快速：span 最多 4 次，报告为简化格式
- 深度：span 最多 9 次，报告为完整六段格式
- **Phase T1-T3 两种模式完全相同，不简化不跳过**

---

## Phase T3: 全景扫描

> 完全等同于 SOP-PROBLEM.md 的 Phase 2，使用相同的 DQL 模板。
> **时间锚点**：优先使用 Phase T2 找到的 Problem 时间窗口；未找到 Problem 时使用 Trace 时间戳。

依次执行：

#### T3.1 并发问题
同 Problem 模式 Phase 2.1。如果 Phase T2 已找到关联 Problem，此步结果与 Phase T2 可能重叠，合并记录即可。

#### T3.2 底层事件
如果关联 Problem 有 `dt.davis.event_ids`，执行此步；否则跳过。

#### T3.3 变更与环境事件
同 Problem 模式 Phase 2.3。

#### T3.4 主机资源
同 Problem 模式 Phase 2.4。

#### T3.5 服务指标
同 Problem 模式 Phase 2.5。

#### T3.6 JVM GC（仅 JVM 服务）
同 Problem 模式 Phase 2.6。

---

## Phase T4: 信号研判 + 定向深挖

> 完全等同于 SOP-PROBLEM.md 的 Phase 3 + Phase 4。

**额外优势**：Trace 模式通常已从 Phase T1 的 `span.events` 中读到了具体异常信息（错误类型、调用栈），这等同于已完成了 Problem 模式中 Phase 4 的"错误模式分析"，可节省 1 次 span 预算。

> 在 Phase T4 入口，先检查 Phase T1 已提取的 `span.events` 信息是否已足以确定应用层根因。若是，直接在信号研判阶段作为 🔴 强信号处理，不需要重新执行错误模式查询。

---

## Phase T5: 输出报告

格式见 SOP-COMMON 报告格式模板。

**Trace 模式特有的报告注意事项**：

1. 在"故障现象"中注明：报告以 Trace `{trace_id}` 为入口，关联 Problem `{display_id}`（如有）
2. 如果未找到关联 Problem，在"影响范围"中注明监控覆盖可能不足，建议补充告警配置
3. 故障持续时长：优先以 Problem 的 `event.start` 到 `event.end` 计算；未关联 Problem 时以 Trace 采样时刻为准，注明"实际持续时长未知"
