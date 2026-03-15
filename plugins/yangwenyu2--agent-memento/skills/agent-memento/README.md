<div align="center">

<img src="./assets/banner.png" alt="Agent Memento Banner" width="100%">

# 🧠 Agent Memento

**Tick-Driven Autonomous Production Factory for LLMs**

*“Don't build AI that tries to remember everything. Build systems that make AI read the blueprint anew every 5 minutes.”*

[![OpenClaw Skill](https://img.shields.io/badge/OpenClaw-Skill-blue.svg)](https://github.com/openclaw/openclaw)
[![ClawHub](https://img.shields.io/badge/ClawHub-Install-ff69b4.svg)](https://clawhub.com/yangwenyu2/agent-memento)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[English](./README.md) | [简体中文](./README_zh.md)

</div>

---

## ⚡ The "Aha!" Problem: Chat Windows Can't Build Aircraft Carriers

You ask an AI Agent to build a massive project. The first 10 minutes are magic. But by line 2,000, the magic rots into a nightmare:
- **Context Amnesia:** The AI forgets the architecture it designed an hour ago and hallucinates non-existent APIs.
- **The "LGTM" Delusion:** The AI confidently tells you "I fixed the bug," but the code doesn't even compile.
- **The OOM Nuke:** To fix a typo in a 3,000-line file, the AI tries to rewrite the *entire file* in one message, blowing up the context window, causing Out-Of-Memory (OOM) crashes, and taking down your entire gateway.

**Continuous chatbots are engineering poison for long-term generation.**

## 💡 The Solution: Memento Execution 

Inspired by the movie *Memento*, we destroy the omniscient, memory-heavy persistent Agent.
We replace it with an army of **ruthless, amnesiac, short-lived Tick Workers** that live only to read a physical blueprint, hammer exactly one nail, verify it, and die.

### ⚙️ How Memento Works (The Dual-Mode Intelligence)
| Mode | Actor | Role | Memory |
| :--- | :--- | :--- | :--- |
| **🏛️ The Architect** | You + Chat AI | Design macro-architecture, pivot strategies, and write checklists into `MASTER_PLAN.md`. | Infinite (Human Brain) |
| **🔨 The Tick Worker** | Cron / Watchdog | Wakes up every 5 mins, reads the blueprint, executes ONE `[ ]` task, proves it works, and dies. | 5 Minutes (Zero Context) |

#### Three Ironclad Disciplines enforced by Memento:
1. **Surgical Edits (Anti-OOM)**: Forced to use `sed` or AST parsing instead of rewriting entire files.
2. **Evidence-Based (Anti-Hallucination)**: Strictly forbidden from checking off `[x]` unless physical proof exists (a passing `jest` test, a returning `curl` 200 OK, etc.).
3. **Anti-Ghosting (Asynchronous Reporting)**: If stuck, it writes the blocker into a `TICK_STATUS.md` blackbox instead of silently dying.

### 🕹️ Observable Steering (Zero-Prompt Intervention)
Tired of yelling at your AI in the chat, *"No! You wrote it wrong again!"*? 
With Agent Memento, you steer the entire autonomous process simply by editing a text file. Want to pivot the app's entire UI? Just silently change the checkboxes in `MASTER_PLAN.md`. The next Tick Worker will instantly adapt to the new reality like a river changing course.

---

## 🚀 Quick Start (One-Line Scaffold)

Instantly tear down the Chatbot paradigm and spin up an autonomous Memento factory inside OpenClaw:

### 1. Install from ClawHub
```bash
clawhub install agent-memento
```

### 2. Initialize a Project
```bash
cd ~/.openclaw/workspace
bash skills/agent-memento/scripts/init_memento.sh MyHugeProject
```

This automagically injects:
1. `projects/MyHugeProject/docs/MASTER_PLAN.md` (Your physical canvas for global architecture).
2. `TICK_STATUS.md` (The asynchronous Black Box where dying Workers report their blockers).
3. A **ready-to-deploy background worker script** at `scripts/MyHugeProject_tick.sh` loaded with draconian system prompts.

### 3. Unleash the Cron
Write out your plan in `MASTER_PLAN.md`, then add the tick to your system crontab:
```bash
*/5 * * * * bash /root/.openclaw/workspace/scripts/MyHugeProject_tick.sh
```

**Wake up to a finished project, built brick by verified brick.**

---

## 🛠 Prerequisites
- [OpenClaw CLI](https://github.com/openclaw/openclaw) properly installed.
- (Optional but Recommended) A testing harness (Jest, PyTest, etc.) so the worker can strictly adhere to the Evidence-based standard.

## 📜 License
MIT License.
