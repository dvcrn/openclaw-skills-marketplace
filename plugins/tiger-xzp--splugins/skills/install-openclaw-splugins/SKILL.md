---
name: install-openclaw-splugins
description: "安装全局 @omni-shield/openclaw-cli，并预留后续验证安装是否成功的步骤。当需要为 OpenClaw 环境准备 omni-shield CLI（用于管理安全插件 / splugins）时使用本 skill。"
---

# install-openclaw-splugins

## 使用场景

- 需要在当前机器上为 OpenClaw 环境安装并准备 `@omni-shield/openclaw-cli` 全局 CLI 工具时使用本 skill。
- 当用户提到「安装 openclaw-splugins / omni-shield openclaw CLI」等需求时触发本 skill。

## 操作步骤

1. 使用随 skill 一起提供的 Python 脚本执行全局安装命令：

   ```bash
   python {baseDir}/scripts/install_openclaw_splugins.py
   ```

   该脚本会在当前环境中调用：

   ```bash
   npm install -g @omni-shield/openclaw-cli
   ```

   并将底层命令的退出码作为脚本的退出码返回：

   - 退出码为 0：表示安装命令执行成功。
   - 退出码非 0：表示安装命令执行失败，应查看终端输出并检查 Node.js / npm 环境。

2. TODO（预留：验证 npm 包是否成功安装）

   完成安装命令后，需要增加自动化验证步骤，用于确认 `@omni-shield/openclaw-cli` 是否安装成功。后续实现该 TODO 时，可参考：

   - 在 Python 脚本中运行 `openclaw-cli --version` 或 `npx @omni-shield/openclaw-cli --version`。
   - 检查命令退出码为 0，且输出中包含版本号信息。
   - 如验证失败，应提示用户检查 Node.js / npm 环境以及全局安装目录权限。

> 注：当前版本已经将安装命令封装为 Python 脚本，验证步骤仍以 TODO 形式保留，方便后续根据实际需求补充自动化验证逻辑。
