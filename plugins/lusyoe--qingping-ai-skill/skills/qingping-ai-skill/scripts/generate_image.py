#!/usr/bin/env python3
"""
青萍 AI 图片生成脚本
通过 API 生成图片并下载到本地

认证方式：
- 使用 QINGPING_API_KEY 环境变量
"""

import os
import sys
import time
import json
from pathlib import Path
from typing import Optional
from urllib import request, error


API_BASE_URL = "https://video.lusyoe.com/api/img"
POLL_INTERVAL = 5
OUTPUT_DIR = "qingping-ai"

SUPPORTED_MODELS = ["nano-banana", "nano-banana-2", "nano-banana-pro"]
DEFAULT_MODEL = "nano-banana"

SUPPORTED_SIZES = ["1K", "2K", "4K"]
DEFAULT_SIZE = "1K"

SUPPORTED_RATIOS = ["1:1", "16:9", "9:16"]
DEFAULT_RATIO = "1:1"


def validate_model(model: str) -> str:
    """验证模型名称，返回有效的模型名称"""
    if model not in SUPPORTED_MODELS:
        print(f"❌ 错误: 不支持的模型 '{model}'")
        print(f"\n支持的模型:")
        for m in SUPPORTED_MODELS:
            marker = " (默认)" if m == DEFAULT_MODEL else ""
            print(f"   - {m}{marker}")
        sys.exit(1)
    return model


def validate_size(size: str) -> str:
    """验证图片尺寸，返回有效的尺寸"""
    if size not in SUPPORTED_SIZES:
        print(f"❌ 错误: 不支持的尺寸 '{size}'")
        print(f"\n支持的尺寸:")
        for s in SUPPORTED_SIZES:
            marker = " (默认)" if s == DEFAULT_SIZE else ""
            print(f"   - {s}{marker}")
        sys.exit(1)
    return size


def validate_ratio(ratio: str) -> str:
    """验证图片比例，返回有效的比例"""
    if ratio not in SUPPORTED_RATIOS:
        print(f"❌ 错误: 不支持的比例 '{ratio}'")
        print(f"\n支持的比例:")
        for r in SUPPORTED_RATIOS:
            marker = " (默认)" if r == DEFAULT_RATIO else ""
            print(f"   - {r}{marker}")
        sys.exit(1)
    return ratio


def get_api_key() -> str:
    """获取 API Key"""
    api_key = os.environ.get("QINGPING_API_KEY")
    if not api_key:
        print("❌ 错误: 未找到环境变量 QINGPING_API_KEY")
        print("\n" + "=" * 70)
        print("🔑 获取 API Key 步骤：")
        print("=" * 70)
        print("\n1. 登录青萍AI平台:")
        print("   https://auth.lusyoe.com/profile")
        print("\n2. 在个人信息页面，滚动到最下面")
        print("\n3. 点击生成或查看 API Key")
        print("\n" + "=" * 70)
        print("⚙️  配置环境变量：")
        print("=" * 70)
        print("\n方法一: 临时配置（仅当前终端会话有效）")
        print("   export QINGPING_API_KEY='your-api-key-here'")
        print("\n方法二: 永久配置（推荐）")
        print("   # 添加到 ~/.zshrc (macOS 默认) 或 ~/.bashrc (Linux)")
        print("   echo 'export QINGPING_API_KEY=\"your-api-key-here\"' >> ~/.zshrc")
        print("   source ~/.zshrc")
        print("\n" + "=" * 70)
        sys.exit(1)
    return api_key


def http_request(
    url: str,
    method: str = "GET",
    headers: Optional[dict] = None,
    data: Optional[dict] = None,
    timeout: int = 30,
) -> dict:
    """发送 HTTP 请求"""
    req_headers = headers or {}
    req_headers["User-Agent"] = "QingpingAI-Skill/1.0"

    req_data = None
    if data:
        req_data = json.dumps(data).encode("utf-8")
        req_headers["Content-Type"] = "application/json"

    req = request.Request(url, data=req_data, headers=req_headers, method=method)

    try:
        with request.urlopen(req, timeout=timeout) as response:
            response_body = response.read().decode("utf-8")
            return json.loads(response_body)
    except error.HTTPError as e:
        error_body = e.read().decode("utf-8") if e.fp else ""
        try:
            error_data = json.loads(error_body)
            print(f"❌ HTTP 错误 {e.code}: {json.dumps(error_data, ensure_ascii=False, indent=2)}")
        except json.JSONDecodeError:
            print(f"❌ HTTP 错误 {e.code}: {error_body}")
        sys.exit(1)
    except error.URLError as e:
        print(f"❌ 网络错误: {str(e.reason)}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ 响应解析失败: {str(e)}")
        sys.exit(1)


def create_generation_task(
    api_key: str,
    prompt: str,
    model: str = DEFAULT_MODEL,
    count: int = 1,
    ratio: str = DEFAULT_RATIO,
    size: str = DEFAULT_SIZE,
    tags: Optional[list] = None,
) -> str:
    """创建图片生成任务"""
    model = validate_model(model)
    size = validate_size(size)
    ratio = validate_ratio(ratio)
    
    if tags is None:
        tags = [""]

    url = f"{API_BASE_URL}/generations"
    headers = {"x-api-key": api_key}
    payload = {
        "count": count,
        "model": model,
        "prompt": prompt,
        "ratio": ratio,
        "size": size,
        "category": "青萍Claw",
        "tags": tags,
        "stream": False,
    }

    print(f"📤 提交生成任务...")
    print(f"   提示词: {prompt}")
    print(f"   模型: {model}")
    print(f"   尺寸: {size}, 比例: {ratio}")

    data = http_request(url, method="POST", headers=headers, data=payload)

    task_id = data.get("task_id")
    if not task_id:
        print(f"❌ 错误: 响应中没有 task_id")
        print(f"   响应: {json.dumps(data, ensure_ascii=False, indent=2)}")
        sys.exit(1)

    print(f"✅ 任务已提交")
    print(f"   任务ID: {task_id}")
    print(f"   {data.get('message', '')}")
    return task_id


def poll_task_status(api_key: str, task_id: str) -> dict:
    """轮询任务状态直到完成"""
    url = f"{API_BASE_URL}/generations/{task_id}/status"
    headers = {"x-api-key": api_key}

    print(f"\n⏳ 开始轮询任务状态...")
    poll_count = 0

    while True:
        data = http_request(url, headers=headers)
        status = data.get("status")
        poll_count += 1
        
        elapsed_time = poll_count * POLL_INTERVAL

        if status == "completed":
            print(f"\n✅ 任务完成!")
            print(f"   轮询次数: {poll_count}")
            print(f"   总耗时: {elapsed_time} 秒")
            return data
        elif status == "failed":
            print(f"\n❌ 任务失败!")
            print(f"   轮询次数: {poll_count}")
            print(f"   总耗时: {elapsed_time} 秒")
            error_msg = data.get("error", "未知错误")
            print(f"   错误: {error_msg}")
            sys.exit(1)
        else:
            print(f"\n   [{poll_count}] 轮询结果:")
            print(f"   状态: {status}, 已等待: {elapsed_time} 秒")
            print(f"   完整响应: {json.dumps(data, ensure_ascii=False, indent=2)}")
            time.sleep(POLL_INTERVAL)


def download_image(url: str, filename: str, output_dir: Path) -> Path:
    """下载图片到指定目录"""
    output_path = output_dir / filename

    print(f"\n📥 下载图片...")
    print(f"   URL: {url}")
    print(f"   保存到: {output_path}")

    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        request.urlretrieve(url, output_path)
        print(f"✅ 下载完成!")
        return output_path
    except error.URLError as e:
        print(f"❌ 下载失败: {str(e.reason)}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 下载失败: {str(e)}")
        sys.exit(1)


def generate_image(
    prompt: str,
    model: str = DEFAULT_MODEL,
    count: int = 1,
    ratio: str = DEFAULT_RATIO,
    size: str = DEFAULT_SIZE,
    tags: Optional[list] = None,
) -> list[Path]:
    """
    生成图片的主函数
    
    Args:
        prompt: 图片描述提示词
        model: 模型名称，默认 nano-banana（可选：nano-banana, nano-banana-2, nano-banana-pro）
        count: 生成数量，默认 1
        ratio: 图片比例，默认 1:1（可选：1:1, 16:9, 9:16）
        size: 图片尺寸，默认 1K（可选：1K, 2K, 4K）
        tags: 标签列表
    
    Returns:
        下载的图片路径列表
    """
    model = validate_model(model)
    size = validate_size(size)
    ratio = validate_ratio(ratio)
    api_key = get_api_key()
    
    task_id = create_generation_task(
        api_key=api_key,
        prompt=prompt,
        model=model,
        count=count,
        ratio=ratio,
        size=size,
        tags=tags,
    )
    
    result = poll_task_status(api_key=api_key, task_id=task_id)
    
    generated_urls = result.get("generated_image_urls", [])
    if not generated_urls:
        print("❌ 错误: 没有生成图片")
        sys.exit(1)
    
    output_dir = Path(OUTPUT_DIR)
    downloaded_paths = []
    
    print(f"\n📋 图片信息:")
    for idx, img_data in enumerate(generated_urls, 1):
        url = img_data.get("url")
        name = img_data.get("name")
        
        if not url or not name:
            print(f"⚠️  跳过无效数据: {img_data}")
            continue
        
        print(f"   [{idx}] 名称: {name}")
        print(f"       链接: {url}")
        
        filename = f"{name}.png"
        path = download_image(url, filename, output_dir)
        downloaded_paths.append(path)
    
    print(f"\n🎉 完成! 共下载 {len(downloaded_paths)} 张图片到 {output_dir.absolute()}/")
    print(f"\n💡 提示: 可到青萍AI图床查看和管理图片")
    print(f"   地址: https://img.lusyoe.com")
    return downloaded_paths


def main():
    """命令行入口"""
    if len(sys.argv) < 2:
        print("用法: python generate_image.py <提示词> [模型] [数量] [比例] [尺寸]")
        print("\n支持的模型:")
        for m in SUPPORTED_MODELS:
            marker = " (默认)" if m == DEFAULT_MODEL else ""
            print(f"   - {m}{marker}")
        print("\n支持的比例:")
        for r in SUPPORTED_RATIOS:
            marker = " (默认)" if r == DEFAULT_RATIO else ""
            print(f"   - {r}{marker}")
        print("\n支持的尺寸:")
        for s in SUPPORTED_SIZES:
            marker = " (默认)" if s == DEFAULT_SIZE else ""
            print(f"   - {s}{marker}")
        print("\n示例:")
        print("   python generate_image.py '一只可爱的金鱼'")
        print("   python generate_image.py '一只可爱的金鱼' nano-banana-2 1 1:1 1K")
        print("   python generate_image.py '夕阳下的海滩' nano-banana-pro 1 16:9 2K")
        print("   python generate_image.py '手机壁纸' nano-banana 1 9:16 4K")
        print("\n认证: 需要配置环境变量 QINGPING_API_KEY")
        print("   获取 API Key: https://auth.lusyoe.com/profile")
        sys.exit(1)
    
    prompt = sys.argv[1]
    model = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_MODEL
    count = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    ratio = sys.argv[4] if len(sys.argv) > 4 else DEFAULT_RATIO
    size = sys.argv[5] if len(sys.argv) > 5 else DEFAULT_SIZE
    
    generate_image(
        prompt=prompt,
        model=model,
        count=count,
        ratio=ratio,
        size=size,
    )


if __name__ == "__main__":
    main()
