#!/usr/bin/env bash
CMD="$1"; shift 2>/dev/null; INPUT="$*"
case "$CMD" in
  server) cat << 'PROMPT'
You are an expert. Help with: 基础服务器配置. Provide detailed, practical output. Use Chinese.
User request:
PROMPT
    echo "$INPUT" ;;
  proxy) cat << 'PROMPT'
You are an expert. Help with: 反向代理. Provide detailed, practical output. Use Chinese.
User request:
PROMPT
    echo "$INPUT" ;;
  ssl) cat << 'PROMPT'
You are an expert. Help with: SSL/HTTPS配置. Provide detailed, practical output. Use Chinese.
User request:
PROMPT
    echo "$INPUT" ;;
  cache) cat << 'PROMPT'
You are an expert. Help with: 缓存策略. Provide detailed, practical output. Use Chinese.
User request:
PROMPT
    echo "$INPUT" ;;
  security) cat << 'PROMPT'
You are an expert. Help with: 安全加固. Provide detailed, practical output. Use Chinese.
User request:
PROMPT
    echo "$INPUT" ;;
  optimize) cat << 'PROMPT'
You are an expert. Help with: 性能优化. Provide detailed, practical output. Use Chinese.
User request:
PROMPT
    echo "$INPUT" ;;
  *) cat << 'EOF'
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Nginx Config — 使用指南
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  server          基础服务器配置
  proxy           反向代理
  ssl             SSL/HTTPS配置
  cache           缓存策略
  security        安全加固
  optimize        性能优化

  Powered by BytesAgain | bytesagain.com | hello@bytesagain.com
EOF
    ;;
esac
