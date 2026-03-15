#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
RUNNER="${SCRIPT_DIR}/caduceusmail.sh"
TMP="$(mktemp -d)"
trap 'rm -rf "${TMP}"' EXIT

MOCK_FABRIC="${TMP}/mock_fabric.py"
SANDBOX_ENV="${TMP}/sandbox.env"
SANDBOX_INTEL="${TMP}/intel"

cat > "${MOCK_FABRIC}" <<'PY'
#!/usr/bin/env python3
import json
import sys

if len(sys.argv) >= 2 and sys.argv[1] == "control-json":
    out = {
        "ok": True,
        "status": "dry_run",
        "results": [
            {"action": "stack.audit", "ok": True, "domain": "example.com", "mailbox": "ops@example.com", "credentials": {"graph_permissions": {"ready": True, "graph_roles_missing": []}, "exchange_authorization": {"missing_roles": []}}, "mail_plane": {"dmarc_summary": {"has_dmarc": True}}},
            {"action": "stack.optimize", "ok": True, "domain": "example.com", "mailbox": "ops@example.com", "credential_plane": {"graph_permissions": {"ready": True, "graph_roles_missing": []}, "exchange_authorization": {"missing_roles": []}}, "dns_plane": {"after_dmarc": {"has_dmarc": True}}},
        ],
    }
    print(json.dumps(out))
    raise SystemExit(0)
print(json.dumps({"ok": False, "error": "unexpected invocation", "argv": sys.argv}))
raise SystemExit(1)
PY

chmod +x "${MOCK_FABRIC}" "${RUNNER}"

CADUCEUSMAIL_FABRIC_SCRIPT="${MOCK_FABRIC}" \
CADUCEUSMAIL_ENV_FILE="${SANDBOX_ENV}" \
CADUCEUSMAIL_INTEL_DIR="${SANDBOX_INTEL}" \
bash "${RUNNER}" \
  --tenant-id "00000000-0000-0000-0000-000000000000" \
  --client-id "11111111-1111-1111-1111-111111111111" \
  --organization-domain "example.com" \
  --mailbox "ops@example.com" \
  --bootstrap-auth-mode device \
  --simulate-bootstrap \
  --dry-run > "${TMP}/run.log"

BOOT_JSON="${SANDBOX_INTEL}/caduceusmail-bootstrap-last.json"
STACK_JSON="${SANDBOX_INTEL}/caduceusmail-stack-last.json"

if [[ ! -f "${BOOT_JSON}" || ! -f "${STACK_JSON}" ]]; then
  echo "☤ sandbox smoke failed: missing output artifacts" >&2
  exit 1
fi

SIGN_IN_EVENTS="$(jq -r '.sign_in_events // 0' "${BOOT_JSON}")"
BOOT_OK="$(jq -r '.ok' "${BOOT_JSON}")"
STACK_OK="$(jq -r '.ok' "${STACK_JSON}")"
SIMULATED="$(jq -r '.simulated // false' "${BOOT_JSON}")"

if [[ "${SIGN_IN_EVENTS}" != "2" ]]; then
  echo "☤ sandbox smoke failed: expected sign_in_events=2, got ${SIGN_IN_EVENTS}" >&2
  exit 1
fi
if [[ "${BOOT_OK}" != "true" || "${STACK_OK}" != "true" ]]; then
  echo "☤ sandbox smoke failed: bootstrap or stack result not ok" >&2
  exit 1
fi
if [[ "${SIMULATED}" != "true" ]]; then
  echo "☤ sandbox smoke failed: expected simulated bootstrap" >&2
  exit 1
fi

echo "☤ caduceusmail sandbox smoke: PASS"
jq '{bootstrap_ok:.ok,sign_in_events:.sign_in_events,sso_mode:.sso_mode,simulated:.simulated,steps:.steps}' "${BOOT_JSON}"
jq '{stack_ok:.ok,status:.status,actions:[.results[].action]}' "${STACK_JSON}"
