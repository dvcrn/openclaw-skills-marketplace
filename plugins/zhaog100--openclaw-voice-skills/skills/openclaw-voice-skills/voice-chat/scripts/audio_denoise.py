#!/usr/bin/env python3
"""
语音降噪处理模块
使用ffmpeg进行音频降噪
"""

import os
import sys
import subprocess
import tempfile
from pathlib import Path


def reduce_noise_ffmpeg(input_file: str, output_file: str = None, 
                        noise_level: str = "moderate") -> str:
    """
    使用ffmpeg进行音频降噪
    
    Args:
        input_file: 输入音频文件
        output_file: 输出文件路径（可选）
        noise_level: 降噪级别 (light/moderate/aggressive)
    
    Returns:
        降噪后的文件路径
    """
    
    # 检查输入文件
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"文件不存在：{input_file}")
    
    # 输出文件
    if output_file is None:
        suffix = Path(input_file).suffix
        output_file = input_file.replace(suffix, f"_denoised{suffix}")
    
    print(f"\n🔊 音频降噪处理")
    print("=" * 50)
    print(f"📁 输入文件：{input_file}")
    print(f"🎯 降噪级别：{noise_level}")
    print(f"💾 输出文件：{output_file}\n")
    
    # 根据降噪级别设置参数
    if noise_level == "light":
        # 轻度降噪
        filter_complex = (
            "highpass=f=200,"  # 高通滤波器，去除低频噪音
            "lowpass=f=3000,"  # 低通滤波器，去除高频噪音
            "afftdn=nf=-25"    # FFT降噪，轻度
        )
    elif noise_level == "aggressive":
        # 强力降噪
        filter_complex = (
            "highpass=f=300,"
            "lowpass=f=2500,"
            "afftdn=nf=-35,"
            "afftdn=nf=-35"    # 两次降噪
        )
    else:  # moderate
        # 中等降噪（默认）
        filter_complex = (
            "highpass=f=200,"
            "lowpass=f=3000,"
            "afftdn=nf=-30"
        )
    
    # 构建ffmpeg命令
    cmd = [
        "ffmpeg",
        "-y",  # 覆盖输出文件
        "-i", input_file,  # 输入文件
        "-af", filter_complex,  # 音频滤镜
        "-acodec", "pcm_s16le",  # 16位PCM编码
        "-ar", "16000",  # 16kHz采样率（Whisper推荐）
        "-ac", "1",  # 单声道
        output_file
    ]
    
    print(f"🔧 降噪参数：{filter_complex}\n")
    
    # 执行降噪
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        print(f"✅ 降噪完成：{output_file}\n")
        return output_file
    except subprocess.CalledProcessError as e:
        print(f"❌ 降噪失败：{e.stderr}")
        raise


def analyze_audio_quality(audio_file: str) -> dict:
    """
    分析音频质量
    
    Args:
        audio_file: 音频文件路径
    
    Returns:
        音频质量信息
    """
    cmd = [
        "ffprobe",
        "-v", "quiet",
        "-print_format", "json",
        "-show_format",
        "-show_streams",
        audio_file
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        import json
        info = json.loads(result.stdout)
        
        # 提取关键信息
        stream = info.get("streams", [{}])[0]
        format_info = info.get("format", {})
        
        return {
            "duration": float(format_info.get("duration", 0)),
            "sample_rate": int(stream.get("sample_rate", 0)),
            "channels": int(stream.get("channels", 0)),
            "codec": stream.get("codec_name", "unknown"),
            "bit_rate": int(format_info.get("bit_rate", 0)),
        }
    except Exception as e:
        print(f"⚠️ 无法分析音频：{e}")
        return {}


def process_with_denoise(audio_file: str, auto_denoise: bool = True) -> str:
    """
    处理音频（自动降噪）
    
    Args:
        audio_file: 原始音频文件
        auto_denoise: 是否自动降噪
    
    Returns:
        处理后的音频文件路径
    """
    
    if not auto_denoise:
        return audio_file
    
    # 分析音频质量
    print("\n📊 分析音频质量...")
    quality = analyze_audio_quality(audio_file)
    
    if quality:
        print(f"  时长：{quality.get('duration', 0):.1f}秒")
        print(f"  采样率：{quality.get('sample_rate', 0)}Hz")
        print(f"  声道：{quality.get('channels', 0)}")
        print(f"  编码：{quality.get('codec', 'unknown')}")
    
    # 判断是否需要降噪
    # 如果时长<2秒或采样率<16000，进行降噪
    needs_denoise = (
        quality.get("duration", 10) < 2 or
        quality.get("sample_rate", 16000) < 16000
    )
    
    if needs_denoise:
        print("\n⚠️ 检测到音质可能不佳，进行降噪处理...")
        return reduce_noise_ffmpeg(audio_file, noise_level="moderate")
    else:
        print("\n✅ 音质良好，无需降噪")
        return audio_file


def test_denoise(input_file: str):
    """
    测试降噪效果
    
    Args:
        input_file: 测试音频文件
    """
    print("\n🧪 降噪效果测试")
    print("=" * 50)
    
    # 原始音频分析
    print("\n📊 原始音频：")
    original_quality = analyze_audio_quality(input_file)
    if original_quality:
        for key, value in original_quality.items():
            print(f"  {key}: {value}")
    
    # 轻度降噪
    print("\n🔧 轻度降噪：")
    light_file = reduce_noise_ffmpeg(input_file, noise_level="light")
    light_quality = analyze_audio_quality(light_file)
    
    # 中等降噪
    print("\n🔧 中等降噪：")
    moderate_file = reduce_noise_ffmpeg(input_file, noise_level="moderate")
    moderate_quality = analyze_audio_quality(moderate_file)
    
    # 强力降噪
    print("\n🔧 强力降噪：")
    aggressive_file = reduce_noise_ffmpeg(input_file, noise_level="aggressive")
    aggressive_quality = analyze_audio_quality(aggressive_file)
    
    print("\n✅ 测试完成！")
    print(f"  轻度降噪：{light_file}")
    print(f"  中等降噪：{moderate_file}")
    print(f"  强力降噪：{aggressive_file}")
    
    print("\n💡 建议：")
    print("  • 语音时长≥3秒：使用轻度降噪")
    print("  • 语音时长<3秒或有背景噪音：使用中等降噪")
    print("  • 严重噪音：使用强力降噪")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="语音降噪处理工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
降噪级别：
  light      - 轻度降噪，保留更多细节
  moderate   - 中等降噪，平衡效果（默认）
  aggressive - 强力降噪，可能损失部分语音

示例：
  # 基本降噪
  %(prog)s audio.mp3
  
  # 指定降噪级别
  %(prog)s audio.mp3 -l aggressive
  
  # 指定输出文件
  %(prog)s audio.mp3 -o denoised.wav
  
  # 测试降噪效果
  %(prog)s audio.mp3 --test
        """
    )
    
    parser.add_argument("audio_file", nargs="?", help="音频文件路径")
    parser.add_argument("-o", "--output", help="输出文件路径")
    parser.add_argument("-l", "--level", 
                       choices=["light", "moderate", "aggressive"],
                       default="moderate",
                       help="降噪级别（默认：moderate）")
    parser.add_argument("--test", action="store_true",
                       help="测试降噪效果")
    
    args = parser.parse_args()
    
    # 测试模式
    if args.test:
        if not args.audio_file:
            print("❌ 测试模式需要指定音频文件")
            sys.exit(1)
        test_denoise(args.audio_file)
        return
    
    # 检查文件参数
    if not args.audio_file:
        parser.print_help()
        sys.exit(1)
    
    # 执行降噪
    reduce_noise_ffmpeg(args.audio_file, args.output, args.level)


if __name__ == "__main__":
    main()
