#!/usr/bin/env python3
"""
reCamera Capture Manager.

Used for reCamera device media capture control, capturing images (JPG), starting video captures,
querying capture status, stopping pending captures, and downloading finished capture files from
the device. The capture manager is independent of the rule-based recording system.

Refer to __all__ for the public API functions, COMMANDS and COMMAND_SCHEMAS for the CLI interface.
"""

from __future__ import annotations

import os.path as osp
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, Optional, TypedDict

SCRIPTS_DIR = osp.dirname(osp.abspath(__file__))
if SCRIPTS_DIR not in sys.path:
    sys.path.append(SCRIPTS_DIR)

from device_manager import (  # noqa: E402
    CONNECTION_TIMEOUT,
    DeviceRecord,
    get_device_api_url,
    get_device_api_headers,
    fetch_file,
    get_device,
)

# MARK: Public API (Important)

__all__ = [
    "CaptureEvent",
    "CaptureStatus",
    "CaptureResult",
    "get_capture_status",
    "start_capture",
    "stop_capture",
    "capture_image",
]

# MARK: Types (Important)


class CaptureEvent(TypedDict):
    id: str  # unique capture event ID
    output_directory: str  # output directory path
    format: str  # capture format ("MP4", "JPG", "RAW")
    video_length_seconds: Optional[
        int
    ]  # present only for video captures with finite length
    status: str  # write event status ("PENDING", "WRITING", "COMPLETED", "FAILED", "INTERRUPTED", "CANCELED", "UNKNOWN")
    timestamp_unix_ms: int  # Unix timestamp in milliseconds
    file_name: str  # generated file name


class CaptureStatus(TypedDict):
    last_capture: Optional[
        CaptureEvent
    ]  # current active or last completed capture, None if none
    ready_to_start_new: bool  # whether a new capture can be started
    stop_requested: bool  # whether a stop capture request is pending


class CaptureResult(TypedDict):
    capture: CaptureEvent  # the completed capture event
    content: bytes  # raw image content bytes
    content_bytes: int  # byte length of the image content


# MARK: Constants and globals

CAPTURE_OUTPUT_DEFAULT = "/mnt/rc_mmcblk0p8/reCamera"
CAPTURE_FORMAT_IMAGE = "JPG"
CAPTURE_POLL_INTERVAL = 0.5  # seconds between status polls
CAPTURE_POLL_TIMEOUT_IMAGE = 5  # max seconds to wait for image capture completion
CAPTURE_STATUS_COMPLETED = "COMPLETED"
CAPTURE_STATUS_FAILED = "FAILED"
CAPTURE_STATUS_INTERRUPTED = "INTERRUPTED"
CAPTURE_STATUS_CANCELED = "CANCELED"
CAPTURE_STATUS_WRITING = "WRITING"
CAPTURE_STATUS_PENDING = "PENDING"
CAPTURE_TERMINAL_STATUSES = {
    CAPTURE_STATUS_COMPLETED,
    CAPTURE_STATUS_FAILED,
    CAPTURE_STATUS_INTERRUPTED,
    CAPTURE_STATUS_CANCELED,
}


# MARK: Internal helpers


def _parse_capture_event(data: Dict[str, Any]) -> CaptureEvent:
    video_length = data.get("iVideoLengthSeconds")
    return CaptureEvent(
        id=str(data.get("sID", "")),
        output_directory=str(data.get("sOutputDirectory", "")),
        format=str(data.get("sFormat", "")),
        video_length_seconds=int(video_length) if video_length is not None else None,
        status=str(data.get("sStatus", "UNKNOWN")),
        timestamp_unix_ms=int(data.get("iTimestamp", 0)),
        file_name=str(data.get("sFileName", "")),
    )


# MARK: Public API functions (Important)


def get_capture_status(device: DeviceRecord) -> CaptureStatus:
    """
    Get the capture status from a specified camera.

    Return the *CaptureStatus* containing the last/active capture event and readiness flags
    on success, otherwise raise an error.
    """
    url = get_device_api_url(device, "/cgi-bin/entry.cgi/record/capture/status")
    headers = get_device_api_headers(device)
    try:
        request = urllib.request.Request(url, headers=headers, method="GET")
        with urllib.request.urlopen(request, timeout=CONNECTION_TIMEOUT) as response:
            data = json.loads(response.read().decode("utf-8"))
        if not isinstance(data, dict):
            raise RuntimeError("Invalid response format: expected an object")
        raw_capture = data.get("dLastCapture")
        return CaptureStatus(
            last_capture=_parse_capture_event(raw_capture)
            if isinstance(raw_capture, dict)
            else None,
            ready_to_start_new=bool(data.get("bReadyToStartNew", False)),
            stop_requested=bool(data.get("bStopRequested", False)),
        )
    except urllib.error.HTTPError as e:
        raise RuntimeError(
            f"Failed to get capture status: HTTP {e.code} {e.reason}"
        ) from e
    except (urllib.error.URLError, json.JSONDecodeError, UnicodeDecodeError) as e:
        raise RuntimeError(f"Failed to get capture status: {e}") from e


def start_capture(
    device: DeviceRecord,
    output: str = CAPTURE_OUTPUT_DEFAULT,
    format: str = CAPTURE_FORMAT_IMAGE,
    video_length_seconds: Optional[int] = None,
) -> CaptureEvent:
    """
    Start a new capture session on a specified camera.

    Supported formats: "JPG" (image), "RAW" (image), "MP4" (video). For video captures, specify video_length_seconds
    is highly recommended to ensure the capture completes and is saved properly.

    Return the started *CaptureEvent* on success, otherwise raise an error.
    """
    url = get_device_api_url(device, "/cgi-bin/entry.cgi/record/capture/start")
    headers = get_device_api_headers(device)
    payload: Dict[str, Any] = {
        "sOutput": output,
        "sFormat": format.upper(),
    }
    if video_length_seconds is not None:
        payload["iVideoLengthSeconds"] = int(video_length_seconds)
    try:
        request_headers = {
            **headers,
            "Content-Type": "application/json",
        }
        request_body = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            url,
            data=request_body,
            headers=request_headers,
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=CONNECTION_TIMEOUT) as response:
            result = json.loads(response.read().decode("utf-8"))
        if not isinstance(result, dict) or result.get("code", -1) != 0:
            raise RuntimeError(
                f"Failed to start capture: {result.get('message', 'Unknown error')}"
            )
        raw_capture = result.get("dCapture")
        if not isinstance(raw_capture, dict):
            raise RuntimeError(
                "Failed to start capture: missing capture event in response"
            )
        return _parse_capture_event(raw_capture)
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"Failed to start capture: HTTP {e.code} {e.reason}") from e
    except (urllib.error.URLError, json.JSONDecodeError, UnicodeDecodeError) as e:
        raise RuntimeError(f"Failed to start capture: {e}") from e


def stop_capture(device: DeviceRecord) -> None:
    """
    Stop the current capture session on a specified camera (video only).

    Return None on success, otherwise raise an error.
    """
    url = get_device_api_url(device, "/cgi-bin/entry.cgi/record/capture/stop")
    headers = get_device_api_headers(device)
    try:
        request_headers = {
            **headers,
            "Content-Type": "application/json",
        }
        request = urllib.request.Request(
            url,
            data=b"{}",
            headers=request_headers,
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=CONNECTION_TIMEOUT) as response:
            result = json.loads(response.read().decode("utf-8"))
        if not isinstance(result, dict) or result.get("code", -1) != 0:
            raise RuntimeError(
                f"Failed to stop capture: {result.get('message', 'Unknown error')}"
            )
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"Failed to stop capture: HTTP {e.code} {e.reason}") from e
    except (urllib.error.URLError, json.JSONDecodeError, UnicodeDecodeError) as e:
        raise RuntimeError(f"Failed to stop capture: {e}") from e


def capture_image(
    device: DeviceRecord,
    output: str = CAPTURE_OUTPUT_DEFAULT,
    poll_interval: float = CAPTURE_POLL_INTERVAL,
    poll_timeout: float = CAPTURE_POLL_TIMEOUT_IMAGE,
) -> CaptureResult:
    """
    Capture an image (JPG or RAW) from a specified device, wait for completion, and download the captured photo.

    This is a high-level convenience function that:
      1. Starts an image capture on the device.
      2. Polls the capture status until the capture completes or times out.
      3. Downloads the captured image file from the device.
      4. Returns a *CaptureResult* with capture metadata and raw image bytes.

    Return a *CaptureResult* containing the capture event and image data on success, otherwise
    raise an error if the capture fails, times out, or if the image cannot be downloaded.
    """
    capture = start_capture(device, output=output, format=CAPTURE_FORMAT_IMAGE)
    elapsed = 0.0
    while elapsed < poll_timeout:
        time.sleep(poll_interval)
        elapsed += poll_interval
        status = get_capture_status(device)
        last = status["last_capture"]
        if last is None:
            continue
        if last["id"] != capture["id"]:
            continue
        if last["status"] in CAPTURE_TERMINAL_STATUSES:
            capture = last
            break
    else:
        raise RuntimeError(
            f"Capture timed out after {poll_timeout}s (last status: '{capture['status']}')"
        )
    if capture["status"] != CAPTURE_STATUS_COMPLETED:
        raise RuntimeError(
            f"Capture did not complete successfully (status: '{capture['status']}')"
        )
    remote_path = str(Path(capture["output_directory"]) / capture["file_name"])
    image_data = fetch_file(device, remote_path)
    return CaptureResult(
        capture=capture,
        content=image_data,
        content_bytes=len(image_data),
    )


def _capture_image_to_local_path(
    device: DeviceRecord,
    local_save_path: Path,
    output: str = CAPTURE_OUTPUT_DEFAULT,
    poll_interval: float = CAPTURE_POLL_INTERVAL,
    poll_timeout: float = CAPTURE_POLL_TIMEOUT_IMAGE,
) -> Dict[str, Any]:
    result = capture_image(
        device=device,
        output=output,
        poll_interval=poll_interval,
        poll_timeout=poll_timeout,
    )
    target_path = local_save_path.expanduser()
    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_bytes(result["content"])
    return {
        "capture": result["capture"],
        "saved_path": str(target_path),
        "bytes": result["content_bytes"],
    }


# MARK: CLI interface (Important)

COMMANDS = {
    "get_capture_status": get_capture_status,
    "start_capture": start_capture,
    "stop_capture": stop_capture,
    "capture_image": _capture_image_to_local_path,
}
COMMAND_SCHEMAS = {
    "get_capture_status": {
        "required_one_of": [("device_name", "device")],
        "optional": set(),
    },
    "start_capture": {
        "required_one_of": [("device_name", "device")],
        "optional": {"output", "format", "video_length_seconds"},
    },
    "stop_capture": {
        "required_one_of": [("device_name", "device")],
        "optional": set(),
    },
    "capture_image": {
        "required": {"local_save_path"},
        "required_one_of": [("device_name", "device")],
        "optional": {"output", "poll_interval", "poll_timeout"},
    },
}


def _usage() -> str:
    return (
        "Usage: python3 capture_manager.py <command> [json-args]\n\n"
        "Commands:\n"
        '  get_capture_status  \'{"device_name":"cam1"}\'\n'
        f'  start_capture       \'{{"device_name":"cam1","output":"{CAPTURE_OUTPUT_DEFAULT}","format":"JPG"}}\'\n'
        '                      \'{"device_name":"cam1","format":"MP4","video_length_seconds":60}\'\n'
        '  stop_capture        \'{"device_name":"cam1"}\'\n'
        '  capture_image       \'{"device_name":"cam1","local_save_path":"./capture.jpg"}\'\n'
        f'                      \'{{"device_name":"cam1","output":"{CAPTURE_OUTPUT_DEFAULT}","local_save_path":"./capture.jpg"}}\'\n\n'
        "Device resolution:\n"
        '  - Provide either "device_name" (loads from device_manager) or inline "device" object\n'
        '  - Inline device format: {"name":"...","host":"...","token":"..."[,"port":80]}\n\n'
    )


def _serialize_json(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, tuple):
        return [_serialize_json(item) for item in value]
    if isinstance(value, list):
        return [_serialize_json(item) for item in value]
    if isinstance(value, dict):
        return {str(k): _serialize_json(v) for k, v in value.items()}
    return value


def _resolve_device_from_args(args: Dict[str, Any]) -> DeviceRecord:
    if "device_name" in args and "device" in args:
        raise ValueError("Provide either 'device_name' or 'device', not both.")

    if "device_name" in args:
        device_name = args["device_name"]
        if not isinstance(device_name, str) or not device_name.strip():
            raise ValueError("'device_name' must be a non-empty string.")
        record = get_device(device_name.strip())
        if record is None:
            raise LookupError(
                f"Device '{device_name}' not found. Use device_manager to add it first."
            )
        return record

    if "device" in args:
        raw = args["device"]
        if not isinstance(raw, dict):
            raise ValueError("'device' must be an object.")
        name = raw.get("name", "inline-device")
        host = raw.get("host")
        token = raw.get("token")
        if not isinstance(host, str) or not host.strip():
            raise ValueError("'device.host' must be a non-empty string.")
        if not isinstance(token, str) or not token.strip():
            raise ValueError("'device.token' must be a non-empty string.")
        resolved = DeviceRecord(name=str(name), host=host.strip(), token=token.strip())
        if "port" in raw:
            resolved["port"] = int(raw["port"])
        return resolved

    raise ValueError("Missing device reference. Provide 'device_name' or 'device'.")


def _validate_command_args(command: str, args: Dict[str, Any]) -> None:
    schema = COMMAND_SCHEMAS[command]
    required = schema.get("required", set())
    required_one_of = schema.get("required_one_of", [])
    optional = schema.get("optional", set())

    allowed = set(required) | set(optional)
    for group in required_one_of:
        allowed |= set(group)

    unknown = sorted(set(args.keys()) - allowed)
    if unknown:
        raise ValueError(f"Unknown field(s): {', '.join(unknown)}")

    missing = sorted(set(required) - set(args.keys()))
    if missing:
        raise ValueError(f"Missing required field(s): {', '.join(missing)}")

    for group in required_one_of:
        present = [key for key in group if key in args]
        if len(present) == 0:
            pretty = " or ".join(f"'{field}'" for field in group)
            raise ValueError(f"Missing required field: provide {pretty}.")
        if len(present) > 1:
            pretty = ", ".join(f"'{field}'" for field in group)
            raise ValueError(f"Provide only one of: {pretty}.")


def _build_call_kwargs(command: str, args: Dict[str, Any]) -> Dict[str, Any]:
    kwargs: Dict[str, Any] = {"device": _resolve_device_from_args(args)}

    if command == "start_capture":
        if "output" in args:
            output = str(args["output"])
            if output.strip():
                kwargs["output"] = output
        if "format" in args:
            kwargs["format"] = str(args["format"])
        if "video_length_seconds" in args:
            kwargs["video_length_seconds"] = int(args["video_length_seconds"])

    elif command == "capture_image":
        local_save_path = args["local_save_path"]
        if not isinstance(local_save_path, str) or not local_save_path.strip():
            raise ValueError("'local_save_path' must be a non-empty string.")
        kwargs["local_save_path"] = Path(local_save_path)
        if "output" in args:
            output = str(args["output"])
            if output.strip():
                kwargs["output"] = output
        if "poll_interval" in args:
            kwargs["poll_interval"] = float(args["poll_interval"])
        if "poll_timeout" in args:
            kwargs["poll_timeout"] = float(args["poll_timeout"])

    return kwargs


def _print_json_stdout(payload: Any) -> None:
    print(json.dumps(_serialize_json(payload), ensure_ascii=False))


def main() -> None:
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print(_usage())
        sys.exit(0)

    command = sys.argv[1]
    if command not in COMMANDS:
        print(
            f"Unknown command: '{command}'. Available: {', '.join(COMMANDS.keys())}.",
            file=sys.stderr,
        )
        sys.exit(2)

    if len(sys.argv) > 3:
        print(
            f"Command '{command}' accepts at most one JSON object argument.",
            file=sys.stderr,
        )
        sys.exit(2)

    args: Dict[str, Any] = {}
    if len(sys.argv) == 3:
        try:
            loaded = json.loads(sys.argv[2])
        except json.JSONDecodeError as e:
            print(f"Invalid JSON argument: {e}", file=sys.stderr)
            sys.exit(2)
        if not isinstance(loaded, dict):
            print("Command arguments must be a JSON object.", file=sys.stderr)
            sys.exit(2)
        args = loaded

    try:
        _validate_command_args(command, args)
        call_kwargs = _build_call_kwargs(command, args)
    except LookupError as e:
        print(str(e), file=sys.stderr)
        sys.exit(3)
    except Exception as e:
        print(f"Invalid arguments for command '{command}': {e}", file=sys.stderr)
        sys.exit(2)

    try:
        result = COMMANDS[command](**call_kwargs)
        if result is None:
            _print_json_stdout({"ok": True})
        else:
            _print_json_stdout(result)
        sys.exit(0)
    except Exception as e:
        print(f"Error executing command '{command}': {e}", file=sys.stderr)
        sys.exit(4)


if __name__ == "__main__":
    main()
