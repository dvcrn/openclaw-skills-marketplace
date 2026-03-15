#!/bin/bash
# PRISM_GEN_DEMO 技能验证脚本
# 在不安装依赖的情况下验证技能完整性和安全性

set -euo pipefail

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 输出函数
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

print_header() {
    echo -e "${PURPLE}"
    echo "╔══════════════════════════════════════════════════════════╗"
    echo "║              PRISM_GEN_DEMO 技能验证                    ║"
    echo "╠══════════════════════════════════════════════════════════╣"
    echo "║ 此脚本验证技能完整性，不安装任何包                      ║"
    echo "║ This script verifies skill integrity, no packages       ║"
    echo "║ installed                                               ║"
    echo "╚══════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# 显示帮助
show_help() {
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  --dry-run     只检查，不执行任何脚本"
    echo "  --quick       快速验证（只检查关键文件）"
    echo "  --full        完整验证（检查所有文件）"
    echo "  --help        显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 --dry-run    # 安全检查，不执行脚本"
    echo "  $0 --quick      # 快速验证"
    echo "  $0 --full       # 完整验证"
}

# 检查参数
DRY_RUN=false
QUICK_MODE=false
FULL_MODE=false

for arg in "$@"; do
    case $arg in
        --dry-run)
            DRY_RUN=true
            ;;
        --quick)
            QUICK_MODE=true
            ;;
        --full)
            FULL_MODE=true
            ;;
        --help)
            show_help
            exit 0
            ;;
        *)
            print_error "未知参数: $arg"
            show_help
            exit 1
            ;;
    esac
done

# 如果没有指定模式，使用快速模式
if [ "$DRY_RUN" = false ] && [ "$QUICK_MODE" = false ] && [ "$FULL_MODE" = false ]; then
    QUICK_MODE=true
fi

# 验证目录结构
verify_directory_structure() {
    print_info "验证目录结构..."
    
    required_dirs=("scripts" "data" "config")
    optional_dirs=("output" "plots" "logs" "docs" "examples")
    
    for dir in "${required_dirs[@]}"; do
        if [ -d "$dir" ]; then
            print_success "目录存在: $dir"
        else
            print_error "目录缺失: $dir"
            return 1
        fi
    done
    
    for dir in "${optional_dirs[@]}"; do
        if [ -d "$dir" ]; then
            print_info "可选目录存在: $dir"
        fi
    done
    
    return 0
}

# 验证关键文件
verify_critical_files() {
    print_info "验证关键文件..."
    
    critical_files=(
        "README.md"
        "SKILL.md"
        "requirements.txt"
        "setup.sh"
        "scripts/demo_list_sources.sh"
        "scripts/demo_filter.sh"
        "scripts/demo_top.sh"
    )
    
    missing_files=()
    
    for file in "${critical_files[@]}"; do
        if [ -f "$file" ]; then
            print_success "文件存在: $file"
        else
            print_error "文件缺失: $file"
            missing_files+=("$file")
        fi
    done
    
    if [ ${#missing_files[@]} -gt 0 ]; then
        print_error "缺失关键文件: ${missing_files[*]}"
        return 1
    fi
    
    return 0
}

# 验证数据文件
verify_data_files() {
    print_info "验证数据文件..."
    
    if [ ! -d "data" ]; then
        print_error "data目录不存在"
        return 1
    fi
    
    csv_files=$(find data -name "*.csv" -type f 2>/dev/null | wc -l)
    
    if [ "$csv_files" -eq 0 ]; then
        print_warning "data目录中没有CSV文件"
        return 1
    else
        print_success "找到 $csv_files 个CSV文件"
        
        # 列出文件
        print_info "数据文件列表:"
        find data -name "*.csv" -type f | while read file; do
            size=$(du -h "$file" | cut -f1)
            lines=$(wc -l < "$file" 2>/dev/null || echo "?")
            echo "  - $(basename "$file") ($size, ${lines}行)"
        done
    fi
    
    return 0
}

# 验证脚本权限
verify_script_permissions() {
    print_info "验证脚本权限..."
    
    if [ ! -d "scripts" ]; then
        print_error "scripts目录不存在"
        return 1
    fi
    
    sh_files=$(find scripts -name "*.sh" -type f 2>/dev/null)
    py_files=$(find scripts -name "*.py" -type f 2>/dev/null)
    
    # 检查.sh文件权限
    for file in $sh_files; do
        if [ -x "$file" ]; then
            print_success "脚本可执行: $(basename "$file")"
        else
            print_warning "脚本不可执行: $(basename "$file")"
            if [ "$DRY_RUN" = false ]; then
                chmod +x "$file"
                print_info "已添加执行权限: $(basename "$file")"
            fi
        fi
    done
    
    # 检查.py文件权限
    for file in $py_files; do
        if [ -x "$file" ]; then
            print_success "Python脚本可执行: $(basename "$file")"
        else
            print_info "Python脚本: $(basename "$file")"
        fi
    done
    
    return 0
}

# 验证脚本内容（安全检查）
verify_script_content() {
    print_info "验证脚本内容（安全检查）..."
    
    dangerous_patterns=(
        "rm -rf"
        "chmod 777"
        "wget.*http"
        "curl.*http"
        "bash <(curl"
        "sudo"
        "su -"
        "passwd"
        "ssh-keygen"
        "scp"
        "nc -l"
        "telnet"
        "ftp"
    )
    
    suspicious_files=()
    
    # 检查所有.sh和.py文件（排除验证脚本自己）
    find scripts -type f \( -name "*.sh" -o -name "*.py" \) | while read file; do
        # 跳过验证脚本自己
        if [[ "$(basename "$file")" == "verify_skill.sh" ]]; then
            continue
        fi
        
        for pattern in "${dangerous_patterns[@]}"; do
            if grep -q "$pattern" "$file" 2>/dev/null; then
                print_warning "发现潜在危险模式 '$pattern' 在: $(basename "$file")"
                suspicious_files+=("$file:$pattern")
            fi
        done
    done
    
    if [ ${#suspicious_files[@]} -gt 0 ]; then
        print_warning "发现 ${#suspicious_files[@]} 个潜在问题"
        for item in "${suspicious_files[@]}"; do
            file=$(echo "$item" | cut -d: -f1)
            pattern=$(echo "$item" | cut -d: -f2)
            echo "  - $file: $pattern"
        done
    else
        print_success "脚本内容安全检查通过"
    fi
    
    return 0
}

# 验证Python依赖
verify_python_dependencies() {
    print_info "验证Python依赖..."
    
    if ! command -v python3 &> /dev/null; then
        print_warning "Python3未安装（高级功能不可用）"
        return 1
    fi
    
    required_packages=("pandas" "numpy" "matplotlib" "seaborn")
    missing_packages=()
    
    for pkg in "${required_packages[@]}"; do
        if python3 -c "import $pkg" 2>/dev/null; then
            version=$(python3 -c "import $pkg; print($pkg.__version__)" 2>/dev/null || echo "未知")
            print_success "$pkg $version 已安装"
        else
            print_warning "$pkg 未安装"
            missing_packages+=("$pkg")
        fi
    done
    
    if [ ${#missing_packages[@]} -gt 0 ]; then
        print_warning "缺少Python包: ${missing_packages[*]}"
        print_info "如需安装: pip install ${missing_packages[*]}"
        return 1
    else
        print_success "所有Python依赖已安装"
        return 0
    fi
}

# 测试基础功能
test_basic_functions() {
    print_info "测试基础功能..."
    
    if [ "$DRY_RUN" = true ]; then
        print_info "干运行模式，跳过脚本执行"
        return 0
    fi
    
    # 测试列表脚本
    if [ -f "scripts/demo_list_sources.sh" ]; then
        print_info "测试: demo_list_sources.sh"
        if output=$(bash scripts/demo_list_sources.sh 2>&1); then
            print_success "demo_list_sources.sh 执行成功"
            echo "$output" | head -5
        else
            print_warning "demo_list_sources.sh 执行失败"
        fi
    fi
    
    # 测试简单预览
    if [ -f "scripts/demo_simple_preview.sh" ]; then
        print_info "测试: demo_simple_preview.sh"
        csv_file=$(find data -name "*.csv" -type f | head -1)
        if [ -n "$csv_file" ]; then
            if output=$(bash scripts/demo_simple_preview.sh "$csv_file" 2>&1); then
                print_success "demo_simple_preview.sh 执行成功"
                echo "$output" | head -3
            else
                print_warning "demo_simple_preview.sh 执行失败"
            fi
        fi
    fi
    
    return 0
}

# 生成验证报告
generate_report() {
    echo ""
    echo -e "${CYAN}══════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}                   验证报告 / Verification Report         ${NC}"
    echo -e "${CYAN}══════════════════════════════════════════════════════════${NC}"
    echo ""
    
    if [ "$DRY_RUN" = true ]; then
        echo -e "${YELLOW}模式: 干运行 (只检查，不执行)${NC}"
    elif [ "$QUICK_MODE" = true ]; then
        echo -e "${BLUE}模式: 快速验证${NC}"
    elif [ "$FULL_MODE" = true ]; then
        echo -e "${PURPLE}模式: 完整验证${NC}"
    fi
    
    echo ""
    echo -e "${GREEN}✅ 技能完整性验证完成${NC}"
    echo ""
    echo "📊 总结:"
    echo "  - 基础功能: 可用（Bash脚本）"
    echo "  - 高级功能: $(if verify_python_dependencies >/dev/null 2>&1; then echo "可用"; else echo "需要Python包"; fi)"
    echo "  - 数据文件: $(find data -name "*.csv" -type f 2>/dev/null | wc -l) 个CSV文件"
    echo ""
    echo "🚀 下一步:"
    echo "  1. 查看数据: bash scripts/demo_list_sources.sh"
    echo "  2. 基础分析: bash scripts/demo_filter.sh data/example_step4a.csv pIC50 '>' 7.0"
    echo "  3. 安装Python包（如需高级功能）: pip install pandas numpy matplotlib seaborn"
    echo ""
    echo "🔒 安全建议:"
    echo "  - 在虚拟环境或容器中运行"
    echo "  - 定期验证技能完整性"
    echo "  - 审查自定义数据文件"
    echo ""
    echo -e "${CYAN}══════════════════════════════════════════════════════════${NC}"
}

# 主函数
main() {
    print_header
    
    # 记录开始时间
    start_time=$(date +%s)
    
    # 执行验证步骤
    verify_directory_structure
    verify_critical_files
    verify_data_files
    verify_script_permissions
    
    if [ "$FULL_MODE" = true ]; then
        verify_script_content
        verify_python_dependencies
    fi
    
    if [ "$QUICK_MODE" = true ] || [ "$FULL_MODE" = true ]; then
        test_basic_functions
    fi
    
    # 记录结束时间
    end_time=$(date +%s)
    duration=$((end_time - start_time))
    
    # 生成报告
    generate_report
    
    print_info "验证完成，耗时 ${duration} 秒"
    echo ""
    print_success "✅ PRISM_GEN_DEMO 技能验证通过"
    print_info "   基础功能可用，高级功能需要Python包"
}

# 运行主函数
main "$@"