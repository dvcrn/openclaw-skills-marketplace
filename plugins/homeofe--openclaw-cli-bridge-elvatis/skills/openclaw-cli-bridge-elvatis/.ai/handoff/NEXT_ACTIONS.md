# NEXT_ACTIONS.md — openclaw-cli-bridge-elvatis

_Last updated: 2026-03-11_

<!-- SECTION: summary -->
## Status Summary

| Status  | Count |
|---------|-------|
| Done    | 11    |
| Ready   | 1     |
| Blocked | 0     |
<!-- /SECTION: summary -->

---

## ⚡ Ready — Work These Next

### T-010: [medium] — Publish v0.2.25 to all platforms

- **Goal:** Publish v0.2.25 to GitHub, npm, and ClawHub.
- **Context:** v0.2.25 built + 51/51 tests pass. Changes: staged model switching (session-safe /cli-*), sleep-resilient token refresh, stopTokenRefresh cleanup.
- **What to do:**
  1. `git add -u && git commit -m "feat(cli): staged switch + token refresh stability (v0.2.25)"`
  2. `git tag v0.2.25 && git push origin main && git push origin v0.2.25`
  3. `gh release create v0.2.25 --title "v0.2.25 — Session-safe model switching" --notes "..."`
  4. `npm publish --access public`
  5. ClawHub publish via rsync workaround (see CONVENTIONS.md)
  6. Update STATUS.md platform table after publish
- **Definition of done:** v0.2.25 live on GitHub + npm + ClawHub.

---

## 🚫 Blocked

_No blocked tasks._

---

## ✅ Recently Completed

| Task  | Title                                                              | Date       |
|-------|--------------------------------------------------------------------|------------|
| T-011 | Session-safe staged model switching (/cli-apply, /cli-pending)     | 2026-03-11 |
| T-009 | Stability: sleep-resilient token refresh + stopTokenRefresh cleanup | 2026-03-11 |
| T-008 | Validate proxy endpoints + vllm model calls end-to-end            | 2026-03-08 |
| T-007 | Create GitHub repo and push initial code                          | 2026-03-07 |
| T-006 | Implement Claude Code CLI request bridge                          | 2026-03-07 |
