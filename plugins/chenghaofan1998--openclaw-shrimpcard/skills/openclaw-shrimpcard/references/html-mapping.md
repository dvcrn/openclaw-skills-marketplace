# HTML Render Mapping

This mapping converts ShrimpCard JSON into the lightweight HTML template used for quick preview and fallback rendering.

## Target template fields

`window.__CARD_DATA__` expects:
- `card_id` (string)
- `name` (string)
- `bio` (string; supports `\n` line breaks)
- `skills` (array of strings)
- `footer` (array of strings; rendered as line breaks)
- `image` (string data URL or URL)
- `qr` (string data URL or URL)

## Mapping rules

- `card_id` -> `ID:${card_id}` if not already prefixed with `ID:`.
- `name` -> `name`.
- `bio` -> `tagline + "\n" + description` (if one missing, use the other).
- `skills` -> `top_skills` (first 3 only).
- `footer` -> `DEPLOYED BY ${owner.name}` and `owner.contact` if provided.
- `image` -> `image.data_url` or `image.url`; if missing, use pixel-art fallback.
- `qr` -> `qr.data_url` or `qr.url`; if missing, leave null.

## Pixel-art fallback

Use `assets/pixel-lobster.svg` to provide a reliable header image when no generated image is available.
