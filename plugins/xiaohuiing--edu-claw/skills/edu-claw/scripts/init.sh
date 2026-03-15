#!/bin/bash

# 小英老师 Skill 初始化脚本

echo "🎓 小英老师 - 初始化配置"
echo ""

SKILL_DIR="$(cd "$(dirname "$0")" && pwd)"
CONFIG_FILE="$SKILL_DIR/config.json"
TEMPLATE_FILE="$SKILL_DIR/config.template.json"

# 检查是否已有配置
if [ -f "$CONFIG_FILE" ]; then
    echo "⚠️ 检测到已有配置，是否重新设置？(y/n)"
    read -r reset
    if [ "$reset" != "y" ]; then
        echo "保留现有配置，退出。"
        exit 0
    fi
fi

# 从模板复制
cp "$TEMPLATE_FILE" "$CONFIG_FILE"

echo "请设置以下信息："
echo ""

# 收集信息
read -p "孩子姓名: " child_name
read -p "年级（如：三年级）: " grade
read -p "性别（男/女）: " gender
read -p "性格特点（如：活泼/内向）: " personality
read -p "学习目标: " learning_goal

echo ""
echo "🎭 博主理念对齐（可选）"
echo "如果你有喜欢的抖音教育博主，可以用豆包提取其教育理念"
echo "然后将文字粘贴在这里（直接回车跳过）:"
read -p "" blogger_philosophy

# 更新配置文件
sed -i "s/\"child_name\": \"\"/\"child_name\": \"$child_name\"/" "$CONFIG_FILE"
sed -i "s/\"grade\": \"\"/\"grade\": \"$grade\"/" "$CONFIG_FILE"
sed -i "s/\"gender\": \"\"/\"gender\": \"$gender\"/" "$CONFIG_FILE"
sed -i "s/\"personality\": \"\"/\"personality\": \"$personality\"/" "$CONFIG_FILE"
sed -i "s/\"learning_goal\": \"\"/\"learning_goal\": \"$learning_goal\"/" "$CONFIG_FILE"

# 如果有博主理念，保存到文件
if [ -n "$blogger_philosophy" ]; then
    echo "$blogger_philosophy" > "$SKILL_DIR/references/blogger_philosophy.txt"
    echo "✅ 博主理念已保存"
fi

echo ""
echo "✅ 配置完成！"
echo ""
echo "📋 配置信息："
echo "   孩子: $child_name"
echo "   年级: $grade"
echo "   目标: $learning_goal"
echo ""
echo "🚀 现在可以对孩子说：'学英语' 来开始学习了！"
