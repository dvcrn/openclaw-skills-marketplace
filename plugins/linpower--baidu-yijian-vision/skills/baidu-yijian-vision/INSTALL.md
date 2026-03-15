# 安装与配置指南

## ⚠️ 本工具必需条件（无法跳过）

此工具无法在以下情况下运行：

| 条件 | 状态 | 说明 |
|------|------|------|
| **YIJIAN_API_KEY** 环境变量 | 🔴 **必需** | 每次使用工具时都需要。可从 https://yijian-next.cloud.baidu.com 获取 |
| **Node.js >= 16.0.0** | 🔴 **必需** | 本工具的运行时依赖 |
| **npm >= 8.0.0** | 🔴 **必需** | 用于安装依赖 |

**如果缺少任何"必需"条件，工具将无法运行。**

---

## ⚠️ 条件依赖

以下条件仅在使用特定功能时需要：

| 功能 | 依赖 | 说明 |
|------|------|------|
| **可视化检测结果** (visualize.mjs, show-grid.mjs) | C++ 编译工具 + sharp | 用于绘制图像上的检测框。需要编译 native 模块，增加安装复杂性 |
| **视频帧提取** | FFmpeg | 用于从视频文件提取帧 |

---

## 系统要求

### 必需（所有用户）

- **Node.js** >= 16.0.0
- **npm** >= 8.0.0
- **git**（用于源代码安装）

### 条件必需

- **C++ 编译工具**（仅用于可视化功能）
  - macOS：Xcode Command Line Tools - 运行 `xcode-select --install`
  - Ubuntu/Debian：`sudo apt-get install build-essential python3`
  - Windows：Visual Studio Build Tools

- **FFmpeg** >= 4.0（仅用于视频帧提取）

## 安装步骤

### 1. 安装依赖

```bash
npm install
```

此步骤将安装所有必需依赖（仅 archiver 用于打包功能）。

**如需可视化功能（可选）**，还需要安装 sharp：

```bash
npm install sharp
```

此时将编译 native 模块，首次运行可能较耗时。如果编译失败，需要安装 C++ 编译工具。

### 2. 配置 API Key

获取 API Key：
1. 登录 [一见平台](https://yijian-next.cloud.baidu.com/apaas/)
2. 激活试用包
3. 导航到 IAM → API Keys
4. 生成新的 API Key

设置环境变量（推荐临时设置）：

**Linux/macOS：**
```bash
# 临时设置（仅当前 shell 会话有效）
export YIJIAN_API_KEY="your-api-key-here"

# 然后运行命令
node scripts/list.mjs
```

**Windows (PowerShell)：**
```powershell
$env:YIJIAN_API_KEY="your-api-key-here"
node scripts/list.mjs
```

**Windows (CMD)：**
```cmd
set YIJIAN_API_KEY=your-api-key-here
node scripts/list.mjs
```

⚠️ **安全提示：** 勿将 API Key 添加到 shell 配置文件（如 `~/.bashrc` 或 `~/.zshrc`），避免密钥意外暴露。详见 [SECURITY.md](./SECURITY.md)。

### 3. 验证安装

```bash
# 列出可用技能
YIJIAN_API_KEY=${YIJIAN_API_KEY} node scripts/list.mjs
```

预期输出：
```
可用技能：
  👤 ep-public-inqm15aq  - 人员摔倒 [预设]
  🏥 ep-public-k8wsrv3c  - 久坐 [预设]
  ...
```

## 可选依赖

### FFmpeg（用于视频处理）

提取视频帧需要 FFmpeg：

**macOS：**
```bash
brew install ffmpeg
```

**Ubuntu/Debian：**
```bash
sudo apt-get install ffmpeg
```

**Windows：**
- 下载：https://ffmpeg.org/download.html
- 添加到 PATH 环境变量

验证安装：
```bash
ffmpeg -version
```

## 故障排除

### "npm install" 失败

**问题：** 编译 native 模块失败

**解决方案：**
```bash
# 清空缓存
rm -rf node_modules package-lock.json

# 重新安装
npm install --verbose
```

如果问题持续，检查：
- Node.js 版本是否 >= 16.0.0：`node -v`
- 是否安装了 C++ 编译工具（Windows: Visual Studio Build Tools，macOS: Xcode Command Line Tools）

### "YIJIAN_API_KEY not set"

**问题：** 环境变量未设置或不生效

**解决方案：**
```bash
# 验证环境变量是否已设置
echo $YIJIAN_API_KEY

# 重新设置
export YIJIAN_API_KEY="your-api-key"

# 验证
echo $YIJIAN_API_KEY  # 应该输出 API Key（或至少显示已设置）
```

### "Cannot find module 'sharp'"

**问题：** sharp 模块未正确编译

**解决方案：**
```bash
# 重新安装 sharp
npm rebuild sharp

# 或者完全重新安装
rm -rf node_modules
npm install
```

## 网络配置

### 远程端点

此工具调用以下远程端点：

- **API 服务：** `https://yijian-next.cloud.baidu.com`
  - 用途：获取技能元数据和执行任务
  - 认证：使用 YIJIAN_API_KEY

确保网络允许访问此端点。如果在企业网络中，可能需要配置代理。

### 代理配置

如果需要通过代理访问，设置：

```bash
# npm 代理
npm config set proxy http://proxy.example.com:8080
npm config set https-proxy http://proxy.example.com:8080

# 或通过环境变量
export HTTP_PROXY=http://proxy.example.com:8080
export HTTPS_PROXY=http://proxy.example.com:8080
```

## 下一步

安装完成后，查看：
- **[SKILL.md](./SKILL.md)** - 使用指南和示例
- **[SECURITY.md](./SECURITY.md)** - 安全性和数据隐私说明
- **[types-guide.md](./types-guide.md)** - 数据类型定义
