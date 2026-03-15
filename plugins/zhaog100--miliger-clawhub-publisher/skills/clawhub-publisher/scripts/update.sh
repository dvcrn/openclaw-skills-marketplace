#!/bin/bash
# update.sh - 一键更新现有技能（检查+对比+下载）
# 用法: bash update.sh <skill-name>
# 示例: bash update.sh session-memory-enhanced

set -e

SKILL_NAME="$1"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TEMP_BASE="/tmp/clawhub-update-$(date +%s)"

if [ -z "$SKILL_NAME" ]; then
    echo "用法: bash update.sh <skill-name>"
    echo ""
    echo "示例:"
    echo "  bash update.sh session-memory-enhanced"
    exit 1
fi

echo "=========================================="
echo "  ClawHub 技能更新助手"
echo "=========================================="
echo ""
echo "技能: $SKILL_NAME"
echo ""

# 1. 检查现有版本
echo "【步骤1/4】检查现有版本..."
CHECK_OUTPUT=$(bash "$SCRIPT_DIR/check-existing.sh" "$SKILL_NAME" 2>&1)
CHECK_EXIT_CODE=$?

if [ $CHECK_EXIT_CODE -eq 0 ]; then
    echo "❌ 技能不存在，无法更新"
    echo "   使用 publish.sh 发布新技能"
    exit 1
elif [ $CHECK_EXIT_CODE -eq 2 ]; then
    echo "❌ 所有者不是当前用户，无法更新"
    echo "   考虑使用不同的slug"
    exit 1
fi

echo "$CHECK_OUTPUT"
echo ""

# 2. 下载远程版本
echo "【步骤2/4】下载远程版本..."
DOWNLOAD_DIR="$TEMP_BASE/remote"
mkdir -p "$DOWNLOAD_DIR"
cd "$DOWNLOAD_DIR"

clawhub install "$SKILL_NAME" --target . 2>&1 | grep -v "^$"

if [ ! -d "./$SKILL_NAME" ]; then
    echo "❌ 下载失败"
    rm -rf "$TEMP_BASE"
    exit 1
fi

echo "✅ 下载完成: $DOWNLOAD_DIR/$SKILL_NAME"
echo ""

# 3. 查找本地版本
echo "【步骤3/4】查找本地版本..."
POSSIBLE_PATHS=(
    "/root/.openclaw/workspace/skills/$SKILL_NAME"
    "./skills/$SKILL_NAME"
    "../$SKILL_NAME"
    "./$SKILL_NAME"
)

LOCAL_SKILL_DIR=""
for path in "${POSSIBLE_PATHS[@]}"; do
    if [ -d "$path" ] && [ -f "$path/SKILL.md" ]; then
        LOCAL_SKILL_DIR="$path"
        break
    fi
done

if [ -z "$LOCAL_SKILL_DIR" ]; then
    echo "❌ 未找到本地技能目录"
    echo ""
    echo "💡 提示:"
    echo "   远程版本已下载到: $DOWNLOAD_DIR/$SKILL_NAME"
    echo "   你可以手动复制到本地目录"
    echo ""
    read -p "是否打开下载目录? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cd "$DOWNLOAD_DIR/$SKILL_NAME"
        ls -la
        echo ""
        echo "📁 当前目录: $(pwd)"
    fi
    exit 1
fi

echo "✅ 本地技能: $LOCAL_SKILL_DIR"
echo ""

# 4. 对比差异
echo "【步骤4/4】对比差异..."
echo "=========================================="

# 简单对比
LOCAL_FILES=$(find "$LOCAL_SKILL_DIR" -type f ! -path "*/\.*" ! -path "*/venv/*" ! -path "*/node_modules/*" | wc -l)
REMOTE_FILES=$(find "./$SKILL_NAME" -type f ! -path "*/\.*" ! -path "*/venv/*" ! -path "*/node_modules/*" | wc -l)

echo "📊 文件统计:"
echo "  - 本地: $LOCAL_FILES 个文件"
echo "  - 远程: $REMOTE_FILES 个文件"
echo ""

echo "📋 文件差异:"
diff -rq "$LOCAL_SKILL_DIR" "./$SKILL_NAME" 2>/dev/null | \
    grep -v "venv\|node_modules\|\.git\|__pycache__" || \
    echo "  ✅ 无差异"

echo "=========================================="
echo ""

# 获取版本信息
REMOTE_VERSION=$(grep -oP 'version["\s:]+\K[\d.]+' "./$SKILL_NAME/package.json" 2>/dev/null || \
                 grep -oP 'version:\s*\K[\d.]+' "./$SKILL_NAME/package.json" 2>/dev/null || \
                 echo "未知")

LOCAL_VERSION=$(grep -oP 'version["\s:]+\K[\d.]+' "$LOCAL_SKILL_DIR/package.json" 2>/dev/null || \
                grep -oP 'version:\s*\K[\d.]+' "$LOCAL_SKILL_DIR/package.json" 2>/dev/null || \
                echo "未知")

echo "版本信息:"
echo "  - 本地: $LOCAL_VERSION"
echo "  - 远程: $REMOTE_VERSION"
echo ""

# 提供操作建议
echo "【操作建议】"

if [ "$LOCAL_FILES" = "$REMOTE_FILES" ] && [ "$(diff -rq "$LOCAL_SKILL_DIR" "./$SKILL_NAME" 2>/dev/null | grep -v "venv\|node_modules\|\.git\|__pycache__" | wc -l)" -eq 0 ]; then
    echo "✅ 本地和远程完全一致，无需更新"
    rm -rf "$TEMP_BASE"
    exit 0
else
    echo "🔍 发现差异，建议操作:"
    echo ""
    echo "  1. 手动审查差异"
    echo "     diff -r $LOCAL_SKILL_DIR $DOWNLOAD_DIR/$SKILL_NAME"
    echo ""
    echo "  2. 合并重要变更"
    echo "     cp -r $DOWNLOAD_DIR/$SKILL_NAME/* $LOCAL_SKILL_DIR/"
    echo ""
    echo "  3. 更新版本号后发布"
    echo "     bash $SCRIPT_DIR/publish.sh $LOCAL_SKILL_DIR x.y.z"
    echo ""
fi

# 询问是否合并
read -p "是否自动合并远程版本到本地? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    # 备份本地版本
    BACKUP_DIR="$TEMP_BASE/backup"
    mkdir -p "$BACKUP_DIR"
    cp -r "$LOCAL_SKILL_DIR" "$BACKUP_DIR/"
    echo "✅ 本地版本已备份: $BACKUP_DIR/$SKILL_NAME"
    
    # 复制远程版本
    cp -rf "./$SKILL_NAME"/* "$LOCAL_SKILL_DIR/"
    echo "✅ 远程版本已合并到本地"
    echo ""
    echo "⚠️  请手动检查并修复冲突"
    echo "   本地目录: $LOCAL_SKILL_DIR"
    echo "   备份目录: $BACKUP_DIR/$SKILL_NAME"
else
    echo "📁 远程版本保留在: $DOWNLOAD_DIR/$SKILL_NAME"
    echo "   你可以手动查看和合并"
fi

echo ""
echo "=== 更新检查完成 ==="
