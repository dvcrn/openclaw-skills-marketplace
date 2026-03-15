# Product DevOps Team Skill

> 产品研发运营协作体系 v3.1 - 四角色协作框架

## 快速导航

### 核心文档
| 文档 | 说明 |
|------|------|
| [SKILL.md](./SKILL.md) | Skill 主文档，包含版本、角色、流程 |
| [README.md](./README.md) | 项目说明和文档索引 |

### 四角色 Agents
| 角色 | 文档 |
|------|------|
| 产品经理 | [product-manager.md](./agents/product-manager.md) |
| 架构师 | [architect.md](./agents/architect.md) |
| 开发助手 | [dev-assistant.md](./agents/dev-assistant.md) |
| 运营经理 | [ops-manager.md](./agents/ops-manager.md) |

### 指令 Commands
| 指令 | 文档 |
|------|------|
| /开工 | [start.md](./commands/start.md) |
| /继续 | [resume.md](./commands/resume.md) |
| /模式 | [mode.md](./commands/mode.md) |
| /状态 | [status.md](./commands/status.md) |
| /归档 | [archive.md](./commands/archive.md) |
| /研讨 | [workshop.md](./commands/workshop.md) |
| /冻结 | [freeze.md](./commands/freeze.md) |

### 模板 Templates
| 类别 | 路径 |
|------|------|
| API | [api/](./templates/api/) |
| PRD | [prd/](./templates/prd/) |
| 研讨会 | [workshop/](./templates/workshop/) |

## 目录结构

```
product-dev-ops/
├── SKILL.md                          # Skill 主文档
├── README.md                         # 项目说明
├── package.json                      # 包配置
├── INDEX.md                          # 本文件（快速导航）
├── agents/                           # 角色定义
│   ├── product-manager.md            # 产品经理
│   ├── architect.md                  # 架构师
│   ├── dev-assistant.md              # 开发助手
│   └── ops-manager.md                # 运营经理
├── commands/                         # 指令定义
│   ├── start.md
│   ├── resume.md
│   ├── mode.md
│   ├── status.md
│   ├── archive.md
│   ├── workshop.md
│   └── freeze.md
├── templates/                        # 模板文件
│   ├── api/
│   ├── prd/
│   └── workshop/
└── docs/                             # 其他文档
```

## 使用方式

```bash
# 启动项目
/开工 项目名

# 启动产品研讨会
/研讨

# 查看角色文档
# 直接点击上方表格中的链接
```

## 扩展技能

**strategy-consultant**（战略顾问技能）：
- 如需外部洞察、Benchmark、BP撰写等战略支持
- 可独立安装使用
- 也可与 product-dev-ops 集成，为研讨会提供输入

## 版本

v3.1 - 四角色协作体系（产品经理、架构师、开发助手、运营经理）
