# API Patterns - AI Video Generation

Common patterns for modern video generation APIs.

## Async-First Contract

Most providers follow this shape:
1. Create job
2. Receive job ID or operation name
3. Poll until terminal state
4. Download output from signed URL

## Provider Pattern Map

| Provider | Create | Status | Notes |
|----------|--------|--------|-------|
| OpenAI Sora 2 | Responses API with `modalities=["video"]` | Response/job status | Supports background and async flows |
| Google Veo (Vertex) | `generateVideos` | Long-running operation | `fetchPredictOperation` for polling |
| Runway | Task create endpoint | Task status endpoint | SDK supports wait helper |
| Luma | Generation create endpoint | Generation status endpoint | URL expiry handling required |
| Vidu | Async create endpoint | Async query endpoint | Includes callback and polling modes |
| Tencent MPS AIGC | `CreateAigcVideoTask` | `DescribeAigcVideoTaskStatus` | Unified multi-model gateway |
| Fal / Replicate | Queue submit | Queue status endpoint | Webhook mode available |

## Retry Strategy

- Use idempotency keys where supported
- Poll with exponential backoff (for example 2s -> 4s -> 8s -> 16s)
- Apply max runtime by model tier
- Fail fast on explicit content-policy or invalid-parameter errors

## Output Handling

- Signed URLs expire quickly
- Download outputs immediately after completion
- Save metadata with model ID, prompt, seed, duration, ratio, and provider job ID

## Fallback Tree

1. Same provider lower tier
2. Equivalent cross-provider model
3. Open-source/local model

## Cost Guardrails

- Draft short (3-5s), finish long only after approval
- Prefer fast tiers for ideation batches
- Disable auto-upscale in early iterations
