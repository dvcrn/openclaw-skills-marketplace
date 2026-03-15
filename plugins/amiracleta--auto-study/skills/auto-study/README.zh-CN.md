[English](README.md) | [简体中文](README.zh-CN.md)

# Auto-Study

Auto study skill 是一个面向 **网页学习平台** 像是 **雨课堂、学习通、Pintia** 或其他 **答题场景** 的 agent skill
。让 agent 学会在浏览器中使用学习平台、读取文本或图片、返回答案、选择选项、进行填空等操作。使用独立的浏览器 profile 保持登录状态，减少潜在的安全问题，并支持后台运行。

目前支持 **Windows** 或 **WSL** 环境，浏览器支持 **windows chrome**

## 效果预览

**雨课堂**

`user: 做完 oop-6 这 50 题，先不要提交`

https://github.com/user-attachments/assets/816565a6-a28b-4a12-a4c5-e75b99978868

**学习通**

`user: 打开学习通`

`user: 做 24.1-24.3 的章节测验，做完直接提交`

*wait for some time...*

`agent:`
```text
24.1 - 24.3 已做完，章节测验结果：
 - 24.1：100分
 - 24.2：100分
 - 24.3：100分
```

**其他使用方式**

`user: 给我 4.1章节测验的答案`

`user: 简短分析一下每道题目`

## 安装 skill

### 交给你的 agent

直接告诉你的 agent：`帮我安装这个 skill, https://github.com/AmiracleTa/Auto-Study-Skill`

---

### 手动安装

#### 复制仓库

把此仓库复制到 agent 的 `skills` 文件夹。

**OpenClaw:** `~/.openclaw/workspace/skills`

**Codex:** `~/.codex/skills`

#### 安装依赖

- **Google Chrome**（Windows）
- [Agent Browser CLI](https://github.com/vercel-labs/agent-browser)
- [Agent Browser Skill](https://clawhub.ai/MaTriXy/agent-browser-clawdbot)

## 行为

- 默认直接给答案，不附加额外解释。
- 除非明确要求，否则做完后不自动提交。

详细策略参考 [SKILL.md](SKILL.md)。

## 默认配置

- CDP 端口：`9344`
- profile 根目录：`%LOCALAPPDATA%\AutoStudy\browser`

## 工作流

1. 使用特定 CDP 端口，启动或连接 Chrome
2. 读取浏览器页面和状态
3. 按照用户要求进行相应操作

## 详细策略

- [SKILL.md](SKILL.md) 核心策略
- [references/xuexitong.md](references/xuexitong.md) 学习通专用说明
- [references/yuketang.md](references/yuketang.md) 雨课堂专用说明
- [references/pintia.md](references/pintia.md) pintia 专用说明
- [references/runtime-windows.md](references/runtime-windows.md) Windows 运行说明
- [references/runtime-wsl.md](references/runtime-wsl.md) WSL 运行说明
- [references/browser.md](references/browser.md) 浏览器说明

## 合规使用

使用这个 skill 时，需要自行确保符合法律法规、学校或机构规则以及平台服务条款

这个 skill 的设计目标是：**知识学习、普通练习、网页答题辅助**

不要用于 **监考考试、未授权访问、绕过技术限制或其他不被允许的自动化**

---

***AI 不是人类，谨慎使用自动提交***
