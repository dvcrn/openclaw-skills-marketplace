# Command Cookbook

## 1) Quark login and account binding

```bash
scripts/backup/quarkpan-login.sh
scripts/backup/quark-account-guard.sh bind --confirm YES_I_UNDERSTAND
scripts/backup/quark-account-guard.sh status
```

## 2) Workspace backup + cloud upload

```bash
scripts/backup/backup-cron.sh daily
scripts/backup/backup-cron.sh weekly
```

## 3) Restore validation (must dry-run first)

```bash
scripts/backup/restore-quarkpan.sh --from-index /root/.openclaw/backup/indexes/cloud-daily-YYYY-MM-DD.txt --dry-run
```

## 4) Lighthouse snapshot (manual only)

Create snapshot:
```bash
scripts/backup/lighthouse-snapshot-create.sh --wait
```

Prune old snapshots (dry-run):
```bash
scripts/backup/lighthouse-snapshot-prune.sh --keep 2
```

Prune apply:
```bash
scripts/backup/lighthouse-snapshot-prune.sh --keep 2 --apply
```

Rollback snapshot (danger):
```bash
scripts/backup/lighthouse-snapshot-apply.sh --snapshot-id lhsnap-xxxx --confirm YES_I_UNDERSTAND
```

## 5) System-state docs package

```bash
scripts/backup/system-state-backup.sh
```
