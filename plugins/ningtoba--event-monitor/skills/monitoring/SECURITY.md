# Security Information

## What This Skill Does

The event-monitor skill collects system resource metrics (CPU and memory usage) from running processes and stores them locally for analysis.

## Data Flow

```
[Running Processes] → psutil → [Metrics] → SQLite (local) → Excel Report
```

## Security Boundaries

### ✅ Safe Operations

| Operation | Library | Scope |
|-----------|---------|-------|
| Read process list | `psutil` | Read-only, public info |
| Read CPU % | `psutil` | Per-process, normalized |
| Read memory % | `psutil` | Per-process |
| Write database | `sqlite3` | Skill directory only |
| Write Excel | `openpyxl` | Skill directory only |

### ❌ What This Skill Does NOT Do

- ❌ No network connections
- ❌ No external API calls
- ❌ No shell command execution
- ❌ No credential access
- ❌ No file system access outside skill directory
- ❌ No registry modifications
- ❌ No process termination or modification

## Dependencies

| Package | Purpose | Source |
|---------|---------|--------|
| `psutil` | System metrics | pip (official) |
| `openpyxl` | Excel generation | pip (official) |
| `sqlite3` | Database | Python stdlib |

## Verification

You can verify the skill's behavior by:

1. **Review the code**: `monitoring.py` is pure Python, no obfuscation
2. **Monitor network**: Use Wireshark or Resource Monitor - no connections
3. **Check file writes**: Only creates files in skill directory
4. **Run in sandbox**: Test in a VM or restricted environment

## False Positive Triggers

Security scanners may flag this skill due to:

| Trigger | Why It's Safe |
|---------|--------------|
| Process enumeration | Read-only, same as Task Manager |
| Database creation | Local SQLite, no server |
| Python script execution | Standard library usage |

## Contact

If you have security concerns, report to the skill author or OpenClaw security team.
