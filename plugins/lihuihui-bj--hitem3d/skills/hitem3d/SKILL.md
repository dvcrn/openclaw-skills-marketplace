---
name: hitem3d
description: "Generate production-grade 3D models from one or multiple images with Hitem3D. Use when users ask to turn photos, concept art, product shots, or portraits into 3D models; request STL/GLB/OBJ/FBX/USDZ exports; run batch image-to-3D jobs; tune model version, resolution, generation mode, or face count; or check Hitem3D credit balance."
---

# Hitem3D — 一句话，图片变 3D

把 AI 3D 生成能力直接装进对话流：发图即生成，不用切网页或应用。

## 执行流程

1. 先确认环境变量：`HITEM3D_AK`、`HITEM3D_SK`。
2. 识别任务类型：单图、多视角、批量、人像、余额查询。
3. 与用户确认关键参数（模型、分辨率、格式、生成模式、面数）。
4. 提交生成任务并轮询状态，完成后返回下载结果与参数摘要。
5. 失败时给出明确重试建议（更换模型/分辨率/输入图质量）。

## 参数与能力

- **模型版本（5）**：通用 `v1.5` / `v2.0`，人像 `portrait-v1.5` / `portrait-v2.0` / `portrait-v2.1`
- **分辨率（4）**：`512^3`、`768^3`、`1024^3`、`1536Pro^3`
- **输出格式（5）**：`GLB`、`OBJ`、`STL`、`FBX`、`USDZ`
- **生成模式（3）**：纯几何、分步贴图、一步到位
- **面数范围**：`100K`–`2M` polygons
- **多视角输入**：最多 4 张（正/背/左/右）

## 典型请求映射

- “把这张椅子照片变成 3D 模型” → 单图 + 默认参数
- “用 STL，我要 3D 打印” → 输出格式 `STL`
- “把 designs/ 30 张图转 GLB” → 批量模式 + 输出 `GLB`
- “以人像模式生成这张头像” → `portrait-*` 模型
- “查还剩多少积分” → 余额查询

## 成本参考

- 低配：`5 credits`/次（`v1.5` + `512^3` + 几何）≈ `$0.10`
- 默认：`50 credits`/次（`v2.0` + `1536^3` + 纹理）≈ `$1.00`

## 配置

安装后设置：

```bash
export HITEM3D_AK="your_access_key"
export HITEM3D_SK="your_secret_key"
```

在 `hitem3d.ai` 开发者平台创建 API Key。

---

# Hitem3D — Images In, 3D Out

Bring production-grade AI 3D generation directly into the conversation: send images, get ready-to-use 3D assets.

## Workflow

1. Verify credentials: `HITEM3D_AK` and `HITEM3D_SK`.
2. Detect task type: single image, multi-view, batch, portrait, or balance check.
3. Confirm parameters with the user.
4. Submit the job, poll status, and return result links plus a parameter summary.
5. On failure, provide concrete retry suggestions.

## Capability Matrix

- **Model versions (5)**: general `v1.5` / `v2.0`, portrait `v1.5` / `v2.0` / `v2.1`
- **Resolution tiers (4)**: `512^3`, `768^3`, `1024^3`, `1536Pro^3`
- **Output formats (5)**: `GLB`, `OBJ`, `STL`, `FBX`, `USDZ`
- **Generation modes (3)**: geometry-only, staged texturing, all-in-one
- **Custom face count**: `100K`–`2M` polygons
- **Multi-view input**: up to 4 views (front/back/left/right)

## Example Requests

- “Turn this chair photo into a 3D model.”
- “Generate STL, I need 3D printing output.”
- “Convert all images in `designs/` to GLB.”
- “Create a 3D bust in portrait mode from this image.”
- “How many credits do I have left?”

## Pricing Reference

- From `5 credits`/generation (`v1.5`, `512^3`, geometry-only) ≈ `$0.10`
- Default `50 credits`/generation (`v2.0`, `1536^3`, textured) ≈ `$1.00`

## Setup

```bash
export HITEM3D_AK="your_access_key"
export HITEM3D_SK="your_secret_key"
```

Create API keys at the Hitem3D developer platform.
