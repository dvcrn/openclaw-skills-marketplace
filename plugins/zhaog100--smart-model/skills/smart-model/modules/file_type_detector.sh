#!/bin/bash
# 文件类型检测模块
# 创建时间：2026-03-12 16:20
# 创建者：小米粒
# 功能：检测文件类型并返回对应模型类型

# ============================================
# 文件扩展名映射表
# ============================================

# 声明全局关联数组
declare -A FILE_TYPE_MAP

# 初始化文件类型映射
init_file_type_map() {
    FILE_TYPE_MAP=(
        # 代码文件
        ["py"]="code"
        ["js"]="code"
        ["sh"]="code"
        ["ts"]="code"
        ["java"]="code"
        ["go"]="code"
        ["rs"]="code"
        ["cpp"]="code"
        ["c"]="code"
        ["h"]="code"
        ["hpp"]="code"
        ["cs"]="code"
        ["php"]="code"
        ["rb"]="code"
        ["swift"]="code"
        ["kt"]="code"
        ["scala"]="code"
        ["lua"]="code"
        ["pl"]="code"
        ["sql"]="code"
        ["json"]="code"
        ["xml"]="code"
        ["yaml"]="code"
        ["yml"]="code"
        ["toml"]="code"
        
        # 文档文件
        ["md"]="document"
        ["txt"]="document"
        ["pdf"]="document"
        ["docx"]="document"
        ["xlsx"]="document"
        ["pptx"]="document"
        ["doc"]="document"
        ["xls"]="document"
        ["ppt"]="document"
        ["rtf"]="document"
        ["odt"]="document"
        ["ods"]="document"
        ["odp"]="document"
        
        # 图片文件
        ["jpg"]="image"
        ["jpeg"]="image"
        ["png"]="image"
        ["gif"]="image"
        ["webp"]="image"
        ["bmp"]="image"
        ["svg"]="image"
        ["ico"]="image"
        ["tiff"]="image"
        ["tif"]="image"
        
        # 音频文件
        ["mp3"]="audio"
        ["wav"]="audio"
        ["ogg"]="audio"
        ["flac"]="audio"
        ["aac"]="audio"
        ["m4a"]="audio"
        ["wma"]="audio"
        
        # 视频文件
        ["mp4"]="video"
        ["avi"]="video"
        ["mkv"]="video"
        ["mov"]="video"
        ["wmv"]="video"
        ["flv"]="video"
        ["webm"]="video"
        
        # 压缩文件
        ["zip"]="archive"
        ["tar"]="archive"
        ["gz"]="archive"
        ["rar"]="archive"
        ["7z"]="archive"
        ["bz2"]="archive"
        
        # 其他
        ["log"]="log"
        ["csv"]="data"
        ["tsv"]="data"
    )
}

# ============================================
# 文件类型检测函数
# ============================================

# 检测文件类型
# 参数：$1 - 文件路径
# 返回：文件类型（code/document/image/audio/video/archive/log/data/none）
detect_file_type() {
    local file_path="$1"
    
    # 获取文件扩展名（小写）
    local ext="${file_path##*.}"
    ext=$(echo "$ext" | tr '[:upper:]' '[:lower:]')
    
    # 优先使用扩展名映射
    if [ -n "${FILE_TYPE_MAP[$ext]}" ]; then
        echo "${FILE_TYPE_MAP[$ext]}"
        return 0
    fi
    
    # 如果文件存在，尝试通过文件内容检测
    if [ -e "$file_path" ]; then
        detect_file_type_by_content "$file_path"
    else
        # 文件不存在且扩展名未知，返回none
        echo "none"
        return 1
    fi
    
    return 0
}

# 通过文件内容检测类型（备用方案）
# 参数：$1 - 文件路径
# 返回：文件类型
detect_file_type_by_content() {
    local file_path="$1"
    
    # 检查是否为目录
    if [ -d "$file_path" ]; then
        echo "directory"
        return 0
    fi
    
    # 检查是否为二进制文件
    if file "$file_path" | grep -q "text"; then
        # 文本文件，进一步分析
        if head -n 1 "$file_path" | grep -q "^#!"; then
            # 脚本文件
            echo "code"
        elif head -n 10 "$file_path" | grep -qE "(function|class|import|from|def|var|let|const)"; then
            # 包含代码关键字
            echo "code"
        else
            # 普通文本
            echo "document"
        fi
    else
        # 二进制文件，通过file命令检测
        local file_info=$(file -b "$file_path")
        
        if echo "$file_info" | grep -qi "image"; then
            echo "image"
        elif echo "$file_info" | grep -qi "audio"; then
            echo "audio"
        elif echo "$file_info" | grep -qi "video"; then
            echo "video"
        elif echo "$file_info" | grep -qi "archive\|compressed"; then
            echo "archive"
        else
            echo "none"
        fi
    fi
    
    return 0
}

# ============================================
# 模型映射函数
# ============================================

# 根据文件类型获取推荐的模型
# 参数：$1 - 文件类型
# 返回：推荐模型
get_recommended_model() {
    local file_type="$1"
    
    case "$file_type" in
        code)
            echo "coding"
            ;;
        document)
            echo "main"
            ;;
        image)
            echo "vision"
            ;;
        audio)
            echo "audio"
            ;;
        video)
            echo "vision"
            ;;
        archive)
            echo "main"
            ;;
        log)
            echo "flash"
            ;;
        data)
            echo "main"
            ;;
        *)
            echo "main"
            ;;
    esac
    
    return 0
}

# ============================================
# 工具函数
# ============================================

# 批量检测文件类型
# 参数：$@ - 文件路径列表
# 返回：文件类型列表（JSON格式）
batch_detect_file_types() {
    local files=("$@")
    local result="["
    local first=true
    
    for file in "${files[@]}"; do
        if [ "$first" = true ]; then
            first=false
        else
            result+=","
        fi
        
        local file_type=$(detect_file_type "$file")
        local model=$(get_recommended_model "$file_type")
        
        result+="{\"file\":\"$file\",\"type\":\"$file_type\",\"model\":\"$model\"}"
    done
    
    result+="]"
    echo "$result"
}

# 检测文件类型并返回详细信息
# 参数：$1 - 文件路径
# 返回：JSON格式的详细信息
detect_file_type_detailed() {
    local file_path="$1"
    
    local file_type=$(detect_file_type "$file_path")
    local model=$(get_recommended_model "$file_type")
    local ext="${file_path##*.}"
    local size=$(stat -f%z "$file_path" 2>/dev/null || stat -c%s "$file_path" 2>/dev/null || echo "0")
    
    cat << EOF
{
    "file": "$file_path",
    "extension": "$ext",
    "type": "$file_type",
    "model": "$model",
    "size": $size
}
EOF
}

# ============================================
# 主函数（用于测试）
# ============================================

main() {
    # 初始化映射表（必须在脚本开始时调用）
    init_file_type_map
    
    # 显示数组内容（调试）
    echo "调试：FILE_TYPE_MAP[py]=${FILE_TYPE_MAP[py]}"
    echo "调试：FILE_TYPE_MAP[md]=${FILE_TYPE_MAP[md]}"
    echo "调试：FILE_TYPE_MAP[png]=${FILE_TYPE_MAP[png]}"
    echo ""
    
    # 测试用例
    echo "=== 文件类型检测测试 ==="
    echo ""
    
    # 测试1：检测代码文件
    echo "测试1：检测代码文件"
    local test_file="test.py"
    echo "文件：$test_file"
    echo "类型：$(detect_file_type "$test_file")"
    echo "模型：$(get_recommended_model "$(detect_file_type "$test_file")")"
    echo ""
    
    # 测试2：检测文档文件
    echo "测试2：检测文档文件"
    local test_file="README.md"
    echo "文件：$test_file"
    echo "类型：$(detect_file_type "$test_file")"
    echo "模型：$(get_recommended_model "$(detect_file_type "$test_file")")"
    echo ""
    
    # 测试3：检测图片文件
    echo "测试3：检测图片文件"
    local test_file="image.png"
    echo "文件：$test_file"
    echo "类型：$(detect_file_type "$test_file")"
    echo "模型：$(get_recommended_model "$(detect_file_type "$test_file")")"
    echo ""
    
    # 测试4：检测未知文件
    echo "测试4：检测未知文件"
    local test_file="unknown.xyz"
    echo "文件：$test_file"
    echo "类型：$(detect_file_type "$test_file")"
    echo "模型：$(get_recommended_model "$(detect_file_type "$test_file")")"
    echo ""
    
    echo "=== 测试完成 ==="
}

# 如果直接运行此脚本，执行主函数
if [ "${BASH_SOURCE[0]}" = "$0" ]; then
    main "$@"
fi
