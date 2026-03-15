# Infra — Configuration & Security Hygiene

Check for configuration duplication, secret exposure, and credential management issues.

## Checks

### 1. Secret Hardcoding
```bash
# Find hardcoded secrets (API keys, passwords, tokens with values)
grep -rn --include="*.sh" --include="*.py" \
  -E '(secret|password|api_key|token)\s*[=:]\s*["'"'"'][A-Za-z0-9+/]{16,}' \
  <project_root> | grep -v "test\|mock\|#"
```
- **Issue if**: Same secret value in >1 file
- **Fix**: Centralize in one config file, all scripts read from it

### 2. Token Logic Duplication
```bash
# Count files that implement their own token fetching
grep -rl --include="*.sh" --include="*.py" \
  "tenant_access_token\|app_access_token" <project_root>
```
- **Issue if**: >2 files independently fetch tokens
- **Fix**: Create shared module (e.g., `common.sh`), all scripts `source` it

### 3. Config Value Duplication
```bash
# Find values appearing in multiple files
grep -roh --include="*.sh" --include="*.py" \
  -E '[a-z]{3}_[a-z0-9]{16,}' <project_root> | sort | uniq -c | sort -rn
```
- **Issue if**: Same identifier appears in >2 files
- **Fix**: Single source of truth (config file or env var)

### 4. Test Data Security
```bash
# Check test files for real credentials
find <project_root> -path "*/test*" -exec \
  grep -l -E '(secret|password)\s*=\s*["'"'"'][A-Za-z0-9]{16,}' {} \;
```
- **Issue if**: Any match → real secrets in test code
- **Fix**: Use dummy values or env vars

### 5. Centralized Config Verification
```bash
# Verify scripts read from central config
grep -rl "openclaw.json\|\.env\|config\.json" <project_root>
```
- Scripts that DON'T read from config → candidates for migration

## Output

```
Infrastructure Health
─────────────────────
Secret hardcoding:  [N files with hardcoded secrets]
Token duplication:  [N files with independent token logic]  
Config values:      [N values duplicated across files]
Test data security: [N test files with real credentials]
Central config:     [N/M scripts use centralized config]
```
