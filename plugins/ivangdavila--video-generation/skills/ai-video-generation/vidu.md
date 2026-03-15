# Vidu

**Best for:** multi-mode generation with references and start/end control.

## Official Model Map

Vidu documentation lists model routing such as:
- `viduq1` (flagship quality)
- `viduq1-se` (cost-optimized)
- `vidu2.0`, `vidu1.5`, and dedicated reference/start-end modes

## API Surface

Vidu exposes async APIs for:
- Text-to-video
- Image-to-video
- Start-End image animation
- Multi-reference generation

## Practical Routing

- `viduq1` for final quality outputs
- `viduq1-se` for low-cost ideation batches
- start/end modes for deterministic transitions

## Reliability Tips

- Keep reference asset styles consistent
- Lock target ratio before generation
- Prefer callback + polling hybrid for production reliability
