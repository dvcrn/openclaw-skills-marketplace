#!/bin/bash

# QQ 音乐播放器 Skill 打包脚本
# 用于创建可上传到 Knot 平台的 ZIP 包

SKILL_NAME="qq-music-radio"
SKILL_DIR="/projects/.openclaw/skills/$SKILL_NAME"
TEMP_DIR="/tmp/skill-package-$$"
OUTPUT_DIR="/tmp"
PACKAGE_NAME="$SKILL_NAME.zip"  # ZIP 文件名必须和顶层文件夹名一致

echo "📦 打包 QQ 音乐播放器 Skill..."
echo "================================"
echo ""

# 创建临时目录
mkdir -p "$TEMP_DIR"

# 复制整个 skill 目录到临时目录
echo "正在复制文件..."
cp -r "$SKILL_DIR" "$TEMP_DIR/$SKILL_NAME"

# 删除不需要的文件
echo "正在清理文件..."
rm -rf "$TEMP_DIR/$SKILL_NAME/player/node_modules"
find "$TEMP_DIR/$SKILL_NAME" -name "*.log" -delete
find "$TEMP_DIR/$SKILL_NAME" -name ".DS_Store" -delete
find "$TEMP_DIR/$SKILL_NAME" -name "*.swp" -delete

# 删除旧的 ZIP 包
rm -f "$OUTPUT_DIR/$PACKAGE_NAME"

# 切换到临时目录并打包
cd "$TEMP_DIR" || exit 1
echo "正在创建 ZIP 包..."
zip -r "$OUTPUT_DIR/$PACKAGE_NAME" "$SKILL_NAME" > /dev/null

if [ $? -eq 0 ]; then
    echo "✅ 打包成功！"
    echo ""
    echo "📦 包信息："
    echo "   ZIP 文件名: $PACKAGE_NAME"
    echo "   顶层文件夹: $SKILL_NAME/"
    echo "   文件路径: $OUTPUT_DIR/$PACKAGE_NAME"
    echo "   大小: $(du -h "$OUTPUT_DIR/$PACKAGE_NAME" | cut -f1)"
    echo ""
    echo "🔍 ZIP 结构验证："
    unzip -l "$OUTPUT_DIR/$PACKAGE_NAME" | head -10
    echo "   ..."
    echo ""
    echo "✅ 格式正确！符合 Knot 平台要求："
    echo "   • ZIP 文件名: $PACKAGE_NAME"
    echo "   • 顶层文件夹: $SKILL_NAME/"
    echo "   • 名称一致: ✓"
    echo ""
    echo "📤 上传方法："
    echo "   1. 下载文件: $OUTPUT_DIR/$PACKAGE_NAME"
    echo "   2. 访问 Knot 技能市场"
    echo "   3. 点击"上传技能""
    echo "   4. 选择下载的 ZIP 文件"
    echo "   5. 填写信息并提交"
else
    echo "❌ 打包失败！"
    rm -rf "$TEMP_DIR"
    exit 1
fi

# 清理临时目录
rm -rf "$TEMP_DIR"

echo ""
echo "🎉 完成！可以上传了！"
