#!/bin/bash
# 复杂度分析器模块
# 创建时间：2026-03-12 17:50
# 创建者：小米粒
# 功能：分析消息/文件的复杂度，4维度加权评分

# ============================================
# 复杂度评分标准
# ============================================

# 4维度加权评分：
# 1. 长度维度（30%）- 消息/文件长度
# 2. 关键词维度（40%）- 复杂度关键词数量
# 3. 代码维度（20%）- 是否包含代码/技术内容
# 4. 视觉维度（10%）- 是否包含图片/视觉内容

# 复杂度级别：
# - flash: 简单快速响应（得分 < 30）
# - main: 标准响应（30 <= 得分 < 60）
# - complex: 复杂任务（60 <= 得分 < 80）
# - complex-deep: 深度分析（得分 >= 80）

# ============================================
# 复杂度关键词映射表
# ============================================

# 声明全局关联数组
declare -A COMPLEXITY_KEYWORDS

# 初始化复杂度关键词
init_complexity_keywords() {
    # 高复杂度关键词（+10分）
    COMPLEXITY_KEYWORDS[high]="分析 架构 设计 优化 重构 集成 部署 调试 性能 算法 数据结构 系统设计 微服务 分布式 容器 kubernetes docker"
    
    # 中复杂度关键词（+5分）
    COMPLEXITY_KEYWORDS[medium]="开发 编程 代码 函数 类 接口 API 数据库 配置 测试 调试 错误 异常 日志 版本控制 Git"
    
    # 技术关键词（+8分）
    COMPLEXITY_KEYWORDS[tech]="Python JavaScript TypeScript Java Go Rust SQL NoSQL Redis MongoDB PostgreSQL MySQL Linux Windows macOS"
    
    # 任务关键词（+6分）
    COMPLEXITY_KEYWORDS[task]="实现 创建 编写 修改 删除 查询 更新 导入 导出 转换 解析 生成"
}

# ============================================
# 评分函数
# ============================================

# 计算长度得分（30%权重）
# 参数：$1 - 消息长度
# 返回：得分（0-30）
calculate_length_score() {
    local length="$1"
    
    if [ "$length" -lt 50 ]; then
        echo "5"  # 短消息：5分
    elif [ "$length" -lt 200 ]; then
        echo "15" # 中等消息：15分
    elif [ "$length" -lt 500 ]; then
        echo "25" # 较长消息：25分
    else
        echo "30" # 长消息：30分
    fi
}

# 计算关键词得分（40%权重）
# 参数：$1 - 消息内容
# 返回：得分（0-40）
calculate_keyword_score() {
    local content="$1"
    local score=0
    
    # 高复杂度关键词（+10分/个，上限20分）
    local high_count=$(echo "$content" | grep -oE "分析|架构|设计|优化|重构|集成|部署|调试|性能|算法|数据结构|系统设计|微服务|分布式|容器|kubernetes|docker" | wc -l)
    score=$((score + high_count * 10))
    
    # 中复杂度关键词（+5分/个，上限15分）
    local medium_count=$(echo "$content" | grep -oE "开发|编程|代码|函数|类|接口|API|数据库|配置|测试|调试|错误|异常|日志|版本控制|Git" | wc -l)
    score=$((score + medium_count * 5))
    
    # 技术关键词（+8分/个，上限16分）
    local tech_count=$(echo "$content" | grep -oE "Python|JavaScript|TypeScript|Java|Go|Rust|SQL|NoSQL|Redis|MongoDB|PostgreSQL|MySQL|Linux|Windows|macOS" | wc -l)
    score=$((score + tech_count * 8))
    
    # 任务关键词（+6分/个，上限12分）
    local task_count=$(echo "$content" | grep -oE "实现|创建|编写|修改|删除|查询|更新|导入|导出|转换|解析|生成" | wc -l)
    score=$((score + task_count * 6))
    
    # 限制总分为40分
    if [ "$score" -gt 40 ]; then
        score=40
    fi
    
    echo "$score"
}

# 计算代码得分（20%权重）
# 参数：$1 - 消息内容
# 返回：得分（0-20）
calculate_code_score() {
    local content="$1"
    local score=0
    
    # 检测代码块
    if echo "$content" | grep -qE '```|`[^`]+`'; then
        score=$((score + 10))
    fi
    
    # 检测代码关键字
    if echo "$content" | grep -qE "function|class|def|import|from|var|let|const|return|if|else|for|while"; then
        score=$((score + 5))
    fi
    
    # 检测文件扩展名（代码文件）
    if echo "$content" | grep -qE "\.(py|js|sh|ts|java|go|rs|cpp|c|h|php|rb)$"; then
        score=$((score + 5))
    fi
    
    # 限制总分为20分
    if [ "$score" -gt 20 ]; then
        score=20
    fi
    
    echo "$score"
}

# 计算视觉得分（10%权重）
# 参数：$1 - 消息内容 或 $2 - 文件路径
# 返回：得分（0-10）
calculate_visual_score() {
    local content="$1"
    local file_path="$2"
    local score=0
    
    # 检测图片标签
    if echo "$content" | grep -qE "<qqimg>|!\[|https?://.*\.(jpg|jpeg|png|gif|webp)"; then
        score=$((score + 10))
    fi
    
    # 检测文件是否为图片
    if [ -n "$file_path" ] && [ -e "$file_path" ]; then
        local ext="${file_path##*.}"
        ext=$(echo "$ext" | tr '[:upper:]' '[:lower:]')
        
        if [ "$ext" = "jpg" ] || [ "$ext" = "jpeg" ] || [ "$ext" = "png" ] || [ "$ext" = "gif" ] || [ "$ext" = "webp" ]; then
            score=10
        fi
    fi
    
    echo "$score"
}

# ============================================
# 综合评分函数
# ============================================

# 分析消息复杂度
# 参数：$1 - 消息内容
# 返回：JSON格式的复杂度分析结果
analyze_message_complexity() {
    local content="$1"
    local length=${#content}
    
    # 计算各维度得分
    local length_score=$(calculate_length_score "$length")
    local keyword_score=$(calculate_keyword_score "$content")
    local code_score=$(calculate_code_score "$content")
    local visual_score=$(calculate_visual_score "$content" "")
    
    # 计算总分
    local total_score=$((length_score + keyword_score + code_score + visual_score))
    
    # 确定推荐模型
    local recommended_model
    if [ "$total_score" -lt 30 ]; then
        recommended_model="flash"
    elif [ "$total_score" -lt 60 ]; then
        recommended_model="main"
    elif [ "$total_score" -lt 80 ]; then
        recommended_model="complex"
    else
        recommended_model="complex-deep"
    fi
    
    # 返回JSON格式结果
    cat << EOF
{
    "length": $length,
    "scores": {
        "length": $length_score,
        "keyword": $keyword_score,
        "code": $code_score,
        "visual": $visual_score,
        "total": $total_score
    },
    "recommended_model": "$recommended_model",
    "level": "$(get_complexity_level "$total_score")"
}
EOF
}

# 分析文件复杂度
# 参数：$1 - 文件路径
# 返回：JSON格式的复杂度分析结果
analyze_file_complexity() {
    local file_path="$1"
    
    if [ ! -e "$file_path" ]; then
        echo '{"error": "file not found"}'
        return 1
    fi
    
    # 获取文件信息
    local file_size=$(stat -f%z "$file_path" 2>/dev/null || stat -c%s "$file_path" 2>/dev/null || echo "0")
    local line_count=$(wc -l < "$file_path" 2>/dev/null || echo "0")
    local content=$(cat "$file_path" 2>/dev/null || echo "")
    
    # 计算各维度得分
    local length_score=$(calculate_length_score "$line_count")
    local keyword_score=$(calculate_keyword_score "$content")
    local code_score=$(calculate_code_score "$content")
    local visual_score=$(calculate_visual_score "" "$file_path")
    
    # 计算总分
    local total_score=$((length_score + keyword_score + code_score + visual_score))
    
    # 确定推荐模型
    local recommended_model
    if [ "$total_score" -lt 30 ]; then
        recommended_model="flash"
    elif [ "$total_score" -lt 60 ]; then
        recommended_model="main"
    elif [ "$total_score" -lt 80 ]; then
        recommended_model="complex"
    else
        recommended_model="complex-deep"
    fi
    
    # 返回JSON格式结果
    cat << EOF
{
    "file": "$file_path",
    "size": $file_size,
    "lines": $line_count,
    "scores": {
        "length": $length_score,
        "keyword": $keyword_score,
        "code": $code_score,
        "visual": $visual_score,
        "total": $total_score
    },
    "recommended_model": "$recommended_model",
    "level": "$(get_complexity_level "$total_score")"
}
EOF
}

# ============================================
# 工具函数
# ============================================

# 获取复杂度级别名称
# 参数：$1 - 总分
# 返回：复杂度级别名称
get_complexity_level() {
    local score="$1"
    
    if [ "$score" -lt 30 ]; then
        echo "simple"
    elif [ "$score" -lt 60 ]; then
        echo "medium"
    elif [ "$score" -lt 80 ]; then
        echo "complex"
    else
        echo "deep"
    fi
}

# 快速获取推荐模型
# 参数：$1 - 消息内容
# 返回：推荐模型名称
get_recommended_model_fast() {
    local content="$1"
    local length=${#content}
    
    # 快速评分（简化版）
    local score=0
    
    # 长度评分
    if [ "$length" -gt 200 ]; then
        score=$((score + 15))
    elif [ "$length" -gt 50 ]; then
        score=$((score + 10))
    fi
    
    # 关键词评分（只检查几个关键关键词）
    if echo "$content" | grep -qE "分析|架构|设计|优化|开发|编程"; then
        score=$((score + 20))
    fi
    
    # 代码评分
    if echo "$content" | grep -qE '```|function|class|def'; then
        score=$((score + 15))
    fi
    
    # 确定模型
    if [ "$score" -lt 30 ]; then
        echo "flash"
    elif [ "$score" -lt 60 ]; then
        echo "main"
    else
        echo "complex"
    fi
}

# ============================================
# 主函数（用于测试）
# ============================================

main() {
    # 初始化关键词（必须在脚本开始时调用）
    init_complexity_keywords
    
    echo "=== 复杂度分析器测试 ==="
    echo ""
    
    # 测试1：简单消息
    echo "测试1：简单消息"
    local test_msg1="你好，在吗？"
    echo "消息：$test_msg1"
    analyze_message_complexity "$test_msg1"
    echo ""
    
    # 测试2：中等复杂度消息
    echo "测试2：中等复杂度消息"
    local test_msg2="帮我写一个Python函数，实现两个数字的加法运算"
    echo "消息：$test_msg2"
    analyze_message_complexity "$test_msg2"
    echo ""
    
    # 测试3：高复杂度消息
    echo "测试3：高复杂度消息"
    local test_msg3="请帮我设计一个分布式微服务架构，包括服务发现、负载均衡、容错机制、数据一致性保证等核心功能，并给出详细的技术选型和实现方案"
    echo "消息：$test_msg3"
    analyze_message_complexity "$test_msg3"
    echo ""
    
    # 测试4：包含代码的消息
    echo "测试4：包含代码的消息"
    local test_msg4="请帮我优化这段代码：
\`\`\`python
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
\`\`\`"
    echo "消息：$test_msg4"
    analyze_message_complexity "$test_msg4"
    echo ""
    
    # 测试5：快速获取推荐模型
    echo "测试5：快速获取推荐模型"
    echo "消息：$test_msg1 -> 模型：$(get_recommended_model_fast "$test_msg1")"
    echo "消息：$test_msg2 -> 模型：$(get_recommended_model_fast "$test_msg2")"
    echo "消息：$test_msg3 -> 模型：$(get_recommended_model_fast "$test_msg3")"
    echo ""
    
    echo "=== 测试完成 ==="
}

# 如果直接运行此脚本，执行主函数
if [ "${BASH_SOURCE[0]}" = "$0" ]; then
    main "$@"
fi
