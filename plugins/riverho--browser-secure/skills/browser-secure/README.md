# 🔒 Browser Secure

> Secure browser automation with vault integration, approval gates, and comprehensive audit logging.

## Philosophy

**"Never trust, always verify, encrypt everything, audit all actions"**

Browser Secure fetches credentials from your password manager (Bitwarden or 1Password) only when needed. Credentials are retrieved from your vault (Bitwarden/1Password) when needed, used immediately, then cleared from memory. For automation convenience, optional `.env` file support is available (gitignored by default) — use this only on trusted, private machines. They're retrieved from the vault, used for the login action, then discarded from memory.

---

## 🚀 Quick Start

### 1. Install (via Clawdbot - Recommended)

The easiest way—just ask Clawdbot to install it for you:

```
Hey Clawdbot, install browser-secure for me
```

Or if you prefer to run it yourself:

```bash
# Clone and install from GitHub
curl -fsSL https://raw.githubusercontent.com/openclaw/openclaw/main/scripts/install-browser-secure.sh | bash
```

This handles everything automatically:
- ✅ Checks prerequisites (Node.js 18+, Chrome)
- 📦 Auto-installs missing dependencies (Playwright browsers, optional vault CLIs)
- 🔨 Builds and links the CLI globally
- 📝 Creates default configuration

### 2. Install (Manual - Advanced)

If you prefer full control or are developing on the tool:

```bash
# Clone the repository
git clone https://github.com/openclaw/openclaw.git
cd openclaw/skills/browser-secure

# Run interactive setup
npm run setup
```

### 3. Create Your Automation Profile

Instead of using your personal Chrome profile (with all your personal data), create an isolated profile specifically for automation:

```bash
# Create a new Chrome profile with welcome page
browser-secure profile --create "The Crustacean Station 🦞"

# Create and immediately launch Chrome
browser-secure profile --create "Automation Profile" --launch
```

This creates:
- An isolated Chrome profile directory
- A custom **welcome page** that opens automatically
- Pre-configured settings for secure automation

### 4. Follow the Welcome Page

When Chrome opens, you'll see a welcome page that guides you through:

#### 🔌 Install Required Extensions

1. **Bitwarden** (Recommended) - Free, open-source password manager
   - Click "Install from Web Store" on the welcome page
   - Or visit: [chrome.google.com/webstore/bitwarden](https://chromewebstore.google.com/detail/bitwarden-password-manage/nngceckbapebfimnlniiiahkandclblb)

2. **OpenClaw Browser Relay** - Connects browser to OpenClaw
   - Click "Install from Web Store" on the welcome page
   - Enables seamless automation control

#### 🗝️ Log In to Your Vault

**Option A: Bitwarden (Recommended - Free)**

1. Create a free account at [bitwarden.com](https://bitwarden.com) (if you don't have one)
2. Click the Bitwarden extension icon in Chrome toolbar
3. Log in with your master password
4. Add passwords to your vault (or import from your current password manager)

5. **Enable CLI access** (in your terminal):
```bash
# If Bitwarden CLI wasn't auto-installed
brew install bitwarden-cli

# Log in
bw login

# Unlock for CLI access
export BW_SESSION=$(bw unlock --raw)
```

**Option B: 1Password (If you have a subscription)**

1. Install the 1Password extension from the Chrome Web Store
2. Log in to your 1Password account
3. Enable CLI access:
```bash
# If 1Password CLI wasn't auto-installed  
brew install 1password-cli

# Sign in
op signin
eval $(op signin)
```

### 5. Start Automating

```bash
# Navigate to a site (uses your new profile with vault credentials)
browser-secure navigate https://github.com --profile "Profile-the-crustacean-station"

# Or use auto-vault discovery
browser-secure navigate https://app.neilpatel.com --auto-vault

# Extract data
browser-secure extract "list my repositories"

# Close when done
browser-secure close
```

---

## 📖 Why This Approach Is Safer

### The Problem with Traditional Automation

Most browser automation tools handle credentials like this:

```bash
# ❌ BAD: Credentials in CLI (visible in history)
my-tool login --username="user@example.com" --password="secret123"

# ❌ BAD: Credentials in environment variables (leaked to child processes)
export PASSWORD="secret123"
my-tool login

# ❌ BAD: Credentials in config files (plaintext on disk)
cat config.json
{ "password": "secret123" }
```

**Problems:**
- Passwords appear in shell history (`~/.bash_history`, `~/.zsh_history`)
- Environment variables are visible to all child processes
- Config files are often committed to git by mistake
- Credentials linger in memory after use

### The Browser Secure Approach

```bash
# ✅ GOOD: No credentials in CLI
browser-secure navigate https://github.com --site=github

# Credentials flow:
# 1. You authenticate to your vault (Bitwarden/1Password) once per session
# 2. Vault stays encrypted at rest
# 3. When needed, credentials are retrieved via secure API
# 4. Used immediately, then cleared from memory
# 5. Session timeout auto-clears everything (30 min default)
```

**Security Features:**

| Feature | Protection |
|---------|------------|
| **Vault Integration** | Credentials never leave encrypted vault until needed |
| **No CLI History** | No passwords in command history or logs |
| **Memory Safety** | Credentials cleared from memory immediately after use |
| **Session Timeout** | Auto-cleanup after 30 minutes (configurable) |
| **Isolated Profiles** | Automation profile separate from personal browsing |
| **Approval Gates** | Must approve sensitive actions (logins, purchases) |
| **Audit Trail** | Every action logged with cryptographic chain hashing |
| **Network Restrictions** | Blocks localhost/private IPs to prevent pivot attacks |

### Chrome Profile Isolation

Using a dedicated automation profile protects you in multiple ways:

| Aspect | Personal Profile | Automation Profile |
|--------|------------------|-------------------|
| **Extensions** | All your personal extensions | Only automation extensions (Bitwarden, Browser Relay) |
| **Cookies** | Personal logins, shopping, social media | Only automation-targeted sites |
| **History** | Personal browsing history | Automation session history only |
| **Security** | Linked to your personal Google account | Isolated, no personal data |
| **Cleanup** | Manual | Automatic session timeout + secure deletion |

**Scenario:** If a malicious script runs during automation:
- With personal profile: Could access your Gmail, banking cookies, personal data
- With automation profile: Only sees automation-targeted sites, no personal data

---

## 🛡️ Security Model

```
┌─────────────────────────────────────────────────────────────────┐
│                      USER REQUEST                                │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│  1. PROFILE SELECTION                                           │
│     • Use isolated automation profile OR                        │
│     • Use incognito mode (no persistence)                       │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│  2. VAULT AUTHENTICATION                                        │
│     • Unlock Bitwarden: export BW_SESSION=$(bw unlock --raw)    │
│     • Unlock 1Password: eval $(op signin)                       │
│     • Vault remains encrypted at rest                           │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│  3. APPROVAL GATE                                               │
│     • Read-only actions: Navigate, screenshot, extract          │
│     • Form fill: Click, type, select (prompts for approval)     │
│     • Authentication: fill_password, submit_login (always ask)  │
│     • Destructive: delete, purchase (requires 2FA if enabled)   │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│  4. ISOLATED SESSION                                            │
│     • Time-bounded (30 min default, auto-expiry)                │
│     • Isolated work directories (UUID-based)                    │
│     • Network restrictions (block localhost/private IPs)        │
│     • Secure cleanup (overwrite + delete)                       │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│  5. AUDIT LOG                                                   │
│     • Immutable logs with SHA-256 chain hashing                 │
│     • Tamper-evident: any modification breaks chain             │
│     • Retention: 30 days (configurable)                         │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📋 Commands Reference

| Command | Description |
|---------|-------------|
| `browser-secure profile --create "Name"` | Create new Chrome profile with welcome page |
| `browser-secure profile --create "Name" --launch` | Create profile and launch Chrome |
| `browser-secure profile --list` | List all Chrome profiles |
| `browser-secure navigate <url>` | Open URL, optionally with profile or authentication |
| `browser-secure navigate <url> --profile <id>` | Use specific Chrome profile |
| `browser-secure navigate <url> --profile select` | Interactively choose Chrome profile |
| `browser-secure navigate <url> --list-profiles` | List available Chrome profiles |
| `browser-secure navigate <url> --site=<name>` | Use pre-configured site credentials |
| `browser-secure navigate <url> --auto-vault` | Auto-discover credentials from vault |
| `browser-secure act "<instruction>"` | Perform natural language action |
| `browser-secure extract "<instruction>"` | Extract data from page |
| `browser-secure screenshot` | Take screenshot |
| `browser-secure close` | Close browser and cleanup |
| `browser-secure status` | Show session status |
| `browser-secure audit` | View audit logs |
| `browser-secure vault --list` | List available vaults |
| `browser-secure vault --test <site>` | Test vault credentials for a site |
| `browser-secure config --edit` | Edit configuration |

---

## ⚙️ Configuration

Create `~/.browser-secure/config.yaml`:

```yaml
vault:
  provider: bitwarden  # Options: bitwarden, 1password, keychain, env
  
  # Pre-configured site credentials
  sites:
    github:
      vault: "Personal"
      item: "GitHub"
      usernameField: "username"
      passwordField: "password"
    
    nytimes:
      vault: "News"
      item: "NYT Account"
      usernameField: "email"

security:
  sessionTimeoutMinutes: 30
  credentialCacheMinutes: 10
  requireApprovalFor:
    - fill_password
    - submit_login
  blockLocalhost: true
  auditScreenshots: true

audit:
  enabled: true
  retentionDays: 30
```

---

## 🔐 Vault Providers

### Bitwarden (Recommended - Free)

Free, open-source, cross-platform. Best choice for most users.

```bash
# Install CLI
brew install bitwarden-cli

# Login
bw login
export BW_SESSION=$(bw unlock --raw)

# Use
browser-secure navigate https://github.com --auto-vault
```

### 1Password (Paid)

If you already have a 1Password subscription.

```bash
# Install CLI
brew install 1password-cli

# Login
op signin
eval $(op signin)

# Use
browser-secure navigate https://github.com --auto-vault
```

### macOS Keychain (Local)

Store credentials locally (no cloud sync). Good for single-machine use.

### Environment Variables (Fallback)

**Note:** Environment variables are supported for compatibility, but vault integration is recommended for security.

```bash
export BROWSER_SECURE_GITHUB_USERNAME="user@example.com"
export BROWSER_SECURE_GITHUB_PASSWORD="secret"
browser-secure navigate https://github.com --site=github
```

For automated workflows, a `.env` file can be used (see `.env.example`). This stores credentials in a gitignored file that is loaded at runtime — suitable only for private, trusted machines.

---

## 🆘 Troubleshooting

**"Vault is locked" error**
```bash
# Bitwarden
export BW_SESSION=$(bw unlock --raw)

# 1Password
eval $(op signin)
```

**Chrome keychain prompt on first run**
This is normal! When Playwright launches Chrome, macOS asks about keychain access. You can click "Deny" since Browser Secure manages credentials through your vault, not Chrome's built-in storage.

**Profile not found**
```bash
browser-secure profile --list  # See available profiles
browser-secure profile --create "My Profile"  # Create new one
```

**Session expired**
Default 30-minute TTL. Restart with `--timeout 3600` for longer sessions (in seconds).

**Approval required for every action**
Use `-y` flag to auto-approve (be careful!): `browser-secure act "click login" -y`

---

## 📄 License

MIT

---

## 🔗 Links

- [OpenClaw Documentation](https://docs.openclaw.ai)
- [Bitwarden](https://bitwarden.com)
- [1Password](https://1password.com)
- [Report Issues](https://github.com/openclaw/openclaw/issues)
