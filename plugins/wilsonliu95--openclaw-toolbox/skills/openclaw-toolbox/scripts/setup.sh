#!/bin/bash
#
# OpenClaw 一键初始化脚本
# 用于在新电脑上快速部署 OpenClaw 环境
# 作者: 虾宝宝 🦐
# 创建时间: 2026-02-05
#

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# OpenClaw 根目录（基于脚本位置）
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../../../../" && pwd)"

# 执行开关（可通过参数控制）
SKIP_NODE=0
SKIP_PACKAGES=0
SKIP_ENV=0
SKIP_MCP=0
SKIP_CLAUDE=0
SKIP_VERIFY=0
VERIFY_ONLY=0
UPDATE_REPO=0
RESET_ENV=0

# 打印函数
print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

usage() {
    cat <<'USAGE'
OpenClaw Setup Script

Usage:
  setup.sh [options]

Options:
  --update           拉取最新仓库（git pull --rebase，工作区需干净）
  --verify-only      仅做验证，不执行安装
  --reset-env        重新生成 .env（会备份旧文件）
  --skip-node        跳过 Node.js 安装
  --skip-packages    跳过全局 CLI 安装
  --skip-env         跳过 .env 配置
  --skip-mcp         跳过 MCP 检查/配置
  --skip-claude      跳过 Claude MCP 配置
  --skip-verify      跳过安装验证
  -h, --help         显示帮助
USAGE
}

# 检查命令是否存在
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# 解析参数
parse_args() {
    while [ $# -gt 0 ]; do
        case "$1" in
            --update) UPDATE_REPO=1 ;;
            --verify-only) VERIFY_ONLY=1 ;;
            --reset-env) RESET_ENV=1 ;;
            --skip-node) SKIP_NODE=1 ;;
            --skip-packages) SKIP_PACKAGES=1 ;;
            --skip-env) SKIP_ENV=1 ;;
            --skip-mcp) SKIP_MCP=1 ;;
            --skip-claude) SKIP_CLAUDE=1 ;;
            --skip-verify) SKIP_VERIFY=1 ;;
            -h|--help) usage; exit 0 ;;
            *)
                print_error "未知参数: $1"
                usage
                exit 1
                ;;
        esac
        shift
    done
}

# 检查基础依赖
check_prereqs() {
    print_header "检查基础依赖"

    if command_exists git; then
        print_success "Git 已安装"
    else
        print_error "未安装 Git（请先安装）"
        exit 1
    fi

    if command_exists curl; then
        print_success "curl 已安装"
    else
        print_error "未安装 curl（请先安装）"
        exit 1
    fi
}

# 检查 Node.js 版本
check_node_version() {
    if command_exists node; then
        NODE_VERSION=$(node --version | cut -d'v' -f2)
        REQUIRED_VERSION="22.0.0"

        if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$NODE_VERSION" | sort -V | head -n1)" = "$REQUIRED_VERSION" ]; then
            print_success "Node.js 版本符合要求: $NODE_VERSION"
            return 0
        else
            print_warning "Node.js 版本过低: $NODE_VERSION，需要 >= $REQUIRED_VERSION"
            return 1
        fi
    else
        print_error "Node.js 未安装"
        return 1
    fi
}

# 安装 Node.js
install_node() {
    print_header "安装 Node.js"

    if command_exists nvm; then
        print_success "nvm 已安装"
    else
        print_warning "安装 nvm..."
        curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.0/install.sh | bash
        export NVM_DIR="$HOME/.nvm"
        [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"
    fi

    nvm install 22
    nvm use 22
    nvm alias default 22

    print_success "Node.js $(node --version) 安装完成"
}

# 安装全局 npm 包
install_global_packages() {
    print_header "安装全局 CLI"

    if ! command_exists npm; then
        print_error "npm 未安装，无法安装全局 CLI"
        return 1
    fi

    # package:command
    PACKAGES=(
        "openclaw:openclaw"
        "@openclaw/mcporter:mcporter"
        "codex:codex"
        "@anthropic-ai/claude-code:claude"
        "@google/gemini-cli:gemini"
    )

    for entry in "${PACKAGES[@]}"; do
        IFS=':' read -r pkg cmd <<< "$entry"
        if command_exists "$cmd"; then
            print_success "$cmd 已安装"
        else
            print_warning "安装 $pkg..."
            npm install -g "$pkg" || print_error "$pkg 安装失败"
        fi
    done

    print_success "全局 CLI 安装完成"
}

backup_file() {
    local file_path="$1"
    if [ -f "$file_path" ]; then
        local ts
        ts=$(date '+%Y%m%d-%H%M%S')
        cp "$file_path" "${file_path}.bak.${ts}"
        print_warning "已备份: ${file_path}.bak.${ts}"
    fi
}

check_env_placeholders() {
    if [ -f ".env" ]; then
        if grep -n "your_\\|YOUR_" .env >/dev/null 2>&1; then
            print_warning "发现未替换的 .env 占位符，请尽快填写"
            grep -n "your_\\|YOUR_" .env || true
        else
            print_success ".env 已填写（未发现占位符）"
        fi
    fi
}

# 配置环境变量
setup_environment() {
    print_header "配置环境变量"

    if [ -f ".env" ] && [ "$RESET_ENV" -eq 0 ]; then
        print_warning ".env 文件已存在，跳过创建"
        print_warning "请检查 .env 文件中的 API Keys 是否正确配置"
        check_env_placeholders
        return 0
    fi

    if [ -f ".env" ] && [ "$RESET_ENV" -eq 1 ]; then
        backup_file ".env"
        rm -f .env
    fi

    if [ -f ".env.example" ]; then
        cp .env.example .env
        print_warning "已从 .env.example 创建 .env 文件"
        print_warning "⚠️ 请编辑 .env 文件，填入你的实际 API Keys！"
    else
        cat > .env << 'EOF'
# ============================================
# 模型/厂商 API Keys（按需填写）
# ============================================
ARK_API_KEY=your_ark_api_key_here
ZAI_API_KEY=your_zai_api_key_here
Z_AI_API_KEY=your_zai_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
OPENCODE_API_KEY=your_opencode_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here

# ============================================
# 飞书 (Feishu)
# ============================================
FEISHU_APP_ID=your_feishu_app_id_main
FEISHU_APP_SECRET=your_feishu_app_secret_main
FEISHU_APP_ID_TEST=your_feishu_app_id_test
FEISHU_APP_SECRET_TEST=your_feishu_app_secret_test

# ============================================
# Telegram
# ============================================
TELEGRAM_BOT_TOKEN=your_telegram_bot_token

# ============================================
# OpenClaw Gateway
# ============================================
OPENCLAW_GATEWAY_TOKEN=your_gateway_token

EOF
        print_warning "已创建默认 .env 文件"
        print_warning "⚠️ 请编辑 .env 文件，填入你的实际 API Keys！"
    fi

    # 加载环境变量
    export $(cat .env | grep -v '^#' | xargs) 2>/dev/null || true

    check_env_placeholders
    print_success "环境变量配置完成"
}

# 配置 MCP 服务器
setup_mcp_servers() {
    print_header "配置 MCP 服务器"

    if ! command_exists mcporter; then
        print_warning "mcporter 未安装，跳过 MCP 检查"
        return 0
    fi

    # 确保配置目录存在
    mkdir -p "$ROOT_DIR/config"

    # 检查 mcporter 配置
    if [ -f "config/mcporter.json" ]; then
        print_success "发现 mcporter.json 配置"

        # 验证配置
        if mcporter list >/dev/null 2>&1; then
            print_success "MCP 服务器验证通过"
            mcporter list
        else
            print_error "MCP 服务器验证失败，请检查配置和 API Keys"
        fi
    else
        print_warning "未找到 config/mcporter.json，跳过 MCP 配置"
    fi

    print_success "MCP 服务器配置完成"
}

# 配置 Claude Code MCP
setup_claude_mcp() {
    print_header "配置 Claude Code MCP"

    mkdir -p ~/.claude

    # 从仓库配置复制
    if [ -f ".claude/mcp.json" ]; then
        if [ -f ~/.claude/mcp.json ]; then
            backup_file ~/.claude/mcp.json
        fi
        cp .claude/mcp.json ~/.claude/mcp.json
        print_success "已复制 Claude Code MCP 配置"
    else
        # 创建默认配置
        if [ -f ~/.claude/mcp.json ]; then
            print_warning "~/.claude/mcp.json 已存在，跳过创建"
        else
            cat > ~/.claude/mcp.json << 'EOF'
{
  "mcpServers": {
    "zai-mcp-server": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@z_ai/mcp-server"],
      "env": {
        "Z_AI_API_KEY": "your_zai_api_key_here",
        "Z_AI_MODE": "ZHIPU"
      }
    }
  }
}
EOF
            print_warning "已创建默认 Claude Code MCP 配置"
            print_warning "⚠️ 请编辑 ~/.claude/mcp.json，填入你的实际 API Keys！"
        fi
    fi

    print_success "Claude Code MCP 配置完成"
}

# 更新仓库
update_repo() {
    if [ "$UPDATE_REPO" -eq 0 ]; then
        return 0
    fi

    print_header "更新仓库"

    if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
        print_warning "当前目录不是 Git 仓库，跳过更新"
        return 0
    fi

    if ! git diff --quiet || ! git diff --staged --quiet; then
        print_warning "工作区有未提交变更，跳过 git pull"
        return 0
    fi

    print_warning "拉取最新代码..."
    git pull --rebase || print_error "git pull 失败，请手动处理"
}

# 验证安装
verify_installation() {
    print_header "验证安装"

    CHECKS=(
        "node:Node.js"
        "npm:npm"
        "git:Git"
        "openclaw:OpenClaw CLI"
        "mcporter:McPorter"
        "codex:Codex CLI"
        "claude:Claude Code"
        "gemini:Gemini CLI"
    )

    for check in "${CHECKS[@]}"; do
        IFS=':' read -r cmd name <<< "$check"
        if command_exists "$cmd"; then
            version=$($cmd --version 2>/dev/null | head -n1 | tr -d '\n')
            print_success "$name: $version"
        else
            print_error "$name: 未安装"
        fi
    done

    print_success "安装验证完成"
}

# 主函数
main() {
    parse_args "$@"

    print_header "OpenClaw 一键初始化脚本"
    echo ""
    echo "项目名称: OpenClaw AI Assistant Environment"
    echo "主人: 深圳刘家（虾宝宝 🦐）"
    echo "仓库: https://github.com/YOUR_USERNAME/YOUR_REPO"
    echo ""

    # 切到 OpenClaw 根目录
    if [ ! -d "$ROOT_DIR" ]; then
        print_error "未找到 OpenClaw 根目录: $ROOT_DIR"
        print_error "请确认此脚本位于 OpenClaw 仓库中"
        exit 1
    fi

    cd "$ROOT_DIR"

    # 检查是否在正确的目录
    if [ ! -f "openclaw.json" ]; then
        print_error "请在 OpenClaw 根目录运行此脚本"
        print_error "请运行: cd $ROOT_DIR && ./workspace/skills/openclaw-toolbox/scripts/setup.sh"
        exit 1
    fi

    check_prereqs

    update_repo

    if [ "$VERIFY_ONLY" -eq 1 ]; then
        check_node_version || true
        verify_installation
        exit 0
    fi

    # 执行安装步骤
    if [ "$SKIP_NODE" -eq 0 ]; then
        if ! check_node_version; then
            install_node
        fi
    else
        print_warning "跳过 Node.js 安装"
    fi

    if [ "$SKIP_PACKAGES" -eq 0 ]; then
        install_global_packages
    else
        print_warning "跳过全局 CLI 安装"
    fi

    if [ "$SKIP_ENV" -eq 0 ]; then
        setup_environment
    else
        print_warning "跳过 .env 配置"
    fi

    if [ "$SKIP_MCP" -eq 0 ]; then
        setup_mcp_servers
    else
        print_warning "跳过 MCP 配置"
    fi

    if [ "$SKIP_CLAUDE" -eq 0 ]; then
        setup_claude_mcp
    else
        print_warning "跳过 Claude MCP 配置"
    fi

    if [ "$SKIP_VERIFY" -eq 0 ]; then
        verify_installation
    else
        print_warning "跳过安装验证"
    fi

    print_header "初始化完成！"
    echo ""
    echo "🎉 OpenClaw 环境已成功初始化！"
    echo ""
    echo "下一步操作："
    echo "1. 编辑 .env 文件，填入你的 API Keys"
    echo "2. 启动 OpenClaw: openclaw gateway start"
    echo "3. 查看状态: openclaw status"
    echo ""
    echo "详细文档: $ROOT_DIR/workspace/skills/openclaw-setup/SETUP.md"
    echo "🦐 虾宝宝为刘家服务"
    echo ""
}

# 运行主函数
main "$@"
