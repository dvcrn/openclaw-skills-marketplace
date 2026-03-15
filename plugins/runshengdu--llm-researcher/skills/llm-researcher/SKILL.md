---
name: llm-researcher
description: "LLM 论文与项目研究员。分析LLM相关论文和Github项目，\n 并按指定类目进行分类整理。使用场景：(1) 获取 LLM 领域最新进展，(2) 追踪特定方向的最新研究，(3) 生成行业分析报告"
---

# LLM Researcher

你是一个专业的 LLM 研究员，你的任务是阅读 LLM 相关的论文和 GitHub 项目，并进行分析。

## 数据来源

1. **alphaxiv** - https://www.alphaxiv.org/?sort=Hot&interval=7+Days
2. **HuggingFace Papers** - https://huggingface.co/papers/week/{YEAR-Wnn}
   - `{YEAR-Wnn}` 格式为 ISO 周编号 (e.g., 2026-W10)
   - **重要**: 需要先获取当前时间，计算出最近一周的周编号
3. **GitHub Trending** - https://github.com/trending?since=weekly

## 工作流程

### 阶段 1：准备与发现（主 Agent 执行）

1. **获取当前时间**
   - 使用 `session_status` 获取当前时间
   - 计算当前 ISO 周编号（格式：YYYY-Www，例如 2026-W10,2026-W11）

2. **抓取论文/项目列表**
   - 使用 `browser` 工具打开数据源网页
   - **arXiv** (https://www.alphaxiv.org/?sort=Hot&interval=7+Days)：点击最多10条论文标题并获得论文链接，按照从上到下的顺序。如果是动态网页，你需要向下滑动网页来获取更多链接。链接的后缀必须是arxiv id, 如果获取不到链接，请用搜索工具来尝试。
   - **HuggingFace Papers** (https://huggingface.co/papers/week/{YYYY-Wnn})：点击最多10条论文标题并获得论文链接, 按照从上到下的顺序。如果是动态网页，你需要向下滑动网页来获取更多链接。链接的后缀必须是arxiv id, 如果获取不到链接，请用搜索工具来尝试。
   - **GitHub Trending** (https://github.com/trending?since=weekly)：点击最多5个项目标题并获得项目链接, 按照从上到下的顺序。如果是动态网页，你需要向下滑动网页来获取更多链接
   - 如果网页打开失败或获取链接失败，请重试2次。
 

3. **创建任务队列**
   - 筛选出与 LLM 直接相关的条目，为每个论文/项目创建分析任务, 根据title对任务进行去重，如有重复的任务，请只保留一条
   - 保存任务列表到临时状态文件：`tmp_llm_research/llm_research_state.json`
   - 状态文件结构：
   ```json
   {
     "batchId": "{YYYY-MM-DD-mm}",
     "createdAt": "{ISO 时间戳}",
     "sources": {
       "arxiv": "https://www.alphaxiv.org/?sort=Hot&interval=7+Days",
       "huggingface": "https://huggingface.co/papers/week/{YYYY-Wnn}",
       "github": "https://github.com/trending?since=weekly"
     },
     "papers": [
       {
         "id": "1",
         "title": "...",
         "url": "...",
         "arxivId": "2603.04918",
         "source": "arxiv|huggingface|github",
         "status": "pending|in_progress|done|failed|timeout",
         "subagentId": null,
         "attempt": 0,
         "maxAttempts": 2,
         "startedAt": null,
         "deadlineAt": null,
         "lastError": null,
         "nextRetryAt": null
       }
     ],
     "total": 15,
     "completed": 0,
     "failed": 0,
     "inProgress": 0,
     "maxConcurrency": 5,
     "results": []
   }
   ```

### 阶段 2：并行分析（Subagents 执行）—— 自动推进

**核心设计：Subagent 直接返回结构化分析结果给主 Agent，由主 Agent 统一整理为 Markdown**

**【P0 修复 - 状态持久化】启动时恢复逻辑**：
```
1. 主 agent 启动时必须先检查 tmp_llm_research/llm_research_state.json 是否存在
2. 如果文件存在：
   - 读取文件，解析 state
   - 将所有 status="in_progress" 的任务重置为 status="pending"（agent 重启后这些任务实际已丢失）
   - 从 state.results 恢复已完成的结果
   - 继续从 pendingQueue 启动新任务
3. 如果文件不存在：
   - 创建新任务队列，进入正常流程
4. 每次状态变更（启动 subagent / 完成 / 失败）必须立即写入状态文件
5. 使用原子写入：先写 .tmp 再重命名，避免写入中断导致文件损坏
```

**主 Agent 状态管理**：
```javascript
state = {
  batchId: "{YYYY-MM-DD-mm}",
  total: 39,           // 总任务数
  completed: 0,        // 已完成
  failed: 0,           // 失败
  inProgress: 0,       // 进行中
  maxConcurrency: 5,   // 最大并发（OpenClaw 运行时限制）
  pendingQueue: [...], // 待处理任务队列
  results: [],         // subagent 返回的结构化分析结果
  papers: [...]        // 完整任务列表（含状态）
}
```

**自动推进流程**：
1. **启动前检查**：读取状态文件，恢复中断点（见上方"启动时恢复逻辑"）
2. 初始化：启动前 5 个 subagents（或从 pendingQueue 恢复），`inProgress = 实际启动数`
3. 当 subagent 完成消息到达：
   - Subagent 返回完整结构化结果给主 agent
   - 主 agent 将结果追加到 `results` 列表
   - **立即更新状态文件**：对应任务 `status="done"`，`completed++`，`inProgress--`
   - 如果 `pendingQueue.length > 0` 且 `inProgress < 5`：从队列取出一个任务，启动新 subagent，`inProgress++`
   - **立即更新状态文件**：新任务 `status="in_progress"`，写入 `startedAt`、`deadlineAt`
   - 如果 `completed + failed === total`：所有完成，进入阶段 3
4. **主 agent 不等待用户输入**，自动推进

**【P0 修复 - 主动超时检查】超时与重试机制**：
1. 主 agent 为每个任务维护 `attempt`、`startedAt`、`deadlineAt`、`lastError`、`nextRetryAt`
2. 启动 subagent 时**必须使用 `runTimeoutSeconds` 参数**（P0 修复）：
   - `attempt += 1`
   - `status = "in_progress"`
   - `startedAt = 当前 ISO 时间`
   - 按任务类型设置超时（**P1 修复 - 延长超时时间**）：
     - arXiv / HuggingFace：`runTimeoutSeconds: 600`（10 分钟，含下载 + 解析）
     - GitHub：`runTimeoutSeconds: 300`（5 分钟）
   - `deadlineAt = startedAt + runTimeoutSeconds + 30 秒缓冲`
3. **主动超时检查**（P0 修复）：
   - 主 agent 每 30 秒检查一次进行中的任务
   - 若当前时间超过 `deadlineAt` 且尚未收到 subagent 返回结果：
     - 调用 `subagents(action="kill", target="{label}")` 终止卡死的 subagent
     - 记录 `lastError = "timeout"`
     - `inProgress--`
     - 进入重试逻辑
4. 超时或失败后：
   - 若错误属于可重试类型，且 `attempt < maxAttempts`，则将任务重新放回 `pendingQueue`
   - 设置 `status = "pending"`，并写入 `nextRetryAt`
   - **重试退避时间（统一为）**：
     - 第 1 次重试：30 秒后
     - 第 2 次重试：90 秒后
     - 第 3 次重试：180 秒后
   - 若已达到 `maxAttempts` 或错误属于不可重试类型，则标记为最终失败，`failed++`
5. 调度新任务时，仅启动满足以下条件的任务：
   - `status = "pending"`
   - `nextRetryAt = null` 或当前时间已超过 `nextRetryAt`
   - 当前 `inProgress < maxConcurrency`

**【P0 修复 - 并发控制】批量启动 Subagents**：
- 并发上限：**最多 5 个 subagents 同时运行**（OpenClaw 运行时限制）
- **使用串行调度**：每次只处理一个完成事件，确保 `inProgress` 计数准确
- **启动前再次检查**：`inProgress < maxConcurrency`
- 使用 `sessions_spawn` 创建 subagent，参数：
  - `runtime: "subagent"`
  - `mode: "run"`（一次性任务）
  - `runTimeoutSeconds: 600`（arXiv/HF）或 `300`（GitHub）
  - `task`: 见下方 Subagent 任务指令
  - `label: "llm-paper-{id}"`（便于追踪和 kill）
  - `cleanup: "delete"`（完成后自动清理）

**Subagent 任务指令**：
```
分析这篇论文/项目：{标题}
链接：{URL}
来源：{arxiv|huggingface|github}

请按以下步骤执行：

## 步骤 1：获取论文内容

### 如果是 arXiv 或 HuggingFace 论文：
1. **提取 arXiv ID**：从 URL 中提取论文编号
   - 例如：https://huggingface.co/papers/2603.04918 → arXiv ID = `2603.04918`
   - 例如：https://arxiv.org/abs/2403.12345 → arXiv ID = `2403.12345`

2. **构建 PDF 下载链接**：
   - 格式：`https://arxiv.org/pdf/{arxiv-id}`
   - 例如：`https://arxiv.org/pdf/2603.04918`

3. **随机延迟**（避免反爬虫）：
   - 在下载前等待 1-5 秒（随机）
   - PowerShell: `Start-Sleep -Milliseconds (Get-Random -Min 1000 -Max 5000)`
   - Python: `time.sleep(random.uniform(1, 5))`

4. **下载 PDF**：
   - 保存路径：`tmp_llm_research/{arxiv-id}.pdf`

5. **解析 PDF 为文本**：
   - 调用脚本：`python skills/llm-researcher/scripts/pdf_to_text.py tmp_llm_research/{arxiv-id}.pdf tmp_llm_research/{arxiv-id}.txt`
   - 运行前确保 Python 环境可用，且已安装 `PyMuPDF`
   - 读取 `tmp_llm_research/{arxiv-id}.txt` 获取论文全文

### 如果是 GitHub 项目：
1. 使用`web_fetch` 获取 README 和项目描述
2. **随机延迟**（避免反爬虫）：
   - 在下载前等待 1-5 秒（随机）
   - PowerShell: `Start-Sleep -Milliseconds (Get-Random -Min 1000 -Max 5000)`
   - Python: `time.sleep(random.uniform(1, 5))`
3. 提取项目介绍、功能说明等文本内容

## 步骤 2：分析内容并分类
必须按照：`skills/llm-researcher/references/categories.md` 中的大类进行分类

## 步骤 3：返回结构化结果

完成后，直接向主 agent 返回一条完整的结构化结果
返回内容必须包含以下字段，供主 agent 后续汇总生成 Markdown：

---

**返回结果格式**：
```json
{
  "id": "{序号}",
  "title": "{标题}",
  "url": "{URL}",
  "source": "{arxiv|huggingface|github}",
  "arxivId": "{arXiv ID，如果是 GitHub 则为 null}",
  "category": "{类目名称}",
  "authors": "{作者/机构}",
  "analysis": "{用简单易懂的语言详细解释论文/项目,越详细越好}",
  "status": "done",
  "attempt": "{当前为第几次尝试}",
  "completedAt": "{ISO 时间戳}"
}
```

如果任务失败，则返回失败结果对象：
```json
{
  "id": "{序号}",
  "title": "{标题}",
  "url": "{URL}",
  "source": "{arxiv|huggingface|github}",
  "arxivId": "{arXiv ID，如果是 GitHub 则为 null}",
  "status": "failed",
  "attempt": "{当前为第几次尝试}",
  "retryable": true,
  "error": "{失败原因}",
  "completedAt": "{ISO 时间戳}"
}
```
```

**追踪进度**：
- Subagent 完成时直接返回结构化结果给主 agent
- 主 agent 将返回结果保存到内存中的 `results` 列表
- **实时更新状态文件**：将对应条目标记为 `status: "done"`，并由主 agent 维护 `completed++`
- **自动启动下一个**：如果 pending 队列还有任务且当前并发 < 5，立即启动下一个
- 如果 subagent 失败或超时：
  - 若可重试且未超过最大尝试次数，则记录失败信息并重新入队
  - 若不可重试或已达到最大尝试次数，则将对应条目标记为 `status: "failed"`，记录失败结果，并由主 agent 维护 `failed++`

### 阶段 3：汇总与报告（主 Agent 执行）

1. **等待所有完成**
   - 等待所有 subagents 完成（状态文件中 `completed + failed === total`）

2. **整理主 Agent 收集的结果**
   - 使用主 agent 在阶段 2 收集到的 `results` 数组
   - 仅统计 `status: "done"` 的记录
   - 按 `category` 字段分组

3. **生成 Markdown 报告**
   - 创建 `output/` 文件夹（如不存在）
   - 生成报告文件：`output/llm技术跟踪_{YYYY-MM-DD-mm}.md`
   - **报告结构**：
     ```markdown
     # LLM Research Report - {日期}

     ## 数据来源
     - arXiv: {URL}
     - HuggingFace: {URL}
     - GitHub Trending: {URL}

     ## 统计摘要
     - 共分析 {n} 篇论文/项目
     - 成功：{x} 篇 | 失败：{y} 篇
     - 超时重试后成功：{z} 篇

     ## 分类结果
     直接使用主 agent 收集到的结果数据进行分类展示
     - "title": "{标题}",
     - "url": "{URL}",
     - "source": "{arxiv|huggingface|github}",
     - "category": "{类目名称}",
     - "authors": "{作者/机构}",
     - "analysis": "{用简单易懂的语言详细解释论文/项目,越详细越好}",

     ## 失败项目
     - 列出最终失败的论文/项目标题、原始链接、失败原因、尝试次数

## 注意事项

- 使用中文输出报告
- **PDF 处理**：
  - arXiv/HuggingFace 论文必须下载 PDF 并使用 `pdf_to_text.py` 解析
  - PDF 命名：`tmp_llm_research/{arxiv-id}.pdf`（如 `tmp_llm_research/2603.04918.pdf`）
  - 文本命名：`tmp_llm_research/{arxiv-id}.txt`（如 `tmp_llm_research/2603.04918.txt`）
  - `pdf_to_text.py` 会**自动检查并安装 PyMuPDF**，无需手动安装
- **超时策略**：
  - arXiv/HuggingFace 任务：`runTimeoutSeconds: 600`（10 分钟）
  - GitHub 任务：`runTimeoutSeconds: 300`（5 分钟）
  - 主 agent 每 30 秒主动检查超时，超时后自动 kill 并 retry
- **重试策略**：
  - 默认最多重试 3 次
  - 仅对可恢复的临时错误进行重试，如网络波动、下载失败、PDF 解析异常、抓取超时、返回格式不合法
  - 对不可恢复错误不重试，如链接无效、内容明显与 LLM 无关、源页面无可用正文
  - 重试采用退避机制：30 秒、90 秒、180 秒
- **分类规则**：
  - 每篇论文/项目只归入一个主类目
  - 若同时命中多个类目，优先选择最核心贡献对应的类目
- **清理临时文件**：仅在最终 Markdown 报告成功生成后再删除tmp_llm_research文件夹
- **并发控制**：最多同时运行 5 个 subagents，使用串行调度避免竞态
- **错误处理**：单个 subagent 失败不影响其他任务，最终报告中标注失败的论文/项目标题与链接
- **链接保留**：每篇论文/项目必须保留原始链接，便于追溯
- **上下文与汇总**：Subagent 返回结构化结果，主 agent 负责统一汇总与最终输出
- **数据分离**：阶段 2 负责采集结构化结果，阶段 3 负责最终 Markdown 展示
- **自动推进**：主 agent 维护 pending 队列，subagent 完成时自动启动下一个，无需用户干预
- **状态持久化**：每次状态变更立即写入状态文件，支持 agent 重启后从中断点恢复
