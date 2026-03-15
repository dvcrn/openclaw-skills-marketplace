#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
蒙语翻译脚本 (Python 版本)
基于毅金云 API 实现蒙汉互译

使用方法:
  python3 translate.py "文本" --from mn --to zh
  python3 translate.py "文本" --target mn
"""

import os
import sys
import argparse
import json
import urllib.request
import urllib.error

# 配置
API_KEY = os.environ.get('MENGGUYU_API_KEY', '')
API_BASE = 'https://api.mengguyu.cn'  # TODO: 确认实际 API 地址

# 语言代码映射
LANG_MAP = {
    'mn': 'mongolian',
    'zh': 'chinese',
    'cn': 'chinese',
}


def translate(text, from_lang='mn', to_lang='zh'):
    """
    调用翻译 API
    
    Args:
        text: 待翻译文本
        from_lang: 源语言代码
        to_lang: 目标语言代码
    
    Returns:
        翻译结果
    """
    if not API_KEY:
        print('❌ 错误：请设置 MENGGUYU_API_KEY 环境变量')
        print('   示例：export MENGGUYU_API_KEY="your_key"')
        sys.exit(1)
    
    from_lang = LANG_MAP.get(from_lang, from_lang)
    to_lang = LANG_MAP.get(to_lang, to_lang)
    
    # TODO: 根据实际 API 文档调整请求格式
    data = {
        'text': text,
        'from': from_lang,
        'to': to_lang,
    }
    
    req = urllib.request.Request(
        f'{API_BASE}/v1/translate',  # TODO: 确认实际 API 路径
        data=json.dumps(data).encode('utf-8'),
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {API_KEY}',
        },
        method='POST'
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result.get('translatedText') or result.get('text') or result
    except urllib.error.HTTPError as e:
        raise Exception(f'API 请求失败：{e.code} - {e.read().decode("utf-8")}')
    except urllib.error.URLError as e:
        raise Exception(f'网络错误：{e.reason}')


def main():
    parser = argparse.ArgumentParser(
        description='蒙语翻译工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  python3 translate.py "ᠰᠠᠶᠢᠨ ᠪᠠᠶᠢᠨᠠ ᠤᠤ" --from mn --to zh
  python3 translate.py "你好" --target mn

环境变量:
  MENGGUYU_API_KEY  毅金云 API Key
        '''
    )
    
    parser.add_argument('text', nargs='?', help='待翻译的文本')
    parser.add_argument('--from', dest='from_lang', default='mn',
                        help='源语言 (mn=蒙古语，zh=中文) 默认：mn')
    parser.add_argument('--to', dest='to_lang', default='zh',
                        help='目标语言 (mn=蒙古语，zh=中文) 默认：zh')
    parser.add_argument('--target', dest='target',
                        help='目标语言（简写，等同于 --to）')
    
    args = parser.parse_args()
    
    if args.target:
        args.to_lang = args.target
    
    if not args.text:
        parser.print_help()
        sys.exit(1)
    
    try:
        print(f'🔄 翻译中... ({args.from_lang} → {args.to_lang})')
        result = translate(args.text, args.from_lang, args.to_lang)
        print(f'✅ 翻译结果：{result}')
    except Exception as e:
        print(f'❌ {e}')
        sys.exit(1)


if __name__ == '__main__':
    main()
