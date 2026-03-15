# ByteDance Seedance

**Best for:** high-motion scenes, multi-shot narratives, and strong visual coherence.

## Official Model Family Signals

Public Seed and ByteDance pages reference:
- Seedance 1.0 (Pro / Lite)
- Seedance 2.0

## API Access Reality

- Official pages clearly market "Get API" access
- Public model-ID docs are less standardized than OpenAI/Vertex paths
- Practical API usage is commonly routed through partner platforms and unified gateways

## Known API Surface in Ecosystem

- Replicate model: `bytedance/seedance-1.5-pro`
- Tencent MPS gateway includes `seedance` options in AIGC task APIs

## Practical Routing

- Use Seedance for motion-heavy and multi-shot prompts
- Keep prompts structured by shot blocks (Shot 1, Shot 2, transition)
- Use reference images for style and character continuity

## Reliability Tips

- Ask for one dominant motion objective per shot
- Avoid overloading a single prompt with many scene jumps
- Archive prompt + seed + model-version metadata for reruns
