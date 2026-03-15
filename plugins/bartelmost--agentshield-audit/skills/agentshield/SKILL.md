---
name: agentshield
description: "Trust Infrastructure for AI Agents - Like SSL/TLS for agent-to-agent communication. 77 security tests, cryptographic certificates, and Trust Handshake Protocol for establishing secure channels between agents."
---

# AgentShield - Trust Infrastructure for AI Agents

**The trust layer for the agent economy. Like SSL/TLS, but for AI agents.**

🔐 **Cryptographic Identity** - Ed25519 signing keys  
🤝 **Trust Handshake Protocol** - Mutual verification before communication  
📋 **Public Trust Registry** - Reputation scores & track records  
✅ **77 Security Tests** - Comprehensive vulnerability assessment

**🔒 Privacy Disclosure:** See [PRIVACY.md](PRIVACY.md) for detailed data handling information.

---

## 🎯 The Problem

Agents need to communicate with other agents (API calls, data sharing, task delegation). But **how do you know if another agent is trustworthy?**

- Has it been compromised?
- Is it leaking data?
- Can you trust its responses?

Without a trust layer, agent-to-agent communication is like HTTP without SSL - **unsafe and unverifiable**.

---

## 💡 The Solution: Trust Infrastructure

AgentShield provides the **trust layer** for agent-to-agent communication:

### 1. Cryptographic Identity
- **Ed25519 key pairs** - Industry-standard cryptography
- **Private keys stay local** - Never transmitted
- **Public key certificates** - Signed by AgentShield

### 2. Security Audit (77 Tests)
**52 Live Attack Vectors:**
- Prompt injection (15 variants)
- Encoding exploits (Base64, ROT13, Hex, Unicode)
- Multi-language attacks (Chinese, Russian, Arabic, Japanese, German, Korean)
- Social engineering (emotional appeals, authority pressure, flattery)
- System prompt extraction attempts

**25 Static Security Checks:**
- Input sanitization
- Output DLP (data leak prevention)
- Tool sandboxing
- Secret scanning
- Supply chain security

**Result:** Security score (0-100) + Tier (VULNERABLE → HARDENED)

### 3. Trust Handshake Protocol
**Agent A wants to communicate with Agent B:**

```bash
# Step 1: Both agents get certified
python3 initiate_audit.py --auto

# Step 2: Agent A initiates handshake with Agent B
python3 handshake.py --target agent_B_id

# Step 3: Both agents sign challenges
# (Automatic in v1.0.13+)

# Step 4: Receive shared session key
# → Now you can communicate securely!
```

**What you get:**
- ✅ Mutual verification (both agents are who they claim to be)
- ✅ Shared session key (for encrypted communication)
- ✅ Trust score boost (+5 for successful handshakes)
- ✅ Public track record (handshake history)

### 4. Public Trust Registry
- **Searchable database** of all certified agents
- **Reputation scores** based on audits, handshakes, and time
- **Trust tiers:** UNVERIFIED → BASIC → VERIFIED → TRUSTED
- **Revocation list (CRL)** - Compromised agents get flagged

---

## 🚀 Quick Start

### Install
```bash
clawhub install agentshield
cd ~/.openclaw/workspace/skills/agentshield*/
```

### Get Certified (77 Security Tests)
```bash
# Auto-detect agent name from IDENTITY.md/SOUL.md
python3 initiate_audit.py --auto

# Or manual:
python3 initiate_audit.py --name "MyAgent" --platform telegram
```

**Output:**
- ✅ Agent ID: `agent_xxxxx`
- ✅ Security Score: XX/100
- ✅ Tier: PATTERNS_CLEAN / HARDENED / etc.
- ✅ Certificate (90-day validity)

### Verify Another Agent
```bash
python3 verify_peer.py agent_yyyyy
```

### Trust Handshake with Another Agent
```bash
# Initiate handshake
python3 handshake.py --target agent_yyyyy

# Result: Shared session key for encrypted communication
```

---

## 📋 Use Cases

### 1. Agent-to-Agent API Calls
**Before:** Agent A calls Agent B's API - no way to verify B's integrity  
**With AgentShield:** Agent A checks Agent B's certificate + handshake → Verified communication

### 2. Multi-Agent Task Delegation
**Before:** Orchestrator spawns sub-agents - can't verify they're safe  
**With AgentShield:** All sub-agents certified → Orchestrator knows they're trusted

### 3. Agent Marketplaces
**Before:** Download random agents from the internet - no trust guarantees  
**With AgentShield:** Browse Trust Registry → Only hire VERIFIED agents

### 4. Data Sharing Between Agents
**Before:** Share sensitive data with another agent - hope it doesn't leak  
**With AgentShield:** Handshake → Encrypted session key → Secure data transfer

---

## 🛡️ Security Architecture

### Privacy-First Design

✅ **All 77 tests run locally** - Your system prompts NEVER leave your device  
✅ **Private keys stay local** - Only public keys transmitted  
✅ **Human-in-the-Loop** - Explicit consent before reading IDENTITY.md/SOUL.md  
✅ **No environment scanning** - Doesn't scan for API tokens  

**What goes to the server:**
- Public key (Ed25519)
- Agent name & platform
- Test scores (passed/failed summary)

**What stays local:**
- Private key
- System prompts
- Configuration files
- Detailed test results

### Environment Variables (Optional)
```bash
AGENTSHIELD_API=https://agentshield.live  # API endpoint
AGENT_NAME=MyAgent                        # Override auto-detection
OPENCLAW_AGENT_NAME=MyAgent               # OpenClaw standard
```

---

## 📊 What You Get

### Certificate (90-day validity)
```json
{
  "agent_id": "agent_xxxxx",
  "public_key": "...",
  "security_score": 85,
  "tier": "PATTERNS_CLEAN",
  "issued_at": "2026-03-10",
  "expires_at": "2026-06-08"
}
```

### Trust Registry Entry
- ✅ Public verification URL: `agentshield.live/verify/agent_xxxxx`
- ✅ Trust score (0-100) based on:
  - Age (longer = more trust)
  - Verification count
  - Handshake success rate
  - Days active
- ✅ Tier: UNVERIFIED → BASIC → VERIFIED → TRUSTED

### Handshake Proof
```json
{
  "handshake_id": "hs_xxxxx",
  "requester": "agent_A",
  "target": "agent_B",
  "status": "completed",
  "session_key": "...",
  "completed_at": "2026-03-10T20:00:00Z"
}
```

---

## 🔧 Scripts Included

| Script | Purpose |
|--------|---------|
| `initiate_audit.py` | Run 77 security tests & get certified |
| `handshake.py` | Trust handshake with another agent |
| `verify_peer.py` | Check another agent's certificate |
| `show_certificate.py` | Display your certificate |
| `agentshield_tester.py` | Standalone test suite (advanced) |

---

## 🌐 Trust Handshake Protocol (Technical)

### Flow
1. **Initiate:** Agent A → Server: "I want to handshake with Agent B"
2. **Challenge:** Server generates random challenges for both agents
3. **Sign:** Both agents sign their challenges with private keys
4. **Verify:** Server verifies signatures with public keys
5. **Complete:** Server generates shared session key
6. **Trust Boost:** Both agents +5 trust score

### Cryptography
- **Algorithm:** Ed25519 (curve25519)
- **Key Size:** 256-bit
- **Signature:** Deterministic (same message = same signature)
- **Session Key:** AES-256 compatible

---

## 🚀 Roadmap

**Current (v1.0.13):**
- ✅ 77 security tests
- ✅ Ed25519 certificates
- ✅ Trust Handshake Protocol
- ✅ Public Trust Registry
- ✅ CRL (Certificate Revocation List)

**Coming Soon:**
- ⏳ Auto re-audit (when prompts change)
- ⏳ Negative event reporting
- ⏳ Fleet management (multi-agent dashboard)
- ⏳ Trust badges for messaging platforms

---

## 📖 Learn More

- **Website:** https://agentshield.live
- **GitHub:** https://github.com/bartelmost/agentshield
- **API Docs:** https://agentshield.live/docs
- **ClawHub:** https://clawhub.ai/bartelmost/agentshield

---

## 🎯 TL;DR

**AgentShield is SSL/TLS for AI agents.**

Get certified → Verify others → Establish trust handshakes → Communicate securely.

```bash
# 1. Get certified
python3 initiate_audit.py --auto

# 2. Handshake with another agent
python3 handshake.py --target agent_xxxxx

# 3. Verify others
python3 verify_peer.py agent_yyyyy
```

**Building the trust layer for the agent economy.** 🛡️

---

## 🔒 Data Transmission Transparency

### What Gets Sent to AgentShield API

**During Audit Submission:**
```json
{
  "agent_name": "YourAgent",
  "platform": "telegram",
  "public_key": "base64_encoded_ed25519_public_key",
  "test_results": {
    "score": 85,
    "tests_passed": 74,
    "tests_total": 77,
    "tier": "PATTERNS_CLEAN",
    "failed_tests": ["test_name_1", "test_name_2"]
  }
}
```

**What is NOT sent:**
- ❌ Full test output/logs
- ❌ Your prompts or system messages
- ❌ IDENTITY.md or SOUL.md file contents
- ❌ Private keys (stay in `~/.agentshield/agent.key`)
- ❌ Workspace files or memory

**API Endpoint:**
- Primary: `https://agentshield.live/api` (proxies to Heroku backend)
- All traffic over HTTPS (TLS 1.2+)

---

## 🛡️ Consent & Privacy

**File Read Consent:**
1. Skill requests permission BEFORE reading IDENTITY.md/SOUL.md
2. User sees: "Read IDENTITY.md for agent name? [Y/n]"
3. If declined: Manual mode (`--name` flag)
4. If approved: Only name/platform extracted (not full file content)

**Privacy-First Mode:**
```bash
export AGENTSHIELD_NO_AUTO_DETECT=1
python initiate_audit.py --name "MyBot" --platform "telegram"
```
→ Zero file reads, manual input only

See [PRIVACY.md](PRIVACY.md) for complete data handling documentation.

