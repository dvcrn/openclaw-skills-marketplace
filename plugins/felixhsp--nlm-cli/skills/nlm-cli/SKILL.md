---
name: nlm-cli
description: "使用 Jacob Brown 的 `notebooklm-mcp-cli`（`nlm` 命令）自动化操作 NotebookLM。适用于处理 Notebook、来源（sources）、Studio 内容生成、Research、分享、MCP 配置，以及音频、视频、报告、幻灯片、信息图、数据表、测验、抽认卡等产物下载。凡是准备使用 `nlm`，尤其是可能需要先安装 CLI 或先完成认证时，都应先读取此技能。"
---

# NLM CLI

在需要使用 **Jacob Brown 的 `notebooklm-mcp-cli`**（`nlm` 命令）时，使用这个技能。

## 前置要求
- 系统中可用 `node`
- 已安装 `nlm`，或者已安装到本地虚拟环境中
- 在执行 NotebookLM 相关操作前，已经通过 `nlm login` 完成认证

## 先安装 CLI
如果当前环境里还没有 `nlm`，先阅读 `references/install-and-auth.md`，完成安装后再继续。

## Wrapper
所有命令统一通过附带的 wrapper 执行：

```bash
node {baseDir}/scripts/nlm.mjs <command> [args...]
```

该 wrapper 会按以下顺序解析 `nlm` 可执行文件：
1. 环境变量 `NLM_BIN`
2. `{baseDir}/.venvs/nlm-mcp/bin/nlm`
3. PATH 中的 `nlm`

优先使用 wrapper，而不是直接调用裸 `nlm`，这样可以减少不同机器、不同 shell、不同 PATH 顺序带来的不确定性。

## 快速开始

```bash
node {baseDir}/scripts/nlm.mjs login
node {baseDir}/scripts/nlm.mjs notebook list
node {baseDir}/scripts/nlm.mjs source add <notebook_id> --url "https://example.com" --wait
node {baseDir}/scripts/nlm.mjs slides create <notebook_id> --confirm
node {baseDir}/scripts/nlm.mjs studio status <notebook_id>
node {baseDir}/scripts/nlm.mjs download slide-deck <notebook_id> --id <artifact_id> --format pdf --output slides.pdf
```

## 工作规则
- 优先使用名词在前的子命令风格，例如 `notebook list`、`source add`、`slides create`、`download slide-deck`
- 如果用户希望来源在导入后立刻可用，执行 `source add` 时加上 `--wait`
- 在生成类命令执行后，用 `studio status <notebook_id>` 检查进度和 artifact ID
- 下载产物时，优先使用专门的 `download <type>` 命令，不要依赖手动抓取原始 artifact 元数据
- 如果认证过期、当前 Google 账号不对、或 profile 不一致，重新执行 `login` 或切换 profile
- 需要命令目录时，读取 `references/cli-commands.md`
- 需要安装、认证、profile、MCP 配置或排障说明时，读取 `references/install-and-auth.md`
