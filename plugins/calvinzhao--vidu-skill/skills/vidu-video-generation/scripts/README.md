# Scripts

Executable helpers for the vidu-video-generation skill. Use them when the environment can run Python for reliable, repeatable API calls.

## Dependency

- **Python 3**
- **requests**: `pip install requests`
- **Pillow** (optional): for `upload_image.py` to auto-detect image size; `pip install Pillow`. If not installed, pass width and height as arguments.

## Environment

All domains used by the skill are configurable via environment variables:

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| VIDU_TOKEN | yes | — | Auth token for vidu APIs |
| VIDU_BASE_URL | no | `https://service.vidu.cn` | API base URL (service domain, also used in User-Agent) |

**Region / 地域**  
- **中国大陆 (Mainland China)**: 使用 `https://service.vidu.cn`（默认）。  
- **非中国地区 / 海外 (Outside China)**: 使用 `https://service.vidu.com`，需设置 `VIDU_BASE_URL=https://service.vidu.com`。

Example:

```bash
export VIDU_TOKEN=your_token
# optional: configure domain (default: service.vidu.cn for China; use service.vidu.com for overseas)
export VIDU_BASE_URL=https://service.vidu.cn   # mainland China
# export VIDU_BASE_URL=https://service.vidu.com  # outside China
```

## Scripts and Examples

### 主体相关脚本流程 (Element scripts workflow)

**pre_process_element.py** 与 **create_element.py** 是两个独立脚本，流程上**必须先调用 pre-process，再调用 create-element**：

1. **pre_process_element.py**（或 POST `/vidu/v1/material/elements/pre-process`）：对已上传的 1–3 张图做预处理，返回 `recaption`（style、description）等。
2. **create_element.py**（或 POST `/vidu/v1/material/elements`）：创建主体，需使用 pre-process 的结果（未传 `--description` 时会用 pre-process 返回的 recaption）。

运行 **create_element.py** 时，脚本会**自动先内部调用 pre_process_element.py**，因此通常只需执行一条命令 `create_element.py` 即可完成“先 pre-process 再 create-element”的完整流程。若只需 recaption 或希望分步执行，可先单独运行 **pre_process_element.py**，再根据需要调用创建接口或脚本。

---

### upload_image.py

Upload a local image and get `ssupload:?id=...` for use in img2video task body.

```bash
# Auto-detect width/height (needs Pillow)
python upload_image.py ./photo.jpg

# Or pass dimensions
python upload_image.py ./photo.jpg 696 984
```

Output: `ssupload:?id=3196909373813933` (one line).

---

### get_upload_url.py

Get public download URL(s) for uploaded resource(s) by ssupload id(s). Use this after Create upload when you need a shareable link for the user to download the file.

**The returned URL(s) are valid for 1 hour only.** After expiry, run this script again to get a new URL.

```bash
# By full ssupload URI or by numeric id
python get_upload_url.py "ssupload:?id=3198227967220872"
python get_upload_url.py 3198227967220872

# Multiple resources (one URL per line, in order)
python get_upload_url.py 3198227967220872 3198227967220873
```

Output: one public URL per line. Exit 0 on success, non-zero on failure.

---

### pre_process_element.py (主体预处理)

Call **POST /material/elements/pre-process** only: input 1–3 already-uploaded image URIs (`ssupload:?id=...`) and subject name; output is the full pre-process response (including `recaption.description`, `recaption.style`). Use this when you need recaption without creating the element, or as a step before create_element.

```bash
# After uploading images with upload_image.py, get recaption for 1 image
python pre_process_element.py --name "机器猫" --image-uri "ssupload:?id=3196909373813933"

# 2–3 images (first=main, rest=auxiliary)
python pre_process_element.py --name "艾莉娅" --image-uri "ssupload:?id=1" --image-uri "ssupload:?id=2"
```

Output: one JSON line with pre-process response (`recaption`, `id`, `name`, etc.). Exit 0 on success, non-zero on failure.

---

### create_element.py (创建主体)

Create a material element (subject) with 1–3 images, name and optional description; for use in character2video. Flow: upload images → **pre_process_element.py** (or POST /material/elements/pre-process) → POST /material/elements. If `--description` is omitted, the script uses the pre-process response `recaption` (style, description) for the create body.

```bash
# 1 image, use pre-process recaption as description
python create_element.py --name "机器猫" --image ./a.jpg

# 1 image with your own description
python create_element.py --name "机器猫" --description "哆啦A梦，一个蓝白相间的卡通机器人..." --image ./a.jpg

# 2–3 images (first=main, rest=auxiliary), optional style
python create_element.py --name "艾莉娅" --description "..." --style "2D动画，卡通" --image ./main.jpg --image ./aux1.jpg
```

Output: one JSON line with `id` and `version`, e.g. `{"id": "3202251954800262", "version": "1773286783"}`. Use these in character2video task body. Exit 0 on success, non-zero on failure.

---

### list_elements.py (查询主体)

Query personal material elements (GET `/vidu/v1/material/elements/personal`). List or search subjects by keyword; use returned `id` and `version` in character2video.

```bash
# List first page (default page=0, pagesz=30)
python list_elements.py

# Search by keyword
python list_elements.py --keyword "机器猫"

# Pagination
python list_elements.py --page 0 --pagesz 30
python list_elements.py --page-token "<next_page_token from previous run>"

# Filter by modality
python list_elements.py --modalities image --modalities text
```

Output: one JSON object per line per element with `id`, `name`, `version` (and optionally `description`, `style`). If there is a next page, a final line contains `{"next_page_token": "..."}`. Exit 0 on success, 1 on failure.

---

### submit_task.py

Submit a task (text2video, img2video, headtailimg2video, character2video). Outputs task_id. See 任务支持列表 in SKILL.md or references/parameters.md for constraints.

```bash
# 文生视频
python submit_task.py --type text2video --prompt "hello apple"
python submit_task.py --type text2video --prompt "hello apple" --duration 8 --resolution 1080p --model-version 3.2 --transition pro

# 图生视频 (exactly 1 image; do not pass --aspect-ratio, script omits it)
python submit_task.py --type img2video --prompt "穿上一件羽绒服" --image-uri "ssupload:?id=3196909373813933"

# 首尾帧生视频 (exactly 2 images: 首帧, 尾帧)
python submit_task.py --type headtailimg2video --prompt "..." --image-uri "ssupload:?id=id1" --image-uri "ssupload:?id=id2"

# 参考生视频 (图+主体+文字，文字必填; Q2 only; script omits transition)
python submit_task.py --type character2video --prompt "..." --image-uri "ssupload:?id=id1" --image-uri "ssupload:?id=id2"
python submit_task.py --type character2video --prompt "[@艾莉娅]" --material "艾莉娅:3073530415201165:1765430214"
python submit_task.py --type character2video --prompt "[@艾莉娅]" --image-uri "ssupload:?id=id1" --material "艾莉娅:3073530415201165:1765430214"

# Use a full JSON body from file
python submit_task.py --body-file task_body.json
```

Output: task_id (one line).

---

### get_task_result.py

Fetch task and print nomark_uri(s) or error info.

```bash
python get_task_result.py 3196909781130908
```

Output: one JSON object per creation line, e.g. `{"nomark_uri": "https://...", "creation_id": ...}`. On failure, JSON to stderr and exit 1.

---

### run_vidu_generation.py (orchestrator)

**Submit only** — optional image upload → submit → **prints task_id and exits**. No wait mode; use **get_task_result.py** \<task_id\> to query status/result when needed. Respects 任务支持列表 (image count, aspect_ratio/transition omitted per type).

```bash
# 文生视频
python run_vidu_generation.py text2video --prompt "hello apple"

# 图生视频 (exactly 1 image)
python run_vidu_generation.py img2video --prompt "穿上一件羽绒服" --image ./photo.jpg

# 首尾帧生视频 (exactly 2 images: 首帧, 尾帧)
python run_vidu_generation.py headtailimg2video --prompt "..." --image ./frame1.jpg --image ./frame2.jpg

# 参考生视频 (图+主体+文字，文字必填; Q2 only)
python run_vidu_generation.py character2video --prompt "..." --image ./a.jpg --image ./b.jpg
python run_vidu_generation.py character2video --prompt "[@艾莉娅]" --material "艾莉娅:3073530415201165:1765430214"
python run_vidu_generation.py character2video --prompt "[@艾莉娅]" --image ./a.jpg --material "艾莉娅:3073530415201165:1765430214"
```

Output: task_id (one line). To get video URL(s) or state: `python get_task_result.py <task_id>`.
