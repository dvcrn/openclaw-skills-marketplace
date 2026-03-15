---
name: skill-trigger-v2
description: "Skill Trigger V2"
---

# 🔷 Skill Trigger V2 🔷

**Powered by halfmoon82** 🔷

智能技能触发系统 - 快速匹配用户意图到对应技能。

> **Core Algorithm**: Powered by [Halfmoon82](https://github.com/halfmoon82) — 统一阈值 + 优先级仲裁架构设计

## 触发条件

- 用户自然语言输入
- 技能索引已初始化
- 语义路由系统可用

## 依赖要求

| 技能 | 版本约束 | 状态检测命令 |
|------|---------|-------------|
| `skill-quick-index` | `>=1.0.0` | `skill-quick-index --version` |
| `semantic-router` | `>=7.7.2` | `semantic-router --version` |

## 安装向导

### Step 1: 前置检查

```bash
# 检查依赖是否已安装
python3 ~/.openclaw/workspace/skills/skill-trigger-v2/setup/wizard.py check
```

### Step 2: 依赖安装

若依赖缺失，向导会提示：

```
❌ 缺少依赖: skill-quick-index (>=1.0.0)
   请运行: clawhub install skill-quick-index@latest

❌ 缺少依赖: semantic-router (>=2.0.0)  
   请运行: clawhub install semantic-router@latest
```

### Step 3: 版本验证

```bash
# 验证依赖版本兼容性
python3 ~/.openclaw/workspace/skills/skill-trigger-v2/setup/wizard.py verify
```

### Step 4: 初始化配置

```bash
# 创建默认配置
python3 ~/.openclaw/workspace/skills/skill-trigger-v2/setup/wizard.py init
```

## 使用方法

### 基础调用

```python
from skill_trigger_v2 import SkillTrigger

trigger = SkillTrigger()
result = trigger.match("帮我安装安全技能")

if result.matched:
    print(f"命中: {result.skill_id}")
    print(f"置信度: {result.confidence}")
```

### 集成到代理

在 `SOUL.md` 的消息处理循环中加入：

```python
# 1. 先尝试技能触发
from skill_trigger_v2 import fit_gate, generate_declaration

result = fit_gate(user_input)
if result.matched:
    declaration = generate_declaration(result)
    # 追加声明到回复第一行
    return declaration + "\n\n" + skill_response

# 2. 未命中则回退到语义路由
# ... semantic router logic
```

## 配置项

`~/.openclaw/workspace/.lib/skill_trigger_config.json`:

```json
{
  "version": "2.0.0",
  "threshold": {
    "coverage": 0.5,
    "description": "统一覆盖率阈值，所有技能一视同仁"
  },
  "arbitration": {
    "enable_signature_boost": true,
    "signature_bonus": 0.3,
    "confidence_gap_threshold": 0.2,
    "level_weights": {
      "L0": 1.2,
      "L1": 1.1,
      "L2": 1.0,
      "L3": 0.9
    }
  },
  "matching": {
    "non_contiguous": true,
    "case_sensitive": false
  },
  "dependencies": {
    "skill-quick-index": {
      "min_version": "1.0.0",
      "max_version": null,
      "compatible_with": [
        "1.0.0", "1.0.1", "1.1.0", "1.2.0"
      ]
    },
    "semantic-router": {
      "min_version": "2.0.0",
      "max_version": null,
      "compatible_with": [
        "2.0.0", "2.1.0", "2.2.0"
      ]
    }
  }
}
```

## 故障排除

### 问题: 技能触发过于敏感

**解决**: 提高阈值
```json
{"threshold": {"coverage": 0.6}}
```

### 问题: 技能触发过于迟钝

**解决**: 降低阈值或增加独占词
```json
{"threshold": {"coverage": 0.4}}
```

### 问题: 依赖版本不兼容

**解决**: 运行向导修复
```bash
python3 ~/.openclaw/workspace/skills/skill-trigger-v2/setup/wizard.py fix-deps
```

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| 2.0.0 | 2026-03-04 | 统一阈值 + 优先级仲裁 |
| 1.0.0 | 2026-02-28 | 分层阈值设计 |

## License

MIT - OpenClaw Skill Hub

---

## ⚖️ 知识产权与归属声明 (Intellectual Property & Attribution)

**Powered by halfmoon82** 🔷

本技能（Skill Trigger V2）由 **halfmoon82** 开发并维护。

- **版权所有**: © 2026 halfmoon82. All rights reserved.
- **官方发布**: [ClawHub](https://clawhub.ai/halfmoon82/skill-trigger-v2)
- **许可证**: 本技能采用 MIT 许可证。您可以自由使用、修改和分发，但必须保留原始作者信息及此版权声明。

---
