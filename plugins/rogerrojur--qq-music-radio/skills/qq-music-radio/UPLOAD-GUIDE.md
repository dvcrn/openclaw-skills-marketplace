# QQ 音乐播放器 - ClawHub 上传指南

## 📦 准备上传

这个版本已经过安全优化，可以安全地上传到 ClawHub。

### ✅ 安全改进

1. **配置化设计**
   - 使用 `.env` 配置文件
   - 支持环境变量覆盖
   - 默认行为可配置

2. **安全提示**
   - 启动时显示安全警告
   - 明确说明网络行为
   - 可关闭公网隧道

3. **完整文档**
   - `README.md` - 使用说明
   - `SECURITY.md` - 详细安全说明
   - `SKILL.md` - OpenClaw skill 说明

4. **代码透明**
   - 所有代码明文可读
   - 无混淆或压缩
   - 依赖清晰列出

### 📋 上传前检查

- [x] 移除敏感信息
- [x] 添加 `.gitignore`
- [x] 完善文档
- [x] 安全说明
- [x] 配置示例
- [x] 测试脚本

### 🔧 关键配置

**默认配置（推荐）：**
```bash
ENABLE_TUNNEL=true              # 启用公网访问
SHOW_SECURITY_WARNING=true      # 显示安全提示
```

**高安全配置：**
```bash
ENABLE_TUNNEL=false             # 仅本地访问
```

### 📝 ClawHub 描述建议

**标题：** QQ 音乐电台播放器 - AI 智能推荐

**简介：**
```
🎵 AI 智能推荐的 QQ 音乐播放器
✨ 自动播放、智能过滤、连续播放
🔒 开源安全、本地运行、可配置
```

**详细说明：**
```
## 特性
- 🎧 AI 智能推荐 - 自动选择热门歌单
- 🎯 智能过滤 - 后端过滤不可播放歌曲
- ♾️ 连续播放 - 自动加载新推荐
- 🎨 精美界面 - 紫色渐变设计
- 🔒 安全可靠 - 开源透明，可配置

## 使用方法
1. 安装 skill
2. 运行 `./start.sh`
3. 在浏览器打开显示的地址

## 安全说明
- 本地运行在 localhost:3000
- 仅调用 QQ 音乐公开 API
- 可选公网隧道（可禁用）
- 所有代码开源可审查

详见 SECURITY.md
```

**标签：**
- 音乐
- QQ音乐
- 播放器
- 电台
- 智能推荐
- 娱乐
- 工具

### 🚨 可能的安全问题回应

如果 ClawHub Security 仍然报警：

1. **SSH 隧道问题**
   - 解释：仅用于 HTTP 转发
   - 默认启用但可禁用
   - 配置：`ENABLE_TUNNEL=false`

2. **后台进程问题**
   - 解释：标准的服务器启动方式
   - 不涉及系统修改
   - 用户可完全控制

3. **外部 API 调用**
   - 仅调用 QQ 音乐公开 API
   - 无数据收集或上传
   - 代码完全透明

### 📄 需要包含的文件

上传到 ClawHub 时，确保包含：

```
qq-music-radio/
├── SKILL.md           # ✅ OpenClaw skill 定义
├── README.md          # ✅ 使用说明
├── SECURITY.md        # ✅ 安全说明（重要！）
├── .env.example       # ✅ 配置示例
├── .gitignore         # ✅ 忽略文件
├── start.sh           # ✅ 启动脚本
├── stop.sh            # ✅ 停止脚本
├── get-url.sh         # ✅ 获取地址脚本
├── LICENSE            # ✅ 许可证
└── player/
    ├── package.json   # ✅ 依赖清单
    ├── server-qqmusic.js  # ✅ 服务器代码
    └── public/
        ├── index.html     # ✅ 前端页面
        └── app-auto.js    # ✅ 前端逻辑
```

**不要包含：**
- `node_modules/` - 依赖文件夹
- `.env` - 用户配置
- `*.log` - 日志文件
- `/tmp/` - 临时文件

### 🎯 上传命令

```bash
# 1. 清理
cd /projects/.openclaw/skills/qq-music-radio
./stop.sh
rm -rf player/node_modules
rm -f *.log .env

# 2. 打包（如果需要）
cd ..
tar -czf qq-music-radio-v3.2.0.tar.gz qq-music-radio/ \
  --exclude='node_modules' \
  --exclude='*.log' \
  --exclude='.env' \
  --exclude='/tmp'

# 3. 或直接上传文件夹
# 使用 ClawHub 的 skill 上传功能
```

### ✅ 上传后验证

上传成功后，建议测试：

1. **本地安装测试**
   ```bash
   openclaw skills install qq-music-radio
   cd ~/.openclaw/skills/qq-music-radio
   ./start.sh
   ```

2. **禁用隧道测试**
   ```bash
   ENABLE_TUNNEL=false ./start.sh
   ```

3. **配置文件测试**
   ```bash
   cp .env.example .env
   # 编辑 .env
   ./start.sh
   ```

### 📞 支持信息

在 ClawHub 页面提供：

- GitHub 仓库链接（如有）
- Issue 追踪链接
- 安全问题报告方式
- 社区支持渠道

---

**准备好了吗？** 按照上述步骤上传到 ClawHub！

如果遇到安全检测问题，请提供 SECURITY.md 文档说明。
