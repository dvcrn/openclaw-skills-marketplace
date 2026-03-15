---
name: modellix
description: "Integrate Modellix's unified API for AI image and video generation into applications. Use this skill whenever the user wants to generate images from text, create videos from text or images, edit images, do virtual try-on, or call any Modellix model API. Also trigger when the user mentions Modellix, model-as-a-service for media generation, or needs to work with providers like Qwen, Wan, Seedream, Seedance, Kling, Hailuo, or MiniMax through a unified API."
---

# Modellix Skill

Modellix is a Model-as-a-Service (MaaS) platform providing unified API access to 100+ AI models for image and video generation. All models — regardless of provider (Alibaba, ByteDance, Kling, MiniMax) — share the same async API pattern: submit a task, get a `task_id`, poll for results.

## Workflow

Follow these steps to integrate any Modellix model. This mirrors the official usage process.

### Step 1: Obtain an API Key

Direct the user to create an API key:

1. Log in to the [Modellix console](https://modellix.ai)
2. Navigate to [API Key](https://modellix.ai/console/api-key) and create a new key
3. **Save the key immediately** — it is only displayed once after creation

Store the key securely as an environment variable (e.g., `MODELLIX_API_KEY`). Never hardcode it.

### Step 2: Find the Right Model

The model catalog is in `references/REFERENCE.md`. Read that file to search for the model that fits the user's task. Each entry follows this pattern:

```
- [Model Name](https://docs.modellix.ai/{provider}/{model-slug}.md): Description
```

**How to select a model:**

1. Identify the task type: text-to-image, text-to-video, image-to-image, image-to-video, or specialized (try-on, outpainting, style transfer, etc.)
2. Search REFERENCE.md for models matching that task type
3. Compare model descriptions to find the best fit (e.g., speed vs quality tradeoffs — "turbo" models are faster/cheaper, "plus"/"pro" models are higher quality)

**After selecting a model, fetch its API documentation** by visiting the URL from REFERENCE.md (e.g., `https://docs.modellix.ai/alibaba/qwen-image-plus.md`). The model's doc page contains the OpenAPI spec with:
- The exact API endpoint path
- Required and optional request parameters (with types, defaults, and allowed values)
- Request/response examples

This step is essential because each model has different parameters (e.g., `size` format, `seed` range, model-specific options). Always read the model's doc page before writing API calls.

### Step 3: Submit an Async Task

All Modellix API calls are asynchronous. Submit a task with a POST request:

```
POST https://api.modellix.ai/api/v1/{type}/{provider}/{model_id}/async
```

**Path parameters:**

| Parameter  | Description      | Examples                                                     |
| ---------- | ---------------- | ------------------------------------------------------------ |
| `type`     | Task type        | text-to-image, text-to-video, image-to-image, image-to-video |
| `provider` | Model provider   | alibaba, bytedance, kling, minimax                           |
| `model_id` | Model identifier | qwen-image-plus, seedream-4.5-t2i, kling-v2.1-t2i            |

**Example — generate an image with Qwen Image Plus:**

```bash
curl -X POST https://api.modellix.ai/api/v1/text-to-image/alibaba/qwen-image-plus/async \
  -H "Authorization: Bearer $MODELLIX_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "A cute cat playing in a garden on a sunny day"}'
```

**Successful submission returns a `task_id`:**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "status": "pending",
    "task_id": "task-abc123",
    "model_id": "qwen-image-plus",
    "duration": 150
  }
}
```

A `code` of `0` means success. Any other value indicates an error (see Error Handling below).

### Step 4: Poll for Results

Query the task status using the `task_id`:

```bash
curl -X GET https://api.modellix.ai/api/v1/tasks/{task_id} \
  -H "Authorization: Bearer $MODELLIX_API_KEY"
```

**Task statuses:**

| Status    | Meaning              | Action                             |
| --------- | -------------------- | ---------------------------------- |
| `pending` | Queued or processing | Wait 2-5 seconds, poll again       |
| `success` | Generation complete  | Extract results from `data.result` |
| `failed`  | Generation failed    | Check error message                |

**Successful result example:**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "status": "success",
    "task_id": "task-abc123",
    "model_id": "qwen-image-plus",
    "duration": 3500,
    "result": {
      "resources": [
        {
          "url": "https://cdn.example.com/images/abc123.png",
          "type": "image",
          "width": 1024,
          "height": 1024,
          "format": "png",
          "role": "primary"
        }
      ],
      "metadata": {
        "image_count": 1,
        "request_id": "req-123456"
      },
      "extensions": {
        "submit_time": "2024-01-01T10:00:00Z",
        "end_time": "2024-01-01T10:00:03Z"
      }
    }
  }
}
```

The generated content URLs are in `data.result.resources`. Download or use them promptly — **results expire after 24 hours**.

**Implement polling with exponential backoff** (1s, 2s, 4s...) rather than fixed intervals. A typical image takes 3-10 seconds; video generation takes longer (30-120 seconds depending on model and duration).

### Step 5: Handle Results

Extract the generated content from the `resources` array:

```python
for resource in data["result"]["resources"]:
    url = resource["url"]        # download URL
    media_type = resource["type"]  # "image" or "video"
    # Download and save before the 24-hour expiration
```

## Error Handling

All errors follow a unified format:

```json
{
  "code": 400,
  "message": "Invalid parameters: parameter 'prompt' is required"
}
```

The `code` field equals the HTTP status code. The `message` contains a category and detail separated by `: `.

| HTTP Status | Description           | Common Scenarios                   | Retryable                     |
| ----------- | --------------------- | ---------------------------------- | ----------------------------- |
| 400         | Bad Request           | Missing or invalid parameters      | No — fix parameters first     |
| 401         | Unauthorized          | Invalid or missing API key         | No — provide a valid key      |
| 404         | Not Found             | Task ID or model not found         | No — check resource ID        |
| 429         | Too Many Requests     | Rate or concurrency limit exceeded | Yes — use exponential backoff |
| 500         | Internal Server Error | Unexpected server error            | Yes — retry up to 3 times     |
| 503         | Service Unavailable   | Provider temporarily down          | Yes — retry with backoff      |

## Implementation Patterns

Modellix has no SDK — all integration is done via REST API calls. Below are reference patterns for common languages. Adapt these to the user's project as needed.

### Python (requests)

```python
import requests, time, os

API_KEY = os.environ["MODELLIX_API_KEY"]
BASE = "https://api.modellix.ai/api/v1"
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

# Step 1: Submit task
resp = requests.post(f"{BASE}/text-to-image/alibaba/qwen-image-plus/async",
                     headers=HEADERS, json={"prompt": "A cat in a garden"})
task_id = resp.json()["data"]["task_id"]

# Step 2: Poll with exponential backoff
wait = 2
while True:
    time.sleep(wait)
    result = requests.get(f"{BASE}/tasks/{task_id}", headers=HEADERS).json()
    if result["data"]["status"] == "success":
        print(result["data"]["result"]["resources"][0]["url"])
        break
    if result["data"]["status"] == "failed":
        raise Exception(result["data"])
    wait = min(wait * 2, 10)
```

### Node.js (fetch)

```javascript
const API_KEY = process.env.MODELLIX_API_KEY;
const BASE = "https://api.modellix.ai/api/v1";
const headers = { "Authorization": `Bearer ${API_KEY}`, "Content-Type": "application/json" };

// Submit task
const submitRes = await fetch(`${BASE}/text-to-image/alibaba/qwen-image-plus/async`, {
  method: "POST", headers, body: JSON.stringify({ prompt: "A cat in a garden" }),
});
const { data: { task_id } } = await submitRes.json();

// Poll with backoff
let wait = 2000;
while (true) {
  await new Promise(r => setTimeout(r, wait));
  const pollRes = await fetch(`${BASE}/tasks/${task_id}`, { headers });
  const { data } = await pollRes.json();
  if (data.status === "success") { console.log(data.result.resources[0].url); break; }
  if (data.status === "failed") { throw new Error(JSON.stringify(data)); }
  wait = Math.min(wait * 2, 10000);
}
```

### Batch Processing

When submitting multiple tasks, respect the concurrent task limit (typically 3 per team). Use a semaphore or queue to throttle parallel submissions.

## Common Pitfalls

- **API key shown once**: Save immediately. Lost keys require creating a new one.
- **Results expire in 24 hours**: Download generated content promptly.
- **All operations are async**: There is no synchronous endpoint. Always poll for results.
- **Rate limits are team-wide**: All API keys under the same team share limits.
- **Concurrent task limit**: Typically 3 per team. Exceeding this triggers 429 errors.
- **Parameter formats vary by model**: Always read the model's API doc. For example, `size` might be `"1024*1024"` (asterisk) for Alibaba models or `"2048x2048"` (letter x) for ByteDance models.
- **Polling too fast wastes resources**: Use exponential backoff, not fixed sub-second intervals.

## Verification Checklist

Before shipping a Modellix integration:

- [ ] API key stored as environment variable, not hardcoded
- [ ] `Authorization: Bearer <key>` header set correctly
- [ ] Model-specific parameters match the model's API doc (read from REFERENCE.md → model doc page)
- [ ] Task submission returns valid `task_id` (check `code == 0`)
- [ ] Polling handles all statuses: `pending`, `success`, `failed`
- [ ] Exponential backoff implemented for polling and retries
- [ ] Retryable (429/500/503) vs non-retryable (400/401/404) errors handled differently
- [ ] Results downloaded/stored before 24-hour expiration
- [ ] Concurrent task limit respected (semaphore or queue)
- [ ] Appropriate timeouts set (30-60s for images, 60-120s for videos)

## Resources

- **Model Catalog**: Read `references/REFERENCE.md` to find available models and their doc page URLs
- **API Usage Guide**: https://docs.modellix.ai/ways-to-use/api
- **Pricing**: https://docs.modellix.ai/get-started/pricing
- **Full Doc Index**: https://docs.modellix.ai/llms.txt
