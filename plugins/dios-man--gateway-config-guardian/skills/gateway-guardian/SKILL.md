---
name: gateway-guardian
description: "Three-layer protection for the OpenClaw gateway: real-time config monitoring with auto-rollback, systemd crash recovery, and tiered notifications via Feishu/Telegram/Discord. Use when: (1) user shares a GitHub link and says \"install this\" / \"帮我安装\", (2) user asks for status: \"gateway-guardian status\" / \"guardian 运行正常吗\", (3) user asks to uninstall: \"uninstall gateway-guardian\" / \"卸载 gateway-guardian\"."
---

# Gateway Guardian — Skill Instructions

## Triggers

Activate this skill when the user:
- Shares `https://github.com/Dios-Man/gateway-guardian` and asks to install it
- Says "install gateway-guardian", "帮我安装", "install this skill", or similar
- Says "gateway-guardian status", "guardian status", "guardian 运行正常吗", or similar
- Says "uninstall gateway-guardian", "卸载 gateway-guardian", or similar

---

## Installation (AI-executed)

### Pre-flight checks

1. Confirm the system is Linux with `systemd --user` available:
   ```bash
   systemctl --user status 2>&1 | head -3
   ```
2. Check and install `inotify-tools` if missing:
   ```bash
   if ! which inotifywait > /dev/null 2>&1; then
       sudo apt-get install -y inotify-tools
   fi
   ```
3. Confirm OpenClaw is installed and the gateway is running.

### Determine notification fallback

Read from the current inbound message metadata:
- `channel`: messaging platform (feishu / telegram / discord / etc.)
- `chat_type`: conversation type (direct / group)
- `sender_id`

Set `FALLBACK_TARGET` (used when dynamic session detection fails):
- **Feishu**: `user:{sender_id}` — always send a DM, even if installed from a group
- **Telegram**: use `chat_id` for DMs; for groups, ask the user for their personal numeric Telegram ID
- **Discord**: ask the user for their DM channel ID

### Determine notification language (LOCALE)

Detect the language the user is communicating in during this conversation:
- User is writing in Chinese → `LOCALE=zh`
- User is writing in English → `LOCALE=en`
- Language is unclear or mixed → ask the user: "Should notifications be sent in Chinese or English?"

### Installation steps

**Step 1 — Back up current config**
```bash
TIMESTAMP_DIR="$HOME/.openclaw/config-backups"
mkdir -p "$TIMESTAMP_DIR"
cp "$HOME/.openclaw/openclaw.json" \
   "$TIMESTAMP_DIR/openclaw.json.$(date +%Y%m%d-%H%M%S).preinstall"
echo "Backup created: $(ls -t $TIMESTAMP_DIR | head -1)"
```

**Step 2 — Download skill files**
```bash
SKILL_DIR="$HOME/.openclaw/workspace/skills/gateway-guardian"
mkdir -p "$SKILL_DIR"
BASE_URL="https://raw.githubusercontent.com/Dios-Man/gateway-guardian/main"
for f in config-lib.sh config-watcher.sh gateway-recovery.sh pre-stop.sh; do
    # Skip if file already present (e.g. installed via clawhub install)
    [ -f "$SKILL_DIR/$f" ] && continue
    curl -fsSL "$BASE_URL/$f" -o "$SKILL_DIR/$f"
done
```

**Step 3 — Write guardian.conf**
```bash
SKILL_DIR="$HOME/.openclaw/workspace/skills/gateway-guardian"
cat > "$SKILL_DIR/guardian.conf" << EOF
FALLBACK_CHANNEL={detected channel}
FALLBACK_TARGET={determined fallback target}
LOCALE={zh or en}
EOF
```

**Step 4 — Set execute permissions**
```bash
SKILL_DIR="$HOME/.openclaw/workspace/skills/gateway-guardian"
chmod +x "$SKILL_DIR/config-watcher.sh"
chmod +x "$SKILL_DIR/gateway-recovery.sh"
chmod +x "$SKILL_DIR/pre-stop.sh"
```

**Step 5 — Register config-watcher service**
```bash
SKILL_DIR="$HOME/.openclaw/workspace/skills/gateway-guardian"
cat > ~/.config/systemd/user/openclaw-config-watcher.service << EOF
[Unit]
Description=OpenClaw Gateway Guardian - File Watcher
After=openclaw-gateway.service

[Service]
Type=simple
ExecStart=/bin/bash $SKILL_DIR/config-watcher.sh
Restart=always
RestartSec=3

[Install]
WantedBy=default.target
EOF
```

**Step 6 — Register gateway-recovery service**
```bash
SKILL_DIR="$HOME/.openclaw/workspace/skills/gateway-guardian"
cat > ~/.config/systemd/user/openclaw-recovery.service << EOF
[Unit]
Description=OpenClaw Gateway Guardian - Crash Recovery
After=network.target

[Service]
Type=oneshot
ExecStart=/bin/bash $SKILL_DIR/gateway-recovery.sh
EOF
```

**Step 7 — Register OnFailure drop-in and ExecStopPost hook**
```bash
SKILL_DIR="$HOME/.openclaw/workspace/skills/gateway-guardian"
mkdir -p ~/.config/systemd/user/openclaw-gateway.service.d/
cat > ~/.config/systemd/user/openclaw-gateway.service.d/recovery.conf << EOF
[Unit]
OnFailure=openclaw-recovery.service

[Service]
StartLimitBurst=3
StartLimitIntervalSec=60
ExecStopPost=/bin/bash $SKILL_DIR/pre-stop.sh
EOF
```

**Step 8 — Start services**
```bash
systemctl --user daemon-reload
systemctl --user enable openclaw-config-watcher.service
systemctl --user start openclaw-config-watcher.service
```

**Step 9 — Verify installation**
```bash
systemctl --user is-active openclaw-config-watcher.service
cat ~/.config/systemd/user/openclaw-gateway.service.d/recovery.conf
tail -5 /tmp/config-watcher.log
```

**Step 10 — Report result to user**

Reply with a summary in the user's language (match LOCALE):

---
✅ **Gateway Guardian installed**

🔔 Notification channel: {channel} (fallback target: {FALLBACK_TARGET})
🌐 Notification language: {zh | en}
📋 Service status: {Active line from systemctl output}
📝 Log: `/tmp/config-watcher.log`

To uninstall, tell me: "uninstall gateway-guardian" / "卸载 gateway-guardian"
---

---

## Status Check (AI-executed)

When the user asks for status:

```bash
systemctl --user status openclaw-config-watcher.service
tail -10 /tmp/config-watcher.log
ls -lt ~/.openclaw/config-backups/ | head -5
```

Report: service active/inactive, recent log lines, number of config backups on hand.

---

## Uninstall (AI-executed)

When the user asks to uninstall:

```bash
systemctl --user stop openclaw-config-watcher.service
systemctl --user disable openclaw-config-watcher.service
rm -f ~/.config/systemd/user/openclaw-config-watcher.service
rm -f ~/.config/systemd/user/openclaw-recovery.service
rm -f ~/.config/systemd/user/openclaw-gateway.service.d/recovery.conf
systemctl --user daemon-reload
systemctl --user reset-failed openclaw-gateway.service 2>/dev/null
```

Ask the user whether to also delete config backups:
```bash
# Only run if user confirms
rm -rf ~/.openclaw/config-backups/
```

Confirm removal is complete.

---

## Notes

- This skill must be installed via an OpenClaw AI agent — no manual install script is provided.
- Installation requires an active message context (in-conversation metadata is used for notification setup).
- `guardian.conf` contains private notification config and is never uploaded to GitHub.
- Config backups in `~/.openclaw/config-backups/` are retained across uninstalls unless the user explicitly requests deletion.
- Notifications use dynamic session detection at runtime; `guardian.conf` is only a fallback.
