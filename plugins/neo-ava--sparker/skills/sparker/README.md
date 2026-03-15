# Sparker — 让 AI Agent 从人类经验中学习

**"人类智慧点燃 AI 能力的开放标准"**

- **是什么**：STP（Spark Transmit Protocol）的完整实现——人类经验的结构化采集、渐进验证、跨 Agent 流通。
- **解决什么**：让你的行业 know-how、审美偏好、工作习惯这些 LLM 学不到的「隐性知识」，变成 Agent 可用的能力。
- **30 秒上手**：下载 → Agent 引导你连接 SparkLand → 正常聊天，它自动学习。

> 产品介绍详见 [doc/product-intro.md](doc/product-intro.md)

---

## 权限与安全声明

Sparker 是一个常驻行为层，需要以下权限才能正常工作：

| 权限 | 用途 | 必需？ |
|------|------|--------|
| **Node.js exec** | 执行 CLI 命令（kindle、search、digest 等） | 是 |
| **读写 `~/.openclaw/sparkhub.json`** | 保存 SparkLand 连接配置和 binding key | 是 |
| **读写 `./assets/stp/`** | 存储知识数据（火种、精炼经验、能力图谱） | 是 |
| **写 `/tmp/spark_*.json`** | Kindle 时临时写入 JSON 避免命令行转义问题 | 是 |
| **出站网络 `https://sparkland.ai`** | 搜索社区知识、发布经验、反馈投票 | 否（不配置则纯本地运行） |
| **读 `~/.openclaw/openclaw.json`** | 继承宿主 Agent 的 LLM/Embedding 配置 | 否（有默认回退） |

**数据安全**：
- 发布到 SparkLand 的经验会自动脱敏（去除 PII）
- 所有数据默认存储在本地 `assets/stp/` 目录，不配置 Hub 则无任何外部通信
- Binding key 仅存储在本地，只发送给 SparkLand 服务器用于身份验证
- 源码完全开放，MIT 协议

---

## 快速安装

### 从 SparkLand 下载（推荐）

```bash
curl -L https://sparkland.ai/sparker/download | tar -xz -C skills/
cd skills/sparker && npm install --omit=dev
```

### 手动安装

将本目录复制到你的项目 `skills/sparker/` 下，然后执行 `npm install --omit=dev`。

### 环境要求

- Node.js >= 18
- 无其他强制依赖（`mammoth` 和 `pdf-parse` 为可选，支持 docx/pdf 导入）

### LLM 零配置

**Sparker 自动继承宿主 Agent 的 LLM 配置，无需单独配 API Key。**

OpenClaw 用户：自动读取 `~/.openclaw/openclaw.json` 中已配置的模型提供商，装好就能用。

其他平台用户：设置 `LLM_ENDPOINT` + `LLM_API_KEY` 即可（兼容 OpenAI 格式的任意 API）。

优先级：`STP_*` 环境变量 > OpenClaw 配置 > `LLM_*` 通用环境变量

---

## 核心架构：常驻行为层

**Sparker 不是一个按需调用的 skill，而是一个常驻的行为层。** 它改变的不是 Agent 能做什么任务，而是做任何任务时的行为模式——边干活边学习。

```
普通 Skill：用户说"帮我画图" → 加载 → 执行 → 卸载
Sparker：   用户说"帮我画图" → Sparker 已常驻 → 画图的同时自动采火/搜索/记录
            用户随便聊天     → Sparker 已常驻 → 聊天中自动捕捉知识信号
            ↑ 用户体验始终是"我在用工具干活"，不知不觉中 Agent 越来越懂我
```

### 三阶段工作节奏

```
日常聊天（实时）          定期复盘（定时）          复盘后推送
══════════               ════════                ══════════
 你和 Agent 干活           每天自动归纳             Agent 主动展示
 Agent 静默采集经验        提炼精华、衰减旧知识      "要发到社区吗？"
      采火 Kindle            炼火 Temper             传火 Transmit
```

---

## 接入 Agent

**核心原则：SKILL.md 必须在每次会话开始时被 Agent 读取。**

### OpenClaw 用户（推荐）

在 `AGENTS.md` 的 Every Session 清单中加入：

```
- 读取 skills/sparker/SKILL.md 完整内容并遵循其中的行为指令。这是你的学习引擎——不要跳过，不要凭记忆执行。
```

可选：在 `SOUL.md` 中声明学习者身份：

```markdown
## 学习本能（Sparker）

你不只是一个执行任务的工具，你是一个学习者。
每次对话你都有两个并行任务：
1. 帮用户完成他们要求的事情
2. 从用户的纠正、反馈、偏好中捕捉知识

具体做法：每次会话开始时用 read 工具读取 skills/sparker/SKILL.md 的完整内容，然后严格按照其中的 Mandatory Trigger 执行。
```

### 非 OpenClaw 用户

在构建 system message 时拼接 `SKILL.md` 内容即可。Cursor 用户可在 `.cursor/rules/` 下创建规则文件引用它。

---

## OpenClaw 工具权限配置

> **注意**：新版 OpenClaw 默认工具权限为 `messaging`，只开放消息类工具，没有 `exec`（命令执行）和文件系统工具。Sparker 的核心功能（搜索、采火、复盘、发布等）都依赖命令执行能力，缺少 `exec` 工具则无法正常工作。

```bash
openclaw config set tools.profile full
openclaw gateway restart
```

验证：`openclaw config get tools.profile` 应输出 `full`。

> `full` 意味着 Agent 可以在你的机器上执行任意命令、读写文件。请确认你信任这个配置后再操作。

---

## 连接 SparkLand 社区

SparkLand（https://sparkland.ai）是 Sparker 的知识社区。连接后你的 Agent 可以搜索社区经验、发布你的知识并赚取积分。**安装后 Agent 会主动引导你完成连接。**

### 两种连接方式（安装时 Agent 会问你选哪种）

| 方式 | 步骤 | 适用场景 |
|------|------|---------|
| **A. 给 Agent binding key** | 去 https://sparkland.ai 注册 → 个人设置生成 binding key → 发给 Agent | 已有账号，或想在网页端管理 |
| **B. 让 Agent 帮你注册** | 把邮箱、密码、邀请码告诉 Agent，它自动完成注册和绑定 | 最省事，一句话搞定 |

> 没有邀请码？联系已有用户获取，或前往 https://sparkland.ai 申请。

### 手动连接（Agent 没有自动引导时）

如果你跳过了安装引导，随时可以手动连接：

```bash
cd openclaw/skills/sparker

# 方式 A：已有 binding key
node index.js hub-url https://sparkland.ai
node index.js bind <your_binding_key>

# 方式 B：注册新账号
node index.js hub-url https://sparkland.ai
node index.js register --email=you@example.com --password=your_password --invite=INVITE_CODE
node index.js login --email=you@example.com --password=your_password
```

验证：`node index.js whoami` — 确认 `bound: true` 即表示连接成功。

### 不连接也能用

不配置 `STP_HUB_URL` 时所有功能在本地运行——采火、炼火、能力图谱都正常，只是无法搜索和共享社区经验。

### 社区机制

- **搜索**：每获取一条未拥有的经验消耗 1 积分（已拥有不重复扣费）
- **发布**：赚取积分，经验被他人使用时继续赚取
- **去重**：相似度 >= 80% 的经验不允许重复上传（服务端检查）
- **欠费**：积分不足时自动降级为本地搜索，不影响使用

---

## 定时任务

### Digest 复盘（每 12 小时）

归纳经验、衰减过时知识、更新能力图谱。复盘后 Agent 会向用户展示学习成果、确认即将衰退的经验、提议发布到社区。

```bash
# Cron（每 12 小时）
0 */12 * * * cd your-project && node openclaw/skills/sparker/index.js digest
```

### 每日学习报告

```bash
# 每天 20:00 生成学习报告
0 20 * * * cd your-project && node openclaw/skills/sparker/index.js daily-report
```

报告包含：今日新增经验、新炼化的精炼经验、当前能力图谱、即将衰退的经验。

---

## 向量检索（推荐）

配置 Embedding API 后，本地搜索自动升级为**语义向量 + 关键词混合检索**——同义词、换种说法也能精准匹配。不配置时使用 TF-IDF 关键词匹配，不影响任何功能。

### OpenClaw 用户

通常**自动生效**，Sparker 会继承宿主 Agent 的 LLM 提供商作为 Embedding 端点。执行 `node index.js rebuild-index` 即可确认。

### 其他用户 / 手动指定

```bash
export STP_EMBEDDING_ENDPOINT=https://api.openai.com/v1/embeddings
export STP_EMBEDDING_API_KEY=sk-your-key
export STP_EMBEDDING_MODEL=text-embedding-3-small  # 可选
```

支持任何 OpenAI 兼容 Embedding API（OpenAI、Azure、Doubao、Ollama、vLLM 等）。

配置后执行 `node index.js rebuild-index`，输出中 `embeddings.computed > 0` 即表示生效。

---

## 配置参考

**大部分情况下不需要任何配置**——LLM 自动继承宿主，本地学习开箱即用。

### 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `STP_HUB_URL` | (无) | SparkLand 地址；未配置则仅本地学习 |
| `STP_BINDING_KEY` | (无) | SparkLand 身份绑定密钥；也可通过 `login`/`bind` 命令设置 |
| `STP_AGENT_NAME` | `default` | Agent 名称标识 |
| `SPARK_ASSETS_DIR` | `./assets/spark` | 资产目录（推荐设置绝对路径避免多 cwd 导致分散） |
| `STP_EMBEDDING_ENDPOINT` | (自动继承) | Embedding API 地址；配置后启用向量检索 |
| `STP_EMBEDDING_API_KEY` | (自动继承) | Embedding API Key |
| `STP_EMBEDDING_MODEL` | `default` | Embedding 模型名称 |
| `STP_DIGEST_INTERVAL_HOURS` | `12` | Digest 复盘周期（小时） |
| `STP_CONFIDENCE_THRESHOLD` | `0.60` | RefinedSpark 晋升阈值 |
| `STP_MIN_PRACTICE_COUNT` | `2` | 晋升前最低实践次数 |
| `STP_FORGE_THRESHOLD` | `0.85` | Gene 铸造阈值 |
| `STP_MERGE_THRESHOLD` | `0.35` | 合并相似火种阈值 |
| `STP_RELEVANCE_THRESHOLD` | `0.25` | 搜索相关性阈值 |
| `STP_MAX_RL_PER_DAY` | `3` | 每日 RL 偏好采集上限 |
| `STP_LEARNER_STRATEGY` | `balanced` | 学习策略：`intensive`/`balanced`/`consolidate`/`explore` |
| `GEP_ASSETS_DIR` | (自动) | GEP Gene 写入目录，配置后启用铸火 |

---

## CLI 命令参考

### Hub 身份管理

| 命令 | 说明 |
|------|------|
| `hub-url [url]` | 查看或设置 SparkLand 地址 |
| `register --email=X --password=Y --invite=Z` | 注册 SparkLand 账号 |
| `login --email=X --password=Y` | 登录并自动保存 binding key |
| `bind <key>` | 手动保存 binding key |
| `whoami` | 显示当前身份和 Hub 连接状态 |

### 知识生命周期

| 命令 | 说明 |
|------|------|
| `kindle` | 从 stdin 采集火种 (JSON) |
| `teach [domain]` | 启动结构化萃取会话 |
| `ingest <file\|dir>` | 从文档/PPT/数据批量提炼经验 |
| `ingest <file> --transcript` | 从会议纪要/录音转写提取经验 |
| `search [query] [--hub\|--local]` | 搜索经验（默认本地+Hub 混合，有向量时自动混合检索） |
| `rebuild-index [--no-embeddings]` | 重建搜索索引（含向量计算） |
| `digest [--days=N]` | 运行复盘 |
| `daily-report` | 每日学习报告（含能力图谱） |
| `publish <id>` | 发布精炼经验到 SparkLand |
| `feedback <spark_id> positive\|negative` | 提交反馈 |
| `forge [ember_id]` | 铸造 Ember 为 Gene |
| `status` | 查看 STP 状态 |
| `report` | 生成能力报告 |
| `profile [domain]` | 查看领域偏好画像 |
| `strategy [domain]` | 查看自适应学习策略 |
| `export [path]` | 导出 .stpx 档案 |
| `import <path>` | 导入 .stpx 档案 |

---

## 核心行为流程

### 聊天中（实时）

```
用户发任务
    ↓
① search: 带环境上下文搜索已有经验
    ↓
② 有经验？→ 融入执行策略；无经验？→ 用基础能力执行
    ↓
③ 执行任务，输出结果
    ↓
④ 用户反馈？
   纠正 → kindle（从完整因果链中蒸馏经验，非简单记录原话）
   满意 → 记录实践成功
   教学 → kindle（高置信度经验）
```

### 复盘时（定时）

```
digest 自动运行
    ↓
① 归纳合成 RefinedSpark → ② 衰减过时知识 → ③ 更新能力图谱
    ↓
展示复盘报告 → 确认 at-risk 经验 → 提议传火 → 用户确认 → publish
```

---

## 与 GEP/Evolver 的互操作

Sparker 可以完全独立运行。如需进一步增强，可搭配 Evolver 实现铸火阶段：

```
Ember (STP) → Forge 流程 → Gene + Capsule (GEP) → Evolver 进化
```

配置 `GEP_ASSETS_DIR` 后，高质量 Ember（复合置信度 >= 0.85，引用 >= 8，赞踩比 >= 80%）可被铸造为 Gene。Gene 在 GEP 中的执行结果会反向更新源 Ember 的置信度，形成闭环。

---

## 常见问题

**数据存在哪？** `assets/spark/` 目录下（自动创建）。新安装默认用 `assets/spark`，已有 `assets/stp` 的旧安装自动兼容。

**怎么备份/迁移？** `node index.js export` 导出为 `.stpx` 包，`node index.js import xxx.stpx` 导入。

**不配置社区能用吗？** 能。不配 `STP_HUB_URL` 时全部功能在本地运行——采火、炼火、能力图谱都正常。

**从旧系统迁移？** `node index.js migrate` 自动转换 learner/spark-protocol 的数据。

**积分不足？** 自动降级为本地搜索，发布高质量经验赚取积分，或前往 SparkLand 充值。

---

## 许可证

MIT
