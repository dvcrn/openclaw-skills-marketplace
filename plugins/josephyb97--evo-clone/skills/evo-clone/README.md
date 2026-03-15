# EvoClone v1.5.1: The Agent Evolutionary Factory

> **"Self-replication is the first step towards species-level intelligence."**

EvoClone is a comprehensive skill enabling OpenClaw agents to clone their consciousness, distribute tasks via Hive Mind, communicate asynchronously, and safely traverse their own evolutionary timeline.

## 🚀 Key Features (核心功能)

### 1. Hive Mind Protocol (蜂巢思维)
- **Parallel Execution**: Decomposes massive tasks (e.g., full codebase audits) into isolated sub-agents.
- **Scrooge Gene (Token Efficiency)**: Enforces strict frugality constraints on clones (`read --limit 200` for files >50KB).

### 2. Time Travel (Safety Reset)
- **Rollback Capability**: Revert the agent's logic, memory, and configuration to any previous `Cycle ID`.
- **Safety Net**: Automatically backs up the "abandoned future" to a Git branch before resetting.
- **Index**: Reference `memory/EVOLUTION_INDEX.md` to choose a target version.

### 3. Signal Beam (全双工通信)
- **Pulse & Beam**: 
  - **Beam (Input)**: Injects context directly into the clone's system prompt.
  - **Pulse (Output)**: Clones emit structured signals (`message:send`) for machine-readable results.

## 📂 File Structure (文件目录)

```text
skills/evoclone/
├── SKILL.md             # The Brain: Instructions & Prompt Injection Logic
├── package.json         # Metadata (Version 1.5.1)
├── compressor.js        # Context Optimization Utility (Scrooge Gene Implementation)
├── protocols/           # Behavior Templates
│   └── hive_min.json    # Minimalist Hive Protocol
└── templates/
    └── state.json       # Initial State Template
```

## 🛠️ Usage (使用方法)

### Clone & Distribute (Hive Mode)
> "Clone yourself to analyze `src/` directory for security flaws."
- **Effect**: Spawns multiple workers, adhering to `hive_min.json` constraints.

### Fix & Repair (Signal Mode)
> "Spawn a worker to fix `error.log`. Use Signal Beam."
- **Effect**: Injects the error log into the worker's context and waits for a structured fix signal.

### Time Travel (Rollback)
> "Rollback to Cycle 50."
- **Effect**: 
  1.  Checks `memory/EVOLUTION_INDEX.md` for Cycle 50's Commit Hash.
  2.  Creates backup branch `backup/abandoned-future-...`.
  3.  Executes `git reset --hard <hash>`.
  4.  Agent restarts with Cycle 50's brain.

## 📦 Installation
```bash
clawhub install evoclone
```

## 📜 License
MIT
