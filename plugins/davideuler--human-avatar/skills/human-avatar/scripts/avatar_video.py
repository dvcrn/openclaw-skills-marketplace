#!/usr/bin/env python3
"""灵眸：基于模板创建播报视频并轮询结果。"""
import argparse
import os
import sys
import time
import urllib.request


def create_client():
    try:
        from alibabacloud_lingmou20250527.client import Client
        from alibabacloud_tea_openapi import models as open_api_models
    except Exception as e:
        raise RuntimeError(
            "需要安装: pip install alibabacloud-lingmou20250527 alibabacloud-tea-openapi"
        ) from e

    config = open_api_models.Config(
        access_key_id=os.environ["ALIBABA_CLOUD_ACCESS_KEY_ID"],
        access_key_secret=os.environ["ALIBABA_CLOUD_ACCESS_KEY_SECRET"],
        endpoint=os.environ.get("LINGMOU_ENDPOINT", "lingmou.cn-beijing.aliyuncs.com"),
        region_id=os.environ.get("LINGMOU_REGION", "cn-beijing"),
    )
    return Client(config)


def submit_video(client, template_id: str, text: str, name: str, resolution: str, fps: int, watermark: bool):
    from alibabacloud_lingmou20250527 import models as lm

    req = lm.CreateBroadcastVideoFromTemplateRequest(
        template_id=template_id,
        name=name,
        variables=[
            lm.TemplateVariable(
                name="text_content",
                type="text",
                properties={"content": text},
            )
        ],
        video_options=lm.CreateBroadcastVideoFromTemplateRequestVideoOptions(
            resolution=resolution,
            fps=fps,
            watermark=watermark,
        ),
    )
    resp = client.create_broadcast_video_from_template(req)
    video_id = resp.body.data.id
    return video_id


def wait_video(client, video_id: str, interval: int = 3, max_wait: int = 1800):
    from alibabacloud_lingmou20250527 import models as lm

    start = time.time()
    while time.time() - start < max_wait:
        req = lm.ListBroadcastVideosByIdRequest(video_ids=[video_id])
        resp = client.list_broadcast_videos_by_id(req)
        data = resp.body.data or []
        if not data:
            time.sleep(interval)
            continue

        video = data[0]
        status = video.status
        print(f"status={status}")
        if status == "SUCCESS":
            return video.video_url
        if status in ("ERROR", "FAILED"):
            raise RuntimeError(f"LingMou task failed: {status}")

        time.sleep(interval)

    raise TimeoutError("LingMou polling timeout")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--template-id", required=True)
    p.add_argument("--text")
    p.add_argument("--text-file")
    p.add_argument("--name", default="OpenClaw Avatar Video")
    p.add_argument("--resolution", default="720p", choices=["720p", "1080p"])
    p.add_argument("--fps", type=int, default=30, choices=[15, 30])
    p.add_argument("--watermark", action="store_true", default=False)
    p.add_argument("--download", action="store_true")
    p.add_argument("--output", default="lingmou_output.mp4")
    args = p.parse_args()

    text = args.text
    if args.text_file:
        text = open(args.text_file, "r", encoding="utf-8").read().strip()
    if not text:
        p.error("Need --text or --text-file")

    client = create_client()
    video_id = submit_video(
        client,
        template_id=args.template_id,
        text=text,
        name=args.name,
        resolution=args.resolution,
        fps=args.fps,
        watermark=args.watermark,
    )
    print(f"video_id={video_id}")
    video_url = wait_video(client, video_id)
    print(f"video_url={video_url}")

    if args.download and video_url:
        urllib.request.urlretrieve(video_url, args.output)
        print(f"saved={args.output}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
