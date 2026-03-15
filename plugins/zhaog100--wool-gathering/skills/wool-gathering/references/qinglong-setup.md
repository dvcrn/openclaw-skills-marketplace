# 青龙面板配置指南

## 📦 已部署环境

- **服务器**: 43.133.55.138
- **青龙面板**: http://43.133.55.138:5700
- **Docker版本**: 29.2.1
- **dailycheckin**: 25.12.9

---

## 🚀 Docker部署（已安装）

### **docker-compose.yml**

```yaml
version: '3.8'

services:
  qinglong:
    image: whyour/qinglong:latest
    container_name: qinglong
    restart: unless-stopped
    ports:
      - "5700:5700"
    environment:
      - TZ=Asia/Shanghai
    volumes:
      - ./data:/ql/data
      - ./scripts:/ql/scripts
      - ./config:/ql/config
      - ./log:/ql/log
      - ./db:/ql/db
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5700"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### **启动命令**

```bash
# 启动
docker compose up -d

# 查看日志
docker logs qinglong --tail 100

# 进入容器
docker exec -it qinglong /bin/sh
```

---

## 🔧 配置文件路径

| 文件 | 路径 | 说明 |
|------|------|------|
| 主配置 | `/ql/data/config/config.sh` | 环境变量配置 |
| 签到配置 | `/ql/config/config.json` | dailycheckin账号配置 |
| 定时任务 | `/ql/data/config/crontab.list` | crontab任务列表 |
| 脚本目录 | `/ql/scripts/` | 自定义脚本 |

---

## 📝 dailycheckin配置

### **配置文件路径**
```
/ql/config/config.json
```

### **配置示例**

```json
{
  "BILIBILI": [
    {
      "name": "我的B站账号",
      "cookie": "buvid3=xxx; SESSDATA=xxx; bili_jct=xxx; ..."
    }
  ],
  "ALIYUN": [
    {
      "name": "我的阿里云盘账号",
      "refresh_token": "你的refresh_token值"
    }
  ],
  "BAIDUWP": [
    {
      "name": "我的百度网盘账号",
      "cookie": "BDUSS=你的BDUSS值"
    }
  ]
}
```

---

## ⏰ 定时任务配置

### **通过Web界面**

1. 打开青龙面板
2. 点击「定时任务」→「添加任务」
3. 填写：
   - 名称：`每日签到`
   - 命令：`dailycheckin`
   - 定时：`0 8 * * *`（每天8点）
4. 保存

### **通过SSH**

```bash
# 进入容器
docker exec -it qinglong /bin/sh

# 编辑crontab
vi /ql/data/config/crontab.list

# 添加任务
0 8 * * * dailycheckin
```

---

## 🛠️ 常用命令

```bash
# 查看容器状态
docker ps | grep qinglong

# 重启容器
docker restart qinglong

# 查看日志
docker logs qinglong --tail 100

# 进入容器
docker exec -it qinglong /bin/sh

# 手动运行签到
docker exec qinglong dailycheckin

# 安装依赖
docker exec qinglong pip3 install 包名
```

---

## 🔔 配置推送通知

### **Server酱（微信）**

```bash
# 编辑配置文件
vi /ql/data/config/config.sh

# 添加
export PUSH_KEY="你的server酱key"
```

### **PushPlus（微信）**

```bash
export PUSHPLUS_TOKEN="你的pushplus token"
```

### **钉钉机器人**

```bash
export DD_BOT_TOKEN="你的钉钉机器人token"
export DD_BOT_SECRET="你的钉钉机器人密钥"
```

---

## ⚠️ 注意事项

1. **配置文件同步**: 修改 `/ql/data/config/dailycheckin_config.json` 后需要同步到 `/ql/config/config.json`
2. **Cookie有效期**: Cookie通常1-3个月过期，需要定期更新
3. **安全组**: 确保云服务器安全组开放5700端口
4. **数据备份**: 定期备份 `/ql/data/` 目录

---

**最后更新**: 2026-03-03
