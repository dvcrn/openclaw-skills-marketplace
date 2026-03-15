# 安全迁移指南

## 🎯 迁移目标
从旧的、分散的维护系统迁移到新的统一维护系统。

## 📋 迁移前准备

### 1. 检查当前系统
```bash
# 查看当前 crontab 任务
crontab -l | grep -i openclaw

# 检查现有脚本
ls -la ~/.openclaw/openclaw-*.sh 2>/dev/null || echo "无旧脚本"
```

### 2. 创建完整备份
```bash
# 创建备份目录
BACKUP_DIR="$HOME/openclaw-migration-backup/$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"

# 备份 crontab
crontab -l > "$BACKUP_DIR/crontab-before.txt"

# 备份旧脚本
cp ~/.openclaw/openclaw-*.sh "$BACKUP_DIR/" 2>/dev/null || true
```

## 🚀 迁移步骤

### 阶段1: 并行运行 (推荐1周)

#### 1.1 安装新系统
```bash
# 运行安装脚本
bash ~/.openclaw/skills/system-maintenance/scripts/install-maintenance-system.sh
```

#### 1.2 验证安装
```bash
# 检查新任务
crontab -l | grep "real-time-monitor\|log-management\|daily-maintenance\|weekly-optimization"

# 应该看到4个新任务
```

#### 1.3 并行运行状态
```
旧系统: 继续运行原有任务
新系统: 同时运行新任务
日志: 分别记录到不同文件
```

### 阶段2: 功能验证 (1-7天)

#### 2.1 验证脚本功能
```bash
# 测试实时监控
timeout 10 ~/.openclaw/skills/system-maintenance/scripts/real-time-monitor.sh

# 测试日志管理
~/.openclaw/skills/system-maintenance/scripts/log-management.sh --dry-run

# 测试日常维护
~/.openclaw/skills/system-maintenance/scripts/daily-maintenance.sh --test
```

#### 2.2 监控执行情况
- 检查新系统日志
- 验证自动恢复功能
- 确认所有任务按时执行

### 阶段3: 切换主用

#### 3.1 准备切换
```bash
# 再次备份当前状态
crontab -l > "$BACKUP_DIR/crontab-before-switch.txt"
```

#### 3.2 执行切换
```bash
# 方法A: 使用安装脚本的切换模式
bash ~/.openclaw/skills/system-maintenance/scripts/install-maintenance-system.sh --switch-only

# 方法B: 手动编辑 crontab
crontab -e
# 注释或删除旧任务，只保留新任务
```

#### 3.3 验证切换
```bash
# 检查当前任务
crontab -l | grep -c "^[^#]"  # 应该只有4个

# 确认新系统为主用
crontab -l | grep -i openclaw
```

### 阶段4: 清理优化

#### 4.1 清理临时文件
```bash
# 清理旧的临时文件
find /tmp -name "openclaw-*.log" -mtime +7 -delete 2>/dev/null

# 清理用户主目录临时文件
rm ~/crontab.backup.* ~/openclaw-*.txt 2>/dev/null || true
```

#### 4.2 归档旧脚本
```bash
# 移动旧脚本到备份目录
mv ~/.openclaw/openclaw-weekly-optimizer.sh "$BACKUP_DIR/" 2>/dev/null || true
mv ~/.openclaw/openclaw-agent-monitor.sh "$BACKUP_DIR/" 2>/dev/null || true
```

#### 4.3 更新文档
- 记录迁移过程和结果
- 创建最终状态报告
- 更新维护计划

## 🔄 回滚指南

### 如果迁移失败
```bash
# 1. 进入备份目录
cd "$BACKUP_DIR"

# 2. 恢复 crontab
crontab crontab-before-switch.txt

# 3. 恢复旧脚本
cp openclaw-weekly-optimizer.sh ~/.openclaw/ 2>/dev/null || true
cp openclaw-agent-monitor.sh ~/.openclaw/ 2>/dev/null || true

# 4. 验证恢复
crontab -l | grep -i openclaw
```

## 📊 迁移检查清单

### 迁移前
- [ ] 完整备份创建
- [ ] 当前状态记录
- [ ] 风险评估完成

### 阶段1: 并行运行
- [ ] 新系统安装成功
- [ ] 新旧系统同时运行
- [ ] 日志正常生成

### 阶段2: 功能验证
- [ ] 所有脚本功能正常
- [ ] 自动恢复工作
- [ ] 无任务冲突

### 阶段3: 切换主用
- [ ] 新系统成为主用
- [ ] 旧系统任务已注释
- [ ] 验证切换成功

### 阶段4: 清理优化
- [ ] 临时文件清理
- [ ] 旧脚本归档
- [ ] 文档更新

## 🚨 风险控制

### 高风险场景
1. **crontab 编辑失败** - 使用备份恢复
2. **脚本权限问题** - 检查并修复权限
3. **系统资源不足** - 监控资源使用

### 应急计划
1. 立即回滚到备份状态
2. 检查错误日志
3. 寻求帮助或技术支持

## 📝 迁移记录模板

### 迁移信息
- **开始时间**: [填写]
- **完成时间**: [填写]
- **负责人**: [填写]

### 执行步骤
1. [步骤1结果]
2. [步骤2结果]
3. [步骤3结果]

### 遇到的问题
- [问题描述和解决方案]

### 最终状态
- [新系统状态]
- [旧系统处理]
- [备份位置]

---

**按照本指南，你可以安全、平滑地完成维护系统迁移。** 🛡️
