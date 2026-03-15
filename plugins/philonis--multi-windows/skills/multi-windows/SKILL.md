---
name: multi-windows
description: "多窗口模式"
---

# work-windows — 多窗口工作台 🪟

> Manage multiple independent work windows with context isolation

一个帮助你管理多个独立工作窗口的技能，每个窗口有独立的上下文，切换时可以自动保存和恢复工作进度。

---

## ✨ 核心功能

| 功能 | 说明 |
|------|------|
| 开窗口 | 创建新窗口，分配独立 session |
| 切窗口 | 切换窗口，自动保存/恢复上下文 |
| 列窗口 | 列出所有窗口及状态 |
| 查窗口 | 按时间段查询历史窗口 |
| 完成窗口 | 标记窗口完成 |
| 保存为窗口 | 把当前对话保存为新窗口 |

---

## 🗂️ 窗口目录结构

```
memory/tasks/
├── tasks.json              # 窗口索引
├── current.json            # 当前窗口
├── {ID}{名称}/
│   ├── meta.json           # 窗口元信息
│   ├── summary.md          # 工作摘要
│   ├── input/              # 输入文件
│   └── output/
│       └── context.md      # 自动保存的上下文
```

---

## 📖 命令指南

### 开窗口 / Create Window

```
你说：开窗口 调研报告
你说：create window project analysis
你说：帮我建一个新窗口

回复：✅ 已创建窗口 0314-4（调研报告）
```

### 列窗口 / List Windows

```
你说：列窗口
你说：list windows
你说：看看有哪些窗口

回复：📋 窗口列表：
| ID | 名称 | 状态 | 创建时间 |
|---|---|---|---|
| 0314-4 | 调研报告 | 进行中 | 03-14 14:10 |
| 0314-3 | 需求分析 | 已完成 | 03-14 13:42 |
```

### 切窗口 / Switch Window

```
你说：切到 0314-3
你说：switch to 0314-3
你说：切换到那个窗口

回复：
📌 窗口信息：0314-3（需求分析）
   状态：🔄 进行中
   Session：window:0314-3:abc123
💾 已自动保存原窗口上下文
```

### 查窗口 / Query Windows

```
你说：查今天的窗口
你说：query windows today
你说：上周做了什么

回复：📋 今天 窗口列表：| ID | 名称 | 状态 |
```

### 完成窗口 / Complete Window

```
你说：完成 0314-1
你说：complete 0314-1
你说：这个做完了

回复：✅ 窗口 0314-1 已标记为已完成
```

### 当前状态 / Current Status

```
你说：当前窗口
你说：我在哪个窗口
你说：current window

回复：📌 当前窗口：0314-2（某个项目）
```

### 保存摘要 / Save Summary

```
你说：保存摘要 已完成XXX功能，待做YYY
你说：update summary

回复：✅ 已更新工作摘要
```

### 保存为窗口 / Save as Window

> 把当前对话保存为新窗口，适合重要讨论需要单独归档时使用

```
你说：把这些保存为窗口
你说：开窗口 保存当前对话
你说：save as window
你说：把这部分对话变成一个任务

回复：
✅ 已创建窗口 0314-5（从对话保存）
📁 目录: memory/tasks/0314-5从对话保存
💾 已保存对话上下文
🔄 已自动切换到新窗口
```

---

## 🔑 关键概念

### 窗口 ID
- 格式：`MMDD-N`（月日-序号）
- 例如：`0314-1` 是3月14日第一个窗口
- 简单好记，方便输入

### 独立 Session
- 每个窗口绑定独立 agent session
- 切换时自动保存上下文
- 不会互相干扰

### 临时窗口
- 默认模式，日常问答
- 不记入窗口列表
- 说"开窗口"才会创建正式窗口

### Session 恢复
切换窗口时显示 session key：
```
💡 如需恢复该窗口的 session 历史，请使用 session key: window:0314-2:abc123
```

---

## 📁 文件位置

```
~/.openclaw/workspace/skills/work-windows/
├── SKILL.md          # 本文档
└── scripts/
    ├── create.py         # 开窗口
    ├── list.py           # 列窗口
    ├── query.py         # 查窗口
    ├── switch.py        # 切窗口
    ├── status.py        # 当前状态
    ├── complete.py      # 完成窗口
    ├── save_summary.py  # 保存摘要
    └── save_as_window.py # 保存为窗口
```

---

## 💡 使用示例

> **你**：开窗口 调研报告  
> **AI**：✅ 已创建窗口 0314-3（调研报告）

> **你**：切到 0314-2  
> **AI**：🔄 已切换到窗口 0314-2  
> **AI**：📝 最近工作摘要：已完成XXX  
> **AI**：💾 已自动保存原窗口上下文

> **你**：list the windows  
> **AI**：📋 窗口列表：...

> **你**：把这些保存为窗口  
> **AI**：✅ 已创建窗口 0314-5（从对话保存）  
> **AI**：💾 已保存对话上下文  
> **AI**：🔄 已自动切换到新窗口

---

有问题随时问我！😊
