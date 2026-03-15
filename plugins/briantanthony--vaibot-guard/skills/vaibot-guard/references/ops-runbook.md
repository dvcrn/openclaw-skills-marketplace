# VAIBot Guard — Ops Runbook

This runbook describes how to run `vaibot-guard-service.mjs` as a service.

CLI usage note: do not assume an executable shim exists. Use:

```bash
node scripts/vaibot-guard.mjs <command> ...
```

Two options are provided:
- **Local workstation mode (recommended for most OpenClaw installs):** user service (`systemctl --user`)
- **VPS / production mode:** system service (`sudo systemctl`)

## Shared environment variables

Retention:
- `VAIBOT_LOG_RETENTION_DAYS` (default 14): remove guard log/state files in `VAIBOT_GUARD_LOG_DIR` older than this many days.

Common env vars (see `SKILL.md` for full list):
- `VAIBOT_GUARD_HOST` (default `127.0.0.1`)
- `VAIBOT_GUARD_PORT` (default `39111`)
- `VAIBOT_GUARD_TOKEN` (recommended)
- `VAIBOT_POLICY_PATH` (default `references/policy.default.json`)
- `VAIBOT_GUARD_LOG_DIR` (default `${VAIBOT_WORKSPACE}/.vaibot-guard`)
- `VAIBOT_API_URL`, `VAIBOT_API_KEY`, `VAIBOT_PROVE_MODE`

## Option A — User service (recommended)

### Install

Copy the unit:

```bash
mkdir -p ~/.config/systemd/user
cp systemd/user/vaibot-guard.service ~/.config/systemd/user/
```

Create an env file:

```bash
mkdir -p ~/.config/vaibot-guard
cp systemd/user/vaibot-guard.env ~/.config/vaibot-guard/vaibot-guard.env
$EDITOR ~/.config/vaibot-guard/vaibot-guard.env
```

Enable + start (will start at login; also tied to `openclaw-gateway.service` if present):

```bash
systemctl --user daemon-reload
systemctl --user enable --now vaibot-guard
systemctl --user status vaibot-guard
```

### Logs

```bash
journalctl --user -u vaibot-guard -f
```

### Run at boot (optional)

If you want the user service to run when you are not logged in:

```bash
loginctl enable-linger $USER
```

## Option B — System service (VPS/production)

### Install

Create a dedicated user:

```bash
sudo useradd --system --create-home --home-dir /var/lib/vaibot-guard --shell /usr/sbin/nologin vaibot-guard
```

Copy unit + env:

```bash
sudo mkdir -p /etc/vaibot-guard
sudo cp systemd/system/vaibot-guard.env /etc/vaibot-guard/vaibot-guard.env
sudo $EDITOR /etc/vaibot-guard/vaibot-guard.env

sudo cp systemd/system/vaibot-guard.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now vaibot-guard
sudo systemctl status vaibot-guard
```

### Logs

```bash
sudo journalctl -u vaibot-guard -f
```

### Hardening

The provided unit includes basic systemd hardening. Adjust if you need filesystem writes outside the configured log dir.
