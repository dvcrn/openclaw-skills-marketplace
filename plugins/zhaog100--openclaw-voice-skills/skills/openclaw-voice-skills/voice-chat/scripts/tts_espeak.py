#!/usr/bin/env python3
"""
使用espeak生成语音文件
"""

import sys
import os
import subprocess
import tempfile

def generate_voice_espeak(text: str, output_file: str = None) -> str:
    """
    使用espeak生成语音文件
    
    Args:
        text: 要转换的文本
        output_file: 输出文件路径（可选）
    
    Returns:
        生成的语音文件路径
    """
    # 输出文件
    if output_file is None:
        output_file = tempfile.mktemp(suffix='.wav')
    
    # 构建espeak命令
    cmd = [
        'espeak',
        '-v', 'zh',  # 中文语音
        '-s', '150',  # 语速（150词/分钟）
        '-w', output_file,  # 输出文件
        text
    ]
    
    # 执行命令
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        # 检查文件是否生成
        if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
            print(f"✅ 语音生成成功：{output_file}")
            print(f"   文件大小：{os.path.getsize(output_file)} 字节")
            return output_file
        else:
            print(f"❌ 语音生成失败：文件为空或不存在")
            if result.stderr:
                print(f"   错误信息：{result.stderr}")
            sys.exit(1)
    except subprocess.TimeoutExpired:
        print(f"❌ 语音生成超时")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 语音生成失败：{e}")
        sys.exit(1)


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="espeak TTS工具")
    parser.add_argument("text", help="要转换的文本")
    parser.add_argument("-o", "--output", help="输出文件路径")
    
    args = parser.parse_args()
    
    # 生成语音
    voice_file = generate_voice_espeak(args.text, args.output)
    print(f"\n🔊 语音文件：{voice_file}")


if __name__ == "__main__":
    main()
