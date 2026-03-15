# ClawHub CLI Reference

## Auth

```bash
clawhub login                          # OAuth via browser
clawhub login --token <token>          # Direct token
clawhub logout                         # Remove stored token
clawhub whoami                         # Validate token, show handle
```

## Search & explore

```bash
clawhub search "postgres backups"      # Semantic search
clawhub explore                        # Browse latest skills
clawhub inspect <slug>                 # View skill metadata and files
```

## Install & manage

```bash
clawhub install <slug>                 # Install latest
clawhub install <slug> --version 1.2.3 # Install specific version
clawhub install <slug> --force         # Overwrite existing
clawhub update <slug>                  # Update to latest
clawhub update --all                   # Update all installed
clawhub update <slug> --version 1.2.3  # Update to specific version
clawhub update --all --force           # Force update all
clawhub uninstall <slug>               # Remove
clawhub list                           # List installed (from lockfile)
```

## Publish

```bash
clawhub publish <path> \
  --slug <slug> \                      # URL-safe identifier
  --name "Display Name" \              # Human-readable name
  --version <semver> \                 # e.g. 1.0.0
  --changelog "What changed" \         # Release notes
  --fork-of <slug[@version]> \         # Mark as fork
  --tags latest,beta                   # Comma-separated tags
```

## Sync (bulk publish)

```bash
clawhub sync                           # Interactive: pick skills to publish
clawhub sync --dry-run                 # Preview what would be uploaded
clawhub sync --all                     # Publish all new/updated
clawhub sync --all --bump patch        # Auto-bump patch version
clawhub sync --all --bump minor        # Auto-bump minor version
clawhub sync --changelog "Bug fixes"   # Set changelog for all updates
clawhub sync --root ~/extra-skills     # Scan additional directories
clawhub sync --concurrency 8           # Parallel registry checks
```

## Admin (moderator/admin only)

```bash
clawhub delete <slug>                  # Soft-delete
clawhub hide <slug>                    # Hide from search
clawhub undelete <slug>                # Restore deleted
clawhub unhide <slug>                  # Unhide
clawhub ban-user <handle>              # Ban user + delete their skills
clawhub set-role <handle> <role>       # Change user role
```

## Social

```bash
clawhub star <slug>                    # Add to highlights
clawhub unstar <slug>                  # Remove from highlights
```

## Environment variables

| Variable | Description |
|----------|-------------|
| `CLAWHUB_REGISTRY` | Registry API base URL (default: https://clawhub.com) |
| `CLAWHUB_SITE` | Site base URL (for browser login) |
| `CLAWHUB_WORKDIR` | Working directory |

## Default paths

- Install directory: `./skills` (override with `--workdir` / `--dir`)
- Token storage: managed by the CLI
