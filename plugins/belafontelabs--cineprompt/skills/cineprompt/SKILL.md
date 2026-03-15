---
name: cineprompt
description: "Build CinePrompt video prompts and share links without a browser. Converts natural language shot descriptions into structured CinePrompt state, generates prompt text, and creates shareable links (cineprompt.io/p/...). Use when asked to create video prompts, build CinePrompt links, describe shots for AI video generation, or batch-create prompts for a sequence of shots."
---

# CinePrompt Skill

Build CinePrompt prompts and share links directly — no browser needed.

## How It Works

1. User describes a shot in natural language
2. You translate it into a CinePrompt state JSON object
3. The `create-share-link.js` script inserts it into Supabase and returns a `/p/` share link
4. User gets the link + prompt text to copy into any AI video tool

## Authentication

Requires a CinePrompt API key (Pro subscribers only). Set via:
- `--api-key cp_xxx` flag
- `CINEPROMPT_API_KEY=cp_xxx` env var

Internal/owner use: set `CINEPROMPT_SERVICE_KEY` env var for direct insert (bypasses Pro check).

## Creating a Share Link

```bash
echo '<STATE_JSON>' | node <skill>/scripts/create-share-link.js --api-key cp_xxx
```

Output is JSON: `{"url":"https://cineprompt.io/p/abc123","shortCode":"abc123","promptText":"...","mode":"single"}`

You can also pass the prompt text explicitly if you've crafted it by hand:

```bash
echo '{"state":<STATE_JSON>,"prompt":"Your custom prompt text"}' | node <skill>/scripts/create-share-link.js --api-key cp_xxx
```

## State JSON Structure

```json
{
  "mode": "single",
  "complexity": "complex",
  "subjectType": "character|object|vehicle|creature|landscape|abstract",
  "fields": { ... },
  "shots": [],
  "characters": []
}
```

### Required Top-Level Fields

- `mode`: Always `"single"` for now (multishot/fm support later)
- `complexity`: `"simple"` or `"complex"` — complex unlocks format, camera body, lens, film stock, color science
- `subjectType`: Which subject panel to show
- `fields`: Object mapping field names to values (strings or arrays)

### Field Reference

All valid field names and values are in `<skill>/field-values.json`. Key fields:

**Style:**
- `media_type` (array): `["cinematic"]`, `["cinematic","documentary"]`, etc.
- `documentary_style`: only when documentary is in media_type
- `genre`: only when cinematic is in media_type (array OK)
- `commercial_type`: only when commercial is in media_type
- `tone` (array): `["peaceful"]`, `["dramatic","moody"]`
- `format`: (complex only) `"35mm Film"`, `"16mm Film"`, `"DSLR / Mirrorless"`, etc.

**Subject — depends on subjectType:**
- landscape: `land_season`, `land_scale`
- character: `char_label`, `age_range`, `build`, `hair_style`, `hair_color`, `subject_description`, `wardrobe`, `expression`, `body_language`, `framing`
- creature: `creature_category`, `creature_label`, `creature_size`, `creature_body`, `creature_skin`, `creature_description`
- object: `obj_description`, `obj_material`, `obj_condition`, `obj_scale`
- vehicle: `veh_type`, `veh_description`, `veh_era`, `veh_condition`
- abstract: `abs_description`, `abs_quality`, `abs_movement`

**Actions:**
- `movement_type` (array): `["walking"]`, `["running","turning"]`
- `pacing`: `"in real-time"`, `"in slow motion"`, `"time-lapse"`, etc.
- `action_primary`: free text describing the primary action

**Environment:**
- `setting`: `"exterior"`, `"interior"`, `"interior to exterior"`, `"exterior to interior"`
- `location_type`: `"open field, meadow"`, `"urban street"`, `"forest"`, etc.
- `custom_location`: free text location description
- `location`: free text additional location details
- `env_time`: `"golden hour, warm late afternoon light"`, `"night"`, `"dawn"`, etc.
- `weather`: `"clear sky"`, `"overcast"`, `"rain"`, `"fog"`, etc.
- `props`: free text
- `env_fg`, `env_mg`, `env_bg`: foreground/midground/background free text

**Cinematography:**
- `shot_type`: `"establishing shot"`, `"close-up"`, `"wide shot"`, `"medium"`, etc.
- `movement`: `"pull out"`, `"push in"`, `"dolly"`, `"tracking"`, `"static"`, `"orbit"`, etc.
- `camera_body`: (complex) `"ARRI Alexa 65"`, `"RED V-Raptor"`, `"Sony Venice 2"`, etc.
- `focal_length`: `"24mm lens"`, `"35mm lens"`, `"50mm lens"`, `"85mm lens"`, etc.
- `lens_brand`: (complex) `"Cooke S4/i"`, `"ARRI Master Prime"`, etc.
- `lens_filter`: (complex) `"Black Pro-Mist"`, `"Glimmerglass"`, etc.
- `dof`: `"deep focus"`, `"shallow depth of field, bokeh"`, `"tilt shift miniature"`, etc.
- `lighting_style`: `"soft light"`, `"hard light"`, `"high contrast"`, `"silhouette"`, `"backlight"`, etc.
- `lighting_type`: `"daylight"`, `"moonlight"`, `"candlelight"`, `"neon"`, etc.
- `key_light`, `fill_light`: (complex) free text

**Palette:**
- `color_science`: (complex) `"ARRI LogC3 flat log footage, ungraded"`, etc.
- `film_stock`: (complex) `"Kodak Portra 400 film colors"`, `"Kodak Vision3 500T film colors"`, etc.
- `color_grade`: `"warm tones"`, `"cool tones"`, `"teal and orange"`, `"desaturated"`, `"black and white"`, etc.
- `palette_colors`: free text (primary/secondary colors)
- `skin_tones`: free text

**Sound:**
- `sfx_environment` (array): `["birds singing, nature ambience"]`, `["city traffic"]`, `["wind"]`
- `sfx_interior` (array): `["room tone"]`, `["clock ticking"]`
- `sfx_mechanical` (array): `["engine"]`, `["machinery"]`
- `sfx_dramatic` (array): `["bass rumble"]`, `["heartbeat"]`
- `ambient`: free text custom ambient/SFX
- `music_genre`: `"orchestral score"`, `"electronic score"`, `"jazz score"`, etc.
- `music_mood`: `"tense, building"`, `"melancholic, sparse"`, etc.
- `music`: free text custom music description

## Translation Guide

When a user describes a shot, map their words to CinePrompt fields:

| User says | CinePrompt field(s) |
|-----------|---------------------|
| "golden hour" | `env_time: "golden hour, warm late afternoon light"` |
| "pulling back" / "pulling out" | `movement: "pull out"` |
| "birds chirping" | `sfx_environment: ["birds singing, nature ambience"]` |
| "empty land" / "open field" | `subjectType: "landscape"`, `location_type: "open field, meadow"` |
| "cinematic documentary" | `media_type: ["cinematic", "documentary"]` |
| "establishing shot" | `shot_type: "establishing shot"` |
| "bokeh" / "blurry background" | `dof: "shallow depth of field, bokeh"` |
| "everything in focus" | `dof: "deep focus"` |
| "handheld feel" | `movement: "handheld"` |
| "slow motion" | `pacing: "in slow motion"` |
| "warm look" | `color_grade: "warm tones"` |
| "shot on film" | `format: "35mm Film"` (complex) |

## Picking the Right Complexity

- **Simple**: Use for most shots. Covers style, subject, actions, environment, basic cinematography, palette, sound.
- **Complex**: Use when the user specifies camera body, lens brand, film stock, color science, lens filters, or custom lighting rigs. These fields only appear in complex mode.

## Example

User: "A weathered fisherman standing on a dock at dawn, fog rolling in, handheld close-up, desaturated"

```json
{
  "mode": "single",
  "complexity": "simple",
  "subjectType": "character",
  "fields": {
    "media_type": ["cinematic"],
    "tone": ["moody"],
    "char_label": "A weathered fisherman",
    "subject_description": "Deep wrinkles, sun-damaged skin, salt-crusted hands",
    "expression": "stoic, gazing out to sea",
    "pacing": "in real-time",
    "setting": "exterior",
    "location_type": "dock, pier",
    "env_time": "dawn, first light",
    "weather": "fog",
    "shot_type": "close-up",
    "movement": "handheld",
    "dof": "shallow depth of field, bokeh",
    "lighting_style": "soft light",
    "lighting_type": "daylight",
    "color_grade": "desaturated",
    "sfx_environment": ["waves crashing, water ambience"]
  },
  "shots": [],
  "characters": []
}
```

Then pipe it to the script and send the user the resulting URL.

## Batch Workflow

For multi-shot sequences, create each shot as a separate share link. Present them as a numbered list with URLs. The user can then open each, tweak, and copy prompts into their video tool of choice.

## Notes

- The script auto-generates prompt text matching CinePrompt's frontend logic (section ordering, merge rules, sentence assembly)
- You can override with `--prompt` if you want to hand-craft the text
- Share links restore the full form state including complexity tab and subject type
- Valid field values: check `<skill>/field-values.json` for exact button values
- Array fields (media_type, tone, sfx_*, movement_type) accept multiple values
- Free text fields (custom_location, subject_description, action_primary, etc.) accept any string
