# OpenClaw Agent Integration Guide

## When to check auth

The agent MUST verify an active session before:

1. **Destructive actions** — deleting files, clearing data, dropping databases
2. **System configuration** — installing packages, modifying system files, changing rules
3. **External impact** — sending emails/messages to third parties, posting to social media, making payments, calling external APIs that mutate state

Read-only operations (searching, listing, reading files, fetching data) do NOT require auth.

## How to check auth (Node.js)

```javascript
const http = require('http');

function checkAuth() {
  return new Promise((resolve) => {
    http.get('http://127.0.0.1:8456/status', (res) => {
      let body = '';
      res.on('data', d => body += d);
      res.on('end', () => {
        try {
          const { hasSession } = JSON.parse(body);
          resolve(hasSession === true);
        } catch { resolve(false); }
      });
    }).on('error', () => resolve(false));
  });
}

// Usage
async function sensitiveAction() {
  const authed = await checkAuth();
  if (!authed) {
    throw new Error('⚠️ Autenticação necessária. Acesse https://<hostname>/auth para autenticar.');
  }
  // ... proceed with action
}
```

## How to check auth (shell/exec)

```bash
SESSION=$(curl -s http://127.0.0.1:8456/status | python3 -c "import sys,json; print(json.load(sys.stdin)['hasSession'])")
if [ "$SESSION" != "True" ]; then
  echo "⚠️ Authentication required. Visit https://<hostname>/auth"
  exit 1
fi
```

## Agent Behavior Pattern

When a sensitive action is requested:

1. Check `http://127.0.0.1:8456/status`
2. If `hasSession: true` → proceed normally
3. If `hasSession: false` → refuse the action and tell the user:
   > "⚠️ Ação sensível bloqueada. Autentique-se em `https://<hostname>/auth` e tente novamente."

Do NOT silently skip the action or proceed anyway.

## Sensitive vs Safe Examples

| Action | Requires auth? |
|--------|----------------|
| `ls`, `cat`, `grep` | ❌ No |
| `rm`, `rmdir`, `truncate` | ✅ Yes |
| `apt install`, `npm install -g` | ✅ Yes |
| `sudo systemctl` changes | ✅ Yes |
| `git push`, `gh pr create` | ✅ Yes |
| `message send` (to 3rd parties) | ✅ Yes |
| `web_fetch`, `web_search` | ❌ No |
| `read`, `memory_search` | ❌ No |
| `write`, `edit` (local workspace) | Depends — use judgment |
