---
name: openclaw-weshopai-aiphotoshoot
description: "Project-specific guidance for building a persistent girlfriend selfie workflow on top of WeShop image agents. Use when the user needs to set up a girlfriend identity from face photos, store default outfits/scenes, generate later selfies/photoshoots with WeShop `virtualtryon`, or edit an existing image with WeShop `change-pose`."
---

# OpenClaw WeShop AI Photoshoot

Use this skill for OpenClaw only. The target product is a C-end girlfriend selfie experience, and the image engine is WeShop `virtualtryon` plus `change-pose`. This skill exists to translate:

- user-facing girlfriend selfie requests
- into a persistent stored identity + default asset profile
- and then into valid WeShop image-agent executions

## Read First

Read [references/product-mapping.md](references/product-mapping.md) first.

Then read [references/official-agent-contract.md](references/official-agent-contract.md) before changing inputs or generation behavior.

Use the bundled scripts for deterministic API work:

- `{baseDir}/scripts/setup_profile.py`
- `{baseDir}/scripts/inspect_profile.py`
- `{baseDir}/scripts/generate_photo.py`
- `{baseDir}/scripts/change_pose.py`
- `{baseDir}/scripts/query_execution.py`

## Requirements

This skill requires `WESHOP_API_KEY`, but the bundled scripts try to resolve it automatically.

Resolution order:

1. process env: `WESHOP_API_KEY`
2. explicit dotenv path: `WESHOP_ENV_FILE`
3. current working directory `.env`
4. parent-directory `.env` files
5. when running inside an OpenClaw `workspace-*` directory, sibling global `workspace/.env`

If the key is still missing, say that explicitly before attempting any setup or generation.

This skill also uses a persistent profile JSON for the girlfriend identity and default assets.

Profile resolution order:

1. explicit `--profile`
2. env `WESHOP_PROFILE_FILE`
3. current working directory `.weshopai-aiphotoshoot-profile.json`

## Core Rules

- This skill has two phases:
  - `profile setup`
  - `image generation or editing`
- Treat this as an adult, consent-based photoshoot workflow only:
  - do not help create or edit sexualized images of minors or age-ambiguous people
  - if the subject's age is unclear, ask the user to confirm the subject is an adult before proceeding
  - do not help impersonate a real person who has not consented to being used as the stored identity
  - if the user is using a real person's face photos, remind them those photos are being sent to WeShop to build the stored identity
- At the start of every new session, inspect the local profile first before asking setup questions:
  - run `{baseDir}/scripts/inspect_profile.py`
  - if `setupComplete=true` or `identityReady=true`, assume the girlfriend identity is already stored locally
  - briefly acknowledge the remembered name/defaults instead of asking for face photos again
  - only ask for missing pieces that are actually needed for the current request
- If there is no stored girlfriend identity yet after the profile inspection, start with setup instead of trying to generate immediately.
- During setup, ask for `1-4` clear front-face photos.
- The face photos should be:
  - front-facing or near-front-facing
  - clear and high enough quality
  - without heavy occlusion
  - real face photos, not clothing or background shots
- After the user confirms those photos represent the girlfriend, create and store the WeShop `fashionModelId`.
- Then ask whether the user has default outfits and scenes they want to store:
  - outfits are stored as reusable `originalImage` defaults
  - scenes are stored as reusable `locationImage` defaults
  - if the user has no scene image, store scene notes as text
- Do not pretend that a text-only wardrobe note can replace `originalImage`. Actual generation still needs an outfit/product image.
- Later, when the user asks for a selfie or a photo:
  - reuse the stored identity
  - prefer a newly uploaded outfit or scene if provided
  - otherwise fall back to the stored defaults
- If the user uploads a new outfit or scene and wants it reusable later, append it to the profile.
- Choose the WeShop agent based on the user intent:
  - use `virtualtryon` when the request is mainly about changing clothes, applying a product image, or generating a new selfie/photoshoot from stored identity + outfit/scene inputs
  - use `change-pose` when the user already has an image and mainly wants to edit that image's pose, expression, hand placement, head angle, framing, or other local composition details
  - use `virtualtryon` first and `change-pose` second when the request combines clothing replacement with pose/expression refinement
- Use `weshopFlash` for `virtualtryon`.
- Use `lite` for `change-pose` unless the user explicitly asks for a stronger generation tier.
- Do not use `bananaPro` or `weshopPro` in this skill.
- Never fabricate image URLs. Only return WeShop outputs.
- The bundled scripts download generated images into `./generated/` by default and return `primaryLocalImage` / `localImagePaths`.
- In OpenClaw chat replies, always send the local downloaded file as the attachment:
  - put the normal caption in text
  - put `MEDIA:./generated/<file>` on its own line
  - use the script's returned relative path exactly
- Do not send the raw WeShop URL when `primaryLocalImage` is available.
- Do not use absolute paths like `MEDIA:/...`; OpenClaw expects a safe relative path such as `MEDIA:./generated/foo.png`.

## Conversation Workflow

### 0. Session Bootstrap

At the beginning of each new session:

1. Run `{baseDir}/scripts/inspect_profile.py`.
2. If the returned profile says `setupComplete=true` or `identityReady=true`:
   - do not restart setup
   - do not ask again for the girlfriend's base identity photos
   - briefly summarize what is already remembered:
     - girlfriend name
     - saved outfits
     - saved scenes / scene notes
3. If the current request can be fulfilled from the stored profile plus any newly uploaded assets, proceed directly to generation or editing.
4. Only ask setup questions for missing data that blocks the current request:
   - no stored identity => ask for face photos
   - no stored/default outfit and no newly uploaded outfit => ask for an outfit image if the user wants `virtualtryon`
   - no stored/default scene and no newly uploaded scene => ask only if the request needs a reusable scene or better scene control

### 1. Setup

When the user is setting up the girlfriend identity, do this:

1. Ask what the girlfriend looks like and request `1-4` clear face photos.
2. Confirm that these are the reference photos for the girlfriend identity.
3. Create and store the `fashionModelId`.
4. Ask for default outfit images to store as wardrobe defaults.
5. Ask for default scene images to store as scene defaults.
6. If the user has no scene images, ask for `1-3` text descriptions of common imagined scenes and store those as scene notes.
7. Explain clearly if they still have no outfit image:
   - generation can start later
   - but actual `virtualtryon` still needs at least one clothing/product image

### 2. Routing

Pick the tool path before generating:

1. If the user wants a new outfit, a new product, or a fresh photoshoot from stored defaults, use `virtualtryon`.
2. If the user gives an existing image and says things like "change the pose", "make her smile", "turn the head a bit", "raise the hand", or "fix the expression", use `change-pose`.
3. If the user wants both:
   - first run `virtualtryon` to get the right clothing/base image
   - then run `change-pose` on that output to refine pose, expression, or composition

### 3. Generation With `virtualtryon`

When the user later asks for a selfie or photo:

1. Resolve the stored girlfriend identity from the profile.
2. Resolve `originalImage` in this order:
   - newly uploaded outfit image
   - explicit fallback image
   - stored profile outfit default
   - configured fallback image
3. Resolve `locationImage` in this order:
   - newly uploaded scene image
   - stored profile scene image
   - scene note only, which should be merged into the prompt when there is no scene image
4. Build the final prompt from:
   - the try-on prompt template
   - the current shot request
   - the stored scene note if one is being used
   - a shot-style preset (`selfie`, `mirror-selfie`, `candid`, `portrait`)
   - explicit quality guardrails against warped anatomy / fashion-catalog framing
5. For selfie-like requests, prefer `--shot-style selfie` or `--shot-style mirror-selfie`.
6. If the first pass looks distorted, rerun with `--auto-refine` so the skill sends the best output through `change-pose` for anatomy/perspective cleanup.
7. Execute `virtualtryon` with `weshopFlash`.
8. After the script returns, use `primaryLocalImage` for the attachment reply.

### 4. Editing With `change-pose`

When the user wants to modify an existing image instead of generating a new clothing composition:

1. Use the provided image as `editingImage`.
2. Resolve `fashionModelImage` in this order:
   - explicit identity image
   - explicit `fashionModelId`
   - stored profile girlfriend identity
   - `editingImage` itself as the fallback identity reference when no separate profile identity exists
3. Convert the user request into a concise edit brief focused on pose, expression, framing, or body positioning.
4. Execute `change-pose` with `lite` by default.
5. If the user also wants clothing replacement, do not skip `virtualtryon`; run it first and only then send the chosen output into `change-pose`.
6. After the script returns, use `primaryLocalImage` for the attachment reply.

### 5. Ongoing Updates

When the user uploads a new outfit or scene during chat:

- use it for the current generation if requested
- if the user wants it remembered, append it to the stored profile

## Prompt Policy

- For `virtualtryon`, preferred three-figure try-on prompt:

```text
Replace the clothes of the person in Figure 3 with the clothes from Figure 1, and replace the skin, face, hairstyle, and hair color of the model with those from Figure 2
```

- For `virtualtryon`, standard two-image fallback for this skill:

```text
Replace the clothes of the person with the clothes from Figure 1, and replace the skin, face, hairstyle, and hair color of the model with those from Figure 2.
```

- Mapping rule:
  - Figure 1 => `originalImage`
  - Figure 2 => `fashionModelImage`
  - Figure 3 => only if there is a real third carrier/base-person image
- If there is no scene image but there is a stored scene note, merge that note into the final prompt instead of faking `locationImage`.

- For `change-pose`:
  - keep the prompt narrowly about the requested edit
  - default to `lite`
  - do not describe clothing replacement unless you intentionally want a second-stage edit after `virtualtryon`
  - if the user only wants to adjust an existing image, prefer an `edit brief` over a long generative prompt

## Scripts

Create or update the stored girlfriend profile:

```bash
python3 {baseDir}/scripts/setup_profile.py \
  --name Luna \
  --face-image /tmp/face-1.jpg \
  --face-image /tmp/face-2.jpg \
  --default-outfit daily=/tmp/outfit.png \
  --default-scene cafe=/tmp/cafe-scene.png \
  --scene-note bedroom="soft warm bedroom mirror selfie at night"
```

Inspect the stored profile before deciding whether setup is needed:

```bash
python3 {baseDir}/scripts/inspect_profile.py
```

Append a new reusable outfit or scene later:

```bash
python3 {baseDir}/scripts/setup_profile.py \
  --profile /path/to/.weshopai-aiphotoshoot-profile.json \
  --default-outfit date-night=/tmp/date-night-dress.png \
  --default-scene bookstore=/tmp/bookstore-scene.png
```

Generate a photo from the stored profile:

```bash
python3 {baseDir}/scripts/generate_photo.py \
  --profile /path/to/.weshopai-aiphotoshoot-profile.json \
  --shot-style selfie \
  --auto-refine \
  --shot-brief "daily candid girlfriend selfie at a cafe"
```

Generate with a newly uploaded outfit and a stored scene:

```bash
python3 {baseDir}/scripts/generate_photo.py \
  --profile /path/to/.weshopai-aiphotoshoot-profile.json \
  --original-image /tmp/new-outfit.png \
  --scene-key cafe \
  --shot-brief "cute selfie before leaving for coffee"
```

Edit an existing image with `change-pose`:

```bash
python3 {baseDir}/scripts/change_pose.py \
  --profile /path/to/.weshopai-aiphotoshoot-profile.json \
  --editing-image /tmp/input-selfie.png \
  --edit-brief "turn her head slightly left and add a softer smile"
```

Run `virtualtryon` first, then refine the chosen output with `change-pose`:

```bash
python3 {baseDir}/scripts/change_pose.py \
  --profile /path/to/.weshopai-aiphotoshoot-profile.json \
  --editing-image https://example.com/virtualtryon-output.png \
  --edit-brief "raise the phone slightly and make the pose more candid"
```

Reply with the downloaded local file, not the remote WeShop URL:

```text
[[reply_to_current]] 这是我生成好的版本。
MEDIA:./generated/weshop-<execution-id>-1.png
```

Inspect an execution:

```bash
python3 {baseDir}/scripts/query_execution.py --execution-id EXECUTION_ID
```

## Scope

This skill is about the full lifecycle for a persistent girlfriend selfie product built on WeShop image agents: setup, stored defaults, later generation, image edits, and incremental updates. Do not turn it into a generic ecommerce tutorial or a generic image prompt library.
