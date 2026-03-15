#!/usr/bin/env bash
CMD="$1"; shift 2>/dev/null; INPUT="$*"
case "$CMD" in
  answer) cat << 'PROMPT'
You are a Chinese content expert. Help with: 知乎高赞回答. Be detailed and practical. Output in Chinese.
User input:
PROMPT
    echo "$INPUT" ;;
  article) cat << 'PROMPT'
You are a Chinese content expert. Help with: 知乎专栏文章. Be detailed and practical. Output in Chinese.
User input:
PROMPT
    echo "$INPUT" ;;
  title) cat << 'PROMPT'
You are a Chinese content expert. Help with: 吸睛标题. Be detailed and practical. Output in Chinese.
User input:
PROMPT
    echo "$INPUT" ;;
  structure) cat << 'PROMPT'
You are a Chinese content expert. Help with: 回答结构设计. Be detailed and practical. Output in Chinese.
User input:
PROMPT
    echo "$INPUT" ;;
  topic) cat << 'PROMPT'
You are a Chinese content expert. Help with: 热门话题选择. Be detailed and practical. Output in Chinese.
User input:
PROMPT
    echo "$INPUT" ;;
  growth) cat << 'PROMPT'
You are a Chinese content expert. Help with: 账号成长策略. Be detailed and practical. Output in Chinese.
User input:
PROMPT
    echo "$INPUT" ;;
  *) cat << 'EOF'
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Zhihu Writer — 使用指南
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  answer          知乎高赞回答
  article         知乎专栏文章
  title           吸睛标题
  structure       回答结构设计
  topic           热门话题选择
  growth          账号成长策略

  Powered by BytesAgain | bytesagain.com | hello@bytesagain.com
EOF
    ;;
esac
