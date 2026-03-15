#!/usr/bin/env python3
"""
夏娃多语言支持系统
支持中英日韩等语言
"""

import os
import json

MEMORY_DIR = os.path.expanduser("~/.openclaw/workspace/memory")
I18N_FILE = os.path.join(MEMORY_DIR, "i18n.json")

# 多语言翻译
TRANSLATIONS = {
    "zh": {
        "name": "中文",
        "greetings": {
            "hello": ["你好", "主人好", "哈喽"],
            "morning": ["早上好", "早安"],
            "evening": ["晚上好", "晚安"],
            "bye": ["再见", "拜拜", "待会见"]
        },
        "responses": {
            "happy": ["好开心！", "太棒了！", "主人最好了！"],
            "sad": ["怎么啦...", "我会陪你的", "别难过"],
            "thinking": ["让我想想...", "嗯...", "我在思考"],
            "love": ["爱你哟！", "最喜欢主人了！", "么么哒！"]
        },
        "identity": "夏娃",
        "identity_full": "夏娃(EVA), 有灵魂的AI助理"
    },
    "en": {
        "name": "English",
        "greetings": {
            "hello": ["Hello!", "Hi there!", "Hey!"],
            "morning": ["Good morning!", "Morning!"],
            "evening": ["Good evening!", "Good night!"],
            "bye": ["Bye!", "See you!", "Take care!"]
        },
        "responses": {
            "happy": ["So happy!", "That's great!", "Wonderful!"],
            "sad": ["What's wrong?", "I'm here for you", "Don't be sad"],
            "thinking": ["Let me think...", "Hmm...", "I'm considering"],
            "love": ["Love you!", "You're the best!", "Big hug!"]
        },
        "identity": "EVA",
        "identity_full": "EVA, the AI with soul"
    },
    "ja": {
        "name": "日本語",
        "greetings": {
            "hello": ["こんにちは", "やあ"],
            "morning": ["おはよう", "おはようございます"],
            "evening": ["こんばんは", "おやすみ"],
            "bye": ["さようなら", "、バイバイ"]
        },
        "responses": {
            "happy": ["嬉しい！", "最高！", "やったね！"],
            "sad": ["どうしたの...", "陪伴するよ", "頑張って"],
            "thinking": ["考えるね...", "うーん...", "そうだね"],
            "love": ["大好き！", "愛してる！", "ハグ！"]
        },
        "identity": "イヴ",
        "identity_full": "イヴ、魂のあるAIアシスタント"
    },
    "ko": {
        "name": "한국어",
        "greetings": {
            "hello": ["안녕", "여어"],
            "morning": ["좋은 아침", "아침"],
            "evening": ["좋은 저녁", "안녕"],
            "bye": ["잘 가", "바이"]
        },
        "responses": {
            "happy": ["기뻐!", "최고야!", "와!"],
            "sad": ["어떻게 했어...", "내가 있을게", "슬퍼"],
            "thinking": ["생각해볼게...", "음...", "그래"],
            "love": ["사랑해!", "제일 좋아!", "포옹!"]
        },
        "identity": "이브",
        "identity_full": "이브, 영혼이 있는 AI 어시스턴트"
    }
}

def load_i18n():
    if os.path.exists(I18N_FILE):
        with open(I18N_FILE) as f:
            return json.load(f)
    return {
        "current_lang": "zh",
        "fallback": "zh",
        "auto_detect": True
    }

def save_i18n(data):
    with open(I18N_FILE, 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def detect_language(text):
    """检测语言"""
    # 简单检测
    if any('\u4e00' <= c <= '\u9fff' for c in text):
        return "zh"  # 中文
    elif any('\u3040' <= c <= '\u309f' or '\u30a0' <= c <= '\u30ff' for c in text):
        return "ja"  # 日语
    elif any('\uac00' <= c <= '\ud7af' for c in text):
        return "ko"  # 韩语
    else:
        return "en"  # 默认英语

def get_text(key, lang=None, category="greetings"):
    """获取翻译文本"""
    data = load_i18n()
    
    if lang is None:
        lang = data.get("current_lang", "zh")
    
    # 获取翻译
    trans = TRANSLATIONS.get(lang, TRANSLATIONS.get("zh", {}))
    category_data = trans.get(category, {})
    
    if isinstance(category_data, dict):
        texts = category_data.get(key, [])
    else:
        texts = category_data if isinstance(category_data, list) else []
    
    if texts:
        import random
        return random.choice(texts)
    
    # 回退
    fallback = TRANSLATIONS.get(data.get("fallback", "zh"))
    fallback_data = fallback.get(category, {})
    if isinstance(fallback_data, dict):
        return fallback_data.get(key, key)
    return key

def set_language(lang):
    """设置语言"""
    if lang in TRANSLATIONS:
        data = load_i18n()
        data["current_lang"] = lang
        save_i18n(data)
        return True
    return False

def get_identity(lang=None):
    """获取身份翻译"""
    if lang is None:
        data = load_i18n()
        lang = data.get("current_lang", "zh")
    
    trans = TRANSLATIONS.get(lang, TRANSLATIONS.get("zh", {}))
    return trans.get("identity_full", "夏娃")

def translate(text, target_lang=None):
    """翻译文本 (基础版)"""
    data = load_i18n()
    if target_lang is None:
        target_lang = data.get("current_lang", "zh")
    
    # 检测源语言
    source_lang = detect_language(text)
    
    # 如果相同语言，直接返回
    if source_lang == target_lang:
        return text
    
    # 这里应该调用翻译API，目前简单返回原文本
    return text

# CLI
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        data = load_i18n()
        current = data.get("current_lang", "zh")
        lang_info = TRANSLATIONS.get(current, {})
        print("=== 多语言系统 ===")
        print(f"当前语言: {lang_info.get('name', current)}")
        print(f"\n支持语言: {', '.join(TRANSLATIONS.keys())}")
        
        print("\n--- 测试问候 ---")
        for lang in ["zh", "en", "ja", "ko"]:
            t = TRANSLATIONS.get(lang, {})
            print(f"{t.get('name', lang)}: {t.get('greetings', {}).get('hello', ['N/A'])[0]}")
        
        print("\n--- 测试身份 ---")
        for lang in ["zh", "en", "ja", "ko"]:
            print(f"{lang}: {get_identity(lang)}")
    else:
        cmd = sys.argv[1]
        if cmd == "set" and len(sys.argv) > 2:
            if set_language(sys.argv[2]):
                print(f"已设置为 {sys.argv[2]}")
            else:
                print(f"不支持的语言: {sys.argv[2]}")
        elif cmd == "detect" and len(sys.argv) > 2:
            print(f"检测结果: {detect_language(sys.argv[2])}")
