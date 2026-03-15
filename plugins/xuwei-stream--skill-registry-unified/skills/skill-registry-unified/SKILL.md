---
name: skill-registry-unified
description: "一体化技能注册表 - 本地优先匹配，无匹配则自动搜索ClawHub并安全安装，新装技能自动注册到细分分类。"
---

# Skill Registry Unified

本地优先匹配 + 自动扩展安装的一站式技能路由系统。

## 核心流程
```
用户输入 → 本地匹配 → 有？直接执行
               ↓ 无
          搜索ClawHub → 找到？→安全扫描→询问用户→安装+注册
               ↓ 没找到
            通用能力执行
```

## 依赖
- find-skills-skill
- skill-vetter
- js-yaml
