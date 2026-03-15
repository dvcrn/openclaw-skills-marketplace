---
name: fact-check
description: "Verify claims, statements, and information against reliable sources. Use when user asks to fact-check, verify, confirm, validate, or check the accuracy of any statement, statistic, quote, date, or claim. Performs cross-reference searches, identifies source credibility, and provides evidence-based verdicts."
---

# Fact Check

Verify information through systematic source verification.

## Workflow

1. **Identify the claim** - Extract the specific statement to verify
2. **Search sources** - Query reliable sources (news outlets, academic papers, official databases)
3. **Cross-reference** - Check multiple independent sources
4. **Evaluate credibility** - Assess source reliability and potential biases
5. **Deliver verdict** - Provide clear conclusion with evidence

## Claim Types

| Type | Approach | Trusted Sources |
|------|----------|-----------------|
| Statistics | Find original study/data | Government databases, peer-reviewed journals |
| Quotes | Locate primary source | Official transcripts, news archives |
| News events | Verify via multiple outlets | Major news organizations |
| Historical facts | Consult academic sources | Encyclopedias, scholarly publications |
| Product/company info | Check official sources | Company websites, SEC filings |

## Source Hierarchy

**Tier 1 (Highest):**
- Peer-reviewed journals
- Government databases/official statistics
- Court records, legal documents

**Tier 2:**
- Major news outlets (Reuters, AP, BBC, etc.)
- Established academic institutions
- Official company/organization statements

**Tier 3:**
- Social media (verify via other sources)
- Blogs, personal websites
- Unverified reports

## Output Format

```
Claim: [exact statement]

Verdict: [TRUE / MOSTLY TRUE / UNVERIFIABLE / MOSTLY FALSE / FALSE]

Evidence:
- Source 1: [details]
- Source 2: [details]

Notes: [context, caveats, or additional context]
```

## Constraints

- Never state certainty beyond what evidence supports
- Distinguish between "unverified" and "false"
- Provide sources, don't just claim verification
- Flag opinions vs facts clearly
- Update verdict if new evidence emerges
