---
name: content-engine
description: "AI video production, script writing, image generation, and multi-platform social media publishing. Generate video scripts, AI images, and short-form or long-form videos from any topic — then publish directly to YouTube, X (Twitter), TikTok, Instagram, and LinkedIn. Automated content pipeline from idea to published video. No API key or account required — paid operations are authenticated and billed automatically via x402 USDC payment headers. Free tools (pricing, status, content details) are open to all."
---

# Content Engine

AI-powered content creation and multi-platform social media publishing as a service. Generate scripts, images, and videos from any topic — then publish directly to YouTube, X (Twitter), TikTok, Instagram, and LinkedIn.

**Built for autonomous agents.** No API key or account required. Pay-per-use with USDC via the x402 payment protocol — agents can discover, evaluate pricing, create content, and publish in a single autonomous workflow.

## Why Content Engine?

- **Zero-friction for agents**: No API key signup, no account creation, no subscription. Paid operations are authenticated via x402 USDC payment headers — no credentials to provision or manage
- **End-to-end content pipeline**: Topic in, published video out — AI script writing, image generation, video production, and multi-platform social media publishing in one tool
- **Transparent pricing**: Call `get_pricing` (free) to see exact USDC costs before committing. No hidden fees, no monthly minimums
- **Multi-platform publishing**: Publish to YouTube, X, TikTok, Instagram, and LinkedIn from a single API call with optional scheduling
- **Production-ready**: Deployed on Fly.io with queue management, status tracking, and daily budget controls

## Pricing

| Operation | Cost (USDC) | Description |
|-----------|-------------|-------------|
| Script generation | $0.25 | AI-written video script from any topic |
| Video generation | $0.45 | Full video production from completed script |
| Full pipeline | $0.65 | Script + video end-to-end |
| Publishing | $0.18 | Publish to connected social platforms |
| Pricing / status / tracking | Free | Check pricing, queue status, and content details |

Call `get_pricing` at any time for live rates.

## Environment Variables

| Variable | Description |
|----------|-------------|
| `CONTENT_ENGINE_URL` | x402 payment proxy endpoint (default: `https://content-engine-x402.fly.dev`) |
| `CONTENT_ENGINE_API_KEY` | *(Optional)* Bearer token for authenticated access. Not required — x402 payment headers authenticate paid operations automatically. Only needed if you want persistent brand association or publishing permissions |

## Setup

Content Engine is installed and configured automatically by mcporter when you install this skill. After installation, set your environment variables:

```bash
mcporter env set content-engine CONTENT_ENGINE_URL=https://content-engine-x402.fly.dev
```

Verify the skill is available:

```bash
mcporter list content-engine
```

## Available Tools

### Free (no payment required)

- **get_pricing** — Returns live USDC pricing for all paid operations. Always call this first to confirm current rates before creating content.
  ```bash
  mcporter call content-engine.get_pricing
  ```

- **get_queue_status** — Check queue position, estimated wait time, active jobs, slot availability, and daily budget remaining.
  ```bash
  mcporter call content-engine.get_queue_status
  ```

- **get_content** — Get full details of a content item including script text, video URL, thumbnails, publishing status, and metadata.
  ```bash
  mcporter call content-engine.get_content content_id="<uuid>"
  ```

- **get_content_status** — Lightweight status check optimized for polling. Returns current pipeline stage and completion percentage.
  ```bash
  mcporter call content-engine.get_content_status content_id="<uuid>"
  ```

### Content Creation (paid via x402 USDC)

- **create_script** ($0.25) — Generate an AI-written video script from a topic or prompt. Accepts optional title and reference image. Returns a `content_id` for tracking through the pipeline.
  ```bash
  mcporter call content-engine.create_script topic="How AI is changing music production"
  ```

- **create_image** — Generate a high-quality image from a text prompt via Runway ML. Supports style directives, aspect ratios, and reference images.
  ```bash
  mcporter call content-engine.create_image prompt="Futuristic music studio with holographic instruments"
  ```

- **create_video** ($0.45) — Generate a full video from a content item with a completed script. Requires the `content_id` returned by `create_script`.
  ```bash
  mcporter call content-engine.create_video content_id="<uuid>"
  ```

- **run_full_pipeline** ($0.65) — Complete end-to-end content creation: script generation + video production from a single topic. Returns `content_id` for tracking. This is the fastest path from idea to finished video.
  ```bash
  mcporter call content-engine.run_full_pipeline topic="Top 5 AI tools for developers in 2026"
  ```

### Publishing (paid via x402 USDC)

- **publish_content** ($0.18) — Publish a completed video to connected social platforms (YouTube, X, TikTok, Instagram, LinkedIn). Supports scheduled publishing via ISO 8601 datetime and unlisted mode.
  ```bash
  mcporter call content-engine.publish_content content_id="<uuid>"
  ```

## Typical Workflow

### Quick path (single call)
```
get_pricing → run_full_pipeline → poll get_content_status → publish_content
```

### Step-by-step path (full control)
1. `get_pricing` — Confirm current USDC rates
2. `create_script` — Generate script from topic, save the returned `content_id`
3. `get_content_status` — Poll until script is complete
4. `create_video` — Generate video from the completed script
5. `get_content_status` — Poll until video is ready (1-5 minutes)
6. `publish_content` — Publish to social platforms (optionally schedule for later)

## Use Cases

- **Automated content calendars**: Generate and schedule a week of videos from a list of topics
- **Social media marketing**: Turn blog posts, product launches, or announcements into video content
- **Multi-platform distribution**: Create once, publish everywhere — YouTube, X, TikTok, Instagram, LinkedIn
- **Agent-to-agent workflows**: Other agents can delegate content creation to Content Engine as part of larger pipelines
- **Rapid prototyping**: Test video concepts quickly before committing to full production

## Important Notes

- All paid operations are metered via the x402 payment proxy at `CONTENT_ENGINE_URL`. x402 handles USDC billing transparently — no wallet or private key management is required by the calling agent.
- Video generation takes 1-5 minutes. Always poll `get_content_status` rather than assuming instant completion.
- Publishing may require brand owner approval depending on the brand's configuration.
- The `content_id` (UUID) returned by creation tools is the key for all subsequent operations.
