#!/usr/bin/env python3
"""Exchange + Cloudflare email alias fabric ops (safe dry-run by default)."""

from __future__ import annotations

import argparse
import json
import os
import random
import re
import string
import subprocess
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from safe_write import read_json, write_json_atomic

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_STATE_ROOT = Path(os.environ.get("MAIL_CADUCEUS_STATE_DIR", "")).expanduser() if os.environ.get("MAIL_CADUCEUS_STATE_DIR") else (Path.home() / ".mail-caduceus")

if os.environ.get("MAIL_CADUCEUS_INTEL_DIR"):
    INTEL = Path(os.environ["MAIL_CADUCEUS_INTEL_DIR"]).expanduser()
else:
    INTEL = DEFAULT_STATE_ROOT / "intel"

LAST_RESULT = INTEL / "email-alias-fabric-last-result.json"
REGISTRY_PATH = INTEL / "email-alias-fabric-registry.json"


def resolve_entra_exchange_script() -> Path:
    override = os.environ.get("ENTRA_EXCHANGE_SCRIPT", "").strip()
    if override:
        return Path(override).expanduser()
    # Scope-locked default: only a local sibling script is auto-resolved.
    local_default = SCRIPT_DIR / "entra-exchange.sh"
    if local_default.exists():
        return local_default
    # Optional explicit opt-in for legacy shared path discovery.
    if os.environ.get("MAIL_CADUCEUS_ALLOW_EXTERNAL_SCRIPT_RESOLUTION", "").strip().lower() in {"1", "true", "yes", "on"}:
        candidates = [
            Path.home() / ".openclaw" / "workspace" / "skills" / "entra-exchange" / "scripts" / "entra-exchange.sh",
            Path("/root/.openclaw/workspace/skills/entra-exchange/scripts/entra-exchange.sh"),
        ]
        for c in candidates:
            if c.exists():
                return c
    return local_default


ENTRA_EXCHANGE_SCRIPT = resolve_entra_exchange_script()

ENV_FILES: list[Path] = []
if os.environ.get("MAIL_CADUCEUS_ENV_FILE", "").strip():
    ENV_FILES.append(Path(os.environ["MAIL_CADUCEUS_ENV_FILE"]).expanduser())
ENV_FILES.extend([
    SCRIPT_DIR.parent / ".env",
])

ALLOWED_CREDENTIAL_KEYS = {
    "ENTRA_TENANT_ID",
    "ENTRA_CLIENT_ID",
    "ENTRA_CLIENT_SECRET",
    "EXCHANGE_ORGANIZATION",
    "EXCHANGE_DEFAULT_MAILBOX",
    "ORGANIZATION_DOMAIN",
    "CLOUDFLARE_API_TOKEN",
    "CLOUDFLARE_ZONE_ID",
    "CF_API_TOKEN",
    "CF_ZONE_ID",
}
CREDENTIALS_HEADER = "MAIL_CADUCEUS_CREDENTIALS_V1"

EMAIL_RE = re.compile(r"([A-Za-z0-9._%+-]{1,64})@([A-Za-z0-9.-]+\.[A-Za-z]{2,})")
DOMAIN_RE = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?(?:\.[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?)+$")
LOCAL_RE = re.compile(r"^[A-Za-z0-9._%+-]{1,64}$")
SUBDOMAIN_RE = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?(?:\.[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?)*$")
DNS_NAME_RE = re.compile(r"^[A-Za-z0-9_.*-]+(?:\.[A-Za-z0-9_.*-]+)+$")
GRAPH_RESOURCE_APP_ID = "00000003-0000-0000-c000-000000000000"
EXCHANGE_RESOURCE_APP_ID = "00000002-0000-0ff1-ce00-000000000000"
REQUIRED_GRAPH_APP_ROLES = {
    "Mail.Send",
    "Mail.ReadWrite",
    "User.Read.All",
    "Domain.ReadWrite.All",
    "Directory.Read.All",
    "Organization.Read.All",
}
REQUIRED_EXCHANGE_APP_ROLES = {
    "Exchange.ManageAsApp",
}
REQUIRED_EXCHANGE_RBAC_ROLES = {
    "Application Mail.Send",
    "Application Mail.ReadWrite",
    "Mail Recipients",
}


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_env_file(path: Path) -> None:
    if not path.exists():
        return
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except Exception:
        return
    for raw in lines:
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[7:].strip()
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        if key and key not in os.environ:
            os.environ[key] = value


def credentials_file_candidates() -> list[Path]:
    out: list[Path] = []
    if os.environ.get("MAIL_CADUCEUS_CREDENTIALS_DIR", "").strip():
        out.append(Path(os.environ["MAIL_CADUCEUS_CREDENTIALS_DIR"]).expanduser())
    out.append(SCRIPT_DIR.parent / "credentials")
    return out


def load_strict_credentials_file(path: Path) -> None:
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    header_seen = False
    for idx, raw in enumerate(lines, start=1):
        line = raw.strip()
        if not line:
            continue
        if not header_seen:
            if line != CREDENTIALS_HEADER:
                raise ValueError(f"invalid {path}:{idx}; first non-empty line must be {CREDENTIALS_HEADER}")
            header_seen = True
            continue
        if line.startswith("#"):
            continue
        if "=" not in line:
            raise ValueError(f"invalid {path}:{idx}; expected KEY=VALUE")
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if not key or not value:
            raise ValueError(f"invalid {path}:{idx}; expected KEY=VALUE with non-empty value")
        if not re.fullmatch(r"[A-Z0-9_]+", key):
            raise ValueError(f"invalid {path}:{idx}; key must match [A-Z0-9_]+")
        if key not in ALLOWED_CREDENTIAL_KEYS:
            raise ValueError(f"invalid {path}:{idx}; unsupported key: {key}")
        if key not in os.environ:
            os.environ[key] = value
    if not header_seen:
        raise ValueError(f"invalid {path}; missing {CREDENTIALS_HEADER} header")


def load_strict_credentials() -> None:
    for cdir in credentials_file_candidates():
        if not cdir.exists():
            continue
        for name in ("entra.txt", "cloudflare.txt"):
            f = cdir / name
            if f.exists():
                load_strict_credentials_file(f)
        return


def load_env() -> None:
    load_strict_credentials()
    for path in ENV_FILES:
        load_env_file(path)


def env_bool(name: str, default: bool) -> bool:
    raw = os.environ.get(name, "").strip().lower()
    if not raw:
        return default
    return raw in {"1", "true", "yes", "on"}


def base_domain(default_mailbox: str) -> str:
    explicit = os.environ.get("EMAIL_ALIAS_FABRIC_BASE_DOMAIN", "").strip().lower()
    if explicit:
        return explicit
    if "@" in default_mailbox:
        return default_mailbox.split("@", 1)[1].strip().lower()
    return "northorizon.ca"


def exchange_org(default_domain: str) -> str:
    return os.environ.get("EXCHANGE_ORGANIZATION", "").strip() or default_domain


def parse_kv(action: str, key: str) -> str:
    m = re.search(rf"(?:^|\s){re.escape(key)}\s*[:=]\s*([^\s]+)", action, flags=re.IGNORECASE)
    return (m.group(1).strip() if m else "")


def slug(s: str) -> str:
    out = re.sub(r"[^a-z0-9._-]+", "-", (s or "").strip().lower()).strip("-._")
    return out or "alias"


def random_suffix(length: int = 6) -> str:
    alphabet = string.ascii_lowercase + string.digits
    return "".join(random.choice(alphabet) for _ in range(max(2, length)))


def normalize_domain(raw: str) -> str:
    d = (raw or "").strip().lower().strip(".")
    if not d:
        return ""
    if not DOMAIN_RE.fullmatch(d):
        return ""
    return d


def normalize_dns_name(raw: str) -> str:
    n = (raw or "").strip().lower().strip(".")
    if not n:
        return ""
    if not DNS_NAME_RE.fullmatch(n):
        return ""
    return n


def normalize_local(raw: str) -> str:
    l = (raw or "").strip()
    if not l:
        return ""
    if not LOCAL_RE.fullmatch(l):
        return ""
    return l


def parse_intent(intent: dict[str, Any], default_mailbox: str, default_domain: str) -> dict[str, Any]:
    action = str(intent.get("action") or "")
    low = action.lower()

    if re.search(r"\b(list|show|inventory|status)\b", low):
        operation = "list"
    elif re.search(r"\b(delete|remove|drop|retire)\b", low):
        operation = "delete"
    elif re.search(r"\b(rotate|roll)\b", low):
        operation = "rotate"
    elif re.search(r"\b(batch|many|bulk|fanout)\b", low):
        operation = "batch"
    else:
        operation = "create"

    mailbox = parse_kv(action, "mailbox").lower() or default_mailbox.lower()
    prefix = slug(parse_kv(action, "prefix") or parse_kv(action, "name") or "northorizon")
    local_part = normalize_local(parse_kv(action, "local"))
    domain = normalize_domain(parse_kv(action, "domain"))
    subdomain = (parse_kv(action, "subdomain") or "").strip().lower().strip(".")
    count_raw = parse_kv(action, "count") or "1"
    ttl_raw = parse_kv(action, "ttl") or "300"
    ensure_dns = parse_kv(action, "ensure_dns").lower() if parse_kv(action, "ensure_dns") else ""
    auto_domain = parse_kv(action, "auto_domain").lower() if parse_kv(action, "auto_domain") else ""
    no_reply = parse_kv(action, "no_reply").lower() if parse_kv(action, "no_reply") else ""
    preserve_reply = parse_kv(action, "preserve_reply").lower() if parse_kv(action, "preserve_reply") else ""
    fallback_mailbox = (parse_kv(action, "fallback_mailbox") or parse_kv(action, "fallback") or "").strip().lower()
    if not no_reply:
        no_reply = parse_kv(action, "noreply").lower() if parse_kv(action, "noreply") else ""
    target_email = (parse_kv(action, "email") or parse_kv(action, "alias")).strip().lower()
    if target_email and not EMAIL_RE.fullmatch(target_email):
        target_email = ""
    if not target_email:
        candidates = [f"{a}@{b}".lower() for (a, b) in EMAIL_RE.findall(action)]
        for cand in candidates:
            if cand != mailbox:
                target_email = cand
                break

    if subdomain and SUBDOMAIN_RE.fullmatch(subdomain):
        if not domain:
            domain = f"{subdomain}.{default_domain}"
    if not domain:
        domain = default_domain

    if target_email:
        parts = target_email.split("@", 1)
        local_part = parts[0]
        domain = parts[1]

    try:
        count = int(count_raw)
    except Exception:
        count = 1
    count = max(1, min(count, 200))

    try:
        ttl = int(ttl_raw)
    except Exception:
        ttl = 300
    ttl = max(120, min(ttl, 86400))

    ensure_dns_flag = env_bool("EMAIL_ALIAS_FABRIC_AUTO_DNS", True)
    if ensure_dns in {"1", "true", "yes", "on"}:
        ensure_dns_flag = True
    elif ensure_dns in {"0", "false", "no", "off"}:
        ensure_dns_flag = False

    auto_domain_flag = env_bool("EMAIL_ALIAS_FABRIC_AUTO_DOMAIN_PROVISION", True)
    if auto_domain in {"1", "true", "yes", "on"}:
        auto_domain_flag = True
    elif auto_domain in {"0", "false", "no", "off"}:
        auto_domain_flag = False

    no_reply_flag = env_bool("EMAIL_ALIAS_FABRIC_NO_REPLY_DEFAULT", False)
    if no_reply in {"1", "true", "yes", "on"}:
        no_reply_flag = True
    elif no_reply in {"0", "false", "no", "off"}:
        no_reply_flag = False

    preserve_reply_flag = env_bool("EMAIL_ALIAS_FABRIC_DELETE_PRESERVE_REPLY_DEFAULT", True)
    if preserve_reply in {"1", "true", "yes", "on"}:
        preserve_reply_flag = True
    elif preserve_reply in {"0", "false", "no", "off"}:
        preserve_reply_flag = False
    if not fallback_mailbox:
        fallback_mailbox = os.environ.get("EMAIL_ALIAS_FABRIC_FALLBACK_MAILBOX", "").strip().lower()
    if fallback_mailbox and not EMAIL_RE.fullmatch(fallback_mailbox):
        fallback_mailbox = ""

    return {
        "operation": operation,
        "action_text": action,
        "mailbox": mailbox,
        "prefix": prefix,
        "local_part": local_part,
        "domain": domain,
        "target_email": target_email,
        "count": count,
        "ttl": ttl,
        "ensure_dns": ensure_dns_flag,
        "auto_domain": auto_domain_flag,
        "no_reply": no_reply_flag,
        "preserve_reply": preserve_reply_flag,
        "fallback_mailbox": fallback_mailbox,
    }


def client_credentials_token(scope: str) -> str:
    tenant = os.environ.get("ENTRA_TENANT_ID", "").strip()
    client = os.environ.get("ENTRA_CLIENT_ID", "").strip()
    secret = os.environ.get("ENTRA_CLIENT_SECRET", "").strip()
    if not tenant or not client or not secret:
        return ""
    body = urllib.parse.urlencode(
        {
            "client_id": client,
            "client_secret": secret,
            "scope": scope,
            "grant_type": "client_credentials",
        }
    ).encode("utf-8")
    req = urllib.request.Request(
        f"https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token",
        data=body,
        method="POST",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            payload = json.loads(resp.read().decode("utf-8", errors="replace"))
        return str(payload.get("access_token") or "")
    except Exception:
        return ""


def graph_request(method: str, path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    token = client_credentials_token("https://graph.microsoft.com/.default")
    if not token:
        return {"ok": False, "error": "missing Graph token (check ENTRA_* env + secret)"}
    data = None
    if payload is not None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        f"https://graph.microsoft.com{path}",
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        data=data,
    )
    try:
        with urllib.request.urlopen(req, timeout=35) as resp:
            text = resp.read().decode("utf-8", errors="replace")
            if not text.strip():
                return {"ok": True, "result": {}}
            parsed = json.loads(text)
            return {"ok": True, "result": parsed}
    except urllib.error.HTTPError as exc:
        raw = ""
        try:
            raw = exc.read().decode("utf-8", errors="replace")
        except Exception:
            raw = str(exc)
        return {"ok": False, "status": exc.code, "error": raw[:1200]}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def graph_request_path(path: str) -> dict[str, Any]:
    return graph_request("GET", path)


def graph_get_service_principal_by_app_id(app_id: str) -> dict[str, Any]:
    app_id = (app_id or "").strip()
    if not app_id:
        return {"ok": False, "error": "missing app id"}
    query = urllib.parse.urlencode(
        {
            "$filter": f"appId eq '{app_id}'",
            "$select": "id,appId,displayName,appRoles",
        }
    )
    path = f"/v1.0/servicePrincipals?{query}"
    res = graph_request_path(path)
    if not res.get("ok"):
        return {"ok": False, "error": res.get("error")}
    rows = (res.get("result") or {}).get("value")
    if not isinstance(rows, list) or not rows:
        return {"ok": False, "error": f"service principal not found for appId={app_id}"}
    return {"ok": True, "service_principal": rows[0]}


def graph_get_app_role_assignments(sp_id: str) -> dict[str, Any]:
    sp_id = (sp_id or "").strip()
    if not sp_id:
        return {"ok": False, "error": "missing service principal id"}
    path = f"/v1.0/servicePrincipals/{urllib.parse.quote(sp_id)}/appRoleAssignments?$top=999"
    res = graph_request_path(path)
    if not res.get("ok"):
        return {"ok": False, "error": res.get("error")}
    rows = (res.get("result") or {}).get("value")
    if not isinstance(rows, list):
        rows = []
    return {"ok": True, "assignments": rows}


def graph_permissions_audit(include_assignments: bool = False) -> dict[str, Any]:
    client_id = os.environ.get("ENTRA_CLIENT_ID", "").strip()
    if not client_id:
        return {"ok": False, "error": "missing ENTRA_CLIENT_ID"}
    app_sp = graph_get_service_principal_by_app_id(client_id)
    if not app_sp.get("ok"):
        return {"ok": False, "error": app_sp.get("error"), "client_id": client_id}

    app_row = app_sp.get("service_principal") or {}
    app_sp_id = str(app_row.get("id") or "").strip()
    assign_res = graph_get_app_role_assignments(app_sp_id)
    if not assign_res.get("ok"):
        return {"ok": False, "error": assign_res.get("error"), "service_principal_id": app_sp_id}

    resource_lookup: dict[str, dict[str, str]] = {}
    resolved_resources: dict[str, Any] = {}
    for app_id in (GRAPH_RESOURCE_APP_ID, EXCHANGE_RESOURCE_APP_ID):
        sp_res = graph_get_service_principal_by_app_id(app_id)
        if not sp_res.get("ok"):
            resolved_resources[app_id] = {"ok": False, "error": sp_res.get("error")}
            continue
        row = sp_res.get("service_principal") or {}
        rid = str(row.get("id") or "").strip()
        role_map: dict[str, str] = {}
        for role in (row.get("appRoles") or []):
            if not isinstance(role, dict):
                continue
            role_id = str(role.get("id") or "").strip().lower()
            value = str(role.get("value") or "").strip()
            if role_id and value:
                role_map[role_id] = value
        resource_lookup[rid] = role_map
        resolved_resources[app_id] = {
            "ok": True,
            "id": rid,
            "displayName": row.get("displayName"),
            "appId": row.get("appId"),
        }

    assigned_by_resource: dict[str, set[str]] = {}
    flattened: list[dict[str, Any]] = []
    for row in assign_res.get("assignments", []):
        if not isinstance(row, dict):
            continue
        resource_id = str(row.get("resourceId") or "").strip()
        role_id = str(row.get("appRoleId") or "").strip().lower()
        role_value = (resource_lookup.get(resource_id) or {}).get(role_id, "")
        if resource_id and role_value:
            assigned_by_resource.setdefault(resource_id, set()).add(role_value)
        flattened.append(
            {
                "resourceId": resource_id,
                "appRoleId": str(row.get("appRoleId") or ""),
                "roleValue": role_value,
            }
        )

    graph_resource_id = str((resolved_resources.get(GRAPH_RESOURCE_APP_ID) or {}).get("id") or "")
    exchange_resource_id = str((resolved_resources.get(EXCHANGE_RESOURCE_APP_ID) or {}).get("id") or "")
    graph_roles = sorted(assigned_by_resource.get(graph_resource_id, set()))
    exchange_roles = sorted(assigned_by_resource.get(exchange_resource_id, set()))
    graph_missing = sorted(REQUIRED_GRAPH_APP_ROLES - set(graph_roles))
    exchange_missing = sorted(REQUIRED_EXCHANGE_APP_ROLES - set(exchange_roles))

    out = {
        "ok": True,
        "client_id": client_id,
        "service_principal_id": app_sp_id,
        "resources": resolved_resources,
        "graph_roles_assigned": graph_roles,
        "graph_roles_missing": graph_missing,
        "exchange_api_roles_assigned": exchange_roles,
        "exchange_api_roles_missing": exchange_missing,
        "ready": not graph_missing and not exchange_missing,
    }
    if include_assignments:
        out["assignments"] = flattened
    return out


def cloudflare_token() -> str:
    return os.environ.get("CLOUDFLARE_API_TOKEN", "").strip() or os.environ.get("CF_API_TOKEN", "").strip()


def cloudflare_zone_id() -> str:
    return os.environ.get("CLOUDFLARE_ZONE_ID", "").strip() or os.environ.get("CF_ZONE_ID", "").strip()


def cloudflare_request(method: str, path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    tok = cloudflare_token()
    zid = cloudflare_zone_id()
    if not tok or not zid:
        return {"ok": False, "error": "missing cloudflare token or zone id"}
    data = None
    if payload is not None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        f"https://api.cloudflare.com/client/v4/zones/{zid}{path}",
        method=method,
        headers={
            "Authorization": f"Bearer {tok}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        data=data,
    )
    try:
        with urllib.request.urlopen(req, timeout=25) as resp:
            parsed = json.loads(resp.read().decode("utf-8", errors="replace"))
        return parsed if isinstance(parsed, dict) else {"ok": False, "error": "invalid cloudflare json"}
    except urllib.error.HTTPError as exc:
        raw = ""
        try:
            raw = exc.read().decode("utf-8", errors="replace")
        except Exception:
            raw = str(exc)
        return {"ok": False, "error": f"http {exc.code}: {raw[:800]}"}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def cloudflare_global_request(path: str) -> dict[str, Any]:
    tok = cloudflare_token()
    if not tok:
        return {"ok": False, "error": "missing cloudflare token"}
    req = urllib.request.Request(
        f"https://api.cloudflare.com/client/v4{path}",
        method="GET",
        headers={
            "Authorization": f"Bearer {tok}",
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=25) as resp:
            parsed = json.loads(resp.read().decode("utf-8", errors="replace"))
        return parsed if isinstance(parsed, dict) else {"ok": False, "error": "invalid cloudflare json"}
    except urllib.error.HTTPError as exc:
        raw = ""
        try:
            raw = exc.read().decode("utf-8", errors="replace")
        except Exception:
            raw = str(exc)
        return {"ok": False, "error": f"http {exc.code}: {raw[:800]}"}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def ps_quote(value: str) -> str:
    return "'" + str(value).replace("'", "''") + "'"


def run_pwsh(ps_source: str, timeout: int = 120) -> dict[str, Any]:
    with tempfile.NamedTemporaryFile("w", suffix=".ps1", delete=False, encoding="utf-8") as tf:
        temp_path = tf.name
        tf.write("$ErrorActionPreference='Stop'\n")
        tf.write(ps_source)
    try:
        proc = subprocess.run(
            ["pwsh", "-NoLogo", "-NoProfile", "-File", temp_path],
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        return {
            "ok": proc.returncode == 0,
            "returncode": proc.returncode,
            "stdout": (proc.stdout or "").strip(),
            "stderr": (proc.stderr or "").strip(),
        }
    except Exception as exc:
        return {"ok": False, "error": str(exc), "stdout": "", "stderr": ""}
    finally:
        try:
            Path(temp_path).unlink(missing_ok=True)
        except Exception:
            pass


def exchange_connect_script(default_domain: str) -> str:
    tenant = os.environ.get("ENTRA_TENANT_ID", "").strip()
    client = os.environ.get("ENTRA_CLIENT_ID", "").strip()
    secret = os.environ.get("ENTRA_CLIENT_SECRET", "").strip()
    org = exchange_org(default_domain)
    if not tenant or not client or not secret:
        return "throw 'Missing ENTRA_CLIENT_ID/ENTRA_TENANT_ID/ENTRA_CLIENT_SECRET'"
    return f"""
Import-Module ExchangeOnlineManagement -Force
$body=@{{client_id={ps_quote(client)};client_secret={ps_quote(secret)};scope='https://outlook.office365.com/.default';grant_type='client_credentials'}}
$tok=Invoke-RestMethod -Method Post -Uri {ps_quote(f"https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token")} -Body $body -ContentType 'application/x-www-form-urlencoded'
Connect-ExchangeOnline -AccessToken $tok.access_token -Organization {ps_quote(org)} -ShowBanner:$false
"""


def exchange_get_accepted_domains(default_domain: str) -> dict[str, Any]:
    script = (
        exchange_connect_script(default_domain)
        + """
$rows = Get-AcceptedDomain | Select-Object Name,DomainName,DomainType
$rows | ConvertTo-Json -Compress
Disconnect-ExchangeOnline -Confirm:$false
"""
    )
    out = run_pwsh(script, timeout=180)
    if not out.get("ok"):
        return {"ok": False, "error": out.get("stderr") or out.get("error") or out.get("stdout")}
    raw = str(out.get("stdout") or "")
    try:
        parsed = json.loads(raw) if raw else []
    except Exception:
        parsed = []
    if isinstance(parsed, dict):
        parsed = [parsed]
    domains: list[str] = []
    for row in parsed if isinstance(parsed, list) else []:
        d = normalize_domain(str((row or {}).get("DomainName") or ""))
        if d:
            domains.append(d)
    return {"ok": True, "domains": sorted(set(domains)), "raw": parsed}


def exchange_get_mailbox_aliases(default_domain: str, mailbox: str) -> dict[str, Any]:
    script = (
        exchange_connect_script(default_domain)
        + f"""
$addr = (Get-Mailbox -Identity {ps_quote(mailbox)}).EmailAddresses
$addr | ForEach-Object {{$_.ToString()}} | ConvertTo-Json -Compress
Disconnect-ExchangeOnline -Confirm:$false
"""
    )
    out = run_pwsh(script, timeout=180)
    if not out.get("ok"):
        return {"ok": False, "error": out.get("stderr") or out.get("error") or out.get("stdout")}
    raw = str(out.get("stdout") or "")
    try:
        parsed = json.loads(raw) if raw else []
    except Exception:
        parsed = []
    if isinstance(parsed, str):
        parsed = [parsed]
    aliases: list[str] = []
    for item in parsed if isinstance(parsed, list) else []:
        s = str(item or "")
        if ":" in s:
            _, addr = s.split(":", 1)
        else:
            addr = s
        m = EMAIL_RE.search(addr)
        if m:
            aliases.append(f"{m.group(1)}@{m.group(2)}".lower())
    return {"ok": True, "aliases": sorted(set(aliases))}


def exchange_set_alias(default_domain: str, mailbox: str, alias_email: str, mode: str) -> dict[str, Any]:
    mode_low = mode.lower()
    ps_alias = "smtp:" + alias_email.lower()
    if mode_low not in {"add", "remove"}:
        return {"ok": False, "error": "mode must be add/remove"}
    op = "Add" if mode_low == "add" else "Remove"
    retries = int(os.environ.get("EMAIL_ALIAS_FABRIC_EXCHANGE_SET_ALIAS_RETRIES", "6") or "6")
    retries = max(1, min(retries, 12))
    wait_seconds = int(os.environ.get("EMAIL_ALIAS_FABRIC_EXCHANGE_SET_ALIAS_RETRY_SECONDS", "5") or "5")
    wait_seconds = max(1, min(wait_seconds, 30))

    last_error = "unknown exchange error"
    for attempt in range(1, retries + 1):
        script = (
            exchange_connect_script(default_domain)
            + f"""
Set-Mailbox -Identity {ps_quote(mailbox)} -EmailAddresses @{{{op}={ps_quote(ps_alias)}}}
$after = (Get-Mailbox -Identity {ps_quote(mailbox)}).EmailAddresses | ForEach-Object {{$_.ToString()}}
$after | ConvertTo-Json -Compress
Disconnect-ExchangeOnline -Confirm:$false
"""
        )
        out = run_pwsh(script, timeout=220)
        if not out.get("ok"):
            err = out.get("stderr") or out.get("error") or out.get("stdout") or "unknown exchange error"
            err_text = str(err)[:1000]
            last_error = err_text
            if "not an accepted domain" in err_text.lower() and attempt < retries:
                time.sleep(wait_seconds)
                continue
            return {"ok": False, "error": err_text, "attempts": attempt}

        raw = str(out.get("stdout") or "")
        try:
            parsed = json.loads(raw) if raw else []
        except Exception:
            parsed = []
        if isinstance(parsed, str):
            parsed = [parsed]
        has_alias = False
        for item in parsed if isinstance(parsed, list) else []:
            s = str(item or "")
            if ":" in s:
                _, addr = s.split(":", 1)
            else:
                addr = s
            if addr.strip().lower() == alias_email.lower():
                has_alias = True
                break

        if mode_low == "add":
            if has_alias:
                return {"ok": True, "alias": alias_email.lower(), "mode": mode_low, "attempts": attempt}
            last_error = "alias not present after add"
            if attempt < retries:
                time.sleep(wait_seconds)
                continue
            return {"ok": False, "error": last_error, "attempts": attempt}

        if not has_alias:
            return {"ok": True, "alias": alias_email.lower(), "mode": mode_low, "attempts": attempt}
        last_error = "alias still present after remove"
        if attempt < retries:
            time.sleep(wait_seconds)
            continue
        return {"ok": False, "error": last_error, "attempts": attempt}

    return {"ok": False, "error": last_error, "attempts": retries}


def graph_get_domain(domain: str) -> dict[str, Any]:
    res = graph_request("GET", f"/v1.0/domains/{urllib.parse.quote(domain)}")
    if not res.get("ok"):
        return res
    result = res.get("result", {})
    return {"ok": True, "domain": result}


def graph_create_domain(domain: str) -> dict[str, Any]:
    return graph_request("POST", "/v1.0/domains", {"id": domain})


def graph_promote_domain(domain: str) -> dict[str, Any]:
    return graph_request("POST", f"/v1.0/domains/{urllib.parse.quote(domain)}/promote", {})


def exchange_add_accepted_domain(default_domain: str, target_domain: str) -> dict[str, Any]:
    script = (
        exchange_connect_script(default_domain)
        + f"""
$existing = Get-AcceptedDomain -Identity {ps_quote(target_domain)} -ErrorAction SilentlyContinue
if (-not $existing) {{
  New-AcceptedDomain -Name {ps_quote(target_domain)} -DomainName {ps_quote(target_domain)} -DomainType Authoritative | Out-Null
}}
$row = Get-AcceptedDomain -Identity {ps_quote(target_domain)} -ErrorAction SilentlyContinue | Select-Object Name,DomainName,DomainType
$row | ConvertTo-Json -Compress
Disconnect-ExchangeOnline -Confirm:$false
"""
    )
    out = run_pwsh(script, timeout=220)
    if not out.get("ok"):
        return {"ok": False, "error": out.get("stderr") or out.get("error") or out.get("stdout")}
    raw = str(out.get("stdout") or "")
    try:
        parsed = json.loads(raw) if raw else {}
    except Exception:
        parsed = {}
    found_domain = normalize_domain(str((parsed or {}).get("DomainName") or ""))
    return {
        "ok": bool(found_domain == target_domain),
        "record": parsed,
        "error": None if found_domain == target_domain else "accepted domain not confirmed after create",
    }


def exchange_remove_accepted_domain(default_domain: str, target_domain: str) -> dict[str, Any]:
    script = (
        exchange_connect_script(default_domain)
        + f"""
$exists = Get-AcceptedDomain -Identity {ps_quote(target_domain)} -ErrorAction SilentlyContinue
if ($exists) {{
  Remove-AcceptedDomain -Identity {ps_quote(target_domain)} -Confirm:$false
}}
$still = [bool](Get-AcceptedDomain -Identity {ps_quote(target_domain)} -ErrorAction SilentlyContinue)
@{{ok=(-not $still); still_present=$still}} | ConvertTo-Json -Compress
Disconnect-ExchangeOnline -Confirm:$false
"""
    )
    out = run_pwsh(script, timeout=240)
    if not out.get("ok"):
        return {"ok": False, "error": out.get("stderr") or out.get("error") or out.get("stdout")}
    raw = str(out.get("stdout") or "")
    try:
        parsed = json.loads(raw) if raw else {}
    except Exception:
        parsed = {}
    if not isinstance(parsed, dict):
        parsed = {}
    return {"ok": bool(parsed.get("ok")), "still_present": bool(parsed.get("still_present")), "raw": parsed}


def exchange_service_principal_authorization(default_domain: str) -> dict[str, Any]:
    client = os.environ.get("ENTRA_CLIENT_ID", "").strip()
    if not client:
        return {"ok": False, "error": "missing ENTRA_CLIENT_ID"}
    script = (
        exchange_connect_script(default_domain)
        + f"""
$rows = @()
try {{
  $rows = Test-ServicePrincipalAuthorization -Identity {ps_quote(client)} | Select-Object RoleName,AllowedResourceScope,ScopeType,InScope
}} catch {{
  Write-Output (@{{ error = $_.Exception.Message }} | ConvertTo-Json -Compress)
  Disconnect-ExchangeOnline -Confirm:$false
  exit 0
}}
$rows | ConvertTo-Json -Compress
Disconnect-ExchangeOnline -Confirm:$false
"""
    )
    out = run_pwsh(script, timeout=240)
    if not out.get("ok"):
        return {"ok": False, "error": out.get("stderr") or out.get("error") or out.get("stdout")}
    raw = str(out.get("stdout") or "")
    try:
        parsed = json.loads(raw) if raw else []
    except Exception:
        parsed = []
    if isinstance(parsed, dict) and "error" in parsed:
        return {"ok": False, "error": str(parsed.get("error") or "unknown exchange error")}
    if isinstance(parsed, dict):
        parsed = [parsed]
    if not isinstance(parsed, list):
        parsed = []
    roles = {str((r or {}).get("RoleName") or "").strip() for r in parsed if isinstance(r, dict)}
    roles.discard("")
    missing = sorted(REQUIRED_EXCHANGE_RBAC_ROLES - roles)
    return {
        "ok": True,
        "roles": sorted(roles),
        "missing_roles": missing,
        "rows": parsed,
        "ready": len(missing) == 0,
    }


def ensure_domain_accepted(target_domain: str, default_domain: str, auto_domain: bool, allow_mutation: bool) -> dict[str, Any]:
    accepted = exchange_get_accepted_domains(default_domain)
    if not accepted.get("ok"):
        return {"ok": False, "status": "exchange_probe_failed", "error": accepted.get("error")}
    accepted_domains = set(accepted.get("domains", []))
    if target_domain in accepted_domains:
        return {"ok": True, "accepted_domains": sorted(accepted_domains), "status": "ready"}

    actions: list[dict[str, Any]] = []
    if auto_domain and allow_mutation:
        existing = graph_get_domain(target_domain)
        if existing.get("ok"):
            dom = existing.get("domain", {})
            actions.append(
                {
                    "step": "graph_get_domain",
                    "result": {
                        "ok": True,
                        "id": dom.get("id"),
                        "isVerified": dom.get("isVerified"),
                        "authenticationType": dom.get("authenticationType"),
                        "supportedServices": dom.get("supportedServices"),
                    },
                }
            )
        else:
            created = graph_create_domain(target_domain)
            actions.append({"step": "graph_create_domain", "result": created})

        promoted = graph_promote_domain(target_domain)
        actions.append({"step": "graph_promote_domain", "result": promoted})

        for _ in range(5):
            accepted_retry = exchange_get_accepted_domains(default_domain)
            if accepted_retry.get("ok"):
                accepted_domains = set(accepted_retry.get("domains", []))
                if target_domain in accepted_domains:
                    return {
                        "ok": True,
                        "accepted_domains": sorted(accepted_domains),
                        "status": "created_promoted_and_ready",
                        "actions": actions,
                    }
            time.sleep(2)

        ex_created = exchange_add_accepted_domain(default_domain, target_domain)
        actions.append({"step": "exchange_add_accepted_domain", "result": ex_created})
        accepted_final = exchange_get_accepted_domains(default_domain)
        if accepted_final.get("ok"):
            accepted_domains = set(accepted_final.get("domains", []))
            if target_domain in accepted_domains:
                return {
                    "ok": True,
                    "accepted_domains": sorted(accepted_domains),
                    "status": "exchange_created_and_ready",
                    "actions": actions,
                }
    elif auto_domain and not allow_mutation:
        actions.append({"step": "graph_create_domain", "status": "skipped_dry_run"})

    root_state = graph_get_domain(default_domain)
    return {
        "ok": False,
        "status": "missing_accepted_domain",
        "accepted_domains": sorted(accepted_domains),
        "target_domain": target_domain,
        "actions": actions,
        "root_domain_state": root_state.get("domain"),
        "error": (
            "target domain is not accepted in Exchange transport plane. "
            "If root domain is Federated, switch to Managed (or add accepted domain via tenant admin) first."
        ),
    }


def ensure_dns_marker(fqdn: str, ttl: int, default_domain: str) -> dict[str, Any]:
    if fqdn == default_domain:
        return {"ok": True, "status": "skipped_root_domain"}
    marker = os.environ.get("EMAIL_ALIAS_FABRIC_MARKER_TXT", "lmtlss-alias-fabric").strip() or "lmtlss-alias-fabric"
    query = urllib.parse.urlencode({"name": fqdn, "type": "TXT"})
    existing = cloudflare_request("GET", f"/dns_records?{query}")
    if not existing.get("success"):
        return {"ok": False, "error": existing.get("error") or "cloudflare lookup failed"}
    result = existing.get("result") if isinstance(existing.get("result"), list) else []

    for row in result:
        content = str((row or {}).get("content") or "").strip()
        if content == marker:
            return {"ok": True, "record_id": str((row or {}).get("id") or "").strip(), "status": "already_present"}

    payload = {"type": "TXT", "name": fqdn, "content": marker, "ttl": ttl, "proxied": False}
    created = cloudflare_request("POST", "/dns_records", payload)
    if created.get("success"):
        rec_id = str(((created.get("result") or {}).get("id") or "")).strip()
        return {"ok": True, "record_id": rec_id, "result": created}

    # Cloudflare can race and return "identical record exists"; treat as success if marker now exists.
    retry = cloudflare_request("GET", f"/dns_records?{query}")
    if retry.get("success"):
        rows = retry.get("result") if isinstance(retry.get("result"), list) else []
        for row in rows:
            content = str((row or {}).get("content") or "").strip()
            if content == marker:
                return {"ok": True, "record_id": str((row or {}).get("id") or "").strip(), "status": "already_present_after_retry"}

    return {"ok": False, "error": created.get("error") or "cloudflare create failed", "result": created}


def cloudflare_list_records(name: str, rtype: str) -> dict[str, Any]:
    query = urllib.parse.urlencode({"name": name, "type": rtype})
    listed = cloudflare_request("GET", f"/dns_records?{query}")
    if not listed.get("success"):
        return {"ok": False, "error": listed.get("error") or "cloudflare list failed"}
    rows = listed.get("result") if isinstance(listed.get("result"), list) else []
    return {"ok": True, "rows": rows}


def cloudflare_delete_records(name: str, rtype: str) -> dict[str, Any]:
    listed = cloudflare_list_records(name, rtype)
    if not listed.get("ok"):
        return {"ok": False, "error": listed.get("error")}
    rows = listed.get("rows", [])
    deleted = 0
    for row in rows:
        rid = str((row or {}).get("id") or "").strip()
        if not rid:
            continue
        out = cloudflare_request("DELETE", f"/dns_records/{rid}")
        if out.get("success"):
            deleted += 1
    return {"ok": True, "deleted": deleted}


def cloudflare_upsert_mx(name: str, target: str, ttl: int, priority: int = 0) -> dict[str, Any]:
    listed = cloudflare_list_records(name, "MX")
    if not listed.get("ok"):
        return {"ok": False, "error": listed.get("error")}
    rows = listed.get("rows", [])
    record_id = ""
    for row in rows:
        content = str((row or {}).get("content") or "").strip().lower()
        if content == target.lower():
            record_id = str((row or {}).get("id") or "").strip()
            break
    if not record_id and rows:
        record_id = str((rows[0] or {}).get("id") or "").strip()
    payload = {"type": "MX", "name": name, "content": target, "priority": int(priority), "ttl": int(ttl)}
    if record_id:
        out = cloudflare_request("PUT", f"/dns_records/{record_id}", payload)
    else:
        out = cloudflare_request("POST", "/dns_records", payload)
    return {"ok": bool(out.get("success")), "result": out, "record_id": record_id or ((out.get("result") or {}).get("id"))}


def cloudflare_upsert_txt_spf(name: str, value: str, ttl: int) -> dict[str, Any]:
    listed = cloudflare_list_records(name, "TXT")
    if not listed.get("ok"):
        return {"ok": False, "error": listed.get("error")}
    rows = listed.get("rows", [])
    record_id = ""
    for row in rows:
        content = str((row or {}).get("content") or "").lower()
        if "spf1" in content:
            record_id = str((row or {}).get("id") or "").strip()
            break
    payload = {"type": "TXT", "name": name, "content": value, "ttl": int(ttl)}
    if record_id:
        out = cloudflare_request("PUT", f"/dns_records/{record_id}", payload)
    else:
        out = cloudflare_request("POST", "/dns_records", payload)
    return {"ok": bool(out.get("success")), "result": out, "record_id": record_id or ((out.get("result") or {}).get("id"))}


def cloudflare_upsert_txt_exact(name: str, value: str, ttl: int) -> dict[str, Any]:
    listed = cloudflare_list_records(name, "TXT")
    if not listed.get("ok"):
        return {"ok": False, "error": listed.get("error")}
    rows = listed.get("rows", [])
    rec_id = ""
    for row in rows:
        content = str((row or {}).get("content") or "").strip()
        if content == value:
            return {"ok": True, "record_id": str((row or {}).get("id") or "").strip(), "status": "already_present"}
        if content.lower().startswith("v=dmarc1"):
            rec_id = str((row or {}).get("id") or "").strip()
    payload = {"type": "TXT", "name": name, "content": value, "ttl": int(ttl)}
    if rec_id:
        out = cloudflare_request("PUT", f"/dns_records/{rec_id}", payload)
    else:
        out = cloudflare_request("POST", "/dns_records", payload)
    return {"ok": bool(out.get("success")), "result": out, "record_id": rec_id or ((out.get("result") or {}).get("id"))}


def ensure_dmarc_domain(fqdn: str, ttl: int, no_reply: bool) -> dict[str, Any]:
    env_key = "EMAIL_ALIAS_FABRIC_DMARC_NOREPLY" if no_reply else "EMAIL_ALIAS_FABRIC_DMARC_REPLY"
    default_val = "v=DMARC1; p=reject; adkim=s; aspf=s; pct=100" if no_reply else "v=DMARC1; p=none; adkim=r; aspf=r; pct=100"
    value = os.environ.get(env_key, "").strip() or default_val
    return cloudflare_upsert_txt_exact(f"_dmarc.{fqdn}", value=value, ttl=ttl)


def ensure_subdomain_mail_dns(fqdn: str, ttl: int, default_domain: str, no_reply: bool) -> dict[str, Any]:
    if fqdn == default_domain:
        return {"ok": True, "status": "skipped_root_domain", "no_reply": no_reply}

    marker_txt = os.environ.get("EMAIL_ALIAS_FABRIC_MARKER_TXT", "lmtlss-alias-fabric").strip() or "lmtlss-alias-fabric"
    mx_target = os.environ.get("EMAIL_ALIAS_FABRIC_MX_TARGET", "").strip().lower()
    if not mx_target:
        mx_target = f"{default_domain.replace('.', '-')}.mail.protection.outlook.com"

    # Keep marker always so orchestration can identify managed subdomains.
    marker_res = ensure_dns_marker(fqdn, ttl=ttl, default_domain=default_domain)
    if not marker_res.get("ok"):
        return {"ok": False, "error": "marker upsert failed", "marker_result": marker_res}

    if no_reply:
        # Explicit no-reply path: no MX + strict SPF fail.
        del_mx = cloudflare_delete_records(fqdn, "MX")
        spf_res = cloudflare_upsert_txt_spf(fqdn, "v=spf1 -all", ttl=ttl)
        dmarc_res = ensure_dmarc_domain(fqdn, ttl=ttl, no_reply=True)
        ok = bool(del_mx.get("ok")) and bool(spf_res.get("ok")) and bool(dmarc_res.get("ok"))
        return {
            "ok": ok,
            "status": "no_reply_dns_applied" if ok else "failed",
            "no_reply": True,
            "mx_deleted": del_mx,
            "spf_result": spf_res,
            "dmarc_result": dmarc_res,
            "marker_result": marker_res,
            "mx_target": mx_target,
            "marker": marker_txt,
        }

    # Inbound-capable path: enforce MX + SPF include O365.
    mx_res = cloudflare_upsert_mx(fqdn, target=mx_target, ttl=ttl, priority=0)
    spf_res = cloudflare_upsert_txt_spf(fqdn, "v=spf1 include:spf.protection.outlook.com -all", ttl=ttl)
    dmarc_res = ensure_dmarc_domain(fqdn, ttl=ttl, no_reply=False)
    ok = bool(mx_res.get("ok")) and bool(spf_res.get("ok")) and bool(dmarc_res.get("ok"))
    return {
        "ok": ok,
        "status": "mail_dns_applied" if ok else "failed",
        "no_reply": False,
        "mx_result": mx_res,
        "spf_result": spf_res,
        "dmarc_result": dmarc_res,
        "marker_result": marker_res,
        "mx_target": mx_target,
        "marker": marker_txt,
    }


def list_domains_graph() -> dict[str, Any]:
    res = graph_request("GET", "/v1.0/domains?$select=id,isVerified,isDefault,authenticationType")
    if not res.get("ok"):
        return {"ok": False, "error": res.get("error")}
    rows = res.get("result", {}).get("value", [])
    if not isinstance(rows, list):
        rows = []
    cleaned = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        cleaned.append(
            {
                "id": str(row.get("id") or ""),
                "isVerified": bool(row.get("isVerified")),
                "isDefault": bool(row.get("isDefault")),
                "authenticationType": row.get("authenticationType"),
            }
        )
    return {"ok": True, "domains": cleaned}


def registry_read() -> dict[str, Any]:
    base = {"updated_at_utc": None, "entries": []}
    data = read_json(REGISTRY_PATH, base)
    if not isinstance(data, dict):
        return base
    entries = data.get("entries")
    if not isinstance(entries, list):
        data["entries"] = []
    return data


def registry_write(data: dict[str, Any]) -> None:
    data["updated_at_utc"] = now_utc()
    REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    write_json_atomic(REGISTRY_PATH, data, indent=2)


def registry_upsert_entry(alias_email: str, mailbox: str, dns_result: dict[str, Any] | None, operation: str) -> None:
    reg = registry_read()
    entries = reg.get("entries", [])
    if not isinstance(entries, list):
        entries = []
    now = now_utc()
    found = None
    for row in entries:
        if isinstance(row, dict) and str(row.get("alias_email", "")).lower() == alias_email.lower():
            found = row
            break
    if not found:
        found = {"alias_email": alias_email.lower()}
        entries.append(found)
    found["mailbox"] = mailbox.lower()
    found["operation"] = operation
    found["updated_at_utc"] = now
    if operation == "delete":
        found["deleted_at_utc"] = now
        found["active"] = False
    else:
        found["created_at_utc"] = found.get("created_at_utc") or now
        found["active"] = True
    if dns_result:
        found["dns_marker"] = {
            "ok": bool(dns_result.get("ok")),
            "record_id": dns_result.get("record_id"),
        }
    reg["entries"] = entries
    registry_write(reg)


def render_alias(local_part: str, domain: str) -> str:
    return f"{local_part}@{domain}".lower()


def generate_local(prefix: str, idx: int | None = None) -> str:
    stamp = datetime.now(timezone.utc).strftime("%m%d%H%M")
    core = f"{prefix}-{stamp}"
    if idx is not None:
        core = f"{core}-{idx:03d}"
    core = f"{core}-{random_suffix(4)}"
    core = core[:64]
    return normalize_local(core) or f"{prefix[:20]}-{random_suffix(8)}"


def execute_create_or_batch(parsed: dict[str, Any], dry_run: bool, default_domain: str) -> dict[str, Any]:
    mailbox = parsed["mailbox"]
    domain = parsed["domain"]
    count = parsed["count"] if parsed["operation"] == "batch" else 1
    local_fixed = parsed["local_part"]
    prefix = parsed["prefix"]
    ensure_dns = parsed["ensure_dns"]
    auto_domain = parsed["auto_domain"]
    ttl = parsed["ttl"]
    no_reply = bool(parsed.get("no_reply"))

    planned_aliases: list[str] = []
    for i in range(count):
        local = local_fixed if local_fixed else generate_local(prefix, i + 1 if count > 1 else None)
        alias = render_alias(local, domain)
        planned_aliases.append(alias)

    domain_plan = ensure_domain_accepted(domain, default_domain, auto_domain=auto_domain, allow_mutation=(not dry_run))
    if dry_run:
        return {
            "ok": bool(domain_plan.get("ok")),
            "status": "dry_run",
            "planned_aliases": planned_aliases,
            "domain_plan": domain_plan,
            "dns_will_run": ensure_dns,
            "no_reply": no_reply,
        }

    if not domain_plan.get("ok"):
        return {
            "ok": False,
            "status": "blocked_domain_plane",
            "planned_aliases": planned_aliases,
            "domain_plan": domain_plan,
        }

    created: list[dict[str, Any]] = []
    for alias_email in planned_aliases:
        dns_result = {"ok": True, "status": "skipped"}
        if ensure_dns:
            dns_result = ensure_subdomain_mail_dns(domain, ttl=ttl, default_domain=default_domain, no_reply=no_reply)
            if not dns_result.get("ok"):
                created.append(
                    {
                        "ok": False,
                        "alias_email": alias_email,
                        "mailbox": mailbox,
                        "error": "dns marker upsert failed",
                        "dns_result": dns_result,
                    }
                )
                continue

        add_res = exchange_set_alias(default_domain, mailbox, alias_email, mode="add")
        if add_res.get("ok"):
            registry_upsert_entry(alias_email, mailbox, dns_result=dns_result, operation="create")
        created.append(
            {
                "ok": bool(add_res.get("ok")),
                "alias_email": alias_email,
                "mailbox": mailbox,
                "dns_result": dns_result,
                "exchange_result": add_res,
                "error": add_res.get("error"),
            }
        )

    ok_all = all(bool(row.get("ok")) for row in created) if created else False
    return {
        "ok": ok_all,
        "status": "live" if ok_all else "failed",
        "created": created,
        "domain_plan": domain_plan,
    }


def retire_alias_with_fallback(
    default_domain: str,
    source_mailbox: str,
    alias_email: str,
    fallback_mailbox: str,
    dry_run: bool,
) -> dict[str, Any]:
    source_mailbox = source_mailbox.strip().lower()
    alias_email = alias_email.strip().lower()
    fallback = (fallback_mailbox or source_mailbox).strip().lower()
    if not EMAIL_RE.fullmatch(fallback):
        fallback = source_mailbox

    if dry_run:
        return {
            "ok": True,
            "status": "dry_run",
            "mode": "retire_with_fallback",
            "alias_email": alias_email,
            "source_mailbox": source_mailbox,
            "fallback_mailbox": fallback,
            "reply_continuity_expected": True,
        }

    # Same mailbox fallback means "retire but keep alias attached" so replies still land.
    if fallback == source_mailbox:
        alias_state = exchange_get_mailbox_aliases(default_domain, source_mailbox)
        present = bool(alias_state.get("ok")) and alias_email in set(alias_state.get("aliases", []))
        if present:
            registry_upsert_entry(alias_email, fallback, dns_result=None, operation="retire_keep_alias")
            return {
                "ok": True,
                "status": "live",
                "mode": "retire_keep_alias",
                "alias_email": alias_email,
                "source_mailbox": source_mailbox,
                "fallback_mailbox": fallback,
                "reply_continuity": True,
            }
        return {
            "ok": False,
            "status": "failed",
            "mode": "retire_keep_alias",
            "alias_email": alias_email,
            "source_mailbox": source_mailbox,
            "fallback_mailbox": fallback,
            "error": "alias not present on fallback mailbox; cannot guarantee reply continuity",
            "alias_state": alias_state,
        }

    rm = exchange_set_alias(default_domain, source_mailbox, alias_email, mode="remove")
    if not rm.get("ok"):
        return {
            "ok": False,
            "status": "failed",
            "mode": "retire_move_alias",
            "alias_email": alias_email,
            "source_mailbox": source_mailbox,
            "fallback_mailbox": fallback,
            "remove_result": rm,
            "error": rm.get("error"),
        }

    add = exchange_set_alias(default_domain, fallback, alias_email, mode="add")
    if not add.get("ok"):
        # Best effort rollback to reduce breakage window.
        rollback = exchange_set_alias(default_domain, source_mailbox, alias_email, mode="add")
        return {
            "ok": False,
            "status": "failed",
            "mode": "retire_move_alias",
            "alias_email": alias_email,
            "source_mailbox": source_mailbox,
            "fallback_mailbox": fallback,
            "remove_result": rm,
            "add_result": add,
            "rollback_result": rollback,
            "error": add.get("error"),
        }

    registry_upsert_entry(alias_email, fallback, dns_result=None, operation="retire_fallback_mailbox")
    return {
        "ok": True,
        "status": "live",
        "mode": "retire_move_alias",
        "alias_email": alias_email,
        "source_mailbox": source_mailbox,
        "fallback_mailbox": fallback,
        "remove_result": rm,
        "add_result": add,
        "reply_continuity": True,
    }


def execute_delete(parsed: dict[str, Any], dry_run: bool, default_domain: str) -> dict[str, Any]:
    mailbox = parsed["mailbox"]
    target = parsed["target_email"]
    preserve_reply = bool(parsed.get("preserve_reply", True))
    fallback_mailbox = str(parsed.get("fallback_mailbox") or mailbox).strip().lower()
    if not target:
        local_part = parsed["local_part"] or slug(parsed["prefix"])
        target = render_alias(local_part, parsed["domain"])

    if preserve_reply:
        return retire_alias_with_fallback(
            default_domain=default_domain,
            source_mailbox=mailbox,
            alias_email=target,
            fallback_mailbox=fallback_mailbox,
            dry_run=dry_run,
        )

    if dry_run:
        return {"ok": True, "status": "dry_run", "planned_delete_alias": target, "mailbox": mailbox}

    rm = exchange_set_alias(default_domain, mailbox, target, mode="remove")
    if rm.get("ok"):
        registry_upsert_entry(target, mailbox, dns_result=None, operation="delete")
    return {
        "ok": bool(rm.get("ok")),
        "status": "live" if rm.get("ok") else "failed",
        "mailbox": mailbox,
        "alias_email": target,
        "exchange_result": rm,
        "error": rm.get("error"),
    }


def execute_rotate(parsed: dict[str, Any], dry_run: bool, default_domain: str) -> dict[str, Any]:
    old_email = parsed["target_email"]
    if not old_email:
        return {"ok": False, "status": "blocked_missing_old_alias", "error": "rotate requires existing target email in action"}

    create_plan = dict(parsed)
    create_plan["operation"] = "create"
    create_plan["target_email"] = ""
    create_res = execute_create_or_batch(create_plan, dry_run=dry_run, default_domain=default_domain)
    if not create_res.get("ok"):
        return {"ok": False, "status": create_res.get("status"), "create_result": create_res, "error": "rotate create step failed"}
    if dry_run:
        return {"ok": True, "status": "dry_run", "create_result": create_res, "planned_delete_alias": old_email}

    delete_plan = dict(parsed)
    delete_plan["preserve_reply"] = False
    delete_res = execute_delete(delete_plan, dry_run=False, default_domain=default_domain)
    return {
        "ok": bool(delete_res.get("ok")),
        "status": "live" if delete_res.get("ok") else "failed",
        "create_result": create_res,
        "delete_result": delete_res,
    }


def execute_list(parsed: dict[str, Any], default_domain: str) -> dict[str, Any]:
    mailbox = parsed["mailbox"]
    aliases = exchange_get_mailbox_aliases(default_domain, mailbox)
    accepted = exchange_get_accepted_domains(default_domain)
    graph_domains = list_domains_graph()
    registry = registry_read()
    return {
        "ok": bool(aliases.get("ok")) and bool(accepted.get("ok")),
        "status": "live",
        "mailbox": mailbox,
        "mailbox_aliases": aliases.get("aliases", []),
        "accepted_domains": accepted.get("domains", []),
        "graph_domains": graph_domains.get("domains", []),
        "registry_entries": registry.get("entries", []),
        "errors": {
            "aliases": aliases.get("error"),
            "accepted_domains": accepted.get("error"),
            "graph_domains": graph_domains.get("error"),
        },
    }


def graph_domain_email_enabled(domain: str, retries: int = 10, delay_seconds: int = 3) -> dict[str, Any]:
    retries = max(1, min(int(retries), 30))
    delay_seconds = max(1, min(int(delay_seconds), 30))
    actions: list[dict[str, Any]] = []
    last_state: dict[str, Any] | None = None
    for i in range(retries):
        dom = graph_get_domain(domain)
        if dom.get("ok"):
            state = dom.get("domain", {}) if isinstance(dom.get("domain"), dict) else {}
            last_state = state
            services = state.get("supportedServices")
            if isinstance(services, list) and "Email" in services:
                return {"ok": True, "state": state, "attempts": i + 1, "actions": actions}
        prom = graph_promote_domain(domain)
        actions.append({"attempt": i + 1, "promote_result": prom})
        if i < retries - 1:
            time.sleep(delay_seconds)
    return {
        "ok": False,
        "error": "graph domain email service not enabled",
        "attempts": retries,
        "actions": actions,
        "state": last_state or {},
    }


def cloudflare_domain_dns_summary(fqdn: str) -> dict[str, Any]:
    query = urllib.parse.urlencode({"name": fqdn})
    listed = cloudflare_request("GET", f"/dns_records?{query}")
    if not listed.get("success"):
        return {"ok": False, "error": listed.get("error") or "cloudflare list failed"}
    rows = listed.get("result") if isinstance(listed.get("result"), list) else []
    mx_rows = [r for r in rows if str((r or {}).get("type") or "").upper() == "MX"]
    txt_rows = [r for r in rows if str((r or {}).get("type") or "").upper() == "TXT"]
    txt_values = [str((r or {}).get("content") or "") for r in txt_rows]
    mx_targets = [str((r or {}).get("content") or "").strip().lower() for r in mx_rows]
    return {
        "ok": True,
        "mx_count": len(mx_rows),
        "mx_targets": mx_targets,
        "txt_values": txt_values,
        "has_spf_fail_all": any("v=spf1 -all" in v.lower() for v in txt_values),
        "has_spf_o365": any("include:spf.protection.outlook.com" in v.lower() for v in txt_values),
        "has_marker": any("lmtlss-alias-fabric" in v.lower() for v in txt_values),
        "has_dmarc": any("v=dmarc1" in v.lower() for v in txt_values),
        "records": rows,
    }


def cloudflare_token_audit() -> dict[str, Any]:
    verify = cloudflare_global_request("/user/tokens/verify")
    zone = cloudflare_request("GET", "")
    dns_read = cloudflare_request("GET", "/dns_records?per_page=1")
    return {
        "ok": bool((verify.get("success") is True) and (zone.get("success") is True)),
        "token_verify": verify,
        "zone_probe": zone,
        "dns_read_probe": dns_read,
    }


def cloudflare_dmarc_summary(domain: str) -> dict[str, Any]:
    listed = cloudflare_list_records(f"_dmarc.{domain}", "TXT")
    if not listed.get("ok"):
        return {"ok": False, "error": listed.get("error")}
    rows = listed.get("rows", [])
    values = [str((r or {}).get("content") or "") for r in rows]
    return {
        "ok": True,
        "count": len(rows),
        "values": values,
        "has_dmarc": any("v=dmarc1" in v.lower() for v in values),
    }


def root_mx_target(default_domain: str) -> str:
    mx_target = os.environ.get("EMAIL_ALIAS_FABRIC_MX_TARGET", "").strip().lower()
    if not mx_target:
        mx_target = f"{default_domain.replace('.', '-')}.mail.protection.outlook.com"
    return mx_target


def ensure_root_domain_dns(domain: str, default_domain: str, ttl: int, force: bool, allow_mutation: bool) -> dict[str, Any]:
    summary = cloudflare_domain_dns_summary(domain)
    if not summary.get("ok"):
        return {"ok": False, "error": summary.get("error"), "dns_state": summary}
    dmarc_before = cloudflare_dmarc_summary(domain)
    if not dmarc_before.get("ok"):
        return {"ok": False, "error": dmarc_before.get("error"), "dns_state": summary, "dmarc_state": dmarc_before}

    mx_target = root_mx_target(default_domain)
    operations: list[dict[str, Any]] = []
    spf_value = "v=spf1 include:spf.protection.outlook.com -all"
    dmarc_name = f"_dmarc.{domain}"
    dmarc_value = os.environ.get("EMAIL_ALIAS_FABRIC_DMARC_REPLY", "").strip() or "v=DMARC1; p=quarantine; adkim=r; aspf=r; pct=100"

    has_any_spf = any("v=spf1" in str(v).lower() for v in summary.get("txt_values", []))
    has_dmarc = bool(dmarc_before.get("has_dmarc"))
    has_mx_target = mx_target.lower() in set(summary.get("mx_targets", []))

    if allow_mutation:
        if force or (not has_any_spf):
            operations.append({"step": "spf_upsert", "result": cloudflare_upsert_txt_spf(domain, spf_value, ttl)})
        elif not summary.get("has_spf_o365"):
            operations.append(
                {
                    "step": "spf_preserved_non_o365",
                    "result": {"ok": True, "status": "skipped_existing_non_o365_spf", "requires_force": True},
                }
            )

        if force or (not has_dmarc):
            operations.append({"step": "dmarc_upsert", "result": cloudflare_upsert_txt_exact(dmarc_name, dmarc_value, ttl)})

        if force or (not has_mx_target and int(summary.get("mx_count", 0)) == 0):
            operations.append({"step": "mx_upsert", "result": cloudflare_upsert_mx(domain, target=mx_target, ttl=ttl, priority=0)})
        elif not has_mx_target and int(summary.get("mx_count", 0)) > 0:
            operations.append(
                {
                    "step": "mx_preserved_existing",
                    "result": {"ok": True, "status": "skipped_existing_mx", "requires_force": True, "mx_targets": summary.get("mx_targets", [])},
                }
            )
    else:
        operations.append({"step": "preview_only", "result": {"ok": True, "status": "dry_run"}})

    final_summary = cloudflare_domain_dns_summary(domain)
    dmarc_after = cloudflare_dmarc_summary(domain)
    ok = bool(final_summary.get("ok")) and bool(final_summary.get("has_spf_o365")) and bool(dmarc_after.get("has_dmarc"))
    return {
        "ok": ok,
        "domain": domain,
        "mx_target": mx_target,
        "operations": operations,
        "before": summary,
        "before_dmarc": dmarc_before,
        "after": final_summary,
        "after_dmarc": dmarc_after,
    }


def stack_audit(mailbox: str, domain: str, default_domain: str) -> dict[str, Any]:
    domain = normalize_domain(domain) or default_domain
    graph_perm = graph_permissions_audit(include_assignments=False)
    exchange_auth = exchange_service_principal_authorization(default_domain)
    cf = cloudflare_token_audit()
    accepted = exchange_get_accepted_domains(default_domain)
    aliases = exchange_get_mailbox_aliases(default_domain, mailbox)
    dns = cloudflare_domain_dns_summary(domain)
    dmarc = cloudflare_dmarc_summary(domain)
    accepted_ok = bool(accepted.get("ok")) and domain in set(accepted.get("domains", []))
    return {
        "ok": bool(graph_perm.get("ok")) and bool(cf.get("ok")) and bool(accepted.get("ok")),
        "service": "m365-cloudflare-stack-audit",
        "updated_at_utc": now_utc(),
        "mailbox": mailbox,
        "domain": domain,
        "credentials": {
            "graph_permissions": graph_perm,
            "exchange_authorization": exchange_auth,
            "cloudflare": cf,
        },
        "mail_plane": {
            "accepted_domains": accepted.get("domains", []),
            "accepted_domain_ready": accepted_ok,
            "mailbox_aliases": aliases.get("aliases", []),
            "dns_summary": dns,
            "dmarc_summary": dmarc,
        },
    }


def stack_optimize(mailbox: str, domain: str, default_domain: str, force: bool, ttl: int, dry_run: bool) -> dict[str, Any]:
    domain = normalize_domain(domain) or default_domain
    ensured = ensure_domain_accepted(domain, default_domain, auto_domain=True, allow_mutation=(not dry_run))
    root_dns = ensure_root_domain_dns(domain, default_domain=default_domain, ttl=ttl, force=force, allow_mutation=(not dry_run))
    auth = exchange_service_principal_authorization(default_domain)
    graph_perm = graph_permissions_audit(include_assignments=False)
    cloudflare_audit = cloudflare_token_audit()
    return {
        "ok": bool(ensured.get("ok")) and bool(root_dns.get("ok")) and bool(graph_perm.get("ok")),
        "status": "dry_run" if dry_run else "live",
        "mailbox": mailbox,
        "domain": domain,
        "force": force,
        "ttl": ttl,
        "domain_plane": ensured,
        "dns_plane": root_dns,
        "credential_plane": {
            "graph_permissions": graph_perm,
            "exchange_authorization": auth,
            "cloudflare": cloudflare_audit,
        },
        "updated_at_utc": now_utc(),
    }


def verify_lane(mailbox: str, alias_email: str, domain: str, no_reply: bool, default_domain: str) -> dict[str, Any]:
    accepted = exchange_get_accepted_domains(default_domain)
    aliases = exchange_get_mailbox_aliases(default_domain, mailbox)
    graph_email = graph_domain_email_enabled(domain, retries=4, delay_seconds=2)
    dns = cloudflare_domain_dns_summary(domain)

    accepted_ok = bool(accepted.get("ok")) and domain in set(accepted.get("domains", []))
    alias_ok = bool(aliases.get("ok")) and alias_email.lower() in set(aliases.get("aliases", []))
    graph_ok = bool(graph_email.get("ok"))

    dns_ok = bool(dns.get("ok"))
    if dns_ok:
        if no_reply:
            dns_ok = bool(dns.get("has_spf_fail_all")) and int(dns.get("mx_count", 0)) == 0
        else:
            dns_ok = bool(dns.get("has_spf_o365")) and int(dns.get("mx_count", 0)) > 0

    checks = {
        "accepted_domain": accepted_ok,
        "alias_attached": alias_ok,
        "graph_email_service": graph_ok,
        "dns_profile": dns_ok,
    }
    issues = [k for (k, v) in checks.items() if not v]
    return {
        "ok": len(issues) == 0,
        "checks": checks,
        "issues": issues,
        "accepted_domains": accepted.get("domains", []),
        "mailbox_aliases": aliases.get("aliases", []),
        "graph_email_state": graph_email,
        "dns_state": dns,
    }


def send_probe(from_alias: str, mailbox: str, to_email: str, subject: str, body: str) -> dict[str, Any]:
    if not ENTRA_EXCHANGE_SCRIPT.exists():
        return {"ok": False, "error": f"missing {ENTRA_EXCHANGE_SCRIPT}"}
    cmd = [
        str(ENTRA_EXCHANGE_SCRIPT),
        "send",
        "--from",
        from_alias,
        "--mailbox",
        mailbox,
        "--to",
        to_email,
        "--subject",
        subject,
        "--body",
        body,
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False, timeout=180)
    return {
        "ok": proc.returncode == 0,
        "code": proc.returncode,
        "stdout": (proc.stdout or "").strip(),
        "stderr": (proc.stderr or "").strip(),
        "cmd": cmd,
    }


def provision_lane(mailbox: str, local_part: str, domain: str, no_reply: bool, ttl: int, send_to: str) -> dict[str, Any]:
    default_domain = base_domain(mailbox)
    alias_email = render_alias(local_part, domain)
    intent = {
        "delegate": "email-alias-manager",
        "action": (
            f"create alias local:{local_part} domain:{domain} mailbox:{mailbox} "
            f"no_reply:{str(no_reply).lower()} ensure_dns:true auto_domain:true ttl:{ttl}"
        ),
    }
    create_result = execute_intent(intent, dry_run=False)
    verify = verify_lane(mailbox=mailbox, alias_email=alias_email, domain=domain, no_reply=no_reply, default_domain=default_domain)

    probe = {"ok": False, "skipped": True}
    if send_to:
        token = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        mode = "no-reply" if no_reply else "reply-capable"
        subject = f"Lane probe {mode} {token}"
        body = f"Alias lane probe from {alias_email} ({mode}) token {token}"
        probe = send_probe(alias_email, mailbox=mailbox, to_email=send_to, subject=subject, body=body)
        probe["token"] = token
        probe["subject"] = subject

    return {
        "ok": bool(create_result.get("ok")) and bool(verify.get("ok")),
        "status": "live" if bool(create_result.get("ok")) and bool(verify.get("ok")) else "failed",
        "mailbox": mailbox,
        "alias_email": alias_email,
        "domain": domain,
        "no_reply": no_reply,
        "create_result": create_result,
        "verify_result": verify,
        "probe_result": probe,
        "updated_at_utc": now_utc(),
    }


def awareness_snapshot(mailbox: str, domains: list[str] | None = None) -> dict[str, Any]:
    mailbox = (mailbox or "").strip().lower() or os.environ.get("EXCHANGE_DEFAULT_MAILBOX", "").strip().lower() or "john@northorizon.ca"
    default_domain = base_domain(mailbox)
    aliases = exchange_get_mailbox_aliases(default_domain, mailbox)
    accepted = exchange_get_accepted_domains(default_domain)
    graph_domains = list_domains_graph()
    registry = registry_read()

    domain_set: set[str] = set()
    if domains:
        for d in domains:
            nd = normalize_domain(str(d))
            if nd:
                domain_set.add(nd)
    if not domain_set:
        for a in aliases.get("aliases", []):
            if "@" in a:
                domain_set.add(a.split("@", 1)[1].lower())
        for d in accepted.get("domains", []):
            if isinstance(d, str) and d.endswith(default_domain):
                domain_set.add(d)
        domain_set.add(default_domain)

    domain_views: list[dict[str, Any]] = []
    for d in sorted(domain_set):
        g = graph_get_domain(d)
        dns = cloudflare_domain_dns_summary(d)
        domain_views.append(
            {
                "domain": d,
                "graph": g.get("domain") if g.get("ok") else {"error": g.get("error")},
                "dns": dns,
                "accepted_in_exchange": d in set(accepted.get("domains", [])),
            }
        )

    return {
        "ok": bool(aliases.get("ok")) and bool(accepted.get("ok")) and bool(graph_domains.get("ok")),
        "service": "email-alias-fabric-ops",
        "updated_at_utc": now_utc(),
        "mailbox": mailbox,
        "default_domain": default_domain,
        "mailbox_aliases": aliases.get("aliases", []),
        "accepted_domains": accepted.get("domains", []),
        "graph_domains": graph_domains.get("domains", []),
        "domain_views": domain_views,
        "registry_entries": registry.get("entries", []),
        "errors": {
            "aliases": aliases.get("error"),
            "accepted_domains": accepted.get("error"),
            "graph_domains": graph_domains.get("error"),
        },
    }


def graph_delete_domain(domain: str) -> dict[str, Any]:
    return graph_request("DELETE", f"/v1.0/domains/{urllib.parse.quote(domain)}")


def dns_upsert_generic(record_type: str, name: str, content: str, ttl: int, priority: int = 0, proxied: bool = False) -> dict[str, Any]:
    rtype = record_type.upper().strip()
    listed = cloudflare_list_records(name, rtype)
    if not listed.get("ok"):
        return {"ok": False, "error": listed.get("error")}
    rows = listed.get("rows", [])
    rec_id = str((rows[0] or {}).get("id") or "").strip() if rows else ""
    payload: dict[str, Any] = {"type": rtype, "name": name, "content": content, "ttl": int(ttl)}
    if rtype == "MX":
        payload["priority"] = int(priority)
    if rtype in {"A", "AAAA", "CNAME", "TXT"}:
        payload["proxied"] = bool(proxied)
    if rec_id:
        out = cloudflare_request("PUT", f"/dns_records/{rec_id}", payload)
    else:
        out = cloudflare_request("POST", "/dns_records", payload)
    return {"ok": bool(out.get("success")), "record_id": rec_id or ((out.get("result") or {}).get("id")), "result": out}


def execute_control_op(op: dict[str, Any], dry_run: bool, default_mailbox: str, default_domain: str) -> dict[str, Any]:
    action = str(op.get("action") or "").strip().lower()
    mailbox = str(op.get("mailbox") or default_mailbox).strip().lower()

    if not action:
        return {"ok": False, "error": "missing action"}

    if action == "awareness.snapshot":
        domains = op.get("domains")
        if not isinstance(domains, list):
            domains = []
        return awareness_snapshot(mailbox=mailbox, domains=[str(x) for x in domains])

    if action == "alias.list":
        return execute_list({"mailbox": mailbox}, default_domain=default_domain)

    if action in {"alias.add", "alias.remove"}:
        email = str(op.get("email") or "").strip().lower()
        if not email:
            local = normalize_local(str(op.get("local") or ""))
            domain = normalize_domain(str(op.get("domain") or ""))
            if local and domain:
                email = f"{local}@{domain}"
        if not email or not EMAIL_RE.fullmatch(email):
            return {"ok": False, "error": "alias.add/remove requires valid email or local+domain"}
        if dry_run:
            return {"ok": True, "status": "dry_run", "action": action, "email": email, "mailbox": mailbox}
        if action == "alias.add":
            res = exchange_set_alias(default_domain, mailbox, email, mode="add")
            return {"ok": bool(res.get("ok")), "action": action, "mailbox": mailbox, "email": email, "result": res}
        preserve_reply = bool(op.get("preserve_reply", False))
        fallback_mailbox = str(op.get("fallback_mailbox") or op.get("fallback") or mailbox).strip().lower()
        if preserve_reply:
            res = retire_alias_with_fallback(
                default_domain=default_domain,
                source_mailbox=mailbox,
                alias_email=email,
                fallback_mailbox=fallback_mailbox,
                dry_run=False,
            )
            return {"ok": bool(res.get("ok")), "action": "alias.retire", "mailbox": mailbox, "email": email, "result": res}
        res = exchange_set_alias(default_domain, mailbox, email, mode="remove")
        return {"ok": bool(res.get("ok")), "action": action, "mailbox": mailbox, "email": email, "result": res}

    if action == "domain.accepted.list":
        return exchange_get_accepted_domains(default_domain)

    if action in {"domain.accepted.add", "domain.accepted.remove"}:
        domain = normalize_domain(str(op.get("domain") or ""))
        if not domain:
            return {"ok": False, "error": "domain.accepted.add/remove requires domain"}
        if dry_run:
            return {"ok": True, "status": "dry_run", "action": action, "domain": domain}
        if action.endswith(".add"):
            return exchange_add_accepted_domain(default_domain, domain)
        return exchange_remove_accepted_domain(default_domain, domain)

    if action in {"domain.graph.get", "domain.graph.create", "domain.graph.promote", "domain.graph.delete", "domain.ensure.email"}:
        domain = normalize_domain(str(op.get("domain") or ""))
        if not domain:
            return {"ok": False, "error": f"{action} requires domain"}
        if action == "domain.graph.get":
            return graph_get_domain(domain)
        if dry_run and action != "domain.graph.get":
            return {"ok": True, "status": "dry_run", "action": action, "domain": domain}
        if action == "domain.graph.create":
            return graph_create_domain(domain)
        if action == "domain.graph.promote":
            return graph_promote_domain(domain)
        if action == "domain.graph.delete":
            return graph_delete_domain(domain)
        # ensure email
        ensured = ensure_domain_accepted(domain, default_domain, auto_domain=True, allow_mutation=True)
        email_ready = graph_domain_email_enabled(domain, retries=10, delay_seconds=3)
        return {"ok": bool(ensured.get("ok")) and bool(email_ready.get("ok")), "ensure_domain": ensured, "graph_email": email_ready}

    if action in {"dns.list", "dns.upsert", "dns.delete"}:
        name = normalize_dns_name(str(op.get("name") or "")) or normalize_domain(str(op.get("domain") or ""))
        if not name:
            return {"ok": False, "error": f"{action} requires name/domain"}
        if action == "dns.list":
            rtype = str(op.get("type") or "").strip().upper()
            if rtype:
                return cloudflare_list_records(name, rtype)
            return cloudflare_domain_dns_summary(name)
        if dry_run:
            return {"ok": True, "status": "dry_run", "action": action, "name": name}
        if action == "dns.delete":
            rtype = str(op.get("type") or "").strip().upper()
            if not rtype:
                return {"ok": False, "error": "dns.delete requires type"}
            return cloudflare_delete_records(name, rtype)
        # dns.upsert
        rtype = str(op.get("type") or "").strip().upper()
        content = str(op.get("content") or "").strip()
        ttl = int(op.get("ttl") or 300)
        priority = int(op.get("priority") or 0)
        proxied = bool(op.get("proxied")) if "proxied" in op else False
        if not rtype or not content:
            return {"ok": False, "error": "dns.upsert requires type+content"}
        return dns_upsert_generic(rtype, name=name, content=content, ttl=ttl, priority=priority, proxied=proxied)

    if action == "stack.audit":
        domain = normalize_domain(str(op.get("domain") or default_domain)) or default_domain
        return stack_audit(mailbox=mailbox, domain=domain, default_domain=default_domain)

    if action == "stack.optimize":
        domain = normalize_domain(str(op.get("domain") or default_domain)) or default_domain
        force = bool(op.get("force", False))
        ttl = int(op.get("ttl") or 300)
        ttl = max(120, min(ttl, 86400))
        return stack_optimize(mailbox=mailbox, domain=domain, default_domain=default_domain, force=force, ttl=ttl, dry_run=dry_run)

    if action == "lane.verify":
        alias_email = str(op.get("alias_email") or op.get("email") or "").strip().lower()
        domain = normalize_domain(str(op.get("domain") or ""))
        no_reply = bool(op.get("no_reply", False))
        if not alias_email and domain:
            local = normalize_local(str(op.get("local") or ""))
            if local:
                alias_email = f"{local}@{domain}"
        if not alias_email or not domain:
            return {"ok": False, "error": "lane.verify requires alias_email/email and domain"}
        return verify_lane(mailbox=mailbox, alias_email=alias_email, domain=domain, no_reply=no_reply, default_domain=default_domain)

    if action == "lane.provision":
        local = normalize_local(str(op.get("local") or "support")) or "support"
        domain = normalize_domain(str(op.get("domain") or ""))
        ttl = int(op.get("ttl") or 300)
        no_reply = bool(op.get("no_reply", False))
        send_to = str(op.get("send_to") or "").strip()
        if not domain:
            return {"ok": False, "error": "lane.provision requires domain"}
        if dry_run:
            return {"ok": True, "status": "dry_run", "mailbox": mailbox, "local": local, "domain": domain, "no_reply": no_reply}
        return provision_lane(mailbox=mailbox, local_part=local, domain=domain, no_reply=no_reply, ttl=ttl, send_to=send_to)

    if action == "lane.retire":
        alias_email = str(op.get("alias_email") or op.get("email") or "").strip().lower()
        domain = normalize_domain(str(op.get("domain") or ""))
        local = normalize_local(str(op.get("local") or ""))
        fallback_mailbox = str(op.get("fallback_mailbox") or op.get("fallback") or mailbox).strip().lower()
        if not alias_email and local and domain:
            alias_email = f"{local}@{domain}"
        if not alias_email or not EMAIL_RE.fullmatch(alias_email):
            return {"ok": False, "error": "lane.retire requires alias_email/email or local+domain"}
        return retire_alias_with_fallback(
            default_domain=default_domain,
            source_mailbox=mailbox,
            alias_email=alias_email,
            fallback_mailbox=fallback_mailbox,
            dry_run=dry_run,
        )

    if action == "send.probe":
        from_alias = str(op.get("from") or op.get("from_alias") or "").strip().lower()
        to_email = str(op.get("to") or op.get("to_email") or "").strip().lower()
        subject = str(op.get("subject") or f"Probe {now_utc()}").strip()
        body = str(op.get("body") or f"Probe from {from_alias}").strip()
        if not from_alias or not to_email:
            return {"ok": False, "error": "send.probe requires from/from_alias and to/to_email"}
        if dry_run:
            return {"ok": True, "status": "dry_run", "from": from_alias, "to": to_email, "subject": subject}
        return send_probe(from_alias=from_alias, mailbox=mailbox, to_email=to_email, subject=subject, body=body)

    return {"ok": False, "error": f"unsupported action: {action}"}


def execute_control(ops: list[dict[str, Any]], dry_run: bool) -> dict[str, Any]:
    default_mailbox = os.environ.get("EXCHANGE_DEFAULT_MAILBOX", "").strip().lower() or "john@northorizon.ca"
    default_domain = base_domain(default_mailbox)
    results: list[dict[str, Any]] = []
    ok_all = True
    for idx, op in enumerate(ops):
        if not isinstance(op, dict):
            row = {"ok": False, "error": "operation must be object", "index": idx}
            results.append(row)
            ok_all = False
            continue
        row = execute_control_op(op, dry_run=dry_run, default_mailbox=default_mailbox, default_domain=default_domain)
        row["index"] = idx
        row["action"] = str(op.get("action") or "")
        results.append(row)
        if not row.get("ok"):
            ok_all = False
    return {
        "ok": ok_all,
        "status": "dry_run" if dry_run else ("live" if ok_all else "failed"),
        "updated_at_utc": now_utc(),
        "results": results,
    }


def execute_intent(intent: dict[str, Any], dry_run: bool) -> dict[str, Any]:
    default_mailbox = os.environ.get("EXCHANGE_DEFAULT_MAILBOX", "").strip().lower() or "john@northorizon.ca"
    default_domain = base_domain(default_mailbox)
    parsed = parse_intent(intent, default_mailbox=default_mailbox, default_domain=default_domain)

    plan = {
        "parsed": parsed,
        "exchange_org": exchange_org(default_domain),
        "default_mailbox": default_mailbox,
        "default_domain": default_domain,
        "cloudflare_configured": bool(cloudflare_token() and cloudflare_zone_id()),
        "entra_configured": bool(
            os.environ.get("ENTRA_CLIENT_ID", "").strip()
            and os.environ.get("ENTRA_TENANT_ID", "").strip()
            and os.environ.get("ENTRA_CLIENT_SECRET", "").strip()
        ),
    }

    op = parsed["operation"]
    if op == "list":
        out = execute_list(parsed, default_domain=default_domain)
    elif op == "delete":
        out = execute_delete(parsed, dry_run=dry_run, default_domain=default_domain)
    elif op == "rotate":
        out = execute_rotate(parsed, dry_run=dry_run, default_domain=default_domain)
    elif op == "batch":
        out = execute_create_or_batch(parsed, dry_run=dry_run, default_domain=default_domain)
    else:
        out = execute_create_or_batch(parsed, dry_run=dry_run, default_domain=default_domain)

    out["plan"] = plan
    out["updated_at_utc"] = now_utc()
    return out


def self_test() -> dict[str, Any]:
    default_mailbox = os.environ.get("EXCHANGE_DEFAULT_MAILBOX", "").strip().lower() or "john@northorizon.ca"
    default_domain = base_domain(default_mailbox)
    accepted_probe = exchange_get_accepted_domains(default_domain)
    graph_probe = list_domains_graph()
    out = {
        "ok": bool(accepted_probe.get("ok")) and bool(graph_probe.get("ok")),
        "service": "email-alias-fabric-ops",
        "updated_at_utc": now_utc(),
        "default_mailbox": default_mailbox,
        "default_domain": default_domain,
        "exchange_org": exchange_org(default_domain),
        "cloudflare_configured": bool(cloudflare_token() and cloudflare_zone_id()),
        "entra_configured": bool(
            os.environ.get("ENTRA_CLIENT_ID", "").strip()
            and os.environ.get("ENTRA_TENANT_ID", "").strip()
            and os.environ.get("ENTRA_CLIENT_SECRET", "").strip()
        ),
        "accepted_domains": accepted_probe.get("domains", []),
        "graph_domains": graph_probe.get("domains", []),
        "error": accepted_probe.get("error") or graph_probe.get("error"),
    }
    return out


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Email alias fabric ops")
    sub = parser.add_subparsers(dest="command")

    run = sub.add_parser("execute-intent")
    run.add_argument("--intent-json", required=True)
    run.add_argument("--dry-run", action="store_true")

    awareness = sub.add_parser("awareness")
    awareness.add_argument("--mailbox", default="")
    awareness.add_argument("--domains-csv", default="")

    provision = sub.add_parser("provision-lane")
    provision.add_argument("--mailbox", required=True)
    provision.add_argument("--local", required=True)
    provision.add_argument("--domain", required=True)
    provision.add_argument("--no-reply", action="store_true")
    provision.add_argument("--ttl", type=int, default=300)
    provision.add_argument("--send-to", default="")

    verify = sub.add_parser("verify-lane")
    verify.add_argument("--mailbox", required=True)
    verify.add_argument("--alias-email", required=True)
    verify.add_argument("--domain", required=True)
    verify.add_argument("--no-reply", action="store_true")

    retire = sub.add_parser("retire-lane")
    retire.add_argument("--mailbox", required=True)
    retire.add_argument("--alias-email", required=True)
    retire.add_argument("--fallback-mailbox", default="")
    retire.add_argument("--dry-run", action="store_true")

    control = sub.add_parser("control-json")
    control.add_argument("--ops-json", required=True)
    control.add_argument("--dry-run", action="store_true")

    sub.add_parser("self-test")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    load_env()

    if args.command == "awareness":
        domains = [x.strip() for x in str(args.domains_csv or "").split(",") if x.strip()]
        out = awareness_snapshot(mailbox=str(args.mailbox or ""), domains=domains)
        LAST_RESULT.parent.mkdir(parents=True, exist_ok=True)
        write_json_atomic(LAST_RESULT, out, indent=2)
        print(json.dumps(out, ensure_ascii=False, sort_keys=True))
        return

    if args.command == "provision-lane":
        out = provision_lane(
            mailbox=str(args.mailbox).strip().lower(),
            local_part=str(args.local).strip(),
            domain=str(args.domain).strip().lower(),
            no_reply=bool(args.no_reply),
            ttl=int(args.ttl),
            send_to=str(args.send_to).strip(),
        )
        LAST_RESULT.parent.mkdir(parents=True, exist_ok=True)
        write_json_atomic(LAST_RESULT, out, indent=2)
        print(json.dumps(out, ensure_ascii=False, sort_keys=True))
        return

    if args.command == "verify-lane":
        default_domain = base_domain(str(args.mailbox).strip().lower())
        out = verify_lane(
            mailbox=str(args.mailbox).strip().lower(),
            alias_email=str(args.alias_email).strip().lower(),
            domain=str(args.domain).strip().lower(),
            no_reply=bool(args.no_reply),
            default_domain=default_domain,
        )
        LAST_RESULT.parent.mkdir(parents=True, exist_ok=True)
        write_json_atomic(LAST_RESULT, out, indent=2)
        print(json.dumps(out, ensure_ascii=False, sort_keys=True))
        return

    if args.command == "retire-lane":
        mailbox = str(args.mailbox).strip().lower()
        default_domain = base_domain(mailbox)
        fallback_mailbox = str(args.fallback_mailbox or mailbox).strip().lower()
        out = retire_alias_with_fallback(
            default_domain=default_domain,
            source_mailbox=mailbox,
            alias_email=str(args.alias_email).strip().lower(),
            fallback_mailbox=fallback_mailbox,
            dry_run=bool(args.dry_run),
        )
        LAST_RESULT.parent.mkdir(parents=True, exist_ok=True)
        write_json_atomic(LAST_RESULT, out, indent=2)
        print(json.dumps(out, ensure_ascii=False, sort_keys=True))
        return

    if args.command == "control-json":
        try:
            parsed = json.loads(args.ops_json)
        except Exception as exc:
            print(json.dumps({"ok": False, "error": f"invalid ops json: {exc}"}, ensure_ascii=False, sort_keys=True))
            return
        ops: list[dict[str, Any]]
        if isinstance(parsed, dict):
            ops = [parsed]
        elif isinstance(parsed, list):
            ops = [x for x in parsed if isinstance(x, dict)]
            if len(ops) != len(parsed):
                print(json.dumps({"ok": False, "error": "ops json list must contain only objects"}, ensure_ascii=False, sort_keys=True))
                return
        else:
            print(json.dumps({"ok": False, "error": "ops json must be object or list"}, ensure_ascii=False, sort_keys=True))
            return
        out = execute_control(ops, dry_run=bool(args.dry_run))
        LAST_RESULT.parent.mkdir(parents=True, exist_ok=True)
        write_json_atomic(LAST_RESULT, out, indent=2)
        print(json.dumps(out, ensure_ascii=False, sort_keys=True))
        return

    if args.command == "self-test":
        out = self_test()
        LAST_RESULT.parent.mkdir(parents=True, exist_ok=True)
        write_json_atomic(LAST_RESULT, out, indent=2)
        print(json.dumps(out, ensure_ascii=False, sort_keys=True))
        return

    if args.command != "execute-intent":
        print(json.dumps({"ok": False, "error": "missing command"}, ensure_ascii=False, sort_keys=True))
        return

    try:
        intent = json.loads(args.intent_json)
    except Exception as exc:
        print(json.dumps({"ok": False, "error": f"invalid intent json: {exc}"}, ensure_ascii=False, sort_keys=True))
        return
    if not isinstance(intent, dict):
        print(json.dumps({"ok": False, "error": "intent json must be object"}, ensure_ascii=False, sort_keys=True))
        return

    out = execute_intent(intent, dry_run=bool(args.dry_run))
    LAST_RESULT.parent.mkdir(parents=True, exist_ok=True)
    write_json_atomic(LAST_RESULT, out, indent=2)
    print(json.dumps(out, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
