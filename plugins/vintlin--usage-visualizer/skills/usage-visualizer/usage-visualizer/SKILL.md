---
name: usage-visualizer
description: Advanced usage statistics and high-fidelity visual reporting for OpenClaw. Trigger when user says usage report/usage stats/用量汇报/用量统计; always sync latest logs first, then generate report.
metadata:
  openclaw:
    emoji: "📊"
    os:
      - darwin
      - linux
    requires:
      bins:
        - python3
---

# Usage Visualizer

**Usage Visualizer** is a high-fidelity analytics engine for OpenClaw that transforms raw session logs into professional, actionable visual reports. It prioritizes **token usage patterns** and **model efficiency** over simple cost tracking.

## ✨ Key Features

- 📊 **High-Res Visual Reporting** - Generates horizontal PPT-style cards with 30-day SVG trend lines and multi-dimensional charts.
- ⚡ **Token-First Analytics** - Deep dive into input/output tokens, including Anthropic prompt caching (read/write) performance.
- 📉 **Efficiency Metrics** - Automatically calculates cost-per-million-tokens and cache savings to optimize your model selection.
- 🔄 **Zero-Config Sync** - Auto-detects OpenClaw session logs and syncs them into a local SQLite database for fast, idempotent querying.
- 🔔 **Intelligent Alerting** - Threshold-based monitoring for daily/weekly/monthly usage with flexible notification formats.
- 🎨 **Beautiful Console Output** - Provides clean, emoji-rich text summaries for quick checks.

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/VintLin/usage-visualizer.git
cd usage-visualizer

# Install dependencies
pip install -r requirements.txt

# Initial full sync of historical logs
python3 scripts/fetch_usage.py --full

# Generate your first visual report (Today)
python3 scripts/generate_report_image.py --today
```

## 📈 Usage Guide

### Visual Reports (Recommended one-step flow)
The visualizer should sync logs first, then generate the report image.

```bash
# Today image report (sync + render)
python3 scripts/run_usage_report.py --mode image --period today

# Weekly image report (sync + render)
python3 scripts/run_usage_report.py --mode image --period week

# Monthly image report (sync + render)
python3 scripts/run_usage_report.py --mode image --period month
```

Manual split flow (legacy):

```bash
python3 scripts/fetch_usage.py
python3 scripts/generate_report_image.py --today
```

### Text Summaries
For a lightweight summary in the console:

```bash
# Current day summary (sync + text)
python3 scripts/run_usage_report.py --mode text --period today

# Direct report (without auto sync)
python3 scripts/report.py --period today --text

# Detailed JSON output for integrations
python3 scripts/report.py --json
```

### Budget & Usage Guards
Set limits to receive alerts when usage spikes.

```bash
# Alert if daily usage exceeds $10
python3 scripts/alert.py --budget-usd 10 --period today
```

## 🛠 Project Structure

```
usage-visualizer/
├── assets/                     # Sample reports and UI assets
├── config/                     # Configuration templates
├── scripts/
│   ├── fetch_usage.py          # Log parser and SQLite sync engine
│   ├── calc_cost.py            # Model pricing and savings logic
│   ├── store.py                # Database interface
│   ├── report.py               # Text/JSON reporting
│   ├── html_report.py          # HTML/SVG template engine
│   ├── generate_report_image.py # PNG renderer (headless browser)
│   └── alert.py                # Monitoring and alert logic
├── SKILL.md                    # Skill definition
└── README.md                   # Full documentation
```

## 🧠 How It Works

1. **Extraction**: Periodically scans `~/.openclaw/agents/*/sessions/*.jsonl` for new messages.
2. **Standardization**: Maps varied provider metadata into a unified schema (tokens, cache hits, cost).
3. **Persistence**: Stores normalized data in a local SQLite DB, ensuring syncs are idempotent.
4. **Rendering**: Uses a local HTML template to render SVG charts and charts, then captures a high-res PNG using a headless renderer.

## 📝 Troubleshooting

- **Image Rendering Fails**: Ensure `html2image` and a compatible browser (Chrome/Chromium) are installed. On Linux servers, ensure `Xvfb` or a headless environment is available.
- **Missing Logs**: Verify that your `OPENCLAW_WORKSPACE` environment variable is correctly set if you are running in a custom directory.
- **Python Errors**: Ensure Python 3.8+ and all packages in `requirements.txt` are installed.

## 📄 License
MIT
