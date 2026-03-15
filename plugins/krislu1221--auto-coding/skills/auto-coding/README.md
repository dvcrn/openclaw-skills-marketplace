# Auto-Coding

> **版本 / Version**: 1.0.0  
> **作者 / Author**: Krislu + Claw Soft  
> **基于 / Based on**: OpenClaw + Claude Quickstarts 最佳实践

---

## 📖 简介

Auto-Coding 是一个基于 OpenClaw 平台的多 Agent 协作编程系统，可以自动将用户需求转化为可运行的应用程序。

### 核心特性

- ✅ **双 Agent 模式** - Initializer(初始化) + Coder(编码) 协作
- ✅ **任务分解** - 自动将需求拆分为 20-50 个可执行功能点
- ✅ **进度追踪** - 实时更新任务状态，支持断点续做
- ✅ **安全沙箱** - 命令白名单机制，防止危险操作
- ✅ **Git 集成** - 自动版本控制和进度提交

---

## 🚀 快速开始

### 基础用法

```python
from auto_coding import AutonomousCodingController

# 创建控制器
controller = AutonomousCodingController(
    project_name="todo-app",
    requirements="创建一个 Todo 应用，包含添加、删除、标记完成功能"
)

# 运行完整周期
result = await controller.run_full_cycle()

# 查看结果
print(f"完成：{result['completed']}/{result['total']} 个任务")
print(f"进度：{result['percentage']}%")
```

### 限制迭代次数 (测试用)

```python
# 只运行 2 次迭代进行测试
result = await controller.run_full_cycle(max_iterations=2)
```

### 查看进度

```python
# 获取状态报告
status = controller.get_status()
print(status['status_report'])
```

---

## 📁 项目结构 / Project Structure

```
auto-coding/
├── __init__.py                 # Skill 注册
├── agent_controller.py         # 主控制器
├── task_manager.py             # 任务管理
├── security.py                 # 安全配置
├── prompts/
│   ├── initializer.md          # Initializer Prompt
│   └── coder.md                # Coder Prompt
├── tests/
│   ├── test_task_manager.py
│   └── test_security.py
└── README.md                   # 本文档
```

---

## 🏗️ 架构设计

### 双 Agent 模式

```
用户
 │
 ▼
┌────────────────────┐
│   主控制器         │
│   (Controller)     │
└────────┬───────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌─────────┐ ┌─────────┐
│Initializ│ │  Coder  │
│   er    │ │  Agent  │
│  Agent  │ │         │
└─────────┘ └─────────┘
```

### Initializer Agent 职责

1. 分析用户需求
2. 生成 feature_list.json (20-50 个功能点)
3. 创建项目目录结构
4. 初始化 git 仓库

### Coder Agent 职责

1. 读取当前任务
2. 实现功能代码
3. 运行测试验证
4. 更新任务状态
5. git commit 提交

---

## 📊 任务状态

| 状态 | 说明 |
|------|------|
| `pending` | 待处理 |
| `in_progress` | 进行中 |
| `done` | 已完成 |
| `blocked` | 已阻塞 (需要人工介入) |

---

## 🛡️ 安全机制

### 命令白名单

**允许的命令**:
- 文件检查：`ls`, `cat`, `head`, `tail`, `grep`, `find`
- 文件操作：`cp`, `mkdir`, `chmod`, `touch`, `mv`
- Node.js: `npm`, `npx`, `node`, `yarn`
- Python: `pip`, `python`, `pytest`
- 版本控制：`git`
- 进程管理：`ps`, `sleep`, `pkill` (仅开发进程)

**禁止的命令**:
- `sudo` - 提权操作
- `rm -rf` - 强制递归删除
- `dd`, `mkfs` - 磁盘操作
- `systemctl`, `service` - 系统服务

### 额外验证

某些命令需要额外验证：
- `pkill` - 只允许杀死开发进程 (node, npm, python 等)
- `chmod` - 只允许 `+x` (添加执行权限)
- `curl/wget` - 禁止直接写入文件

---

## 📋 输出示例

### feature_list.json

```json
[
  {
    "id": 1,
    "name": "创建项目结构",
    "description": "初始化项目目录和基础文件",
    "status": "done",
    "priority": "high",
    "estimated_complexity": "low"
  },
  {
    "id": 2,
    "name": "安装依赖",
    "description": "安装 npm 或 pip 依赖",
    "status": "pending",
    "priority": "high"
  }
]
```

### 进度报告

```
==================================================
📊 项目进度报告
==================================================
总任务数：20
✅ 已完成：15
⏳ 待处理：5
🚫 已阻塞：0
📈 进度：75.0%

✅ 已完成任务:
  - 创建项目结构
  - 安装依赖
  - 创建 HTML 骨架
  ...

⏳ 待处理任务:
  - 添加用户认证
  - 实现数据导出
  ...
==================================================
```

---

## 🧪 测试

### 运行所有测试 / Run All Tests

```bash
cd auto-coding/

# 测试 TaskManager
python3 task_manager.py

# 测试 Security
python3 security.py

# 测试 Controller
python3 agent_controller.py
```

### 测试结果

```
🎉 所有 TaskManager 测试通过!
🎉 所有 Security 测试通过!
🎉 所有 AutonomousCodingController 测试通过!
```

---

## 🔧 配置

### 环境变量

```bash
# 项目根目录 (可选，默认：/tmp/auto-coding-projects)
# Project root directory (optional, default: /tmp/auto-coding-projects)
export AUTO_CODING_PROJECTS_DIR="/path/to/projects"

# 最大迭代次数 (可选，默认：无限制)
export MAX_ITERATIONS="50"
```

### OpenClaw 集成

需要 OpenClaw sessions_spawn 支持：

```python
# 确保 OpenClaw 已安装并配置
openclaw --version

# 检查 sessions_spawn 可用性
python3 -c "from openclaw.tools import sessions_spawn; print('OK')"
```

---

## 📝 使用场景

### 1. 快速原型开发

```python
controller = AutonomousCodingController(
    project_name="demo-app",
    requirements="创建一个展示天气信息的 Web 应用"
)
result = await controller.run_full_cycle(max_iterations=10)
```

### 2. 完整项目开发

```python
controller = AutonomousCodingController(
    project_name="blog-system",
    requirements="创建一个个人博客系统，包含文章管理、评论、标签功能"
)
result = await controller.run_full_cycle()
```

### 3. 代码重构

```python
controller = AutonomousCodingController(
    project_name="refactor-legacy",
    requirements="将 legacy.py 重构为模块化结构，添加单元测试"
)
result = await controller.run_full_cycle()
```

---

## ⚠️ 注意事项

### 适用场景

- ✅ 中小型项目开发
- ✅ 原型快速验证
- ✅ 代码重构和测试添加
- ✅ 学习新技术栈

### 不适用场景

- ❌ 大型复杂系统 (建议人工架构设计)
- ❌ 性能关键型应用 (需要人工优化)
- ❌ 安全敏感系统 (需要人工审计)
- ❌ 遗留系统集成 (可能需要特殊工具)

### 最佳实践

1. **明确需求** - 需求越清晰，任务分解越准确
2. **限制范围** - 从小项目开始，逐步扩大
3. **定期检查** - 每 10-20 个任务检查一次进度
4. **及时介入** - 遇到 blocked 任务及时处理

---

## 🚧 开发计划

### Phase 1 (已完成) ✅

- [x] TaskManager 实现
- [x] Security 配置
- [x] Agent 控制器
- [x] Initializer/Coder Prompt
- [x] 单元测试

### Phase 2 (进行中) 🚧

- [ ] OpenClaw sessions_spawn 集成
- [ ] 真实项目测试
- [ ] 进度报告优化

### Phase 3 (计划) 📋

- [ ] Web UI 界面
- [ ] 多项目并行
- [ ] 性能优化
- [ ] 文档完善

---

## 📞 支持

- **作者 / Author**: Krislu + Claw Soft
- **邮箱**: [内部联系]
- **文档**: 参见 prompts/ 目录

---

## 📄 许可证

内部使用 - 龙虾团队

---

*最后更新：2026-03-14*
