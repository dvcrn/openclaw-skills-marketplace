# prompt-token-counter

[English](README.md)

一个 **OpenClaw skill**，用于统计 token 数量并估算 API 成本。

## 这个 Skill 能做什么

加载后，Agent 可以：

| 能力 | 使用场景 |
|------|----------|
| **统计 token** | 「这段 prompt 有多少 token？」、「X 的 token 长度」 |
| **估算成本** | 「这段文字用 GPT-4 要多少钱？」、「Claude 的 API 成本」 |
| **审计 OpenClaw 工作区** | 「我的工作区用了多少 token？」、「哪些 memory/persona/skills 消耗 token？」 |
| **对比模型** | 「对比不同模型的 token 成本」、「哪个模型更便宜？」 |

### OpenClaw Token 审计

该 skill 帮助识别工作区各组件的 token 消耗：

- **Memory 与 persona**：AGENTS.md、SOUL.md、IDENTITY.md、USER.md、MEMORY.md、TOOLS.md 等
- **Skills**：`~/.openclaw/skills/` 或 `workspace/skills/` 下的每个 SKILL.md

审计示例：
```bash
python -m scripts.cli -m gpt-4o -c -f AGENTS.md -f SOUL.md -f MEMORY.md
```

## 何时触发

- 用户询问 token 数量、prompt 长度、API 成本
- 用户提到 OpenClaw 上下文大小或工作区 token 使用
- Agent 需要在变更前后审计 token 消耗

## 快速参考

```bash
python -m scripts.cli -m gpt-4 "Hello, world!"
python -m scripts.cli -f input.txt -m claude-3-opus -c
python -m scripts.cli -l   # 列出 300+ 模型
```

MIT
