#!/bin/bash

# 测试脚本
# 功能：测试引用检测和提取功能

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=== 测试引用检测功能 ==="
echo ""

# 测试1：飞书引用
echo "测试1：飞书引用"
MESSAGE1="[message_id: om_x100b55b] 这个是指什么？"
echo "输入：$MESSAGE1"
RESULT1=$("$SCRIPT_DIR/detect-quote.sh" "$MESSAGE1")
echo "输出："
echo "$RESULT1" | jq .
echo ""

# 测试2：QQ引用
echo "测试2：QQ引用"
MESSAGE2="[reply:12345678] 继续展开"
echo "输入：$MESSAGE2"
RESULT2=$("$SCRIPT_DIR/detect-quote.sh" "$MESSAGE2")
echo "输出："
echo "$RESULT2" | jq .
echo ""

# 测试3：通用引用
echo "测试3：通用引用"
MESSAGE3="引用：QMD向量生成受阻，怎么解决？"
echo "输入：$MESSAGE3"
RESULT3=$("$SCRIPT_DIR/detect-quote.sh" "$MESSAGE3")
echo "输出："
echo "$RESULT3" | jq .
echo ""

# 测试4：无引用
echo "测试4：无引用"
MESSAGE4="今天天气怎么样？"
echo "输入：$MESSAGE4"
RESULT4=$("$SCRIPT_DIR/detect-quote.sh" "$MESSAGE4")
echo "输出："
echo "$RESULT4" | jq .
echo ""

echo "=== 测试引用提取功能 ==="
echo ""

# 测试5：提取引用内容
echo "测试5：提取飞书引用"
QUOTE_INFO='{"has_quote":true,"platform":"feishu","message_id":"om_x100b55b","quoted_text":null,"quote_position":0}'
echo "输入：$QUOTE_INFO"
RESULT5=$("$SCRIPT_DIR/extract-quote.sh" "$QUOTE_INFO")
echo "输出："
echo "$RESULT5" | jq .
echo ""

# 测试6：提取通用引用
echo "测试6：提取通用引用"
QUOTE_INFO2='{"has_quote":true,"platform":"generic","message_id":null,"quoted_text":"QMD向量生成需要CUDA支持","quote_position":0}'
echo "输入：$QUOTE_INFO2"
RESULT6=$("$SCRIPT_DIR/extract-quote.sh" "$QUOTE_INFO2")
echo "输出："
echo "$RESULT6" | jq .
echo ""

echo "=== 测试AI集成 ==="
echo ""

# 测试7：AI集成（有引用）
echo "测试7：AI集成（有引用）"
MESSAGE7="[message_id: om_x100b55b] 这个是指什么？"
echo "输入：$MESSAGE7"
RESULT7=$("$SCRIPT_DIR/integrate-quote.sh" "$MESSAGE7")
echo "输出："
echo "$RESULT7"
echo ""

# 测试8：AI集成（无引用）
echo "测试8：AI集成（无引用）"
MESSAGE8="今天天气怎么样？"
echo "输入：$MESSAGE8"
RESULT8=$("$SCRIPT_DIR/integrate-quote.sh" "$MESSAGE8")
if [ -z "$RESULT8" ]; then
    echo "输出：（静默，无输出）"
else
    echo "输出：$RESULT8"
fi
echo ""

echo "=== 测试完成 ==="
