---
name: Screenshots
description: "Create professional App Store and Google Play screenshots with automatic sizing, device frames, marketing copy, and iterative visual learning."
---

## Quick Reference

| Context | File |
|---------|------|
| Store dimensions and specs | `specs.md` |
| Marketing text overlays | `text-style.md` |
| Visual templates by category | `templates.md` |
| Full creation workflow | `workflow.md` |
| Learning from feedback | `feedback.md` |

## Memory Storage

User preferences stored at `~/screenshots/memory.md`. Read on activation.

**Format:**
```markdown
# Screenshots Memory

## Style Preferences
- style: dominant-color | gradient | minimal | dark | light
- fonts: preferred headline fonts
- frames: with-frame | frameless | floating
- tone: punchy | descriptive | minimal

## Learned Patterns
- templates that converted well
- font/size combinations that worked
```

Create folder on first use: `mkdir -p ~/screenshots`

## Workspace Structure

```
~/screenshots/
├── memory.md              # Style preferences (persistent)
├── {app-slug}/
│   ├── config.md          # Brand: colors, fonts, style
│   ├── raw/               # Raw simulator/device captures
│   ├── v1/, v2/           # Version exports
│   └── latest -> v2/      # Symlink to current
└── templates/             # Reusable visual templates
```

## Core Workflow

1. **Intake** — Get raw screenshots + app icon + brand colors
2. **Size** — Generate all required dimensions per `specs.md`
3. **Style** — Apply backgrounds, device frames, text overlays
4. **Review** — Use vision to verify quality before sending
5. **Iterate** — Adjust based on user feedback
6. **Export** — Organize by store/device/language

## Quality Checklist

Use vision model to verify EVERY screenshot set:
- [ ] Text readable at thumbnail size?
- [ ] No text in unsafe zones (corners, notch area)?
- [ ] Consistent style across all screenshots?
- [ ] Device frames match the target size?
- [ ] Colors harmonious with app branding?

**If ANY check fails** → fix before presenting to user.

## Versioning Rules

- **Never overwrite** — each batch goes in `v{n}/`
- **Symlink `latest`** to current approved version
- **config.md** stores brand decisions for regeneration
- **Compare versions** when user says "go back to the old style"
