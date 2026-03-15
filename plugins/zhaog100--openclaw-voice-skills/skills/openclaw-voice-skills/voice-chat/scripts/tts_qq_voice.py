#!/usr/bin/env python3
"""
QQ语音消息生成工具
生成QQ Bot可播放的SILK格式语音消息
"""

import os
import sys
import subprocess
import tempfile
from pathlib import Path
from io import BytesIO

def text_to_silk(text: str, output_file: str = None, rate: int = 150) -> str:
    """
    将文本转换为SILK格式语音文件
    
    Args:
        text: 要转换的文本
        output_file: 输出文件路径（可选）
        rate: 语速（默认150）
    
    Returns:
        SILK文件路径
    """
    
    # 输出文件
    if output_file is None:
        output_file = tempfile.mktemp(suffix='.silk')
    
    # 步骤1: 使用espeak生成WAV
    wav_file = tempfile.mktemp(suffix='.wav')
    cmd = ['espeak', '-v', 'zh', '-s', str(rate), '-w', wav_file, text]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if not os.path.exists(wav_file) or os.path.getsize(wav_file) == 0:
            raise Exception("espeak生成WAV失败")
    except Exception as e:
        print(f"❌ WAV生成失败：{e}")
        sys.exit(1)
    
    # 步骤2: 转换为QQ支持的格式（24kHz, mono, PCM）
    pcm_file = tempfile.mktemp(suffix='.pcm')
    cmd = [
        'ffmpeg', '-y', '-i', wav_file,
        '-f', 's16le',  # PCM格式
        '-ar', '24000',  # QQ要求的采样率
        '-ac', '1',  # 单声道
        '-acodec', 'pcm_s16le',
        pcm_file
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if not os.path.exists(pcm_file) or os.path.getsize(pcm_file) == 0:
            raise Exception("PCM转换失败")
    except Exception as e:
        print(f"❌ PCM转换失败：{e}")
        sys.exit(1)
    
    # 步骤3: 转换为SILK格式
    try:
        import pysilk
        
        # 读取PCM数据
        with open(pcm_file, 'rb') as f:
            pcm_data = f.read()
        
        # 编码为SILK（QQ要求的24000Hz采样率)
        output_buffer = BytesIO()
        pysilk.encode(BytesIO(pcm_data), output_buffer, 24000, 24000)
        
        # 保存SILK文件
        with open(output_file, 'wb') as f:
            f.write(output_buffer.getvalue())
        
        # 清理临时文件
        os.remove(wav_file)
        os.remove(pcm_file)
        
        print(f"✅ SILK语音生成成功：{output_file}")
        print(f"   文件大小：{os.path.getsize(output_file)} 字节")
        return output_file
        
    except ImportError:
        print("❌ 错误：未安装silk-python")
        print("请运行：pip3 install silk-python --break-system-packages")
        sys.exit(1)
    except Exception as e:
        print(f"❌ SILK编码失败：{e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="QQ语音消息生成工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  # 生成语音消息
  %(prog)s "官家，语音消息已修复！"
  
  # 指定输出文件
  %(prog)s "你好" -o voice.silk
  
  # 调整语速
  %(prog)s "测试语音" -r 120
        """
    )
    
    parser.add_argument("text", help="要转换的文本")
    parser.add_argument("-o", "--output", help="输出文件路径")
    parser.add_argument("-r", "--rate", type=int, default=150, help="语速（默认150）")
    
    args = parser.parse_args()
    
    # 生成语音
    silk_file = text_to_silk(args.text, args.output, args.rate)
    print(f"\n🔊 语音文件：{silk_file}")


if __name__ == "__main__":
    main()
