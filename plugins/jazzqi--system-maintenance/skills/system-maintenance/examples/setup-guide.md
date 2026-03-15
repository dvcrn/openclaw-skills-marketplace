# 系统维护技能设置指南

## 🎯 目标

通过本技能实现 OpenClaw 系统的自动化维护，包括：
- 定期清理日志和临时文件
- 监控系统健康状态
- 优化内存和 Token 使用
- 确保关键服务正常运行

## 📦 安装方法

### 方法1：直接复制（推荐）
```bash
# 创建技能目录
mkdir -p ~/.openclaw/skills/system-maintenance

# 复制文件
cp -r /path/to/skill/* ~/.openclaw/skills/system-maintenance/
```

### 方法2：ClawHub 安装
```bash
# 发布技能后
clawhub install system-maintenance
```

## ⚙️ 配置步骤

### 1. 测试技能功能
```bash
cd ~/.openclaw/skills/system-maintenance
node entry.js status     # 检查系统状态
node entry.js quick      # 运行快速清理
```

### 2. 安装定时任务
```bash
# 安装到 crontab
node entry.js install-cron

# 或者手动添加
echo "30 3 * * * ~/.openclaw/skills/system-maintenance/scripts/daily-maintenance-optimization.sh >> /tmp/openclaw-maintenance.log 2>&1" | crontab -
```

### 3. 验证安装
```bash
# 查看定时任务
crontab -l | grep maintenance

# 查看维护日志
tail -f /tmp/openclaw-maintenance.log
```

## 🔧 自定义配置

### 修改维护时间
编辑 crontab：
```bash
# 例如改为凌晨4:30
0 4 * * * ~/.openclaw/skills/system-maintenance/scripts/daily-maintenance-optimization.sh
```

### 调整清理策略
编辑 `scripts/daily-maintenance-optimization.sh`：
- 修改日志保留天数：`mtime +3` → `mtime +7`
- 调整磁盘检查阈值
- 添加自定义检查项

### 扩展功能
1. 在 `entry.js` 中添加新方法
2. 创建新的脚本文件
3. 集成到其他自动化流程

## 📊 监控维护效果

### 检查维护日志
```bash
# 查看最近维护记录
ls -la /tmp/openclaw-maintenance-*.log
tail -50 /tmp/openclaw-maintenance-$(date +%Y%m%d).log
```

### 监控系统资源
```bash
# Gateway 内存使用
ps aux | grep openclaw-gateway | awk '{print $6/1024" MB"}'

# 工作区大小变化
du -sh ~/.openclaw/workspace/
```

### 验证定时任务
```bash
# 查看任务执行状态
openclaw cron list | grep -i "财经\|news"

# 检查下次执行时间
openclaw cron list --json | jq '.jobs[] | select(.name | contains("财经"))'
```

## 🚨 故障排除

### 问题1：维护脚本不执行
```bash
# 检查 crontab
crontab -l

# 检查脚本权限
ls -la ~/.openclaw/skills/system-maintenance/scripts/

# 手动测试
bash ~/.openclaw/skills/system-maintenance/scripts/daily-maintenance-optimization.sh
```

### 问题2：Gateway 重启失败
```bash
# 检查 Gateway 状态
curl -s http://localhost:18789/

# 手动重启
openclaw gateway restart

# 查看日志
tail -50 /tmp/openclaw/openclaw-$(date +%Y-%m-%d).log
```

### 问题3：磁盘空间不足
```bash
# 检查磁盘使用
df -h /

# 清理大文件
find ~/.openclaw -name "*.log" -size +100M -exec ls -lh {} \;
find /tmp -name "openclaw-*.log" -size +50M -exec rm -f {} \;
```

## 🔄 更新技能

### 获取更新
```bash
cd ~/.openclaw/skills/system-maintenance
git pull origin main  # 如果是 git 仓库
```

### 手动更新
1. 备份当前配置
2. 下载新版本
3. 测试新功能
4. 应用更新

---

*基于 2026-03-08 的实践经验编写*
