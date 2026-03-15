---
name: auto-coding
description: "Auto-Coding"
---

# Auto-Coding Skill

> **Version**: 1.0.0  
> **Author**: Krislu + Claw Soft  
> **Description**: Multi-Agent Autonomous Coding System

---

## 📖 Overview / 概述

Auto-Coding is a multi-agent collaboration system built on OpenClaw that automatically transforms user requirements into runnable applications.

Auto-Coding 是一个基于 OpenClaw 的多 Agent 协作系统，可以自动将用户需求转化为可运行的应用程序。

---

## 🎯 Features / 功能特性

- **Multi-Agent Collaboration** - Initializer + Coder dual-agent pattern
  **多 Agent 协作** - 初始化器 + 编码器双代理模式

- **Automatic Task Breakdown** - Split requirements into 20-50 features
  **自动任务分解** - 将需求拆分为 20-50 个功能点

- **Progress Tracking** - Real-time status updates with Git integration
  **进度追踪** - 实时更新状态，集成 Git 版本控制

- **Security Sandbox** - Command allowlist with 40+ safe commands
  **安全沙箱** - 40+ 安全命令白名单机制

---

## 🚀 Usage / 使用方法

### Command Triggers / 命令触发

```bash
# English commands
/auto-coding create a Todo app
/auto-coding build a weather app

# Chinese commands
/auto-coding 创建一个 Todo 应用
/auto-coding 帮我开发一个天气应用

# Natural language
帮我创建一个 博客系统
Help me create a blog system
```

### Python API / Python 接口

```python
from auto_coding import AutonomousCodingController

controller = AutonomousCodingController(
    project_name="my-app",
    requirements="Create a Todo application"
)

result = await controller.run_full_cycle(max_iterations=10)
print(f"Completed: {result['completed']}/{result['total']} tasks")
```

---

## 📁 Project Structure / 项目结构

```
auto-coding/
├── skill.py                    # OpenClaw Skill implementation
├── agent_controller.py         # Main controller
├── task_manager.py             # Task management
├── security.py                 # Security configuration
├── test_auto_coding.py         # Test scripts
├── prompts/
│   ├── initializer.md          # Initializer agent prompt
│   └── coder.md                # Coder agent prompt
└── README.md                   # Documentation
```

---

## 🛡️ Security / 安全性

### Allowed Commands / 允许的命令 (40+)

| Category / 类别 | Commands / 命令 |
|----------------|-----------------|
| **File Inspection / 文件检查** | `ls`, `cat`, `head`, `tail`, `grep`, `find` |
| **File Operations / 文件操作** | `cp`, `mkdir`, `chmod`, `touch`, `mv` |
| **Node.js** | `npm`, `npx`, `node`, `yarn`, `pnpm` |
| **Python** | `pip`, `python`, `pytest`, `unittest` |
| **Version Control / 版本控制** | `git` |
| **Process Management / 进程管理** | `ps`, `sleep`, `pkill` (dev processes only) |

### Blocked Commands / 禁止的命令

- ❌ `sudo` - Privilege escalation
- ❌ `rm -rf` - Forced recursive deletion
- ❌ `dd`, `mkfs` - Disk operations
- ❌ `systemctl`, `service` - System services

---

## 🧪 Testing / 测试

```bash
cd auto-coding/

# Run all tests
python3 test_auto_coding.py 1  # Minimal test
python3 test_auto_coding.py 2  # Real project test
python3 test_auto_coding.py 3  # All tests
```

### Expected Output / 预期输出

```
🧪 Auto-Coding Test
==================================================
✅ TaskManager tests passed
✅ Security tests passed
✅ Controller tests passed
🎉 All tests passed!
```

---

## 📋 Configuration / 配置

### Environment Variables / 环境变量

```bash
# Project root directory (optional)
export AUTO_CODING_PROJECTS_DIR="/path/to/projects"

# Max iterations (optional)
export MAX_ITERATIONS="50"
```

---

## ⚠️ Known Limitations / 已知限制

1. **OpenClaw Integration** - Requires `sessions_spawn` support from OpenClaw Gateway
   **OpenClaw 集成** - 需要 OpenClaw Gateway 的 `sessions_spawn` 支持

2. **Mock Mode** - Currently runs in mock mode without real Gateway configuration
   **模拟模式** - 当前在没有真实 Gateway 配置的情况下运行在模拟模式

3. **Language Support** - Best results with Chinese and English prompts
   **语言支持** - 中文和英文提示效果最佳

---

## 📚 Documentation / 文档

- **README.md** - Full user guide with examples
- **prompts/initializer.md** - Initializer agent instructions
- **prompts/coder.md** - Coder agent instructions
- **Security-Compliance-Report.md** - Security audit report

---

## 📄 License / 许可证

**Internal Use Only** - Lobster Team

---

## 👥 Authors / 作者

- **Krislu** - Project Initiator
- **Claw Soft** - Lead Developer

---

*Last Updated: 2026-03-14*
