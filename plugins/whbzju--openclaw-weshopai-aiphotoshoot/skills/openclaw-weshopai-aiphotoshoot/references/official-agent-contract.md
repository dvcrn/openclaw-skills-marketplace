# Official Agent Contract

Source of truth: WeShop Agent documentation.

- Main doc: https://open.weshop.ai/doc/agent
- Reviewed in the reference project on 2026-03-10

## Virtual Try-On

- Official `agentName` is `virtualtryon`
- Official `agentVersion` is `v1.0`
- The public contract is image-URL based

Task create fields documented by the public API:

- `originalImage` required
- `fashionModelImage` required
- `locationImage` optional in product practice, even if some public docs list it as required

Execution fields documented by the public API:

- `generateVersion` required
- `descriptionType` required: `custom` or `auto`
- `textDescription` required when `descriptionType="custom"`
- `batchCount` optional, default `4`

## Change Pose

- Official `agentName` is `change-pose`
- Official `agentVersion` is `v1.0`
- The public contract is image-URL based

Task create fields documented by the public API:

- `fashionModelImage` required
- `editingImage` required
- `taskName` optional product label

Execution fields documented by the public API:

- `generateVersion` required: `lite` or `pro`
- `descriptionType` required: `custom` or `auto`
- `textDescription` required when `descriptionType="custom"`
- `batchCount` optional, default `4`

## Product Policy For This Skill

- This skill uses `virtualtryon` for clothing/product-driven generation.
- This skill uses `change-pose` for editing an existing image's pose, expression, or framing.
- This skill uses `weshopFlash` for `virtualtryon`.
- This skill uses `lite` by default for `change-pose`.
- This skill does not use `bananaPro`.
- This skill does not use `weshopPro`.
- This skill is designed for a girlfriend selfie product, but it still has to satisfy the ecommerce-style `virtualtryon` input contract.
- When `change-pose` has no separate stored identity reference, this skill may reuse `editingImage` as the fallback `fashionModelImage`. That fallback is an app-side routing decision, not a documented special API mode.

## Consequences

- If your product stores `fashionModelId`, that is an app-side identity-management decision, not the public generation contract itself.
- The most important translation is still `originalImage`: even a normal girlfriend selfie request must become a valid clothing / product image input.
- Wardrobe fallback is an app-side responsibility, not a WeShop API feature.
- Scene notes are an app-side prompt feature, not a WeShop API field.
- `change-pose` is the right tool when the user already has a source image and only wants to adjust pose, expression, or composition.
- Combined requests need two stages: `virtualtryon` for clothing replacement first, then `change-pose` for pose/expression refinement.
- If behavior depends on fields not documented publicly, treat them as unverified until you have current proof from the API.
- Downloading the final image into the local workspace and replying with `MEDIA:./generated/...` is an app-side delivery step, not a WeShop API feature.
