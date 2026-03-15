# OpenAI Sora 2

**Best for:** premium text-to-video quality and strong prompt adherence.

## Official Models

- `sora-2`
- `sora-2-pro`

## API Path

Use the OpenAI Responses API with video modality.
Key pattern: set `model` to Sora 2 variant and include `"video"` in `modalities`.

## Practical Routing

- Use `sora-2-pro` for final hero outputs
- Use `sora-2` for earlier iterations or lower-cost tests
- Keep shot prompts explicit about subject, motion, and camera timing

## Reliability Tips

- Treat jobs as async and poll status for completion
- Keep prompts scoped to one shot objective to reduce drift
- Store response IDs and download outputs immediately
