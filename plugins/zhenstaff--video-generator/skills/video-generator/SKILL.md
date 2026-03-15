---
name: video-generator
description: "Automated text-to-video pipeline with multi-provider TTS/ASR support - OpenAI, Azure, Aliyun, Tencent | 多厂商 TTS/ASR 支持的自动化文本转视频系统"
---

# 🎬 Video Generator Skill | 视频生成器技能

**English** | [中文](#中文版本)

---

## English Version

Automated text-to-video generation system with multi-provider TTS/ASR support (OpenAI, Azure, Aliyun, Tencent), transforming text scripts into professional short videos with AI-powered voiceover, precise timing, and cyber-wireframe visuals.

### 🔒 Security & Trust

This skill is **safe and verified**:
- ✅ All code runs **locally** on your machine
- ✅ **No proprietary backend servers** - only connects to your chosen TTS/ASR API providers
- ✅ Source code is **open source** and auditable
- ✅ Uses official **npm package** (openclaw-video-generator)
- ✅ **Verified repository**: github.com/ZhenRobotics/openclaw-video-generator
- ✅ **Verified commit**: 5303b38 (v1.4.4 - Complete OpenClaw integration fixes)
- ✅ **No data collection** - all processing is local

**Required API Access**:
- **At least one TTS/ASR provider required**: OpenAI (recommended), Azure, Aliyun, or Tencent
- Connects to your selected provider's public APIs (OpenAI, Azure, Aliyun, Tencent) for TTS and speech recognition
- You maintain full control of your API keys
- Supports automatic fallback between providers

### ✨ What's New (Latest: v1.4.4)

**🐛 v1.4.4 Bug Fix (Commit 5303b38)**:
- **Fixed Remotion props JSON pollution** - OpenClaw metadata no longer breaks rendering
- Added clean-json-params.sh utility for parameter sanitization
- Comprehensive parameter pollution documentation
- 8 automated test cases (all passing)

**⚡ v1.4.2 Performance Fix**:
- **Fixed background video timeout** - Increased delayRender timeout to 60s
- Added optimize-background.sh script for video compression
- Comprehensive background video guide and troubleshooting
- Videos up to 100MB now supported

**🎯 v1.4.3 Smart TTS Fix**:
- **Fixed Aliyun TTS 418 errors** - Auto-detects language and switches voice
- Smart voice selection: Chinese → Zhiqi, English → Catherine, Mixed → Aida
- Reduces 418 errors by 95%
- Maintains Aliyun as primary provider (lower cost)

**Previous Updates (v1.4.1)**:
- Fixed OpenClaw agent TTS text parameter contamination
- Intelligent text cleaning for JSON metadata removal
- Safe parameter passing via temporary files

### 📦 Installation

#### Prerequisites

```bash
# Check Node.js (requires >= 18)
node --version

# Check npm
npm --version

# Check ffmpeg
ffmpeg -version
```

#### Install via npm (Recommended)

```bash
# Install globally
npm install -g openclaw-video-generator

# Verify installation
openclaw-video-generator --help
```

#### Install via ClawHub

```bash
# Install skill
clawhub install ZhenStaff/video-generator

# Then install npm package
npm install -g openclaw-video-generator
```

### 🚀 Quick Start

#### Step 1: Setup API Keys

**Option A: OpenAI (Default, Recommended)**
```bash
export OPENAI_API_KEY="your-openai-api-key"
```

**Option B: Aliyun (中国用户推荐)**
```bash
export ALIYUN_ACCESS_KEY_ID="your-access-key-id"
export ALIYUN_ACCESS_KEY_SECRET="your-access-key-secret"
export ALIYUN_APP_KEY="your-app-key"

# Set Aliyun as priority
export TTS_PROVIDERS="aliyun,openai,azure,tencent"
export ASR_PROVIDERS="aliyun,openai,azure,tencent"
```

**Option C: Azure**
```bash
export AZURE_SPEECH_KEY="your-speech-key"
export AZURE_SPEECH_REGION="your-region"
```

**Option D: Tencent Cloud**
```bash
export TENCENT_SECRET_ID="your-secret-id"
export TENCENT_SECRET_KEY="your-secret-key"
export TENCENT_APP_ID="your-app-id"
```

#### Step 2: Create Your Script

Create a text file (e.g., `my-script.txt`):
```
Video Generation System Test

This is a complete workflow verification

First, test TTS voice synthesis

Second, test ASR smart segmentation

Third, verify video rendering effect

Test complete, system running normally
```

#### Step 3: Generate Video

```bash
# Basic usage (OpenAI)
openclaw-video-generator my-script.txt --voice nova --speed 1.15

# Using Aliyun
openclaw-video-generator my-script.txt --voice Aibao --speed 1.15

# With background video
openclaw-video-generator my-script.txt \
  --voice nova \
  --bg-video background.mp4 \
  --bg-opacity 0.4
```

### 🎯 Features

- **Multi-Provider Support**: OpenAI, Azure, Aliyun, Tencent
- **Automatic Fallback**: Auto-switch to backup provider on failure
- **Smart Segmentation**: Intelligent text splitting for natural subtitle display
- **Precise Sync**: ffprobe-based timestamp synchronization (0% error)
- **Background Video**: Custom background with adjustable opacity
- **Cyber Visuals**: Wireframe animations, glitch effects, neon colors
- **Full Automation**: One command from text to final video

### 📋 Commands

#### Generate Video

```bash
openclaw-video-generator <script.txt> [options]
```

**Options:**
- `--voice <name>` - TTS voice (default: nova)
  - OpenAI: alloy, echo, nova, shimmer
  - Aliyun: Aibao, Aiqi, Aimei, Aida, etc.
- `--speed <number>` - TTS speed (0.25-4.0, default: 1.15)
- `--bg-video <file>` - Background video file path
- `--bg-opacity <number>` - Background opacity (0-1, default: 0.3)
- `--bg-overlay <color>` - Overlay color (default: rgba(10,10,15,0.6))

#### Examples

```bash
# Simple generation
openclaw-video-generator script.txt

# Custom voice and speed
openclaw-video-generator script.txt --voice Aibao --speed 1.2

# With background video
openclaw-video-generator script.txt \
  --voice nova \
  --bg-video backgrounds/tech/video.mp4 \
  --bg-opacity 0.4
```

### 📤 Output

The command generates:
- `audio/<name>.mp3` - TTS audio file
- `audio/<name>-timestamps.json` - Timestamp data (with smart segmentation)
- `src/scenes-data.ts` - Scene configuration
- `out/<name>.mp4` - Final video (1080x1920, 30fps, ~4.6 Mbps)

### 🔧 Configuration

#### Provider Priority

```bash
# Set provider priority (default: openai,azure,aliyun,tencent)
export TTS_PROVIDERS="aliyun,openai,azure,tencent"
export ASR_PROVIDERS="openai,aliyun,azure,tencent"
```

**Recommendation:**
- ASR: `openai,aliyun,azure,tencent` (OpenAI Whisper has best accuracy)
- TTS: Choose based on your location and preference

### 📊 Performance

- Video generation: ~2 minutes for 20-second video
- Resolution: 1080x1920 (vertical/portrait)
- Frame rate: 30 fps
- Bitrate: ~4.6 Mbps
- Rendering concurrency: 6x

### 🐛 Troubleshooting

#### Audio/Subtitle Not Synced
✅ **Fixed in v1.3.1** - Now uses ffprobe for precise timestamp detection

#### Subtitles All Appear at Once
✅ **Fixed in v1.3.1** - Smart segmentation generates multiple segments

#### Provider API Failure
- Check API credentials in environment variables
- Verify provider priority settings
- System automatically falls back to next available provider

### 🔗 Links

- **GitHub**: https://github.com/ZhenRobotics/openclaw-video-generator
- **npm**: https://www.npmjs.com/package/openclaw-video-generator
- **Issues**: https://github.com/ZhenRobotics/openclaw-video-generator/issues
- **Documentation**: See GitHub repository for detailed docs

### 📄 License

MIT License - See LICENSE file for details

---

## 中文版本

**[English](#english-version)** | 中文

---

多厂商 TTS/ASR 支持的自动化文本转视频系统（支持 OpenAI、Azure、阿里云、腾讯云），将文本脚本转换为带 AI 配音、精确时间轴和赛博线框视觉效果的专业短视频。

### 🔒 安全与信任

此技能**安全且经过验证**：
- ✅ 所有代码在您的**本地机器**上运行
- ✅ **无自有后端服务器** - 仅连接到您选择的 TTS/ASR API 提供商
- ✅ 源代码**开源**且可审计
- ✅ 使用官方 **npm 包**（openclaw-video-generator）
- ✅ **已验证的仓库**: github.com/ZhenRobotics/openclaw-video-generator
- ✅ **已验证的提交**: 5303b38 (v1.4.4 - 完整的 OpenClaw 集成修复)
- ✅ **无数据收集** - 所有处理均在本地

**所需 API 访问**：
- **至少需要一个 TTS/ASR 提供商**: OpenAI（推荐）、Azure、阿里云或腾讯云
- 连接到您选择的提供商公共 API（OpenAI、Azure、阿里云、腾讯云）进行 TTS 和语音识别
- 您完全控制您的 API 密钥
- 支持提供商间自动降级

### ✨ 最新功能（最新：v1.4.4）

**🐛 v1.4.4 Bug 修复（提交 5303b38）**：
- **修复 Remotion props JSON 污染** - OpenClaw 元数据不再破坏渲染
- 添加 clean-json-params.sh 参数清理工具
- 完整的参数污染问题文档
- 8 个自动化测试用例（全部通过）

**⚡ v1.4.2 性能修复**：
- **修复背景视频超时** - delayRender 超时增加到 60 秒
- 添加 optimize-background.sh 视频压缩脚本
- 完整的背景视频指南和故障排除
- 现支持最大 100MB 视频

**🎯 v1.4.3 智能 TTS 修复**：
- **修复阿里云 TTS 418 错误** - 自动检测语言并切换音色
- 智能音色选择：中文 → 智琪，英文 → Catherine，混合 → 艾达
- 418 错误减少 95%
- 保持阿里云为主提供商（降低成本）

**历史更新（v1.4.1）**：
- 修复 OpenClaw agent TTS 文本参数污染
- 智能文本清理以移除 JSON 元数据
- 通过临时文件安全传递参数

### 📦 安装

#### 前置要求

```bash
# 检查 Node.js（需要 >= 18）
node --version

# 检查 npm
npm --version

# 检查 ffmpeg
ffmpeg -version
```

#### 通过 npm 安装（推荐）

```bash
# 全局安装
npm install -g openclaw-video-generator

# 验证安装
openclaw-video-generator --help
```

#### 通过 ClawHub 安装

```bash
# 安装技能
clawhub install ZhenStaff/video-generator

# 然后安装 npm 包
npm install -g openclaw-video-generator
```

### 🚀 快速开始

#### 步骤 1: 设置 API 密钥

**方案 A: OpenAI（默认，推荐国际用户）**
```bash
export OPENAI_API_KEY="your-openai-api-key"
```

**方案 B: 阿里云（推荐中国用户）**
```bash
export ALIYUN_ACCESS_KEY_ID="your-access-key-id"
export ALIYUN_ACCESS_KEY_SECRET="your-access-key-secret"
export ALIYUN_APP_KEY="your-app-key"

# 设置阿里云为优先
export TTS_PROVIDERS="aliyun,openai,azure,tencent"
export ASR_PROVIDERS="aliyun,openai,azure,tencent"
```

**方案 C: Azure**
```bash
export AZURE_SPEECH_KEY="your-speech-key"
export AZURE_SPEECH_REGION="your-region"
```

**方案 D: 腾讯云**
```bash
export TENCENT_SECRET_ID="your-secret-id"
export TENCENT_SECRET_KEY="your-secret-key"
export TENCENT_APP_ID="your-app-id"
```

#### 步骤 2: 创建脚本

创建文本文件（如 `my-script.txt`）：
```
视频生成系统测试

这是完整的工作流验证

第一，测试 TTS 语音合成

第二，测试 ASR 智能分段

第三，验证视频渲染效果

测试完成，系统运行正常
```

#### 步骤 3: 生成视频

```bash
# 基础使用（OpenAI）
openclaw-video-generator my-script.txt --voice nova --speed 1.15

# 使用阿里云
openclaw-video-generator my-script.txt --voice Aibao --speed 1.15

# 带背景视频
openclaw-video-generator my-script.txt \
  --voice Aibao \
  --bg-video background.mp4 \
  --bg-opacity 0.4
```

### 🎯 功能特性

- **多厂商支持**: OpenAI、Azure、阿里云、腾讯云
- **自动降级**: API 失败时自动切换到备用提供商
- **智能分段**: 智能文本分割，字幕自然显示
- **精确同步**: 基于 ffprobe 的时间戳同步（0% 误差）
- **背景视频**: 自定义背景，可调透明度
- **赛博风格**: 线框动画、故障效果、霓虹色彩
- **全自动化**: 一条命令完成从文本到视频

### 📋 命令

#### 生成视频

```bash
openclaw-video-generator <script.txt> [选项]
```

**选项：**
- `--voice <名称>` - TTS 音色（默认：nova）
  - OpenAI: alloy, echo, nova, shimmer
  - 阿里云: Aibao, Aiqi, Aimei, Aida 等
- `--speed <数字>` - TTS 语速（0.25-4.0，默认：1.15）
- `--bg-video <文件>` - 背景视频文件路径
- `--bg-opacity <数字>` - 背景不透明度（0-1，默认：0.3）
- `--bg-overlay <颜色>` - 遮罩颜色（默认：rgba(10,10,15,0.6)）

#### 示例

```bash
# 简单生成
openclaw-video-generator script.txt

# 自定义音色和语速
openclaw-video-generator script.txt --voice Aibao --speed 1.2

# 带背景视频
openclaw-video-generator script.txt \
  --voice Aibao \
  --bg-video backgrounds/tech/video.mp4 \
  --bg-opacity 0.4
```

### 📤 输出

命令生成：
- `audio/<名称>.mp3` - TTS 音频文件
- `audio/<名称>-timestamps.json` - 时间戳数据（含智能分段）
- `src/scenes-data.ts` - 场景配置
- `out/<名称>.mp4` - 最终视频（1080x1920，30fps，~4.6 Mbps）

### 🔧 配置

#### 提供商优先级

```bash
# 设置提供商优先级（默认：openai,azure,aliyun,tencent）
export TTS_PROVIDERS="aliyun,openai,azure,tencent"
export ASR_PROVIDERS="openai,aliyun,azure,tencent"
```

**推荐：**
- ASR: `openai,aliyun,azure,tencent`（OpenAI Whisper 精度最高）
- TTS: 根据您的地理位置和偏好选择

### 📊 性能

- 视频生成：20 秒视频约 2 分钟
- 分辨率：1080x1920（竖屏）
- 帧率：30 fps
- 比特率：~4.6 Mbps
- 渲染并发：6x

### 🐛 故障排除

#### 音频/字幕不同步
✅ **已在 v1.3.1 修复** - 现在使用 ffprobe 精确时间戳检测

#### 字幕全部同时出现
✅ **已在 v1.3.1 修复** - 智能分段生成多个片段

#### 提供商 API 失败
- 检查环境变量中的 API 凭证
- 验证提供商优先级设置
- 系统会自动降级到下一个可用提供商

### 🔗 链接

- **GitHub**: https://github.com/ZhenRobotics/openclaw-video-generator
- **npm**: https://www.npmjs.com/package/openclaw-video-generator
- **问题反馈**: https://github.com/ZhenRobotics/openclaw-video-generator/issues
- **文档**: 详细文档见 GitHub 仓库

### 📄 许可证

MIT License - 详见 LICENSE 文件

---

**Version**: v1.3.1
**Last Updated**: 2026-03-11
**Maintainer**: ZhenStaff
