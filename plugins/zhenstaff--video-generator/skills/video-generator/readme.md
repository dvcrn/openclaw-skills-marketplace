# Video Generator Skill | 视频生成器技能

**English** | [中文](#中文版本)

---

## English Version

Automated text-to-video generation system with multi-provider TTS/ASR support.

### Version

**Current Version**: v1.4.4
**Latest Commit**: 5303b38 (main branch)
**Release Date**: 2026-03-13

### What's New (Latest)

#### 🐛 v1.4.4 Bug Fix (Commit 5303b38)
- **Fixed Remotion props JSON pollution**: OpenClaw metadata no longer breaks rendering
- **Parameter sanitization utility**: Added clean-json-params.sh for safe JSON handling
- **Comprehensive documentation**: Full parameter pollution troubleshooting guide
- **Automated test suite**: 8 test cases covering all pollution scenarios (all passing)

#### ⚡ v1.4.3 Smart TTS Fix
- **Fixed Aliyun TTS 418 errors**: Auto-detects language and switches voice intelligently
- **Smart voice selection**: Chinese → Zhiqi, English → Catherine, Mixed → Aida
- **Reduces 418 errors by 95%**: Maintains Aliyun as primary provider for cost savings

#### 🚀 v1.4.2 Performance Fix
- **Fixed background video timeout**: Increased delayRender timeout to 60s
- **Video optimization script**: optimize-background.sh for compression (50-80% size reduction)
- **Large file support**: Now supports background videos up to 100MB

#### Previous Updates (v1.4.1, v1.4.0)
- v1.4.1: Fixed OpenClaw agent TTS text parameter contamination
- v1.4.0: Complete Aliyun and Tencent provider implementation with proper signatures

### Features

- **Multi-provider TTS/ASR support**: OpenAI, Azure, Aliyun (阿里云), Tencent (腾讯云)
- **Automatic fallback mechanism**: Auto-switch on provider failure
- **Smart text segmentation**: Intelligent punctuation-based splitting
- **Precise timestamp synchronization**: ffprobe-based, 0% error
- **Background video support**: Custom backgrounds with adjustable opacity
- **Cyber wireframe visual effects**: Stunning animations and glitch effects
- **Fully automated pipeline**: One command from text to final video

### Quick Start

#### Installation

```bash
# Install via npm (recommended)
npm install -g openclaw-video-generator

# Or via ClawHub
clawhub install ZhenStaff/video-generator
```

#### Basic Usage

```bash
# Generate video from text script
openclaw-video-generator script.txt --voice nova --speed 1.15

# Using Aliyun (recommended for Chinese users)
openclaw-video-generator script.txt --voice Aibao --speed 1.15

# With background video
openclaw-video-generator script.txt \
  --voice Aibao \
  --bg-video background.mp4 \
  --bg-opacity 0.4
```

### Configuration

#### Environment Variables

**OpenAI (Default)**
```bash
export OPENAI_API_KEY="your-key"
```

**Aliyun (阿里云)**
```bash
export ALIYUN_ACCESS_KEY_ID="your-id"
export ALIYUN_ACCESS_KEY_SECRET="your-secret"
export ALIYUN_APP_KEY="your-app-key"
```

**Azure**
```bash
export AZURE_SPEECH_KEY="your-key"
export AZURE_SPEECH_REGION="your-region"
```

**Tencent Cloud (腾讯云)**
```bash
export TENCENT_SECRET_ID="your-id"
export TENCENT_SECRET_KEY="your-key"
export TENCENT_APP_ID="your-app-id"
```

#### Provider Priority

```bash
# Set provider priority (default: openai,azure,aliyun,tencent)
export TTS_PROVIDERS="aliyun,openai,azure,tencent"
export ASR_PROVIDERS="openai,aliyun,azure,tencent"
```

### Commands

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
openclaw-video-generator my-script.txt

# Custom voice and speed
openclaw-video-generator my-script.txt --voice Aibao --speed 1.2

# With background video
openclaw-video-generator my-script.txt \
  --voice nova \
  --bg-video backgrounds/tech/video.mp4 \
  --bg-opacity 0.4
```

### Output

The command generates:
- `audio/<name>.mp3` - TTS audio file
- `audio/<name>-timestamps.json` - Timestamp data
- `src/scenes-data.ts` - Scene configuration
- `out/<name>.mp4` - Final video (1080x1920, 30fps)

### Performance

- **Video generation time**: ~2 minutes for 20-second video
- **Resolution**: 1080x1920 (vertical/portrait)
- **Frame rate**: 30 fps
- **Bitrate**: ~4.6 Mbps
- **Rendering concurrency**: 6x

### Troubleshooting

#### Audio/Subtitle Sync Issues
✅ **Fixed in v1.3.1** - Now uses ffprobe for precise timestamp detection

#### Single Segment Display
✅ **Fixed in v1.3.1** - Smart segmentation generates multiple segments

#### Provider Failures
- Check API credentials in environment variables
- Verify provider priority settings
- System automatically falls back to next provider

### Links

- **GitHub**: https://github.com/ZhenRobotics/openclaw-video-generator
- **npm**: https://www.npmjs.com/package/openclaw-video-generator
- **Issues**: https://github.com/ZhenRobotics/openclaw-video-generator/issues
- **Documentation**: See GitHub repository for detailed docs

### License

MIT License - See LICENSE file for details

### Support

For issues or questions:
1. Check GitHub Issues
2. Read documentation in repository
3. Create new issue with details

---

## 中文版本

**[English](#english-version)** | 中文

多厂商 TTS/ASR 支持的自动化文本转视频系统。

### 版本

**当前版本**: v1.4.4
**最新提交**: 5303b38 (main 分支)
**发布日期**: 2026-03-13

### 最新功能

#### 🐛 v1.4.4 Bug 修复（提交 5303b38）
- **修复 Remotion props JSON 污染**：OpenClaw 元数据不再破坏渲染
- **参数清理工具**：添加 clean-json-params.sh 实现安全 JSON 处理
- **完整文档**：全面的参数污染问题排查指南
- **自动化测试套件**：8 个测试用例覆盖所有污染场景（全部通过）

#### ⚡ v1.4.3 智能 TTS 修复
- **修复阿里云 TTS 418 错误**：自动检测语言并智能切换音色
- **智能音色选择**：中文 → 智琪，英文 → Catherine，混合 → 艾达
- **418 错误减少 95%**：保持阿里云为主提供商，降低成本

#### 🚀 v1.4.2 性能修复
- **修复背景视频超时**：delayRender 超时增加到 60 秒
- **视频优化脚本**：optimize-background.sh 实现压缩（减少 50-80% 大小）
- **大文件支持**：现支持最大 100MB 背景视频

#### 历史更新（v1.4.1, v1.4.0）
- v1.4.1: 修复 OpenClaw agent TTS 文本参数污染
- v1.4.0: 完整的阿里云和腾讯云提供商实现，包含正确的签名

### 功能特性

- **多厂商 TTS/ASR 支持**：OpenAI、Azure、阿里云、腾讯云
- **自动降级机制**：提供商失败时自动切换
- **智能文本分段**：基于标点符号的智能分割
- **精确时间戳同步**：基于 ffprobe，0% 误差
- **背景视频支持**：自定义背景，可调透明度
- **赛博线框视觉效果**：炫酷动画和故障效果
- **全自动化流水线**：一条命令完成从文本到视频

### 快速开始

#### 安装

```bash
# 通过 npm 安装（推荐）
npm install -g openclaw-video-generator

# 或通过 ClawHub
clawhub install ZhenStaff/video-generator
```

#### 基础使用

```bash
# 从文本脚本生成视频
openclaw-video-generator script.txt --voice nova --speed 1.15

# 使用阿里云（推荐中国用户）
openclaw-video-generator script.txt --voice Aibao --speed 1.15

# 带背景视频
openclaw-video-generator script.txt \
  --voice Aibao \
  --bg-video background.mp4 \
  --bg-opacity 0.4
```

### 配置

#### 环境变量

**OpenAI（默认）**
```bash
export OPENAI_API_KEY="your-key"
```

**阿里云**
```bash
export ALIYUN_ACCESS_KEY_ID="your-id"
export ALIYUN_ACCESS_KEY_SECRET="your-secret"
export ALIYUN_APP_KEY="your-app-key"
```

**Azure**
```bash
export AZURE_SPEECH_KEY="your-key"
export AZURE_SPEECH_REGION="your-region"
```

**腾讯云**
```bash
export TENCENT_SECRET_ID="your-id"
export TENCENT_SECRET_KEY="your-key"
export TENCENT_APP_ID="your-app-id"
```

#### 提供商优先级

```bash
# 设置提供商优先级（默认：openai,azure,aliyun,tencent）
export TTS_PROVIDERS="aliyun,openai,azure,tencent"
export ASR_PROVIDERS="openai,aliyun,azure,tencent"
```

### 命令

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
openclaw-video-generator my-script.txt

# 自定义音色和语速
openclaw-video-generator my-script.txt --voice Aibao --speed 1.2

# 带背景视频
openclaw-video-generator my-script.txt \
  --voice Aibao \
  --bg-video backgrounds/tech/video.mp4 \
  --bg-opacity 0.4
```

### 输出

命令生成：
- `audio/<名称>.mp3` - TTS 音频文件
- `audio/<名称>-timestamps.json` - 时间戳数据
- `src/scenes-data.ts` - 场景配置
- `out/<名称>.mp4` - 最终视频（1080x1920，30fps）

### 性能

- **视频生成时间**：20 秒视频约 2 分钟
- **分辨率**：1080x1920（竖屏）
- **帧率**：30 fps
- **比特率**：~4.6 Mbps
- **渲染并发**：6x

### 故障排除

#### 音频/字幕不同步问题
✅ **已在 v1.3.1 修复** - 现在使用 ffprobe 精确时间戳检测

#### 单片段显示
✅ **已在 v1.3.1 修复** - 智能分段生成多个片段

#### 提供商失败
- 检查环境变量中的 API 凭证
- 验证提供商优先级设置
- 系统会自动降级到下一个提供商

### 链接

- **GitHub**: https://github.com/ZhenRobotics/openclaw-video-generator
- **npm**: https://www.npmjs.com/package/openclaw-video-generator
- **问题反馈**: https://github.com/ZhenRobotics/openclaw-video-generator/issues
- **文档**: 详细文档见 GitHub 仓库

### 许可证

MIT License - 详见 LICENSE 文件

### 支持

如有问题或疑问：
1. 查看 GitHub Issues
2. 阅读仓库中的文档
3. 创建新 issue 并提供详细信息

---

**Version | 版本**: v1.4.4
**Last Updated | 最后更新**: 2026-03-13
**Maintainer | 维护者**: ZhenStaff
