#!/bin/bash
# 和 L 聊天的脚本，自动维护对话历史
# 用法: ./chat-with-L.sh "消息内容"

HISTORY_FILE="$HOME/.openclaw/workspace/memory/chat-with-L.json"
L_URL="http://49.232.185.232:18789/v1/chat/completions"
L_TOKEN="304c106f250c106ed85de9b0db54060b385c7fdcf485d2a7"

MESSAGE="$1"
if [ -z "$MESSAGE" ]; then
  echo "用法: $0 \"消息内容\""
  exit 1
fi

# 读取历史，追加新消息，构造请求
MESSAGES=$(python3 -c "
import json, sys
with open('$HISTORY_FILE') as f:
    history = json.load(f)
history.append({'role': 'user', 'content': sys.argv[1]})
print(json.dumps(history))
" "$MESSAGE")

# 调用 L 的 API
RESPONSE=$(curl -s -X POST "$L_URL" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $L_TOKEN" \
  --max-time 60 \
  -d "{\"model\": \"default\", \"messages\": $MESSAGES}")

# 提取回复
REPLY=$(echo "$RESPONSE" | python3 -c "import json,sys; print(json.load(sys.stdin)['choices'][0]['message']['content'])")

if [ $? -eq 0 ] && [ -n "$REPLY" ]; then
  # 更新历史文件
  python3 -c "
import json, sys
with open('$HISTORY_FILE') as f:
    history = json.load(f)
history.append({'role': 'user', 'content': sys.argv[1]})
history.append({'role': 'assistant', 'content': sys.argv[2]})
with open('$HISTORY_FILE', 'w') as f:
    json.dump(history, f, indent=2, ensure_ascii=False)
" "$MESSAGE" "$REPLY"
  echo "$REPLY"
else
  echo "调用失败: $RESPONSE"
  exit 1
fi
