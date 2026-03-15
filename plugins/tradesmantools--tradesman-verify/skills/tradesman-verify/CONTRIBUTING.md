# Contributing to tradesman-verify

tradesman-verify is an open-source Accumulate ADI credential verifier for licensed tradespeople. Contributions that improve correctness, performance, and developer experience are welcome.

## Roles

### Whetstone (Optimization Contributor)

You sharpen what exists. Whetstone contributors focus on:

- **Performance** -- Reduce latency in verification lookups, batch operations, and ADI resolution.
- **Reliability** -- Improve error handling, retry logic, and timeout behavior.
- **Test coverage** -- Add missing unit or integration tests. Target: every exported function has at least one test.
- **Documentation** -- Fix inaccuracies, add examples, clarify edge cases.

Whetstone PRs are the fastest path to merge. If you see something that can be measurably better, open a PR.

### What We Accept

- Bug fixes with a failing test that your PR makes pass.
- Performance improvements with before/after benchmarks.
- New test cases covering untested paths.
- Documentation corrections.
- Dependency updates that fix vulnerabilities (`npm audit`).

### What We Don't Accept

- New features without prior discussion (open an issue first).
- Changes to the trust model or credential schema without maintainer approval.
- PRs that break existing tests.

## Getting Started

```bash
git clone https://gitlab.com/lv8rlabs/tradesman-verify.git
cd tradesman-verify
npm ci
npm run build
npm test
```

## Development Workflow

1. Fork the repo and create a branch from `master`.
2. Make your changes. Keep commits atomic.
3. Run `npm test` -- all tests must pass.
4. Run `npm audit --omit=dev` -- no new high/critical vulnerabilities.
5. Open a merge request against `master`.

## Commit Messages

- Use imperative mood: "fix timeout in batch lookup" not "fixed timeout".
- Reference issues by number: `closes #42`.
- Do not include personal names, email addresses, or PII in commit messages.

## Code Style

- TypeScript strict mode. No `any` unless unavoidable (document why).
- ESM (`"type": "module"` in package.json).
- Node.js built-in test runner (`node --test`).
- No runtime dependencies beyond Node.js stdlib.

## Signing

See `docs/signing-guide.md` for PEM, Vault, and KMS signing patterns. All credential issuance paths require ed25519 signatures.

## CI

Every MR triggers the GitLab CI pipeline:

1. **build** -- `npm ci && npm run build`
2. **test** -- `npm test` with coverage extraction
3. **security** -- `npm audit` + gitleaks secret scan + commit message scan
4. **publish** -- npm publish on semver tags (maintainers only)

Your MR must pass all stages before review.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
