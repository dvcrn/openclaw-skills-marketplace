#!/usr/bin/env python3
"""
四川话语音识别测试脚本
专门测试四川方言识别效果
"""

import sys
import os

# 添加脚本目录到路径
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

from recognize_enhanced import recognize_dialect

def test_sichuanese():
    """测试四川话识别"""
    
    print("🌶️ 四川话语音识别测试")
    print("=" * 50)
    
    # 测试音频文件（如果有）
    if len(sys.argv) > 1:
        audio_file = sys.argv[1]
        
        print(f"\n📁 测试文件：{audio_file}")
        print(f"🎤 方言：四川话")
        print(f"🔧 模型：medium\n")
        
        # 使用medium模型识别四川话
        result = recognize_dialect(audio_file, dialect="sichuanese", model_size="medium")
        
        print("\n" + "=" * 50)
        print("✅ 测试完成！")
        print(f"📝 识别结果：{result['text']}")
        print(f"🌍 检测语言：{result['language']}")
        
    else:
        print("\n使用方法：")
        print(f"  python3 {sys.argv[0]} <音频文件>")
        print("\n示例：")
        print(f"  python3 {sys.argv[0]} test.wav")
        print(f"  python3 {sys.argv[0]} ~/Downloads/sichuanese.mp3")
        
        print("\n说明：")
        print("  • 使用medium模型（更准确）")
        print("  • 指定四川话方言")
        print("  • 支持WAV/MP3/OGG等格式")
        print("  • 推荐语音时长≥3秒")

if __name__ == "__main__":
    test_sichuanese()
