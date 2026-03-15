#!/usr/bin/env python3
"""Extract media assets (images, videos, audio) and their prompts from Langfuse trace JSON files.

Scans all trace-*.json files in the case directory, extracts tool call parameters
for generation tools, deduplicates, downloads media files, and outputs assets.json.

Usage:
    python3 extract-assets.py --case-dir analysis/langfuse-data/cases/<CASE_ID>
"""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import unquote
from concurrent.futures import ThreadPoolExecutor, as_completed


GENERATION_TOOLS = {
    "video_generate", "image_generate", "tts_generate",
    "music_generate", "execute_edit_video",
}

TOOL_ALIASES = {
    "video-editor__execute_edit_video": "execute_edit_video",
    "videoagent-image-studio__image_generate": "image_generate",
    "videoagent-audio-studio__tts_generate": "tts_generate",
    "videoagent-audio-studio__music_generate": "music_generate",
}


def parse_args(obs: dict) -> Optional[dict]:
    """Extract tool call arguments from an observation, handling partial_json."""
    meta = obs.get("metadata") or {}
    pj = meta.get("partial_json")
    if pj:
        try:
            return json.loads(pj) if isinstance(pj, str) else pj
        except (json.JSONDecodeError, TypeError):
            pass

    inp = obs.get("input")
    if isinstance(inp, dict):
        return inp
    if isinstance(inp, str):
        try:
            return json.loads(inp)
        except (json.JSONDecodeError, TypeError):
            pass

    return None


def resolve_tool_call(obs: dict) -> tuple:
    """Extract (tool_name, args) from an observation, handling nested tool_call format."""
    inp = obs.get("input")
    if not inp:
        return None, None

    if isinstance(inp, dict) and inp.get("__type") == "tool_call_with_context":
        tc = inp.get("tool_call", {})
        raw_name = tc.get("name", "")
        tool_name = TOOL_ALIASES.get(raw_name, raw_name)
        args = tc.get("args")
        return tool_name, args

    if obs.get("type") == "TOOL":
        raw_name = obs.get("name", "")
        tool_name = TOOL_ALIASES.get(raw_name, raw_name)
        args = inp if isinstance(inp, dict) else None
        return tool_name, args

    return None, None


def extract_from_trace(trace_path: str) -> list:
    """Extract asset records from a single trace JSON file."""
    with open(trace_path) as f:
        trace = json.load(f)

    observations = trace.get("observations", [])
    assets = []

    for obs in observations:
        tool_name, args = resolve_tool_call(obs)

        if not tool_name or tool_name not in GENERATION_TOOLS:
            continue

        if not args:
            continue

        asset = {
            "tool": tool_name,
            "trace_file": os.path.basename(trace_path),
            "observation_id": obs.get("id", ""),
        }

        if tool_name == "video_generate":
            asset["prompt"] = args.get("prompt", "")
            asset["model"] = args.get("model", "")
            asset["mode"] = "reference2video" if args.get("image_list") or args.get("video_list") else "text2video"
            asset["name"] = args.get("name", "video")
            asset["type"] = "video"

            image_urls = []
            for img in (args.get("image_list") or []):
                url = img.get("image_url") or img.get("url") or ""
                if url:
                    image_urls.append(url)
            if image_urls:
                asset["reference_urls"] = image_urls

        elif tool_name == "image_generate":
            asset["prompt"] = args.get("prompt", "")
            asset["model"] = args.get("model", "")
            asset["name"] = args.get("name", "image")
            asset["type"] = "image"

        elif tool_name == "tts_generate":
            asset["prompt"] = args.get("text", args.get("input", ""))
            asset["model"] = args.get("model_id", args.get("model", ""))
            asset["name"] = args.get("name", "tts")
            asset["type"] = "audio"

        elif tool_name == "music_generate":
            asset["prompt"] = args.get("prompt", args.get("description", ""))
            asset["model"] = args.get("model_id", args.get("model", ""))
            asset["name"] = args.get("name", "music")
            asset["type"] = "audio"

        elif tool_name == "execute_edit_video":
            edit_spec = args.get("edit_spec")
            if isinstance(edit_spec, str):
                try:
                    edit_spec = json.loads(edit_spec)
                except (json.JSONDecodeError, TypeError):
                    edit_spec = None

            if edit_spec:
                asset["name"] = edit_spec.get("name", args.get("name", "assembly"))
                asset["type"] = "assembly"
                asset["prompt"] = ""

                urls = []
                total_clips = 0

                for track in (edit_spec.get("tracks") or []):
                    for clip in (track.get("clips") or []):
                        src = clip.get("url") or clip.get("source") or clip.get("src") or ""
                        if src and ("http" in src or src.startswith("/")):
                            urls.append(src)
                        total_clips += 1

                for clip in (edit_spec.get("clips") or []):
                    src = clip.get("url") or clip.get("source") or ""
                    if src and ("http" in src or src.startswith("/")):
                        urls.append(src)
                    total_clips += 1

                for at in (edit_spec.get("audio_tracks") or []):
                    src = at.get("url") or at.get("source") or ""
                    if src and ("http" in src or src.startswith("/")):
                        urls.append(src)

                asset["assembly_urls"] = urls
                asset["clip_count"] = total_clips

                duration = edit_spec.get("timeline", {}).get("duration")
                if duration:
                    asset["duration"] = duration
            else:
                continue

        assets.append(asset)

    return assets


def deduplicate(assets: list) -> list:
    """Deduplicate by (tool, name, prompt) tuple."""
    seen = set()
    unique = []
    for a in assets:
        key = (a.get("tool"), a.get("name"), a.get("prompt", "")[:100])
        if key not in seen:
            seen.add(key)
            unique.append(a)
    return unique


def url_to_filename(url: str) -> str:
    """Extract a clean filename from a URL, handling URL-encoded paths."""
    path_part = url.split("?")[0]
    decoded = unquote(path_part)
    return decoded.split("/")[-1]


def collect_downloadable_urls(assets: list) -> dict:
    """Build name → URL mapping from assembly_urls and reference_urls."""
    url_map = {}

    for a in assets:
        for url in a.get("assembly_urls", []):
            if "http" in url:
                name = url_to_filename(url)
                if name and name not in url_map:
                    url_map[name] = url

        for url in a.get("reference_urls", []):
            if "http" in url:
                name = url_to_filename(url)
                if name and name not in url_map:
                    url_map[name] = url

    return url_map


def download_file(url: str, dest: str) -> bool:
    """Download a single file via curl."""
    try:
        result = subprocess.run(
            ["curl", "-sL", "-o", dest, "-w", "%{http_code}", url],
            capture_output=True, text=True, timeout=120,
        )
        code = result.stdout.strip()
        return code == "200" and os.path.getsize(dest) > 0
    except Exception:
        return False


def download_all(url_map: dict, media_dir: str, max_workers: int = 4):
    """Download all media files in parallel."""
    os.makedirs(media_dir, exist_ok=True)

    to_download = {}
    for name, url in url_map.items():
        dest = os.path.join(media_dir, name)
        if os.path.exists(dest) and os.path.getsize(dest) > 0:
            continue
        to_download[name] = (url, dest)

    if not to_download:
        print(f"  All {len(url_map)} files already downloaded.")
        return

    print(f"  Downloading {len(to_download)} files ({len(url_map) - len(to_download)} cached)...")

    results = {"ok": 0, "fail": 0}
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {
            pool.submit(download_file, url, dest): name
            for name, (url, dest) in to_download.items()
        }
        for future in as_completed(futures):
            name = futures[future]
            if future.result():
                results["ok"] += 1
            else:
                results["fail"] += 1
                print(f"    FAIL: {name}", file=sys.stderr)

    print(f"  Done: {results['ok']} OK, {results['fail']} failed.")


def main():
    parser = argparse.ArgumentParser(description="Extract media assets from Langfuse traces")
    parser.add_argument("--case-dir", required=True, help="Path to case directory with trace-*.json files")
    parser.add_argument("--skip-download", action="store_true", help="Skip downloading media files")
    args = parser.parse_args()

    case_dir = args.case_dir
    trace_files = sorted(Path(case_dir).glob("trace-*.json"))

    if not trace_files:
        print(f"No trace files found in {case_dir}", file=sys.stderr)
        sys.exit(1)

    print(f"Scanning {len(trace_files)} trace files...")
    all_assets = []
    for tf in trace_files:
        assets = extract_from_trace(str(tf))
        all_assets.extend(assets)
        if assets:
            print(f"  {tf.name}: {len(assets)} assets")

    unique_assets = deduplicate(all_assets)
    print(f"\nTotal: {len(all_assets)} raw → {len(unique_assets)} unique assets")

    by_type = {}
    for a in unique_assets:
        t = a.get("type", "unknown")
        by_type[t] = by_type.get(t, 0) + 1
    print(f"  Types: {by_type}")

    assets_path = os.path.join(case_dir, "assets.json")
    with open(assets_path, "w") as f:
        json.dump(unique_assets, f, indent=2, ensure_ascii=False)
    print(f"\nSaved to {assets_path}")

    if not args.skip_download:
        url_map = collect_downloadable_urls(unique_assets)
        if url_map:
            url_map_path = os.path.join(case_dir, "url_map.json")
            with open(url_map_path, "w") as f:
                json.dump(url_map, f, indent=2, ensure_ascii=False)

            media_dir = os.path.join(case_dir, "media")
            print(f"\nDownloading {len(url_map)} media files to {media_dir}/")
            download_all(url_map, media_dir)
        else:
            print("\nNo downloadable URLs found in assets.")


if __name__ == "__main__":
    main()
