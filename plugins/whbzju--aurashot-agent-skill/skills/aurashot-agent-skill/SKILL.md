---
name: aurashot-agent-skill
description: "Use AuraShot to run virtual try-on or pose change workflows via AuraShot's Aesthetics API."
---

# AuraShot Agent Skill

Use the bundled Python script to run AuraShot aesthetic workflows: **Virtual Try-On** and **Pose Change**.

## What This Skill Does

- authenticates with a Studio API key
- routes user intent to the correct workflow (`virtual_try_on` or `pose_change`)
- calls AuraShot's Aesthetics API without exposing WeShop internals

## Before Running

Check for an AuraShot key in this order:

- `AURASHOT_API_KEY`
- `AURASHOT_STUDIO_KEY`

If neither key exists, stop and tell the user to:

- register at `https://www.aurashot.art/login`
- generate a key at `https://www.aurashot.art/studio?tab=keys`

## Decide The Workflow

Use `virtual_try_on` when the user wants to dress a model in a product, change the model, or change the scene.

Common user phrasing:
- "穿上这件"
- "换个模特"
- "换个场景"
- "用这件衣服拍一张"
- "把这件上身"

Use `pose_change` when the user has an existing image and only wants to change the pose, gesture, or body position.

Common user phrasing:
- "换个姿势"
- "改成站姿"
- "手放下来"
- "只改动作，人和背景不变"

If it is ambiguous, ask one concise clarification question before running.

## Input Rules

For `virtual_try_on`:
- require `--product-image` (the clothing/product)
- require `--model-image` (the person)
- require `--scene-image` (the background/location)
- optional `--description` (custom style prompt)
- optional `--version` (default: `weshopFlash`)

For `pose_change`:
- require `--original-image` (the image to modify)
- require `--description` (what pose/action to apply)
- optional `--version` (default: `lite`, use `pro` for higher quality)

## Run

### Virtual Try-On

```bash
python3 {baseDir}/scripts/aurashot.py generate \
  --workflow virtual_try_on \
  --product-image "https://example.com/clothes.jpg" \
  --model-image "https://example.com/model.jpg" \
  --scene-image "https://example.com/cafe.jpg" \
  --description "穿上这件，坐在窗边，像生活方式照片"
```

### Pose Change

```bash
python3 {baseDir}/scripts/aurashot.py generate \
  --workflow pose_change \
  --original-image "https://example.com/current.jpg" \
  --description "换个站姿，背景和人物不变"
```

### Query an existing job

```bash
python3 {baseDir}/scripts/aurashot.py query \
  --workflow virtual_try_on \
  --execution-id "returned_execution_id"
```

## Notes

- Keep end-user language natural. Do not expose workflow names or API parameters to the user.
- Image inputs can be public URLs (https://...) or local file paths — local files are uploaded automatically via AuraShot.
- For production use, omit `--wait` and poll with `query` to avoid long-running requests.
- See [references/api.md](references/api.md) for full payload reference.
