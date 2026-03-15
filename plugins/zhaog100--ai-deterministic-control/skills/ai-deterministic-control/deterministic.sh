#!/bin/bash
# AI 确定性控制工具 - CLI 入口
# 版权声明：MIT License | Copyright (c) 2026 思捷娅科技
# GitHub: https://github.com/zhaog100/openclaw-skills

set -e

# 获取脚本目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/deterministic.py"
CONSISTENCY_SCRIPT="$SCRIPT_DIR/consistency.py"

# 显示帮助
show_help() {
    cat << HELP
AI 确定性控制工具 v1.0.0

用法:
    deterministic <command> [arguments]

命令:
    temperature <value>    设置温度参数（0.0-2.0）
    temp <value>           同上（简写）
    check <outputs...>     检查输出一致性（多个输出）
    seed <value>           设置随机种子
    config                 显示当前配置
    help                   显示此帮助信息

温度模式:
    0.0-0.3                高度确定性（代码/配置生成）
    0.3-0.7                平衡模式（常规对话）
    0.7-1.0                创造性模式（创意写作）
    1.0-2.0                高创造性模式（头脑风暴）

示例:
    deterministic temperature 0.2    # 设置高度确定性模式
    deterministic check "输出1" "输出2" "输出3"  # 检查一致性
    deterministic seed 12345        # 设置随机种子
    deterministic config            # 查看配置

文档:
    GitHub: https://github.com/zhaog100/openclaw-skills
    ClawHub: https://clawhub.com

版权:
    MIT License - Copyright (c) 2026 思捷娅科技
HELP
}

# 检查 Python 是否可用
check_python() {
    if ! command -v python3 &> /dev/null; then
        echo "错误: 未找到 Python 3"
        echo "请安装 Python 3.8+ 后重试"
        exit 1
    fi
}

# 主逻辑
main() {
    check_python
    
    if [ $# -eq 0 ]; then
        show_help
        exit 0
    fi
    
    command="$1"
    shift
    
    case "$command" in
        temperature|temp)
            if [ $# -eq 0 ]; then
                echo "错误: 请提供温度值（0.0-2.0）"
                exit 1
            fi
            python3 -c "
import sys
sys.path.insert(0, '$SCRIPT_DIR')
from deterministic import set_temperature
result = set_temperature($1)
print(f'✅ {result[\"message\"]}')
print(f'   温度: {result[\"temperature\"]}')
print(f'   模式: {result[\"mode\"]}')
"
            ;;
        
        check)
            if [ $# -lt 2 ]; then
                echo "错误: 至少需要2个输出进行一致性检查"
                exit 1
            fi
            # 将参数转换为 Python 列表
            outputs=$(printf "'%s'," "$@")
            outputs="[${outputs%,}]"
            python3 -c "
import sys
sys.path.insert(0, '$SCRIPT_DIR')
from consistency import check_consistency
result = check_consistency($outputs)
print(f'✅ 一致性检查完成')
print(f'   输出数量: {result[\"output_count\"]}')
print(f'   平均相似度: {result[\"average_similarity\"]}%')
print(f'   一致性级别: {result[\"consistency_level\"]}')
print(f'   建议: {result[\"recommendation\"]}')
"
            ;;
        
        seed)
            if [ $# -eq 0 ]; then
                echo "错误: 请提供随机种子值"
                exit 1
            fi
            python3 -c "
import sys
sys.path.insert(0, '$SCRIPT_DIR')
from deterministic import set_seed
result = set_seed($1)
print(f'✅ {result[\"message\"]}')
"
            ;;
        
        config)
            python3 -c "
import sys
sys.path.insert(0, '$SCRIPT_DIR')
from deterministic import get_temperature, get_seed
temp = get_temperature()
seed = get_seed()
print('📋 当前配置:')
print(f'   温度: {temp[\"temperature\"]} ({temp[\"mode\"]})')
print(f'   种子: {seed if seed else \"未设置\"}')
"
            ;;
        
        help|--help|-h)
            show_help
            ;;
        
        *)
            echo "错误: 未知命令 '$command'"
            echo "运行 'deterministic help' 查看帮助"
            exit 1
            ;;
    esac
}

main "$@"
