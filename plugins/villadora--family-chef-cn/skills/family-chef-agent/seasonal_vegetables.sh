#!/bin/bash

# 季节食材脚本
# 输出当前季节的推荐食材

# 获取当前月份
MONTH=$(date +%-m)

# 根据月份判断季节 (使用数字)
get_season_num() {
  if [ $MONTH -ge 3 ] && [ $MONTH -le 5 ]; then
    echo "1"  # 春季
  elif [ $MONTH -ge 6 ] && [ $MONTH -le 8 ]; then
    echo "2"  # 夏季
  elif [ $MONTH -ge 9 ] && [ $MONTH -le 11 ]; then
    echo "3"  # 秋季
  else
    echo "4"  # 冬季
  fi
}

SEASON_NUM=$(get_season_num)

# 输出 JSON 格式
output_json() {
  echo "{"
  echo "  \"season_number\": $SEASON_NUM,"

  case $SEASON_NUM in
    1)  echo "  \"season\": \"春季\"," ;;
    2)  echo "  \"season\": \"夏季\"," ;;
    3)  echo "  \"season\": \"秋季\"," ;;
    4)  echo "  \"season\": \"冬季\"," ;;
  esac

  echo "  \"month\": $MONTH,"
  echo "  \"recommendations\": ["

  case $SEASON_NUM in
    1)
      echo "    \"菠菜\", \"春笋\", \"韭菜\", \"荠菜\", \"香椿\", \"豌豆苗\", \"蚕豆\""
      ;;
    2)
      echo "    \"西红柿\", \"黄瓜\", \"苦瓜\", \"茄子\", \"豆角\", \"冬瓜\", \"丝瓜\", \"空心菜\""
      ;;
    3)
      echo "    \"南瓜\", \"莲藕\", \"萝卜\", \"栗子\", \"山药\", \"菱角\", \"菊花\""
      ;;
    4)
      echo "    \"白菜\", \"土豆\", \"胡萝卜\", \"萝卜\", \"红薯\", \"大葱\", \"芥菜\""
      ;;
  esac

  echo "  ],"
  echo "  \"reason\": \"当季食材价格低、更新鲜、营养丰富\""
  echo "}"
}

# 输出人类可读格式
output_human() {
  case $SEASON_NUM in
    1)  SEASON_NAME="春季" ;;
    2)  SEASON_NAME="夏季" ;;
    3)  SEASON_NAME="秋季" ;;
    4)  SEASON_NAME="冬季" ;;
  esac

  echo "=== 当前季节: $SEASON_NAME (月份: $MONTH) ==="
  echo ""
  echo "推荐食材:"

  case $SEASON_NUM in
    1)
      echo "  ✓ 菠菜"
      echo "  ✓ 春笋"
      echo "  ✓ 韭菜"
      echo "  ✓ 荠菜"
      echo "  ✓ 香椿"
      echo "  ✓ 豌豆苗"
      echo "  ✓ 蚕豆"
      ;;
    2)
      echo "  ✓ 西红柿"
      echo "  ✓ 黄瓜"
      echo "  ✓ 苦瓜"
      echo "  ✓ 茄子"
      echo "  ✓ 豆角"
      echo "  ✓ 冬瓜"
      echo "  ✓ 丝瓜"
      echo "  ✓ 空心菜"
      ;;
    3)
      echo "  ✓ 南瓜"
      echo "  ✓ 莲藕"
      echo "  ✓ 萝卜"
      echo "  ✓ 栗子"
      echo "  ✓ 山药"
      echo "  ✓ 菱角"
      echo "  ✓ 菊花"
      ;;
    4)
      echo "  ✓ 白菜"
      echo "  ✓ 土豆"
      echo "  ✓ 胡萝卜"
      echo "  ✓ 萝卜"
      echo "  ✓ 红薯"
      echo "  ✓ 大葱"
      echo "  ✓ 芥菜"
      ;;
  esac

  echo ""
  echo "原因: 当季食材价格低、更新鲜、营养丰富"
}

# 主逻辑
if [ "$1" = "--json" ]; then
  output_json
else
  output_human
fi
