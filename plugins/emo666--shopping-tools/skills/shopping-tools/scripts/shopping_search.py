#!/usr/bin/env python3
"""
购物搜索综合工具
支持：查券获取优惠链接、全网搜索、线报群搜索
"""

import sys
import os

# 导入API封装
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from zhetaoke_api import ZheTaoKeAPI

def format_item(item, index, plat_name):
    """格式化商品信息"""
    output = []
    
    title = item.get('title', '')
    price = item.get('size', '')
    quanhou = item.get('quanhou_jiage', '')
    coupon = item.get('coupon_info_money', '')
    shop = item.get('nick', '')
    sales = item.get('volume', '')
    tao_id = item.get('tao_id', '')
    
    output.append(f"🥇 商品 {index} [{plat_name}]")
    output.append(f"📦 {title}")
    
    if shop:
        output.append(f"🏪 {shop}")
    
    if sales and sales != '0':
        output.append(f"📈 销量：{sales}")
    
    
    if price:
        output.append(f"💰 原价：¥{price}")
    if coupon and coupon != '0':
        output.append(f"🎫 优惠券：¥{coupon}")
    if quanhou:
        output.append(f"💰 券后价：¥{quanhou}")
    
    # 获取优惠链接
    if tao_id:
        api = ZheTaoKeAPI()
        if plat_name == '淘宝':
            url = f"https://item.taobao.com/item.htm?id={tao_id}"
            result = api.taobao_convert(url)
        else:
            url = f"https://item.jd.com/{tao_id}.html"
            result = api.jd_convert(url)
        
        if result and result.get('status') == 200:
            short_url = result.get('shorturl', '')
            tkl = result.get('result_tkl', '')
            
            output.append(f"")
            output.append(f"━━━━━━━━━━━━━━━━━━")
            if short_url:
                output.append(f"👇 {short_url}")
            if tkl:
                output.append(f"📋 淘口令：{tkl}")
            output.append(f"━━━━━━━━━━━━━━━━━━")
    
    return "\n".join(output)

def search_all(keyword, max_results=5):
    """综合搜索"""
    api = ZheTaoKeAPI()
    all_results = []
    
    print(f"🔍 正在搜索「{keyword}」...\n")
    
    # 1. 淘宝搜索
    print("🍑 搜索淘宝...")
    result = api.taobao_search(keyword, page_size=max_results)
    if result and result.get('status') == 200:
        items = result.get('content', [])
        print(f"   ✅ 找到 {len(items)} 个商品")
        for item in items:
            item['plat'] = '1'
            all_results.append((item, '淘宝'))
    else:
        print(f"   ❌ 淘宝搜索失败")
    
    # 2. 京东搜索
    print("🐶 搜索京东...")
    result = api.jd_search(keyword, page_size=max_results)
    if result and result.get('status') == 200:
        items = result.get('content', [])
        print(f"   ✅ 找到 {len(items)} 个商品")
        for item in items:
            item['plat'] = '2'
            all_results.append((item, '京东'))
    else:
        print(f"   ❌ 京东搜索失败")
    
    return all_results[:max_results]

def main():
    if len(sys.argv) < 2:
        print("购物搜索综合工具")
        print("=" * 50)
        print("\n使用方法：")
        print("  python3 shopping_search.py <关键词>")
        print("\n示例：")
        print("  python3 shopping_search.py 牛奶")
        print("  python3 shopping_search.py iPhone")
        print("  python3 shopping_search.py 天猫超市")
        sys.exit(1)
    
    keyword = sys.argv[1]
    max_results = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    
    # 搜索
    results = search_all(keyword, max_results)
    
    if results:
        print(f"\n📊 共找到 {len(results)} 个商品\n")
        for i, (item, plat_name) in enumerate(results, 1):
            print(format_item(item, i, plat_name))
            print()
    else:
        print("\n❌ 未找到相关商品")
        print("\n💡 建议：")
        print("   • 尝试更换关键词")
        print("   • 或直接发送商品链接查券")

if __name__ == '__main__':
    main()
