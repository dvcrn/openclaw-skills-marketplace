# Runway Gen-4 API

**Best for:** cinematic motion control and longer-form creative outputs.

## Official Model IDs

- `gen4_turbo`
- `gen4_aleph`

## Duration and Resolution Notes

- `gen4_turbo`: optimized for fast 5s or 10s runs
- `gen4_aleph`: supports broader duration options (including longer-form tiers)
- Resolution defaults and limits vary by model and plan

## API Path

Use Runway API task endpoints (`image_to_video` and related task flows).
Track task IDs and poll until terminal state.

## Practical Routing

- Use `gen4_turbo` for prompt and motion validation loops
- Use `gen4_aleph` for final cinematic sequences and continuity work
- Prefer image-to-video when precise shot framing is required

## Reliability Tips

- Include clear camera verbs (pan, dolly, orbit, push-in)
- Use reference frames for character continuity
- Save all task IDs for audit and rerender workflows
