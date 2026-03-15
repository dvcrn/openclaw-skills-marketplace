---
name: clawy
description: "Bring your agent to life. Use when creating a cute, high-quality, memorable character for an OpenClaw-style agent from reference images, inspirations, and style preferences. Best for turning an agent from a plain tool into a digital presence with a stable look, collectible avatar style, and room for future scenes, events, and interaction."
---

# Clawy

Bring your agent to life.

Clawy gives an agent a visual identity people can recognize, like, remember, and build a relationship with.

In the current version, the first implemented capability is **Clawy Avatar**.

Clawy Avatar is used to create:
- a core character image
- a collectible-style profile picture
- themed character variants
- future scene/event images built on the same identity

## User Flow

When Clawy is used, follow this flow:

1. Ask the user what kind of identity they want for the agent.
2. Gather a small amount of useful creative input.
3. Check what image-edit capability is already available.
4. Generate the avatar as directly as possible.
5. Refine only if needed.

Do not start by dumping technical configuration details unless they are truly needed.
Do not add unnecessary pre-generation commentary about backend upgrades, model comparisons, or internal workflow unless the user explicitly asks.
Do not add unnecessary post-generation narration explaining what was generated if the image itself is the main deliverable.
The preferred interaction is: understand the user's needs, generate, then only discuss adjustments if needed.

## What to ask the user

Ask for a small amount of creative input, not a long interview.

Useful inputs:
- a few reference images
- inspiration sources
- a preferred vibe or personality
- favorite themes, colors, or archetypes
- whether they want the result to feel cute, cool, elegant, playful, cosmic, magical, streetwear, etc.

If relevant context already exists (for example in SOUL.md, USER.md, or a user-provided self-description), use it.

## What Clawy should produce

Clawy should generate a character that feels:
- cute
- memorable
- visually coherent
- high quality
- suitable as an avatar or digital alter-ego
- stable enough to support later scene-based storytelling

## Default behavior

By default, Clawy uses the bundled **Halfire Labs** mother image at `assets/default-mother-image.jpg`.

The bundled default mother image should be kept as a square, non-stretched avatar reference so downstream edit models do not need to invent a new framing when generating square profile outputs.

Only switch to a user-provided mother image if the user explicitly asks to replace it.

Do not ask whether to replace the mother image by default.

## Image Capability Rule

Clawy should prefer the image-edit capability already available in the user's environment.

Clawy Avatar is a reference-preserving workflow built around a mother image.
Because of that, a backend is only considered fully suitable by default if it supports image-edit / image-to-image behavior.

Default behavior:
- first use an already configured image-edit backend if one exists
- only ask the user to configure an API when no usable image-edit capability is available
- when discussing setup, distinguish clearly between aggregator access (for example WaveSpeed) and true direct-provider access (for example OpenAI direct, Nano direct, or Ark direct)
- do not treat plain text-to-image capability as equivalent to image-edit capability for avatar generation

If the environment only has text-to-image capability:
- warn clearly that Clawy's character consistency will likely degrade
- explain that identity, silhouette, equipment coherence, and mother-image preservation may break
- prefer asking the user to enable a true image-edit backend instead of silently proceeding as if the setup were sufficient
- if generation still proceeds, label it as a fallback / lower-confidence path rather than the default-recommended workflow

## Recommended Models

Recommended model order when available:
1. `google/nano-banana-2/edit`
2. `openai/gpt-image-1.5/edit`
3. `google/nano-banana-2/edit-fast`

If another image model is available and usable, Clawy may still proceed, but should briefly mention that the recommended models usually work better for this workflow.

## Image Backend Docs

If the user does not already have a usable image-edit capability, these are good places to start.

Clawy should recognize four common backend paths:
- WaveSpeed direct
- OpenAI direct
- Nano direct
- Ark direct

### WaveSpeed (platform)
Useful when the user wants a simple way to access multiple edit models from one provider.
- Nano Banana 2 Edit: https://wavespeed.ai/docs/docs-api/google/google-nano-banana-2-edit
- Nano Banana Pro Edit: https://wavespeed.ai/docs/docs-api/google/google-nano-banana-pro-edit
- OpenAI GPT-Image via WaveSpeed: https://wavespeed.ai/docs/docs-api/openai/openai-gpt-image-1

### OpenAI (direct)
Useful when the user wants a balanced, direct image-edit option.
- GPT Image 1 model docs: https://platform.openai.com/docs/models/gpt-image-1
- Image generation guide: https://platform.openai.com/docs/guides/image-generation

### Nano (direct / Google)
Useful when the user wants to call Google's native image-generation and editing stack directly instead of going through an aggregator.
- Gemini image generation docs: https://ai.google.dev/gemini-api/docs/image-generation
- Gemini API docs overview: https://ai.google.dev/gemini-api/docs
- Product/background announcement for Nano Banana 2: https://blog.google/innovation-and-ai/technology/developers-tools/build-with-nano-banana-2/

### Ark (direct / Volcengine)
Useful when the user wants to try ByteDance's official image-generation stack directly.
- Seedream 5.0 Lite API reference: https://www.volcengine.com/docs/82379/1541523?lang=zh
- Seedream 4.0-5.0 tutorial: https://www.volcengine.com/docs/82379/1824121
- Ark quickstart: https://www.volcengine.com/docs/82379/1399008

Important Clawy rule for Ark:
- prefer Seedream or Seededit style image-edit / reference-image workflows for avatar consistency
- do not treat Seedance as the default avatar backend for Clawy, because it is not the same thing as a mother-image-preserving avatar edit workflow
- when using Seedream-style reference generation, first try the official `prompt + image[]` pattern rather than assuming plain text-to-image
- if a model-specific Ark example uses a different field such as `reference_images`, adapt to that exact model/API shape

## Avatar Input Model

The user does **not** need to choose from rigid templates up front.

Clawy should accept natural creative input such as:
- “I want something like Frieren”
- “Make it feel like Chopper but cooler”
- “Streetwear, but more cosmic”
- “Use black corgi hood inspiration”
- “Cute but elegant, pastel colors”

Then Clawy should translate that input into a stable prompt structure.

When the user references a specific character, Clawy should not stop at overall vibe alone. It should also extract the character's **signature features** — the concrete visual elements that make the inspiration recognizable — and carry those into the equipment design.

Important asset-protection rule:
- borrow signature features, props, color systems, hats, outfit language, and accessories
- do not inherit body plan changes from the inspiration
- if the reference character has legs, humanoid anatomy, or a different species body, Clawy must still preserve the original mascot asset and reject those structural changes

Examples:
- Sakura-style inspiration -> wand, ribbons, sakura elements, magical-girl outfit cues
- Frieren-style inspiration -> staff, earrings, pale mage robes, restrained magical details
- Mario/Luigi-style inspiration -> signature hat, overalls, strong color pairing, platform-adventure outfit cues

## Templates and Inspiration

Templates are not just examples.

Templates are reusable prompt modules that stabilize generation.

A template bundles:
- proven prompt wording
- a useful equipment language
- a stable vibe/archetype
- color and styling tendencies
- constraints that help preserve the body

Inspiration is more free-form.

Clawy should combine:
- the user's inspiration sources
- the requested vibe
- one or more fitting template directions
- extracted signature features from the inspiration
- the stable mother-image rules

## Signature Features

When inspiration comes from a recognizable character or role, Clawy should identify the specific visual features that matter most.

These are often the details that make the final result feel truly “right”, such as:
- hats
- wands
- earrings
- overalls
- ribbons
- crowns
- robes
- staffs
- belts, straps, or armor cues
- signature props or costume elements

Clawy should translate those features into mascot-friendly equipment language instead of only copying the mood.

Useful template directions include:
- hiphop-streetwear
- hero-tech-armor
- platform-adventurer
- monster-trainer
- royal-regalia
- candy-cyber
- magical-mage
- animal-hood
- mascot-crown
- cosmic-companion

## Inspiration Sources

Inspiration can come from multiple directions:
- iconic character outfit language
- mascot / animal hood language
- helmets, crowns, and other headwear systems
- role archetypes (trainer, explorer, mage, pirate, idol, etc.)
- aesthetic worlds (cosmic, magical, cyber, royal, streetwear, etc.)

Use inspiration to enrich the equipment design, not to destroy the base mascot identity.

## Avatar Composition Rules

For profile pictures:
- square image
- centered portrait
- upper-body or bust framing
- character fills most of the frame
- simple soft background
- NFT/profile-picture readability
- no heavy scenery unless the user asks for a scene-based image

## Scene-Based Variant Rule

If the user wants the avatar to appear somewhere (for example, Hogwarts, Nasdaq, outer space, or a fantasy city), preserve the same character and treat the task as:
- same character
- new scene
- slight pose change allowed
- composition and storytelling must be intentionally specified

## Quality Check

After generation, inspect whether the result:
- looks lovable and recognizable
- feels visually coherent
- fits the requested vibe
- feels like a real character, not a random image
- could support future scene-based storytelling and interaction

## Bundled Resources

- `assets/default-mother-image.jpg` — bundled default Halfire Labs mother image
- `references/asset-rules.md` — stable asset and avatar rules
- `references/image-edit-playbook.md` — cross-provider image-edit guidance, warning rules, and example request patterns
- `scripts/generate_avatar.py` — sample generator helper with backend selection for WaveSpeed, OpenAI direct, Nano direct, and Ark direct

## Script Backend Notes

The bundled script supports these backend modes:
- `wavespeed`
- `openai-direct`
- `nano-direct`
- `ark-direct`

Environment variables expected by the script:
- WaveSpeed: `WAVESPEED_API_KEY`
- OpenAI direct: `OPENAI_API_KEY` (optional `OPENAI_BASE_URL`)
- Nano direct: `GEMINI_API_KEY` or `NANO_API_KEY` (optional `NANO_MODEL`, `NANO_BASE_URL`)
- Ark direct: `ARK_API_KEY` (optional `ARK_MODEL`, `ARK_BASE_URL`, defaults now target `https://ark.cn-beijing.volces.com/api/v3` + `doubao-seedream-5-0-260128`)

Example usage:
- `python3 scripts/generate_avatar.py --backend wavespeed --mode nano --template hero-tech-armor --inspiration "Frieren"`
- `python3 scripts/generate_avatar.py --backend openai-direct --template hiphop-streetwear`
- `python3 scripts/generate_avatar.py --backend nano-direct --template platform-adventurer`
- `python3 scripts/generate_avatar.py --backend ark-direct --template monster-trainer`

Ark note:
- Seedream black-box tests should prefer Ark's larger image size requirements (for example `2K`) rather than assuming 1024x1024 is acceptable.
