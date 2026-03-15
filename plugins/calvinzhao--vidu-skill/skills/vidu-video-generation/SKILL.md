---
name: vidu-video-generation
description: "Generate video with vidu via bundled scripts. Use when the user wants 文生视频, 图生视频, 首尾帧生视频, 参考生视频, 创建主体 (material element), or to submit or check vidu tasks. 创建主体: upload 1–3 images, name and description, call material/elements API. Execution is script-based; run scripts in scripts/ with VIDU_TOKEN set."
---

# Vidu Video Generation Skill

## Execution model: use scripts

**All execution for this skill is done by running the bundled scripts** in `scripts/`. Do not implement the API calls yourself; run the appropriate script and use its output.

- **Submit task**: Run **scripts/run_vidu_generation.py** with the user’s prompt and optional image path(s). It handles upload (if needed) → submit → **returns task_id**. No wait mode; use task_id to query status/result when needed.
- **Query task status/result**: Use **scripts/get_task_result.py** \<task_id\> (or GET `/vidu/v1/tasks/{task_id}`) to get current state and, when success, video URL(s).
- **Task state SSE (流式)**: GET `https://service.vidu.cn/vidu/v1/tasks/state?id={task_id}` is an **SSE** stream. When using this endpoint, **return the SSE output directly to the model** — do not wait for a terminal state. Each event includes `state`, `estimated_time_left`, `err_code`, and **queue_wait_time** (排队预测时间, **unit: minutes**).
- **主体预处理 (script)**: Run **scripts/pre_process_element.py** with `--name` and 1–3 `--image-uri` (ssupload:?id=...); calls POST material/elements/pre-process only, outputs full response including `recaption` (style, description). Use when you need recaption alone or as a step before create_element.
- **创建主体 (script)**: Run **scripts/create_element.py** with `--name`, 1–3 `--image` paths, and optional `--description`/`--style`; uploads images → runs **pre_process_element.py** (required every time) → POSTs to material/elements (uses pre-process recaption when `--description` is omitted), outputs element `id` and `version`.
- **Step-by-step**: If you need to run individual steps, use **scripts/upload_image.py**, **scripts/pre_process_element.py**, **scripts/create_element.py**, **scripts/list_elements.py**, **scripts/submit_task.py**, **scripts/get_task_result.py**, and **scripts/get_upload_url.py** as needed. See scripts/README.md for usage and examples.

Ensure the environment has **VIDU_TOKEN** set. **VIDU_BASE_URL** configures the service domain: **中国大陆** 使用 `https://service.vidu.cn`（默认），**海外/非中国地区** 使用 `https://service.vidu.com`。Scripts require Python 3 and `requests`; see **scripts/README.md** for details.

---

## Overview

Vidu video generation is **asynchronous**: submit a task → get **task_id** → use task_id to **query** task status/result (e.g. get_task_result.py or GET API) when needed. The scripts do not wait; they return task_id after submit.

- **文生视频 (text2video)**: 一段文字。Q3 时长 1–16、宽高比 16:9/9:16/1:1/4:3/3:4、transition pro/speed；Q2 时长 2–8、不传 transition。
- **图生视频 (img2video)**: **一张图 + 一段文字**。宽高比不传（由输入图决定）。Q3 时长 1–16、transition pro/speed；Q2 时长 2–8、transition pro/speed。
- **首尾帧生视频 (headtailimg2video)**: **两张图（首帧、尾帧）+ 一段文字**。Q3 时长 1–16、Q2 时长 2–8，transition pro/speed。
- **参考生视频 (character2video)**: **图 + 主体 + 文字**（可组合）；**文字必填**。**图+主体合计最多 7 个**，至少提供一种（图或主体）。仅 Q2，时长 2–8，**不传 transition**。主体在 prompts 中通过 `type: "material"`、`material.id`、`material.version` 引用。
- **创建主体 (Create element)**: 上传 1–3 张图片，提供主体名称和可选描述；**必须先**调用 **POST** `/vidu/v1/material/elements/pre-process`（即使用户指定了描述也需调用），再调用 **POST** `/vidu/v1/material/elements`；未指定描述时使用 pre-process 返回的 recaption。图片需先经现有上传流程得到 `ssupload:?id=...`。响应含主体 `id` 与 `version`，用于参考生任务。
- **查询主体**: **GET** `/vidu/v1/material/elements/personal`，参数 pager.page、pager.pagesz、keyword、modalities；返回 `elements[].id`、`version`。

详见上方「任务支持列表」与 **references/parameters.md**。

---

## 任务支持列表 (Supported task list)

Before choosing script arguments, ensure the user’s request matches one of the supported task types and constraints below. **references/parameters.md** has the same list for quick lookup.

**模型版本 (Model version)**  
- **Q3** → `model_version: "3.2"`  
- **Q2** → `model_version: "3.1"`

| 任务类型 | type | 输入 | 模型 | 时长(秒) | 宽高比 | 生成模式 transition | 清晰度 |
|----------|------|------|------|----------|--------|----------------------|--------|
| 文生视频 | text2video | 一段文字 | Q3 | 1–16 | 16:9, 9:16, 1:1, 4:3, 3:4 | pro(电影大片), speed(闪电出片) | 1080p |
| 文生视频 | text2video | 一段文字 | Q2 | 2–8 | 16:9, 9:16, 1:1, 4:3, 3:4 | 不传 | 1080p |
| 图生视频 | img2video | **一张图 + 一段文字** | Q3 | 1–16 | **依据输入图片，参数不传** | pro, speed | 1080p |
| 图生视频 | img2video | 一张图 + 一段文字 | Q2 | 2–8 | 依据输入图片，不传 | pro, speed | 1080p |
| 首尾帧生视频 | headtailimg2video | **两张图 + 一段文字** | Q3 | 1–16 | — | pro, speed | 1080p |
| 首尾帧生视频 | headtailimg2video | 两张图 + 一段文字 | Q2 | 2–8 | — | pro, speed | 1080p |
| 参考生视频 | character2video | **图+主体+文字（文字必填；图+主体合计最多7）** | Q2 | 2–8 | — | **不传** | 1080p |

- **文生视频**: 只传文字，`--type text2video`。Q2 时不要传 transition。
- **图生视频**: 仅支持 **1 张图片 + 1 段文字**；宽高比由输入图决定，调用时 **不要传 aspect_ratio**。
- **首尾帧生视频**: 固定 **2 张图 + 1 段文字**，`--type headtailimg2video`；两张图顺序为「首帧、尾帧」。
- **参考生视频**: **图+主体+文字**（文字必填；图+主体合计最多 7），`--type character2video`；仅 Q2，**不要传 transition**。可用 `--image-uri`、`--material "name:id:version"` 组合。

脚本会根据 `--type` 自动省略不该传的参数（如 img2video 不传 aspect_ratio，character2video 不传 transition）。选 type 和 model-version 时请严格按上表。

---

## 创建主体（先 pre-process，再 POST /vidu/v1/material/elements）

创建主体用于在参考生任务中使用的 material element：上传 1–3 张图、名称与描述，接口返回主体 id 与 version。**流程**：**必须先**调用 **POST** `/vidu/v1/material/elements/pre-process`（即使用户指定了描述也需调用；body: `components`, `name`, `type: "user"`），响应中的 `recaption`（style、description）为 vidu 预生成描述；若未特别指定描述，可用该描述填充主体描述；再调用创建主体接口。

- **Pre-process URL**: `{VIDU_BASE_URL}/vidu/v1/material/elements/pre-process`，详见 **references/api_reference.md** §3b。
- **创建主体 URL**: `https://service.vidu.cn/vidu/v1/material/elements`（或 `{VIDU_BASE_URL}/vidu/v1/material/elements`）
- **Method**: POST
- **Headers**: 与现有约定一致（Authorization: Token {token}, Content-Type: application/json, User-Agent）。

**前置条件**: 每张图片先按「Upload images」三步（CreateUpload → PUT to put_url → FinishUpload）得到 `ssupload:?id={id}`；共 1–3 张图。同一张图可复用同一 id 填 `content` 与 `src_img`，或按 API 要求使用不同 id。

**Request body**: `id`（pre-process 响应中的主体 id，创建时必带）, `name`（主体名称）, `modality: "image"`, `type: "user"`, `components`（1–3 个：第一个 `type: "main"`，其余 `type: "auxiliary"`；每项含 `content`、`src_img` 均为 `ssupload:?id=...`，`content_type: "image"`）, `version: "0"`, `recaption: { description, style? }`（可由 pre-process 响应的 recaption 填充）。详见 **references/api_reference.md** §3b、§3c。

**Example**: 见 api_reference。成功响应含 element `id`、`version`，用于参考生任务。

---

## 查询主体（GET /vidu/v1/material/elements/personal）

- **URL**: `https://service.vidu.cn/vidu/v1/material/elements/personal`
- **Method**: GET
- **Query**: `pager.page`（页码）、`pager.pagesz`（每页条数）、`pager.page_token`（可选）、`keyword`（搜索词，URL 编码）、`modalities`（可重复，如 `modalities=image`）。
- **Response**: `elements[]`，每项含 `id`、`name`、`version`、`components`、`recaption` 等；用 `id` 与 `version` 在参考生任务中引用。另有 `next_page_token`。

---

## 参考生任务中引用主体（character2video）

主体**仅可在参考生任务（character2video）**中使用。提交 **POST** `/vidu/v1/tasks` 时：`type: "character2video"`；`input.prompts` 需包含 **(1) 文本 prompt（必填）**；(2) 可选图 prompt（`type: "image"`）；(3) 可选 material prompt（`type: "material"`, `name`, `material: { "id", "version" }`）。可**图+主体+文字**组合，文字必填，**图+主体合计最多 7 个**，至少一种。

**Example**:

```json
{
  "input": {
    "prompts": [
      { "type": "text", "content": "[@艾莉娅]" },
      { "type": "material", "name": "艾莉娅", "material": { "id": "3073530415201165", "version": "1765430214" } }
    ],
    "editor_mode": "normal",
    "enhance": true
  },
  "type": "character2video",
  "settings": { "duration": 5, "resolution": "1080p", "movement_amplitude": "auto", "aspect_ratio": "16:9", "sample_count": 1, "schedule_mode": "normal", "codec": "h265", "model_version": "3.1", "use_trial": false }
}
```

---

## Bundled resources

- **scripts/** — **Use these for all execution.** See **scripts/README.md** for dependency (Python 3, requests), environment (VIDU_TOKEN, VIDU_BASE_URL), and example commands for each script.
- **references/api_reference.md** — Full API contracts (for understanding or when debugging).
- **references/parameters.md** — 任务支持列表与参数约束 (supported task list and parameter constraints).
- **references/errors_and_retry.md** — Error handling (read when interpreting failures).

---

## Workflow (script-based)

1. **Get token and domain**: Ensure **VIDU_TOKEN** is set. Set **VIDU_BASE_URL** by region: mainland China → `https://service.vidu.cn` (default); outside China → `https://service.vidu.com`.

2. **文生视频 (text2video)**  
   `run_vidu_generation.py text2video --prompt "<user text>"`，按任务支持列表加 `--model-version 3.2|3.1`、`--duration`、`--aspect-ratio`、`--transition`（Q2 时不传 transition）。

3. **图生视频 (img2video)**  
   仅 **1 张图 + 1 段文字**。`run_vidu_generation.py img2video --prompt "<user text>" --image <path>`。不要传 `--aspect-ratio`（脚本会省略）。

4. **首尾帧生视频 (headtailimg2video)**  
   **2 张图（首帧、尾帧）+ 1 段文字**。`run_vidu_generation.py headtailimg2video --prompt "<user text>" --image <首帧路径> --image <尾帧路径>`，并加 `--model-version`、`--duration`、`--transition`。

5. **参考生视频 (character2video)**  
   **图+主体+文字**（文字必填；图+主体合计最多 7），仅 Q2。`run_vidu_generation.py character2video --prompt "<user text>" [--image ...] [--material "name:id:version" ...]`（不要传 transition）。

6. **Interpret output**  
   - Script exits 0 and prints **task_id**. Caller uses this task_id to query status/result later (e.g. `get_task_result.py <task_id>` or GET `/vidu/v1/tasks/{task_id}`).
   - Script exits non-zero or prints error JSON to stderr: report failure to the user and, if present, err_code / err_msg.

If you cannot use **run_vidu_generation.py** (e.g. custom body or step-by-step control), run the steps manually in order:

- **Upload images**: `python scripts/upload_image.py <image_path>` for each image; capture the output `ssupload:?id=...`. The same upload flow is used for img2video/headtailimg2video/character2video and for **创建主体** (1–3 images).
- **Get upload resource URL (optional)**: To obtain a public download URL for an uploaded file, run `python scripts/get_upload_url.py <ssupload_uri_or_id>`. **The returned URL is valid for 1 hour only;** after expiry, run the script again to get a new URL.
- **Submit**: `python scripts/submit_task.py --type ... --prompt "..." [--image-uri ...] [--material ...]`；character2video 时**文字必填**，图+主体合计最多 7。Capture task_id from stdout. Respect 任务支持列表 (img2video 不传 aspect_ratio，character2video 不传 transition).
- **Query status/result**: `python scripts/get_task_result.py <task_id>`. Call when needed; response includes state and, when success, nomark_uri line(s).

---

## Output to the user

- **After submit**: Return the **task_id** to the user; mention that video generation is in progress and they can query status/result later with that task_id (e.g. get_task_result.py or GET `/vidu/v1/tasks/{task_id}`).
- **After query (get_task_result.py)**: If state is success, return the **nomark_uri** link(s) to the user; if failed, report err_code / err_msg.
- **Failure (submit or script error)**: Clearly state that the task failed and, if available, the reason (err_code / err_msg from script or references).

---

## Fallback (no Python)

If the environment **cannot** run Python scripts, you cannot execute this skill as intended. Tell the user that this skill requires script execution (Python 3, requests, VIDU_TOKEN) and point them to **scripts/README.md** and **references/api_reference.md** for manual API usage elsewhere.
