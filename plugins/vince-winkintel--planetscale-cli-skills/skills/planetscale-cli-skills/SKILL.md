---
name: planetscale-cli-skills
description: "Comprehensive PlanetScale CLI (pscale) command reference and workflows for database management via terminal. Use when user mentions PlanetScale CLI, pscale commands, database branches, deploy requests, schema migrations, or any PlanetScale terminal operations. Routes to specialized sub-skills for auth, branches, deploy requests, databases, backups, and 10+ other pscale commands. Triggers on pscale, PlanetScale CLI, database branch, deploy request, schema migration, PlanetScale automation."
---

# PlanetScale CLI Skills

Comprehensive `pscale` command reference and workflows for managing PlanetScale databases via terminal.

## Overview

The PlanetScale CLI brings database branches, deploy requests, and schema migrations to your fingertips. This skill provides command references, automation scripts, and decision trees for all `pscale` operations.

## Sub-Skills

| Command | Skill | Use When |
|---------|-------|----------|
| **auth** | `pscale-auth` | Login, logout, service tokens, authentication management |
| **branch** | `pscale-branch` | Create, delete, promote, diff, list database branches |
| **deploy-request** | `pscale-deploy-request` | Create, review, deploy, revert schema changes |
| **database** | `pscale-database` | Create, list, show, delete databases |
| **backup** | `pscale-backup` | Create, list, show, delete branch backups |
| **password** | `pscale-password` | Create, list, delete connection passwords |
| **org** | `pscale-org` | List, show, switch organizations |
| **service-token** | `pscale-service-token` | Create, manage CI/CD service tokens |

## Decision Trees

### Should I use a branch or deploy request?

```
What's your goal?
├─ Experimenting with schema changes → Create branch (pscale-branch)
├─ Testing schema in isolation → Create branch (pscale-branch)
├─ Ready to deploy schema to production → Create deploy request (pscale-deploy-request)
└─ Reviewing schema changes before production → Review deploy request (pscale-deploy-request)
```

### Service token vs password?

```
What's your use case?
├─ CI/CD pipeline → Service token (pscale-service-token)
├─ Local development → Password (pscale-password)
├─ Production application → Service token (rotatable, secure)
└─ One-off admin task → Password (temporary)
```

### Direct promotion vs deploy request?

```
Production readiness?
├─ Immediate promotion (dangerous) → pscale branch promote (pscale-branch)
├─ Review + approval workflow → pscale deploy-request create (pscale-deploy-request)
└─ Safe production deployment → Always use deploy requests
```

## Common Workflows

### Schema Migration Workflow

Complete workflow from branch creation to production deployment:

```bash
# 1. Create development branch
pscale branch create <database> <branch-name>

# 2. Make schema changes (via shell, ORM, or direct SQL)
pscale shell <database> <branch-name>

# 3. View schema diff
pscale branch diff <database> <branch-name>

# 4. Create deploy request
pscale deploy-request create <database> <branch-name>

# 5. Review and deploy
pscale deploy-request deploy <database> <deploy-request-number>

# 6. Verify deployment
pscale deploy-request show <database> <deploy-request-number>
```

See `scripts/` directory for automation.

### Branch Development Workflow

```bash
# Create branch from main
pscale branch create <database> <feature-branch> --from main

# Work on schema changes
pscale shell <database> <feature-branch>

# Check diff before deploying
pscale branch diff <database> <feature-branch>

# Create deploy request when ready
pscale deploy-request create <database> <feature-branch>
```

### CI/CD Integration

```bash
# Create service token for CI/CD
pscale service-token create --org <org>

# Use in CI/CD pipelines (GitHub Actions, GitLab CI, etc.)
export PLANETSCALE_SERVICE_TOKEN_ID=<token-id>
export PLANETSCALE_SERVICE_TOKEN=<token>

# Deploy via CI/CD
pscale deploy-request create <database> <branch> --auto-approve
```

## Quick Reference

### Most Common Commands

```bash
# Authentication
pscale auth login
pscale auth logout

# Branch management
pscale branch create <database> <branch> [--from <source-branch>]
pscale branch list <database>
pscale branch delete <database> <branch>

# Deploy requests
pscale deploy-request create <database> <branch>
pscale deploy-request list <database>
pscale deploy-request deploy <database> <number>

# Database operations
pscale database create <database> --org <org>
pscale database list
pscale shell <database> <branch>
```

## Related Skills

- **drizzle-kit** - ORM schema management and migrations
- **gitlab-cli-skills** - GitLab MR workflow integration
- **github** - GitHub PR and CI/CD integration

## Automation Scripts

See `scripts/` directory for token-efficient automation:

- `create-branch-for-mr.sh` - Create PlanetScale branch matching your MR/PR branch name
- `deploy-schema-change.sh` - Complete schema migration workflow
- `sync-branch-with-main.sh` - Sync development branch with main

Scripts execute without loading into context (~90% token savings).

## Resources

- Official docs: https://planetscale.com/docs/reference/planetscale-cli
- GitHub: https://github.com/planetscale/cli
- Community: https://github.com/planetscale/discussion
