---
name: theta-edgecloud-skill
description: "Theta EdgeCloud API-key-first runtime scaffold with secure command-scoped auth and dry-run safety."
---

# Theta EdgeCloud Skill (Cloud API Runtime)

## Dedicated inference status (revalidated 2026-03-11)
- **Dedicated OpenAI-compatible inference (`theta.inference.models`, `theta.inference.chat`) was revalidated successfully after Developer Plan / quota upgrade.**
- Important readiness nuance: endpoint creation is not instantly probe-ready.
- Observed post-upgrade warm-up pattern during successful live validation:
  - early authenticated `GET /v1/models` returned transient `404`, then transient `502`, then succeeded
  - authenticated `POST /v1/chat/completions` succeeded after warm-up
- Operational guidance:
  - use authenticated readiness retries for ~1-2 minutes before declaring dedicated endpoint failure
  - prefer `vm_gt1` first when allocator capacity is available
  - if `vm_gt1` is capacity-blocked, fall back to `vm_gt2` or V100-backed options

## Credential scope model (important)
This skill is command-scoped: only provide the credentials needed for the command family you use.

- Controller/deployment/project commands: `THETA_EC_API_KEY`, `THETA_EC_PROJECT_ID`
- Balance command: add `THETA_ORG_ID`
- On-demand inference commands: `THETA_ONDEMAND_API_TOKEN` or `THETA_ONDEMAND_API_KEY`
- Inference endpoint commands: `THETA_INFERENCE_ENDPOINT` + auth (`THETA_INFERENCE_AUTH_TOKEN` or user/pass)

Credentials above are not globally required all at once.

## Quick setup (new users)
1) Log in at `https://www.thetaedgecloud.com/`.
2) Go to **Account -> Projects** and select your project.
3) Click **Create API Key** and copy the key.
4) Provide these on install/setup prompt:
   - `THETA_EC_API_KEY`
   - `THETA_EC_PROJECT_ID`
5) (Recommended for on-demand image/video generation) create On-demand API key/token and set:
   - `THETA_ONDEMAND_API_KEY` (or `THETA_ONDEMAND_API_TOKEN`)
6) For dedicated deployments / GPU-backed serving, check **Account -> Quota** and click **Increase Quota** if needed.
   - Default machine-type quotas may be too low (or zero) for dedicated GPU deployment creation.
   - Current live operator guidance: add at least **$20** in credits first so the organization can reach **Developer Plan**, then retry **Increase Quota** for fuller functionality.
   - Higher quota tiers may still exist beyond Developer Plan.

If a command says a key is missing, run `theta.auth.capabilities` to see exactly what to configure.

This runtime artifact is scoped to cloud API operations only.

## Security behavior (explicit)
- Runtime command handlers do not execute local shell commands.
- Runtime does not read local files for upload operations.
- Runtime does not call localhost/default local RPC endpoints.
- Dedicated inference endpoint override via `args.endpoint` is disabled in runtime commands; use `THETA_INFERENCE_ENDPOINT`.
- Runtime secret resolution uses OpenClaw secret provider first, then env fallback for:
  - `THETA_ONDEMAND_API_TOKEN`
  - `THETA_INFERENCE_AUTH_TOKEN`
  - `THETA_INFERENCE_AUTH_USER` / `THETA_INFERENCE_AUTH_PASS`
- Paid/mutating operations are user-triggered and can be gated by `THETA_DRY_RUN=1`.

## Credential model (what users actually need)
Users need a Theta EdgeCloud account with billing/credits enabled for paid operations.

Use only credentials required for the feature set you plan to call:

- Deployments API:
  - `THETA_EC_API_KEY`
  - `THETA_EC_PROJECT_ID`
- Dedicated inference endpoint:
  - `THETA_INFERENCE_ENDPOINT`
  - EITHER basic auth:
    - `THETA_INFERENCE_AUTH_USER`
    - `THETA_INFERENCE_AUTH_PASS`
  - OR bearer token auth:
    - `THETA_INFERENCE_AUTH_TOKEN`
- On-demand model API:
  - `THETA_ONDEMAND_API_TOKEN`
- Theta Video API:
  - `THETA_VIDEO_SA_ID`
  - `THETA_VIDEO_SA_SECRET`

## Runtime-only package
This ClawHub artifact is a dist/docs bundle intended for transparent inspection and low scanner surface.

## Env knobs (selected)
- `THETA_DRY_RUN`
- `THETA_EC_API_KEY`
- `THETA_EC_PROJECT_ID`
- `THETA_ORG_ID`
- `THETA_INFERENCE_ENDPOINT`
- `THETA_INFERENCE_AUTH_USER`
- `THETA_INFERENCE_AUTH_PASS`
- `THETA_INFERENCE_AUTH_TOKEN`
- `THETA_ONDEMAND_API_TOKEN`
- `THETA_ONDEMAND_API_KEY`
- `THETA_VIDEO_SA_ID`
- `THETA_VIDEO_SA_SECRET`
- `THETA_HTTP_TIMEOUT_MS`
- `THETA_HTTP_MAX_RETRIES`
- `THETA_HTTP_RETRY_BACKOFF_MS`


## AI Services coverage
- Deployments API: list + create + stop + delete
- Dedicated model templates: standard + custom
- On-demand model APIs: live discovery + infer/status/poll
- Dedicated inference endpoint: models + chat
- Dedicated deployments listing
- Jupyter notebook listing
- GPU node and GPU cluster listing
- Persistent storage listing
- Agentic AI (chatbot) listing
- Theta Video APIs: list/upload/video/stream/ingestor operations

## Theta-only OpenClaw operating options (no other subscriptions)
If Theta is the only paid AI backend, this skill can still cover most OpenClaw execution routes:

- Content generation:
  - image/logo/creative generation (`flux`, `stable_diffusion_*`) via `theta.ondemand.infer`
  - image enhancement/upscale (`esrgan`)
  - identity-preserving generation (`instant_id`)
  - virtual try-on/product visualization (`stable_viton`)
  - video generation (`step_video`) and talking avatars (`talking_head`)
- Website AI features:
  - chatbot/support/Q&A/rewrite pipelines using on-demand LLMs (`llama_3_8b`, `llama_3_1_70b`)
- Vision/media intelligence:
  - captioning/alt-text (`blip`), object detection (`grounding_dino`), transcription (`whisper`)
- Video infrastructure:
  - upload/video/stream/ingestor operations via `theta.video.*`
- Compute/ops:
  - VM/deployment lifecycle + GPU/storage listings + capability/balance checks via `theta.deployments.*`, `theta.ai.*`, `theta.auth.capabilities`, `theta.billing.balance`

Recommended reliability route:
- Prefer on-demand + video/controller flows for production automation.
- Current validated daily-use routes include `flux` image generation, `step_video` on-demand video generation, and dedicated OpenAI-compatible inference after readiness warm-up.
- Dedicated endpoint commands are now valid when the project has quota/plan support, but should use authenticated readiness retries instead of immediate fail-fast assumptions.

## Organization & Project scope
- Theta dashboard uses Organization + Project context.
- Runtime commands are project-scoped and require explicit `projectId` where relevant.
- Org membership/invite/session management endpoints are web-dashboard auth flows and not included in this skill runtime.


## API key vs user/password auth (validated)
- API key (`THETA_EC_API_KEY`) + project/org IDs can access project-scoped controller APIs and org balance.
- API key is sufficient for key runtime operations; dashboard username/password is not required for these flows.
- Username/password session auth is still required for account-management endpoints (org/project membership, invite, charge usage history APIs).


## On-demand API key alias
The runtime accepts either `THETA_ONDEMAND_API_TOKEN` or `THETA_ONDEMAND_API_KEY` for on-demand model API auth.


## Reliability behavior
- `theta.ai.dedicatedDeployments.list` now emits warning metadata if serving-template catalog calls fail; this avoids silent empty output.
- `theta.ondemand.listServices` returns service entries tagged by source (`live` or `catalog`) and includes fallback reason/warning fields when live discovery is unavailable.
- `step_video` now uses service-aware timeout behavior:
  - submit timeout is automatically raised above generic HTTP defaults
  - poll/completion timeout auto-scales from requested video size when the request status exposes frame/fps metadata
  - sizing rounds up with extra variance buffer to reduce false local timeouts under load


## Auth diagnostics
Use `theta.auth.capabilities` to quickly see which command families are available with the current credential set and which env vars are missing.


## First-run setup command
Use `theta.setup` to get a one-screen checklist for new users, including where to create API keys and which env vars to set.
