# Open-Source Local Video Models

**Best for:** privacy-first workflows, custom infrastructure, and no per-call SaaS fees.

## Leading Open Models

- Wan2.2 (`Wan-Video/Wan2.2`)
- HunyuanVideo 1.5 (`Tencent-Hunyuan/HunyuanVideo`)
- CogVideoX ecosystem variants

## When to Choose Local

- Data sensitivity prevents external upload
- Long-running batch generation on owned GPUs
- Need for model customization and reproducibility

## Tradeoffs

- Higher setup complexity and GPU requirements
- Slower iteration without tuned infrastructure
- Operational burden shifts to your own stack

## Reliability Tips

- Start with smaller resolution and frame count
- Keep deterministic seeds for repeatability
- Version prompts and model checkpoints together
