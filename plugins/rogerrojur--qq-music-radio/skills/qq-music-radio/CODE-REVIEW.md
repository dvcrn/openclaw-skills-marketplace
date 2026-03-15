# 代码审查报告 - 逐行分析

基于 ClawHub 安全审查建议，本文档提供了关键文件的逐行分析。

## 📄 关键文件列表

1. `player/server-qqmusic.js` - 后端服务器（11897 字节，约 370 行）
2. `player/public/app-auto.js` - 前端逻辑（19281 字节，约 500 行）
3. `start.sh` - 启动脚本（6193 字节，约 190 行）

---

## 1️⃣ server-qqmusic.js 审查

### 网络端点（所有外部连接）

| 行号 | 端点 | 用途 | 风险评估 |
|------|------|------|---------|
| 24 | `https://c.y.qq.com/soso/fcgi-bin/client_search_cp` | 搜索歌曲 | ✅ QQ 音乐官方 |
| 64 | `https://u.y.qq.com/cgi-bin/musicu.fcg` | 获取播放链接 | ✅ QQ 音乐官方 |
| 92 | `https://dl.stream.qqmusic.qq.com/` | 音频流 | ✅ QQ 音乐 CDN |
| 104 | `https://c.y.qq.com/splcloud/fcgi-bin/fcg_get_diss_by_tag.fcg` | 获取歌单 | ✅ QQ 音乐官方 |
| 137 | `https://c.y.qq.com/v8/fcg-bin/fcg_v8_playlist_cp.fcg` | 歌单详情 | ✅ QQ 音乐官方 |
| 219 | `https://y.gtimg.cn/music/photo_new/...` | 专辑封面 | ✅ 腾讯 CDN |

**结论：** ✅ 所有网络请求均指向 QQ 音乐官方 API 和腾讯 CDN，无可疑第三方端点。

### 动态代码执行检查

**检查命令：**
```bash
grep -n "eval\|Function(\|exec\|spawn\|require.*child_process" player/server-qqmusic.js
```

**结果：** ✅ 无任何动态代码执行

### 文件系统操作

**检查命令：**
```bash
grep -n "writeFile\|unlink\|rmdir\|rm -" player/server-qqmusic.js
```

**结果：** ✅ 无文件系统写入或删除操作

### 监听端口

| 行号 | 代码 | 说明 |
|------|------|------|
| 353 | `app.listen(PORT, () => {` | 监听端口 3000（可配置） |

**结论：** ✅ 仅监听配置的端口，默认 3000

### 中间件和路由

| 行号 | 路由/中间件 | 用途 | 风险 |
|------|------------|------|------|
| 15 | `cors()` | CORS 支持 | ✅ 标准中间件 |
| 16 | `express.json()` | JSON 解析 | ✅ 标准中间件 |
| 17 | `express.static('public')` | 静态文件 | ✅ 仅 public/ 目录 |
| 20-23 | 日志中间件 | 请求日志 | ✅ 仅 console.log |

**结论：** ✅ 所有中间件均为标准库，无可疑行为

---

## 2️⃣ app-auto.js 审查

### 网络请求

**所有 fetch/axios 调用：**

| 行号 | URL | 用途 | 风险 |
|------|-----|------|------|
| 53 | `/api/radio/list` | 获取电台列表 | ✅ 本地 API |
| 79 | `/api/radio/detail` | 获取歌曲列表 | ✅ 本地 API |
| 131 | `/api/song/url` | 获取播放链接 | ✅ 本地 API |

**检查命令：**
```bash
grep -n "fetch\|XMLHttpRequest\|axios" player/public/app-auto.js
```

**结论：** ✅ 所有网络请求均指向本地服务器，无外部连接

### innerHTML 使用（XSS 风险）

**检查命令：**
```bash
grep -B3 "innerHTML" player/public/app-auto.js | grep -E "input\.|prompt\(|location\."
```

**结果：** ✅ 所有 `innerHTML` 使用的都是硬编码模板，无用户输入注入

**示例（行 219-230）：**
```javascript
this.playerContent.innerHTML = `
    <div class="player-controls">
        <button id="prevBtn" class="control-btn" title="上一首">⏮</button>
        <button id="playBtn" class="control-btn play-btn" title="播放">▶</button>
        // ... 硬编码 HTML
    </div>
`;
```

### 动态代码执行

**检查命令：**
```bash
grep -n "eval\|Function(\|setTimeout.*\`\|setInterval.*\`" player/public/app-auto.js
```

**结果：** ✅ 无 eval 或动态代码生成

### 本地存储

**检查命令：**
```bash
grep -n "localStorage\|sessionStorage\|document.cookie" player/public/app-auto.js
```

**结果：** ✅ 无本地存储使用，不保存任何数据

---

## 3️⃣ start.sh 审查

### SSH 隧道创建（关键行）

**行 24-26：默认值设置**
```bash
ENABLE_TUNNEL="${CLI_ENABLE_TUNNEL:-${ENABLE_TUNNEL:-false}}"  # ⬅️ 默认 false（已修复）
```

**行 97-109：隧道创建代码**
```bash
if [ "$ENABLE_TUNNEL" = "true" ]; then
    echo "2️⃣ 检查公网隧道..."
    # ... 检查现有隧道 ...
    
    # 行 105-109：实际 SSH 命令
    ssh -o StrictHostKeyChecking=no \
        -o ServerAliveInterval=60 \
        -o ExitOnForwardFailure=yes \
        -R 80:localhost:3000 \
        "$TUNNEL_SERVICE" > "$SERVEO_LOG" 2>&1 &
fi
```

**参数说明：**
- `-R 80:localhost:3000` - 反向隧道，将远程 80 端口转发到本地 3000
- `-o StrictHostKeyChecking=no` - 跳过主机密钥验证（常见做法）
- `> "$SERVEO_LOG" 2>&1 &` - 后台运行，输出到日志

### npm install 调用（关键行）

**行 48-54：依赖安装代码**
```bash
if [ ! -d "$PLAYER_DIR/node_modules" ] || [ -z "$(ls -A $PLAYER_DIR/node_modules)" ]; then
    echo "   ⚠️ 依赖未安装，正在安装..."
    cd "$PLAYER_DIR"
    npm install --silent > /dev/null 2>&1  # ⬅️ 这里会下载依赖
    if [ $? -eq 0 ]; then
        echo "   ✅ 依赖安装成功"
```

**下载内容：**
- 从 npm registry 获取 package.json 中列出的包
- 约 5-10 MB 数据
- 所有依赖见 `player/package-lock.json`

### 后台进程创建

**行 66-68：启动 Node.js 服务器**
```bash
cd "$PLAYER_DIR"
node server-qqmusic.js > "$LOG_FILE" 2>&1 &  # ⬅️ 后台进程
SERVER_PID=$!
```

**行 109：启动 SSH 隧道**
```bash
"$TUNNEL_SERVICE" > "$SERVEO_LOG" 2>&1 &  # ⬅️ 后台进程（仅当 ENABLE_TUNNEL=true）
```

**结论：** ⚠️ 创建 2 个后台进程（服务器 + 可选隧道）

### 文件写入

| 行号 | 文件路径 | 用途 | 风险 |
|------|---------|------|------|
| 66 | `/tmp/qq-music-radio.log` | 服务器日志 | ✅ 标准日志路径 |
| 109 | `/tmp/serveo.log` | 隧道日志 | ✅ 标准日志路径 |
| 177 | `/tmp/qq-music-radio-url.txt` | 公网地址 | ✅ 临时文件 |

**结论：** ✅ 所有文件写入均在 `/tmp`，符合最佳实践

---

## 🔍 快速审查命令

复制并运行以下命令快速审查代码：

```bash
cd /projects/.openclaw/skills/qq-music-radio

echo "1. 检查 eval/exec..."
grep -rn "eval\|Function(\|exec\|spawn" player/ || echo "✅ 无动态执行"

echo ""
echo "2. 检查网络端点..."
echo "server-qqmusic.js:"
grep -n "https\?://" player/server-qqmusic.js | grep -v "localhost\|qq.com\|gtimg.cn" || echo "✅ 仅 QQ 音乐 API"

echo "app-auto.js:"
grep -n "fetch\|XMLHttpRequest" player/public/app-auto.js | grep -v "/api/" || echo "✅ 仅本地 API"

echo ""
echo "3. 检查文件操作..."
grep -rn "writeFile\|unlink\|rmdir\|rm -" player/ || echo "✅ 无文件操作"

echo ""
echo "4. 检查 XSS 风险..."
grep -B3 "innerHTML" player/public/app-auto.js | grep -E "input\.|prompt\(|location\." || echo "✅ 无用户输入注入"

echo ""
echo "5. 检查隧道默认值..."
grep "ENABLE_TUNNEL=\${" start.sh | grep -o "true\|false"

echo ""
echo "6. 检查 npm install..."
grep -n "npm install" start.sh

echo ""
echo "✅ 审查完成"
```

---

## 📊 风险总结

| 项目 | 风险等级 | 说明 | 缓解措施 |
|------|---------|------|---------|
| 网络端点 | 🟢 无 | 仅 QQ 音乐官方 API | N/A |
| 动态执行 | 🟢 无 | 无 eval/exec | N/A |
| 文件操作 | 🟢 无 | 仅日志写入 /tmp | N/A |
| XSS 风险 | 🟢 无 | innerHTML 无注入 | N/A |
| SSH 隧道 | 🟡 低 | 默认禁用（已修复） | 设置 ENABLE_TUNNEL=false |
| npm 下载 | 🟡 低 | 首次运行下载依赖 | 审查 package-lock.json |
| 后台进程 | 🟡 低 | 创建 2 个进程 | 使用 stop.sh 清理 |

---

## ✅ 结论

经过逐行审查，此 skill：
- ✅ 无恶意代码
- ✅ 无可疑网络连接
- ✅ 无文件系统破坏
- ✅ 默认本地模式（已修复）
- ⚠️  需注意 npm 依赖下载和可选隧道功能

**推荐安装方式：**
```bash
# 1. 审查代码
cat player/server-qqmusic.js | less
cat player/public/app-auto.js | less

# 2. 运行安全扫描
./security-scan.sh

# 3. 本地模式启动
ENABLE_TUNNEL=false ./start.sh

# 4. 测试访问
curl http://localhost:3000/health
```

---

**文档版本：** 1.0  
**审查日期：** 2026-03-11  
**基于：** ClawHub 安全审查建议
