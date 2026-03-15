#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智谱AI GLM-4V 图片理解脚本
用于分析图片内容并返回描述
"""

import os
import sys
import base64
import json

try:
    from zhipuai import ZhipuAI
except ImportError:
    print("错误: 请先安装智谱AI SDK")
    print("运行: pip install zhipuai")
    sys.exit(1)


def get_api_key():
    """获取API Key，优先从环境变量，其次从用户输入"""
    api_key = os.getenv("ZHIPU_API_KEY")
    if api_key:
        return api_key
    
    print("\n未找到 ZHIPU_API_KEY 环境变量")
    print("请输入你的智谱AI API Key (或按Ctrl+C退出)")
    print("获取地址: https://bigmodel.cn/console/apikeys")
    api_key = input("\nAPI Key: ").strip()
    
    if not api_key:
        print("错误: API Key不能为空")
        sys.exit(1)
    
    return api_key


def encode_image_to_base64(image_path):
    """将图片文件转为base64编码"""
    try:
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    except FileNotFoundError:
        print(f"错误: 找不到图片文件 {image_path}")
        sys.exit(1)
    except Exception as e:
        print(f"错误: 读取图片失败 {e}")
        sys.exit(1)


def analyze_image(image_path, question, api_key):
    """调用智谱API分析图片"""
    client = ZhipuAI(api_key=api_key)
    
    # 判断是本地文件还是URL
    if image_path.startswith("http://") or image_path.startswith("https://"):
        image_url = image_path
    else:
        # 本地文件转为base64
        b64_img = encode_image_to_base64(image_path)
        image_url = f"data:image/jpeg;base64,{b64_img}"
    
    try:
        response = client.chat.completions.create(
            model="glm-4v",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": question},
                        {"type": "image_url", "image_url": {"url": image_url}}
                    ]
                }
            ]
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"API调用错误: {e}")
        sys.exit(1)


def main():
    if len(sys.argv) < 2:
        print("用法: python analyze_image.py <图片路径> [<问题>]")
        print("\n示例:")
        print('  python analyze_image.py /path/to/image.jpg "这张图片里有什么?"')
        print('  python analyze_image.py https://example.com/image.jpg "描述这张图片"')
        sys.exit(1)
    
    image_path = sys.argv[1]
    question = sys.argv[2] if len(sys.argv) > 2 else "请详细描述这张图片的内容"
    
    print(f"\n图片: {image_path}")
    print(f"问题: {question}")
    print("\n正在分析...")
    
    api_key = get_api_key()
    result = analyze_image(image_path, question, api_key)
    
    print("\n" + "="*50)
    print("分析结果:")
    print("="*50)
    print(result)


if __name__ == "__main__":
    main()
