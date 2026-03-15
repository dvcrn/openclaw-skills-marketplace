#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
FABRIC_SCRIPT="${CADUCEUSMAIL_FABRIC_SCRIPT:-${SCRIPT_DIR}/email_alias_fabric_ops.py}"
DEFAULT_CREDENTIALS_DIR="$(cd -- "${SCRIPT_DIR}/.." && pwd)/credentials"
CREDENTIALS_DIR="${CADUCEUSMAIL_CREDENTIALS_DIR:-${DEFAULT_CREDENTIALS_DIR}}"
REPO_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
VERSION="$(cat "${REPO_ROOT}/VERSION" 2>/dev/null || echo 5.3.3)"
DEFAULT_ENV_FILE="${HOME}/.caduceusmail/.env"
ENV_FILE="${CADUCEUSMAIL_ENV_FILE:-${DEFAULT_ENV_FILE}}"

DEFAULT_INTEL_DIR="${HOME}/.caduceusmail/intel"
INTEL_DIR="${CADUCEUSMAIL_INTEL_DIR:-${DEFAULT_INTEL_DIR}}"
PS_BOOTSTRAP="${CADUCEUSMAIL_BOOTSTRAP_SCRIPT:-}"
TEMP_BOOTSTRAP=""

cleanup() {
  if [[ -n "${TEMP_BOOTSTRAP}" && -f "${TEMP_BOOTSTRAP}" ]]; then
    rm -f "${TEMP_BOOTSTRAP}"
  fi
}
trap cleanup EXIT

usage() {
  cat <<'EOF'
☤ caduceusmail: one-line Microsoft365 + Cloudflare stack bootstrap.

Usage:
  bash ./scripts/caduceusmail.sh \
    --organization-domain <root-domain> \
    --mailbox <primary-mailbox>

Required values can be supplied either by CLI flags or strict credentials files:
  credentials/entra.txt
  credentials/cloudflare.txt

Optional:
  --credentials-dir <dir>                       (default: ../credentials; loads entra.txt/cloudflare.txt)
  --tenant-id <entra-tenant-id>
  --client-id <entra-app-client-id>
  --exchange-org <exchange-org-domain>          (default: organization-domain)
  --cloudflare-token <token>                    (or CLOUDFLARE_API_TOKEN/CF_API_TOKEN)
  --cloudflare-zone-id <zone-id>                (or CLOUDFLARE_ZONE_ID/CF_ZONE_ID)
  --rotate-client-secret                        (create new app secret)
  --secret-lifetime-days <days>                 (default: 365)
  --bootstrap-auth-mode <auto|browser|device>   (default: auto; device recommended in sandboxes/VPS)
  --bootstrap-admin-upn <admin@domain>          (optional hint for browser-based Exchange login)
  --set-accepted-domain-internal-relay          (Exchange accepted domain tuning)
  --enable-accepted-domain-match-subdomains     (Exchange accepted domain tuning)
  --dry-run                                     (audit only; no DNS/domain mutation)
  --force                                       (allow root-DNS overwrite paths where safe)
  --skip-m365-bootstrap                         (skip PowerShell auth/permission bootstrap)
  --skip-stack-optimize                         (skip email fabric optimize pass)
  --simulate-bootstrap                          (skip pwsh and emit a deterministic bootstrap result)
  --gateway-login-handoff                       (attempt OpenClaw browser handoff for Microsoft device login)
  --no-gateway-login-handoff                    (disable OpenClaw browser handoff)
  --persist-env                                 (persist non-secret runtime keys to env file)
  --persist-secrets                             (persist secrets/tokens to env file; implies --persist-env)
  --version                                     (print version)
EOF
}

simulate_bootstrap_json() {
  local mode="$1"
  local sign_in_events="1"
  local sso_mode="interactive_browser_simulated"
  if [[ "${mode}" == "device" || "${mode}" == "auto" ]]; then
    sign_in_events="2"
    sso_mode="device_code_simulated"
  fi
  jq -cn --arg version "${VERSION}" --arg mode "${mode}" --arg sso_mode "${sso_mode}" --argjson sign_in_events "${sign_in_events}" '{ok:true,toolVersion:$version,simulated:true,bootstrapAuthMode:$mode,steps:["simulation_mode","graph_connected_simulated","exchange_connected_simulated","exchange_rbac_ready_simulated"],sign_in_events:$sign_in_events,sso_mode:$sso_mode}'
}

require_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Missing required command: $1" >&2
    exit 1
  fi
}

extract_bootstrap_json() {
  local raw_file="$1"
  python3 - "${raw_file}" <<'PY'
import json
import sys

path = sys.argv[1]
text = open(path, encoding="utf-8", errors="replace").read()
decoder = json.JSONDecoder()
idx = 0
best = None

while idx < len(text):
    ch = text[idx]
    if ch != "{":
        idx += 1
        continue
    try:
        obj, end = decoder.raw_decode(text, idx)
    except Exception:
        idx += 1
        continue
    if isinstance(obj, dict) and ("ok" in obj or "steps" in obj):
        best = obj
    idx = end

if best is None:
    sys.exit(1)

print(json.dumps(best))
PY
}

maybe_gateway_login_handoff() {
  local auth_mode="$1"
  if [[ "${GATEWAY_LOGIN_HANDOFF}" == "0" ]]; then
    return 0
  fi
  if [[ "${auth_mode}" == "browser" ]]; then
    return 0
  fi
  if ! command -v openclaw >/dev/null 2>&1; then
    return 0
  fi

  local url="https://microsoft.com/devicelogin"
  local gateway_url="${CADUCEUSMAIL_GATEWAY_URL:-${OPENCLAW_GATEWAY_URL:-}}"
  local gateway_token="${CADUCEUSMAIL_GATEWAY_TOKEN:-${OPENCLAW_GATEWAY_TOKEN:-}}"
  local browser_profile="${CADUCEUSMAIL_GATEWAY_BROWSER_PROFILE:-}"
  local oc_args=()
  if [[ -n "${gateway_url}" ]]; then oc_args+=(--url "${gateway_url}"); fi
  if [[ -n "${gateway_token}" ]]; then oc_args+=(--token "${gateway_token}"); fi
  if [[ -n "${browser_profile}" ]]; then oc_args+=(--browser-profile "${browser_profile}"); fi

  mkdir -p "${INTEL_DIR}"
  echo "[☤ caduceusmail] login handoff: ${url}"
  if openclaw browser start "${oc_args[@]}" >/dev/null 2>&1 && openclaw browser open "${url}" "${oc_args[@]}" >/dev/null 2>&1; then
    echo "[☤ caduceusmail] login handoff opened in OpenClaw browser"
    jq -cn --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" --arg status "opened_in_openclaw_browser" --arg url "${url}" \
      '{ts:$ts,status:$status,url:$url}' > "${INTEL_DIR}/caduceusmail-login-handoff.json"
  else
    echo "[☤ caduceusmail] login handoff unavailable (gateway/browser not ready); continue with device code in terminal"
    local dash_line=""
    if dash_line="$(openclaw dashboard --no-open 2>/dev/null | rg -m1 '^Dashboard URL:' || true)" && [[ -n "${dash_line}" ]]; then
      local dash_url="${dash_line#Dashboard URL: }"
      echo "[☤ caduceusmail] dashboard handoff URL: ${dash_url}"
      jq -cn --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" --arg status "dashboard_url_emitted" --arg url "${url}" --arg dashboard_url "${dash_url}" \
        '{ts:$ts,status:$status,url:$url,dashboard_url:$dashboard_url}' > "${INTEL_DIR}/caduceusmail-login-handoff.json"
    else
      jq -cn --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" --arg status "handoff_unavailable" --arg url "${url}" \
        '{ts:$ts,status:$status,url:$url}' > "${INTEL_DIR}/caduceusmail-login-handoff.json"
    fi
  fi
}

resolve_bootstrap_script() {
  if [[ -n "${PS_BOOTSTRAP}" && -f "${PS_BOOTSTRAP}" ]]; then
    return 0
  fi

  local candidates=(
    "${SCRIPT_DIR}/caduceusmail-bootstrap.ps1"
    "${SCRIPT_DIR}/caduceusmail_bootstrap.ps1"
  )
  local c=""
  for c in "${candidates[@]}"; do
    if [[ -f "${c}" ]]; then
      PS_BOOTSTRAP="${c}"
      return 0
    fi
  done

  local text_candidates=(
    "${SCRIPT_DIR}/caduceusmail-bootstrap.ps1.txt"
    "${SCRIPT_DIR}/caduceusmail_bootstrap.ps1.txt"
  )
  for c in "${text_candidates[@]}"; do
    if [[ -f "${c}" ]]; then
      TEMP_BOOTSTRAP="$(mktemp /tmp/caduceusmail-bootstrap.XXXXXX.ps1)"
      cp "${c}" "${TEMP_BOOTSTRAP}"
      chmod 600 "${TEMP_BOOTSTRAP}"
      PS_BOOTSTRAP="${TEMP_BOOTSTRAP}"
      return 0
    fi
  done

  echo "Missing bootstrap script near ${SCRIPT_DIR} (expected .ps1 or .ps1.txt)." >&2
  exit 1
}

parse_strict_credentials_file() {
  local file="$1"
  local source_name="$2"
  local line=""
  local line_no=0
  local header_seen="0"

  while IFS= read -r line || [[ -n "${line}" ]]; do
    line_no=$((line_no + 1))
    line="${line%$'\r'}"
    local trimmed
    trimmed="$(printf '%s' "${line}" | sed 's/^[[:space:]]*//; s/[[:space:]]*$//')"

    if [[ -z "${trimmed}" ]]; then
      continue
    fi

    if [[ "${header_seen}" != "1" ]]; then
      if [[ "${trimmed}" != "CADUCEUSMAIL_CREDENTIALS_V1" ]]; then
        echo "Invalid ${source_name}:${line_no} (first non-empty line must be CADUCEUSMAIL_CREDENTIALS_V1)" >&2
        exit 1
      fi
      header_seen="1"
      continue
    fi

    if [[ "${trimmed}" =~ ^# ]]; then
      continue
    fi
    if [[ ! "${trimmed}" =~ ^[A-Z0-9_]+=.+$ ]]; then
      echo "Invalid ${source_name}:${line_no} (expected KEY=VALUE)" >&2
      exit 1
    fi

    local key="${trimmed%%=*}"
    local value="${trimmed#*=}"
    case "${key}" in
      ENTRA_TENANT_ID|ENTRA_CLIENT_ID|ENTRA_CLIENT_SECRET|EXCHANGE_ORGANIZATION|EXCHANGE_DEFAULT_MAILBOX|ORGANIZATION_DOMAIN|CLOUDFLARE_API_TOKEN|CLOUDFLARE_ZONE_ID|CF_API_TOKEN|CF_ZONE_ID)
        export "${key}=${value}"
        ;;
      *)
        echo "Invalid ${source_name}:${line_no} (unsupported key: ${key})" >&2
        exit 1
        ;;
    esac
  done < "${file}"

  if [[ "${header_seen}" != "1" ]]; then
    echo "Invalid ${source_name} (missing CADUCEUSMAIL_CREDENTIALS_V1 header)" >&2
    exit 1
  fi
}

autoload_credentials() {
  local loaded="0"
  if [[ -f "${CREDENTIALS_DIR}/entra.txt" ]]; then
    parse_strict_credentials_file "${CREDENTIALS_DIR}/entra.txt" "${CREDENTIALS_DIR}/entra.txt"
    loaded="1"
  fi
  if [[ -f "${CREDENTIALS_DIR}/cloudflare.txt" ]]; then
    parse_strict_credentials_file "${CREDENTIALS_DIR}/cloudflare.txt" "${CREDENTIALS_DIR}/cloudflare.txt"
    loaded="1"
  fi
  if [[ "${loaded}" == "1" ]]; then
    echo "[☤ caduceusmail] loaded credentials from ${CREDENTIALS_DIR}"
  fi
}

upsert_env_key() {
  local key="$1"
  local value="$2"
  mkdir -p "$(dirname "${ENV_FILE}")"
  touch "${ENV_FILE}"
  if grep -q "^${key}=" "${ENV_FILE}"; then
    sed -i "s|^${key}=.*|${key}=${value}|" "${ENV_FILE}"
  else
    printf '%s=%s\n' "${key}" "${value}" >> "${ENV_FILE}"
  fi
}

TENANT_ID=""
CLIENT_ID=""
ORG_DOMAIN=""
EXCHANGE_ORG=""
MAILBOX=""
CF_TOKEN=""
CF_ZONE_ID=""
ROTATE_SECRET="0"
SECRET_LIFETIME_DAYS="365"
BOOTSTRAP_AUTH_MODE="auto"
BOOTSTRAP_ADMIN_UPN=""
SET_INTERNAL_RELAY="0"
ENABLE_MATCH_SUBDOMAINS="0"
DRY_RUN="0"
FORCE="0"
SKIP_M365="0"
SKIP_OPTIMIZE="0"
SIMULATE_BOOTSTRAP="0"
PERSIST_ENV="0"
PERSIST_SECRETS="0"
GATEWAY_LOGIN_HANDOFF="${CADUCEUSMAIL_GATEWAY_LOGIN_HANDOFF:-auto}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --credentials-dir) CREDENTIALS_DIR="${2:-}"; shift 2 ;;
    --tenant-id) TENANT_ID="${2:-}"; shift 2 ;;
    --client-id) CLIENT_ID="${2:-}"; shift 2 ;;
    --organization-domain) ORG_DOMAIN="${2:-}"; shift 2 ;;
    --exchange-org) EXCHANGE_ORG="${2:-}"; shift 2 ;;
    --mailbox) MAILBOX="${2:-}"; shift 2 ;;
    --cloudflare-token) CF_TOKEN="${2:-}"; shift 2 ;;
    --cloudflare-zone-id) CF_ZONE_ID="${2:-}"; shift 2 ;;
    --rotate-client-secret) ROTATE_SECRET="1"; shift ;;
    --secret-lifetime-days) SECRET_LIFETIME_DAYS="${2:-}"; shift 2 ;;
    --bootstrap-auth-mode) BOOTSTRAP_AUTH_MODE="${2:-}"; shift 2 ;;
    --bootstrap-admin-upn) BOOTSTRAP_ADMIN_UPN="${2:-}"; shift 2 ;;
    --set-accepted-domain-internal-relay) SET_INTERNAL_RELAY="1"; shift ;;
    --enable-accepted-domain-match-subdomains) ENABLE_MATCH_SUBDOMAINS="1"; shift ;;
    --dry-run) DRY_RUN="1"; shift ;;
    --force) FORCE="1"; shift ;;
    --skip-m365-bootstrap) SKIP_M365="1"; shift ;;
    --skip-stack-optimize) SKIP_OPTIMIZE="1"; shift ;;
    --simulate-bootstrap) SIMULATE_BOOTSTRAP="1"; shift ;;
    --gateway-login-handoff) GATEWAY_LOGIN_HANDOFF="1"; shift ;;
    --no-gateway-login-handoff) GATEWAY_LOGIN_HANDOFF="0"; shift ;;
    --persist-env) PERSIST_ENV="1"; shift ;;
    --persist-secrets) PERSIST_SECRETS="1"; shift ;;
    --version) printf "%s\n" "${VERSION}"; exit 0 ;;
    -h|--help) usage; exit 0 ;;
    *)
      echo "Unknown arg: $1" >&2
      usage
      exit 1
      ;;
  esac
done

autoload_credentials

if [[ -z "${TENANT_ID}" ]]; then TENANT_ID="${ENTRA_TENANT_ID:-}"; fi
if [[ -z "${CLIENT_ID}" ]]; then CLIENT_ID="${ENTRA_CLIENT_ID:-}"; fi
if [[ -z "${MAILBOX}" ]]; then MAILBOX="${EXCHANGE_DEFAULT_MAILBOX:-}"; fi
if [[ -z "${ORG_DOMAIN}" ]]; then ORG_DOMAIN="${ORGANIZATION_DOMAIN:-${EMAIL_ALIAS_FABRIC_BASE_DOMAIN:-}}"; fi
if [[ -z "${ORG_DOMAIN}" && "${MAILBOX}" == *"@"* ]]; then ORG_DOMAIN="${MAILBOX#*@}"; fi
if [[ -z "${EXCHANGE_ORG}" ]]; then EXCHANGE_ORG="${EXCHANGE_ORGANIZATION:-}"; fi
if [[ -z "${CF_TOKEN}" ]]; then CF_TOKEN="${CLOUDFLARE_API_TOKEN:-${CF_API_TOKEN:-}}"; fi
if [[ -z "${CF_ZONE_ID}" ]]; then CF_ZONE_ID="${CLOUDFLARE_ZONE_ID:-${CF_ZONE_ID:-}}"; fi

if [[ -z "${TENANT_ID}" || -z "${CLIENT_ID}" || -z "${ORG_DOMAIN}" || -z "${MAILBOX}" ]]; then
  echo "Missing required args." >&2
  echo "Provide CLI flags or strict credentials files in ${CREDENTIALS_DIR}." >&2
  usage
  exit 1
fi

if [[ "${PERSIST_SECRETS}" == "1" && "${PERSIST_ENV}" != "1" ]]; then
  PERSIST_ENV="1"
  echo "[☤ caduceusmail] --persist-secrets enabled; auto-enabling --persist-env"
fi

require_cmd python3
require_cmd jq
if [[ "${SKIP_M365}" != "1" && "${SIMULATE_BOOTSTRAP}" != "1" ]]; then
  require_cmd pwsh
fi

resolve_bootstrap_script
if [[ ! -f "${FABRIC_SCRIPT}" ]]; then
  echo "Missing fabric script: ${FABRIC_SCRIPT}" >&2
  exit 1
fi

if [[ -z "${EXCHANGE_ORG}" ]]; then
  EXCHANGE_ORG="${ORG_DOMAIN}"
fi
if [[ "${PERSIST_ENV}" == "1" ]]; then
  echo "[☤ caduceusmail] persisting non-secret env keys to ${ENV_FILE}"
  upsert_env_key "ENTRA_TENANT_ID" "${TENANT_ID}"
  upsert_env_key "ENTRA_CLIENT_ID" "${CLIENT_ID}"
  upsert_env_key "EXCHANGE_DEFAULT_MAILBOX" "${MAILBOX}"
  upsert_env_key "EXCHANGE_ORGANIZATION" "${EXCHANGE_ORG}"
fi
if [[ "${PERSIST_SECRETS}" == "1" ]]; then
  echo "[☤ caduceusmail] persisting secret env keys to ${ENV_FILE}"
  if [[ -n "${CF_TOKEN}" ]]; then upsert_env_key "CLOUDFLARE_API_TOKEN" "${CF_TOKEN}"; fi
  if [[ -n "${CF_ZONE_ID}" ]]; then upsert_env_key "CLOUDFLARE_ZONE_ID" "${CF_ZONE_ID}"; fi
fi

bootstrap_out='{"ok":true,"skipped":true}'
if [[ "${SKIP_M365}" != "1" ]]; then
  echo "[☤ caduceusmail] running Microsoft365 permission bootstrap (${BOOTSTRAP_AUTH_MODE} auth mode)"
  if [[ "${SIMULATE_BOOTSTRAP}" == "1" ]]; then
    bootstrap_out="$(simulate_bootstrap_json "${BOOTSTRAP_AUTH_MODE}")"
  else
    maybe_gateway_login_handoff "${BOOTSTRAP_AUTH_MODE}"
    ps_args=(
      -NoLogo -NoProfile
      -File "${PS_BOOTSTRAP}"
      -TenantId "${TENANT_ID}"
      -ClientId "${CLIENT_ID}"
      -OrganizationDomain "${ORG_DOMAIN}"
      -ExchangeOrg "${EXCHANGE_ORG}"
      -SecretLifetimeDays "${SECRET_LIFETIME_DAYS}"
      -BootstrapAuthMode "${BOOTSTRAP_AUTH_MODE}"
    )
    if [[ "${PERSIST_ENV}" == "1" ]]; then
      ps_args+=(-WriteEnv -EnvPath "${ENV_FILE}")
    fi
    if [[ "${PERSIST_SECRETS}" == "1" ]]; then
      ps_args+=(-WriteSecrets)
    fi
    if [[ -n "${BOOTSTRAP_ADMIN_UPN}" ]]; then ps_args+=(-BootstrapAdminUpn "${BOOTSTRAP_ADMIN_UPN}"); fi
    if [[ "${ROTATE_SECRET}" == "1" ]]; then ps_args+=(-RotateClientSecret); fi
    if [[ "${SET_INTERNAL_RELAY}" == "1" ]]; then ps_args+=(-SetAcceptedDomainInternalRelay); fi
    if [[ "${ENABLE_MATCH_SUBDOMAINS}" == "1" ]]; then ps_args+=(-EnableAcceptedDomainMatchSubdomains); fi
    bootstrap_raw_file="$(mktemp /tmp/caduceusmail-bootstrap-out.XXXXXX.log)"
    if ! pwsh "${ps_args[@]}" >"${bootstrap_raw_file}" 2>&1; then
      cat "${bootstrap_raw_file}" >&2
      rm -f "${bootstrap_raw_file}"
      exit 1
    fi
    if ! bootstrap_out="$(extract_bootstrap_json "${bootstrap_raw_file}")"; then
      echo "[☤ caduceusmail] bootstrap completed but JSON parse failed; raw output follows:" >&2
      cat "${bootstrap_raw_file}" >&2
      rm -f "${bootstrap_raw_file}"
      exit 1
    fi
    rm -f "${bootstrap_raw_file}"
  fi
  printf '%s\n' "${bootstrap_out}" | jq '{ok,simulated:(.simulated // false),steps,error,sign_in_events:(.sign_in_events // "unknown"),sso_mode:(.sso_mode // "default")}'
fi

stack_out='{"ok":true,"status":"skipped","results":[]}'
if [[ "${SKIP_OPTIMIZE}" != "1" ]]; then
  echo "[☤ caduceusmail] running stack audit + optimization"
  export ENTRA_TENANT_ID="${TENANT_ID}"
  export ENTRA_CLIENT_ID="${CLIENT_ID}"
  export EXCHANGE_DEFAULT_MAILBOX="${MAILBOX}"
  export EXCHANGE_ORGANIZATION="${EXCHANGE_ORG}"
  if [[ -n "${CF_TOKEN}" ]]; then export CLOUDFLARE_API_TOKEN="${CF_TOKEN}"; fi
  if [[ -n "${CF_ZONE_ID}" ]]; then export CLOUDFLARE_ZONE_ID="${CF_ZONE_ID}"; fi

  optimize_json="$(jq -cn \
    --arg mailbox "${MAILBOX}" \
    --arg domain "${ORG_DOMAIN}" \
    --argjson force "$([[ "${FORCE}" == "1" ]] && echo true || echo false)" \
    '[{"action":"stack.audit","mailbox":$mailbox,"domain":$domain},{"action":"stack.optimize","mailbox":$mailbox,"domain":$domain,"force":$force}]'
  )"
  if [[ "${DRY_RUN}" == "1" ]]; then
    stack_out="$(python3 "${FABRIC_SCRIPT}" control-json --dry-run --ops-json "${optimize_json}")"
  else
    stack_out="$(python3 "${FABRIC_SCRIPT}" control-json --ops-json "${optimize_json}")"
  fi
fi

mkdir -p "${INTEL_DIR}"
printf '%s\n' "${bootstrap_out}" > "${INTEL_DIR}/caduceusmail-bootstrap-last.json"
printf '%s\n' "${stack_out}" > "${INTEL_DIR}/caduceusmail-stack-last.json"

printf '%s\n' "${stack_out}" | jq '{ok,status,results:[.results[]|{action,ok,domain,mailbox,graph_ready:(.credentials.graph_permissions.ready // .credential_plane.graph_permissions.ready),missing_graph:(.credentials.graph_permissions.graph_roles_missing // .credential_plane.graph_permissions.graph_roles_missing),missing_exchange_rbac:(.credentials.exchange_authorization.missing_roles // .credential_plane.exchange_authorization.missing_roles),dmarc:(.mail_plane.dmarc_summary.has_dmarc // .dns_plane.after_dmarc.has_dmarc // false)}]}' || true
echo "[☤ caduceusmail] complete"
