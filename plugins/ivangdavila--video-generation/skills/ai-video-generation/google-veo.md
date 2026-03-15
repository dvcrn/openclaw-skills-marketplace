# Google Veo 3.x (Vertex AI)

**Best for:** API-first generation tiers with strong quality-speed options.

## Official Model IDs

- `veo-3.0-generate-001`
- `veo-3.0-fast-generate-001`
- `veo-3.1-generate-001`
- `veo-3.1-fast-generate-001`

## Supported Modes

- Text-to-video (all Veo 3.x IDs above)
- Image-to-video (available on Veo 3.0 path)

## API Path

Use Vertex AI `generateVideos` with long-running operation polling.
Prefer explicit `aspectRatio`, `durationSeconds`, and quality-tier selection.

## Practical Routing

- `veo-3.1-generate-001` for premium final outputs
- `veo-3.1-fast-generate-001` for fast ideation
- `veo-3.0-generate-001` when image-to-video is required

## Reliability Tips

- Check allowlist/region availability before production rollout
- Separate prompt templates for fast and premium tiers
- Keep one cross-provider fallback when Veo capacity is constrained
