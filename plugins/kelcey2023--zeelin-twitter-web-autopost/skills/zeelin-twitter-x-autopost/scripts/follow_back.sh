#!/bin/bash
# follow_back.sh — 在粉丝列表中点「关注」回关（只点 Follow/关注/回关，不点 Following/已关注）
# Usage: bash follow_back.sh [username] [base_url] [max_count]
# Example: bash follow_back.sh Gsdata5566 https://x.com 10

USER="${1:-Gsdata5566}"
BASE_URL="${2:-https://x.com}"
MAX="${3:-10}"
CLI="openclaw browser"

echo "============================================"
echo "  Twitter/X 回关"
echo "============================================"
echo "账号: $USER | 最多回关: $MAX"
echo ""

echo "=== 打开粉丝列表 ==="
$CLI open "${BASE_URL}/${USER}/followers" 2>/dev/null
sleep 8

echo "=== 处理「关注者」列表 ==="
$CLI press "PageDown" 2>/dev/null || true
sleep 2
$CLI press "PageDown" 2>/dev/null || true
sleep 2

do_follow_back() {
  local SNAP REF
  SNAP=$($CLI snapshot 2>/dev/null)
  REF=$(echo "$SNAP" | grep -E 'button.*"回关|button.*"Follow"|button.*"关注"' | grep -v 'Following\|已关注' | grep -oE 'ref=e[0-9]+' | head -1 | sed 's/ref=//')
  if [ -z "$REF" ]; then
    REF=$(echo "$SNAP" | grep -E 'Follow|关注|回关' | grep -v 'Following|已关注' | grep -oE 'ref=e[0-9]+' | head -1 | sed 's/ref=//')
  fi
  if [ -z "$REF" ]; then
    REF=$(echo "$SNAP" | grep -B1 -E ': Follow$|: 关注$|: 回关$|"Follow"|"关注"|"回关"' | grep -v 'Following|已关注' | grep -oE 'ref=e[0-9]+' | head -1 | sed 's/ref=//')
  fi
  if [ -z "$REF" ]; then
    REF=$(echo "$SNAP" | grep -B2 -E 'Follow|关注|回关' | grep -v 'Following|已关注' | grep -oE 'ref=e[0-9]+' | tail -1 | sed 's/ref=//')
  fi
  if [ -z "$REF" ]; then
    REF=$(echo "$SNAP" | grep -E 'cursor=pointer.*(Follow|回关)|(Follow|回关).*cursor=pointer' | grep -v Following | grep -oE 'ref=e[0-9]+' | head -1 | sed 's/ref=//')
  fi
  echo "$REF"
}

CLICKED=0
for i in $(seq 1 "$MAX"); do
  REF=$(do_follow_back)
  if [ -z "$REF" ]; then
    if [ $CLICKED -eq 0 ]; then
      SNAP=$($CLI snapshot 2>/dev/null)
      echo "  未找到 Follow/关注/回关 按钮。页面片段（供排查）："
      echo "$SNAP" | grep -iE "follow|关注|回关|button" | head -20
    fi
    break
  fi
  echo "  点击回关 ($((CLICKED+1))/$MAX) ref=$REF"
  $CLI click "$REF" 2>/dev/null
  CLICKED=$((CLICKED+1))
  sleep 2
done

SNAP0=$($CLI snapshot 2>/dev/null)
if [ $CLICKED -lt $MAX ] && echo "$SNAP0" | grep -q 'tab.*认证关注者'; then
  TAB_REF=$(echo "$SNAP0" | grep 'tab.*认证关注者' | grep -oE 'ref=e[0-9]+' | head -1 | sed 's/ref=//')
  if [ -n "$TAB_REF" ]; then
    echo "  切换到「认证关注者」标签，继续回关"
    $CLI click "$TAB_REF" 2>/dev/null
    sleep 4
    $CLI press "PageDown" 2>/dev/null || true
    sleep 2
    $CLI press "PageDown" 2>/dev/null || true
    sleep 2
    while [ $CLICKED -lt $MAX ]; do
      REF=$(do_follow_back)
      if [ -z "$REF" ]; then
        echo "  认证关注者列表中无更多可回关。"
        break
      fi
      echo "  点击回关 ($((CLICKED+1))/$MAX) ref=$REF"
      $CLI click "$REF" 2>/dev/null
      CLICKED=$((CLICKED+1))
      sleep 2
    done
  fi
fi

if [ $CLICKED -eq 0 ]; then
  echo "  没有更多可回关的按钮，或页面结构变化。"
fi

echo ""
echo "=== 完成 ==="
echo "本次回关 $CLICKED 人。"
