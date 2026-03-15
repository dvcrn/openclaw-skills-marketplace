#!/bin/bash
# 提交前自动检查脚本
# 在提交前运行此脚本，确保代码质量和安全性

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }
log_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }

echo "🔍 开始提交前检查..."
echo "======================"
echo

# ===================== 1. Git 状态检查 =====================
log_info "1. Git 状态检查"
git status --short

UNTRACKED_COUNT=$(git status --porcelain | grep -c "^??")
MODIFIED_COUNT=$(git status --porcelain | grep -c "^ M")
DELETED_COUNT=$(git status --porcelain | grep -c "^ D")

if [ "$UNTRACKED_COUNT" -gt 5 ]; then
    log_warning "有 $UNTRACKED_COUNT 个未跟踪文件，请确认是否需要提交"
fi

echo

# ===================== 2. 敏感信息检查 =====================
log_info "2. 敏感信息检查"

# 检查常见的敏感信息模式
SENSITIVE_PATTERNS=(
    "password[[:space:]]*="
    "token[[:space:]]*="
    "secret[[:space:]]*="
    "api[_-]key[[:space:]]*="
    "private[_-]key[[:space:]]*="
    "access[_-]token[[:space:]]*="
    "auth[[:space:]]*="
    "credentials"
)

FOUND_SENSITIVE=false
for pattern in "${SENSITIVE_PATTERNS[@]}"; do
    # 排除测试和示例文件
    RESULTS=$(grep -r -i "$pattern" . --include="*.json" --include="*.js" --include="*.sh" --include="*.md" --include="*.yaml" --include="*.yml" 2>/dev/null | grep -v -E "(test|example|dummy|placeholder|YOUR_)" || true)
    
    if [ -n "$RESULTS" ]; then
        log_error "发现可能的敏感信息 (模式: $pattern):"
        echo "$RESULTS" | head -5
        FOUND_SENSITIVE=true
    fi
done

if [ "$FOUND_SENSITIVE" = false ]; then
    log_success "未发现敏感信息"
fi

echo

# ===================== 3. .gitignore 检查 =====================
log_info "3. .gitignore 检查"

if [ -f ".gitignore" ]; then
    log_success ".gitignore 文件存在"
    
    # 检查关键规则
    REQUIRED_RULES=("backup" "node_modules" ".env" "*.log" "*.tmp")
    MISSING_RULES=()
    
    for rule in "${REQUIRED_RULES[@]}"; do
        if ! grep -q "$rule" .gitignore 2>/dev/null; then
            MISSING_RULES+=("$rule")
        fi
    done
    
    if [ ${#MISSING_RULES[@]} -eq 0 ]; then
        log_success "包含所有关键忽略规则"
    else
        log_warning "缺少以下忽略规则: ${MISSING_RULES[*]}"
    fi
else
    log_error "无 .gitignore 文件"
fi

echo

# ===================== 4. 版本号检查 =====================
log_info "4. 版本号检查"

if [ -f "package.json" ]; then
    VERSION=$(grep '"version"' package.json | head -1 | cut -d'"' -f4)
    if [ -n "$VERSION" ]; then
        log_success "当前版本: $VERSION"
        
        # 检查版本号格式 (语义化版本)
        if [[ $VERSION =~ ^[0-9]+\.[0-9]+\.[0-9]+(-[a-zA-Z0-9]+(\.[a-zA-Z0-9]+)*)?$ ]]; then
            log_success "版本号格式正确"
        else
            log_warning "版本号格式可能不符合语义化版本规范"
        fi
    else
        log_error "无法获取版本号"
    fi
else
    log_warning "无 package.json 文件"
fi

echo

# ===================== 5. 文件大小检查 =====================
log_info "5. 文件大小检查"

# 检查是否有大文件 (>10MB)
LARGE_FILES=$(find . -type f -size +10M -not -path "./.git/*" -not -path "./node_modules/*" 2>/dev/null | head -5)
if [ -n "$LARGE_FILES" ]; then
    log_error "发现大文件 (>10MB)，建议不要提交到 Git:"
    echo "$LARGE_FILES"
else
    log_success "无过大文件"
fi

echo

# ===================== 6. 脚本可执行性检查 =====================
log_info "6. 脚本可执行性检查"

NON_EXECUTABLE_SCRIPTS=$(find scripts -name "*.sh" -type f ! -executable 2>/dev/null | head -5)
if [ -n "$NON_EXECUTABLE_SCRIPTS" ]; then
    log_warning "以下脚本不可执行:"
    echo "$NON_EXECUTABLE_SCRIPTS"
    echo "建议运行: chmod +x scripts/*.sh"
else
    log_success "所有脚本都可执行"
fi

echo

# ===================== 7. 备份目录检查 =====================
log_info "7. 备份目录检查"

BACKUP_DIRS=$(find . -type d -name "*backup*" -not -path "./.git/*" 2>/dev/null | head -5)
if [ -n "$BACKUP_DIRS" ]; then
    log_warning "发现备份目录:"
    echo "$BACKUP_DIRS"
    echo "请确认这些目录是否应该被提交"
    
    # 检查是否在 .gitignore 中
    for dir in $BACKUP_DIRS; do
        DIR_NAME=$(basename "$dir")
        if grep -q "$DIR_NAME" .gitignore 2>/dev/null; then
            log_success "  ✅ $DIR_NAME 已在 .gitignore 中"
        else
            log_warning "  ⚠️  $DIR_NAME 不在 .gitignore 中"
        fi
    done
else
    log_success "无备份目录"
fi

echo

# ===================== 8. README 和文档检查 =====================
log_info "8. 文档检查"

# 检查 README.md
if [ -f "README.md" ]; then
    README_SIZE=$(wc -l < README.md)
    if [ "$README_SIZE" -lt 50 ]; then
        log_warning "README.md 可能过短 ($README_SIZE 行)"
    else
        log_success "README.md 文档完整 ($README_SIZE 行)"
    fi
else
    log_warning "无 README.md 文件"
fi

# 检查 SKILL.md
if [ -f "SKILL.md" ]; then
    log_success "SKILL.md 存在"
else
    log_warning "无 SKILL.md 文件"
fi

echo

# ===================== 9. 最终摘要 =====================
log_info "9. 检查摘要"

echo "📊 检查结果统计:"
echo "  - Git 状态: $MODIFIED_COUNT 修改, $DELETED_COUNT 删除, $UNTRACKED_COUNT 未跟踪"
echo "  - 敏感信息: $(if [ "$FOUND_SENSITIVE" = true ]; then echo "发现"; else echo "未发现"; fi)"
echo "  - .gitignore: $(if [ -f ".gitignore" ]; then echo "存在"; else echo "缺失"; fi)"
echo "  - 版本号: ${VERSION:-未找到}"
echo "  - 大文件: $(if [ -n "$LARGE_FILES" ]; then echo "发现"; else echo "无"; fi)"
echo "  - 脚本权限: $(if [ -n "$NON_EXECUTABLE_SCRIPTS" ]; then echo "有问题"; else echo "正常"; fi)"

echo
echo "🎯 建议操作:"

if [ "$FOUND_SENSITIVE" = true ]; then
    echo "  ❗ 立即处理敏感信息泄露风险"
fi

if [ -n "$LARGE_FILES" ]; then
    echo "  📦 考虑移除或忽略大文件"
fi

if [ -n "$NON_EXECUTABLE_SCRIPTS" ]; then
    echo "  🔧 修复脚本权限: chmod +x scripts/*.sh"
fi

if [ ${#MISSING_RULES[@]} -gt 0 ]; then
    echo "  📝 更新 .gitignore 添加规则: ${MISSING_RULES[*]}"
fi

echo
echo "📋 检查完成！请根据以上结果决定是否提交。"
echo
echo "🚀 如果一切正常，可以运行:"
echo "  git commit -m \"你的提交信息\""

# 如果有严重问题，退出码为非0
if [ "$FOUND_SENSITIVE" = true ]; then
    exit 1
fi

exit 0