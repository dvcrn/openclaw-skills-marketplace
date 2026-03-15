## 主要接口入参与含义

> 这里只列出最常用、最重要的字段，长尾参数（例如各种蒙版细节字段）按功能“成组”说明，避免文档过长。完整字段列表以 `app.py` 与对应的 `*_impl.py` 为准。

Base URL 与鉴权约定见：[auth_and_env.md](./auth_and_env.md) 与 [api_endpoints.md](./api_endpoints.md)。

---

### 1. 草稿相关

#### `POST /create_draft`

| 字段      | 必填 | 类型   | 默认值 | 含义                         |
|-----------|------|--------|--------|------------------------------|
| width     | 否   | int    | 1080   | 画布宽度（像素）             |
| height    | 否   | int    | 1920   | 画布高度（像素）             |
| cover     | 否   | string | -      | 封面图片 URL                 |
| name      | 否   | string | -      | 草稿名称                     |

返回：`output.draft_id`、`output.draft_url`（可在剪映/CapCut 打开）。

#### `POST /query_script`

| 字段        | 必填 | 类型   | 默认值 | 含义                 |
|-------------|------|--------|--------|----------------------|
| draft_id    | 是   | string | -      | 草稿 ID              |
| force_update| 否   | bool   | true   | 是否强制刷新后再读取 |

返回：`output` 为工程脚本 JSON 字符串。

#### `POST /generate_draft_url`

| 字段     | 必填 | 类型   | 含义   |
|----------|------|--------|--------|
| draft_id | 是   | string | 草稿 ID |

返回：`output.draft_url`。

---

### 2. 媒体与时间线

#### `POST /add_video`

最常用字段：

| 字段           | 必填 | 类型    | 默认值     | 含义                                   |
|----------------|------|---------|------------|----------------------------------------|
| draft_id       | 是   | string  | -          | 草稿 ID                                |
| video_url      | 是   | string  | -          | 视频素材 URL                           |
| track_name     | 否   | string  | video_main | 放入的轨道名                           |
| start          | 否   | float   | 0          | 从源视频的什么时间开始裁剪（秒）       |
| end            | 否   | float   | 视频末尾   | 从源视频的什么时间结束裁剪（秒）       |
| target_start   | 否   | float   | 轨道末尾   | 放到时间线的什么时间点（秒）           |
| speed          | 否   | float   | 1.0        | 播放速度                               |
| volume         | 否   | float   | 1.0        | 音量（相对）                           |
| transition     | 否   | string  | -          | 与前一个片段的转场类型（见枚举接口）   |
| transition_duration | 否 | float | -         | 转场时长（秒）                         |

常见变换类字段（按需选用）：

- 位置与缩放：`transform_x`, `transform_y`, `transform_x_px`, `transform_y_px`, `scale_x`, `scale_y`, `rotation`
- 透明度与翻转：`alpha`, `flip_horizontal`
- 蒙版：`mask_type`, `mask_center_x`, `mask_center_y`, `mask_size`, `mask_rotation`, `mask_feather`, `mask_invert`, `mask_rect_width`, `mask_round_corner`
- 背景与混合：`background_blur`, `mix_type`

#### `POST /add_audio`

| 字段              | 必填 | 类型    | 默认值     | 含义                                   |
|-------------------|------|---------|------------|----------------------------------------|
| draft_id          | 是   | string  | -          | 草稿 ID                                |
| audio_url         | 是   | string  | -          | 音频素材 URL                           |
| track_name        | 否   | string  | audio_main | 放入的轨道名                           |
| start             | 否   | float   | 0          | 从源音频的什么时间开始裁剪（秒）       |
| end               | 否   | float   | 音频末尾   | 从源音频的什么时间结束裁剪（秒）       |
| target_start      | 否   | float   | 轨道末尾   | 放到时间线的什么时间点（秒）           |
| volume            | 否   | float   | 1.0        | 音量                                   |
| speed             | 否   | float   | 1.0        | 播放速度                               |
| fade_in_duration  | 否   | float   | 0          | 淡入时长（秒）                         |
| fade_out_duration | 否   | float   | 0          | 淡出时长（秒）                         |
| effect_type       | 否   | string  | -          | 单个音效类型（配合 effect_params）     |
| effect_params     | 否   | object  | -          | 音效参数（内部会组装到 sound_effects） |

#### `POST /add_image`

| 字段           | 必填 | 类型    | 默认值      | 含义                                       |
|----------------|------|---------|-------------|--------------------------------------------|
| draft_id       | 是   | string  | -           | 草稿 ID                                    |
| image_url      | 是   | string  | -           | 图片素材 URL                               |
| track_name     | 否   | string  | image_main  | 放入的轨道名                               |
| start          | 否   | float   | 0           | 出现在时间线的开始时间（秒）               |
| end            | 否   | float   | 3           | 结束时间（秒）                             |
| intro_animation| 否   | string  | -           | 入场动画类型（见 `get_intro_animation_types`） |
| intro_animation_duration | 否 | float | -       | 入场动画时长（秒）                         |
| outro_animation| 否   | string  | -           | 出场动画类型                               |
| outro_animation_duration | 否 | float | -       | 出场动画时长（秒）                         |
| combo_animation| 否   | string  | -           | 组合动画类型（见 `get_combo_animation_types`） |
| combo_animation_duration | 否 | float | -       | 组合动画时长（秒）                         |
| transition     | 否   | string  | -           | 与上一段的转场类型                         |
| transition_duration | 否| float | -           | 转场时长                                   |
| mask_type      | 否   | string  | -           | 蒙版类型（如“矩形”、“圆形”）               |
| mask_center_x  | 否   | float   | 0           | 蒙版中心 X                                 |
| mask_center_y  | 否   | float   | 0           | 蒙版中心 Y                                 |
| mask_size      | 否   | float   | 0.5         | 蒙版大小                                   |
| mask_rotation  | 否   | float   | 0           | 蒙版旋转                                   |
| mask_feather   | 否   | float   | 0           | 蒙版羽化 (0-100)                           |
| mask_invert    | 否   | bool    | false       | 蒙版翻转                                   |
| mask_rect_width| 否   | float   | -           | 矩形蒙版宽度                               |
| mask_round_corner| 否 | float   | 0           | 矩形蒙版圆角 (0-100)                       |
| background_blur| 否   | int     | -           | 背景模糊档位 (1-4, 仅 main 轨道生效)       |
| alpha          | 否   | float   | 1.0         | 透明度                                     |
| flip_horizontal| 否   | bool    | false       | 镜像翻转                                   |
| rotation       | 否   | float   | 0           | 旋转角度                                   |
| mix_type       | 否   | string  | -           | 混合模式（如“正片叠底”）                   |

变换与蒙版字段与 `add_video` 类似。

#### `POST /add_subtitle`

| 字段       | 必填 | 类型    | 默认值   | 含义                                          |
|------------|------|---------|----------|-----------------------------------------------|
| draft_id   | 是   | string  | -        | 草稿 ID                                       |
| srt        | 是   | string  | -        | SRT 内容（或可被解析为 SRT 的文本/URL）      |
| time_offset| 否   | float   | 0        | 整体时间偏移（秒）                            |
| track_name | 否   | string  | subtitle | 字幕轨道名                                    |

样式类字段（可选）：`font`, `font_size`, `bold`, `italic`, `underline`, `font_color`, `alpha`，以及边框/背景/位置/缩放/旋转等。

#### `POST /add_text`

| 字段        | 必填 | 类型    | 默认值      | 含义                             |
|-------------|------|---------|-------------|----------------------------------|
| draft_id    | 是   | string  | -           | 草稿 ID                          |
| text        | 是   | string  | -           | 文本内容                         |
| start       | 是   | float   | -           | 出现时间（秒）                   |
| end         | 是   | float   | -           | 结束时间（秒）                   |
| track_name  | 否   | string  | text_main   | 文本轨道名                       |
| font        | 否   | string  | -           | 字体（见 `get_font_types`）      |
| font_color  | 否   | string  | "#FFFFFF"   | 字体颜色                         |
| font_size   | 否   | float   | 5.0         | 字号                             |
| font_alpha  | 否   | float   | 1.0         | 文本不透明度                     |
| align       | 否   | string  | center      | 对齐方式（left/center/right）   |
| vertical    | 否   | bool    | false       | 是否垂直显示                     |
| background_color | 否 | string | "#000000" | 背景颜色                         |
| background_alpha | 否 | float  | 0.0       | 背景透明度                       |
| background_round_radius | 否 | float | 0.0 | 背景圆角 (0-1)                  |
| border_color| 否   | string  | "#000000"   | 描边颜色                         |
| border_width| 否   | float   | 0.0         | 描边宽度                         |
| shadow_enabled | 否 | bool   | false       | 是否启用阴影                     |
| shadow_color| 否   | string  | "#000000"   | 阴影颜色                         |
| shadow_distance| 否| float   | 5.0         | 阴影距离                         |
| shadow_angle| 否   | float   | -45.0       | 阴影角度                         |
| intro_animation | 否 | string | -          | 入场动画                         |
| intro_duration  | 否 | float  | -          | 入场动画时长                     |
| outro_animation | 否 | string | -          | 出场动画                         |
| outro_duration  | 否 | float  | -          | 出场动画时长                     |
| loop_animation  | 否 | string | -          | 循环动画                         |
| loop_duration   | 否 | float  | -          | 循环动画时长                     |
| text_styles     | 否 | array  | -          | 多样式文本设置（见示例）         |
| effect_effect_id| 否 | string | -          | 花字效果 ID                      |
| bubble_effect_id| 否 | string | -          | 气泡效果 ID                      |

#### 其他接口（入参模式类似）

- `POST /add_text_template`：关键字段 `template_id`（模板 ID）、`texts`（占位文本数组）、`start`、`end`、`draft_id`、`track_name`。
- `POST /add_preset`：关键字段 `preset_id`、`replacements`（占位内容替换）、`start`、`draft_id`，可选 `target_start`、变换/蒙版/音量等。
- `POST /add_sticker`：关键字段 `sticker_id`、`draft_id`、`start`、`end`，可选位置、缩放、翻转等。
- `POST /add_video_keyframe`：支持单个或批量关键帧；关键字段 `draft_id`、`track_name`、`property_type(s)`、`time(s)`、`value(s)`。
- `POST /add_effect`：关键字段 `effect_type`（见 `get_video_scene_effect_types` 或 `get_video_character_effect_types`）、`effect_category`、`start`、`end`、`draft_id`。
- `POST /add_filter`：关键字段 `filter_type`（见 `get_filter_types`）、`start`、`end`、`draft_id`、`intensity`。

---

### 3. 渲染相关

#### `POST /generate_video`

| 字段        | 必填 | 类型    | 默认值 | 含义                                        |
|-------------|------|---------|--------|---------------------------------------------|
| draft_id    | 是   | string  | -      | 草稿 ID                                     |
| resolution  | 否   | string  | 720P   | 分辨率（如 `720P`、`1080P`）                |
| framerate   | 否   | string  | "24"   | 帧率（字符串形式，如 `"24"`、`"30"`）       |
| license_key | 否   | string  | -      | 授权/计费用的 License Key（如启用计费）    |

返回：`output.task_id`，用于后续查询任务状态。

#### `POST /task_status`

| 字段   | 必填 | 类型   | 含义             |
|--------|------|--------|------------------|
| task_id| 是   | string | 渲染任务 ID      |

返回：状态信息（如 `status`、`progress`、结果 URL 等）。

---

### 4. 工具接口

#### `GET /get_filter_types`

获取支持的滤镜名称列表。
返回：`output` (list of dicts), 每个元素含 `name`（如“奶油”、“复古工业”）。
用于 `add_filter` 时，设置 `filter_type` 为列表中的名称。

#### `GET /get_font_types`

返回：`output` (list of strings)，可用字体名称列表。

#### `GET /get_audio_effect_types`

获取支持的音效类型列表（如“麦霸”、“萝莉”等）。
返回结构体包含 `name` (音效名), `type` (类别), 和 `params` (参数定义，如最大最小值)。

#### `GET /get_video_scene_effect_types`

获取支持的场景特效名称列表。
返回：`output` (list of dicts), 每个元素含 `name`。
用于 `add_effect` 时，设置 `effect_category="scene"`，`effect_type` 为列表中的名称。

#### `GET /get_video_character_effect_types`

获取支持的人物特效名称列表。
返回：`output` (list of dicts), 每个元素含 `name`。
用于 `add_effect` 时，设置 `effect_category="character"`，`effect_type` 为列表中的名称。

#### `POST /get_duration`

获取音视频文件的时长，常用于音画对齐。

| 字段 | 必填 | 类型   | 含义        |
|------|------|--------|-------------|
| url  | 是   | string | 音/视频文件 URL |

返回：
- `output.duration`: 时长（秒，浮点数）
- `output.video_url`: 返回原始 URL


---

### 5. 高级能力

#### `POST /generate_image`

调用 AI 生成图片并自动添加到草稿。支持文生图、图生图（参考图）。

| 字段           | 必填 | 类型   | 含义                                         |
|----------------|------|--------|----------------------------------------------|
| prompt         | 是   | string | 图片生成提示词                               |
| model          | 否   | string | 模型名称 (默认 `nano_banana`)。可选：`nano_banana`, `nano_banana_pro`, `jimeng-4.5` |
| reference_image| 否   | string | 参考图 URL (图生图/重绘时使用)               |
| size           | 否   | string | 图片分辨率 (如 "1024x1024", 需符合模型支持的比例) |
| draft_id       | 否   | string | 草稿 ID（若不传则创建新草稿）                |
| track_name     | 否   | string | 轨道名称                                     |
| ...            | 否   | -      | 支持大部分 `add_image` 的剪辑参数(transform, mask等) |

**模型支持的分辨率说明：**
- **nano_banana / nano_banana_pro**: 支持 `1024x1024 (1:1)`, `768x1344 (9:16)`, `1344x768 (16:9)` 等多种比例。
- **jimeng-4.5**: 支持 1K/2K/4K 分辨率，如 `1024x1024`, `2048x2048`, `4096x4096` 等。

返回：`output.image_url`、`output.draft_id`。

#### `POST /generate_ai_video`

调用 AI 模型生成视频。这是一个异步任务。

| 字段          | 必填 | 类型   | 含义                                         |
|---------------|------|--------|----------------------------------------------|
| prompt        | 是   | string | 视频生成提示词                               |
| model         | 是   | string | 模型名称：`veo3.1`, `veo3.1-pro` |
| resolution    | 否   | string | 分辨率 (如 `1080x1920`, `1920x1080`)         |
| image_url     | 否   | string | 首帧参考图 URL                               |
| end_image_url | 否   | string | 尾帧参考图 URL                               |
| ref_images    | 否   | array  | 多张参考图 URL 列表 (部分模型支持)           |
| duration      | 否   | int    | 生成时长 (秒，仅部分模型如 sora2 支持)       |
| draft_id      | 否   | string | (可选) 若生成后需自动添加到草稿              |
| ...           | 否   | -      | 支持大部分 `add_video` 的剪辑参数            |

**模型能力说明：**
- **veo3.1 / veo3.1-pro**: 支持首帧、首尾帧、多图参考。分辨率支持 `1080x1920`, `1920x1080`, `720x1280`, `1280x720`。不支持 `duration`。
- **jimeng-video-3.0**: 支持首尾帧。
- **sora2**: 支持 `duration` (如 10秒)。

返回：`task_id`。需通过 `POST /task_status` 轮询结果。

#### `POST /generate_speech`

TTS 语音合成，并将音频添加到草稿。

| 字段        | 必填 | 类型   | 含义                                     |
|-------------|------|--------|------------------------------------------|
| text        | 是   | string | 要朗读的文本                             |
| provider    | 否   | string | TTS 提供商。可选：`azure`, `minimax`, `doubao`, `fish` |
| model       | 否   | string | 模型 (仅 minimax 需要，如 `speech-2.6-turbo`) |
| voice_id    | 是   | string | 音色 ID (见下文说明)                     |
| volume      | 否   | float  | 音量 (默认 1.0)                          |
| speed       | 否   | float  | 语速 (默认 1.0)                          |
| draft_id    | 否   | string | 草稿 ID                                  |
| target_start| 否   | float  | 插入时间点                               |

**音色 ID 说明 (voice_id)：**
更多常用音色列表请参考：[voice_list.md](./voice_list.md)

- **azure**: 如 `zh-CN-XiaoxiaoNeuralFemale` (晓晓), `zh-CN-YunjianNeuralMale` (云健)。
- **minimax**: 如 `audiobook_male_1`, `audiobook_female_1`。需配合 `model` 使用。
- **doubao (火山/剪映)**: 如 `zh_female_tianxinxiaomei_emo_v2_mars_bigtts` (甜心小美), `zh_male_guangzhoudege_emo_mars_bigtts` (广州德哥)。
- **fish**: 使用 32 位 UUID，如 `54a5170264694bfc8e9ad98df7bd89c3` (丁真)。

返回：`output.audio_url`、`output.draft_id`。

#### `POST /remove_bg`

对视频进行智能抠像（移除背景），并生成“原视频+蒙版视频”的组合预设添加到草稿。
注意：此接口会消耗较多资源/点数。

| 字段           | 必填 | 类型   | 含义                                         |
|----------------|------|--------|----------------------------------------------|
| video_url      | 是   | string | 视频 URL                                     |
| draft_id       | 否   | string | 草稿 ID                                      |
| speed          | 否   | float  | 播放速度 (默认 1.0)                          |
| transform_y    | 否   | float  | Y 轴位移                                     |
| scale_x        | 否   | float  | X 轴缩放                                     |
| scale_y        | 否   | float  | Y 轴缩放                                     |
| license_key    | 否   | string | 授权 Key                                     |

返回：`output.mask_url`、`output.inverted_mask_url`、`output.draft_id`。

#### `POST /search_sticker`

搜索在线贴纸素材。

| 字段     | 必填 | 类型   | 默认值 | 含义             |
|----------|------|--------|--------|------------------|
| keywords | 是   | string | -      | 搜索关键词       |
| count    | 否   | int    | 50     | 返回数量         |
| offset   | 否   | int    | 0      | 翻页偏移         |

返回：`output.data`（列表），每项包含：
- `sticker_id`: 贴纸 ID（用于 `/add_sticker`）
- `title`: 贴纸标题
- `sticker.preview_cover`: 预览图 URL

---

### 6. AI 相关接口（简要）

#### `POST /deepseek`

| 字段         | 必填 | 类型   | 默认值 | 含义                       |
|--------------|------|--------|--------|----------------------------|
| user_prompt  | 是   | string | -      | 用户输入                   |
| system_prompt| 否   | string | -      | 系统提示词                 |
| json_format  | 否   | bool   | false  | 是否要求模型输出 JSON      |

#### `POST /gemini` 与 `POST /gemini_with_fallback`

字段与 `deepseek` 类似，额外可选：

- `online`：bool，是否启用联网搜索。

这两个接口通常用于生成文案、镜头脚本、字幕文本等，上层再用本文件中列出的 HTTP 接口去真正修改/生成视频。
