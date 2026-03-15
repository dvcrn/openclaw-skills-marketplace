---
name: vectcut-skill
description: "通过curl 调用 HTTP 服务，自动创建剪映/CapCut 草稿、编排素材/字幕/特效并发起渲染。用户要做AI视频生成或批量剪辑自动化时调用。"
---

# VectCut Skill（AI 视频制作）

这个技能把你的本地服务（curl请求 HTTP 的 API）封装成可复用的 AI 视频制作流程：创建草稿、添加视频/图片/音频/文本/字幕/贴纸/特效/滤镜、发起渲染并轮询任务状态。

## 适用场景

- 你想“给我做一个 X 主题的短视频”，并希望直接产出可在剪映/CapCut 打开的草稿或渲染任务
- 你已有素材 URL（视频/图片/音频），想自动排版、加字幕、转场、特效与滤镜
- 你在做批量视频生产，希望用固定流程批量生成草稿或渲染任务

## 前置条件

- 服务通过 HTTP 提供，无需在文档中涉及本地 Python 启动命令；

- 服务地址：
  - 远端：`http://open.vectcut.com/cut_jianying`
- 所有请求都必须携带 API Key：
  - Header：`Authorization: Bearer $VECTCUT_API_KEY`
  - VECTCUT_API_KEY要通过环境变量读取，不要把真实 API Key 写入仓库；

在终端统一配置环境变量VECTCUT_API_KEY（仅用于 curl 的 Header 拼接），所有服务都通过 HTTP 请求调用：

```bash
export VECTCUT_BASE_URL="http://open.vectcut.com/cut_jianying"
```

快捷脚本与示例请求体见：

- `scripts/`：命令行调用示例（curl 等）
- `assets/`：示例请求 JSON 与提示词模版
- `references/`：鉴权、端点列表与详细入参与含义（见 `endpoint_params.md`）

## 交互约定（输出格式）

当你使用本技能完成“创建/编辑/渲染”类任务时，输出优先包含这些字段，便于后续继续编辑或查询：

- `draft_id`：草稿 ID
- `draft_url`：可打开的剪映/CapCut 草稿 URL，应封装为 markdown 超链接格式：`[草稿名称](draft_url)`
- `task_id`：云端渲染任务 ID（如果触发了渲染）

## 常用能力（可组合）

### 1) 创建草稿

调用：`POST /create_draft`

示例（1080x1920 竖屏）：

```bash
curl -X POST http://open.vectcut.com/cut_jianying/create_draft \
  -H "Authorization: Bearer $VECTCUT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"width":1080,"height":1920,"name":"demo"}'
```

### 2) 添加素材与时间线编排

你可以按需组合以下操作（都为 `POST` JSON）：

- `/add_video`：添加视频（支持裁切、速度、变换、蒙版、混合、转场等）
- `/add_image`：添加图片（支持入/出场动画、转场、蒙版、混合等）
- `/add_audio`：添加音频（支持音量、变速、淡入淡出、音效等）
- `/add_text`：添加文字（支持字体、描边、阴影、背景、动画、多样式范围等）
- `/add_subtitle`：添加字幕（SRT + 样式）
- `/add_sticker`：添加贴纸
- `/add_effect`：添加特效（scene/character）
- `/add_filter`：添加滤镜
- `/add_video_keyframe`：添加关键帧（如透明度等）
- `/get_video_scene_effect_types`：获取场景特效（用于 effect_category=scene）
- `/get_video_character_effect_types`：获取人物特效（用于 effect_category=character）
- `/get_filter_types`：添加滤镜

### 3) 高级能力（AI 与搜索）

- `/generate_image`：AI 文生图并添加到草稿
- `/generate_ai_video`：AI 文生视频（异步任务）
- `/generate_speech`：TTS 语音合成并添加到草稿
- `/remove_bg`：智能抠像（移除背景）并生成合成预设
- `/search_sticker`：搜索在线贴纸素材

### 4) 获取可用枚举（动画/转场/特效/滤镜/字体）

用于让 AI 在可用范围内选型：

- `GET /get_transition_types`
- `GET /get_mask_types`
- `GET /get_intro_animation_types`、`/get_outro_animation_types`、`/get_combo_animation_types`
- `GET /get_text_intro_types`、`/get_text_outro_types`、`/get_text_loop_anim_types`
- `GET /get_video_scene_effect_types`、`/get_video_character_effect_types`
- `GET /get_filter_types`
- `GET /get_font_types`
- `GET /get_audio_effect_types`

示例（以转场枚举为例）：

```bash
curl -X GET "http://open.vectcut.com/cut_jianying/get_transition_types" \
  -H "Authorization: Bearer $VECTCUT_API_KEY"
```

### 4) 发起渲染并查询状态

- `POST /generate_video`：对草稿 `draft_id` 发起渲染（返回 `task_id`）
- `POST /task_status`：轮询 `task_id` 获取渲染进度与结果

### 5. 典型场景示例

#### 场景 A：成语故事/绘本视频制作（文生图 + 配音 + 自动对齐）

当用户需要制作“亡羊补牢”这样的故事视频时，建议按以下逻辑编排：

1.  **分镜拆解**：将故事拆分为 N 个片段（图片 Prompt + 旁白文本）。
2.  **生成循环**（对每个片段）：
    *   调用 `generate_image` 生成插图，获得 `image_url`。
    *   调用 `generate_speech` 生成配音，获得 `audio_url`。
    *   **关键点**：调用 `get_duration(url=audio_url)` 获取配音时长 `duration`。
    *   调用 `add_image`，将 `image_url` 加入草稿，并设置 `duration` 等于配音时长，确保音画同步。
    *   （如果 `generate_speech` 未自动添加）调用 `add_audio` 添加配音。

参考 Prompt 模板：`assets/prompts/story_creation_zh.md`

#### 场景 B：素材混剪

1) 创建草稿 → 2) add_video/add_audio/add_subtitle → 3) generate_video → 4) task_status 轮询

```bash
curl -X POST http://open.vectcut.com/cut_jianying/create_draft \
  -H "Authorization: Bearer $VECTCUT_API_KEY" \
  -d '{"name":"my short"}'
```

假设返回 `draft_id=xxx` 后：

```bash
curl -X POST http://open.vectcut.com/cut_jianying/add_video \
  -H "Authorization: Bearer $VECTCUT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"draft_id":"xxx","video_url":"https://example.com/a.mp4","start":0,"end":10,"target_start":0}'
```

```bash
curl -X POST http://open.vectcut.com/cut_jianying/add_subtitle \
  -H "Authorization: Bearer $VECTCUT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"draft_id":"xxx","srt":"1\\n00:00:00,000 --> 00:00:02,000\\n你好\\n"}'
```

发起渲染：

```bash
curl -X POST http://open.vectcut.com/cut_jianying/generate_video \
  -H "Authorization: Bearer $VECTCUT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"draft_id":"xxx","resolution":"1080P","framerate":"30"}'
```

轮询：

```bash
curl -X POST http://open.vectcut.com/cut_jianying/task_status \
  -H "Authorization: Bearer $VECTCUT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"task_id":"TASK_ID"}'
```

## 使用提示（让 AI 更“会剪”）

- 让用户提供素材 URL、期望时长、画面比例（9:16/16:9/1:1）、字幕风格、BGM 风格
- 需要严格可控的效果时，先拉取枚举（转场/特效/滤镜/字体），再进行选择与组装
- 复杂需求可以在上层自己组织调用顺序，这里只负责暴露基础视频编辑与渲染接口
