---
name: searxng-auto-proxy
description: "SearXNG 自适应代理检测技能，自动检测 Clash 代理可用性，智能切换全球/国内搜索引擎。支持定时检测、日志记录、故障告警。"
---

# SearXNG Auto Proxy - 自适应代理检测

自动检测代理，智能切换搜索引擎。

---

## 🎯 功能特性

### 核心功能

- ✅ **自动检测** - 每小时检测 Clash 代理可用性
- ✅ **智能切换** - 根据代理状态启用/禁用全球引擎
- ✅ **日志记录** - 完整检测日志
- ✅ **故障告警** - 代理异常时通知
- ✅ **无缝重启** - SearXNG 平滑重启

### 支持的搜索引擎

**全球引擎（代理可用时）：**
- Google
- DuckDuckGo
- Wikipedia
- Brave
- Startpage

**国内引擎（始终可用）：**
- 百度
- 必应中国

---

## 🚀 快速开始

### 安装

```bash
# 克隆技能
git clone https://github.com/pengong101/searxng-auto-proxy.git
cd searxng-auto-proxy

# 安装依赖
pip3 install -r requirements.txt

# 配置
cp config.example.py config.py
nano config.py  # 修改配置

# 运行
python3 adapter.py
```

---

### 配置 Cron（每小时检测）

```bash
# 编辑 crontab
crontab -e

# 添加（每小时执行）
0 * * * * /usr/bin/python3 /path/to/adapter.py >> /var/log/searxng-proxy-check.log 2>&1

# 或（NAS 启动时执行）
@reboot /usr/bin/python3 /path/to/adapter.py >> /var/log/searxng-proxy-check.log 2>&1
```

---

## 📊 使用示例

### 手动运行

```bash
# 运行检测
python3 adapter.py

# 查看日志
tail -f /var/log/searxng-proxy-check.log
```

### 输出示例

**代理可用时：**
```
[2026-03-11 13:08:38] ========================================
[2026-03-11 13:08:38] 🚀 SearXNG 自适应代理检测启动
[2026-03-11 13:08:38] ========================================
[2026-03-11 13:08:38] 🔍 检测 Clash 代理可用性...
[2026-03-11 13:08:38] ✅ 代理可用，可以访问全球搜索引擎
[2026-03-11 13:08:38] 🌐 启用全球搜索引擎（Google, DuckDuckGo, Wikipedia...）
[2026-03-11 13:08:38] 🔄 重启 SearXNG 容器...
[2026-03-11 13:08:46] ✅ SearXNG 已重启
[2026-03-11 13:08:46] 🧪 测试搜索功能...
[2026-03-11 13:08:46] ✅ Google 搜索正常
[2026-03-11 13:08:46] ✅ 百度搜索正常
[2026-03-11 13:08:46] ========================================
[2026-03-11 13:08:46] ✅ 自适应代理检测完成
[2026-03-11 13:08:46] ========================================
🌐 当前状态：全球搜索引擎已启用
```

---

**代理不可用时：**
```
[2026-03-11 13:08:38] 🔍 检测 Clash 代理可用性...
[2026-03-11 13:08:38] ❌ 代理不可用：Connection refused
[2026-03-11 13:08:38] 🇨🇳 禁用全球搜索引擎，仅保留国内引擎
[2026-03-11 13:08:38] 🔄 重启 SearXNG 容器...
[2026-03-11 13:08:46] ✅ SearXNG 已重启
[2026-03-11 13:08:46] 🧪 测试搜索功能...
[2026-03-11 13:08:46] ✅ 百度搜索正常
[2026-03-11 13:08:46] ✅ 必应搜索正常
🇨🇳 当前状态：仅国内搜索引擎
```

---

## 🔧 配置说明

### config.py

```python
# Clash 代理配置
CLASH_HOST = "${CLASH_HOST:-localhost}"
CLASH_PORT = "7890"

# SearXNG 配置
SEARXNG_CONTAINER = "searxng"
SEARXNG_URL = "http://${CLASH_HOST:-localhost}:8081"

# 日志配置
LOG_FILE = "/var/log/searxng-proxy-check.log"
LOG_LEVEL = "INFO"

# 检测配置
TIMEOUT = 5  # 代理检测超时（秒）
RESTART_WAIT = 10  # 重启后等待时间（秒）

# 告警配置（可选）
ALERT_WEBHOOK = ""  # Discord/Telegram Webhook
ALERT_ON_CHANGE = True  # 状态变化时告警
```

---

## 📋 依赖要求

### Python 包

**requirements.txt:**
```
requests>=2.28.0
pyyaml>=6.0
```

### 系统要求

- Python 3.8+
- Docker（用于重启 SearXNG）
- SearXNG 容器
- Clash 代理（可选）

---

## 🎯 高级功能

### Webhook 告警

**配置：**
```python
ALERT_WEBHOOK = "https://discord.com/api/webhooks/xxx"
ALERT_ON_CHANGE = True
```

**触发条件：**
- 代理状态变化
- 检测失败
- SearXNG 重启失败

---

### 自定义搜索引擎

**编辑 config.py：**
```python
GLOBAL_ENGINES = ['google', 'duckduckgo', 'wikipedia']
CN_ENGINES = ['baidu', 'bing', 'sogou']
```

---

## 📊 监控指标

### 日志分析

**查看日志：**
```bash
tail -f /var/log/searxng-proxy-check.log
```

**统计代理可用率：**
```bash
grep "✅ 代理可用" /var/log/searxng-proxy-check.log | wc -l
grep "❌ 代理不可用" /var/log/searxng-proxy-check.log | wc -l
```

---

### 性能指标

| 指标 | 目标 | 实际 |
|------|------|------|
| 代理检测时间 | <5 秒 | ~1 秒 |
| 配置更新时间 | <10 秒 | ~5 秒 |
| SearXNG 重启 | <30 秒 | ~8 秒 |
| 总耗时 | <60 秒 | ~15 秒 |

---

## 🛠️ 故障排查

### 问题 1：代理检测失败

**检查：**
```bash
# Clash 容器状态
docker ps | grep clash

# 代理端口
netstat -tlnp | grep 7890

# 手动测试代理
curl --proxy http://${CLASH_HOST:-localhost}:7890 https://www.google.com
```

**解决：**
```bash
# 重启 Clash
docker restart clash

# 检查配置
docker exec clash cat /root/config.yaml
```

---

### 问题 2：SearXNG 重启失败

**检查：**
```bash
# SearXNG 容器状态
docker ps | grep searxng

# 查看日志
docker logs searxng --tail 50
```

**解决：**
```bash
# 手动重启
docker restart searxng

# 检查配置
docker exec searxng cat /etc/searxng/settings.yml
```

---

### 问题 3：搜索无结果

**检查：**
```bash
# 测试 API
curl "http://${CLASH_HOST:-localhost}:8081/search?q=test&format=json"

# 检查引擎状态
docker exec searxng cat /etc/searxng/settings.yml | grep -A3 "name: google"
```

**解决：**
```bash
# 重新运行检测
python3 adapter.py

# 查看检测日志
tail -f /var/log/searxng-proxy-check.log
```

---

## 📈 更新日志

### v2.0.0 (2026-03-11)

- ✨ 新增自适应代理检测
- ✨ 智能切换全球/国内引擎
- ✨ 每小时自动检测
- ✨ 完整日志记录
- ✨ Webhook 告警支持

### v1.0.0 (2026-03-10)

- 🎉 初始版本
- ✅ SearXNG 部署
- ✅ 基础配置

---

## 📞 支持

### 问题反馈

- **GitHub Issues:** https://github.com/pengong101/searxng-auto-proxy/issues
- **Discord:** https://discord.gg/clawd
- **邮箱:** pengong101@gmail.com

### 文档

- [部署指南](docs/DEPLOYMENT.md)
- [配置说明](docs/CONFIGURATION.md)
- [故障排查](docs/TROUBLESHOOTING.md)

---

## 📄 许可

MIT No Attribution (MIT-0) - 详见 [LICENSE](LICENSE)

---

**技能作者：** CTO 智能体 + CEO 智能体（pengong101）  
**公司：** 无人全智能体公司  
**版本：** v2.0.0  
**发布日期：** 2026-03-11
