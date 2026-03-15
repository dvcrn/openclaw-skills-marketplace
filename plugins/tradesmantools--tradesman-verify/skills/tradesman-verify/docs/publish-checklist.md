# Publication Checklist

Checklist for ACME Foundation sign-off, npm publish, and ClawHub submission.

---

## Pre-sign-off (complete before foundation review)

### Code quality
- [x] TypeScript build passes — `npm run build` exits 0
- [x] 0 TypeScript errors, 0 lint suppressions
- [x] All pre-signoff review findings resolved (see git log)
- [x] `crypto.randomUUID()` for credential IDs — no collision risk
- [x] `defaultClient` lazy-initialized — safe in serverless/test environments
- [x] Cache keys canonical — sorted JSON keys

### Security & privacy
- [x] No private keys stored or logged anywhere in the library
- [x] No PII in credential claims — enforced by schema guidance in `docs/acme-integration.md`
- [x] Revocation checked before credential validation in `verifyContractor()`
- [x] Self-attestation capped at `level: 'basic'` — cannot reach `enhanced` without third-party KYC
- [x] `@protected: true` in JSON-LD context — prevents context injection attacks

### Correctness
- [x] Revocation path tested (write `CredentialRevocation`, re-verify, confirm `result.revoked` populated)
- [x] `selfAttestedOnly` flag correct when all present credentials share issuer === subject
- [x] `verify_business_entity` handles 429, 401, empty result, and network errors
- [x] CLI shows `revoked[]` in verify output
- [x] CLI PEM key extraction validates 32-byte length

### Documentation
- [x] `README.md` — verify, issue, revoke, skill usage, open-core model, env vars
- [x] `docs/trust-model.md` — verification levels, revocation, self-attestation, threat model
- [x] `docs/acme-integration.md` — all 4 credential schemas, RPC methods, revocation entry format
- [x] `docs/pipeline.md` — off-chain → on-chain workflow, open-core boundary
- [x] `docs/privacy.md` — write mode disclosed, PII guidance, GDPR posture
- [x] `examples/verify-contractor.ts` — all verification modes
- [x] `examples/issue-credential.ts` — issuance, self-attest, revoke, skill runtimes
- [x] `examples/openai-integration.ts` — full OpenAI tool-call loop

### Context URL
- [ ] **TODO before v1.0**: Change `TRADESMAN_CONTEXT` in `src/schemas/index.ts` from
  `/main/contexts/v1.json` to `/v1.0.0/contexts/v1.json` and create git tag `v1.0.0`.
  Credentials issued before this change will have the `main`-branch context URL.

---

## npm publish (after ACME Foundation sign-off)

```bash
# 1. Confirm dist/ is current
npm run build

# 2. Dry-run to preview what gets published
npm pack --dry-run

# 3. Verify files array is correct (dist/, contexts/, docs/*.md, README.md, LICENSE)
npm publish --dry-run

# 4. Login and publish
npm login
npm publish --access public

# 5. Create git tag
git tag v0.1.0
git push origin v0.1.0

# 6. Update TRADESMAN_CONTEXT to pinned tag URL (see above)
# Edit src/schemas/index.ts, rebuild, commit, publish v0.1.1
```

**npm package name**: `tradesman-verify`
**Scope**: unscoped (public)
**Access**: public

---

## ClawHub submission (after npm publish)

The ClawHub skill lives at `skills/tradesman-verify/` in the LV8RLabs internal tooling repo.

```bash
# From skills/tradesman-verify/
npm install          # installs tradesman-verify from npm (post-publish)
npm test             # smoke test with mock data
```

Submission checklist:
- [x] `SKILL.md` frontmatter uses `metadata.openclaw` format
- [x] `requires.env: [OPENCORPORATES_API_KEY]` declared
- [x] `primaryEnv: OPENCORPORATES_API_KEY` declared
- [x] `install` spec declares `tradesman-verify` npm package
- [x] `src/index.js` imports from `tradesman-verify` npm (no relative external paths)
- [x] `LICENSE` file present
- [x] `.clawhubignore` excludes internal files
- [ ] Run `clawhub publish` or submit via ClawHub UI
- [ ] Verify skill appears in registry search

---

## OpenAI integration (parallel, no blocking dependencies)

- [x] `toOpenAIFunctions()` produces valid OpenAI function calling schema
- [x] `examples/openai-integration.ts` demonstrates full tool-call loop
- [x] README documents OpenAI function calling usage
- [ ] Optional: wrap in a FastAPI/Express server + `openapi.yaml` for GPT Actions
  (requires hosted endpoint decision — deferred pending monetization gate)

---

## Claude Code skill (via ClawHub)

- [x] `toClaudeTools()` produces valid Claude `tool_use` format
- [x] ClawHub submission installs `tradesman-verify` binary via `install` spec
- [x] `SKILL.md` provides complete agent instructions
- [x] `instructions.md` covers tool invocation patterns for Claude Code

---

## Post-launch monitoring

- [ ] Watch npm download count — confirms adoption
- [ ] Monitor GitLab issues for community integration questions
- [ ] Rotate `OPENCORPORATES_API_KEY` if used in CI/CD
- [ ] Pin context URL to versioned release after v1.0 (see note above)
- [ ] Follow up with ACME Foundation for official endorsement page/badge
