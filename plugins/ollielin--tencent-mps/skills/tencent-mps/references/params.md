# 参数参考文档

## 目录

- [通用参数](#通用参数所有脚本)
- [音视频/图片处理类通用参数](#音视频--图片处理类脚本通用参数)
- [AIGC 类通用参数](#aigc-类脚本通用参数)
- [转码参数 mps_transcode.py](#转码脚本参数-mps_transcodepy)
- [视频增强参数 mps_enhance.py](#视频增强参数-mps_enhancepy)
- [智能字幕参数 mps_subtitle.py](#智能字幕参数-mps_subtitlepy)
- [去字幕擦除参数 mps_erase.py](#智能去字幕与擦除参数-mps_erasepy)
- [图片处理参数 mps_imageprocess.py](#图片处理参数-mps_imageprocesspy)
- [AIGC 生图参数 mps_aigc_image.py](#aigc-生图参数-mps_aigc_imagepy)
- [AIGC 生视频参数 mps_aigc_video.py](#aigc-生视频参数-mps_aigc_videopy)
- [COS 文件上传参数 mps_cos_upload.py](#cos-文件上传参数-mps_cos_uploadpy)
- [COS 文件下载参数 mps_cos_download.py](#cos-文件下载参数-mps_cos_downloadpy)

---

## 通用参数（所有脚本）

| 参数 | 说明 |
|------|------|
| `--help` | 显示完整的帮助文档 |
| `--dry-run` | 仅打印请求参数，不实际调用 API |
| `--region` | 腾讯云区域，默认 `ap-guangzhou` |

## 音视频 / 图片处理类脚本通用参数

适用脚本：`mps_transcode.py`、`mps_enhance.py`、`mps_subtitle.py`、`mps_erase.py`、`mps_imageprocess.py`

| 参数 | 说明 |
|------|------|
| `--url` | 输入文件的 URL 地址 |
| `--cos-object` | COS 输入对象路径（使用环境变量中的 Bucket） |
| `--cos-bucket` | 指定输入 COS Bucket（覆盖环境变量） |
| `--cos-region` | 指定输入 COS 区域 |
| `--output-bucket` | 输出 COS Bucket |
| `--output-region` | 输出 COS Bucket 区域（默认取环境变量） |
| `--output-dir` | 输出目录，默认 `/output/` |
| `--output-object-path` | 输出文件路径模板，如 `/output/{inputName}_transcode.{format}`（适用：`mps_transcode.py`、`mps_enhance.py`、`mps_subtitle.py`、`mps_erase.py`） |
| `--output-path` | 输出文件路径模板（仅适用：`mps_imageprocess.py`） |
| `--notify-url` | 任务完成回调 URL（**仅适用音视频脚本**：`mps_transcode.py`、`mps_enhance.py`、`mps_subtitle.py`、`mps_erase.py`；**不适用** `mps_imageprocess.py`） |
| `--no-wait` | 仅提交任务，不等待结果（返回 TaskId 后退出） |
| `--poll-interval` | 轮询间隔（秒），音视频类默认 `10`，图片处理默认 `5` |
| `--max-wait` | 最长等待时间（秒），音视频类默认 `600`，图片处理默认 `300` |

## AIGC 类脚本通用参数

适用脚本：`mps_aigc_image.py`、`mps_aigc_video.py`

| 参数 | 说明 |
|------|------|
| `--no-wait` | 仅提交任务，不等待结果 |
| `--task-id` | 查询已有任务的结果 |
| `--poll-interval` | 轮询间隔（秒），生图默认 5，生视频默认 10 |
| `--max-wait` | 最长等待时间（秒），生图默认 300，生视频默认 600 |
| `--cos-bucket-name` | 结果存储 COS Bucket（可选，不配置则使用 MPS 临时存储 12 小时） |
| `--cos-bucket-region` | 结果存储 COS 区域 |
| `--cos-bucket-path` | 结果存储 COS 路径前缀 |
| `--operator` | 操作者名称（可选） |

## 转码脚本参数（mps_transcode.py）

| 参数 | 说明 |
|------|------|
| `--codec` | 视频编码格式：`h264`、`h265`（默认）、`h266`、`av1`、`vp9` |
| `--container` | 封装格式：`mp4`（默认）、`hls`、`flv`、`mp3`、`m4a` |
| `--width` / `--height` | 输出分辨率（像素） |
| `--bitrate` | 视频码率（kbps） |
| `--fps` | 帧率 |
| `--audio-codec` | 音频编码：`aac`（默认）、`mp3`、`copy` |
| `--audio-bitrate` | 音频码率（kbps），默认 128 |
| `--compress-type` | 压缩策略：`ultra_compress`（极致压缩）、`standard_compress`（综合最优）、`high_compress`（码率优先）、`low_compress`（画质优先） |
| `--scene-type` | 视频场景：`normal`（通用）、`pgc`（高清影视）、`ugc`（UGC短视频）、`materials_video`（素材）、`e-commerce_video`（电商）、`educational_video`（教育） |

## 视频增强参数（mps_enhance.py）

| 参数 | 说明 |
|------|------|
| `--template` | **大模型增强专用模板 ID（327001~327020），优先级最高，指定后忽略 --preset 等增强参数**。按场景和分辨率细分，内置降噪+超分+综合增强，开箱即用：<br>• **真人场景（Real）**：适合真人实拍，保护人脸与文字区域 → `327001`(720P) `327003`(1080P) `327005`(2K) `327007`(4K)<br>• **漫剧场景（Anime）**：适合动漫风格，增强线条色块特征 → `327002`(720P) `327004`(1080P) `327006`(2K) `327008`(4K)<br>• **抖动优化（JitterOpt）**：减少帧间抖动与纹理跳变 → `327009`(720P) `327010`(1080P) `327011`(2K) `327012`(4K)<br>• **细节最强（DetailMax）**：最大化纹理细节还原 → `327013`(720P) `327014`(1080P) `327015`(2K) `327016`(4K)<br>• **人脸保真（FaceFidelity）**：最大程度保留人脸五官细节 → `327017`(720P) `327018`(1080P) `327019`(2K) `327020`(4K) |
| `--preset` | 预设模式（自定义参数模式，与 `--template` 互斥）：`diffusion`（大模型）、`comprehensive`（综合）、`artifact`（去毛刺/去伪影） |
| `--diffusion-type` | 大模型增强强度：`strong`、`normal`（默认）、`weak` |
| `--comprehensive-type` | 综合增强强度：`strong`、`normal`、`weak`（默认） |
| `--artifact-type` | 去毛刺强度：`strong`、`weak`（默认） |
| `--scene-type` | 增强场景：`common`、`AIGC`、`short_play`、`short_video`、`game`、`HD_movie_series`、`LQ_material`、`lecture` |
| `--super-resolution` | 启用超分辨率（2倍）。**不可与大模型增强同时使用** |
| `--sr-type` | 超分类型：`lq`（低清晰度有噪声，默认）、`hq`（高清晰度） |
| `--sr-size` | 超分倍数，目前仅支持 `2` |
| `--denoise` | 启用降噪。**不可与大模型增强同时使用** |
| `--denoise-type` | 降噪强度：`weak`（默认）、`strong` |
| `--color-enhance` | 启用色彩增强 |
| `--color-enhance-type` | 色彩增强强度：`weak`（默认）、`normal`、`strong` |
| `--scratch-repair` | 划痕修复强度（浮点数 0.0~1.0，如 `0.5`、`0.8`），适合老片修复 |
| `--low-light-enhance` | 启用低光照增强 |
| `--hdr` | HDR 模式：`HDR10`、`HLG` |
| `--frame-rate` | 目标帧率（插帧），如 `60` |
| `--audio-denoise` | 启用音频降噪 |
| `--audio-separate` | 音频分离：`vocal`（提取人声）、`background`（提取背景声）、`accompaniment`（提取伴奏） |
| `--volume-balance` | 启用音量均衡 |
| `--volume-balance-type` | 音量均衡类型：`loudNorm`（响度标准化，默认）、`gainControl`（减小突变） |
| `--audio-beautify` | 启用音频美化（杂音去除 + 齿音压制） |
| `--codec` | 输出视频编码：`h264`、`h265`（默认）、`h266`、`av1`、`vp9` |
| `--width` | 输出视频宽度/长边（像素），如 `1920` |
| `--height` | 输出视频高度/短边（像素），`0` 表示按比例缩放 |
| `--bitrate` | 输出视频码率（kbps），`0` 表示自动 |
| `--fps` | 输出视频帧率（Hz），`0` 表示保持原始 |
| `--container` | 输出封装格式：`mp4`（默认）、`hls`、`flv` |
| `--audio-codec` | 输出音频编码：`aac`（默认）、`mp3`、`copy` |
| `--audio-bitrate` | 输出音频码率（kbps），默认 `128` |

## 智能字幕参数（mps_subtitle.py）

| 参数 | 说明 |
|------|------|
| `--process-type` | 识别方式：`asr`（语音识别，默认）、`ocr`（图像识别）、`translate`（纯字幕翻译，不做识别） |
| `--src-lang` | 源语言。**ASR 模式**：`zh`（简体中文）、`en`（英语）、`ja`（日语）、`ko`（韩语）、`zh-PY`（中英粤）、`yue`（粤语）、`zh_dialect`（中文方言）、`prime_zh`（中英方言）、`vi`（越南语）、`ms`（马来语）、`id`（印尼语）、`th`（泰语）、`fr`（法语）、`de`（德语）、`es`（西班牙语）、`pt`（葡萄牙语）、`ru`（俄语）、`ar`（阿拉伯语）等；**OCR 模式**：`zh_en`（中英，默认）、`multi`（多语种） |
| `--translate` | 翻译目标语言，支持多语言用 `/` 分隔，如 `en/ja`。支持：`zh`（中文）、`en`（英语）、`ja`（日语）、`ko`（韩语）、`fr`（法语）、`es`（西班牙语）、`de`（德语）、`it`（意大利语）、`ru`（俄语）、`pt`（葡萄牙语）、`ar`（阿拉伯语）、`th`（泰语）、`vi`（越南语）、`id`（印尼语）、`ms`（马来语）、`tr`（土耳其语）、`nl`（荷兰语）、`pl`（波兰语）、`sv`（瑞典语）等 30+ 种语言 |
| `--subtitle-type` | 字幕语言类型：`0`=源语言、`1`=翻译语言、`2`=双语（有翻译时默认） |
| `--subtitle-format` | 字幕文件格式：`vtt`（默认）、`srt`、`original` |
| `--hotwords-id` | ASR 热词库 ID，提高专业术语识别准确率，如 `hwd-xxxxx` |
| `--ocr-area` | OCR 识别区域（百分比坐标 0~1），格式 `x1,y1,x2,y2`，可多次指定 |
| `--sample-width` | 示例视频/图片的宽度（像素），配合 `--ocr-area` 使用，帮助 OCR 精确定位区域 |
| `--sample-height` | 示例视频/图片的高度（像素），配合 `--ocr-area` 使用 |
| `--template` | 智能字幕预设模板 ID（如 `110167`），不指定则使用自定义参数模式 |

## 智能去字幕与擦除参数（mps_erase.py）

| 参数 | 说明 |
|------|------|
| `--template` | 预设模板：`101`（去字幕，默认）、`102`（去字幕+OCR提取）、`201`（去水印高级版）、`301`（人脸模糊）、`302`（人脸+车牌模糊） |
| `--method` | 擦除方式：`auto`（AI自动识别，默认）、`custom`（指定区域直接擦除） |
| `--model` | 擦除模型：`standard`（默认）、`area`（区域模型，适合花体/阴影字幕） |
| `--position` | 区域预设（仅模板 101/102 支持）：`top`、`bottom`、`left`、`right`、`center`、`top-left`、`top-right`、`bottom-left`、`bottom-right`、`top-half`、`bottom-half`、`fullscreen`，共 12 种；不传则默认识别视频**中下部**区域 |
| `--area` | 自动擦除自定义区域，格式 `x1,y1,x2,y2`（0~1 相对坐标），可多次指定 |
| `--custom-area` | 指定区域+时间段擦除，格式 `beginMs,endMs,x1,y1,x2,y2`，可多次指定 |
| `--ocr` | 同时 OCR 提取字幕内容 |
| `--subtitle-lang` | 字幕语言：`zh_en`（中英，默认）、`multi`（多语种） |
| `--subtitle-format` | 字幕文件格式：`vtt`（默认）、`srt` |
| `--translate` | 提取后翻译目标语言（**必须同时开启 `--ocr`**）。支持：`zh`（中文）、`en`（英语）、`ja`（日语）、`ko`（韩语）、`fr`（法语）、`es`（西班牙语）、`it`（意大利语）、`de`（德语）、`tr`（土耳其语）、`ru`（俄语）、`pt`（葡萄牙语）、`vi`（越南语）、`id`（印尼语）、`ms`（马来语）、`th`（泰语）、`ar`（阿拉伯语）、`hi`（印地语），共 17 种 |

## 图片处理参数（mps_imageprocess.py）

| 参数 | 说明 |
|------|------|
| `--super-resolution` | 启用超分辨率（2 倍） |
| `--sr-type` | 超分类型：`lq`（低清晰度有噪声，默认）、`hq`（高清晰度） |
| `--advanced-sr` | 启用高级超分 |
| `--adv-sr-type` | 高级超分类型：`standard`（通用，默认）、`super`（高级super）、`ultra`（高级ultra） |
| `--sr-mode` | 高级超分输出模式：`percent`（倍率）、`aspect`（等比，默认）、`fixed`（固定） |
| `--sr-percent` | 高级超分倍率（配合 `--sr-mode percent`，如 `3.0`） |
| `--sr-width` / `--sr-height` | 高级超分目标宽/高（不超过 4096） |
| `--sr-long-side` | 高级超分目标长边（不超过 4096） |
| `--sr-short-side` | 高级超分目标短边（不超过 4096） |
| `--denoise` | 降噪强度：`weak`（轻度）、`strong`（强力） |
| `--quality-enhance` | 综合增强强度：`weak`（轻度）、`normal`（中度）、`strong`（强力） |
| `--color-enhance` | 色彩增强：`weak`、`normal`、`strong` |
| `--sharp-enhance` | 细节增强（0.0~1.0） |
| `--face-enhance` | 人脸增强强度（0.0~1.0） |
| `--lowlight-enhance` | 启用低光照增强 |
| `--beauty` | 美颜效果，格式 `类型:强度`（强度 0~100），可多次指定。口红可附加颜色值：`FaceFeatureLipsLut:50:#ff0000`。类型：`Whiten`（美白）、`BlackAlpha1`（美黑）、`BlackAlpha2`（较强美黑）、`FoundationAlpha2`（粉白）、`Clear`（清晰度）、`Sharpen`（锐化）、`Smooth`（磨皮）、`BeautyThinFace`（瘦脸）、`NatureFace`（自然脸型）、`VFace`（V脸）、`EnlargeEye`（大眼）、`EyeLighten`（亮眼）、`RemoveEyeBags`（祛眼袋）、`ThinNose`（瘦鼻）、`RemoveLawLine`（祛法令纹）、`CheekboneThin`（瘦颧骨）、`FaceFeatureLipsLut`（口红）、`ToothWhiten`（牙齿美白）、`FaceFeatureSoftlight`（柔光）、`Makeup`（美妆），共 20 种 |
| `--filter` | 滤镜效果，格式 `类型:强度`，如 `Qingjiaopian:70`。类型：`Dongjing`（东京）、`Qingjiaopian`（轻胶片）、`Meiwei`（美味） |
| `--erase-detect` | 自动擦除类型（可多选）：`logo`（图标）、`text`（文字）、`watermark`（水印） |
| `--erase-area` | 指定擦除区域（像素坐标），格式 `x1,y1,x2,y2`，可多次指定 |
| `--erase-box` | 指定擦除区域（百分比坐标 0~1），格式 `x1,y1,x2,y2`，可多次指定 |
| `--erase-area-type` | 指定区域擦除的类型：`logo`（图标，默认）、`text`（文字） |
| `--add-watermark` | 添加盲水印，指定水印文字（最多 4 字节，约 1 个中文字或 4 个 ASCII 字符，超出会被截断） |
| `--extract-watermark` | 提取盲水印 |
| `--remove-watermark` | 移除盲水印 |
| `--resize-percent` | 百分比缩放倍率（如 `2.0` 表示放大 2 倍） |
| `--resize-mode` | 缩放模式：`percent`、`mfit`、`lfit`、`fill`、`pad`、`fixed` |
| `--resize-width` / `--resize-height` | 目标宽/高（像素） |
| `--resize-long-side` | 目标长边（像素），未指定宽高时使用 |
| `--resize-short-side` | 目标短边（像素），未指定宽高时使用 |
| `--format` | 输出格式：`WebP`、`JPEG`、`PNG`、`BMP` |
| `--quality` | 输出质量（1~100） |
| `--definition` | 图片处理模板 ID（使用预设模板时指定） |
| `--schedule-id` | 编排场景 ID：`30000`（文字水印擦除）、`30010`（图片扩展）、`30100`（换装） |
| `--resource-id` | 资源 ID（默认为账号主资源 ID） |

## AIGC 生图参数（mps_aigc_image.py）

| 参数 | 说明 |
|------|------|
| `--model` | 模型：`Hunyuan`（默认）、`GEM`、`Qwen` |
| `--model-version` | 模型版本，如 GEM `2.5` / `3.0` |
| `--prompt` | 图片描述文本（最多 1000 字符），未传参考图时必填 |
| `--negative-prompt` | 反向提示词，描述不希望出现在图片中的内容（部分模型支持） |
| `--enhance-prompt` | 开启提示词增强，自动优化 prompt 以提升生成质量 |
| `--aspect-ratio` | 宽高比：`1:1`、`3:2`、`2:3`、`4:3`、`3:4`、`4:5`、`5:4`、`9:16`、`16:9`、`21:9` 等 |
| `--resolution` | 分辨率：`720P`、`1080P`、`2K`、`4K` |
| `--image-url` | 参考图片 URL（可多次指定，GEM 最多 3 张；图生图） |
| `--image-ref-type` | 参考类型（与 `--image-url` 一一对应）：`asset`（素材参考）、`style`（风格参考） |

## AIGC 生视频参数（mps_aigc_video.py）

| 参数 | 说明 |
|------|------|
| `--model` | 模型：`Hunyuan`（默认）、`Hailuo`、`Kling`、`Vidu`、`OS`、`GV` |
| `--model-version` | 模型版本，如 Kling `2.5`/`O1`，Hailuo `2.3`，Vidu `q2-pro` |
| `--scene-type` | 场景类型（部分模型支持）：`motion_control`（Kling 动作控制）、`land2port`（横转竖）、`template_effect`（Vidu 特效模板） |
| `--prompt` | 视频描述文本（最多 2000 字符），未传图片时必填 |
| `--negative-prompt` | 反向提示词，描述不希望出现在视频中的内容（部分模型支持） |
| `--enhance-prompt` | 开启提示词增强，自动优化 prompt 以提升生成质量 |
| `--duration` | 视频时长（秒） |
| `--resolution` | 分辨率：`720P`、`1080P`、`2K`、`4K` |
| `--aspect-ratio` | 宽高比：`16:9`、`9:16`、`1:1`、`4:3`、`3:4`、`3:2`、`2:3`、`4:5`、`5:4`、`21:9` 等 |
| `--no-logo` | 去除水印/Logo（Hailuo/Kling/Vidu 支持） |
| `--enable-bgm` | 启用背景音乐（部分模型版本支持） |
| `--enable-audio` | 是否为视频生成音频（GV/OS 支持，默认 `true`） |
| `--image-url` | 首帧图片 URL（图生视频） |
| `--last-image-url` | 尾帧图片 URL（首尾帧生视频，部分模型支持） |
| `--ref-image-url` | 多图参考 URL（可多次指定，GV/Vidu 支持，最多 3 张） |
| `--ref-image-type` | 参考类型（与 `--ref-image-url` 一一对应）：`asset`（素材参考）、`style`（风格参考） |
| `--ref-video-url` | 参考视频 URL（仅 Kling O1 支持） |
| `--ref-video-type` | 参考视频类型：`feature`（特征参考）、`base`（待编辑视频，默认） |
| `--keep-original-sound` | 保留原声：`yes`、`no` |
| `--off-peak` | 错峰模式（仅 Vidu），任务 48 小时内生成 |
| `--additional-params` | JSON 格式附加参数，用于传递模型专属扩展参数。如 Kling 的相机控制（**仅 Kling 支持**）：`'{"camera_control":{"type":"simple"}}'` |

## COS 文件上传参数（mps_cos_upload.py）

| 参数 | 说明 |
|------|------|
| `--local-file` / `-f` | 本地文件路径（必填） |
| `--cos-key` / `-k` | COS 对象键（Key），如 `input/video.mp4`（必填），**默认前缀使用 `input/`** |
| `--bucket` / `-b` | COS Bucket 名称（默认使用环境变量 `TENCENTCLOUD_COS_BUCKET`） |
| `--region` / `-r` | COS Bucket 区域（默认使用环境变量 `TENCENTCLOUD_COS_REGION` 或 `ap-guangzhou`） |
| `--secret-id` | 腾讯云 SecretId（默认使用环境变量 `TENCENTCLOUD_SECRET_ID`） |
| `--secret-key` | 腾讯云 SecretKey（默认使用环境变量 `TENCENTCLOUD_SECRET_KEY`） |
| `--verbose` / `-v` | 显示详细日志（文件大小、Bucket、Region、Key、ETag、URL 等） |

## COS 文件下载参数（mps_cos_download.py）

| 参数 | 说明 |
|------|------|
| `--cos-key` / `-k` | COS 对象键（Key），如 `output/result.mp4`（必填） |
| `--local-file` / `-f` | 本地保存路径（必填），建议保存到工作目录 `/data/workspace/` 下 |
| `--bucket` / `-b` | COS Bucket 名称（默认使用环境变量 `TENCENTCLOUD_COS_BUCKET`） |
| `--region` / `-r` | COS Bucket 区域（默认使用环境变量 `TENCENTCLOUD_COS_REGION` 或 `ap-guangzhou`） |
| `--secret-id` | 腾讯云 SecretId（默认使用环境变量 `TENCENTCLOUD_SECRET_ID`） |
| `--secret-key` | 腾讯云 SecretKey（默认使用环境变量 `TENCENTCLOUD_SECRET_KEY`） |
| `--verbose` / `-v` | 显示详细日志（Bucket、Region、Key、本地路径、文件大小、URL 等） |
