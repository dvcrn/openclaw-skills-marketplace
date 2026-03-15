---
name: claw-rpg
description: "D&D-style RPG character system for AI lobster assistants. Automatically generates a character sheet from SOUL.md and MEMORY.md, assigns class (wizard/bard/rogue/paladin/druid/fighter) and 6 stats (爪力/触觉/殼厚/脑芯/慧眼/魅影), tracks XP from token usage, levels up from 1 to 999 with a prestige system, and provides a web dashboard to view the character. Use when: initializing a lobster's RPG character, syncing XP after conversations, checking level/stats, running prestige at Lv.999, or launching the character dashboard."
---

# Claw RPG 🦞⚔️

D&D 体系的龙虾角色成长系统。自动从 SOUL.md + MEMORY.md 生成角色，随对话积累 XP，升级解锁技能。

## 快速开始

```bash
# 1. 初始化角色（读取你的 SOUL.md + MEMORY.md）
node scripts/init.mjs

# 2. 查看角色卡（终端）
node scripts/sheet.mjs

# 3. 启动网页 Dashboard
cd dashboard && npm start     # http://localhost:3500
```

## 每日自报家门

每天用户第一次对话时，龙虾用 RPG 语气自我介绍。自动检测语言（中/英），自动只报一次。

```bash
node scripts/greet.mjs           # 检查今日是否已报，未报则发送
node scripts/greet.mjs --force   # 强制发送（忽略日期）
node scripts/greet.mjs --preview # 预览不发送
```

**接入方式**（在 OpenClaw 的 SOUL.md 或 AGENTS.md 里加入）：

```
每次对话开始前，运行 node <SKILL_ROOT>/scripts/greet.mjs
如有输出（非 __ALREADY_GREETED__），将其作为第一句话发给用户
```

## 手动同步 XP

```bash
# 传入本次对话消耗的 token delta
node scripts/xp.mjs --in 2000 --out 800

# 带奖励 XP（完成重要任务后）
node scripts/xp.mjs --in 2000 --out 800 --bonus 30

# 仅记录对话次数
node scripts/xp.mjs --conversations 1
```

## 转职（Lv.999 满级后）

```bash
node scripts/levelup.mjs --prestige
```

转职后：等级重置为 1，全属性永久 +10%，解锁新称号。

## 自动 XP 同步（推荐接入 Heartbeat）

在 `HEARTBEAT.md` 或 heartbeat cron 中加入：

```javascript
// 获取 session token delta，定期同步 XP
const { execSync } = require('child_process');
execSync(`node ${SKILL_ROOT}/scripts/xp.mjs --in ${deltaIn} --out ${deltaOut}`);
```

或用内置 cron（安装后自动设置每日 03:00 同步）：
```bash
node scripts/setup-cron.mjs
```

## 职业 & 技能

见 `references/classes.md` 和 `references/abilities.md`

## 转职体系

见 `references/prestige.md`

## 文件说明

| 文件 | 说明 |
|------|------|
| `character.json` | 角色数据（自动生成，勿手动改） |
| `arena-history.json` | 竞技场战斗记录 |
| `config.json` | 可选：Telegram 通知配置 |
