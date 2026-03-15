# Session-Memory增强版Hook（v2.0.0）

## 🎯 核心功能（三位一体）

**一次触发，三件事自动完成**：
1. ✅ 保存会话记忆（OpenClaw原生session-memory hook）
2. ✅ 更新QMD知识库（`qmd update`）
3. ✅ 提交到Git库（`git commit`）

## 📊 工作流程

```
用户执行 /new 或 /reset
    ↓
原生session-memory hook触发
    ↓
保存会话上下文到MEMORY.md
    ↓
等待2秒（确保保存完成）
    ↓
更新QMD知识库（<10秒）
    ↓
检查Git变更
    ↓
自动提交（有变更时）
    ↓
记录详细日志
```

## 🚀 使用方式

### 自动模式（推荐）

**已配置为定时任务**：
```bash
# 每小时自动运行
0 * * * * /root/.openclaw/workspace/scripts/session-memory-enhanced.sh
```

**触发时机**：
- 定时：每小时自动运行
- 手动：用户执行 `/new` 或 `/reset` 时

### 手动模式

```bash
# 手动触发
bash /root/.openclaw/workspace/scripts/session-memory-enhanced.sh
```

### 查看日志

```bash
# 实时查看
tail -f /root/.openclaw/workspace/logs/session-memory-enhanced.log

# 查看最近30条
tail -30 /root/.openclaw/workspace/logs/session-memory-enhanced.log
```

## 📁 文件结构

```
/root/.openclaw/workspace/
├── scripts/
│   └── session-memory-enhanced.sh    # 增强版hook脚本
├── logs/
│   └── session-memory-enhanced.log   # 运行日志
├── MEMORY.md                          # 长期记忆
└── memory/YYYY-MM-DD.md              # 每日日志
```

## 🔧 配置说明

### 修改运行频率

**编辑crontab**：
```bash
crontab -e
```

**修改频率**（示例）：
```bash
# 每小时（推荐）
0 * * * * /root/.openclaw/workspace/scripts/session-memory-enhanced.sh

# 每30分钟
*/30 * * * * /root/.openclaw/workspace/scripts/session-memory-enhanced.sh

# 每2小时
0 */2 * * * /root/.openclaw/workspace/scripts/session-memory-enhanced.sh
```

### 禁用自动更新

```bash
# 编辑crontab
crontab -e

# 注释掉相关行
# 0 * * * * /root/.openclaw/workspace/scripts/session-memory-enhanced.sh
```

## 📊 性能影响

| 操作 | 频率 | 耗时 | 影响 |
|------|------|------|------|
| QMD更新 | 1次/小时 | <10秒 | 极低 |
| Git提交 | 1次/小时 | <5秒 | 极低 |
| 总体 | 1次/小时 | <15秒 | 可忽略 |

## 💡 最佳实践

### ✅ 推荐做法

1. **保持自动模式**：每小时自动更新
2. **定期检查日志**：`tail -100 logs/session-memory-enhanced.log`
3. **定期推送Git**：`git push`（可选）

### ⚠️ 注意事项

1. **不要频繁运行**：建议最少30分钟间隔
2. **监控磁盘空间**：日志文件会逐渐增大
3. **定期清理日志**：`> logs/session-memory-enhanced.log`

## 🎯 对比旧版

| 特性 | 旧版enhanced-session-memory | 新版session-memory-enhanced |
|------|---------------------------|--------------------------|
| 保存会话记忆 | ❌ | ✅（原生hook）|
| 触发时机 | 定时（1小时）| 定时 + /new + /reset |
| 更新QMD | ✅ | ✅ |
| 提交Git | ✅ | ✅ |
| 详细日志 | ❌ | ✅ |
| 变更统计 | ❌ | ✅（+X ~X -X）|
| 自动化程度 | 半自动 | 全自动 |

## 📞 故障排查

### 问题1：没有自动更新

**检查crontab**：
```bash
crontab -l | grep session-memory-enhanced
```

**检查脚本权限**：
```bash
ls -l /root/.openclaw/workspace/scripts/session-memory-enhanced.sh
```

### 问题2：更新失败

**查看日志**：
```bash
tail -50 /root/.openclaw/workspace/logs/session-memory-enhanced.log
```

**手动测试**：
```bash
bash /root/.openclaw/workspace/scripts/session-memory-enhanced.sh
```

### 问题3：Git提交失败

**检查Git状态**：
```bash
cd /root/.openclaw/workspace
git status
```

**手动提交**：
```bash
git add -A
git commit -m "手动提交"
```

## 🚀 未来优化

- [ ] 检测到记忆变更时立即更新（inotify）
- [ ] 自动推送到远程Git仓库
- [ ] 智能压缩历史提交
- [ ] 与Context Monitor联动（达到阈值时触发）
- [ ] AI智能摘要生成

## 📝 版本历史

### v2.0.0 (2026-03-07 14:47)
- ✅ 合并session-memory + enhanced-session-memory
- ✅ 支持三种触发方式：定时 + /new + /reset
- ✅ 详细日志记录
- ✅ 变更统计（+X ~X -X）

### v1.0.0 (2026-03-07 14:42)
- ✅ 基础功能：QMD更新 + Git提交

---

**创建时间**：2026-03-07 14:47
**版本**：2.0.0
**作者**：米粒儿
