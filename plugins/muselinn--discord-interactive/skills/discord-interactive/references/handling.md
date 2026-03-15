# Handling Component Interactions

When users click buttons or select options, Discord sends interaction events. Here's how to handle them.

## Receiving Interactions

Interaction appears in incoming message:

```python
{
  "interaction": {
    "type": "button",           # or "select_menu"
    "custom_id": "approve",     # the ID you set
    "user": {
      "id": "1106438955500584971",
      "username": "Linn"
    },
    "message": {
      "id": "1234567890",
      "channel_id": "1477679555148779662"
    }
  }
}
```

## Basic Handler Pattern

```python
def handle_interaction(message):
    interaction = message.get("interaction")
    if not interaction:
        return  # Not an interaction
    
    custom_id = interaction.get("custom_id")
    user = interaction.get("user", {}).get("username")
    
    if custom_id == "approve":
        # Execute approval logic
        execute_task()
        # Update message to show completed
        update_message(interaction["message"], "✅ Approved by " + user)
        
    elif custom_id == "reject":
        # Handle rejection
        cancel_task()
        update_message(interaction["message"], "❌ Rejected by " + user)
        
    elif custom_id == "later":
        # Schedule reminder
        schedule_reminder()
        update_message(interaction["message"], "⏰ Snoozed by " + user)
```

## Updating the Message

After handling, update the component to show result:

```python
def update_message(original_msg, status_text):
    message(
        action="edit",
        channel="discord",
        channelId=original_msg["channel_id"],
        messageId=original_msg["id"],
        components={
            "type": "container",
            "accent_color": 0x2ecc71,  # Green for success
            "components": [
                {"type": "text_display", "content": status_text}
            ]
        }
    )
```

## Select Menu Handling

```python
if interaction["type"] == "select_menu":
    selected_value = interaction.get("values", [])[0]  # First selection
    
    if interaction["custom_id"] == "select_agent":
        if selected_value == "engineer":
            assign_to_engineer()
        elif selected_value == "researcher":
            assign_to_researcher()
```

## Timeout Handling

Users may not click immediately. Design for delays:

```python
# Store pending confirmations with timestamp
pending_confirmations = {
    "msg_id_123": {
        "created_at": time.time(),
        "expires_at": time.time() + 3600,  # 1 hour timeout
        "action": "cleanup"
    }
}

# Check if expired when handling
if time.time() > pending["expires_at"]:
    # Show expired message
    update_message(msg, "⏰ This request has expired")
    return
```

## Acknowledgment

Discord requires acknowledging the interaction quickly (within 3 seconds). OpenClaw handles this automatically, but for long operations:

```python
# For operations > 3 seconds, defer first
def handle_with_defer(interaction):
    # Immediate acknowledgment
    message(
        action="edit",  # Defer by editing
        channel="discord",
        channelId=interaction["message"]["channel_id"],
        messageId=interaction["message"]["id"],
        components={
            "type": "container",
            "components": [
                {"type": "text_display", "content": "🔄 Processing..."}
            ]
        }
    )
    
    # Then do long operation
    result = long_operation()
    
    # Finally update with result
    update_message(interaction["message"], f"✅ Done: {result}")
```

## Security Considerations

1. **Verify user**: Check `interaction["user"]["id"]` matches expected user
2. **Rate limiting**: Prevent spam by tracking clicks per user
3. **Idempotency**: Ensure repeated clicks don't cause duplicate actions

```python
# Verify only authorized user can click
AUTHORIZED_USERS = ["1106438955500584971"]

if interaction["user"]["id"] not in AUTHORIZED_USERS:
    # Silently ignore or show error
    return
```
