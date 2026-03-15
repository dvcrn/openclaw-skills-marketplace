#!/bin/bash

# YiDun Defense - Smart Defense Script
# 易盾智能加固脚本 - 支持多平台自动识别

set -e

# 配置
YIDUN_DIR="$HOME/.yidun-defense"
TOOL_JAR="$YIDUN_DIR/NHPProtect.jar"
CONFIG_FILE="$YIDUN_DIR/config.ini"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${CYAN}[STEP]${NC} $1"
}

# 显示使用帮助
show_usage() {
    echo "易盾智能加固工具"
    echo ""
    echo "用法:"
    echo "  $0 <file>              # 自动识别文件类型并加固"
    echo "  $0 <file> --auto       # 完全自动模式（不询问）"
    echo "  $0 <file> --platform <type>   # 指定平台类型"
    echo "  $0 --help              # 显示帮助信息"
    echo ""
    echo "支持的文件类型:"
    echo "  .apk      - Android APK"
    echo "  .aab      - Android AAB"
    echo "  .ipa      - iOS IPA"
    echo "  .xcarchive - iOS xcarchive"
    echo "  .hap      - 鸿蒙 HAP"
    echo "  .app      - 鸿蒙/macOS APP"
    echo "  .zip      - H5/SDK/SO（需进一步识别）"
    echo "  .exe      - Windows 应用"
    echo ""
    echo "平台类型:"
    echo "  android   - Android 平台"
    echo "  ios       - iOS 平台"
    echo "  harmony   - 鸿蒙平台"
    echo "  h5        - H5/小程序"
    echo "  sdk       - SDK/组件"
    echo "  pc        - PC 应用"
    echo ""
    echo "示例:"
    echo "  $0 /path/to/app.apk"
    echo "  $0 /path/to/game.ipa --platform ios"
    echo "  $0 /path/to/test.hap --auto"
    echo ""
}

# 检测文件类型
detect_file_type() {
    local file="$1"
    local extension="${file##*.}"

    case "$extension" in
        apk)
            echo "android_apk"
            ;;
        aab)
            echo "android_aab"
            ;;
        ipa)
            echo "ios_ipa"
            ;;
        xcarchive)
            echo "ios_xcarchive"
            ;;
        hap)
            echo "harmony_hap"
            ;;
        app)
            # 需要进一步判断是鸿蒙还是 macOS
            if [[ "$OSTYPE" == "darwin"* ]]; then
                echo "harmony_or_mac"
            else
                echo "harmony_app"
            fi
            ;;
        zip)
            echo "zip_unknown"
            ;;
        exe)
            echo "pc_windows"
            ;;
        *)
            echo "unknown"
            ;;
    esac
}

# 交互式询问平台
ask_platform() {
    echo ""
    echo -e "${CYAN}=== 选择加固平台 ===${NC}"
    echo "1) Android"
    echo "2) iOS"
    echo "3) 鸿蒙"
    echo "4) H5/小程序"
    echo "5) SDK/组件"
    echo "6) PC 应用"
    echo ""
    read -p "请选择平台 [1-6]: " platform_choice

    case "$platform_choice" in
        1) echo "android" ;;
        2) echo "ios" ;;
        3) echo "harmony" ;;
        4) echo "h5" ;;
        5) echo "sdk" ;;
        6) echo "pc" ;;
        *) echo "android" ;;  # 默认 Android
    esac
}

# 交互式询问引擎类型
ask_engine_type() {
    local platform="$1"

    echo ""
    echo -e "${CYAN}=== 选择应用类型 ===${NC}"
    echo "1) 普通应用/整包"
    echo "2) Unity 引擎"
    echo "3) Cocos 引擎"
    echo "4) UE 引擎（Unreal）"
    echo "5) Laya 引擎"
    echo ""
    read -p "请选择类型 [1-5]: " engine_choice

    case "$engine_choice" in
        1) echo "normal" ;;
        2) echo "unity" ;;
        3) echo "cocos" ;;
        4) echo "ue" ;;
        5) echo "laya" ;;
        *) echo "normal" ;;  # 默认普通应用
    esac
}

# 询问是否需要签名
ask_sign_option() {
    local platform="$1"

    echo ""
    read -p "是否需要自动签名？[y/N]: " sign_choice

    case "$sign_choice" in
        [Yy]* ) echo "yes" ;;
        * ) echo "no" ;;
    esac
}

# 询问是否需要对齐（Android）
ask_align_option() {
    echo ""
    read -p "是否需要 zipalign 对齐？（建议）[Y/n]: " align_choice

    case "$align_choice" in
        [Nn]* ) echo "no" ;;
        * ) echo "yes" ;;  # 默认 yes
    esac
}

# 询问是否需要 DEX 加密（Android）
ask_dex_option() {
    echo ""
    read -p "是否需要 DEX 加密？[y/N]: " dex_choice

    case "$dex_choice" in
        [Yy]* ) echo "yes" ;;
        * ) echo "no" ;;
    esac
}

# 构建 Android 加固参数
build_android_params() {
    local file="$1"
    local engine="$2"
    local auto_mode="$3"
    local params="-yunconfig"

    # 引擎特定参数
    case "$engine" in
        unity)
            # Unity 不需要额外参数，使用默认
            ;;
        cocos)
            params="$params -cocos"
            ;;
        ue)
            params="$params -ue"
            ;;
        laya)
            params="$params -laya"
            ;;
        normal)
            params="$params -fullapk"
            ;;
    esac

    # 交互式询问选项（非自动模式）
    if [ "$auto_mode" != "true" ]; then
        # 对齐选项
        if [ "$(ask_align_option)" = "yes" ]; then
            params="$params -zipalign"
        fi

        # 签名选项
        if [ "$(ask_sign_option android)" = "yes" ]; then
            params="$params -apksign"
        fi

        # DEX 加密（仅普通应用）
        if [ "$engine" = "normal" ]; then
            if [ "$(ask_dex_option)" = "yes" ]; then
                params="$params -dex -antirepack"
            fi
        fi
    else
        # 自动模式：使用推荐配置
        params="$params -zipalign"
    fi

    echo "$params"
}

# 构建 iOS 加固参数
build_ios_params() {
    local file="$1"
    local engine="$2"
    local params="-iOS -nobitcode -yunconfig"

    # 引擎特定参数
    case "$engine" in
        cocos)
            params="$params -cocos"
            ;;
    esac

    echo "$params"
}

# 构建鸿蒙加固参数
build_harmony_params() {
    local file="$1"
    local engine="$2"
    local auto_mode="$3"
    local params="-yunconfig -fullapp -harmony"

    # 引擎特定参数
    case "$engine" in
        unity)
            # Unity 鸿蒙
            ;;
        cocos)
            params="$params -cocos"
            ;;
    esac

    # 交互式询问签名（非自动模式）
    if [ "$auto_mode" != "true" ]; then
        if [ "$(ask_sign_option harmony)" = "yes" ]; then
            params="$params -hapsign"
        fi
    fi

    echo "$params"
}

# 执行加固
perform_defense() {
    local file="$1"
    local params="$2"
    local output_file="$3"

    log_step "开始加固..."
    log_info "输入文件: $file"
    log_info "输出文件: $output_file"
    echo ""

    # 切换到工具目录执行
    cd "$YIDUN_DIR"

    # 执行加固
    if java -jar "$TOOL_JAR" $params -input "$file" -output "$output_file" 2>&1 | tee /tmp/yidun-defense.log; then
        echo ""
        log_success "加固完成！"

        if [ -f "$output_file" ]; then
            # 获取文件大小（字节）
            local input_bytes=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null)
            local output_bytes=$(stat -f%z "$output_file" 2>/dev/null || stat -c%s "$output_file" 2>/dev/null)

            # 转换为MB
            local input_mb=$(awk "BEGIN {printf \"%.2f\", $input_bytes/1024/1024}")
            local output_mb=$(awk "BEGIN {printf \"%.2f\", $output_bytes/1024/1024}")

            # 计算差异
            local diff_bytes=$((output_bytes - input_bytes))
            local diff_mb=$(awk "BEGIN {printf \"%.2f\", $diff_bytes/1024/1024}")
            local diff_percent=$(awk "BEGIN {printf \"%.1f\", ($diff_bytes*100.0)/$input_bytes}")

            echo ""
            log_info "输出文件: $output_file"
            echo ""
            echo "═══════════════════════════════════════"
            echo "  体积对比"
            echo "═══════════════════════════════════════"
            printf "  原始大小: %8.2f MB\n" "$input_mb"
            printf "  加固后:   %8.2f MB\n" "$output_mb"
            printf "  增加:     %+8.2f MB (%+.1f%%)\n" "$diff_mb" "$diff_percent"
            echo "═══════════════════════════════════════"
        else
            log_warning "输出文件未在指定位置生成"
            log_info "请查看日志: /tmp/yidun-defense.log"
        fi

        return 0
    else
        echo ""
        log_error "加固失败！"
        log_info "详细日志: /tmp/yidun-defense.log"
        log_info "工具日志: ~/.yidun-defense/Log/"

        echo ""
        log_info "查看完整日志（包含成本和失败详情）："
        log_info "  ls -lt ~/.yidun-defense/Log/ | head -1"
        log_info "  cat ~/.yidun-defense/Log/Constants_*.txt"

        echo ""
        echo "可能的原因："
        echo "  1. AppKey 无效或已过期"
        echo "  2. 包名未在易盾后台报备"
        echo "  3. 文件格式不正确"
        echo "  4. 网络连接问题"
        echo "  5. 服务配额不足"
        echo ""
        echo "请查看日志或访问控制台："
        echo "  https://dun.163.com/dashboard"

        return 1
    fi
}

# 主流程
main() {
    local input_file=""
    local platform=""
    local auto_mode=false

    # 解析参数
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --help|-h)
                show_usage
                exit 0
                ;;
            --auto)
                auto_mode=true
                shift
                ;;
            --platform)
                platform="$2"
                shift 2
                ;;
            *)
                if [ -z "$input_file" ]; then
                    input_file="$1"
                fi
                shift
                ;;
        esac
    done

    # 检查输入文件
    if [ -z "$input_file" ]; then
        log_error "请指定要加固的文件"
        echo ""
        show_usage
        exit 1
    fi

    if [ ! -f "$input_file" ]; then
        log_error "文件不存在: $input_file"
        exit 1
    fi

    # 转换为绝对路径
    input_file="$(cd "$(dirname "$input_file")" && pwd)/$(basename "$input_file")"

    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}  易盾智能加固工具${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""

    # 检测文件类型
    local file_type=$(detect_file_type "$input_file")
    log_info "文件类型: $file_type"

    # 确定平台
    if [ -z "$platform" ]; then
        case "$file_type" in
            android_*)
                platform="android"
                ;;
            ios_*)
                platform="ios"
                ;;
            harmony_*)
                platform="harmony"
                ;;
            harmony_or_mac)
                if [ "$auto_mode" = true ]; then
                    platform="harmony"
                else
                    platform=$(ask_platform)
                fi
                ;;
            zip_unknown)
                if [ "$auto_mode" = true ]; then
                    platform="h5"
                else
                    platform=$(ask_platform)
                fi
                ;;
            pc_*)
                platform="pc"
                ;;
            *)
                if [ "$auto_mode" = true ]; then
                    log_error "无法自动识别文件类型"
                    exit 1
                else
                    platform=$(ask_platform)
                fi
                ;;
        esac
    fi

    log_info "平台: $platform"

    # 确定引擎类型
    local engine="normal"
    if [ "$auto_mode" != "true" ] && [ "$platform" = "android" ] || [ "$platform" = "ios" ] || [ "$platform" = "harmony" ]; then
        engine=$(ask_engine_type "$platform")
        log_info "引擎: $engine"
    fi

    # 构建加固参数
    local params=""
    case "$platform" in
        android)
            params=$(build_android_params "$input_file" "$engine" "$auto_mode")
            ;;
        ios)
            params=$(build_ios_params "$input_file" "$engine")
            ;;
        harmony)
            params=$(build_harmony_params "$input_file" "$engine" "$auto_mode")
            ;;
        *)
            log_error "暂不支持的平台: $platform"
            exit 1
            ;;
    esac

    # 生成输出文件名
    local dir=$(dirname "$input_file")
    local filename=$(basename "$input_file")
    local name="${filename%.*}"
    local ext="${filename##*.}"
    local output_file="${dir}/${name}_protected.${ext}"

    # 执行加固
    perform_defense "$input_file" "$params" "$output_file"
}

# 执行主函数
main "$@"
