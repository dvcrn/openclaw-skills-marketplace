#!/usr/bin/env python3
"""
视频资源下载脚本

此脚本接收已解析的资源 URL 进行下载，不负责解析。
解析应通过 MCP parse_video 工具完成。

用法:
    # 下载单个视频
    python download.py --video "https://xxx.mp4"
    
    # 下载多个资源
    python download.py --video "url1" --video "url2" --image "url3"
    
    # 指定输出目录和文件名前缀
    python download.py --video "url" --output ./downloads --name "我的视频"

示例工作流:
    1. Agent 调用 MCP parse_video 工具获取资源 URL
    2. Agent 执行此脚本下载资源
"""

import argparse
import os
import sys
import re
import requests
from datetime import datetime
from urllib.parse import urlparse, unquote


def sanitize_filename(name: str, max_length: int = 100) -> str:
    """清理文件名，移除非法字符"""
    # 移除非法字符
    name = re.sub(r'[\\/:*?"<>|]', '', name)
    # 移除多余空格
    name = re.sub(r'\s+', ' ', name).strip()
    # 限制长度
    if len(name) > max_length:
        name = name[:max_length]
    return name or "untitled"


def get_extension_from_url(url: str, default: str = "") -> str:
    """从 URL 获取文件扩展名"""
    parsed = urlparse(url)
    path = unquote(parsed.path)
    ext = os.path.splitext(path)[1].lower()
    # 只保留常见扩展名
    valid_exts = {'.mp4', '.mov', '.avi', '.mkv', '.webm', '.mp3', '.m4a', '.wav', '.jpg', '.jpeg', '.png', '.gif', '.webp'}
    return ext if ext in valid_exts else default


def download_file(url: str, filepath: str) -> bool:
    """下载文件到指定路径"""
    try:
        print(f"  下载中: {url[:80]}...")
        response = requests.get(url, stream=True, timeout=120, headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        })
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        print(f"\r  进度: {percent:.1f}% ({downloaded}/{total_size} bytes)", end="")
        
        print(f"\n  ✓ 已保存: {filepath}")
        return True
    except Exception as e:
        print(f"\n  ✗ 下载失败: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="下载已解析的视频资源",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 下载单个视频
  python download.py --video "https://example.com/video.mp4"
  
  # 下载视频和音频
  python download.py --video "https://xxx/v.mp4" --audio "https://xxx/a.mp3"
  
  # 下载多张图片
  python download.py --image "url1" --image "url2" --image "url3"
  
  # 指定输出目录和名称
  python download.py --video "url" -o ~/Downloads -n "搞笑视频"
        """
    )
    parser.add_argument("--video", "-v", action="append", default=[], help="视频 URL（可多次指定）")
    parser.add_argument("--audio", "-a", action="append", default=[], help="音频 URL（可多次指定）")
    parser.add_argument("--image", "-i", action="append", default=[], help="图片 URL（可多次指定）")
    parser.add_argument("--thumbnail", "-t", help="缩略图 URL")
    parser.add_argument("--output", "-o", default="./downloads", help="输出目录 (默认: ./downloads)")
    parser.add_argument("--name", "-n", default="video", help="文件名前缀 (默认: video)")
    
    args = parser.parse_args()
    
    # 检查是否有资源要下载
    total_resources = len(args.video) + len(args.audio) + len(args.image) + (1 if args.thumbnail else 0)
    if total_resources == 0:
        print("错误: 请至少提供一个资源 URL")
        print("用法: python download.py --video <url> [--audio <url>] [--image <url>]")
        sys.exit(1)
    
    # 创建输出目录
    os.makedirs(args.output, exist_ok=True)
    
    name = sanitize_filename(args.name)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    results = {
        "success": [],
        "failed": []
    }
    
    # 下载视频
    if args.video:
        print(f"\n📹 下载视频 ({len(args.video)} 个):")
        for i, url in enumerate(args.video):
            ext = get_extension_from_url(url, ".mp4")
            suffix = f"_{i+1}" if len(args.video) > 1 else ""
            filename = f"{name}{suffix}_{timestamp}{ext}"
            filepath = os.path.join(args.output, filename)
            
            if download_file(url, filepath):
                results["success"].append(filepath)
            else:
                results["failed"].append(url)
    
    # 下载音频
    if args.audio:
        print(f"\n🎵 下载音频 ({len(args.audio)} 个):")
        for i, url in enumerate(args.audio):
            ext = get_extension_from_url(url, ".mp3")
            suffix = f"_{i+1}" if len(args.audio) > 1 else ""
            filename = f"{name}_audio{suffix}_{timestamp}{ext}"
            filepath = os.path.join(args.output, filename)
            
            if download_file(url, filepath):
                results["success"].append(filepath)
            else:
                results["failed"].append(url)
    
    # 下载图片
    if args.image:
        print(f"\n🖼️  下载图片 ({len(args.image)} 个):")
        for i, url in enumerate(args.image):
            ext = get_extension_from_url(url, ".jpg")
            filename = f"{name}_{i+1}_{timestamp}{ext}"
            filepath = os.path.join(args.output, filename)
            
            if download_file(url, filepath):
                results["success"].append(filepath)
            else:
                results["failed"].append(url)
    
    # 下载缩略图
    if args.thumbnail:
        print(f"\n🖼️  下载缩略图:")
        url = args.thumbnail
        ext = get_extension_from_url(url, ".jpg")
        filename = f"{name}_thumbnail_{timestamp}{ext}"
        filepath = os.path.join(args.output, filename)
        
        if download_file(url, filepath):
            results["success"].append(filepath)
        else:
            results["failed"].append(url)
    
    # 输出结果
    print(f"\n" + "=" * 50)
    print(f"下载完成!")
    print(f"  成功: {len(results['success'])} 个")
    print(f"  失败: {len(results['failed'])} 个")
    print(f"  保存目录: {os.path.abspath(args.output)}")
    
    if results["success"]:
        print(f"\n已下载文件:")
        for f in results["success"]:
            print(f"  - {f}")
    
    if results["failed"]:
        print(f"\n下载失败:")
        for f in results["failed"]:
            print(f"  - {f}")
        sys.exit(1)


if __name__ == "__main__":
    main()
