#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
哈萨克文字转换工具
支持西里尔文和阿拉伯文之间的双向转换

用法:
    kazConvert A "сэнің атың кім болады?"   # 西里尔文转阿拉伯文
    kazConvert C "سەنىڭ اتىڭ كىم بولادى؟"   # 阿拉伯文转西里尔文
"""

import sys
import os

# 设置UTF-8编码
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'

CYRILLIC_TO_ARABIC_MAP = {
    'ю': 'يۋ', 'ё': 'يو', 'щ': 'شش', 'ц': 'تس', 'я': 'يا', 'ә': 'ءا', 'і': 'ءى', 'ү': 'ءۇ', 'ө': 'ءو',
    'й': 'ي', 'у': 'ۋ', 'к': 'ك', 'е': 'ە', 'н': 'ن', 'г': 'گ', 'ш': 'ش', 'з': 'ز',
    'х': 'ح', 'ф': 'ف', 'ы': 'ى', 'в': 'ۆ', 'а': 'ا', 'п': 'پ', 'р': 'ر', 'о': 'و',
    'л': 'ل', 'д': 'د', 'ж': 'ج', 'э': 'ە', 'ч': 'چ', 'с': 'س', 'м': 'م', 'и': 'ي', 'т': 'ت',
    'ь': '', 'б': 'ب', 'ң': 'ڭ', 'ғ': 'ع', 'ұ': 'ۇ', 'қ': 'ق', 'һ': 'ھ',
    ';': '؛', ',': '،', '?': '؟'
}

ARABIC_TO_CYRILLIC_MAP = {}
for cyrillic, arabic in CYRILLIC_TO_ARABIC_MAP.items():
    if arabic != '':
        ARABIC_TO_CYRILLIC_MAP[arabic] = cyrillic


def arabic_grammar(text):
    lines = text.split('\n')
    processed_lines = []
    for line in lines:
        words = line.split()
        processed_words = []
        for word in words:
            if 'ء' in word:
                if 'ك' in word or 'گ' in word or 'ە' in word:
                    word = word.replace('ء', '')
                else:
                    if len(word) > 2:
                        word = 'ء' + word.replace('ء', '')
                        first_two = word[:2]
                        rest = word[2:].replace('ء', '')
                        word = first_two + rest
            processed_words.append(word)
        processed_lines.append(' '.join(processed_words))
    return '\n'.join(processed_lines)


def cyrillic_grammar(text):
    lines = text.split('\n')
    processed_lines = []
    for line in lines:
        words = line.split()
        processed_words = []
        for word in words:
            if 'к' in word or 'г' in word or 'э' in word or 'ء' in word:
                new_word = ''
                for char in word:
                    if char == 'а':
                        new_word += 'ә'
                    elif char == 'о':
                        new_word += 'ө'
                    elif char == 'ұ':
                        new_word += 'ү'
                    elif char == 'ы':
                        new_word += 'і'
                    else:
                        new_word += char
                word = new_word
            word = word.replace('ء', '')
            word = word.replace('Ь', '')
            processed_words.append(word)
        processed_lines.append(' '.join(processed_words))
    return '\n'.join(processed_lines)


def convert_cyrillic_to_arabic(text):
    text = text.lower()
    result = ''
    for char in text:
        if char in CYRILLIC_TO_ARABIC_MAP:
            result += CYRILLIC_TO_ARABIC_MAP[char]
        else:
            result += char
    return arabic_grammar(result)


def convert_arabic_to_cyrillic(text):
    result = text
    arabic_chars = sorted(ARABIC_TO_CYRILLIC_MAP.keys(), key=len, reverse=True)
    for arabic_char in arabic_chars:
        result = result.replace(arabic_char, ARABIC_TO_CYRILLIC_MAP[arabic_char])
    return cyrillic_grammar(result)


def main():
    if len(sys.argv) < 3:
        print("用法: kazConvert A \"сэнің атың кім болады?\"   # 西里尔文转阿拉伯文")
        print("      kazConvert C \"سەنىڭ اتىڭ كىم بولادى؟\"   # 阿拉伯文转西里尔文")
        sys.exit(1)
    
    mode = sys.argv[1].upper()
    text = sys.argv[2]
    
    if mode == 'A':
        result = convert_cyrillic_to_arabic(text)
    elif mode == 'C':
        result = convert_arabic_to_cyrillic(text)
    else:
        print(f"错误: 无效的模式 '{mode}'")
        print("模式必须是 'A' (西里尔文转阿拉伯文) 或 'C' (阿拉伯文转西里尔文)")
        sys.exit(1)
    
    print(result)


if __name__ == '__main__':
    main()
