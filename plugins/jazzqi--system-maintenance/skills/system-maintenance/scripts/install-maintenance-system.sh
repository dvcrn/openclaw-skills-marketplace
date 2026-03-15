#!/bin/bash
# OpenClaw 维护系统安装脚本
# 一键安装和配置完整的维护系统

set -e

# 配置
MAINTENANCE_DIR="$HOME/.openclaw/maintenance"
SCRIPTS_DIR="$MAINTENANCE_DIR/scripts"
CONFIG_DIR="$MAINTENANCE_DIR/config"
LOGS_DIR="$MAINTENANCE_DIR/logs"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() {
    local level="$1"
    local message="$2"
    local color="$NC"
    
    case "$level" in
        "SUCCESS") color="$GREEN" ;;
        "ERROR") color="$RED" ;;
        "WARN") color="$YELLOW" ;;
        "INFO") color="$BLUE" ;;
    esac
    
    echo -e "${color}[$(date '+%Y-%m-%d %H:%M:%S')] [$level] $message${NC}"
}

# 开始安装
echo "========================================"
log "INFO" "🚀 OpenClaw 维护系统安装开始"
echo "========================================"

# ===================== 1. 检查环境 =====================
log "INFO" "🔍 检查系统环境..."

# 检查操作系统
if [[ "$(uname)" != "Darwin" ]]; then
    log "WARN" "⚠️  当前系统不是 macOS，某些功能可能不兼容"
fi

# 检查必要的命令
REQUIRED_COMMANDS=("bash" "crontab" "curl" "find" "gzip")
for cmd in "${REQUIRED_COMMANDS[@]}"; do
    if ! command -v "$cmd" > /dev/null; then
        log "ERROR" "❌ 缺少必要命令: $cmd"
        exit 1
    fi
done

log "SUCCESS" "✅ 环境检查通过"

# ===================== 2. 创建目录结构 =====================
log "INFO" "📁 创建目录结构..."

mkdir -p "$SCRIPTS_DIR"
mkdir -p "$CONFIG_DIR"
mkdir -p "$LOGS_DIR"

log "SUCCESS" "✅ 目录结构创建完成"

# ===================== 3. 检查现有脚本 =====================
log "INFO" "🔍 检查现有脚本..."

# 列出现有脚本
EXISTING_SCRIPTS=(
    "$HOME/.openclaw/openclaw-weekly-optimizer.sh"
    "$HOME/.openclaw/openclaw-agent-monitor.sh"
    "$HOME/.openclaw/scripts/daily-maintenance-optimization.sh"
)

for script in "${EXISTING_SCRIPTS[@]}"; do
    if [ -f "$script" ]; then
        log "INFO" "📄 发现现有脚本: $(basename "$script")"
    fi
done

# ===================== 4. 设置脚本权限 =====================
log "INFO" "🔐 设置脚本权限..."

# 为所有脚本设置可执行权限
find "$SCRIPTS_DIR" -name "*.sh" -exec chmod +x {} \;

log "SUCCESS" "✅ 脚本权限设置完成"

# ===================== 5. 安装定时任务 =====================
log "INFO" "⏰ 安装定时任务..."

# 备份当前 crontab
CRONTAB_BACKUP="$HOME/crontab.backup.$(date +%Y%m%d%H%M%S)"
crontab -l > "$CRONTAB_BACKUP" 2>/dev/null || true
log "INFO" "📋 当前 crontab 已备份到: $CRONTAB_BACKUP"

# 定义新的定时任务
NEW_CRON_TASKS=(
    "# ===================== OpenClaw 统一维护系统 ====================="
    "# 安装时间: $(date '+%Y-%m-%d %H:%M:%S')"
    "# 版本: 2.0.0"
    ""
    "# 实时监控 - 每5分钟"
    "*/5 * * * * $SCRIPTS_DIR/real-time-monitor.sh >> $LOGS_DIR/real-time-monitor.log 2>&1"
    ""
    "# 日志管理 - 每天凌晨2:00"
    "0 2 * * * $SCRIPTS_DIR/log-management.sh >> $LOGS_DIR/log-management.log 2>&1"
    ""
    "# 日常维护 - 每天凌晨3:30"
    "30 3 * * * $SCRIPTS_DIR/daily-maintenance.sh >> $LOGS_DIR/daily-maintenance.log 2>&1"
    ""
    "# 每周优化 - 每周日凌晨3:00"
    "0 3 * * 0 $SCRIPTS_DIR/weekly-optimization.sh >> $LOGS_DIR/weekly-optimization.log 2>&1"
    ""
    "# ===================== 旧任务清理区域 ====================="
    "# 以下旧任务已被新系统替代，可以安全删除:"
    "# 0 3 * * 0 /Users/qfei/.openclaw/openclaw-weekly-optimizer.sh"
    "# */5 * * * * /Users/qfei/.openclaw/openclaw-agent-monitor.sh"
    "# 0 2 * * * find /tmp -name 'openclaw-*.log' -mtime +7 -delete"
    "# 0 2 * * * find /tmp -name 'openclaw-agent-monitor.log' -size +10M -exec truncate -s 5M {} \\;"
    "# 30 3 * * * /Users/qfei/.openclaw/scripts/daily-maintenance-optimization.sh"
)

# 创建临时 crontab 文件
TEMP_CRONTAB=$(mktemp)

# 保留非 OpenClaw 相关任务
if [ -f "$CRONTAB_BACKUP" ]; then
    grep -v "openclaw\|OpenClaw" "$CRONTAB_BACKUP" > "$TEMP_CRONTAB" 2>/dev/null || true
fi

# 添加新任务
for line in "${NEW_CRON_TASKS[@]}"; do
    echo "$line" >> "$TEMP_CRONTAB"
done

# 安装新的 crontab
if crontab "$TEMP_CRONTAB"; then
    log "SUCCESS" "✅ 定时任务安装成功"
else
    log "ERROR" "❌ 定时任务安装失败"
    exit 1
fi

rm "$TEMP_CRONTAB"

# ===================== 6. 验证安装 =====================
log "INFO" "🔍 验证安装..."

# 检查 crontab
log "INFO" "📋 当前定时任务:"
crontab -l | grep -A2 -B2 "openclaw\|OpenClaw" || true

# 检查脚本
SCRIPT_COUNT=$(find "$SCRIPTS_DIR" -name "*.sh" | wc -l)
log "INFO" "📄 已安装 $SCRIPT_COUNT 个脚本"

# 检查目录
log "INFO" "📁 维护系统目录: $MAINTENANCE_DIR"
ls -la "$MAINTENANCE_DIR"

# ===================== 7. 创建管理工具 =====================
log "INFO" "🛠️ 创建管理工具..."

# 创建快速检查脚本
cat > "$MAINTENANCE_DIR/check-status.sh" << 'EOF'
#!/bin/bash
# 维护系统状态检查

MAINTENANCE_DIR="$HOME/.openclaw/maintenance"

echo "🔍 OpenClaw 维护系统状态检查"
echo "========================================"

# 检查目录
echo "📁 目录结构:"
find "$MAINTENANCE_DIR" -type d | sort

# 检查脚本
echo ""
echo "📄 脚本文件:"
find "$MAINTENANCE_DIR" -name "*.sh" -exec ls -la {} \;

# 检查定时任务
echo ""
echo "⏰ 定时任务:"
crontab -l | grep -E "(openclaw|OpenClaw|维护)" || echo "未找到相关任务"

# 检查日志
echo ""
echo "📊 日志文件:"
find "$MAINTENANCE_DIR/logs" -name "*.log*" -exec ls -la {} \; 2>/dev/null | head -10

echo ""
echo "✅ 检查完成"
EOF

chmod +x "$MAINTENANCE_DIR/check-status.sh"

# 创建测试脚本
cat > "$MAINTENANCE_DIR/test-maintenance.sh" << 'EOF'
#!/bin/bash
# 测试维护系统

MAINTENANCE_DIR="$HOME/.openclaw/maintenance"
SCRIPTS_DIR="$MAINTENANCE_DIR/scripts"

echo "🧪 OpenClaw 维护系统测试"
echo "========================================"

# 测试实时监控（快速模式）
echo "1. 🚀 测试实时监控..."
"$SCRIPTS_DIR/real-time-monitor.sh" 2>&1 | tail -5

# 测试日志管理（模拟模式）
echo ""
echo "2. 📁 测试日志管理..."
"$SCRIPTS_DIR/log-management.sh" 2>&1 | tail -5

echo ""
echo "✅ 测试完成"
EOF

chmod +x "$MAINTENANCE_DIR/test-maintenance.sh"

log "SUCCESS" "✅ 管理工具创建完成"

# ===================== 8. 更新 skill =====================
log "INFO" "📦 更新维护技能..."

# 检查是否存在 skill
SKILL_DIR="$HOME/.openclaw/skills/system-maintenance"
if [ -d "$SKILL_DIR" ]; then
    log "INFO" "🔍 发现现有技能，准备更新..."
    
    # 备份技能
    SKILL_BACKUP="${SKILL_DIR}.backup.$(date +%Y%m%d%H%M%S)"
    cp -r "$SKILL_DIR" "$SKILL_BACKUP"
    log "INFO" "📋 技能已备份到: $SKILL_BACKUP"
    
    # 更新技能内容
    cp -r "$MAINTENANCE_DIR" "$SKILL_DIR/maintenance-system/"
    log "INFO" "✅ 技能内容已更新"
else
    log "INFO" "ℹ️  未发现现有技能，可以稍后手动发布"
fi

# ===================== 9. 安装完成 =====================
echo ""
echo "========================================"
log "SUCCESS" "🎉 OpenClaw 维护系统安装完成！"
echo "========================================"
echo ""
echo "📋 安装摘要:"
echo "  📁 目录: $MAINTENANCE_DIR"
echo "  📄 脚本: $SCRIPT_COUNT 个维护脚本"
echo "  ⏰ 定时: 4个定时任务已配置"
echo "  🛠️  工具: 2个管理工具"
echo ""
echo "🚀 使用方法:"
echo "  1. 检查状态: $MAINTENANCE_DIR/check-status.sh"
echo "  2. 测试系统: $MAINTENANCE_DIR/test-maintenance.sh"
echo "  3. 查看日志: ls -la $MAINTENANCE_DIR/logs/"
echo ""
echo "📅 维护计划:"
echo "  ⏱️  每5分钟 - 实时监控"
echo "  🕑  02:00 - 日志管理"
echo "  🕞  03:30 - 日常维护"
echo "  🕒  03:00 (周日) - 每周优化"
echo ""
echo "🔧 后续步骤:"
echo "  1. 测试系统运行: bash $MAINTENANCE_DIR/test-maintenance.sh"
echo "  2. 等待第一次自动执行"
echo "  3. 查看执行日志"
echo "  4. 更新技能到 ClawHub"
echo ""

exit 0