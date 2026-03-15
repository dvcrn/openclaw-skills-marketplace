#!/usr/bin/env python3
"""
LinkFoxAI CLI - Call LinkFox AI Open Platform APIs.

Auth: LINKFOXAI_APP_ID + LINKFOXAI_APP_SECRET (sign) or LINKFOXAI_API_KEY (Bearer).
Base URL: https://sbappstoreapi.ziniao.com/openapi-router (or set LINKFOXAI_BASE_URL).

Commands:
    material-list   --type 1                                     # 作图素材（连通性测试）
    upload-base64   --file image.png                             # base64 上传
    change-model    --image-url <url> --head-url <url> ...       # AI 换模特
    make-info       --id <task_id>                               # 查询作图结果（单次）
    poll            --id <task_id> [--interval 3] [--timeout 300]# 轮询作图结果直到完成
    chat            --content "你好" [--model 1]                  # AI 对话
    cutout          --image-url <url> --sub-type 1               # 自动抠图
    scene-fission   --image-url <url> ...                        # 场景裂变
    expand-image    --image-url <url> --width 1024 --height 1024 # 智能扩图
    super-resolution --image-url <url> --magnification 2         # 高清放大
    image-edit      --image-url <url> --prompt "描述"             # 智能修图
    erase           --image-url <url> --mask-url <url>           # 消除笔
    refresh         --id <image_id> [--format jpg]               # 刷新结果图片地址
    api-call        --path /linkfox-ai/... --body '{...}'        # 通用 API 调用
"""

import argparse
import base64
import hashlib
import json
import os
import sys
import time
import uuid
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

DEFAULT_BASE_URL = "https://sbappstoreapi.ziniao.com/openapi-router"
PATH_PREFIX = "/linkfox-ai"


def get_base_url() -> str:
    return os.environ.get("LINKFOXAI_BASE_URL", DEFAULT_BASE_URL).rstrip("/")


def get_credentials():
    app_id = os.environ.get("LINKFOXAI_APP_ID")
    app_secret = os.environ.get("LINKFOXAI_APP_SECRET")
    api_key = os.environ.get("LINKFOXAI_API_KEY")
    if app_id and app_secret:
        return app_id, app_secret, None
    if api_key:
        return None, None, api_key
    return None, None, None


def build_sign_headers(app_id: str, app_secret: str) -> dict:
    ts = str(int(time.time() * 1000))
    trace_id = uuid.uuid4().hex.upper()
    noce = uuid.uuid4().hex[:6].upper()
    raw = app_id + trace_id + ts + noce + app_secret
    sign = hashlib.sha256(raw.encode()).hexdigest().upper()
    return {
        "Content-Type": "application/json",
        "appId": app_id,
        "ts": ts,
        "traceId": trace_id,
        "noce": noce,
        "sign": sign,
        "User-Agent": "LinkFoxAI-Skill/1.0",
    }


def build_auth_headers() -> dict:
    app_id, app_secret, api_key = get_credentials()
    if app_id and app_secret:
        return build_sign_headers(app_id, app_secret)
    if api_key:
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
            "User-Agent": "LinkFoxAI-Skill/1.0",
        }
    print(
        "Error: Set LINKFOXAI_APP_ID + LINKFOXAI_APP_SECRET, or LINKFOXAI_API_KEY.\n"
        "See: https://open.ziniao.com",
        file=sys.stderr,
    )
    sys.exit(1)


def api_post(path: str, body: dict, timeout: int = 60) -> dict:
    base = get_base_url()
    url = base + path
    data = json.dumps(body).encode("utf-8")
    headers = build_auth_headers()
    req = Request(url, data=data, headers=headers, method="POST")
    try:
        with urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except HTTPError as e:
        raw = e.read().decode("utf-8") if e.fp else ""
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return {"code": str(e.code), "msg": e.reason, "details": raw}
    except URLError as e:
        return {"error": f"Connection failed: {e.reason}"}
    except Exception as e:
        return {"error": str(e)}


def extract_code(resp: dict):
    """Extract status code from nested open-platform response."""
    if "data" in resp and isinstance(resp["data"], dict):
        inner = resp["data"]
        if "code" in inner:
            return str(inner.get("code", ""))
    return str(resp.get("code", ""))


def is_success(resp: dict) -> bool:
    code = extract_code(resp)
    return code in ("200", "0")


# ─── Polling ────────────────────────────────────────────────────────────

def poll_make_info(task_id, interval: int = 3, timeout: int = 300) -> dict:
    """Poll make-info until status is 3 (success) or 4 (fail), or timeout."""
    start = time.time()
    last_status = None
    while True:
        elapsed = time.time() - start
        if elapsed > timeout:
            return {"error": f"Polling timeout after {timeout}s", "last_status": last_status}
        resp = api_post(f"{PATH_PREFIX}/image/v2/make/info", {"id": int(task_id)})
        data = resp.get("data", resp)
        if isinstance(data, dict) and "data" in data:
            data = data["data"]
        status = data.get("status") if isinstance(data, dict) else None
        last_status = status
        if status == 3:
            return resp
        if status == 4:
            return resp
        remaining = timeout - (time.time() - start)
        if remaining <= 0:
            return {"error": f"Polling timeout after {timeout}s", "last_status": last_status}
        print(f"[poll] status={status}, elapsed={int(elapsed)}s, next check in {interval}s...", file=sys.stderr)
        time.sleep(min(interval, remaining))


# ─── Command implementations ───────────────────────────────────────────

def cmd_material_list(typ: str, page_num: int = 1, page_size: int = 10) -> dict:
    return api_post(f"{PATH_PREFIX}/image/v2/material/list",
                    {"type": typ, "pageNum": page_num, "pageSize": page_size})


def cmd_upload_base64(file_path: str) -> dict:
    with open(file_path, "rb") as f:
        raw = f.read()
    b64 = base64.b64encode(raw).decode("ascii")
    name = os.path.basename(file_path)
    return api_post(f"{PATH_PREFIX}/image/v2/uploadByBase64", {"fileName": name, "base64": b64})


def cmd_change_model(image_url, head_url, scene_url=None, output_num=1) -> dict:
    body = {"imageUrl": image_url, "modelHeadImageUrl": head_url, "outputNum": output_num}
    if scene_url:
        body["sceneImgUrl"] = scene_url
    return api_post(f"{PATH_PREFIX}/image/v2/make/changeModel", body)


def cmd_make_info(task_id) -> dict:
    tid = int(task_id) if isinstance(task_id, str) and task_id.isdigit() else task_id
    return api_post(f"{PATH_PREFIX}/image/v2/make/info", {"id": tid})


def cmd_chat(content: str, model_param: int = 1) -> dict:
    return api_post(f"{PATH_PREFIX}/chat/v1/stream/completion/create", {
        "content": content,
        "modelParam": model_param,
        "checkSensitiveWord": False,
        "maxTokens": 2000,
        "temperature": 0.7,
    })


def cmd_cutout(image_url: str, sub_type: int, cloth_class: str = None) -> dict:
    body = {"imageUrl": image_url, "subType": sub_type}
    if cloth_class:
        body["clothClass"] = cloth_class
    return api_post(f"{PATH_PREFIX}/image/v2/make/cutout", body)


def cmd_scene_fission(image_url: str, strength: str = None, prompt: str = None,
                      provider: str = None, output_num: int = 1) -> dict:
    body = {"imageUrl": image_url, "outputNum": output_num}
    if strength:
        body["strength"] = strength
    if prompt:
        body["prompt"] = prompt
    if provider:
        body["provider"] = provider
    return api_post(f"{PATH_PREFIX}/image/v2/make/sceneFission", body)


def cmd_expand_image(image_url: str, width: int, height: int,
                     prompt: str = None, output_num: int = 1) -> dict:
    body = {"imageUrl": image_url, "width": width, "height": height, "outputNum": output_num}
    if prompt:
        body["prompt"] = prompt
    return api_post(f"{PATH_PREFIX}/image/v2/make/expandImage", body)


def cmd_super_resolution(image_url: str, magnification: float, enhance: bool = False) -> dict:
    body = {"imageUrl": image_url, "magnification": str(magnification), "enhanceQuality": enhance}
    return api_post(f"{PATH_PREFIX}/image/v2/make/superResolution", body)


def cmd_image_edit(image_url: str, prompt: str, output_num: int = 1,
                   pro: bool = False, template: str = None) -> dict:
    body = {"imageUrl": image_url, "prompt": prompt, "outputNum": output_num}
    if pro:
        body["pro"] = True
    if template:
        body["template"] = template
    return api_post(f"{PATH_PREFIX}/image/v2/make/imageEdit", body)


def cmd_erase(image_url: str, mask_url: str) -> dict:
    return api_post(f"{PATH_PREFIX}/image/v2/make/interactErase",
                    {"imageUrl": image_url, "maskImageUrl": mask_url})


def cmd_refresh(image_id, fmt: str = None) -> dict:
    body = {"id": int(image_id)}
    if fmt:
        body["downloadFormat"] = fmt
    return api_post(f"{PATH_PREFIX}/image/v2/info", body)


def cmd_api_call(path: str, body_str: str) -> dict:
    try:
        body = json.loads(body_str)
    except json.JSONDecodeError as e:
        return {"error": f"Invalid JSON body: {e}"}
    return api_post(path, body)


# ─── CLI ────────────────────────────────────────────────────────────────

def build_parser():
    parser = argparse.ArgumentParser(
        description="LinkFoxAI Open Platform CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # material-list
    p = sub.add_parser("material-list", help="作图素材列表（连通性测试）")
    p.add_argument("--type", required=True, help="素材类型 1-10")
    p.add_argument("--page", type=int, default=1)
    p.add_argument("--size", type=int, default=10)

    # upload-base64
    p = sub.add_parser("upload-base64", help="base64 上传图片")
    p.add_argument("--file", required=True, help="图片文件路径")

    # change-model
    p = sub.add_parser("change-model", help="AI 换模特")
    p.add_argument("--image-url", required=True)
    p.add_argument("--head-url", required=True)
    p.add_argument("--scene-url", default=None)
    p.add_argument("--output-num", type=int, default=1, choices=[1, 2, 3, 4])
    p.add_argument("--wait", action="store_true", help="提交后自动轮询结果")
    p.add_argument("--timeout", type=int, default=300)
    p.add_argument("--interval", type=int, default=3)

    # make-info
    p = sub.add_parser("make-info", help="查询作图结果（单次）")
    p.add_argument("--id", required=True)

    # poll
    p = sub.add_parser("poll", help="轮询作图结果直到完成")
    p.add_argument("--id", required=True)
    p.add_argument("--interval", type=int, default=3)
    p.add_argument("--timeout", type=int, default=300)

    # chat
    p = sub.add_parser("chat", help="AI 对话（非流式）")
    p.add_argument("--content", required=True)
    p.add_argument("--model", type=int, default=1)

    # cutout
    p = sub.add_parser("cutout", help="自动抠图")
    p.add_argument("--image-url", required=True)
    p.add_argument("--sub-type", type=int, required=True, help="1=通用 2=人像 3=商品 9=服饰 12=头发 13=人脸")
    p.add_argument("--cloth-class", default=None, help="服饰分类(subType=9): tops,coat,skirt,pants,bag,shoes,hat")
    p.add_argument("--wait", action="store_true")
    p.add_argument("--timeout", type=int, default=300)
    p.add_argument("--interval", type=int, default=3)

    # scene-fission
    p = sub.add_parser("scene-fission", help="场景裂变")
    p.add_argument("--image-url", required=True)
    p.add_argument("--strength", default=None)
    p.add_argument("--prompt", default=None)
    p.add_argument("--provider", default=None, help="SCENE_FISSION_REALISTIC/SIMPLE/INTELLIGENT")
    p.add_argument("--output-num", type=int, default=1)
    p.add_argument("--wait", action="store_true")
    p.add_argument("--timeout", type=int, default=300)
    p.add_argument("--interval", type=int, default=3)

    # expand-image
    p = sub.add_parser("expand-image", help="智能扩图")
    p.add_argument("--image-url", required=True)
    p.add_argument("--width", type=int, required=True)
    p.add_argument("--height", type=int, required=True)
    p.add_argument("--prompt", default=None)
    p.add_argument("--output-num", type=int, default=1)
    p.add_argument("--wait", action="store_true")
    p.add_argument("--timeout", type=int, default=300)
    p.add_argument("--interval", type=int, default=3)

    # super-resolution
    p = sub.add_parser("super-resolution", help="图片高清放大")
    p.add_argument("--image-url", required=True)
    p.add_argument("--magnification", type=float, required=True, help="放大倍数 [1,4]")
    p.add_argument("--enhance", action="store_true", help="是否高清化")
    p.add_argument("--wait", action="store_true")
    p.add_argument("--timeout", type=int, default=300)
    p.add_argument("--interval", type=int, default=3)

    # image-edit
    p = sub.add_parser("image-edit", help="智能修图")
    p.add_argument("--image-url", required=True)
    p.add_argument("--prompt", required=True)
    p.add_argument("--output-num", type=int, default=1)
    p.add_argument("--pro", action="store_true", help="高品质模式")
    p.add_argument("--template", default=None)
    p.add_argument("--wait", action="store_true")
    p.add_argument("--timeout", type=int, default=300)
    p.add_argument("--interval", type=int, default=3)

    # erase
    p = sub.add_parser("erase", help="消除笔")
    p.add_argument("--image-url", required=True)
    p.add_argument("--mask-url", required=True, help="消除区域（黑白图，白色为消除区域）")
    p.add_argument("--wait", action="store_true")
    p.add_argument("--timeout", type=int, default=300)
    p.add_argument("--interval", type=int, default=3)

    # refresh
    p = sub.add_parser("refresh", help="刷新结果图片地址")
    p.add_argument("--id", required=True, help="图片 ID（非任务 ID）")
    p.add_argument("--format", default=None, help="下载格式：jpg/png")

    # api-call
    p = sub.add_parser("api-call", help="通用 API 调用（任意路径）")
    p.add_argument("--path", required=True, help="接口路径，如 /linkfox-ai/image/v2/make/aiDraw")
    p.add_argument("--body", required=True, help="请求体 JSON 字符串")

    return parser


def maybe_poll(resp: dict, args) -> dict:
    """If --wait is set and resp contains a task id, auto-poll."""
    if not getattr(args, "wait", False):
        return resp
    if not is_success(resp):
        return resp
    data = resp.get("data", resp)
    if isinstance(data, dict) and "data" in data:
        data = data["data"]
    task_id = data.get("id") if isinstance(data, dict) else None
    if not task_id:
        return resp
    print(f"[wait] Task created: {task_id}, polling...", file=sys.stderr)
    return poll_make_info(task_id, args.interval, args.timeout)


def main():
    parser = build_parser()
    args = parser.parse_args()
    out = None

    if args.command == "material-list":
        out = cmd_material_list(args.type, args.page, args.size)
    elif args.command == "upload-base64":
        out = cmd_upload_base64(args.file)
    elif args.command == "change-model":
        out = maybe_poll(cmd_change_model(args.image_url, args.head_url, args.scene_url, args.output_num), args)
    elif args.command == "make-info":
        out = cmd_make_info(args.id)
    elif args.command == "poll":
        out = poll_make_info(args.id, args.interval, args.timeout)
    elif args.command == "chat":
        out = cmd_chat(args.content, args.model)
    elif args.command == "cutout":
        out = maybe_poll(cmd_cutout(args.image_url, args.sub_type, args.cloth_class), args)
    elif args.command == "scene-fission":
        out = maybe_poll(cmd_scene_fission(args.image_url, args.strength, args.prompt, args.provider, args.output_num), args)
    elif args.command == "expand-image":
        out = maybe_poll(cmd_expand_image(args.image_url, args.width, args.height, args.prompt, args.output_num), args)
    elif args.command == "super-resolution":
        out = maybe_poll(cmd_super_resolution(args.image_url, args.magnification, args.enhance), args)
    elif args.command == "image-edit":
        out = maybe_poll(cmd_image_edit(args.image_url, args.prompt, args.output_num, args.pro, args.template), args)
    elif args.command == "erase":
        out = maybe_poll(cmd_erase(args.image_url, args.mask_url), args)
    elif args.command == "refresh":
        out = cmd_refresh(args.id, getattr(args, "format", None))
    elif args.command == "api-call":
        out = cmd_api_call(args.path, args.body)

    if out is None:
        sys.exit(1)

    print(json.dumps(out, indent=2, ensure_ascii=False))
    if not is_success(out) and "error" not in out:
        sys.exit(1)


if __name__ == "__main__":
    main()
