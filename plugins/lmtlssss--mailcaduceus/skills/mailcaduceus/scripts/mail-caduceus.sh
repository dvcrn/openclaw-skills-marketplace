#!/usr/bin/env bash
set -euo pipefail
umask 077

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
FABRIC_SCRIPT="${MAIL_CADUCEUS_FABRIC_SCRIPT:-${SCRIPT_DIR}/email_alias_fabric_ops.py}"
DEFAULT_CREDENTIALS_DIR="$(cd -- "${SCRIPT_DIR}/.." && pwd)/credentials"
CREDENTIALS_DIR="${MAIL_CADUCEUS_CREDENTIALS_DIR:-${DEFAULT_CREDENTIALS_DIR}}"
DEFAULT_ENV_FILE="${HOME}/.openclaw/.env"
ENV_FILE="${MAIL_CADUCEUS_ENV_FILE:-${DEFAULT_ENV_FILE}}"
DEFAULT_INTEL_DIR="${HOME}/.mail-caduceus/intel"
INTEL_DIR="${MAIL_CADUCEUS_INTEL_DIR:-${DEFAULT_INTEL_DIR}}"
PERSIST_ENV="${MAIL_CADUCEUS_PERSIST_ENV:-0}"
PERSIST_SECRETS="${MAIL_CADUCEUS_PERSIST_SECRETS:-0}"
PS_BOOTSTRAP="${MAIL_CADUCEUS_BOOTSTRAP_SCRIPT:-}"
TEMP_BOOTSTRAP=""

cleanup() {
  if [[ -n "${TEMP_BOOTSTRAP}" && -f "${TEMP_BOOTSTRAP}" ]]; then
    rm -f "${TEMP_BOOTSTRAP}"
  fi
}
trap cleanup EXIT

usage() {
  cat <<'EOF'
mail_caduceus: one-line Microsoft365 + Cloudflare stack bootstrap.

Usage:
  bash ./scripts/mail-caduceus.sh \
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
  --rotate-client-secret                        (create new app secret and write to env)
  --secret-lifetime-days <days>                 (default: 365)
  --set-accepted-domain-internal-relay          (Exchange accepted domain tuning)
  --enable-accepted-domain-match-subdomains     (Exchange accepted domain tuning)
  --dry-run                                     (audit only; no DNS/domain mutation)
  --force                                       (allow root-DNS overwrite paths where safe)
  --skip-m365-bootstrap                         (skip PowerShell auth/permission bootstrap)
  --skip-stack-optimize                         (skip email fabric optimize pass)
  --persist-env                                 (persist non-secret runtime keys to ENV_FILE)
  --persist-secrets                             (persist secrets to ENV_FILE; only valid with --persist-env)
  --no-persist-env                              (explicitly disable ENV_FILE writes; default)
EOF
}

require_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Missing required command: $1" >&2
    exit 1
  fi
}

resolve_bootstrap_script() {
  if [[ -n "${PS_BOOTSTRAP}" && -f "${PS_BOOTSTRAP}" ]]; then
    return 0
  fi

  local candidates=(
    "${SCRIPT_DIR}/mail-caduceus-bootstrap.ps1"
    "${SCRIPT_DIR}/mail_caduceus_bootstrap.ps1"
  )
  local c=""
  for c in "${candidates[@]}"; do
    if [[ -f "${c}" ]]; then
      PS_BOOTSTRAP="${c}"
      return 0
    fi
  done

  local text_candidates=(
    "${SCRIPT_DIR}/mail-caduceus-bootstrap.ps1.txt"
    "${SCRIPT_DIR}/mail_caduceus_bootstrap.ps1.txt"
  )
  for c in "${text_candidates[@]}"; do
    if [[ -f "${c}" ]]; then
      TEMP_BOOTSTRAP="$(mktemp /tmp/mail-caduceus-bootstrap.XXXXXX.ps1)"
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
      if [[ "${trimmed}" != "MAIL_CADUCEUS_CREDENTIALS_V1" ]]; then
        echo "Invalid ${source_name}:${line_no} (first non-empty line must be MAIL_CADUCEUS_CREDENTIALS_V1)" >&2
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
    echo "Invalid ${source_name} (missing MAIL_CADUCEUS_CREDENTIALS_V1 header)" >&2
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
    echo "[mail_caduceus] loaded credentials from ${CREDENTIALS_DIR}"
  fi
}

upsert_env_key() {
  local key="$1"
  local value="$2"
  mkdir -p "$(dirname "${ENV_FILE}")"
  touch "${ENV_FILE}"
  chmod 600 "${ENV_FILE}" 2>/dev/null || true
  if rg -q "^${key}=" "${ENV_FILE}"; then
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
SET_INTERNAL_RELAY="0"
ENABLE_MATCH_SUBDOMAINS="0"
DRY_RUN="0"
FORCE="0"
SKIP_M365="0"
SKIP_OPTIMIZE="0"

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
    --set-accepted-domain-internal-relay) SET_INTERNAL_RELAY="1"; shift ;;
    --enable-accepted-domain-match-subdomains) ENABLE_MATCH_SUBDOMAINS="1"; shift ;;
    --dry-run) DRY_RUN="1"; shift ;;
    --force) FORCE="1"; shift ;;
    --skip-m365-bootstrap) SKIP_M365="1"; shift ;;
    --skip-stack-optimize) SKIP_OPTIMIZE="1"; shift ;;
    --persist-env) PERSIST_ENV="1"; shift ;;
    --persist-secrets) PERSIST_SECRETS="1"; shift ;;
    --no-persist-env) PERSIST_ENV="0"; PERSIST_SECRETS="0"; shift ;;
    -h|--help) usage; exit 0 ;;
    *)
      echo "Unknown arg: $1" >&2
      usage
      exit 1
      ;;
  esac
done

autoload_credentials

if [[ "${PERSIST_ENV}" != "1" && "${PERSIST_SECRETS}" == "1" ]]; then
  echo "--persist-secrets requires --persist-env" >&2
  exit 1
fi

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

require_cmd pwsh
require_cmd python3
require_cmd jq
require_cmd rg

resolve_bootstrap_script
if [[ ! -f "${FABRIC_SCRIPT}" ]]; then
  echo "Missing fabric script: ${FABRIC_SCRIPT}" >&2
  exit 1
fi

if [[ -z "${EXCHANGE_ORG}" ]]; then
  EXCHANGE_ORG="${ORG_DOMAIN}"
fi
if [[ "${PERSIST_ENV}" == "1" ]]; then
  echo "[mail_caduceus] persisting runtime keys to ${ENV_FILE}"
  upsert_env_key "ENTRA_TENANT_ID" "${TENANT_ID}"
  upsert_env_key "ENTRA_CLIENT_ID" "${CLIENT_ID}"
  upsert_env_key "EXCHANGE_DEFAULT_MAILBOX" "${MAILBOX}"
  upsert_env_key "EXCHANGE_ORGANIZATION" "${EXCHANGE_ORG}"
  if [[ "${PERSIST_SECRETS}" == "1" ]]; then
    if [[ -n "${CF_TOKEN}" ]]; then upsert_env_key "CLOUDFLARE_API_TOKEN" "${CF_TOKEN}"; fi
    if [[ -n "${CF_ZONE_ID}" ]]; then upsert_env_key "CLOUDFLARE_ZONE_ID" "${CF_ZONE_ID}"; fi
  fi
else
  echo "[mail_caduceus] running in non-persistent mode (no .env writes)"
fi

bootstrap_out='{"ok":true,"skipped":true}'
if [[ "${SKIP_M365}" != "1" ]]; then
  echo "[mail_caduceus] running Microsoft365 permission bootstrap (interactive SSO)"
  ps_args=(
    -NoLogo -NoProfile
    -File "${PS_BOOTSTRAP}"
    -TenantId "${TENANT_ID}"
    -ClientId "${CLIENT_ID}"
    -OrganizationDomain "${ORG_DOMAIN}"
    -ExchangeOrg "${EXCHANGE_ORG}"
    -SecretLifetimeDays "${SECRET_LIFETIME_DAYS}"
  )
  if [[ "${PERSIST_ENV}" == "1" ]]; then
    ps_args+=(-WriteEnv -EnvPath "${ENV_FILE}")
  fi
  if [[ "${ROTATE_SECRET}" == "1" ]]; then ps_args+=(-RotateClientSecret); fi
  if [[ "${SET_INTERNAL_RELAY}" == "1" ]]; then ps_args+=(-SetAcceptedDomainInternalRelay); fi
  if [[ "${ENABLE_MATCH_SUBDOMAINS}" == "1" ]]; then ps_args+=(-EnableAcceptedDomainMatchSubdomains); fi
  bootstrap_out="$(pwsh "${ps_args[@]}")"
  printf '%s\n' "${bootstrap_out}" | jq '{ok,steps,error,sign_in_events:(.sign_in_events // "unknown"),sso_mode:(.sso_mode // "default")}'
fi

stack_out='{"ok":true,"status":"skipped","results":[]}'
if [[ "${SKIP_OPTIMIZE}" != "1" ]]; then
  echo "[mail_caduceus] running stack audit + optimization"
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
chmod 700 "${INTEL_DIR}" 2>/dev/null || true
bootstrap_safe="$(printf '%s\n' "${bootstrap_out}" | jq 'if type=="object" and .generatedSecret and (.generatedSecret|type)=="object" then .generatedSecret.value="[REDACTED]" else . end' 2>/dev/null || printf '%s\n' "${bootstrap_out}")"
printf '%s\n' "${bootstrap_safe}" > "${INTEL_DIR}/mail-caduceus-bootstrap-last.json"
printf '%s\n' "${stack_out}" > "${INTEL_DIR}/mail-caduceus-stack-last.json"
chmod 600 "${INTEL_DIR}/mail-caduceus-bootstrap-last.json" "${INTEL_DIR}/mail-caduceus-stack-last.json" 2>/dev/null || true

printf '%s\n' "${stack_out}" | jq '{ok,status,results:[.results[]|{action,ok,domain,mailbox,graph_ready:(.credentials.graph_permissions.ready // .credential_plane.graph_permissions.ready),missing_graph:(.credentials.graph_permissions.graph_roles_missing // .credential_plane.graph_permissions.graph_roles_missing),missing_exchange_rbac:(.credentials.exchange_authorization.missing_roles // .credential_plane.exchange_authorization.missing_roles),dmarc:(.mail_plane.dmarc_summary.has_dmarc // .dns_plane.after_dmarc.has_dmarc // false)}]}' || true
echo "[mail_caduceus] complete"
