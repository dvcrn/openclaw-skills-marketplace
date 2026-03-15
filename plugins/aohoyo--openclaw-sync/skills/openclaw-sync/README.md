# OpenClaw 数据同步 - 使用说明

## 快速开始

### 1. 首次配置

运行配置向导：

```bash
cd /home/node/.openclaw/workspace/skills/openclaw-sync
bash scripts/setup.sh
```

配置向导会引导你：
- 选择云存储服务商（腾讯云/七牛云/阿里云）
- 配置访问密钥
- 选择同步模式（实时/定时/手动）
- 测试连接

### 2. 手动同步

立即同步数据到云端：

```bash
bash scripts/sync-now.sh
```

### 3. 查看云端文件

列出云端备份的文件：

```bash
bash scripts/list-remote.sh
```

### 4. 恢复数据

从云端恢复数据到本地：

```bash
bash scripts/restore.sh
```

## 同步模式

### 实时同步

文件修改后自动同步到云端（延迟约 10-30 秒）。

启动服务：
```bash
sudo cp systemd/openclaw-sync.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable openclaw-sync
sudo systemctl start openclaw-sync
```

查看状态：
```bash
sudo systemctl status openclaw-sync
```

### 定时同步

每天固定时间同步一次（通过 crontab）。

配置向导会自动添加定时任务，也可以手动配置：
```bash
# 每天凌晨 3 点同步
0 3 * * * /home/node/.openclaw/workspace/skills/openclaw-sync/scripts/sync-now.sh >> /var/log/openclaw-sync.log 2>&1
```

### 手动同步

需要时手动触发：
```bash
bash scripts/sync-now.sh
```

## 同步的数据

默认同步以下数据（可在 `data/sync-list.txt` 中修改）：

- **核心数据**：MEMORY.md, memory/, USER.md, IDENTITY.md, SOUL.md 等
- **技能配置**：skills/*/config.json
- **自定义工具**：tools/, *.sh

## 配置文件

- `config/rclone.conf` - rclone 配置（包含云存储密钥）
- `config/backup.json` - 备份配置（云服务商、bucket 等）
- `data/sync-list.txt` - 同步文件列表

## 故障排查

### 同步失败

1. 检查 rclone 配置：
```bash
rclone config show --config config/rclone.conf
```

2. 测试连接：
```bash
rclone ls openclaw-backup:YOUR_BUCKET --config config/rclone.conf
```

3. 查看日志：
```bash
tail -f /var/log/openclaw-sync.log
```

### 恢复失败

1. 确认云端有数据：
```bash
bash scripts/list-remote.sh
```

2. 检查本地权限：
```bash
ls -la /home/node/.openclaw/workspace/
```

## 成本估算

数据量通常 < 1MB，成本几乎为零：

| 云服务商 | 免费额度 | 月成本 |
|---------|---------|--------|
| 腾讯云 COS | 6个月 50GB | ¥0 |
| 七牛云 Kodo | 每月 10GB | ¥0 |
| 阿里云 OSS | 无 | < ¥0.01 |

## 安全提示

- ✅ 配置文件权限为 600，保护密钥安全
- ✅ 不要将 `config/rclone.conf` 提交到 Git
- ✅ 定期检查同步日志，确保备份正常
- ✅ 重要修改后建议立即手动同步一次

## 迁移到新服务器

1. 在旧服务器上执行最后一次同步：
```bash
bash scripts/sync-now.sh
```

2. 在新服务器上：
```bash
# 安装 OpenClaw
# 安装 openclaw-sync 技能
cd /home/node/.openclaw/workspace/skills/openclaw-sync
bash scripts/setup.sh  # 使用相同的云服务商和密钥
bash scripts/restore.sh
```

3. 完成！所有数据已恢复。
