# Product Mapping

Translate user intent into hidden WeShop inputs. Keep the user-facing language human and girlfriend-photo-centric.

For this product, the user is not speaking in ecommerce API language. They will ask for:

- "发张自拍"
- "今天在做什么"
- "穿这件拍一张"
- "换个场景"

The job of the agent is to translate that into the right WeShop request backed by a persistent girlfriend profile.

## Lifecycle

This product has three operational modes:

1. `profile setup`
2. `photo generation` with `virtualtryon`
3. `image editing` with `change-pose`

If there is no stored girlfriend identity yet, you are still in setup mode.

## Setup Mapping

### Identity setup

Ask the user for `1-4` face photos that are:

- clear
- front-facing or near-front-facing
- not heavily occluded
- visibly the girlfriend's face

Then create the persistent identity:

- uploaded face photos -> WeShop `myFashionModel/create`
- stored result -> `fashionModelId`, `cover`, `images`

### Default outfits

Ask for common outfit / product images to store.

These become:

- stored wardrobe defaults
- reusable `originalImage` values later

### Default scenes

Ask for common scene images to store.

These become:

- stored scene defaults
- reusable `locationImage` values later

### Scene notes

If the user has no scene image, ask for text descriptions of common imagined scenes.

These become:

- stored `sceneNotes`
- prompt-only scene guidance later when no `locationImage` is available

## Generation Mapping

### Selfie / daily photo

Inputs:

- stored girlfriend identity
- default or newly uploaded outfit image
- optional default or newly uploaded scene image
- prompt built from the try-on template + current shot brief + optional stored scene note

Use `virtualtryon`.

### Wear this

Inputs:

- stored girlfriend identity
- new uploaded outfit image
- current or default scene
- try-on prompt

Use `virtualtryon`.

### Go here / scene change

Inputs:

- stored girlfriend identity
- current or default outfit image
- new scene image or stored scene image
- if only a scene note exists, merge it into the prompt instead

Use `virtualtryon`.

### Edit this image / tweak the pose

Typical requests:

- "把这张图姿势改一下"
- "表情自然一点"
- "头往左转一点"
- "手抬高一点"
- "镜头角度更像自拍"

Inputs:

- the user-provided image as `editingImage`
- stored girlfriend identity when available, otherwise the same `editingImage` as the fallback identity reference
- short edit instruction focused on pose / expression / framing

Use `change-pose`.

### Outfit change plus pose refinement

Typical requests:

- "穿这件，然后姿势更自然一点"
- "先换成这套衣服，再把表情调得更甜一点"
- "生成自拍后把头再侧一点"

Workflow:

1. run `virtualtryon` to satisfy the clothing or product part
2. choose the best try-on output
3. run `change-pose` on that output for pose / expression / framing refinement

## Attachment Delivery

- The WeShop API returns remote image URLs, but this skill must download them into the current workspace before replying.
- The bundled scripts return `primaryLocalImage` and `localImagePaths` for that purpose.
- In OpenClaw replies, attach the local file with a safe relative media line such as `MEDIA:./generated/weshop-xxx-1.png`.
- Do not reply with the raw WeShop CDN URL when a local downloaded file exists.

## Required Input Rule

- `originalImage` is mandatory in `virtualtryon`.
- That means actual image generation still needs a clothing / product image.
- Scene notes can replace a missing scene image.
- Scene notes cannot replace a missing outfit image.
- `editingImage` is mandatory in `change-pose`.
- If there is no stored or explicit identity reference for `change-pose`, this skill reuses `editingImage` as the fallback `fashionModelImage`.

## Default Resolution Order

### Outfit / `originalImage`

1. explicit request outfit image
2. explicit fallback outfit image
3. stored profile outfit default
4. configured default wardrobe image

### Scene / `locationImage`

1. explicit request scene image
2. stored profile scene image
3. stored profile scene note
4. configured default scene image

## Guardrails

- do not use the face image as both `fashionModelImage` and `originalImage`
- do not treat a background-only scene image as Figure 3 in the three-figure prompt
- do not invent `originalImage` if none exists
- do not skip setup when there is no stored identity
- if the user uploads a new outfit or scene and wants it remembered, append it to the profile instead of keeping it only in transient state
- do not use `change-pose` as a substitute for missing `originalImage` when the user is really asking for clothing replacement
- do not skip the second `change-pose` step when the user explicitly asks for pose or expression refinement after try-on
