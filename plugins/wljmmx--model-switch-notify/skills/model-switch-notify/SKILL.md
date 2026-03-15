---
name: model-switch-notify
description: "模型切换通知。当agent使用的模型发生变化时，第一时间通知当前会话用户。触发条件：agent首次回复、模型切换后首次对话、用户询问当前模型。所有agent可使用的公共skill。"
---

# 模型切换通知 Skill

## 概述

当 agent 使用的模型发生变化时，第一时间通过当前 channel 通知用户，简要说明切换后的模型名称。

## 工作原理

### 模型信息来源

从运行时上下文获取当前模型信息：
- 运行时信息：`Runtime: model=xxx` (在系统提示中提供)
- 默认模型：`default_model` 配置

### 检测机制

1. **首次回复**：agent 在首次回复时，检查当前模型并简要说明
2. **模型切换**：当检测到模型与上次记录不同时，通知用户
3. **用户询问**：用户询问当前模型时，告知模型信息

### 通知时机

```
会话开始 → 检查模型 → 记录到状态 → 回复用户（附带模型信息）

模型切换 → 下次回复 → 检测变化 → 通知用户（新模型信息）
```

## 使用方法

### 步骤 1：获取当前模型信息

从 Runtime 信息中读取：
```
Runtime: agent=coder | host=xxx | model=ollama/qwen3.5-code | ...
```

### 步骤 2：检查模型变化

调用检查脚本：
```bash
python3 ~/.openclaw/skills/model-switch-notify/scripts/check_model.py \
  --agent "coder" \
  --current-model "ollama/qwen3.5-code" \
  --channel "qqbot" \
  --session "qqbot:c2c:xxx"
```

返回：
```json
{
  "changed": true,
  "previousModel": "ollama/glm-5:cloud",
  "currentModel": "ollama/qwen3.5-code",
  "shouldNotify": true,
  "notifyMessage": "老板，模型已切换，当前使用：ollama/qwen3.5-code"
}
```

### 步骤 3：通知用户

如果 `shouldNotify` 为 `true`，在回复中包含模型信息通知。

## 通知模板

### 首次回复模板

```
当前使用模型：ollama/qwen3.5-code
```

### 模型切换模板

```
老板，模型已切换，当前使用：ollama/qwen3.5-code
```

### 简短模板（推荐）

```
老板，当前模型：ollama/qwen3.5-code
```

## 目录结构

```
~/.openclaw/skills/model-switch-notify/
├── SKILL.md              # 本文档
├── scripts/
│   └── check_model.py    # 模型检查脚本
└── README.md             # 使用说明
```

## 状态存储

每个 agent 的上次模型记录存储在：
```
~/.openclaw/workspace/{agentId}/.model-state.json
```

文件内容：
```json
{
  "lastModel": "ollama/qwen3.5-code",
  "lastNotify": "2026-03-13T10:42:00",
  "channel": "qqbot",
  "session": "qqbot:c2c:xxx"
}
```

## Agent 集成指南

### 在回复中包含模型信息

当以下情况发生时，agent 应在回复中简要说明模型：

1. **首次回复**：告知用户当前使用的模型
2. **模型切换后**：第一时间通知用户
3. **用户询问**：直接回答当前模型

### 回复格式

```
[正常回复内容]

老板，当前模型：ollama/qwen3.5-code
```

### 注意事项

1. **不要过度通知**：只在首次或切换时通知，不要每次回复都提
2. **简洁明了**：一句话说明模型名称即可
3. **保持友好**：使用用户熟悉的称呼

## 配置选项

可在 agent 的 `USER.md` 中配置通知偏好：

```markdown
## 模型通知偏好
- model_notify: true/false  # 是否启用模型切换通知
- model_notify_style: brief/detailed  # 通知风格
```

## 示例

### 场景 1：首次对话

**用户**：你好

**Agent**：你好！有什么可以帮你的？

老板，当前模型：ollama/qwen3.5-code

### 场景 2：模型切换

**系统**：模型从 glm-5:cloud 切换到 qwen3.5-code

**用户**：请帮我写个函数

**Agent**：老板，模型已切换，当前使用：ollama/qwen3.5-code

好的，我来帮你写函数...

### 场景 3：用户询问

**用户**：你现在用的什么模型？

**Agent**：当前使用的是 **ollama/qwen3.5-code** 模型，这是专门针对代码任务优化的本地模型。

---

## 更新日志

- **v1.0.0** (2026-03-13): 初始版本