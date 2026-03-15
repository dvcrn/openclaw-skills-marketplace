#!/bin/bash
# 打包前的完整性检查

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
    echo "║            ClawHub 上传前完整性检查                     ║"
    echo "╠══════════════════════════════════════════════════════════╣"
    echo "║ 检查技能包是否符合ClawHub上传标准                       ║"
    echo "╚══════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

print_section() {
    echo ""
    echo -e "${CYAN}=== $1 ===${NC}"
}

check_file_exists() {
    local file="$1"
    local description="$2"
    
    if [ -f "$file" ]; then
        size=$(du -h "$file" | cut -f1)
        echo -e "${GREEN}✅ $description: $file ($size)${NC}"
        return 0
    else
        echo -e "${RED}❌ $description: $file (缺失)${NC}"
        return 1
    fi
}

check_directory_exists() {
    local dir="$1"
    local description="$2"
    
    if [ -d "$dir" ]; then
        file_count=$(find "$dir" -type f 2>/dev/null | wc -l)
        echo -e "${GREEN}✅ $description: $dir ($file_count 个文件)${NC}"
        return 0
    else
        echo -e "${RED}❌ $description: $dir (缺失)${NC}"
        return 1
    fi
}

check_file_content() {
    local file="$1"
    local pattern="$2"
    local description="$3"
    
    if [ -f "$file" ]; then
        if grep -q "$pattern" "$file" 2>/dev/null; then
            echo -e "${GREEN}✅ $description: 包含 '$pattern'${NC}"
            return 0
        else
            echo -e "${YELLOW}⚠️  $description: 不包含 '$pattern'${NC}"
            return 1
        fi
    else
        echo -e "${RED}❌ $description: 文件不存在${NC}"
        return 1
    fi
}

check_no_problematic_content() {
    local file="$1"
    local pattern="$2"
    local description="$3"
    
    if [ -f "$file" ]; then
        if grep -q "$pattern" "$file" 2>/dev/null; then
            echo -e "${RED}❌ $description: 包含 '$pattern' (需要修复)${NC}"
            return 1
        else
            echo -e "${GREEN}✅ $description: 不包含 '$pattern'${NC}"
            return 0
        fi
    else
        echo -e "${RED}❌ $description: 文件不存在${NC}"
        return 1
    fi
}

check_version_consistency() {
    print_section "版本一致性检查"
    
    # 从VERSION文件获取版本
    if [ -f "VERSION" ]; then
        version_line=$(grep -i "version:" VERSION | head -1)
        version=$(echo "$version_line" | grep -o "[0-9]\+\.[0-9]\+\.[0-9]\+" || echo "")
        
        if [ -n "$version" ]; then
            echo -e "${GREEN}✅ 主版本号: $version${NC}"
            
            # 检查所有SKILL文件中的版本
            skill_files=$(find . -name "SKILL*.md" -type f)
            inconsistent=0
            
            for file in $skill_files; do
                file_version=$(grep -i "version:" "$file" | head -1 | grep -o '"[^"]*"' | tr -d '"' | grep -o "[0-9]\+\.[0-9]\+\.[0-9]\+" || echo "")
                if [ "$file_version" = "$version" ]; then
                    echo -e "${GREEN}  ✅ $(basename "$file"): $file_version${NC}"
                else
                    echo -e "${RED}  ❌ $(basename "$file"): $file_version (应为: $version)${NC}"
                    inconsistent=1
                fi
            done
            
            if [ $inconsistent -eq 0 ]; then
                return 0
            else
                return 1
            fi
        else
            echo -e "${RED}❌ 无法从VERSION文件解析版本号${NC}"
            return 1
        fi
    else
        echo -e "${RED}❌ VERSION文件不存在${NC}"
        return 1
    fi
}

check_documentation_consistency() {
    print_section "文档一致性检查"
    
    # 检查是否还有错误的"11个真实"描述
    problematic_count=$(grep -r "11个真实的PRISM预计算结果文件" . --include="*.md" 2>/dev/null | grep -v "FIXES_SUMMARY.md" | wc -l)
    
    if [ "$problematic_count" -eq 0 ]; then
        echo -e "${GREEN}✅ 文档描述准确（无错误的'11个真实'描述）${NC}"
    else
        echo -e "${RED}❌ 发现 $problematic_count 处错误的'11个真实'描述${NC}"
        grep -r "11个真实的PRISM预计算结果文件" . --include="*.md" 2>/dev/null | grep -v "FIXES_SUMMARY.md"
        return 1
    fi
    
    # 检查网络依赖声明
    wrong_network_count=$(grep -r "无网络依赖\|No network dependencies" . --include="*.md" 2>/dev/null | grep -v "无需网络连接\|No network connection required" | grep -v "安装需要网络\|Network required for installation" | grep -v "FIXES_SUMMARY.md" | wc -l)
    
    if [ "$wrong_network_count" -eq 0 ]; then
        echo -e "${GREEN}✅ 网络依赖声明准确${NC}"
    else
        echo -e "${RED}❌ 发现 $wrong_network_count 处错误的网络依赖声明${NC}"
        grep -r "无网络依赖\|No network dependencies" . --include="*.md" 2>/dev/null | grep -v "无需网络连接\|No network connection required" | grep -v "安装需要网络\|Network required for installation" | grep -v "FIXES_SUMMARY.md"
        return 1
    fi
    
    return 0
}

check_security_files() {
    print_section "安全文件检查"
    
    check_file_exists "SECURITY.md" "安全声明文件"
    security_exists=$?
    
    check_file_exists "scripts/verify_skill.sh" "验证脚本"
    verify_exists=$?
    
    check_file_exists "scripts/list_scripts_info.sh" "脚本信息文件"
    info_exists=$?
    
    # 检查setup.sh中的安全警告
    check_file_content "setup.sh" "安全警告 / Security Notice" "安装脚本安全警告"
    setup_warning=$?
    
    if [ $security_exists -eq 0 ] && [ $verify_exists -eq 0 ] && [ $info_exists -eq 0 ] && [ $setup_warning -eq 0 ]; then
        return 0
    else
        return 1
    fi
}

check_script_permissions() {
    print_section "脚本权限检查"
    
    # 检查所有.sh文件是否有执行权限
    sh_files=$(find scripts -name "*.sh" -type f)
    total_sh=$(echo "$sh_files" | wc -l)
    executable_sh=0
    non_executable_sh=0
    
    for file in $sh_files; do
        if [ -x "$file" ]; then
            executable_sh=$((executable_sh + 1))
        else
            non_executable_sh=$((non_executable_sh + 1))
            echo -e "${YELLOW}⚠️  不可执行: $(basename "$file")${NC}"
        fi
    done
    
    if [ $non_executable_sh -eq 0 ]; then
        echo -e "${GREEN}✅ 所有 $total_sh 个.sh脚本都可执行${NC}"
        return 0
    else
        echo -e "${RED}❌ $non_executable_sh/$total_sh 个.sh脚本不可执行${NC}"
        return 1
    fi
}

check_data_files() {
    print_section "数据文件检查"
    
    check_directory_exists "data" "数据目录"
    data_dir_exists=$?
    
    if [ $data_dir_exists -eq 0 ]; then
        csv_files=$(find data -name "*.csv" -type f 2>/dev/null)
        csv_count=$(echo "$csv_files" | wc -l)
        
        if [ "$csv_count" -gt 0 ]; then
            echo -e "${GREEN}✅ 数据目录包含 $csv_count 个CSV文件${NC}"
            
            # 检查示例文件是否存在
            if find data -name "example_step4a.csv" -type f 2>/dev/null | grep -q .; then
                echo -e "${GREEN}✅ 示例文件存在: example_step4a.csv${NC}"
            else
                echo -e "${YELLOW}⚠️  示例文件不存在: example_step4a.csv${NC}"
            fi
            
            return 0
        else
            echo -e "${RED}❌ 数据目录为空${NC}"
            return 1
        fi
    else
        return 1
    fi
}

run_functional_tests() {
    print_section "功能测试"
    
    echo -e "${BLUE}运行基础功能测试...${NC}"
    
    # 测试列表功能
    if bash scripts/demo_list_sources.sh 2>&1 | grep -q "可用数据源"; then
        echo -e "${GREEN}✅ 基础功能测试通过: demo_list_sources.sh${NC}"
    else
        echo -e "${YELLOW}⚠️  基础功能测试警告: demo_list_sources.sh${NC}"
    fi
    
    # 测试验证脚本
    if bash scripts/verify_skill.sh --dry-run 2>&1 | grep -q "技能完整性验证完成"; then
        echo -e "${GREEN}✅ 验证脚本测试通过: verify_skill.sh --dry-run${NC}"
    else
        echo -e "${YELLOW}⚠️  验证脚本测试警告${NC}"
    fi
    
    # 测试安装脚本（不实际安装）
    if timeout 5 bash setup.sh --help 2>&1 | grep -q "PRISM_GEN_DEMO"; then
        echo -e "${GREEN}✅ 安装脚本测试通过${NC}"
    else
        echo -e "${YELLOW}⚠️  安装脚本测试警告${NC}"
    fi
    
    return 0
}

generate_report() {
    echo ""
    echo -e "${PURPLE}══════════════════════════════════════════════════════════${NC}"
    echo -e "${PURPLE}                   检查完成报告                           ${NC}"
    echo -e "${PURPLE}══════════════════════════════════════════════════════════${NC}"
    echo ""
    
    local version="未知"
    if [ -f "VERSION" ]; then
        version_line=$(grep -i "version:" VERSION | head -1)
        version=$(echo "$version_line" | grep -o "[0-9]\+\.[0-9]\+\.[0-9]\+" || echo "未知")
    fi
    
    echo -e "${CYAN}技能包信息:${NC}"
    echo "  - 名称: PRISM_GEN_DEMO"
    echo "  - 版本: $version"
    echo "  - 检查时间: $(date)"
    echo ""
    
    echo -e "${GREEN}✅ 检查项目:${NC}"
    echo "  1. 版本一致性"
    echo "  2. 文档准确性"
    echo "  3. 安全文件完整性"
    echo "  4. 脚本权限"
    echo "  5. 数据文件"
    echo "  6. 功能测试"
    echo ""
    
    echo -e "${YELLOW}📋 上传前建议:${NC}"
    echo "  1. 确保所有测试通过"
    echo "  2. 更新CHANGELOG.md记录修复"
    echo "  3. 运行 package.sh 创建发布包"
    echo "  4. 在ClawHub上传时说明安全修复"
    echo ""
    
    echo -e "${BLUE}🚀 下一步:${NC}"
    echo "  # 创建发布包"
    echo "  bash package.sh"
    echo ""
    echo "  # 查看修复总结"
    echo "  cat FIXES_SUMMARY.md"
    echo ""
    
    echo -e "${PURPLE}══════════════════════════════════════════════════════════${NC}"
}

main() {
    print_header
    
    local errors=0
    local warnings=0
    
    # 运行检查
    check_version_consistency || errors=$((errors + 1))
    check_documentation_consistency || errors=$((errors + 1))
    check_security_files || errors=$((errors + 1))
    check_script_permissions || warnings=$((warnings + 1))
    check_data_files || errors=$((errors + 1))
    run_functional_tests || warnings=$((warnings + 1))
    
    # 生成报告
    generate_report
    
    # 总结
    echo ""
    if [ $errors -eq 0 ] && [ $warnings -eq 0 ]; then
        echo -e "${GREEN}🎉 所有检查通过！可以安全上传到ClawHub。${NC}"
        exit 0
    elif [ $errors -eq 0 ]; then
        echo -e "${YELLOW}⚠️  有 $warnings 个警告，但无错误。可以上传，但建议修复警告。${NC}"
        exit 0
    else
        echo -e "${RED}❌ 有 $errors 个错误和 $warnings 个警告。请修复错误后再上传。${NC}"
        exit 1
    fi
}

main "$@"