# Agent Audit Trail 🔐

**Tamper-evident, hash-chained audit logging for AI agents. EU AI Act ready.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![OpenClaw](https://img.shields.io/badge/OpenClaw-skill-orange.svg)](https://github.com/openclaw/openclaw)

---

## Why This Exists

AI agents act autonomously — writing files, executing commands, calling APIs, making decisions. **But how do you prove what happened?** How do you demonstrate that records weren't altered after the fact?

From **2 August 2026**, the [EU AI Act](https://eur-lex.europa.eu/eli/reg/2024/1689/oj) enters full applicability. If you deploy AI systems that affect EU citizens, you need:

| Requirement | EU AI Act Article | This Tool |
|-------------|------------------|-----------|
| **Automatic event logging** | Article 12 (Record-Keeping) | ✅ Every action logged with timestamp, actor, domain |
| **Tamper-evident records** | Article 12 (Integrity) | ✅ SHA-256 hash chaining — any modification breaks the chain |
| **Human oversight capability** | Article 14 (Human Oversight) | ✅ Gate references link actions to human approvals |
| **Transparency / auditability** | Article 50 (Transparency) | ✅ Human-readable NDJSON, one-command verification |
| **Chronological ordering** | Article 12 (Traceability) | ✅ Monotonic ordering tokens |

**This isn't just good practice anymore. In 163 days, it's the law.**

---

## What It Does

A simple, zero-dependency audit log with cryptographic integrity:

- **Append-only NDJSON** — Human-readable, grep-friendly, machine-parseable
- **SHA-256 hash chaining** — Each entry cryptographically links to all previous entries
- **Tamper detection** — Any modification breaks the chain from that point forward
- **One-command verification** — Instantly validate the entire audit history
- **Gate references** — Link autonomous actions to human approval events
- **Domain partitioning** — Separate audit trails by security domain
- **Zero dependencies** — Python 3.9+ stdlib only. No packages to audit.

---

## Quick Start

```bash
# Clone or copy the script
curl -O https://raw.githubusercontent.com/roosch269/agent-audit-trail/main/scripts/auditlog.py
chmod +x auditlog.py

# Log an action
./auditlog.py append --kind "file-write" --summary "Created config.yaml"

# Verify integrity
./auditlog.py verify
# Output: OK (1 entries verified)
```

---

## Usage

### Log an Action

```bash
./auditlog.py append \
  --kind "exec" \
  --summary "Ran database backup" \
  --target "pg_dump production" \
  --domain "ops" \
  --gate "approval-123" \
  --provenance '{"channel": "slack", "user": "admin"}' \
  --details '{"duration_ms": 4500}'
```

### Verify the Chain

```bash
./auditlog.py verify
# OK (42 entries verified)
```

Returns exit code 0 if valid, 1 if tampered, with details about which line failed.

### Configuration

| Environment Variable | Default | Description |
|---------------------|---------|-------------|
| `AUDIT_LOG_PATH` | `audit/agent-actions.ndjson` | Log file location |
| `AUDIT_LOG_TZ` | `UTC` | Timezone for timestamps |
| `AUDIT_LOG_ACTOR` | `agent` | Default actor name |

Or use CLI flags: `--log`, `--tz`, `--actor`

---

## Log Format

Each line is a self-contained JSON object:

```json
{
  "ts": "2026-02-24T07:15:00+00:00",
  "kind": "exec",
  "actor": "atlas",
  "domain": "ops",
  "plane": "action",
  "target": "pg_dump production",
  "summary": "Ran database backup",
  "gate": "approval-123",
  "provenance": {"channel": "slack", "user": "admin"},
  "ord": 42,
  "chain": {
    "prev": "abc123...",
    "hash": "def456...",
    "algo": "sha256(prev\\nline_c14n)"
  }
}
```

### Field Reference

| Field | Required | Description |
|-------|----------|-------------|
| `ts` | Auto | ISO-8601 timestamp with timezone offset |
| `kind` | Yes | Event type (`file-write`, `exec`, `api-call`, `credential-access`, `external-write`) |
| `actor` | Auto | Who performed the action |
| `domain` | No | Security domain for partitioning (`ops`, `personal`, `client`, etc.) |
| `plane` | Auto | Processing plane (default: `action`) |
| `target` | No | What was acted upon (file path, URL, command) |
| `summary` | Yes | Human-readable description |
| `gate` | No | Reference to human approval (for gated actions) |
| `provenance` | No | Source attribution — channel, user, message ID |
| `details` | No | Additional structured data |
| `ord` | Auto | Monotonic ordering token |
| `chain` | Auto | Hash chain: `prev` hash, current `hash`, algorithm |

---

## EU AI Act Compliance Guide

### For Deployers (Article 12 — Record-Keeping)

The EU AI Act requires automatic logging of events for AI systems. This tool provides:

1. **What was logged**: Every action includes `kind`, `summary`, `target` — answering *what happened*
2. **When it happened**: ISO-8601 timestamps with timezone — answering *when*
3. **Who authorised it**: `gate` field links to human approval — answering *who approved this*
4. **Proof of integrity**: Hash chain means the record can't be altered without detection
5. **Traceability**: Monotonic `ord` tokens provide chronological ordering

### For High-Risk Systems (Articles 12 + 14)

If your AI system is classified as **high-risk** under the EU AI Act:

```bash
# Log with full provenance for high-risk actions
./auditlog.py append \
  --kind "decision" \
  --summary "Credit scoring model output: approved" \
  --target "application-12345" \
  --domain "high-risk" \
  --gate "human-review-req-456" \
  --provenance '{"model": "credit-v2", "confidence": 0.87}' \
  --details '{"input_hash": "sha256:abc...", "output": "approved", "reviewer": "jane@company.com"}'
```

### Recommended Audit Kinds for Compliance

| Kind | When to Use | EU AI Act Relevance |
|------|------------|-------------------|
| `decision` | AI makes/recommends a decision | Art. 14 — human oversight |
| `file-write` | Agent creates or modifies files | Art. 12 — record-keeping |
| `exec` | Agent runs a command | Art. 12 — traceability |
| `api-call` | External API interaction | Art. 12 — record-keeping |
| `credential-access` | Secrets or credentials accessed | Art. 12 — security logging |
| `external-write` | Agent writes to external systems | Art. 12 + Art. 14 |
| `human-override` | Human overrides AI decision | Art. 14 — oversight evidence |
| `disclosure` | AI identity disclosed to user | Art. 50 — transparency |

---

## How It Works

```
Entry N-1                    Entry N
┌─────────────────┐         ┌─────────────────┐
│ ts, kind, ...   │         │ ts, kind, ...   │
│ chain.hash: H1  │───┬────▶│ chain.prev: H1  │
└─────────────────┘   │     │ chain.hash: H2  │
                      │     └─────────────────┘
                      │            │
                      └────────────┴──▶ H2 = sha256(H1 + "\n" + canonical(entry))
```

Tampering with any entry changes its hash, which breaks the chain for all subsequent entries. Verification is O(n) — one pass through the log.

---

## Integration

### OpenClaw (Heartbeat)

Add to your `HEARTBEAT.md` for automatic integrity checks:

```markdown
## Audit integrity check
- Run: `./scripts/auditlog.py verify`
  - If fails: alert with line number
  - If OK: silent
```

### CI/CD Pipeline

```yaml
# .github/workflows/audit-verify.yml
- name: Verify audit trail
  run: python scripts/auditlog.py verify
```

### Python Integration

```python
from scripts.auditlog import append_entry, verify

# Log from your agent code
append_entry("audit/agent-actions.ndjson", {
    "kind": "api-call",
    "summary": "Called OpenAI API",
    "target": "gpt-4",
    "domain": "inference",
})

# Verify programmatically
success, message = verify("audit/agent-actions.ndjson")
assert success, f"Audit chain broken: {message}"
```

---

## Security Model

**What this provides:**
- ✅ Evidence of what happened
- ✅ Detection of post-hoc tampering
- ✅ Chronological ordering guarantees
- ✅ Domain-partitioned audit trails
- ✅ Human approval linkage (gate references)

**What this doesn't provide:**
- ❌ Prevention of malicious logging (a compromised agent can lie)
- ❌ Protection against log deletion (use offsite backups)
- ❌ Root-level security (admins can rewrite everything)

This is *audit*, not *access control*. It makes tampering **detectable**, not impossible. For comprehensive agent governance, pair with access controls, human-in-the-loop gates, and offsite log replication.

---

## Comparison

| Feature | Agent Audit Trail | Basic file logging | Database logging |
|---------|------------------|--------------------|-----------------|
| Tamper detection | ✅ Hash chain | ❌ | ❌ |
| Zero dependencies | ✅ | ✅ | ❌ |
| Human-readable | ✅ NDJSON | ✅ | ❌ |
| Chronological proof | ✅ Monotonic ord | ❌ | Partial |
| EU AI Act ready | ✅ | ❌ | Partial |
| Setup time | 30 seconds | 30 seconds | Hours |
| Gate references | ✅ | ❌ | Custom |

---

## Requirements

- Python 3.9+ (for `zoneinfo`; falls back to UTC on older versions)
- No external dependencies
- Works on Linux, macOS, WSL

---

## Roadmap (v2.1+)

- [ ] `export` command — generate compliance report from log
- [ ] `stats` command — event counts, domain breakdown, time range queries
- [ ] JSON Schema for log validation
- [ ] Optional remote log shipping (append-only S3/GCS)
- [ ] Compliance report template (EU AI Act Article 12)

---

## Contributing

Issues and PRs welcome! Please:
- Keep it simple (no new dependencies)
- Maintain backward compatibility with existing logs
- Add tests for new features

---

## License

MIT — Use freely, contribute back if you improve it.

---

## Links

- **EU AI Act full text**: [eur-lex.europa.eu](https://eur-lex.europa.eu/eli/reg/2024/1689/oj)
- **OpenClaw**: [github.com/openclaw/openclaw](https://github.com/openclaw/openclaw)
- **ClawHub**: [clawhub.com](https://clawhub.com)

---

Built with 🔐 by [Roosch](https://github.com/roosch269) and [Atlas](https://github.com/roosch269/agent-audit-trail)
