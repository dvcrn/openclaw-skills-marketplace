#!/bin/bash
# Suno 自动登录环境检查脚本
# 模仿小红书 MCP 的 check_env.sh
# 用法: bash suno/check_env.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COOKIE_FILE="${SUNO_COOKIE_FILE:-$HOME/.suno/cookies.json}"
PYTHON="${SUNO_PYTHON:-python3}"

echo "=== 🎵 Suno 自动登录环境检查 ==="
echo ""

echo "=== 1. 检查 Python3 ==="
if command -v "$PYTHON" &>/dev/null; then
    PY_VER=$("$PYTHON" --version 2>&1)
    echo "✅ $PY_VER"
else
    echo "❌ 未找到 Python3，请先安装 Python 3.8+"
    exit 1
fi

echo ""
echo "=== 2. 检查 Playwright ==="
if "$PYTHON" -c "import playwright" 2>/dev/null; then
    echo "✅ Playwright 已安装"
else
    echo "❌ Playwright 未安装"
    echo "   请执行: pip install playwright && playwright install chromium"
    exit 1
fi

echo ""
echo "=== 3. 检查 Chromium 浏览器 ==="
# Playwright 的 chromium 通常安装在特定目录
if "$PYTHON" -c "
from playwright.sync_api import sync_playwright
import sys
try:
    p = sync_playwright().start()
    browser = p.chromium.launch(headless=True, args=['--no-sandbox'])
    browser.close()
    p.stop()
    print('✅ Chromium 浏览器可用')
except Exception as e:
    print(f'❌ Chromium 不可用: {e}')
    sys.exit(1)
" 2>/dev/null; then
    :
else
    echo "❌ Chromium 浏览器不可用"
    echo "   请执行: playwright install chromium"
    exit 1
fi

echo ""
echo "=== 4. 检查 Cookie 文件 ==="
if [ -f "$COOKIE_FILE" ]; then
    COOKIE_COUNT=$(python3 -c "import json; print(len(json.load(open('$COOKIE_FILE'))))" 2>/dev/null || echo "0")
    COOKIE_AGE=$(python3 -c "
import os, time
age = time.time() - os.path.getmtime('$COOKIE_FILE')
days = age / 86400
if days < 1:
    print(f'{age/3600:.1f} 小时前')
else:
    print(f'{days:.1f} 天前')
" 2>/dev/null || echo "未知")
    echo "✅ Cookie 文件存在: $COOKIE_FILE"
    echo "   数量: ${COOKIE_COUNT} 条"
    echo "   保存: ${COOKIE_AGE}"
else
    echo "⚠️ Cookie 文件不存在: $COOKIE_FILE"
    echo "   需要先登录（运行 suno_login.py）"
    exit 2
fi

echo ""
echo "=== 5. 检查登录状态 ==="
"$PYTHON" "$SCRIPT_DIR/suno_login.py" --check-only 2>/dev/null
CHECK_EXIT=$?

if [ $CHECK_EXIT -eq 0 ]; then
    echo ""
    echo "=== ✅ 所有检查通过，可以正常使用 ==="
    exit 0
elif [ $CHECK_EXIT -eq 2 ]; then
    echo "❌ 未登录（Cookie 可能已过期）"
    echo "   请运行: python $SCRIPT_DIR/suno_login.py --email <邮箱> --password <密码>"
    exit 2
else
    echo "❌ 登录状态检查失败"
    echo "   请检查网络连接或重新登录"
    exit 2
fi
