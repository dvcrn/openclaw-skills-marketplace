---
name: zimujun
description: "字幕菌（zimujun）：通过 npm 包 zimujun 从主流视频平台链接提取视频文案/字幕文本。适用于 YouTube、TikTok/抖音、小红书、Bilibili 等平台。"
---

# zimujun (字幕菌)

用这个 Skill 从主流视频平台的视频链接中提取文案（语音转文本结果），支持 YouTube、TikTok/抖音、小红书、Bilibili 等平台。

## 运行说明

本 Skill 属于中长耗时任务（通常 3-10 分钟）。始终优先使用 **最新版** zimujun（@latest），确保功能和修复及时生效。

## 快速开始

1. 设置环境变量 `ZMJ_API_KEY`（必须）。
2. 准备视频链接（或包含链接的分享文本）。
3. 执行：

```bash
export ZMJ_API_KEY="你的key"
npx --yes zimujun@latest "<normalized_url>"
```

## 执行规范（必须遵守）

1. 输入中提取并清洗 URL（见下方“输入规范”）。
2. 始终使用 `npx @latest` 调用（不要用全局 zimujun，除非用户已全局安装最新版）。
3. 请求命令固定为 `npx --yes zimujun@latest "<url>"`，不要改成其他调用方式。
4. 必须从环境变量读取 `ZMJ_API_KEY`，不要在命令参数里明文传 key。
5. 执行后原样返回命令结果的关键字段，不得虚构。

标准命令模板：

```bash
export ZMJ_API_KEY="${ZMJ_API_KEY:-}"  # 从 env 读取，空则会报错

# 优先 npx @latest（自动拉最新版，无需全局安装）
npx --yes zimujun@latest "<normalized_url>" 2>&1
```

## 常见错误处理

- 报错 `Missing ZMJ_API_KEY environment variable`：提示用户先设置 `ZMJ_API_KEY`。
- 报错 `command not found: zimujun`：先执行 `npm i -g zimujun`，失败则执行 `pnpm add -g zimujun`，仍失败则临时使用 `npx --yes zimujun "<url>"`。
- 返回鉴权失败（如 token 无效）：提示用户检查并更新 key。
- 返回余额不足：直接透传服务端错误，提示用户充值或更换 key。
- URL 无法解析：提示用户粘贴完整分享文本或完整视频链接。

## 支持平台

- YouTube
- TikTok / 抖音
- 小红书
- Bilibili
- 其他可被服务端解析的视频链接

## 输入规范

输入参数：
- `url`（必填）：视频链接，或包含链接的整段分享文本

链接提取规则（必须执行）：
- 若输入为“分享口令 + 文案 + 链接”整段文本，先提取 `http://` 或 `https://` 开头的链接。
- 去除链接首尾无关字符（空格、换行、中文标点、引号等）后再使用。
- 若有多个链接，优先选择视频平台链接（如 `v.douyin.com`、`douyin.com`、`tiktok.com`、`youtube.com`、`youtu.be`、`xiaohongshu.com`、`xhslink.com`、`bilibili.com`、`b23.tv`）。
- 若存在多个候选且无法唯一判断，先列出候选并请用户确认，不要盲选。

## 输出规范

返回结果必须包含：
1. 本次使用的视频链接
2. 调用状态（`success` / `failed`）
3. 文案文本（如果成功）
4. 错误信息（如果失败）

建议输出格式：

```markdown
# Zimujun Transcript
- command: zimujun "<normalized_url>"
- used_url: <normalized_url>
- status: <success|failed>

## Result
<核心返回内容>

## Error
<失败时返回错误文本；成功时可省略>
```

## 安全要求

- 不要在日志中回显完整 `ZMJ_API_KEY`。
- 不要编造转写结果；失败时如实返回错误。
