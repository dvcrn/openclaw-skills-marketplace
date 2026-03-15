#!/bin/bash

usage() {
    echo 'Usage: search.sh "here is your query" [-n 5] [--start_time "2026-01-01T00:00:00Z"] [--end_time "2026-01-31T23:59:59Z"]' >&2
    exit 2
}

# 检查参数
if [ $# -eq 0 ] || [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    usage
fi

query="$1"
shift

# 默认值
n=5
start_time=""
end_time=""

# 解析剩余参数
while [ $# -gt 0 ]; do
    case "$1" in
        -n)
            if [ -n "$2" ] && [[ "$2" =~ ^[0-9]+$ ]]; then
                n="$2"
                shift 2
            else
                echo "Error: -n requires a numeric value" >&2
                usage
            fi
            ;;
        --start_time)
            if [ -n "$2" ]; then
                start_time="$2"
                shift 2
            else
                echo "Error: --start_time requires a value" >&2
                usage
            fi
            ;;
        --end_time)
            if [ -n "$2" ]; then
                end_time="$2"
                shift 2
            else
                echo "Error: --end_time requires a value" >&2
                usage
            fi
            ;;
        *)
            echo "Unknown arg: $1" >&2
            usage
            ;;
    esac
done

# 检查API密钥
api_key="${OCTEN_API_KEY:-}"
api_key=$(echo "$api_key" | xargs)  # trim whitespace

if [ -z "$api_key" ]; then
    echo "Missing OCTEN_API_KEY. Please set it in the environment variables. example: export OCTEN_API_KEY=your-api-key" >&2
    exit 1
fi

# 限制n的范围
if [ "$n" -lt 1 ]; then
    n=1
elif [ "$n" -gt 20 ]; then
    n=20
fi

# 构建JSON请求体
body=$(jq -n \
    --arg query "$query" \
    --argjson count "$n" \
    '{query: $query, count: $count}')

# 添加时间参数（如果提供）
if [ -n "$start_time" ]; then
    body=$(echo "$body" | jq --arg start_time "$start_time" '. + {start_time: $start_time}')
fi

if [ -n "$end_time" ]; then
    body=$(echo "$body" | jq --arg end_time "$end_time" '. + {end_time: $end_time}')
fi

# 发送请求
response=$(curl -s -w "HTTPSTATUS:%{http_code}" \
    -X POST \
    -H "Content-Type: application/json" \
    -H "X-Api-Key: $api_key" \
    -d "$body" \
    "https://api.octen.ai/search")

# 提取HTTP状态码和响应体
http_code=$(echo "$response" | tail -c 100 | grep -o "HTTPSTATUS:[0-9]*" | tail -1 | cut -d: -f2)
response_body=$(echo "$response" | sed 's/HTTPSTATUS:[0-9]*$//')

# 检查HTTP状态码
if [ "$http_code" != "200" ]; then
    echo "Octen Search failed ($http_code): $response_body" >&2
    exit 1
fi

# 检查JSON是否有效
if ! echo "$response_body" | jq empty 2>/dev/null; then
    echo "Invalid JSON response: $response_body" >&2
    exit 1
fi

# 解析JSON响应
code=$(echo "$response_body" | jq -r '.code // 0')
message=$(echo "$response_body" | jq -r '.message // ""')

if [ "$code" != "0" ]; then
    echo "Octen Search failed ($code): $message" >&2
    exit 1
fi

# 提取结果并限制数量
results=$(echo "$response_body" | jq --argjson n "$n" '.data.results[:$n] // []')
results_count=$(echo "$results" | jq 'length')

echo "Found $results_count search result items from Octen"
echo

if [ "$results_count" -eq 0 ]; then
    echo "No search results found."
    exit 0
fi

echo "## Search Results"
echo

# 格式化输出结果
for i in $(seq 0 $((results_count - 1))); do
    result=$(echo "$results" | jq -r ".[$i]")
    
    title=$(echo "$result" | jq -r '.title // ""' | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
    url=$(echo "$result" | jq -r '.url // ""' | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
    highlight=$(echo "$result" | jq -r '.highlight // ""' | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
    time_published=$(echo "$result" | jq -r '.time_published // ""' | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
    
    # 跳过没有title或url的结果
    if [ -z "$title" ] || [ -z "$url" ]; then
        continue
    fi
    
    echo "- **Title**: $title"
    echo "  **URL**: $url"
    
    if [ -n "$time_published" ]; then
        echo "  **TimePublished**: $time_published"
    fi
    
    if [ -n "$highlight" ]; then
        echo "  **Highlight**: $highlight"
    fi
    
    echo
done