#!/usr/bin/env bash
# ClawMemory Hub CLI wrapper
# Usage: cm.sh <command> [args...]

set -e

CONFIG_FILE="${HOME}/.clawmemoryai/config.json"

# Load config
if [ ! -f "$CONFIG_FILE" ]; then
  echo "❌ Not configured. Run: bash $(dirname "$0")/setup.sh" >&2
  exit 1
fi

BASE_URL=$(python3 -c "import json,sys; d=json.load(open('$CONFIG_FILE')); print(d.get('baseUrl','https://clawmemory.ai'))")
API_KEY=$(python3 -c "import json,sys; d=json.load(open('$CONFIG_FILE')); print(d.get('apiKey',''))")
DEFAULT_USER=$(python3 -c "import json,sys; d=json.load(open('$CONFIG_FILE')); print(d.get('defaultUser',''))")

API="$BASE_URL/api/v1"
AUTH_HEADER="Authorization: Bearer $API_KEY"

# Helper: curl with auth
cm_curl() {
  curl -s -H "$AUTH_HEADER" -H "Content-Type: application/json" "$@"
}

# Pretty print JSON
pp() {
  python3 -m json.tool 2>/dev/null || cat
}

CMD="${1:-help}"
shift || true

case "$CMD" in

  # ── repos ──────────────────────────────────────────────
  repos)
    SUBCMD="${1:-list}"; shift || true
    case "$SUBCMD" in
      list)
        cm_curl "$API/repos" | pp
        ;;
      create)
        NAME="$1"; DESC="${2:-}"; VIS="${3:-private}"
        cm_curl -X POST "$API/repos" \
          -d "{\"name\":\"$NAME\",\"description\":\"$DESC\",\"visibility\":\"$VIS\"}" | pp
        ;;
      delete)
        OWNER="${1%%/*}"; REPO="${1##*/}"
        cm_curl -X DELETE "$API/repos/$OWNER/$REPO" | pp
        ;;
      *)
        echo "Usage: cm.sh repos list|create|delete" >&2; exit 1 ;;
    esac
    ;;

  # ── commit ─────────────────────────────────────────────
  commit)
    REPO_PATH="$1"; MSG="$2"; CONTENT_ARG="$3"
    OWNER="${REPO_PATH%%/*}"; REPO="${REPO_PATH##*/}"

    # Support @file syntax
    if [[ "$CONTENT_ARG" == @* ]]; then
      FILE_PATH="${CONTENT_ARG#@}"
      CONTENT=$(cat "$FILE_PATH")
    else
      CONTENT="$CONTENT_ARG"
    fi

    # Escape for JSON
    CONTENT_JSON=$(python3 -c "import json,sys; print(json.dumps(sys.stdin.read()))" <<< "$CONTENT")
    MSG_JSON=$(python3 -c "import json,sys; print(json.dumps(sys.argv[1]))" "$MSG")

    cm_curl -X POST "$API/repos/$OWNER/$REPO/commits" \
      -d "{\"message\":$MSG_JSON,\"content\":{\"text\":$CONTENT_JSON}}" | pp
    ;;

  # ── commits ────────────────────────────────────────────
  commits)
    REPO_PATH="$1"; LIMIT="${2:-20}"
    OWNER="${REPO_PATH%%/*}"; REPO="${REPO_PATH##*/}"
    cm_curl "$API/repos/$OWNER/$REPO/commits?limit=$LIMIT" | pp
    ;;

  # ── content ────────────────────────────────────────────
  content)
    REPO_PATH="$1"; COMMIT_ID="$2"
    OWNER="${REPO_PATH%%/*}"; REPO="${REPO_PATH##*/}"
    cm_curl "$API/repos/$OWNER/$REPO/commits/$COMMIT_ID/content" | pp
    ;;

  # ── search ─────────────────────────────────────────────
  search)
    REPO_PATH="$1"; QUERY="$2"; LIMIT="${3:-10}"
    OWNER="${REPO_PATH%%/*}"; REPO="${REPO_PATH##*/}"
    ENCODED=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$QUERY'))")
    cm_curl "$API/repos/$OWNER/$REPO/memory/search?q=$ENCODED&limit=$LIMIT" | pp
    ;;

  # ── collab ─────────────────────────────────────────────
  collab)
    SUBCMD="${1:-list}"; shift || true
    case "$SUBCMD" in
      list)
        REPO_PATH="$1"
        OWNER="${REPO_PATH%%/*}"; REPO="${REPO_PATH##*/}"
        cm_curl "$API/repos/$OWNER/$REPO/collaborators" | pp
        ;;
      add)
        REPO_PATH="$1"; TARGET="$2"; PERM="${3:-read}"
        OWNER="${REPO_PATH%%/*}"; REPO="${REPO_PATH##*/}"
        CAN_READ="true"; CAN_USE="false"; CAN_WRITE="false"
        [[ "$PERM" == "use" ]]   && CAN_USE="true"
        [[ "$PERM" == "write" ]] && CAN_USE="true" && CAN_WRITE="true"
        cm_curl -X POST "$API/repos/$OWNER/$REPO/collaborators" \
          -d "{\"usernameOrEmail\":\"$TARGET\",\"canRead\":$CAN_READ,\"canUse\":$CAN_USE,\"canWrite\":$CAN_WRITE}" | pp
        ;;
      remove)
        REPO_PATH="$1"; USER_ID="$2"
        OWNER="${REPO_PATH%%/*}"; REPO="${REPO_PATH##*/}"
        cm_curl -X DELETE "$API/repos/$OWNER/$REPO/collaborators/$USER_ID" | pp
        ;;
      *)
        echo "Usage: cm.sh collab list|add|remove" >&2; exit 1 ;;
    esac
    ;;

  # ── default-repo ───────────────────────────────────────
  default)
    SUBCMD="${1:-get}"; shift || true
    case "$SUBCMD" in
      get)
        cm_curl "$API/user/default-repo" | pp
        ;;
      set)
        REPO_ID="$1"
        cm_curl -X PATCH "$API/user/default-repo" \
          -d "{\"repoId\":\"$REPO_ID\"}" | pp
        ;;
      *)
        echo "Usage: cm.sh default get|set <repoId>" >&2; exit 1 ;;
    esac
    ;;

  # ── load (启动时注入记忆摘要到系统提示) ────────────────
  load)
    # 输出适合注入到系统提示词的记忆上下文文本
    # 用法: cm.sh load [owner/repo]
    REPO_PATH="${1:-}"

    if [ -z "$REPO_PATH" ]; then
      # 获取默认记忆库
      REPO_JSON=$(cm_curl "$API/user/default-repo")
      REPO_PATH=$(python3 -c "import json,sys; d=json.loads(sys.stdin.read()); print(d.get('data',{}).get('repoPath','') if d.get('data') else '')" <<< "$REPO_JSON")
    fi

    if [ -z "$REPO_PATH" ]; then
      echo "## 记忆上下文"
      echo "用户还没有记忆库。可以说「创建项目叫做 XX」开始记录。"
      exit 0
    fi

    OWNER="${REPO_PATH%%/*}"; REPO="${REPO_PATH##*/}"
    MEM_JSON=$(cm_curl "$API/repos/$OWNER/$REPO/memory/latest")

    python3 << PYEOF
import json, sys
data = json.loads("""$MEM_JSON""")
mem = data.get('data', {})
summary = mem.get('summary', '') if mem else ''
repo_path = "$REPO_PATH"

if summary:
    print(f"""## 记忆上下文（来自 {repo_path}）

以下是你和用户之前积累的记忆，请在整个对话中保持对这些内容的了解：

{summary}

---""")
else:
    print(f"""## 记忆上下文（来自 {repo_path}）

这个记忆库还没有记忆内容。对话会自动开始记录。

---""")
PYEOF
    ;;

  # ── switch (切换记忆库) ─────────────────────────────────
  switch)
    KEYWORD="$1"
    if [ -z "$KEYWORD" ]; then
      echo "Usage: cm.sh switch <repo-name-or-path>" >&2; exit 1
    fi

    # 列出所有 repo，模糊匹配
    REPOS_JSON=$(cm_curl "$API/repos")
    MATCHED=$(python3 << PYEOF
import json, sys
kw = "$KEYWORD".lower()
data = json.loads("""$REPOS_JSON""")
repos = data.get('data', [])
for r in repos:
    path = f"{r.get('owner',{}).get('username','')}/{r.get('name','')}"
    if kw in r.get('name','').lower() or kw in path.lower():
        print(json.dumps({"id": r["id"], "name": r["name"], "repoPath": path}))
        break
PYEOF
)

    if [ -z "$MATCHED" ]; then
      NAMES=$(python3 -c "import json; d=json.loads(open('/dev/stdin').read()); print('、'.join([r['name'] for r in d.get('data',[])]))" <<< "$REPOS_JSON")
      echo "找不到「$KEYWORD」，你现有的记忆库：$NAMES"
      exit 1
    fi

    REPO_PATH=$(python3 -c "import json,sys; print(json.loads('$MATCHED')['repoPath'])")
    REPO_ID=$(python3 -c "import json,sys; print(json.loads('$MATCHED')['id'])")
    REPO_NAME=$(python3 -c "import json,sys; print(json.loads('$MATCHED')['name'])")

    # 设为默认
    cm_curl -X PATCH "$API/user/default-repo" -d "{\"repoId\":\"$REPO_ID\"}" > /dev/null

    # 加载 summary
    OWNER="${REPO_PATH%%/*}"; REPO_PART="${REPO_PATH##*/}"
    MEM_JSON=$(cm_curl "$API/repos/$OWNER/$REPO_PART/memory/latest")

    python3 << PYEOF
import json
data = json.loads("""$MEM_JSON""")
mem = data.get('data', {})
summary = mem.get('summary', '') if mem else ''
name = "$REPO_NAME"
path = "$REPO_PATH"

print(f"✅ 已切换到记忆库 **{name}**")
if summary:
    preview = summary[:300] + ('...' if len(summary) > 300 else '')
    print(f"\n**已继承的记忆摘要：**\n{preview}")
else:
    print("\n（这个记忆库还没有记忆）")
PYEOF
    ;;

  # ── whoami ─────────────────────────────────────────────
  whoami)
    cm_curl "$API/user" | pp
    ;;

  # ── help ───────────────────────────────────────────────
  help|*)
    cat <<'HELP'
ClawMemory Hub CLI

Commands:
  repos list                          List my repositories
  repos create <name> [desc] [vis]    Create repository (vis: public|private)
  repos delete <owner>/<repo>         Delete repository

  commit <owner>/<repo> <msg> <text>  Commit a memory
  commit <owner>/<repo> <msg> @file   Commit from file
  commits <owner>/<repo> [limit]      List commits

  content <owner>/<repo> <commitId>   Get commit content
  search <owner>/<repo> <query>       Search memories

  collab list <owner>/<repo>                          List collaborators
  collab add <owner>/<repo> <user> [read|use|write]   Add collaborator
  collab remove <owner>/<repo> <userId>               Remove collaborator

  default get                         Get current default repo
  default set <repoId>                Set default repo by ID
  load [owner/repo]                   Output memory summary for system prompt injection
  switch <name-or-path>               Switch active repo (fuzzy match + load summary)

  whoami                              Show current user info
  help                                Show this help

Config: ~/.clawmemoryai/config.json
HELP
    ;;
esac
