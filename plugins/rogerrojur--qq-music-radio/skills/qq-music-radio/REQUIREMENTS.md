# QQ 音乐电台播放器 - 系统要求

## 📋 运行时依赖

在运行此 skill 之前，请确保系统已安装以下工具：

### 必需工具

| 工具 | 版本要求 | 用途 | 检查命令 |
|------|---------|------|---------|
| **node** | >= 14.0.0 | Node.js 运行时 | `node --version` |
| **npm** | >= 6.0.0 | 包管理器 | `npm --version` |
| **curl** | 任意版本 | 健康检查 | `curl --version` |
| **pgrep** 或 **lsof** | 任意版本 | 进程管理 | `pgrep --version` 或 `lsof -v` |

### 可选工具（仅公网访问时需要）

| 工具 | 用途 | 检查命令 |
|------|------|---------|
| **ssh** | 创建 serveo.net 隧道 | `ssh -V` |

### 系统权限

- ✅ `/tmp` 目录写权限（用于日志文件）
- ✅ 端口 3000 监听权限
- ❌ **不需要** root 权限
- ❌ **不需要** sudo 权限

## 🔍 安装检查

运行以下脚本检查所有依赖：

```bash
#!/bin/bash
echo "🔍 检查系统依赖..."
echo ""

# 必需工具
echo "必需工具："
command -v node >/dev/null 2>&1 && echo "  ✅ node $(node --version)" || echo "  ❌ node 未安装"
command -v npm >/dev/null 2>&1 && echo "  ✅ npm $(npm --version)" || echo "  ❌ npm 未安装"
command -v curl >/dev/null 2>&1 && echo "  ✅ curl" || echo "  ❌ curl 未安装"
command -v pgrep >/dev/null 2>&1 && echo "  ✅ pgrep" || command -v lsof >/dev/null 2>&1 && echo "  ✅ lsof" || echo "  ❌ pgrep/lsof 未安装"

echo ""
echo "可选工具（公网访问）："
command -v ssh >/dev/null 2>&1 && echo "  ✅ ssh" || echo "  ⚠️  ssh 未安装（仅本地访问时可忽略）"

echo ""
echo "系统权限："
touch /tmp/test 2>/dev/null && rm /tmp/test && echo "  ✅ /tmp 可写" || echo "  ❌ /tmp 无写权限"

echo ""
echo "检查完成！"
```

## 🐧 不同系统的安装方法

### Ubuntu / Debian
```bash
sudo apt update
sudo apt install -y nodejs npm curl
```

### CentOS / RHEL
```bash
sudo yum install -y nodejs npm curl
```

### macOS
```bash
brew install node
```

### Arch Linux
```bash
sudo pacman -S nodejs npm curl
```

## 🐳 Docker 环境（推荐）

如果你想在隔离环境中运行，使用 Docker：

### 使用官方 Node 镜像
```bash
# 直接运行（本地模式）
docker run -it --rm \
  -v $(pwd):/app \
  -w /app \
  -p 3000:3000 \
  node:18 \
  bash -c "ENABLE_TUNNEL=false ./start.sh"

# 或进入容器交互式测试
docker run -it --rm \
  -v $(pwd):/app \
  -w /app \
  -p 3000:3000 \
  node:18 \
  bash

# 然后在容器内
cd /app
ENABLE_TUNNEL=false ./start.sh
```

### 创建自定义镜像（可选）

如果需要，可以创建 Dockerfile：

```dockerfile
# Dockerfile 内容
FROM node:18-slim

# 安装系统工具
RUN apt-get update && apt-get install -y \
    curl procps && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app/

# 暴露端口
EXPOSE 3000

# 默认本地模式
ENV ENABLE_TUNNEL=false

CMD ["./start.sh"]
```

然后构建和运行：
```bash
docker build -t qq-music-radio .
docker run -p 3000:3000 qq-music-radio
```

## ⚠️ 网络下载

首次运行时，`npm install` 会从以下来源下载依赖：

- **官方 npm registry:** https://registry.npmjs.org
- **或镜像:** 如果配置了 npm 镜像（如淘宝镜像）

**下载的包：**
- express@^4.18.2 (约 200KB)
- axios@^1.6.0 (约 150KB)
- cors@^2.8.5 (约 20KB)
- dotenv@^16.3.1 (约 30KB)

**总下载大小：** 约 5-10 MB（含依赖的依赖）

**检查依赖来源：**
```bash
cd player
npm config get registry
cat package-lock.json | grep "resolved" | head -10
```

## 🚫 不需要的特权

此 skill **不需要**：
- ❌ root / sudo 权限
- ❌ 修改系统文件
- ❌ 安装系统服务
- ❌ 监听特权端口（< 1024）
- ❌ 访问敏感目录（/etc, /home 等）

## 🔒 推荐安全实践

1. **专用用户运行**
   ```bash
   # 创建专用用户
   sudo useradd -m -s /bin/bash qqmusic
   sudo su - qqmusic
   
   # 在该用户下安装和运行
   cd ~/.openclaw/skills/qq-music-radio
   ENABLE_TUNNEL=false ./start.sh
   ```

2. **防火墙规则**
   ```bash
   # 仅允许本地访问端口 3000
   sudo ufw deny 3000
   sudo ufw allow from 127.0.0.1 to any port 3000
   ```

3. **限制资源**
   ```bash
   # 使用 systemd 限制资源（可选）
   systemd-run --user --scope \
     -p MemoryLimit=500M \
     -p CPUQuota=50% \
     ENABLE_TUNNEL=false ./start.sh
   ```

---

**总结：** 此 skill 是一个标准的 Node.js Web 应用，不需要特殊权限，遵循"最小权限原则"。
