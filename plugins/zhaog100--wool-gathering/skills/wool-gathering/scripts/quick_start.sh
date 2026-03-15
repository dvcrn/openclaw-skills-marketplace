#!/bin/bash
# 价格监控系统 - 快速启动脚本

echo "🌾 薅羊毛综合技能 - 价格监控系统"
echo "=================================="

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="${SCRIPT_DIR}/../assets/config_template.json"

cd "$SCRIPT_DIR"

case "$1" in
    --monitor|-m)
        echo "🚀 启动价格监控..."
        python3 test_price_monitor.py --config "$CONFIG_FILE" --monitor
        ;;

    --add|-a)
        if [ -z "$2" ] || [ -z "$3" ]; then
            echo "用法: $0 --add 商品名称 商品链接"
            exit 1
        fi
        python3 test_price_monitor.py --config "$CONFIG_FILE" --add --name "$2" --url "$3"
        ;;

    --history|-h)
        if [ -z "$2" ]; then
            echo "用法: $0 --history 商品ID [天数]"
            exit 1
        fi
        DAYS=${3:-7}
        python3 test_price_monitor.py --config "$CONFIG_FILE" --history "$2" --days "$DAYS"
        ;;

    --test|-t)
        echo "🧪 测试模式 - 使用示例数据"
        python3 test_price_monitor.py --config "$CONFIG_FILE" --monitor
        ;;

    --help|*)
        echo "用法: $0 [选项]"
        echo ""
        echo "选项:"
        echo "  -m, --monitor        启动价格监控"
        echo "  -a, --add 名称 链接  添加监控商品"
        echo "  -h, --history ID [天数]  查看价格历史"
        echo "  -t, --test          测试模式"
        echo "      --help          显示帮助"
        echo ""
        echo "示例:"
        echo "  $0 --monitor                    # 监控所有商品"
        echo "  $0 --add 'iPhone' 'https://...'  # 添加商品"
        echo "  $0 --history 100012043978 30    # 查看30天历史"
        ;;

esac
