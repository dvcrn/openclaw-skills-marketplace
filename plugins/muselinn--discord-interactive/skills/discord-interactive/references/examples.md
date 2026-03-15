# Component Examples

Complete, ready-to-use examples for common scenarios.

## 1. Simple Yes/No Confirmation

```python
message(
    action="send",
    channel="discord",
    target="channel:1477679555148779662",
    components={
        "type": "container",
        "accent_color": 0x3498db,
        "components": [
            {"type": "text_display", "content": "🧹 **Cleanup Request**\n\nDelete 5 temporary files (120MB)?"},
            {"type": "action_row", "components": [
                {"type": "button", "custom_id": "cleanup_yes", "label": "✅ Yes, clean up", "style": "success"},
                {"type": "button", "custom_id": "cleanup_no", "label": "❌ No, keep them", "style": "secondary"}
            ]}
        ]
    }
)

# Handler
if interaction.get("custom_id") == "cleanup_yes":
    # Delete files
    exec("rm -rf /tmp/old-*")
    update_message("✅ Cleaned up 5 files")
elif interaction.get("custom_id") == "cleanup_no":
    update_message("❌ Cleanup cancelled")
```

## 2. Agent Selection

```python
message(
    action="send",
    channel="discord",
    target="channel:1477679555148779662",
    components={
        "type": "container",
        "accent_color": 0x667eea,
        "components": [
            {"type": "text_display", "content": "🎯 **Assign Task**\n\nSelect the best agent for this task:"},
            {"type": "action_row", "components": [{
                "type": "string_select",
                "custom_id": "assign_agent",
                "placeholder": "Choose an agent...",
                "options": [
                    {
                        "label": "🛠️ Engineer",
                        "value": "engineer",
                        "description": "Python, algorithms, code review",
                        "emoji": {"name": "🛠️"}
                    },
                    {
                        "label": "🔬 Researcher",
                        "value": "researcher",
                        "description": "Literature, theory, analysis",
                        "emoji": {"name": "🔬"}
                    },
                    {
                        "label": "📝 Writer",
                        "value": "writer",
                        "description": "Documentation, LaTeX, reports",
                        "emoji": {"name": "📝"}
                    }
                ]
            }]}
        ]
    }
)

# Handler
agent = interaction.get("values", [])[0]
if agent == "engineer":
    assign_to_engineer()
elif agent == "researcher":
    assign_to_researcher()
elif agent == "writer":
    assign_to_writer()
```

## 3. Task Status Card

```python
message(
    action="send",
    channel="discord",
    target="channel:THREAD_ID",
    components={
        "type": "container",
        "accent_color": 0xf1c40f,  # Yellow = in progress
        "components": [
            {
                "type": "section",
                "components": [
                    {"type": "text_display", "content": "🎯 **TASK_001: Implement Filter**"},
                    {"type": "text_display", "content": "Status: 🔵 In Progress\nAssigned: Engineer\nETA: 2 hours"}
                ],
                "accessory": {"type": "thumbnail", "url": "https://cdn.../task-icon.png"}
            },
            {"type": "separator"},
            {"type": "action_row", "components": [
                {"type": "button", "custom_id": "task_done", "label": "✅ Complete", "style": "success"},
                {"type": "button", "custom_id": "task_block", "label": "🚧 Blocked", "style": "danger"},
                {"type": "button", "custom_id": "task_update", "label": "📝 Update", "style": "primary"}
            ]}
        ]
    }
)
```

## 4. Priority Selection

```python
message(
    action="send",
    channel="discord",
    target="channel:1477679555148779662",
    components={
        "type": "container",
        "accent_color": 0xe74c3c,
        "components": [
            {"type": "text_display", "content": "⚡ **Set Priority**\n\nHow urgent is this task?"},
            {"type": "action_row", "components": [
                {"type": "button", "custom_id": "prio_high", "label": "🔴 High", "style": "danger"},
                {"type": "button", "custom_id": "prio_medium", "label": "🟡 Medium", "style": "primary"},
                {"type": "button", "custom_id": "prio_low", "label": "🟢 Low", "style": "secondary"}
            ]}
        ]
    }
)
```

## 5. Multi-Step Workflow

```python
# Step 1: Request confirmation
msg = message(
    action="send",
    channel="discord",
    target="channel:1477679555148779662",
    components={
        "type": "container",
        "accent_color": 0x667eea,
        "components": [
            {"type": "text_display", "content": "📋 **New Request**\n\nRun full system analysis?"},
            {"type": "action_row", "components": [
                {"type": "button", "custom_id": "analysis_start", "label": "▶️ Start Analysis", "style": "success"},
                {"type": "button", "custom_id": "analysis_cancel", "label": "Cancel", "style": "secondary"}
            ]}
        ]
    }
)

# Step 2: When user clicks "Start"
if interaction.get("custom_id") == "analysis_start":
    # Update to show progress
    message(
        action="edit",
        channel="discord",
        channelId=msg["channel_id"],
        messageId=msg["message_id"],
        components={
            "type": "container",
            "accent_color": 0xf1c40f,
            "components": [
                {"type": "text_display", "content": "🔄 **Analysis Running...**\n\nThis may take a few minutes."}
            ]
        }
    )
    
    # Run analysis
    result = run_analysis()
    
    # Step 3: Show results with action buttons
    message(
        action="edit",
        channel="discord",
        channelId=msg["channel_id"],
        messageId=msg["message_id"],
        components={
            "type": "container",
            "accent_color": 0x2ecc71,
            "components": [
                {"type": "text_display", "content": f"✅ **Analysis Complete**\n\n{result.summary}"},
                {"type": "separator"},
                {"type": "action_row", "components": [
                    {"type": "button", "custom_id": "view_report", "label": "📄 View Report", "style": "primary"},
                    {"type": "button", "custom_id": "download_csv", "label": "📥 Download CSV", "style": "secondary"}
                ]}
            ]
        }
    )
```
