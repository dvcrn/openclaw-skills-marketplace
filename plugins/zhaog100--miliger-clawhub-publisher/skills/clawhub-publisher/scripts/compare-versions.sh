#!/bin/bash
# compare-versions.sh - 对比本地和远程技能版本差异
# 用法: bash compare-versions.sh <skill-name> [--download]

set -e

SKILL_NAME="$1"
DOWNLOAD_FLAG="$2"
TEMP_DIR="/tmp/clawhub-compare-$SKILL_NAME-$(date +%s)"
LOCAL_SKILL_DIR=""  # 需要根据实际情况调整

if [ -z "$SKILL_NAME" ]; then
    echo "用法: bash compare-versions.sh <skill-name> [--download]"
    exit 1
fi

echo "=== 版本对比: $SKILL_NAME ==="
echo ""

# 1. 查找本地技能目录
echo "【1/5】查找本地技能..."
POSSIBLE_PATHS=(
    "/root/.openclaw/workspace/skills/$SKILL_NAME"
    "./skills/$SKILL_NAME"
    "../$SKILL_NAME"
    "./$SKILL_NAME"
)

for path in "${POSSIBLE_PATHS[@]}"; do
    if [ -d "$path" ] && [ -f "$path/SKILL.md" ]; then
        LOCAL_SKILL_DIR="$path"
        break
    fi
done

if [ -z "$LOCAL_SKILL_DIR" ]; then
    echo "❌ 未找到本地技能目录"
    echo "请确保技能目录包含 SKILL.md 文件"
    exit 1
fi

echo "✅ 本地技能: $LOCAL_SKILL_DIR"
echo ""

# 2. 获取远程版本信息
echo "【2/5】获取远程版本信息..."
REMOTE_INFO=$(clawhub inspect "$SKILL_NAME" 2>&1)
if [ $? -ne 0 ]; then
    echo "❌ 远程版本不存在"
    exit 1
fi

REMOTE_VERSION=$(echo "$REMOTE_INFO" | grep -oP 'version:\s*\K[\d.]+' || echo "未知")
echo "✅ 远程版本: $REMOTE_VERSION"
echo ""

# 3. 下载远程版本到临时目录
echo "【3/5】下载远程版本..."
mkdir -p "$TEMP_DIR"
cd "$TEMP_DIR"
clawhub install "$SKILL_NAME" --target ./remote 2>&1 | grep -v "^$"

if [ ! -d "./remote/$SKILL_NAME" ]; then
    echo "❌ 下载失败"
    rm -rf "$TEMP_DIR"
    exit 1
fi

echo "✅ 下载完成: $TEMP_DIR/remote/$SKILL_NAME"
echo ""

# 4. 对比版本
echo "【4/5】获取本地版本..."
LOCAL_VERSION=$(grep -oP 'version["\s:]+\K[\d.]+' "$LOCAL_SKILL_DIR/package.json" 2>/dev/null || \
                grep -oP 'version:\s*\K[\d.]+' "$LOCAL_SKILL_DIR/package.json" 2>/dev/null || \
                echo "未知")
echo "✅ 本地版本: $LOCAL_VERSION"
echo ""

# 5. 对比文件差异
echo "【5/5】对比文件差异..."
echo "=========================================="

# 文件数量统计
LOCAL_FILES=$(find "$LOCAL_SKILL_DIR" -type f ! -path "*/\.*" ! -path "*/venv/*" ! -path "*/node_modules/*" | wc -l)
REMOTE_FILES=$(find "./remote/$SKILL_NAME" -type f ! -path "*/\.*" ! -path "*/venv/*" ! -path "*/node_modules/*" | wc -l)

echo "📊 文件统计:"
echo "  - 本地: $LOCAL_FILES 个文件"
echo "  - 远程: $REMOTE_FILES 个文件"
echo ""

# 使用diff对比
echo "📋 文件差异:"
diff -rq "$LOCAL_SKILL_DIR" "./remote/$SKILL_NAME" 2>/dev/null | \
    grep -v "venv\|node_modules\|\.git\|__pycache__" || \
    echo "  ✅ 无差异"

echo ""
echo "=========================================="

# 生成详细报告
REPORT_FILE="$TEMP_DIR/comparison-report.txt"
echo "=== 详细对比报告 ===" > "$REPORT_FILE"
echo "时间: $(date)" >> "$REPORT_FILE"
echo "技能: $SKILL_NAME" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"
echo "版本信息:" >> "$REPORT_FILE"
echo "  - 本地: $LOCAL_VERSION" >> "$REPORT_FILE"
echo "  - 远程: $REMOTE_VERSION" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"
echo "文件差异:" >> "$REPORT_FILE"
diff -rq "$LOCAL_SKILL_DIR" "./remote/$SKILL_NAME" 2>/dev/null | \
    grep -v "venv\|node_modules\|\.git\|__pycache__" >> "$REPORT_FILE" || \
    echo "  无差异" >> "$REPORT_FILE"

echo ""
echo "📄 详细报告已保存: $REPORT_FILE"

# 如果指定了--download，保留临时目录
if [ "$DOWNLOAD_FLAG" = "--download" ]; then
    echo ""
    echo "✅ 远程版本已下载到: $TEMP_DIR/remote/$SKILL_NAME"
    echo "   查看命令: ls -la $TEMP_DIR/remote/$SKILL_NAME"
else
    echo ""
    echo "💡 使用 --download 参数保留远程版本文件"
    read -p "是否删除临时文件? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf "$TEMP_DIR"
        echo "✅ 临时文件已删除"
    else
        echo "📁 临时文件保留在: $TEMP_DIR"
    fi
fi

echo ""
echo "=== 对比完成 ==="
