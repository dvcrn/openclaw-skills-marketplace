---
name: papermc-ai-ops
description: "Manage PaperMC Minecraft servers through safe, controlled interfaces. Use for server lifecycle management, backups, plugin operations, and health monitoring with backup-first safety policy."
---

# PaperMC Server AI Operations

AI-managed PaperMC Minecraft server operations with safety-first approach.

## When to Use This Skill

Use this skill when you need to:
- Manage PaperMC server lifecycle (status, logs, restart)
- Create backups (world, plugins, PaperMC jar)
- Install or update plugins safely
- Update PaperMC server version
- Monitor server health and diagnose issues

## Requirements

- Linux system with systemd
- Java 21+ (Zulu JDK recommended for ARM)
- Python 3.10+
- PaperMC server installation

## Quick Start

### 1. Configure

Edit paths in the scripts:
```python
# In manage_server.py, plugin_manager.py, update_paper.py
SERVER_DIR = Path("/path/to/your/papermc-server")
```

### 2. Check Status

```bash
python3 manage_server.py status
```

### 3. Create Backup

```bash
python3 manage_server.py backup
```

## Core Scripts

### manage_server.py

Server lifecycle management:
```bash
python3 manage_server.py status          # Service status
python3 manage_server.py logs -n 50      # View logs
python3 manage_server.py backup          # Backup world
python3 manage_server.py restart         # Safe restart
```

### plugin_manager.py

Plugin operations:
```bash
python3 plugin_manager.py list                           # List plugins
python3 plugin_manager.py backup <plugin.jar>           # Backup plugin
python3 plugin_manager.py install-url <url> --filename <name>
```

### update_paper.py

PaperMC updates:
```bash
python3 update_paper.py backup-jar                    # Backup current jar
python3 update_paper.py update-from-url <paper_jar_url>
```

## Safety Rules

### ❌ Never Use Direct Commands
- `kill`, `kill -9`
- `rm -rf`
- `systemctl stop/restart`
- Direct file overwrites

### ✅ Always Use Scripts
All operations go through approved Python scripts.

### 📦 Backup-First Policy
Before ANY risky operation:
1. Run backup command
2. Verify backup created
3. Proceed with change

## Health Monitoring

```bash
bash scripts/health_check.sh
```

Checks:
- Service status
- Log errors
- Plugin count
- Backup age
- Disk space
- Memory usage

## Version Management Strategy

### Balanced Upgrade Strategy
Adopt a balanced approach with 1-version lag for stability.

### Weekly Upgrade Scoring System
```bash
python3 scripts/weekly-upgrade-scorer.py
```

**Scoring Criteria (100 points total):**
1. **PaperMC Stability (30 points)**
   - Official API confirmation
   - Release age (>2 weeks)
   - Security patches included

2. **Plugin Compatibility (40 points)**
   - Core plugins compatibility
   - All plugins compatible
   - Recent plugin updates
   - No critical warnings

3. **Testing & Validation (20 points)**
   - Test environment validation
   - Performance benchmarks
   - Functionality verification

4. **Risk Management (10 points)**
   - Backup readiness
   - Rollback plan tested

### Upgrade Decision Matrix
- **≥ 80 points**: Proceed with upgrade (low risk)
- **60-79 points**: Further evaluation needed
- **< 60 points**: Do not upgrade (high risk)

### Weekly Scanning Procedure
1. **Monday**: Run automated scoring
2. **Review**: Analyze report and scores
3. **Decision**: Human confirmation required for ≥80 scores
4. **Execution**: Scheduled upgrade with full backup

### Emergency Rollback
Trigger conditions:
- Server crash on startup
- TPS consistently below 15
- Critical plugin failures
- Player data corruption

Rollback steps:
1. Stop server immediately
2. Restore from latest backup
3. Revert to previous version
4. Verify and restart

## Directory Structure

```
papermc-server/
├── manage_server.py      # Main control script
├── plugin_manager.py     # Plugin operations
├── update_paper.py       # PaperMC updates
├── backup.sh             # Backup automation
├── scripts/
│   └── health_check.sh   # Health monitoring
├── docs/
│   ├── architecture.md   # System design
│   └── changelog.md      # Change history
├── backup/               # World backups
├── plugin_backup/        # Plugin backups
└── jar_backup/           # PaperMC jar backups
```

## Workflow Examples

### Daily Health Check
```bash
bash scripts/health_check.sh
```

### Before Plugin Update
```bash
python3 manage_server.py backup
python3 plugin_manager.py backup OldPlugin.jar
python3 plugin_manager.py install-url <new_plugin_url> --filename NewPlugin.jar
python3 manage_server.py restart
python3 manage_server.py status
```

### PaperMC Update
```bash
python3 update_paper.py backup-jar
python3 update_paper.py update-from-url <paper_download_url>
python3 manage_server.py restart
python3 manage_server.py status
```

## Configuration

### Environment Variables (.env)
```bash
SERVER_NAME=my-server
SERVER_DIR=/path/to/server
BACKUP_RETENTION=10
```

## Troubleshooting

### Service Won't Start
```bash
python3 manage_server.py logs -n 100
```

### Check Disk Space
```bash
df -h
```

### Verify Java
```bash
java -version
```

## Safety First

This skill enforces operational discipline:
- All actions through controlled interfaces
- Mandatory backups before changes
- No destructive direct commands
- Full traceability

Never bypass the script layer for "quick fixes."

## License

MIT License - See LICENSE file
