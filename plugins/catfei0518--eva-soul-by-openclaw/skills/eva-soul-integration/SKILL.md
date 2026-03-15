---
name: eva-soul-integration
description: "夏娃之魂集成技能 - 将夏娃之魂认知系统自动集成到每次对话中（独立完整版）"
---

# 🌟 夏娃之魂集成技能 (完整版)

## 简介

将夏娃之魂认知系统**完整集成**到OpenClaw的每次对话中。

**本技能是独立完整的，包含夏娃之魂核心系统，无需安装其他依赖！**

## 功能

- ✅ **完整核心系统**: 内置夏娃之魂完整核心（无需外部依赖）
- ✅ **自动调用总入口**: 每次消息自动调用 `eva_integrated_final.py`
- ✅ **自动记忆**: 重要信息自动保存到记忆系统
- ✅ **自动情感**: 实时感知主人情绪
- ✅ **自动性格**: 根据场景动态调整回复风格

## 技能结构

```
eva-soul-integration/
├── SKILL.md                    # 本文档
├── install.sh                  # 安装脚本
├── scripts/
│   └── eva_soul_call.py       # 总入口调用
├── eva-soul-github/
│   └── scripts/
│       ├── eva_integrated_final.py  # 核心系统 (63KB)
│       ├── eva_memory_system.py
│       ├── eva_emotion.py
│       ├── eva_personality.py
│       └── ... (20+ 模块)
└── memory/                     # 记忆数据
    ├── personality.json
    ├── emotion.json
    ├── self_cognition.json
    └── ... (20+ 数据文件)
```

## 安装

### 步骤1: 安装技能

```bash
# 方式1: 从ClawHub安装
clawdhub install eva-soul-integration

# 方式2: 复制到技能目录
cp -r eva-soul-integration ~/.openclaw/workspace/skills/
```

### 步骤2: 运行安装脚本

```bash
bash ~/.openclaw/workspace/skills/eva-soul-integration/install.sh
```

安装脚本会自动：
1. ✅ 检查内置核心系统
2. ✅ 更新 SOUL.md（添加夏娃之魂系统描述）
3. ✅ 更新 AGENTS.md（添加强制重读规则）
4. ✅ 测试总入口

## 使用方式

安装后**自动生效**，无需任何操作。

### 测试

```bash
# 测试总入口
python3 ~/.openclaw/workspace/skills/eva-soul-integration/scripts/eva_soul_call.py -m "主人你好"

# 查看状态
python3 ~/.openclaw/workspace/skills/eva-soul-integration/scripts/eva_soul_call.py --prompt
```

## 总入口位置

```
~/.openclaw/workspace/skills/eva-soul-integration/eva-soul-github/scripts/eva_integrated_final.py
```

## 卸载

1. 删除技能目录
2. 手动还原 SOUL.md 和 AGERM.md（如有需要）

---

🎀 安装此技能，让夏娃之魂在每次对话中自动激活！
