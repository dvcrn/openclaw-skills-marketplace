#!/usr/bin/env python3
import argparse
import json
import os
import stat
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen


DEFAULT_CONFIG = "~/.mcporter/xiaodu-mcp-oauth.json"
LEGACY_CONFIG = "~/.mcporter/xiaodu-iot-oauth.json"
CONFIG_ENV = "XIAODU_MCP_OAUTH_CONFIG"


def resolve_path(raw: str) -> Path:
    return Path(os.path.expanduser(raw)).resolve()


def resolve_default_config_path(raw: str) -> Path:
    if raw != DEFAULT_CONFIG:
        return resolve_path(raw)

    env_raw = os.environ.get(CONFIG_ENV)
    if env_raw:
        return resolve_path(env_raw)

    path = resolve_path(raw)
    if path.exists():
        return path

    legacy_path = resolve_path(LEGACY_CONFIG)
    if legacy_path.exists():
        print(f"[xiaodu-control] 未找到默认凭据文件，回退到旧路径: {legacy_path}")
        return legacy_path

    return path


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def atomic_write_json(path: Path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=str(path.parent), delete=False) as tmp:
        json.dump(payload, tmp, ensure_ascii=False, indent=2)
        tmp.write("\n")
        temp_name = tmp.name
    os.replace(temp_name, path)


def mask_token(token: str) -> str:
    if len(token) <= 12:
        return token
    return f"{token[:6]}...{token[-6:]}"


def parse_iso_datetime(raw: str):
    if not raw:
        return None
    normalized = raw.replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(normalized)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def should_refresh(config: dict, within_days: int | None, force: bool):
    if force or within_days is None:
        return True

    last_refresh = config.get("last_refresh", {})
    expires_at = parse_iso_datetime(last_refresh.get("expires_at", ""))
    if expires_at is None:
        print("[xiaodu-control] 未找到 expires_at，执行刷新")
        return True

    now = datetime.now(timezone.utc)
    remaining = expires_at - now
    threshold = timedelta(days=within_days)
    if remaining <= threshold:
        print(f"[xiaodu-control] token 剩余有效期 {remaining}，已进入 {within_days} 天窗口，执行刷新")
        return True

    print(f"[xiaodu-control] token 仍有 {remaining} 有效期，未进入 {within_days} 天窗口，本次跳过刷新")
    return False


def fetch_refreshed_token(config: dict):
    params = {
        "grant_type": "refresh_token",
        "refresh_token": config["refresh_token"],
        "client_id": config["client_id"],
        "client_secret": config["client_secret"],
    }
    url = f'{config.get("token_endpoint", "https://openapi.baidu.com/oauth/2.0/token")}?{urlencode(params)}'
    request = Request(url, headers={"User-Agent": "xiaodu-control/refresh-token"})
    with urlopen(request, timeout=30) as response:
        data = json.loads(response.read().decode("utf-8"))

    if "access_token" in data:
        return data

    wrapped = data.get("data")
    if isinstance(wrapped, dict) and "access_token" in wrapped:
        return wrapped

    raise RuntimeError(f"刷新 token 失败，返回内容无法识别: {data}")


def update_mcporter_config(config: dict, new_access_token: str):
    mcporter_path = resolve_path(config["mcporter_config"])
    mcporter = load_json(mcporter_path)
    servers = mcporter.setdefault("mcpServers", {})
    targets = config.get("targets") or []
    if not targets:
        raise RuntimeError("凭据配置里缺少 targets，无法回写 mcporter 配置")

    updated = []
    for target in targets:
        server_name = target["server"]
        container = target.get("container", "env")
        key = target.get("key", "ACCESS_TOKEN")
        entry = servers.get(server_name)
        if not isinstance(entry, dict):
            raise RuntimeError(f"mcporter 配置中不存在 server: {server_name}")
        bucket = entry.setdefault(container, {})
        if not isinstance(bucket, dict):
            raise RuntimeError(f"{server_name}.{container} 不是对象，无法写入 token")
        bucket[key] = new_access_token
        updated.append(f"{server_name}.{container}.{key}")

    atomic_write_json(mcporter_path, mcporter)
    try:
        os.chmod(mcporter_path, stat.S_IRUSR | stat.S_IWUSR)
    except OSError:
        pass
    return mcporter_path, updated


def update_credentials_file(path: Path, config: dict, token_payload: dict):
    refreshed_at = datetime.now(timezone.utc)
    expires_in = int(token_payload.get("expires_in", 0) or 0)
    expires_at = refreshed_at + timedelta(seconds=expires_in) if expires_in > 0 else None

    config["refresh_token"] = token_payload.get("refresh_token", config["refresh_token"])
    config["current_access_token"] = token_payload["access_token"]
    config["scope"] = token_payload.get("scope", config.get("scope", ""))
    config["last_refresh"] = {
        "refreshed_at": refreshed_at.isoformat(),
        "expires_in": expires_in,
        "expires_at": expires_at.isoformat() if expires_at else "",
        "access_token_preview": mask_token(token_payload["access_token"]),
        "refresh_token_preview": mask_token(config["refresh_token"]),
    }
    atomic_write_json(path, config)
    try:
        os.chmod(path, stat.S_IRUSR | stat.S_IWUSR)
    except OSError:
        pass


def mirror_compat_credentials_file(active_path: Path, config: dict):
    default_path = resolve_path(DEFAULT_CONFIG)
    legacy_path = resolve_path(LEGACY_CONFIG)

    candidates = []
    if active_path == default_path and legacy_path.exists():
        candidates.append(legacy_path)
    if active_path == legacy_path and default_path.exists():
        candidates.append(default_path)

    mirrored = []
    for path in candidates:
        atomic_write_json(path, config)
        try:
            os.chmod(path, stat.S_IRUSR | stat.S_IWUSR)
        except OSError:
            pass
        mirrored.append(path)

    return mirrored


def main():
    parser = argparse.ArgumentParser(description="刷新小度 MCP 平台 ACCESS_TOKEN 并回写 mcporter 配置")
    parser.add_argument(
        "--config",
        default=DEFAULT_CONFIG,
        help="凭据配置文件路径",
    )
    parser.add_argument(
        "--refresh-if-within-days",
        type=int,
        default=None,
        help="仅当 token 在 N 天内过期时才刷新",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="忽略有效期窗口，强制刷新",
    )
    args = parser.parse_args()

    config_path = resolve_default_config_path(args.config)
    if not config_path.exists():
        raise SystemExit(f"未找到凭据配置文件: {config_path}")

    config = load_json(config_path)
    if not should_refresh(config, args.refresh_if_within_days, args.force):
        return

    token_payload = fetch_refreshed_token(config)
    access_token = token_payload["access_token"]

    print("[xiaodu-control] token 刷新成功")
    print(f"[xiaodu-control] 新 access_token 预览: {mask_token(access_token)}")
    print(f"[xiaodu-control] 新 refresh_token 预览: {mask_token(token_payload.get('refresh_token', config['refresh_token']))}")
    print(f"[xiaodu-control] expires_in: {token_payload.get('expires_in', '')}")

    mcporter_path, updated_paths = update_mcporter_config(config, access_token)
    update_credentials_file(config_path, config, token_payload)
    mirrored_paths = mirror_compat_credentials_file(config_path, config)

    print(f"[xiaodu-control] 已更新 mcporter 配置: {mcporter_path}")
    print("[xiaodu-control] 已回写字段:")
    for item in updated_paths:
        print(f"  - {item}")
    print(f"[xiaodu-control] 已更新凭据文件: {config_path}")
    for path in mirrored_paths:
        print(f"[xiaodu-control] 已同步兼容凭据文件: {path}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"[xiaodu-control] 刷新失败: {exc}", file=sys.stderr)
        raise SystemExit(1)
