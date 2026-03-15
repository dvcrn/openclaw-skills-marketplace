# Token Pilot

OpenClaw Agent 自动省 Token 技能。纯 Node.js，跨平台，零依赖。

## 5 分钟快速优化

### 第 1 步：安装

```bash
clawhub install token-pilot
```

### 第 2 步：扫描当前状态

```bash
node ~/.openclaw/skills/token-pilot/scripts/optimize.js
```

脚本会自动扫描你的**所有 workspace**、cron 任务、agent 配置，输出每项的优化建议和预估节省量。

### 第 3 步：一键清理（安全）

```bash
node ~/.openclaw/skills/token-pilot/scripts/optimize.js --apply
```

自动执行：
- 把 workspace 根目录的 .js/.txt/.log/.cmd 等临时文件移到 `scripts/` 子目录
- 删除已完成 bootstrap 后遗留的 BOOTSTRAP.md

**只做安全操作，不改配置文件，不改 SOUL.md。**

### 第 4 步：替换臃肿的 AGENTS.md（最大收益！）

```bash
node ~/.openclaw/skills/token-pilot/scripts/optimize.js --template
```

会输出一个 ~300 token 的精简版 AGENTS.md 模板。复制后替换你的 `~/.openclaw/workspace/AGENTS.md`。

默认 AGENTS.md 约 2000 tok，替换后**每次会话省 ~1700 tok**。

### 第 5 步：按建议手动调整（如适用）

**有 cron 任务？**
```bash
node ~/.openclaw/skills/token-pilot/scripts/optimize.js --cron
```
会告诉你哪些 job 该加 `lightContext`、哪些该用便宜模型、哪些 prompt 太长。

**有多个 agent？**
```bash
node ~/.openclaw/skills/token-pilot/scripts/optimize.js --agents
```
会建议 main agent 用最好模型，团队 agent 降到中档。

**查配置是否到位？**
```bash
node ~/.openclaw/skills/token-pilot/scripts/audit.js --config
```
5 项评分：bootstrapMaxChars、bootstrapTotalMaxChars、heartbeat interval、activeHours、compaction。

### 第 6 步：完成

装好后 **6 条行为规则自动生效**，Agent 会在交互中自动：
- 先 peek 再全读（省读取量）
- 压缩工具返回结果（省输出）
- 简短回答简单问题
- 不重复读已读文件
- 批量发起独立工具调用
- 用 edit 代替 write

无需额外配置，无需记住任何命令。

---

## 预期效果

| 场景 | 节省 |
|------|------|
| 首次优化（替换 AGENTS.md + 清理） | **~2000-5000 tok/session** |
| 6 条运行时规则 | **15-30% 运行时 token** |
| cron 模型分层（如有） | **cron 费用 -70~90%** |
| agent 模型分层（如有多 agent） | **交互费用 -70~80%** |
| lightContext（如有轻量 cron） | **每 job 省 2000-5000 tok** |

## 插件协同（自动检测，没装也不影响）

装了以下技能会自动获得额外优化，没装则用内置兜底：

- **qmd** → 搜索代替盲读文件
- **smart-agent-memory** → 查历史避免重复调查
- **coding-lead** → ACP 磁盘上下文省 90%
- **multi-search-engine** → 精准搜索引擎选择

检测协同状态：
```bash
node ~/.openclaw/skills/token-pilot/scripts/audit.js --synergy
```

## 全部命令

```bash
SKILL=~/.openclaw/skills/token-pilot

# 优化
node $SKILL/scripts/optimize.js               # 全扫描 + 建议
node $SKILL/scripts/optimize.js --apply       # 安全自动清理
node $SKILL/scripts/optimize.js --template    # 精简 AGENTS.md 模板
node $SKILL/scripts/optimize.js --cron        # cron 优化
node $SKILL/scripts/optimize.js --agents      # agent 模型分层

# 审计
node $SKILL/scripts/audit.js --all            # 全量审计
node $SKILL/scripts/audit.js --config         # 配置评分
node $SKILL/scripts/audit.js --synergy        # 插件协同

# 目录
node $SKILL/scripts/catalog.js                # 生成技能索引
```

Windows 用户把 `~` 替换为 `%USERPROFILE%`，或用绝对路径。

所有命令自动发现 `~/.openclaw/` 下全部 `workspace-*` 目录，新增 workspace 零配置覆盖。
