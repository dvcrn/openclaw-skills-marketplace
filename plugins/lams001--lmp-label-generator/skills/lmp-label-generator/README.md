# LMP Label Generator

Generate professional product labels from natural language descriptions and push them directly to your [LabelMake Pro](https://labelmakepro.com) designer — powered by your own AI tokens.

## Installation

**Via ClawHub CLI (recommended):**

```bash
# Install ClawHub CLI if you haven't
npm i -g clawhub

# Install this skill
clawhub install lmp-label-generator
```

Then start a new OpenClaw session — the skill is ready to use.

**Manual install:**

```bash
# Copy the skill folder to your OpenClaw workspace
cp -r lmp-label-generator ~/.openclaw/workspace/skills/
```

Restart OpenClaw to pick up the new skill.

## What It Does

Describe a label in plain language. The skill generates a complete LMP-format label design with:

- Proper layout zones (header, content, barcode, footer)
- Typography hierarchy (brand name, product name, specs, caption)
- Color schemes matched to product category (food = green, industrial = blue, etc.)
- Barcodes (EAN13, QR Code, Code128, etc.)
- Exact mm-level positioning

**Every generation always does both:**

| Step | When | What happens |
|------|------|--------------|
| **① Local file** (always) | Every time | Saves `.lmp` file to `~/Downloads/` — works even without an account |
| **② Cloud push** (if apiKey set) | `apiKey` is configured | Also calls your SaaS API and returns a direct designer link |

No API key? You still get the LMP file every time. Want the one-click link? Add your API key.

## How to Use

### Quick Start (Mode A — No setup required)

Just ask:

> "生成一个 60×40mm 食品标签，品牌名：皮虾零食，产品：原味鸡爪，净重 200g，EAN13 条码"

The skill generates the LMP JSON and saves it locally.

### Cloud Push Mode (Mode B — Recommended)

**Step 1**: Get your API key from [LabelMake Pro → Account Settings → OpenClaw Integration](https://labelmakepro.com/admin/user/profile)

**Step 2**: Configure this skill:

```yaml
config:
  apiEndpoint: "https://labelmakepro.com/api/v1/oc/import"
  apiKey: "oc_sk_your_key_here"
  frontendUrl: "https://labelmakepro.com"
```

**Step 3**: Ask the same way. After generation, the skill calls the API and returns a direct link to open the label in the designer.

## Example Prompts

```
Generate a 60×40mm food label for "Spicy Chicken Feet" by brand "PiXia Snacks", green theme, EAN13 barcode 6901234567890

创建一个快递标签，80×50mm，包含收件人姓名、地址、电话、QR码

Design a price tag 40×25mm, product: Wireless Earphones, price: ¥299, black luxury theme
```

## Label Format (LMP)

This skill produces labels in the open [LMP (Label Management Project) format](https://github.com/lams001/lmp-protocol) — a JSON standard for label design interchange.

Supported element types:

| Type | Description |
|------|-------------|
| `text` | Text with full typography control |
| `rectangle` | Filled color blocks, backgrounds |
| `barcode` | EAN13, EAN8, CODE128, CODE39, ITF14 |
| `qrcode` | QR codes with error correction |
| `line` | Divider lines |
| `ellipse` | Circles and ovals |
| `table` | Structured data tables |

## Permissions Used

| Permission | Why |
|------------|-----|
| `filesystem` | Save generated LMP file locally (Mode A fallback) |
| `http` | POST to **your own** LabelMake Pro API endpoint (Mode B). No data is sent to any third party. |

> **Privacy**: The skill calls only the API endpoint you configure. Your label content never leaves your configured endpoint.

## 🔐 API Key Security

By default, `config.apiKey` is stored as plaintext in `openclaw.json`. For better security, use OpenClaw's **SecretRef** system to store the key in an environment variable:

```json
"config": {
  "apiKey": { "source": "env", "provider": "default", "id": "LABELMAKER_OC_API_KEY" }
}
```

Set the environment variable:
```bash
export LABELMAKER_OC_API_KEY="oc_sk_xxxxx"   # Linux/macOS
$env:LABELMAKER_OC_API_KEY = "oc_sk_xxxxx"   # Windows PowerShell
```

Run `openclaw secrets audit --check` to detect any plaintext credentials in your config.

> **Note**: `oc_sk_` keys have limited scope (label import only) and can be revoked instantly from your LabelMake Pro account settings.

## Requirements

- For **Mode B**: A [LabelMake Pro](https://labelmakepro.com) account (free tier available)
- For **Mode A**: No requirements — works offline

## Troubleshooting

**401 error**: API key is invalid or revoked. Generate a new key in LabelMake Pro → Account Settings → OpenClaw Integration.

**400 error**: LMP data validation failed. The skill will retry with a corrected structure automatically.

**Label opens but elements look wrong**: Ensure `canvas.unit` is `"mm"` (not `"units"`). This skill v1.3.0+ always generates the correct field name.

**Mode B not working, no API key set**: Check that `config.apiKey` is filled in the skill configuration, not left as empty string.

## Changelog

### v1.4.0
- Always output local LMP file regardless of API key configuration
- When API key is set, additionally return a direct designer link
- Clearer output format with actionable onboarding for users without API key

### v1.3.0
- Fixed `canvas.unit` field name (was incorrectly `units`)
- Complete API request body example with `lmpData` wrapper
- Fixed `stroke: "none"` → `stroke: ""` for correct rendering
- Cloud push mode: elements stored as LMP format in metadata for proper conversion

### v1.2.0
- Added cloud push mode (Mode B) with SaaS API integration
- API key management via LabelMake Pro account settings
- Automatic fallback to local file on API error

### v1.0.0
- Initial release with local file mode

## License

MIT-0 — free to use, modify, and distribute. No attribution required.

## Links

- [LMP Protocol (Open Source)](https://github.com/lams001/lmp-protocol)
- [LabelMake Pro](https://labelmakepro.com)
- [Report Issues](https://github.com/lams001/lmp-protocol/issues)
