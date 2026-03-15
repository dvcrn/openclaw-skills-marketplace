#!/usr/bin/env bash
# wechat.sh — 微信公众号文章生成器
# 用法: wechat.sh <command> [args]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

exec python3 "${SCRIPT_DIR}/wechat_core.py" "${@:-help}"
echo ""
echo "  Powered by BytesAgain | bytesagain.com | hello@bytesagain.com"
