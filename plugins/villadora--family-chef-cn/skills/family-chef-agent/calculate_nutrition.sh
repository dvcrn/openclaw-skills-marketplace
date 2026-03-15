#!/bin/bash

# 营养计算脚本
# 基于内置数据库计算食材营养

# 营养数据库 (100g) - 格式: 名称,热量,蛋白质,脂肪
NUTRITION_DATA="
chicken_breast,165,31,3.6,鸡胸肉
chicken_leg,209,26,10.9,鸡腿肉
pork,143,27,3.0,猪肉
beef,250,26,15.0,牛肉
salmon,208,20,13.0,三文鱼
egg,70,6,5,鸡蛋
duck_egg,90,6,7,鸭蛋
tofu,76,8,4,豆腐
soy_milk,54,3,2,豆浆
rice,116,2,0.3,米饭
noodles,109,3,1,面条
steamed_bread,223,7,1,馒头
tomato,18,1,0.2,西红柿
cucumber,15,1,0.2,黄瓜
spinach,23,2,0.4,菠菜
cabbage,17,1,0.2,白菜
potato,77,2,0.1,土豆
carrot,41,1,0.2,胡萝卜
pumpkin,26,1,0.1,南瓜
radish,20,1,0.1,萝卜
"

# 查找营养数据
find_nutrition() {
  echo "$NUTRITION_DATA" | while IFS=',' read -r key cal pro fat cn; do
    if [ "$key" = "$1" ] || [ "$cn" = "$1" ]; then
      echo "$cal|$pro|$fat"
      return 0
    fi
  done
}

# 输出 JSON
output_json() {
  echo "{"
  echo "  \"ingredients\": ["

  local first=1
  local total_cal=0
  local total_pro=0
  local total_fat=0

  for item in "$@"; do
    local data=$(find_nutrition "$item")
    if [ -n "$data" ]; then
      local cal=$(echo "$data" | cut -d'|' -f1)
      local pro=$(echo "$data" | cut -d'|' -f2)
      local fat=$(echo "$data" | cut -d'|' -f3)

      total_cal=$(awk "BEGIN {print $total_cal + $cal}")
      total_pro=$(awk "BEGIN {print $total_pro + $pro}")
      total_fat=$(awk "BEGIN {print $total_fat + $fat}")

      if [ $first -eq 1 ]; then
        first=0
      else
        echo ","
      fi
      echo -n "    {\"name\": \"$item\", \"calories\": $cal, \"protein\": $pro, \"fat\": $fat}"
    else
      if [ $first -eq 1 ]; then
        first=0
      else
        echo ","
      fi
      echo -n "    {\"name\": \"$item\", \"calories\": 0, \"protein\": 0, \"fat\": 0, \"note\": \"未找到数据\"}"
    fi
  done

  echo ""
  echo "  ],"
  echo "  \"total\": {"
  echo "    \"calories\": $total_cal,"
  echo "    \"protein\": $total_pro,"
  echo "    \"fat\": $total_fat"
  echo "  },"
  echo "  \"daily_estimate\": {"
  echo "    \"calories\": $(awk "BEGIN {print $total_cal * 3}"),"
  echo "    \"protein\": $(awk "BEGIN {print $total_pro * 3}"),"
  echo "    \"fat\": $(awk "BEGIN {print $total_fat * 3}")"
  echo "  }"
  echo "}"
}

# 输出人类可读格式
output_human() {
  local total_cal=0
  local total_pro=0
  local total_fat=0

  echo "=== 营养计算结果 ==="
  echo ""

  for item in "$@"; do
    local data=$(find_nutrition "$item")
    if [ -n "$data" ]; then
      local cal=$(echo "$data" | cut -d'|' -f1)
      local pro=$(echo "$data" | cut -d'|' -f2)
      local fat=$(echo "$data" | cut -d'|' -f3)

      total_cal=$(awk "BEGIN {print $total_cal + $cal}")
      total_pro=$(awk "BEGIN {print $total_pro + $pro}")
      total_fat=$(awk "BEGIN {print $total_fat + $fat}")

      echo "$item (100g):"
      echo "  热量: ${cal}kcal"
      echo "  蛋白质: ${pro}g"
      echo "  脂肪: ${fat}g"
      echo ""
    else
      echo "$item: 未找到营养数据"
    fi
  done

  echo "=== 总计 (100g each) ==="
  echo "热量: ${total_cal}kcal"
  echo "蛋白质: ${total_pro}g"
  echo "脂肪: ${total_fat}g"
  echo ""
  echo "=== 每日估算 (三餐) ==="
  echo "热量: $(awk "BEGIN {print $total_cal * 3}")kcal"
  echo "蛋白质: $(awk "BEGIN {print $total_pro * 3}")g"
  echo "脂肪: $(awk "BEGIN {print $total_fat * 3}")g"
}

# 主逻辑
if [ $# -eq 0 ]; then
  echo "用法: $0 <食材1> <食材2> ..."
  echo ""
  echo "示例: $0 鸡胸肉 西红柿 鸡蛋"
  echo ""
  echo "可用食材: 鸡胸肉, 鸡腿肉, 猪肉, 牛肉, 三文鱼, 鸡蛋, 鸭蛋, 豆腐, 豆浆, 米饭, 面条, 馒头, 西红柿, 黄瓜, 菠菜, 白菜, 土豆, 胡萝卜, 南瓜, 萝卜"
  exit 0
fi

# 判断输出格式
if [ "$1" = "--json" ]; then
  shift
  output_json "$@"
else
  output_human "$@"
fi
