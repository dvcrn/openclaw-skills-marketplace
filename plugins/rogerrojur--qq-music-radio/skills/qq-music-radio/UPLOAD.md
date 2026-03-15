# 📤 Knot 平台上传指南

## ✅ SKILL.md 格式已修复

SKILL.md 现在以正确的 YAML front matter 开头：

```yaml
---
name: qq-music-radio
displayName: QQ音乐电台
description: AI 智能推荐的 QQ 音乐播放器，支持自动播放、智能过滤、连续播放，一键启动即可享受音乐
version: 3.1.0
author: OpenClaw AI
tags:
  - 音乐
  - QQ音乐
  - 播放器
  - 电台
  - 智能推荐
triggers:
  - QQ音乐
  - qq音乐
  - 音乐电台
  - 电台
  - 音乐播放器
  - 听歌
  - 放歌
  - 播放音乐
  - 个性化推荐
  - 推荐歌曲
  - 打开音乐播放器
---
```

## 📦 打包 Skill

### 方式 1：使用打包脚本（推荐）

```bash
/projects/.openclaw/skills/qq-music-radio/package.sh
```

这会创建：`/tmp/qq-music-radio-skill.zip`

### 方式 2：手动打包

```bash
cd /projects/.openclaw/skills/
zip -r qq-music-radio-skill.zip qq-music-radio/ -x "qq-music-radio/player/node_modules/*"
```

## 📤 上传到 Knot 平台

### 步骤 1：获取 ZIP 包

打包完成后，ZIP 包位置：
```
/tmp/qq-music-radio-skill.zip
```

大小：约 52KB

### 步骤 2：准备技能信息

上传时需要填写的信息：

**基本信息：**
- **技能名称：** QQ音乐电台
- **技能标识：** qq-music-radio
- **版本：** 3.1.0
- **作者：** OpenClaw AI

**描述信息：**
- **简短描述：** AI 智能推荐的 QQ 音乐播放器
- **详细描述：**
  ```
  一个功能完整的 QQ 音乐个性化推荐电台播放器。
  
  核心特性：
  • AI 智能推荐 - 自动选择并播放热门歌曲
  • 后端智能过滤 - 只返回可播放的歌曲，避免版权错误
  • 连续播放 - 播放完自动加载新的推荐
  • 智能封面 - 10种精美渐变色方案
  • 精美界面 - 紫色渐变设计，响应式布局
  • 一键启动 - 自动安装依赖并创建公网访问地址
  
  使用方法：
  1. 对 AI 说"打开音乐播放器"
  2. AI 自动启动服务器
  3. 点击返回的链接
  4. 点击"开始播放"按钮
  5. 享受音乐！
  
  技术栈：
  • Node.js + Express
  • QQ 音乐非官方 API
  • Serveo.net 公网隧道
  • 无需 API Token
  
  完全独立，开箱即用！
  ```

**标签：**
- 音乐
- QQ音乐
- 播放器
- 电台
- 智能推荐

**触发词：**
- QQ音乐
- 音乐电台
- 听歌
- 播放音乐
- 打开音乐播放器

### 步骤 3：上传文件

1. 登录 Knot 技能市场
2. 点击"创建技能"或"上传技能"
3. 选择 `/tmp/qq-music-radio-skill.zip`
4. 填写上述信息
5. 提交审核

## 📋 包含的文件

ZIP 包包含以下文件：

```
qq-music-radio/
├── SKILL.md              # Skill 定义（必需）
├── README.md             # 主说明
├── INSTALL.md            # 安装指南
├── EXAMPLES.md           # 使用示例
├── SUMMARY.md            # 项目总结
├── FINAL.md              # 完成报告
├── LICENSE               # MIT 许可证
├── start.sh              # 启动脚本
├── stop.sh               # 停止脚本
├── get-url.sh            # 获取地址脚本
├── package.sh            # 打包脚本
└── player/               # 播放器代码
    ├── package.json      # 依赖配置
    ├── package-lock.json # 依赖锁定
    ├── server-qqmusic.js # 服务器
    ├── .env              # 环境配置
    └── public/           # 前端文件
        ├── index.html
        ├── app-auto.js
        └── test.html
```

**注意：** `node_modules/` 目录已排除，用户首次运行时会自动安装。

## ✅ 检查清单

上传前请确认：

- [x] SKILL.md 格式正确（以 `---` 开头）
- [x] 包含所有必需文件
- [x] 脚本有执行权限
- [x] 文档完整清晰
- [x] LICENSE 文件存在
- [x] 不包含 node_modules（体积优化）
- [x] 版本号正确
- [x] 作者信息正确

## 🔍 验证 SKILL.md 格式

可以用这个命令检查：

```bash
head -25 /projects/.openclaw/skills/qq-music-radio/SKILL.md
```

应该看到：
```yaml
---
name: qq-music-radio
displayName: QQ音乐电台
description: ...
version: 3.1.0
...
---
```

## 📊 包大小

- **总大小：** 约 52KB
- **压缩比：** 良好
- **不含：** node_modules（约 20-30MB）

用户安装后首次运行 `start.sh` 会自动安装依赖。

## 🎉 上传完成后

其他用户可以：

1. **从 Knot 安装：**
   ```bash
   # AI 会自动安装到
   /projects/.openclaw/skills/qq-music-radio/
   ```

2. **直接使用：**
   - 对 AI 说："打开音乐播放器"
   - AI 自动执行启动脚本
   - 返回访问地址

3. **手动启动：**
   ```bash
   /projects/.openclaw/skills/qq-music-radio/start.sh
   ```

## ⚠️ 常见问题

### Q: 上传失败，提示格式错误

**A:** 确认 SKILL.md 第一行是 `---`，不是标题或空行。

### Q: ZIP 包太大

**A:** 确认已排除 `node_modules/`。使用 `package.sh` 脚本自动排除。

### Q: 用户安装后无法运行

**A:** 确保：
- 脚本有执行权限 (`chmod +x *.sh`)
- 包含 `player/package.json`
- `start.sh` 会自动安装依赖

### Q: 如何更新版本

**A:** 修改 SKILL.md 中的 `version` 字段，重新打包上传。

## 📞 需要帮助？

- 查看 [README.md](README.md) 了解功能
- 查看 [INSTALL.md](INSTALL.md) 了解安装
- 查看 [EXAMPLES.md](EXAMPLES.md) 了解使用
- 查看 Knot 平台文档

---

**现在可以上传了！** 🚀

```bash
# 打包
/projects/.openclaw/skills/qq-music-radio/package.sh

# 文件位置
ls -lh /tmp/qq-music-radio-skill.zip
```
