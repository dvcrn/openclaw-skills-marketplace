# Max Auth - OpenClaw Security Plugin

## Overview

Max Auth adds a biometric/password authentication gate to OpenClaw sensitive actions. Before destructive, configuration, or external-impact actions, the agent checks for an active session. If none exists, it refuses and prompts the user to authenticate at the dashboard.

**Architecture:**
- Node.js HTTP server (`auth-server.js`) runs locally on port 8456
- Served over Tailscale HTTPS at `https://<hostname>/auth`
- Sessions last 2 hours; passkeys (WebAuthn) or master password accepted

## Setup

### 1. Deploy the server

```bash
mkdir -p ~/.max-auth
cp assets/auth-server.js ~/.max-auth/
cp assets/setup-tailscale.sh ~/.max-auth/
cp assets/package.json ~/.max-auth/
cd ~/.max-auth && npm install
node auth-server.js set-password 'your_strong_password'
```

### 2. Install as systemd service

```bash
sudo tee /etc/systemd/system/max-auth.service > /dev/null << EOF
[Unit]
Description=Max Auth Server
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$HOME/.max-auth
ExecStart=/usr/bin/node $HOME/.max-auth/auth-server.js
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
sudo systemctl daemon-reload && sudo systemctl enable --now max-auth
```

### 3. Expose via Tailscale

```bash
sudo tailscale serve --set-path=/auth --bg http://127.0.0.1:8456
```

### 4. Register a passkey

Visit `https://<your-tailscale-hostname>/auth`, log in with your master password, then click "+ Register new passkey". Confirm your master password and use Touch ID / Face ID.

## Integration with OpenClaw Agent

See `references/integration.md` for full agent integration guide.

**Quick reference — check auth before sensitive actions:**

```javascript
const { checkAuthStatus } = require('/home/ubuntu/.max-auth/auth-server.js');
if (!checkAuthStatus()) throw new Error('⚠️ Authentication required. Visit https://<hostname>/auth to log in.');
```

Or via HTTP:

```bash
curl -s http://127.0.0.1:8456/status
# Returns: {"hasPassword":true,"hasSession":true,"sessionExpiresAt":...}
```

## API Reference

| Endpoint | Method | Description |
|---|---|---|
| `GET /auth/status` | GET | Public status (session active?) |
| `GET /auth` | GET | Dashboard UI |
| `POST /auth/login` | POST | Password login → `{token}` |
| `POST /auth/logout` | POST | Clear session |
| `GET /auth/verify` | GET | Verify Bearer token |
| `POST /auth/passkey/reg-options` | POST | Get WebAuthn reg options (requires session + password) |
| `POST /auth/passkey/reg-verify` | POST | Complete passkey registration |
| `GET /auth/passkey/auth-options` | GET | Get WebAuthn auth options |
| `POST /auth/passkey/auth-verify` | POST | Complete passkey auth → `{token}` |
| `POST /auth/passkey/delete` | POST | Remove a passkey |

## CLI Commands

```bash
node auth-server.js                          # Start server
node auth-server.js set-password 'password'  # Set master password
node auth-server.js status                   # Show status
```
