# OpenClaw Security Scanner - 使用说明

## 技能概述

OpenClaw Security Scanner 是一个专业的安全审计技能，用于扫描 OpenClaw 部署中的安全漏洞，并提供安全的修复建议。

## 安装方法

### 方法 1: 通过 ClawHub 安装（推荐）

```bash
# 从 ClawHub 注册表安装
clawhub install openclaw-security-scanner

# 验证安装
clawhub list | grep security-scanner
```

### 方法 2: 本地安装

```bash
# 复制技能到工作区
cp -r openclaw-security-scanner ~/.openclaw/workspace/skills/

# 验证安装
python3 ~/.openclaw/workspace/skills/skill-creator/scripts/quick_validate.py openclaw-security-scanner
```

### 方法 3: 从 ClawHub 下载

```bash
# 浏览 ClawHub
clawhub search security

# 安装
clawhub install openclaw-security-scanner --from-clawhub
```

### 系统依赖（可选）

端口绑定检测需要 `lsof`（macOS/Linux）或 `ss`（Linux，来自 iproute2）。如果两者都不可用，端口扫描仍可正常工作，但无法判断端口绑定在 0.0.0.0 还是 127.0.0.1。

## 使用方法

### 完整安全扫描

```bash
# 运行完整扫描
openclaw security-scan

# 保存报告到文件
openclaw security-scan --output security_report.md

# 详细输出
openclaw security-scan --verbose
```

### 针对性扫描

```bash
# 仅扫描网络端口
openclaw security-scan --ports-only

# 仅审计 IM 通道配置
openclaw security-scan --channels

# 仅分析权限配置
openclaw security-scan --permissions
```

### 直接运行脚本

```bash
# 使用 Python 脚本
python3 skills/openclaw-security-scanner/scripts/security_scan.py
```

## 输出示例

```
============================================================
OpenClaw Security Scanner v1.0.0
============================================================

[1/3] Network port scanning...
Port 18789 (gateway) is OPEN
Port 22 (ssh) is OPEN

[2/3] Channel policy audit...
Scanning channel configurations...

[3/3] Permission analysis...
Analyzing permissions...

============================================================
Scan complete. 8 findings.
============================================================

Risk Level: HIGH

Findings:
🔴 CRITICAL: 2
🟠 HIGH: 3
🟡 MEDIUM: 2
🔵 LOW: 1

Report saved to: security_report_20260308_163000.md
```

## 风险等级说明

| 等级 | 响应时间 | 示例 |
|------|----------|------|
| 🔴 CRITICAL | < 1 小时 | 暴露的管理端口、允许所有人的频道策略 |
| 🟠 HIGH | < 24 小时 | 缺少认证、过度的工具权限 |
| 🟡 MEDIUM | < 1 周 | 弱速率限制、详细的错误信息 |
| 🔵 LOW | < 1 个月 | 缺少安全头文件、日志记录不佳 |

## 安全修复原则

⚠️ **重要**: 在应用可能破坏远程访问的修复之前，必须：

1. ✅ 确认有备用访问方式（SSH、控制台）
2. ✅ 备份当前配置
3. ✅ 准备回滚方案
4. ✅ 安排维护窗口

### 高风险修复的分阶段流程

```
阶段 1: 准备
├─ 备份配置
├─ 记录当前状态
├─ 验证备用访问
└─ 安排维护窗口

阶段 2: 测试环境
├─ 先在测试环境应用
├─ 验证功能正常
├─ 测试回滚流程
└─ 获得批准

阶段 3: 生产环境
├─ 在维护窗口应用
├─ 密切监控 24-48 小时
├─ 保持回滚就绪
└─ 记录变更

阶段 4: 验证
├─ 测试关键功能
├─ 验证安全改进
├─ 监控问题
└─ 更新文档
```

## 定期扫描

### 添加到心跳检查

编辑 `~/.openclaw/workspace/HEARTBEAT.md`:

```markdown
## 每周安全检查

每周日 02:00:
- 运行：`openclaw security-scan -o weekly_security.md`
- 审查 CRITICAL/HIGH 发现
- 应用低风险修复
- 向管理员频道报告摘要
```

### 使用 Cron

```bash
# 添加到 crontab
0 2 * * 0 cd ~/.openclaw/workspace && openclaw security-scan -o docs/reports/weekly_security_$(date +\%Y\%m\%d).md
```

## 文件结构

```
openclaw-security-scanner/
├── SKILL.md                    # 技能定义
├── README.md                   # 使用说明
├── clawhub.json                # ClawHub 配置
├── scripts/
│   ├── security_scan.py        # 主扫描脚本
│   ├── cli.py                  # CLI 包装器
│   └── package_skill.py        # 打包脚本
└── references/
    ├── permission-management.md    # 权限管理指南
    └── remediation-playbook.md     # 修复操作手册
```

## 故障排除

### 配置文件未找到

```
[WARN] No config file found
```

**解决方法**: 确保 OpenClaw 配置文件存在于：
- `~/.openclaw/config.json`
- `~/.openclaw/gateway.config.json`
- 或设置 `OPENCLAW_CONFIG` 环境变量

### 权限被拒绝

```
Error: [Errno 13] Permission denied
```

**解决方法**: 使用适当权限运行或检查文件所有权。

## 支持

对于安全紧急情况：
1. 立即运行完整扫描
2. 应用 CRITICAL 修复（准备好回滚）
3. 向安全团队报告
4. 7 天内安排后续审计

## 更新技能

```bash
# 从 ClawHub 更新
clawhub update openclaw-security-scanner

# 或重新安装
clawhub install openclaw-security-scanner --force
```

## 卸载

```bash
# 通过 ClawHub 卸载
clawhub uninstall openclaw-security-scanner

# 或手动删除
rm -rf ~/.openclaw/workspace/skills/openclaw-security-scanner
```

---

**版本**: 1.0.2
**更新日期**: 2026-03-09  
**维护者**: Security Team
