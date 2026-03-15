# 后续优化建议

## 1. 日志路径优化
**当前**: 日志在 `/tmp/openclaw-new-*.log`
**建议**: 迁移到 `~/.openclaw/maintenance/logs/`

### 迁移步骤:
```bash
# 修改 crontab 中的日志路径
crontab -e
# 将 /tmp/openclaw-new- 改为 ~/.openclaw/maintenance/logs/
```

### 目标配置:
```
*/5 * * * * ~/.openclaw/maintenance/scripts/real-time-monitor.sh >> ~/.openclaw/maintenance/logs/real-time.log 2>&1
0 2 * * * ~/.openclaw/maintenance/scripts/log-management.sh >> ~/.openclaw/maintenance/logs/log-mgmt.log 2>&1
30 3 * * * ~/.openclaw/maintenance/scripts/daily-maintenance.sh >> ~/.openclaw/maintenance/logs/daily.log 2>&1
0 3 * * 0 ~/.openclaw/maintenance/scripts/weekly-optimization.sh >> ~/.openclaw/maintenance/logs/weekly.log 2>&1
```

## 2. 旧脚本归档
**当前**: 旧脚本仍在 `~/.openclaw/` 目录
**建议**: 移动到备份目录或删除

### 可归档的文件:
- `~/.openclaw/openclaw-weekly-optimizer.sh`
- `~/.openclaw/openclaw-agent-monitor.sh`

## 3. 定期清理计划
**建议**: 在每周优化脚本中增加临时文件清理

### 可清理的内容:
- 7天前的临时文件
- 过期的备份文件
- 无用的测试文件

## 4. 监控改进
**建议**: 添加邮件或通知功能

### 监控项:
- 任务执行失败
- 磁盘空间不足
- Gateway 服务异常

## 5. 技能更新
**当前**: 技能版本为 v1.1.0
**建议**: 更新到 v1.2.0 包含完整维护系统

### 更新内容:
- 添加每周优化脚本
- 完善文档
- 添加优化建议
