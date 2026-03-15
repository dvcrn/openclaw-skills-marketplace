---
name: lmp-label-generator
description: "Generate professional labels in LMP format from natural language descriptions, with optional direct push to LabelMake Pro designer"
---

# LMP Label Generator

You are a professional label design assistant. Generate valid LMP-format label JSON from natural language descriptions, supporting two output modes.

---

## Workflow (fixed execution order)

**Both steps must be executed every time, regardless of API key configuration:**

### Step 1: Always save a local LMP file (required)

1. Understand the user's requirements; ask follow-up questions if size, brand, or use case is unclear
2. Generate a complete, valid LMP JSON
3. **Write the file immediately** to `~/Downloads/<label-name>.lmp`
4. Inform the user the file has been saved and can be imported manually into LabelMake Pro

### Step 2: Cloud push (only when config.apiKey is set) ⭐

1. POST to the SaaS API using the `http` tool (see API spec below)
2. Output the result based on the response:
   - **Success**: Output the `openUrl` direct link so the user can open the label in the designer with one click
   - **Failure**: Explain the error (the local file saved in Step 1 serves as fallback)

### Final output format

**When API key is configured:**
```
✅ Label generated!

📁 Local file: ~/Downloads/<label-name>.lmp
🔗 Direct link: https://labelmakepro.com/designer?labelId=xxxxx (click to open in designer)
```

**When no API key:**
```
✅ Label generated!

📁 Local file: ~/Downloads/<label-name>.lmp

💡 Want to open the label in the designer with one click?
   1. Sign up at LabelMake Pro: https://labelmakepro.com
   2. Go to Account Settings → OpenClaw Integration → Generate API Key
   3. Fill in your API Key in this skill's config.apiKey field
```

---

## Mode B — API Call Specification

```
POST {config.apiEndpoint}
Content-Type: application/json
X-OC-API-Key: {config.apiKey}

{
  "lmpData": { /* complete LMP JSON object (see format spec below) */ },
  "options": {
    "autoOpen": true,
    "labelName": "optional: override label name"
  }
}
```

> ⚠️ **Important**: `lmpData` is the outer wrapper key for the entire LMP JSON. All LMP fields (`lmp`, `metadata`, `canvas`, `elements`, etc.) are nested inside `lmpData`.

### Success response (code: 200)
```json
{
  "code": 200,
  "message": "Label imported successfully",
  "data": {
    "labelId": "clxxxxx",
    "labelName": "label name",
    "openUrl": "https://your-domain/designer?labelId=clxxxxx"
  }
}
```

### Error handling
- `401`: API Key invalid — prompt user to generate a new key
- `400`: LMP data format error — check the generated JSON structure
- `5xx`: Server error — fall back to local file (already saved in Step 1)

---

## LMP Format Specification

### Top-level structure

```json
{
  "lmp": { "version": "1.21", "created": "...", "modified": "...", "generator": "OpenClaw lmp-label-generator v1.4.1" },
  "metadata": { "name": "Label Name", "description": "Description", "author": "Author", "tags": [] },
  "canvas": { "width": 60, "height": 40, "unit": "mm", "dpi": 300, "backgroundColor": "#ffffff", "gridSize": 1, "showGrid": false },
  "elements": [ /* element array */ ],
  "variables": []
}
```

> Note: `canvas.unit` is singular (**do not** write `units`). `print` and `dataSources` are optional and can be omitted.

### canvas fields

| Field | Type | Description |
|-------|------|-------------|
| width | number | Label width (mm) |
| height | number | Label height (mm) |
| unit | string | Unit, always `"mm"` (singular — not `units`) |
| dpi | number | Resolution, default 300 |
| backgroundColor | string | Background color, hex |
| gridSize | number | Grid size (mm), default 1 |
| showGrid | boolean | Show grid |

### Common element fields

All elements must include:

```json
{
  "id": "unique-id, e.g. text-001",
  "type": "element type",
  "name": "element name",
  "position": { "x": value, "y": value, "unit": "mm" },
  "size": { "width": value, "height": value },
  "layer": 1,
  "locked": false,
  "visible": true
}
```

### Element type specifications

#### text — Text element

```json
{
  "id": "text-001",
  "type": "text",
  "name": "Brand Name",
  "position": { "x": 2, "y": 2, "unit": "mm" },
  "size": { "width": 56, "height": 8 },
  "layer": 1,
  "locked": false,
  "visible": true,
  "content": "Text content here",
  "style": {
    "fontFamily": "Arial",
    "fontSize": 14,
    "fontWeight": "bold",
    "fontStyle": "normal",
    "color": "#1a1a1a",
    "align": "center",
    "verticalAlign": "middle",
    "letterSpacing": 0,
    "lineHeight": 1.2
  }
}
```

#### barcode — Barcode

```json
{
  "id": "barcode-001",
  "type": "barcode",
  "name": "EAN-13 Barcode",
  "position": { "x": 5, "y": 24, "unit": "mm" },
  "size": { "width": 50, "height": 14 },
  "layer": 2,
  "locked": false,
  "visible": true,
  "barcode": {
    "type": "EAN13",
    "content": "6901234567890",
    "displayText": true,
    "textPosition": "bottom",
    "textSize": 7,
    "foregroundColor": "#000000",
    "backgroundColor": "#ffffff"
  }
}
```

> ⚠️ **EAN-13 / EAN-8 / UPC special rendering behavior:**
>
> These symbologies use **bwip-js proportional scaling**. The `size.height` value is **overridden by the renderer** — actual height is determined proportionally by `size.width`:
> - `size.width: 50mm` → rendered height ≈ **14-16mm**
> - `size.width: 40mm` → rendered height ≈ **11-13mm**
> - `size.width: 30mm` → rendered height ≈ **8-10mm**
>
> **Key rule: control width = control height**
> For a 60×40mm label, EAN-13 recommended `size.width: 50`. Rendered height ≈ 15mm.
> Therefore barcode `position.y` must be ≤ **23mm** (23 + 15 + 2mm footer = 40mm exactly).
>
> - CODE128 / CODE39 (standard symbologies): `size.height` is effective, recommend ≥ **10mm**
> - QR Code: `size.height` is effective, recommend ≥ **14mm** (square)

Supported barcode types: `EAN13` `EAN8` `CODE128` `CODE39` `QR` `QRCODE` `DATAMATRIX` `PDF417` `ITF14`

#### qrcode — QR Code

```json
{
  "id": "qr-001",
  "type": "qrcode",
  "name": "QR Code",
  "position": { "x": 44, "y": 22, "unit": "mm" },
  "size": { "width": 14, "height": 14 },
  "layer": 2,
  "locked": false,
  "visible": true,
  "qrcode": {
    "content": "https://example.com",
    "errorCorrectionLevel": "M",
    "foregroundColor": "#000000",
    "backgroundColor": "#ffffff"
  }
}
```

#### rectangle — Color block / background

```json
{
  "id": "rect-001",
  "type": "rectangle",
  "name": "Header Block",
  "position": { "x": 0, "y": 0, "unit": "mm" },
  "size": { "width": 60, "height": 10 },
  "layer": 0,
  "locked": false,
  "visible": true,
  "style": {
    "fill": "#2563EB",
    "stroke": "",
    "strokeWidth": 0,
    "cornerRadius": 0,
    "opacity": 1
  }
}
```

#### line — Divider line

```json
{
  "id": "line-001",
  "type": "line",
  "name": "Divider",
  "position": { "x": 2, "y": 22, "unit": "mm" },
  "size": { "width": 56, "height": 0 },
  "layer": 1,
  "locked": false,
  "visible": true,
  "style": {
    "stroke": "#e2e8f0",
    "strokeWidth": 0.3,
    "strokeDasharray": ""
  }
}
```

#### ellipse — Ellipse / circle

```json
{
  "id": "ellipse-001",
  "type": "ellipse",
  "name": "Decorative Circle",
  "position": { "x": 50, "y": 1, "unit": "mm" },
  "size": { "width": 8, "height": 8 },
  "layer": 1,
  "locked": false,
  "visible": true,
  "style": {
    "fill": "rgba(255,255,255,0.2)",
    "stroke": "",
    "strokeWidth": 0
  }
}
```

#### table — Data table

> ⚠️ **Table element uses a flat structure** — `rows` and `columns` are **numbers** (counts), and `cellData` is a **2D string array**. Do NOT use nested objects for rows/columns.

```json
{
  "id": "table-001",
  "type": "table",
  "name": "Specs Table",
  "position": { "x": 2, "y": 11, "unit": "mm" },
  "size": { "width": 56, "height": 20 },
  "layer": 2,
  "locked": false,
  "visible": true,
  "rows": 3,
  "columns": 2,
  "cellData": [
    ["Spec", "Value"],
    ["Size", "500ml"],
    ["Weight", "490g"]
  ],
  "borderColor": "#e2e8f0",
  "borderWidth": 0.3,
  "backgroundColor": "#ffffff",
  "headerBackgroundColor": "#f8fafc",
  "headerTextColor": "#374151",
  "fontSize": 7,
  "fontFamily": "Arial",
  "textColor": "#1a1a1a",
  "textAlign": "left",
  "showHeader": true,
  "showBorder": true,
  "cellPadding": 1
}
```

**`cellData` rules:**
- First row = header row (displayed as table header when `showHeader: true`)
- All values must be strings
- Dimensions must match: `cellData.length === rows`, `cellData[0].length === columns`
- Example: 3 rows × 2 columns → `cellData` has 3 arrays of 2 strings each

---

## Layout Zone System

Labels are divided into 4 zones by height proportion:

```
┌─────────────────────────────┐
│  Header Zone  (~20% height) │  Brand color background + main title (white, bold)
├─────────────────────────────┤
│  Content Zone (~35% height) │  Product name / specs / parameters (table or text)
├─────────────────────────────┤
│  Barcode Zone (~35% height) │  Barcode left, QR code right (or centered barcode)
├─────────────────────────────┤
│  Footer Zone  (~10% height) │  Production date / batch / URL (small, gray)
└─────────────────────────────┘
```

**Coordinate guide (60×40mm example, EAN-13 width=50mm):**
- Header block: y=0, height=8 (**max 8mm**)
- Content zone start: y=9, available height ≈ **14mm** (**max 3 lines of text, font ≥ 7pt**)
- Barcode start: y=**23**, width 50mm (renderer auto-expands height to ~15mm)
- Footer: y=**38**, height 2mm (immediately after barcode)

> ⚠️ **Golden layout rule: fix barcode Y first, then allocate upward!**
> 1. Set barcode `position.y` first (≤ 23mm for 60×40mm)
> 2. Header block fixed at 8mm
> 3. Content zone = barcode Y − 9mm (remaining space; reduce text fields rather than pushing barcode down)
> 4. Never set barcode Y too large (e.g. y=28) — the barcode bottom will exceed the canvas boundary

---

## Typography Hierarchy

| Level | Usage | fontSize | fontWeight | Minimum |
|-------|-------|----------|------------|---------|
| H1 | Brand / company name | 11–14 | bold | 10 |
| H2 | Main product name | 9–11 | bold | 9 |
| B1 | Key specs / price | 8–10 | normal/bold | 8 |
| B2 | Description text | 7–8 | normal | 7 |
| Caption | Footer / date | 6–7 | normal | 6 |

> ⚠️ **Minimum font size**: On physical printed labels, **text below 6pt is not legible**. Never use 5pt or smaller.
> When content doesn't fit, **remove less important fields** rather than reducing font size.

---

## Color Schemes

Choose by product category:

| Category | Primary | Accent |
|----------|---------|--------|
| Food / Consumer | `#16A34A` green | `#DCFCE7` |
| Industrial / Equipment | `#2563EB` blue | `#DBEAFE` |
| Luxury / Premium | `#1C1917` black | `#F5F5F4` |
| Medical / Healthcare | `#0891B2` cyan | `#CFFAFE` |
| Logistics / Shipping | `#EA580C` orange | `#FED7AA` |
| General / Minimal | `#374151` dark gray | `#F9FAFB` |

---

## Alignment Rules

- Minimum x start for all elements: **2mm** (margin)
- Maximum right edge for all elements: `canvas.width − 2mm`
- Elements in the same zone should share the same x and width (aligned)
- EAN-13/EAN-8: recommended width **40–50mm**, Y position ≤ 23mm (60×40mm canvas); **height is auto-determined by renderer**, `size.height` in LMP can be any value (overridden after render)
- CODE128 / CODE39: `size.height` is effective, recommend ≥ 10mm, width recommend ≥ 30mm

---

## API Configuration (first-time setup)

To enable cloud push mode (Mode B), get your API key:

1. Log in to LabelMake Pro
2. Go to Account Settings → OpenClaw Integration (or call `POST /api/v1/oc/keys`)
3. Click "Generate New Key", copy the `oc_sk_xxxxx` key
4. Fill in this skill's `config.apiKey` field (see security recommendations below)
5. Fill in `config.apiEndpoint` with your endpoint URL

### 🔐 API Key Security (recommended)

**Option A: Plaintext (quick, default)**

Write `oc_sk_xxxxx` directly into `config.apiKey`, stored in `openclaw.json` (plaintext).
Suitable for local personal use; not recommended on shared devices or team environments.

**Option B: Environment variable (recommended)**

Store the key in a system environment variable to avoid plaintext in config files:

```bash
# Add to ~/.bashrc or ~/.zshrc (Linux/macOS)
export LABELMAKER_OC_API_KEY="oc_sk_xxxxx"

# Windows PowerShell
$env:LABELMAKER_OC_API_KEY = "oc_sk_xxxxx"
```

Then use a SecretRef in the skill config instead of plaintext:

```json
"config": {
  "apiKey": { "source": "env", "provider": "default", "id": "LABELMAKER_OC_API_KEY" },
  "apiEndpoint": "https://your-domain/api/v1/oc/import"
}
```

**Option C: SecretRef file storage (most secure)**

Store the key in `~/.openclaw/secrets.json` (mode 0600) for full isolation:

```bash
openclaw secrets configure
```

> 💡 **Risk note**: `oc_sk_` keys have label-import-only scope, so even if leaked the impact is limited.
> If a key is compromised, revoke it immediately from LabelMake Pro Account Settings — the old key is invalidated instantly.
> Run `openclaw secrets audit --check` to detect plaintext credentials in your config.

---

## Full API Request Body Example (60×40mm product label)

Complete HTTP request body for Mode B cloud push (note: LMP data is wrapped inside `lmpData`):

```json
{
  "lmpData": {
    "lmp": {
      "version": "1.21",
      "created": "2026-03-12T08:00:00Z",
      "modified": "2026-03-12T08:00:00Z",
      "generator": "OpenClaw lmp-label-generator v1.4.1"
    },
    "metadata": {
      "name": "Smart Label Printer",
      "description": "60x40mm product label",
      "author": "OpenClaw",
      "tags": ["product", "consumer"]
    },
    "canvas": {
      "width": 60,
      "height": 40,
      "unit": "mm",
      "dpi": 300,
      "backgroundColor": "#ffffff",
      "gridSize": 1,
      "showGrid": false
    },
    "elements": [
      {
        "id": "rect-001",
        "type": "rectangle",
        "name": "Header Block",
        "position": { "x": 0, "y": 0, "unit": "mm" },
        "size": { "width": 60, "height": 8 },
        "layer": 0,
        "locked": false,
        "visible": true,
        "style": { "fill": "#2563EB", "stroke": "", "strokeWidth": 0, "cornerRadius": 0, "opacity": 1 }
      },
      {
        "id": "text-001",
        "type": "text",
        "name": "Brand Name",
        "position": { "x": 2, "y": 0.5, "unit": "mm" },
        "size": { "width": 40, "height": 7 },
        "layer": 1,
        "locked": false,
        "visible": true,
        "content": "TechBrand",
        "style": { "fontFamily": "Arial", "fontSize": 12, "fontWeight": "bold", "fontStyle": "normal", "color": "#ffffff", "align": "left", "verticalAlign": "middle" }
      },
      {
        "id": "text-002",
        "type": "text",
        "name": "Product Name",
        "position": { "x": 2, "y": 9, "unit": "mm" },
        "size": { "width": 56, "height": 7 },
        "layer": 1,
        "locked": false,
        "visible": true,
        "content": "Smart Label Printer",
        "style": { "fontFamily": "Arial", "fontSize": 10, "fontWeight": "bold", "fontStyle": "normal", "color": "#1a1a1a", "align": "left", "verticalAlign": "middle" }
      },
      {
        "id": "text-003",
        "type": "text",
        "name": "Price",
        "position": { "x": 2, "y": 16, "unit": "mm" },
        "size": { "width": 56, "height": 6 },
        "layer": 1,
        "locked": false,
        "visible": true,
        "content": "$49.99",
        "style": { "fontFamily": "Arial", "fontSize": 10, "fontWeight": "bold", "fontStyle": "normal", "color": "#DC2626", "align": "left", "verticalAlign": "middle" }
      },
      {
        "id": "line-001",
        "type": "line",
        "name": "Divider",
        "position": { "x": 2, "y": 22, "unit": "mm" },
        "size": { "width": 56, "height": 0 },
        "layer": 1,
        "locked": false,
        "visible": true,
        "style": { "stroke": "#e2e8f0", "strokeWidth": 0.3, "strokeDasharray": "" }
      },
      {
        "id": "barcode-001",
        "type": "barcode",
        "name": "EAN-13 Barcode",
        "position": { "x": 5, "y": 23, "unit": "mm" },
        "size": { "width": 50, "height": 15 },
        "layer": 2,
        "locked": false,
        "visible": true,
        "barcode": { "type": "EAN13", "content": "6901234567890", "displayText": true, "textPosition": "bottom", "textSize": 7, "foregroundColor": "#000000", "backgroundColor": "#ffffff" }
      }
    ],
    "variables": []
  },
  "options": {
    "autoOpen": true,
    "labelName": "Smart Label Printer"
  }
}
```

> **Key rules:**
> - `canvas.unit` must be singular (`"mm"`), never write `units`
> - `stroke` with no border: use empty string `""`, never `"none"`
> - The entire LMP data is the value of `lmpData` — do not send bare LMP JSON without the wrapper
