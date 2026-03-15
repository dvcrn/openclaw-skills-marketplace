#!/usr/bin/env python3
import argparse
import datetime as dt
import json
import os
import shutil
import socket
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

DEFAULT_AUTH_PATH = str(Path.home() / ".openclaw" / "agents" / "main" / "agent" / "auth-profiles.json")
DEFAULT_ENDPOINT = "https://chatgpt.com/backend-api/wham/usage"
ALLOWED_ENDPOINT_HOSTS = {"chatgpt.com"}


def fmt_ts(ms):
    if not ms:
        return "n/a"
    try:
        return dt.datetime.fromtimestamp(ms / 1000, tz=dt.timezone.utc).isoformat()
    except Exception:
        return "n/a"


def fmt_expiry(raw):
    if not raw:
        return "n/a"
    ts = float(raw)
    if ts > 10_000_000_000:
        ts = ts / 1000.0
    now = dt.datetime.now(dt.timezone.utc)
    exp = dt.datetime.fromtimestamp(ts, tz=dt.timezone.utc)
    delta = exp - now
    sign = "-" if delta.total_seconds() < 0 else "+"
    mins = int(abs(delta.total_seconds()) // 60)
    return f"{exp.isoformat()} ({sign}{mins}m)"


def load_store(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_store(path, store):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(p.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(store, f, indent=2)
        f.write("\n")
    os.replace(tmp, p)


def backup_store(path):
    p = Path(path)
    if not p.exists():
        return None
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup_path = p.with_name(f"{p.name}.bak.delete-{stamp}")
    shutil.copy2(p, backup_path)
    return str(backup_path)


def list_codex_profiles(store):
    profiles = store.get("profiles", {})
    ids = []
    for pid, cred in profiles.items():
        if cred.get("provider") == "openai-codex":
            ids.append(pid)
    return sorted(ids)


def resolve_targets(store, selector):
    codex_ids = list_codex_profiles(store)
    if not codex_ids:
        return []

    selector = (selector or "all").strip()
    if selector in ("all", "both"):
        return codex_ids

    if selector == "default":
        if "openai-codex:default" in codex_ids:
            return ["openai-codex:default"]
        return [codex_ids[0]]

    if selector in codex_ids:
        return [selector]

    if not selector.startswith("openai-codex:"):
        expanded = f"openai-codex:{selector}"
        if expanded in codex_ids:
            return [expanded]

    return []


def detach_targets(store, targets):
    targets = sorted(set(targets or []))
    profiles = store.get("profiles", {})

    order = store.setdefault("order", {})
    codex_order = order.get("openai-codex", []) or []
    codex_order = [pid for pid in codex_order if pid not in set(targets)]
    order["openai-codex"] = codex_order

    last_good = store.setdefault("lastGood", {})
    if last_good.get("openai-codex") in set(targets):
        last_good["openai-codex"] = codex_order[0] if codex_order else None

    detached = [pid for pid in targets if pid in profiles]
    store["order"] = order
    store["lastGood"] = last_good

    return {
        "detached": detached,
        "remaining": list_codex_profiles(store),
        "order": codex_order,
        "lastGood": last_good.get("openai-codex"),
    }


def hard_delete_targets(store, targets):
    targets = sorted(set(targets or []))
    profiles = store.get("profiles", {})
    usage_stats = store.get("usageStats", {})

    deleted = []
    for pid in targets:
        if pid in profiles:
            profiles.pop(pid, None)
            deleted.append(pid)
        usage_stats.pop(pid, None)

    detach_result = detach_targets(store, targets)
    store["profiles"] = profiles
    store["usageStats"] = usage_stats

    return {
        "deleted": deleted,
        "remaining": detach_result["remaining"],
        "order": detach_result["order"],
        "lastGood": detach_result["lastGood"],
    }


def validate_endpoint(raw_endpoint):
    endpoint = (raw_endpoint or "").strip() or DEFAULT_ENDPOINT
    parsed = urllib.parse.urlparse(endpoint)
    if parsed.scheme.lower() != "https":
        return DEFAULT_ENDPOINT, False, "endpoint_forced_to_default_non_https"
    host = (parsed.hostname or "").lower()
    if host not in ALLOWED_ENDPOINT_HOSTS:
        return DEFAULT_ENDPOINT, False, "endpoint_forced_to_default_untrusted_host"
    return endpoint, True, None


def endpoint_reachable(endpoint, timeout_sec=6):
    """Return True when host/path is reachable over HTTPS, even if auth is rejected.

    This preflight is network reachability only; 401/403 should still be considered
    reachable so the main usage call can classify auth behavior precisely.
    """
    req = urllib.request.Request(endpoint, method="HEAD", headers={"User-Agent": "CodexBar"})
    try:
        with urllib.request.urlopen(req, timeout=timeout_sec):
            return True
    except urllib.error.HTTPError as e:
        # Host/path reachable; endpoint answered with HTTP status.
        return True
    except Exception:
        return False


def call_remote_usage(endpoint, token, account_id=None, timeout_sec=20, retries=1):
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "User-Agent": "CodexBar",
    }
    if account_id:
        headers["ChatGPT-Account-Id"] = str(account_id)

    last_err = None
    for attempt in range(1, retries + 2):
        start = time.time()
        req = urllib.request.Request(endpoint, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
                body = resp.read().decode("utf-8", errors="replace")
                elapsed_ms = int((time.time() - start) * 1000)
                parse_error = False
                try:
                    payload = json.loads(body)
                except Exception:
                    payload = {}
                    parse_error = True
                return {
                    "ok": True,
                    "status": int(resp.status),
                    "payload": payload,
                    "attempt": attempt,
                    "elapsed_ms": elapsed_ms,
                    "parse_error": parse_error,
                }
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")
            elapsed_ms = int((time.time() - start) * 1000)
            try:
                payload = json.loads(body)
            except Exception:
                payload = {}
            if e.code >= 500 and attempt <= retries + 1:
                last_err = {
                    "ok": False,
                    "status": int(e.code),
                    "error": "server_error",
                    "payload": payload,
                    "attempt": attempt,
                    "elapsed_ms": elapsed_ms,
                }
                time.sleep(min(1.5 * attempt, 4))
                continue
            err_type = "http_error"
            if int(e.code) == 401:
                err_type = "auth_not_accepted_by_usage_endpoint"
            elif int(e.code) == 403:
                err_type = "forbidden_by_usage_endpoint"
            return {
                "ok": False,
                "status": int(e.code),
                "error": err_type,
                "payload": payload,
                "attempt": attempt,
                "elapsed_ms": elapsed_ms,
            }
        except socket.timeout:
            elapsed_ms = int((time.time() - start) * 1000)
            last_err = {
                "ok": False,
                "status": None,
                "error": "timeout",
                "attempt": attempt,
                "elapsed_ms": elapsed_ms,
            }
            if attempt <= retries + 1:
                time.sleep(min(1.5 * attempt, 4))
                continue
        except Exception as e:
            elapsed_ms = int((time.time() - start) * 1000)
            last_err = {
                "ok": False,
                "status": None,
                "error": "request_exception",
                "message": str(e),
                "attempt": attempt,
                "elapsed_ms": elapsed_ms,
            }
            if attempt <= retries + 1:
                time.sleep(min(1.5 * attempt, 4))
                continue

    return last_err or {"ok": False, "error": "unknown"}


def format_reset_in(seconds):
    if not isinstance(seconds, (int, float)):
        return "n/a"
    total = int(max(0, seconds))
    if total < 3600:
        mins = max(1, total // 60)
        return f"{mins} minutes"
    hours = total // 3600
    mins = (total % 3600) // 60
    if mins == 0:
        return f"{hours}h"
    return f"{hours}h {mins}m"


def format_reset_at(ts):
    if not isinstance(ts, (int, float)):
        return "n/a"
    d = dt.datetime.fromtimestamp(ts, tz=dt.timezone.utc).astimezone()
    return d.strftime("%d/%m/%Y, %H:%M")


def format_duration_dhm(seconds):
    if not isinstance(seconds, (int, float)):
        return "n/a"
    total = int(max(0, seconds))
    days = total // 86400
    hours = (total % 86400) // 3600
    minutes = (total % 3600) // 60
    return f"{days} Days, {hours} Hours, {minutes} Minutes"


def format_pct(value):
    if not isinstance(value, (int, float)):
        return "n/a"
    return f"{int(round(float(value)))}% left"


def format_bool_icon(flag):
    return "✅" if bool(flag) else "❌"


def parse_codex_usage(payload):
    rl = (payload or {}).get("rate_limit") or {}
    pw = rl.get("primary_window") or {}
    sw = rl.get("secondary_window") or {}

    def win(obj, fallback_label):
        if not obj:
            return None
        secs = obj.get("limit_window_seconds")
        reset = obj.get("reset_at")
        reset_after = obj.get("reset_after_seconds")
        label = fallback_label
        try:
            if isinstance(secs, (int, float)) and secs > 0:
                hours = round(float(secs) / 3600)
                label = f"{hours}h" if hours < 24 else ("Week" if hours >= 168 else "Day")
        except Exception:
            pass
        used = obj.get("used_percent")
        remaining = None
        if isinstance(used, (int, float)):
            remaining = max(0, 100 - float(used))
        return {
            "label": label,
            "used_percent": used,
            "remaining_percent": remaining,
            "reset_in": format_reset_in(reset_after),
            "reset_at": format_reset_at(reset),
            "reset_after_seconds": reset_after,
        }

    windows = []
    p = win(pw, "5h")
    s = win(sw, "Week")
    if p:
        windows.append(p)
    if s:
        windows.append(s)

    plan = payload.get("plan_type") if isinstance(payload, dict) else None
    credits = None
    try:
        bal = payload.get("credits", {}).get("balance")
        if bal is not None:
            credits = float(bal)
    except Exception:
        credits = None

    return {
        "plan": plan,
        "credits_balance": credits,
        "allowed": rl.get("allowed"),
        "limit_reached": rl.get("limit_reached"),
        "windows": windows,
    }


def build_template_line(profile_report):
    remote = profile_report.get("remote_usage") or {}
    windows = remote.get("windows") or []

    five_hour = {"remaining": "n/a", "reset_at": "n/a", "time_left": "n/a"}
    week = {"remaining": "n/a", "reset_at": "n/a", "time_left": "n/a"}

    for w in windows:
        label = str(w.get("label") or "").lower()
        row = {
            "remaining": format_pct(w.get("remaining_percent")),
            "reset_at": w.get("reset_at") or "n/a",
            "time_left": format_duration_dhm(w.get("reset_after_seconds")),
        }
        if label in {"5h", "5", "5-hour", "5 hours"}:
            five_hour = row
        elif "week" in label or label in {"7d", "168h"}:
            week = row

    usable = remote.get("allowed")
    limited = remote.get("limit_reached")

    if usable is None:
        usable = bool(profile_report.get("remote_usage_ok"))
    if limited is None:
        limited = False

    return (
        f"Profile: {profile_report.get('profile')}\n"
        f"  Usable: {format_bool_icon(usable)}\n"
        f"  Limited: {format_bool_icon(limited)}\n"
        f"  5h Left: {five_hour['remaining']}\n"
        f"  5h Reset: {five_hour['reset_at']}\n"
        f"  5h Time left: {five_hour['time_left']}\n"
        f"  Week Left: {week['remaining']}\n"
        f"  Week Reset: {week['reset_at']}\n"
        f"  Week Time left: {week['time_left']}"
    )


def render_text_output(out):
    lines = []
    lines.append(out.get("progress_message") or "Running Codex usage checks now…")
    lines.append("")

    for line in out.get("formatted_profiles") or []:
        lines.append(line)
        lines.append("")

    summary = out.get("summary") or {}
    if summary:
        lines.append("")
        lines.append(
            "Summary: "
            f"checked={summary.get('profiles_checked', 0)}, "
            f"remote_ok={summary.get('remote_ok_count', 0)}, "
            f"remote_failed={summary.get('remote_failed_count', 0)}"
        )

    msg = out.get("suggested_user_message")
    if msg:
        lines.append(msg)

    return "\n".join(lines).strip() + "\n"


def scrub_sensitive(obj):
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            lk = str(k).lower()
            if lk in {"access", "refresh", "token", "authorization", "api_key", "apikey"}:
                out[k] = "[redacted]"
            else:
                out[k] = scrub_sensitive(v)
        return out
    if isinstance(obj, list):
        return [scrub_sensitive(v) for v in obj]
    return obj


def report_profile(store, profile_id, include_remote=False, endpoint=None, timeout_sec=20, retries=1, debug=False):
    profiles = store.get("profiles", {})
    usage_stats = store.get("usageStats", {})

    p = profiles.get(profile_id)
    if not p:
        return {"profile": profile_id, "status": "missing"}

    u = usage_stats.get(profile_id, {})

    result = {
        "profile": profile_id,
        "provider": p.get("provider"),
        "type": p.get("type"),
        "token_expiry": fmt_expiry(p.get("expires")),
        "last_used": fmt_ts(u.get("lastUsed")),
        "last_failure": fmt_ts(u.get("lastFailureAt")),
        "cooldown_until": fmt_ts(u.get("cooldownUntil")),
        "error_count": u.get("errorCount", 0),
        "failure_counts": u.get("failureCounts", {}),
    }

    if include_remote and endpoint:
        token = p.get("access")
        account_id = p.get("accountId")
        if token:
            remote = call_remote_usage(endpoint, token, account_id=account_id, timeout_sec=timeout_sec, retries=retries)
            result["remote_usage_ok"] = bool(remote.get("ok"))
            if remote.get("ok"):
                result["remote_usage"] = parse_codex_usage(remote.get("payload") or {})
            else:
                result["remote_error"] = remote.get("error") or "request_failed"
                if remote.get("status") is not None:
                    result["remote_status"] = remote.get("status")
                if int(remote.get("status") or 0) == 401:
                    result["remote_hint"] = (
                        "usage_endpoint_rejected_token_format_or_session; "
                        "this endpoint may require a different auth/session type than stored OAuth tokens"
                    )
            if debug:
                result["remote_debug"] = {
                    "attempt": remote.get("attempt"),
                    "elapsed_ms": remote.get("elapsed_ms"),
                    "status": remote.get("status"),
                    "endpoint": endpoint,
                }
        else:
            result["remote_usage_ok"] = False
            result["remote_error"] = "missing_access_token"

    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--profile", default="all", help="all|default|<profile-id>|<suffix>")
    ap.add_argument("--auth-path", default=DEFAULT_AUTH_PATH)
    ap.add_argument("--timeout-sec", type=int, default=20)
    ap.add_argument("--retries", type=int, default=1, help="number of retries after first attempt")
    ap.add_argument("--debug", action="store_true")
    ap.add_argument(
        "--delete-profile",
        default=None,
        help="Delete codex profile(s): all|default|<profile-id>|<suffix>",
    )
    ap.add_argument(
        "--confirm-delete",
        action="store_true",
        help="Required safeguard to perform mutation (without this flag, script only previews).",
    )
    ap.add_argument(
        "--hard-delete",
        action="store_true",
        help="Permanently delete profile+usage entries. Default is safer detach-only (keeps token/profile entry).",
    )
    ap.add_argument("--dry-run", action="store_true", help="Show delete result without writing auth file")
    ap.add_argument("--format", choices=["json", "text"], default="json", help="Output format for usage checks")
    args = ap.parse_args()

    try:
        store = load_store(args.auth_path)
    except Exception as e:
        print(json.dumps({"ok": False, "error": f"failed_to_read_auth_profiles: {e}"}))
        sys.exit(1)

    if args.delete_profile:
        delete_targets_list = resolve_targets(store, args.delete_profile)
        if not delete_targets_list:
            print(
                json.dumps(
                    {
                        "ok": False,
                        "error": "no_matching_codex_profiles_for_delete",
                        "selector": args.delete_profile,
                        "available_profiles": list_codex_profiles(store),
                        "hint": "Use --delete-profile all/default/<profile-id>/<suffix>",
                    },
                    indent=2,
                )
            )
            sys.exit(3)

        mode = "hard_delete" if args.hard_delete else "detach_only"

        # Verification safeguard: require explicit confirmation flag before mutating auth store.
        if not args.confirm_delete:
            print(
                json.dumps(
                    {
                        "ok": False,
                        "error": "delete_confirmation_required",
                        "action": "delete_profiles_preview",
                        "mode": mode,
                        "selector": args.delete_profile,
                        "would_mutate": delete_targets_list,
                        "auth_path": args.auth_path,
                        "safety_note": "Default mode is detach-only (removes from order/lastGood, keeps token/profile).",
                        "backup_note": "A timestamped backup will be created automatically before mutation.",
                        "how_to_confirm": "Re-run with --confirm-delete (optionally add --dry-run first; use --hard-delete for permanent removal).",
                    },
                    indent=2,
                )
            )
            sys.exit(4)

        if args.hard_delete:
            mutate_result = hard_delete_targets(store, delete_targets_list)
            action = "hard_delete_profiles"
        else:
            mutate_result = detach_targets(store, delete_targets_list)
            action = "detach_profiles"

        backup_path = None
        if not args.dry_run:
            backup_path = backup_store(args.auth_path)
            save_store(args.auth_path, store)

        print(
            json.dumps(
                {
                    "ok": True,
                    "action": action,
                    "mode": mode,
                    "dry_run": bool(args.dry_run),
                    "auth_path": args.auth_path,
                    "backup_path": backup_path,
                    **mutate_result,
                },
                indent=2,
            )
        )
        return

    targets = resolve_targets(store, args.profile)
    if not targets:
        print(json.dumps({
            "ok": False,
            "error": "no_matching_codex_profiles",
            "available_profiles": list_codex_profiles(store),
            "hint": "Use --profile all/default/<profile-id>/<suffix>",
        }, indent=2))
        sys.exit(2)

    raw_endpoint = os.getenv("CODEX_USAGE_ENDPOINT", DEFAULT_ENDPOINT).strip()
    endpoint, endpoint_ok, endpoint_reason = validate_endpoint(raw_endpoint)
    include_remote = endpoint_ok and endpoint_reachable(endpoint)

    reports = []
    for pid in targets:
        reports.append(
            report_profile(
                store,
                pid,
                include_remote=include_remote,
                endpoint=endpoint,
                timeout_sec=max(5, args.timeout_sec),
                retries=max(0, args.retries),
                debug=args.debug,
            )
        )

    ok_remote = sum(1 for p in reports if p.get("remote_usage_ok") is True)
    failed_remote = sum(1 for p in reports if p.get("remote_usage_ok") is False)

    out = {
        "ok": True,
        "source": "auth-profiles",
        "remote_endpoint": endpoint,
        "remote_endpoint_enabled": include_remote,
        "profiles": reports,
        "progress_message": "Running Codex usage checks now…",
        "response_template": "Profile: %name%\nUsable: ✅/❌\nLimited: ✅/❌\n5h Left: %remaining left\n5h Reset: dd/mm/yyyy, hh:mm\n5h Time left: x Days, y Hours, z Minutes\nWeek Left: %remaining left\nWeek Reset: dd/mm/yyyy, hh:mm\nWeek Time left: x Days, y Hours, z Minutes",
    }
    if endpoint_reason:
        out["remote_endpoint_note"] = endpoint_reason
    if endpoint_ok and not include_remote:
        out["remote_endpoint_note"] = "endpoint_unreachable_local_health_only"

    auth_rejects = [p.get("profile") for p in reports if int(p.get("remote_status") or 0) == 401]
    if auth_rejects:
        out["remote_auth_note"] = "usage_endpoint_rejected_available_oauth_tokens_401"
        out["remote_auth_affected_profiles"] = auth_rejects

    out["summary"] = {
        "profiles_checked": len(reports),
        "remote_ok_count": ok_remote,
        "remote_failed_count": failed_remote,
    }
    out["formatted_profiles"] = [build_template_line(r) for r in reports]

    if auth_rejects:
        out["suggested_user_message"] = (
            "Usage endpoint rejected current OAuth/session token format (401) for one or more profiles. "
            "Local profile health is still available; rotate to a healthy fallback profile."
        )
    elif failed_remote > 0 and ok_remote == 0:
        out["suggested_user_message"] = (
            "Remote usage checks are currently unavailable; showing local profile health only."
        )
    else:
        out["suggested_user_message"] = "Codex usage check completed."

    if args.format == "text":
        print(render_text_output(scrub_sensitive(out)), end="")
    else:
        print(json.dumps(scrub_sensitive(out), indent=2))


if __name__ == "__main__":
    main()
