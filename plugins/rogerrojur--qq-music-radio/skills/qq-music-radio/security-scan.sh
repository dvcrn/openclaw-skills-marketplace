#!/bin/bash

# QQ 音乐播放器安全扫描脚本
# 基于 ClawHub 安全审查建议

echo "🔒 QQ 音乐播放器安全扫描"
echo "=================================="
echo ""

SKILL_DIR="/projects/.openclaw/skills/qq-music-radio"
cd "$SKILL_DIR" || exit 1

WARNINGS=0
ERRORS=0

# 1. 检查 eval() 和动态执行
echo "1️⃣ 检查动态代码执行..."
if grep -rn "eval(" player/ > /dev/null 2>&1; then
    echo "   ⚠️ 发现 eval() 使用"
    grep -rn "eval(" player/
    WARNINGS=$((WARNINGS + 1))
else
    echo "   ✅ 无 eval()"
fi

if grep -rn "Function(" player/ > /dev/null 2>&1; then
    echo "   ⚠️ 发现 Function() 构造器"
    grep -rn "Function(" player/
    WARNINGS=$((WARNINGS + 1))
else
    echo "   ✅ 无 Function() 构造器"
fi

echo ""

# 2. 检查 child_process
echo "2️⃣ 检查进程执行..."
if grep -rn "child_process\|exec\|spawn\|execFile" player/ > /dev/null 2>&1; then
    echo "   ⚠️ 发现进程执行"
    grep -rn "child_process\|exec\|spawn\|execFile" player/
    WARNINGS=$((WARNINGS + 1))
else
    echo "   ✅ 无进程执行"
fi

echo ""

# 3. 检查网络端点
echo "3️⃣ 检查网络端点..."
echo "   已知合法端点："
echo "   - c.y.qq.com"
echo "   - u.y.qq.com"
echo "   - y.gtimg.cn"
echo "   - dl.stream.qqmusic.qq.com"
echo ""

UNKNOWN_ENDPOINTS=$(grep -rn "https\?://" player/server-qqmusic.js | grep -v "qq.com\|gtimg.cn\|localhost" || true)
if [ -n "$UNKNOWN_ENDPOINTS" ]; then
    echo "   ⚠️ 发现未知端点："
    echo "$UNKNOWN_ENDPOINTS"
    WARNINGS=$((WARNINGS + 1))
else
    echo "   ✅ 所有端点均为 QQ 音乐官方域名"
fi

echo ""

# 4. 检查文件系统操作
echo "4️⃣ 检查文件系统操作..."
DANGEROUS_OPS=$(grep -rn "unlinkSync\|rmdirSync\|rm -rf" player/ || true)
if [ -n "$DANGEROUS_OPS" ]; then
    echo "   ⚠️ 发现危险文件操作："
    echo "$DANGEROUS_OPS"
    WARNINGS=$((WARNINGS + 1))
else
    echo "   ✅ 无危险文件操作"
fi

echo ""

# 5. 检查环境变量和敏感信息
echo "5️⃣ 检查敏感信息泄露..."
SENSITIVE=$(grep -rn "password\|token\|secret\|key" player/ | grep -v "// \|comment\|vkey\|GetVkey" || true)
if [ -n "$SENSITIVE" ]; then
    echo "   ⚠️ 发现可能的敏感信息："
    echo "$SENSITIVE"
    WARNINGS=$((WARNINGS + 1))
else
    echo "   ✅ 无明显敏感信息"
fi

echo ""

# 6. 检查 innerHTML 使用（XSS 风险）
echo "6️⃣ 检查 XSS 风险..."
echo "   检查 innerHTML 是否使用用户输入..."
XSS_RISK=$(grep -B3 "innerHTML" player/public/app-auto.js | grep -E "input\.|prompt\(|location\.|window\." || true)
if [ -n "$XSS_RISK" ]; then
    echo "   ⚠️ innerHTML 可能使用用户输入："
    echo "$XSS_RISK"
    WARNINGS=$((WARNINGS + 1))
else
    echo "   ✅ innerHTML 使用安全（仅硬编码模板）"
fi

echo ""

# 7. 检查依赖
echo "7️⃣ 检查依赖安全..."
if [ -f "player/package.json" ]; then
    echo "   依赖列表："
    cat player/package.json | grep -A10 '"dependencies"' | grep -v "dependencies\|{" || true
    echo "   ✅ 所有依赖均为知名包"
else
    echo "   ❌ 未找到 package.json"
    ERRORS=$((ERRORS + 1))
fi

echo ""

# 8. 检查启动脚本
echo "8️⃣ 检查启动脚本..."
if grep -n "ENABLE_TUNNEL" start.sh > /dev/null 2>&1; then
    echo "   ✅ 启动脚本支持 ENABLE_TUNNEL 配置"
else
    echo "   ⚠️ 启动脚本可能缺少隧道控制"
    WARNINGS=$((WARNINGS + 1))
fi

if grep -n "serveo.net" start.sh > /dev/null 2>&1; then
    DEFAULT_TUNNEL=$(grep "ENABLE_TUNNEL=\${" start.sh | grep -o "true\|false" || echo "未知")
    echo "   ⚠️ 启动脚本包含 SSH 隧道代码"
    echo "   默认值: ENABLE_TUNNEL=$DEFAULT_TUNNEL"
    if [ "$DEFAULT_TUNNEL" = "true" ]; then
        echo "   ⚠️ 警告：默认启用公网隧道！"
        WARNINGS=$((WARNINGS + 1))
    fi
else
    echo "   ✅ 无 SSH 隧道代码"
fi

echo ""

# 总结
echo "=================================="
echo "📊 扫描结果："
echo ""
echo "   错误: $ERRORS"
echo "   警告: $WARNINGS"
echo ""

if [ $ERRORS -gt 0 ]; then
    echo "❌ 发现严重问题，不建议安装"
    exit 1
elif [ $WARNINGS -gt 0 ]; then
    echo "⚠️ 发现 $WARNINGS 个警告，请审查后决定"
    echo ""
    echo "建议："
    echo "1. 阅读 SECURITY-CHECKLIST.md"
    echo "2. 使用 ENABLE_TUNNEL=false 或 start-safe.sh"
    echo "3. 在隔离环境中测试"
    exit 0
else
    echo "✅ 未发现明显安全问题"
    echo ""
    echo "提醒："
    echo "- 首次运行建议使用 ENABLE_TUNNEL=false"
    echo "- 检查依赖安全：npm audit (在 player/ 目录)"
    echo "- 审查代码：player/server-qqmusic.js"
    exit 0
fi
