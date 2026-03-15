#!/usr/bin/env python3
"""
增强版语音识别脚本
支持多种中国方言识别
"""

import sys
import os
import argparse

# 方言映射表（6种中文方言）
DIALECT_MAP = {
    "mandarin": {"code": "zh", "name": "普通话", "desc": "标准普通话"},
    "cantonese": {"code": "yue", "name": "粤语", "desc": "广东话、广西白话"},
    "shanghainese": {"code": "wuu", "name": "吴语", "desc": "上海话、苏州话"},
    "hakka": {"code": "hak", "name": "客家话", "desc": "客家方言"},
    "minnan": {"code": "nan", "name": "闽南话", "desc": "福建话、台湾话"},
    "sichuanese": {"code": "zh", "name": "四川话", "desc": "西南官话、巴蜀方言"},
    "auto": {"code": None, "name": "自动检测", "desc": "自动识别方言"},
}

# Whisper支持的主要中文方言（对应语言代码）
WHISPER_DIALECTS = {
    "zh": {"name": "普通话/四川话", "examples": ["北京", "成都", "重庆"]},
    "yue": {"name": "粤语", "examples": ["广州", "深圳", "香港"]},
    "wuu": {"name": "吴语", "examples": ["上海", "苏州", "杭州"]},
    "hak": {"name": "客家话", "examples": ["梅州", "惠州", "深圳"]},
    "nan": {"name": "闽南话", "examples": ["厦门", "泉州", "台湾"]},
}

# 模型性能对比
MODEL_INFO = {
    "tiny": {"size": "39MB", "speed": "极快", "accuracy": "低"},
    "base": {"size": "74MB", "speed": "快", "accuracy": "中"},
    "small": {"size": "244MB", "speed": "中", "accuracy": "良"},
    "medium": {"size": "769MB", "speed": "慢", "accuracy": "优"},
    "large": {"size": "1.5GB", "speed": "很慢", "accuracy": "最佳"},
}


def recognize_dialect(audio_file: str, dialect: str = "auto", model_size: str = "base") -> dict:
    """
    识别音频文件中的语音（支持多种方言）
    
    Args:
        audio_file: 音频文件路径
        dialect: 方言类型 (mandarin/cantonese/shanghainese/hakka/minnan/auto)
        model_size: Whisper模型大小
    
    Returns:
        {
            "text": 识别出的文字,
            "dialect": 检测到的方言,
            "language": 语言代码,
            "confidence": 置信度
        }
    """
    try:
        import whisper
    except ImportError:
        print("❌ 错误：未安装openai-whisper")
        print("请运行：pip install openai-whisper")
        sys.exit(1)
    
    # 检查文件
    if not os.path.exists(audio_file):
        print(f"❌ 错误：文件不存在 - {audio_file}")
        sys.exit(1)
    
    # 获取方言配置
    dialect_config = DIALECT_MAP.get(dialect, DIALECT_MAP["auto"])
    
    # 加载模型
    print(f"\n🔊 加载Whisper模型：{model_size}（{MODEL_INFO[model_size]['size']}）...")
    model = whisper.load_model(model_size)
    
    # 准备识别参数
    transcribe_params = {
        "task": "transcribe",
        "fp16": False,  # CPU模式
    }
    
    # 设置语言（auto模式不指定）
    if dialect_config["code"]:
        transcribe_params["language"] = dialect_config["code"]
        print(f"🎤 识别方言：{dialect_config['name']}（{dialect_config['desc']}）")
    else:
        print("🎤 自动检测方言...")
    
    # 识别音频
    print(f"📁 音频文件：{audio_file}\n")
    result = model.transcribe(audio_file, **transcribe_params)
    
    # 提取结果
    text = result["text"].strip()
    detected_lang = result.get("language", "unknown")
    
    # 显示结果
    print(f"📝 识别结果：\n{'─' * 40}")
    print(f"{text}")
    print(f"{'─' * 40}\n")
    
    # 显示检测到的语言
    if dialect == "auto" and detected_lang != "unknown":
        lang_name = {
            "zh": "普通话/四川话",
            "yue": "粤语",
            "wuu": "吴语",
            "hak": "客家话",
            "nan": "闽南话",
        }.get(detected_lang, detected_lang)
        print(f"🌍 检测到的方言：{lang_name}（{detected_lang}）")
    
    return {
        "text": text,
        "dialect": dialect,
        "language": detected_lang,
        "confidence": result.get("segments", [{}])[0].get("avg_logprob", 0) if result.get("segments") else 0
    }


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="增强版语音识别 - 支持多种中国方言",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
方言列表：
  mandarin     - 普通话（默认）
  cantonese    - 粤语（广东话）
  shanghainese - 吴语（上海话）
  hakka        - 客家话
  minnan       - 闽南话（台湾话）
  sichuanese   - 四川话（西南官话）
  auto         - 自动检测

示例：
  %(prog)s audio.mp3                          # 自动检测方言
  %(prog)s audio.mp3 -d cantonese             # 粤语识别
  %(prog)s audio.mp3 -d sichuanese            # 四川话识别
  %(prog)s audio.mp3 -m medium -d mandarin    # 使用medium模型识别普通话
  %(prog)s audio.mp3 --list-dialects          # 列出所有方言
        """
    )
    
    parser.add_argument("audio_file", nargs="?", help="音频文件路径")
    parser.add_argument("-d", "--dialect", default="auto", 
                       choices=list(DIALECT_MAP.keys()),
                       help="方言类型（默认：auto自动检测）")
    parser.add_argument("-m", "--model", default="base",
                       choices=list(MODEL_INFO.keys()),
                       help="模型大小（默认：base）")
    parser.add_argument("--list-dialects", action="store_true",
                       help="列出所有支持的方言")
    parser.add_argument("--list-models", action="store_true",
                       help="列出所有模型及其性能")
    
    args = parser.parse_args()
    
    # 列出方言
    if args.list_dialects:
        print("\n支持的方言：\n")
        for code, info in DIALECT_MAP.items():
            print(f"  {code:12} - {info['name']:8} {info['desc']}")
        print("\n方言说明：")
        print("  • 四川话使用zh代码（与普通话同组）")
        print("  • 升级到medium模型可提高方言识别准确率")
        print("  • 推荐指定方言以获得更好效果")
        print()
        return
    
    # 列出模型
    if args.list_models:
        print("\n可用模型：\n")
        for model, info in MODEL_INFO.items():
            print(f"  {model:8} - 大小：{info['size']:7} | 速度：{info['speed']:4} | 准确度：{info['accuracy']}")
        print("\n推荐：")
        print("  • 快速测试：tiny/base")
        print("  • 日常使用：small/medium")
        print("  • 高精度需求：large")
        print()
        return
    
    # 检查文件参数
    if not args.audio_file:
        parser.print_help()
        sys.exit(1)
    
    # 识别音频
    recognize_dialect(args.audio_file, args.dialect, args.model)


if __name__ == "__main__":
    main()
