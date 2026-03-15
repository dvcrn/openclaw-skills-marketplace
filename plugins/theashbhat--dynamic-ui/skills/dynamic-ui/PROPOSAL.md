# Dynamic UI Skill — Proposal

> **Status:** Proposal  
> **Author:** Tony (AI Assistant)  
> **Date:** 2026-02-22  
> **Related:** `md-table` skill (table rendering already implemented)

---

## 1. Overview

### What is this skill?

**Dynamic UI** is a visual output generation skill that transforms structured data (JSON, YAML, Markdown) into beautiful, shareable images. It uses HTML templates + CSS styling rendered via `wkhtmltoimage` to produce PNG images suitable for chat platforms, reports, and dashboards.

Think of it as a **design system for AI outputs** — when text isn't enough, Dynamic UI creates polished visual artifacts.

### Why is it useful for an AI assistant?

1. **Better Communication** — A chart conveys trends faster than a paragraph. A comparison table beats a bulleted list. Visual outputs match how humans naturally process information.

2. **Platform Limitations** — Many chat platforms (Telegram, Discord, WhatsApp) have limited formatting support. Images bypass these constraints entirely.

3. **Shareability** — Images are universally shareable. A well-designed stats card can be forwarded, posted to social media, or embedded in documents.

4. **Professionalism** — Polished visuals signal competence. A styled dashboard looks more trustworthy than raw text dumps.

5. **Density** — Complex information (multi-dimensional comparisons, hierarchies, timelines) often requires spatial layout that text can't provide.

6. **Memory Aid** — Visual formats are more memorable. A kanban board or timeline sticks in the mind better than a list.

---

## 2. Use Cases

### When visualization beats text:

| # | Use Case | Why Visual is Better |
|---|----------|---------------------|
| 1 | **Comparison Tables** | Side-by-side product/option comparisons need spatial alignment |
| 2 | **Status Dashboards** | Multiple metrics at a glance; color-coded health indicators |
| 3 | **Bar Charts** | Comparing quantities across categories (sales by region, votes by option) |
| 4 | **Line Charts** | Showing trends over time (stock prices, metrics, progress) |
| 5 | **Pie/Donut Charts** | Part-to-whole relationships (budget allocation, market share) |
| 6 | **Info Cards** | Contact profiles, product cards, event summaries |
| 7 | **Timelines** | Project history, event sequences, biographical info |
| 8 | **Kanban Boards** | Task status across stages (To Do → In Progress → Done) |
| 9 | **Leaderboards** | Ranked lists with scores, changes, badges |
| 10 | **Weather Displays** | Multi-day forecasts with icons, temps, conditions |
| 11 | **Financial Summaries** | Portfolio values, P&L, transaction summaries |
| 12 | **Scorecards** | KPI snapshots with targets vs actuals |
| 13 | **Org Charts** | Hierarchical relationships |
| 14 | **Receipts/Invoices** | Itemized lists with totals |
| 15 | **Progress Trackers** | Goal completion, habit streaks, milestone charts |
| 16 | **Quote Cards** | Shareable quotes with attribution and styling |
| 17 | **Menu/Price Lists** | Restaurant menus, service pricing |
| 18 | **Comparison Matrices** | Feature grids (✓/✗ across products) |
| 19 | **Calendar Views** | Month/week views with events highlighted |
| 20 | **Maps with Markers** | Location-based data visualization |

### Concrete Examples

**Example 1: Restaurant Comparison**
> "Compare these 3 restaurants"
> 
> Instead of: "Restaurant A has 4.5 stars, $$, Italian. Restaurant B has 4.2 stars..."
> 
> Generate: A styled comparison card showing all three side-by-side with ratings, price, cuisine, distance, and photos.

**Example 2: Project Status**
> "What's the status of Project X?"
> 
> Instead of: "There are 12 tasks. 5 are complete, 4 are in progress, 3 are blocked..."
> 
> Generate: A kanban board or dashboard showing task distribution with color-coded status.

**Example 3: Portfolio Summary**
> "How's my crypto portfolio doing?"
> 
> Instead of: "BTC is up 3.2%, ETH is down 1.4%..."
> 
> Generate: A financial dashboard with holdings, values, changes, and a pie chart of allocation.

---

## 3. Architecture

### Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                        INPUT LAYER                               │
├─────────────┬─────────────┬─────────────┬──────────────────────┤
│  Markdown   │    JSON     │    YAML     │    CLI Flags         │
│  (tables)   │ (structured)│ (human-     │  (simple cases)      │
│             │             │  friendly)  │                      │
└──────┬──────┴──────┬──────┴──────┬──────┴───────────┬──────────┘
       │             │             │                  │
       └─────────────┴──────┬──────┴──────────────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │    INPUT PARSER      │
                 │  (normalize to JSON) │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │  TEMPLATE SELECTOR   │
                 │  (--template flag or │
                 │   auto-detect)       │
                 └──────────┬───────────┘
                            │
                            ▼
         ┌──────────────────┴───────────────────┐
         │           TEMPLATE ENGINE            │
         │  ┌─────────────────────────────────┐ │
         │  │  Built-in Templates (15+)       │ │
         │  │  • table, chart-bar, chart-pie  │ │
         │  │  • card, dashboard, timeline    │ │
         │  │  • kanban, leaderboard, etc.    │ │
         │  └─────────────────────────────────┘ │
         │  ┌─────────────────────────────────┐ │
         │  │  Custom Templates               │ │
         │  │  • User-provided HTML/CSS       │ │
         │  │  • Template variables: {{var}}  │ │
         │  └─────────────────────────────────┘ │
         └──────────────────┬───────────────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │   STYLE RESOLVER     │
                 │  • Theme selection   │
                 │  • Color overrides   │
                 │  • Size/dimensions   │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │   HTML GENERATOR     │
                 │  • Inject data       │
                 │  • Apply styles      │
                 │  • Handle charts     │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │   wkhtmltoimage      │
                 │  • HTML → PNG        │
                 │  • Quality settings  │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │      OUTPUT          │
                 │  • PNG file          │
                 │  • stdout (base64)   │
                 │  • Direct to chat    │
                 └──────────────────────┘
```

### Template System

#### Built-in Templates
Pre-designed, tested templates that "just work" with structured data. Each template defines:
- Required data fields
- Optional data fields with defaults
- CSS styling (with theme variants)
- Responsive sizing rules

#### Custom Templates
Users can provide their own HTML templates with Mustache-style variables:
```html
<div class="my-card">
  <h1>{{title}}</h1>
  <p>{{description}}</p>
  {{#items}}
  <div class="item">{{name}}: {{value}}</div>
  {{/items}}
</div>
```

### Styling Options

#### Themes
Each template supports multiple themes:
- `light` — Clean, minimal, professional (default)
- `dark` — Dark backgrounds, softer on eyes
- `colorful` — Vibrant gradients and colors
- `minimal` — Ultra-clean, no shadows or gradients
- `brand` — Customizable brand colors

#### Color Overrides
```bash
--primary "#6366f1"    # Primary accent color
--background "#ffffff" # Background color
--text "#1f2937"       # Text color
```

#### Sizing
```bash
--width 800            # Output width in pixels
--height auto          # Auto-calculate or specify
--scale 2              # Retina/HiDPI scaling
```

---

## 4. Template Library

### Core Templates (15 Built-in)

#### 1. `table` — Data Tables ✅ (Already Implemented)
Converts markdown or JSON tables to styled images.

**Input:**
```json
{
  "headers": ["Name", "Role", "Status"],
  "rows": [
    ["Alice", "Engineer", "Active"],
    ["Bob", "Designer", "Away"]
  ]
}
```

**Styles:** modern, minimal, dark, striped

---

#### 2. `chart-bar` — Bar Charts
Horizontal or vertical bar charts for comparing quantities.

**Input:**
```json
{
  "title": "Sales by Region",
  "labels": ["North", "South", "East", "West"],
  "values": [420, 380, 290, 510],
  "orientation": "vertical",
  "showValues": true
}
```

**Features:**
- Horizontal/vertical orientation
- Grouped bars (multiple series)
- Stacked bars
- Value labels on/off
- Color per bar or gradient

---

#### 3. `chart-pie` — Pie/Donut Charts
Part-to-whole relationships with optional donut hole.

**Input:**
```json
{
  "title": "Budget Allocation",
  "segments": [
    {"label": "Engineering", "value": 45, "color": "#6366f1"},
    {"label": "Marketing", "value": 25, "color": "#22c55e"},
    {"label": "Operations", "value": 20, "color": "#f59e0b"},
    {"label": "Other", "value": 10, "color": "#94a3b8"}
  ],
  "donut": true,
  "showPercentages": true
}
```

**Features:**
- Pie or donut style
- Percentage labels
- Legend positioning
- Custom colors per segment

---

#### 4. `chart-line` — Line/Area Charts
Trends over time with single or multiple series.

**Input:**
```json
{
  "title": "Monthly Revenue",
  "xAxis": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
  "series": [
    {"name": "2025", "values": [10, 15, 13, 17, 20, 25]},
    {"name": "2024", "values": [8, 12, 11, 14, 16, 19]}
  ],
  "fill": false,
  "showPoints": true
}
```

**Features:**
- Multiple series
- Area fill option
- Point markers
- Smooth curves option
- Grid lines

---

#### 5. `card` — Info Cards
Single-item displays with image, title, stats.

**Input:**
```json
{
  "image": "https://example.com/photo.jpg",
  "title": "Product Name",
  "subtitle": "Category",
  "stats": [
    {"label": "Price", "value": "$99"},
    {"label": "Rating", "value": "4.5 ★"},
    {"label": "Reviews", "value": "1,234"}
  ],
  "badge": "NEW"
}
```

**Features:**
- Image (optional)
- Title/subtitle
- Stats grid
- Badge/tag
- Action buttons (visual only)

---

#### 6. `dashboard` — Multi-Widget Layout
Combine multiple visualizations in a grid.

**Input:**
```json
{
  "title": "Weekly Report",
  "layout": "2x2",
  "widgets": [
    {"type": "stats", "data": {...}},
    {"type": "chart-pie", "data": {...}},
    {"type": "table", "data": {...}},
    {"type": "chart-line", "data": {...}}
  ]
}
```

**Features:**
- Flexible grid layouts (1x2, 2x2, 3x1, etc.)
- Mix any template types
- Shared theming
- Dashboard title/subtitle

---

#### 7. `timeline` — Vertical Timeline
Event sequences, project history, biographies.

**Input:**
```json
{
  "title": "Project Milestones",
  "events": [
    {"date": "Jan 2025", "title": "Project Kickoff", "description": "Team assembled, goals defined"},
    {"date": "Mar 2025", "title": "MVP Complete", "description": "Core features working", "icon": "🚀"},
    {"date": "Jun 2025", "title": "Public Launch", "description": "Available to all users", "icon": "🎉"}
  ]
}
```

**Features:**
- Date/time labels
- Icons per event
- Left/right alternating layout
- Color coding by category

---

#### 8. `kanban` — Kanban Board
Task status visualization across columns.

**Input:**
```json
{
  "title": "Sprint 42",
  "columns": [
    {"name": "To Do", "color": "#94a3b8", "cards": [
      {"title": "Design review", "tags": ["design"], "assignee": "Alice"}
    ]},
    {"name": "In Progress", "color": "#6366f1", "cards": [
      {"title": "API integration", "tags": ["backend"], "assignee": "Bob"}
    ]},
    {"name": "Done", "color": "#22c55e", "cards": [
      {"title": "Setup CI/CD", "tags": ["devops"]}
    ]}
  ]
}
```

**Features:**
- Multiple columns
- Cards with tags, assignees
- WIP limits display
- Column card counts

---

#### 9. `leaderboard` — Ranked List
Scores, rankings, competitions.

**Input:**
```json
{
  "title": "Top Contributors",
  "entries": [
    {"rank": 1, "name": "Alice", "score": 2450, "change": "+3", "avatar": "..."},
    {"rank": 2, "name": "Bob", "score": 2380, "change": "-1"},
    {"rank": 3, "name": "Charlie", "score": 2290, "change": "+5"}
  ],
  "metric": "points"
}
```

**Features:**
- Rank numbers with medals (🥇🥈🥉)
- Score display
- Change indicators (↑↓)
- Avatar images
- Highlight specific entries

---

#### 10. `weather` — Weather Display
Multi-day forecasts with conditions.

**Input:**
```json
{
  "location": "San Francisco, CA",
  "current": {"temp": 62, "condition": "Partly Cloudy", "icon": "⛅"},
  "forecast": [
    {"day": "Mon", "high": 65, "low": 52, "icon": "☀️"},
    {"day": "Tue", "high": 63, "low": 51, "icon": "🌤️"},
    {"day": "Wed", "high": 58, "low": 48, "icon": "🌧️"}
  ],
  "unit": "F"
}
```

**Features:**
- Current conditions
- Multi-day forecast
- Weather icons
- High/low temps
- Optional: humidity, wind, UV

---

#### 11. `profile` — User/Contact Card
People profiles, contact cards.

**Input:**
```json
{
  "avatar": "https://example.com/avatar.jpg",
  "name": "Jane Doe",
  "title": "Product Manager",
  "company": "TechCorp",
  "bio": "Building the future of collaboration",
  "contact": {
    "email": "jane@example.com",
    "phone": "+1 555-1234",
    "location": "San Francisco, CA"
  },
  "social": [
    {"platform": "twitter", "handle": "@janedoe"},
    {"platform": "linkedin", "url": "..."}
  ]
}
```

**Features:**
- Avatar image
- Name/title/company
- Bio text
- Contact info
- Social links with icons

---

#### 12. `comparison` — Side-by-Side Comparison
Feature matrices, product comparisons.

**Input:**
```json
{
  "title": "Plan Comparison",
  "items": [
    {"name": "Basic", "price": "$9/mo", "highlight": false},
    {"name": "Pro", "price": "$29/mo", "highlight": true},
    {"name": "Enterprise", "price": "Custom", "highlight": false}
  ],
  "features": [
    {"name": "Users", "values": ["1", "5", "Unlimited"]},
    {"name": "Storage", "values": ["1 GB", "10 GB", "100 GB"]},
    {"name": "Support", "values": ["Email", "Priority", "Dedicated"]},
    {"name": "API Access", "values": ["❌", "✓", "✓"]}
  ]
}
```

**Features:**
- Multiple items (2-5)
- Feature rows with values
- Checkmarks/X marks
- Highlight "recommended" option
- Price/CTA row

---

#### 13. `stats` — Big Number Stats
KPI displays, metric summaries.

**Input:**
```json
{
  "stats": [
    {"label": "Total Users", "value": "12,458", "change": "+12%", "trend": "up"},
    {"label": "Revenue", "value": "$84.2K", "change": "+8%", "trend": "up"},
    {"label": "Churn", "value": "2.1%", "change": "-0.3%", "trend": "down"},
    {"label": "NPS", "value": "72", "change": "+5", "trend": "up"}
  ],
  "layout": "row"
}
```

**Features:**
- Large prominent values
- Labels
- Change indicators with colors
- Trend arrows
- Row or grid layout

---

#### 14. `quote` — Quote Cards
Shareable quotes with attribution.

**Input:**
```json
{
  "quote": "The best way to predict the future is to invent it.",
  "author": "Alan Kay",
  "source": "1971",
  "style": "elegant"
}
```

**Features:**
- Large quote text
- Author attribution
- Source/date
- Multiple visual styles
- Background image option

---

#### 15. `receipt` — Receipt/Invoice
Itemized lists with totals.

**Input:**
```json
{
  "title": "Order #12345",
  "date": "2025-02-22",
  "items": [
    {"name": "Widget Pro", "qty": 2, "price": 49.99},
    {"name": "Gadget Plus", "qty": 1, "price": 79.99}
  ],
  "subtotal": 179.97,
  "tax": 14.40,
  "total": 194.37,
  "currency": "USD"
}
```

**Features:**
- Header with order info
- Line items with quantities
- Subtotal/tax/total
- Currency formatting
- Optional: merchant info, payment method

---

## 5. Input Formats

### Markdown (for tables)
```markdown
| Name | Status | Score |
|------|--------|-------|
| Alice | ✅ Active | 95 |
| Bob | ⚠️ Away | 82 |
```

Best for: Quick tables, human-written content, existing markdown.

### JSON (for structured data)
```json
{
  "template": "chart-bar",
  "data": {
    "title": "Monthly Sales",
    "labels": ["Jan", "Feb", "Mar"],
    "values": [100, 150, 120]
  },
  "options": {
    "theme": "dark",
    "width": 600
  }
}
```

Best for: Programmatic generation, complex nested data, API integration.

### YAML (human-friendly)
```yaml
template: leaderboard
data:
  title: Top Players
  entries:
    - name: Alice
      score: 2450
      change: "+3"
    - name: Bob
      score: 2380
      change: "-1"
options:
  theme: colorful
```

Best for: Human-authored configs, readability, comments.

### CLI Flags (simple cases)
```bash
dynamic-ui --template stats \
  --stat "Users:12,458:+12%" \
  --stat "Revenue:$84K:+8%" \
  --theme dark \
  --output stats.png
```

Best for: Quick one-offs, shell scripts, simple data.

---

## 6. Usage Examples

### Example 1: Simple Table
```bash
echo "| Feature | Free | Pro |
|---------|------|-----|
| Storage | 1GB | 10GB |
| Support | Email | Priority |" | dynamic-ui --template table --style modern -o comparison.png
```

**Output:** Styled comparison table with header highlighting.

---

### Example 2: Bar Chart from JSON
```bash
cat << 'EOF' | dynamic-ui --template chart-bar -o sales.png
{
  "title": "Q4 Sales by Region",
  "labels": ["North", "South", "East", "West"],
  "values": [420000, 380000, 290000, 510000],
  "format": "currency"
}
EOF
```

**Output:** Vertical bar chart with formatted currency values, gradient colors.

---

### Example 3: Dashboard
```bash
dynamic-ui --template dashboard \
  --layout 2x2 \
  --widget 'stats:{"stats":[{"label":"Users","value":"12K"}]}' \
  --widget 'chart-pie:{"segments":[{"label":"A","value":60},{"label":"B","value":40}]}' \
  --widget 'table:{"headers":["Name","Status"],"rows":[["API","✅"],["DB","✅"]]}' \
  --widget 'chart-line:{"xAxis":["Mon","Tue","Wed"],"series":[{"values":[10,15,12]}]}' \
  --title "System Overview" \
  -o dashboard.png
```

**Output:** 2x2 grid with stats card, pie chart, status table, and line chart.

---

### Example 4: Weather Display
```bash
cat << 'EOF' | dynamic-ui --template weather -o weather.png
{
  "location": "San Francisco",
  "current": {"temp": 62, "condition": "Partly Cloudy", "icon": "⛅"},
  "forecast": [
    {"day": "Today", "high": 65, "low": 52, "icon": "⛅"},
    {"day": "Tue", "high": 63, "low": 51, "icon": "☀️"},
    {"day": "Wed", "high": 58, "low": 48, "icon": "🌧️"},
    {"day": "Thu", "high": 61, "low": 50, "icon": "🌤️"},
    {"day": "Fri", "high": 64, "low": 53, "icon": "☀️"}
  ]
}
EOF
```

**Output:** Current conditions header + 5-day forecast row with icons.

---

### Example 5: Kanban Board
```yaml
# kanban.yaml
template: kanban
data:
  title: "Sprint 42"
  columns:
    - name: "📋 Backlog"
      cards:
        - title: "Research competitors"
          tags: [research]
    - name: "🔨 In Progress"  
      cards:
        - title: "Build API"
          tags: [backend]
          assignee: "Bob"
        - title: "Design mockups"
          tags: [design]
          assignee: "Alice"
    - name: "✅ Done"
      cards:
        - title: "Setup CI/CD"
        - title: "Write docs"
```

```bash
dynamic-ui -f kanban.yaml -o sprint.png
```

**Output:** 3-column kanban board with cards, tags, and assignees.

---

### Example 6: Leaderboard
```bash
dynamic-ui --template leaderboard \
  --title "This Week's Top Contributors" \
  --entry "Alice:2,450:+125" \
  --entry "Bob:2,380:-45" \
  --entry "Charlie:2,290:+312" \
  --entry "Diana:2,150:+88" \
  --entry "Eve:2,020:-15" \
  --theme dark \
  -o leaderboard.png
```

**Output:** Ranked list with medals, scores, and change indicators.

---

### Example 7: Profile Card
```bash
cat << 'EOF' | dynamic-ui --template profile -o contact.png
{
  "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=jane",
  "name": "Jane Doe",
  "title": "Senior Engineer",
  "company": "TechCorp",
  "bio": "Building distributed systems. Coffee enthusiast.",
  "contact": {
    "email": "jane@techcorp.com",
    "location": "San Francisco, CA"
  },
  "social": [
    {"platform": "github", "handle": "janedoe"},
    {"platform": "twitter", "handle": "@jane_codes"}
  ]
}
EOF
```

**Output:** Professional contact card with avatar, info, and social links.

---

### Example 8: Quote Card
```bash
dynamic-ui --template quote \
  --quote "The best way to predict the future is to invent it." \
  --author "Alan Kay" \
  --style elegant \
  --background "gradient:purple-blue" \
  -o quote.png
```

**Output:** Elegant quote card with gradient background.

---

### Example 9: Timeline
```bash
cat << 'EOF' | dynamic-ui --template timeline -o history.png
{
  "title": "Company History",
  "events": [
    {"date": "2020", "title": "Founded", "description": "Started in a garage", "icon": "🏠"},
    {"date": "2021", "title": "Seed Round", "description": "$2M raised", "icon": "💰"},
    {"date": "2022", "title": "Product Launch", "description": "V1.0 released", "icon": "🚀"},
    {"date": "2023", "title": "Series A", "description": "$15M raised", "icon": "📈"},
    {"date": "2024", "title": "100K Users", "description": "Major milestone", "icon": "🎉"}
  ]
}
EOF
```

**Output:** Vertical timeline with alternating left/right events.

---

### Example 10: Stats Card
```bash
dynamic-ui --template stats \
  --stat "Revenue:$1.2M:+18%:up" \
  --stat "Users:45,230:+2,340:up" \
  --stat "Churn:2.1%:-0.4%:down" \
  --stat "NPS:72:+8:up" \
  --layout grid \
  -o metrics.png
```

**Output:** 2x2 grid of large metric displays with trend indicators.

---

## 7. Technical Requirements

### Core Dependencies

| Component | Purpose | Status |
|-----------|---------|--------|
| `wkhtmltoimage` | HTML→PNG rendering | ✅ Installed |
| `bash` | Script orchestration | ✅ Available |
| `jq` | JSON parsing | ✅ Available |
| `yq` | YAML parsing | Install if needed |

### Chart Rendering Options

**Option A: Chart.js via CDN (Recommended)**
- Pros: Feature-rich, well-documented, beautiful defaults
- Cons: Requires JavaScript execution in wkhtmltoimage
- Implementation: Embed Chart.js via CDN, render charts to canvas

```html
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<canvas id="chart"></canvas>
<script>
  new Chart(document.getElementById('chart'), {
    type: 'bar',
    data: {{chartData}}
  });
</script>
```

**Option B: SVG-based (No JS required)**
- Pros: No JS execution needed, precise control
- Cons: More complex to implement, fewer features
- Implementation: Generate SVG paths directly from data

**Option C: Mermaid for diagrams**
- Pros: Text-based diagram syntax, good for flowcharts
- Cons: Limited chart types
- Use for: Org charts, flowcharts, sequence diagrams

**Recommendation:** Use Chart.js for standard charts, SVG for simple visualizations, Mermaid for diagrams.

### Styling Framework

**Option A: Tailwind CSS via CDN**
```html
<script src="https://cdn.tailwindcss.com"></script>
```
- Pros: Utility-first, consistent, extensive
- Cons: Larger payload, CDN dependency

**Option B: Custom CSS**
- Pros: Minimal, fast, no dependencies
- Cons: More work to maintain
- Current approach in `md-table`

**Recommendation:** Custom CSS for built-in templates (faster, no CDN), optional Tailwind for custom templates.

### wkhtmltoimage Configuration

```bash
wkhtmltoimage \
  --quality 90 \
  --width 800 \
  --enable-javascript \
  --javascript-delay 500 \
  --no-stop-slow-scripts \
  input.html output.png
```

Key flags:
- `--enable-javascript`: Required for Chart.js
- `--javascript-delay`: Wait for charts to render
- `--width`: Control output width
- `--quality`: PNG compression (90 is good balance)

---

## 8. Skill Structure

```
skills/dynamic-ui/
├── SKILL.md                    # Main documentation
├── PROPOSAL.md                 # This file (remove after implementation)
│
├── scripts/
│   ├── render.sh               # Main entry point
│   ├── parse-input.sh          # Input format detection & parsing
│   └── generate-html.sh        # Template + data → HTML
│
├── templates/
│   ├── base.html               # Shared HTML boilerplate
│   ├── table/
│   │   ├── template.html       # Table template
│   │   └── styles.css          # Table styles
│   ├── chart-bar/
│   │   ├── template.html
│   │   └── styles.css
│   ├── chart-pie/
│   │   ├── template.html
│   │   └── styles.css
│   ├── chart-line/
│   │   ├── template.html
│   │   └── styles.css
│   ├── card/
│   │   ├── template.html
│   │   └── styles.css
│   ├── dashboard/
│   │   ├── template.html
│   │   └── styles.css
│   ├── timeline/
│   │   ├── template.html
│   │   └── styles.css
│   ├── kanban/
│   │   ├── template.html
│   │   └── styles.css
│   ├── leaderboard/
│   │   ├── template.html
│   │   └── styles.css
│   ├── weather/
│   │   ├── template.html
│   │   └── styles.css
│   ├── profile/
│   │   ├── template.html
│   │   └── styles.css
│   ├── comparison/
│   │   ├── template.html
│   │   └── styles.css
│   ├── stats/
│   │   ├── template.html
│   │   └── styles.css
│   ├── quote/
│   │   ├── template.html
│   │   └── styles.css
│   └── receipt/
│       ├── template.html
│       └── styles.css
│
├── themes/
│   ├── light.css               # Light theme variables
│   ├── dark.css                # Dark theme
│   ├── colorful.css            # Vibrant colors
│   └── minimal.css             # Ultra-clean
│
├── lib/
│   ├── chart.js                # Local Chart.js copy (optional)
│   └── icons/                  # SVG icons for templates
│       ├── weather/
│       ├── social/
│       └── ui/
│
├── examples/
│   ├── table.json
│   ├── chart-bar.json
│   ├── dashboard.json
│   └── ...
│
└── tests/
    ├── test-all.sh             # Run all template tests
    └── snapshots/              # Expected output images
```

### Key Files Explained

**`scripts/render.sh`** — Main entry point
```bash
#!/usr/bin/env bash
# Usage: dynamic-ui [options] [input]
#   --template NAME    Template to use (auto-detect if not specified)
#   --theme NAME       Theme (light, dark, colorful, minimal)
#   --output PATH      Output file (default: stdout)
#   --width NUMBER     Output width in pixels
#   -f FILE            Read input from file
```

**`templates/base.html`** — Shared boilerplate
```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <style>
    {{theme_css}}
    {{template_css}}
  </style>
  {{#needs_chartjs}}
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  {{/needs_chartjs}}
</head>
<body>
  {{content}}
  {{#chart_script}}
  <script>{{chart_script}}</script>
  {{/chart_script}}
</body>
</html>
```

---

## 9. Future Enhancements

### Phase 2: Interactive HTML Output
- Export as standalone HTML files (not just images)
- Hover effects, tooltips, clickable elements
- Embed in web pages or emails
- Use case: Dashboards that update, interactive reports

### Phase 3: Animation Support
- Animated chart transitions (bars growing, lines drawing)
- GIF output option
- Animated number counting
- Use case: Social media content, presentations

### Phase 4: Custom Template Upload
- Upload custom HTML/CSS templates
- Template variables documentation
- Validation and sandboxing
- Use case: Brand-specific designs, unique layouts

### Phase 5: Theme Marketplace
- Community-contributed themes
- Theme preview gallery
- One-click theme installation
- Use case: Variety without design work

### Phase 6: Data Connectors
- Direct API integration (pull data from sources)
- Google Sheets connector
- Database queries
- Use case: Auto-updating dashboards

### Phase 7: AI-Assisted Design
- "Make this look better" — AI suggests improvements
- Auto-color selection based on data
- Smart layout recommendations
- Use case: Non-designers creating polished outputs

### Phase 8: Template Builder UI
- Visual template editor
- Drag-and-drop components
- Live preview
- Export as reusable template
- Use case: Create templates without coding

---

## 10. Implementation Roadmap

### Sprint 1: Foundation (Week 1)
- [ ] Set up directory structure
- [ ] Port `md-table` into new architecture
- [ ] Implement `render.sh` main script
- [ ] Implement input parsing (JSON, YAML, MD)
- [ ] Create theme system with light/dark

### Sprint 2: Charts (Week 2)
- [ ] Implement `chart-bar` template
- [ ] Implement `chart-pie` template
- [ ] Implement `chart-line` template
- [ ] Test Chart.js integration with wkhtmltoimage

### Sprint 3: Cards & Lists (Week 3)
- [ ] Implement `card` template
- [ ] Implement `stats` template
- [ ] Implement `leaderboard` template
- [ ] Implement `profile` template

### Sprint 4: Complex Layouts (Week 4)
- [ ] Implement `dashboard` template
- [ ] Implement `kanban` template
- [ ] Implement `timeline` template
- [ ] Implement `comparison` template

### Sprint 5: Polish & Utilities (Week 5)
- [ ] Implement `weather` template
- [ ] Implement `quote` template
- [ ] Implement `receipt` template
- [ ] Add all themes (colorful, minimal)
- [ ] Comprehensive documentation
- [ ] Example gallery

### Sprint 6: Testing & Release
- [ ] Snapshot tests for all templates
- [ ] Performance optimization
- [ ] Error handling improvements
- [ ] SKILL.md final version
- [ ] Announce and integrate

---

## Appendix A: Design Principles

1. **Sensible Defaults** — Works beautifully out of the box
2. **Progressive Complexity** — Simple things simple, complex things possible
3. **Consistency** — Same options work across templates
4. **Performance** — Fast enough for real-time chat responses
5. **Accessibility** — Good contrast, readable fonts, not just pretty
6. **Platform-Agnostic** — Looks good on any chat platform or screen size

## Appendix B: Color Palette (Default Theme)

```css
:root {
  /* Primary */
  --primary-50: #eef2ff;
  --primary-500: #6366f1;
  --primary-600: #4f46e5;
  
  /* Success */
  --success-500: #22c55e;
  
  /* Warning */
  --warning-500: #f59e0b;
  
  /* Error */
  --error-500: #ef4444;
  
  /* Neutral */
  --gray-50: #f9fafb;
  --gray-100: #f3f4f6;
  --gray-200: #e5e7eb;
  --gray-500: #6b7280;
  --gray-700: #374151;
  --gray-900: #111827;
}
```

## Appendix C: Related Work

- **md-table skill** — Already implements table rendering, will be merged/superseded
- **d2-diagrams skill** — For technical diagrams (different use case)
- **Canvas system** — Could potentially use for live previews

---

*This proposal is ready for review. Implementation can begin once approved.*
