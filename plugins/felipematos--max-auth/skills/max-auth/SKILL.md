---
name: max-auth
description: "Security authentication gate for OpenClaw sensitive actions. Deploys a local Node.js auth server with biometric passkeys (WebAuthn/Touch ID/Face ID) and master password. Exposes a dashboard via Tailscale HTTPS. Use when: (1) setting up authentication for sensitive agent actions, (2) checking if user is authenticated before destructive/external operations, (3) registering or managing passkeys, (4) integrating auth into OpenClaw workflows. Sensitive actions = delete files, install packages, send messages to 3rd parties, call mutating APIs."
---

# Max Auth

Biometric + password authentication server for OpenClaw. Runs at `http://127.0.0.1:8456`, exposed via Tailscale at `https://<hostname>/auth`.

## Quick Setup

```bash
mkdir -p ~/.max-auth
cp <skill>/assets/auth-server.js ~/.max-auth/
cp <skill>/assets/package.json ~/.max-auth/
cd ~/.max-auth && npm install
node auth-server.js set-password 'your_password'
```

Install as systemd service + Tailscale serve — see `references/api.md` for full instructions.

## Checking Auth Before Sensitive Actions

```bash
# Shell
STATUS=$(curl -s http://127.0.0.1:8456/status)
HAS_SESSION=$(echo $STATUS | python3 -c "import sys,json; print(json.load(sys.stdin)['hasSession'])")
[ "$HAS_SESSION" = "True" ] || { echo "⚠️ Auth required: https://<hostname>/auth"; exit 1; }
```

**Sensitive actions requiring auth:** delete files, install packages, system config changes, sending messages/emails to third parties, external API mutations.

**Safe without auth:** read, search, list, web_fetch, memory_search.

When auth is missing, refuse the action and tell the user: "⚠️ Autenticação necessária. Acesse `https://<hostname>/auth`."

## References

- **Full API + setup**: `references/api.md`
- **Agent integration patterns**: `references/integration.md`
