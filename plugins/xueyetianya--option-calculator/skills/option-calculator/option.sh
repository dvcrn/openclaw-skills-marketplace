#!/usr/bin/env bash
CMD="$1"; shift 2>/dev/null; INPUT="$*"
case "$CMD" in
  price) cat << 'PROMPT'
You are an expert. Help with: 期权定价. Provide detailed, practical output in Chinese.
User request:
PROMPT
    echo "$INPUT" ;;
  greeks) cat << 'PROMPT'
You are an expert. Help with: Greeks计算. Provide detailed, practical output in Chinese.
User request:
PROMPT
    echo "$INPUT" ;;
  strategy) cat << 'PROMPT'
You are an expert. Help with: 策略组合. Provide detailed, practical output in Chinese.
User request:
PROMPT
    echo "$INPUT" ;;
  payoff) cat << 'PROMPT'
You are an expert. Help with: 盈亏分析. Provide detailed, practical output in Chinese.
User request:
PROMPT
    echo "$INPUT" ;;
  iv) cat << 'PROMPT'
You are an expert. Help with: 隐含波动率. Provide detailed, practical output in Chinese.
User request:
PROMPT
    echo "$INPUT" ;;
  exercise) cat << 'PROMPT'
You are an expert. Help with: 行权分析. Provide detailed, practical output in Chinese.
User request:
PROMPT
    echo "$INPUT" ;;
  *) cat << 'EOF'
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Option Calculator — 使用指南
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  price           期权定价
  greeks          Greeks计算
  strategy        策略组合
  payoff          盈亏分析
  iv              隐含波动率
  exercise        行权分析

  Powered by BytesAgain | bytesagain.com | hello@bytesagain.com
EOF
    ;;
esac
