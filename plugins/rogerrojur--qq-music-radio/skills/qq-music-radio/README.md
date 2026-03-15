# QQ 音乐电台播放器

> ⚠️ **ClawHub 安全警告：** 此 skill 已被 ClawHub 标记为高风险。请仔细阅读 [SECURITY-WARNING.md](SECURITY-WARNING.md) 和 [PRE-INSTALL-CHECKLIST.md](PRE-INSTALL-CHECKLIST.md) 后再决定是否使用。
>
> **推荐使用安全版本：** `./start-secure.sh`（无隧道功能）

---

🎵 AI 智能推荐的 QQ 音乐播放器，支持自动播放、智能过滤、连续播放

## ⚠️ 安全提示

**在安装前，请务必：**
1. 阅读 [SECURITY-WARNING.md](SECURITY-WARNING.md) - ClawHub 审查说明
2. 阅读 [PRE-INSTALL-CHECKLIST.md](PRE-INSTALL-CHECKLIST.md) - 安装前检查清单
3. 运行 `./security-scan.sh` - 自动安全扫描
4. 在 Docker 或隔离环境中测试

**此 skill 会：**
- ⚠️ 下载 npm 依赖包（约 5-10 MB）
- ⚠️ 创建后台进程
- ⚠️ 连接 QQ 音乐 API
- ⚠️ 写入日志到 /tmp

**安全版本（推荐）：**
```bash
./start-secure.sh  # 无隧道，仅本地访问
```

---

## ✨ 特性

- **🎧 AI 智能推荐** - 自动选择热门歌单并打乱播放顺序
- **🎯 智能过滤** - 后端自动过滤不可播放的歌曲
- **♾️ 连续播放** - 播放完自动加载新推荐
- **🎨 精美界面** - 紫色渐变设计，响应式布局
- **🔒 安全可靠** - 开源透明，本地运行

## 🚀 快速开始

### ⭐ 方法 1：安全版本（强烈推荐）

```bash
# 使用无隧道的安全版本
./start-secure.sh

# 特点：
# - ✅ 无 SSH 隧道功能
# - ✅ 无公网暴露
# - ✅ 仅监听 localhost
# - ✅ 完全安全透明
```

### 方法 2：Docker 隔离（最安全）

```bash
# 在完全隔离的容器中运行
docker run -it --rm \
  -v $(pwd):/app -w /app -p 3000:3000 \
  node:18 \
  bash -c "./start-secure.sh"

# 访问 http://localhost:3000
```

### 方法 3：标准版本（需确认配置）

```bash
# 确保禁用隧道
ENABLE_TUNNEL=false ./start.sh

# 或先检查默认值
grep "ENABLE_TUNNEL=" start.sh | grep ":-"
```

# 2. 安装依赖
cd player
npm install

# 3. 启动
cd ..
./start.sh
```

## 📱 使用方式

### 本地访问
启动后，在浏览器访问：
```
http://localhost:3000
```

### 公网访问（默认启用）
启动脚本会自动创建公网隧道，输出类似：
```
🌐 公网地址: https://xxx.serveousercontent.com
```

点击该地址即可在任何设备访问。

### 禁用公网访问
如果只需本地使用，禁用公网隧道：

```bash
# 环境变量方式
ENABLE_TUNNEL=false ./start.sh

# 或在启动脚本所在目录创建 .env 文件：
# ENABLE_TUNNEL=false
# TUNNEL_SERVICE=serveo.net
# SHOW_SECURITY_WARNING=true
```

**.env 配置选项：**
```bash
# 是否启用公网隧道（true/false）
ENABLE_TUNNEL=true

# 隧道服务提供商
TUNNEL_SERVICE=serveo.net

# 是否显示安全提示（true/false）
SHOW_SECURITY_WARNING=true

# 服务器端口
PORT=3000

# 日志文件路径
LOG_FILE=/tmp/qq-music-radio.log
SERVEO_LOG=/tmp/serveo.log
```

## 🎵 播放器功能

- **🎧 开始播放** - 点击按钮，AI 自动推荐并播放
- **⏯️ 播放控制** - 播放/暂停、上一首/下一首
- **🎚️ 音量控制** - 拖动滑块调节音量
- **⏱️ 进度条** - 拖动跳转到任意位置
- **📃 播放列表** - 查看即将播放的歌曲
- **♾️ 自动续播** - 播放完自动加载新推荐

## 🔧 配置选项

通过创建 `.env` 文件配置（在 skill 根目录）：

```bash
# 基本配置
PORT=3000                        # 服务器端口

# 公网访问
ENABLE_TUNNEL=true              # 是否启用公网隧道（true/false）
TUNNEL_SERVICE=serveo.net       # 隧道服务提供商

# 安全
SHOW_SECURITY_WARNING=true      # 显示安全提示（true/false）

# 日志
LOG_FILE=/tmp/qq-music-radio.log
SERVEO_LOG=/tmp/serveo.log
```

**快速禁用公网访问：**
```bash
# 创建 .env 文件
echo "ENABLE_TUNNEL=false" > .env
./start.sh
```

## 🔒 安全说明

### ✅ 安全特性
- **开源透明** - 所有代码可审查
- **本地运行** - 服务器在 localhost
- **公开 API** - 仅调用 QQ 音乐公开接口
- **无数据收集** - 不收集或上传用户数据
- **可配置** - 可禁用公网访问

### 网络行为
- `c.y.qq.com` - QQ 音乐 API
- `u.y.qq.com` - 播放链接获取
- `y.gtimg.cn` - 专辑封面 CDN
- `serveo.net` - 公网隧道（可选）

详细安全说明请查看 [SECURITY.md](./SECURITY.md)

## 📝 管理命令

```bash
# 启动播放器
./start.sh

# 停止播放器
./stop.sh

# 获取公网地址
./get-url.sh

# 查看日志
tail -f /tmp/qq-music-radio.log

# 查看隧道日志
tail -f /tmp/serveo.log
```

## 🛠️ 技术栈

- **后端:** Node.js + Express
- **API:** QQ 音乐非官方 API
- **隧道:** Serveo.net SSH 反向代理
- **前端:** HTML5 + Vanilla JavaScript

## 📋 依赖项

```json
{
  "express": "^4.18.2",
  "axios": "^1.6.0",
  "cors": "^2.8.5",
  "dotenv": "^16.3.1"
}
```

所有依赖都是官方维护的热门包，无已知安全漏洞。

## 🐛 故障排除

### 端口被占用
```bash
# 查看占用进程
lsof -i :3000
# 杀死进程
kill -9 <PID>
```

### 隧道断开
```bash
# 停止并重新启动
./stop.sh
./start.sh
```

### 歌曲无法播放
- QQ 音乐版权限制，已自动过滤大部分
- 后端会跳过不可播放的歌曲
- 尝试刷新页面重新加载

### 无法访问公网地址
- 检查网络连接
- 查看隧道日志：`tail -f /tmp/serveo.log`
- 尝试重启：`./stop.sh && ./start.sh`

## 📄 许可证

**MIT-0 (MIT No Attribution License)**

Copyright (c) 2026 OpenClaw AI

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

## ⚠️ 免责声明

- 本项目仅供学习和个人使用
- 音乐内容版权归 QQ 音乐所有
- 使用非官方 API，可能随时失效
- 请遵守相关法律法规

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📞 支持

- GitHub Issues
- OpenClaw 社区
- ClawHub Skill 页面

---

**版本:** v3.2.0  
**更新时间:** 2026-03-11  
**作者:** OpenClaw AI
