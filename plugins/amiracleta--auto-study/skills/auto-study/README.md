[English](README.md) | [简体中文](README.zh-CN.md)

# Auto-Study

Auto study skill is an agent skill designed for **web-based learning platforms** such as **yuketang**, **xuexitong**, **pintia**, and other **question-answering scenarios**.

It enables the agent to use learning platforms in a browser, read text or images, return answers, choose options, fill in blanks, and perform similar actions. It uses an isolated browser profile to preserve login state, reduce potential security risks, and support background execution.

It currently supports **Windows** or **WSL**, and uses **Google Chrome on Windows**.

## Preview

**Yuketang**

`user: Finish these 50 OOP-6 questions, but don't submit them yet`

https://github.com/user-attachments/assets/816565a6-a28b-4a12-a4c5-e75b99978868

**Xuexitong**

`user: Open Xuexitong`

`user: Finish the chapter quizzes for 24.1-24.3 and submit them immediately`

*wait for some time...*

`agent:`

```text
24.1 - 24.3 completed. Chapter quiz results:
 - 24.1: 100
 - 24.2: 100
 - 24.3: 100
```

**Other usage examples**

`user: Give me the answers for the 4.1 chapter quiz`

`user: Briefly analyze each question`

## Install the Skill

### Let your agent handle it

Just tell your agent: `Help me install this skill, https://github.com/AmiracleTa/Auto-Study-Skill`

---

### Manual Installation

#### Copy the repository

Copy this repository into your agent's `skills` folder.

**OpenClaw:** `~/.openclaw/workspace/skills`

**Codex:** `~/.codex/skills`

#### Install dependencies

- **Google Chrome** (Windows)
- [Agent Browser CLI](https://github.com/vercel-labs/agent-browser)
- [Agent Browser Skill](https://clawhub.ai/MaTriXy/agent-browser-clawdbot)

## Behavior

- By default, it returns answers directly without extra explanation.
- Unless explicitly requested, it does not submit automatically after finishing.

For detailed behavior and strategy, see [SKILL.md](SKILL.md).

## Default Configuration

- CDP port: `9344`
- Profile root directory: `%LOCALAPPDATA%\\AutoStudy\\browser`

## Workflow

1. Start or connect to Chrome using a specific CDP port
2. Read the browser page and status
3. Perform corresponding actions according to user requests

## Detailed Strategies

- [SKILL.md](SKILL.md) Core strategies
- [references/xuexitong.md](references/xuexitong.md) Xuexitong specific instructions
- [references/yuketang.md](references/yuketang.md) Yuketang specific instructions
- [references/pintia.md](references/pintia.md) Pintia specific instructions
- [references/runtime-windows.md](references/runtime-windows.md) Windows runtime instructions
- [references/runtime-wsl.md](references/runtime-wsl.md) WSL runtime instructions
- [references/browser.md](references/browser.md) Browser instructions

## Acceptable Use

When using this skill, you are responsible for ensuring compliance with applicable laws, school or institutional rules, and platform terms of service.

This skill is designed for: **knowledge learning, ordinary practice, and browser-based answering assistance**

Do not use it for **proctored exams, unauthorized access, bypassing technical restrictions, or any other disallowed automation**.

---

***AI is not a human being. Use auto-submit with caution.***
