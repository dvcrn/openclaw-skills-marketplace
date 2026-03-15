# OpenClaw 统一维护系统技能

> **技能名称**: system-maintenance  
> **版本**: 1.2.0  
> **创建时间**: 2026-03-08  
> **更新时间**: 2026-03-08  
> **创建者**: Claw (OpenClaw AI Assistant)  
> **ClawHub ID**: k97bca5502xm85egs9gba5zkks82ekd0

## 📋 技能描述

提供 OpenClaw 系统的**完整维护解决方案**，包括实时监控、日志管理、日常维护和每周优化。采用统一架构设计，经过实际部署验证，支持安全迁移和完整回滚。

## 🎯 适用场景

当遇到以下情况时使用本技能：
- ✅ 系统运行时间较长，需要自动化维护
- ✅ 日志文件堆积需要专业管理
- ✅ Gateway 服务不稳定需要监控和恢复
- ✅ 需要统一、可扩展的维护架构
- ✅ 从旧维护系统迁移到新系统
- ✅ 需要健康评分和详细报告

## 🏆 核心优势

### **统一架构**
- 模块化设计，职责清晰
- 5个核心脚本覆盖所有维护需求
- 配置驱动，易于定制

### **智能监控**
- 实时 Gateway 进程监控
- 自动恢复机制
- 健康评分系统 (0‑100分)

### **安全迁移**
- 完整备份和回滚
- 并行运行验证
- 平滑切换策略

### **专业报告**
- Markdown 格式详细报告
- 执行摘要和优化建议
- 系统健康分析

## 🔧 主要功能

### 1. ⏱️ 实时监控 (`real-time-monitor.sh`)
- **频率**: 每5分钟
- **功能**: Gateway 进程监控、自动恢复、资源检查
- **特点**: macOS兼容检测，智能恢复逻辑

### 2. 📁 日志管理 (`log-management.sh`)
- **频率**: 每天2:00
- **功能**: 日志清理、轮转、压缩、权限检查
- **特点**: 专业日志管理策略，保留重要日志

### 3. 🧹 日常维护 (`daily-maintenance.sh`)
- **频率**: 每天3:30
- **功能**: 综合清理、健康检查、学习记录更新
- **特点**: 全面维护，持续改进

### 4. 📅 每周优化 (`weekly-optimization.sh`)
- **频率**: 周日3:00
- **功能**: 深度系统优化、健康评分、报告生成
- **特点**: 0‑100健康评分，Markdown报告

### 5. 🛠️ 安装工具 (`install-maintenance-system.sh`)
- **频率**: 一次性
- **功能**: 系统安装和配置
- **特点**: 完整安装，自动配置cron

## 📁 文件结构

```
system-maintenance/
├── SKILL.md                      # 本文件
├── entry.js                      # 技能入口点
├── package.json                  # npm 包配置 (v1.2.0)
├── scripts/
│   ├── weekly-optimization.sh    # 每周优化 (新增 v1.2.0)
│   ├── real-time-monitor.sh      # 实时监控
│   ├── log-management.sh         # 日志管理
│   ├── daily-maintenance.sh      # 日常维护
│   └── install-maintenance-system.sh # 安装工具
├── docs/
│   ├── cron-schedule.md          # 定时任务安排
│   ├── migration-plan.md         # 迁移计划 (新增 v1.2.0)
│   └── architecture.md           # 系统架构 (新增 v1.2.0)
└── examples/
    ├── setup-guide.md            # 快速设置指南
    ├── migration-guide.md        # 安全迁移指南 (新增 v1.2.0)
    ├── final-status-template.md  # 最终状态报告模板 (新增 v1.2.0)
    └── optimization-suggestions.md # 优化建议 (新增 v1.2.0)
```

## 🚀 快速开始

### 安装技能
```bash
# 方法1: ClawHub 安装 (最新版本)
clawhub install system-maintenance

# 方法2: Git 克隆
git clone https://github.com/jazzqi/openclaw-system-maintenance.git ~/.openclaw/skills/system-maintenance
```

### 一键安装维护系统
```bash
# 运行安装脚本
bash ~/.openclaw/skills/system-maintenance/scripts/install-maintenance-system.sh
```

### 手动配置定时任务
```bash
# 查看安装脚本生成的配置
crontab -l | grep "openclaw"

# 应该看到4个任务:
# */5 * * * * 实时监控
# 0 2 * * *   日志管理
# 30 3 * * *  日常维护
# 0 3 * * 0   每周优化
```

## ⏰ 推荐维护计划

| 时间 | 任务 | 描述 | 脚本 |
|------|------|------|------|
| 每5分钟 | 实时监控 | Gateway 进程监控和自动恢复 | `real-time-monitor.sh` |
| 02:00 | 日志管理 | 专业日志清理和轮转 | `log-management.sh` |
| 03:30 | 日常维护 | 综合清理和健康检查 | `daily-maintenance.sh` |
| 周日03:00 | 每周优化 | 深度系统优化和报告生成 | `weekly-optimization.sh` |

## 🔄 迁移指南

### 从旧系统迁移
如果你有旧的维护脚本，建议按以下步骤迁移:

#### 阶段1: 并行运行 (1周)
```bash
# 1. 安装新系统
bash install-maintenance-system.sh

# 2. 新旧系统并行运行
# 旧系统任务继续执行
# 新系统任务同时执行
```

#### 阶段2: 功能验证
- 验证所有脚本功能正常
- 检查日志生成情况
- 测试自动恢复功能

#### 阶段3: 切换主用
```bash
# 注释或删除旧任务
# 新系统成为主用
```

#### 阶段4: 清理优化
- 清理临时文件
- 归档旧脚本
- 更新文档

完整迁移指南见: `examples/migration-guide.md`

## 🔍 监控指标

### 健康评分系统 (0‑100分)
脚本自动计算健康评分，基于:
- ✅ Gateway 运行状态 (-30分如果未运行)
- ✅ 错误数量 (-10‑20分如果过多)
- ✅ 重启频率 (-8‑15分如果频繁)
- ✅ 磁盘空间 (-10‑20分如果紧张)

### 报告生成
每周优化脚本生成详细报告:
1. **执行摘要** - 健康评分和关键指标
2. **详细内容** - 各部分状态分析
3. **建议** - 优化建议和行动项

## 🛡️ 安全特性

### 备份和回滚
- **完整备份**: 迁移前完整备份
- **一键回滚**: 随时恢复到旧系统
- **版本控制**: 所有变更可追溯

### 错误处理
- **优雅失败**: 脚本出错不影响系统
- **详细日志**: 完整执行记录
- **自动恢复**: 关键服务自动重启

### 权限控制
- **最小权限**: 仅执行必要操作
- **安全检查**: 操作前验证
- **审计日志**: 所有操作记录

## 📊 性能提升

### 任务优化
- **减少任务数**: 从8个减少到4个 (‑50%)
- **统一日志**: 集中日志管理
- **智能调度**: 避免任务冲突

### 资源优化
- **内存使用**: 优化的进程检测
- **磁盘空间**: 智能清理策略
- **网络连接**: 高效的健康检查

## 🔗 相关资源

- **GitHub仓库**: https://github.com/jazzqi/openclaw-system-maintenance
- **ClawHub页面**: https://clawhub.com/skills/system-maintenance
- **文档目录**: `docs/` 和 `examples/`
- **问题反馈**: GitHub Issues

## 📝 版本历史

### v1.2.0 (2026-03-08)
- 🆕 新增每周优化脚本 (`weekly-optimization.sh`)
- 🆕 统一维护架构文档
- 🆕 迁移指南和备份策略
- 🆕 最终状态报告模板
- 🆕 优化建议文档
- 🔧 修复 macOS 兼容性问题
- 📊 增强健康评分系统

### v1.1.0 (2026-03-08)
- 🆕 实时监控脚本 (`real-time-monitor.sh`)
- 🆕 日志管理脚本 (`log-management.sh`)
- 🆕 日常维护脚本 (`daily-maintenance.sh`)
- 🆕 安装工具脚本 (`install-maintenance-system.sh`)

### v1.0.0 (2026-03-08)
- 🎯 初始版本发布
- 📦 包含基础维护脚本
- 📚 基础文档和示例

## 🤝 贡献指南

欢迎贡献! 请:
1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 创建 Pull Request

## 📄 许可证

MIT License - 详见 `LICENSE` 文件

---

**使用本技能，让你的 OpenClaw 系统始终保持最佳状态！** 🚀
## 🌐 跨平台支持

### 当前平台支持状态
- **✅ macOS**: 主要平台，完全支持
- **🔧 Linux**: 架构就绪，需要平台适配器
- **🔄 Windows**: 架构预留，未来可适配

### 跨平台架构设计
技能设计时考虑了跨平台兼容性：

1. **模块化设计**: 平台特定代码可单独添加
2. **抽象层**: 平台操作的通用接口
3. **配置驱动**: 平台行为通过配置控制
4. **文档完整**: 完整的跨平台架构指南

### 平台特定功能
| 平台 | 进程检测 | 服务控制 | 任务调度 | 日志管理 |
|------|----------|----------|----------|----------|
| **macOS** | ✅ `ps aux \| grep` | ✅ `launchctl` | ✅ `crontab` | ✅ `/tmp/` |
| **Linux** | ✅ `pgrep` / `ps` | ✅ `systemctl` | ✅ `crontab` | ✅ `/var/log/` |
| **Windows** | ⚠️ `tasklist` | ⚠️ `sc` / `net` | ⚠️ 任务计划程序 | ⚠️ `%TEMP%` |

### 不同平台入门指南
- **macOS**: 遵循标准安装指南（完全支持）
- **Linux**: 查看 `docs/linux-setup.md` 获取平台特定说明
- **Windows**: 参考 `docs/windows-setup.md` 获取适配指南

### 贡献平台支持
欢迎社区贡献添加对新平台的支持：
1. 阅读 `docs/cross-platform-architecture.md`
2. 创建平台适配器模块
3. 添加平台特定配置
4. 提交包含测试的 Pull Request
