# Dynatrace 故障排查 SOP — Problem 模式

> **入口**：收到 URL 包含 `/problem/P-` 的故障链接。
> **公共资源**：查询铁律、DQL 模板、报告格式见 [SOP-COMMON.md](SOP-COMMON.md)。

---

## 流程总览

```
Phase 1         Phase 2            Phase 3          Phase 4          Phase 5
问题概况 ───→ 全景扫描 ───→ 信号研判 ───→ 定向深挖 ───→ 输出报告
(1 query)   (events+timeseries)   (分析,0 查询)   (span queries)
            不消耗 span 预算                       消耗 span 预算
```

---

## 排查模式

收到故障链接后，检查用户指令：
- 含 **"快速"** → 快速模式
- 含 **"深度"/"完整"** → 深度模式
- 无指定 → Phase 1 后自动判断

**自动判断**（Phase 1 完成后，满足任一 → 深度）：

| 条件 | 字段 |
|---|---|
| `affected_entity_ids` 长度 > 5 | affected_entity_ids |
| `event.category == "AVAILABILITY"` | event.category |
| `root_cause_entity_name` 为空 | root_cause_entity_name |
| `dt.davis.event_ids` 长度 > 3 | dt.davis.event_ids |

Phase 2 完成后，若同时段独立 problem ≥ 2 → 也升级为深度。

以上均不满足 → 快速模式。

**两种模式的区别仅在 Phase 4**：
- 快速：Phase 4 最多 4 次 span，报告为简化格式
- 深度：Phase 4 最多 9 次 span，报告为完整六段格式
- **Phase 1-3 两种模式完全相同，不简化不跳过**

---

## Phase 1: 问题概况

从故障链接提取 ID，按 URL 格式选择查询方式（见 SOP-ROUTER.md）：

**新版 URL（davis.problems）**：EVENT_ID 在路径末段，如 `-187049689802719993_1773133500000V2`
```dql
fetch events, from: now()-7d
| filter event.kind == "DAVIS_PROBLEM"
| filter event.id == "{EVENT_ID}"
| limit 3
```

**旧版 URL（classic.problems）**：PROBLEM_ID 在 `pid=` 参数，如 `P-26034976`
```dql
fetch events, from: now()-7d
| filter event.kind == "DAVIS_PROBLEM"
| filter display_id == "{PROBLEM_ID}"
| limit 3
```

> 新版 EVENT_ID 中 `_{毫秒时间戳}` 部分即故障开始时间，可代入后续查询的时间窗口（毫秒 ÷ 1000 → epoch → ISO），减少对 `now()-7d` 的依赖。

提取并记录：

| 字段 | 记为 | 用途 |
|---|---|---|
| `event.name` | 问题类型 | 参考信号，**不用于路由决策** |
| `event.start` / `event.end` | 故障窗口 | 后续查询的时间锚点 |
| `event.category` | 分类 | 参考信号之一 |
| `affected_entity_ids` | 受影响实体 | Phase 2/4 过滤条件（见 SOP-COMMON 实体 ID 提取规则） |
| `dt.entity.host` | 主机 ID | 过滤条件（可能为空） |
| `dt.entity.process_group_instance` | 进程实例 ID | 备用过滤条件 |
| `root_cause_entity_name` | Davis 根因 | 参考，不可盲信 |
| `dt.davis.event_ids` | 底层事件 | Phase 2.2 查询用 |
| `entity_tags` | 业务标签 | 影响范围 + 语言判断 |
| `host.name` | 主机名 | 报告可读性 |

提取完成后，从 `affected_entity_ids` 按前缀分类（规则见 SOP-COMMON），记录 HOST_IDs、SERVICE_IDs、PGI_IDs。

**时间窗口**：以 `event.start` 和 `event.end`（如为空则用当前时间）作为后续查询的 `{window_start}` / `{window_end}`。

---

## Phase 2: 全景扫描

> **目的**：在消耗 span 预算之前，用低成本查询从多个维度建立环境认知。所有查询均为 events 或 timeseries，**不消耗 span 预算**。
>
> **记录原则**：只记录异常发现和关键数值。正常的维度记录一行"⚪ 正常"，不复述原始数据。

使用 SOP-COMMON 中的 DQL 模板，依次执行：

#### 2.1 并发问题
时间窗口：`event.start - 30min` 到 `event.start + 60min`

#### 2.2 底层事件
> 如果 Phase 1 的 `dt.davis.event_ids` 为空，跳过此步。

用 `event.id` 过滤，时间窗口同 2.1。

#### 2.3 变更与环境事件
时间窗口：`event.start - 24h` 到 `event.start + 1h`，实体过滤用 HOST_IDs（最多 3 台）。

> 如果返回 20 条（limit 已满），说明事件频繁被截断，可缩小时间窗口到 `event.start - 4h` 重查。

#### 2.4 主机资源
时间窗口：`event.start - 3h` 到 `event.start + 1h`，最多 3 台主机。

> **内存异常时必须扩查长趋势**：若内存在故障时段明显偏高或出现骤降（OOM 重启迹象），**追加查询 `event.start - 48h` 的长时间窗口**，判断内存是今天才升高还是长期处于高位/持续爬升。长期高位或缓慢爬升 = 内存泄漏信号，直接影响 Phase 3 的假设方向。

#### 2.5 服务指标
时间窗口：`event.start - 3h` 到 `event.start + 1h`，Davis 根因服务 + 最多 2 个其他受影响 SERVICE。

#### 2.6 JVM GC（仅 JVM 服务）
从 `entity_tags`、进程名或已知服务信息判断语言，非 JVM 服务跳过。
时间窗口：`event.start - 1h` 到 `event.start + 30min`。

---

## Phase 3: 信号研判

> **此阶段不执行任何查询。**

对 Phase 2 每个维度按 SOP-COMMON 信号研判表标注信号强度，然后：

1. 列出所有 🔴 信号
2. 判断多个 🔴 信号是因果链还是独立事件——**必须用时间戳验证先后顺序**，确认"因"发生在"果"之前；时间接近不等于因果，时序倒置的信号降级为 🟡
3. 无 🔴 信号，将 🟡 列为待验证方向
4. 全是 ⚪ → 记录"环境扫描未发现外部触发因素，需从应用 span 数据入手"
5. **比例性校验**：假设"X 导致故障"时，评估 X 的量级是否足以解释故障规模

**输出格式**（内部记录）：
```
信号总结：
- 🔴 2.3: 故障前 15min 有部署 (v2.3.1 → v2.3.2)
- 🔴 2.5: 响应时间从 200ms 突增至 8s
- ⚪ 2.4: CPU/Memory 正常

假设：新版本引入性能缺陷
Phase 4 策略：4.1 + 4.2 对比部署前后
```

> **可跳过 Phase 4 的情况**：如果 Phase 2 发现明确的基础设施根因（如 HOST_SHUTDOWN 时间与故障完全吻合），可直接 Phase 5 输出报告，不消耗 span 预算。但必须确认因果关系明确，不能仅凭时间接近就下结论。

---

## Phase 4: 定向深挖

> **这是唯一消耗 span 预算的阶段。**

根据 Phase 3 的假设，从 SOP-COMMON DQL 模板库中选择对应查询。标准切入点：

| 假设方向 | 优先使用 |
|---|---|
| 新部署引入问题 | 故障时段全貌 + 基线对比（deep 模式） |
| 资源瓶颈（CPU/GC/Memory） | CPU 比值 → 资源耗尽归因 |
| 下游依赖故障/网络问题 | 下游依赖分析 |
| 错误率飙升 | 错误模式分析 |
| 基础设施事件 | Phase 2 已足以定论，直接 Phase 5 |
| 无明确假设 | 故障时段全貌 → CPU 比值 → 按结果决定 |

### CPU 比值判断规则
- **cpu/duration > 10%** → CPU 密集型 → 取详情查代码路径
- **cpu/duration < 1%** → 线程被阻塞 → 结合 Phase 2.6 GC 信号强度判断：
  - **GC 🔴**（suspension > 0.5s/min 且时间吻合）→ GC 是直接阻塞原因。**⚠️ 遵循设计原则 6（时序是因果的前提）：GC 期间出现的慢 span / 依赖超时默认是症状，不是根因。** 先查内存 48h 趋势判断是泄漏还是外部压力，再按设计原则 7 选择追因路径。
  - **GC 🟡**（0.1~0.5s/min）→ GC 是可能因素之一，同时执行下游依赖分析 + 错误模式分析，不预设结论
  - **GC ⚪ 或数据不可用** → 转下游依赖分析；无结论时报告中注明
- **1%~10%** → 兼有因素，结合其他信号判断

### 快速 → 深度升级
当 4 次 span 无法定论时：
1. 列出已完成清单和消耗的 span 次数
2. 声明升级为深度模式
3. 预算：9 - 已消耗 = 剩余
4. 继续执行基线对比及未完成的诊断

### 全局兜底（span 预算耗尽仍无定论）
(a) 重新审视 Phase 2 的 🟡 弱信号
(b) 从 2.1 并发 problem 列表中选开始时间更早的 problem 作为新入口，最多切换 1 次
(c) 输出已有证据，根因标注"未确定"，列出已排除方向和剩余可能性

---

## Phase 5: 输出报告

格式见 SOP-COMMON 报告格式模板（快速/深度按模式选择）。

所有时间转换为北京时间（UTC+8）。
