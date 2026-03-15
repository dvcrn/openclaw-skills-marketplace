---
name: telegram-footer-patch
description: "Patch OpenClaw Telegram private-chat replies to append a footer at the platform layer (`🧠 Model + 💭 Think + 📊 Context`), with backup, syntax validation, upgrade-aware reapply hints, rollback, and restart workflow."
---

# Telegram Footer Patch

![Footer Preview](./assets/footer-preview.jpg)

给 Telegram 私聊回复追加平台层尾注，不依赖模型记忆。

## Features

- Add a Telegram private-chat footer: `🧠 Model + 💭 Think + 📊 Context`
- Support dry-run, backup, rollback, and reapply after upgrades

## 功能

- 给 Telegram 私聊回复追加 `🧠 Model + 💭 Think + 📊 Context` 尾注
- 支持预览、备份、回滚，以及升级后重打

当前实现：自动探测并修改当前版本实际可能命中的 dist 文件（`reply-*.js`、`compact-*.js`、`pi-embedded-*.js`），自动备份，可重复覆盖更新，可回滚。

## What to consider before installing / 安装前需要考虑的事项

This skill does what it says (patches OpenClaw dist JS files to append a Telegram footer), but it **writes into your OpenClaw installation directory** and requires **Node.js + Python 3**.

Before installing/running:
1) Inspect the scripts yourself and run `--dry-run` to see which files would be touched.
2) Ensure `node` is installed and you have a plan for filesystem permissions (consider a staging instance/container).
3) Confirm backups are created (`*.bak.telegram-footer.*`) and test the revert script.
4) Only run the patch on systems you control and trust.

这项技能的功能正如其名（修改 OpenClaw 分发目录中的 JS 文件，添加 Telegram 页脚），但它会**写入 OpenClaw 安装目录**，并且需要 **Node.js + Python 3**。

安装/运行前：
1) 请自行检查脚本，并运行 `--dry-run` 先预览将会修改哪些文件。
2) 确保已安装 `node`，并规划好文件系统权限（建议先在测试环境/容器中跑）。
3) 确认已创建备份（查找 `*.bak.telegram-footer.*`）并测试还原脚本。
4) 仅在你控制且信任的系统上运行；不确定就先上 staging。

## 使用

### 1) 预览

```bash
python3 scripts/patch_reply_footer.py --dry-run
```

### 2) 应用

```bash
python3 scripts/patch_reply_footer.py
```

### 3) 重启网关（生效）

```bash
openclaw gateway restart
```

### 4) 回滚

```bash
python3 scripts/revert_reply_footer.py
openclaw gateway restart
```

## 现在包含的保护

- patch 后自动执行 `node --check`
- 语法校验失败时自动恢复刚写入前的备份
- 若 marker 丢失但已有历史备份，会提示“可能被升级覆盖，正在重打”
- 若 insertion needle 在候选 reply bundle 中失效，会明确报错，不再静默跳过
- 会清理已知旧版 Telegram 尾注块，避免双尾注叠加

## 说明

- 当前会 patch：`dist/reply-*.js`、`dist/compact-*.js`、`dist/pi-embedded-*.js`
- 已打过补丁时，会按 marker 直接覆盖更新，不会重复注入
- 每次写入前会自动生成 `.bak.telegram-footer.*` 备份
- OpenClaw 升级后若补丁被覆盖，重新执行 `patch_reply_footer.py` 即可；脚本会给出 upgrade-aware 提示
