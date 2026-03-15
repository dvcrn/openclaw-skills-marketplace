#!/bin/bash
# publish.sh - 发布技能到ClawHub
# 用法: bash publish.sh <skill-path> <version> [--slug <custom-slug>]
# 示例:
#   bash publish.sh ./skills/my-skill 1.0.0
#   bash publish.sh /absolute/path/to/skill 2.1.0 --slug miliger-my-skill

set -e

SKILL_PATH="$1"
VERSION="$2"
SLUG_FLAG="$3"
CUSTOM_SLUG="$4"

# 参数验证
if [ -z "$SKILL_PATH" ] || [ -z "$VERSION" ]; then
    echo "用法: bash publish.sh <skill-path> <version> [--slug <custom-slug>]"
    echo ""
    echo "示例:"
    echo "  bash publish.sh ./skills/my-skill 1.0.0"
    echo "  bash publish.sh /absolute/path/to/skill 2.1.0 --slug miliger-my-skill"
    exit 1
fi

# 转换为绝对路径
SKILL_PATH="$(cd "$(dirname "$SKILL_PATH")" && pwd)/$(basename "$SKILL_PATH")"

if [ ! -d "$SKILL_PATH" ]; then
    echo "❌ 技能目录不存在: $SKILL_PATH"
    exit 1
fi

# 验证SKILL.md存在
if [ ! -f "$SKILL_PATH/SKILL.md" ]; then
    echo "❌ 缺少 SKILL.md 文件"
    echo "   技能必须包含 SKILL.md 文件"
    exit 1
fi

# 确定slug
if [ "$SLUG_FLAG" = "--slug" ] && [ -n "$CUSTOM_SLUG" ]; then
    SLUG="$CUSTOM_SLUG"
else
    SLUG="$(basename "$SKILL_PATH")"
fi

echo "=== ClawHub 技能发布 ==="
echo "技能路径: $SKILL_PATH"
echo "版本: $VERSION"
echo "Slug: $SLUG"
echo ""

# 验证版本号格式
if ! [[ "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "⚠️  版本号格式不正确: $VERSION"
    echo "   正确格式: MAJOR.MINOR.PATCH (如: 1.0.0, 2.1.3)"
    read -p "是否继续? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 检查.clawhubignore
IGNORE_FILE="$SKILL_PATH/.clawhubignore"
if [ ! -f "$IGNORE_FILE" ]; then
    echo "⚠️  未找到 .clawhubignore 文件"
    echo ""
    echo "建议创建 .clawhubignore 排除以下内容:"
    echo "  venv/"
    echo "  node_modules/"
    echo "  __pycache__/"
    echo "  *.log"
    echo "  logs/"
    echo ""
    read -p "是否创建默认 .clawhubignore? (Y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        cat > "$IGNORE_FILE" << 'EOF'
venv/
node_modules/
__pycache__/
*.log
logs/
.git/
.gitignore
*.pyc
.env
EOF
        echo "✅ 已创建 .clawhubignore"
    fi
fi

# 检查publish.js是否需要修改
PUBLISH_JS="/usr/lib/node_modules/clawhub/dist/cli/commands/publish.js"
if [ -f "$PUBLISH_JS" ]; then
    if ! grep -q "acceptLicenseTerms" "$PUBLISH_JS"; then
        echo ""
        echo "⚠️  ClawHub CLI 需要 patch"
        echo "   publish.js 缺少 acceptLicenseTerms 字段"
        echo ""
        read -p "是否自动修复? (Y/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Nn]$ ]]; then
            # 备份原文件
            sudo cp "$PUBLISH_JS" "$PUBLISH_JS.bak"
            
            # 添加 acceptLicenseTerms
            sudo sed -i "s/form\.set('payload', JSON\.stringify({/form.set('payload', JSON.stringify({\n        acceptLicenseTerms: true,/" "$PUBLISH_JS"
            
            echo "✅ publish.js 已修复"
            echo "   备份文件: $PUBLISH_JS.bak"
        else
            echo "❌ 取消发布"
            exit 1
        fi
    fi
fi

echo ""
echo "【发布前检查】"

# 统计文件
TOTAL_FILES=$(find "$SKILL_PATH" -type f ! -path "*/venv/*" ! -path "*/node_modules/*" ! -path "*/.git/*" | wc -l)
SKILL_SIZE=$(du -sh "$SKILL_PATH" | cut -f1)

echo "  - 文件数: $TOTAL_FILES"
echo "  - 总大小: $SKILL_SIZE"
echo ""

# 最后确认
read -p "确认发布? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ 取消发布"
    exit 1
fi

echo ""
echo "【发布中...】"

# 执行发布
cd "$SKILL_PATH"
PUBLISH_OUTPUT=$(clawhub publish "$SKILL_PATH" --slug "$SLUG" --version "$VERSION" 2>&1)
PUBLISH_EXIT_CODE=$?

if [ $PUBLISH_EXIT_CODE -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "✅ 发布成功!"
    echo "=========================================="
    echo ""
    
    # 提取Package ID
    PACKAGE_ID=$(echo "$PUBLISH_OUTPUT" | grep -oP 'packageId["\s:]+\K\w+' || echo "未知")
    
    echo "📦 发布信息:"
    echo "  - Slug: $SLUG"
    echo "  - 版本: $VERSION"
    echo "  - Package ID: $PACKAGE_ID"
    echo ""
    echo "🔗 ClawHub 链接: https://clawhub.com/skills/$SLUG"
    echo ""
    echo "验证命令:"
    echo "  clawhub inspect $SLUG"
else
    echo ""
    echo "=========================================="
    echo "❌ 发布失败!"
    echo "=========================================="
    echo ""
    echo "错误信息:"
    echo "$PUBLISH_OUTPUT"
    echo ""
    echo "常见问题:"
    echo "  1. 文件过多 - 创建 .clawhubignore 排除大目录"
    echo "  2. acceptLicenseTerms 缺失 - 需要修改 publish.js"
    echo "  3. 网络问题 - 检查网络连接"
    exit 1
fi
