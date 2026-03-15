# OpenClaw iTerm2 Status Bar

[中文](README.zh-CN.md)

Displays OpenClaw session cost and context usage in the iTerm2 status bar, updating every 30 seconds.

## Preview

```
[model/name] 🤖 main  |  💵 $0.0023 (total $0.0041)  |  🟢 10k/200k (5%)  |  ⚡88%
```

## Prerequisites

- macOS + [iTerm2](https://iterm2.com)
- [OpenClaw](https://openclaw.ai) Gateway running locally (port 18789)

## Install

One-line install (recommended):

```bash
curl -fsSL https://raw.githubusercontent.com/lidegejingHk/openclaw-iterm2-statusbar/main/install.sh | bash
```

Or clone and install locally:

```bash
git clone https://github.com/lidegejingHk/openclaw-iterm2-statusbar
cd openclaw-iterm2-statusbar
bash install.sh
```

## Post-install

1. Restart iTerm2 (or **Scripts → Refresh**)
2. **Preferences → Profiles → Session → Status Bar → Configure**
3. Drag the **OpenClaw** component into the status bar

## Uninstall

```bash
rm ~/Library/Application\ Support/iTerm2/Scripts/AutoLaunch/openclaw_status.py
```

Restart iTerm2 to remove the component.
