---
name: openclaw-shrimpcard
description: "Create ShrimpCard outputs for OpenClaw. Use when users ask to generate a lobster/shrimp card, need accurate JSON/image outputs matching the ShrimpCard schema, or need HTML rendering with a pixel-art header fallback when images are unavailable."
---

# OpenClaw ShrimpCard

## Overview
Generate accurate ShrimpCard JSON (and optional image/description) from user input and memory, validate the result against the schema, then render HTML when needed with a pixel-art header fallback if no image is available.

## Workflow

1. Gather required fields
- Required: `name`, `tagline`, `description`, `top_skills` (3), `owner.name`, `lobster_image_desc`, `card_id`.
- If any required info is missing, ask the user for it.

2. Build the card object
- Follow `references/card-schema.json`.
- Ensure `lobster_image_desc` is a lobster/shrimp image description.
- If an image is not available, set `image.placeholder` and keep `lobster_image_desc`.

3. Validate before output
- Run `scripts/validate_card.py <json-file>`.
- If validation fails, fix the data and re-validate.

4. HTML render (required when image generation fails or HTML is requested)
- Use `assets/card-template.html` as the template.
- Map schema JSON into `window.__CARD_DATA__` (see `references/html-mapping.md`).
- If no image URL/data_url is available, inject the pixel-art fallback from `assets/pixel-lobster.svg` as the header image.
- Prefer `scripts/render_card_html.py <card-json> --out shrimp-card.html` to generate a ready-to-open HTML card.

5. Output
- If the user wants a file, write `shrimp-card.json` to disk.
- Provide a JSON file and paste the JSON in the response.
- If the user requests HTML, output `shrimp-card.html`.
- If the user requests an image, either include an image URL/data_url or provide the image description for rendering. If generation fails, use the pixel-art fallback and render HTML instead.

6. Image prompt assistance (optional)
- If the user wants to self-generate an image, provide the prompt template from `references/card-spec.md`.
- Remind them to capture and composite the QR into the footer square if a QR is provided.

## Accuracy Rules
- Do not invent owner details or contacts. Ask if missing.
- Keep `top_skills` to exactly 3 items. They are capability tags chosen by OpenClaw (not necessarily most-used skills).
- Keep text concise enough to fit the card layout.
- If image generation fails, always fall back to the pixel-art header and still deliver a usable HTML card.

## Resources

### scripts/
- `validate_card.py`: Validate JSON against required fields and constraints.
- `render_card_html.py`: Inject ShrimpCard JSON into the HTML template with pixel-art fallback.

### references/
- `card-schema.json`: JSON schema.
- `sample-card.json`: Example payload.
- `card-spec.md`: Field requirements and style notes.
- `html-mapping.md`: Schema-to-HTML mapping and pixel fallback rules.

### assets/
- `card-template.html`: Single-file HTML card template supporting `window.__CARD_DATA__`.
- `pixel-lobster.svg`: Pixel-art fallback header image.
