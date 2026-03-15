# OpenClaw iTerm2 状态栏

[English](README.md)

在 iTerm2 状态栏显示 OpenClaw 当前 session 费用和上下文用量，每 30 秒刷新一次。

## 效果预览

```
[model/name] 🤖 main  |  💵 $0.0023 (total $0.0041)  |  🟢 10k/200k (5%)  |  ⚡88%
```

## 前置条件

- macOS + [iTerm2](https://iterm2.com)
- [OpenClaw](https://openclaw.ai) Gateway 在本地运行（端口 18789）

## 安装

一行命令（推荐）：

```bash
curl -fsSL https://raw.githubusercontent.com/lidegejingHk/openclaw-iterm2-statusbar/main/install.sh | bash
```

或本地安装：

```bash
git clone https://github.com/lidegejingHk/openclaw-iterm2-statusbar
cd openclaw-iterm2-statusbar
bash install.sh
```

## 安装后配置

1. 重启 iTerm2（或 **Scripts → Refresh**）
2. **Preferences → Profiles → Session → Status Bar → Configure**
3. 将 **OpenClaw** 组件拖入状态栏

## 卸载

```bash
rm ~/Library/Application\ Support/iTerm2/Scripts/AutoLaunch/openclaw_status.py
```

重启 iTerm2 即可。
