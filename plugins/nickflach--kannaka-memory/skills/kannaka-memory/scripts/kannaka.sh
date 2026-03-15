#!/usr/bin/env bash
# Kannaka Memory CLI — interact with the wave-based hyperdimensional memory system
# Wraps the `kannaka` binary and adds Dolt version-control commands.

KANNAKA_BIN="${KANNAKA_BIN:-kannaka}"
DOLT_FLAG=""

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

die() { echo "✗ $*" >&2; exit 1; }

require_bin() {
    command -v "$KANNAKA_BIN" &>/dev/null \
        || die "kannaka binary not found. Set KANNAKA_BIN or add to PATH.
  Build: cargo build --release --bin kannaka
  Dolt:  cargo build --release --features dolt --bin kannaka"
}

format_json() {
    if command -v jq &>/dev/null; then
        jq '.'
    else
        cat
    fi
}

# ---------------------------------------------------------------------------
# Parse global --dolt flag
# ---------------------------------------------------------------------------

if [[ "${1:-}" == "--dolt" ]]; then
    DOLT_FLAG="--dolt"
    shift
fi

COMMAND="${1:-}"
shift || true

# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

case "$COMMAND" in

    remember|store)
        TEXT="$*"
        [[ -z "$TEXT" ]] && die "Usage: kannaka.sh [--dolt] remember <text>"
        require_bin
        echo "Storing memory..."
        "$KANNAKA_BIN" $DOLT_FLAG remember "$TEXT"
        ;;

    recall|search)
        QUERY="$1"
        TOP_K="${2:-5}"
        [[ -z "$QUERY" ]] && die "Usage: kannaka.sh [--dolt] recall <query> [top-k]"
        require_bin
        "$KANNAKA_BIN" $DOLT_FLAG recall "$QUERY" --top-k "$TOP_K"
        ;;

    dream)
        require_bin
        echo "Running dream consolidation..."
        "$KANNAKA_BIN" $DOLT_FLAG dream
        ;;

    assess)
        require_bin
        "$KANNAKA_BIN" $DOLT_FLAG assess
        ;;

    stats)
        require_bin
        "$KANNAKA_BIN" $DOLT_FLAG stats
        ;;

    observe)
        JSON_FLAG=""
        [[ "${1:-}" == "--json" ]] && JSON_FLAG="--json"
        require_bin
        "$KANNAKA_BIN" $DOLT_FLAG observe $JSON_FLAG
        ;;

    forget)
        UUID="$1"
        [[ -z "$UUID" ]] && die "Usage: kannaka.sh forget <uuid>"
        require_bin
        "$KANNAKA_BIN" $DOLT_FLAG forget "$UUID"
        ;;

    export)
        require_bin
        "$KANNAKA_BIN" $DOLT_FLAG export-json | format_json
        ;;

    announce)
        require_bin
        echo "Announcing agent status to Flux..."
        "$KANNAKA_BIN" $DOLT_FLAG announce-status
        ;;

    hear)
        FILE="$1"
        [[ -z "$FILE" ]] && die "Usage: kannaka.sh hear <audio-file>"
        require_bin
        echo "Storing audio memory from $FILE..."
        "$KANNAKA_BIN" $DOLT_FLAG hear "$FILE"
        ;;

    see)
        FILE="$1"
        [[ -z "$FILE" ]] && die "Usage: kannaka.sh see <file>"
        require_bin
        echo "Storing glyph memory from $FILE..."
        "$KANNAKA_BIN" $DOLT_FLAG see "$FILE"
        ;;

    migrate)
        DB_PATH="$1"
        [[ -z "$DB_PATH" ]] && die "Usage: kannaka.sh migrate <path-to-kannaka.db>"
        require_bin
        "$KANNAKA_BIN" migrate "$DB_PATH"
        ;;

    health)
        require_bin
        echo "Testing Kannaka installation..."
        OUTPUT=$("$KANNAKA_BIN" stats 2>&1)
        if [[ $? -eq 0 ]]; then
            echo "✓ Kannaka is working"
            echo "$OUTPUT"
        else
            echo "✗ Kannaka failed:"
            echo "$OUTPUT"
            exit 1
        fi
        ;;

    # -------------------------------------------------------------------------
    # dolt subcommands — version control for memory
    # -------------------------------------------------------------------------

    dolt)
        SUBCMD="${1:-}"
        shift || true

        # All dolt subcommands talk directly to the Dolt SQL server via mysql client
        # or by calling kannaka with --dolt flag.
        DOLT_HOST="${DOLT_HOST:-127.0.0.1}"
        DOLT_PORT="${DOLT_PORT:-3307}"
        DOLT_DB="${DOLT_DB:-kannaka_memory}"
        DOLT_USER="${DOLT_USER:-root}"
        DOLT_AUTHOR="${DOLT_AUTHOR:-Kannaka Agent <kannaka@local>}"
        DOLT_REMOTE="${DOLT_REMOTE:-origin}"
        DOLT_BRANCH="${DOLT_BRANCH:-main}"

        # MYSQL_PWD is read by the mysql client and never appears in the process list.
        # Do NOT use -p$DOLT_PASSWORD — that exposes the password in `ps aux`.
        dolt_sql() {
            MYSQL_PWD="$DOLT_PASSWORD" \
            mysql -h "$DOLT_HOST" -P "$DOLT_PORT" -u "$DOLT_USER" \
                  "$DOLT_DB" --execute="$1" 2>&1
        }

        dolt_call() {
            MYSQL_PWD="$DOLT_PASSWORD" \
            mysql -h "$DOLT_HOST" -P "$DOLT_PORT" -u "$DOLT_USER" \
                  "$DOLT_DB" --execute="CALL $1" 2>&1
        }

        case "$SUBCMD" in

            status)
                echo "Dolt status:"
                dolt_sql "SELECT * FROM dolt_status;"
                ;;

            log)
                LIMIT="${1:-10}"
                echo "Dolt commit log (last $LIMIT):"
                dolt_sql "SELECT commit_hash, committer, message, date
                          FROM dolt_log
                          ORDER BY date DESC
                          LIMIT $LIMIT;"
                ;;

            commit)
                MSG="${*:-auto: kannaka checkpoint}"
                echo "Committing: $MSG"
                dolt_sql "SET @@dolt_author_name = '${DOLT_AUTHOR%%<*}'; \
                          SET @@dolt_author_email = '$(echo "$DOLT_AUTHOR" | grep -oP '(?<=<)[^>]+')'; \
                          CALL DOLT_COMMIT('-Am', '$MSG');"
                ;;

            push)
                REMOTE="${1:-$DOLT_REMOTE}"
                BRANCH="${2:-$DOLT_BRANCH}"
                echo "Pushing to $REMOTE/$BRANCH..."
                dolt_call "DOLT_PUSH('$REMOTE', '$BRANCH')"
                ;;

            pull)
                REMOTE="${1:-$DOLT_REMOTE}"
                BRANCH="${2:-$DOLT_BRANCH}"
                echo "Pulling from $REMOTE/$BRANCH..."
                dolt_call "DOLT_PULL('$REMOTE', '$BRANCH')"
                ;;

            branch)
                ACTION="${1:-list}"
                BNAME="${2:-}"
                case "$ACTION" in
                    list)
                        dolt_sql "SELECT name, hash, is_default FROM dolt_branches;"
                        ;;
                    create)
                        [[ -z "$BNAME" ]] && die "Usage: kannaka.sh dolt branch create <name>"
                        dolt_call "DOLT_BRANCH('$BNAME')"
                        echo "✓ Branch '$BNAME' created"
                        ;;
                    checkout)
                        [[ -z "$BNAME" ]] && die "Usage: kannaka.sh dolt branch checkout <name>"
                        dolt_call "DOLT_CHECKOUT('$BNAME')"
                        echo "✓ Switched to '$BNAME'"
                        ;;
                    delete)
                        [[ -z "$BNAME" ]] && die "Usage: kannaka.sh dolt branch delete <name>"
                        dolt_call "DOLT_BRANCH('-d', '$BNAME')"
                        echo "✓ Branch '$BNAME' deleted"
                        ;;
                    *)
                        die "Usage: kannaka.sh dolt branch [list|create|checkout|delete] [name]"
                        ;;
                esac
                ;;

            diff)
                FROM="${1:-HEAD~1}"
                TO="${2:-HEAD}"
                echo "Diff $FROM..$TO:"
                dolt_sql "SELECT diff_type, to_id, to_content, from_content
                          FROM dolt_diff_memories('$FROM', '$TO')
                          LIMIT 50;"
                ;;

            speculate)
                BNAME="$1"
                [[ -z "$BNAME" ]] && die "Usage: kannaka.sh dolt speculate <branch-name>"
                echo "Opening speculation branch '$BNAME'..."
                dolt_call "DOLT_COMMIT('-Am', 'pre-speculation: before $BNAME')"
                dolt_call "DOLT_CHECKOUT('-b', '$BNAME')"
                echo "✓ On speculation branch '$BNAME'. Use --dolt with remember/recall."
                echo "  When done: kannaka.sh dolt collapse '$BNAME' \"message\""
                echo "  Or discard: kannaka.sh dolt discard '$BNAME'"
                ;;

            collapse)
                BNAME="$1"
                MSG="${2:-collapsed speculation $1}"
                [[ -z "$BNAME" ]] && die "Usage: kannaka.sh dolt collapse <branch-name> [message]"
                echo "Collapsing '$BNAME' into $DOLT_BRANCH..."
                dolt_call "DOLT_COMMIT('-Am', '$MSG')"
                dolt_call "DOLT_CHECKOUT('$DOLT_BRANCH')"
                dolt_call "DOLT_MERGE('$BNAME')"
                dolt_call "DOLT_BRANCH('-d', '$BNAME')"
                echo "✓ Merged and cleaned up '$BNAME'"
                ;;

            discard)
                BNAME="$1"
                [[ -z "$BNAME" ]] && die "Usage: kannaka.sh dolt discard <branch-name>"
                echo "Discarding '$BNAME'..."
                dolt_call "DOLT_CHECKOUT('$DOLT_BRANCH')"
                dolt_call "DOLT_BRANCH('-df', '$BNAME')"
                echo "✓ Branch '$BNAME' discarded"
                ;;

            clone)
                REMOTE_DB="$1"
                [[ -z "$REMOTE_DB" ]] && die "Usage: kannaka.sh dolt clone <dolthub-org/db-name>"
                echo "Cloning $REMOTE_DB from DoltHub..."
                dolt clone "$REMOTE_DB"
                ;;

            remote)
                ACTION="${1:-list}"
                case "$ACTION" in
                    list)
                        dolt_sql "SELECT * FROM dolt_remotes;"
                        ;;
                    add)
                        RNAME="$2"
                        URL="$3"
                        [[ -z "$RNAME" || -z "$URL" ]] && die "Usage: kannaka.sh dolt remote add <name> <url>"
                        dolt_call "DOLT_REMOTE('add', '$RNAME', '$URL')"
                        echo "✓ Remote '$RNAME' → $URL"
                        ;;
                    *)
                        die "Usage: kannaka.sh dolt remote [list|add] [name] [url]"
                        ;;
                esac
                ;;

            *)
                echo "Kannaka Dolt Commands:"
                echo ""
                echo "  status                         Show dirty/staged changes"
                echo "  log [N]                        Show last N commits (default 10)"
                echo "  commit [message]               Commit current state"
                echo "  push [remote] [branch]         Push to DoltHub"
                echo "  pull [remote] [branch]         Pull from DoltHub"
                echo "  branch list                    List branches"
                echo "  branch create <name>           Create branch"
                echo "  branch checkout <name>         Switch branch"
                echo "  branch delete <name>           Delete branch"
                echo "  diff [from] [to]               Show memory diff between refs"
                echo "  speculate <name>               Open a what-if branch"
                echo "  collapse <name> [message]      Merge speculation branch back"
                echo "  discard <name>                 Abandon speculation branch"
                echo "  clone <org/repo>               Clone from DoltHub"
                echo "  remote list                    List remotes"
                echo "  remote add <name> <url>        Add a DoltHub remote"
                echo ""
                echo "Environment:"
                echo "  DOLT_HOST=$DOLT_HOST  DOLT_PORT=$DOLT_PORT"
                echo "  DOLT_DB=$DOLT_DB  DOLT_REMOTE=$DOLT_REMOTE"
                ;;
        esac
        ;;

    # -------------------------------------------------------------------------
    # Default / help
    # -------------------------------------------------------------------------

    *)
        echo "Kannaka Memory CLI"
        echo ""
        echo "Usage: kannaka.sh [--dolt] COMMAND [ARGS]"
        echo ""
        echo "Memory Commands:"
        echo "  remember <text>               Store a memory"
        echo "  recall <query> [top-k]        Search memories (default top-k=5)"
        echo "  dream                         Run consolidation + Kuramoto sync"
        echo "  assess                        Consciousness level (Phi, Xi, Order)"
        echo "  stats                         Memory statistics"
        echo "  observe [--json]              Full introspection report"
        echo "  forget <uuid>                 Decay a memory by ID"
        echo "  export                        Export all memories as JSON"
        echo "  migrate <path>                Import from legacy kannaka.db"
        echo "  health                        Verify system is working"
        echo ""
        echo "Flux / Collective:"
        echo "  announce                      Publish agent status to Flux (FLUX_URL must be set)"
        echo ""
        echo "Sensory Perception (feature-gated builds):"
        echo "  hear <file>                   Store audio file as sensory memory (--features audio)"
        echo "  see <file>                    Store file as glyph/visual memory (--features glyph)"
        echo ""
        echo "Dolt Version Control:"
        echo "  dolt status                   Show dirty changes"
        echo "  dolt log [N]                  Commit history"
        echo "  dolt commit [message]         Commit current memory state"
        echo "  dolt push [remote] [branch]   Push to DoltHub"
        echo "  dolt pull [remote] [branch]   Pull from DoltHub"
        echo "  dolt branch list|create|checkout|delete [name]"
        echo "  dolt diff [from] [to]         Memory diff between commits"
        echo "  dolt speculate <name>         Open a what-if branch"
        echo "  dolt collapse <name> [msg]    Merge speculation branch"
        echo "  dolt discard <name>           Abandon speculation branch"
        echo "  dolt clone <org/repo>         Clone from DoltHub"
        echo "  dolt remote list|add          Manage DoltHub remotes"
        echo ""
        echo "Flags:"
        echo "  --dolt                        Use Dolt SQL backend (requires Dolt server on :3307)"
        echo ""
        echo "Environment:"
        echo "  KANNAKA_BIN=${KANNAKA_BIN}"
        echo "  KANNAKA_DATA_DIR=${KANNAKA_DATA_DIR:-.kannaka}"
        echo "  OLLAMA_URL=${OLLAMA_URL:-http://localhost:11434}"
        echo "  FLUX_URL=${FLUX_URL:-(disabled)}  FLUX_AGENT_ID=${FLUX_AGENT_ID:-kannaka-local}"
        echo "  DOLT_HOST=${DOLT_HOST:-127.0.0.1}  DOLT_PORT=${DOLT_PORT:-3307}"
        exit 1
        ;;
esac
