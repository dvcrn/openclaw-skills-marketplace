#!/bin/bash
# AI Agent Security Scanner Wrapper
# 用法: ./scan.sh [选项]

SCANNER_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# 激活虚拟环境
cd "$SCANNER_DIR" || exit 1
source venv/bin/activate

# 默认参数
VERBOSE="-v"
OUTPUT=""
HTML=""
FEISHU=false
LLM=false
LLM_PROVIDER="zhipu"

# 解析参数
while [[ $# -gt 0 ]]; do
    case $1 in
        -o|--output)
            OUTPUT="--output $2"
            shift 2
            ;;
        --html)
            HTML="--html $2"
            shift 2
            ;;
        --feishu)
            FEISHU=true
            shift
            ;;
        --llm)
            LLM=true
            shift
            ;;
        --llm-provider)
            LLM_PROVIDER="$2"
            shift 2
            ;;
        -q|--quiet)
            VERBOSE=""
            shift
            ;;
        discover|check-apikey|check-skill)
            COMMAND="$1"
            shift
            ;;
        *)
            shift
            ;;
    esac
done

# 构建命令
if [[ -n "$COMMAND" ]]; then
    CMD="aascan $COMMAND $VERBOSE"
else
    CMD="aascan scan $VERBOSE $OUTPUT $HTML"
    
    if $FEISHU; then
        CMD="$CMD --feishu --feishu-title 'AI Agent 安全扫描报告 - $(date +%Y-%m-%d)'"
    fi
    
    if $LLM; then
        CMD="$CMD --llm --llm-provider $LLM_PROVIDER"
    fi
fi

# 执行扫描
echo "🛡️ AI Agent Security Scanner"
echo "命令: $CMD"
echo ""

eval "$CMD"
