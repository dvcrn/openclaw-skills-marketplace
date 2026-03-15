# Replicate Routing

**Best for:** rapid provider comparison and hosted access to many video models.

## Setup

```bash
export REPLICATE_API_TOKEN=r8_xxx
```

## Practical Usage Pattern

1. Pick model slug from Replicate library
2. Submit prediction request
3. Poll until completion
4. Download output before URL expiry

## Known Example

- `bytedance/seedance-1.5-pro` (text/image to video with synced audio support)

## Routing Advice

- Use Replicate for model evaluation and fallback coverage
- Do not hardcode temporary community aliases as stable IDs
- Keep a provider-neutral abstraction so you can swap models quickly

## Reliability Tips

- Persist prediction IDs for audits
- Standardize timeout and retry policy
- Validate output duration and fps before downstream edits
