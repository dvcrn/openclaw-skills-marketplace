#!/usr/bin/env python3
"""
Orchestrate vidu flow: optional image upload → submit task → return task_id.
No wait mode: caller uses task_id to query status/result via get_task_result.py or GET API.

Usage:
  export VIDU_TOKEN=your_token
  # 文生视频
  python run_vidu_generation.py text2video --prompt "hello apple"
  # 图生视频 (1 张图 + 文字)
  python run_vidu_generation.py img2video --prompt "穿上一件羽绒服" --image ./photo.jpg
  # 首尾帧生视频 (2 张图: 首帧、尾帧 + 文字)
  python run_vidu_generation.py headtailimg2video --prompt "..." --image ./frame1.jpg --image ./frame2.jpg
  # 参考生视频 (2-7 张图 + 文字, Q2 only)
  python run_vidu_generation.py character2video --prompt "..." --image ./a.jpg --image ./b.jpg [...]
  # 参考生视频 (图+主体+文字，文字必填; Q2 only)
  python run_vidu_generation.py character2video --prompt "..." --material "name:id:version" [...]
  python run_vidu_generation.py character2video --prompt "..." --image ./a.jpg --material "name:id:version" [...]

Options:
  --prompt "text"          (required; for character2video text is always required)
  --image path             (img2video: 1; headtailimg2video: 2; character2video: image+subject combined at most 7)
  --material "name:id:version"  (character2video only; image+subject combined at most 7)
  --duration 8  --resolution 1080p  --aspect-ratio "16:9"  (aspect_ratio not sent for img2video)
  --model-version 3.2 | 3.1  --transition pro | speed  (transition not sent for character2video or text2video Q2)

Output: Prints task_id to stdout and exits 0. To query task status/result, use get_task_result.py <task_id>.
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent


def run(cmd: list[str], capture: bool = True) -> tuple[int, str]:
    r = subprocess.run(
        cmd,
        capture_output=capture,
        text=True,
        cwd=SCRIPT_DIR,
    )
    out = (r.stdout or "").strip() if capture else ""
    if capture and r.stderr:
        err = (r.stderr or "").strip()
        if err and r.returncode != 0:
            sys.stderr.write(err + "\n")
    return r.returncode, out


def main() -> int:
    ap = argparse.ArgumentParser(description="Run full vidu generation flow")
    ap.add_argument("task_type", choices=("text2video", "img2video", "headtailimg2video", "character2video"))
    ap.add_argument("--prompt", help="Text prompt (required except character2video with --material only)")
    ap.add_argument("--image", action="append", dest="images", help="Image path(s): img2video=1, headtail=2, character2video=2-7")
    ap.add_argument("--material", action="append", help="character2video only: name:id:version (1-7 material elements)")
    ap.add_argument("--duration", type=int, default=8)
    ap.add_argument("--resolution", default="1080p")
    ap.add_argument("--aspect-ratio", default="16:9")
    ap.add_argument("--model-version", default="3.2")
    ap.add_argument("--transition", default="pro")
    args = ap.parse_args()

    # Validate image count per 任务支持列表
    images = args.images or []
    materials = args.material or []
    if args.task_type == "img2video" and len(images) != 1:
        print(json.dumps({"error": "img2video requires exactly 1 --image"}), file=sys.stderr)
        return 1
    if args.task_type == "headtailimg2video" and len(images) != 2:
        print(json.dumps({"error": "headtailimg2video requires exactly 2 --image (首帧, 尾帧)"}), file=sys.stderr)
        return 1
    if args.task_type == "character2video":
        if not args.prompt:
            print(json.dumps({"error": "character2video requires --prompt (text is required)"}), file=sys.stderr)
            return 1
        if len(images) + len(materials) > 7:
            print(json.dumps({"error": "character2video: image + subject combined at most 7 (got %d image + %d material)" % (len(images), len(materials))}), file=sys.stderr)
            return 1
        if len(images) == 0 and len(materials) == 0:
            print(json.dumps({"error": "character2video requires at least one of --image or --material (image and/or subject)"}), file=sys.stderr)
            return 1
    if args.task_type != "character2video" and not args.prompt:
        print(json.dumps({"error": "--prompt required for this task type"}), file=sys.stderr)
        return 1

    image_uris = []
    use_images = args.task_type in ("img2video", "headtailimg2video", "character2video") and images
    if use_images:
        for path in images:
            if not Path(path).is_file():
                print(json.dumps({"error": f"Image not found: {path}"}), file=sys.stderr)
                return 1
            code, out = run([sys.executable, str(SCRIPT_DIR / "upload_image.py"), path])
            if code != 0:
                print(json.dumps({"error": "upload failed", "output": out}), file=sys.stderr)
                return 1
            image_uris.append(out.strip())

    # Submit (submit_task.py omits aspect_ratio for img2video, transition for character2video and text2video Q2)
    submit_cmd = [
        sys.executable, str(SCRIPT_DIR / "submit_task.py"),
        "--type", args.task_type,
        "--duration", str(args.duration),
        "--resolution", args.resolution,
        "--model-version", args.model_version,
        "--transition", args.transition,
    ]
    if args.prompt:
        submit_cmd += ["--prompt", args.prompt]
    if args.task_type != "img2video":
        submit_cmd += ["--aspect-ratio", args.aspect_ratio]
    for u in image_uris:
        submit_cmd += ["--image-uri", u]
    for m in materials:
        submit_cmd += ["--material", m]
    code, task_id_out = run(submit_cmd)
    if code != 0:
        return 1
    task_id = task_id_out.strip()
    if not task_id:
        print(json.dumps({"error": "submit returned no task_id"}), file=sys.stderr)
        return 1

    print(task_id)
    return 0


if __name__ == "__main__":
    sys.exit(main())
