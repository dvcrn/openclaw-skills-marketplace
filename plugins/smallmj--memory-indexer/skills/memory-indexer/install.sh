#!/bin/bash
#
# Memory Indexer 安装脚本
# 用法: ./install.sh
#

set -e

echo "🧠 Memory Indexer 安装程序"
echo "=============================="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}错误: 未找到 Python3${NC}"
    exit 1
fi

echo "✅ Python3 已安装: $(python3 --version)"

# 检查并创建 workspace 目录
WORKSPACE="${HOME}/.openclaw/workspace"
if [ ! -d "$WORKSPACE" ]; then
    echo -e "${YELLOW}警告: 未找到 OpenClaw workspace ($WORKSPACE)${NC}"
    echo "  将只在当前目录创建 memory-index 数据"
    WORKSPACE="$(pwd)/memory-index-data"
    mkdir -p "$WORKSPACE"
fi

# 安装 jieba
echo ""
echo "📦 安装依赖..."
if python3 -c "import jieba" 2>/dev/null; then
    echo "✅ jieba 已安装"
else
    uv pip install jieba || pip3 install jieba
    echo "✅ jieba 安装完成"
fi

# 创建软链接（可选）
SKILLS_DIR="$WORKSPACE/skills"
if [ -d "$SKILLS_DIR" ]; then
    echo ""
    echo "🔗 创建软链接到 skills 目录..."
    mkdir -p "$SKILLS_DIR"
    SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
    if [ ! -L "$SKILLS_DIR/memory-indexer" ]; then
        ln -sf "$SCRIPT_DIR" "$SKILLS_DIR/memory-indexer"
        echo "✅ 软链接创建完成: $SKILLS_DIR/memory-indexer"
    else
        echo "⚠️ 软链接已存在"
    fi
fi

# 配置 AGENTS.md
echo ""
echo "📝 配置 AGENTS.md..."
AGENTS_FILE="$WORKSPACE/AGENTS.md"
MEMORY_INDEXER_RULE='
### 🧠 Memory Indexer (长期记忆检索)

当需要回忆某事时，必须按以下顺序搜索：

1. **先用 memory-indexer 搜索**（检索关键词索引）
   - 使用 user_id + 关键词搜索
   - 搜索"偏好"、"项目"、"任务"等通用关键词
   ```bash
   cd ~/.openclaw/workspace && uv run python skills/memory-indexer/memory-indexer.py search "关键词"
   ```

2. **再用 memory_search 搜索**（检索原始记忆文件）
   ```bash
   memory_search query
   ```
'

if [ -f "$AGENTS_FILE" ]; then
    if grep -q "Memory Indexer" "$AGENTS_FILE" 2>/dev/null; then
        echo "⚠️ AGENTS.md 已包含 Memory Indexer 配置"
    else
        echo "$MEMORY_INDEXER_RULE" >> "$AGENTS_FILE"
        echo "✅ 已添加配置到 AGENTS.md"
    fi
else
    echo -e "${YELLOW}警告: 未找到 AGENTS.md，跳过配置${NC}"
fi

# 配置 MEMORY.md（强制规则）
echo ""
echo "📝 配置 MEMORY.md（强制规则）..."
MEMORY_FILE="$WORKSPACE/MEMORY.md"
MEMORY_RULE='
2. **保存记忆时** - 必须同时调用 memory-indexer 建立索引
   - 执行命令：`cd ~/.openclaw/workspace && uv run python skills/memory-indexer/memory-indexer.py add "记忆内容" [标签...]`
   - 搜索命令：`cd ~/.openclaw/workspace && uv run python skills/memory-indexer/memory-indexer.py search "关键词"`
3. **新会话开始时** - 自动调用 memory-indexer 搜索相关记忆
   - 执行命令：`cd ~/.openclaw/workspace && uv run python skills/memory-indexer/memory-indexer.py search "关键词"`
   - 触发条件：读取完 USER.md 后，自动搜索与用户相关的重要记忆（如项目、偏好等）'

if [ -f "$MEMORY_FILE" ]; then
    if grep -q "memory-indexer" "$MEMORY_FILE" 2>/dev/null; then
        echo "⚠️ MEMORY.md 已包含 memory-indexer 配置"
    else
        # 找到 "## 强制规则" 部分，在其后添加
        if grep -q "## 强制规则" "$MEMORY_FILE"; then
            sed -i "/## 强制规则/a\\$MEMORY_RULE" "$MEMORY_FILE"
            echo "✅ 已添加配置到 MEMORY.md"
        else
            echo -e "${YELLOW}警告: MEMORY.md 中未找到强制规则部分，跳过${NC}"
        fi
    fi
else
    echo -e "${YELLOW}警告: 未找到 MEMORY.md，跳过配置${NC}"
fi

# 配置 HEARTBEAT.md
echo ""
echo "📝 配置 HEARTBEAT.md..."
HEARTBEAT_FILE="$WORKSPACE/HEARTBEAT.md"
HEARTBEAT_RULE='
### 记忆索引同步
- 每次添加记忆时自动建立索引（add 命令已内置）
- 定期备份索引文件到 memory-index/ 目录
- 频率：每次保存记忆时自动执行

### 会话备份与精简
- 备份会话内容到 memory-indexer（关键词索引）
- 精简原会话文件到 ~10KB（避免无限增长）
- 脚本：`cd ~/.openclaw/workspace && uv run python skills/memory-indexer/session_backup.py`
- 频率：每次心跳时执行（自动增量处理最近 3 个会话）

### Memory 文件精简
- 备份 memory/*.md 到 memory-indexer
- 精简大文件到 ~10KB
- 脚本：`cd ~/.openclaw/workspace && uv run python skills/memory-indexer/memory_compact.py`
- 频率：每次心跳时执行'

if [ -f "$HEARTBEAT_FILE" ]; then
    if grep -q "记忆索引同步" "$HEARTBEAT_FILE" 2>/dev/null; then
        echo "⚠️ HEARTBEAT.md 已包含记忆索引配置"
    else
        echo "$HEARTBEAT_RULE" >> "$HEARTBEAT_FILE"
        echo "✅ 已添加配置到 HEARTBEAT.md"
    fi
else
    echo -e "${YELLOW}警告: 未找到 HEARTBEAT.md，跳过配置${NC}"
fi

# 配置 Cron（可选）
echo ""
echo "⏰ 配置 Cron 定时同步（可选）..."
read -p "是否配置每天自动同步? [y/N]: " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    CRON_CMD="0 6 * * * cd $WORKSPACE && python3 skills/memory-indexer/memory-indexer.py sync >> $WORKSPACE/logs/memory-indexer.log 2>&1"
    (crontab -l 2>/dev/null | grep -v "memory-indexer"; echo "$CRON_CMD") | crontab -
    echo "✅ Cron 配置完成（每天 6 点自动同步）"
fi

# 安装 Hook（新对话自动搜索记忆）
echo ""
echo "🪝 安装 Hook (memory-indexer-on-new)..."
HOOKS_DIR="${HOME}/.openclaw/hooks"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
if [ -d "$SCRIPT_DIR/hooks/memory-indexer-on-new" ]; then
    mkdir -p "$HOOKS_DIR"
    cp -rf "$SCRIPT_DIR/hooks/memory-indexer-on-new" "$HOOKS_DIR/"
    echo "✅ Hook 已安装到: $HOOKS_DIR/memory-indexer-on-new"
    echo "   重启 Gateway 使其生效: openclaw gateway restart"
else
    echo "⚠️ 未找到 Hook 目录，跳过"
fi

# 完成
echo ""
echo "=============================="
echo -e "${GREEN}🎉 安装完成！${NC}"
echo ""
echo "📖 使用方法:"
echo "  添加记忆:   python3 memory-indexer.py add \"记忆内容\""
echo "  搜索记忆:   python3 memory-indexer.py search \"关键词\""
echo "  同步索引:   python3 memory-indexer.py sync"
echo "  查看状态:   python3 memory-indexer.py status"
echo ""
echo "📖 OpenClaw 集成:"
echo "  命令: uv run python skills/memory-indexer/memory-indexer.py search \"关键词\""
echo ""
