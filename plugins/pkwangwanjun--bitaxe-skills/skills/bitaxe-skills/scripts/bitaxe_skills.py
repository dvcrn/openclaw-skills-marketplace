#!/usr/bin/env python3

from __future__ import annotations

import argparse
import concurrent.futures
import datetime as dt
import ipaddress
import json
import re
import socket
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

DEFAULT_TIMEOUT = 0.35
DEFAULT_WORKERS = 64

DOCUMENTED_SETTINGS = {
    "useFallbackStratum",
    "stratumURL",
    "fallbackStratumURL",
    "stratumUser",
    "stratumPassword",
    "fallbackStratumUser",
    "fallbackStratumPassword",
    "stratumPort",
    "fallbackStratumPort",
    "ssid",
    "wifiPass",
    "hostname",
    "coreVoltage",
    "frequency",
    "rotation",
    "overheat_mode",
    "overclockEnabled",
    "invertscreen",
    "autofanspeed",
    "fanspeed",
    "temptarget",
    "displayTimeout",
    "statsFrequency",
}

OBSERVED_NERD_SETTINGS = {
    "flipscreen",
    "autoscreenoff",
    "invertfanpolarity",
    "stratum_keep",
    "pidTargetTemp",
    "pidP",
    "pidI",
    "pidD",
    "stratumDifficulty",
    "overheat_temp",
    "vrFrequency",
}

KNOWN_SETTINGS = DOCUMENTED_SETTINGS | OBSERVED_NERD_SETTINGS
SETTING_KEY_LOOKUP: dict[str, str] = {}

FIELD_ALIASES = {
    "bestdifficulty": "best_diff",
    "historicalbest": "best_diff",
    "lifetimebest": "best_diff",
    "bestsessiondifficulty": "best_session_diff",
    "currentroundbest": "best_session_diff",
    "roundbest": "best_session_diff",
    "pooldifficulty": "pool_difficulty",
    "difficulty": "pool_difficulty",
    "hashrate": "hash_rate_ghs",
    "hashrate1m": "hash_rate_1m_ghs",
    "hashrate10m": "hash_rate_10m_ghs",
    "hashrate1h": "hash_rate_1h_ghs",
    "hashrate1d": "hash_rate_1d_ghs",
    "temp": "temp_c",
    "temperature": "temp_c",
    "vrtemp": "vr_temp_c",
    "fanrpm": "fan_rpm",
    "fanspeed": "fan_speed_percent",
    "uptime": "uptime_seconds",
    "pool": "pool_url",
    "version": "firmware_version",
    "model": "device_model",
    "ip": "ip",
    "mac": "mac_addr",
}


class RequestFailure(Exception):
    def __init__(self, url: str, message: str, status: int | None = None) -> None:
        super().__init__(message)
        self.url = url
        self.message = message
        self.status = status


def normalize_token(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.lower())


SETTING_KEY_LOOKUP = {normalize_token(key): key for key in KNOWN_SETTINGS}


def build_base_url(target: str) -> str:
    text = target.strip().rstrip("/")
    if not text:
        raise ValueError("target is empty")
    if "://" not in text:
        text = f"http://{text}"
    return text


def coerce_value(raw: str) -> Any:
    lowered = raw.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    if lowered in {"null", "none"}:
        return None
    try:
        if raw.startswith("0") and raw not in {"0", "0.0"} and not raw.startswith("0."):
            raise ValueError
        return int(raw)
    except ValueError:
        try:
            return float(raw)
        except ValueError:
            return raw


def first_non_none(*values: Any) -> Any:
    for value in values:
        if value is not None:
            return value
    return None


def format_value(value: Any) -> str:
    if value is None:
        return "-"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, float):
        text = f"{value:.2f}"
        return text.rstrip("0").rstrip(".")
    return str(value)


def json_dump(data: Any) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2))


def parse_ip_or_none(value: str) -> ipaddress.IPv4Address | None:
    try:
        ip = ipaddress.ip_address(value)
    except ValueError:
        return None
    return ip if isinstance(ip, ipaddress.IPv4Address) else None


def local_ip_via_socket() -> list[tuple[ipaddress.IPv4Address, int]]:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.connect(("8.8.8.8", 80))
            ip_text = sock.getsockname()[0]
    except OSError:
        return []
    ip_value = parse_ip_or_none(ip_text)
    if ip_value is None or not ip_value.is_private:
        return []
    return [(ip_value, 24)]


def parse_ip_output() -> list[tuple[ipaddress.IPv4Address, int]]:
    try:
        result = subprocess.run(
            ["ip", "-o", "-f", "inet", "addr", "show"],
            check=False,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        return []

    entries: list[tuple[ipaddress.IPv4Address, int]] = []
    pattern = re.compile(r"inet (\d+\.\d+\.\d+\.\d+)/(\d+)")
    for match in pattern.finditer(result.stdout):
        ip_value = parse_ip_or_none(match.group(1))
        if ip_value is None or not ip_value.is_private or ip_value.is_loopback or ip_value.is_link_local:
            continue
        entries.append((ip_value, int(match.group(2))))
    return entries


def parse_ifconfig_output() -> list[tuple[ipaddress.IPv4Address, int]]:
    try:
        result = subprocess.run(
            ["ifconfig"],
            check=False,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        return []

    entries: list[tuple[ipaddress.IPv4Address, int]] = []
    pattern = re.compile(r"inet (\d+\.\d+\.\d+\.\d+)\s+netmask (0x[0-9a-fA-F]+|\d+\.\d+\.\d+\.\d+)")
    for match in pattern.finditer(result.stdout):
        ip_value = parse_ip_or_none(match.group(1))
        if ip_value is None or not ip_value.is_private or ip_value.is_loopback or ip_value.is_link_local:
            continue

        mask_text = match.group(2)
        if mask_text.startswith("0x"):
            mask_text = str(ipaddress.IPv4Address(int(mask_text, 16)))
        prefix = ipaddress.IPv4Network(f"0.0.0.0/{mask_text}").prefixlen
        entries.append((ip_value, prefix))
    return entries


def autodetect_networks(include_ap_default: bool) -> list[str]:
    networks: set[str] = set()
    for ip_value, prefix in parse_ip_output() + parse_ifconfig_output() + local_ip_via_socket():
        scan_prefix = prefix if 24 <= prefix <= 30 else 24
        network = ipaddress.ip_network(f"{ip_value}/{scan_prefix}", strict=False)
        networks.add(str(network))
    if include_ap_default:
        networks.add("192.168.4.1/32")
    return sorted(networks)


def iter_targets(networks: list[str], hosts: list[str]) -> list[str]:
    targets: list[str] = []
    seen: set[str] = set()

    for host in hosts:
        cleaned = host.strip()
        if cleaned and cleaned not in seen:
            seen.add(cleaned)
            targets.append(cleaned)

    for network_text in networks:
        network = ipaddress.ip_network(network_text, strict=False)
        if network.prefixlen == 32:
            candidate_values = [str(network.network_address)]
        else:
            candidate_values = [str(host) for host in network.hosts()]
        for candidate in candidate_values:
            if candidate not in seen:
                seen.add(candidate)
                targets.append(candidate)

    return targets


def request(
    base_url: str,
    path: str,
    method: str = "GET",
    payload: dict[str, Any] | None = None,
    timeout: float = DEFAULT_TIMEOUT,
) -> tuple[int, Any]:
    url = f"{base_url}{path}"
    headers: dict[str, str] = {}
    data: bytes | None = None

    if payload is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(payload).encode("utf-8")

    request_obj = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request_obj, timeout=timeout) as response:
            raw_body = response.read().decode("utf-8", errors="replace")
            if not raw_body.strip():
                return response.status, None
            try:
                return response.status, json.loads(raw_body)
            except json.JSONDecodeError:
                return response.status, raw_body
    except urllib.error.HTTPError as exc:
        body_text = exc.read().decode("utf-8", errors="replace")
        detail = body_text.strip() or exc.reason
        raise RequestFailure(url, detail, exc.code) from exc
    except urllib.error.URLError as exc:
        raise RequestFailure(url, str(exc.reason)) from exc
    except OSError as exc:
        raise RequestFailure(url, str(exc)) from exc


def detect_device_type(info: dict[str, Any]) -> str:
    if any(key in info for key in ("deviceModel", "hostip", "hashRate_1d")):
        return "nerd"
    if isinstance(info.get("stratum"), dict):
        return "nerd"
    if any(key in info for key in ("axeOSVersion", "ipv4", "boardVersion")):
        return "bitaxe"
    return "unknown"


def build_device_model(info: dict[str, Any], device_type: str) -> str | None:
    direct = info.get("deviceModel")
    if isinstance(direct, str) and direct:
        return direct
    board_version = info.get("boardVersion")
    if device_type == "bitaxe" and board_version:
        return f"Bitaxe {board_version}"
    if device_type == "bitaxe":
        return "Bitaxe"
    if device_type == "nerd":
        return "NerdAxe"
    return None


def normalize_device(info: dict[str, Any], target: str) -> dict[str, Any]:
    device_type = detect_device_type(info)
    parsed_host = urllib.parse.urlparse(build_base_url(target)).hostname or target

    return {
        "ip": first_non_none(info.get("ipv4"), info.get("hostip"), parsed_host),
        "device_type": device_type,
        "hostname": info.get("hostname"),
        "device_model": build_device_model(info, device_type),
        "board_version": info.get("boardVersion"),
        "asic_model": info.get("ASICModel"),
        "firmware_version": first_non_none(info.get("axeOSVersion"), info.get("version")),
        "wifi_ssid": info.get("ssid"),
        "wifi_rssi": info.get("wifiRSSI"),
        "mac_addr": info.get("macAddr"),
        "power_w": info.get("power"),
        "voltage_mv": info.get("voltage"),
        "current_ma": info.get("current"),
        "temp_c": info.get("temp"),
        "vr_temp_c": info.get("vrTemp"),
        "hash_rate_ghs": info.get("hashRate"),
        "hash_rate_1m_ghs": info.get("hashRate_1m"),
        "hash_rate_10m_ghs": info.get("hashRate_10m"),
        "hash_rate_1h_ghs": info.get("hashRate_1h"),
        "hash_rate_1d_ghs": info.get("hashRate_1d"),
        "best_diff": info.get("bestDiff"),
        "best_session_diff": info.get("bestSessionDiff"),
        "pool_difficulty": info.get("poolDifficulty"),
        "shares_accepted": info.get("sharesAccepted"),
        "shares_rejected": info.get("sharesRejected"),
        "frequency_mhz": info.get("frequency"),
        "core_voltage_mv": info.get("coreVoltage"),
        "pool_url": info.get("stratumURL"),
        "pool_port": info.get("stratumPort"),
        "pool_user": info.get("stratumUser"),
        "fallback_pool_url": info.get("fallbackStratumURL"),
        "fallback_pool_port": info.get("fallbackStratumPort"),
        "fallback_pool_user": info.get("fallbackStratumUser"),
        "uptime_seconds": info.get("uptimeSeconds"),
        "response_time_ms": first_non_none(info.get("responseTime"), info.get("lastpingrtt")),
        "fan_speed_percent": first_non_none(info.get("fanspeed"), info.get("manualFanSpeed")),
        "fan_rpm": info.get("fanrpm"),
        "found_blocks": first_non_none(info.get("blockFound"), info.get("foundBlocks")),
        "total_found_blocks": info.get("totalFoundBlocks"),
        "source_target": target,
    }


def fetch_info(target: str, timeout: float) -> tuple[dict[str, Any], dict[str, Any]]:
    base_url = build_base_url(target)
    _, body = request(base_url, "/api/system/info", timeout=timeout)
    if not isinstance(body, dict):
        raise RequestFailure(f"{base_url}/api/system/info", "unexpected non-JSON response")
    return normalize_device(body, target), body


def sort_devices(devices: list[dict[str, Any]]) -> list[dict[str, Any]]:
    def key_fn(device: dict[str, Any]) -> tuple[int, str]:
        ip_text = str(device.get("ip") or "")
        ip_value = parse_ip_or_none(ip_text)
        if ip_value is not None:
            return (0, f"{int(ip_value):010d}")
        return (1, ip_text)

    return sorted(devices, key=key_fn)


def print_table(devices: list[dict[str, Any]]) -> None:
    if not devices:
        print("No devices found.")
        return

    columns = [
        ("ip", "IP"),
        ("device_type", "Type"),
        ("hostname", "Hostname"),
        ("device_model", "Model"),
        ("asic_model", "ASIC"),
        ("hash_rate_ghs", "GH/s"),
        ("temp_c", "TempC"),
        ("power_w", "PowerW"),
        ("best_session_diff", "BestSession"),
    ]
    widths = {
        key: max(len(label), *(len(format_value(device.get(key))) for device in devices))
        for key, label in columns
    }

    header = "  ".join(label.ljust(widths[key]) for key, label in columns)
    print(header)
    print("  ".join("-" * widths[key] for key, _ in columns))
    for device in devices:
        print(
            "  ".join(format_value(device.get(key)).ljust(widths[key]) for key, _ in columns)
        )


def resolve_field(device: dict[str, Any], raw_info: dict[str, Any], requested_field: str) -> tuple[str, Any]:
    normalized_requested = normalize_token(requested_field)

    lookup: dict[str, tuple[str, Any]] = {}
    for key, value in device.items():
        lookup[normalize_token(key)] = (key, value)
    for key, value in raw_info.items():
        lookup.setdefault(normalize_token(key), (key, value))

    alias_target = FIELD_ALIASES.get(normalized_requested)
    if alias_target:
        alias_key = normalize_token(alias_target)
        if alias_key in lookup:
            return lookup[alias_key]

    if normalized_requested in lookup:
        return lookup[normalized_requested]

    available = sorted(device.keys())
    raise KeyError(
        f"Unknown field '{requested_field}'. Available normalized fields: {', '.join(available)}"
    )


def discover_command(args: argparse.Namespace) -> int:
    hosts = args.host or []
    networks = args.cidr or autodetect_networks(include_ap_default=not args.skip_ap_default)
    targets = iter_targets(networks, hosts)

    devices: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
        future_map = {
            executor.submit(fetch_info, target, args.timeout): target
            for target in targets
        }
        for future in concurrent.futures.as_completed(future_map):
            target = future_map[future]
            try:
                device, raw_info = future.result()
            except (RequestFailure, KeyError, ValueError):
                failures.append({"target": target})
                continue
            if args.include_raw:
                device["raw_info"] = raw_info
            devices.append(device)

    devices = sort_devices(devices)
    result = {
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "targets_scanned": len(targets),
        "networks": networks,
        "devices": devices,
    }

    if args.save:
        save_path = Path(args.save)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        save_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")

    if args.format == "json":
        json_dump(result)
    else:
        print_table(devices)
        if args.save:
            print(f"\nSaved inventory to {args.save}")
        if failures and args.verbose:
            print(f"\nSkipped {len(failures)} unreachable targets.", file=sys.stderr)

    return 0


def show_command(args: argparse.Namespace) -> int:
    try:
        device, raw_info = fetch_info(args.target, args.timeout)
    except RequestFailure as exc:
        print(f"Request failed: {exc.message} ({exc.url})", file=sys.stderr)
        return 1

    if args.field:
        try:
            field_name, value = resolve_field(device, raw_info, args.field)
        except KeyError as exc:
            print(str(exc), file=sys.stderr)
            return 1

        if args.format == "json":
            json_dump({"target": args.target, "field": field_name, "value": value})
        else:
            print(format_value(value))
        return 0

    if args.format == "raw":
        json_dump(raw_info)
    elif args.format == "json":
        json_dump(device)
    else:
        print_table([device])
    return 0


def parse_settings(items: list[str], allow_unknown: bool) -> tuple[dict[str, Any], list[str]]:
    payload: dict[str, Any] = {}
    warnings: list[str] = []
    for item in items:
        if "=" not in item:
            raise ValueError(f"Invalid setting '{item}'. Expected key=value.")
        key, raw_value = item.split("=", 1)
        supplied_key = key.strip()
        if not supplied_key:
            raise ValueError(f"Invalid setting '{item}'. Key is empty.")
        key = SETTING_KEY_LOOKUP.get(normalize_token(supplied_key), supplied_key)
        if key not in KNOWN_SETTINGS and not allow_unknown:
            raise ValueError(
                f"Unknown setting '{supplied_key}'. Use --allow-unknown only after verifying the firmware supports it."
            )
        if key in OBSERVED_NERD_SETTINGS and key not in DOCUMENTED_SETTINGS:
            warnings.append(
                f"Setting '{key}' is treated as Nerd-specific and firmware-dependent."
            )
        payload[key] = coerce_value(raw_value.strip())
    return payload, warnings


def set_command(args: argparse.Namespace) -> int:
    try:
        payload, warnings = parse_settings(args.setting, args.allow_unknown)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    if args.dry_run:
        json_dump({"target": args.target, "payload": payload, "restart": args.restart})
        return 0

    base_url = build_base_url(args.target)
    try:
        status, body = request(base_url, "/api/system", method="PATCH", payload=payload, timeout=args.timeout)
    except RequestFailure as exc:
        print(f"Request failed: {exc.message} ({exc.url})", file=sys.stderr)
        return 1

    result: dict[str, Any] = {
        "target": args.target,
        "status": status,
        "payload": payload,
        "response": body,
        "restart_sent": False,
    }

    if args.restart:
        try:
            restart_status, restart_body = request(
                base_url,
                "/api/system/restart",
                method="POST",
                timeout=args.timeout,
            )
        except RequestFailure as exc:
            print(f"Settings updated but restart failed: {exc.message} ({exc.url})", file=sys.stderr)
            return 1
        result["restart_sent"] = True
        result["restart_status"] = restart_status
        result["restart_response"] = restart_body

    for warning in warnings:
        print(f"Warning: {warning}", file=sys.stderr)
    if not args.restart:
        print(
            "Warning: settings were sent without restart. Some firmware builds require a restart before changes apply.",
            file=sys.stderr,
        )

    json_dump(result)
    return 0


def restart_command(args: argparse.Namespace) -> int:
    base_url = build_base_url(args.target)
    try:
        status, body = request(base_url, "/api/system/restart", method="POST", timeout=args.timeout)
    except RequestFailure as exc:
        print(f"Request failed: {exc.message} ({exc.url})", file=sys.stderr)
        return 1

    json_dump({"target": args.target, "status": status, "response": body})
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Discover and manage Bitaxe and Nerd solo miners on the local network.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    discover_parser = subparsers.add_parser("discover", help="Scan the local LAN for miners.")
    discover_parser.add_argument("--cidr", action="append", help="CIDR to scan, repeatable.")
    discover_parser.add_argument("--host", action="append", help="Specific host or IP to probe, repeatable.")
    discover_parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT, help="HTTP timeout in seconds.")
    discover_parser.add_argument("--workers", type=int, default=DEFAULT_WORKERS, help="Concurrent probe count.")
    discover_parser.add_argument("--format", choices=("table", "json"), default="table")
    discover_parser.add_argument("--save", help="Write normalized discovery output to a JSON file.")
    discover_parser.add_argument("--include-raw", action="store_true", help="Include raw /api/system/info payloads.")
    discover_parser.add_argument("--skip-ap-default", action="store_true", help="Do not probe 192.168.4.1.")
    discover_parser.add_argument("--verbose", action="store_true", help="Print scan warnings to stderr.")
    discover_parser.set_defaults(func=discover_command)

    show_parser = subparsers.add_parser("show", help="Show one miner or one field from one miner.")
    show_parser.add_argument("target", help="IP, hostname, or URL of the miner.")
    show_parser.add_argument("--field", help="One normalized or raw field name to print.")
    show_parser.add_argument("--format", choices=("table", "json", "raw"), default="table")
    show_parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT, help="HTTP timeout in seconds.")
    show_parser.set_defaults(func=show_command)

    set_parser = subparsers.add_parser("set", help="PATCH /api/system with one or more settings.")
    set_parser.add_argument("target", help="IP, hostname, or URL of the miner.")
    set_parser.add_argument("setting", nargs="+", help="One or more key=value pairs.")
    set_parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT, help="HTTP timeout in seconds.")
    set_parser.add_argument("--restart", action="store_true", help="Restart after updating settings.")
    set_parser.add_argument("--allow-unknown", action="store_true", help="Allow settings outside the known allowlist.")
    set_parser.add_argument("--dry-run", action="store_true", help="Print the outgoing payload without sending it.")
    set_parser.set_defaults(func=set_command)

    restart_parser = subparsers.add_parser("restart", help="Restart one miner.")
    restart_parser.add_argument("target", help="IP, hostname, or URL of the miner.")
    restart_parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT, help="HTTP timeout in seconds.")
    restart_parser.set_defaults(func=restart_command)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
