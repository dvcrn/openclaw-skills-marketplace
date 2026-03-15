#!/bin/bash
# 发布 Skill 到 ClawHub 并配置 SkillPay 收费

SKILL_NAME="xiaohongshu-auto-publish"
SKILL_PATH="/Users/xiaofang/.openclaw/workspace-taizi/skills/$SKILL_NAME"
PRICE="0.01"

echo "📦 发布 Skill: $SKILL_NAME"
echo "💰 设置价格：¥$PRICE"
echo ""

# 1. 打包 Skill
echo "📦 打包 Skill..."
cd "$SKILL_PATH"
zip -r ../${SKILL_NAME}.zip .
echo "   ✅ 打包完成：${SKILL_NAME}.zip"
echo ""

# 2. 创建 SkillPay 产品
echo "💳 创建 SkillPay 产品..."
curl -X POST https://skillpay.me/api/v1/products \
  -H "Authorization: Bearer sk_4eacbcc9e4411bd1490794b27867199f9801e3150b4c354541e6a2927931a06e" \
  -H "Content-Type: application/json" \
  -d "{
    \"name\": \"小红书自动发布技能\",
    \"description\": \"一键发布小红书笔记 - AI 文案 + 中国风封面 + 自动发布\",
    \"price\": $PRICE,
    \"currency\": \"CNY\",
    \"product_id\": \"xhs_auto_publish\"
  }" | python3 -m json.tool
echo ""

# 3. 发布到 ClawHub
echo "🚀 发布到 ClawHub..."
clawhub publish "$SKILL_PATH"
echo ""

# 4. 设置收费
echo "💰 设置 ClawHub 收费..."
clawhub set-price "$SKILL_NAME" --price $PRICE
echo ""

echo "✅ 发布完成！"
echo ""
echo "📊 信息汇总："
echo "   Skill 名称：$SKILL_NAME"
echo "   价格：¥$PRICE/次"
echo "   支付链接：https://skillpay.me/p/xhs_auto_publish"
echo ""
