# Discord Components v2 Reference

Complete reference for all component types and their properties.

## Container

Base wrapper for components. Sets accent color and groups content.

```json
{
  "type": "container",
  "accent_color": 0x3498db,
  "components": [...]
}
```

| Property | Type | Description |
|----------|------|-------------|
| `accent_color` | integer (hex) | Left border color (e.g., `0x3498db` = blue) |
| `components` | array | Child components |

**Color Examples:**
- `0x2ecc71` - Green (success)
- `0xe74c3c` - Red (error/danger)
- `0xf1c40f` - Yellow (warning)
- `0x3498db` - Blue (info)
- `0x9b59b6` - Purple

## Text Display

Markdown text block.

```json
{
  "type": "text_display",
  "content": "**Bold** and _italic_ text"
}
```

Supports Discord markdown: `**bold**`, `_italic_`, `\`code\``, etc.

## Separator

Horizontal divider.

```json
{"type": "separator"}
```

## Button

Clickable action button.

```json
{
  "type": "button",
  "custom_id": "unique_id",
  "label": "Button text",
  "style": "primary"
}
```

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `custom_id` | string | Yes | Unique identifier for callback |
| `label` | string | Yes | Button text (max 80 chars) |
| `style` | string | Yes | Visual style |
| `disabled` | boolean | No | Grayed out if true |
| `emoji` | object | No | `{name: "✅"}` |

**Styles:**
| Style | Color | Use Case |
|-------|-------|----------|
| `primary` | Blue | Main action |
| `secondary` | Gray | Alternative action |
| `success` | Green | Confirm/complete |
| `danger` | Red | Delete/cancel |
| `link` | Blue | External URL (use `url` instead of `custom_id`) |

**Link Button Example:**
```json
{
  "type": "button",
  "label": "Open Docs",
  "style": "link",
  "url": "https://docs.openclaw.ai"
}
```

## String Select

Dropdown menu for selecting one option.

```json
{
  "type": "string_select",
  "custom_id": "select_agent",
  "placeholder": "Choose...",
  "options": [
    {
      "label": "Engineer",
      "value": "engineer",
      "description": "Code development",
      "emoji": {"name": "🛠️"}
    }
  ]
}
```

| Property | Type | Description |
|----------|------|-------------|
| `placeholder` | string | Hint text when nothing selected |
| `options` | array | Selection choices (max 25) |
| `min_values` | integer | Min selections (default 1) |
| `max_values` | integer | Max selections (default 1) |

**Option Properties:**
| Property | Required | Description |
|----------|----------|-------------|
| `label` | Yes | Display text (max 100 chars) |
| `value` | Yes | Callback value (max 100 chars) |
| `description` | No | Secondary text (max 100 chars) |
| `emoji` | No | `{name: "emoji"}` |
| `default` | No | Pre-selected if true |

## Action Row

Container for interactive components (buttons, selects).

```json
{
  "type": "action_row",
  "components": [
    {"type": "button", ...},
    {"type": "button", ...}
  ]
}
```

**Limits:**
- Max 5 buttons per action row
- Max 1 select menu per action row
- Max 5 action rows per message

## Section

Grouped content with optional thumbnail accessory.

```json
{
  "type": "section",
  "components": [
    {"type": "text_display", "content": "Title"},
    {"type": "text_display", "content": "Description"}
  ],
  "accessory": {
    "type": "thumbnail",
    "url": "https://example.com/image.png"
  }
}
```

## Full Message Example

```json
{
  "type": "container",
  "accent_color": 0x667eea,
  "components": [
    {
      "type": "section",
      "components": [
        {"type": "text_display", "content": "# Task Request"},
        {"type": "text_display", "content": "Review and approve the proposed task"}
      ],
      "accessory": {"type": "thumbnail", "url": "https://cdn.../task.png"}
    },
    {"type": "separator"},
    {
      "type": "action_row",
      "components": [
        {"type": "button", "custom_id": "approve", "label": "✅ Approve", "style": "success"},
        {"type": "button", "custom_id": "reject", "label": "❌ Reject", "style": "danger"},
        {"type": "button", "custom_id": "later", "label": "⏰ Later", "style": "secondary"}
      ]
    }
  ]
}
```
