#!/bin/bash

# Nero Market Research - 一键安装脚本
# 版本: v4.0 Final
# 作者: Nero Team

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印函数
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 欢迎信息
echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                                                            ║"
echo "║              Nero Market Research v4.0 Final               ║"
echo "║                                                            ║"
echo "║      从500条噪音中，精准找到那1-2个神仙点子               ║"
echo "║                                                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# 检查系统依赖
print_info "检查系统依赖..."

# 检查 Python
if ! command -v python3 &> /dev/null; then
    print_error "未找到 Python 3，请先安装 Python 3.10+"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | awk '{print $2}')
print_success "Python 版本: $PYTHON_VERSION"

# 检查 pip
if ! command -v pip3 &> /dev/null; then
    print_error "未找到 pip3，请先安装 pip"
    exit 1
fi

print_success "pip3 已安装"

# 检查 systemd
if ! command -v systemctl &> /dev/null; then
    print_warning "未找到 systemd，将使用 Cron 替代"
    USE_SYSTEMD=false
else
    USE_SYSTEMD=true
    print_success "systemd 已安装"
fi

# 获取安装目录
INSTALL_DIR="${INSTALL_DIR:-$HOME/.nero-market-research}"
print_info "安装目录: $INSTALL_DIR"

# 创建目录结构
print_info "创建目录结构..."

mkdir -p "$INSTALL_DIR"/{scripts,config,logs,memory/{research/{daily,opportunities},translation_cache}}

print_success "目录结构已创建"

# 复制文件
print_info "复制文件..."

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 复制核心脚本
cp -r "$SCRIPT_DIR"/scripts/* "$INSTALL_DIR/scripts/" 2>/dev/null || true

# 复制配置文件
cp -r "$SCRIPT_DIR"/config/* "$INSTALL_DIR/config/" 2>/dev/null || true

# 复制配置模板
if [ ! -f "$INSTALL_DIR/config.json" ]; then
    if [ -f "$SCRIPT_DIR/config.json.example" ]; then
        cp "$SCRIPT_DIR/config.json.example" "$INSTALL_DIR/config.json"
        print_success "配置模板已复制"
    fi
fi

print_success "文件复制完成"

# 安装 Python 依赖
print_info "安装 Python 依赖..."

cat > "$INSTALL_DIR/requirements.txt" << 'EOF'
requests>=2.28.0
schedule>=1.2.0
python-dateutil>=2.8.0
EOF

pip3 install -q -r "$INSTALL_DIR/requirements.txt"

print_success "Python 依赖已安装"

# 创建命令别名
print_info "创建命令别名..."

# 创建命令脚本
cat > "$INSTALL_DIR/nero" << 'EOF'
#!/bin/bash
INSTALL_DIR="$HOME/.nero-market-research"

case "$1" in
    start)
        systemctl --user start nero-cycle.service 2>/dev/null || \
        nohup python3 "$INSTALL_DIR/scripts/cycle_execution.py" > "$INSTALL_DIR/logs/cycle_execution.log" 2>&1 &
        echo "✅ Nero 系统已启动"
        ;;
    stop)
        systemctl --user stop nero-cycle.service 2>/dev/null || \
        pkill -f "cycle_execution.py"
        echo "✅ Nero 系统已停止"
        ;;
    restart)
        $0 stop
        sleep 2
        $0 start
        ;;
    status)
        if pgrep -f "cycle_execution.py" > /dev/null; then
            echo "✅ Nero 系统运行中"
            echo ""
            tail -n 20 "$INSTALL_DIR/logs/cycle_execution.log"
        else
            echo "❌ Nero 系统未运行"
        fi
        ;;
    logs)
        tail -f "$INSTALL_DIR/logs/cycle_execution.log"
        ;;
    run)
        python3 "$INSTALL_DIR/scripts/cycle_execution.py" --once
        ;;
    sync)
        python3 "$INSTALL_DIR/scripts/sync_to_notion.py"
        ;;
    report)
        python3 "$INSTALL_DIR/scripts/generate_report.py"
        ;;
    cleanup)
        python3 "$INSTALL_DIR/scripts/cleanup_old_data.py"
        ;;
    stats)
        echo "📊 统计数据："
        echo "  总机会数: $(find "$INSTALL_DIR/memory/research/opportunities" -name "*.json" -exec cat {} \; | jq -s 'add | length' 2>/dev/null || echo 0)"
        echo "  今日数据: $(ls -1 "$INSTALL_DIR/memory/research/daily" | wc -l)"
        ;;
    *)
        echo "用法: nero {start|stop|restart|status|logs|run|sync|report|cleanup|stats}"
        ;;
esac
EOF

chmod +x "$INSTALL_DIR/nero"

# 创建软链接
if [ -w "/usr/local/bin" ]; then
    ln -sf "$INSTALL_DIR/nero" /usr/local/bin/nero
    print_success "全局命令已创建: nero"
else
    print_warning "无法创建全局命令，请手动添加到 PATH"
    echo "export PATH=\"\$PATH:$INSTALL_DIR\"" >> ~/.bashrc
fi

# 创建 systemd 服务（如果可用）
if [ "$USE_SYSTEMD" = true ]; then
    print_info "创建 systemd 服务..."
    
    mkdir -p ~/.config/systemd/user
    
    cat > ~/.config/systemd/user/nero-cycle.service << EOF
[Unit]
Description=Nero Market Research - 24小时自动化市场研究
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 $INSTALL_DIR/scripts/cycle_execution.py
WorkingDirectory=$INSTALL_DIR
Restart=always
RestartSec=10

[Install]
WantedBy=default.target
EOF
    
    systemctl --user daemon-reload
    systemctl --user enable nero-cycle.service
    
    print_success "systemd 服务已创建"
fi

# 创建快速启动脚本
cat > "$INSTALL_DIR/start.sh" << 'EOF'
#!/bin/bash
echo "🚀 启动 Nero Market Research..."
nero start
echo ""
echo "📊 查看日志: nero logs"
echo "📈 查看状态: nero status"
echo "🌐 Notion 数据库: 打开你的 Notion 查看商机池"
EOF

chmod +x "$INSTALL_DIR/start.sh"

# 创建环境变量文件
cat > "$INSTALL_DIR/.env" << EOF
# Nero Market Research 环境变量
# 请根据实际情况修改

NOTION_API_KEY=ntn_your_api_key_here
NOTION_DATABASE_ID=your_database_id_here
NOTION_DAILY_REPORT_DB_ID=your_daily_report_db_id_here

LIBRETRANSLATE_URL=https://translate.example.com
LIBRETRANSLATE_TOKEN=your_token_here

SEARXNG_PRIMARY_URL=http://localhost:8080
SEARXNG_FALLBACK_URL=https://search.example.com
EOF

print_success "环境变量模板已创建"

# 最终提示
echo ""
echo "════════════════════════════════════════════════════════════"
echo ""
print_success "✅ 安装完成！"
echo ""
echo "════════════════════════════════════════════════════════════"
echo ""
echo "📋 下一步："
echo ""
echo "1️⃣  配置 API Keys："
echo "   nano $INSTALL_DIR/config.json"
echo ""
echo "2️⃣  创建 Notion 数据库："
echo "   查看 docs/SETUP_GUIDE.md 了解详细步骤"
echo ""
echo "3️⃣  启动系统："
echo "   nero start"
echo ""
echo "4️⃣  查看日志："
echo "   nero logs"
echo ""
echo "════════════════════════════════════════════════════════════"
echo ""
echo "📚 文档："
echo "   - 安装指南: $INSTALL_DIR/../docs/SETUP_GUIDE.md"
echo "   - 配置说明: $INSTALL_DIR/../docs/CONFIGURATION.md"
echo "   - 使用手册: $INSTALL_DIR/../docs/USAGE.md"
echo ""
echo "════════════════════════════════════════════════════════════"
echo ""
echo "🎉 准备开始从噪音中挖掘神仙点子！"
echo ""
