---
name: ai-video-pro
description: "Professional AI video generation with cinematic prompt optimization, auto-detection of optimal generation backends (ComfyUI/LumaAI/Runway/Replicate/DALL-E), and multi-platform publishing to Chinese social platforms (Weibo, Xiaohongshu, Douyin). Analyzes camera language, character dynamics, hit-impact feel, facial expressions, and mecha motion. Beta stage - not for production use."
---

This skill generates professional AI videos with cinematic-quality prompt engineering. It transforms casual user descriptions into film-industry-grade prompts, auto-detects the best available video generation backend, and supports publishing to Chinese social platforms (Weibo, Xiaohongshu, Douyin).

**⚠️ BETA 测试阶段** — 本技能包正在测试中，请勿用于生产环境。

用户提供视频概念、场景描述或创意简报，本技能将优化提示词、选择最佳生成方案、生产视频，并可选择发布到多个平台。

---

## Phase 1: 镜头语言提示词优化引擎

当用户描述想要创建的视频时，在调用任何视频生成 API 之前，必须先执行以下影视级分析流程：

### 1.1 场景分解

将用户描述拆解为结构化的影视元素：

- **镜头类型 (Shot Type)**: 特写(ECU)、近景(CU)、中景(MS)、全景(FS)、远景(WS)、大远景(EWS)、鸟瞰、仰拍、荷兰角、过肩镜头
- **运镜方式 (Camera Movement)**: 固定、横摇(Pan)、纵摇(Tilt)、推轨(Dolly)、跟拍(Tracking)、摇臂(Crane)、手持、斯坦尼康、甩镜(Whip Pan)、变焦拉伸(Rack Focus)
- **灯光设计 (Lighting)**: 主光、补光、轮廓光、伦勃朗光、蝴蝶光、劈裂光、剪影、明暗对比、黄金时刻、霓虹光、体积光
- **色彩分级 (Color Grading)**: 青橙对比、去饱和、高对比、柔和色调、单色、暖色调、冷色调、胶片模拟
- **时间控制 (Temporal)**: 慢动作、延时摄影、正常速度、变速、定格

### 1.2 角色动态分析

对于涉及角色的场景，必须明确建模以下要素：

- **空间关系**: 角色相对位置、距离、朝向
- **动作动态**: 冲击力、动量、加速度（对战斗/动作场景至关重要）
- **打击感 (Hit/Impact Feel)**:
  - 打击的重量感和力度反馈
  - 反应时间和节奏感
  - 冲击形变效果（身体弯曲、衣物飘动）
  - 粒子效果（火花、碎片、冲击波）
  - 画面震动等同效果
- **面部表情渐变**: 镜头时间内的微表情序列变化（如：惊讶 → 坚定 → 胜利）
- **身体语言**: 姿态转换、手势弧线、重心转移
- **机甲/机器人运动**: 关节铰接运动、液压运动、质量惯性、变形序列

### 1.3 缺失元素检测

在最终确定提示词之前，主动检查并向用户询问缺失的关键元素：

**必须询问（如未指定）：**
- 画面比例？(16:9 横屏, 9:16 竖屏适用于抖音, 1:1 方形适用于小红书)
- 目标时长？(3秒/5秒/10秒，取决于生成后端)
- 视觉风格？(写实、动漫、3D渲染、水彩、油画)

**动作场景必须询问（如未指定）：**
- 打击/冲击力度级别？(轻触、重击、影视夸张)
- 是否需要反应特效？(火花、碎片、冲击波、慢动作冲击)
- 被击中角色的状态变化？(倒退、倒地、防御姿态)
- 角色受伤效果？(划痕、破损、变形)
- 场景的情感弧线是什么？

**角色场景必须询问（如未指定）：**
- 镜头起止的面部表情分别是什么？
- 角色的服装以及运动中服装如何交互？
- 角色之间是否有眼神交流？

### 1.4 Provider 适配输出

不同视频生成 API 对 prompt 风格的响应不同，优化后的镜头语言 prompt 需要适配：

- **LumaAI (Dream Machine)**: 偏好自然语言嵌入镜头指令，如 "camera slowly pans", "in the style of"。单次最长5秒
- **Runway Gen-3/Gen-4**: 结构化 prompt 效果更好，分离镜头/主体/风格描述。支持图生视频
- **DALL-E + FFmpeg 管线**: 先生成关键帧图片再插值，适合保持风格一致性
- **Replicate (各模型)**: 按模型调整。Stable Video Diffusion 偏好简洁描述，AnimateDiff 偏好 LoRA 风格标签
- **ComfyUI (本地)**: 基于节点的工作流，需指定 checkpoint + scheduler + sampler

向用户同时展示原始描述和优化后的 prompt，供确认或修改。

---

## Phase 2: 环境自动探测与最优后端选择

在生成视频之前，执行环境检测流程：

### 2.1 环境检测

运行检测脚本：
```bash
python3 scripts/env_detect.py
```

检测内容：
1. **GPU**: NVIDIA (CUDA) / AMD (ROCm) / Apple Silicon (MPS) / 仅CPU
2. **显存**: 可用 GPU 显存（决定本地模型可行性）
3. **已安装工具**: ffmpeg、ComfyUI、Python 包 (torch, diffusers 等)
4. **可用 API 密钥**: 哪些 Provider 凭证已配置
5. **网络**: 互联网连通性、API 端点可达性
6. **磁盘空间**: 可用空间（模型下载需要）

### 2.2 后端选择优先级（最小代价优先）

| 优先级 | 后端 | 条件 | 成本 | 质量 |
|--------|------|------|------|------|
| 1 | ComfyUI 本地 | NVIDIA GPU 8GB+ VRAM | 免费 | 高 |
| 2 | Replicate 免费层 | API Key | 免费(有限) | 中 |
| 3 | LumaAI 免费层 | API Key | 免费(有限) | 高 |
| 4 | Runway 试用额度 | API Key | 免费试用 | 极高 |
| 5 | LumaAI 付费 | API Key + 计费 | ~¥3.5/视频 | 高 |
| 6 | Runway 付费 | API Key + 计费 | ~¥7/视频 | 极高 |
| 7 | DALL-E + FFmpeg | OpenAI Key | ~¥0.5/帧 | 中 |

向用户展示推荐方案及预估成本，获得确认后再继续。

### 2.3 自动安装

如果选定后端需要尚未安装的工具，提供自动安装：
```bash
python3 scripts/install_deps.py --backend <selected_backend>
```

支持安装：
- **ffmpeg**: winget (Windows) / brew (macOS) / apt (Linux)
- **ComfyUI**: git clone + pip install
- **Python 依赖包**: pip install API 客户端库

**始终在安装前征得用户确认。**

---

## Phase 3: 视频生成与预览

### 3.1 生成执行

1. 向用户展示优化后的 prompt 供审批
2. 通过 `scripts/provider_manager.py` 调用选定的 Provider API
3. 展示进度（异步 API 轮询状态）
4. 下载生成的视频到本地工作目录

### 3.2 在线预览

启动本地预览服务器：
```bash
python3 scripts/preview_server.py --file <video_path> --port 8765
```

预览功能：
- 带播放控制的视频播放器
- 逐帧导航
- 多版本并列对比（如果有多次生成）

预览地址: `http://localhost:8765`

### 3.3 迭代优化

如果用户希望修改：
- 基于反馈修改 prompt
- 使用相同或不同的 Provider 重新生成
- 支持图生视频优化（上传关键帧）

---

## Phase 4: 多平台发布

### 4.1 平台规格适配

发布前自动转码至平台要求：

| 平台 | 最大分辨率 | 最大时长 | 最大文件 | 推荐比例 | 格式 |
|------|-----------|---------|---------|---------|------|
| 微博 | 1080p | 15分钟 | 500MB | 16:9, 9:16 | MP4 (H.264) |
| 小红书 | 1080p | 15分钟 | 100MB | 3:4, 1:1, 9:16 | MP4 (H.264) |
| 抖音 | 1080p | 15分钟 | 128MB | 9:16 | MP4 (H.264) |
| 云存储 | 不限 | 不限 | 不限 | 不限 | 不限 |

### 4.2 发布流程

```bash
python3 scripts/publish.py --platform <platform> --mode <draft|publish> --file <video_path>
```

- **草稿模式 (draft)**: 准备元数据和转码，不上传。生成发布就绪的打包文件
- **发布模式 (publish)**: 上传到指定平台（需要平台凭证）
- **云存储模式 (cloud)**: 上传到配置的云存储 (S3/OSS/COS) 并返回分享链接

### 4.3 版本管理

在本地 `.ai-video-pro/projects.json` 维护项目清单：
- 记录所有生成的视频及元数据
- 标记为草稿或已发布
- 记录各平台接收的版本
- 支持更新版本重新发布

---

## 凭证安全

### 环境变量配置

**视频生成（至少配置一个）：**
- `LUMAAI_API_KEY` — LumaAI Dream Machine API
- `RUNWAY_API_KEY` — Runway Gen-3/Gen-4 API
- `REPLICATE_API_TOKEN` — Replicate API
- `OPENAI_API_KEY` — OpenAI DALL-E（用于关键帧生成）

**平台发布（可选）：**
- `WEIBO_ACCESS_TOKEN` — 微博开放平台
- `XHS_COOKIE` — 小红书会话（无官方 API，注意 TOS 风险）
- `DOUYIN_ACCESS_TOKEN` — 抖音开放平台

**安全原则：**
- 所有凭证仅通过环境变量读取，零持久化
- 不记录、不打印、不缓存任何密钥值
- 首次使用时通过最小化测试调用验证密钥有效性
- 如果缺少凭证，引导用户逐步完成设置

### OpenClaw 凭证集成

在 `openclaw.json` 中配置：
```json
{
  "skills": {
    "entries": {
      "ai-video-pro": {
        "apiKey": { "source": "env", "name": "LUMAAI_API_KEY" }
      }
    }
  }
}
```

---

## 错误处理

- 无 API 密钥 → 引导用户逐步设置
- Provider 失败 → 自动降级到下一优先级 Provider
- ffmpeg 缺失 → 提供自动安装
- 网络不可用 → 明确说明哪些操作需要网络
- 视频生成失败 → 展示错误、建议修改 prompt、提供切换 Provider 的选项
- 平台发布失败 → 保存发布就绪的本地包，提供手动上传指引
