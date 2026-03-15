# 安全检查清单 (Security Checklist)

## ⚠️ 安装前必读

ClawHub 安全审查发现了一些需要注意的风险点，请在安装前仔细阅读。

## 🔍 已识别的风险点

### 1. **默认公网暴露** ⚠️ 高优先级

**问题：**
- `start.sh` 默认 `ENABLE_TUNNEL=true`
- 会自动创建 SSH 反向隧道到 serveo.net
- 本地端口 3000 会暴露到互联网

**解决方案：**
```bash
# 方法 1: 使用环境变量
ENABLE_TUNNEL=false ./start.sh

# 方法 2: 使用安全版本脚本
./start-safe.sh

# 方法 3: 创建配置文件
echo "ENABLE_TUNNEL=false" > .env
./start.sh
```

**推荐：** 首次安装时使用 `start-safe.sh` 或设置 `ENABLE_TUNNEL=false`

---

### 2. **未声明的运行时依赖** ⚠️ 中优先级

**需要的系统工具：**
- `node` (v14+) - Node.js 运行时
- `npm` - 包管理器
- `ssh` - 用于创建隧道（仅当 `ENABLE_TUNNEL=true` 时）
- `curl` - 健康检查
- `pgrep`/`lsof` - 进程管理
- `/tmp` 写权限 - 日志文件

**检查方法：**
```bash
# 检查所需工具
command -v node && echo "✅ node" || echo "❌ node 未安装"
command -v npm && echo "✅ npm" || echo "❌ npm 未安装"
command -v ssh && echo "✅ ssh" || echo "❌ ssh 未安装"
command -v curl && echo "✅ curl" || echo "❌ curl 未安装"
command -v pgrep && echo "✅ pgrep" || echo "❌ pgrep 未安装"

# 检查写权限
touch /tmp/test && rm /tmp/test && echo "✅ /tmp 可写" || echo "❌ /tmp 无写权限"
```

---

### 3. **自动网络下载** ⚠️ 中优先级

**首次运行时会：**
- 执行 `npm install` 下载依赖
- 从 npm 或镜像获取包（见 `player/package-lock.json`）

**依赖列表：**
```json
{
  "express": "^4.18.2",    // Web 框架
  "axios": "^1.6.0",       // HTTP 客户端
  "cors": "^2.8.5",        // CORS 中间件
  "dotenv": "^16.3.1"      // 环境变量
}
```

**检查方法：**
```bash
# 审查依赖
cat player/package.json
cat player/package-lock.json | grep "resolved" | head -20

# 手动安装依赖（可选）
cd player
npm install --dry-run  # 预览安装
npm install            # 实际安装
```

---

### 4. **持久化自动任务** ⚠️ 低优先级

**skill 文档中提到：**
- 创建 cron 定时任务
- 自动重启服务

**注意：**
- 仅在你明确需要时创建定时任务
- 不要自动运行未审查的定时脚本

---

## ✅ 推荐的安装步骤

### 步骤 1: 审查源代码

**必须检查的文件：**

1. **`player/server-qqmusic.js`** (服务器核心)
   ```bash
   # 检查网络端点
   grep -n "axios\|http\|https" player/server-qqmusic.js
   
   # 检查动态执行
   grep -n "eval\|exec\|Function(" player/server-qqmusic.js
   
   # 检查文件操作
   grep -n "writeFile\|unlink\|rm" player/server-qqmusic.js
   ```

2. **`player/public/app-auto.js`** (前端逻辑)
   ```bash
   # 检查网络请求
   grep -n "fetch\|XMLHttpRequest\|axios" player/public/app-auto.js
   
   # 检查动态代码
   grep -n "eval\|innerHTML\|document.write" player/public/app-auto.js
   ```

3. **`start.sh`** (启动脚本)
   ```bash
   # 检查 SSH 隧道命令
   grep -n "ssh.*serveo" start.sh
   
   # 检查后台进程
   grep -n "nohup\|&" start.sh
   ```

**预期结果：**
- ✅ 无 `eval()` 或动态代码执行
- ✅ 网络请求仅限于 QQ 音乐 API 和 serveo.net
- ✅ 无文件系统破坏性操作
- ✅ 无混淆或加密代码

---

### 步骤 2: 隔离环境测试（推荐）

如果不确定，在隔离环境中运行：

**选项 A: Docker 容器**
```bash
docker run -it --rm -v $(pwd):/skill node:18 bash
cd /skill
ENABLE_TUNNEL=false ./start.sh
```

**选项 B: 虚拟机**
- 在 VM 中安装并测试
- 验证无异常网络活动

**选项 C: 沙盒环境**
- 使用 firejail 或其他沙盒工具

---

### 步骤 3: 本地测试

**首次运行使用安全模式：**
```bash
# 方法 1: 使用 start-safe.sh
./start-safe.sh

# 方法 2: 禁用隧道
ENABLE_TUNNEL=false ./start.sh

# 方法 3: 配置文件
echo "ENABLE_TUNNEL=false" > .env
./start.sh
```

**验证运行：**
```bash
# 检查进程
ps aux | grep "node.*server-qqmusic"

# 检查端口
lsof -i :3000

# 测试访问
curl http://localhost:3000/health

# 检查日志
tail -f /tmp/qq-music-radio.log
```

---

### 步骤 4: 监控（如果启用公网隧道）

**如果需要公网访问，监控以下内容：**

```bash
# 1. 检查隧道日志
tail -f /tmp/serveo.log

# 2. 检查公网地址
cat /tmp/qq-music-radio-url.txt

# 3. 监控网络连接
netstat -tuln | grep 3000

# 4. 查看访问日志
tail -f /tmp/qq-music-radio.log
```

---

## 📋 文件审查清单

### 必须审查的文件

- [ ] `player/server-qqmusic.js` - 服务器代码
- [ ] `player/public/app-auto.js` - 前端逻辑
- [ ] `player/public/index.html` - 前端页面
- [ ] `start.sh` - 启动脚本
- [ ] `stop.sh` - 停止脚本
- [ ] `player/package.json` - 依赖清单

### 关键检查点

#### `server-qqmusic.js` 检查
- [ ] 无 `eval()` 或 `Function()` 动态执行
- [ ] 网络请求仅限于预期端点
- [ ] 无文件系统写入（除日志）
- [ ] 无 child_process.exec()
- [ ] 端口绑定仅 3000

#### `app-auto.js` 检查
- [ ] 无 `eval()` 或 `innerHTML` 注入
- [ ] AJAX 请求仅到本地服务器
- [ ] 无 WebSocket 或 SSE 连接到外部
- [ ] 无 localStorage 敏感数据

#### `start.sh` 检查
- [ ] SSH 命令仅在 ENABLE_TUNNEL=true 时执行
- [ ] 日志路径为 /tmp（非敏感位置）
- [ ] 无 rm -rf 或破坏性命令
- [ ] 进程管理仅限当前 skill

---

## 🛡️ 安全建议

### 最小权限原则

1. **不要以 root 运行**
   ```bash
   # 创建专用用户
   sudo useradd -m -s /bin/bash qqmusic
   sudo su - qqmusic
   ```

2. **限制端口范围**
   - 使用高端口（如 8080）代替 3000
   - 配置防火墙规则

3. **网络隔离**
   - 如果可能，在独立 VLAN 运行
   - 使用反向代理（nginx/caddy）代替直接暴露

---

### 防火墙配置（如果启用公网）

```bash
# 仅允许本地访问 3000 端口
sudo ufw deny 3000
sudo ufw allow from 127.0.0.1 to any port 3000

# 或使用 iptables
sudo iptables -A INPUT -p tcp --dport 3000 -i lo -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 3000 -j DROP
```

---

## 🔍 自动扫描脚本

可以运行以下脚本自动检查可疑模式：

```bash
#!/bin/bash
echo "🔍 扫描可疑模式..."

# 检查 eval
echo "1. 检查 eval()..."
grep -rn "eval(" player/ && echo "⚠️ 发现 eval" || echo "✅ 无 eval"

# 检查动态执行
echo "2. 检查动态执行..."
grep -rn "Function(.*)" player/ && echo "⚠️ 发现 Function" || echo "✅ 无 Function"

# 检查外部连接
echo "3. 检查网络端点..."
grep -rn "http:/\|https:/" player/server-qqmusic.js | grep -v "qq.com\|gtimg.cn"

# 检查文件操作
echo "4. 检查文件操作..."
grep -rn "unlink\|rmdir\|rm -" . && echo "⚠️ 发现文件删除" || echo "✅ 无危险文件操作"

echo ""
echo "✅ 扫描完成"
```

---

## 📞 需要帮助？

如果你希望我：
- ✅ 扫描 `server-qqmusic.js` 和前端文件
- ✅ 提供具体文件/行号的检查清单
- ✅ 创建自动安全扫描脚本
- ✅ 生成隔离环境测试指南

请随时联系！

---

## ⚠️ 免责声明

- 本 skill 使用非官方 QQ 音乐 API，可能随时失效
- 音乐内容版权归 QQ 音乐所有
- 仅供学习和个人使用
- 作者不对任何安全风险负责

**使用前请充分理解风险并采取适当的安全措施。**

---

**文档版本：** 1.0  
**更新时间：** 2026-03-11  
**基于 ClawHub 安全审查建议**
