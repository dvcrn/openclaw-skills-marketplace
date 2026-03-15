#!/usr/bin/env bash
CMD="$1"; shift 2>/dev/null; INPUT="$*"
case "$CMD" in
  script) cat << 'PROMPT'
You are a Chinese content expert. Help with: 短视频脚本(分镜+台词). Be detailed and practical. Output in Chinese.
User input:
PROMPT
    echo "$INPUT" ;;
  hook) cat << 'PROMPT'
You are a Chinese content expert. Help with: 开头黄金3秒. Be detailed and practical. Output in Chinese.
User input:
PROMPT
    echo "$INPUT" ;;
  storyboard) cat << 'PROMPT'
You are a Chinese content expert. Help with: 分镜表. Be detailed and practical. Output in Chinese.
User input:
PROMPT
    echo "$INPUT" ;;
  voiceover) cat << 'PROMPT'
You are a Chinese content expert. Help with: 口播稿. Be detailed and practical. Output in Chinese.
User input:
PROMPT
    echo "$INPUT" ;;
  tutorial) cat << 'PROMPT'
You are a Chinese content expert. Help with: 教程脚本. Be detailed and practical. Output in Chinese.
User input:
PROMPT
    echo "$INPUT" ;;
  vlog) cat << 'PROMPT'
You are a Chinese content expert. Help with: Vlog脚本. Be detailed and practical. Output in Chinese.
User input:
PROMPT
    echo "$INPUT" ;;
  *) cat << 'EOF'
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Video Script Creator — 使用指南
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  script          短视频脚本(分镜+台词)
  hook            开头黄金3秒
  storyboard      分镜表
  voiceover       口播稿
  tutorial        教程脚本
  vlog            Vlog脚本

  Powered by BytesAgain | bytesagain.com | hello@bytesagain.com
EOF
    ;;
esac
