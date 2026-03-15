---
name: session-guardian
description: "Never lose a conversation again. Auto-backup every 5 minutes, smart summaries, and instant recovery when models crash or Gateway restarts. Works for solo agents and multi-agent teams. Use when you need bulletproof session protection, task tracking across agents, or collaboration history. Prevents token overflow with AI-powered compaction (30-50% savings)."
---

# Session Guardian 🛡️

**Your Conversation Guardian** - Enterprise-grade session backup + project management solution

## Problem Statement

- 🔴 **Model disconnections** - Conversations lost, work wasted
- 🔴 **Gateway restarts** - Forgot what you were doing, task state lost
- 🔴 **Cross-channel confusion** - Private info sent to group chat, or vice versa
- 🔴 **Complex task tracking** - Tasks span multiple sessions, hard to track state
- 🔴 **Multi-agent chaos** - Multiple agents working simultaneously, unclear who's doing what
- 🔴 **Large session files** - Causing timeouts, slow responses, high token consumption

## Quick Start

```bash
# Install
clawhub install session-guardian

# One-click deployment (auto-configure all cron jobs)
cd ~/.openclaw/workspace/skills/session-guardian
bash scripts/install.sh

# Verify
crontab -l | grep session-guardian
openclaw cron list
```

## Use Cases

### Scenario 1: Enterprise Multi-Agent Collaboration
**Typical User**: Enterprise teams with multiple agents working together

**Example**:
- Main agent → Dev team lead → UI designer + Full-stack developer
- Main agent → Finance team lead → Strategy research + Risk control + Execution
- Main agent → Operations team lead → Content creation + Data analysis

**Benefits**:
- ✅ Collaboration tracking: Visualize task flow
- ✅ Collaboration health: Monitor team collaboration quality
- ✅ Knowledge base: Accumulate team best practices

### Scenario 2: Personal Assistant Team
**Typical User**: Individual users with multiple specialized assistants

**Example**:
- Research assistant: Find resources, organize literature
- Coding assistant: Write code, debug issues
- Writing assistant: Write articles, polish copy
- Translation assistant: Multi-language translation

**Benefits**:
- ✅ Smart backup: Protect each assistant's memory
- ✅ Knowledge extraction: Each assistant accumulates expertise
- ✅ Collaboration tracking: Know which assistant has the task

### Scenario 3: Single-Agent Deep Usage
**Typical User**: Users with one main agent

**Example**:
- Personal AI assistant: Handle all daily tasks
- Professional consultant: Deep conversations, long-term memory

**Benefits**:
- ✅ Smart backup: Prevent conversation loss
- ✅ Knowledge extraction: Accumulate personal best practices
- ✅ Task management: Track complex task states

### Scenario 4: Enterprise Multi-Department Collaboration
**Typical User**: Enterprises with agents in different departments

**Example**:
- Sales agent: Customer management, opportunity tracking
- Support agent: Issue handling, ticket management
- Tech agent: Technical support, troubleshooting
- Finance agent: Report generation, data analysis

**Benefits**:
- ✅ Session isolation: Prevent cross-department information leakage
- ✅ Collaboration health: Monitor cross-department collaboration

## Core Features

### 1. Five-Layer Protection System

#### Layer 1: Incremental Backup (Every 5 minutes)
- Auto-backup new conversations
- Minimal storage, fast recovery
- Supports all agent sessions

#### Layer 2: Snapshot Backup (Every 1 hour)
- Complete session snapshots
- Version control, rollback support
- Automatic cleanup of old versions

#### Layer 3: Smart Summary (Daily)
- Extract key information from conversations
- Auto-update MEMORY.md
- Generate collaboration summaries

#### Layer 4: Health Check (Every 6 hours)
- Monitor session file size
- Detect abnormal token consumption
- Alert on collaboration issues

#### Layer 5: Project Management
- Task state tracking
- Milestone management
- Progress reports

### 2. Multi-Agent Collaboration Features (v2.0)

#### Collaboration Tracking
- Visualize task flow: King → Team Lead → Members
- Record collaboration links
- Generate collaboration reports

#### Smart Backup Strategy
- High-frequency agents: More frequent backups
- Low-frequency agents: Reduce backup frequency
- Save storage and token consumption

#### Knowledge Base Extraction
- Extract best practices from conversations
- Auto-update AGENTS.md
- Generate FAQ

#### Collaboration Health Scoring
- Communication efficiency
- Task completion rate
- Response time
- Collaboration quality

### 3. Integration with Self-Improving-Agent

**Complementary Design**:
- Session Guardian: Macro perspective, overall progress
- Self-Improving-Agent: Micro perspective, specific issues

**Workflow**:
1. Self-Improving-Agent records errors and learnings in real-time (lightweight)
2. Session Guardian reads SI records during daily summary
3. Session Guardian extracts knowledge to MEMORY.md
4. Avoid duplicate analysis

**Token Savings**:
- Before: ~30k tokens/day
- After: ~10.5k tokens/day
- **Save 65% tokens**

## Installation

### Method 1: ClawHub (Recommended)

```bash
clawhub install session-guardian
```

### Method 2: Manual Installation

```bash
# Clone repository
git clone https://github.com/1052326311/session-guardian.git ~/.openclaw/workspace/skills/session-guardian

# Run installation script
cd ~/.openclaw/workspace/skills/session-guardian
bash scripts/install.sh
```

### Method 3: npm Installation

```bash
npm install -g @openclaw/session-guardian
```

## Configuration

### Basic Configuration

Edit `~/.openclaw/workspace/skills/session-guardian/config.json`:

```json
{
  "backup": {
    "incremental": {
      "enabled": true,
      "interval": 5,
      "retention": 7
    },
    "snapshot": {
      "enabled": true,
      "interval": 60,
      "retention": 30
    }
  },
  "summary": {
    "enabled": true,
    "schedule": "0 0 * * *"
  },
  "healthCheck": {
    "enabled": true,
    "interval": 6
  },
  "collaboration": {
    "tracking": true,
    "healthScore": true
  },
  "integration": {
    "selfImprovingAgent": {
      "enabled": true,
      "readLearnings": true
    }
  }
}
```

### Advanced Configuration

#### Custom Backup Path

```json
{
  "backup": {
    "path": "/custom/backup/path"
  }
}
```

#### Agent-Specific Settings

```json
{
  "agents": {
    "main": {
      "backup": {
        "interval": 3
      }
    },
    "dev-lead": {
      "backup": {
        "interval": 10
      }
    }
  }
}
```

## Usage

### Manual Backup

```bash
# Backup all sessions
openclaw skill run session-guardian backup

# Backup specific agent
openclaw skill run session-guardian backup --agent main
```

### Manual Summary

```bash
# Generate daily summary
openclaw skill run session-guardian summary

# Generate weekly summary
openclaw skill run session-guardian summary --weekly
```

### Health Check

```bash
# Run health check
openclaw skill run session-guardian health-check

# View health report
cat ~/.openclaw/workspace/Assets/SessionBackups/health-reports/latest.md
```

### Restore Session

```bash
# List available backups
openclaw skill run session-guardian list-backups

# Restore from backup
openclaw skill run session-guardian restore --backup 2026-03-06-10-00
```

## File Structure

```
~/.openclaw/workspace/
├── skills/
│   └── session-guardian/
│       ├── SKILL.md                    # This file
│       ├── config.json                 # Configuration
│       ├── scripts/
│       │   ├── install.sh              # Installation script
│       │   ├── incremental-backup.sh   # Incremental backup
│       │   ├── snapshot-backup.sh      # Snapshot backup
│       │   ├── daily-summary.sh        # Daily summary
│       │   ├── health-check.sh         # Health check
│       │   ├── collaboration-tracker.sh # Collaboration tracking
│       │   └── knowledge-extractor.sh  # Knowledge extraction
│       └── templates/
│           ├── summary.md              # Summary template
│           └── health-report.md        # Health report template
└── Assets/
    └── SessionBackups/
        ├── incremental/                # Incremental backups
        ├── snapshots/                  # Snapshot backups
        ├── summaries/                  # Daily summaries
        ├── health-reports/             # Health reports
        └── collaboration/              # Collaboration data
```

## Cron Jobs

After installation, the following cron jobs are automatically configured:

```bash
# Incremental backup (every 5 minutes)
*/5 * * * * cd ~/.openclaw/workspace/skills/session-guardian && bash scripts/incremental-backup.sh

# Snapshot backup (every hour)
0 * * * * cd ~/.openclaw/workspace/skills/session-guardian && bash scripts/snapshot-backup.sh

# Daily summary (midnight)
0 0 * * * cd ~/.openclaw/workspace/skills/session-guardian && bash scripts/daily-summary.sh

# Health check (every 6 hours)
0 */6 * * * cd ~/.openclaw/workspace/skills/session-guardian && bash scripts/health-check.sh

# Collaboration tracking (every 30 minutes)
*/30 * * * * cd ~/.openclaw/workspace/skills/session-guardian && bash scripts/collaboration-tracker.sh
```

## Best Practices

### 1. Regular Monitoring

- Check health reports weekly
- Review collaboration health scores
- Monitor token consumption

### 2. Backup Management

- Keep 7 days of incremental backups
- Keep 30 days of snapshots
- Archive important conversations

### 3. Knowledge Extraction

- Review daily summaries
- Update MEMORY.md regularly
- Share best practices with team

### 4. Integration with Other Skills

- Use with self-improving-agent for error learning
- Use with project management tools
- Integrate with notification systems

## Troubleshooting

### Backup Not Running

```bash
# Check cron jobs
crontab -l | grep session-guardian

# Check logs
tail -f ~/.openclaw/workspace/skills/session-guardian/logs/backup.log
```

### Large Session Files

```bash
# Run health check
openclaw skill run session-guardian health-check

# View recommendations
cat ~/.openclaw/workspace/Assets/SessionBackups/health-reports/latest.md
```

### Missing Summaries

```bash
# Manually generate summary
openclaw skill run session-guardian summary

# Check summary logs
tail -f ~/.openclaw/workspace/skills/session-guardian/logs/summary.log
```

## Performance

### Token Consumption

- Incremental backup: ~100 tokens/run
- Snapshot backup: ~500 tokens/run
- Daily summary: ~5k tokens/run (with SI integration: ~8k)
- Health check: ~200 tokens/run
- Collaboration tracking: ~300 tokens/run

**Total**: ~10-15k tokens/day (with SI integration)

### Storage

- Incremental backup: ~10KB/session/day
- Snapshot backup: ~100KB/session/day
- Summaries: ~5KB/day
- Health reports: ~2KB/report

**Total**: ~1-2MB/agent/month

## Roadmap

### v2.1 (Planned)
- [ ] Web dashboard for visualization
- [ ] Real-time collaboration monitoring
- [ ] Advanced analytics
- [ ] Custom alert rules

### v2.2 (Planned)
- [ ] Cloud backup support
- [ ] Team collaboration features
- [ ] API for third-party integration
- [ ] Mobile app

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

- GitHub: https://github.com/1052326311/session-guardian
- Issues: https://github.com/1052326311/session-guardian/issues
- ClawHub: https://clawhub.com/session-guardian

## Changelog

### v2.0.0 (2026-03-05)
- ✨ Added collaboration tracking
- ✨ Added smart backup strategy
- ✨ Added knowledge extraction
- ✨ Added collaboration health scoring
- ✨ Integration with self-improving-agent
- 🐛 Fixed session isolation issues
- 📝 Improved documentation

### v1.0.0 (2026-03-01)
- 🎉 Initial release
- ✨ Five-layer protection system
- ✨ Multi-agent support
- ✨ Project management features

---

# 中文版 / Chinese Version

## 核心功能

### 1. 五层防护体系

#### 第1层：增量备份（每5分钟）
- 自动备份新对话
- 存储占用小，恢复快
- 支持所有agent的session

#### 第2层：快照备份（每1小时）
- 完整session快照
- 版本控制，支持回滚
- 自动清理旧版本

#### 第3层：智能总结（每天）
- 从对话中提取关键信息
- 自动更新MEMORY.md
- 生成协作总结

#### 第4层：健康检查（每6小时）
- 监控session文件大小
- 检测异常token消耗
- 协作问题预警

#### 第5层：项目管理
- 任务状态追踪
- 里程碑管理
- 进度报告

### 2. 多智能体协作功能（v2.0）

#### 协作链路追踪
- 可视化任务流转：King → 团长 → 成员
- 记录协作链路
- 生成协作报告

#### 智能备份策略
- 高频agent：更频繁备份
- 低频agent：降低备份频率
- 节省存储和token消耗

#### 知识库沉淀
- 从对话中提取最佳实践
- 自动更新AGENTS.md
- 生成FAQ

#### 协作健康度评分
- 沟通效率
- 任务完成率
- 响应时间
- 协作质量

### 3. 与Self-Improving-Agent集成

**互补设计**：
- Session Guardian：宏观视角，看整体进展
- Self-Improving-Agent：微观视角，看具体问题

**工作流**：
1. Self-Improving-Agent实时记录错误和学习（轻量级）
2. Session Guardian每日总结时读取SI记录
3. Session Guardian提取知识到MEMORY.md
4. 避免重复分析

**Token节省**：
- 优化前：~30k tokens/天
- 优化后：~10.5k tokens/天
- **节省65% tokens**

## 安装

### 方法1：ClawHub（推荐）

```bash
clawhub install session-guardian
```

### 方法2：手动安装

```bash
# 克隆仓库
git clone https://github.com/1052326311/session-guardian.git ~/.openclaw/workspace/skills/session-guardian

# 运行安装脚本
cd ~/.openclaw/workspace/skills/session-guardian
bash scripts/install.sh
```

## 配置

编辑 `~/.openclaw/workspace/skills/session-guardian/config.json`:

```json
{
  "backup": {
    "incremental": {
      "enabled": true,
      "interval": 5,
      "retention": 7
    },
    "snapshot": {
      "enabled": true,
      "interval": 60,
      "retention": 30
    }
  },
  "summary": {
    "enabled": true,
    "schedule": "0 0 * * *"
  },
  "healthCheck": {
    "enabled": true,
    "interval": 6
  },
  "collaboration": {
    "tracking": true,
    "healthScore": true
  },
  "integration": {
    "selfImprovingAgent": {
      "enabled": true,
      "readLearnings": true
    }
  }
}
```

## 使用

### 手动备份

```bash
# 备份所有session
openclaw skill run session-guardian backup

# 备份特定agent
openclaw skill run session-guardian backup --agent main
```

### 手动总结

```bash
# 生成每日总结
openclaw skill run session-guardian summary

# 生成每周总结
openclaw skill run session-guardian summary --weekly
```

### 健康检查

```bash
# 运行健康检查
openclaw skill run session-guardian health-check

# 查看健康报告
cat ~/.openclaw/workspace/Assets/SessionBackups/health-reports/latest.md
```

## 性能

### Token消耗

- 增量备份：~100 tokens/次
- 快照备份：~500 tokens/次
- 每日总结：~5k tokens/次（集成SI后：~8k）
- 健康检查：~200 tokens/次
- 协作追踪：~300 tokens/次

**总计**：~10-15k tokens/天（集成SI后）

### 存储

- 增量备份：~10KB/session/天
- 快照备份：~100KB/session/天
- 总结：~5KB/天
- 健康报告：~2KB/报告

**总计**：~1-2MB/agent/月

## 支持

- GitHub: https://github.com/1052326311/session-guardian
- Issues: https://github.com/1052326311/session-guardian/issues
- ClawHub: https://clawhub.com/session-guardian

## 更新日志

### v2.0.0 (2026-03-05)
- ✨ 新增协作链路追踪
- ✨ 新增智能备份策略
- ✨ 新增知识库沉淀
- ✨ 新增协作健康度评分
- ✨ 集成self-improving-agent
- 🐛 修复session隔离问题
- 📝 改进文档

### v1.0.0 (2026-03-01)
- 🎉 首次发布
- ✨ 五层防护体系
- ✨ 多智能体支持
- ✨ 项目管理功能
