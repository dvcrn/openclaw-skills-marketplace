#!/bin/bash
# 快速完成剩余配置

echo "======================================"
echo "📱 小红书自动发布 Skill - 快速配置"
echo "======================================"
echo ""

# 1. ClawHub 登录
echo "📋 步骤 1: ClawHub 登录"
echo "   请打开浏览器访问："
echo "   https://clawhub.ai/cli/auth"
echo ""
echo "   扫码确认后按回车继续..."
read -p ""

# 2. 发布到 ClawHub
echo ""
echo "📦 步骤 2: 发布到 ClawHub"
cd /Users/xiaofang/.openclaw/workspace-taizi/skills/xiaohongshu-auto-publish
clawhub publish .

# 3. SkillPay 产品创建
echo ""
echo "💳 步骤 3: SkillPay 产品创建"
echo "   请访问："
echo "   https://skillpay.me/dashboard/products"
echo ""
echo "   创建产品："
echo "   - 名称：小红书自动发布技能"
echo "   - 价格：¥0.01"
echo "   - 产品 ID: xhs_auto_publish"
echo ""

# 4. 设置收费
echo ""
echo "💰 步骤 4: 设置 ClawHub 收费"
clawhub set-price xiaohongshu-auto-publish --price 0.01

echo ""
echo "======================================"
echo "✅ 配置完成！"
echo "======================================"
echo ""
echo "📊 信息汇总："
echo "   Skill 名称：xiaohongshu-auto-publish"
echo "   价格：¥0.01/次"
echo "   支付链接：https://skillpay.me/p/xhs_auto_publish"
echo ""
