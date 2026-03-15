---
name: openclaw-sync
description: "OpenClaw 数据轻量同步技能。基于 rclone + cron，支持 70+ 云存储后端，\n 定时备份 workspace 数据，资源占用极低。"
---

# 🔄 OpenClaw 轻量同步

基于 **rclone + cron** 的数据备份方案，定时同步 workspace 到云端。

## 特点

- ✅ **轻量**：无常驻进程，cron 定时触发
- ✅ **通用**：支持 70+ 云存储（七牛/腾讯/阿里/百度/Google Drive...）
- ✅ **智能**：无变化不传输，节省流量
- ✅ **简单**：一条命令完成配置

## 快速开始

### 1. 安装 rclone

```bash
# 自动安装
curl https://rclone.org/install.sh | sudo bash

# 或手动安装
sudo apt-get install rclone
```

### 2. 配置云存储

```bash
# 交互式配置
rclone config

# 按照提示选择云服务商，填写密钥
```

### 3. 配置同步

```bash
cd skills/openclaw-sync

# 编辑配置
vim config/sync-config.json
```

```json
{
  "remote": "myqiniu",           // rclone 配置的 remote 名称
  "bucket": "mybucket",          // 存储桶名称
  "prefix": "openclaw-backup",   // 云端目录前缀
  "interval": "5"                // 同步间隔（分钟）
}
```

### 4. 启动同步

```bash
# 手动测试
bash scripts/sync.sh

# 添加到 cron（推荐）
bash scripts/setup-cron.sh
```

## 目录结构

```
skills/openclaw-sync/
├── config/
│   ├── sync-config.json      # 同步配置
│   └── sync-list.txt         # 文件过滤规则
├── scripts/
│   ├── sync.sh               # 同步脚本
│   ├── setup-cron.sh         # 安装定时任务
│   └── status.sh             # 查看状态
├── logs/
│   └── sync.log              # 同步日志
└── SKILL.md                  # 本文件
```

## 配置文件

### sync-config.json

```json
{
  "remote": "myqiniu",           // rclone remote 名称
  "bucket": "mybucket",          // 存储桶
  "prefix": "openclaw-backup",   // 云端前缀
  "interval": "5",               // 同步间隔（分钟）
  "syncDelete": false            // 是否同步删除
}
```

### sync-list.txt

```
# 包含规则（+开头）
+MEMORY.md
+memory/
+IDENTITY.md
+USER.md
+SOUL.md
+AGENTS.md
+TOOLS.md
+HEARTBEAT.md
+BOOTSTRAP.md
+README.md
+skills/
+tools/

# 排除规则（-开头）
-.git/**
-node_modules/**
-*.tmp
-*.log
-.DS_Store
```

## 常用命令

| 命令 | 说明 |
|------|------|
| `bash scripts/sync.sh` | 手动执行同步 |
| `bash scripts/setup-cron.sh` | 安装定时任务 |
| `bash scripts/remove-cron.sh` | 移除定时任务 |
| `bash scripts/status.sh` | 查看同步状态 |
| `tail -f logs/sync.log` | 查看实时日志 |

## 支持的后端

- 七牛云 Kodo
- 腾讯云 COS
- 阿里云 OSS
- 百度云 BOS
- Google Drive
- Dropbox
- OneDrive
- WebDAV
- FTP/SFTP
- ...（共 70+）

配置方法：`rclone config` 交互式配置

## 故障排查

### 检查 rclone 配置
```bash
rclone listremotes          # 列出已配置的 remote
rclone ls myqiniu:mybucket  # 测试连接
```

### 检查同步日志
```bash
tail -50 logs/sync.log
```

### 手动测试同步
```bash
bash scripts/sync.sh --dry-run  # 模拟运行，不实际上传
```

## 许可证

MIT License
