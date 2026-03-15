# 安装前检查清单 (Pre-Installation Checklist)

**基于 ClawHub 安全审查建议 | 2026-03-11**

---

## ⚠️ 在安装或运行此 skill 之前必须检查和执行

### 1️⃣ 确认隧道行为

**问题：** skill 可以创建公网反向 SSH 隧道（serveo.net）。

**检查默认值：**
```bash
# 查看 start.sh 中的默认隧道设置
grep "ENABLE_TUNNEL=\${" start.sh

# 预期结果：应该看到 ":-false"
# ENABLE_TUNNEL="${CLI_ENABLE_TUNNEL:-${ENABLE_TUNNEL:-false}}"
```

**具体行号（start.sh）：**
- **行 24：** 默认值设置
  ```bash
  ENABLE_TUNNEL="${CLI_ENABLE_TUNNEL:-${ENABLE_TUNNEL:-false}}"
  ```
- **行 97-109：** SSH 隧道创建代码
  ```bash
  if [ "$ENABLE_TUNNEL" = "true" ]; then
      ssh -o StrictHostKeyChecking=no \
          -R 80:localhost:3000 \
          serveo.net > "$SERVEO_LOG" 2>&1 &
  fi
  ```

**安全启动方式：**
```bash
# 方式 1：使用环境变量（推荐）
ENABLE_TUNNEL=false ./start.sh

# 方式 2：使用安全脚本
./start-safe.sh

# 方式 3：创建配置文件
echo "ENABLE_TUNNEL=false" > .env
./start.sh
```

**验证隧道状态：**
```bash
# 检查是否有 serveo 进程
ps aux | grep serveo

# 检查隧道日志
cat /tmp/serveo.log

# 如果发现不想要的隧道，立即停止
pkill -f serveo
```

---

### 2️⃣ 在隔离环境中运行

**原因：** start.sh 会运行 `npm install` 并启动后台进程。

#### 选项 A：Docker 容器（最安全）

```bash
# 使用官方 Node 镜像测试
docker run -it --rm \
  -v $(pwd):/app \
  -w /app \
  -p 3000:3000 \
  --name qq-music-test \
  node:18-slim \
  bash

# 在容器内
cd /app
ENABLE_TUNNEL=false ./start.sh

# 在另一个终端测试
curl http://localhost:3000/health

# 完成后清理
docker stop qq-music-test
```

**具体 npm install 行号（start.sh）：**
- **行 48-54：** npm install 调用
  ```bash
  if [ ! -d "$PLAYER_DIR/node_modules" ]; then
      echo "   ⚠️ 依赖未安装，正在安装..."
      cd "$PLAYER_DIR"
      npm install --silent > /dev/null 2>&1
  fi
  ```

#### 选项 B：专用用户账户

```bash
# 创建低权限用户
sudo useradd -m -s /bin/bash qqmusic-test
sudo su - qqmusic-test

# 复制 skill 到用户目录
cp -r /path/to/qq-music-radio ~/

# 在该用户下运行
cd ~/qq-music-radio
ENABLE_TUNNEL=false ./start.sh

# 测试完成后，删除用户
# exit
# sudo userdel -r qqmusic-test
```

#### 选项 C：虚拟机

```bash
# 在 VM 中安装并测试
# 确保 VM 网络隔离
# 监控网络活动
```

---

### 3️⃣ 审查依赖和代码

#### 检查依赖包

```bash
# 查看 package.json
cat player/package.json

# 预期依赖（仅 4 个）：
# - express: ^4.18.2
# - axios: ^1.6.0
# - cors: ^2.8.5
# - dotenv: ^16.3.1

# 查看完整依赖树
cat player/package-lock.json | grep '"resolved":' | head -20

# 检查是否有可疑包
cat player/package-lock.json | grep '"resolved":' | grep -v "registry.npmjs.org"
```

#### 审查服务器代码（server-qqmusic.js）

```bash
# 检查网络端点
echo "=== 网络端点 ==="
grep -n "https\?://" player/server-qqmusic.js

# 预期结果（仅 QQ 音乐 API）：
# - c.y.qq.com
# - u.y.qq.com
# - y.gtimg.cn
# - dl.stream.qqmusic.qq.com

# 检查动态执行
echo "=== 动态执行 ==="
grep -n "eval\|Function(\|exec\|spawn" player/server-qqmusic.js || echo "✅ 无动态执行"

# 检查文件操作
echo "=== 文件操作 ==="
grep -n "writeFile\|unlink\|rmdir" player/server-qqmusic.js || echo "✅ 无文件操作"
```

#### 审查前端代码（app-auto.js）

```bash
# 检查网络请求
echo "=== 前端网络请求 ==="
grep -n "fetch\|XMLHttpRequest" player/public/app-auto.js

# 预期结果（仅本地 API）：
# - /api/radio/list
# - /api/radio/detail
# - /api/song/url

# 检查 XSS 风险
echo "=== XSS 检查 ==="
grep -B3 "innerHTML" player/public/app-auto.js | grep -E "input\.|prompt\(|location\." || echo "✅ 无用户输入注入"
```

#### 自动安全扫描

```bash
# 运行自动扫描脚本
./security-scan.sh

# 预期结果：
# - 0 错误
# - 1 警告（SSH 隧道，已默认禁用）
```

---

### 4️⃣ 谨慎对待 cron/自动重启

**警告：** 文档中的示例会创建持久化定时任务。

**检查是否有定时任务：**
```bash
# 检查当前 cron 任务
crontab -l

# 搜索与 qq-music 相关的任务
crontab -l | grep qq-music
```

**如果需要定时任务，手动添加：**
```bash
# 仅在理解并需要时添加
# 示例：每天重启一次（仅作参考，不要盲目添加）
# 0 3 * * * cd /path/to/qq-music-radio && ./stop.sh && ./start.sh
```

**推荐：** 不使用 cron，手动控制启动和停止。

---

### 5️⃣ 日志和文件

**skill 会写入以下文件：**

| 文件路径 | 内容 | 大小 | 风险 |
|---------|------|------|------|
| `/tmp/qq-music-radio.log` | 服务器日志 | ~100KB | 低（标准日志） |
| `/tmp/serveo.log` | 隧道日志（如果启用） | ~50KB | 低（仅隧道） |
| `/tmp/qq-music-radio-url.txt` | 公网地址（如果启用） | ~100B | 低（临时文件） |

**检查日志内容：**
```bash
# 启动后检查日志
tail -f /tmp/qq-music-radio.log

# 检查是否有异常连接
grep -i "error\|fail\|refused" /tmp/qq-music-radio.log

# 检查隧道日志（如果启用了）
tail -f /tmp/serveo.log
```

**清理日志：**
```bash
# 停止服务后清理
./stop.sh
rm -f /tmp/qq-music-radio*.log /tmp/serveo.log /tmp/qq-music-radio-url.txt
```

**如果 `/tmp` 不可接受：**
```bash
# 修改日志路径（创建 .env）
cat > .env << 'EOF'
ENABLE_TUNNEL=false
LOG_FILE=~/qq-music-radio.log
SERVEO_LOG=~/serveo.log
EOF

./start.sh
```

---

## 🔬 完整的沙盒测试流程（Docker）

### 步骤 1：准备环境

```bash
# 解压 skill
unzip qq-music-radio-v3.3.1-clawhub-final.zip
cd qq-music-radio

# 运行安全扫描
./security-scan.sh
```

### 步骤 2：在 Docker 中测试

```bash
# 启动 Docker 容器
docker run -it --rm \
  --name qq-music-sandbox \
  -v $(pwd):/app \
  -w /app \
  -p 3000:3000 \
  --network bridge \
  node:18-slim \
  bash

# 在容器内执行以下命令
```

**在容器内：**

```bash
# 1. 安装必要工具
apt-get update && apt-get install -y curl procps

# 2. 检查默认配置
grep "ENABLE_TUNNEL=" start.sh | grep ":-"

# 3. 审查代码（可选）
cat player/server-qqmusic.js | less
cat player/package.json

# 4. 启动（本地模式）
ENABLE_TUNNEL=false ./start.sh

# 5. 等待启动（约 10-20 秒）
sleep 15

# 6. 检查进程
ps aux | grep node

# 7. 检查端口
netstat -tuln | grep 3000

# 8. 健康检查
curl http://localhost:3000/health

# 9. 测试 API
curl http://localhost:3000/api/radio/list

# 10. 检查日志
tail -20 /tmp/qq-music-radio.log
```

### 步骤 3：在主机上测试

```bash
# 在另一个终端（主机上）
curl http://localhost:3000/health

# 在浏览器访问
# http://localhost:3000
```

### 步骤 4：清理

```bash
# 在容器内停止
./stop.sh

# 检查进程是否已停止
ps aux | grep node

# 退出容器
exit

# 容器会自动删除（因为 --rm）
```

---

## ✅ 安全检查清单总结

安装前必须完成：

- [ ] **检查隧道默认值** - 确认 `ENABLE_TUNNEL=false`
- [ ] **审查 start.sh 行 24 和 97-109** - 验证隧道代码
- [ ] **审查 player/package.json** - 确认依赖仅 4 个
- [ ] **运行 security-scan.sh** - 自动安全扫描
- [ ] **审查 server-qqmusic.js** - 检查网络端点
- [ ] **在 Docker 中测试** - 隔离环境验证
- [ ] **检查日志位置** - 确认 /tmp 可接受
- [ ] **不添加 cron** - 除非明确需要
- [ ] **创建专用用户** - 不要以 root 运行
- [ ] **监控网络活动** - 确认无异常连接

---

## 🆘 如果发现问题

### 发现不想要的隧道

```bash
# 立即杀死 serveo 进程
pkill -f serveo

# 检查是否还有连接
ps aux | grep serveo

# 修改配置
echo "ENABLE_TUNNEL=false" > .env

# 重启
./stop.sh
./start.sh
```

### 发现异常网络连接

```bash
# 查看所有网络连接
netstat -tuln

# 查看 Node 进程的连接
lsof -p $(pgrep -f "node.*server-qqmusic")

# 如果发现可疑连接，立即停止
./stop.sh
```

### 发现可疑依赖

```bash
# 检查 npm 安装的包
cd player
npm list

# 审查某个包
npm info <package-name>

# 如果不信任，删除并重新审查
rm -rf node_modules
# 不要运行 npm install
```

---

## 📞 需要帮助？

ClawHub 提供的额外帮助选项：

1. **显示具体行号**
   - start.sh 中创建 SSH 隧道的代码
   - npm install 的具体行

2. **Docker 测试命令清单**
   - 一键复制粘贴的完整测试流程

**这个文档已经包含了以上内容！**

---

**结论：** 遵循此检查清单，可以安全地评估和测试这个 skill。如果任何步骤失败或发现可疑行为，立即停止并报告。

**最后更新：** 2026-03-11  
**基于：** ClawHub 安全审查建议  
**版本：** v3.3.1
