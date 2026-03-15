---
name: quarkpan-backup-suite
description: "Build and operate a QuarkPan-based backup + restore workflow for OpenClaw workspaces, including QR login, account UID binding guard, cloud upload, dry-run restore, and Lighthouse snapshot policy (manual create only, weekly prompt). Use when users ask to set up/secure Quark backup automation, recovery runbooks, or share this backup capability with other OpenClaw users."
---

# QuarkPan Backup Suite

Use this skill to deploy a production-safe backup workflow with these goals:
- Keep automated workspace backups to QuarkPan.
- Enforce account binding so uploads cannot silently go to a wrong account.
- Keep system rollback snapshots manual-only (no auto overwrite risk).
- Provide reproducible restore steps and distributable skill package.

## Workflow

1. Run preflight checks with `scripts/check_env.sh`.
2. Configure backup policy using `references/commands.md`.
3. Enforce account guard (`bind`, `check`, `rotate-*`) before uploads.
4. Verify restore path with dry-run first.
5. Keep Lighthouse snapshots manual-only; use weekly prompt policy.
6. Package/share this skill with `package_skill.py`.

## Guardrails

- Do not auto-apply destructive restore.
- Do not auto-create system snapshots by cron.
- Require explicit confirmation for snapshot creation and snapshot rollback.
- Keep cloud upload failure non-fatal for local backup success.

## References

- Command cookbook: `references/commands.md`
- Security and rotation policy: `references/security-policy.md`
- Sharing/export steps: `references/share.md`
