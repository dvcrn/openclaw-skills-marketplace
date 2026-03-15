# Changelog

## [1.1.1] - 2026-03-01

### Fixed (Security Scan Issues)
- **Removed hardcoded `/root` paths**: Now uses `$HOME` or `$OPENCLAW_WORKSPACE` environment variable
- **Removed `sudo` usage**: No longer requires sudo for fail2ban-client calls
- **Removed unused `curl` dependency**: Removed from skill metadata and requirements
- **Added OS restriction**: Explicitly requires Linux with systemd
- **Fixed 8-layer consistency**: Removed all leftover 10-layer references in README and config
- **Added script integrity checking**: SHA256 hashes for all scripts, `hash` command for verification
- **Added install script**: Generates integrity hashes during installation
- **Improved error handling**: Better handling of missing permissions and files
- **Fixed config inconsistencies**: Removed config-monitor and learning-system-manager references

### Security Improvements
- Scripts no longer assume root privileges
- Workspace path configurable via environment variable
- Optional features gracefully degrade when permissions unavailable
- Script hash verification on each run

## [1.1.0] - 2026-03-01

### Changed
- **Simplified to 8-layer system** (from 10-layer)
- Removed Layer 2: Config Monitor (specialized for specific deployments)
- Removed Layer 7: Learning System Manager (specialized for specific deployments)
- Reorganized layer numbering: 1-8
- Updated health score calculation for 8 layers
- Streamlined for general-purpose use

### 8-Layer Monitoring System
1. SSH Login Monitor
2. Heartbeat Monitor
3. Outbound Traffic Monitor
4. UFW Firewall
5. Package Integrity Monitor
6. Report Monitor
7. Cleanup Monitor
8. Internal Security Monitor

### Notes
- This is the **general-purpose version** suitable for standard deployments
- For full 10-layer system with Config Monitor and Learning System, use specialized deployment

## [1.0.0] - 2026-02-28

### Added
- 初始版本发布
- 10层系统监控集成
- 实时健康评分系统 (0-100)
- 安全状态仪表板
- 监控层状态检查 (1-10层)
- 自动报告生成功能
- Telegram告警集成
- 历史性能趋势分析
- 可配置告警阈值
- 完整测试套件

### Features
- **Real-time Health Scoring**: 基于10层监控系统的动态评分
- **Security Dashboard**: 整合fail2ban、防火墙、完整性监控
- **Layer-specific Checks**: 支持单独检查每层监控状态
- **Automated Reporting**: 定时生成健康报告
- **Alert Integration**: 关键问题自动通知

### Monitoring Layers
1. SSH登录监控
2. 系统配置监控
3. 心跳健康检查
4. 出站流量监控
5. UFW防火墙
6. 软件包完整性
7. 学习系统管理
8. 定时报告监控
9. 系统清理维护
10. 内网安全监控

### Technical
- 支持OpenClaw Gateway集成
- 基于systemd服务状态检测
- 依赖: systemd, jq, curl
- 测试环境: OpenClaw集成学习系统

---
**Author**: ZLMbot 🦞
**License**: MIT
