#!/usr/bin/env bash
CMD="$1"; shift 2>/dev/null; INPUT="$*"
case "$CMD" in
  apy) cat << 'PROMPT'
You are an expert. Help with: APY/APR计算. Provide detailed, practical output in Chinese.
User request:
PROMPT
    echo "$INPUT" ;;
  impermanent) cat << 'PROMPT'
You are an expert. Help with: 无常损失计算. Provide detailed, practical output in Chinese.
User request:
PROMPT
    echo "$INPUT" ;;
  farming) cat << 'PROMPT'
You are an expert. Help with: 流动性挖矿分析. Provide detailed, practical output in Chinese.
User request:
PROMPT
    echo "$INPUT" ;;
  staking) cat << 'PROMPT'
You are an expert. Help with: 质押收益. Provide detailed, practical output in Chinese.
User request:
PROMPT
    echo "$INPUT" ;;
  gas) cat << 'PROMPT'
You are an expert. Help with: Gas费估算. Provide detailed, practical output in Chinese.
User request:
PROMPT
    echo "$INPUT" ;;
  compare) cat << 'PROMPT'
You are an expert. Help with: 协议收益对比. Provide detailed, practical output in Chinese.
User request:
PROMPT
    echo "$INPUT" ;;
  *) cat << 'EOF'
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  DeFi Calculator — 使用指南
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  apy             APY/APR计算
  impermanent     无常损失计算
  farming         流动性挖矿分析
  staking         质押收益
  gas             Gas费估算
  compare         协议收益对比

  Powered by BytesAgain | bytesagain.com | hello@bytesagain.com
EOF
    ;;
esac
