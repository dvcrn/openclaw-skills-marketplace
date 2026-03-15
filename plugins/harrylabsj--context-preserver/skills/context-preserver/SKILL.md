---
name: context-preserver
description: "Preserve working context with automatic snapshots, on-demand recovery, version management, and context export tools. Use when you want to save progress before a risky change, recover an earlier state, or keep restorable context checkpoints across long-running work."
---

# Context Preserver

Preserve working context with snapshots, recovery tools, and export options.

## What It Helps With

- create automatic snapshots at useful moments
- create manual tagged snapshots
- restore a previous snapshot
- list, inspect, and delete snapshots
- export or import snapshots
- manage automatic snapshot behavior

## Typical Commands

```bash
context-preserver snapshot "snapshot-name" --tags tag1,tag2
context-preserver list
context-preserver restore <snapshot-id>
context-preserver delete <snapshot-id>
context-preserver show <snapshot-id>
context-preserver export <snapshot-id> [output-path]
context-preserver import <file-or-directory>
context-preserver config
context-preserver auto on
context-preserver auto off
context-preserver clean
context-preserver help
```
