# Clawy Image Edit Playbook

## Purpose

This playbook exists to keep Clawy generation consistent across different image providers.

Clawy is not a generic text-to-image workflow.
It is a **mother-image-preserving character edit workflow**.

Core principle:
- keep the same base character
- preserve silhouette and structure
- protect the original asset before applying inspiration
- change equipment / styling / scene intentionally
- avoid drift into random redesigns

---

## Capability Rule

A backend is considered **fully suitable** for Clawy Avatar only if it supports:
- image edit
- image-to-image
- reference-preserving generation

Plain text-to-image is **not equivalent**.

If only text-to-image is available:
- warn the user
- explain that consistency may drop sharply
- treat it as a fallback, not the recommended default

---

## Standard Input Contract

Every Clawy edit flow should try to supply:
- 1 mother image
- 1 edit prompt
- square avatar output
- high fidelity / strong reference preservation when supported
- png or other loss-light output when supported

Preferred outcome:
- same body
- same perspective family
- same claw / tail / screen-face identity
- different equipment, outfit, theme, or scene

---

## Core Prompt Structure

A stable Clawy edit prompt usually contains four layers:

1. **Body lock**
   - do not change the base body
   - preserve silhouette, proportions, claw scale, tail placement, screen-face behavior, floating structure
   - do not add legs, feet, humanoid lower limbs, or walking anatomy
   - if the inspiration character has legs, keep only costume/accessory cues and reject the limb structure

2. **Equipment / theme change**
   - specify the new equipment or role direction
   - e.g. magical mage, platform adventurer, cyber hero, monster trainer

3. **Composition constraint**
   - avatar mode: square portrait, centered, upper body, clean background
   - event mode: same character placed in a new scene with controlled pose changes

4. **Style lock**
   - preserve the original cartoon / mascot / render style
   - avoid switching to realistic, painterly, or unrelated visual languages unless explicitly asked

---

## Avatar Edit Prompt Template

Use this as a provider-neutral structure:

```text
Use the provided mother image as the base character reference.
Keep the exact same character identity, silhouette family, body proportions, large claws, tail placement, screen-face logic, and floating body structure.
Do not add lower limbs.
Do not add legs, feet, knees, shoes, pants legs, or humanoid walking anatomy.
Do not add antennae unless explicitly requested.
If the inspiration includes a character with legs or a human body, only translate costume, prop, color, and accessory cues; do not inherit the limb structure.
Only change the equipment, outfit, headwear, accessories, and coordinated theme details.
Preserve the same cute, clean, collectible mascot style and keep the result highly consistent with the reference.
Compose as a centered square avatar portrait with a simple clean background.
Theme direction: <theme>.
Inspiration details to translate into mascot-friendly equipment: <inspiration>.
Color direction: <colors>.
Extra constraints: <extra>.
```

---

## Event / Scene Edit Prompt Template

Use this when the same Clawy character appears in a place or moment:

```text
Use the provided mother image as the base character reference.
Preserve the same exact character identity, body proportions, claws, tail, screen-face behavior, and overall silhouette.
This is the same character in a new scene, not a redesign.
Allow only minor pose adjustments needed for the scene.
Keep the same cute, stylized mascot rendering quality.
Place the character in this event scene: <scene>.
Scene storytelling goal: <goal>.
Keep the scene readable, charming, and clearly centered around the character.
```

---

## Provider Notes

### WaveSpeed
Best when the user wants one provider that exposes multiple edit models.

Suggested settings when available:
- model mode: nano / openai / fast
- use image-edit endpoint, not plain text-to-image
- keep sync/base64 options simple unless needed

### OpenAI direct
Best for a balanced direct edit workflow.

Suggested pattern:
- use image edit endpoint
- send the mother image as the source image
- prefer square output
- prefer high quality where supported

### Nano direct (Google)
Best when the user wants direct access to Google's native image generation/editing stack.

Suggested pattern:
- use image generation/editing API with both text and image input
- supply the mother image inline
- request image output modality
- keep the prompt strongly reference-preserving

### Ark direct
Best when the user wants ByteDance / Ark image generation directly.

Suggested pattern:
- prefer Seedream or Seededit image-to-image / edit-capable flows
- pass the mother image as image input / reference image input when supported
- for Seedream-style reference generation, prefer the official `prompt + image[]` mental model first
- if a specific model or SDK example uses `reference_images`, adapt to that model-specific API
- avoid silently downgrading to text-only generation for avatar consistency tasks
- do not treat Seedance as the default Clawy avatar backend

---

## Warning Copy for Text-to-Image Fallback

Recommended warning wording:

```text
Current backend appears to support only text-to-image generation, not image-edit / image-to-image.
Clawy can still attempt a fallback generation, but character consistency may degrade significantly.
The result may drift in silhouette, equipment structure, body proportions, or overall identity.
For best results, enable a true image-edit backend.
```

---

## Minimum Backend Examples

These are workflow examples, not strict API specs.
Adjust field names to the provider's official API.

### WaveSpeed edit

```json
{
  "images": ["<uploaded-mother-image-url>"],
  "prompt": "<clawy-edit-prompt>",
  "output_format": "png"
}
```

### OpenAI direct edit

```text
POST /images/edits
- model: gpt-image-1
- image: @mother_image.png
- prompt: <clawy-edit-prompt>
- size: 1024x1024
- quality: high
```

### Nano direct edit

```json
{
  "contents": [{
    "parts": [
      {"text": "<clawy-edit-prompt>"},
      {"inline_data": {"mime_type": "image/png", "data": "<base64-mother-image>"}}
    ]
  }],
  "generationConfig": {
    "responseModalities": ["IMAGE", "TEXT"]
  }
}
```

### Ark direct edit

```json
{
  "model": "doubao-seedream-5-0-260128",
  "prompt": "<clawy-edit-prompt>",
  "image": ["https://example.com/mother-image.png"],
  "response_format": "url",
  "size": "2K"
}
```

Recommended default Ark entry for Clawy black-box testing:
- base URL: `https://ark.cn-beijing.volces.com/api/v3`
- model: `doubao-seedream-5-0-260128`

If a specific Ark model or SDK example expects `reference_images` instead of `image`, follow the official model-specific API. But for Seedream 4.0-5.0 style black-box usage, treat `prompt + image[]` as the first pattern to try.

---

## Product Boundary Reminder

Clawy Avatar is not just “make a nice image.”

It is:
- identity-preserving
- reference-driven
- mascot-consistent
- future-scene-compatible

If a backend cannot reliably preserve the mother image, that limitation should be surfaced clearly instead of hidden.
