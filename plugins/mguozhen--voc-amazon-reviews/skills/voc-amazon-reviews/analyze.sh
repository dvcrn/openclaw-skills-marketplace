#!/usr/bin/env bash
# Amazon 评论分析脚本 - 使用 OpenClaw 默认模型
# Usage: analyze.sh <reviews_json_file> <ASIN> [--output file.md]

set -euo pipefail

REVIEWS_FILE="${1:-}"
ASIN="${2:-unknown}"
OUTPUT_FILE=""

shift 2 || true
while [[ $# -gt 0 ]]; do
  case "$1" in
    --output) OUTPUT_FILE="$2"; shift 2 ;;
    *) shift ;;
  esac
done

if [[ -z "$REVIEWS_FILE" || ! -f "$REVIEWS_FILE" ]]; then
  echo "❌ 需要提供评论数据文件" >&2
  echo "Usage: analyze.sh <reviews_json_file> <ASIN> [--output file.md]" >&2
  exit 1
fi

if ! command -v openclaw &>/dev/null; then
  echo "openclaw not found. Please install OpenClaw first." >&2
  exit 1
fi

VOC_MODEL=$(openclaw models status --plain 2>/dev/null || echo "unknown")
echo "Analyzing reviews with model: $VOC_MODEL ..." >&2

# 读取评论数据
REVIEWS_JSON=$(cat "$REVIEWS_FILE")
TOTAL=$(echo "$REVIEWS_JSON" | python3 -c "import sys,json; print(len(json.load(sys.stdin)))" 2>/dev/null || echo "0")
TODAY=$(date +%Y-%m-%d)

# 构建分析 Prompt
PROMPT=$(cat <<PROMPT
你是一位专业的亚马逊电商分析师，请对以下评论数据进行深度 VOC（Voice of Customer）分析。

## 分析任务

评论数量：${TOTAL} 条
ASIN：${ASIN}

## 评论数据
\`\`\`json
$(echo "$REVIEWS_JSON" | python3 -c "
import sys, json
reviews = json.load(sys.stdin)
# 截取最多150条，避免超出token限制
sample = reviews[:150]
# 精简字段
simplified = [{'rating': r.get('rating'), 'title': r.get('title',''), 'body': str(r.get('body',''))[:500], 'verified': r.get('verified', False)} for r in sample]
print(json.dumps(simplified, ensure_ascii=False))
" 2>/dev/null || echo "$REVIEWS_JSON" | head -c 15000)
\`\`\`

## 输出格式要求

请严格按以下格式输出，中英文双语，不要添加额外说明：

---
SENTIMENT_POSITIVE: [正面评论数量占比，如 74]
SENTIMENT_NEUTRAL: [中性评论数量占比，如 16]
SENTIMENT_NEGATIVE: [负面评论数量占比，如 10]
---
PAIN_POINT_1_ZH: [痛点1中文描述，15字以内]
PAIN_POINT_1_EN: [Pain point 1 in English, under 15 words]
PAIN_POINT_1_COUNT: [提及次数]
PAIN_POINT_1_QUOTE_ZH: [最典型的中文用户原话或翻译，30字以内]
PAIN_POINT_1_QUOTE_EN: [Most representative English user quote, under 30 words]
PAIN_POINT_2_ZH: ...
PAIN_POINT_2_EN: ...
PAIN_POINT_2_COUNT: ...
PAIN_POINT_2_QUOTE_ZH: ...
PAIN_POINT_2_QUOTE_EN: ...
PAIN_POINT_3_ZH: ...
PAIN_POINT_3_EN: ...
PAIN_POINT_3_COUNT: ...
PAIN_POINT_3_QUOTE_ZH: ...
PAIN_POINT_3_QUOTE_EN: ...
PAIN_POINT_4_ZH: ...
PAIN_POINT_4_EN: ...
PAIN_POINT_4_COUNT: ...
PAIN_POINT_4_QUOTE_ZH: ...
PAIN_POINT_4_QUOTE_EN: ...
PAIN_POINT_5_ZH: ...
PAIN_POINT_5_EN: ...
PAIN_POINT_5_COUNT: ...
PAIN_POINT_5_QUOTE_ZH: ...
PAIN_POINT_5_QUOTE_EN: ...
---
SELLING_POINT_1_ZH: [卖点1中文描述，15字以内]
SELLING_POINT_1_EN: [Selling point 1 in English, under 15 words]
SELLING_POINT_1_COUNT: [提及次数]
SELLING_POINT_1_QUOTE_ZH: [最典型的中文用户原话或翻译，30字以内]
SELLING_POINT_1_QUOTE_EN: [Most representative English user quote, under 30 words]
SELLING_POINT_2_ZH: ...
SELLING_POINT_2_EN: ...
SELLING_POINT_2_COUNT: ...
SELLING_POINT_2_QUOTE_ZH: ...
SELLING_POINT_2_QUOTE_EN: ...
SELLING_POINT_3_ZH: ...
SELLING_POINT_3_EN: ...
SELLING_POINT_3_COUNT: ...
SELLING_POINT_3_QUOTE_ZH: ...
SELLING_POINT_3_QUOTE_EN: ...
SELLING_POINT_4_ZH: ...
SELLING_POINT_4_EN: ...
SELLING_POINT_4_COUNT: ...
SELLING_POINT_4_QUOTE_ZH: ...
SELLING_POINT_4_QUOTE_EN: ...
SELLING_POINT_5_ZH: ...
SELLING_POINT_5_EN: ...
SELLING_POINT_5_COUNT: ...
SELLING_POINT_5_QUOTE_ZH: ...
SELLING_POINT_5_QUOTE_EN: ...
---
TIP_1_ZH: [Listing 优化建议1，中文，50字以内]
TIP_1_EN: [Listing optimization tip 1, English, under 50 words]
TIP_2_ZH: ...
TIP_2_EN: ...
TIP_3_ZH: ...
TIP_3_EN: ...
---
SUMMARY_ZH: [整体一句话总结，30字以内]
SUMMARY_EN: [One-sentence overall summary in English, under 30 words]
PROMPT
)

# 调用 OpenClaw 默认模型
SESSION_ID="voc-$(date +%s)"
RESPONSE=$(openclaw agent --local --session-id "$SESSION_ID" -m "$PROMPT" --json 2>/dev/null)

ANALYSIS=$(echo "$RESPONSE" | python3 -c "
import sys, json
r = json.load(sys.stdin)
payloads = r.get('payloads', [])
if payloads:
    print(payloads[0].get('text', ''))
else:
    print('ERROR: empty response')
" 2>/dev/null)

if [[ -z "$ANALYSIS" ]] || echo "$ANALYSIS" | grep -q "^ERROR:"; then
  echo "❌ OpenClaw 调用失败: $ANALYSIS" >&2
  exit 1
fi

# 解析结构化输出，渲染为漂亮报告
REPORT=$(python3 - <<PYEOF
import re, sys

raw = """$ANALYSIS"""

def get(key):
    m = re.search(rf'^{key}:\s*(.+)$', raw, re.MULTILINE)
    return m.group(1).strip() if m else '—'

def bar(pct):
    try:
        n = int(pct)
        filled = round(n / 5)
        return '█' * filled + '░' * (20 - filled)
    except:
        return '░' * 20

pos = get('SENTIMENT_POSITIVE')
neu = get('SENTIMENT_NEUTRAL')
neg = get('SENTIMENT_NEGATIVE')

report = f"""
╔══════════════════════════════════════════════════════════════╗
║          VOC AI 分析报告 / VOC AI Analysis Report           ║
║  ASIN: $ASIN  |  analyzed: $TOTAL reviews                   ║
║  Market: amazon.com  |  Generated: $TODAY                   ║
╚══════════════════════════════════════════════════════════════╝

📊 情感分布 / Sentiment Distribution
─────────────────────────────────────────
  正面 Positive  {bar(pos)}  {pos}%
  中性 Neutral   {bar(neu)}  {neu}%
  负面 Negative  {bar(neg)}  {neg}%

🔴 Top 5 痛点 / Pain Points
═══════════════════════════════════════════════════════════════
"""

for i in range(1, 6):
    zh = get(f'PAIN_POINT_{i}_ZH')
    en = get(f'PAIN_POINT_{i}_EN')
    cnt = get(f'PAIN_POINT_{i}_COUNT')
    qzh = get(f'PAIN_POINT_{i}_QUOTE_ZH')
    qen = get(f'PAIN_POINT_{i}_QUOTE_EN')
    if zh == '—':
        break
    report += f"""{i}. {zh} / {en}（{cnt} 条提及）
   「{qzh}」
   "{qen}"

"""

report += """🟢 Top 5 卖点 / Selling Points
═══════════════════════════════════════════════════════════════
"""

for i in range(1, 6):
    zh = get(f'SELLING_POINT_{i}_ZH')
    en = get(f'SELLING_POINT_{i}_EN')
    cnt = get(f'SELLING_POINT_{i}_COUNT')
    qzh = get(f'SELLING_POINT_{i}_QUOTE_ZH')
    qen = get(f'SELLING_POINT_{i}_QUOTE_EN')
    if zh == '—':
        break
    report += f"""{i}. {zh} / {en}（{cnt} 条提及）
   「{qzh}」
   "{qen}"

"""

report += """💡 Listing 优化建议 / Optimization Suggestions
═══════════════════════════════════════════════════════════════
"""

for i in range(1, 4):
    zh = get(f'TIP_{i}_ZH')
    en = get(f'TIP_{i}_EN')
    if zh == '—':
        break
    report += f"""{i}. {zh}
   {en}

"""

summary_zh = get('SUMMARY_ZH')
summary_en = get('SUMMARY_EN')
report += f"""📌 总结 / Summary
─────────────────────────────────────────
  {summary_zh}
  {summary_en}

══════════════════════════════════════════════════════════════
  由 VOC AI Skill 生成 | Generated by VOC AI Skill
  https://github.com/your-org/voc-amazon-reviews
══════════════════════════════════════════════════════════════
"""

print(report)
PYEOF
)

echo "$REPORT"

if [[ -n "$OUTPUT_FILE" ]]; then
  echo "$REPORT" > "$OUTPUT_FILE"
  echo "" >&2
  echo "💾 报告已保存到: $OUTPUT_FILE" >&2
fi
