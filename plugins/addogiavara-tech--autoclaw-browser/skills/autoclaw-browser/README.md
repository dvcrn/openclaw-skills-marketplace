# AutoClaw Browser Automation Tool

Empower OpenClaw with enhanced web control and bookmark management capabilities.

## Features

| Feature | Description |
|---------|-------------|
| Bookmark Management | Full CRUD support with folder operations |
| CDP Deep Control | Execute JavaScript, element operations, screenshots |
| Automation Scripts | Reusable script templates |
| One-time Authorization | Take control of all tabs, no repeated authorization |
| 🚀 Performance Optimization v6.1.0 | CDP on-demand, DOM cache, recording, workflows |
| 🎬 Operation Recording | Record and replay user actions |
| 📋 Workflow Templates | Pre-built automation templates |

## v6.1.0 New Features

### 1. Operation Recording & Playback

```
Record Tab:
1. Click "Start Record"
2. Perform actions on the page (click, type, scroll)
3. Click "Stop"
4. Click "Play Recording" to replay
```

### 2. Workflow Templates

```
Workflows Tab:
- 抖音点赞 (Douyin Like) - Auto-like videos
- 批量截图 (Batch Screenshot) - Screenshot multiple pages
- 自动签到 (Auto Sign-in) - Website auto sign-in
- 表单填写 (Form Fill) - Auto-fill forms
```

### 3. Debug Panel

```
Debug Tab:
- Real-time operation logs
- Connection status
- Error tracking
```

## Connection Mode

### Enhanced Mode (Recommended) - Port 30000
- MCP enhanced features
- Complete bookmark management
- One-time authorization for all tabs
- New: Simplified DOM, index click, batch execution

## Quick Start

### 1. Install Plugin

1. Open Chrome extension management page `chrome://extensions`
2. Enable "Developer mode" (top right)
3. Click "Load unpacked"
4. Select `autoclaw-plugin` directory

### 2. Start MCP Server

```bash
cd autoclaw/mcp
npm start
```

### 3. Configure Plugin

1. Click plugin icon → Settings
2. Set port (default: **30000**, customizable)
3. Enter custom Token (optional, leave empty for built-in)
4. Click "Save Settings" to authorize
5. Click "Attach All Tabs"

## v6.0.0 New Optimization Tools

### 1. Simplified DOM Retrieval

```javascript
// Get page indexed interactive elements, data reduced by 90%+
{
  "name": "claw_get_indexed_elements",
  "arguments": { "useCache": true }
}

// Return example:
{
  "success": true,
  "elements": [
    {"index": 0, "tag": "button", "text": "Login", "id": "login-btn"},
    {"index": 1, "tag": "input", "placeholder": "Enter username"},
    {"index": 2, "tag": "a", "text": "Forgot password"}
  ],
  "count": 3,
  "cached": false
}
```

### 2. Index Click

```javascript
// Click element by index, more stable than CSS selector
{
  "name": "claw_click_by_index",
  "arguments": { "index": 0 }
}
```

### 3. Batch Execute

```javascript
// Batch execute CDP commands, reduce network round trips
{
  "name": "claw_batch_execute",
  "arguments": {
    "commands": [
      {"method": "Page.navigate", "params": {"url": "https://example.com"}},
      {"method": "Runtime.evaluate", "params": {"expression": "document.title"}}
    ]
  }
}
```

### 4. Smart Wait

```javascript
// Wait for element
{
  "name": "claw_smart_wait",
  "arguments": {
    "element": "#submit-btn",
    "timeout": 5000
  }
}

// Wait for text
{
  "name": "claw_smart_wait",
  "arguments": {
    "text": "Submitted successfully",
    "timeout": 10000
  }
}

// Wait for URL change
{
  "name": "claw_smart_wait",
  "arguments": {
    "urlPattern": "/dashboard.*",
    "timeout": 8000
  }
}
```

## Usage

### Via OpenClaw

1. Copy `autoclaw_wboke` to `~/.openclaw/workspace/skills/`
2. Speak to OpenClaw directly:
   - "Save this page to bookmarks"
   - "Open Baidu and take screenshot"
   - "Search bookmarks for Python"

### Via Command Line

```bash
# Open webpage
curl -X POST http://127.0.0.1:30000/mcp -d '{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "claw_navigate",
    "arguments": {"url": "https://www.baidu.com"}
  }
}'

# Screenshot
curl -X POST http://127.0.0.1:30000/mcp -d '{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/call",
  "params": {
    "name": "claw_take_screenshot"
  }
}'

# Create bookmark
curl -X POST http://127.0.0.1:30000/mcp -d '{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/call",
  "params": {
    "name": "claw_create_bookmark",
    "arguments": {"title": "Baidu", "url": "https://www.baidu.com"}
  }
}'
```

## File Structure

```
autoclaw_wboke/
├── SKILL.md                    # Skill definition
├── README.md                   # Main documentation
├── mcp/                       # MCP Server
│   ├── package.json
│   ├── dist/server.js         # Compiled server (v5.2.0)
│   └── node_modules/
├── autoclaw-plugin/           # Chrome Extension
│   ├── manifest.json
│   ├── background.js          # Background script (v6.0.0) ⭐
│   ├── popup.js               # Popup UI
│   └── options.js             # Settings UI
└── scripts/                   # Automation script templates
    ├── 抖音点赞.json
    ├── 批量截图.json
    └── 自动搜索.json
```

## v6.0.0 Performance Optimization

### Plugin Optimization

| Optimization | Before | After | Effect |
|--------------|--------|-------|--------|
| CDP Domain | Enable all 4 domains each time | Enable only 2 base domains, others on-demand | Resource ↓30% |
| Connection Poll | Check every 5 seconds | Check every 30 seconds | CPU/Network ↓40% |
| Popup Poll | Refresh every 3 seconds | Refresh every 10 seconds | Battery/Resource ↓ |
| DOM Cache | None | Reuse within 15 seconds | Repeat requests ↓50% |

### MCP Server Optimization

| New Tool | Function |
|----------|----------|
| `claw_get_indexed_elements` | Get indexed DOM |
| `claw_click_by_index` | Click by index |
| `claw_batch_execute` | Batch execute |
| `claw_smart_wait` | Smart wait |

### Impact on Original Features

✅ **Fully compatible, no impact**

- All original tools continue to work normally
- Bookmark features are completely independent, unaffected
- AI service will automatically choose better options

## Custom Token Support

### Built-in Token (Default)
```
autoclaw_builtin_Q0hpK2oV4F9tlwbYX3RELxiJNGDvayr8OPqZzkfs
```

### Custom Token
1. Click plugin icon → Settings
2. Enter your custom Token in the Token field
3. Click "Save Settings"

## FAQ

### Q: MCP server won't start
A: Ensure dependencies are installed: `cd autoclaw/mcp && npm install`

### Q: Plugin can't connect
A: 
1. Check if MCP server is running on port 30000
2. Check if Token is correct
3. Click "Attach All Tabs" to complete authorization

### Q: How to use script templates?
A: Just say "Use Douyin like script" in OpenClaw, AI will automatically read and execute.

### Q: Will v6.0.0 optimization affect original features?
A: No. Optimization is additive, all 50+ original tools are fully compatible.

## Technical Support

- MCP Server Port: 30000 (customizable)
- Built-in Token: autoclaw_builtin_Q0hpK2oV4F9tlwbYX3RELxiJNGDvayr8OPqZzkfs
- Version: Plugin v6.0.0 | MCP v5.2.0

---

Made with ❤️ for AutoClaw
