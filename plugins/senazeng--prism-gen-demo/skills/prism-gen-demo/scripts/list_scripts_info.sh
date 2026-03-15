#!/bin/bash
# 列出所有脚本的功能和依赖信息

set -euo pipefail

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${PURPLE}"
    echo "╔══════════════════════════════════════════════════════════╗"
    echo "║              PRISM_GEN_DEMO 脚本目录                    ║"
    echo "╠══════════════════════════════════════════════════════════╣"
    echo "║ 列出所有脚本的功能、依赖和权限信息                      ║"
    echo "╚══════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

print_script_info() {
    local script="$1"
    local category="$2"
    local dependencies="$3"
    local description="$4"
    
    echo -e "${CYAN}脚本:${NC} $script"
    echo -e "${BLUE}类别:${NC} $category"
    echo -e "${GREEN}依赖:${NC} $dependencies"
    echo -e "${YELLOW}描述:${NC} $description"
    
    # 检查文件是否存在
    if [ -f "scripts/$script" ]; then
        if [ -x "scripts/$script" ]; then
            echo -e "${GREEN}状态:${NC} 可执行"
        else
            echo -e "${YELLOW}状态:${NC} 不可执行"
        fi
        
        # 显示文件大小
        size=$(du -h "scripts/$script" | cut -f1)
        lines=$(wc -l < "scripts/$script" 2>/dev/null || echo "?")
        echo -e "${BLUE}信息:${NC} $size, ${lines}行"
    else
        echo -e "${RED}状态:${NC} 文件不存在"
    fi
    
    echo ""
}

main() {
    print_header
    
    echo -e "${GREEN}=== 基础功能脚本（无需Python，完全离线） ===${NC}"
    echo ""
    
    print_script_info \
        "demo_list_sources.sh" \
        "数据管理" \
        "Bash, awk, grep" \
        "列出所有可用的CSV数据文件"
    
    print_script_info \
        "demo_simple_preview.sh" \
        "数据预览" \
        "Bash, head, wc" \
        "快速预览CSV文件的前几行和基本信息"
    
    print_script_info \
        "demo_filter.sh" \
        "数据筛选" \
        "Bash, awk, grep" \
        "基于单条件筛选CSV数据"
    
    print_script_info \
        "demo_top.sh" \
        "数据排序" \
        "Bash, sort, head" \
        "获取Top N排序结果"
    
    echo -e "${YELLOW}=== 高级功能脚本（需要Python包） ===${NC}"
    echo ""
    
    print_script_info \
        "demo_plot_distribution.sh" \
        "数据可视化" \
        "Python, pandas, matplotlib" \
        "生成分布图（直方图+密度曲线）"
    
    print_script_info \
        "demo_plot_scatter.sh" \
        "数据可视化" \
        "Python, pandas, matplotlib, seaborn" \
        "生成散点图（含趋势线和统计检验）"
    
    print_script_info \
        "demo_plot_boxplot.sh" \
        "数据可视化" \
        "Python, pandas, matplotlib, seaborn" \
        "生成箱线图"
    
    print_script_info \
        "demo_correlation.sh" \
        "数据分析" \
        "Python, pandas, scipy" \
        "计算相关性系数和统计显著性"
    
    echo -e "${BLUE}=== 工具脚本 ===${NC}"
    echo ""
    
    print_script_info \
        "verify_skill.sh" \
        "系统工具" \
        "Bash" \
        "验证技能完整性和安全性"
    
    print_script_info \
        "list_scripts_info.sh" \
        "系统工具" \
        "Bash" \
        "列出所有脚本信息（本脚本）"
    
    print_script_info \
        "test_fixed.sh" \
        "测试工具" \
        "Bash" \
        "运行固定测试用例"
    
    print_script_info \
        "test_visualization.sh" \
        "测试工具" \
        "Python, pandas, matplotlib" \
        "测试可视化功能"
    
    echo -e "${PURPLE}=== 总结 ===${NC}"
    echo ""
    
    # 统计脚本数量
    total_scripts=$(find scripts -name "*.sh" -o -name "*.py" | wc -l)
    bash_scripts=$(find scripts -name "*.sh" | wc -l)
    python_scripts=$(find scripts -name "*.py" | wc -l)
    
    echo -e "${CYAN}脚本统计:${NC}"
    echo "  - 总脚本数: $total_scripts"
    echo "  - Bash脚本: $bash_scripts (基础功能，离线可用)"
    echo "  - Python脚本: $python_scripts (高级功能，需要Python包)"
    echo ""
    
    echo -e "${GREEN}使用建议:${NC}"
    echo "  1. 首先运行基础功能脚本验证数据"
    echo "  2. 如需可视化，安装Python包后使用高级脚本"
    echo "  3. 定期运行 verify_skill.sh 检查完整性"
    echo ""
    
    echo -e "${YELLOW}快速开始:${NC}"
    echo "  # 查看可用数据"
    echo "  bash scripts/demo_list_sources.sh"
    echo ""
    echo "  # 快速预览示例数据"
    echo "  bash scripts/demo_simple_preview.sh data/example_step4a.csv"
    echo ""
    echo "  # 筛选高活性分子"
    echo "  bash scripts/demo_filter.sh data/example_step4a.csv pIC50 '>' 7.0"
}

main "$@"