#!/usr/bin/env python3
"""Minimal WeShop client for skill scripts.

Uses only the Python standard library so the skill works on hosts that have
`python3` but not `requests`.
"""

from __future__ import annotations

import json
import mimetypes
import os
import time
import uuid
from pathlib import Path
from typing import Any
from urllib import error, parse, request

BASE_URL = "https://openapi.weshop.ai/openapi/v1"
DEFAULT_GENERATE_VERSION = "weshopFlash"
DEFAULT_CHANGE_POSE_GENERATE_VERSION = "lite"
DEFAULT_PROFILE_FILENAME = ".weshopai-aiphotoshoot-profile.json"
DEFAULT_DOWNLOAD_DIR = "generated"
DEFAULT_TRY_ON_PROMPT = (
    "Replace the clothes of the person with the clothes from Figure 1, "
    "and replace the skin, face, hairstyle, and hair color of the model "
    "with those from Figure 2."
)
DEFAULT_CHANGE_POSE_PROMPT = (
    "Adjust the pose or expression of the provided image while preserving "
    "the same person's identity, outfit, and overall styling."
)
DEFAULT_SELFIE_QUALITY_GUIDANCE = (
    "Prioritize a realistic human selfie look over ecommerce catalog composition. "
    "Use natural body proportions, natural hands, realistic arms and shoulders, "
    "balanced facial symmetry, and a believable phone-camera perspective. "
    "Avoid warped anatomy, extra fingers, distorted limbs, stretched torso, oversized head, "
    "overly wide-angle distortion, mannequin-like posing, and fashion product showcase framing."
)

SHOT_STYLE_GUIDANCE = {
    "selfie": (
        "Frame as a close-up or half-body handheld phone selfie with the face as the main subject. "
        "Keep the composition intimate, casual, and natural."
    ),
    "mirror-selfie": (
        "Frame as a natural mirror selfie with a visible phone, relaxed posture, and realistic mirror perspective. "
        "Prefer half-body composition and avoid dramatic fashion-shoot angles."
    ),
    "candid": (
        "Frame as a candid daily-life photo with natural posture, relaxed shoulders, and believable body proportions."
    ),
    "portrait": (
        "Frame as a clean chest-up or half-body portrait with natural perspective, balanced facial features, and soft expression."
    ),
}


class WeShopError(RuntimeError):
    pass


def _strip_wrapping_quotes(value: str) -> str:
    trimmed = value.strip()
    if len(trimmed) >= 2 and trimmed[0] == trimmed[-1] and trimmed[0] in {"'", '"'}:
        return trimmed[1:-1]
    return trimmed


def _read_dotenv_value(path: Path, key: str) -> str:
    if not path.exists() or not path.is_file():
        return ""
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[7:].strip()
        if "=" not in line:
            continue
        current_key, raw_value = line.split("=", 1)
        if current_key.strip() != key:
            continue
        return _strip_wrapping_quotes(raw_value)
    return ""


def _candidate_env_files() -> list[Path]:
    candidates: list[Path] = []

    explicit_env = os.getenv("WESHOP_ENV_FILE", "").strip()
    if explicit_env:
        candidates.append(Path(explicit_env).expanduser())

    current_dir = Path.cwd().resolve(strict=False)
    candidates.append(current_dir / ".env")

    for parent in current_dir.parents:
        candidates.append(parent / ".env")

    if current_dir.name.startswith("workspace-"):
        sibling_workspace_env = current_dir.parent / "workspace" / ".env"
        candidates.append(sibling_workspace_env)

    deduped: list[Path] = []
    seen: set[Path] = set()
    for path in candidates:
        resolved = path.resolve(strict=False)
        if resolved in seen or not resolved.exists() or not resolved.is_file():
            continue
        seen.add(resolved)
        deduped.append(resolved)
    return deduped


def _candidate_profile_files() -> list[Path]:
    candidates: list[Path] = []

    explicit_profile = os.getenv("WESHOP_PROFILE_FILE", "").strip()
    if explicit_profile:
        candidates.append(Path(explicit_profile).expanduser())

    current_profile = Path.cwd() / DEFAULT_PROFILE_FILENAME
    if current_profile.exists():
        candidates.append(current_profile)

    deduped: list[Path] = []
    seen: set[Path] = set()
    for path in candidates:
        resolved = path.resolve(strict=False)
        if resolved in seen:
            continue
        seen.add(resolved)
        deduped.append(resolved)
    return deduped


def _default_profile_output_path() -> Path:
    explicit_profile = os.getenv("WESHOP_PROFILE_FILE", "").strip()
    if explicit_profile:
        return Path(explicit_profile).expanduser()

    return Path.cwd() / DEFAULT_PROFILE_FILENAME


def _read_json_file(path: Path) -> dict[str, Any]:
    if not path.exists() or not path.is_file():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return payload if isinstance(payload, dict) else {}


def _write_json_file(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _api_key() -> str:
    api_key = os.getenv("WESHOP_API_KEY", "").strip()
    if api_key:
        return api_key

    for env_file in _candidate_env_files():
        dotenv_value = _read_dotenv_value(env_file, "WESHOP_API_KEY")
        if dotenv_value:
            return dotenv_value

    raise WeShopError(
        "WESHOP_API_KEY is not set. Set it directly, point WESHOP_ENV_FILE at a dotenv "
        "file, or add WESHOP_API_KEY to a .env file in the current working directory."
    )


def _read_first_config_value(*keys: str) -> str:
    for key in keys:
        value = os.getenv(key, "").strip()
        if value:
            return value

    for env_file in _candidate_env_files():
        for key in keys:
            value = _read_dotenv_value(env_file, key)
            if value:
                return value
    return ""


def _headers(content_type: str | None = "application/json") -> dict[str, str]:
    headers = {
        "Authorization": _api_key(),
        "User-Agent": "openclaw-skill-weshopai-aiphotoshoot/1.0",
    }
    if content_type:
        headers["Content-Type"] = content_type
    return headers


def _load_json_response(resp: request.addinfourl) -> dict[str, Any]:
    raw = resp.read()
    try:
        data = json.loads(raw.decode("utf-8"))
    except Exception as exc:  # pragma: no cover - defensive
        raise WeShopError(f"WeShop invalid JSON response: {raw[:500]!r}") from exc
    if not isinstance(data, dict):
        raise WeShopError(f"WeShop invalid response payload: {data!r}")
    if not data.get("success"):
        raise WeShopError(
            f"WeShop API failed: code={data.get('code')}, msg={data.get('msg')}, data={data.get('data')}"
        )
    return data


def _request_json(
    method: str,
    path: str,
    *,
    payload: dict[str, Any] | None = None,
    params: dict[str, Any] | None = None,
    body: bytes | None = None,
    content_type: str | None = "application/json",
    timeout: int = 120,
    retries: int = 3,
    retry_delay_seconds: float = 2.0,
) -> dict[str, Any]:
    url = f"{BASE_URL}{path}"
    if params:
        query = parse.urlencode(params)
        url = f"{url}?{query}"
    if payload is not None:
        body = json.dumps(payload).encode("utf-8")
    req = request.Request(url=url, data=body, method=method, headers=_headers(content_type))

    last_exc: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            with request.urlopen(req, timeout=timeout) as resp:
                return _load_json_response(resp)
        except error.HTTPError as exc:
            raw = exc.read()
            try:
                data = json.loads(raw.decode("utf-8"))
            except Exception:
                data = None
            if isinstance(data, dict):
                raise WeShopError(
                    f"WeShop HTTP {exc.code}: code={data.get('code')}, msg={data.get('msg')}"
                ) from exc
            raise WeShopError(f"WeShop HTTP {exc.code}: {raw[:500]!r}") from exc
        except (error.URLError, TimeoutError, OSError) as exc:
            last_exc = exc
            if attempt >= retries:
                break
            time.sleep(retry_delay_seconds * attempt)
    raise WeShopError(f"WeShop request failed after {retries} attempts: {last_exc}") from last_exc

def _multipart_body(field_name: str, file_path: str) -> tuple[bytes, str]:
    path = Path(file_path)
    mime_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    boundary = f"----OpenClawSkill{uuid.uuid4().hex}"
    file_bytes = path.read_bytes()
    parts = [
        f"--{boundary}\r\n".encode("utf-8"),
        (
            f'Content-Disposition: form-data; name="{field_name}"; filename="{path.name}"\r\n'
            f"Content-Type: {mime_type}\r\n\r\n"
        ).encode("utf-8"),
        file_bytes,
        b"\r\n",
        f"--{boundary}--\r\n".encode("utf-8"),
    ]
    return b"".join(parts), f"multipart/form-data; boundary={boundary}"


def is_remote_url(value: str) -> bool:
    parsed = parse.urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def upload_image(file_path: str) -> str:
    body, content_type = _multipart_body("image", file_path)
    data = _request_json(
        "POST",
        "/asset/upload/image",
        body=body,
        content_type=content_type,
    )
    image_url = data.get("data", {}).get("image")
    if not image_url:
        raise WeShopError(f"WeShop upload returned no image URL: {data}")
    return str(image_url)


def resolve_image_input(value: str | None) -> str:
    if value is None:
        return ""
    trimmed = value.strip()
    if not trimmed:
        return ""
    if is_remote_url(trimmed):
        return trimmed
    path = Path(trimmed).expanduser()
    if not path.exists():
        raise WeShopError(f"Image input is neither a URL nor an existing file: {value}")
    return upload_image(str(path))


def create_my_fashion_model(images: list[str], name: str) -> int:
    data = _request_json(
        "POST",
        "/agent/myFashionModel/create",
        payload={
            "images": images,
            "name": name,
            "agentName": "aimodel",
            "agentVersion": "v1.0",
        },
    )
    fashion_model_id = data.get("data", {}).get("fashionModelId")
    if fashion_model_id in {None, ""}:
        raise WeShopError(f"WeShop create myFashionModel returned no fashionModelId: {data}")
    return int(fashion_model_id)


def query_my_fashion_model(fashion_model_id: int | str) -> dict[str, Any]:
    data = _request_json(
        "GET",
        "/agent/myFashionModel/query",
        params={"fashionModelId": fashion_model_id},
    )
    payload = data.get("data")
    if not isinstance(payload, dict):
        raise WeShopError(f"Unexpected myFashionModel payload: {data}")
    return payload


def wait_for_my_fashion_model(
    fashion_model_id: int | str,
    *,
    max_retries: int = 60,
    delay_seconds: int = 5,
) -> dict[str, Any]:
    last_status = "unknown"
    for _ in range(max_retries):
        info = query_my_fashion_model(fashion_model_id)
        status = str(info.get("status", "")).lower()
        last_status = status or last_status
        if status == "complete":
            return info
        if status == "failed":
            raise WeShopError(f"fashionModelId build failed: {info}")
        time.sleep(delay_seconds)
    raise WeShopError(
        f"Timeout waiting for fashionModelId={fashion_model_id} (last_status={last_status})"
    )


def resolve_fashion_model_image(
    *,
    fashion_model_image: str | None,
    fashion_model_id: int | str | None,
) -> str:
    if fashion_model_image and fashion_model_image.strip():
        return resolve_image_input(fashion_model_image)
    if fashion_model_id in {None, ""}:
        raise WeShopError("Provide either fashion_model_image or fashion_model_id.")
    info = wait_for_my_fashion_model(fashion_model_id)
    cover = str(info.get("cover", "")).strip()
    if cover:
        return cover
    images = info.get("images")
    if isinstance(images, list):
        for image in images:
            candidate = str(image or "").strip()
            if candidate:
                return candidate
    raise WeShopError(f"fashionModelId={fashion_model_id} has no usable image URL: {info}")


def normalize_profile(profile: dict[str, Any] | None) -> dict[str, Any]:
    normalized = dict(profile) if isinstance(profile, dict) else {}
    girlfriend = normalized.get("girlfriend")
    defaults = normalized.get("defaults")
    meta = normalized.get("meta")

    normalized["girlfriend"] = girlfriend if isinstance(girlfriend, dict) else {}
    normalized["defaults"] = defaults if isinstance(defaults, dict) else {}
    normalized["meta"] = meta if isinstance(meta, dict) else {}

    defaults_dict = normalized["defaults"]
    for key in ("outfits", "scenes", "sceneNotes"):
        value = defaults_dict.get(key)
        defaults_dict[key] = value if isinstance(value, list) else []

    return normalized


def load_profile(profile_path: str | None = None) -> tuple[dict[str, Any], Path]:
    if profile_path and profile_path.strip():
        resolved_path = Path(profile_path).expanduser().resolve(strict=False)
        return normalize_profile(_read_json_file(resolved_path)), resolved_path

    for candidate in _candidate_profile_files():
        payload = _read_json_file(candidate)
        if payload:
            return normalize_profile(payload), candidate

    default_path = _default_profile_output_path().resolve(strict=False)
    return normalize_profile({}), default_path


def save_profile(profile: dict[str, Any], profile_path: str | Path | None = None) -> Path:
    if profile_path is None:
        target_path = _default_profile_output_path()
    elif isinstance(profile_path, Path):
        target_path = profile_path
    else:
        target_path = Path(profile_path).expanduser()
    resolved_path = target_path.resolve(strict=False)
    _write_json_file(resolved_path, normalize_profile(profile))
    return resolved_path


def _match_profile_entry(entries: list[Any], key: str | None) -> dict[str, Any] | None:
    dict_entries = [entry for entry in entries if isinstance(entry, dict)]
    if not dict_entries:
        return None
    if not key or not key.strip():
        return dict_entries[0]

    normalized_key = key.strip().lower()
    for entry in dict_entries:
        for field in ("id", "label", "name"):
            candidate = str(entry.get(field, "")).strip().lower()
            if candidate and candidate == normalized_key:
                return entry
    return None


def resolve_identity_for_photoshoot(
    *,
    fashion_model_image: str | None,
    fashion_model_id: int | str | None,
    profile: dict[str, Any],
) -> tuple[str, str, str]:
    if fashion_model_image and fashion_model_image.strip():
        return (
            resolve_image_input(fashion_model_image),
            "explicit-fashion-model-image",
            str(fashion_model_id or "").strip(),
        )

    if fashion_model_id not in {None, ""}:
        return (
            resolve_fashion_model_image(
                fashion_model_image=None,
                fashion_model_id=fashion_model_id,
            ),
            "explicit-fashion-model-id",
            str(fashion_model_id).strip(),
        )

    girlfriend = profile.get("girlfriend", {})
    cover = str(girlfriend.get("cover", "")).strip()
    if cover:
        return cover, "profile:cover", str(girlfriend.get("fashionModelId", "")).strip()

    stored_images = girlfriend.get("images")
    if isinstance(stored_images, list):
        for image in stored_images:
            candidate = str(image or "").strip()
            if candidate:
                return candidate, "profile:images", str(girlfriend.get("fashionModelId", "")).strip()

    stored_model_id = girlfriend.get("fashionModelId")
    if stored_model_id not in {None, ""}:
        return (
            resolve_fashion_model_image(
                fashion_model_image=None,
                fashion_model_id=stored_model_id,
            ),
            "profile:fashionModelId",
            str(stored_model_id).strip(),
        )

    raise WeShopError(
        "No girlfriend identity available. Run setup_profile.py first, or provide "
        "--fashion-model-image / --fashion-model-id."
    )


def resolve_identity_for_change_pose(
    *,
    fashion_model_image: str | None,
    fashion_model_id: int | str | None,
    editing_image_url: str,
    profile: dict[str, Any],
) -> tuple[str, str, str]:
    if fashion_model_image and fashion_model_image.strip():
        return (
            resolve_image_input(fashion_model_image),
            "explicit-fashion-model-image",
            str(fashion_model_id or "").strip(),
        )

    if fashion_model_id not in {None, ""}:
        return (
            resolve_fashion_model_image(
                fashion_model_image=None,
                fashion_model_id=fashion_model_id,
            ),
            "explicit-fashion-model-id",
            str(fashion_model_id).strip(),
        )

    girlfriend = profile.get("girlfriend", {})
    cover = str(girlfriend.get("cover", "")).strip()
    if cover:
        return cover, "profile:cover", str(girlfriend.get("fashionModelId", "")).strip()

    stored_images = girlfriend.get("images")
    if isinstance(stored_images, list):
        for image in stored_images:
            candidate = str(image or "").strip()
            if candidate:
                return candidate, "profile:images", str(girlfriend.get("fashionModelId", "")).strip()

    stored_model_id = girlfriend.get("fashionModelId")
    if stored_model_id not in {None, ""}:
        return (
            resolve_fashion_model_image(
                fashion_model_image=None,
                fashion_model_id=stored_model_id,
            ),
            "profile:fashionModelId",
            str(stored_model_id).strip(),
        )

    return editing_image_url, "editing-image-fallback", ""


def resolve_profile_outfit(
    *,
    profile: dict[str, Any],
    outfit_key: str | None,
) -> tuple[str, str]:
    entry = _match_profile_entry(profile.get("defaults", {}).get("outfits", []), outfit_key)
    if not entry:
        return "", ""
    image_url = resolve_image_input(str(entry.get("image", "")))
    if not image_url:
        return "", ""
    label = str(entry.get("id") or entry.get("label") or "default")
    return image_url, f"profile-outfit:{label}"


def resolve_profile_scene(
    *,
    profile: dict[str, Any],
    scene_key: str | None,
) -> tuple[str, str, str, str]:
    scene_entry = _match_profile_entry(profile.get("defaults", {}).get("scenes", []), scene_key)
    if scene_entry:
        image_url = resolve_image_input(str(scene_entry.get("image", "")))
        if image_url:
            label = str(scene_entry.get("id") or scene_entry.get("label") or "default")
            return image_url, f"profile-scene:{label}", "", ""

    note_entry = _match_profile_entry(profile.get("defaults", {}).get("sceneNotes", []), scene_key)
    if note_entry:
        description = str(note_entry.get("description", "")).strip()
        if description:
            label = str(note_entry.get("id") or note_entry.get("label") or "default")
            return "", "", description, f"profile-scene-note:{label}"

    return "", "", "", ""


def resolve_original_image_with_fallback(
    *,
    original_image: str | None,
    default_original_image: str | None,
    profile: dict[str, Any],
    outfit_key: str | None,
) -> tuple[str, str]:
    direct_original = resolve_image_input(original_image)
    if direct_original:
        return direct_original, "explicit-original-image"

    direct_default = resolve_image_input(default_original_image)
    if direct_default:
        return direct_default, "explicit-default-original-image"

    profile_original, profile_source = resolve_profile_outfit(profile=profile, outfit_key=outfit_key)
    if profile_original:
        return profile_original, profile_source

    configured_default = _read_first_config_value(
        "WESHOP_DEFAULT_ORIGINAL_IMAGE",
        "WESHOP_DEFAULT_WARDROBE_IMAGE",
    )
    resolved_configured_default = resolve_image_input(configured_default)
    if resolved_configured_default:
        return resolved_configured_default, "configured-default-original-image"

    raise WeShopError(
        "Missing originalImage (clothing/product image). Provide --original-image, "
        "--default-original-image, save a default outfit in the profile, or set an "
        "environment fallback via WESHOP_DEFAULT_ORIGINAL_IMAGE or "
        "WESHOP_DEFAULT_WARDROBE_IMAGE."
    )


def resolve_location_image_with_defaults(
    *,
    location_image: str | None,
    profile: dict[str, Any],
    scene_key: str | None,
) -> tuple[str, str, str, str]:
    direct_location = resolve_image_input(location_image)
    if direct_location:
        return direct_location, "explicit-location-image", "", ""

    profile_location, profile_location_source, scene_note, scene_note_source = resolve_profile_scene(
        profile=profile,
        scene_key=scene_key,
    )
    if profile_location or scene_note:
        return profile_location, profile_location_source, scene_note, scene_note_source

    configured_scene = _read_first_config_value(
        "WESHOP_DEFAULT_SCENE_IMAGE",
    )
    resolved_configured_scene = resolve_image_input(configured_scene)
    if resolved_configured_scene:
        return resolved_configured_scene, "configured-default-location-image", "", ""

    return "", "", "", ""


def _ensure_sentence(text: str) -> str:
    trimmed = text.strip()
    if not trimmed:
        return ""
    if trimmed[-1] in {".", "!", "?"}:
        return trimmed
    return f"{trimmed}."


def build_photoshoot_prompt(
    *,
    prompt: str | None,
    shot_brief: str | None,
    scene_note: str | None,
    appearance_note: str | None,
    shot_style: str | None = None,
) -> str:
    parts = [prompt.strip() if prompt and prompt.strip() else DEFAULT_TRY_ON_PROMPT]

    if shot_style:
        style_guidance = SHOT_STYLE_GUIDANCE.get(shot_style.strip().lower(), "")
        if style_guidance:
            parts.append(style_guidance)
    parts.append(DEFAULT_SELFIE_QUALITY_GUIDANCE)

    if shot_brief and shot_brief.strip():
        parts.append(f"Shot brief: {_ensure_sentence(shot_brief)}")
    if scene_note and scene_note.strip():
        parts.append(f"Scene direction: {_ensure_sentence(scene_note)}")
    if appearance_note and appearance_note.strip():
        parts.append(f"Character note: {_ensure_sentence(appearance_note)}")

    return " ".join(part.strip() for part in parts if part.strip())


def build_change_pose_prompt(
    *,
    prompt: str | None,
    edit_brief: str | None,
    appearance_note: str | None,
) -> str:
    parts = [prompt.strip() if prompt and prompt.strip() else DEFAULT_CHANGE_POSE_PROMPT]

    if edit_brief and edit_brief.strip():
        parts.append(f"Edit brief: {_ensure_sentence(edit_brief)}")
    if appearance_note and appearance_note.strip():
        parts.append(f"Character note: {_ensure_sentence(appearance_note)}")

    return " ".join(part.strip() for part in parts if part.strip())


def create_virtual_try_on_task(
    *,
    fashion_model_image_url: str,
    original_image_url: str,
    location_image_url: str = "",
    task_name: str = "OpenClaw AI Photoshoot",
) -> str:
    payload = {
        "agentName": "virtualtryon",
        "agentVersion": "v1.0",
        "initParams": {
            "taskName": task_name[:20],
            "fashionModelImage": fashion_model_image_url,
            "originalImage": original_image_url,
        },
    }
    if location_image_url:
        payload["initParams"]["locationImage"] = location_image_url
    data = _request_json("POST", "/agent/task/create", payload=payload)
    task_id = data.get("data", {}).get("taskId")
    if not task_id:
        raise WeShopError(f"WeShop create task returned no taskId: {data}")
    return str(task_id)


def create_change_pose_task(
    *,
    fashion_model_image_url: str,
    editing_image_url: str,
    task_name: str = "OpenClaw Pose Edit",
) -> str:
    payload = {
        "agentName": "aipose",
        "agentVersion": "v1.0",
        "initParams": {
            "taskName": task_name[:20],
            "originalImage": editing_image_url,
        },
    }
    data = _request_json("POST", "/agent/task/create", payload=payload)
    task_id = data.get("data", {}).get("taskId")
    if not task_id:
        raise WeShopError(f"WeShop create task returned no taskId: {data}")
    return str(task_id)


def execute_virtual_try_on_task(
    task_id: str,
    *,
    prompt: str,
    fashion_model_image_url: str,
    location_image_url: str = "",
    description_type: str = "custom",
    batch_count: int = 1,
    max_retries: int = 3,
    retry_delay_seconds: int = 3,
) -> str:
    last_error: Exception | None = None
    for attempt in range(1, max_retries + 1):
        params: dict[str, Any] = {
            "generateVersion": DEFAULT_GENERATE_VERSION,
            "descriptionType": description_type,
            "batchCount": batch_count,
            "fashionModelImage": fashion_model_image_url,
        }
        if description_type == "custom":
            params["textDescription"] = prompt.strip() or DEFAULT_TRY_ON_PROMPT
        if location_image_url:
            params["locationImage"] = location_image_url
        payload = {"taskId": task_id, "params": params}
        try:
            data = _request_json("POST", "/agent/task/execute", payload=payload)
            execution_id = data.get("data", {}).get("executionId")
            if not execution_id:
                raise WeShopError(f"WeShop execute returned no executionId: {data}")
            return str(execution_id)
        except Exception as exc:  # pragma: no cover - defensive retry path
            last_error = exc
            msg = str(exc)
            retryable = any(
                token in msg for token in ("code=50004", "HTTP 502", "HTTP 503", "HTTP 504")
            )
            if not retryable or attempt >= max_retries:
                raise
            time.sleep(retry_delay_seconds * attempt)
    raise WeShopError(f"Execute virtual try-on failed after retries: {last_error}")


def execute_change_pose_task(
    task_id: str,
    *,
    prompt: str,
    generate_version: str = DEFAULT_CHANGE_POSE_GENERATE_VERSION,
    description_type: str = "custom",
    batch_count: int = 1,
    max_retries: int = 3,
    retry_delay_seconds: int = 3,
) -> str:
    last_error: Exception | None = None
    for attempt in range(1, max_retries + 1):
        params: dict[str, Any] = {
            "generateVersion": generate_version,
            "descriptionType": description_type,
            "batchCount": batch_count,
        }
        if description_type == "custom":
            params["textDescription"] = prompt.strip() or DEFAULT_CHANGE_POSE_PROMPT
        payload = {
            "taskId": task_id,
            "params": params,
            "agentName": "aipose",
            "agentVersion": "v1.0",
        }
        try:
            data = _request_json("POST", "/agent/task/execute", payload=payload)
            execution_id = data.get("data", {}).get("executionId")
            if not execution_id:
                raise WeShopError(f"WeShop execute returned no executionId: {data}")
            return str(execution_id)
        except Exception as exc:  # pragma: no cover - defensive retry path
            last_error = exc
            msg = str(exc)
            retryable = any(
                token in msg for token in ("code=50004", "HTTP 502", "HTTP 503", "HTTP 504")
            )
            if not retryable or attempt >= max_retries:
                raise
            time.sleep(retry_delay_seconds * attempt)
    raise WeShopError(f"Execute change pose failed after retries: {last_error}")


def query_execution(execution_id: str) -> dict[str, Any]:
    data = _request_json(
        "POST",
        "/agent/task/query",
        payload={"executionId": execution_id},
    )
    payload = data.get("data")
    if not isinstance(payload, dict):
        raise WeShopError(f"Unexpected task query payload: {data}")
    return payload


def poll_execution(
    execution_id: str,
    *,
    max_retries: int = 120,
    delay_seconds: int = 5,
) -> dict[str, Any]:
    last_status = "unknown"
    last_progress = ""
    for _ in range(max_retries):
        payload = query_execution(execution_id)
        executions = payload.get("executions", [])
        if isinstance(executions, list) and executions:
            execution = next(
                (item for item in executions if item.get("executionId") == execution_id),
                executions[-1],
            )
            status = str(execution.get("status", ""))
            last_status = status or last_status
            result_items = execution.get("result", [])
            if isinstance(result_items, list) and result_items:
                last_progress = str(result_items[0].get("progress", ""))
            if status == "Success":
                return execution
            if status in {"Failed", "Error"}:
                raise WeShopError(f"Task execution failed: {payload}")
        result = payload.get("result", {})
        if isinstance(result, dict):
            status = str(result.get("status", ""))
            last_status = status or last_status
            if status == "Success":
                return result
            if status in {"Failed", "Error"}:
                raise WeShopError(f"Task execution failed: {payload}")
        time.sleep(delay_seconds)
    progress = f", progress={last_progress}" if last_progress else ""
    raise WeShopError(
        f"Timeout waiting for executionId={execution_id} (last_status={last_status}{progress})"
    )


def extract_image_urls(result: dict[str, Any]) -> list[str]:
    image_urls: list[str] = []
    result_items = result.get("result")
    if isinstance(result_items, list):
        for item in result_items:
            if not isinstance(item, dict):
                continue
            if item.get("status") != "Success":
                continue
            image = str(item.get("image", "")).strip()
            if image:
                image_urls.append(image)
    if image_urls:
        return image_urls
    legacy_urls = result.get("imageUrls")
    if isinstance(legacy_urls, list):
        return [str(url).strip() for url in legacy_urls if str(url).strip()]
    legacy_url = str(result.get("imageUrl", "")).strip()
    return [legacy_url] if legacy_url else []


def _guess_image_extension(url: str, content_type: str) -> str:
    normalized_content_type = content_type.split(";", 1)[0].strip().lower()
    guessed_from_mime = mimetypes.guess_extension(normalized_content_type) if normalized_content_type else ""
    if guessed_from_mime == ".jpe":
        return ".jpg"
    if guessed_from_mime:
        return guessed_from_mime

    path_suffix = Path(parse.unquote(parse.urlparse(url).path)).suffix.lower()
    if path_suffix in {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp"}:
        return path_suffix
    return ".png"


def _to_relative_media_path(path: Path, *, base_dir: Path) -> str:
    relative = path.resolve(strict=False).relative_to(base_dir.resolve(strict=False))
    normalized = relative.as_posix()
    return f"./{normalized}" if not normalized.startswith("./") else normalized


def download_result_images(
    image_urls: list[str],
    *,
    download_dir: str | None,
    file_prefix: str,
) -> list[str]:
    if not image_urls:
        return []

    relative_download_dir = (download_dir or DEFAULT_DOWNLOAD_DIR).strip() or DEFAULT_DOWNLOAD_DIR
    cwd = Path.cwd().resolve(strict=False)
    target_dir = (cwd / relative_download_dir).resolve(strict=False)
    target_dir.mkdir(parents=True, exist_ok=True)

    local_paths: list[str] = []
    for index, image_url in enumerate(image_urls, start=1):
        if not is_remote_url(image_url):
            continue

        req = request.Request(
            url=image_url,
            method="GET",
            headers={"User-Agent": "openclaw-skill-weshopai-aiphotoshoot/1.0"},
        )
        try:
            with request.urlopen(req, timeout=120) as resp:
                image_bytes = resp.read()
                content_type = str(resp.headers.get("Content-Type", "")).strip()
        except error.HTTPError as exc:
            raise WeShopError(f"Failed to download generated image (HTTP {exc.code}): {image_url}") from exc
        except (error.URLError, TimeoutError, OSError) as exc:
            raise WeShopError(f"Failed to download generated image: {image_url}") from exc

        extension = _guess_image_extension(image_url, content_type)
        file_path = target_dir / f"{file_prefix}-{index}{extension}"
        file_path.write_bytes(image_bytes)
        local_paths.append(_to_relative_media_path(file_path, base_dir=cwd))

    return local_paths


def submit_virtual_try_on(
    *,
    profile_path: str | None,
    fashion_model_image: str | None,
    fashion_model_id: int | str | None,
    original_image: str | None,
    default_original_image: str | None = None,
    outfit_key: str | None = None,
    location_image: str | None = None,
    scene_key: str | None = None,
    prompt: str | None = None,
    shot_brief: str | None = None,
    shot_style: str | None = None,
    auto_refine: bool = False,
    task_name: str = "OpenClaw AI Photoshoot",
    description_type: str = "custom",
    batch_count: int = 1,
    poll_retries: int = 120,
    poll_delay_seconds: int = 5,
    download_dir: str | None = DEFAULT_DOWNLOAD_DIR,
) -> dict[str, Any]:
    profile, _resolved_profile_path = load_profile(profile_path)
    fashion_model_image_url, identity_source, resolved_fashion_model_id = resolve_identity_for_photoshoot(
        fashion_model_image=fashion_model_image,
        fashion_model_id=fashion_model_id,
        profile=profile,
    )
    original_image_url, original_image_source = resolve_original_image_with_fallback(
        original_image=original_image,
        default_original_image=default_original_image,
        profile=profile,
        outfit_key=outfit_key,
    )
    location_image_url, location_image_source, scene_note, scene_note_source = (
        resolve_location_image_with_defaults(
            location_image=location_image,
            profile=profile,
            scene_key=scene_key,
        )
    )
    if fashion_model_image_url == original_image_url:
        raise WeShopError("fashionModelImage and originalImage cannot be the same image.")

    appearance_note = str(profile.get("girlfriend", {}).get("appearanceNote", "")).strip()
    prompt_text = build_photoshoot_prompt(
        prompt=prompt,
        shot_brief=shot_brief,
        scene_note=scene_note,
        appearance_note=appearance_note,
        shot_style=shot_style,
    )

    task_id = create_virtual_try_on_task(
        fashion_model_image_url=fashion_model_image_url,
        original_image_url=original_image_url,
        location_image_url=location_image_url,
        task_name=task_name,
    )
    execution_id = execute_virtual_try_on_task(
        task_id,
        prompt=prompt_text,
        fashion_model_image_url=fashion_model_image_url,
        location_image_url=location_image_url,
        description_type=description_type,
        batch_count=batch_count,
    )
    result = poll_execution(
        execution_id,
        max_retries=poll_retries,
        delay_seconds=poll_delay_seconds,
    )
    image_urls = extract_image_urls(result)
    primary_image = image_urls[0] if image_urls else ""
    refinement: dict[str, Any] | None = None

    if auto_refine and primary_image:
        refine_brief = (
            "Refine this into a more natural realistic selfie. Fix warped anatomy, hands, arms, shoulders, "
            "and facial symmetry. Keep a believable phone-camera perspective, relaxed posture, and natural expression."
        )
        refined = submit_change_pose(
            profile_path=profile_path,
            fashion_model_image=fashion_model_image_url,
            fashion_model_id=resolved_fashion_model_id or None,
            editing_image=primary_image,
            edit_brief=refine_brief,
            task_name=f"{task_name[:12]} refine",
            generate_version=DEFAULT_CHANGE_POSE_GENERATE_VERSION,
            description_type="custom",
            batch_count=1,
            poll_retries=poll_retries,
            poll_delay_seconds=poll_delay_seconds,
        )
        refined_urls = refined.get("imageUrls") or []
        if refined_urls:
            primary_image = str(refined_urls[0])
            image_urls = [str(url) for url in refined_urls]
            refinement = refined

    local_image_paths = download_result_images(
        image_urls,
        download_dir=download_dir,
        file_prefix=f"weshop-{execution_id}",
    )

    return {
        "taskId": task_id,
        "executionId": execution_id,
        "resolvedInputs": {
            "fashionModelId": resolved_fashion_model_id,
            "fashionModelImage": fashion_model_image_url,
            "fashionModelImageSource": identity_source,
            "originalImage": original_image_url,
            "originalImageSource": original_image_source,
            "locationImage": location_image_url,
            "locationImageSource": location_image_source,
            "sceneNoteSource": scene_note_source,
        },
        "resolvedSettings": {
            "generateVersion": DEFAULT_GENERATE_VERSION,
            "profileLoaded": bool(profile),
            "promptText": prompt_text,
            "sceneNoteUsed": scene_note,
            "shotStyle": shot_style or "",
            "autoRefine": auto_refine,
            "batchCount": batch_count,
        },
        "result": result,
        "refinement": refinement,
        "imageUrls": image_urls,
        "primaryImage": primary_image,
        "localImagePaths": local_image_paths,
        "primaryLocalImage": local_image_paths[0] if local_image_paths else "",
    }


def submit_change_pose(
    *,
    profile_path: str | None,
    fashion_model_image: str | None,
    fashion_model_id: int | str | None,
    editing_image: str,
    prompt: str | None = None,
    edit_brief: str | None = None,
    task_name: str = "OpenClaw Pose Edit",
    generate_version: str = DEFAULT_CHANGE_POSE_GENERATE_VERSION,
    description_type: str = "custom",
    batch_count: int = 1,
    poll_retries: int = 120,
    poll_delay_seconds: int = 5,
    download_dir: str | None = DEFAULT_DOWNLOAD_DIR,
) -> dict[str, Any]:
    editing_image_url = resolve_image_input(editing_image)
    if not editing_image_url:
        raise WeShopError("Missing editingImage. Provide --editing-image as a URL or local file.")

    profile, _resolved_profile_path = load_profile(profile_path)
    fashion_model_image_url, identity_source, resolved_fashion_model_id = (
        resolve_identity_for_change_pose(
            fashion_model_image=fashion_model_image,
            fashion_model_id=fashion_model_id,
            editing_image_url=editing_image_url,
            profile=profile,
        )
    )
    appearance_note = str(profile.get("girlfriend", {}).get("appearanceNote", "")).strip()
    prompt_text = build_change_pose_prompt(
        prompt=prompt,
        edit_brief=edit_brief,
        appearance_note=appearance_note,
    )

    task_id = create_change_pose_task(
        fashion_model_image_url=fashion_model_image_url,
        editing_image_url=editing_image_url,
        task_name=task_name,
    )
    execution_id = execute_change_pose_task(
        task_id,
        prompt=prompt_text,
        generate_version=generate_version,
        description_type=description_type,
        batch_count=batch_count,
    )
    result = poll_execution(
        execution_id,
        max_retries=poll_retries,
        delay_seconds=poll_delay_seconds,
    )
    image_urls = extract_image_urls(result)
    local_image_paths = download_result_images(
        image_urls,
        download_dir=download_dir,
        file_prefix=f"weshop-{execution_id}",
    )
    return {
        "taskId": task_id,
        "executionId": execution_id,
        "resolvedInputs": {
            "fashionModelId": resolved_fashion_model_id,
            "fashionModelImage": fashion_model_image_url,
            "fashionModelImageSource": identity_source,
            "editingImage": editing_image_url,
            "editingImageSource": "explicit-editing-image",
        },
        "resolvedSettings": {
            "generateVersion": generate_version,
            "profileLoaded": bool(profile),
            "promptText": prompt_text,
            "batchCount": batch_count,
        },
        "result": result,
        "imageUrls": image_urls,
        "primaryImage": image_urls[0] if image_urls else "",
        "localImagePaths": local_image_paths,
        "primaryLocalImage": local_image_paths[0] if local_image_paths else "",
    }
