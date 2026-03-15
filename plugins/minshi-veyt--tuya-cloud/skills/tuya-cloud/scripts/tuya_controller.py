"""Tuya Cloud device controller — list, read, and control via tinytuya."""

import json
import os
import sys
import argparse
from datetime import datetime
from typing import Any, Dict, List

from dotenv import load_dotenv
import tinytuya

load_dotenv(override=True)


# ---------------------------------------------------------------------------
# Client
# ---------------------------------------------------------------------------

def load_tuya_client() -> tinytuya.Cloud:
    """Return an authenticated tinytuya Cloud client from .env credentials."""
    access_id = os.getenv("TUYA_ACCESS_ID")
    access_secret = os.getenv("TUYA_ACCESS_SECRET")
    endpoint = os.getenv("TUYA_API_ENDPOINT", "https://openapi.tuyaus.com")

    if not access_id or not access_secret:
        raise ValueError("TUYA_ACCESS_ID and TUYA_ACCESS_SECRET must be set in .env")

    region_map = {'tuyacn': 'cn', 'tuyaus': 'us', 'tuyaeu': 'eu', 'tuyain': 'in'}
    region = next((r for k, r in region_map.items() if k in endpoint), 'us')

    return tinytuya.Cloud(apiRegion=region, apiKey=access_id, apiSecret=access_secret)


# ---------------------------------------------------------------------------
# Core API
# ---------------------------------------------------------------------------

def list_all_devices(client: tinytuya.Cloud) -> List[Dict[str, Any]]:
    """Return all project devices with real-time online status."""
    resp = client.cloudrequest(
        "/v1.0/iot-01/associated-users/devices",
        query={"last_row_key": ""},
    )
    if resp.get('success'):
        return resp.get('result', {}).get('devices', [])
    raise Exception(f"list_all_devices failed ({resp.get('code')}): {resp.get('msg')}")


def get_device_info(client: tinytuya.Cloud, device_id: str) -> Dict[str, Any]:
    """Return device metadata (name, model, local_key, online, …)."""
    resp = client.cloudrequest(f"/v1.0/devices/{device_id}")
    if resp.get('success'):
        return resp.get('result', {})
    raise Exception(f"get_device_info failed ({resp.get('code')}): {resp.get('msg')}")


def get_device_status(client: tinytuya.Cloud, device_id: str) -> Dict[str, Any]:
    """Return current DP status as a flat {code: value} dict."""
    resp = client.getstatus(device_id)
    if resp.get('success'):
        result = resp.get('result', [])
        # getstatus returns [{code, value}, …]; normalize to flat dict
        return {item['code']: item['value'] for item in result} if isinstance(result, list) else result
    raise Exception(f"get_device_status failed ({resp.get('code')}): {resp.get('msg')}")


def send_device_commands(
    client: tinytuya.Cloud, device_id: str, commands: List[Dict[str, Any]]
) -> bool:
    """Send a list of {code, value} commands to a device. Returns True on success."""
    # tinytuya.sendcommand posts its second arg as the raw request body
    resp = client.sendcommand(device_id, {'commands': commands})
    if resp.get('success'):
        return True
    raise Exception(f"send_device_commands failed ({resp.get('code')}): {resp.get('msg')}")


# ---------------------------------------------------------------------------
# Data parsing & formatting
# ---------------------------------------------------------------------------

def parse_sensor_data(status: Dict[str, Any]) -> Dict[str, Any]:
    """Parse raw DP status dict into typed, human-readable fields."""
    parsed: Dict[str, Any] = {}

    temp_raw = status.get('va_temperature') or status.get('temp_current') or status.get('temp_set')
    if temp_raw is not None:
        parsed['temperature_celsius'] = round(temp_raw / 10.0, 1)

    humidity = status.get('va_humidity') or status.get('humidity_value')
    if humidity is not None:
        parsed['humidity_percent'] = float(humidity)

    battery = status.get('battery_percentage') or status.get('battery')
    if battery is not None:
        parsed['battery_percent'] = int(battery)
        parsed['battery_status'] = 'Good' if battery > 80 else 'Medium' if battery > 20 else 'Low'

    motion = status.get('pir')
    if motion is not None:
        parsed['motion_detected'] = (motion == 'pir')

    door_state = status.get('doorcontact_state')
    if door_state is not None:
        parsed['door_open'] = bool(door_state)
        parsed['door_status'] = 'Open' if door_state else 'Closed'

    state = status.get('state')
    if state is not None:
        parsed['state'] = state
        if isinstance(state, (int, bool)):
            parsed['state_text'] = 'On' if state else 'Off'

    parsed['raw_status'] = status
    parsed['last_updated'] = datetime.utcnow().isoformat() + 'Z'
    return parsed


def format_device_status(
    device_id: str,
    info: Dict[str, Any],
    status: Dict[str, Any],
    parsed_data: Dict[str, Any],
    format_type: str = 'json',
) -> str:
    """Format device info + status as JSON or human-readable text."""
    online = bool(info.get('online') or info.get('is_online'))

    if format_type == 'json':
        return json.dumps({
            'device_id': device_id,
            'name': info.get('name', 'Unknown'),
            'category': info.get('category', 'Unknown'),
            'online': online,
            'model': info.get('model', 'Unknown'),
            'status': status,
            'parsed_data': parsed_data,
        }, indent=2)

    lines = [
        f"Device: {info.get('name', 'Unknown')} ({device_id})",
        f"Category: {info.get('category', 'Unknown')}",
        f"Status: {'Online' if online else 'Offline'}",
        f"Model: {info.get('model', 'Unknown')}",
        "",
        "Device Data:",
    ]
    has_data = False
    for key, label, fmt in [
        ('temperature_celsius', '🌡️  Temperature', lambda v: f"{v}°C"),
        ('humidity_percent',    '💧 Humidity',     lambda v: f"{v}%"),
        ('battery_percent',     '🔋 Battery',      lambda v: f"{v}% ({parsed_data.get('battery_status')})"),
        ('motion_detected',     '🚶 Motion',       lambda v: 'Detected' if v else 'Not Detected'),
        ('door_status',         '🚪 Door',         lambda v: v),
        ('state',               '🔘 State',        lambda v: parsed_data.get('state_text', str(v))),
    ]:
        if key in parsed_data:
            lines.append(f"  {label}: {fmt(parsed_data[key])}")
            has_data = True

    if not has_data:
        lines += ["  No parsed data", "", "Raw Status:"] + [f"  • {k}: {v}" for k, v in status.items()]

    lines += ["", f"Last Updated: {parsed_data.get('last_updated', '')}"]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI command handlers
# ---------------------------------------------------------------------------

def cmd_list_devices(args: argparse.Namespace) -> None:
    client = load_tuya_client()
    devices = list_all_devices(client)
    if args.output_format == 'json':
        print(json.dumps(devices, indent=2))
        return
    print(f"Found {len(devices)} device(s):\n")
    for dev in devices:
        online = bool(dev.get('online'))
        print(f"  {'🟢' if online else '🔴'} {dev.get('name', 'Unknown')}")
        print(f"     ID: {dev.get('id')}  category: {dev.get('category')}  {'Online' if online else 'Offline'}")


def cmd_read_sensor(args: argparse.Namespace) -> None:
    client = load_tuya_client()
    info = get_device_info(client, args.device_id)
    status = get_device_status(client, args.device_id)
    parsed = parse_sensor_data(status)
    print(format_device_status(args.device_id, info, status, parsed, format_type=args.output_format))


def cmd_control_device(args: argparse.Namespace) -> None:
    commands = json.loads(args.commands)
    client = load_tuya_client()
    send_device_commands(client, args.device_id, commands)
    print(f"✓ Sent to {args.device_id}")
    for cmd in commands:
        print(f"  • {cmd['code']} = {cmd['value']}")


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Tuya Cloud Controller",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python tuya_controller.py list_devices
  python tuya_controller.py list_devices --output_format json

  python tuya_controller.py read_sensor bf0a155b2e49d3367bafrz
  python tuya_controller.py read_sensor bf0a155b2e49d3367bafrz --output_format text

  python tuya_controller.py control_device bffc2c6de8e82861e5vlhh '[{"code":"switch_1","value":true}]'
        """,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("list_devices", help="List all Tuya devices")
    p.add_argument("--output_format", choices=["json", "text"], default="text")
    p.set_defaults(func=cmd_list_devices)

    p = sub.add_parser("read_sensor", help="Read sensor data from a device")
    p.add_argument("device_id")
    p.add_argument("--output_format", choices=["json", "text"], default="json")
    p.set_defaults(func=cmd_read_sensor)

    p = sub.add_parser("control_device", help="Send commands to a Tuya device")
    p.add_argument("device_id")
    p.add_argument("commands", help='JSON array, e.g. \'[{"code":"switch_1","value":true}]\'')
    p.set_defaults(func=cmd_control_device)

    args = parser.parse_args()
    try:
        args.func(args)
    except Exception as e:
        print(f"❌ {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
