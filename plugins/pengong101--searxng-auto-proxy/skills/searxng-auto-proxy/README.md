# SearXNG Auto Proxy v2.0.0

**自适应代理检测 - 智能切换全球/国内搜索引擎**

---

## 🎉 新功能

### 自适应代理检测

- 🌐 自动检测 Clash 代理可用性
- 🔄 智能切换全球/国内搜索引擎
- ⏰ 每小时自动检测
- 📝 完整日志记录
- 🔔 故障告警（可选）

---

## 🚀 快速开始

### 安装

```bash
git clone https://github.com/pengong101/searxng-auto-proxy.git
cd searxng-auto-proxy
pip3 install -r requirements.txt
python3 adapter.py
```

### 配置 Cron

```bash
# 每小时检测
0 * * * * /usr/bin/python3 /path/to/adapter.py
```

---

## 📊 工作原理

```
检测 Clash 代理
    ↓
代理可用？
    ├─ 是 → 启用 Google, DuckDuckGo, Wikipedia...
    └─ 否 → 仅用百度，必应中国
    ↓
重启 SearXNG
    ↓
测试搜索
    ↓
记录日志
```

---

## 📋 详细文档

- [部署指南](docs/DEPLOYMENT.md)
- [配置说明](docs/CONFIGURATION.md)
- [故障排查](docs/TROUBLESHOOTING.md)

---

**版本：** v2.0.0  
**发布日期：** 2026-03-11  
**许可：** MIT
