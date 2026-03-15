---
name: openclaw-iterm2-statusbar
description: "Install the OpenClaw iTerm2 status bar that shows session cost and context usage in real time."
---

# OpenClaw iTerm2 Status Bar

Displays OpenClaw session cost and context usage directly in the iTerm2 status bar, refreshing every 30 seconds.

## Install

One-line installer:
```bash
curl -fsSL https://raw.githubusercontent.com/lidegejingHk/openclaw-iterm2-statusbar/main/install.sh | bash
```

Or manually:
```bash
DEST="$HOME/Library/Application Support/iTerm2/Scripts/AutoLaunch"
mkdir -p "$DEST"
curl -fsSL https://raw.githubusercontent.com/lidegejingHk/openclaw-iterm2-statusbar/main/openclaw_status.py \
  -o "$DEST/openclaw_status.py"
chmod +x "$DEST/openclaw_status.py"
```

## Post-install

1. Restart iTerm2 (or **Scripts → Refresh**)
2. **Preferences → Profiles → Session → Status Bar → Configure**
3. Drag the **OpenClaw** component into the status bar

## What It Shows

```
[kiro/claude-sonnet-4.6] 🤖 main  |  💵 $0.0023 (total $0.0041)  |  🟢 10k/200k (5%)  |  ⚡88%
```

- Model name
- Main session cost + total across all sessions
- Context usage with color indicator (🟢🟡🟠🔴)
- Compaction threshold (⚡)

## Requirements

- macOS + iTerm2
- OpenClaw Gateway running locally on port 18789

## Uninstall

```bash
rm ~/Library/Application\ Support/iTerm2/Scripts/AutoLaunch/openclaw_status.py
```

Restart iTerm2 to remove the component.
