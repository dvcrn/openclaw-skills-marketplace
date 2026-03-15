---
name: product-dev-ops-package
description: "Product Dev Ops Package"
---

# SKILL.md - Product DevOps Team

## 名称
产品研发运营协作体系 (Product-Dev-Ops Team)

## 描述
一套完整的AI团队协作体系，包含产品经理、架构师、开发助手、运营经理四个角色，支持从需求到上线的全流程协作。

**核心理念**：
- 产品经理守护 Why，不控制 How
- **产品研讨会**（Why 冻结前四角色对齐）
- 开发自治（不改变 Why 的前提下修改需求）
- 文档分层（核心文档 vs 工作文档）
- 运营早期介入

## 版本
v3.1

## 包含角色

| 角色 | 职责 | 文件 |
|------|------|------|
| 产品经理(王校长) | 守护Why、需求访谈、版本归档、主持研讨会 | agents/product-manager.md |
| 架构师 | 架构设计、API契约、团队协调、研讨会技术评估 | agents/architect.md |
| 开发助手 | 代码实现、需求自治、自己测试、研讨会实现评估 | agents/dev-assistant.md |
| 运营经理 | 运营策略、工作流、权限、研讨会运营评估 | agents/ops-manager.md |

## 命令

### /开工 [项目名]
启动新项目，初始化目录结构，开始结构化访谈

### /研讨
发起产品研讨会（访谈后、冻结前）
- **自动检测**：检测是否有战略顾问输入材料
- **智能提示**：如缺少，建议启用 strategy-consultant 技能

### /冻结
Why 冻结，开发自治启动

### /继续
继续上次中断的流程

### /模式
查看/切换协作模式

### /状态
查看项目当前状态

### /归档 [版本]
版本归档

## 项目结构

```
projects/[name]/
├── WHY.md                    # 核心：Why
├── 01-product/               # 核心：产品需求
├── 03-architecture/          # 核心：技术架构
├── 05-operations/            # 核心：运营
├── 00-work/                  # 工作文档
│   ├── interview/            # 访谈记录
│   │   ├── external/         # 外部客户访谈
│   │   └── workshop/         # ⭐ 研讨会过程和结论
│   ├── daily/                # 站会记录
│   └── discussion/           # 临时讨论
├── 02-design/wireframes/     # 工作文档：低保真原型
├── 04-development/           # 工作文档
└── 07-archive/               # 归档
```

## 使用流程

### 基础流程（四角色）

1. **启动**：`/开工 项目名`
2. **访谈**：王校长6步结构化访谈
3. **研讨**：`/研讨` → 四角色对齐Why
4. **冻结**：`/冻结` → Why确定，开发自治启动
5. **开发**：开发自治修改 + 自己测试 + 同步文档
6. **检查**：架构师契约检查 + 每3天文档检查
7. **归档**：版本发布，工作文档合并

### 扩展流程（四角色 + 战略顾问）

```
/开工 项目名
    ↓
产品经理访谈（王校长）
    ↓
【可选】战略顾问外部访谈（strategy-consultant 技能）
    ├── /strategy-consultant/interview
    ├── /strategy-consultant/benchmark
    └── /strategy-consultant/bp
    ↓
输出到 00-work/interview/workshop/:
    - insights.md
    - benchmark-report.md
    - strategic-recommendations.md
    ↓
/研讨（自动检测并加载战略顾问输入）
    ↓
/freeze → 开发自治启动
```

## 可选扩展：战略顾问技能

**strategy-consultant**（独立技能包）：
- 提供外部洞察、Benchmark、BP撰写、财务预测等专业战略支持
- 与 product-dev-ops 集成，为研讨会提供专业输入
- **自动检测机制**：`/研讨` 时自动检测是否有战略顾问输入
- **智能提示**：如缺少战略输入，建议启用 strategy-consultant 技能
- 详见 [战略顾问集成指南](./docs/strategy-integration-guide.md)

### 何时启用战略顾问？

| 项目特征 | 建议 |
|----------|------|
| 全新业务方向 | ✅ 强烈建议 |
| 需要融资 | ✅ 强烈建议 |
| 复杂商业模式 | ✅ 强烈建议 |
| 高度竞争市场 | ✅ 强烈建议 |
| 内部工具/系统 | ⚠️ 可选 |
| 快速迭代试错 | ⚠️ 可选 |
| 技术重构 | ❌ 通常不需要 |

## 模板

- PRD模板：templates/prd/
- API模板：templates/api/
- 测试模板：templates/test/
- 工作文档模板：templates/work/
- 研讨会模板：templates/workshop/

## 依赖

- OpenClaw >= 2026.2.0
- Feishu/DingTalk/WeCom 插件（用于通知）
- strategy-consultant（可选，用于战略支持）

## 作者
Damon + OpenClaw

## 许可证
MIT
