---
name: discord-interactive
description: "Create Discord Components v2 interactive messages with buttons, select menus, and containers. Use when you need user confirmations, selections, or action triggers in Discord."
homepage: https://github.com/openclaw/openclaw
---

# Discord Interactive Components

Use Discord Components v2 to create interactive messages with buttons and select menus for asynchronous user interactions.

## When to Use

- ✅ **Confirmations**: "Execute cleanup?" [Yes] [No]
- 📋 **Selections**: Choose agent, priority, or task type
- 🔄 **Actions**: Quick status updates or task triggers
- 📊 **Feedback**: Voting or rating interfaces

## Quick Start

```python
message(
    action="send",
    channel="discord",
    target="channel:CHANNEL_ID",
    components={
        "type": "container",
        "accent_color": 0x3498db,
        "components": [
            {"type": "text_display", "content": "**Confirm action?**"},
            {"type": "action_row", "components": [
                {"type": "button", "custom_id": "yes", "label": "✅ Yes", "style": "success"},
                {"type": "button", "custom_id": "no", "label": "❌ No", "style": "secondary"}
            ]}
        ]
    }
)
```

## Component Types

| Component | Use For | See |
|-----------|---------|-----|
| `button` | Single actions | [references/components.md](references/components.md) |
| `string_select` | Multiple options | [references/components.md](references/components.md) |
| `container` | Layout + styling | [references/components.md](references/components.md) |

## Handling Interactions

When user clicks, check `message.interaction.custom_id`:

```python
if message.get("interaction", {}).get("custom_id") == "yes":
    # Execute confirmed action
    pass
```

See [references/handling.md](references/handling.md) for full callback examples.

## Important Notes

- ❌ Don't combine `components` with `embeds` (Discord rejects)
- ✅ Use `custom_id` to identify button clicks
- ⏰ Users may click minutes later - design for async
- 🎨 Use `accent_color` (hex) for visual distinction

## Examples

See [references/examples.md](references/examples.md) for complete use cases:
- Task confirmation
- Agent selection
- Status update cards
