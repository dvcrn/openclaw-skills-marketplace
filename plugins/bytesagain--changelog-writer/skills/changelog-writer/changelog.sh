#!/usr/bin/env bash
CMD="$1"; shift 2>/dev/null; INPUT="$*"
case "$CMD" in
  generate) cat << 'PROMPT'
You are an expert. Help with: 生成CHANGELOG. Provide detailed, practical output. Use Chinese.
User request:
PROMPT
    echo "$INPUT" ;;
  format) cat << 'PROMPT'
You are an expert. Help with: 格式化. Provide detailed, practical output. Use Chinese.
User request:
PROMPT
    echo "$INPUT" ;;
  release) cat << 'PROMPT'
You are an expert. Help with: 发布说明. Provide detailed, practical output. Use Chinese.
User request:
PROMPT
    echo "$INPUT" ;;
  semver) cat << 'PROMPT'
You are an expert. Help with: 语义化版本. Provide detailed, practical output. Use Chinese.
User request:
PROMPT
    echo "$INPUT" ;;
  diff) cat << 'PROMPT'
You are an expert. Help with: 版本差异. Provide detailed, practical output. Use Chinese.
User request:
PROMPT
    echo "$INPUT" ;;
  template) cat << 'PROMPT'
You are an expert. Help with: 模板. Provide detailed, practical output. Use Chinese.
User request:
PROMPT
    echo "$INPUT" ;;
  *) cat << 'EOF'
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Changelog Writer — 使用指南
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  generate        生成CHANGELOG
  format          格式化
  release         发布说明
  semver          语义化版本
  diff            版本差异
  template        模板

  Powered by BytesAgain | bytesagain.com | hello@bytesagain.com
EOF
    ;;
esac
