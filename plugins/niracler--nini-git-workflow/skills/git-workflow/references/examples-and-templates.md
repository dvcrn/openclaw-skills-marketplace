# Examples and Templates

## Commit Examples

### Good

```text
feat(gateway): add group control support
```

```text
fix(sensor): correct energy calculation overflow
```

```text
refactor: move register_listener to entity objects

- Add register_listener() to Device/Group/Scene in SDK
- Remove gateway parameter from integration entities
- Simplify all-light creation from 14 lines to 1 line
```

```text
chore(release): bump version to 0.2.0
```

### Bad

```text
refactor: cleanup
```

*Too vague - what was cleaned up?*

```text
fix: bug fixes
```

*Not specific - which bugs?*

```text
feat: implement new authentication system

🤖 Generated with Claude Code

Co-Authored-By: Claude <noreply@anthropic.com>
```

*Contains forbidden AI markers*

## PR Template

**Merge strategy**: Squash and merge.

### Body

```markdown
## Summary
- Key change 1
- Key change 2
- Key change 3

## Test plan
- [ ] Test case 1
- [ ] Test case 2
- [ ] Test case 3
```

### Example

**Title**: `feat(auth): add OAuth2 authentication`

```markdown
## Summary
- Implement OAuth2 flow with Google provider
- Add token refresh mechanism
- Update login UI with OAuth button

## Test plan
- [ ] Test Google OAuth login flow
- [ ] Verify token refresh works after expiration
- [ ] Check error handling for failed authentication
```

## CHANGELOG Format

Follow [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) format:

```markdown
## [x.y.z] - YYYY-MM-DD

### Added
- New user-facing features

### Fixed
- Important bug fixes (#issue)

### Technical
- Dependency updates, CI/CD improvements, code refactoring
```

### Guidelines

- **Added**: User-facing features
- **Fixed**: Bug fixes with issue references (#123)
- **Technical**: Internal changes (dependencies, CI/CD, refactoring)
  - Include commit hashes (abc1234) for technical changes without issues
- Keep entries concise and user-focused
- Update version links at bottom of changelog

### Example

```markdown
## [0.3.0] - 2025-12-01

### Added
- Group control support for smart home devices (#45)
- Energy monitoring dashboard (#48)

### Fixed
- Energy calculation overflow in sensor component (#52)

### Technical
- Migrate to new SDK API structure (commit: abc1234)
- Update dependencies to latest versions (commit: def5678)

[0.3.0]: https://github.com/owner/repo/compare/v0.2.0...v0.3.0
```
