#!/usr/bin/env python3
"""
reCamera Detection Manager.

Used for managing reCamera device AI configurations and retrieval of detection events, including: retrieval
of available object detection models and their metadata (IDs, names, labels), querying and setting the active
detection model, configuring detection schedules, managing detection rules (debounce times, confidence/label/region
filters), and retrieving detection events with associated image snapshots for further analysis or archiving.

Refer to __all__ for the public API functions, COMMANDS and COMMAND_SCHEMAS for the CLI interface.
"""

from __future__ import annotations

import os.path as osp
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, TypedDict, Tuple

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
    "DetectionModel",
    "DetectionSchedule",
    "DetectionRule",
    "DetectionEvent",
    "get_detection_models_info",
    "get_detection_model",
    "set_detection_model",
    "get_detection_schedule",
    "set_detection_schedule",
    "get_detection_rules",
    "set_detection_rules",
    "get_detection_events",
    "clear_detection_events",
    "fetch_detection_event_image",
]

# MARK: Types (Important)


class DetectionModel(TypedDict):
    id: int
    name: str
    labels: list[str]


class DetectionSchedule(TypedDict):
    active_weekdays: list[
        Tuple[str, str]
    ]  # list of (start_time, end_time) tuples in "Day HH:MM:SS", case-sensitive short weekday name with ISO 8601 time, (Day: Sun, Mon, Tue, Wed, Thu, Fri, Sat)


class DetectionRule(TypedDict):
    name: str
    debounce_times: (
        int  # number of consecutive frames that must meet the rule to trigger an event
    )
    confidence_range_filter: Tuple[
        float, float
    ]  # [min_confidence, max_confidence], values between 0 and 1
    label_filter: list[int]  # list of label indices to include (empty means all labels)
    region_filter: Optional[
        list[list[Tuple[float, float]]]
    ]  # [[(x1, y1), (x2, y2), ...], ...], list of polygons defined by normalized coordinates (0 to 1, top-left as origin), use [[0,0],[1,0],[1,1],[0,1]] to include all regions, None means no region


class DetectionEvent(TypedDict):
    timestamp: str  # ISO 8601 format
    timestamp_unix_ms: int
    rule_name: str
    snapshot_path: Optional[
        Path
    ]  # remote file path to the snapshot image associated with the event, None if no snapshot is available


# MARK: Constants and globals

DEBOUNCE_TIMES_DEFAULT = 3
CONFIDENCE_RANGE_DEFAULT = (0.25, 1.0)
FULL_REGION_POLYGON: list[Tuple[float, float]] = [
    (0.0, 0.0),
    (1.0, 0.0),
    (1.0, 1.0),
    (0.0, 1.0),
]
REGION_FILTER_DEFAULT = [FULL_REGION_POLYGON]  # means include all regions
STORAGE_DEV_PATH_DEFAULT = "/dev/mmcblk0p8"


# MARK: Internal helpers


def _validate_schedule_time_format(time_str: str) -> bool:
    try:
        day, time = time_str.split()
        if day not in ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]:
            return False
        hour, minute, second = map(int, time.split(":"))
        if hour == 24:
            return minute == 0 and second == 0
        if not (0 <= hour < 24 and 0 <= minute < 60 and 0 <= second < 60):
            return False
        return True
    except ValueError:
        return False


def _unix_ms_to_iso8601(unix_ms: int) -> str:
    return datetime.fromtimestamp(unix_ms / 1000.0, tz=timezone.utc).isoformat(
        timespec="milliseconds"
    )


def _normalize_region_filter(
    region_filter: Optional[list[list[Tuple[float, float]]]],
) -> list[list[Tuple[float, float]]]:
    return [list(FULL_REGION_POLYGON)] if not region_filter else region_filter


def _request_json(
    url: str,
    headers: Dict[str, str],
    *,
    method: str,
    error_prefix: str,
    params: Optional[Dict[str, str]] = None,
    payload: Optional[Dict[str, Any]] = None,
) -> Any:
    target_url = url
    if params:
        target_url = f"{url}?{urllib.parse.urlencode(params)}"
    request_headers = dict(headers)
    body: Optional[bytes] = None
    if payload is not None:
        request_headers["Content-Type"] = "application/json"
        body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        target_url,
        data=body,
        headers=request_headers,
        method=method,
    )
    try:
        with urllib.request.urlopen(request, timeout=CONNECTION_TIMEOUT) as response:
            raw = response.read()
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"{error_prefix}: HTTP {e.code} {e.reason}") from e
    except urllib.error.URLError as e:
        raise RuntimeError(f"{error_prefix}: {e.reason}") from e
    except TimeoutError as e:
        raise RuntimeError(
            f"{error_prefix}: request timed out after {CONNECTION_TIMEOUT}s"
        ) from e
    try:
        return json.loads(raw.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        raise RuntimeError(f"{error_prefix}: invalid JSON response") from e


def _get_json(
    url: str,
    headers: Dict[str, str],
    *,
    error_prefix: str,
    params: Optional[Dict[str, str]] = None,
) -> Any:
    return _request_json(
        url,
        headers,
        method="GET",
        error_prefix=error_prefix,
        params=params,
    )


def _post_json(
    url: str,
    headers: Dict[str, str],
    *,
    error_prefix: str,
    params: Optional[Dict[str, str]] = None,
    payload: Optional[Dict[str, Any]] = None,
) -> Any:
    return _request_json(
        url,
        headers,
        method="POST",
        error_prefix=error_prefix,
        params=params,
        payload=payload,
    )


def _check_record_image(device: DeviceRecord) -> bool:
    url = get_device_api_url(device, "/cgi-bin/entry.cgi/record/rule/config")
    headers = get_device_api_headers(device)
    try:
        rules_data = _get_json(
            url,
            headers,
            error_prefix="Failed to get record image config",
        )
        if not isinstance(rules_data, dict) or not rules_data.get(
            "bRuleEnabled", False
        ):
            return False
        writer_config = rules_data.get("dWriterConfig", {})
        if not isinstance(writer_config, dict):
            return False
        return writer_config.get("sFormat", "").upper() == "JPG"
    except Exception:
        return False


def _enable_record_image(device: DeviceRecord) -> None:
    url = get_device_api_url(device, "/cgi-bin/entry.cgi/record/rule/config")
    headers = get_device_api_headers(device)
    payload = {
        "bRuleEnabled": True,
        "dWriterConfig": {
            "iIntervalMs": 0,  # NOTE: 0 means capture image immediately when event is triggered if no pending capture
            "sFormat": "JPG",
        },
    }
    result = _post_json(
        url,
        headers,
        payload=payload,
        error_prefix="Failed to enable record image",
    )
    if not isinstance(result, dict) or result.get("code", -1) != 0:
        raise RuntimeError(
            f"Failed to enable record image: {result.get('message', 'Unknown error')}"
        )


def _check_storage_enabled(device: DeviceRecord) -> bool:
    url = get_device_api_url(device, "/cgi-bin/entry.cgi/record/storage/status")
    headers = get_device_api_headers(device)
    try:
        storage_info = _get_json(
            url,
            headers,
            error_prefix="Failed to get storage status",
        )
        if not isinstance(storage_info, dict):
            return False
        for slot in storage_info.get("lSlots", []):
            if slot.get("bEnabled", False) and slot.get("bQuotaRotate", False):
                return True
    except Exception:
        pass
    return False


def _enable_default_storage(device: DeviceRecord) -> None:
    url = get_device_api_url(device, "/cgi-bin/entry.cgi/record/storage/config")
    headers = get_device_api_headers(device)
    payload = {
        "dSelectSlotToEnable": {"sByDevPath": STORAGE_DEV_PATH_DEFAULT, "sByUUID": ""}
    }
    result = _post_json(
        url,
        headers,
        payload=payload,
        error_prefix="Failed to enable default storage",
    )
    if not isinstance(result, dict) or result.get("code", -1) != 0:
        raise RuntimeError(
            f"Failed to enable default storage: {result.get('message', 'Unknown error')}"
        )
    url = get_device_api_url(device, "/cgi-bin/entry.cgi/record/storage/control")
    payload = {
        "sAction": "CONFIG",
        "sSlotDevPath": STORAGE_DEV_PATH_DEFAULT,
        "dSlotConfig": {
            "iQuotaLimitBytes": -1,  # -1 means no limit
            "bQuotaRotate": True,
        },
    }
    result = _post_json(
        url,
        headers,
        payload=payload,
        error_prefix="Failed to configure default storage",
    )
    if not isinstance(result, dict) or result.get("code", -1) != 0:
        raise RuntimeError(
            f"Failed to configure default storage: {result.get('message', 'Unknown error')}"
        )


# MARK: Public API functions (Important)


def get_detection_models_info(device: DeviceRecord) -> List[DetectionModel]:
    """
    Get information about available detection models from a specified camera,
    including the model IDs, names, and label mappings.

    Return a list of *DetectionModel* on success, otherwise raise an error.
    """
    url = get_device_api_url(device, "/cgi-bin/entry.cgi/model/list")
    headers = get_device_api_headers(device)
    models_info: List[DetectionModel] = []
    raw_models = _get_json(
        url, headers, error_prefix="Failed to get detection models info"
    )
    if not isinstance(raw_models, list):
        raise ValueError("Invalid response format: expected a list of models")
    for i, model in enumerate(raw_models):
        name = model["model"]
        labels = [
            label if isinstance(label, str) else str(label)
            for label in model.get("modelInfo", {}).get("classes", [])
        ]
        models_info.append(DetectionModel(id=i, name=name, labels=labels))
    return models_info


def get_detection_model(device: DeviceRecord) -> Optional[DetectionModel]:
    """
    Get the currently active detection model for a specified camera.

    Return the active *DetectionModel*, otherwise return None if detection is disabled or
    raise an error if the request fails.
    """
    url = get_device_api_url(device, "/cgi-bin/entry.cgi/model/inference")
    headers = get_device_api_headers(device)
    model_info = _get_json(
        url, headers, error_prefix="Failed to get active detection model"
    )
    if not isinstance(model_info, dict) or model_info.get("iEnable", 0) == 0:
        return None
    name = model_info.get("sModel", "")
    models_info = get_detection_models_info(device)
    for model in models_info:
        if model["name"] == name:
            return model
    return None


def set_detection_model(
    device: DeviceRecord,
    model_id: Optional[int] = None,
    model_name: Optional[str] = None,
) -> None:
    """
    Set the active detection model for a specified camera by *model_id* or *model_name*.

    Return None on success, otherwise raise an error.
    """
    if (model_id is None and model_name is None) or (
        model_id is not None and model_name is not None
    ):
        raise ValueError("Provide exactly one of 'model_id' or 'model_name'.")
    target_model: Optional[DetectionModel] = None
    models_info = get_detection_models_info(device)
    if model_id is not None:
        target_id = int(model_id)
        for item in models_info:
            if int(item["id"]) == target_id:
                target_model = item
                break
        if target_model is None:
            raise ValueError(f"Model ID '{target_id}' not found on device.")
    if model_name is not None:
        target_name = str(model_name).strip()
        if not target_name:
            raise ValueError("'model_name' must be a non-empty string.")
        for item in models_info:
            if str(item["name"]) == target_name:
                target_model = item
                break
        if target_model is None:
            raise ValueError(f"Model name '{target_name}' not found on device.")
    url = get_device_api_url(device, "/cgi-bin/entry.cgi/model/inference")
    headers = get_device_api_headers(device)
    params = {"id": str(int(target_model["id"]))}
    payload = {"iEnable": 1, "iFPS": 30, "sModel": target_model["name"]}
    result = _post_json(
        url,
        headers,
        params=params,
        payload=payload,
        error_prefix="Failed to set active detection model",
    )
    if not isinstance(result, dict) or result.get("code", -1) != 0:
        raise RuntimeError(
            f"Failed to set active detection model: {result.get('message', 'Unknown error')}"
        )


def get_detection_schedule(device: DeviceRecord) -> Optional[DetectionSchedule]:
    """
    Get the current detection schedule for a specified camera.

    Return a *DetectionSchedule* containing active weekdays and time ranges on success, None if
    schedule is disabled or not set, otherwise raise an error.
    """
    url = get_device_api_url(
        device, "/cgi-bin/entry.cgi/record/record/rule/schedule-rule-config"
    )
    headers = get_device_api_headers(device)
    schedule_data = _get_json(
        url, headers, error_prefix="Failed to get detection schedule"
    )
    if (
        not isinstance(schedule_data, dict)
        or schedule_data.get("bEnable", False) is False
    ):
        return None
    active_weekdays = [
        (rng["sStart"], rng["sEnd"]) for rng in schedule_data.get("lActiveWeekdays", [])
    ]
    return (
        DetectionSchedule(active_weekdays=active_weekdays) if active_weekdays else None
    )


def set_detection_schedule(
    device: DeviceRecord, schedule: Optional[DetectionSchedule]
) -> None:
    """
    Set the detection schedule for a specified camera.

    Use None to disable schedule (detection active all the time), otherwise replacing any existing schedule,
    time format of schedule range for detection schedule should be "Day HH:MM:SS" with case-sensitive short
    weekday name (Day: Sun, Mon, Tue, Wed, Thu, Fri, Sat) and ISO 8601 time.

    Return None on success, otherwise raise an error.
    """
    url = get_device_api_url(
        device, "/cgi-bin/entry.cgi/record/record/rule/schedule-rule-config"
    )
    headers = get_device_api_headers(device)
    activate_weekdays = []
    if schedule is not None:
        for start, end in schedule["active_weekdays"]:
            if not _validate_schedule_time_format(
                start
            ) or not _validate_schedule_time_format(end):
                raise ValueError(
                    f"Invalid schedule time format: '{start}' or '{end}'. Expected format is 'Day HH:MM:SS' with case-sensitive short weekday name (Day: Sun, Mon, Tue, Wed, Thu, Fri, Sat) and ISO 8601 time."
                )
            activate_weekdays.append({"sStart": start, "sEnd": end})
    payload = {
        "bEnable": True if schedule is not None else False,
        "lActiveWeekdays": activate_weekdays,
    }
    result = _post_json(
        url,
        headers,
        payload=payload,
        error_prefix="Failed to set detection schedule",
    )
    if not isinstance(result, dict) or result.get("code", -1) != 0:
        raise RuntimeError(
            f"Failed to set detection schedule: {result.get('message', 'Unknown error')}"
        )


def get_detection_rules(device: DeviceRecord) -> List[DetectionRule]:
    """
    Get the current activated detection rules for a specified camera.

    Checks will be performed to ensure record image and storage are enabled since rules require
    both to function properly, if either is not enabled, an empty list will be returned treating
    it as no rules active.

    Return a list of *DetectionRule* on success, otherwise raise an error.
    """
    if not _check_record_image(device):
        return []  # Treat no record image as no rules, since rules require record image to function
    if not _check_storage_enabled(device):
        return []  # Treat no storage as no rules, since rules require storage to function
    url = get_device_api_url(
        device, "/cgi-bin/entry.cgi/record/rule/record-rule-config"
    )
    headers = get_device_api_headers(device)
    rules: List[DetectionRule] = []
    rules_data = _get_json(url, headers, error_prefix="Failed to get detection rules")
    if (
        not isinstance(rules_data, dict)
        or rules_data.get("sCurrentSelected", "") != "INFERENCE_SET"
    ):
        return rules
    rules_list = rules_data.get("lInferenceSet", [])
    for rule in rules_list:
        name = rule.get("sID", "")
        debounce_times = rule.get("iDebounceTimes", 0)
        confidence_range_filter = rule.get("lConfidenceFilter", [0.0, 1.0])
        label_filter = rule.get("lClassFilter", [])
        region_filter = [
            region.get("lPolygon", []) for region in rule.get("lRegionFilter", [])
        ]
        rules.append(
            DetectionRule(
                name=name,
                debounce_times=debounce_times,
                confidence_range_filter=tuple(confidence_range_filter),
                label_filter=label_filter,
                region_filter=region_filter,
            )
        )
    return rules


def set_detection_rules(device: DeviceRecord, rules: List[DetectionRule]) -> None:
    """
    Set the detection rules for a specified camera.

    Automatic checks and enabling of record image and storage will be performed since rules require
    both to function properly, replacing any existing rules.

    Return None on success, otherwise raise an error.
    """
    if not _check_record_image(device):
        _enable_record_image(
            device
        )  # Enable record image if not already enabled, since rules require record image to function
    if not _check_storage_enabled(device):
        _enable_default_storage(
            device
        )  # Enable default storage if not already enabled, since rules require storage to function
    url = get_device_api_url(
        device, "/cgi-bin/entry.cgi/record/rule/record-rule-config"
    )
    headers = get_device_api_headers(device)
    payload = {
        "sCurrentSelected": "INFERENCE_SET",
        "lInferenceSet": [
            {
                "sID": rule["name"],
                "iDebounceTimes": rule["debounce_times"],
                "lConfidenceFilter": list(rule["confidence_range_filter"]),
                "lClassFilter": rule["label_filter"],
                "lRegionFilter": [
                    {"lPolygon": region}
                    for region in _normalize_region_filter(rule["region_filter"])
                ],
            }
            for rule in rules
        ],
    }
    result = _post_json(
        url,
        headers,
        payload=payload,
        error_prefix="Failed to set detection rules",
    )
    if not isinstance(result, dict) or result.get("code", -1) != 0:
        raise RuntimeError(
            f"Failed to set detection rules: {result.get('message', 'Unknown error')}"
        )


def get_detection_events(
    device: DeviceRecord,
    start_unix_ms: Optional[int] = None,
    end_unix_ms: Optional[int] = None,
) -> List[DetectionEvent]:
    """
    Get detection events from a specified camera within an optional time range.

    Time point *start_unix_ms* is always recommended to ensure a reasonable number of events are returned.

    Return a list of *DetectionEvent* on success, otherwise raise an error.
    """
    url = get_device_api_url(device, "/api/v1/events")
    headers = get_device_api_headers(device)
    params: Dict[str, str] = {}
    if start_unix_ms is not None:
        params["start"] = str(int(start_unix_ms))
    if end_unix_ms is not None:
        params["end"] = str(int(end_unix_ms))
    raw_events: Any = _get_json(
        url,
        headers,
        params=params or None,
        error_prefix="Failed to get detection events",
    )
    if not isinstance(raw_events, list):
        raise RuntimeError("Failed to get detection events: invalid response format")
    events: List[DetectionEvent] = []
    for item in raw_events:
        if not isinstance(item, dict):
            continue
        ts_raw = item.get("timestamp")
        try:
            ts_ms = int(ts_raw)
        except (TypeError, ValueError):
            continue
        event_id = item.get("id")
        rule_type = item.get("type")
        rule_name = (
            event_id.strip()
            if isinstance(event_id, str) and event_id.strip()
            else str(rule_type or "")
        )
        snapshot_path: Optional[Path] = None
        file_event = item.get("file_event")
        if isinstance(file_event, dict):
            path = file_event.get("path")
            if isinstance(path, str) and path.strip():
                snapshot_path = Path(path)
        events.append(
            DetectionEvent(
                timestamp=_unix_ms_to_iso8601(ts_ms),
                timestamp_unix_ms=ts_ms,
                rule_name=rule_name,
                snapshot_path=snapshot_path,
            )
        )
    return events


def clear_detection_events(device: DeviceRecord) -> None:
    """
    Clear cached detection events on a specified camera.

    Return None on success, otherwise raise an error.
    """
    url = get_device_api_url(device, "/api/v1/events/clear")
    headers = get_device_api_headers(device)
    result = _post_json(
        url,
        headers,
        error_prefix="Failed to clear detection events",
    )
    if not isinstance(result, dict):
        raise RuntimeError("Failed to clear detection events: invalid response format")
    status = str(result.get("status", "")).strip().lower()
    if status != "ok":
        raise RuntimeError(
            f"Failed to clear detection events: {result.get('error', result)}"
        )
    return None


def fetch_detection_event_image(device: DeviceRecord, snapshot_path: Path) -> bytes:
    """
    Fetch the photo associated with a detection event from the camera at *snapshot_path*.

    Return the photo content (JPG by default) as bytes on success, otherwise raise an error.
    """
    return fetch_file(device, str(snapshot_path))


def _fetch_detection_event_image_to_local_path(
    device: DeviceRecord, snapshot_path: Path, local_save_path: Path
) -> Dict[str, Any]:
    content = fetch_detection_event_image(device, snapshot_path)
    target_path = local_save_path.expanduser()
    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_bytes(content)
    return {
        "saved_path": str(target_path),
        "bytes": len(content),
    }


# MARK: CLI interface (Important)

COMMANDS = {
    "get_detection_models_info": get_detection_models_info,
    "get_detection_model": get_detection_model,
    "set_detection_model": set_detection_model,
    "get_detection_schedule": get_detection_schedule,
    "set_detection_schedule": set_detection_schedule,
    "get_detection_rules": get_detection_rules,
    "set_detection_rules": set_detection_rules,
    "get_detection_events": get_detection_events,
    "clear_detection_events": clear_detection_events,
    "fetch_detection_event_image": _fetch_detection_event_image_to_local_path,
}
COMMAND_SCHEMAS = {
    "get_detection_models_info": {
        "required_one_of": [("device_name", "device")],
        "optional": set(),
    },
    "get_detection_model": {
        "required_one_of": [("device_name", "device")],
        "optional": set(),
    },
    "set_detection_model": {
        "required_one_of": [("model_id", "model_name"), ("device_name", "device")],
        "optional": set(),
    },
    "get_detection_schedule": {
        "required_one_of": [("device_name", "device")],
        "optional": set(),
    },
    "set_detection_schedule": {
        "required_one_of": [("device_name", "device")],
        "optional": {"schedule"},
    },
    "get_detection_rules": {
        "required_one_of": [("device_name", "device")],
        "optional": set(),
    },
    "set_detection_rules": {
        "required": {"rules"},
        "required_one_of": [("device_name", "device")],
        "optional": set(),
    },
    "get_detection_events": {
        "required_one_of": [("device_name", "device")],
        "optional": {"start_unix_ms", "end_unix_ms"},
    },
    "clear_detection_events": {
        "required_one_of": [("device_name", "device")],
        "optional": set(),
    },
    "fetch_detection_event_image": {
        "required": {"snapshot_path", "local_save_path"},
        "required_one_of": [("device_name", "device")],
        "optional": set(),
    },
}


def _usage() -> str:
    return (
        "Usage: python3 detection_manager.py <command> [json-args]\n\n"
        "Commands:\n"
        '  get_detection_models_info   \'{"device_name":"cam1"}\'\n'
        '  get_detection_model         \'{"device_name":"cam1"}\'\n'
        '  set_detection_model         \'{"device_name":"cam1","model_id":0}\'\n'
        '                              \'{"device_name":"cam1","model_name":"your-model"}\'\n'
        '  get_detection_schedule      \'{"device_name":"cam1"}\'\n'
        '  set_detection_schedule      \'{"device_name":"cam1","schedule":{...}}\'\n'
        '                              \'{"device_name":"cam1","schedule":null}\'  # disable schedule\n'
        '                              \'{"device_name":"cam1"}\'                  # disable schedule\n'
        '  get_detection_rules         \'{"device_name":"cam1"}\'\n'
        '  set_detection_rules         \'{"device_name":"cam1","rules":[...]}\'\n'
        '  get_detection_events        \'{"device_name":"cam1","start_unix_ms":...,"end_unix_ms":...}\'\n'
        '  clear_detection_events      \'{"device_name":"cam1"}\'\n'
        '  fetch_detection_event_image \'{"device_name":"cam1","snapshot_path":"/mnt/sdcard/..jpg","local_save_path":"./event.jpg"}\'\n\n'
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
                f"Device '{device_name}' not found. Add it via device_manager first."
            )
        return record

    if "device" in args:
        raw = args["device"]
        if not isinstance(raw, dict):
            raise ValueError("'device' must be a JSON object.")
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

    if command == "set_detection_model":
        if "model_id" in args:
            kwargs["model_id"] = int(args["model_id"])
        if "model_name" in args:
            model_name = args["model_name"]
            if not isinstance(model_name, str) or not model_name.strip():
                raise ValueError("'model_name' must be a non-empty string.")
            kwargs["model_name"] = model_name.strip()

    elif command == "set_detection_schedule":
        if "schedule" not in args or args["schedule"] is None:
            kwargs["schedule"] = None
        else:
            schedule = args["schedule"]
            if not isinstance(schedule, dict):
                raise ValueError("'schedule' must be an object or null.")
            kwargs["schedule"] = schedule

    elif command == "set_detection_rules":
        rules = args["rules"]
        if not isinstance(rules, list):
            raise ValueError("'rules' must be an array.")
        kwargs["rules"] = rules

    elif command == "get_detection_events":
        if "start_unix_ms" in args:
            kwargs["start_unix_ms"] = int(args["start_unix_ms"])
        if "end_unix_ms" in args:
            kwargs["end_unix_ms"] = int(args["end_unix_ms"])

    elif command == "fetch_detection_event_image":
        snapshot_path = args["snapshot_path"]
        if not isinstance(snapshot_path, str) or not snapshot_path.strip():
            raise ValueError("'snapshot_path' must be a non-empty string.")
        local_save_path = args["local_save_path"]
        if not isinstance(local_save_path, str) or not local_save_path.strip():
            raise ValueError("'local_save_path' must be a non-empty string.")
        kwargs["snapshot_path"] = Path(snapshot_path)
        kwargs["local_save_path"] = Path(local_save_path)

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
        if result is not None:
            _print_json_stdout(result)
        sys.exit(0)
    except Exception as e:
        print(f"Error executing command '{command}': {e}", file=sys.stderr)
        sys.exit(4)


if __name__ == "__main__":
    main()
