# Security Declaration

## Code Safety
- ✅ No malicious code or backdoors
- ✅ No hardcoded credentials or API keys
- ✅ No dangerous system operations
- ✅ Standard browser automation only

## Data Handling
- User credentials: Stored locally in SQLite (encrypted)
- Session data: Local cache only, no external transmission
- No data collection or telemetry

## Dependencies
- playwright>=1.40.0 (Mozilla official)
- Standard Python libraries only

## Permissions Required
- Local file system (for cache)
- Network access (for web automation)
- Browser control (via Playwright)

## Audit
Last security scan: 2026-03-10
Scan result: PASSED
