# 模型切换通知 Skill

## 功能

当 agent 使用的模型发生变化时，第一时间通知当前会话用户。

## 快速使用

### 检查模型变化

```bash
python3 ~/.openclaw/skills/model-switch-notify/scripts/check_model.py check \
  --agent "coder" \
  --current-model "ollama/qwen3.5-code" \
  --channel "qqbot" \
  --session "qqbot:c2c:xxx"
```

### 获取当前模型

```bash
python3 ~/.openclaw/skills/model-switch-notify/scripts/check_model.py get \
  --agent "coder"
```

### 重置状态

```bash
python3 ~/.openclaw/skills/model-switch-notify/scripts/check_model.py reset \
  --agent "coder"
```

## 返回示例

### 首次使用

```json
{
  "changed": false,
  "previousModel": null,
  "currentModel": "ollama/qwen3.5-code",
  "shouldNotify": true,
  "notifyMessage": "当前使用模型：ollama/qwen3.5-code",
  "firstTime": true
}
```

### 模型切换

```json
{
  "changed": true,
  "previousModel": "ollama/glm-5:cloud",
  "currentModel": "ollama/qwen3.5-code",
  "shouldNotify": true,
  "notifyMessage": "老板，模型已切换，当前使用：ollama/qwen3.5-code",
  "firstTime": false
}
```

### 无变化

```json
{
  "changed": false,
  "previousModel": "ollama/qwen3.5-code",
  "currentModel": "ollama/qwen3.5-code",
  "shouldNotify": false,
  "notifyMessage": "",
  "firstTime": false
}
```

## Agent 集成

在回复前检查模型状态：

```python
# 从 Runtime 信息获取当前模型
current_model = "ollama/qwen3.5-code"  # 从 Runtime 获取

# 检查是否需要通知
result = check_model(agent_id, current_model, channel, session)

# 如果需要通知，在回复中包含
if result["shouldNotify"]:
    reply = f"{reply}\n\n{result['notifyMessage']}"
```

---

版本: 1.0.0
更新: 2026-03-13