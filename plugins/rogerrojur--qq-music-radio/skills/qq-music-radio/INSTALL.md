# 🎵 QQ 音乐播放器 Skill - 安装指南

## 📦 完整独立的 Skill

这个 skill 包含了完整的播放器代码，无需外部依赖！

## 📂 文件结构

```
/projects/.openclaw/skills/qq-music-radio/
├── SKILL.md          # Skill 定义（AI 读取）
├── README.md         # 使用说明
├── INSTALL.md        # 本文件 - 安装指南
├── EXAMPLES.md       # 使用示例
├── SUMMARY.md        # 完成总结
├── start.sh          # 启动脚本 ⭐
├── stop.sh           # 停止脚本
├── get-url.sh        # 获取公网地址
└── player/           # 播放器代码（完整独立）
    ├── package.json          # Node.js 依赖配置
    ├── server-qqmusic.js     # 服务器主文件
    ├── .env                  # 环境配置（空文件）
    └── public/               # 前端文件
        ├── index.html        # 主页面
        ├── app-auto.js       # 播放器脚本
        └── test.html         # 测试页面
```

## 🚀 快速安装

### 方式 1：从零开始（推荐）

如果你是第一次安装这个 skill：

```bash
# 1. 确认 skill 目录存在
ls -la /projects/.openclaw/skills/qq-music-radio/

# 2. 安装依赖（首次运行会自动安装）
/projects/.openclaw/skills/qq-music-radio/start.sh
```

**就这么简单！** 首次运行 `start.sh` 会自动：
- ✅ 检查并安装 npm 依赖
- ✅ 启动服务器
- ✅ 创建公网隧道
- ✅ 返回访问地址

### 方式 2：手动安装依赖

如果你想手动安装依赖：

```bash
cd /projects/.openclaw/skills/qq-music-radio/player
npm install
```

依赖包括：
- `express` - Web 服务器框架
- `axios` - HTTP 客户端
- `cors` - 跨域支持
- `dotenv` - 环境变量管理

## ✅ 验证安装

### 1. 检查文件结构

```bash
ls -lh /projects/.openclaw/skills/qq-music-radio/
ls -lh /projects/.openclaw/skills/qq-music-radio/player/
```

应该看到：
- ✅ Shell 脚本（start.sh、stop.sh、get-url.sh）
- ✅ 文档文件（SKILL.md、README.md 等）
- ✅ player/ 目录
- ✅ player/public/ 目录

### 2. 测试启动

```bash
/projects/.openclaw/skills/qq-music-radio/start.sh
```

应该看到：
```
🎵 QQ 音乐播放器启动脚本
==========================

0️⃣ 检查依赖...
   ✅ 依赖已存在（或正在安装...）

1️⃣ 检查服务器状态...
   ✅ 服务器已启动，PID: xxxxx

2️⃣ 检查公网隧道...
   ✅ 隧道已创建，PID: xxxxx
   ✅ 公网地址: https://xxx.serveousercontent.com

==========================
✅ QQ 音乐播放器已就绪！
```

### 3. 访问播放器

```bash
# 获取公网地址
/projects/.openclaw/skills/qq-music-radio/get-url.sh

# 或直接访问本地
curl http://localhost:3000/health
```

## 🎯 使用方式

### 对话触发（推荐）

直接对 AI 说：
- "打开音乐播放器"
- "我想听歌"
- "播放音乐"

AI 会自动：
1. 读取 SKILL.md
2. 执行 start.sh
3. 返回访问地址

### 命令行使用

```bash
# 启动
/projects/.openclaw/skills/qq-music-radio/start.sh

# 获取地址
/projects/.openclaw/skills/qq-music-radio/get-url.sh

# 停止
/projects/.openclaw/skills/qq-music-radio/stop.sh
```

## 📋 系统要求

### 必需
- ✅ Linux 系统（或支持 bash 的系统）
- ✅ Node.js（v14 或更高）
- ✅ npm
- ✅ curl
- ✅ ssh
- ✅ 互联网连接

### 可选
- OpenClaw Gateway（用于对话触发）
- Canvas 支持（用于直接展示）

## 🔧 配置说明

### 端口配置

默认使用 3000 端口。如需修改：

编辑 `player/server-qqmusic.js`：
```javascript
const PORT = process.env.PORT || 3000;
```

或设置环境变量：
```bash
export PORT=8080
/projects/.openclaw/skills/qq-music-radio/start.sh
```

### 环境变量

`player/.env` 文件（可选配置）：
```bash
# 端口号（默认 3000）
PORT=3000

# QQ 音乐 Token（可选，暂不支持）
# TOKEN=your_token_here
```

## 🐛 故障排除

### 依赖安装失败

```bash
cd /projects/.openclaw/skills/qq-music-radio/player
rm -rf node_modules package-lock.json
npm install
```

### 端口被占用

```bash
# 查看占用进程
lsof -i :3000

# 杀死进程
kill -9 <PID>

# 或使用其他端口
PORT=8080 /projects/.openclaw/skills/qq-music-radio/start.sh
```

### 隧道无法建立

```bash
# 检查 SSH 连接
ssh -T serveo.net

# 查看隧道日志
tail -f /tmp/serveo.log

# 重启隧道
/projects/.openclaw/skills/qq-music-radio/stop.sh
/projects/.openclaw/skills/qq-music-radio/start.sh
```

### 服务器无响应

```bash
# 查看服务器日志
tail -f /tmp/qq-music-radio.log

# 重启服务器
/projects/.openclaw/skills/qq-music-radio/stop.sh
/projects/.openclaw/skills/qq-music-radio/start.sh
```

## 📦 分享 Skill

### 方式 1：打包整个目录

```bash
cd /projects/.openclaw/skills/
tar -czf qq-music-radio.tar.gz qq-music-radio/
```

发送 `qq-music-radio.tar.gz` 给其他人。

### 方式 2：Git 仓库（推荐）

```bash
cd /projects/.openclaw/skills/qq-music-radio/
git init
git add .
git commit -m "QQ Music Radio Player Skill"
git remote add origin <your-repo-url>
git push -u origin main
```

其他人可以：
```bash
cd /projects/.openclaw/skills/
git clone <your-repo-url> qq-music-radio
cd qq-music-radio
./start.sh
```

## 🔄 更新 Skill

### 更新代码

如果有新版本：

```bash
cd /projects/.openclaw/skills/qq-music-radio/

# 停止旧版本
./stop.sh

# 更新文件（根据你的更新方式）
# 例如：git pull 或解压新版本

# 重新安装依赖（如果需要）
cd player
rm -rf node_modules
npm install

# 启动新版本
cd ..
./start.sh
```

## 📊 监控和维护

### 检查运行状态

```bash
# 检查服务器
pgrep -f "node.*server-qqmusic.js"

# 检查隧道
pgrep -f "ssh.*serveo.net"

# 健康检查
curl http://localhost:3000/health
```

### 查看日志

```bash
# 服务器日志
tail -f /tmp/qq-music-radio.log

# 隧道日志
tail -f /tmp/serveo.log

# 实时监控
watch -n 1 'pgrep -f "node.*server-qqmusic.js" && pgrep -f "ssh.*serveo.net"'
```

### 定期重启（可选）

如果需要定期重启保持稳定：

```bash
# 添加到 crontab
crontab -e

# 每天凌晨 4 点重启
0 4 * * * /projects/.openclaw/skills/qq-music-radio/stop.sh && sleep 5 && /projects/.openclaw/skills/qq-music-radio/start.sh
```

## 🎉 安装完成

现在你可以：

1. ✅ 对 AI 说"打开音乐播放器"
2. ✅ 或运行 `./start.sh`
3. ✅ 访问返回的地址
4. ✅ 享受音乐！🎵

---

**需要帮助？**
- 查看 `README.md` - 使用说明
- 查看 `EXAMPLES.md` - 使用示例
- 查看日志文件 - 故障排查

---

> 版本：v3.1  
> 最后更新：2026-03-11  
> 完全独立，开箱即用！
