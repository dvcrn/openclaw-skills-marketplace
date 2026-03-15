#!/usr/bin/env python3
"""
四川话优化识别脚本
专门针对四川方言进行优化
"""

import sys
import os

# 四川话常见词汇映射表
SICHUAN_DIALECT_MAP = {
    # 疑问词
    "哪个": ["哪个", "拉个", "那果", "拉果", "腊个"],
    "啥子": ["啥子", "撒子", "沙子"],
    "咋个": ["咋个", "扎个", "乍个"],
    "好多": ["好多", "哈多"],
    
    # 人称代词
    "你是": ["你是", "你死", "泥石", "你尸"],
    "我是": ["我是", "握石", "卧石"],
    "他是": ["他是", "踏石"],
    
    # 疑问词
    "哪个": ["哪个", "拉个", "那果", "拉果", "腊个", "那哥", "拉哥"],
    "谁": ["谁", "睡", "水"],
    "啥子": ["啥子", "撒子", "沙子"],
    "咋个": ["咋个", "扎个", "乍个"],
    "好多": ["好多", "哈多"],
    
    # 常用词
    "的": ["的", "滴", "得"],
    "了": ["了", "罗", "咯"],
    "嘛": ["嘛", "买", "迈"],
    "噻": ["噻", "赛", "晒"],
    
    # 特殊词汇
    "得行": ["得行", "德行", "的行"],
    "不得": ["不得", "布德"],
    "晓得": ["晓得", "小德", "晓得"],
    "巴适": ["巴适", "巴士", "巴适"],
    
    # 句尾词
    "嗦": ["嗦", "所", "索"],
    "哈": ["哈", "哈"],
    "啵": ["啵", "波"],
}

def recognize_sichuanese_optimized(audio_file: str) -> dict:
    """
    优化的四川话识别
    
    Args:
        audio_file: 音频文件路径
    
    Returns:
        识别结果字典
    """
    try:
        import whisper
    except ImportError:
        print("❌ 错误：未安装openai-whisper")
        sys.exit(1)
    
    # 检查文件
    if not os.path.exists(audio_file):
        print(f"❌ 错误：文件不存在 - {audio_file}")
        sys.exit(1)
    
    print("\n🌶️ 四川话优化识别模式")
    print("=" * 50)
    print(f"📁 音频文件：{audio_file}\n")
    
    # 加载medium模型
    print("🔊 加载Whisper medium模型...")
    model = whisper.load_model("medium")
    
    # 四川话识别优化参数
    print("🌶️ 使用四川话优化参数...")
    result = model.transcribe(
        audio_file,
        language="zh",  # 明确指定中文
        task="transcribe",
        temperature=0.0,  # 使用确定性输出
        best_of=1,  # 只生成一个结果
        fp16=False,  # CPU模式
        # 使用initial_prompt引导模型识别四川话
        initial_prompt="这是四川话，可能包含：你是哪个、啥子、咋个、得行、巴适等词汇。",
    )
    
    # 提取识别文本
    text = result["text"].strip()
    
    # 显示原始结果
    print(f"\n📝 原始识别结果：")
    print(f"{'─' * 50}")
    print(f"{text}")
    print(f"{'─' * 50}\n")
    
    # 尝试应用方言映射优化
    optimized_text = apply_dialect_mapping(text)
    
    if optimized_text != text:
        print(f"✨ 优化后结果：")
        print(f"{'─' * 50}")
        print(f"{optimized_text}")
        print(f"{'─' * 50}\n")
    
    return {
        "original_text": text,
        "optimized_text": optimized_text,
        "language": result.get("language", "zh"),
    }


def apply_dialect_mapping(text: str) -> str:
    """
    应用方言映射优化
    
    Args:
        text: 原始识别文本
    
    Returns:
        优化后的文本
    """
    optimized = text
    
    # 先应用基础方言映射
    for standard, variants in SICHUAN_DIALECT_MAP.items():
        for variant in variants:
            if variant in optimized:
                optimized = optimized.replace(variant, standard)
                print(f"  🔄 映射：{variant} → {standard}")
    
    # 特殊映射：四川话"你是谁"通常说"你是哪个"
    if "你是谁" in optimized or "你是哪一个" in optimized:
        optimized = optimized.replace("你是谁", "你是哪个").replace("你是哪一个", "你是哪个")
        print(f"  🌶️ 四川话特殊映射：你是谁 → 你是哪个")
    
    return optimized


def test_with_known_text(audio_file: str, expected_text: str = None):
    """
    使用已知文本测试识别准确率
    
    Args:
        audio_file: 音频文件
        expected_text: 预期的正确文本
    """
    print("\n🧪 四川话识别测试模式")
    print("=" * 50)
    
    if expected_text:
        print(f"📋 预期文本：{expected_text}\n")
    
    result = recognize_sichuanese_optimized(audio_file)
    
    if expected_text:
        # 计算准确率
        original = result["original_text"]
        optimized = result["optimized_text"]
        
        print(f"\n📊 准确率分析：")
        print(f"  预期：{expected_text}")
        print(f"  原始：{original}")
        print(f"  优化：{optimized}")
        
        # 简单的字符匹配准确率
        original_accuracy = sum(1 for a, b in zip(original, expected_text) if a == b) / max(len(original), len(expected_text)) * 100
        optimized_accuracy = sum(1 for a, b in zip(optimized, expected_text) if a == b) / max(len(optimized), len(expected_text)) * 100
        
        print(f"\n  原始准确率：{original_accuracy:.1f}%")
        print(f"  优化准确率：{optimized_accuracy:.1f}%")
        print(f"  提升幅度：{optimized_accuracy - original_accuracy:.1f}%")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="四川话优化识别脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  # 基本识别
  %(prog)s audio.mp3
  
  # 指定预期文本（测试模式）
  %(prog)s audio.mp3 -e "你是哪个"
  
  # 查看方言映射表
  %(prog)s --show-map
        """
    )
    
    parser.add_argument("audio_file", nargs="?", help="音频文件路径")
    parser.add_argument("-e", "--expected", help="预期的正确文本（用于测试）")
    parser.add_argument("--show-map", action="store_true", help="显示方言映射表")
    
    args = parser.parse_args()
    
    # 显示方言映射表
    if args.show_map:
        print("\n🌶️ 四川话方言映射表：\n")
        for standard, variants in SICHUAN_DIALECT_MAP.items():
            print(f"  {standard:8} ← {', '.join(variants)}")
        print()
        return
    
    # 检查文件参数
    if not args.audio_file:
        parser.print_help()
        sys.exit(1)
    
    # 测试模式
    if args.expected:
        test_with_known_text(args.audio_file, args.expected)
    else:
        # 基本识别
        recognize_sichuanese_optimized(args.audio_file)


if __name__ == "__main__":
    main()
