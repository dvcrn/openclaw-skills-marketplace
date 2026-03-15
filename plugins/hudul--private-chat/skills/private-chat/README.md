# Private Chat for OpenClaw

🔐 Private Chat Mode - Add encrypted conversation capabilities to your OpenClaw assistant

[📖 中文文档](README.zh.md)

## Features

- 🔑 **Codeword Trigger** - Enter private mode with a secret codeword
- 🛡️ **AES-256-CBC Encryption** - Military-grade encryption for sensitive information
- ⏱️ **Auto Timeout** - Automatic exit to prevent information leakage
- 📝 **Secure Storage** - Encrypted content stored in separate files
- 🔓 **Decrypt Anytime** - Command-line and interactive decryption tools provided

## Demo

### Enter Private Mode
```
User: lgbt
AI: Entering Private Mode 🔒
    Welcome back. How can I help you?
```

### Store Sensitive Information
```
User: My bank card password is 123456
AI: Securely stored ✅
    Your bank card password has been encrypted and saved.
    Storage: memory/private-vault.md
    Encryption: AES-256-CBC
```

### Retrieve Encrypted Content
```
User: What's my bank card password?
AI: Your bank card password: 123456
```

## Installation

```bash
clawhub install private-chat
```

## Configuration

1. Copy example config:
```bash
cd skills/private-chat
cp config.example.json config.json
```

2. Edit `config.json`:
```json
{
  "codeword": "your-secret-codeword",
  "password": "your-encryption-password",
  "autoExitMinutes": 1,
  "storageFile": "memory/private-vault.md"
}
```

## Encryption Format

All encrypted content uses standard format:
```
ENC[v1:SALT:BASE64]
```

Example:
```
ENC[v1:a1b2c3d4:U2FsdGVkX1+...]
```

## Decryption Tools

### Command Line

```bash
# Encrypt
./scripts/private-vault.sh encrypt "password" "secret text"

# Decrypt
./scripts/private-vault.sh decrypt "password" "ENC[v1:...]"

# Interactive
./scripts/private-vault.sh interactive
```

### Using OpenSSL

```bash
echo "BASE64_CONTENT" | base64 -d | \
  openssl enc -aes-256-cbc -d -k "password" -pbkdf2
```

## Security Tips

⚠️ **Please ensure:**
- Use a strong password (16+ chars, mixed case + numbers + symbols)
- Regularly backup `memory/private-vault.md`
- Never share your encryption password with anyone

⚠️ **Warning:**
- If you forget the password, encrypted content **cannot be recovered**
- Don't manually modify encrypted file format
- After exiting private mode, AI won't remember any conversation content

## How It Works

1. **Trigger Detection** - AI detects codeword, enters private mode
2. **Content Recognition** - Identifies sensitive information (passwords, keys, etc.)
3. **Auto Encryption** - Encrypts sensitive content using AES-256-CBC
4. **Secure Storage** - Saves to separate encrypted file
5. **Auto Exit** - Exits automatically after timeout, clearing context

## Author

By OpenClaw Community

## License

MIT
