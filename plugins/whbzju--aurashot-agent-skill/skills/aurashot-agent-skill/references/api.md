# AuraShot Aesthetics API Reference

## Environment Variables

- `AURASHOT_API_KEY`: preferred AuraShot Studio key
- `AURASHOT_STUDIO_KEY`: fallback AuraShot Studio key
- `AURASHOT_BASE_URL`: defaults to `https://www.aurashot.art`

## Endpoints

### POST /api/aesthetic/generate

Submit a workflow job.

**Headers:**
```
Authorization: Bearer <studio_key>
Content-Type: application/json
```

**Body — Virtual Try-On:**
```json
{
  "workflow": "virtual_try_on",
  "waitForResult": false,
  "input": {
    "productImage": "https://...",
    "modelImage": "https://...",
    "sceneImage": "https://...",
    "generateVersion": "weshopFlash",
    "descriptionType": "custom",
    "textDescription": "穿上这件，坐在窗边"
  }
}
```

**Body — Pose Change:**
```json
{
  "workflow": "pose_change",
  "waitForResult": false,
  "input": {
    "originalImage": "https://...",
    "generateVersion": "lite",
    "textDescription": "换个站姿，背景不变"
  }
}
```

**`generateVersion` options:**
- `virtual_try_on`: `weshopFlash` (fast), `weshopPro` (quality), `bananaPro` (4K)
- `pose_change`: `lite` (fast), `pro` (quality)

**`descriptionType`** (`virtual_try_on` only): `auto` or `custom`. Use `custom` when providing `textDescription`.

**`waitForResult`**: `true` blocks until done (dev/testing). `false` returns immediately with `executionId` for polling.

### POST /api/aesthetic/query

Poll the status of a submitted job.

**Body:**
```json
{
  "workflow": "virtual_try_on",
  "executionId": "returned_execution_id"
}
```

## Response Shape

```json
{
  "workflow": "virtual_try_on",
  "taskId": "...",
  "executionId": "...",
  "status": "submitted | processing | success | failed",
  "completed": false,
  "images": ["https://..."],
  "results": [
    {
      "status": "Success",
      "image": "https://...",
      "progress": null,
      "error": null
    }
  ]
}
```
