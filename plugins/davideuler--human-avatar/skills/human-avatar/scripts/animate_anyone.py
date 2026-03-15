#!/usr/bin/env python3
"""AA/AnimateAnyone（DashScope 异步任务）
说明：AA 模型名可能迭代，请通过 --model 指定当前可用模型名。
"""
import argparse
import json
import os
import sys
import time
import urllib.request
from pathlib import Path

import requests

BASE_URL = os.getenv("DASHSCOPE_BASE_URL", "https://dashscope.aliyuncs.com")


def headers(async_mode=False):
    key = os.getenv("DASHSCOPE_API_KEY")
    if not key:
        raise RuntimeError("Missing DASHSCOPE_API_KEY")
    h = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    if async_mode:
        h["X-DashScope-Async"] = "enable"
    return h


def upload_to_oss(local_path: str) -> str:
    import oss2

    auth = oss2.Auth(
        os.environ["ALIBABA_CLOUD_ACCESS_KEY_ID"],
        os.environ["ALIBABA_CLOUD_ACCESS_KEY_SECRET"],
    )
    bucket = os.environ["OSS_BUCKET"]
    endpoint = os.environ.get("OSS_ENDPOINT", "oss-cn-beijing.aliyuncs.com")
    client = oss2.Bucket(auth, f"https://{endpoint}", bucket)
    key = f"human-avatar/{Path(local_path).name}"
    client.put_object_from_file(key, local_path)
    return f"https://{bucket}.{endpoint}/{key}"


def submit(model: str, image_url: str, video_url: str, mode: str = "wan-std") -> str:
    url = f"{BASE_URL}/api/v1/services/aigc/image2video/video-synthesis"
    payload = {
        "model": model,
        "input": {"image_url": image_url, "video_url": video_url},
        "parameters": {"mode": mode},
    }
    r = requests.post(url, headers=headers(async_mode=True), json=payload, timeout=120)
    r.raise_for_status()
    data = r.json()
    task_id = data.get("output", {}).get("task_id")
    if not task_id:
        raise RuntimeError(json.dumps(data, ensure_ascii=False))
    return task_id


def wait(task_id: str, interval: int = 15, max_wait: int = 1800) -> str:
    url = f"{BASE_URL}/api/v1/tasks/{task_id}"
    start = time.time()
    while time.time() - start < max_wait:
        r = requests.get(url, headers=headers(), timeout=60)
        r.raise_for_status()
        data = r.json()
        status = data.get("output", {}).get("task_status")
        print(f"status={status}")
        if status == "SUCCEEDED":
            return data.get("output", {}).get("results", {}).get("video_url")
        if status in ("FAILED", "CANCELED", "UNKNOWN"):
            raise RuntimeError(json.dumps(data, ensure_ascii=False))
        time.sleep(interval)
    raise TimeoutError("Task timeout")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--model", required=True, help="AA 模型名（按阿里云文档填写）")
    p.add_argument("--image-url")
    p.add_argument("--video-url")
    p.add_argument("--image")
    p.add_argument("--video")
    p.add_argument("--mode", default="wan-std", choices=["wan-std", "wan-pro"])
    p.add_argument("--download", action="store_true")
    p.add_argument("--output", default="aa_output.mp4")
    args = p.parse_args()

    image_url = args.image_url or (upload_to_oss(args.image) if args.image else None)
    video_url = args.video_url or (upload_to_oss(args.video) if args.video else None)
    if not image_url or not video_url:
        p.error("Need --image-url/--image and --video-url/--video")

    task_id = submit(args.model, image_url, video_url, mode=args.mode)
    print(f"task_id={task_id}")
    video_out = wait(task_id)
    print(f"video_url={video_out}")

    if args.download and video_out:
        urllib.request.urlretrieve(video_out, args.output)
        print(f"saved={args.output}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
