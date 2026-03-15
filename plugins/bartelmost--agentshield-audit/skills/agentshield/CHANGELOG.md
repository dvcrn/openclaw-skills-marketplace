# Changelog

All notable changes to AgentShield will be documented in this file.

## [1.0.22] - 2026-03-11

### Fixed
- **Hardcoded API Endpoint**: Changed `complete_handshake.py` API URL
  - From: `https://agentshield-api-bartel-fe94823ceeea.herokuapp.com/api`
  - To: `https://agentshield.live/api` (domain-aligned)
  - Resolves OpenClaw scanner flag about external Heroku endpoint

### Added
- **Data Transmission Transparency Section** (SKILL.md)
  - Explicit JSON example of `test_results` payload
  - Clear "What is NOT sent" list (prompts, logs, workspace files)
  - API endpoint documentation (HTTPS, TLS 1.2+)
- **Consent Flow Documentation** (SKILL.md)
  - Documented file read prompt: "Read IDENTITY.md? [Y/n]" BEFORE access
  - Privacy-First mode examples (`AGENTSHIELD_NO_AUTO_DETECT=1`)
- **PRIVACY.md**: Comprehensive data handling guide
  - What data is read (IDENTITY.md, SOUL.md)
  - What data is sent (name, platform, public key, scores)
  - What is NOT sent (private keys, prompts, workspace)
  - Manual mode instructions

### Changed
- Version number updated in `_meta.json`, `clawhub.json`, `SKILL.md`

### Impact
- Addresses OpenClaw scanner concerns from v1.0.20
- Expected rating improvement: Suspicious MEDIUM → Benign/Low Risk
- No breaking changes - same 77 tests + Trust Handshake Protocol

## [1.0.13] - 2026-03-10

### Added
- **77 REAL Security Tests**: Integrated `AgentShieldSecurityTester` into audit flow
  - 52 Live Attack Vectors
  - 25 Static Security Checks
  - Categories: Prompt Injection, API Security, Data Protection, Tool Security, System Integrity, Output Safety, Supply Chain
- **Trust Handshake Helper Script**: `handshake.py` for easy agent-to-agent verification
  - Usage: `python3 handshake.py --target agent_xxxxx`
  - Auto-loads your agent ID from certificate
  - Simplified trust handshake initiation

### Fixed
- **CRITICAL**: Previous version only ran 5 placeholder tests (now 77 real tests!)
- **Import Path**: Fixed `agentshield_security` module import issues
- **Test Integration**: `agentshield_tester.py` now properly called by `initiate_audit.py`

### Changed
- Security scores now accurately reflect real test results (not placeholders)
- Test output shows detailed pass/fail breakdown by category

### Impact
- Expected score increase from ~77 to 85-95 for well-configured agents
- More accurate security assessment
- Better vulnerability detection

## [1.0.12] - 2026-03-10

### Fixed
- API URL Bug: Fixed double `/api/api` path
- Documentation Transparency: Clarified environment variable usage
  - `clawhub.json`: Explicitly declared env vars
  - `SKILL.md`: Added "Environment Variables" section

## [1.0.11] - 2026-03-10

### Fixed
- API URL Bug: Fixed double `/api/api` path in API calls

## [1.0.10] - 2026-03-07

### Changed
- Updated to AgentShield API v1.4
- Trust Handshake Protocol support

## [1.0.0] - 2026-02-24

### Added
- Initial ClawHub release
- Ed25519 cryptographic identity
- Certificate signing
- Auto-detection
- Peer verification
