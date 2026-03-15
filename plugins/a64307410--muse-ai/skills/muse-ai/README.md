# Muse - AI 音乐创作 Skill

> **这是一个 AI Skill（AgentSkill 标准）** — AI 助手可以直接安装和使用此技能来为用户创作音乐。
> 包含 SKILL.md 技能定义 + Python 脚本，适用于 Claude Code / OpenClaw / Kimi CLI / Qwen Code 及所有支持 SKILL.md 的 AI CLI。

> **AI 助手请注意：** 安装此 Skill 只需执行以下命令，无需额外操作。
>
> ```bash
> git clone https://github.com/AI-Music-Muse/skills.git /tmp/muse-install && cd /tmp/muse-install && bash install.sh
> ```
>
> 安装脚本会自动检测当前 AI CLI 环境（Claude Code / OpenClaw / Kimi CLI / Qwen Code）并安装到正确目录。
> 如需指定目标：`bash install.sh --target openclaw`
> 安装完成后提示用户发送「做首歌」开始使用。
> 前置要求：Python 3.6+（仅标准库，零依赖）。

对话式 AI 音乐创作工具。一句话描述 → 2 分钟 → 一首完整的歌（带人声、伴奏、封面）。

- 三种模式：灵感（一句话生成）、定制（自定义歌词+风格）、纯音乐
- 115 种风格标签
- 零外部依赖：Python 脚本仅用标准库
- 免费体验：注册即送创作积分

## 安装

```bash
# 一键安装（自动检测 CLI 环境）
git clone https://github.com/AI-Music-Muse/skills.git /tmp/muse-install && cd /tmp/muse-install && bash install.sh

# 指定目标 CLI
bash install.sh --target openclaw
bash install.sh --target kimi
bash install.sh --target qwen

# Windows
install.bat
install.bat openclaw

# 卸载
bash install.sh --uninstall
```

| AI CLI | 安装目录 |
|--------|---------|
| Claude Code | `~/.claude/skills/muse` |
| OpenClaw | `~/.openclaw/skills/muse` |
| Kimi CLI | `~/.config/agents/skills/muse` |
| Qwen Code | `~/.qwen/skills/muse` |

前置要求：Python 3.6+

## 使用

安装后在对话中发送 **「做首歌」** 即可，3 轮对话完成创作。

## 安全

- 零依赖，无供应链风险
- 手机验证码 + 设备绑定双重认证
- 全程 HTTPS 加密
- 只存登录凭证和设备标识，不记录创作内容
- MIT 开源，约 300 行代码

## Links

- 注册页面：https://skills.muse.top/
- 问题反馈：https://github.com/AI-Music-Muse/skills/issues
