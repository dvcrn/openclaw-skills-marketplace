#!/usr/bin/env python3
"""
音频合并脚本 - 将多个音频 URL 合并成一个完整的长音频文件

用法：
    python merge_audio.py --input dialogue.json --output merged.mp3
    python merge_audio.py --urls url1 url2 url3 --output merged.mp3
    
依赖：
    pip install pydub requests

注意：需要系统安装 FFmpeg
    - macOS: brew install ffmpeg
    - Ubuntu: sudo apt install ffmpeg
"""

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

try:
    import requests
except ImportError:
    print("错误: 缺少 requests 库，请运行: pip install requests")
    sys.exit(1)

try:
    from pydub import AudioSegment
except ImportError:
    print("错误: 缺少 pydub 库，请运行: pip install pydub")
    sys.exit(1)


def download_audio(url: str, temp_dir: str, index: int) -> Optional[str]:
    """
    从 URL 下载音频文件到临时目录
    
    Args:
        url: 音频文件 URL
        temp_dir: 临时目录路径
        index: 文件索引，用于命名
        
    Returns:
        下载文件的本地路径，失败返回 None
    """
    try:
        # 从 URL 获取文件扩展名
        parsed = urlparse(url)
        path = parsed.path
        ext = os.path.splitext(path)[1] or '.mp3'
        
        # 下载文件
        print(f"  下载第 {index + 1} 段音频...")
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # 保存到临时文件
        local_path = os.path.join(temp_dir, f"segment_{index:03d}{ext}")
        with open(local_path, 'wb') as f:
            f.write(response.content)
        
        return local_path
        
    except requests.RequestException as e:
        print(f"  警告: 下载失败 - {e}")
        return None


def merge_audio_files(audio_paths: list[str], output_path: str, 
                      gap_ms: int = 300, format: str = "mp3") -> bool:
    """
    合并多个音频文件
    
    Args:
        audio_paths: 音频文件路径列表
        output_path: 输出文件路径
        gap_ms: 音频之间的间隔（毫秒）
        format: 输出格式
        
    Returns:
        是否成功
    """
    if not audio_paths:
        print("错误: 没有可合并的音频文件")
        return False
    
    try:
        print(f"\n正在合并 {len(audio_paths)} 段音频...")
        
        # 加载第一个音频
        combined = AudioSegment.from_file(audio_paths[0])
        
        # 创建间隔静音
        silence = AudioSegment.silent(duration=gap_ms)
        
        # 依次添加其他音频
        for i, path in enumerate(audio_paths[1:], 2):
            print(f"  合并第 {i} 段...")
            segment = AudioSegment.from_file(path)
            combined += silence + segment
        
        # 导出合并后的音频
        print(f"\n正在导出到: {output_path}")
        combined.export(output_path, format=format)
        
        # 计算总时长
        duration_sec = len(combined) / 1000
        duration_min = int(duration_sec // 60)
        duration_sec_remain = duration_sec % 60
        
        print(f"\n✅ 合并完成!")
        print(f"   总时长: {duration_min}分{duration_sec_remain:.1f}秒")
        print(f"   文件大小: {os.path.getsize(output_path) / 1024:.1f} KB")
        
        return True
        
    except Exception as e:
        print(f"错误: 合并失败 - {e}")
        return False


def load_urls_from_json(json_path: str) -> list[str]:
    """
    从 dialogue.json 文件加载音频 URL 列表
    
    支持两种格式：
    1. 简单 URL 列表: ["url1", "url2", ...]
    2. 对话格式: { "dialogues": [{ "audio_url": "..." }, ...] }
    """
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    urls = []
    
    # 格式1: 直接是 URL 列表
    if isinstance(data, list):
        if all(isinstance(item, str) for item in data):
            urls = data
        else:
            # 可能是对话列表
            for item in data:
                if isinstance(item, dict) and 'audio_url' in item:
                    urls.append(item['audio_url'])
    
    # 格式2: 对话数据格式
    elif isinstance(data, dict):
        dialogues = data.get('dialogues', [])
        for d in dialogues:
            if 'audio_url' in d:
                urls.append(d['audio_url'])
    
    return urls


def merge_from_urls(urls: list[str], output_path: str, 
                    gap_ms: int = 300, keep_segments: bool = False,
                    segments_dir: Optional[str] = None) -> bool:
    """
    从 URL 列表下载并合并音频
    
    Args:
        urls: 音频 URL 列表
        output_path: 输出文件路径
        gap_ms: 音频之间的间隔（毫秒）
        keep_segments: 是否保留分段音频文件
        segments_dir: 分段音频保存目录
        
    Returns:
        是否成功
    """
    if not urls:
        print("错误: URL 列表为空")
        return False
    
    print(f"共 {len(urls)} 段音频待处理\n")
    
    # 确定临时/分段目录
    if keep_segments and segments_dir:
        temp_dir = segments_dir
        os.makedirs(temp_dir, exist_ok=True)
        cleanup = False
    else:
        temp_dir = tempfile.mkdtemp(prefix="audio_merge_")
        cleanup = True
    
    try:
        # 下载所有音频
        print("📥 下载音频文件...")
        audio_paths = []
        for i, url in enumerate(urls):
            local_path = download_audio(url, temp_dir, i)
            if local_path:
                audio_paths.append(local_path)
        
        if not audio_paths:
            print("错误: 没有成功下载任何音频")
            return False
        
        print(f"\n成功下载 {len(audio_paths)}/{len(urls)} 段音频")
        
        # 确定输出格式
        output_ext = os.path.splitext(output_path)[1].lower().lstrip('.')
        if output_ext not in ['mp3', 'wav', 'ogg', 'flac', 'm4a']:
            output_ext = 'mp3'
        
        # 合并音频
        success = merge_audio_files(audio_paths, output_path, gap_ms, output_ext)
        
        return success
        
    finally:
        # 清理临时文件
        if cleanup:
            import shutil
            try:
                shutil.rmtree(temp_dir)
            except:
                pass


def main():
    parser = argparse.ArgumentParser(
        description='合并多个音频 URL 为一个长音频文件',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 从 JSON 文件读取 URL 列表
  python merge_audio.py --input dialogue.json --output merged.mp3
  
  # 直接指定 URL
  python merge_audio.py --urls https://example.com/1.mp3 https://example.com/2.mp3 --output merged.mp3
  
  # 保留分段音频文件
  python merge_audio.py --input dialogue.json --output merged.mp3 --keep-segments --segments-dir ./segments
  
  # 自定义音频间隔
  python merge_audio.py --input dialogue.json --output merged.mp3 --gap 500
        """
    )
    
    parser.add_argument('--input', '-i', type=str,
                        help='包含音频 URL 的 JSON 文件路径')
    parser.add_argument('--urls', '-u', nargs='+',
                        help='音频 URL 列表')
    parser.add_argument('--output', '-o', type=str, required=True,
                        help='输出文件路径')
    parser.add_argument('--gap', '-g', type=int, default=300,
                        help='音频之间的间隔毫秒数 (默认: 300)')
    parser.add_argument('--keep-segments', '-k', action='store_true',
                        help='保留下载的分段音频文件')
    parser.add_argument('--segments-dir', '-s', type=str,
                        help='分段音频保存目录 (需配合 --keep-segments 使用)')
    
    args = parser.parse_args()
    
    # 检查参数
    if not args.input and not args.urls:
        parser.error("必须指定 --input 或 --urls")
    
    # 获取 URL 列表
    if args.input:
        if not os.path.exists(args.input):
            print(f"错误: 文件不存在 - {args.input}")
            sys.exit(1)
        urls = load_urls_from_json(args.input)
    else:
        urls = args.urls
    
    if not urls:
        print("错误: 未找到有效的音频 URL")
        sys.exit(1)
    
    # 执行合并
    success = merge_from_urls(
        urls=urls,
        output_path=args.output,
        gap_ms=args.gap,
        keep_segments=args.keep_segments,
        segments_dir=args.segments_dir
    )
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
