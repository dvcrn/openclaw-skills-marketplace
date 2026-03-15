# 关键代码行号速查 (Quick Line Reference)

## start.sh 关键行

### 默认隧道设置
**行 24：**
```bash
ENABLE_TUNNEL="${CLI_ENABLE_TUNNEL:-${ENABLE_TUNNEL:-false}}"  # 默认 false
```

### SSH 隧道创建
**行 97-109：**
```bash
if [ "$ENABLE_TUNNEL" = "true" ]; then
    echo "2️⃣ 检查公网隧道..."
    
    # 检查现有隧道
    if pgrep -f "ssh.*serveo.net" > /dev/null; then
        echo "   ⚠️ 检测到已有 serveo 隧道进程"
    fi
    
    # 创建隧道
    echo "   正在创建公网隧道..."
    ssh -o StrictHostKeyChecking=no \
        -o ServerAliveInterval=60 \
        -o ExitOnForwardFailure=yes \
        -R 80:localhost:3000 \
        "$TUNNEL_SERVICE" > "$SERVEO_LOG" 2>&1 &
    
    TUNNEL_PID=$!
fi
```

### npm install 调用
**行 48-54：**
```bash
if [ ! -d "$PLAYER_DIR/node_modules" ] || [ -z "$(ls -A $PLAYER_DIR/node_modules)" ]; then
    echo "   ⚠️ 依赖未安装，正在安装..."
    cd "$PLAYER_DIR"
    npm install --silent > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo "   ✅ 依赖安装成功"
```

### 后台进程启动
**行 66-68：**
```bash
cd "$PLAYER_DIR"
node server-qqmusic.js > "$LOG_FILE" 2>&1 &
SERVER_PID=$!
```

---

## server-qqmusic.js 网络端点

### QQ 音乐搜索 API
**行 24：**
```javascript
const response = await axios.get('https://c.y.qq.com/soso/fcgi-bin/client_search_cp', {
```

### 获取播放链接
**行 64：**
```javascript
const response = await axios.get('https://u.y.qq.com/cgi-bin/musicu.fcg', {
```

### 获取歌单列表
**行 104：**
```javascript
const response = await axios.get('https://c.y.qq.com/splcloud/fcgi-bin/fcg_get_diss_by_tag.fcg', {
```

### 获取歌单详情
**行 137：**
```javascript
const response = await axios.get('https://c.y.qq.com/v8/fcg-bin/fcg_v8_playlist_cp.fcg', {
```

### 专辑封面 CDN
**行 219：**
```javascript
albumPic: `https://y.gtimg.cn/music/photo_new/T002R300x300M000${song.album.mid}.jpg`,
```

### 音频流 URL
**行 92：**
```javascript
return `https://dl.stream.qqmusic.qq.com/${purl}`;
```

---

## app-auto.js 前端请求

### 获取电台列表
**行 53：**
```javascript
const response = await fetch('/api/radio/list');
```

### 获取歌曲列表
**行 79：**
```javascript
const response = await fetch('/api/radio/detail', {
```

### 获取播放链接
**行 131：**
```javascript
const url = await fetch('/api/song/url', {
```

---

## 快速验证命令

```bash
# 1. 检查隧道默认值（应该是 false）
sed -n '24p' start.sh

# 2. 查看隧道创建代码
sed -n '97,109p' start.sh

# 3. 查看 npm install 代码
sed -n '48,54p' start.sh

# 4. 检查所有网络端点
grep -n "https://" player/server-qqmusic.js

# 5. 检查前端请求
grep -n "fetch(" player/public/app-auto.js
```

---

## Docker 一键测试命令

```bash
# 复制粘贴执行（完整测试流程）
docker run -it --rm \
  --name qq-music-sandbox \
  -v $(pwd):/app \
  -w /app \
  -p 3000:3000 \
  node:18-slim \
  bash -c '
    apt-get update -qq && apt-get install -y -qq curl procps &&
    echo "=== 检查默认配置 ===" &&
    grep "ENABLE_TUNNEL=" start.sh | grep ":-" &&
    echo "" &&
    echo "=== 审查依赖 ===" &&
    cat player/package.json | grep -A10 "dependencies" &&
    echo "" &&
    echo "=== 启动服务器（本地模式） ===" &&
    ENABLE_TUNNEL=false ./start.sh &&
    sleep 15 &&
    echo "" &&
    echo "=== 健康检查 ===" &&
    curl -s http://localhost:3000/health &&
    echo "" &&
    echo "" &&
    echo "=== 进程列表 ===" &&
    ps aux | grep node | grep -v grep &&
    echo "" &&
    echo "=== 端口监听 ===" &&
    netstat -tuln | grep 3000 &&
    echo "" &&
    echo "=== 日志（最后 10 行） ===" &&
    tail -10 /tmp/qq-music-radio.log &&
    echo "" &&
    echo "✅ 测试完成！按 Ctrl+C 停止服务器"
  '
```

---

**用法：**
1. 解压 skill 到当前目录
2. 运行上面的 Docker 命令
3. 观察输出，确认：
   - ✅ 默认配置是 `ENABLE_TUNNEL=false`
   - ✅ 依赖仅 4 个（express, axios, cors, dotenv）
   - ✅ 健康检查返回成功
   - ✅ 进程正常运行
   - ✅ 仅监听 localhost:3000

**最后更新：** 2026-03-11
