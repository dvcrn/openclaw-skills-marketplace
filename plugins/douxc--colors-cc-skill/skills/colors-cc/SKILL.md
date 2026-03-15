---
name: colors-cc
description: "A native UI asset and color toolset for OpenClaw and other AI Agents. Generate SVG placeholders, animated gradients, theme-based palettes, and perform color conversions without hallucination."
---

# SKILL: ColorsCC

A high-performance, stateless Color API and toolset optimized for AI Agents (OpenClaw, Cursor, Cline, GPTs).

## 🚀 Usage Rules for Agents
- **Inline Images**: Always embed SVG placeholders directly using `<img>` or Markdown `![alt](url)`.
- **URL Encoding**: The `#` character must be encoded as `%23` (e.g., `start=%23FF003C`).
- **No Fetching**: Do not attempt to download binary image data; let the user's client render the URL.
- **Valid Dimensions**: Width and height are clamped between 50-4000px automatically.
- **Text Limit**: Placeholder text is truncated to 100 characters max.

## 🛠 Capabilities

### 1. SVG Gradient Placeholders
Generate dynamic, lightweight placeholders for UI mockups with linear gradients.
- **Endpoint**: `https://api.colors-cc.top/placeholder`
- **Params**: 
  - `w`: Width in pixels (default: 800, range: 50-4000)
  - `h`: Height in pixels (default: 400, range: 50-4000)
  - `text`: Center text, URL-encoded (default: "{width} x {height}", max: 100 chars)
  - `start`: Start gradient color as hex (default: random, must be valid 6-digit hex)
  - `end`: End gradient color as hex (default: random, must be valid 6-digit hex)
- **Example**: `<img src="https://api.colors-cc.top/placeholder?w=1200&h=630&text=Hero+Banner&start=%23F06292&end=%2364B5F6" alt="Hero">`
- **Response**: SVG image with `Cache-Control: public, max-age=31536000, immutable`

### 2. Fluid Animated Placeholders
Generate dynamic SVG gradients with smooth color transitions and animations.
- **Endpoint**: `https://api.colors-cc.top/fluid-placeholder`
- **Params**: 
  - `w`: Width in pixels (default: 800, range: 50-4000)
  - `h`: Height in pixels (default: 400, range: 50-4000)
  - `stops`: Comma-separated HEX colors for gradient (default: warm pastel theme, range: 2-10 colors)
  - `speed`: Animation duration in seconds (default: 10, range: 1-30)
  - `text`: Optional center text (max 100 chars)
- **Example**: `<img src="https://api.colors-cc.top/fluid-placeholder?w=1200&h=400&stops=%23FFD6A5,%23FFADAD,%23E2A0FF&speed=8&text=Animated+Hero" alt="Warm Gradient">`
- **Response**: Animated SVG with smooth color transitions and `Cache-Control: public, max-age=31536000, immutable`

### 3. Random Colors
Get a random HEX and RGB color with generation timestamp.
- **Endpoint**: `GET https://api.colors-cc.top/random`
- **Returns**: `{"hex": "#A1B2C3", "rgb": "rgb(161, 178, 195)", "timestamp": "2024-03-12T10:30:00.000Z"}`
- **Example**: Fetch this endpoint when you need random colors for mock data or UI components.

### 4. Curated Theme Palettes
Fetch high-quality color sets for design inspiration.
- **Endpoint**: `GET https://api.colors-cc.top/palette?theme={theme_name}`
- **Themes**: `cyberpunk`, `vaporwave`, `retro`, `monochrome`
- **Returns**: `{"theme": "cyberpunk", "colors": ["#FCEE09", "#00FF41", ...], "count": 5}`
- **Example**: `fetch('https://api.colors-cc.top/palette?theme=vaporwave')`

### 5. Universal Color Converter
Stateless conversion between HEX, RGB, HSL, and CMYK formats.
- **Endpoint**: `GET https://api.colors-cc.top/convert?hex={hex}|rgb={rgb}|hsl={hsl}|cmyk={cmyk}`
- **Params**: Provide ONE of: `hex`, `rgb`, `hsl`, or `cmyk`
- **Returns**: `{"hex": "#FF5733", "rgb": "rgb(255, 87, 51)", "hsl": "hsl(10, 100%, 60%)", "cmyk": "cmyk(0%, 66%, 80%, 0%)"}`
- **Example**: `https://api.colors-cc.top/convert?hex=%23FF5733`
- **Error**: Returns `{"error": "Invalid color format"}` with status 400 if input is invalid

### 6. CSS Color Names Directory
Get all standard CSS color names mapped to their HEX values (~140 colors).
- **Endpoint**: `GET https://api.colors-cc.top/all-names`
- **Returns**: `{"AliceBlue": "#F0F8FF", "AntiqueWhite": "#FAEBD7", "Tomato": "#FF6347", ...}`
- **Example**: Use this to look up named colors like 'tomato' → '#FF6347'

## 📖 Common Use Cases

### Use Case 1: Building a Landing Page
```html
<section class="hero">
  <!-- Animated hero banner with text -->
  <img src="https://api.colors-cc.top/fluid-placeholder?w=1200&h=600&text=Hero+Section&stops=%23FFD6A5,%23FFADAD,%23E2A0FF&speed=10" alt="Hero">
</section>
<div class="features">
  <!-- Static placeholder images -->
  <img src="https://api.colors-cc.top/placeholder?w=400&h=300&text=Feature+1" alt="Feature 1">
  <img src="https://api.colors-cc.top/placeholder?w=400&h=300&text=Feature+2" alt="Feature 2">
</div>
```

### Use Case 2: Generating Mock Data with Colors
```javascript
const palette = await fetch('https://api.colors-cc.top/palette?theme=vaporwave')
  .then(r => r.json())

const mockData = palette.colors.map((color, i) => ({
  id: i,
  name: `Item ${i+1}`,
  color: color,
  thumbnail: `https://api.colors-cc.top/placeholder?w=200&h=200&start=${color.slice(1)}`
}))
```

### Use Case 3: Color Picker Component
```javascript
async function getRandomColor() {
  const res = await fetch('https://api.colors-cc.top/random')
  const data = await res.json()
  return data.hex
}
```

### Use Case 4: Universal Color Converter
```javascript
// Convert any color format to all formats
const result = await fetch('https://api.colors-cc.top/convert?hsl=hsl(200,50%,50%)')
  .then(r => r.json())
console.log(result.hex) // #4099BF
```

## ⚠️ Common Pitfalls & Solutions

### ❌ Mistake 1: Unencoded Hash Symbol
```
BAD:  start=#FF0000
GOOD: start=%23FF0000
```

### ❌ Mistake 2: Fetching SVG and Re-processing
```javascript
// BAD - Don't do this
const svg = await fetch(placeholderUrl).then(r => r.text())
const encoded = btoa(svg)

// GOOD - Use URL directly
<img src="https://api.colors-cc.top/placeholder?w=800&h=400" alt="Direct">
```

### ❌ Mistake 3: Invalid Dimensions
```
BAD:  w=10 (too small, will be clamped to 50)
BAD:  w=9999 (too large, will be clamped to 4000)
GOOD: w=800&h=600
```

### ❌ Mistake 4: Multiple Color Parameters in /api/convert
```
BAD:  /api/convert?hex=%23FF0000&rgb=rgb(255,0,0)
GOOD: /api/convert?hex=%23FF0000
```

### ❌ Mistake 5: Invalid Number of Color Stops in Fluid Placeholder
```
BAD:  stops=%23FF0000 (only 1 color, minimum is 2)
BAD:  stops=%23FF0000,%23... (more than 10 colors, will be ignored)
GOOD: stops=%23FF0000,%230000FF,%2300FF00 (2-10 colors)
```

## 🌐 Web Tools (For Users)
- Universal Color Converter: https://colors-cc.top/tools/converter
- Random Palette Generator: https://colors-cc.top/tools/random-palette
- CSS Color Names Reference: https://colors-cc.top/tools/color-names
- Fluid Gradient Placeholder: https://colors-cc.top/tools/fluid-placeholder

## 📚 Full Documentation
For complete API documentation, reference:
- LLM-optimized docs: https://colors-cc.top/llms.txt
- OpenAPI specification: https://colors-cc.top/openapi.json
- Live site: https://colors-cc.top/

## 💡 Rate Limits
None. All endpoints are free and unlimited.
