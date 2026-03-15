#!/usr/bin/env python3

from __future__ import annotations

import argparse
import datetime as dt
import json
import mimetypes
import os
import platform
import re
import shutil
import subprocess
import sys
import uuid
from pathlib import Path
from urllib import error, request


BV_PATTERN = re.compile(r"(BV[0-9A-Za-z]+)", re.IGNORECASE)
EMPTY_HINTS = (
    "no subtitle",
    "subtitle not found",
    "未找到字幕",
    "无字幕",
    "没有字幕",
    "暂无字幕",
    "暂无 ai 总结",
    "该视频暂无 ai 总结",
    "无 ai 总结",
    "⚠️",
    "failed",
    "error",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Collect Bilibili video details, subtitles/comments, and optional ASR fallback."
    )
    parser.add_argument("--source", required=True, help="Bilibili video URL or BV number")
    parser.add_argument("--output", help="Output directory. Default: output/<bv-or-slug>")
    parser.add_argument(
        "--login-if-needed",
        action="store_true",
        help="Run `bili login` interactively when login is missing.",
    )
    parser.add_argument(
        "--transcribe-if-needed",
        action="store_true",
        help="Extract audio and call local ASR when subtitles are unavailable.",
    )
    parser.add_argument(
        "--parakeet-url",
        default=os.environ.get("PARAKEET_URL", "http://localhost:9001/v1/audio/transcriptions"),
        help="OpenAI-compatible transcription endpoint.",
    )
    parser.add_argument(
        "--parakeet-model",
        default=os.environ.get("PARAKEET_MODEL", "parakeet"),
        help="Model field sent to the transcription endpoint.",
    )
    parser.add_argument(
        "--asr-provider",
        choices=["auto", "parakeet", "aliyun"],
        default="auto",
        help="ASR provider selection. `auto` chooses by operating system.",
    )
    return parser.parse_args()


def run_command(command: list[str], interactive: bool = False) -> subprocess.CompletedProcess[str]:
    if interactive:
        return subprocess.run(command, check=False)
    return subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def ensure_tool(tool: str) -> None:
    if shutil.which(tool):
        return
    raise SystemExit(f"Missing required command: {tool}")


def extract_bv(source: str) -> str | None:
    match = BV_PATTERN.search(source)
    if match:
        return match.group(1)
    return None


def slugify(source: str) -> str:
    bv = extract_bv(source)
    if bv:
        return bv
    slug = re.sub(r"[^0-9A-Za-z._-]+", "-", source).strip("-")
    return slug[:80] or f"video-{uuid.uuid4().hex[:8]}"


def detect_os() -> str:
    system = platform.system().lower()
    if system.startswith("win"):
        return "windows"
    if system == "darwin":
        return "macos"
    if system == "linux":
        return "linux"
    return system or "unknown"


def choose_asr_providers(requested: str, current_os: str) -> list[str]:
    if requested != "auto":
        return [requested]
    if current_os == "windows":
        return ["aliyun"]
    if current_os in {"linux", "macos"}:
        return ["parakeet", "aliyun"]
    return ["aliyun"]


def make_output_dir(source: str, output: str | None) -> Path:
    if output:
        path = Path(output)
    else:
        path = Path("output") / slugify(source)
    path.mkdir(parents=True, exist_ok=True)
    return path


def save_text(path: Path, content: str) -> None:
    path.write_text(content.strip() + "\n", encoding="utf-8")


def save_json(path: Path, data: object) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def command_text(result: subprocess.CompletedProcess[str]) -> str:
    stdout = (result.stdout or "").strip()
    stderr = (result.stderr or "").strip()
    if stdout and stderr:
        return f"{stdout}\n\n[stderr]\n{stderr}"
    return stdout or stderr


def extract_primary_body(text: str) -> str:
    stripped = text.strip()
    if not stripped:
        return ""

    marker_patterns = (
        r"字幕内容:\s*",
        r"AI 总结:\s*",
        r"热门评论:\s*",
    )

    for pattern in marker_patterns:
        parts = re.split(pattern, stripped, maxsplit=1)
        if len(parts) == 2:
            return parts[1].strip()

    return stripped


def looks_like_useful_text(text: str) -> bool:
    stripped = extract_primary_body(text)
    if len(stripped) < 20:
        return False
    lowered = stripped.lower()
    return not any(hint in lowered for hint in EMPTY_HINTS)


def ensure_login(login_if_needed: bool, output_dir: Path) -> dict:
    status_result = run_command(["bili", "status"])
    status_text = command_text(status_result)
    save_text(output_dir / "auth_status.txt", status_text or "(empty output)")

    authenticated = status_result.returncode == 0 and "not logged in" not in status_text.lower()

    if authenticated or not login_if_needed:
        return {
            "checked": True,
            "authenticated": authenticated,
            "login_attempted": False,
            "status_command": "bili status",
        }

    login_result = run_command(["bili", "login"], interactive=True)
    refreshed = run_command(["bili", "status"])
    refreshed_text = command_text(refreshed)
    save_text(output_dir / "auth_status_after_login.txt", refreshed_text or "(empty output)")
    refreshed_ok = refreshed.returncode == 0 and "not logged in" not in refreshed_text.lower()

    return {
        "checked": True,
        "authenticated": refreshed_ok,
        "login_attempted": True,
        "login_exit_code": login_result.returncode,
        "status_command": "bili status",
    }


def collect_text(output_dir: Path, source: str, label: str, extra_args: list[str]) -> dict:
    command = ["bili", "video", source, *extra_args]
    result = run_command(command)
    text = command_text(result)
    path = output_dir / f"{label}.txt"

    if text:
        save_text(path, text)

    return {
        "command": command,
        "exit_code": result.returncode,
        "path": str(path) if text else None,
        "has_text": bool(text.strip()),
        "useful": looks_like_useful_text(text),
    }


def collect_video_json(output_dir: Path, source: str) -> dict:
    command = ["bili", "video", source, "--json"]
    result = run_command(command)
    text = command_text(result)
    path = output_dir / "video_details.json"

    if result.returncode != 0 or not text.strip():
        return {
            "command": command,
            "exit_code": result.returncode,
            "path": None,
            "has_json": False,
            "error": text or None,
        }

    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        save_text(output_dir / "video_details_json_error.txt", text)
        return {
            "command": command,
            "exit_code": result.returncode,
            "path": None,
            "has_json": False,
            "error": "Invalid JSON returned by `bili video --json`.",
        }

    save_json(path, payload)
    return {
        "command": command,
        "exit_code": result.returncode,
        "path": str(path),
        "has_json": True,
    }


def gather_audio_files(audio_dir: Path) -> list[Path]:
    patterns = ("*.wav", "*.mp3", "*.m4a", "*.flac", "*.aac")
    files: list[Path] = []
    for pattern in patterns:
        files.extend(audio_dir.rglob(pattern))
    return sorted(set(files))


def build_multipart(fields: dict[str, str], file_field: str, file_path: Path) -> tuple[bytes, str]:
    boundary = f"----CodexBoundary{uuid.uuid4().hex}"
    chunks: list[bytes] = []

    for key, value in fields.items():
        chunks.extend(
            [
                f"--{boundary}\r\n".encode("utf-8"),
                f'Content-Disposition: form-data; name="{key}"\r\n\r\n'.encode("utf-8"),
                str(value).encode("utf-8"),
                b"\r\n",
            ]
        )

    mime_type = mimetypes.guess_type(file_path.name)[0] or "application/octet-stream"
    file_bytes = file_path.read_bytes()
    chunks.extend(
        [
            f"--{boundary}\r\n".encode("utf-8"),
            (
                f'Content-Disposition: form-data; name="{file_field}"; '
                f'filename="{file_path.name}"\r\n'
            ).encode("utf-8"),
            f"Content-Type: {mime_type}\r\n\r\n".encode("utf-8"),
            file_bytes,
            b"\r\n",
            f"--{boundary}--\r\n".encode("utf-8"),
        ]
    )
    return b"".join(chunks), f"multipart/form-data; boundary={boundary}"


def transcribe_file_parakeet(audio_file: Path, url: str, model: str) -> str:
    body, content_type = build_multipart(
        {"model": model, "response_format": "text"},
        "file",
        audio_file,
    )
    http_request = request.Request(
        url,
        data=body,
        headers={"Content-Type": content_type},
        method="POST",
    )

    with request.urlopen(http_request, timeout=600) as response:
        payload = response.read().decode("utf-8", errors="replace").strip()

    if payload.startswith("{"):
        parsed = json.loads(payload)
        return str(parsed.get("text", "")).strip()
    return payload


def transcribe_file_aliyun(audio_file: Path, entrypoint: Path) -> str:
    result = run_command([sys.executable, str(entrypoint), str(audio_file)])
    if result.returncode != 0:
        raise RuntimeError(command_text(result) or f"Aliyun ASR exited with code {result.returncode}")
    return (result.stdout or "").strip()


def fallback_to_asr(
    output_dir: Path,
    source: str,
    providers: list[str],
    parakeet_url: str,
    parakeet_model: str,
    aliyun_entrypoint: Path,
) -> dict:
    audio_dir = output_dir / "audio"
    audio_dir.mkdir(parents=True, exist_ok=True)

    audio_result = run_command(["bili", "audio", source, "-o", str(audio_dir)])
    audio_text = command_text(audio_result)
    save_text(output_dir / "audio_extraction.txt", audio_text or "(empty output)")

    files = gather_audio_files(audio_dir)
    transcript_dir = output_dir / "transcripts"
    transcript_dir.mkdir(parents=True, exist_ok=True)
    combined_parts: list[str] = []
    items: list[dict] = []
    errors_seen: list[str] = []
    providers_used: list[str] = []

    for audio_file in files:
        transcript_path = transcript_dir / f"{audio_file.stem}.txt"
        provider_attempts: list[dict[str, str]] = []
        transcript = ""
        selected_provider = None

        for provider in providers:
            try:
                if provider == "parakeet":
                    transcript = transcribe_file_parakeet(audio_file, url=parakeet_url, model=parakeet_model)
                elif provider == "aliyun":
                    transcript = transcribe_file_aliyun(audio_file, entrypoint=aliyun_entrypoint)
                else:
                    raise RuntimeError(f"Unsupported ASR provider: {provider}")

                if transcript.strip():
                    selected_provider = provider
                    providers_used.append(provider)
                    break

                message = f"{provider} returned empty transcript"
                provider_attempts.append({"provider": provider, "error": message})
                errors_seen.append(f"{audio_file.name}: {message}")
            except (error.URLError, TimeoutError, OSError, json.JSONDecodeError, RuntimeError) as exc:
                provider_attempts.append({"provider": provider, "error": str(exc)})
                errors_seen.append(f"{audio_file.name}: {provider}: {exc}")

        if transcript.strip():
            save_text(transcript_path, transcript)
            combined_parts.append(f"## {audio_file.name}\n{transcript.strip()}\n")

        items.append(
            {
                "audio": str(audio_file),
                "transcript": str(transcript_path) if transcript.strip() else None,
                "success": bool(transcript.strip()),
                "provider": selected_provider,
                "attempts": provider_attempts,
            }
        )

    transcript_file = output_dir / "transcript.txt"
    if combined_parts:
        save_text(transcript_file, "\n".join(combined_parts))

    return {
        "audio_command": ["bili", "audio", source, "-o", str(audio_dir)],
        "audio_exit_code": audio_result.returncode,
        "provider_order": providers,
        "providers_used": sorted(set(providers_used)),
        "audio_files": [str(path) for path in files],
        "transcript_file": str(transcript_file) if combined_parts else None,
        "segments": items,
        "errors": errors_seen,
    }


def build_context(output_dir: Path, source: str, manifest: dict) -> None:
    details = read_text_if_exists(output_dir / "video_details.txt")
    subtitles = read_text_if_exists(output_dir / "subtitles.txt")
    ai_summary = read_text_if_exists(output_dir / "ai_summary.txt")
    comments = read_text_if_exists(output_dir / "comments.txt")
    transcript = read_text_if_exists(output_dir / "transcript.txt")

    preferred_transcript = subtitles if looks_like_useful_text(subtitles) else transcript
    transcript_source = "subtitles" if preferred_transcript == subtitles and subtitles else "asr"

    sections = [
        "# Bilibili Mindmap Context",
        "",
        "## Source",
        source,
        "",
        "## Retrieval Summary",
        json.dumps(
            {
                "authenticated": manifest["auth"].get("authenticated"),
                "subtitle_used": bool(subtitles and looks_like_useful_text(subtitles)),
                "asr_used": bool(transcript.strip()),
                "transcript_source": transcript_source if preferred_transcript else None,
            },
            ensure_ascii=False,
            indent=2,
        ),
        "",
        "## Video Details",
        details or "(missing)",
        "",
        "## Preferred Transcript",
        preferred_transcript or "(missing)",
        "",
        "## AI Summary",
        ai_summary or "(missing)",
        "",
        "## Hot Comments",
        comments or "(missing)",
        "",
        "## Outline Reminder",
        "- Use the video title as the root topic.",
        "- Prefer transcript evidence over comments and AI summary.",
        "- Treat comments as supplemental viewpoints.",
        "- Mark uncertain or conflicting points explicitly.",
    ]
    save_text(output_dir / "context.md", "\n".join(sections))


def read_text_if_exists(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace").strip()


def load_json_if_exists(path: Path) -> dict | list | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except json.JSONDecodeError:
        return None


def main() -> int:
    args = parse_args()
    ensure_tool("bili")
    current_os = detect_os()
    root_dir = Path(__file__).resolve().parents[1]
    aliyun_entrypoint = root_dir / "vendor" / "aliyun_asr" / "main.py"
    provider_order = choose_asr_providers(args.asr_provider, current_os)

    output_dir = make_output_dir(args.source, args.output)
    manifest: dict[str, object] = {
        "source": args.source,
        "output_dir": str(output_dir),
        "environment": {
            "os": current_os,
            "requested_asr_provider": args.asr_provider,
            "asr_provider_order": provider_order,
        },
        "auth": {},
        "files": {},
        "fallback": {},
        "warnings": [],
    }

    auth_info = ensure_login(args.login_if_needed, output_dir)
    manifest["auth"] = auth_info

    manifest["files"] = {
        "video_details_json": collect_video_json(output_dir, args.source),
        "video_details": collect_text(output_dir, args.source, "video_details", []),
        "subtitles": collect_text(output_dir, args.source, "subtitles", ["--subtitle"]),
        "ai_summary": collect_text(output_dir, args.source, "ai_summary", ["--ai"]),
        "comments": collect_text(output_dir, args.source, "comments", ["--comments"]),
    }

    subtitle_info = manifest["files"]["subtitles"]
    has_subtitle = isinstance(subtitle_info, dict) and bool(subtitle_info.get("useful"))

    if not has_subtitle and args.transcribe_if_needed:
        manifest["fallback"] = fallback_to_asr(
            output_dir,
            source=args.source,
            providers=provider_order,
            parakeet_url=args.parakeet_url,
            parakeet_model=args.parakeet_model,
            aliyun_entrypoint=aliyun_entrypoint,
        )
    elif not has_subtitle:
        manifest["warnings"].append("Subtitle unavailable and ASR fallback not enabled.")

    build_context(output_dir, args.source, manifest)
    (output_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(json.dumps({"output_dir": str(output_dir), "manifest": str(output_dir / 'manifest.json')}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
