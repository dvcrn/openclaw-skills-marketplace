#!/usr/bin/env python3
"""
腾讯云 MPS 媒体处理任务查询脚本

功能：
  通过任务 ID 查询 ProcessMedia 提交的媒体处理任务的执行状态和结果详情。
  最多可以查询 7 天之内提交的任务。

  支持查询任务的整体状态（WAITING / PROCESSING / FINISH），以及各子任务
  （转码、截图、字幕、画质增强等）的执行结果和输出文件信息。

用法：
  # 查询指定任务
  python mps_get_video_task.py --task-id 1234567890-WorkflowTask-80108cc3380155d98b2e3573a48a

  # 查询并输出完整 JSON 响应
  python mps_get_video_task.py --task-id 1234567890-WorkflowTask-80108cc3380155d98b2e3573a48a --verbose

  # 仅输出原始 JSON（方便管道处理）
  python mps_get_video_task.py --task-id 1234567890-WorkflowTask-80108cc3380155d98b2e3573a48a --json

环境变量：
  TENCENTCLOUD_SECRET_ID   - 腾讯云 SecretId
  TENCENTCLOUD_SECRET_KEY  - 腾讯云 SecretKey
"""

import argparse
import json
import os
import sys

try:
    from tencentcloud.common import credential
    from tencentcloud.common.profile.client_profile import ClientProfile
    from tencentcloud.common.profile.http_profile import HttpProfile
    from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
    from tencentcloud.mps.v20190612 import mps_client, models
except ImportError:
    print("错误：请先安装腾讯云 SDK：pip install tencentcloud-sdk-python", file=sys.stderr)
    sys.exit(1)


try:
    from load_env import ensure_env_loaded as _ensure_env_loaded
    _LOAD_ENV_AVAILABLE = True
except ImportError:
    _LOAD_ENV_AVAILABLE = False
    def _ensure_env_loaded(**kwargs):
        return False

# 任务状态中文映射
STATUS_MAP = {
    "WAITING": "等待中",
    "PROCESSING": "处理中",
    "FINISH": "已完成",
    "SUCCESS": "成功",
    "FAIL": "失败",
}

# 子任务类型中文映射
TASK_TYPE_MAP = {
    "Transcode": "转码",
    "AnimatedGraphic": "转动图",
    "SnapshotByTimeOffset": "时间点截图",
    "SampleSnapshot": "采样截图",
    "ImageSprite": "雪碧图",
    "AdaptiveDynamicStreaming": "自适应码流",
    "AiAnalysis": "AI 内容分析",
    "AiRecognition": "AI 内容识别",
    "AiContentReview": "AI 内容审核",
    "AiQualityControl": "媒体质检",
}


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


def format_status(status):
    """格式化状态显示。"""
    return STATUS_MAP.get(status, status)


def print_input_info(input_info):
    """打印输入文件信息。"""
    if not input_info:
        return
    input_type = input_info.get("Type", "")
    if input_type == "COS":
        cos = input_info.get("CosInputInfo", {}) or {}
        print(f"   输入: COS - {cos.get('Bucket', '')}:{cos.get('Object', '')} (region: {cos.get('Region', '')})")
    elif input_type == "URL":
        url_info = input_info.get("UrlInputInfo", {}) or {}
        print(f"   输入: URL - {url_info.get('Url', '')}")
    else:
        print(f"   输入类型: {input_type}")


def print_meta_data(meta):
    """打印媒体元信息。"""
    if not meta:
        return
    duration = meta.get("Duration", 0)
    width = meta.get("Width", 0)
    height = meta.get("Height", 0)
    bitrate = meta.get("Bitrate", 0)
    container = meta.get("Container", "")
    size = meta.get("Size", 0)
    print(f"   原始信息: {container.upper() if container else 'N/A'} | "
          f"{width}x{height} | "
          f"{bitrate // 1000 if bitrate else 0} kbps | "
          f"{duration:.1f}s | "
          f"{size / 1024 / 1024:.2f} MB")


def print_media_process_results(result_set):
    """打印媒体处理子任务结果。"""
    if not result_set:
        print("   子任务: 无")
        return

    for i, item in enumerate(result_set, 1):
        task_type = item.get("Type", "")
        type_name = TASK_TYPE_MAP.get(task_type, task_type)

        # 根据类型取对应的任务详情字段
        task_key_map = {
            "Transcode": "TranscodeTask",
            "AnimatedGraphic": "AnimatedGraphicTask",
            "SnapshotByTimeOffset": "SnapshotByTimeOffsetTask",
            "SampleSnapshot": "SampleSnapshotTask",
            "ImageSprite": "ImageSpriteTask",
            "AdaptiveDynamicStreaming": "AdaptiveDynamicStreamingTask",
        }
        task_key = task_key_map.get(task_type, "")
        task_detail = item.get(task_key, {}) if task_key else None

        if task_detail:
            status = task_detail.get("Status", "")
            err_code = task_detail.get("ErrCode", 0)
            message = task_detail.get("Message", "")
            progress = task_detail.get("Progress", None)

            status_str = format_status(status)
            progress_str = f" ({progress}%)" if progress is not None else ""
            err_str = f" | 错误码: {err_code} - {message}" if err_code != 0 else ""

            print(f"   [{i}] {type_name}: {status_str}{progress_str}{err_str}")

            # 打印输出文件信息
            output = task_detail.get("Output", {})
            if output:
                out_storage = output.get("OutputStorage", {}) or {}
                out_path = output.get("Path", "")
                out_type = out_storage.get("Type", "")
                if out_type == "COS":
                    cos_out = out_storage.get("CosOutputStorage", {}) or {}
                    bucket = cos_out.get("Bucket", "")
                    region = cos_out.get("Region", "")
                    print(f"       输出: COS - {bucket}:{out_path} (region: {region})")
                elif out_path:
                    print(f"       输出: {out_path}")

                # 打印输出视频信息
                out_width = output.get("Width", 0)
                out_height = output.get("Height", 0)
                out_bitrate = output.get("Bitrate", 0)
                out_duration = output.get("Duration", 0)
                out_size = output.get("Size", 0)
                out_container = output.get("Container", "")
                if out_width or out_height:
                    print(f"       规格: {out_container.upper() if out_container else 'N/A'} | "
                          f"{out_width}x{out_height} | "
                          f"{out_bitrate // 1000 if out_bitrate else 0} kbps | "
                          f"{out_duration:.1f}s | "
                          f"{out_size / 1024 / 1024:.2f} MB")
        else:
            print(f"   [{i}] {type_name}: 无详情")


def query_task(args):
    """查询媒体处理任务详情。"""
    region = args.region or "ap-guangzhou"

    # 1. 获取凭证和客户端
    cred = get_credentials()
    client = create_mps_client(cred, region)

    # 2. 构建请求
    params = {"TaskId": args.task_id}

    # 3. 发起调用
    try:
        req = models.DescribeTaskDetailRequest()
        req.from_json_string(json.dumps(params))

        resp = client.DescribeTaskDetail(req)
        result = json.loads(resp.to_json_string())

        # 仅输出 JSON 模式
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return result

        # 解析响应
        task_type = result.get("TaskType", "")
        status = result.get("Status", "")
        create_time = result.get("CreateTime", "")
        begin_time = result.get("BeginProcessTime", "")
        finish_time = result.get("FinishTime", "")

        print("=" * 60)
        print("腾讯云 MPS 媒体处理任务详情")
        print("=" * 60)
        print(f"   TaskId:    {args.task_id}")
        print(f"   任务类型:  {task_type}")
        print(f"   状态:      {format_status(status)}")
        print(f"   创建时间:  {create_time}")
        if begin_time:
            print(f"   开始时间:  {begin_time}")
        if finish_time:
            print(f"   完成时间:  {finish_time}")
        print("-" * 60)

        # WorkflowTask（ProcessMedia 提交的任务）
        workflow_task = result.get("WorkflowTask")
        if workflow_task:
            wf_status = workflow_task.get("Status", "")
            wf_err = workflow_task.get("ErrCode", 0)
            wf_msg = workflow_task.get("Message", "")

            print(f"   工作流状态: {format_status(wf_status)}", end="")
            if wf_err != 0:
                print(f" | 错误码: {wf_err} - {wf_msg}", end="")
            print()

            # 输入信息
            print_input_info(workflow_task.get("InputInfo"))

            # 元信息
            print_meta_data(workflow_task.get("MetaData"))

            # 子任务结果
            print("-" * 60)
            print("   子任务结果：")
            print_media_process_results(workflow_task.get("MediaProcessResultSet", []))
        else:
            # 非 WorkflowTask 类型，提示用户
            print(f"   提示：该任务类型为 {task_type}，非 ProcessMedia 提交的 WorkflowTask。")
            print(f"         如需查看完整信息，请使用 --verbose 或 --json 参数。")

        print("-" * 60)
        print(f"   RequestId: {result.get('RequestId', 'N/A')}")

        # 详细模式：输出完整 JSON
        if args.verbose:
            print("\n完整响应：")
            print(json.dumps(result, ensure_ascii=False, indent=2))

        return result

    except TencentCloudSDKException as e:
        print(f"❌ 请求失败: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="腾讯云 MPS 媒体处理任务查询 —— 查询 ProcessMedia 提交的任务状态和结果",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  # 查询指定任务
  python mps_get_video_task.py --task-id 235303-WorkflowTask-80108cc3380155d98b2e3573a48a

  # 查询并输出完整 JSON 响应
  python mps_get_video_task.py --task-id 235303-WorkflowTask-80108cc3380155d98b2e3573a48a --verbose

  # 仅输出原始 JSON（方便管道处理）
  python mps_get_video_task.py --task-id 235303-WorkflowTask-80108cc3380155d98b2e3573a48a --json

环境变量：
  TENCENTCLOUD_SECRET_ID   腾讯云 SecretId
  TENCENTCLOUD_SECRET_KEY  腾讯云 SecretKey
        """
    )

    parser.add_argument("--task-id", type=str, required=True,
                        help="媒体处理任务 ID，由 ProcessMedia 接口返回")
    parser.add_argument("--region", type=str,
                        help="MPS 服务区域（默认 ap-guangzhou）")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="输出完整 JSON 响应")
    parser.add_argument("--json", action="store_true",
                        help="仅输出原始 JSON，不打印格式化摘要")

    args = parser.parse_args()

    print("=" * 60)
    print("腾讯云 MPS 媒体处理任务查询")
    print("=" * 60)
    print(f"TaskId: {args.task_id}")
    print("-" * 60)

    query_task(args)


if __name__ == "__main__":
    main()
