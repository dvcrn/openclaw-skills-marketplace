---
name: douyin-report-search
description: "This skill automates end-to-end Douyin topic research and report generation. Given a search keyword and a target video count, it handles QR-code login, batch video collection via API interception, automatic CAPTCHA solving (slide-puzzle), detail page enrichment (likes, shares, collects, comments, followers), multi-factor engagement analysis, and final interactive HTML report generation. This skill should be used when the user wants to research Douyin content trends, analyze what makes videos go viral, or generate a data-driven report for any topic keyword."
---

# Douyin Topic Research & Report Skill

## Purpose

Automate the full pipeline: **keyword → data collection → CAPTCHA bypass → enrichment → analysis → HTML report**, replicating a proven workflow that successfully collected and analyzed 100 videos on the topic "女性成长".

## Applicable Scenarios

- "帮我分析抖音上 [关键词] 的视频，哪些因素让视频更多点赞转发"
- "采集抖音 [话题] 最近 N 条视频数据，生成分析报告"
- "我想研究抖音某类内容的爆款规律"
- "给我一份抖音 [关键词] 的可视化数据报告"

## Default Parameters

| Parameter | Default | Notes |
|-----------|---------|-------|
| `KEYWORD` | `女性成长` | Search keyword (URL-encoded automatically) |
| `TOTAL` | `100` | Total videos to collect |
| `DETAIL_LIMIT` | `50` | Max videos to visit detail pages |
| `COMMENTS_TOP` | `5` | Top comments per video |

## Full Pipeline (5 Steps)

### Step 1 — Environment Setup

```bash
cd <work_dir>
python3 -m venv venv && source venv/bin/activate
pip install playwright pillow numpy scipy scikit-image openpyxl
playwright install chromium
```

### Step 2 — Login & Save Session

Run `scripts/douyin_login.py` (or adapt inline). The script:
1. Launches Chromium (headless=False)
2. Navigates to `https://www.douyin.com`
3. Waits for user to scan QR code (polls `document.cookie` until login detected)
4. Saves cookies to `douyin_session.json`

**Key anti-detection settings** (always apply):
```python
args=["--disable-blink-features=AutomationControlled", "--no-sandbox",
      "--window-size=1440,900"]
# Init script:
"Object.defineProperty(navigator,'webdriver',{get:()=>undefined});"
```

### Step 3 — Batch Video Collection

See `scripts/collect_videos.py`. Core logic:
- Intercept `search/item` API response (`aweme_list` field contains video data)
- Navigate to `https://www.douyin.com/search/{keyword}?type=video`
- For batch 2+: scroll down 8× with `window.scrollBy(0, 600)` then wait 4s
- Extract fields: `aweme_id`, `desc` (title), `statistics` (likes/shares/collects/comments), `author.uid`, `author.nickname`, `author.follower_count`, `video.duration`, `text_extra` (tags)

### Step 4 — Detail Enrichment + CAPTCHA Solving

See `scripts/parse_videos.py` and `scripts/captcha_solver.py`.

#### CAPTCHA Solving Algorithm (proven, use exactly)

The algorithm is embedded in `scripts/captcha_solver.py`. Key findings from empirical testing:

1. **Template matching is the primary method** (most accurate, directly gives left edge of gap)
2. **Sobel edge detection is secondary** (detects right edge of gap → left peak of dual-peak = left edge)
3. **Decision**: if diff ≤ 25px → weighted average (70% template + 30% Sobel); else → use template only

```python
# Element selectors (抖音 captcha iframe)
captcha_frame selector: frame.url contains "verifycenter" or "captcha"
bg_el  = frame.locator(".captcha-verify-image").first
sl_el  = frame.locator(".captcha-verify-image-slide").first
btn_el = frame.locator(".captcha-slider-btn").first

# Slide distance formula
gap_center_abs = bg_bb["x"] + gap_x + sl_bb["width"] / 2
btn_center_abs = btn_bb["x"] + btn_bb["width"] / 2
slide_distance = gap_center_abs - btn_center_abs
```

#### Human-like Slide Path (ease-out + overshoot)

```python
def ease_out_cubic(t): return 1 - (1 - t) ** 3

# overshoot 3-7px, then pull back in final 15% of path
# Y-axis jitter ±2px, X-axis jitter ±1px during 5%-80%
# Timing: fast phase (frac<0.5) 5-8ms, mid 10-18ms, slow 25-45ms
```

#### Refresh captcha between retries

```python
rb = frame.locator(".vc-captcha-refresh,.captcha-refresh,[class*='refresh']").first
```

### Step 5 — Analysis & Report Generation

See `scripts/analyze_factors.py` and `scripts/generate_report.py`.

**Analysis dimensions** (all proven to have measurable effect):

| Dimension | Key Finding |
|-----------|-------------|
| Duration | 2-3 min is sweet spot (15× better than >5 min) |
| Tag count | 1-2 tags >> 5+ tags (up to 6× difference) |
| Best tags | #自我成长 #个人成长 #认知 #女生必看 |
| Follower (log-corr) | r=0.617, moderate positive |
| Title with `！` | +2× likes vs no exclamation |
| Title length | 11-20 chars optimal |
| Emotion keywords | Love/marriage/mood words → higher shares |

Report output: `douyin_analysis_report.html` with 10 interactive Chart.js charts.

## File Structure

```
work_dir/
├── douyin_session.json      # saved login cookies
├── douyin_raw_data.json     # raw collected videos
├── douyin_parsed.json       # enriched with detail data
├── analysis_result.json     # computed analysis metrics
├── douyin_report.xlsx       # Excel version
└── douyin_analysis_report.html  # final interactive HTML report
```

## Critical Notes

- **headless=False** is required for CAPTCHA solving (screenshot-based)
- Always mask the slider overlay in the background image before edge detection:
  `bg_arr[:mask_h, :mask_w] = column_mean_fill`
- `search_start = sl_w + 12` to skip the initial slider position area
- Max retries for captcha: 5 attempts with captcha refresh between each
- After captcha success, wait 3s before continuing
- The `douyin_session.json` expires; re-login if 401/redirect to login page

## Dependencies

```
playwright, pillow, numpy, scipy, scikit-image, openpyxl
```
