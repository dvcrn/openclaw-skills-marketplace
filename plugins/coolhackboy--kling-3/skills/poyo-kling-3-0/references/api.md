# PoYo Kling 3 0 API Reference

## Endpoint

- Submit task: `https://api.poyo.ai/api/generate/submit`
- Status query: <https://docs.poyo.ai/api-manual/task-management/status>
- Source docs: <https://docs.poyo.ai/api-manual/video-series/kling-3-0>
- OpenAPI JSON: <https://docs.poyo.ai/api-manual/video-series/kling-3-0.json>

## Auth

Send:

```http
Authorization: Bearer YOUR_API_KEY
Content-Type: application/json
```

Get API keys from <https://poyo.ai/dashboard/api-key>.

Recommended skill env var:

- `POYO_API_KEY`

## Models

- `kling-3.0/standard` — default-quality or standard jobs
- `kling-3.0/pro` — higher-quality or premium jobs

## Key input fields

- `model` (string, required) — choose one of the documented model ids
- `callback_url` (string, optional) — Webhook callback URL for result notifications
- `sound` (boolean, required) — Whether to enable sound effects. true enables sound effects, false disables them. When multi_shots is true, this field must be true.
- `multi_shots` (boolean, required) — Enable multi-shot mode. When true, use multi_prompt array instead of prompt. When false, use prompt string. Default is false
- `prompt` (string, optional) — Video generation prompt. Required when multi_shots is false. You can reference elements using @element_name syntax (e.g., @element_dog)
- `image_urls` (string[], required) — Array of image URLs. For single shot mode (multi_shots: false), provide start and end frame URLs. For multi-shot mode (multi_shots: true), provide only the start frame URL. **Required** when `kling_elements` is provided
- `duration` (integer, required) — Video duration in seconds. For single shot mode, duration can be 3-15 seconds. For multi-shot mode, duration is the total duration of all shots
- `aspect_ratio` (string, optional) — Video aspect ratio. When the input does not contain reference images (image_urls), the default is 1:1 if the aspect_ratio parameter is not passed; when the input contains the first frame image, the aspect_ratio parameter will be ignored, and the output will use the aspect ratio of the first frame image options: 1:1, 16:9, 9:16
- `multi_prompt` (object[], optional) — Array of prompt objects for multi-shot mode. Required when multi_shots is true. Each object contains a prompt and duration. Total duration of all shots cannot exceed 15 seconds
- `kling_elements` (object[], optional) — Array of element objects that can be referenced in prompts using @element_name syntax. Elements can be defined using images (2-4 images) or a single video. When provided, `image_urls` is required

## Submission example

```bash
curl -sS https://api.poyo.ai/api/generate/submit   -H 'Authorization: Bearer YOUR_API_KEY'   -H 'Content-Type: application/json'   -d '{
  "model": "kling-3.0/standard",
  "callback_url": "https://your-domain.com/callback",
  "input": {
    "prompt": "A chef carefully plating a gourmet dish in a modern kitchen, steam rising from the food under warm lighting",
    "multi_shots": false,
    "duration": 5,
    "sound": true,
    "aspect_ratio": "16:9"
  }
}'
```

## Polling notes

- PoYo returns a `task_id` after submission.
- If `callback_url` is present, PoYo sends a POST callback when the task reaches `finished` or `failed`.
- Whether or not callbacks are used, the same unified task status docs apply: <https://docs.poyo.ai/api-manual/task-management/status>.

## Practical guidance

- Use `image_urls` only when the task genuinely depends on reference imagery.
- Match aspect ratio to the destination surface: 1:1, 16:9, 9:16.
- Save the returned `task_id` immediately so status polling is straightforward.
