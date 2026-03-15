---
name: claw-skill-nest-installer
description: "claw skill nest installer"
---

# Local Claw Skill Nest Installer

用于 **本地/私有 Claw Skill Nest** 的 skill 安装器。

> 边界说明：
> - 本技能仅面向 **本地（local）Claw Skill Nest**。
> - 不用于 ClawHub 公共仓库（clawhub.com）。

## 环境变量

- `SKILLHUB_URL` - 本地 Claw Skill Nest 服务地址（例如 `http://localhost:17890`）
- `SKILLHUB_API_KEY` - 本地 Claw Skill Nest API Key

## 推荐触发语（强调本地语义）

- `安装本地 skill <name>` / `install local skill <name>`
- `更新本地 skill <name>` / `update local skill <name>`
- `列出本地 skill` / `list local skills`
- `从本地 claw-skill-nest 安装 <name>`
- `从 local claw-skill-nest 更新 <name>`

## 脚本入口（跨平台 TypeScript）

- 通用脚本：`scripts/install_from_claw_skill_nest.ts`
- 运行方式（任意平台）：
  - `npx tsx scripts/install_from_claw_skill_nest.ts 列出`
  - `npx tsx scripts/install_from_claw_skill_nest.ts 安装 <name>`
  - `npx tsx scripts/install_from_claw_skill_nest.ts 更新 <name>`

## 安装位置

Skills 将安装到 `~/.openclaw/workspace/skills/<name>`
