---
name: agent-memento
description: "Tick-Driven Autonomous Production Factory for LLMs. A framework for long-running agents using Cron/Heartbeats and physical Markdown checklists to prevent OOM and context decay."
---

# Agent Memento (Tick-Driven Autonomous Execution)

> “Don't build AI that tries to remember everything. Build systems that make AI read the blueprint anew every 5 minutes.”

当我们在聊天框里让大模型“写一个游戏”时，开头总是美好的。但随着代码超过 2000 行，模型开始：
- **失忆症 (Amnesia)**：忘记了自己定义的接口，开始凭空捏造。
- **幻觉重构 (Hallucination)**：自信满满地输出一堆根本没有跑过的“完美”代码。
- **上下文核爆 (Resource Overload)**：为了修一个小 Bug，强行覆盖整个大文件，导致内存耗尽 (OOM)。

**核心原则：把“全知全能的超级 Agent”降级为无数个“只有 5 分钟记忆的、无情的 Tick 机器”。**

## The Methodology：双态智能与外部状态机
1. **状态剥离（物理外置大脑）**：Agent 不在内存池中记忆项目历史，长线记忆与当前状态全部下放至物理文件（`MASTER_PLAN.md` 验证清单）。
2. **架构师态（The Architect）**：人类与大模型在主 Session 里讨论，将宏大叙事翻译成 `MASTER_PLAN.md` 里的每一个 `[ ]`。
3. **泥瓦匠态（The Tick Worker）**：Cron 脚本每隔几分钟自动唤醒一个全新的、绝对专注的短命进程。它只寻找清单里**第一个未打钩的 `[ ]`**，修好它，执行物理验证，然后离线。

## 系统化实施方法 (How to Deploy)

当用户说要启动 Memento 流水线时，使用以下命令：

```bash
bash skills/agent-memento/scripts/init_memento.sh <ProjectName>
```

### 铁血纪律 (Execution Sandbox)
作为一个被 Memento 唤醒的 Tick Worker（或要求你写 Tick 脚本时），你必须遵循：
1. **防爆底线 (Surgical Edits Only)**：严禁输出完整文件要求覆写。必须通过精准定位工具修改。
2. **拒绝脑内验算 (Evidence-based Audit)**：跑脚本看真实退出码，没有 `Exit Code 0`，不许在 `[ ]` 上画一个 `x`。
3. **不要静默空转 (No Silent Ghosting)**：卡死时，把死亡原因写进 `TICK_STATUS.md` 中。

## Security & Transparency

### Data Access — Exactly What Is Read
- Reads `<project-dir>/docs/MASTER_PLAN.md` to determine the current task.
- Reads source code files within the target project directory as needed to accomplish the task.

### Data Written
- Creates project scaffolding (`MASTER_PLAN.md`, `TICK_STATUS.md`, `*_tick.sh`).
- Updates `[ ]` to `[x]` in `MASTER_PLAN.md` via tick worker.
- Edits source files within the target project directory.

### Persistence & Autonomous Scheduling
- The `init_memento.sh` script generates a bash script intended to be run via `cron` (e.g., `*/5 * * * *`). The user must manually add this to their crontab to enable autonomous execution. 
- You can stop the agent at any time by removing the entry from `crontab -e` or killing the background process.

### Credentials
- Operates entirely locally. Relies on the default `openclaw agent` command, utilizing the underlying system's existing LLM configurations. No new keys are requested or stored.

### Network Access
- No outbound network access is initiated by the core framework scripts themselves, except when the user's specific project tasks require installing packages (e.g., `npm install`). 
