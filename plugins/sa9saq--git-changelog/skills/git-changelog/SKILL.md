---
name: git-changelog
description: "Generate changelogs and release notes from git commit history with conventional commit parsing."
---

# Git Changelog

Auto-generate changelogs from git commit history.

**Use when** creating release notes, changelogs, or summarizing git history between versions.

## Requirements

- Git repository with commit history
- No API keys needed

## Instructions

1. **Detect version range**:
   ```bash
   # Latest tag
   git tag --sort=-version:refname | head -1
   # Commits since last tag
   git log $(git describe --tags --abbrev=0)..HEAD --oneline
   # If no tags: last 50 commits
   git log -50 --oneline
   ```

2. **Fetch commit history**:
   ```bash
   git log <range> --pretty=format:"%H|%s|%an|%ai" --no-merges
   ```

3. **Parse and categorize** using Conventional Commits:
   | Prefix | Category |
   |--------|----------|
   | `feat:` | ✨ Features |
   | `fix:` | 🐛 Bug Fixes |
   | `docs:` | 📝 Documentation |
   | `refactor:` | ♻️ Refactoring |
   | `perf:` | ⚡ Performance |
   | `test:` | ✅ Tests |
   | `chore:` | 🔧 Chores |
   | `BREAKING CHANGE` | 💥 Breaking Changes |

   Non-conventional commits go under **📦 Other Changes**.

4. **Generate commit links** if remote exists:
   ```bash
   git remote get-url origin  # → extract GitHub/GitLab URL
   # Link format: [abc1234](https://github.com/user/repo/commit/abc1234)
   ```

5. **Output format**:
   ```markdown
   # Changelog

   ## [1.2.0] — 2025-01-15

   ### 💥 Breaking Changes
   - Removed deprecated `oldAPI()` method ([abc1234])

   ### ✨ Features
   - Add user authentication flow ([def5678])

   ### 🐛 Bug Fixes
   - Fix memory leak in connection pool ([ghi9012])
   ```

6. **Write to file** if requested: append to top of `CHANGELOG.md` (preserve existing content).

## Edge Cases

- **No conventional commits**: Group by date instead, use full commit messages.
- **Monorepo**: Filter by path with `git log -- path/to/package`.
- **Custom date range**: `git log --since="2025-01-01" --until="2025-02-01"`.
- **Empty range**: Report "No changes since last release."
- **Squash merges**: Check `--first-parent` for cleaner history.

## Troubleshooting

- `fatal: No names found`: No tags exist — fall back to commit count.
- Garbled author names: Check `git config` encoding settings.
