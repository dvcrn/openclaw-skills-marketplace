#!/usr/bin/env python3
"""
天幕（Tomoviee）文生视频脚本

完整流程：获取鉴权token → 创建文生视频任务 → 轮询任务状态 → 下载视频

环境变量：
  TOMOVIEE_ACCESS_KEY  - 天幕平台的 Access Key（App Key）
  TOMOVIEE_SECRET      - 天幕平台的 Secret Key
"""

import argparse
import json
import os
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path


# API 端点
BASE_URL = "https://open-api.wondershare.cc"
GET_TOKEN_URL = f"{BASE_URL}/v1/open/capacity/get/token"
CREATE_TASK_URL = f"{BASE_URL}/v1/open/capacity/application/tm_text2video_b"
GET_RESULT_URL = f"{BASE_URL}/v1/open/pub/task"

# 任务状态
STATUS_MAP = {
    1: "排队中",
    2: "处理中",
    3: "处理成功",
    4: "处理失败",
    5: "已关闭/已取消",
    6: "已超时",
}


def get_credentials():
    """获取 access_key 和 secret"""
    access_key = os.environ.get("TOMOVIEE_ACCESS_KEY")
    secret = os.environ.get("TOMOVIEE_SECRET")

    if not access_key:
        print("错误：未设置环境变量 TOMOVIEE_ACCESS_KEY", file=sys.stderr)
        print("请设置：export TOMOVIEE_ACCESS_KEY=\"你的access_key\"", file=sys.stderr)
        print("获取地址：https://www.tomoviee.cn/developers.html", file=sys.stderr)
        sys.exit(1)

    if not secret:
        print("错误：未设置环境变量 TOMOVIEE_SECRET", file=sys.stderr)
        print("请设置：export TOMOVIEE_SECRET=\"你的secret\"", file=sys.stderr)
        print("获取地址：https://www.tomoviee.cn/developers.html", file=sys.stderr)
        sys.exit(1)

    return access_key, secret


def http_get(url, timeout=30):
    """发送 GET 请求"""
    req = urllib.request.Request(url, method="GET")
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8") if e.fp else ""
        print(f"HTTP 错误 {e.code}: {error_body}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"网络错误: {e.reason}", file=sys.stderr)
        sys.exit(1)


def http_post(url, data, headers, timeout=30):
    """发送 POST 请求"""
    json_data = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(url, data=json_data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8") if e.fp else ""
        print(f"HTTP 错误 {e.code}: {error_body}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"网络错误: {e.reason}", file=sys.stderr)
        sys.exit(1)


def get_access_token(access_key, secret):
    """
    步骤1：通过 access_key 和 secret 获取 access_token

    调用接口：GET /v1/open/capacity/get/token?access_key={key}&secret={secret}
    返回的 access_token 已包含 "Basic " 前缀，可直接用于 Authorization header
    """
    url = f"{GET_TOKEN_URL}?access_key={access_key}&secret={secret}"
    print("正在获取鉴权 token...")

    result = http_get(url)

    if result.get("code") != 0:
        print(f"获取 token 失败: {result.get('msg', '未知错误')}", file=sys.stderr)
        print("请检查 access_key 和 secret 是否正确", file=sys.stderr)
        sys.exit(1)

    access_token = result["data"]["access_token"]
    print("鉴权 token 获取成功！")
    return access_token


def make_auth_headers(access_key, access_token):
    """构造认证请求头"""
    return {
        "Content-Type": "application/json",
        "X-App-Key": access_key,
        "Authorization": access_token,  # 已包含 "Basic " 前缀
    }


def create_task(prompt, access_key, access_token, duration=5, resolution="720p",
                aspect_ratio="16:9", camera_move_index=None, callback=None, params=None):
    """
    步骤2：创建文生视频任务

    POST /v1/open/capacity/application/tm_text2video_b
    返回 task_id 用于后续轮询
    """
    body = {"prompt": prompt}

    if duration is not None:
        body["duration"] = duration
    if resolution is not None:
        body["resolution"] = resolution
    if aspect_ratio is not None:
        body["aspect_ratio"] = aspect_ratio
    if camera_move_index is not None:
        body["camera_move_index"] = camera_move_index
    if callback is not None:
        body["callback"] = callback
    if params is not None:
        body["params"] = params

    print(f"\n正在创建文生视频任务...")
    print(f"  Prompt: {prompt}")
    print(f"  时长: {duration}s | 分辨率: {resolution} | 比例: {aspect_ratio}")

    headers = make_auth_headers(access_key, access_token)
    result = http_post(CREATE_TASK_URL, body, headers)

    if result.get("code") != 0:
        print(f"创建任务失败: code={result.get('code')} msg={result.get('msg', '未知错误')}", file=sys.stderr)
        sys.exit(1)

    task_id = result["data"]["task_id"]
    print(f"任务创建成功！Task ID: {task_id}")
    return task_id


def poll_task(task_id, access_key, access_token, poll_interval=10, max_wait=600):
    """
    步骤3：轮询任务状态直到完成

    POST /v1/open/pub/task
    状态: 1-排队中 2-处理中 3-成功 4-失败 5-已取消 6-已超时
    """
    headers = make_auth_headers(access_key, access_token)
    start_time = time.time()

    while True:
        elapsed = time.time() - start_time
        if elapsed > max_wait:
            print(f"\n任务等待超时（已等待 {max_wait} 秒）", file=sys.stderr)
            sys.exit(1)

        result = http_post(GET_RESULT_URL, {"task_id": task_id}, headers)

        data = result.get("data")
        if data is None:
            print(f"\n查询任务失败: code={result.get('code')} msg={result.get('msg', '未知错误')}", file=sys.stderr)
            sys.exit(1)

        status = data.get("status", 0)
        progress = data.get("progress", 0)
        reason = data.get("reason", "")
        status_text = STATUS_MAP.get(status, f"未知状态({status})")

        print(f"\r  状态: {status_text} | 进度: {progress}% | 已等待: {int(elapsed)}s", end="", flush=True)

        if status == 3:  # 处理成功
            print()
            return data

        if status in (4, 5, 6):  # 失败/取消/超时
            print()
            print(f"任务{status_text}: {reason}", file=sys.stderr)
            if "insufficient balance" in reason.lower():
                print("提示：账户积分不足，请前往 https://app.tomoviee.cn/pricing 充值", file=sys.stderr)
            sys.exit(1)

        time.sleep(poll_interval)


def download_video(video_url, output_dir):
    """可选步骤：下载生成的视频文件到本地"""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"tomoviee_video_{timestamp}.mp4"
    filepath = output_path / filename

    print(f"正在下载视频到 {filepath}...")

    try:
        req = urllib.request.Request(video_url)
        with urllib.request.urlopen(req, timeout=120) as response:
            with open(filepath, "wb") as f:
                total = 0
                while True:
                    chunk = response.read(8192)
                    if not chunk:
                        break
                    f.write(chunk)
                    total += len(chunk)
    except Exception as e:
        print(f"下载视频失败: {e}", file=sys.stderr)
        sys.exit(1)

    file_size = filepath.stat().st_size
    print(f"视频下载完成！文件大小: {file_size / 1024 / 1024:.2f} MB")
    return str(filepath)


def main():
    parser = argparse.ArgumentParser(
        description="天幕文生视频 - 将文字描述转化为AI视频"
    )
    parser.add_argument("--prompt", required=True, help="视频描述文字（必填）")
    parser.add_argument("--duration", type=int, default=5, choices=[5, 10],
                        help="视频时长（秒），支持 5 或 10（默认: 5）")
    parser.add_argument("--resolution", default="720p", choices=["480p", "720p", "1080p"],
                        help="视频分辨率（默认: 720p）")
    parser.add_argument("--aspect_ratio", default="16:9",
                        choices=["16:9", "9:16", "1:1", "3:4", "4:3"],
                        help="视频画面比例（默认: 16:9）")
    parser.add_argument("--camera_move_index", type=int, default=None,
                        help="镜头运动类型索引（可选）")
    parser.add_argument("--callback", default=None, help="回调地址（可选）")
    parser.add_argument("--params", default=None, help="透传参数（可选）")
    parser.add_argument("--download", action="store_true", default=False,
                        help="是否下载视频到本地（默认仅输出视频链接）")
    parser.add_argument("--output", default=os.path.expanduser("~/Desktop"),
                        help="视频下载目录，仅在 --download 时生效（默认: ~/Desktop/）")
    parser.add_argument("--poll_interval", type=int, default=10,
                        help="轮询间隔秒数（默认: 10）")
    parser.add_argument("--max_wait", type=int, default=600,
                        help="最大等待秒数（默认: 600）")

    args = parser.parse_args()

    # 步骤1：获取凭证
    access_key, secret = get_credentials()

    # 步骤2：获取鉴权 token
    access_token = get_access_token(access_key, secret)

    # 步骤3：创建文生视频任务
    task_id = create_task(
        prompt=args.prompt,
        access_key=access_key,
        access_token=access_token,
        duration=args.duration,
        resolution=args.resolution,
        aspect_ratio=args.aspect_ratio,
        camera_move_index=args.camera_move_index,
        callback=args.callback,
        params=args.params,
    )

    # 步骤4：轮询等待任务完成
    print("\n等待视频生成中...")
    task_data = poll_task(
        task_id, access_key, access_token,
        poll_interval=args.poll_interval,
        max_wait=args.max_wait,
    )

    # 步骤5：解析结果并下载视频
    result_str = task_data.get("result", "{}")
    try:
        result_data = json.loads(result_str)
    except json.JSONDecodeError:
        print(f"解析任务结果失败: {result_str}", file=sys.stderr)
        sys.exit(1)

    video_paths = result_data.get("video_path", [])
    if not video_paths:
        print("任务成功但未返回视频路径", file=sys.stderr)
        sys.exit(1)

    # 输出结果摘要
    print("\n" + "=" * 50)
    print("视频生成完成！")
    print(f"  Prompt: {args.prompt}")
    if result_data.get("translate_prompt"):
        print(f"  翻译后 Prompt: {result_data['translate_prompt']}")
    if result_data.get("model_version"):
        print(f"  模型版本: {result_data['model_version']}")

    print(f"  视频链接:")
    for url in video_paths:
        print(f"    {url}")

    if args.download:
        print(f"\n正在下载视频...")
        for video_url in video_paths:
            download_video(video_url, args.output)

    print("=" * 50)

    # 最后一行输出第一个视频链接，供调用方使用
    print(video_paths[0])


if __name__ == "__main__":
    main()
