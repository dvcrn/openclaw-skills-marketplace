# 🛠️ 灵犀维护手册

> **维护指南和故障排查**  
> **版本：** v3.3.6  
> **最后更新：** 2026-03-13

---

## 📋 日常维护清单

### 每日检查

- [ ] Dashboard 可访问性测试
- [ ] 任务记录是否正常
- [ ] 日志文件大小检查
- [ ] 数据库备份

### 每周检查

- [ ] 系统资源使用（CPU/内存/磁盘）
- [ ] Token 消耗统计
- [ ] 技能使用频率分析
- [ ] 错误日志审查

---

## 🔍 故障排查指南

### 问题 1：Dashboard 无法访问

**症状：**
- 浏览器显示"拒绝连接"
- curl 返回错误

**排查步骤：**

```bash
# 1. 检查 Dashboard 进程
ps aux | grep "python3 server.py"

# 2. 检查端口监听
netstat -tlnp | grep 8765
# 或
ss -tlnp | grep 8765

# 3. 查看 Dashboard 日志
tail -50 /tmp/dashboard.log

# 4. 测试本地访问
curl http://127.0.0.1:8765/

# 5. 重启 Dashboard
pkill -f "python3 server.py"
cd /root/lingxi-ai-latest/dashboard/v3
nohup python3 server.py > /tmp/dashboard.log 2>&1 &
sleep 2
curl http://127.0.0.1:8765/
```

**常见原因：**
- Dashboard 进程未运行
- 端口被占用
- 防火墙阻止访问

---

### 问题 2：任务列表不更新

**症状：**
- 记忆文件有记录
- Dashboard 任务列表停滞

**排查步骤：**

```bash
# 1. 检查 httpx 模块
python3 -c "import httpx; print('OK')"

# 2. 检查 Dashboard Token
cat ~/.openclaw/workspace/.lingxi/dashboard_token.txt

# 3. 测试 Dashboard 客户端
python3 << 'EOF'
import sys
sys.path.insert(0, '/root/lingxi-ai-latest')
from scripts.dashboard_client import get_dashboard_client

client = get_dashboard_client()
print("Token:", client.token[:20] + "..." if client.token else "EMPTY")

result = client.record_task({
    "user_id": "test",
    "channel": "test",
    "user_input": "测试",
    "status": "completed"
})
print("Result:", result)
EOF

# 4. 检查数据库
python3 -c "
import sqlite3
conn = sqlite3.connect('/root/lingxi-ai-latest/data/dashboard_v3.db')
cur = conn.cursor()
cur.execute('SELECT COUNT(*) FROM tasks')
print('Total:', cur.fetchone()[0])
"
```

**解决方案：**

```bash
# 安装缺失的 httpx 模块
pip3 install httpx --break-system-packages

# 验证
python3 -c "import httpx; print('✅ httpx installed')"
```

---

### 问题 3：时间显示错误

**症状：**
- 数据库时间戳正确
- Dashboard 显示日期错误（如 3 月 14 日而非 3 月 13 日）

**排查：**

```bash
# 检查数据库时间戳
python3 -c "
import sqlite3, time
conn = sqlite3.connect('/root/lingxi-ai-latest/data/dashboard_v3.db')
cur = conn.cursor()
cur.execute('SELECT created_at FROM tasks ORDER BY created_at DESC LIMIT 1')
ts = cur.fetchone()[0]
print('Timestamp:', ts)
print('UTC:', time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(ts)))
print('Beijing:', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(ts)))
"
```

**解决方案：**

修改 `dashboard/v3/index.html` 的 `formatTimeBeijing` 函数，确保秒级时间戳 × 1000 转换为毫秒。

---

### 问题 4：灵犀无响应

**症状：**
- 发送消息后长时间无回复
- OpenClaw 日志无错误

**排查：**

```bash
# 1. 检查 OpenClaw Gateway
openclaw gateway status

# 2. 查看 OpenClaw 日志
tail -100 /tmp/openclaw/openclaw-$(date +%Y-%m-%d).log

# 3. 检查 Layer0 规则
cat ~/.openclaw/workspace/.lingxi/layer0_rules.json

# 4. 测试灵犀导入
cd /root/lingxi-ai-latest
python3 -c "from scripts.orchestrator_v2 import SmartOrchestrator; print('✅ Import OK')"
```

---

### 问题 5：内存/记忆不保存

**症状：**
- 对话正常
- 重启后记忆丢失

**排查：**

```bash
# 1. 检查记忆文件
ls -la ~/.openclaw/workspace/memory/items/
cat ~/.openclaw/workspace/memory/items/memories.jsonl | tail -5

# 2. 检查 MindCore 数据库
python3 -c "
import sqlite3
conn = sqlite3.connect('/root/.openclaw/workspace/.lingxi/mindcore.db')
cur = conn.cursor()
cur.execute('SELECT COUNT(*) FROM memories')
print('Memories:', cur.fetchone()[0])
"

# 3. 检查写入权限
ls -la ~/.openclaw/workspace/.lingxi/
```

---

## 📊 监控脚本

### 健康检查脚本

```bash
#!/bin/bash
# save as: /root/lingxi-ai-latest/scripts/health_check.sh

echo "=== 灵犀健康检查 ==="
echo "时间：$(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 1. Dashboard 检查
echo "📊 Dashboard 状态:"
if curl -s http://127.0.0.1:8765/api/health > /dev/null 2>&1; then
    echo "  ✅ Dashboard 在线"
else
    echo "  ❌ Dashboard 离线"
fi

# 2. 数据库检查
echo ""
echo "💾 数据库状态:"
python3 -c "
import sqlite3
conn = sqlite3.connect('/root/lingxi-ai-latest/data/dashboard_v3.db')
cur = conn.cursor()
cur.execute('SELECT COUNT(*) FROM tasks')
print(f'  任务数：{cur.fetchone()[0]}')
cur.execute('SELECT COUNT(*) FROM skills')
print(f'  技能数：{cur.fetchone()[0]}')
"

# 3. 磁盘使用
echo ""
echo "💿 磁盘使用:"
df -h /root | tail -1 | awk '{print "  使用率："$5" ("$3" used)"}'

# 4. 进程检查
echo ""
echo "⚙️  进程状态:"
ps aux | grep -c "[p]ython3 server.py" | xargs -I {} echo "  Dashboard 进程：{}"

echo ""
echo "=== 检查完成 ==="
```

---

## 🔄 备份策略

### 数据库备份

```bash
#!/bin/bash
# save as: /root/lingxi-ai-latest/scripts/backup.sh

BACKUP_DIR="/backup/lingxi"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# 备份 Dashboard 数据库
cp /root/lingxi-ai-latest/data/dashboard_v3.db $BACKUP_DIR/dashboard_v3_$DATE.db

# 备份 MindCore 数据库
cp ~/.openclaw/workspace/.lingxi/mindcore.db $BACKUP_DIR/mindcore_$DATE.db

# 备份记忆文件
cp ~/.openclaw/workspace/memory/items/memories.jsonl $BACKUP_DIR/memories_$DATE.jsonl

# 删除 7 天前的备份
find $BACKUP_DIR -name "*.db" -mtime +7 -delete
find $BACKUP_DIR -name "*.jsonl" -mtime +7 -delete

echo "✅ 备份完成：$BACKUP_DIR"
```

### 定时备份（Cron）

```bash
# 每天凌晨 2 点备份
0 2 * * * /root/lingxi-ai-latest/scripts/backup.sh >> /tmp/lingxi_backup.log 2>&1
```

---

## 📈 性能优化

### 1. 数据库索引优化

```sql
-- 添加索引加速查询
CREATE INDEX IF NOT EXISTS idx_tasks_created_at ON tasks(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_tasks_channel ON tasks(channel);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
```

### 2. 日志轮转

```bash
# /etc/logrotate.d/lingxi
/tmp/lingxi-ai-latest/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
}
```

### 3. 缓存清理

```bash
#!/bin/bash
# 清理旧缓存文件
find /root/lingxi-ai-latest/cache -type f -mtime +3 -delete
```

---

## 🚨 紧急恢复

### Dashboard 崩溃恢复

```bash
# 1. 停止旧进程
pkill -f "python3 server.py"

# 2. 检查数据库完整性
python3 -c "
import sqlite3
conn = sqlite3.connect('/root/lingxi-ai-latest/data/dashboard_v3.db')
cur = conn.cursor()
cur.execute('PRAGMA integrity_check')
print(cur.fetchone()[0])
"

# 3. 重启 Dashboard
cd /root/lingxi-ai-latest/dashboard/v3
nohup python3 server.py > /tmp/dashboard.log 2>&1 &

# 4. 验证
sleep 2
curl http://127.0.0.1:8765/api/health
```

### 数据库损坏恢复

```bash
# 1. 从备份恢复
cp /backup/lingxi/dashboard_v3_20260313.db /root/lingxi-ai-latest/data/dashboard_v3.db

# 2. 或使用 SQLite 恢复
sqlite3 /root/lingxi-ai-latest/data/dashboard_v3.db ".recover" | sqlite3 dashboard_v3_recovered.db
mv dashboard_v3_recovered.db /root/lingxi-ai-latest/data/dashboard_v3.db
```

---

## 📞 获取帮助

### 查看日志

```bash
# Dashboard 日志
tail -f /tmp/dashboard.log

# OpenClaw 日志
tail -f /tmp/openclaw/openclaw-$(date +%Y-%m-%d).log

# 灵犀脚本日志
tail -f /root/lingxi-ai-latest/logs/debug.log
```

### 调试模式

```bash
# 启用 Dashboard 调试
cd /root/lingxi-ai-latest/dashboard/v3
python3 server.py --reload --debug
```

---

*定期维护，系统更稳定* 🦞✨
