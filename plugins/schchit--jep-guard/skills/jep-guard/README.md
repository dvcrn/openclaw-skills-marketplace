# JEP Guard for OpenClaw

**Version 1.0.2**

JEP Guard adds a **responsibility layer** to your Clawbot. It intercepts high-risk commands, requires your confirmation, and optionally generates verifiable JEP receipts for every action.

---

## ⚠️ Important Privacy Notice

**JEP Guard logs commands to `~/.jep-guard-audit.log`**

### Log Levels

| Level | What gets logged | Risk |
|-------|------------------|------|
| `minimal` (default) | Command names only | ✅ Safe |
| `normal` | Commands + redacted arguments | ⚠️ Medium |
| `verbose` | Full command lines | ❌ High |

**Sensitive data (passwords, tokens, API keys) may be logged if you:**
- Set log level to `verbose`
- Use commands with sensitive arguments

**Your responsibility:** Review logs regularly and set appropriate log level.

---

## 📦 Dependencies

**Optional:** `@jep-eth/sdk` for real JEP signatures
- Without it: Receipts are **not generated**
- Install: `npm install -g @jep-eth/sdk`
- Generate keys: `claw run jep-guard keygen` (requires SDK)

---

## ✨ Features

- **🛡️ High-risk command interception** - `rm`, `mv`, `cp` commands need your approval
- **✅ User confirmation** - Popup dialog before dangerous operations
- **🔐 Temporary authorization** - 5-minute tokens for approved commands
- **📝 Audit logging** - All actions recorded with timestamps
- **🔑 JEP receipt generation** - Optional cryptographically verifiable receipts (requires SDK + your key)
- **📤 Export logs** - Export audit trail as JSON

---

## 📥 Installation

```bash
claw install jep-guard
```

During installation, you will see a privacy warning. Read it carefully before proceeding.

---

## 🚀 Quick Start

```bash
# 1. Check current settings
claw run jep-guard config

# 2. (Optional) Generate JEP keys for signed receipts
claw run jep-guard keygen

# 3. Test protection - try to delete a file
rm test.txt
# JEP Guard will ask for confirmation

# 4. Export audit logs
claw run jep-guard export
```

---

## ⚙️ Configuration

```bash
# View current configuration
claw run jep-guard config

# Set log level
claw run jep-guard config set logLevel minimal   # Safe (default)
claw run jep-guard config set logLevel normal    # Redacted arguments
claw run jep-guard config set logLevel verbose   # Full arguments (caution!)

# Show recent logs
claw run jep-guard config show
```

---

## 🔐 JEP Signing

JEP Guard **never uses placeholder or default keys**. Receipts are only generated if you:

1. Install JEP SDK: `npm install -g @jep-eth/sdk`
2. Generate your own key pair: `claw run jep-guard keygen`
3. Your private key is stored in `~/.jep-guard-config.json`

Without a key, receipts are **not generated**.

**⚠️ Private key security:** Your key is stored in plain text in the config file. Protect this file accordingly.

---

## 📤 Export Logs

```bash
claw run jep-guard export
```

Exports audit logs as JSON with redaction based on your current log level setting.

---

## 🗑️ Uninstall

```bash
claw uninstall jep-guard
```

During uninstall, you will be asked whether to keep or delete audit logs.

---

## 📄 License

MIT-0

---

## 🔗 Links

- **Repository:** https://github.com/hjs-eth/jep-claw-integration/tree/main/jep-guard
- **JEP Protocol:** https://github.com/hjs-spec

---

## ⚠️ Known Limitations

- Config file stores private key in plain text
- JEP receipts require separate SDK installation
- No network features (all processing local)
- Logs may contain sensitive data if set to verbose mode
