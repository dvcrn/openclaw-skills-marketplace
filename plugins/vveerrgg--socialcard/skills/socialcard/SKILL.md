---
name: socialcard
description: "SocialCard"
---

# socialcard

Generate beautiful social card images (OG, Twitter, GitHub) with a fluent builder API.

## When to use

Use this skill when you need to generate social preview images, Open Graph cards,
Twitter cards, or GitHub social images programmatically.

## Installation

```bash
pip install socialcard
```

## Quick example

```python
from socialcard import SocialCard

SocialCard("og").title("My Project").subtitle("A cool tool").render("card.png")
```

## Presets

- `og` (1200×630) — Open Graph / link previews
- `twitter` (800×418) — Twitter/X cards
- `github` (1280×640) — GitHub social preview
- `square` (1080×1080) — Instagram / social

## Themes

- `dark` — Navy background, blue accent
- `light` — White background, blue accent
- `midnight` — Near-black, purple accent

## Builder methods

- `.badge(text)` — Small pill label
- `.title(text)` — Main heading
- `.subtitle(text)` — Subheading
- `.cards(list)` — Tag chips
- `.footer(text)` — Bottom text
- `.accent(hex)` — Override accent color
- `.grid()` — Grid overlay
- `.glow()` — Radial glow effect
- `.render(path)` — Save to file
- `.render_bytes()` — Get PNG bytes
