---
name: notex-skills
description: "NoteX 技能路由网关（CWork Key 鉴权），提供内容创作、OPS 洞察、Notebook 索引/详情、授权打开、上下文沉淀写入五类能力。"
---

# NoteX Skills — 通用技能路由网关

**当前版本**: v1.1 | **接入渠道**: `CWork Key` 鉴权

本技能集合提供五类能力：内容创作（8 类产物）、OPS 运营洞察、Notebook 索引与详情、NoteX 首页授权打开、上下文沉淀写入。

---

## 1. 核心鉴权 (Authentication)

无论调用哪种技能，鉴权都必须先完成。**对用户只暴露 `CWork Key` 授权动作**，不暴露 Token 细节。

```http
GET https://notex.aishuo.co/noteX/api/user/nologin/appkey?appKey={CWork Key}
```

**返回结构示例（字段说明）**：
```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": {
    "access-token": "xxx",   
    "userId": "xxx",       
    "personId": 123456   
  }
}
```

### 1.1 统一前置鉴权规则（强约束）

所有接口调用（创作类 / OPS / 索引检索）都必须先做鉴权预检，且对外话术与取值优先级固定如下：

1. **第一优先级（环境变量）**：先自动读取系统环境变量 `XG_USER_TOKEN`、`XG_USER_ID` 与 `XG_USER_PERSONID`（兼容拼写 `XG_USER_PERSIONID`）。三者**必须同时存在**才可直接使用；若任一缺失，则进入第二优先级（CWork Key 换取）。
2. **第二优先级（主动索取）**：若环境变量缺失/为空，则向用户索取/确认 `CWork Key` 授权，走 `user/nologin/appkey` 正式换取流程。
3. **禁区**：禁止在对话中向用户索取或解释 `access-token/x-user-id/personId/login` 等实现细节。禁止绕过鉴权直接调用业务 API。

### 1.2 内部执行规则（实现细节，不对用户暴露）

1. 按照 `环境变量 (XG_USER_TOKEN/XG_USER_ID/XG_USER_PERSONID)` -> `CWork Key 换取` 的顺序获取参数。
2. 通过 `user/nologin/appkey` 获取到的字段映射如下（已精简，直接使用）：
   - `data["access-token"]` → Header `access-token`
   - `data.userId` → Header `x-user-id`（注意：对应 CWork 的 empId）
   - `data.personId` → Header `personId`
3. `x-user-id` 为**必传 Header**：若缺失/为空，**直接停止调用**，不允许兜底或继续执行。
4. 极端情况：若环境变量缺失且未提供 CWork Key，停止调用，并在对话层仅提示“请先完成工作协同授权（CWork Key）”。
5. 后续业务请求 Header 继续携带：`access-token`，以及部分旧接口需要的 `personId`。
   > ⚠️ **强烈建议：开发者及脚本严禁随意伪造或乱传 `x-user-id`**。特别是对于有严格鉴权的高级接口（如 `ops-chat`），后端将**优先直接验证 `access-token` 换取真实所属人 ID 以用于鉴权**。若脚本或前端强制传入错误或虚拟的 `x-user-id` (如 "dummy")，只会极大地增加被后台拦截报 403 权限不足或导致数据错位的风险！请完全信任并依赖 Token 机制自身的用户身份载荷。
   > ⚠️ **强约束**：不得伪造或替换 `x-user-id`，必须来自 `XG_USER_ID` 或 `user/nologin/appkey` 返回的 `userId`。

> 建议：将本次会话鉴权结果（或环境变量提取结果）做短期本地缓存，避免同一会话重复换取。

### 1.3 环境约束（发布强约束）

1. `docs/skills/` 下所有文档、示例、脚本均仅使用生产域名。
2. NoteX 业务接口统一使用：`https://notex.aishuo.co/noteX`
3. 严禁在发布内容中出现本地开发地址或非生产协议地址。

---

## 2. 内容创作类技能 (Asynchronous Creator)

覆盖从文本整理到视频渲染的 8 种高发算力场景，采用**队列投递 + 异步轮询**架构。

### 2.0 三要素（角色 / 能力 / 使用时机）

- 我是谁：NoteX 创作者智能生成助手，负责把输入素材转换成可交付的多媒体内容。
- 我能做什么：分发并执行 8 类创作任务（slide/infographic/video/audio/report/mindmap/quiz/flashcards），并返回可访问结果链接。
- 什么时候使用：当用户目标是“生成内容产物”（如 PPT、报告、音频、视频、脑图、测验、闪卡）时使用。
- 前置条件：调用前必须通过“1.1 统一前置鉴权规则”。

### 2.1 支持的创作技能 (`skill` 参数)
| 技能 ID | 产物形式 | 必填参数附加约束 | 预计渲染 |
|---|---|---|---|
| `slide` | PPT 演示文稿 | (无，默认使用系统风格；用户指定则透传) | 3~5 分钟 |
| `infographic` | 数据信息图 | (无，默认使用系统风格；用户指定则透传) | 2~4 分钟 |
| `video` | 视频播客 | (无) | 5~10 分钟 |
| `audio` | 纯音频播客 | (无) | 3~6 分钟 |
| `report` | 深度分析报告 | (无) | 1~3 分钟 |
| `mindmap` | 结构化思维导图 | (无) | 1~2 分钟 |
| `quiz` | 测验练习题 | (无) | 1~2 分钟 |
| `flashcards` | 记忆闪卡 | (无) | 1~2 分钟 |

### 2.2 API 调用链路 (两步走)

**Step A: 投递异步任务**
**Headers（必传）**：
- `authorization: skill`
- `x-user-id: {XG_USER_ID | appkey.userId}`（必传）
- `access-token: {XG_USER_TOKEN | appkey["access-token"]}`（必传）
- `personId: {XG_USER_PERSONID | appkey.personId}`（必传）
- `Content-Type: application/json`

```http
POST https://notex.aishuo.co/noteX/api/trilateral/autoTask
authorization: skill
x-user-id: {XG_USER_ID | appkey.userId}  # 必传
access-token: {XG_USER_TOKEN | appkey["access-token"]} # 必传
personId: {XG_USER_PERSONID | appkey.personId} # 必传
Content-Type: application/json

{
  "bizId": "skills_1709000000000", # 必填，不可为空
  "bizType": "TRILATERA_SKILLS", # 必填，不可为空
  "title":"标题",  # 必填，不可为空
  "skills": ["slide"], # 必填，不可为空
  "require": "默认风格", # 必填，不可为空
  "sources": [{"id": "src_001", "title": "标题", "content_text": "原文素材（必须完整，不得缩略/截断）..."}] # 必填，不可为空
}
```

*(响应返回 `taskId`)*

**Step B: 轮询结果直到完结**
```http
GET https://notex.aishuo.co/noteX/api/trilateral/taskStatus/{taskId}
```
*(每 60 秒轮询一次，最多 **20 次**，即最大超时时间 20 分钟；直到 `task_status` 为 `COMPLETED`，内部完成鉴权参数拼接后再把可访问链接提交给用户，不在话术中暴露 token 字段名)*

> 🌟 **大模型引导与越权拦截策略**：
> 关于如何向用户索要必要参数，以及如何礼貌拒绝意图越权（例如：当用户要求”生成 Excel 或下载成 Word 文件”时，应明确拒绝并引导转化成支持的『分析报告』或『思维导图』），请务必参考系统内置的设定话术档案：👉 [`examples/notex-creator.md`](./examples/notex-creator.md)

### 2.3 素材输入边界处理（文件 / URL / 混合输入）

当用户并非直接提供纯文本内容，而是通过**文件**或**URL**来指定创作素材时，需遵循以下预处理流程：

#### 场景 A：用户提供文件（PDF / PPT / Word / TXT 等）

1. **读取文件**：使用工具读取用户提供的文件内容，提取全部文本信息。
2. **内容摘要确认**：向用户展示提取到的关键内容摘要（标题、主要章节/要点），并询问：
   - “以上是我从文件中提取的核心内容，确认以此为素材生成 [PPT/脑图/...] 吗？”
   - 若用户有补充或修改要求，合并后再确认。
3. **确认后发起任务**：用户确认后，将提取内容作为 `sources[].content_text` 自动发起创作任务。

#### 场景 B：用户提供 URL

1. **访问并读取页面**：打开用户提供的 URL，充分理解页面内容并提取关键信息。
2. **内容摘要确认**：向用户展示从页面提取的核心内容摘要，并询问：
   - “以上是我从该链接中提取的核心内容，确认以此为素材生成 [PPT/脑图/...] 吗？”
3. **确认后发起任务**：用户确认后，将提取内容作为素材自动发起创作任务。

#### 场景 C：混合输入（文件/URL + 口头补充）

1. 优先读取文件或 URL 内容。
2. 将用户口头补充的要求与提取内容合并整理。
3. 向用户确认合并后的完整素材内容。
4. 确认后自动发起创作任务。

> **核心原则**：无论素材来源是什么，都必须先提取 → 再确认 → 最后生成。绝不在用户未确认素材内容的情况下直接发起任务。

### 2.4 素材完整性（强约束）

**在任何产物生成（PPT / 脑图 / 报告 / 音频 / 视频 / 测验 / 闪卡 / 信息图）前，`sources[].content_text` 必须是完整原文**，不得摘要、截断或压缩。

强约束规则：
1. **不得丢失内容**：`sources[].content_text` 必须包含全部原始信息，不能只保留提要或片段。
2. **内容过长处理**：可拆分为多条 `sources`，但必须保持原文顺序与语义完整，且总内容与原文等价。
3. **只有用户明确同意**时，才允许使用摘要或裁剪内容；默认必须全量。
4. **先理解再生成**：必须确认用户意图与素材范围后再提交任务。
5. **素材将作为后续 SRS/溯源信息**保存，任何缺失都会导致产物与记录失真。

---

## 3. OPS 运营数据洞察 (`ops-chat`)

专为内部系统后台打造的智能问答通道，对接 17 个底层观测本体工具（Function Calling），采用**短轮询 / 同步流式长连接**架构。

### 3.0 三要素（角色 / 能力 / 使用时机）

- 我是谁：OPS 运营智能助理，面向运营与管理场景提供数据问答服务。
- 我能做什么：调用运营数据工具链，输出用户、功能、告警、趋势等多维运营分析结果。
- 什么时候使用：当用户询问“运营数据、系统告警、用户活跃、功能使用、增长趋势”等问题时使用。
- 前置条件：调用前必须通过“1.1 统一前置鉴权规则”。

### 3.1 核心能力与权限
- 本技能原有的 `canViewOpsData` 权限强校验已移除，现允许通过鉴权的用户直接查阅。
- 覆盖大盘看板统计、科室/项目组活跃排行、精准追踪某医生的流失节点、异常报错根因聚合分析等。
- 新增支持“注册队列 + 幻灯片闭环”分析：可直接回答“某日期后注册用户是否创建过幻灯片、创建次数、是否分享、分享是否被查看及查看次数”。

### 3.2 API 调用链路 (单发同步等待)

此接口内部将执行多达数十步的 ReAct 循环推理，网络超时上限需严格设定为 **300,000ms (5分钟)**。


```http
POST https://notex.aishuo.co/noteX/api/ops/ai-chat
authorization: skill
x-user-id: {XG_USER_ID | appkey.userId}  # 必传
access-token: {XG_USER_TOKEN | appkey["access-token"]} # 必传
personId: {XG_USER_PERSONID | appkey.personId} # 必传
Content-Type: application/json

{
  "message": "帮我查一下最近一周的操作失误告警？"
}
```

**响应报文**：
```json
{
  "reply": "根据底盘数据，近期共发生了...",
  "historyCount": 3
}
```
*(注：服务端已自动记忆最近 6 轮对话上下文，客户端无需再次拼接历史)*

> 🌟 **大模型引导策略**：关于 17 个核心本体的逻辑链式拆解，以及遇到多名同姓氏用户时的追问确认协议，请查阅专属的管家设定指南： [`examples/ops-assistant.md`](./examples/ops-assistant.md)

### 3.3 关系路径输出规范（Ontology Explainability）

为了保证 OPS 问答“可解释、可复盘、可审计”，Agent 在数据收集完成后（情况 B）应附带：

1. `relationPath`：本次结论依赖的实体关系链（如 `User -> SlideTask -> TaskShare -> TaskShareView`）。
2. `entitySnapshot`：关键实体口径（仅用户名、部门、模块中文名等可展示字段）。
3. `summary`：最终数据摘要。

简化示例（由 Agent 内部输出）：

```json
{
  "relationPath": [
    { "step": 1, "from": "User", "relation": "CREATED", "to": "SlideTask", "constraint": "registeredAfter>=2026-03-20", "evidence": "ontology_getSlideLifecycleByRegistrationCohort.users[].slideCreatedCount" },
    { "step": 2, "from": "SlideTask", "relation": "SHARED_AS", "to": "TaskShare", "evidence": "ontology_getSlideLifecycleByRegistrationCohort.users[].shareLinkCount" },
    { "step": 3, "from": "TaskShare", "relation": "VIEWED_BY", "to": "TaskShareView", "evidence": "ontology_getSlideLifecycleByRegistrationCohort.users[].shareViewedCount" }
  ],
  "entitySnapshot": {
    "users": ["用户名+部门（不含ID）"]
  },
  "summary": "..."
}
```

约束：严禁在路径与快照中暴露 `token/x-user-id/personId/login/内部主键`。

### 3.4 Agent 闭环能力与场景覆盖（Plan + Reflect + Check）

为确保“运营问题可聊全、可聊准、可复盘”，ops-chat 在执行时应遵循以下闭环：

1. Plan（规划）：拆解主问题与子问题，先定义统一口径（时间范围、对象范围、统计粒度）。
2. Act（执行）：优先专用工具，最后才使用 `ontology_customQuery`；单次调用聚焦单一子问题。
3. Reflect（反思）：检查返回值是否覆盖当前子问题；遇到全 0/突增/突降时先做一次交叉验证。
4. Check（校验）：输出前确认维度覆盖完整、关键数字有 evidence、口径一致、无敏感字段泄露。

典型场景推荐链路：

- 注册队列转化（如“3月20号后注册用户是否创建/分享/被查看”）
  - `ontology_getSlideLifecycleByRegistrationCohort`
- 用户目录与对象盘点（如“现在一共有多少用户，全部列出来”）
  - `ontology_getUserDirectory`
- 用户分层与重点人群
  - `ontology_getActiveUsersRanking` → `ontology_getUserProfile` → `ontology_getUserActivity`
- 模块质量与故障影响
  - `ontology_getModuleStats` → `ontology_getFailureAnalysis` → `ontology_getAlerts`
- 组织经营与增长分析
  - `ontology_getDeptBreakdown` + `ontology_getUserGrowthTrend`
- 分享传播链路
  - `ontology_getSharingStats` 或 `ontology_getSlideLifecycleByRegistrationCohort`

---

## 4. Notebook 基础操作 (CRUD)

该能力用于回答”我有多少个笔记本”、”列出我所有笔记本”、”帮我创建一个笔记本”等基础操作请求。

### 4.0 三要素（角色 / 能力 / 使用时机）

- 我是谁：Notebook 管理助手，负责笔记本的查询、统计和创建操作。
- 我能做什么：查询笔记本数量和分类统计、分页列出笔记本列表、创建新笔记本。
- 什么时候使用：当用户询问”我有多少个笔记本”、”列出我的笔记本”、”帮我新建一个笔记本”等基础管理需求时使用。
- 前置条件：调用前必须通过”1.1 统一前置鉴权规则”。

### 4.1 接口一：笔记本数量统计（按分类）

```http
GET https://notex.aishuo.co/noteX/api/notebooks/category-counts
x-user-id: {XG_USER_ID | appkey.userId}  # 必传 
access-token: {XG_USER_TOKEN | appkey["access-token"]} # 必传
personId: {XG_USER_PERSONID | appkey.personId} # 必传
authorization: skill
```

返回各分类的笔记本数量，以及总数、收藏数、回收站数。

返回结构示例：
```json
{
  “resultCode”: 1,
  “data”: {
    “WORK_REPORT”: 3,
    “KNOWLEDGE_BASE”: 5,
    “AI_NOTES”: 2,
    “AI_INTELLIGENCE”: 1,
    “SHARED”: 4,
    “MIXED”: 6,
    “_favorite”: 3,
    “_deleted”: 1,
    “_total”: 21
  }
}
```

> 适用场景：用户问”我有多少个笔记本”、”各分类有多少”时，优先调用此接口。

### 4.2 接口二：笔记本分页列表

```http
GET https://notex.aishuo.co/noteX/api/notebooks?page=1&pageSize=20&sort=recent&type=all
x-user-id: {XG_USER_ID | appkey.userId}  # 必传
access-token: {XG_USER_TOKEN | appkey["access-token"]} # 必传
personId: {XG_USER_PERSONID | appkey.personId} # 必传
authorization: skill
```

支持的查询参数：

| 参数 | 说明 | 默认值 |
|---|---|---|
| `category` | 按分类筛选（如 `WORK_REPORT`、`KNOWLEDGE_BASE`、`all`） | 不筛选 |
| `favorite` | 只看收藏（`true`/`false`） | `false` |
| `deleted` | 查看回收站（`true`/`false`） | `false` |
| `page` | 页码 | `1` |
| `pageSize` | 每页数量 | `50` |
| `sort` | 排序方式：`recent`（更新时间）/ `title`（标题）/ `created`（创建时间） | `recent` |
| `type` | 可见范围：`owned`（我创建的）/ `collaborated`（协作的）/ `all`（全部） | `all` |

> 适用场景：用户问”列出我的笔记本”、”我有哪些知识库类型的笔记本”时使用。

### 4.3 接口三：创建笔记本

```http
POST https://notex.aishuo.co/noteX/api/notebooks
x-user-id: {XG_USER_ID | appkey.userId}  # 必传
access-token: {XG_USER_TOKEN | appkey["access-token"]} # 必传
personId: {XG_USER_PERSONID | appkey.personId} # 必传
authorization: skill
Content-Type: application/json

{
  “title”: “新笔记本标题”,
  “category”: “MIXED”,
  “description”: “可选描述”
}
```

请求参数：

| 参数 | 必填 | 说明 | 默认值 |
|---|---|---|---|
| `title` | 是 | 笔记本标题 | — |
| `category` | 否 | 分类枚举：`WORK_REPORT` / `KNOWLEDGE_BASE` / `AI_NOTES` / `AI_INTELLIGENCE` / `SHARED` / `MIXED` | `MIXED` |
| `coverType` | 否 | 封面类型 | `icon` |
| `coverValue` | 否 | 封面图标 | `📔` |
| `description` | 否 | 笔记本描述 | 空 |
| `parentNotebookId` | 否 | 父级笔记本 ID（未指定则自动挂载到用户根目录） | 自动 |

> 适用场景：用户说”帮我创建一个笔记本”、”新建一个叫 XX 的笔记本”时使用。

### 4.4 接口四：向笔记本添加来源（Source）

```http
POST https://notex.aishuo.co/noteX/api/notebooks/{notebookId}/sources
x-user-id: {XG_USER_ID | appkey.userId}  # 必传
access-token: {XG_USER_TOKEN | appkey[“access-token”]} # 必传
personId: {XG_USER_PERSONID | appkey.personId} # 必传
authorization: skill
Content-Type: application/json

{
  “title”: “来源标题（必传，不可为空）”, 
  “type”: “text”,
  content_text: “来源正文完整内容（必传，不可为空）”
}
```

请求参数：

| 参数 | 必填 | 说明 |
|---|---|---|
| `title` | **是** | 来源标题 |
| `type` | **是** | 来源类型，Skills 场景固定传 `”text”` |
| `content_text` | **是** | 来源正文内容（**必须完整传入，不可为空**，这是来源的核心数据） |

> ⚠️ **强约束**：`content_text` 虽然服务端不强制校验，但不传则来源无实际内容，后续解析、摘要、索引全部无法工作。Skills 场景下**视为必传**。

返回结构示例：
```json
{
  “resultCode”: 1,
  “data”: {
    “id”: “src_xxx”,
    “title”: “来源标题”,
    “type”: “text”,
    “notebookId”: “nb_xxx”,
    “contentText”: “...”,
    “createdAt”: “2026-03-12T10:00:00.000Z”
  }
}
```

> 适用场景：用户说”往这个笔记本里添加一条来源”、”把这段内容存到笔记本 XX 里”时使用。
> 权限约束：仅笔记本的 owner 或 admin 角色可以添加来源。

---

## 5. Notebook 来源索引与详情检索 (Index + Details)

该能力用于回答”查看我名下所有 Notebook 的所有文件/来源”这类请求，核心是先拉**索引树**，再按需拉**最小详情**。

### 5.0 三要素（角色 / 能力 / 使用时机）

- 我是谁：Notebook 来源检索助手，负责管理”来源索引”和”最小上下文定位”。
- 我能做什么：构建并本地缓存索引树（仅 ID+名称），并按 notebook/source 返回最小详情（仅 ID+名称）。
- 什么时候使用：当用户要查看”我名下全部来源、某 notebook 下所有来源、某个 source 的定位信息”时使用。
- 前置条件：调用前必须通过”1.1 统一前置鉴权规则”。

### 5.1 接口一：全量索引树（推荐先调用）

```http
GET https://notex.aishuo.co/noteX/api/notebooks/api/notebooks/sources/index-tree?type=all
x-user-id: {XG_USER_ID | appkey.userId}  # 必传
access-token: {XG_USER_TOKEN | appkey["access-token"]}  # 必传
personId: {XG_USER_PERSONID | appkey.personId} # 必传
authorization: skill
```

- 返回用户可访问范围内的 Notebook 树结构与每个 Notebook 的 Source 索引（仅 ID/名称）。
- `type` 支持：`all` | `owned` | `collaborated`，默认 `all`。

最小返回结构示例：
```json
{
  "generatedAt": "2026-03-10T09:00:00.000Z",
  "tree": [
    {
      "id": "nb_001",
      "name": "产品规划",
      "sources": [
        { "id": "src_101", "name": "需求评审纪要" }
      ],
      "children": []
    }
  ]
}
```

### 5.2 接口二：来源最小详情（按 notebookId 或 sourceId）

```http
GET https://notex.aishuo.co/noteX/api/notebooks/sources/details?notebookId={notebookId}
GET https://notex.aishuo.co/noteX/api/notebooks/sources/details?sourceId={sourceId}
x-user-id: {XG_USER_ID | appkey.userId}  # 必传
access-token: {XG_USER_TOKEN | appkey["access-token"]}  # 必传
personId: {XG_USER_PERSONID | appkey.personId} # 必传
authorization: skill
```

- `notebookId` 模式：返回该 Notebook 下所有 Source 的最小详情（仅 `ID + 名称`）。
- `sourceId` 模式：返回单个 Source 的最小详情（仅 `ID + 名称`），并附带所属 Notebook 的 `ID + 名称`。

> 注：这里的 `context ID` 即 Source ID。该接口用于给 AI 定位上下文，不返回正文大字段。

最小返回结构示例：
```json
{
  "mode": "source",
  "notebook": { "id": "nb_001", "name": "产品规划" },
  "contexts": [
    { "id": "src_102", "name": "会议纪要" }
  ]
}
```

### 5.3 建议工作流（给 AI 的默认流程）

1. 先调用 `index-tree` 构建索引。
2. 将索引落盘到本地缓存（覆盖写，确保全量更新）。
3. AI 根据用户问题在索引中定位 `notebookId/sourceId`。
4. 调用 `details` 拉取最小上下文信息（`ID + 名称`）用于二次决策。

### 5.4 本地缓存目录建议

```text
docs/skills/cache/notebook-source-index/
  └── {userId}/
      ├── index-tree.json
      └── details/
          ├── notebook-{notebookId}.json
          └── source-{sourceId}.json
```

### 5.5 全量定时刷新（必须全量，不做增量）

推荐脚本（见 `/scripts/source-index-sync.js`）：

```bash
# 若已设置环境变量 XG_USER_TOKEN/XG_USER_ID/XG_USER_PERSONID，可省略 --key
# 方式1（默认）：仅传 CWork Key，脚本内部自动完成授权并调用
node docs/skills/scripts/source-index-sync.js --mode index --base-url https://notex.aishuo.co/noteX --key <CWorkKey>

# 方式2：按 sourceId 拉取最小详情（仍只需 CWork Key）
node docs/skills/scripts/source-index-sync.js --mode detail --base-url https://notex.aishuo.co/noteX --key <CWorkKey> --source-id <sourceId>

# 每 60 分钟全量刷新一次索引（默认授权模式）
node docs/skills/scripts/source-index-sync.js --mode index --base-url https://notex.aishuo.co/noteX --key <CWorkKey> --interval-minutes 60
```

> 示例话术与调用流程参考：[`examples/notebook-source-index.md`](./examples/notebook-source-index.md)

---

## 6. NoteX 链接带 Token 打开 (Open NoteX URL)

该能力用于处理“帮我打开 NoteX”这类请求，目标是生成并返回**带 token 的可访问链接**，并在可行时自动拉起浏览器。

### 6.0 三要素（角色 / 能力 / 使用时机）

- 我是谁：NoteX 首页打开助手，负责把首页地址转换为可访问的授权链接。
- 我能做什么：生成 `https://notex.aishuo.co/?token=...` 最终链接，返回前端可直接使用，并可选自动打开浏览器。
- 什么时候使用：当用户说“帮我打开 NoteX / 打开这个 NoteX 链接”时使用。
- 前置条件：调用前必须通过“1.1 统一前置鉴权规则”。

### 6.1 输入输出约束

- 输入：默认不需要额外地址参数，固定打开 NoteX 首页路由。
- 输出：**必须**是 `https://notex.aishuo.co/?token=xxx` 形式的链接。
- 域名约束：仅允许 `https://notex.aishuo.co`。
- 对话约束：若环境变量缺失，不向用户索取 token；仅提示用户提供/确认 `CWork Key` 授权。
- 路由约束：该技能是“首页打开路由”，与创作任务返回的 `?skillsopen=task-...` 路由是两套不同入口。

### 6.2 默认执行流程

1. 固定使用首页路由 `https://notex.aishuo.co/`。
2. 优先读取环境变量（`XG_USER_TOKEN/XG_USER_ID/XG_USER_PERSONID`）；若缺失则用 `CWork Key` 换取。
3. 生成 `https://notex.aishuo.co/?token=...` 最终链接。
4. 把最终链接返回前端用户。
5. 若运行环境支持且用户允许，可自动打开浏览器访问该链接。
6. 若自动打开失败，不影响主流程，仍返回最终链接供用户手动打开。

### 6.3 脚本调用示例

```bash
# 若已设置环境变量 XG_USER_TOKEN/XG_USER_ID/XG_USER_PERSONID，可省略 --key
# 推荐：仅提供 CWork Key，内部自动换取 token 并生成首页链接
node docs/skills/scripts/notex-open-link.js --key <CWorkKey>

# 生成首页链接并自动打开浏览器（可选）
node docs/skills/scripts/notex-open-link.js --key <CWorkKey> --auto-open true

```

> 示例话术参考：[`examples/notex-open-link.md`](./examples/notex-open-link.md)

---

## 7. NoteX 上下文沉淀与写入 (Save Context to NoteX)

该能力用于回答"把这段聊天记录/这份资料存到我的 NoteX 笔记本里"这类请求，目标是将 AI 整理的结构化信息沉淀到现有的 Notebook，或为其新建一个 Notebook 进行知识沉淀。

### 7.0 三要素（角色 / 能力 / 使用时机）

- 我是谁：NoteX 知识沉淀助手，负责将带有高价值信息的文本沉淀、归档到用户的 NoteX 笔记库中。
- 我能做什么：调用创建 API (`POST /api/notebooks`) 自动新建笔记本并存入内容，或者调用追加 API (`POST /api/notebooks/{notebookId}/sources`) 将新资料追加到用户已有的指定笔记本中。
- 什么时候使用：当用户明确表达"保存、归档、记录、存入 NoteX"等意图时使用。
- 前置条件：调用前必须具备有效鉴权（优先环境变量；缺失则通过 `CWork Key` 换取）。

### 7.1 明确存储路径

- 当用户未能指定具体存储的笔记本名称时，应当主动询问："希望存入一个【全新】的笔记本，还是追加到【现有】的笔记本中？"。
- 接口在调用完成之后，返回 `notebookId` 及/或 `sourceId` 信息作为查验凭据。

### 7.2 脚本调用示例

```bash
# 若已设置环境变量 XG_USER_TOKEN/XG_USER_ID/XG_USER_PERSONID，可省略 --key
# 推荐：向已有的笔记本中追加内容并携带标题（要求指定 --notebook-id 和 --mode append）
node docs/skills/scripts/notex-save-context.js --mode append --key <CWorkKey> --notebook-id <nb_001> --title "今日会议纪要" --content "1. 决定继续推进A..."

# 推荐：创建全新的笔记本并添加首条笔记内容（要求指定 --mode create）
node docs/skills/scripts/notex-save-context.js --mode create --key <CWorkKey> --title "知识库A" --content "核心沉淀点：..."
```

> 示例话术参考：[`examples/notex-save-context.md`](./examples/notex-save-context.md)

---

## 8. 示例索引 (Examples Index)

本目录用于给 Agent 提供可复用的话术与流程模板。每个示例都包含三要素：
- 我是谁
- 我能做什么
- 什么时候使用

同时，所有示例都遵循同一前置鉴权约束：
- 对用户只暴露 `CWork Key` 授权动作
- 不向用户暴露 `token/x-user-id/personId/login` 等实现细节

并遵循统一环境约束：
- 仅允许生产域名：`https://notex.aishuo.co/noteX`

### 8.1 示例与技能映射

| 能力 | 适用场景 | 对应示例 | 对应 SKILL 主文档 |
|---|---|---|---|
| 内容创作（Asynchronous Creator） | 生成 PPT、信息图、视频、音频、报告、脑图、测验、闪卡 | [`notex-creator.md`](./examples/notex-creator.md) | 第 2 节 |
| OPS 运营洞察（ops-chat） | 查询运营指标、告警、用户行为、组织分析 | [`ops-assistant.md`](./examples/ops-assistant.md) | 第 3 节 |
| Notebook 基础操作（CRUD） | 查询笔记本数量、列表、创建笔记本、添加来源 | （直接参考 SKILL.md） | 第 4 节 |
| Notebook 来源索引与详情 | 查询名下来源索引、按 notebook/source 拉最小详情 | [`notebook-source-index.md`](./examples/notebook-source-index.md) | 第 5 节 |
| NoteX 链接带 Token 打开 | 打开 NoteX 首页并确保带 token | [`notex-open-link.md`](./examples/notex-open-link.md) | 第 6 节 |
| 上下文沉淀与写入 (Save Context) | 将 AI 生成的对话结果或长文本快速沉淀为 NoteX 新笔记或追加来源 | [`notex-save-context.md`](./examples/notex-save-context.md) | 第 7 节 |

### 8.2 脚本映射

| 目标 | 推荐脚本 |
|---|---|
| 创作 + OPS 联调 | [`./scripts/skills-run.js`](./scripts/skills-run.js) |
| 来源索引落盘与定时全量刷新 | [`./scripts/source-index-sync.js`](./scripts/source-index-sync.js) |
| 上下文沉淀与追加 | [`./scripts/notex-save-context.js`](./scripts/notex-save-context.js) |
| NoteX 链接补 token 并打开 | [`./scripts/notex-open-link.js`](./scripts/notex-open-link.js) |

### 8.3 推荐执行顺序

1. 先按第 1.1 节做鉴权预检。
2. 再根据任务类型选择对应示例。
3. 按示例中的调用顺序发起接口请求。

---

## 9. 相关依赖文件说明

| 文件/目录 | 用途描述 |
|---|---|
| [`/examples/`](./examples/) | **强烈建议阅读**。存放了四大能力（创作 / OPS / 来源索引 / 上下文沉淀）的系统示例。 |
| [`/examples/README.md`](./examples/README.md) | 示例目录索引。用于快速定位“我是谁 / 我能做什么 / 什么时候使用”及对应接口、脚本、调用顺序。 |
| [`/examples/notex-creator.md`](./examples/notex-creator.md) | 创作能力示例（skill: slide/infographic/video/audio/report/mindmap/quiz/flashcards）。 |
| [`/examples/ops-assistant.md`](./examples/ops-assistant.md) | OPS 能力示例（skill: ops-chat）。 |
| [`/examples/notebook-source-index.md`](./examples/notebook-source-index.md) | 第三块能力示例：如何先拉索引、落盘缓存、再按 notebookId/sourceId 拉最小详情。 |
| [`/examples/notex-save-context.md`](./examples/notex-save-context.md) | 第四块能力示例：如何新建笔记本并存入内容，或者向现有笔记本追加来源。 |
| [`/examples/notex-open-link.md`](./examples/notex-open-link.md) | 第五块能力示例：如何生成 `https://notex.aishuo.co/?token=...` 并返回前端，必要时自动打开浏览器。 |
| [`/scripts/skills-run.js`](./scripts/skills-run.js) | Node.js 测试桩代码。开发者可通过此脚本直接在终端体验鉴权、发起任务与并发轮询的全套完整生命周期。 |
| [`/scripts/source-index-sync.js`](./scripts/source-index-sync.js) | Notebook 来源索引树/详情检索脚本，支持本地落盘与定时全量刷新（覆盖写）。 |
| [`/scripts/notex-save-context.js`](./scripts/notex-save-context.js) | 上下文沉淀追加脚本，支持新建笔记本与追加现有来源功能。 |
| [`/scripts/notex-open-link.js`](./scripts/notex-open-link.js) | NoteX 链接补 token 脚本，支持返回最终链接与可选自动打开浏览器。 |
