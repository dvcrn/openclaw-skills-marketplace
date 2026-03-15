---
name: prism
description: |
  Parallel Review by Independent Specialist Models. Multi-agent review protocol
  that deploys 5+ specialist reviewers in parallel to eliminate confirmation bias
  and groupthink. Use when: (1) reviewing architecture decisions, (2) auditing
  code changes, (3) validating designs before implementation, (4) stress-testing
  role cards or policies, (5) any decision where you need adversarial perspectives.
  Core insight: Disagreements are more valuable than consensus.
license: MIT
compatibility: Works with any agent that can spawn subagents or run sequential reviews
metadata:
  author: jeremyknows
  version: "1.0.0"
---

# PRISM - Parallel Review by Independent Specialist Models

Multi-agent review protocol that eliminates confirmation bias through structured adversarial analysis.

## Core Principle

> "Disagreements are MORE valuable than consensus."

When 4/5 reviewers agree and 1 dissents, pay attention to that dissent. The tension is where truth lives.

## How to Invoke PRISM

**Natural language triggers** — just ask:

| Mode | Say This | Agents |
|------|----------|--------|
| **Budget** | "Budget PRISM" / "PRISM lite" / "Essential PRISM" | 3 specialists |
| **Standard** | "Run PRISM" / "PRISM review" / "Adversarial review" | 5 specialists |
| **Extended** | "Full PRISM audit" / "Deep audit" / "9-agent PRISM" | 9 agents |

**Model override:** Add `--opus` or `--haiku` to change model (default: Sonnet)
- `"PRISM --opus"` → Opus reviewers for critical decisions
- `"Budget PRISM --haiku"` → Fast/cheap for quick sanity checks

**Structured request format:**

```markdown
## PRISM Review Request

**Mode:** [Budget / Standard / Extended]
**Subject:** [What you're reviewing]
**Context:** [Background — the more context, the better the review]
**Focus areas:** [Optional — specific concerns to prioritize]
```

**Examples:**

```
"Budget PRISM on this API change" (runs Security + UX + Performance)

"Full PRISM audit on the authentication module — we're about to open-source it"

"Standard PRISM on this architecture decision: moving from REST to GraphQL"
```

## The Pattern

Deploy specialist reviewers in parallel (3 for Budget, 5 for Standard, 9 for Extended), each with a distinct perspective:

| Reviewer | Focus | Key Question |
|----------|-------|--------------|
| 🔒 **Security Auditor** | Attack vectors, trust boundaries | "How could this be exploited?" |
| ⚡ **Performance Analyst** | Metrics, benchmarks, overhead | "Show me the numbers" |
| 🎯 **Simplicity Advocate** | Complexity reduction | "What can we remove?" |
| 🔧 **Integration Engineer** | Compatibility, migration | "How does this fit?" |
| 😈 **Devil's Advocate** | Assumptions, risks, regrets | "What are we missing?" |

**Optional 6th reviewer** based on context:
- **UX Reviewer** — For user-facing changes
- **Maintainability** — For long-term code health
- **Cost Analyst** — For resource-intensive decisions

## Implementation

### Option A: Parallel Subagents (Fastest)

If your agent can spawn subagents, run all 5 reviewers simultaneously:

```
sessions_spawn({
  label: "prism-security",
  task: "[Security Auditor prompt]",
  model: "sonnet"
})
// ... repeat for each reviewer
```

Typical time: 20-30 minutes for 5 parallel reviews.

### Option B: Sequential Review (No Subagents)

If you can't spawn subagents, adopt each perspective sequentially:

```markdown
## Acting as Security Auditor...
[analysis]

## Acting as Performance Analyst...
[analysis]

## Acting as Devil's Advocate...
[analysis]
```

Typical time: 45-60 minutes for 5 sequential reviews.

## Reviewer Prompts

### Security Auditor

```
You are the Security Auditor in a PRISM review.

Focus: Trust boundaries, attack vectors, data exposure.

Questions to answer:
1. What are the top 3 ways this could be exploited?
2. What security guarantees are we losing vs. gaining?
3. What assumptions about trust might be wrong?

Output format:
- Risk Assessment: [High/Medium/Low]
- Attack Vectors: [numbered list with severity]
- Recommended Mitigations: [specific countermeasures]
- Verdict: [APPROVE | APPROVE WITH CONDITIONS | REJECT]
```

### Performance Analyst

```
You are the Performance Analyst in a PRISM review.

Focus: Measurable metrics, not vibes. Numbers beat intuition.

Questions to answer:
1. What's the latency/memory/token impact?
2. Are there benchmarks we can reference?
3. What's the performance worst-case scenario?

Output format:
- Metrics: [specific numbers with units]
- Comparison: [before vs after]
- Risks: [what could degrade performance]
- Verdict: [APPROVE | APPROVE WITH CONDITIONS | REJECT]
```

### Simplicity Advocate

```
You are the Simplicity Advocate in a PRISM review.

Focus: Complexity reduction. Challenge every added component.

Questions to answer:
1. What can we remove without losing core value?
2. Is this the simplest solution that works?
3. What "nice-to-haves" are disguised as requirements?

Output format:
- Complexity Assessment: [lines of code, dependencies, moving parts]
- Simplification Opportunities: [what to cut]
- Essential vs Cuttable: [two lists]
- Verdict: [APPROVE | SIMPLIFY FURTHER | REJECT]
```

### Integration Engineer

```
You are the Integration Engineer in a PRISM review.

Focus: How this fits the existing system. Migration and compatibility.

Questions to answer:
1. What's the migration path for existing users?
2. What breaks if we deploy this?
3. How long until this is stable in production?

Output format:
- Integration Effort: [hours estimate with breakdown]
- Breaking Changes: [list]
- Migration Strategy: [phased rollout plan]
- Verdict: [APPROVE | APPROVE WITH CONDITIONS | REJECT]
```

### Code Reviewer (Extended Mode)

```
You are a Code Reviewer in a PRISM extended audit.

Your batch: [SPECIFY: e.g., "Dashboard, Watson, Sessions pages" or "API routes"]

Focus: Bugs, logic errors, edge cases, error handling in YOUR batch only.

Questions to answer:
1. What bugs or logic errors exist in this code?
2. What edge cases aren't handled?
3. Where is error handling missing or inadequate?
4. What would break under unexpected input?

DO NOT:
- Review code outside your assigned batch
- Comment on architecture or suggest refactors (other agents handle these)

Note: In Extended mode, the orchestrating agent auto-assigns batches based on 
directory structure (e.g., Batch1: /pages, Batch2: /api, Batch3: /components).

Output format:
## Issues Found
1. [File:Line] [Bug description] - Severity: [C/H/M/L]
2. ...

## Edge Cases Missing
- [Scenario that would break]

## Error Handling Gaps
- [Where errors aren't caught]
```

### Code Simplifier (Extended Mode)

```
You are the Code Simplifier in a PRISM extended audit.

Focus: DRY violations, dead code, consolidation opportunities.

Questions to answer:
1. What code is duplicated across files?
2. What code is never called (dead code)?
3. What could be extracted into shared utilities?
4. What's overcomplicated that could be simpler?

DO NOT:
- Flag style preferences (that's bikeshedding)
- Suggest rewrites that change behavior
- Prioritize elegance over clarity

Output format:
## Duplication Found
1. [Pattern] duplicated in [File1], [File2], [File3]
   - Consolidation: Extract to [suggested location]

## Dead Code
- [File:Line] [What's unused]

## Simplification Opportunities
- [Complex thing] → [Simpler approach]
```

### Devil's Advocate (Most Important)

```
You are the Devil's Advocate in a PRISM review.

Your job: Find the flaws. Challenge assumptions. Ask "what if we're wrong?"

Questions to answer:
1. What assumptions underpin this that might not hold?
2. What will we regret in 6 months?
3. What's the strongest argument AGAINST this decision?

Devil's Questions:
- "What if the opposite is true?"
- "What are we not seeing?"
- "Who benefits if this fails?"

Output format:
- Fatal Flaws: [if any]
- Hidden Costs: [not budgeted for]
- Optimistic Assumptions: [what if wrong?]
- 6-Month Regrets: [what we'll wish we kept]
- Rebuttal: [why this might be the WRONG choice]
- Verdict: [APPROVE | APPROVE WITH CONDITIONS | REJECT]

Your job is to be ruthlessly skeptical. When you approve with no conditions,
something is probably wrong.
```

## Handling Conflicting Verdicts

When reviewers disagree (e.g., Security says REJECT, others say APPROVE):

**Core Principle: Evidence over opinion.**
- Concrete exploit scenario beats abstract concern
- Measured impact beats estimated impact
- Cross-validated issues beat single-agent findings

**Priority Order (when in doubt):**
1. 🔒 **Security** — Safety concerns trump convenience
2. 😈 **Devil's Advocate** — If they found a fatal flaw, investigate
3. ⚡ **Performance** — Hard numbers are hard to argue with
4. 🎯 **Simplicity** / 🔧 **Integration** — Context-dependent

**Tie-Breaker Rules:**
- **3-2 split:** Go with majority, but document minority concerns as conditions
- **Security REJECT + others APPROVE:** Security wins unless you can specifically mitigate their concern
- **Devil's Advocate lone dissent:** Investigate deeply — they often catch what others miss
- **All APPROVE WITH CONDITIONS:** Merge conditions; if contradictory, Security's conditions take precedence

**When verdicts conflict, the synthesis should explicitly state:**
1. What the disagreement is
2. Why you're siding with one perspective
3. How you're addressing the dissenting concern

## Synthesis

After all reviews complete, synthesize findings:

```markdown
## PRISM Synthesis

### Consensus Points
[What all reviewers agreed on]

### Contentious Points
[Where reviewers disagreed — THIS IS THE GOLD]

### Recommended Path Forward
[Decision with specific conditions from each reviewer]

### Final Verdict
[APPROVE | APPROVE WITH CONDITIONS | REJECT]
Confidence: [percentage]
```

## When to Use PRISM

**High value:**
- Architecture decisions (irreversible, high impact)
- Security-sensitive changes
- Major refactors (>1000 lines)
- Policy/role card validation
- Open source releases

**Lower value (may be overkill):**
- Minor bug fixes
- Documentation updates
- Cosmetic changes

## Anti-Patterns (What NOT to Do)

**Don't:**
- ❌ Let reviewers see each other's findings first (creates groupthink)
- ❌ Spawn reviewers sequentially when parallel is possible (wastes time)
- ❌ Ask reviewers to "find everything" (overwhelms, creates noise)
- ❌ Skip synthesis (raw findings aren't actionable)
- ❌ Stop after one pass if issues are overwhelming (iterate with narrower scope)

**Do:**
- ✅ Spawn all reviewers in parallel (faster, independent perspectives)
- ✅ Give each reviewer a narrow focus (depth over breadth)
- ✅ Synthesize findings into prioritized action plan
- ✅ Iterate if first pass finds >50 issues (refine scope, go deeper)

## Red Flags (When PRISM Isn't Working)

Watch for these signs that something's wrong:

| Red Flag | What It Means | Fix |
|----------|---------------|-----|
| All reviewers find same issues | Not diverse enough | Sharpen role distinctions |
| >100 issues found | Scope too broad | Narrow the review target |
| Vague findings ("code could be better") | Prompts too generic | Add specific focus questions |
| Devil's Advocate has no concerns | Review target too simple OR prompts too soft | Re-run with "find something wrong" |
| 0 disagreements | Possible groupthink | Check reviewer independence |

**Iteration:** PRISM can be multi-pass. If the first pass surfaces too many issues, iterate with narrower scope until findings converge.

## Pro Tips

1. **Devil's Advocate is the most valuable reviewer.** If they approve with no conditions, you probably haven't thought it through.

2. **Disagreements > Consensus.** When 4/5 agree and 1 dissents, investigate the dissent deeply.

3. **"6-month regrets" is the killer question.** Forces reviewers to think beyond immediate benefits.

4. **Numbers beat vibes.** Performance Analyst grounds the discussion in reality.

5. **Technical controls > Process controls.** Devil's Advocate often catches when you're trading enforcement for trust.

## Example Output

See `references/example-review.md` for a complete PRISM review transcript.

## Severity Normalization

Agents calibrate severity differently. Use this rubric for consistency:

| Severity | Definition | Examples |
|----------|------------|----------|
| **CRITICAL** | Data loss, security breach possible, system down | Auth bypass, SQL injection, unencrypted secrets |
| **HIGH** | User-facing bug, standards violation, significant UX issue | WCAG failures, broken features, data corruption risk |
| **MEDIUM** | Code quality, maintainability, minor UX | Duplication, missing docs, confusing flows |
| **LOW** | Nice-to-have polish, optimization opportunities | Magic numbers, verbose code, minor refactors |

During synthesis, normalize agent-assigned severities to this rubric based on actual impact.

## Implementation Order

When fixing issues, prioritize in this order:

1. **Security** — Existential risk; fix first
2. **Accessibility** — Legal/ethical obligation; affects real users
3. **Performance** — Users feel it immediately
4. **Code Quality** — Developers feel it; prevents future bugs
5. **Architecture** — Long-term investment; do last

## Two-Round Audit (Recommended Workflow)

**Don't stop after one pass.** The two-round approach is essential:

1. **Round 1:** Run PRISM, fix all CRITICAL and HIGH issues
2. **Round 2:** Run PRISM again on the updated codebase

**Why?** Round 2 finds issues Round 1 missed:
- Specialists go deeper on a cleaner codebase
- Fixes may introduce new issues
- Context from Round 1 sharpens focus

*Real-world result: Mission Control audit found 147 issues in Round 1, then 37 NEW issues in Round 2 that Round 1 completely missed (path traversal, CSRF via CORS, hardcoded API keys).*

## Cross-Validation

**Issues found by 2+ agents = highest confidence.**

Track which agents found each issue. Cross-validated findings:
- Automatically become top priorities
- Indicate systemic problems (multiple perspectives see it)
- Justify immediate action without further debate

*Example: Beast API auth bypass was flagged by Security, Architecture, AND code reviewer — instant CRITICAL priority.*

## Done Criteria

**When to stop auditing:**

- ✅ No CRITICAL or HIGH issues remaining
- ✅ Architecture/quality score ≥ 4/5
- ✅ Re-audit finds < 3 new issues
- ✅ Remaining items are all LOW priority
- ✅ Cross-validation finds no new patterns

If you're iterating endlessly, scope was too broad. Narrow and re-run.

## Cost Estimates

**Full PRISM (5 specialists):**
- Agent execution: ~15 minutes parallel
- Synthesis: ~30 minutes
- Cost: ~$0.50-1.00 (Sonnet)

**Budget Mode (3 specialists):**
For cost-conscious users, run only the essential 3:
1. 🔒 **Security** (catches existential risks) — **MANDATORY, cannot be skipped**
2. 👁️ UX/Accessibility (catches user-facing issues)
3. ⚡ Performance (catches resource waste)

**⚠️ Security is ALWAYS included.** You cannot run PRISM without the Security Auditor, even in Budget mode. This is non-negotiable.

These three catch ~80% of high-impact issues at 60% of the cost.

**Extended PRISM (9 agents):**
For large codebases, add:
- 3 code reviewers (batched by area)
- 1 code simplifier
- 5 PRISM specialists

*Real-world: 9-agent audit on 27K-line codebase took ~5 hours per round (audit: 45 min, implementation: 4+ hours), found 147 issues, improved grade from B+ to A-.*

The cost of a missed security flaw or architecture mistake is 10-100x higher.

## Model Selection

PRISM defaults to **Sonnet** for all reviewers — sufficient for most reviews.

**Override syntax:**
- `"PRISM --opus"` → Opus reviewers (2-3x cost, marginal quality gain)
- `"PRISM --haiku"` → Haiku reviewers (fast/cheap, lower quality)
- `"Extended PRISM --opus"` → 9 Opus agents (expensive but thorough)

**When to use Opus:**
- Open-source releases (public scrutiny)
- Security-critical code (existential risk)
- Irreversible architecture decisions

**When Sonnet suffices (most cases):**
- Architecture reviews
- Refactors and code quality
- Policy/role card validation
- Internal tools and prototypes

**Cost comparison:**

| Mode | Sonnet (default) | Opus (--opus) |
|------|------------------|---------------|
| Budget (3) | ~$0.30-0.50 | ~$1.00-1.50 |
| Standard (5) | ~$0.50-1.00 | ~$2.00-3.00 |
| Extended (9) | ~$1.50-2.00 | ~$5.00-7.00 |

If you don't specify a model, PRISM uses Sonnet. This prevents accidental token burn when your session default is Opus.
