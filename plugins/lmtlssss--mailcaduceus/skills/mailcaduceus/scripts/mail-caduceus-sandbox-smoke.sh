#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
RUNNER="${SCRIPT_DIR}/mail-caduceus.sh"
TMP="$(mktemp -d)"
trap 'rm -rf "${TMP}"' EXIT

MOCK_BOOT="${TMP}/mock_bootstrap.ps1"
MOCK_FABRIC="${TMP}/mock_fabric.py"
SANDBOX_ENV="${TMP}/sandbox.env"
SANDBOX_INTEL="${TMP}/intel"

cat > "${MOCK_BOOT}" <<'PS1'
#!/usr/bin/env pwsh
$summary = @{
  ok = $true
  steps = @("simulation_mode","graph_connected_simulated","exchange_connected_simulated","exchange_rbac_ready_simulated")
  sign_in_events = 1
  sso_mode = "single_sign_on_simulated"
}
$summary | ConvertTo-Json -Depth 6
PS1

cat > "${MOCK_FABRIC}" <<'PY'
#!/usr/bin/env python3
import json
import sys

if len(sys.argv) >= 2 and sys.argv[1] == "control-json":
    out = {
        "ok": True,
        "status": "dry_run",
        "results": [
            {"action": "stack.audit", "ok": True, "domain": "northorizon.ca", "mailbox": "john@northorizon.ca", "credentials": {"graph_permissions": {"ready": True, "graph_roles_missing": []}, "exchange_authorization": {"missing_roles": []}}, "mail_plane": {"dmarc_summary": {"has_dmarc": True}}},
            {"action": "stack.optimize", "ok": True, "domain": "northorizon.ca", "mailbox": "john@northorizon.ca", "credential_plane": {"graph_permissions": {"ready": True, "graph_roles_missing": []}, "exchange_authorization": {"missing_roles": []}}, "dns_plane": {"after_dmarc": {"has_dmarc": True}}},
        ],
    }
    print(json.dumps(out))
    raise SystemExit(0)
print(json.dumps({"ok": False, "error": "unexpected invocation", "argv": sys.argv}))
raise SystemExit(1)
PY

chmod +x "${MOCK_BOOT}" "${MOCK_FABRIC}" "${RUNNER}"

MAIL_CADUCEUS_BOOTSTRAP_SCRIPT="${MOCK_BOOT}" \
MAIL_CADUCEUS_FABRIC_SCRIPT="${MOCK_FABRIC}" \
MAIL_CADUCEUS_ENV_FILE="${SANDBOX_ENV}" \
MAIL_CADUCEUS_INTEL_DIR="${SANDBOX_INTEL}" \
bash "${RUNNER}" \
  --tenant-id "00000000-0000-0000-0000-000000000000" \
  --client-id "11111111-1111-1111-1111-111111111111" \
  --organization-domain "northorizon.ca" \
  --mailbox "john@northorizon.ca" \
  --dry-run > "${TMP}/run.log"

BOOT_JSON="${SANDBOX_INTEL}/mail-caduceus-bootstrap-last.json"
STACK_JSON="${SANDBOX_INTEL}/mail-caduceus-stack-last.json"

if [[ ! -f "${BOOT_JSON}" || ! -f "${STACK_JSON}" ]]; then
  echo "sandbox smoke failed: missing output artifacts" >&2
  exit 1
fi

SIGN_IN_EVENTS="$(jq -r '.sign_in_events // 0' "${BOOT_JSON}")"
BOOT_OK="$(jq -r '.ok' "${BOOT_JSON}")"
STACK_OK="$(jq -r '.ok' "${STACK_JSON}")"

if [[ "${SIGN_IN_EVENTS}" != "1" ]]; then
  echo "sandbox smoke failed: expected sign_in_events=1, got ${SIGN_IN_EVENTS}" >&2
  exit 1
fi
if [[ "${BOOT_OK}" != "true" || "${STACK_OK}" != "true" ]]; then
  echo "sandbox smoke failed: bootstrap or stack result not ok" >&2
  exit 1
fi

echo "mail_caduceus sandbox smoke: PASS"
echo "artifacts:"
echo "  ${BOOT_JSON}"
echo "  ${STACK_JSON}"
echo "summary:"
jq '{bootstrap_ok:.ok,sign_in_events:.sign_in_events,sso_mode:.sso_mode,steps:.steps}' "${BOOT_JSON}"
jq '{stack_ok:.ok,status:.status,actions:[.results[].action]}' "${STACK_JSON}"
