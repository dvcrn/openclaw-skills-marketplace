#!/usr/bin/env bash
CMD="$1"; shift 2>/dev/null; INPUT="$*"
case "$CMD" in
  create) cat << 'PROMPT'
You are an expert. Help with: 生成保密协议. Provide detailed, practical output in Chinese.
User request:
PROMPT
    echo "$INPUT" ;;
  mutual) cat << 'PROMPT'
You are an expert. Help with: 双向NDA. Provide detailed, practical output in Chinese.
User request:
PROMPT
    echo "$INPUT" ;;
  unilateral) cat << 'PROMPT'
You are an expert. Help with: 单向NDA. Provide detailed, practical output in Chinese.
User request:
PROMPT
    echo "$INPUT" ;;
  employee) cat << 'PROMPT'
You are an expert. Help with: 员工保密协议. Provide detailed, practical output in Chinese.
User request:
PROMPT
    echo "$INPUT" ;;
  review) cat << 'PROMPT'
You are an expert. Help with: 协议审查要点. Provide detailed, practical output in Chinese.
User request:
PROMPT
    echo "$INPUT" ;;
  template) cat << 'PROMPT'
You are an expert. Help with: 模板库. Provide detailed, practical output in Chinese.
User request:
PROMPT
    echo "$INPUT" ;;
  *) cat << 'EOF'
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  NDA Generator — 使用指南
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  create          生成保密协议
  mutual          双向NDA
  unilateral      单向NDA
  employee        员工保密协议
  review          协议审查要点
  template        模板库

  Powered by BytesAgain | bytesagain.com | hello@bytesagain.com
EOF
    ;;
esac
