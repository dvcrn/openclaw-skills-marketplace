---
name: human-avatar
description: "使用阿里云 DashScope/灵眸 API 生成人脸口播视频（talking head video）。支持三种模式：EMO（人像+音频驱动口播，两步流程）、AA/Animate Anyone（全身动画）、灵眸（基于模板的数字人口播视频）。当用户需要制作口播视频、数字人视频、EMO/AA 人脸动画、VideoRetalk 视频换人时触发此技能。"
---

# Human Avatar — 阿里云口播视频生成

## 三种模式

| 模式 | 接口 | 认证 | Region | 说明 |
|------|------|------|--------|------|
| **EMO** | DashScope | `DASHSCOPE_API_KEY` | **cn-beijing** | 人像+音频→口播，需先 detect |
| **AA** (Animate Anyone) | DashScope | `DASHSCOPE_API_KEY` | **cn-beijing** | 人像+动作视频→全身动画 |
| **灵眸** (LingMou) | 独立产品 SDK | AK/SK | **cn-beijing** | 基于模板的数字人口播 |
| **VideoRetalk** (视频换人) | DashScope | `DASHSCOPE_API_KEY` | **cn-beijing** | 视频角色替换 |

> ⚠️ **Region 固定为 cn-beijing**，API Key 需在北京地域开通，不可与新加坡 Key 混用。

## 前置条件

```bash
pip install requests dashscope oss2
# 灵眸额外需要:
pip install alibabacloud-lingmou20250527 alibabacloud-tea-openapi
```

环境变量：
```bash
export DASHSCOPE_API_KEY=sk-xxxx          # DashScope API Key（百炼控制台获取）
export ALIBABA_CLOUD_ACCESS_KEY_ID=xxx    # 灵眸用
export ALIBABA_CLOUD_ACCESS_KEY_SECRET=xxx
export OSS_BUCKET=xxx                     # 本地文件上传用
export OSS_ENDPOINT=oss-cn-beijing.aliyuncs.com
```

## EMO 工作流（两步）

```
Step 1: emo-detect-v1 检测人脸 → 获取 face_bbox, ext_bbox
  ↓
Step 2: emo-v1 提交生成 → task_id
  ↓
轮询 GET /api/v1/tasks/{task_id} → SUCCEEDED → video_url
```

```bash
python scripts/portrait_animate.py \
  --image-url "https://example.com/portrait.jpg" \
  --audio-url "https://example.com/speech.mp3" \
  --download
```

## 灵眸工作流（基于模板）

```
1. 查询模板列表 → templateId（已存 digital_human_template.json）
2. CreateBroadcastVideoFromTemplate (variables 替换 text_content)
3. 轮询 ListBroadcastVideosById → SUCCESS → videoURL
```

```bash
python scripts/avatar_video.py \
  --template-id "BS1b2WNnRMu4ouRzT4clY9Jhg" \
  --text "大家好，欢迎收看今天的科技新闻。" \
  --download
```

## 一键 Demo Pipeline

```bash
# EMO
python scripts/demo_pipeline.py --mode emo --image ./face.jpg --audio ./speech.mp3 --download

# AA
python scripts/demo_pipeline.py --mode aa --model <AA_MODEL_NAME> --image-url https://... --video-url https://... --download

# 灵眸
python scripts/demo_pipeline.py --mode lingmou --template-id BSxxxx --text "大家好" --download
```

## API 参考

- **EMO** (emo-detect + emo-v1): [references/emo-api.md](references/emo-api.md)
- **AA** (Animate Anyone): [references/aa-api.md](references/aa-api.md)
- **灵眸** (LingMou): [references/lingmou-api.md](references/lingmou-api.md)
- **OSS 上传**: [references/oss-upload.md](references/oss-upload.md)

## 图片/音频要求

| 参数 | EMO 要求 |
|------|---------|
| 图片格式 | jpg/jpeg/png/bmp/webp |
| 图片分辨率 | 最小边 ≥400px，最大边 ≤7000px |
| 单人正面 | 必须，面部完整无遮挡 |
| 音频格式 | mp3/wav |
| 音频大小 | ≤15MB |
| 音频时长 | ≤60s，需清晰人声（去背景噪音） |
| URL 类型 | 必须是公网 HTTP/HTTPS（不支持 file:// 本地路径） |
