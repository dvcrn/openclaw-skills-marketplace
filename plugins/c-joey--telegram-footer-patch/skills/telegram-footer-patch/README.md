# Telegram Footer Patch

![Footer Preview](./assets/footer-preview.jpg)

Patch OpenClaw's Telegram reply pipeline to append a one-line footer in private chats (`🧠 Model + 💭 Think + 📊 Context`).

## What it does
- Adds a persistent footer at the platform layer
- Shows model, think level, and context usage in one line
- Supports dry-run preview
- Creates a backup before patching
- Supports rollback and post-restart verification

## Recommended flow
1. Dry-run
2. Apply patch
3. Restart gateway after confirmation
4. Send a test message and verify footer output

## Before you run
- This patches OpenClaw installation files under `.../openclaw/dist/`.
- Run `python3 scripts/patch_reply_footer.py --dry-run` first.
- Ensure backups are created (`*.bak.telegram-footer.*`) and test rollback (`python3 scripts/revert_reply_footer.py --dry-run`).
- Only run on machines you control/trust.

## Key files
- `SKILL.md` — usage guidance
- `scripts/patch_reply_footer.py` — patch script
- `scripts/revert_reply_footer.py` — rollback script
- `CHANGELOG.md` — release notes
- `LICENSE` — MIT license
