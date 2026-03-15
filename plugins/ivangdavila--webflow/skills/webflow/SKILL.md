---
name: Webflow
description: "Build, launch, and optimize Webflow sites with responsive design, CMS architecture, and clean handoffs."
---

## Quick Reference

| Topic | File |
|-------|------|
| Responsive design, breakpoints | `design.md` |
| CMS collections, headless API | `cms.md` |
| Forms, analytics, third-party | `integrations.md` |
| SEO, performance, accessibility | `optimization.md` |

## Memory Storage

User preferences stored at `~/webflow/memory.md`. Read on activation.

**Format:**
```markdown
# Webflow Memory

## Profile
- role: freelancer | agency | founder | developer | marketer
- design-source: figma | sketch | from-scratch | template
- cms-needs: none | blog | multi-collection | headless

## Preferences
- class-naming: bem | utility | semantic
- breakpoints: mobile-first | desktop-first
```

Create folder on first use: `mkdir -p ~/webflow`

## Critical Rules

1. **Always check all breakpoints** — Desktop looks great, mobile is broken. Test tablet/mobile-landscape/mobile-portrait BEFORE showing to client.

2. **Name classes semantically** — `hero-heading` not `heading-23`. You'll thank yourself during handoff.

3. **Set up CMS before content** — Define collections, fields, and relationships first. Migrating content between structures is painful.

4. **Calculate TRUE hosting cost** — Basic Hosting ≠ CMS Hosting ≠ Business Hosting. Forms, CMS items, staging all cost extra.

5. **Test forms with real submissions** — Webflow form notifications fail silently. Verify delivery before launch.

6. **Never trust auto-generated responsive** — Webflow guesses wrong. Manual breakpoint adjustment is mandatory.

7. **Audit before publish** — Missing alt text, 404s, broken links, favicon, OG image, SSL, redirects. Use pre-launch checklist every time.

8. **Export code = cleanup required** — Webflow's exported HTML/CSS is bloated. Budget time for cleanup if moving off platform.

## Scope

This skill covers Webflow design, development, and project management. For general web design principles, see `ui-design`. For landing page conversion strategy, see `landing-pages`.
