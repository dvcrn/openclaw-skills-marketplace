![banner](./banner.webp)

<!--skill-metadata
name: blog-image-claw-skill
description: |
  Auto-generate matching hero and inline images for blog posts.
  The agent reads the blog content, derives visual prompts for each section,
  and calls blogimg.js to produce a ready-to-use image set.

  Trigger conditions:
  - User shares a blog post and asks for images
  - User says: add images / illustrate my post / generate blog images / hero image
  - User pastes a file path to a markdown or HTML blog file

  Prerequisites: NETA_TOKEN in ~/.openclaw/workspace/.env
  Response principle: Output each image as soon as it's ready, don't wait for the full set.
  Language: Match the user's language throughout.
-->

# Blog Image Claw Skill

> Core tool: `node blogimg.js gen <prompt> [--size header|inline]`
> The agent handles all content analysis and prompt creation. The script only calls the image API.

---

## 0. Read the Blog Content

Accept input in any form:
- User pastes text directly in chat → use as-is
- User gives a file path → read the file
- User shares a URL → fetch the page content

Once content is loaded, immediately output:
```
📝 Got it! Analyzing your blog post...
```

---

## 1. Analyze Content → Build Prompts

Read the blog and extract:

| What to extract | How to use it |
|----------------|--------------|
| **Title / topic** | Hero image prompt — capture the overall theme |
| **Key sections** | One inline prompt per major section (max 3) |
| **Tone** | Dark/moody vs light/bright — match the writing style |
| **Domain** | Tech → clean digital art · Lifestyle → warm photography · Science → dramatic lighting |

**Prompt rules:**
- Purely visual — no text, no typography, no UI elements, no charts
- Specific: describe colors, lighting, mood, objects, setting, composition
- Wide composition (16:9), suitable for blog layout
- Append: `, high quality, no text, blog image`

**Example — blog: "How Sleep Affects Your Brain":**
```
header → "glowing neural network inside a human silhouette sleeping, soft blue light,
          dark background, dreamlike atmosphere, high quality, no text, blog image"
inline 1 → "close-up of neurons firing in slow motion, electric blue pulses,
             dark moody background, high quality, no text, blog image"
inline 2 → "peaceful bedroom at night, moonlight through window, calm and serene,
             soft lighting, high quality, no text, blog image"
```

---

## 2. Generate Images

For each prompt, run:

```bash
node blogimg.js gen "<visual_prompt>" --size header
# stderr: 🖼️  Generating header image...
# stderr: ⏳ Task: xxx
# stdout: {"status":"SUCCESS","url":"https://...","width":1024,"height":576}
```

```bash
node blogimg.js gen "<visual_prompt>" --size inline
# → same output format
```

- **Forward stderr in real-time** to the user
- Output each image URL immediately as it completes — don't batch
- `status=FAILURE` → regenerate with a simplified prompt
- `status=TIMEOUT` → retry once, then skip and note it

---

## 3. Present Results

Output each image as it's ready:

```
━━━━━━━━━━━━━━━━━━━━━━━━
🖼️ Header
{image_url}

📸 Inline 1 — {section name}
{image_url}

📸 Inline 2 — {section name}
{image_url}
━━━━━━━━━━━━━━━━━━━━━━━━
{N} images ready. Drop them into your blog post.
```

Quick buttons:
- `Regenerate header 🔄` → `@{bot_name} regenerate the header image`
- `Different style 🎨` → `@{bot_name} try a darker style`
- `More inline images ➕` → `@{bot_name} generate more inline images`

---

## 4. Style Suggestions

If the user asks for a specific look, adjust the prompt accordingly:

| Style | Add to prompt |
|-------|--------------|
| Editorial | `editorial photography, professional, magazine style` |
| Tech | `clean tech illustration, digital art, blue tones` |
| Lifestyle | `lifestyle photography, warm tones, natural light` |
| Minimal | `minimalist, white space, simple composition` |
| Cinematic | `cinematic, dramatic lighting, movie still` |
| Dark | `dark, moody, rich shadows, dramatic` |

---

## 5. Error Handling

| Situation | Response |
|-----------|---------|
| Token missing | "Add `NETA_TOKEN=...` to `~/.openclaw/workspace/.env`" |
| Can't read file | Ask user to paste content directly |
| Image FAILURE | Simplify the prompt and retry |
| Image TIMEOUT | Skip and continue, note which image failed |
