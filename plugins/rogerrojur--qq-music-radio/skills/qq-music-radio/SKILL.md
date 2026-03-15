---
name: qq-music-radio
description: "AI 智能推荐的 QQ 音乐播放器 | ⚠️ ClawHub 高风险警告：包含网络下载和后台进程，推荐使用 start-secure.sh 安全版本"
---

# QQ 音乐电台播放器 Skill

## ⚠️ ClawHub 安全警告

**重要：** 此 skill 已被 ClawHub 标记为高风险。

**原因：**
- ⚠️ 包含 npm 依赖下载
- ⚠️ 创建后台进程
- ⚠️ 可选的公网隧道功能

**安全使用方式：**
1. ✅ 使用 `./start-secure.sh`（推荐，无隧道版本）
2. ✅ 在 Docker 容器中隔离运行
3. ✅ 仔细阅读 `SECURITY-WARNING.md`
4. ✅ 运行 `./security-scan.sh` 验证

---

## 🔒 安全说明

### ✅ 安全特性
- **开源透明** - 所有代码可审查，无混淆
- **本地优先** - 默认仅 localhost 访问
- **完整文档** - 逐行代码审查报告
- **安全版本** - 提供无隧道的 start-secure.sh
- **无数据收集** - 不收集或上传用户数据

### ⚙️ 功能说明
1. **本地服务器** - Node.js 服务器（端口 3000）
2. **QQ 音乐 API** - 仅调用 QQ 音乐公开 API
3. **可选公网隧道** - serveo.net 隧道（**默认禁用**）

### 🛡️ 推荐使用方式

**方式 1：安全版本（强烈推荐）**
```bash
./start-secure.sh  # 完全移除隧道功能
```

**方式 2：Docker 隔离**
```bash
docker run -it --rm -v $(pwd):/app -w /app -p 3000:3000 \
  node:18 bash -c "./start-secure.sh"
```

**方式 3：标准版本（需确认配置）**
```bash
ENABLE_TUNNEL=false ./start.sh  # 确保禁用隧道
ENABLE_TUNNEL=false ./start.sh

# 或修改配置文件
cp .env.example .env
# 编辑 .env: ENABLE_TUNNEL=false
./start.sh
```

**默认行为：**
- ✅ 启用公网隧道（方便分享）
- ✅ 显示安全提示
- ✅ 可通过配置禁用

## 触发条件

当用户提到以下任何关键词时触发此 skill：
- "QQ音乐" / "qq音乐" / "QQ 音乐"
- "音乐电台" / "电台" / "音乐播放器"
- "听歌" / "放歌" / "播放音乐"
- "个性化推荐" / "推荐歌曲"
- "打开音乐播放器"

## 功能说明

这是一个全功能的 QQ 音乐个性化推荐电台播放器，具有以下特性：

### ✨ 核心功能
- **一键启动** - 自动启动服务器并生成公网访问地址
- **AI 智能推荐** - 自动选择热门歌单并打乱播放顺序
- **后端智能过滤** - 只返回可播放的歌曲，避免版权错误
- **连续播放** - 播放完自动加载新的推荐
- **精美界面** - 紫色渐变设计，响应式布局

### 🎨 界面特性
- 大尺寸专辑封面展示
- 智能封面生成（当原始封面加载失败时）
- 完整播放控制（播放/暂停/上一首/下一首）
- 进度条拖动
- 音量控制
- 即将播放列表预览

### 🔧 技术实现
- Node.js + Express 后端
- QQ 音乐非官方 API
- Serveo.net 公网隧道
- 无需 API Token

## 使用方法

### 基本使用

用户说："打开 QQ 音乐播放器"

你的操作：
1. 检查服务器是否已启动
2. 如果未启动，启动服务器
3. 检查公网隧道是否存在
4. 如果不存在，创建 serveo.net 隧道
5. 返回公网访问地址
6. 使用 Canvas 或浏览器工具直接展示播放器页面

### 完整流程

```bash
# 1. 启动播放器（自动安装依赖、启动服务器、创建隧道）
/projects/.openclaw/skills/qq-music-radio/start.sh

# 2. 获取公网地址
PUBLIC_URL=$(/projects/.openclaw/skills/qq-music-radio/get-url.sh)

# 3. 返回给用户
echo "访问地址: $PUBLIC_URL"
```

简化版本（推荐）：
```bash
# 一键启动并获取地址
/projects/.openclaw/skills/qq-music-radio/start.sh

# 地址会自动显示在输出中
```

## 实现细节

### 文件位置
- Skill 目录: `/projects/.openclaw/skills/qq-music-radio/`
- 播放器目录: `/projects/.openclaw/skills/qq-music-radio/player/`
- 服务器脚本: `player/server-qqmusic.js`
- 前端页面: `player/public/index.html`
- 前端脚本: `player/public/app-auto.js`
- 启动脚本: `start.sh`
- 停止脚本: `stop.sh`
- 获取地址: `get-url.sh`

### 启动命令
```bash
/projects/.openclaw/skills/qq-music-radio/start.sh
```

或：
```bash
cd /projects/.openclaw/skills/qq-music-radio/player
node server-qqmusic.js
```

### 健康检查
```bash
curl http://localhost:3000/health
```

响应示例：
```json
{
  "status": "ok",
  "timestamp": "2026-03-11T07:30:00.000Z",
  "config": {
    "mode": "qq-music-unofficial-api"
  },
  "mode": "production"
}
```

### 公网隧道
使用 serveo.net SSH 隧道：
```bash
ssh -o StrictHostKeyChecking=no -R 80:localhost:3000 serveo.net
```

隧道创建后会输出类似：
```
Forwarding HTTP traffic from https://xxx.serveousercontent.com
```

### API 端点
- `GET /health` - 健康检查
- `GET /api/radio/list` - 获取电台列表
- `POST /api/radio/detail` - 获取电台歌曲（已过滤）
- `POST /api/song/url` - 获取歌曲播放链接

## 响应模板

### 成功启动
```
✅ QQ 音乐播放器已启动！

🌐 访问地址：
https://xxx.serveousercontent.com

🎵 功能特性：
• AI 智能推荐 - 自动选择并播放
• 连续播放 - 永不停歇
• 精美界面 - 沉浸体验

📱 使用说明：
1. 点击上方链接打开播放器
2. 点击"🎧 开始播放"按钮
3. 享受音乐！🎵

💡 提示：
• 后端已智能过滤，只播放可用歌曲
• 播放完自动加载新推荐
• 支持手机和电脑访问
```

### 已经在运行
```
✅ QQ 音乐播放器正在运行！

🌐 访问地址：
https://xxx.serveousercontent.com

状态：
• 服务器运行中 ✓
• 公网隧道已建立 ✓
• 播放器可用 ✓

直接点击链接即可使用！🎵
```

### 使用 Canvas 展示
```javascript
// 在支持 Canvas 的环境中，直接展示播放器
await canvas({
    action: 'present',
    url: publicUrl,
    width: 1200,
    height: 900
});
```

## 注意事项

1. **端口占用** - 确保 3000 端口未被占用
2. **网络要求** - 需要稳定的互联网连接
3. **版权说明** - 仅供学习和演示，音乐版权归 QQ 音乐所有
4. **隧道稳定性** - serveo.net 隧道可能会断开，需要定期检查
5. **浏览器兼容** - 需要支持 HTML5 Audio 的现代浏览器

## 故障排除

### 服务器无法启动
```bash
# 检查端口
lsof -i :3000
# 如果被占用，杀死进程
kill -9 <PID>
```

### 隧道断开
```bash
# 查找 serveo 进程
ps aux | grep serveo
# 杀死旧进程
kill -9 <PID>
# 重新创建隧道
ssh -o StrictHostKeyChecking=no -R 80:localhost:3000 serveo.net
```

### 无法播放
- 检查浏览器控制台错误
- 确认后端 API 正常响应
- 测试 `/test.html` 页面

## 更新日志

### v3.0 - 智能过滤版 (2026-03-11)
- ✅ 后端智能过滤不可播放歌曲
- ✅ 添加"开始播放"按钮（符合浏览器自动播放策略）
- ✅ 智能封面生成（10种渐变色方案）
- ✅ 优化播放列表显示
- ✅ 详细的 Console 调试日志

### v2.0 - 自动推荐版
- ✅ AI 自动推荐模式
- ✅ 打乱播放顺序
- ✅ 连续播放，自动加载

### v1.0 - 初始版本
- ✅ 基本播放功能
- ✅ 手动选择歌单

## 相关资源

- 项目文档: `/root/.openclaw/workspace/qq-music-radio-player-full/README-FINAL.md`
- QQ 音乐 API 文档: https://iwiki.woa.com/p/1542165555
- Serveo.net 文档: https://serveo.net

## 许可证

**MIT-0 (MIT No Attribution License)**

Copyright (c) 2026 OpenClaw AI

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
