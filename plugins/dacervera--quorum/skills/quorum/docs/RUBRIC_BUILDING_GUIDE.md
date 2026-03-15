# Rubric Building Guide

*How to encode a standard into something Quorum can actually run.*

---

## 1. Overview

A rubric is a machine-readable encoding of what "good" looks like. It's not a vague checklist — it's a set of testable criteria, each with a clear assertion, a severity level, assessment guidance, and evidence requirements. When Quorum runs a rubric, critics evaluate an artifact against each criterion and must cite evidence. No evidence, no finding.

The distinction that matters: a rubric turns a compliance question from *"does this seem right?"* into *"can you prove it meets criterion X from standard Y?"* That's substantiation. It's the difference between a vibe check and a defensible finding.

Building a rubric is fundamentally a knowledge-encoding problem. You take a standard — a published specification, an RFC, an NIST document — and systematically extract its requirements into a form Quorum's critics can evaluate. This guide walks through that process, using PKI publications as worked examples throughout.

**The payoff is compounding.** A good rubric runs indefinitely. You build it once; every subsequent evaluation is essentially free expertise.

---

## 2. Prerequisites

Before you start, you need:

1. **The source document in parseable format.** PDFs with embedded text work fine; scanned PDFs need OCR. See Step 1.
2. **Domain knowledge.** This is non-negotiable. Standards are dense, and normative decomposition without domain knowledge produces rubrics that are technically correct and practically useless. The criteria generation step (Step 3) is where expertise matters most.
3. **A clear scope boundary.** Full standards are large. Decide upfront which sections or requirement types you're encoding. Scope creep kills rubric projects.
4. **The Quorum rubric schema.** See [CONFIG_REFERENCE.md](CONFIG_REFERENCE.md) for the full spec. A rubric is a JSON file; critics consume it at evaluation time.

---

## 3. Step 1: Source Acquisition

Getting the standard into clean markdown is the foundation. Everything downstream depends on text quality.

### Tools

| Situation | Tool | Notes |
|-----------|------|-------|
| Clean, text-based PDF | **PyMuPDF** (`fitz`) | Fast, accurate, preserves structure |
| Scanned or OCR-heavy PDF | **Marker** | Higher quality output, slower |
| Already HTML | Direct fetch | IETF RFCs, many NIST docs |
| DOCX/XLSX | **python-docx** / **openpyxl** | Straightforward |

### Examples

**For RFCs (RFC 3647, RFC 5280):** Fetch directly from IETF — clean plaintext or HTML available at `https://www.rfc-editor.org/rfc/rfcNNNN.txt`. No PDF processing needed.

```bash
curl https://www.rfc-editor.org/rfc/rfc3647.txt -o rfc3647.txt
```

**For NIST SPs:** PDFs from `csrc.nist.gov`. Most have embedded text — PyMuPDF works:

```python
import fitz  # PyMuPDF
doc = fitz.open("sp800-57pt1r5.pdf")
text = "\n".join(page.get_text() for page in doc)
```

**For CA/B Forum Baselines:** Available as PDF from `cabforum.org`. Text-based — PyMuPDF works. Watch for frequent version updates; pin the version in your rubric metadata.

**For ISO standards:** Purchase required. If you have access, export to PDF and process with PyMuPDF or Marker.

### Quality Check

Before proceeding, verify:
- Section numbers are preserved (you'll need them for citations)
- Tables rendered correctly (many requirements live in tables)
- No garbled characters from encoding issues

Invest time here. Garbage in, garbage rubric out.

---

## 4. Step 2: Normative Decomposition

This is the systematic extraction of testable requirements from the source text.

### What You're Looking For

Standards use normative language to distinguish requirements from background text. Per RFC 2119:

| Keyword | Strength | Rubric Category |
|---------|----------|-----------------|
| SHALL / MUST | Mandatory | **CRITICAL** |
| SHALL NOT / MUST NOT | Prohibited | **CRITICAL** |
| SHOULD / RECOMMENDED | Advisory | **HIGH** |
| SHOULD NOT / NOT RECOMMENDED | Advisory prohibition | **HIGH** |
| MAY / OPTIONAL | Permissive | **MEDIUM** |
| Informational / best practice | Non-normative | **LOW** |

Category mapping is deterministic from normative strength. This isn't a judgment call — it's a mechanical mapping. The domain judgment comes in Step 3 when you define what evidence satisfies the criterion.

### Decomposition Process

For each normative statement you find:

1. **Record the section reference** — e.g., `RFC3647 §4.2.1`
2. **Extract the full statement** — verbatim, not paraphrased
3. **Identify the subject** — what entity does this apply to? (CA, subscriber, RA, relying party, etc.)
4. **Tag normative strength** — SHALL/SHOULD/MAY
5. **Flag compound statements** — "The CA SHALL do X AND Y AND Z" → three separate criteria

Compound requirements are the most common mistake. A single sentence can contain multiple independent testable assertions. Decompose them. Assessment against a compound assertion is ambiguous; assessment against three atomic assertions is precise.

### RFC 3647 Note

RFC 3647's structure is unusually well-suited to decomposition. The CP/CPS framework is organized into 9 major sections (1-9) with standardized subsections — certificate issuance, revocation, operational security, etc. Each subsection maps cleanly to a policy component. This means section references carry semantic weight: if you're looking for subscriber obligations, you know where to look.

### Output Format

Produce a working document (markdown table or spreadsheet) with columns:

| Section | Statement (verbatim) | Subject | Normative Strength | Notes |
|---------|---------------------|---------|-------------------|-------|
| RFC3647 §4.2.1 | The CA SHALL verify the identity of... | CA | SHALL | Compound — split into 3a, 3b, 3c |

Don't try to generate rubric JSON yet. This intermediate format lets you review and refine before committing to structure.

---

## 5. Step 3: Criteria Generation

This is where the rubric comes alive — and where domain expertise is irreplaceable.

Each normative statement from Step 2 becomes a rubric criterion. A criterion has:

- **`id`** — unique identifier, e.g., `rfc3647.4.2.1.a`
- **`category`** — severity tier: `CRITICAL` / `HIGH` / `MEDIUM` / `LOW` (from Step 2 mapping)
- **`criterion`** — the testable claim (what must be true)
- **`evidence_type`** — how to gather evidence: `tool` (grep, file read), `web_search`, `manual`
- **`evidence_instruction`** — specific directions for what the critic should look for and how
- **`rationale`** — *why* this criterion matters; what risk does a failure represent?

The **evidence instruction** is where expertise earns its keep. "The CA SHALL verify subscriber identity" is the normative statement. But what does verification look like in evidence? Does a ceremony record suffice? A signed attestation? An audit log entry? A configuration file showing the verification step? Someone who doesn't know PKI operations will write vague guidance. Someone who does knows exactly what to look for.

### Example: RFC 3647 §4.2.1

Normative statement: *"The CA SHALL verify the identity of all subscribers before issuing certificates."*

```json
{
  "id": "rfc3647.4.2.1",
  "category": "CRITICAL",
  "criterion": "The CA verifies subscriber identity prior to certificate issuance using documented procedures.",
  "evidence_type": "tool",
  "evidence_instruction": "Search the CP/CPS for identity verification procedures (typically §3.2 or equivalent). Check for: (1) a documented verification procedure specific enough to be auditable — 'we verify identity' is insufficient; 'government-issued photo ID verified in-person or via video call per [procedure ref]' is sufficient, (2) evidence the procedure distinguishes between certificate types if the CA issues multiple, (3) RA delegation documentation if verification is outsourced.",
  "rationale": "Identity verification is the foundation of certificate trust. A CA that issues certificates without verified identity undermines the entire PKI trust chain. Unverified subscribers enable impersonation and man-in-the-middle attacks."
}
```

### Practical Notes

- **Start with SHALL statements.** CRITICAL criteria define the floor. Get those right first.
- **Evidence instruction is the hard part.** Budget most of your domain expertise time here.
- **Evidence instructions should be concrete.** "Check documentation" is too vague. "Search CP/CPS §3.2 for identity verification procedure" is better. "Grep for RA ceremony records showing dual-control authorization" is best.
- **Avoid circular criteria.** "The CA shall comply with the CA/B Forum requirements" isn't testable — it's a reference to another standard. Decompose the actual requirement.

---

## 6. Step 4: Concordance Mapping (Optional but Powerful)

Concordance mapping cross-references terms and requirements across related standards. It's optional for a working rubric — but it turns a rubric into an intelligence layer.

### What It Adds

Single-standard rubrics answer: *"Does this meet RFC 3647?"*

Multi-standard concordance answers: *"This requirement in RFC 3647 maps to this requirement in CA/B Baselines, which is addressed differently in WebTrust — here's the gap."*

That's a qualitatively different output. It surfaces alignment, gaps, and conflicts across the standards landscape automatically.

### Process

1. **Identify related standards.** For PKI: RFC 3647 ↔ CA/B Forum Baselines ↔ WebTrust ↔ RFC 5280 ↔ ETSI EN 319 411.
2. **Extract vocabulary.** Key terms from each standard. "Subscriber," "Subject," "End Entity" may refer to the same concept across standards — or subtly different ones.
3. **Map requirements to requirements.** Which criterion in Standard A corresponds to which in Standard B? One-to-one, one-to-many, or gap (no counterpart)?
4. **Document the mapping.** Add `concordance` metadata to each criterion:

```json
{
  "id": "rfc3647.4.2.1",
  "concordance": {
    "cab_baselines": "BR §3.2.2",
    "webtrust": "Principle 1, Criterion 1.2.4",
    "alignment": "aligned",
    "notes": "CA/B is more specific about acceptable verification methods; RFC 3647 is framework-level"
  }
}
```

### Timeline Impact

Concordance adds 1-2 days to a single-standard rubric build. The payoff: future rubrics for related standards build on existing mappings rather than starting from scratch. The first concordance-mapped rubric in a domain is expensive; subsequent ones are incremental.

---

## 7. Step 5: Packaging

Structure your criteria as a Quorum rubric configuration.

### Rubric File Structure

```json
{
  "id": "rfc3647-v1.0",
  "name": "RFC 3647 — Certificate Policy / CPS Framework",
  "version": "1.0.0",
  "source": {
    "standard": "RFC 3647",
    "title": "Internet X.509 Public Key Infrastructure Certificate Policy and Certification Practices Framework",
    "url": "https://www.rfc-editor.org/rfc/rfc3647",
    "pinned_version": "2003-11"
  },
  "scope": "Evaluates certificate policies and CPS documents against RFC 3647 framework requirements.",
  "critics": ["correctness", "completeness"],
  "grading": {
    "pass_threshold": 0.85,
    "critical_tolerance": 0,
    "high_tolerance": 2
  },
  "criteria": [
    {
      "id": "rfc3647.4.2.1",
      "category": "CRITICAL",
      "criterion": "The CA verifies subscriber identity prior to certificate issuance using documented procedures.",
      "evidence_type": "tool",
      "evidence_instruction": "Search CP/CPS for identity verification procedures...",
      "rationale": "Identity verification is the foundation of certificate trust..."
    }
    // ... more criteria
  ]
}
```

### Key Packaging Decisions

**Which critics?** Match critics to what the rubric is evaluating:
- `correctness` — always include; verifies claims are accurate
- `completeness` — always include; checks coverage
- Additional critics (security, architecture, delegation) are on the roadmap — see SPEC.md for the full 9-agent design

**Grading thresholds:**
- `critical_tolerance: 0` means any CRITICAL failure → REJECT verdict. Appropriate for compliance rubrics.
- `pass_threshold: 0.85` means 85% of criteria must pass for a PASS verdict.

**Evidence requirements format:** Be specific. Critics use these to know what to look for in the artifact.

---

## 8. Worked Example: RFC 3647 §4.2 — Certificate Application Processing

This walks through all five steps for a concrete slice of RFC 3647.

### Source Text (Step 1)

From `https://www.rfc-editor.org/rfc/rfc3647.txt`, section 4.2:

> **4.2. Certificate Application Processing**
>
> This section describes procedures for processing certificate applications, including:
>
> 4.2.1. Performing identification and authentication functions
>
> CPs or CPSs may describe how the CA or RA performs identification and authentication for certificate applications, including:
>
> - Verification of identity claims
> - Validation of supporting documentation
> - The means by which authentication of individuals is performed

### Normative Decomposition (Step 2)

RFC 3647 is a framework document — it describes what a CP/CPS *should address*, not always in SHALL terms. The normative force here is about the CP/CPS being complete and explicit on these points.

| Section | Statement | Subject | Strength | Notes |
|---------|-----------|---------|----------|-------|
| 4.2.1 | CP/CPS SHALL address how identity claims are verified | CA/RA | SHALL | Framework completeness requirement |
| 4.2.1 | CP/CPS SHALL address how supporting documentation is validated | CA/RA | SHALL | Framework completeness requirement |
| 4.2.1 | CP/CPS SHALL describe authentication method for individuals | CA/RA | SHALL | Framework completeness requirement |

### Criteria Generation (Step 3)

```json
[
  {
    "id": "rfc3647.4.2.1.a",
    "category": "CRITICAL",
    "criterion": "The CP/CPS explicitly describes the procedure for verifying identity claims in certificate applications.",
    "evidence_type": "tool",
    "evidence_instruction": "Search the CP/CPS for identity verification subsections (typically §3.2 or equivalent). The description must be specific enough to be auditable — 'we verify identity' is insufficient; 'government-issued photo ID verified in-person or via video call per [procedure ref]' is sufficient. Check that the procedure distinguishes between certificate types if the CA issues multiple. If RA-delegated, look for RA agreement specifying verification responsibilities.",
    "rationale": "Without a documented, auditable identity verification procedure, there is no basis for trusting that certificates were issued to verified subscribers. This is a foundational CP/CPS requirement."
  },
  {
    "id": "rfc3647.4.2.1.b",
    "category": "CRITICAL",
    "criterion": "The CP/CPS explicitly describes what supporting documentation is required and how it is validated.",
    "evidence_type": "tool",
    "evidence_instruction": "Look for an enumeration of acceptable document types (government ID, organizational attestation, domain control verification methods, etc.) and the validation procedure for each. Vague language ('appropriate documentation') does not satisfy this criterion. Check for document retention requirements.",
    "rationale": "Without specified documentation requirements, verification procedures are unauditable and inconsistent across issuance events."
  },
  {
    "id": "rfc3647.4.2.1.c",
    "category": "CRITICAL",
    "criterion": "The CP/CPS explicitly describes the authentication method(s) used for individual subscribers.",
    "evidence_type": "tool",
    "evidence_instruction": "The description must cover the authentication mechanism (in-person, video, notarized, vouching) and who performs it (CA directly, accredited RA, trusted third party). Check that the method is appropriate for the certificate assurance level claimed. If multiple certificate types: method must be specified per type.",
    "rationale": "Authentication method determines the assurance level of the issued certificate. Undocumented methods cannot be audited or compared against claimed assurance levels."
  }
]
```

### Packaging (Step 5)

These three criteria go into a rubric file targeting PKI policy documents (CPS, CP). The critic configuration:
- `correctness` — are the documented procedures actually sound?
- `completeness` — does the document cover all §4.2.1 requirements?

The output: a running Quorum evaluation of any CP/CPS against RFC 3647 §4.2, with cited evidence gaps and actionable findings.

---

## 9. Timeline Estimates

| Milestone | Duration |
|-----------|----------|
| Source acquisition + quality check | 2-4 hours |
| Normative decomposition (single standard) | 4-8 hours |
| Criteria generation (with domain expertise) | 1-2 days |
| Review pass + refinement | 4-8 hours |
| **Working rubric** | **1-2 days** |
| Validation run (dogfood against known-good artifact) | 4 hours |
| Refinement based on validation | 4-8 hours |
| **Validated rubric** | **3 days** |
| Concordance mapping (1 related standard) | 1-2 days |
| **Rubric with concordance** | **4-5 days** |

These assume focused work, good source quality, and pre-existing domain expertise. If you're learning the domain as you go, add 50-100%.

---

## 10. Tips

**Scope discipline is the most important thing.** Pick one section of one standard and do it well. A complete rubric for RFC 3647 §4.2 beats a sketchy rubric for all of RFC 3647. You can always extend.

**Start with the highest-ROI standards.** "ROI" means: how often will this rubric run, and what's the cost of a missed finding? For PKI: CA/B Baselines are high-frequency (every audit) and high-stakes (public trust). NIST SP 800-57 is relevant to anyone operating a CKMS. RFC 3647 is essential for any CA writing or reviewing a CPS.

**Dogfood immediately.** Run your rubric against a document you already understand — ideally one with known issues. If the rubric catches the issues you know about, it's working. If it misses them, your assessment guidance needs refinement.

**Evidence instructions are more important than criteria.** A critic with a clear criterion but vague evidence instruction will produce findings you can't verify. A critic with specific evidence instructions forces the evaluation to be concrete.

**Version your rubrics.** Standards update. CA/B Baselines version frequently. When a standard changes, your rubric needs a version bump with a changelog. Build this expectation in from the start.

**Build concordance incrementally.** Don't try to map everything at once. When you build your second rubric in a domain, map it to your first. Concordance grows naturally if you make it a habit.

---

*Questions or rubric contributions → [CONTRIBUTING.md](../CONTRIBUTING.md)*
