#!/bin/bash
# AI 确定性控制工具 - 测试脚本

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PASS=0
FAIL=0

echo "🧪 开始测试 AI 确定性控制工具"
echo "========================"

# 测试1：温度设置
echo ""
echo "测试1：温度参数设置"
if python3 -c "
import sys
sys.path.insert(0, '$SCRIPT_DIR')
from deterministic import set_temperature, get_temperature

result = set_temperature(0.2)
assert result['temperature'] == 0.2
assert result['mode'] == '高度确定性'

result = set_temperature(0.7)
assert result['temperature'] == 0.7
assert result['mode'] == '平衡模式'

result = set_temperature(1.2)
assert result['temperature'] == 1.2
assert result['mode'] == '高创造性模式'

print('  ✅ 温度设置测试通过')
"; then
    ((PASS++))
else
    echo "  ❌ 温度设置测试失败"
    ((FAIL++))
fi

# 测试2：温度范围验证
echo ""
echo "测试2：温度范围验证"
if python3 -c "
import sys
sys.path.insert(0, '$SCRIPT_DIR')
from deterministic import set_temperature

try:
    set_temperature(2.5)  # 超出范围
    sys.exit(1)  # 应该抛出异常
except ValueError:
    print('  ✅ 温度范围验证测试通过')
    sys.exit(0)
"; then
    ((PASS++))
else
    echo "  ❌ 温度范围验证测试失败"
    ((FAIL++))
fi

# 测试3：随机种子
echo ""
echo "测试3：随机种子设置"
if python3 -c "
import sys
sys.path.insert(0, '$SCRIPT_DIR')
from deterministic import set_seed, get_seed

result = set_seed(12345)
assert result['seed'] == 12345

seed = get_seed()
assert seed == 12345

print('  ✅ 随机种子测试通过')
"; then
    ((PASS++))
else
    echo "  ❌ 随机种子测试失败"
    ((FAIL++))
fi

# 测试4：一致性检查
echo ""
echo "测试4：一致性检查"
if python3 -c "
import sys
sys.path.insert(0, '$SCRIPT_DIR')
from consistency import check_consistency

outputs = ['测试输出', '测试输出', '测试输出']
result = check_consistency(outputs)
assert result['average_similarity'] == 100.0
assert result['consistency_level'] == '优秀'

print('  ✅ 一致性检查测试通过')
"; then
    ((PASS++))
else
    echo "  ❌ 一致性检查测试失败"
    ((FAIL++))
fi

# 测试5：CLI命令
echo ""
echo "测试5：CLI命令测试"
if bash deterministic.sh config > /dev/null 2>&1; then
    echo '  ✅ CLI命令测试通过'
    ((PASS++))
else
    echo '  ❌ CLI命令测试失败'
    ((FAIL++))
fi

# 输出测试结果
echo ""
echo "========================"
echo "📊 测试结果："
echo "  ✅ 通过: $PASS"
echo "  ❌ 失败: $FAIL"
echo ""

if [ $FAIL -eq 0 ]; then
    echo "🎉 所有测试通过！"
    exit 0
else
    echo "⚠️ 有 $FAIL 个测试失败"
    exit 1
fi
