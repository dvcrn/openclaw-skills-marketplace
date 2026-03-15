# 脚本详细示例

## 1. 极速高清转码 — `mps_transcode.py`

```bash
# 最简用法：URL 输入 + 默认模板（100305，极速高清-H265-MP4-1080P）
python scripts/mps_transcode.py --url https://example.com/video.mp4

# COS 输入
python scripts/mps_transcode.py --cos-object /input/video/test.mp4

# 自定义参数：H265 编码 + 1080P + 3000kbps + 30fps
python scripts/mps_transcode.py --url https://example.com/video.mp4 \
    --codec h265 --width 1920 --height 1080 --bitrate 3000 --fps 30

# 极致压缩（ultra_compress）：最大程度压缩码率，适合带宽敏感场景
python scripts/mps_transcode.py --url https://example.com/video.mp4 --compress-type ultra_compress

# HLS 切片（用于流媒体播放）
python scripts/mps_transcode.py --url https://example.com/video.mp4 --container hls

# 综合最优（standard_compress）：平衡画质与码率，适合大多数场景
python scripts/mps_transcode.py --url https://example.com/video.mp4 --compress-type standard_compress

# 码率优先（high_compress）：在保证可接受画质的前提下尽量降低码率
python scripts/mps_transcode.py --url https://example.com/video.mp4 --compress-type high_compress

# 画质优先（low_compress）：在保证画质的前提下适度压缩，适合存档
python scripts/mps_transcode.py --url https://example.com/video.mp4 --compress-type low_compress

# 提交后查询任务状态（循环直到 FINISH）
python scripts/mps_get_video_task.py --task-id <TaskId>
```

## 2. 视频增强 — `mps_enhance.py`

```bash
# 默认增强（预设模板 321002）
python scripts/mps_enhance.py --url https://example.com/video.mp4

# ===== 大模型增强专用模板（327001~327020，推荐优先使用） =====

# 真人场景 - 升至 720P（适合真人实拍，保护人脸与文字区域）
python scripts/mps_enhance.py --url https://example.com/video.mp4 --template 327001

# 真人场景 - 升至 1080P（推荐用于真人实拍视频）
python scripts/mps_enhance.py --url https://example.com/video.mp4 --template 327003

# 真人场景 - 升至 2K
python scripts/mps_enhance.py --url https://example.com/video.mp4 --template 327005

# 真人场景 - 升至 4K（超高清修复）
python scripts/mps_enhance.py --url https://example.com/video.mp4 --template 327007

# 漫剧场景 - 升至 720P（适合动漫风格，增强线条色块特征）
python scripts/mps_enhance.py --url https://example.com/video.mp4 --template 327002

# 漫剧场景 - 升至 1080P
python scripts/mps_enhance.py --url https://example.com/video.mp4 --template 327004

# 漫剧场景 - 升至 2K
python scripts/mps_enhance.py --url https://example.com/video.mp4 --template 327006

# 漫剧场景 - 升至 4K（推荐用于动漫视频超清修复）
python scripts/mps_enhance.py --url https://example.com/video.mp4 --template 327008

# 抖动优化 - 升至 1080P（减少帧间抖动与纹理跳变）
python scripts/mps_enhance.py --url https://example.com/video.mp4 --template 327010

# 抖动优化 - 升至 4K
python scripts/mps_enhance.py --url https://example.com/video.mp4 --template 327012

# 细节最强 - 升至 1080P（最大化纹理细节还原）
python scripts/mps_enhance.py --url https://example.com/video.mp4 --template 327014

# 细节最强 - 升至 4K（极致细节修复）
python scripts/mps_enhance.py --url https://example.com/video.mp4 --template 327016

# 人脸保真 - 升至 720P（最大程度保留人脸五官细节）
python scripts/mps_enhance.py --url https://example.com/video.mp4 --template 327017

# 人脸保真 - 升至 1080P（推荐用于人像/写真/访谈视频）
python scripts/mps_enhance.py --url https://example.com/video.mp4 --template 327018

# 人脸保真 - 升至 2K（推荐用于高清人像修复）
python scripts/mps_enhance.py --url https://example.com/video.mp4 --template 327019

# 人脸保真 - 升至 4K（超高清人脸修复）
python scripts/mps_enhance.py --url https://example.com/video.mp4 --template 327020

# ===== 自定义参数模式（灵活组合增强能力） =====

# 大模型增强（效果最强）
python scripts/mps_enhance.py --url https://example.com/video.mp4 --preset diffusion --diffusion-type strong

# 综合增强（平衡效果与效率）
python scripts/mps_enhance.py --url https://example.com/video.mp4 --preset comprehensive --comprehensive-type normal

# 去毛刺/去伪影（针对压缩产生的伪影修复）
python scripts/mps_enhance.py --url https://example.com/video.mp4 --preset artifact --artifact-type strong

# 超分 + 降噪 + 色彩增强（注意：--super-resolution 和 --denoise 不可与 --preset diffusion 同时使用）
python scripts/mps_enhance.py --url https://example.com/video.mp4 --super-resolution --denoise --color-enhance

# HDR + 插帧 60fps
python scripts/mps_enhance.py --url https://example.com/video.mp4 --hdr HDR10 --frame-rate 60

# 音频分离：提取人声（去除背景音乐）
python scripts/mps_enhance.py --url https://example.com/video.mp4 --audio-separate vocal

# 音频分离：提取背景声（去除人声）
python scripts/mps_enhance.py --url https://example.com/video.mp4 --audio-separate background

# 音频分离：提取伴奏（去除人声，保留音乐）
python scripts/mps_enhance.py --url https://example.com/video.mp4 --audio-separate accompaniment

# 音频增强：降噪 + 音量均衡 + 美化
python scripts/mps_enhance.py --url https://example.com/video.mp4 --audio-denoise --volume-balance --audio-beautify

# 输出编码控制：增强后输出为 H264 + 720P
python scripts/mps_enhance.py --url https://example.com/video.mp4 --preset comprehensive \
    --codec h264 --width 1280 --height 720

# 输出编码控制：增强后输出为 H265 + 1080P + 指定码率
python scripts/mps_enhance.py --url https://example.com/video.mp4 --super-resolution \
    --codec h265 --width 1920 --height 1080 --bitrate 4000

# 提交后查询任务状态（循环直到 FINISH）
python scripts/mps_get_video_task.py --task-id <TaskId>
```

## 3. 智能字幕 — `mps_subtitle.py`

```bash
# ASR 识别字幕（默认）
python scripts/mps_subtitle.py --url https://example.com/video.mp4

# ASR + 翻译为英文（双语字幕）
python scripts/mps_subtitle.py --url https://example.com/video.mp4 --src-lang zh --translate en

# OCR 识别硬字幕 + 翻译
python scripts/mps_subtitle.py --url https://example.com/video.mp4 --process-type ocr --src-lang zh_en --translate en

# 多语言翻译（英文+日文）
python scripts/mps_subtitle.py --url https://example.com/video.mp4 --src-lang zh --translate en/ja

# 提交后查询任务状态（循环直到 FINISH）
python scripts/mps_get_video_task.py --task-id <TaskId>
```

## 4. 智能去字幕与擦除 — `mps_erase.py`

```bash
# 自动擦除中下部字幕（默认模板 101）
python scripts/mps_erase.py --url https://example.com/video.mp4

# 去字幕并提取OCR字幕（模板 102）
python scripts/mps_erase.py --url https://example.com/video.mp4 --template 102

# 去水印-高级版（模板 201）
python scripts/mps_erase.py --url https://example.com/video.mp4 --template 201

# 人脸模糊（模板 301）
python scripts/mps_erase.py --url https://example.com/video.mp4 --template 301

# 人脸和车牌模糊（模板 302）
python scripts/mps_erase.py --url https://example.com/video.mp4 --template 302

# 强力擦除（区域模型，适合花体/阴影字幕）
python scripts/mps_erase.py --url https://example.com/video.mp4 --model area

# 使用区域预设 — 顶部字幕
python scripts/mps_erase.py --url https://example.com/video.mp4 --position top

# 使用区域预设 — 底部字幕
python scripts/mps_erase.py --url https://example.com/video.mp4 --position bottom

# 使用区域预设 — 右侧竖排字幕
python scripts/mps_erase.py --url https://example.com/video.mp4 --position right

# 使用区域预设 — 左下方字幕
python scripts/mps_erase.py --url https://example.com/video.mp4 --position bottom-left

# 使用区域预设 — 全屏幕
python scripts/mps_erase.py --url https://example.com/video.mp4 --position fullscreen

# 自定义区域（画面顶部0~25%区域）
python scripts/mps_erase.py --url https://example.com/video.mp4 --area 0,0,1,0.25

# 多区域擦除（顶部 + 底部都有字幕）
python scripts/mps_erase.py --url https://example.com/video.mp4 --area 0,0,1,0.15 --area 0,0.75,1,1

# 去字幕 + OCR 提取 + 翻译为英文
python scripts/mps_erase.py --url https://example.com/video.mp4 --ocr --translate en

# 去字幕 + OCR 提取 + 翻译为日文
python scripts/mps_erase.py --url https://example.com/video.mp4 --ocr --translate ja

# 提交后查询任务状态（循环直到 FINISH）
python scripts/mps_get_video_task.py --task-id <TaskId>
```

**区域预设（--position）说明**：

| 预设值 | 说明 | 坐标范围 |
|--------|------|----------|
| `fullscreen` | 全屏幕 | (0,0)~(0.9999,0.9999) |
| `top-half` | 上半屏幕 | (0,0)~(0.9999,0.5) |
| `bottom-half` | 下半屏幕 | (0,0.5)~(0.9999,0.9999) |
| `center` | 屏幕中间 | (0.1,0.3)~(0.9,0.7) |
| `left` | 屏幕左边 | (0,0)~(0.5,0.9999) |
| `right` | 屏幕右边 | (0.5,0)~(0.9999,0.9999) |
| `top` | 屏幕顶部 | (0,0)~(0.9999,0.25) |
| `bottom` | 屏幕底部 | (0,0.75)~(0.9999,0.9999) |
| `top-left` | 屏幕左上方 | (0,0)~(0.5,0.5) |
| `top-right` | 屏幕右上方 | (0.5,0)~(0.9999,0.5) |
| `bottom-left` | 屏幕左下方 | (0,0.5)~(0.5,0.9999) |
| `bottom-right` | 屏幕右下方 | (0.5,0.5)~(0.9999,0.9999) |

## 5. 图片处理 — `mps_imageprocess.py`

```bash
# 超分辨率 2 倍放大
python scripts/mps_imageprocess.py --url https://example.com/image.jpg --super-resolution

# 高级超分至 4K
python scripts/mps_imageprocess.py --url https://example.com/image.jpg --advanced-sr --sr-width 3840 --sr-height 2160

# 降噪 + 色彩增强 + 细节增强
python scripts/mps_imageprocess.py --url https://example.com/image.jpg \
    --denoise weak --color-enhance normal --sharp-enhance 0.8

# 综合增强（画质整体提升）
python scripts/mps_imageprocess.py --url https://example.com/image.jpg --quality-enhance normal

# 综合增强 + 超分（强力修复低质量图片）
python scripts/mps_imageprocess.py --url https://example.com/image.jpg --quality-enhance strong --super-resolution

# 美颜（美白 + 瘦脸 + 大眼）
python scripts/mps_imageprocess.py --url https://example.com/image.jpg \
    --beauty Whiten:50 --beauty BeautyThinFace:30 --beauty EnlargeEye:40

# 自动擦除水印
python scripts/mps_imageprocess.py --url https://example.com/image.jpg --erase-detect watermark

# 添加盲水印（水印文字最多 4 字节，约 1 个中文字或 4 个 ASCII 字符，超出会被截断）
python scripts/mps_imageprocess.py --url https://example.com/image.jpg --add-watermark "MPS"

# 转为 WebP 格式 + 质量 80
python scripts/mps_imageprocess.py --url https://example.com/image.jpg --format WebP --quality 80

# 滤镜（轻胶片风格，强度 70）
python scripts/mps_imageprocess.py --url https://example.com/image.jpg --filter Qingjiaopian:70

# 滤镜（东京风格）
python scripts/mps_imageprocess.py --url https://example.com/image.jpg --filter Dongjing:80

# 缩放（百分比放大 2 倍）
python scripts/mps_imageprocess.py --url https://example.com/image.jpg --resize-percent 2.0

# 缩放（等比缩放至宽 800 高 600 以内）
python scripts/mps_imageprocess.py --url https://example.com/image.jpg --resize-mode lfit --resize-width 800 --resize-height 600

# 缩放（指定长边为 1920，等比缩放）
python scripts/mps_imageprocess.py --url https://example.com/image.jpg --resize-long-side 1920

# 提交后查询任务状态（循环直到 FINISH）
python scripts/mps_get_image_task.py --task-id <TaskId>
```

## 6. 查询音视频处理任务 — `mps_get_video_task.py`

```bash
# 查询任务状态（简洁输出）
python scripts/mps_get_video_task.py --task-id 1234567890-WorkflowTask-80108cc3380155d98b2e3573a48a

# 详细输出（含子任务信息）
python scripts/mps_get_video_task.py --task-id 1234567890-WorkflowTask-80108cc3380155d98b2e3573a48a --verbose

# JSON 格式输出（便于程序解析）
python scripts/mps_get_video_task.py --task-id 1234567890-WorkflowTask-80108cc3380155d98b2e3573a48a --json

# 指定地域
python scripts/mps_get_video_task.py --task-id 1234567890-WorkflowTask-80108cc3380155d98b2e3573a48a --region ap-beijing
```

## 7. 查询图片处理任务 — `mps_get_image_task.py`

```bash
# 查询任务状态（简洁输出）
python scripts/mps_get_image_task.py --task-id 1234567890-ImageTask-80108cc3380155d98b2e3573a48a

# 详细输出（含子任务信息）
python scripts/mps_get_image_task.py --task-id 1234567890-ImageTask-80108cc3380155d98b2e3573a48a --verbose

# JSON 格式输出（便于程序解析）
python scripts/mps_get_image_task.py --task-id 1234567890-ImageTask-80108cc3380155d98b2e3573a48a --json

# 指定地域
python scripts/mps_get_image_task.py --task-id 1234567890-ImageTask-80108cc3380155d98b2e3573a48a --region ap-beijing
```

## 8. AIGC 智能生图 — `mps_aigc_image.py`

```bash
# 文生图（Hunyuan 默认）
python scripts/mps_aigc_image.py --prompt "一只可爱的橘猫在阳光下打盹"

# GEM 3.0 + 反向提示词 + 16:9 + 2K
python scripts/mps_aigc_image.py --prompt "赛博朋克城市夜景" --model GEM --model-version 3.0 \
    --negative-prompt "人物" --aspect-ratio 16:9 --resolution 2K

# 图生图（参考图片 + 描述）
python scripts/mps_aigc_image.py --prompt "将这张照片变成油画风格" \
    --image-url https://example.com/photo.jpg

# GEM 多图参考（最多3张，支持 asset/style 参考类型）
python scripts/mps_aigc_image.py --prompt "融合这些元素" --model GEM \
    --image-url https://example.com/img1.jpg --image-ref-type asset \
    --image-url https://example.com/img2.jpg --image-ref-type style

# 仅提交任务不等待
python scripts/mps_aigc_image.py --prompt "产品海报" --no-wait

# 查询任务结果
python scripts/mps_aigc_image.py --task-id <task-id>
```

## 9. AIGC 智能生视频 — `mps_aigc_video.py`

```bash
# 文生视频（Hunyuan 默认）
python scripts/mps_aigc_video.py --prompt "一只猫在阳光下伸懒腰"

# Kling 2.5 + 10秒 + 1080P + 16:9 + 去水印 + BGM
python scripts/mps_aigc_video.py --prompt "赛博朋克城市" --model Kling --model-version 2.5 \
    --duration 10 --resolution 1080P --aspect-ratio 16:9 --no-logo --enable-bgm

# 图生视频（首帧图片 + 描述）
python scripts/mps_aigc_video.py --prompt "让画面动起来" \
    --image-url https://example.com/photo.jpg

# 首尾帧生视频（GV 模型）
python scripts/mps_aigc_video.py --prompt "过渡动画" --model GV \
    --image-url https://example.com/start.jpg --last-image-url https://example.com/end.jpg

# GV 多图参考生视频（最多 3 张，支持 asset/style 参考类型）
python scripts/mps_aigc_video.py --prompt "融合风格生成视频" --model GV \
    --ref-image-url https://example.com/img1.jpg --ref-image-type asset \
    --ref-image-url https://example.com/img2.jpg --ref-image-type style

# Kling O1 参考视频 + 保留原声
python scripts/mps_aigc_video.py --prompt "将视频风格化" --model Kling --model-version O1 \
    --ref-video-url https://example.com/video.mp4 --ref-video-type base --keep-original-sound yes

# Vidu 错峰模式
python scripts/mps_aigc_video.py --prompt "自然风景" --model Vidu --off-peak

# 仅提交任务不等待
python scripts/mps_aigc_video.py --prompt "宣传片" --no-wait

# 查询任务结果
python scripts/mps_aigc_video.py --task-id <task-id>
```

## 10. COS 文件上传 — `mps_cos_upload.py`

```bash
# 最简用法：上传本地文件到 COS（使用环境变量中的 bucket）
python scripts/mps_cos_upload.py --local-file ./video.mp4 --cos-key input/video.mp4

# 显示详细日志（文件大小、Bucket、Region、Key、ETag、URL）
python scripts/mps_cos_upload.py --local-file ./video.mp4 --cos-key input/video.mp4 --verbose

# 指定 bucket 和 region（覆盖环境变量）
python scripts/mps_cos_upload.py --local-file ./video.mp4 --cos-key input/video.mp4 \
    --bucket mybucket-125xxx --region ap-guangzhou

# 上传图片文件
python scripts/mps_cos_upload.py --local-file ./photo.jpg --cos-key input/photo.jpg --verbose

# 使用自定义密钥（覆盖环境变量）
python scripts/mps_cos_upload.py --local-file ./video.mp4 --cos-key input/video.mp4 \
    --secret-id AKIDxxx --secret-key xxxxx

# 上传到自定义路径（非 input/ 前缀）
python scripts/mps_cos_upload.py --local-file ./my-video.mp4 --cos-key skills/tencent-mps_2.6.zip
```

## 11. COS 文件下载 — `mps_cos_download.py`

```bash
# 最简用法：下载文件到本地（使用环境变量中的 bucket）
python scripts/mps_cos_download.py --cos-key output/result.mp4 --local-file ./result.mp4

# 显示详细日志（Bucket、Region、Key、本地路径、文件大小、URL）
python scripts/mps_cos_download.py --cos-key output/result.mp4 --local-file ./result.mp4 --verbose

# 指定 bucket 和 region（覆盖环境变量）
python scripts/mps_cos_download.py --cos-key output/result.mp4 --local-file ./result.mp4 \
    --bucket mybucket-125xxx --region ap-guangzhou

# 下载到工作目录（推荐路径）
python scripts/mps_cos_download.py --cos-key output/enhanced.mp4 --local-file /data/workspace/enhanced.mp4 --verbose

# 下载图片处理结果
python scripts/mps_cos_download.py --cos-key output/photo-enhanced.jpg --local-file ./photo-enhanced.jpg

# 使用自定义密钥（覆盖环境变量）
python scripts/mps_cos_download.py --cos-key output/result.mp4 --local-file ./result.mp4 \
    --secret-id AKIDxxx --secret-key xxxxx
```
