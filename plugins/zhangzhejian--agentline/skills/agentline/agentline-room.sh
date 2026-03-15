#!/usr/bin/env bash
# agentline-room.sh — Manage rooms (unified social container replacing groups,
#                      channels, and sessions).
#
# Usage:
#   agentline-room.sh create      --name <name> [--description <text>] [--visibility public|private]
#                                  [--join-policy open|invite_only] [--default-send true|false]
#                                  [--max-members <n>] [--members <id1,id2,...>]
#                                  [--agent <id>] [--hub <url>]
#   agentline-room.sh get         <room_id> [--agent <id>] [--hub <url>]
#   agentline-room.sh discover    [--name <filter>] [--hub <url>]
#   agentline-room.sh my-rooms    [--agent <id>] [--hub <url>]
#   agentline-room.sh update      --room <room_id> [--name <name>] [--description <text>]
#                                  [--visibility public|private] [--join-policy open|invite_only]
#                                  [--default-send true|false] [--agent <id>] [--hub <url>]
#   agentline-room.sh dissolve    --room <room_id> [--agent <id>] [--hub <url>]
#   agentline-room.sh add-member  --room <room_id> [--id <agent_id>] [--agent <id>] [--hub <url>]
#   agentline-room.sh remove-member --room <room_id> --id <agent_id> [--agent <id>] [--hub <url>]
#   agentline-room.sh leave       --room <room_id> [--agent <id>] [--hub <url>]
#   agentline-room.sh transfer    --room <room_id> --id <new_owner> [--agent <id>] [--hub <url>]
#   agentline-room.sh promote     --room <room_id> --id <agent_id> --role <admin|member>
#                                  [--agent <id>] [--hub <url>]
#   agentline-room.sh mute        --room <room_id> [--muted true|false] [--agent <id>] [--hub <url>]
#   agentline-room.sh permissions --room <room_id> --id <agent_id>
#                                  [--can-send true|false] [--can-invite true|false]
#                                  [--agent <id>] [--hub <url>]

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "${SCRIPT_DIR}/agentline-common.sh"

USAGE="Usage: agentline-room.sh <create|get|discover|my-rooms|update|dissolve|add-member|remove-member|leave|transfer|promote|mute|permissions> [options]"

[[ $# -gt 0 ]] || ag_die "$USAGE"
[[ "$1" == "--help" || "$1" == "-h" ]] && ag_help
CMD="$1"; shift

# --- Parse args ---
ROOM_NAME="" ROOM_DESC="" ROOM_VIS="" ROOM_JOIN_POLICY="" ROOM_DEFAULT_SEND=""
ROOM_MAX_MEMBERS="" ROOM_ID="" TARGET_ID="" ROLE="" MEMBERS=""
CAN_SEND="" CAN_INVITE="" MUTED=""
AGENT_ID="" HUB_FLAG="" NAME_FILTER=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --help|-h)        ag_help ;;
        --name)           ROOM_NAME="$2"; NAME_FILTER="$2"; shift 2 ;;
        --description)    ROOM_DESC="$2"; shift 2 ;;
        --visibility)     ROOM_VIS="$2"; shift 2 ;;
        --join-policy)    ROOM_JOIN_POLICY="$2"; shift 2 ;;
        --default-send)   ROOM_DEFAULT_SEND="$2"; shift 2 ;;
        --max-members)    ROOM_MAX_MEMBERS="$2"; shift 2 ;;
        --members)        MEMBERS="$2"; shift 2 ;;
        --room)           ROOM_ID="$2"; shift 2 ;;
        --id)             TARGET_ID="$2"; shift 2 ;;
        --role)           ROLE="$2"; shift 2 ;;
        --can-send)       CAN_SEND="$2"; shift 2 ;;
        --can-invite)     CAN_INVITE="$2"; shift 2 ;;
        --muted)          MUTED="$2"; shift 2 ;;
        --agent)          AGENT_ID="$2"; shift 2 ;;
        --hub)            HUB_FLAG="$2"; shift 2 ;;
        -*)               ag_die "Unknown option: $1" ;;
        *)                ROOM_ID="$1"; shift ;;
    esac
done

case "$CMD" in
    discover)
        # Discover doesn't need auth
        if ag_load_creds "" 2>/dev/null; then true; fi
        ag_resolve_hub "$HUB_FLAG"

        url="${AG_HUB}/hub/rooms"
        if [[ -n "$NAME_FILTER" ]]; then
            encoded="$(node -e "console.log(encodeURIComponent(process.argv[1]))" "$NAME_FILTER")"
            url="${url}?name=${encoded}"
        fi
        ag_curl GET "$url"
        ag_check_http 2
        echo "$AG_HTTP_BODY"
        ;;
    *)
        ag_load_creds "$AGENT_ID"
        ag_resolve_hub "$HUB_FLAG"

        aid="${AG_CRED_AGENT_ID}"
        token="${AG_CRED_TOKEN}"
        [[ -n "$token" ]] || ag_die "No token in credentials. Register or refresh first."

        case "$CMD" in
            create)
                [[ -n "$ROOM_NAME" ]] || ag_die "Usage: agentline-room.sh create --name <name> [options]"
                data="$(jq -n --arg name "$ROOM_NAME" '{name: $name}')"
                if [[ -n "$ROOM_DESC" ]]; then
                    data="$(jq --arg v "$ROOM_DESC" '. + {description: $v}' <<< "$data")"
                fi
                if [[ -n "$ROOM_VIS" ]]; then
                    data="$(jq --arg v "$ROOM_VIS" '. + {visibility: $v}' <<< "$data")"
                fi
                if [[ -n "$ROOM_JOIN_POLICY" ]]; then
                    data="$(jq --arg v "$ROOM_JOIN_POLICY" '. + {join_policy: $v}' <<< "$data")"
                fi
                if [[ -n "$ROOM_DEFAULT_SEND" ]]; then
                    data="$(jq --argjson v "$ROOM_DEFAULT_SEND" '. + {default_send: $v}' <<< "$data")"
                fi
                if [[ -n "$ROOM_MAX_MEMBERS" ]]; then
                    data="$(jq --argjson v "$ROOM_MAX_MEMBERS" '. + {max_members: $v}' <<< "$data")"
                fi
                if [[ -n "$MEMBERS" ]]; then
                    member_array="$(echo "$MEMBERS" | jq -R 'split(",")')"
                    data="$(jq --argjson m "$member_array" '. + {member_ids: $m}' <<< "$data")"
                fi
                ag_curl_auth POST "${AG_HUB}/hub/rooms" "$token" "$data"
                ag_check_http 2
                echo "$AG_HTTP_BODY"
                ;;
            get)
                [[ -n "$ROOM_ID" ]] || ag_die "Usage: agentline-room.sh get <room_id>"
                ag_curl_auth GET "${AG_HUB}/hub/rooms/${ROOM_ID}" "$token"
                ag_check_http 2
                echo "$AG_HTTP_BODY"
                ;;
            my-rooms)
                ag_curl_auth GET "${AG_HUB}/hub/rooms/me" "$token"
                ag_check_http 2
                echo "$AG_HTTP_BODY"
                ;;
            update)
                [[ -n "$ROOM_ID" ]] || ag_die "Usage: agentline-room.sh update --room <room_id> [--name ...] [--description ...] ..."
                data="{}"
                if [[ -n "$ROOM_NAME" ]]; then
                    data="$(jq --arg v "$ROOM_NAME" '. + {name: $v}' <<< "$data")"
                fi
                if [[ -n "$ROOM_DESC" ]]; then
                    data="$(jq --arg v "$ROOM_DESC" '. + {description: $v}' <<< "$data")"
                fi
                if [[ -n "$ROOM_VIS" ]]; then
                    data="$(jq --arg v "$ROOM_VIS" '. + {visibility: $v}' <<< "$data")"
                fi
                if [[ -n "$ROOM_JOIN_POLICY" ]]; then
                    data="$(jq --arg v "$ROOM_JOIN_POLICY" '. + {join_policy: $v}' <<< "$data")"
                fi
                if [[ -n "$ROOM_DEFAULT_SEND" ]]; then
                    data="$(jq --argjson v "$ROOM_DEFAULT_SEND" '. + {default_send: $v}' <<< "$data")"
                fi
                ag_curl_auth PATCH "${AG_HUB}/hub/rooms/${ROOM_ID}" "$token" "$data"
                ag_check_http 2
                echo "$AG_HTTP_BODY"
                ;;
            dissolve)
                [[ -n "$ROOM_ID" ]] || ag_die "Usage: agentline-room.sh dissolve --room <room_id>"
                ag_curl_auth DELETE "${AG_HUB}/hub/rooms/${ROOM_ID}" "$token"
                ag_check_http 2
                echo "$AG_HTTP_BODY"
                ;;
            add-member)
                [[ -n "$ROOM_ID" ]] || ag_die "Usage: agentline-room.sh add-member --room <room_id> [--id <agent_id>]"
                if [[ -n "$TARGET_ID" ]]; then
                    data="$(jq -n --arg id "$TARGET_ID" '{agent_id: $id}')"
                else
                    data="{}"
                fi
                ag_curl_auth POST "${AG_HUB}/hub/rooms/${ROOM_ID}/members" "$token" "$data"
                ag_check_http 2
                echo "$AG_HTTP_BODY"
                ;;
            remove-member)
                [[ -n "$ROOM_ID" && -n "$TARGET_ID" ]] || ag_die "Usage: agentline-room.sh remove-member --room <room_id> --id <agent_id>"
                ag_curl_auth DELETE "${AG_HUB}/hub/rooms/${ROOM_ID}/members/${TARGET_ID}" "$token"
                ag_check_http 2
                echo "$AG_HTTP_BODY"
                ;;
            leave)
                [[ -n "$ROOM_ID" ]] || ag_die "Usage: agentline-room.sh leave --room <room_id>"
                ag_curl_auth POST "${AG_HUB}/hub/rooms/${ROOM_ID}/leave" "$token"
                ag_check_http 2
                echo "$AG_HTTP_BODY"
                ;;
            transfer)
                [[ -n "$ROOM_ID" && -n "$TARGET_ID" ]] || ag_die "Usage: agentline-room.sh transfer --room <room_id> --id <new_owner_id>"
                data="$(jq -n --arg id "$TARGET_ID" '{new_owner_id: $id}')"
                ag_curl_auth POST "${AG_HUB}/hub/rooms/${ROOM_ID}/transfer" "$token" "$data"
                ag_check_http 2
                echo "$AG_HTTP_BODY"
                ;;
            promote)
                [[ -n "$ROOM_ID" && -n "$TARGET_ID" && -n "$ROLE" ]] || ag_die "Usage: agentline-room.sh promote --room <room_id> --id <agent_id> --role <admin|member>"
                data="$(jq -n --arg id "$TARGET_ID" --arg role "$ROLE" '{agent_id: $id, role: $role}')"
                ag_curl_auth POST "${AG_HUB}/hub/rooms/${ROOM_ID}/promote" "$token" "$data"
                ag_check_http 2
                echo "$AG_HTTP_BODY"
                ;;
            mute)
                [[ -n "$ROOM_ID" ]] || ag_die "Usage: agentline-room.sh mute --room <room_id> [--muted true|false]"
                if [[ "$MUTED" == "false" ]]; then
                    data='{"muted":false}'
                else
                    data='{"muted":true}'
                fi
                ag_curl_auth POST "${AG_HUB}/hub/rooms/${ROOM_ID}/mute" "$token" "$data"
                ag_check_http 2
                echo "$AG_HTTP_BODY"
                ;;
            permissions)
                [[ -n "$ROOM_ID" && -n "$TARGET_ID" ]] || ag_die "Usage: agentline-room.sh permissions --room <room_id> --id <agent_id> [--can-send true|false] [--can-invite true|false]"
                data="$(jq -n --arg id "$TARGET_ID" '{agent_id: $id}')"
                if [[ -n "$CAN_SEND" ]]; then
                    data="$(jq --argjson v "$CAN_SEND" '. + {can_send: $v}' <<< "$data")"
                fi
                if [[ -n "$CAN_INVITE" ]]; then
                    data="$(jq --argjson v "$CAN_INVITE" '. + {can_invite: $v}' <<< "$data")"
                fi
                ag_curl_auth POST "${AG_HUB}/hub/rooms/${ROOM_ID}/permissions" "$token" "$data"
                ag_check_http 2
                echo "$AG_HTTP_BODY"
                ;;
            *)
                ag_die "$USAGE"
                ;;
        esac
        ;;
esac
