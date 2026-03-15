---
name: pdf-generation
description: "PDF Generation"
---

# PDF Generation Skill

**Purpose:** Generate professional PDFs from HTML/CSS without whitespace gaps or layout issues.

## The Problem

When generating PDFs from HTML, `page-break-inside: avoid` causes **orphan whitespace** — content that can't fit on the current page gets pushed entirely to the next page, leaving huge gaps.

## The Solution

### 1. Use Flow-Based Layout (NOT Fixed Page Containers)

**❌ WRONG:**
```html
<div class="page" style="min-height: 297mm;">
  <!-- Content -->
</div>
```

**✅ RIGHT:**
```html
<body>
  <!-- Content flows naturally -->
</body>
```

Use `@page` CSS rules instead of fixed page containers:
```css
@page {
    size: A4;
    margin: 18mm 15mm;
}
```

### 2. Protect ONLY Small Elements

Only use `break-inside: avoid` on elements that:
- Are **small** (cards, single rows, short boxes)
- Would look **broken** if split

**✅ Protect:**
- Individual table rows (`tr`)
- Cards (< 100px tall)
- Timeline items
- Step items
- Highlight boxes

**❌ Do NOT Protect:**
- Entire tables
- Large containers
- Entire sections
- Multi-column layouts
- Quote boxes at document end

### 3. Use Modern + Legacy Properties

```css
.small-element {
    break-inside: avoid;        /* Modern spec */
    page-break-inside: avoid;   /* Legacy support */
}
```

### 4. Keep Headers With Content

```css
h2, h3, h4, .section-header {
    break-after: avoid;
    page-break-after: avoid;
}
```

### 5. Prevent Orphan Lines

```css
body {
    orphans: 3;  /* Min lines at bottom of page */
    widows: 3;   /* Min lines at top of page */
}
```

### 6. Allow Tables to Break (But Keep Rows Together)

```css
table {
    /* NO break-inside: avoid */
}

tr {
    break-inside: avoid;
    page-break-inside: avoid;
}
```

## Template

```css
@page {
    size: A4;
    margin: 18mm 15mm;
}

body {
    font-size: 10pt;
    line-height: 1.5;
    orphans: 3;
    widows: 3;
}

/* Headers stay with content */
h2, h3, h4 {
    break-after: avoid;
    page-break-after: avoid;
}

/* Small elements don't break */
.card, .highlight-box, .step, .timeline-item {
    break-inside: avoid;
    page-break-inside: avoid;
}

/* Table rows stay together, table can break */
tr {
    break-inside: avoid;
    page-break-inside: avoid;
}

/* Large containers flow naturally */
table, .section, .two-col {
    /* NO break-inside: avoid */
}

@media print {
    body { 
        -webkit-print-color-adjust: exact; 
        print-color-adjust: exact; 
    }
}
```

## Tools

| Tool | Use Case | Install |
|------|----------|---------|
| **WeasyPrint** | HTML/CSS → PDF (best CSS support) | `brew install weasyprint` or `pip install weasyprint` |
| **Pandoc** | Markdown → PDF via LaTeX | `brew install pandoc` |
| **wkhtmltopdf** | Complex layouts | Download from wkhtmltopdf.org |
| **Puppeteer** | JS-rendered content | `npm install puppeteer` |

### WeasyPrint Command
```bash
weasyprint input.html output.pdf
```

## Pre-Flight Checklist

Before sending ANY PDF:

- [ ] Open in PDF viewer, scroll through ALL pages
- [ ] Check for large whitespace gaps between content
- [ ] Ensure no single-line orphans at page tops
- [ ] Verify tables don't have awkward mid-row breaks
- [ ] Confirm headers are followed by content (not at page bottom alone)

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| `page-break-inside: avoid` on large containers | Remove it, let content flow |
| Fixed-height page divs | Use `@page` rules instead |
| Quote box at document end with break protection | Remove break protection |
| Entire table protected from breaking | Only protect `tr`, not `table` |
| No `orphans`/`widows` set | Add `orphans: 3; widows: 3;` |

## Resources

- WeasyPrint docs: https://doc.courtbouillon.org/weasyprint/
- CSS Paged Media: https://www.w3.org/TR/css-page-3/
- Print CSS Guide: https://www.smashingmagazine.com/2018/05/print-stylesheets-in-2018/

---

*Skill created by Bartok — March 6, 2026*
