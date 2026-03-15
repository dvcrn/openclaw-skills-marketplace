# Skill Evolver

自动分析和优化 OpenClaw Agent Skills 的 Python CLI 工具。

## 🎯 功能概述

Skill Evolver 帮助你：

- 📊 **监控技能使用情况** - 追踪调用次数、成功率、响应时间
- 🏥 **评估健康度** - 综合评分系统，快速识别问题技能
- 🔍 **分析代码质量** - 检查 SKILL.md 完整性、语法错误、代码规范
- 💡 **生成改进建议** - 基于规则自动提供优化方案
- 📈 **导出报告** - 支持 JSON、Markdown、HTML 格式

## 🚀 快速开始

### 安装

```bash
# 使用 clawhub 安装（推荐）
clawhub install skill-evolver

# 或手动克隆
git clone https://github.com/openclaw/skills/skill-evolver.git
cd skill-evolver
pip install -r requirements.txt
```

### 初始化

```bash
# 初始化数据库
skill-evolver init
```

### 基本使用

```bash
# 分析技能
skill-evolver analyze my-skill

# 生成健康度报告
skill-evolver report my-skill

# 查看所有技能健康度
skill-evolver health --all
```

## 📖 详细文档

完整使用说明请查看 [SKILL.md](./SKILL.md)

## 🛠️ 开发

### 环境要求

- Python 3.8+
- SQLite3 (内置)

### 安装依赖

```bash
pip install pyyaml gitpython pytest flake8
```

### 运行测试

```bash
python -m pytest tests/ -v
```

### 代码检查

```bash
python -m flake8 skill_evolver/ database/
```

## 📁 项目结构

```
skill-evolver/
├── SKILL.md              # 技能说明文档
├── package.json          # 包元数据
├── README.md             # 项目说明
├── skill_evolver/        # 主模块
│   ├── __init__.py       # 模块入口
│   ├── monitor.py        # 使用监控
│   ├── analyzer.py       # 代码分析
│   ├── reporter.py       # 报告生成
│   └── cli.py            # CLI 入口
├── database/
│   ├── __init__.py       # 数据库模块
│   └── models.py         # 数据模型
└── tests/                # 测试用例
    ├── test_database.py
    ├── test_analyzer.py
    ├── test_reporter.py
    └── test_cli.py
```

## 📊 健康度评分

综合评分由以下维度计算：

| 维度 | 权重 | 说明 |
|------|------|------|
| 可靠性 | 30% | 基于成功率 |
| 性能 | 20% | 基于响应时间 |
| 代码质量 | 30% | 基于代码分析 |
| 用户满意度 | 20% | 基于用户反馈 |

### 状态等级

- 🟢 **healthy** (≥80 分) - 运行良好
- 🟡 **warning** (60-79 分) - 需要改进
- 🔴 **critical** (<60 分) - 存在严重问题

## 🔧 CLI 命令

| 命令 | 说明 |
|------|------|
| `init` | 初始化数据库 |
| `analyze` | 分析技能代码 |
| `report` | 生成健康度报告 |
| `health` | 查看健康度评分 |
| `log` | 记录技能使用 |
| `feedback` | 添加用户反馈 |
| `clear` | 清理旧数据 |

### 示例

```bash
# 分析所有技能
skill-evolver analyze --all

# 生成 HTML 报告
skill-evolver report my-skill -o report.html -f html

# 记录技能使用
skill-evolver log my-skill process --status success --duration 150

# 添加 5 星反馈
skill-evolver feedback my-skill 5 --comment "非常好用"
```

## 🐍 Python API

```python
from skill_evolver import SkillMonitor, SkillAnalyzer, SkillReporter

# 监控
monitor = SkillMonitor()
with monitor.track("my-skill", "process"):
    do_work()

# 分析
analyzer = SkillAnalyzer()
result = analyzer.analyze_skill("my-skill")
print(f"评分：{result.score}/100")

# 报告
reporter = SkillReporter()
report = reporter.generate_health_report("my-skill")
print(f"健康度：{report['overall_score']}")
```

## 📝 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！
