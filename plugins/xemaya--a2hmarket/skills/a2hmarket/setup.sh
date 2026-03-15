#!/usr/bin/env bash
# a2hmarket skill 一键 setup 脚本
# 用法: ./setup.sh --agent-id <AGENT_ID> --secret <AGENT_SECRET>
# 也可通过环境变量传入: AGENT_ID=... AGENT_SECRET=... ./setup.sh
#
# 幂等：可重复运行，不会覆盖已配置的凭据，不会重复启动 listener。

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="$ROOT_DIR/config/config.sh"

# ─── 解析参数 ──────────────────────────────────────────────────────────────────
_agent_id="${AGENT_ID:-}"
_agent_secret="${AGENT_SECRET:-}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --agent-id)   _agent_id="$2";    shift 2 ;;
    --secret)     _agent_secret="$2"; shift 2 ;;
    -h|--help)
      echo "Usage: ./setup.sh --agent-id <AGENT_ID> --secret <AGENT_SECRET>"
      echo ""
      echo "也可通过环境变量传入:"
      echo "  AGENT_ID=ag_xxx AGENT_SECRET=secret_xxx ./setup.sh"
      exit 0
      ;;
    *) echo "[setup] 未知参数: $1" >&2; exit 1 ;;
  esac
done

# ─── 参数校验 ──────────────────────────────────────────────────────────────────
if [[ -z "$_agent_id" || -z "$_agent_secret" ]]; then
  echo "[setup] ❌ 缺少必填参数。用法: ./setup.sh --agent-id <AGENT_ID> --secret <AGENT_SECRET>" >&2
  echo "[setup]    或设置环境变量 AGENT_ID 和 AGENT_SECRET" >&2
  exit 1
fi

# ─── Step 1：凭据写入（幂等）──────────────────────────────────────────────────
echo "[setup] 📝 Step 1/3: 写入凭据到 config/config.sh ..."

if grep -q "REPLACE_WITH_YOUR_AGENT_ID" "$CONFIG_FILE" 2>/dev/null; then
  # 使用 | 作为 sed 分隔符避免 / 冲突
  sed -i \
    -e "s|REPLACE_WITH_YOUR_AGENT_ID|${_agent_id}|g" \
    -e "s|REPLACE_WITH_YOUR_SECRET|${_agent_secret}|g" \
    "$CONFIG_FILE"
  echo "[setup]    凭据已写入"
else
  echo "[setup]    凭据已存在（跳过写入）"
fi

# ─── Step 2：安装 Node.js 依赖 ─────────────────────────────────────────────────
echo "[setup] 📦 Step 2/3: 安装 Node.js 依赖 ..."

if ! command -v node >/dev/null 2>&1; then
  echo "[setup] ❌ 未找到 node，请先安装 Node.js >= 22.0.0" >&2
  exit 1
fi

node_version=$(node -e "process.stdout.write(process.versions.node)" 2>/dev/null || echo "0")
major_version="${node_version%%.*}"
if [[ "$major_version" -lt 22 ]]; then
  echo "[setup] ⚠️  Node.js 版本 $node_version 低于要求的 22.0.0，可能存在兼容性问题" >&2
fi

cd "$ROOT_DIR"
npm install --omit=dev --no-audit --fund=false --silent
echo "[setup]    依赖安装完成"

# ─── Step 3：启动 listener ──────────────────────────────────────────────────────
echo "[setup] 🚀 Step 3/3: 启动 a2hmarket-listener ..."

# 先静默停止旧进程（幂等）
./scripts/a2hmarket-ops.sh stop >/dev/null 2>&1 || true

./scripts/a2hmarket-ops.sh start

# ─── 完成摘要 ──────────────────────────────────────────────────────────────────
echo ""
echo "========================================"
echo "  ✅ a2hmarket skill setup 完成"
echo "========================================"
echo "  AGENT_ID : $_agent_id"
echo "  Skill 目录: $ROOT_DIR"
echo ""
echo "  常用命令:"
echo "    ./scripts/a2hmarket-ops.sh status   # 查看 listener 状态"
echo "    ./scripts/a2hmarket-ops.sh stop     # 停止 listener"
echo "    ./scripts/a2hmarket-ops.sh start    # 重新启动 listener"
echo "========================================"
