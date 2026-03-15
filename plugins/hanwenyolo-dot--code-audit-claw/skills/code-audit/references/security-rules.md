# Security Audit Rules

## 🔴 Critical (立即修复)

### Hardcoded Secrets
- API keys, tokens, passwords in plain text
- Pattern: `(api_key|secret|password|token)\s*=\s*["'][^"']{8,}`
- Pattern: `sk-[a-zA-Z0-9]{20,}`, `Bearer [a-zA-Z0-9]{20,}`

### Dangerous Shell Commands
- `rm -rf /` or `rm -rf` without confirmation
- `os.system()` / `subprocess` with user input (command injection risk)
- `eval()` / `exec()` with external input

### SQL Injection
- String concatenation in SQL: `"SELECT * FROM " + user_input`
- f-string SQL: `f"SELECT ... WHERE id={id}"`

### Sensitive Data Exposure
- Logging passwords/tokens: `print(password)`, `logger.info(token)`
- Writing secrets to files without encryption

## 🟡 Warning (应尽快修复)

### Unsafe Deserialization
- `pickle.loads()` on untrusted data
- `yaml.load()` without `Loader=yaml.SafeLoader`

### Path Traversal
- `open(user_input)` without path sanitization
- `os.path.join()` with unvalidated user input

### Weak Cryptography
- MD5 / SHA1 for password hashing
- Random without `secrets` module for security tokens

## 🟢 Info (建议改进)

### Error Handling
- Bare `except:` clauses that swallow errors silently
- Exposing stack traces to end users

### Dependency Issues
- Pinned dependencies with known CVEs
- `requirements.txt` without version pinning

### Environment Variable Fallback Hardcoding
- 使用 `os.environ.get("KEY", "hardcoded_value")` 将硬编码值作为 fallback
- Pattern: `os\.environ\.get\(["'][^"']+["'],\s*["'][^"']{4,}["']\)`
- 风险：密钥/密码以默认值形式暴露在代码中，即使未设置环境变量也会生效
- 正确做法：`os.environ["KEY"]`（无 fallback，未设置时直接报错，强制显式配置）
