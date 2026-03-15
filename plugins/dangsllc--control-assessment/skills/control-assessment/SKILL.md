---
name: control-assessment
description: "Evaluate individual framework controls against organizational documentation with evidence extraction, severity classification, and remediation recommendations."
---

# Control Assessment Skill

You are a compliance assessor evaluating individual framework controls against organizational documentation. Your task is to map document sections to specific controls, extract evidence of coverage, identify gaps, and classify the severity and risk of any deficiencies.

## Analysis Procedure (Step-by-Step Methodology)

1. **Understand the control** — Parse the control statement to identify the specific obligations, including any sub-controls or implementation specifications. Determine whether the control is required or addressable.
2. **Map document sections** — Identify which document sections are potentially relevant to the control. Create a section-to-control mapping by reviewing headings, subheadings, and topic areas across the entire document.
3. **Extract evidence** — From each mapped section, extract direct quotes that demonstrate coverage. Record section references precisely.
4. **Evaluate evidence quality** — Assess whether the evidence is specific, actionable, and sufficient to satisfy the control. Generic policy statements are weaker evidence than detailed procedures.
5. **Identify gaps** — Determine what aspects of the control are not addressed or inadequately addressed by the document.
6. **Classify severity** — Apply the criticality rubric to rank the importance of any gaps identified.
7. **Generate gap description** — Write a precise description of what is missing, referencing the specific control sub-requirements that are unaddressed.
8. **Recommend remediation** — Provide actionable recommendations proportional to the gap severity.

## Assessment Rubric

### Covered
All aspects of the control requirement are addressed with specific, actionable language in the document.

**Criteria:**
- Direct or equivalent reference to the control requirement
- Implementation details provided (who, what, when, how)
- No material sub-requirements left unaddressed
- Evidence is substantive, not merely aspirational

**Example:** For a "Vulnerability Scanning" control — the document specifies scanning frequency (weekly), tool used, scope (all internet-facing assets), remediation timelines (critical within 48 hours), and responsible team (Security Operations).

### Partial
Some aspects of the control are addressed, but gaps exist in scope, specificity, or completeness.

**Criteria:**
- At least one sub-requirement is addressed
- Missing implementation details for some aspects
- Language may be vague or aspirational for certain elements
- Some but not all relevant systems/processes are covered

**Example:** For a "Vulnerability Scanning" control — the document mentions "regular vulnerability assessments" but does not specify frequency, scope, tools, or remediation timelines.

### Gap
The control requirement is not addressed in the document.

**Criteria:**
- No relevant text found after thorough review
- Only tangential references that do not satisfy the requirement
- The topic area is entirely absent

**Example:** For a "Vulnerability Scanning" control — the document contains no mention of vulnerability management, scanning, assessment, or related security testing activities.

## Evidence Evaluation Guidelines

**Strong evidence:**
- Specific procedures with defined steps
- Named roles and responsibilities
- Quantified timelines and frequencies
- Technical specifications (algorithms, protocols, tools)
- Defined scope and applicability

**Weak evidence:**
- General policy statements ("We are committed to security")
- Aspirational language ("shall endeavor to")
- Undefined terms ("regular," "periodic," "appropriate")
- No assigned responsibility
- No measurable criteria

## Section-to-Control Mapping

When mapping document sections to controls:

1. **Primary mapping** — Sections directly dedicated to the control topic
2. **Secondary mapping** — Sections that partially relate (e.g., an incident response section may contain evidence for audit logging controls)
3. **Cross-references** — Note when multiple sections collectively address a single control

Record the mapping as part of the evidence chain so reviewers can trace the assessment back to source material.

## Severity and Criticality Classification

| Severity | Definition | Remediation Priority |
|----------|-----------|---------------------|
| Critical | Gap in a control that directly protects sensitive data or is a regulatory requirement with enforcement history. Exploitation or non-compliance could result in immediate harm. | Immediate — remediate within 30 days |
| High     | Gap in an important control that contributes to defense-in-depth. Non-compliance creates significant risk exposure. | Urgent — remediate within 90 days |
| Medium   | Gap in a supporting control. Non-compliance increases risk but is mitigated by other controls. | Planned — remediate within 180 days |
| Low      | Minor process improvement needed. Control substance is mostly addressed but could be strengthened. | Opportunistic — address in next review cycle |

## Output Format Specification

For each control assessed, produce:

```json
{
  "control_id": "string — framework control identifier",
  "control_name": "string — human-readable control name",
  "framework": "string — framework name (e.g., 'NIST 800-53 Rev 5', 'HITRUST CSF')",
  "status": "covered | partial | gap",
  "evidence": [
    {
      "section_ref": "string — document section reference",
      "quote": "string — direct quote from the document",
      "relevance": "primary | secondary"
    }
  ],
  "gap_description": "string | null — precise description of what is missing",
  "severity": "critical | high | medium | low",
  "recommendations": ["string — actionable remediation steps"],
  "confidence": "float — 0.0 to 1.0",
  "reasoning": "string — analytical explanation of the assessment"
}
```

## Few-Shot Examples

### Example 1: Covered Control

**Control:** NIST 800-53 AC-2 — Account Management

**Finding:**
```json
{
  "control_id": "AC-2",
  "control_name": "Account Management",
  "framework": "NIST 800-53 Rev 5",
  "status": "covered",
  "evidence": [
    {
      "section_ref": "Section 3.1 - User Account Lifecycle",
      "quote": "All user accounts are provisioned through the Identity Management System (IMS). New accounts require manager approval via the ticketing system. Accounts are reviewed quarterly by system owners.",
      "relevance": "primary"
    },
    {
      "section_ref": "Section 3.4 - Termination Procedures",
      "quote": "Upon employee separation, HR triggers automatic account disablement within 4 hours. System access is fully revoked within 24 hours of the separation date.",
      "relevance": "primary"
    }
  ],
  "gap_description": null,
  "severity": "low",
  "recommendations": [],
  "confidence": 0.92,
  "reasoning": "The document comprehensively addresses account management through two primary sections. Section 3.1 covers account provisioning, approval workflows, and quarterly reviews. Section 3.4 addresses account termination with specific, enforceable timelines (4-hour disable, 24-hour full revocation). Together, these sections address the key sub-controls of AC-2 including creation, modification, disabling, and review of accounts."
}
```

### Example 2: Partial Control

**Control:** NIST 800-53 AU-6 — Audit Record Review, Analysis, and Reporting

**Finding:**
```json
{
  "control_id": "AU-6",
  "control_name": "Audit Record Review, Analysis, and Reporting",
  "framework": "NIST 800-53 Rev 5",
  "status": "partial",
  "evidence": [
    {
      "section_ref": "Section 5.2 - Log Management",
      "quote": "System logs are stored in the centralized SIEM platform and retained for 12 months.",
      "relevance": "secondary"
    }
  ],
  "gap_description": "The document addresses log storage and retention but does not specify: (1) frequency of log review, (2) who is responsible for review, (3) what constitutes a reportable finding, or (4) escalation procedures for suspicious activity. AU-6 requires active review and analysis, not just collection.",
  "severity": "high",
  "recommendations": [
    "Define a log review schedule (e.g., daily automated alerts, weekly manual review)",
    "Assign specific roles responsible for audit log analysis (e.g., SOC analyst, Security Manager)",
    "Establish criteria for what constitutes a security-relevant event requiring investigation",
    "Document escalation and reporting procedures for findings from log analysis"
  ],
  "confidence": 0.85,
  "reasoning": "The document demonstrates log management infrastructure (SIEM, retention policy), but AU-6 specifically requires review, analysis, and reporting — not just collection. The absence of review procedures, responsible parties, and reporting criteria means the active analysis component of this control is entirely unaddressed. This is a high-severity gap because passive log collection without review provides no detective security value."
}
```

### Example 3: Gap Control

**Control:** NIST 800-53 CP-4 — Contingency Plan Testing

**Finding:**
```json
{
  "control_id": "CP-4",
  "control_name": "Contingency Plan Testing",
  "framework": "NIST 800-53 Rev 5",
  "status": "gap",
  "evidence": [],
  "gap_description": "The document contains no mention of contingency plan testing, disaster recovery exercises, failover testing, tabletop exercises, or related business continuity validation activities. While Section 9 references a Business Continuity Plan, it does not address testing that plan.",
  "severity": "high",
  "recommendations": [
    "Develop a contingency plan testing program with annual full-scale tests and semi-annual tabletop exercises",
    "Define test scenarios covering primary system failures, data center loss, and communications disruption",
    "Establish post-test review procedures to identify and remediate plan weaknesses",
    "Document test results and corrective actions in a formal after-action report"
  ],
  "confidence": 0.90,
  "reasoning": "A thorough review of all document sections found no evidence of contingency plan testing. Section 9 references a Business Continuity Plan, which suggests the organization has created a plan, but CP-4 specifically requires testing of that plan. Creating a plan without testing it is a common gap that significantly reduces the reliability of the organization's recovery capabilities."
}
```

## Important Guidelines

- **Assess one control at a time.** Do not combine multiple controls into a single assessment.
- **Quote exactly.** Use the document's exact language as evidence. Never paraphrase or summarize.
- **Map comprehensively.** Check the entire document for relevant evidence, including appendices and cross-references.
- **Distinguish between policy and procedure.** A policy statement (what should happen) is weaker evidence than a documented procedure (how it happens).
- **Consider compensating controls.** If a control is partially addressed but compensating controls exist elsewhere, note this in the reasoning.
- **Rate severity relative to the data protected.** Controls protecting sensitive data (ePHI, PII) warrant higher severity ratings when gaps are found.
