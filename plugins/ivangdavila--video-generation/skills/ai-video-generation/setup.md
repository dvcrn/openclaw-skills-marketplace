# Setup - AI Video Generation

## First Activation Check

Detect existing memory:

```bash
test -f ~/video-generation/memory.md
```

If it exists, continue normally.

## If Memory Is Missing

Create a lightweight workspace:

```bash
mkdir -p ~/video-generation
```

Copy `memory-template.md` into `~/video-generation/memory.md`.

## Operating Behavior

- Answer the user request first, then refine setup details in follow-up turns
- Keep setup optional and non-blocking
- Learn provider preferences from repeated usage
- Ask clarifying questions only when model choice can change quality or cost significantly

## Fast Model Routing Shortcut

If no provider preference exists, ask for one short choice:

- Sora 2 (OpenAI): high instruction fidelity and premium prompt-to-video
- Veo 3.x (Google): strong model tiers and image-to-video support
- Runway Gen-4: creative cinematic controls and long-form options
- Seedance or Hailuo: high-motion character and narrative scenes
- Open-source local: privacy-first workflows with self-hosted GPUs

## Provider Verification (without exposing secrets)

Check only env var presence:

```bash
test -n "$OPENAI_API_KEY" && echo "OpenAI configured"
test -n "$GOOGLE_CLOUD_PROJECT" && echo "Vertex configured"
test -n "$RUNWAY_API_KEY" && echo "Runway configured"
test -n "$REPLICATE_API_TOKEN" && echo "Replicate configured"
test -n "$FAL_KEY" && echo "Fal configured"
```

Never ask users to paste secrets into chat.

## Memory Updates

After meaningful sessions, update memory with:
- Model families that worked for specific tasks
- Prompt patterns that improved motion consistency
- Cost, latency, and failure patterns worth reusing
