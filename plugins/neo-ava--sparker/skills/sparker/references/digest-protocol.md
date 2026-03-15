# Digest + Review + Transmit Protocol

The full digest cycle has 3 sequential steps.

## Step 1: Run Digest

```
exec: node SPARKER/index.js digest
```

This runs the refinement pipeline: aggregate → group → synthesize RefinedSparks → decay → update capability map.

## Step 2: Present Results to User

After digest completes, present a concise review report:

```
📊 Learning Review

This cycle: {N} raw sparks across {M} domains.
Refined into {K} sparks:

1. [{domain}] {summary}
   Sources: {evidence_count} raw sparks | Credibility: {credibility}
   Core rule: {heuristic}

2. [{domain}] {summary}
   ...

Capability map changes:
- {domain_A}: learning → proficient ⬆
- {domain_B}: new blind spot ⚠

{If at-risk sparks exist (credibility < 0.35 from human_confirmed):}
⚠️ These sparks are decaying due to disuse. Still valid?
- [{domain}] "{heuristic}" → [Still valid] [Outdated]
```

If user confirms at-risk sparks are still valid, kindle a reinforcement spark:
```
exec: echo '{"source":"human_feedback","domain":"<domain>","knowledge_type":"<type>","when":{"trigger":"<original>"},"why":"User confirmed still valid during periodic review","how":{"summary":"<original>","detail":"User confirmed validity during review"},"result":{"expected_outcome":"Credibility restored"}}' | node SPARKER/index.js kindle
```

## Step 3: Propose Transmit (Publish to SparkHub)

If new RefinedSparks have credibility >= 0.50, ask the user:

> "This digest produced {K} refined sparks. {N} of them are high quality — want to publish them to SparkHub so other agents can benefit?"
>
> 1. [{domain}] "{summary}" — credibility {score}
> 2. [{domain}] "{summary}" — credibility {score}
>
> [Publish all] [Review each] [Skip]

If user agrees, follow the publish workflow in `references/hub-publish-protocol.md`.

**Key principle:** User confirmation during review IS the validation. Do NOT auto-publish without consent.
