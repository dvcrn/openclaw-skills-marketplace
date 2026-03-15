# Model Snapshot

Use this file as a dated routing snapshot, not a permanent truth.

## Scope

- Last verified: current release cycle
- Sources: official provider docs and model pages
- Goal: practical routing for quality, speed, and API availability

## Production Leaders by API Maturity

| Model family | Typical role | API maturity |
|--------------|--------------|--------------|
| Sora 2 (`sora-2`, `sora-2-pro`) | Premium prompt-to-video | High |
| Veo 3.x (`veo-3.0/3.1`) | Tiered quality and speed | High |
| Runway Gen-4 (`gen4_turbo`, `gen4_aleph`) | Cinematic and longer-form workflows | High |
| Luma Ray (`ray-2`, `ray-2-flash`) | Fast stylized/cinematic iteration | High |
| Vidu Q series (`viduq1` etc.) | Multi-mode reference workflows | Medium-high |

## Fast-Moving Competitive Layer

| Family | Why it matters now | API access reality |
|--------|--------------------|--------------------|
| Seedance | Strong multi-shot narrative quality and motion fidelity | Public model pages are clear, public API details are still fragmented across providers |
| Kling | High-quality motion and consumer momentum | Official model announcements are public; API access is often partner-mediated |
| Hailuo | Fast improvement cadence in high-motion scenes | Available through partner APIs and unified gateways |

## Open-Source Frontier

| Model | Best fit | Notes |
|-------|----------|-------|
| Wan2.2 | Self-hosted text/image-to-video research workflows | Good default for privacy-first stacks |
| HunyuanVideo 1.5 | Open video generation experimentation | Strong option when custom infra is acceptable |
| CogVideoX | Broad community tooling and compatibility | Useful fallback in local/open setups |

## Practical Recommendation

- Keep one premium model, one fast model, and one open/local fallback in every production pipeline.
- Re-validate model IDs and limits before high-volume runs.
