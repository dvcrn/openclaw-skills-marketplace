---
name: ios-device-automation
description: "Vision-driven iOS device automation using Midscene CLI. Operates entirely from screenshots — no DOM or accessibility labels required. Can interact with all visible elements on screen regardless of technology stack.\n Control iOS devices with natural language commands via WebDriverAgent.\n \n Triggers: ios, iphone, ipad, ios app, tap on iphone, swipe, mobile app ios,\n ios device, ios testing, iphone automation, ipad automation, ios screen, ios navigate\n\n Powered by Midscene.js (https://midscenejs.com)"
---

# iOS Device Automation

> **CRITICAL RULES — VIOLATIONS WILL BREAK THE WORKFLOW:**
>
> 1. **Never run midscene commands in the background.** Each command must run synchronously so you can read its output (especially screenshots) before deciding the next action. Background execution breaks the screenshot-analyze-act loop.
> 2. **Run only one midscene command at a time.** Wait for the previous command to finish, read the screenshot, then decide the next action. Never chain multiple commands together.
> 3. **Allow enough time for each command to complete.** Midscene commands involve AI inference and screen interaction, which can take longer than typical shell commands. A typical command needs about 1 minute; complex `act` commands may need even longer.
> 4. **Always report task results before finishing.** After completing the automation task, you MUST proactively summarize the results to the user — including key data found, actions completed, screenshots taken, and any relevant findings. Never silently end after the last automation step; the user expects a complete response in a single interaction.

Automate iOS devices using `npx @midscene/ios@1`. Each CLI command maps directly to an MCP tool — you (the AI agent) act as the brain, deciding which actions to take based on screenshots.

## Prerequisites

Midscene requires models with strong visual grounding capabilities. The following environment variables must be configured — either as system environment variables or in a `.env` file in the current working directory (Midscene loads `.env` automatically):

```bash
MIDSCENE_MODEL_API_KEY="your-api-key"
MIDSCENE_MODEL_NAME="model-name"
MIDSCENE_MODEL_BASE_URL="https://..."
MIDSCENE_MODEL_FAMILY="family-identifier"
```

> ⚠️ **Security**: Add `.env` to your `.gitignore` to prevent API keys from being accidentally committed to version control.
> Only use official, trusted provider URLs for `MIDSCENE_MODEL_BASE_URL`.

Example: Gemini (Gemini-3-Flash)

```bash
MIDSCENE_MODEL_API_KEY="your-google-api-key"
MIDSCENE_MODEL_NAME="gemini-3-flash"
MIDSCENE_MODEL_BASE_URL="https://generativelanguage.googleapis.com/v1beta/openai/"
MIDSCENE_MODEL_FAMILY="gemini"
```

Example: Qwen 3.5

```bash
MIDSCENE_MODEL_API_KEY="your-aliyun-api-key"
MIDSCENE_MODEL_NAME="qwen3.5-plus"
MIDSCENE_MODEL_BASE_URL="https://dashscope.aliyuncs.com/compatible-mode/v1"
MIDSCENE_MODEL_FAMILY="qwen3.5"
MIDSCENE_MODEL_REASONING_ENABLED="false"
# If using OpenRouter, set:
# MIDSCENE_MODEL_API_KEY="your-openrouter-api-key"
# MIDSCENE_MODEL_NAME="qwen/qwen3.5-plus"
# MIDSCENE_MODEL_BASE_URL="https://openrouter.ai/api/v1"
```

Example: Doubao Seed 2.0 Lite

```bash
MIDSCENE_MODEL_API_KEY="your-doubao-api-key"
MIDSCENE_MODEL_NAME="doubao-seed-2-0-lite"
MIDSCENE_MODEL_BASE_URL="https://ark.cn-beijing.volces.com/api/v3"
MIDSCENE_MODEL_FAMILY="doubao-seed"
```

Commonly used models: Doubao Seed 2.0 Lite, Qwen 3.5, Zhipu GLM-4.6V, Gemini-3-Pro, Gemini-3-Flash.

If the model is not configured, ask the user to set it up. See [Model Configuration](https://midscenejs.com/model-common-config) for supported providers.

## Commands

### Connect to Device

```bash
npx @midscene/ios@1 connect
```

### Take Screenshot

```bash
npx @midscene/ios@1 take_screenshot
```

After taking a screenshot, read the saved image file to understand the current screen state before deciding the next action.

### Perform Action

Use `act` to interact with the device and get the result. It autonomously handles all UI interactions internally — tapping, typing, scrolling, swiping, waiting, and navigating — so you should give it complex, high-level tasks as a whole rather than breaking them into small steps. Describe **what you want to do and the desired effect** in natural language:

```bash
# specific instructions
npx @midscene/ios@1 act --prompt "type hello world in the search field and press Enter"
npx @midscene/ios@1 act --prompt "tap Delete, then confirm in the alert dialog"

# or target-driven instructions
npx @midscene/ios@1 act --prompt "open Settings and navigate to Wi-Fi, tell me the connected network name"
```

### Disconnect

```bash
npx @midscene/ios@1 disconnect
```

## Workflow Pattern

Since CLI commands are stateless between invocations, follow this pattern:

1. **Connect** to establish a session
2. **Launch the target app and take screenshot** to see the current state, make sure the app is launched and visible on the screen.
3. **Execute action** using `act` to perform the desired action or target-driven instructions.
4. **Disconnect** when done
5. **Report results** — summarize what was accomplished, present key findings and data extracted during the task, and list any generated files (screenshots, logs, etc.) with their paths

## Best Practices

1. **Be specific about UI elements**: Instead of vague descriptions, provide clear, specific details. Say `"the Settings icon in the top-right corner"` instead of `"the icon"`.
2. **Describe locations when possible**: Help target elements by describing their position (e.g., `"the search icon at the top right"`, `"the third item in the list"`).
3. **Never run in background**: Every midscene command must run synchronously — background execution breaks the screenshot-analyze-act loop.
4. **Batch related operations into a single `act` command**: When performing consecutive operations within the same app, combine them into one `act` prompt instead of splitting them into separate commands. For example, "open Settings, tap Wi-Fi, and check the connected network" should be a single `act` call, not three. This reduces round-trips, avoids unnecessary screenshot-analyze cycles, and is significantly faster.
5. **Always report results after completion**: After finishing the automation task, you MUST proactively present the results to the user without waiting for them to ask. This includes: (1) the answer to the user's original question or the outcome of the requested task, (2) key data extracted or observed during execution, (3) screenshots and other generated files with their paths, (4) a brief summary of steps taken. Do NOT silently finish after the last automation command — the user expects complete results in a single interaction.

**Example — Alert dialog interaction:**

```bash
npx @midscene/ios@1 act --prompt "tap the Delete button and confirm in the alert dialog"
npx @midscene/ios@1 take_screenshot
```

**Example — Form interaction:**

```bash
npx @midscene/ios@1 act --prompt "fill in the username field with 'testuser' and the password field with 'pass123', then tap the Login button"
npx @midscene/ios@1 take_screenshot
```

## Troubleshooting

### WebDriverAgent Not Running
**Symptom:** Connection refused or timeout errors.
**Solution:**
- Ensure WebDriverAgent is installed and running on the device.
- See https://midscenejs.com/zh/usage-ios.html for setup instructions.

### Device Not Found
**Symptom:** No device detected or connection errors.
**Solution:**
- Ensure the device is connected via USB and trusted.

### API Key Issues
**Symptom:** Authentication or model errors.
**Solution:**
- Check `.env` file contains `MIDSCENE_MODEL_API_KEY=<your-key>`.
- See https://midscenejs.com/zh/model-common-config.html for details.