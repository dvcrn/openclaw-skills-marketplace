---
name: fact-checker
description: "Verify claims with web search, assign confidence scores, and generate structured fact-check reports."
---

# Fact Checker

Automated fact-checking with confidence scoring and source attribution.

**Use when** verifying claims, checking article accuracy, or fact-checking content before publishing.

## Requirements

- `web_search` tool access
- No API keys needed

## Instructions

1. **Extract claims** from the provided text. List each claim separately. Skip opinions and subjective statements — only fact-check factual assertions.

2. **Search for evidence** using `web_search` for each claim. Search for the core factual assertion, not the full sentence. Run 2-3 searches with different phrasings if initial results are inconclusive.

3. **Evaluate sources** with this hierarchy:
   - 🥇 Official sources (government, organizations cited in the claim)
   - 🥈 Peer-reviewed research, established wire services (AP, Reuters)
   - 🥉 Major news outlets with editorial standards
   - ⚠️ Blogs, social media, opinion pieces (note as weak evidence)

4. **Assign verdict** to each claim:
   | Verdict | Confidence | Criteria |
   |---------|-----------|----------|
   | ✅ Verified | 90-100% | Multiple reliable sources confirm |
   | ⚠️ Partially True | 50-89% | True with caveats or missing context |
   | ❌ False | 0-29% | Contradicted by reliable sources |
   | 🔍 Unverifiable | N/A | Insufficient sources to determine |

5. **Output format**:
   ```
   ## 🔍 Fact Check Report
   **Source:** [article/text title]
   **Date checked:** YYYY-MM-DD

   ### Claim 1: "[exact claim text]"
   **Verdict:** ✅ Verified (95%)
   **Evidence:** [2-3 sentence summary]
   **Sources:**
   - [Source name](URL) — [key finding]
   - [Source name](URL) — [key finding]

   ### Summary
   | # | Claim | Verdict |
   |---|-------|---------|
   | 1 | [short claim] | ✅ Verified |
   | 2 | [short claim] | ❌ False |
   **Overall accuracy: X/Y claims verified**
   ```

## Edge Cases & Troubleshooting

- **Date-sensitive claims**: Note when the info was last verified. Facts about statistics, rankings, or prices change frequently.
- **Ambiguous claims**: If a claim can be interpreted multiple ways, check the most charitable interpretation first, then note caveats.
- **No sources found**: Mark as 🔍 Unverifiable — absence of evidence is not evidence of absence.
- **Conflicting sources**: Report the conflict explicitly. Note which sources are more authoritative and why.
- **Satire/parody**: Flag if the original source appears to be satirical.

## Security Considerations

- Never fabricate sources or URLs — only cite actually found results.
- Don't present search snippets as verified facts; always cross-reference.
- Disclose limitations transparently in the report.
