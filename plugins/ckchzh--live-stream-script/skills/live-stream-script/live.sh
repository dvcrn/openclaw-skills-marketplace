#!/usr/bin/env bash
CMD="$1"; shift 2>/dev/null; INPUT="$*"
case "$CMD" in
  script) cat << 'PROMPT'
You are a Chinese content expert. Help with: 直播脚本(时间轴). Be detailed and practical. Output in Chinese.
User input:
PROMPT
    echo "$INPUT" ;;
  opening) cat << 'PROMPT'
You are a Chinese content expert. Help with: 开场话术. Be detailed and practical. Output in Chinese.
User input:
PROMPT
    echo "$INPUT" ;;
  product) cat << 'PROMPT'
You are a Chinese content expert. Help with: 商品讲解话术. Be detailed and practical. Output in Chinese.
User input:
PROMPT
    echo "$INPUT" ;;
  interact) cat << 'PROMPT'
You are a Chinese content expert. Help with: 互动话术. Be detailed and practical. Output in Chinese.
User input:
PROMPT
    echo "$INPUT" ;;
  closing) cat << 'PROMPT'
You are a Chinese content expert. Help with: 下播话术. Be detailed and practical. Output in Chinese.
User input:
PROMPT
    echo "$INPUT" ;;
  plan) cat << 'PROMPT'
You are a Chinese content expert. Help with: 直播排期计划. Be detailed and practical. Output in Chinese.
User input:
PROMPT
    echo "$INPUT" ;;
  *) cat << 'EOF'
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Live Stream Script — 使用指南
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  script          直播脚本(时间轴)
  opening         开场话术
  product         商品讲解话术
  interact        互动话术
  closing         下播话术
  plan            直播排期计划

  Powered by BytesAgain | bytesagain.com | hello@bytesagain.com
EOF
    ;;
esac
