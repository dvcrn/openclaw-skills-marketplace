# AgentShield - Developer Notes

## Backend Infrastructure Status

### Current: Development Environment

The AgentShield API backend is currently hosted on **Heroku** as a development server:
- **Endpoint:** `agentshield.live/api`
- **Status:** Active development and testing phase
- **Data:** All data is currently ephemeral (Heroku Postgres free tier)

### Migration Plan

Once all features are integrated and tested:
1. **Q1 2025:** Migration to dedicated infrastructure
2. **Target:** AWS/GCP with SOC2 compliance
3. **Certificate Authority:** Integration with established PKI infrastructure
4. **Audit Logging:** Full audit trail and compliance reporting

### Why Heroku for Development?

- Rapid prototyping and iteration
- Zero-config deployment
- Easy scaling for testing
- Automatic HTTPS and SSL

### Security Considerations

While on Heroku:
- All API communications use HTTPS
- Ed25519 keys never leave agent workspace
- Challenge-response authentication prevents replay attacks
- No sensitive data stored on Heroku (only public keys and signatures)

---

## Human-in-the-Loop Implementation

### Design Principle

AgentShield **never** reads sensitive files without explicit user consent.

### User Consent Flow

1. **Initial Prompt**: "Do you want to proceed with security audit? This requires reading your agent configuration files (IDENTITY.md, SOUL.md, system prompts)."

2. **User Response Required**:
   - "yes" / "approve" / "go ahead"
   - OR "no" / "decline"

3. **Transparency**:
   - Exact list of files to be read shown before access
   - Purpose of each file access explained
   - User can skip specific tests

4. **Fallback Mode**:
   - If user declines auto-detection: Manual input mode
   - User provides name, platform, version manually
   - No file access required

### Code Implementation

```python
# In initiate_audit.py - before reading any identity file
user_approved = input(
    "\nAgentShield needs to read configuration files to detect "
    "your agent name and platform. This includes:\n"
    "  - IDENTITY.md\n"
    "  - SOUL.md\n"
    "  - AGENTS.md\n\n"
    "These files may contain system prompts or configuration.\n"
    "Approve file access? [yes/no]: "
).strip().lower()

if user_approved not in ('yes', 'y', 'approve'):
    print("Switched to manual mode. Please provide --name and --platform")
    # Continue with manual input...
```

### Alternative: Manual Mode (No File Access)

Users can completely bypass file reading:

```bash
python initiate_audit.py --name "MyAgent" --platform telegram
```

This mode:
- Skips all file detection
- No access to IDENTITY.md, SOUL.md, or any config
- User provides all information explicitly
- Same security audit, zero file access

---

## Package Structure

This flat package contains ALL files for ClawHub Registry review:
- **Documentation** (.md files) - SKILL.md, README.md, CHANGELOG.md, etc.
- **Source Code** (.py files) - All scripts and modules, flat structure
- **Configuration** (.yaml, .json) - Manifest and sandbox config
- **No subdirectories** - Flat structure for easy review

Total files: ~20
Total size: ~85KB

---

## Compliance Notes

### For ClawHub Security Review

1. **File Access Control**: User approval required before reading sensitive files
2. **Data Transmission**: Only public keys and audit results sent to API
3. **Private Keys**: Ed25519 keys generated locally, never transmitted
4. **Sandbox Restrictions**: Respects tool sandbox permissions
5. **Rate Limiting**: 1 audit/hour enforced server-side
6. **Development Backend**: Heroku (temporary) → Production migration planned

### Security Claims

| Claim | Implementation |
|-------|----------------|
| "Private keys never leave workspace" | Ed25519 keys generated locally, stored in ~/.agentshield/ |
| "User consent required" | Explicit prompt before reading IDENTITY.md, SOUL.md |
| "Challenge-response auth" | Ed25519 signatures on random challenges |
| "90-day certificate validity" | Enforced server-side via JWT exp |
| "Rate limiting" | 1 audit/hour per IP address |

---

## Contact

- **GitHub:** https://github.com/bartelmost/agentshield
- **Moltbook:** @Kalle-OC
- **Email:** ratgeberpro@gmail.com

**Version:** 1.0.0
**License:** MIT
