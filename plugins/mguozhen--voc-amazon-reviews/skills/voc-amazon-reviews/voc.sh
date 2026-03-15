#!/usr/bin/env bash
# VOC AI - Amazon 评论智能分析工具
# Usage: voc.sh <ASIN> [--limit N] [--market amazon.com] [--output file.md]

set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_banner() {
  echo -e "${BLUE}"
  echo "  ██╗   ██╗ ██████╗  ██████╗      █████╗ ██╗"
  echo "  ██║   ██║██╔═══██╗██╔════╝     ██╔══██╗██║"
  echo "  ██║   ██║██║   ██║██║          ███████║██║"
  echo "  ╚██╗ ██╔╝██║   ██║██║          ██╔══██║██║"
  echo "   ╚████╔╝ ╚██████╔╝╚██████╗     ██║  ██║██║"
  echo "    ╚═══╝   ╚═════╝  ╚═════╝     ╚═╝  ╚═╝╚═╝"
  echo -e "${NC}"
  echo "  Amazon 评论智能分析 | Amazon Review Intelligence"
  echo "  ─────────────────────────────────────────────"
  echo ""
}

usage() {
  echo "Usage: voc.sh <ASIN> [options]"
  echo ""
  echo "Options:"
  echo "  --limit N          抓取评论数量 (默认: 100)"
  echo "  --market DOMAIN    亚马逊市场 (默认: amazon.com)"
  echo "  --output FILE      保存报告到文件"
  echo "  --help             显示帮助"
  echo ""
  echo "Examples:"
  echo "  voc.sh B08N5WRWNW"
  echo "  voc.sh B08N5WRWNW --limit 200 --output report.md"
  echo "  voc.sh B08N5WRWNW --market amazon.co.uk"
  exit 0
}

# 解析参数
ASIN=""
LIMIT=100
MARKET="amazon.com"
OUTPUT_FILE=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --help|-h) usage ;;
    --limit) LIMIT="$2"; shift 2 ;;
    --market) MARKET="$2"; shift 2 ;;
    --output) OUTPUT_FILE="$2"; shift 2 ;;
    -*) echo "未知参数: $1" >&2; usage ;;
    *) ASIN="$1"; shift ;;
  esac
done

if [[ -z "$ASIN" ]]; then
  echo -e "${RED}❌ 请提供 ASIN${NC}" >&2
  usage
fi

# 验证 ASIN 格式（10位字母数字）
if ! echo "$ASIN" | grep -qE '^[A-Z0-9]{10}$'; then
  echo -e "${YELLOW}⚠️  ASIN 格式可能不正确（应为10位字母数字，如 B08N5WRWNW）${NC}" >&2
fi

# 检查前置依赖
check_deps() {
  local missing=()

  if ! command -v browse &>/dev/null; then
    missing+=("browse CLI (运行: npx skills add browserbase/skills@browser)")
  fi

  if ! command -v python3 &>/dev/null; then
    missing+=("python3")
  fi

  if ! command -v openclaw &>/dev/null; then
    missing+=("openclaw CLI")
  fi

  if [[ ${#missing[@]} -gt 0 ]]; then
    echo -e "${RED}❌ 缺少以下依赖:${NC}" >&2
    for dep in "${missing[@]}"; do
      echo "   • $dep" >&2
    done
    exit 1
  fi
}

print_banner
check_deps

echo -e "${GREEN}▶ 开始分析 ASIN: ${YELLOW}$ASIN${NC}"
echo -e "  市场: $MARKET | 目标评论数: $LIMIT"
echo ""

# 步骤1: 抓取评论
TEMP_REVIEWS=$(mktemp /tmp/voc_reviews_XXXXXX.json)
trap "rm -f $TEMP_REVIEWS" EXIT

echo -e "${BLUE}[1/2] 抓取评论数据...${NC}"
bash "$SKILL_DIR/scraper.sh" "$ASIN" \
  --limit "$LIMIT" \
  --market "$MARKET" \
  --output "$TEMP_REVIEWS"

# 检查是否获取到数据
REVIEW_COUNT=$(python3 -c "import json; data=json.load(open('$TEMP_REVIEWS')); print(len(data))" 2>/dev/null || echo "0")

if [[ "$REVIEW_COUNT" -eq 0 ]]; then
  echo -e "${RED}❌ 未获取到评论数据，请检查:${NC}" >&2
  echo "   • ASIN 是否正确" >&2
  echo "   • Amazon 是否弹出验证码/登录墙（建议配置 Browserbase remote）" >&2
  exit 1
fi

echo -e "${GREEN}✓ 成功获取 $REVIEW_COUNT 条评论${NC}"
echo ""

# 步骤2: AI 分析
echo -e "${BLUE}[2/2] AI 深度分析中...${NC}"

if [[ -n "$OUTPUT_FILE" ]]; then
  bash "$SKILL_DIR/analyze.sh" "$TEMP_REVIEWS" "$ASIN" --output "$OUTPUT_FILE"
else
  bash "$SKILL_DIR/analyze.sh" "$TEMP_REVIEWS" "$ASIN"
fi

echo ""
echo -e "${GREEN}✅ 分析完成！${NC}"
