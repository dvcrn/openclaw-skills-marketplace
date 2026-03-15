# Release Guard Checklist

## Critical Checks (Block Release if Failed)

### C1: SKILL.md Exists
- **Check**: File `SKILL.md` exists in skill directory
- **Failure**: Cannot proceed without skill definition
- **Auto-fix**: No

### C2: Valid YAML Frontmatter
- **Check**: File starts with `---` and has valid YAML frontmatter
- **Failure**: Metadata required for skill registry
- **Auto-fix**: No

### C3: Required Fields Present
- **Check**: `name:` and `description:` fields exist in frontmatter
- **Failure**: Minimum metadata required
- **Auto-fix**: No

### C4: No Nested Skills
- **Check**: No `SKILL.md` files in subdirectories
- **Failure**: Skills must be flat, single-directory
- **Auto-fix**: No

### C5: No Secrets in Content
- **Check**: No patterns matching API keys, passwords, tokens
- **Failure**: Security risk
- **Auto-fix**: No

## Standard Checks (Warn if Failed)

### S1: References Directory
- **Check**: `references/` directory exists
- **Warning**: Best practice for documentation
- **Auto-fix**: Can scaffold

### S2: Scripts Executable
- **Check**: Files in `scripts/` have executable bit
- **Warning**: Scripts won't run without this
- **Auto-fix**: Yes (chmod +x)

### S3: Meaningful Description
- **Check**: Description is more than 20 characters
- **Warning**: Users need to understand the skill
- **Auto-fix**: No

### S4: Content Length
- **Check**: SKILL.md has at least 50 lines
- **Warning**: Very short skills may be incomplete
- **Auto-fix**: No

### S5: Examples Provided
- **Check**: Has example usage or trigger examples
- **Warning**: Users need to know how to invoke
- **Auto-fix**: No

## Optional Checks (Info Only)

### O1: README.md
- **Check**: Additional README exists
- **Info**: Nice to have but not required
- **Auto-fix**: Can scaffold

### O2: Test Script
- **Check**: `scripts/test.sh` exists
- **Info**: Enables automated testing
- **Auto-fix**: Can scaffold

### O3: License
- **Check**: LICENSE file exists
- **Info**: Clarifies usage rights
- **Auto-fix**: Can scaffold

## Check Execution Order

1. Run Critical checks first
2. Stop immediately if any critical check fails
3. Run Standard checks
4. Run Optional checks
5. Generate report

## Scoring

- Critical: 10 points each (must pass)
- Standard: 5 points each
- Optional: 2 points each

**Pass**: All critical + 70% of standard
**Pass with Warnings**: All critical + 50% of standard
**Fail**: Any critical failed or < 50% of standard
