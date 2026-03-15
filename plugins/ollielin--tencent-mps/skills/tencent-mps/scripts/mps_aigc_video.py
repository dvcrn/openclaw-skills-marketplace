#!/usr/bin/env python3
"""
腾讯云 MPS AIGC 智能生视频脚本

功能：
  使用 MPS AIGC 智能内容创作功能，通过输入文本、图片、视频等内容，生成视频结果。
  媒体处理汇聚多家大模型能力（Hunyuan / Hailuo / Kling / Vidu / OS / GV），
  提供一站式的调用。
  封装 CreateAigcVideoTask + DescribeAigcVideoTask 两个 API，
  支持创建任务 + 自动轮询等待结果。

支持的模型：
  - Hunyuan（腾讯混元）
  - Hailuo（海螺，版本 02 / 2.3）
  - Kling（可灵，版本 2.0 / 2.1 / 2.5 / O1 / 2.6 / 3.0 / 3.0-Omni）
  - Vidu（版本 q2 / q2-pro / q2-turbo / q3-pro / q3-turbo）
  - OS（版本 2.0）
  - GV（版本 3.1）

核心能力：
  - 文生视频（Text-to-Video）：输入文本描述生成视频
  - 图生视频（Image-to-Video）：输入首帧图片 + 文本描述生成视频
  - 首尾帧生视频：指定首帧和尾帧图片生成视频（部分模型支持）
  - 多图参考生视频（GV/Vidu）：最多3张参考图
  - 参考视频生视频（Kling O1）：基于参考视频进行编辑或特征参考
  - 特效场景（Kling 动作控制 / Vidu 特效模板等）
  - 自定义时长、分辨率、宽高比
  - 水印控制、音频生成、背景音乐
  - 结果存储到 COS

COS 存储配置（可选）：
  通过 --cos-bucket-name / --cos-bucket-region / --cos-bucket-path 参数，
  或环境变量 TENCENTCLOUD_COS_BUCKET / TENCENTCLOUD_COS_REGION 指定存储桶。
  不配置时使用 MPS 默认临时存储（视频存储12小时）。

用法：
  # 文生视频：最简用法（Hunyuan 模型）
  python mps_aigc_video.py --prompt "一只可爱的橘猫在阳光下伸懒腰"

  # 指定模型和版本
  python mps_aigc_video.py --prompt "赛博朋克城市夜景" --model Kling --model-version 2.5

  # 图生视频：首帧图片 + 描述
  python mps_aigc_video.py --prompt "让画面动起来" \
      --image-url https://example.com/photo.jpg

  # 首尾帧生视频（GV / Kling 2.1 / Vidu q2-pro）
  python mps_aigc_video.py --prompt "过渡动画" --model GV \
      --image-url https://example.com/start.jpg \
      --last-image-url https://example.com/end.jpg

  # GV 多图参考（最多3张，指定 asset/style）
  python mps_aigc_video.py --prompt "融合元素" --model GV \
      --ref-image-url https://example.com/img1.jpg --ref-image-type asset \
      --ref-image-url https://example.com/img2.jpg --ref-image-type style

  # Kling O1 参考视频（待编辑视频 + 保留原声）
  python mps_aigc_video.py --prompt "将视频风格化" --model Kling --model-version O1 \
      --ref-video-url https://example.com/video.mp4 --ref-video-type base --keep-original-sound yes

  # 指定时长、分辨率、宽高比
  python mps_aigc_video.py --prompt "日出延时" --model Kling --duration 10 \
      --resolution 1080P --aspect-ratio 16:9

  # Kling 动作控制场景
  python mps_aigc_video.py --prompt "人物行走" --model Kling --scene-type motion_control

  # 去除水印 + 生成音频 + 背景音乐
  python mps_aigc_video.py --prompt "产品展示" --model Kling \
      --no-logo --enable-audio true --enable-bgm

  # Vidu 错峰模式（48小时内生成）
  python mps_aigc_video.py --prompt "自然风景" --model Vidu --off-peak

  # 附加参数（JSON 格式，如相机控制）
  python mps_aigc_video.py --prompt "飞越城市" --model Kling \
      --additional-params '{"camera_control":{"type":"simple"}}'

  # 存储到 COS
  python mps_aigc_video.py --prompt "宣传片" \
      --cos-bucket-name mybucket-125xxx --cos-bucket-region ap-guangzhou

  # 仅创建任务（不等待结果）
  python mps_aigc_video.py --prompt "延时摄影" --no-wait

  # 查询已有任务结果
  python mps_aigc_video.py --task-id 1234567890-xxxxxxxxxxxxx

  # Dry Run（仅打印请求参数，不实际调用 API）
  python mps_aigc_video.py --prompt "测试视频" --dry-run

环境变量：
  TENCENTCLOUD_SECRET_ID   - 腾讯云 SecretId
  TENCENTCLOUD_SECRET_KEY  - 腾讯云 SecretKey
  TENCENTCLOUD_COS_BUCKET       - COS Bucket 名称（可选，用于结果存储）
  TENCENTCLOUD_COS_REGION       - COS Bucket 区域（默认 ap-guangzhou）
"""

import argparse
import json
import os
import sys
import time

try:
    from tencentcloud.common import credential
    from tencentcloud.common.profile.client_profile import ClientProfile
    from tencentcloud.common.profile.http_profile import HttpProfile
    from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
    from tencentcloud.mps.v20190612 import mps_client, models
except ImportError:
    print("错误：请先安装腾讯云 SDK：pip install tencentcloud-sdk-python", file=sys.stderr)
    sys.exit(1)


# =============================================================================
# 模型信息
# =============================================================================
SUPPORTED_MODELS = {
    "Hunyuan": {
        "description": "腾讯混元大模型",
        "versions": [],
        "duration_options": [],
        "default_duration": None,
    },
    "Hailuo": {
        "description": "海螺视频模型",
        "versions": ["02", "2.3"],
        "duration_options": [6, 10],
        "default_duration": 6,
    },
    "Kling": {
        "description": "可灵视频模型",
        "versions": ["2.0", "2.1", "2.5", "O1", "2.6", "3.0", "3.0-Omni"],
        "duration_options": [5, 10],
        "default_duration": 5,
    },
    "Vidu": {
        "description": "Vidu 视频模型",
        "versions": ["q2", "q2-pro", "q2-turbo", "q3-pro", "q3-turbo"],
        "duration_options": list(range(1, 11)),
        "default_duration": 4,
    },
    "OS": {
        "description": "OS 视频模型",
        "versions": ["2.0"],
        "duration_options": [4, 8, 12],
        "default_duration": 8,
    },
    "GV": {
        "description": "GV 视频模型",
        "versions": ["3.1"],
        "duration_options": [8],
        "default_duration": 8,
    },
}

# 场景类型
SCENE_TYPES = {
    "motion_control": "Kling — 动作控制",
    "land2port": "Mingmou — 横转竖",
    "template_effect": "Vidu — 特效模板",
}

# 轮询配置
DEFAULT_POLL_INTERVAL = 10   # 秒（视频生成较慢）
DEFAULT_MAX_WAIT = 600       # 最长等待10分钟


def get_cos_bucket():
    """从环境变量获取 COS Bucket 名称。"""
    return os.environ.get("TENCENTCLOUD_COS_BUCKET", "")


def get_cos_region():
    """从环境变量获取 COS Bucket 区域，默认 ap-guangzhou。"""
    return os.environ.get("TENCENTCLOUD_COS_REGION", "ap-guangzhou")


try:
    from load_env import ensure_env_loaded as _ensure_env_loaded
    _LOAD_ENV_AVAILABLE = True
except ImportError:
    _LOAD_ENV_AVAILABLE = False
    def _ensure_env_loaded(**kwargs):
        return False

def get_credentials():
    """从环境变量获取腾讯云凭证。若缺失则尝试从系统文件自动加载后重试。"""
    secret_id = os.environ.get("TENCENTCLOUD_SECRET_ID", "")
    secret_key = os.environ.get("TENCENTCLOUD_SECRET_KEY", "")
    if not secret_id or not secret_key:
        # 尝试从系统环境变量文件自动加载
        if _LOAD_ENV_AVAILABLE:
            print("[load_env] 环境变量未设置，尝试从系统文件自动加载...", file=sys.stderr)
            _ensure_env_loaded(verbose=True)
            secret_id = os.environ.get("TENCENTCLOUD_SECRET_ID", "")
            secret_key = os.environ.get("TENCENTCLOUD_SECRET_KEY", "")
        if not secret_id or not secret_key:
            if _LOAD_ENV_AVAILABLE:
                from load_env import _print_setup_hint, _TARGET_VARS
                _print_setup_hint(["TENCENTCLOUD_SECRET_ID", "TENCENTCLOUD_SECRET_KEY"])
            else:
                print(
                    "\n错误：TENCENTCLOUD_SECRET_ID / TENCENTCLOUD_SECRET_KEY 未设置。\n"
                    "请在 /etc/environment、~/.profile 等文件中添加这些变量后重新发起对话，\n"
                    "或直接在对话中发送变量值，由 AI 帮您配置。",
                    file=sys.stderr,
                )
            sys.exit(1)
    return credential.Credential(secret_id, secret_key)


def create_mps_client(cred, region):
    """创建 MPS 客户端。"""
    http_profile = HttpProfile()
    http_profile.endpoint = "mps.tencentcloudapi.com"
    http_profile.reqMethod = "POST"

    client_profile = ClientProfile()
    client_profile.httpProfile = http_profile

    return mps_client.MpsClient(cred, region, client_profile)


def build_create_params(args):
    """构建 CreateAigcVideoTask 请求参数。"""
    params = {}

    # 模型名称（必填）
    params["ModelName"] = args.model

    # 模型版本（可选）
    if args.model_version:
        params["ModelVersion"] = args.model_version

    # 场景类型（可选）
    if args.scene_type:
        params["SceneType"] = args.scene_type

    # 提示词
    if args.prompt:
        params["Prompt"] = args.prompt

    # 反向提示词
    if args.negative_prompt:
        params["NegativePrompt"] = args.negative_prompt

    # 提示词增强
    if args.enhance_prompt:
        params["EnhancePrompt"] = True

    # 首帧图片（简单模式）
    if args.image_url:
        params["ImageUrl"] = args.image_url

    # 尾帧图片
    if args.last_image_url:
        params["LastImageUrl"] = args.last_image_url

    # 多图参考（ImageInfos）
    if args.ref_image_url:
        image_infos = []
        ref_types = args.ref_image_type or []
        for i, url in enumerate(args.ref_image_url):
            info = {"ImageUrl": url}
            if i < len(ref_types):
                info["ReferenceType"] = ref_types[i]
            image_infos.append(info)
        params["ImageInfos"] = image_infos

    # 参考视频（VideoInfos）
    if args.ref_video_url:
        video_infos = []
        ref_types = args.ref_video_type or []
        keep_sounds = args.keep_original_sound or []
        for i, url in enumerate(args.ref_video_url):
            info = {"VideoUrl": url}
            if i < len(ref_types):
                info["ReferType"] = ref_types[i]
            if i < len(keep_sounds):
                info["KeepOriginalSound"] = keep_sounds[i]
            video_infos.append(info)
        params["VideoInfos"] = video_infos

    # 时长
    if args.duration is not None:
        params["Duration"] = args.duration

    # 额外参数（ExtraParameters）
    extra = {}
    if args.resolution:
        extra["Resolution"] = args.resolution
    if args.aspect_ratio:
        extra["AspectRatio"] = args.aspect_ratio
    if args.no_logo:
        extra["LogoAdd"] = 0
    if args.enable_audio is not None:
        extra["EnableAudio"] = args.enable_audio
    if args.off_peak:
        extra["OffPeak"] = True
    if args.enable_bgm:
        extra["EnableBgm"] = True
    if extra:
        params["ExtraParameters"] = extra

    # COS 存储
    cos_param = build_store_cos_param(args)
    if cos_param:
        params["StoreCosParam"] = cos_param

    # 附加参数（JSON 字符串）
    if args.additional_params:
        params["AdditionalParameters"] = args.additional_params

    # 操作者
    if args.operator:
        params["Operator"] = args.operator

    return params


def build_store_cos_param(args):
    """构建 COS 存储参数。"""
    bucket_name = args.cos_bucket_name or get_cos_bucket()
    bucket_region = args.cos_bucket_region or get_cos_region()

    if not bucket_name:
        return None

    cos_param = {
        "CosBucketName": bucket_name,
        "CosBucketRegion": bucket_region,
    }
    if args.cos_bucket_path:
        cos_param["CosBucketPath"] = args.cos_bucket_path

    return cos_param


def create_aigc_video_task(client, params):
    """调用 CreateAigcVideoTask API 创建生视频任务。"""
    req = models.CreateAigcVideoTaskRequest()
    req.from_json_string(json.dumps(params))
    resp = client.CreateAigcVideoTask(req)
    return json.loads(resp.to_json_string())


def describe_aigc_video_task(client, task_id):
    """调用 DescribeAigcVideoTask API 查询任务状态。"""
    req = models.DescribeAigcVideoTaskRequest()
    req.from_json_string(json.dumps({"TaskId": task_id}))
    resp = client.DescribeAigcVideoTask(req)
    return json.loads(resp.to_json_string())


def poll_task_result(client, task_id, poll_interval, max_wait):
    """轮询等待任务完成。"""
    elapsed = 0
    while elapsed < max_wait:
        result = describe_aigc_video_task(client, task_id)
        status = result.get("Status", "")

        if status == "DONE":
            return result
        elif status == "FAIL":
            message = result.get("Message", "未知错误")
            print(f"\n❌ 任务失败: {message}", file=sys.stderr)
            sys.exit(1)

        # 打印进度
        status_text = {"WAIT": "等待中", "RUN": "执行中"}.get(status, status)
        print(f"\r⏳ 任务状态: {status_text}（已等待 {elapsed}s / 最长 {max_wait}s）", end="", flush=True)

        time.sleep(poll_interval)
        elapsed += poll_interval

    print(f"\n⚠️  等待超时（已等待 {max_wait}s），任务仍在进行中。", file=sys.stderr)
    print(f"   请稍后使用 --task-id {task_id} 查询结果。", file=sys.stderr)
    sys.exit(1)


def validate_args(args, parser):
    """校验参数。"""
    # 如果是查询模式，不需要其他参数
    if args.task_id:
        return

    # 创建模式：至少需要 prompt 或 image_url
    if not args.prompt and not args.image_url and not args.ref_image_url:
        parser.error("请至少指定 --prompt（文本描述）或 --image-url（首帧图片）")

    # 模型版本校验
    model_info = SUPPORTED_MODELS.get(args.model)
    if model_info and args.model_version:
        valid_versions = model_info["versions"]
        if valid_versions and args.model_version not in valid_versions:
            parser.error(
                f"模型 {args.model} 支持的版本为: {', '.join(valid_versions)}，"
                f"当前指定: {args.model_version}"
            )

    # 尾帧图片校验：使用 GV 时必须同时传入首帧
    if args.last_image_url and not args.image_url:
        parser.error("--last-image-url 需要同时指定 --image-url 作为首帧图片")

    # 多图参考与 ImageUrl/LastImageUrl 互斥（GV 模型限制）
    if args.ref_image_url and (args.image_url or args.last_image_url):
        if args.model == "GV":
            parser.error("GV 模型使用多图参考（--ref-image-url）时，不可同时使用 --image-url / --last-image-url")

    # ref_image_type 数量不能超过 ref_image_url 数量
    if args.ref_image_type and args.ref_image_url:
        if len(args.ref_image_type) > len(args.ref_image_url):
            parser.error("--ref-image-type 数量不能超过 --ref-image-url 数量")
    elif args.ref_image_type and not args.ref_image_url:
        parser.error("--ref-image-type 需要配合 --ref-image-url 使用")

    # 参考视频校验
    if args.ref_video_url:
        if args.model != "Kling" or args.model_version != "O1":
            parser.error("参考视频（--ref-video-url）目前仅 Kling O1 版本支持")

    if args.ref_video_type and args.ref_video_url:
        if len(args.ref_video_type) > len(args.ref_video_url):
            parser.error("--ref-video-type 数量不能超过 --ref-video-url 数量")
    elif args.ref_video_type and not args.ref_video_url:
        parser.error("--ref-video-type 需要配合 --ref-video-url 使用")

    if args.keep_original_sound and not args.ref_video_url:
        parser.error("--keep-original-sound 需要配合 --ref-video-url 使用")

    # 错峰模式仅 Vidu 支持
    if args.off_peak and args.model != "Vidu":
        parser.error("错峰模式（--off-peak）目前仅 Vidu 模型支持")

    # 场景类型校验
    if args.scene_type:
        valid_scenes = {
            "Kling": ["motion_control"],
            "Vidu": ["template_effect"],
        }
        model_scenes = valid_scenes.get(args.model, [])
        if args.scene_type not in model_scenes and args.scene_type != "land2port":
            parser.error(
                f"模型 {args.model} 不支持场景类型 {args.scene_type}。"
                f"支持的场景: {', '.join(model_scenes) if model_scenes else '无'}"
            )


def run(args):
    """执行主流程。"""
    region = args.region or "ap-guangzhou"
    cred = get_credentials()
    client = create_mps_client(cred, region)

    # 模式1: 查询已有任务
    if args.task_id:
        print("=" * 60)
        print("腾讯云 MPS AIGC 生视频 — 查询任务")
        print("=" * 60)
        print(f"TaskId: {args.task_id}")
        print("-" * 60)

        try:
            result = describe_aigc_video_task(client, args.task_id)
            status = result.get("Status", "")
            status_text = {
                "WAIT": "等待中", "RUN": "执行中",
                "DONE": "已完成", "FAIL": "失败"
            }.get(status, status)

            print(f"任务状态: {status_text}")

            if status == "DONE":
                video_urls = result.get("VideoUrls", [])
                resolution = result.get("Resolution", "")
                print(f"视频分辨率: {resolution}")
                print(f"生成视频数量: {len(video_urls)}")
                for i, url in enumerate(video_urls, 1):
                    print(f"  视频 {i}: {url}")
                print("\n⚠️  视频存储12小时，请尽快下载使用。")
            elif status == "FAIL":
                print(f"失败原因: {result.get('Message', '未知')}")

            if args.verbose:
                print("\n完整响应：")
                print(json.dumps(result, ensure_ascii=False, indent=2))

        except TencentCloudSDKException as e:
            print(f"❌ 查询失败: {e}", file=sys.stderr)
            sys.exit(1)
        return

    # 模式2: 创建任务
    params = build_create_params(args)

    if args.dry_run:
        print("=" * 60)
        print("【Dry Run 模式】仅打印请求参数，不实际调用 API")
        print("=" * 60)
        print(json.dumps(params, ensure_ascii=False, indent=2))
        return

    # 打印执行信息
    print("=" * 60)
    print("腾讯云 MPS AIGC 智能生视频")
    print("=" * 60)
    model_info = SUPPORTED_MODELS.get(args.model, {})
    model_desc = model_info.get("description", args.model)
    print(f"模型: {args.model}（{model_desc}）")
    if args.model_version:
        print(f"版本: {args.model_version}")
    if args.scene_type:
        scene_desc = SCENE_TYPES.get(args.scene_type, args.scene_type)
        print(f"场景: {scene_desc}")
    if args.prompt:
        prompt_display = args.prompt[:80] + "..." if len(args.prompt) > 80 else args.prompt
        print(f"提示词: {prompt_display}")
    if args.negative_prompt:
        print(f"反向提示词: {args.negative_prompt}")
    if args.enhance_prompt:
        print("提示词增强: 开启")
    if args.image_url:
        print(f"首帧图片: {args.image_url}")
    if args.last_image_url:
        print(f"尾帧图片: {args.last_image_url}")
    if args.ref_image_url:
        print(f"参考图片: {len(args.ref_image_url)} 张")
        for i, url in enumerate(args.ref_image_url, 1):
            ref_type = ""
            if args.ref_image_type and i - 1 < len(args.ref_image_type):
                ref_type = f"（{args.ref_image_type[i - 1]}）"
            print(f"  图片 {i}{ref_type}: {url}")
    if args.ref_video_url:
        print(f"参考视频: {len(args.ref_video_url)} 个")
        for i, url in enumerate(args.ref_video_url, 1):
            ref_type = ""
            if args.ref_video_type and i - 1 < len(args.ref_video_type):
                ref_type = f"（{args.ref_video_type[i - 1]}）"
            keep_sound = ""
            if args.keep_original_sound and i - 1 < len(args.keep_original_sound):
                keep_sound = f" [原声: {args.keep_original_sound[i - 1]}]"
            print(f"  视频 {i}{ref_type}{keep_sound}: {url}")
    if args.duration is not None:
        print(f"时长: {args.duration}s")
    if args.resolution:
        print(f"分辨率: {args.resolution}")
    if args.aspect_ratio:
        print(f"宽高比: {args.aspect_ratio}")

    extras = []
    if args.no_logo:
        extras.append("去水印")
    if args.enable_audio is not None:
        extras.append(f"音频: {'开启' if args.enable_audio else '关闭'}")
    if args.enable_bgm:
        extras.append("背景音乐")
    if args.off_peak:
        extras.append("错峰模式")
    if extras:
        print(f"其他: {' | '.join(extras)}")
    print("-" * 60)

    if args.verbose:
        print("请求参数：")
        print(json.dumps(params, ensure_ascii=False, indent=2))
        print()

    try:
        result = create_aigc_video_task(client, params)
        task_id = result.get("TaskId", "N/A")
        request_id = result.get("RequestId", "N/A")

        print(f"✅ AIGC 生视频任务创建成功！")
        print(f"   TaskId: {task_id}")
        print(f"   RequestId: {request_id}")

        if args.no_wait:
            print(f"\n提示：使用以下命令查询任务结果：")
            print(f"  python mps_aigc_video.py --task-id {task_id}")
            return result

        # 自动轮询等待结果
        print(f"\n正在等待任务完成（轮询间隔 {args.poll_interval}s，最长等待 {args.max_wait}s）...")
        poll_result = poll_task_result(client, task_id, args.poll_interval, args.max_wait)

        video_urls = poll_result.get("VideoUrls", [])
        resolution = poll_result.get("Resolution", "")
        print(f"\n✅ 任务完成！")
        if resolution:
            print(f"   分辨率: {resolution}")
        print(f"   生成视频数量: {len(video_urls)}")
        for i, url in enumerate(video_urls, 1):
            print(f"   视频 {i}: {url}")
        print("\n⚠️  视频存储12小时，请尽快下载使用。")

        if args.verbose:
            print("\n完整响应：")
            print(json.dumps(poll_result, ensure_ascii=False, indent=2))

        return poll_result

    except TencentCloudSDKException as e:
        print(f"❌ 请求失败: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="腾讯云 MPS AIGC 智能生视频 —— 汇聚 Hunyuan/Hailuo/Kling/Vidu/OS/GV 等多家大模型，一站式文生视频、图生视频",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  # 文生视频（默认 Hunyuan 模型）
  python mps_aigc_video.py --prompt "一只可爱的橘猫在阳光下伸懒腰"

  # 指定 Kling 模型 2.5 版本 + 10秒时长
  python mps_aigc_video.py --prompt "赛博朋克" --model Kling --model-version 2.5 --duration 10

  # 图生视频（首帧图片）
  python mps_aigc_video.py --prompt "让画面动起来" --image-url https://example.com/photo.jpg

  # 首尾帧生视频（GV 模型）
  python mps_aigc_video.py --prompt "过渡" --model GV \\
      --image-url https://example.com/start.jpg \\
      --last-image-url https://example.com/end.jpg

  # GV 多图参考
  python mps_aigc_video.py --prompt "融合" --model GV \\
      --ref-image-url https://example.com/img1.jpg --ref-image-type asset \\
      --ref-image-url https://example.com/img2.jpg --ref-image-type style

  # Kling O1 参考视频 + 保留原声
  python mps_aigc_video.py --prompt "风格化" --model Kling --model-version O1 \\
      --ref-video-url https://example.com/video.mp4 \\
      --ref-video-type base --keep-original-sound yes

  # 1080P + 16:9 + 去水印 + 音频 + BGM
  python mps_aigc_video.py --prompt "产品展示" --model Kling \\
      --resolution 1080P --aspect-ratio 16:9 --no-logo --enable-audio true --enable-bgm

  # Vidu 错峰模式
  python mps_aigc_video.py --prompt "风景" --model Vidu --off-peak

  # 查询任务结果
  python mps_aigc_video.py --task-id 4-AigcVideo-c3b145ec76xxxx

  # Dry Run（仅打印请求参数）
  python mps_aigc_video.py --prompt "测试" --dry-run

支持的模型：
  Hunyuan     腾讯混元大模型（默认）
  Hailuo      海螺视频模型，版本 02 / 2.3，时长 6 / 10 秒
  Kling       可灵视频模型，版本 2.0-3.0/O1/3.0-Omni，时长 5 / 10 秒
  Vidu        Vidu 视频模型，版本 q2/q2-pro/q2-turbo/q3-pro/q3-turbo，时长 1-10 秒
  OS          OS 视频模型，版本 2.0，时长 4 / 8 / 12 秒
  GV          GV 视频模型，版本 3.1，时长 8 秒

场景类型（部分模型支持）：
  motion_control   Kling — 动作控制
  land2port        Mingmou — 横转竖
  template_effect  Vidu — 特效模板

分辨率选项：
  720P  1080P  2K  4K

宽高比选项（部分模型支持）：
  16:9  9:16  1:1  4:3  3:4

环境变量：
  TENCENTCLOUD_SECRET_ID   腾讯云 SecretId
  TENCENTCLOUD_SECRET_KEY  腾讯云 SecretKey
  TENCENTCLOUD_COS_BUCKET       COS Bucket 名称（可选，用于结果存储）
  TENCENTCLOUD_COS_REGION       COS Bucket 区域（默认 ap-guangzhou）
        """
    )

    # ---- 任务查询 ----
    query_group = parser.add_argument_group("任务查询（查询已有任务，与创建任务互斥）")
    query_group.add_argument("--task-id", type=str,
                             help="查询已有任务的 TaskId")

    # ---- 模型配置 ----
    model_group = parser.add_argument_group("模型配置")
    model_group.add_argument("--model", type=str, default="Hunyuan",
                             choices=["Hunyuan", "Hailuo", "Kling", "Vidu", "OS", "GV"],
                             help="模型名称（默认 Hunyuan）")
    model_group.add_argument("--model-version", type=str,
                             help="模型版本号（如 Kling: 2.5, Hailuo: 2.3, Vidu: q2-pro）")
    model_group.add_argument("--scene-type", type=str,
                             choices=["motion_control", "land2port", "template_effect"],
                             help="场景类型（部分模型支持）")

    # ---- 生视频内容 ----
    content_group = parser.add_argument_group("生视频内容")
    content_group.add_argument("--prompt", type=str,
                               help="视频描述文本（最多2000字符）。未传图片时必填")
    content_group.add_argument("--negative-prompt", type=str,
                               help="反向提示词：描述不想生成的内容（部分模型支持）")
    content_group.add_argument("--enhance-prompt", action="store_true",
                               help="开启提示词增强：自动优化 prompt 以提升生成质量")

    # ---- 图片输入（简单模式） ----
    image_group = parser.add_argument_group("图片输入（图生视频）")
    image_group.add_argument("--image-url", type=str,
                             help="首帧图片 URL（推荐 < 10M，支持 jpeg/png）")
    image_group.add_argument("--last-image-url", type=str,
                             help="尾帧图片 URL（部分模型支持，需同时传 --image-url）")

    # ---- 多图参考（ImageInfos） ----
    multi_image_group = parser.add_argument_group("多图参考（GV / Vidu 支持，与 --image-url 互斥于 GV 模型）")
    multi_image_group.add_argument("--ref-image-url", type=str, action="append",
                                   help="参考图片 URL（可多次指定，最多3张）")
    multi_image_group.add_argument("--ref-image-type", type=str, action="append",
                                   choices=["asset", "style"],
                                   help="参考类型（与 --ref-image-url 一一对应）: asset=素材 | style=风格")

    # ---- 参考视频（VideoInfos） ----
    video_ref_group = parser.add_argument_group("参考视频（仅 Kling O1 支持）")
    video_ref_group.add_argument("--ref-video-url", type=str, action="append",
                                 help="参考视频 URL")
    video_ref_group.add_argument("--ref-video-type", type=str, action="append",
                                 choices=["feature", "base"],
                                 help="参考视频类型: feature=特征参考 | base=待编辑视频（默认）")
    video_ref_group.add_argument("--keep-original-sound", type=str, action="append",
                                 choices=["yes", "no"],
                                 help="是否保留视频原声（与 --ref-video-url 对应）")

    # ---- 视频输出配置 ----
    output_group = parser.add_argument_group("视频输出配置")
    output_group.add_argument("--duration", type=int,
                              help="视频时长（秒）。不同模型支持不同选项，详见说明")
    output_group.add_argument("--resolution", type=str,
                              choices=["720P", "1080P", "2K", "4K"],
                              help="输出分辨率（不同模型默认不同）")
    output_group.add_argument("--aspect-ratio", type=str,
                              help="宽高比（如 16:9, 9:16, 1:1）。不同模型支持不同选项")
    output_group.add_argument("--no-logo", action="store_true",
                              help="去除图标水印（Hailuo/Kling/Vidu 支持）")
    output_group.add_argument("--enable-audio", type=bool, default=None,
                              help="是否为视频生成音频（GV/OS 支持，默认 true）")
    output_group.add_argument("--enable-bgm", action="store_true",
                              help="是否添加背景音乐（部分模型版本支持）")
    output_group.add_argument("--off-peak", action="store_true",
                              help="错峰模式（仅 Vidu），任务48小时内生成，超时自动取消")

    # ---- COS 存储 ----
    cos_group = parser.add_argument_group("COS 存储配置（可选，不配置则使用 MPS 临时存储，12小时有效）")
    cos_group.add_argument("--cos-bucket-name", type=str,
                           help="COS Bucket 名称（默认取 TENCENTCLOUD_COS_BUCKET 环境变量）")
    cos_group.add_argument("--cos-bucket-region", type=str,
                           help="COS Bucket 区域（默认取 TENCENTCLOUD_COS_REGION 环境变量，默认 ap-guangzhou）")
    cos_group.add_argument("--cos-bucket-path", type=str,
                           help="COS 存储路径前缀（如 aigc_output）")

    # ---- 附加参数 ----
    extra_group = parser.add_argument_group("附加参数")
    extra_group.add_argument("--additional-params", type=str,
                             help="JSON 格式附加参数（如相机控制: '{\"camera_control\":{\"type\":\"simple\"}}'）")

    # ---- 执行控制 ----
    control_group = parser.add_argument_group("执行控制")
    control_group.add_argument("--no-wait", action="store_true",
                               help="仅创建任务，不等待结果。稍后用 --task-id 查询")
    control_group.add_argument("--poll-interval", type=int, default=DEFAULT_POLL_INTERVAL,
                               help=f"轮询间隔（秒），默认 {DEFAULT_POLL_INTERVAL}")
    control_group.add_argument("--max-wait", type=int, default=DEFAULT_MAX_WAIT,
                               help=f"最长等待时间（秒），默认 {DEFAULT_MAX_WAIT}")
    control_group.add_argument("--operator", type=str,
                               help="操作者名称")

    # ---- 其他 ----
    other_group = parser.add_argument_group("其他配置")
    other_group.add_argument("--region", type=str,
                             help="MPS 服务区域（默认 ap-guangzhou）")
    other_group.add_argument("--verbose", "-v", action="store_true",
                             help="输出详细信息")
    other_group.add_argument("--dry-run", action="store_true",
                             help="仅打印请求参数，不实际调用 API")

    args = parser.parse_args()

    # 参数校验
    validate_args(args, parser)

    # 执行
    run(args)


if __name__ == "__main__":
    main()
