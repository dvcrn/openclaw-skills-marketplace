#!/usr/bin/env bash
# Amazon 评论抓取脚本 - 基于 browse CLI (browser skill)
# 说明：本版本不依赖 Claude/Anthropic/OpenRouter key；页面解析由 OpenClaw 默认模型完成。
# Usage: scraper.sh <ASIN> [--limit N] [--market amazon.com] [--output out.json]

set -euo pipefail

ASIN="${1:-}"
LIMIT=100
MARKET="amazon.com"
OUTPUT_FILE=""

# 解析参数
shift || true
while [[ $# -gt 0 ]]; do
  case "$1" in
    --limit) LIMIT="$2"; shift 2 ;;
    --market) MARKET="$2"; shift 2 ;;
    --output) OUTPUT_FILE="$2"; shift 2 ;;
    *) shift ;;
  esac
done

if [[ -z "$ASIN" ]]; then
  echo "Usage: scraper.sh <ASIN> [--limit N] [--market amazon.com] [--output out.json]" >&2
  exit 1
fi

# deps
if ! command -v browse &>/dev/null; then
  echo "❌ 未找到 browse CLI，请先安装 browser skill:" >&2
  echo "   npx skills add browserbase/skills@browser" >&2
  exit 1
fi

if ! command -v openclaw &>/dev/null; then
  echo "❌ 未找到 openclaw CLI" >&2
  exit 1
fi

if ! command -v python3 &>/dev/null; then
  echo "❌ 未找到 python3" >&2
  exit 1
fi

PAGE=1
COLLECTED=0
MAX_PAGES=$(( (LIMIT + 9) / 10 ))  # 每页约 10 条（实际可能不同）

TMP_PAGES=$(mktemp /tmp/voc_pages_XXXXXX.jsonl)
trap 'rm -f "$TMP_PAGES"' EXIT

echo "🔍 开始抓取 ASIN: $ASIN (目标: $LIMIT 条)" >&2
echo "   市场: https://www.$MARKET" >&2

REVIEW_URL="https://www.${MARKET}/product-reviews/${ASIN}/ref=cm_cr_dp_d_show_all_btm?ie=UTF8&reviewerType=all_reviews&sortBy=recent"

browse open "$REVIEW_URL" 2>/dev/null || {
  echo "❌ 无法打开评论页面，请检查 ASIN 是否正确" >&2
  exit 1
}

sleep 3

# helper: call openclaw agent and return text
openclaw_text() {
  local prompt="$1"
  local session_id="$2"

  local resp
  resp=$(openclaw agent --local --session-id "$session_id" -m "$prompt" --json 2>/dev/null || true)

  echo "$resp" | python3 - <<'PY'
import json,sys
raw=sys.stdin.read().strip()
if not raw:
    print("")
    raise SystemExit
try:
    r=json.loads(raw)
    payloads=r.get('payloads') or []
    if payloads:
        print((payloads[0].get('text') or '').strip())
    else:
        print("")
except Exception:
    print("")
PY
}

# 逐页抓取
while [[ $PAGE -le $MAX_PAGES && $COLLECTED -lt $LIMIT ]]; do
  echo "   📄 正在抓取第 $PAGE 页..." >&2

  PAGE_TEXT=$(browse get text "body" 2>/dev/null || echo "")
  if [[ -z "$PAGE_TEXT" ]]; then
    echo "   ⚠️  第 $PAGE 页内容为空，停止抓取" >&2
    break
  fi

  if echo "$PAGE_TEXT" | grep -qi "robot\|captcha\|verify you are human\|automated access"; then
    echo "   ⚠️  检测到反爬/验证码。建议配置 Browserbase remote（否则可能抓不到评论）" >&2
    break
  fi

  PAGE_HTML=$(browse get html "#cm_cr-review_list" 2>/dev/null || echo "")
  if [[ -z "$PAGE_HTML" ]]; then
    echo "   ⚠️  未获取到评论区 HTML，尝试继续" >&2
  else
    # 控制输入长度
    HTML_SNIP=$(python3 - <<'PY'
import sys
html=sys.stdin.read()
print(html[:12000])
PY <<<"$PAGE_HTML")

    PROMPT=$(cat <<PROMPT
从下面亚马逊评论列表 HTML 片段中，提取所有评论，输出 JSON 数组。每条评论对象字段：
- rating: 1-5 整数
- title: string
- body: string
- date: string (如果能提取)
- verified: boolean (Verified Purchase)

严格要求：只输出 JSON 数组，不要任何额外文字。

HTML:\n${HTML_SNIP}
PROMPT
)

    SESSION_ID="voc-scrape-${ASIN}-${PAGE}-$(date +%s)"
    PAGE_REVIEWS=$(openclaw_text "$PROMPT" "$SESSION_ID")

    # 验证 JSON 数组
    if echo "$PAGE_REVIEWS" | python3 -c "import sys,json; data=json.load(sys.stdin); assert isinstance(data, list)" 2>/dev/null; then
      COUNT=$(echo "$PAGE_REVIEWS" | python3 -c "import sys,json; print(len(json.load(sys.stdin)))")
      echo "$PAGE_REVIEWS" >> "$TMP_PAGES"
      COLLECTED=$((COLLECTED + COUNT))
      echo "   ✓ 第 $PAGE 页获取 $COUNT 条评论（累计 $COLLECTED 条）" >&2
    else
      echo "   ⚠️  第 $PAGE 页解析失败（模型未返回 JSON），跳过" >&2
    fi
  fi

  PAGE=$((PAGE + 1))
  if [[ $PAGE -le $MAX_PAGES && $COLLECTED -lt $LIMIT ]]; then
    NEXT_CLICKED=$(browse click "li.a-last a" 2>/dev/null && echo "ok" || echo "fail")
    if [[ "$NEXT_CLICKED" == "fail" ]]; then
      # 备用选择器
      browse click "a[data-hook='pagination-bar-anchor']:last-child" 2>/dev/null || {
        echo "   ℹ️  已到最后一页" >&2
        break
      }
    fi
    sleep 2
  fi
done

browse stop 2>/dev/null || true

echo "📦 合并评论数据..." >&2

MERGED=$(cat "$TMP_PAGES" | python3 - <<'PY'
import json,sys
all_reviews=[]
for line in sys.stdin:
    line=line.strip()
    if not line:
        continue
    try:
        arr=json.loads(line)
        if isinstance(arr,list):
            all_reviews.extend(arr)
    except Exception:
        continue

# 去重：按 body 前120字符
seen=set(); unique=[]
for r in all_reviews:
    body=str(r.get('body',''))
    key=body[:120]
    if key in seen:
        continue
    seen.add(key)
    # 规范字段
    try:
        rating=int(r.get('rating')) if r.get('rating') is not None else None
    except:
        rating=None
    unique.append({
        'rating': rating,
        'title': (r.get('title') or '').strip(),
        'body': body.strip(),
        'date': (r.get('date') or '').strip(),
        'verified': bool(r.get('verified')),
    })

print(json.dumps(unique, ensure_ascii=False, indent=2))
PY)

TOTAL=$(echo "$MERGED" | python3 -c "import sys,json; print(len(json.load(sys.stdin)))" 2>/dev/null || echo "0")

echo "✅ 抓取完成，共获取 $TOTAL 条有效评论" >&2

if [[ -n "$OUTPUT_FILE" ]]; then
  echo "$MERGED" > "$OUTPUT_FILE"
  echo "💾 数据已保存到: $OUTPUT_FILE" >&2
else
  echo "$MERGED"
fi
