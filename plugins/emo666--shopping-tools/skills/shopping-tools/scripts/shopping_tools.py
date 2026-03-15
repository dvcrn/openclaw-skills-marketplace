#!/usr/bin/env python3
"""
购物工具箱 - 确保所有链接都经过获取优惠链接
支持：搜索、榜单查询、商品详情
"""

import sys
import os

# 导入API封装
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from zhetaoke_api import ZheTaoKeAPI

def format_item(item, index, plat_name):
    """格式化商品信息 - 优化版"""
    api = ZheTaoKeAPI()
    
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
    
    # 计算节省金额
    save_amount = 0
    if price and price != '0' and quanhou and quanhou != '0':
        save_amount = float(price) - float(quanhou)
    
    # 使用项目符号格式
    if price and price != '0':
        output.append(f"• 💰 原价：¥{price}")
    if coupon and coupon != '0':
        output.append(f"• 🎫 优惠券：¥{coupon}")
    if quanhou and quanhou != '0':
        output.append(f"• 💰 券后价：¥{quanhou}")
    if save_amount > 0:
        output.append(f"• 💡 可省：¥{save_amount:.2f}")
    if shop:
        output.append(f"• 🏪 店铺：{shop}")
    if sales and sales != '0' and sales != '-1':
        output.append(f"• 📈 销量：{sales}")
    
    # 获取优惠链接
    if tao_id:
        if plat_name == '淘宝':
            url = f"https://item.taobao.com/item.htm?id={tao_id}"
            result = api.taobao_convert(url)
        else:
            url = f"https://item.jd.com/{tao_id}.html"
            result = api.jd_convert(url)
        
        if result and result.get('status') == 200:
            short_url = result.get('shorturl', '')
            tkl = result.get('result_tkl', '')
            
            if short_url or tkl:
                output.append(f"━━━━━━━━━━━━━━━━━━")
                output.append(f"👇 点击链接直达，或者复制淘口令打开淘宝APP自动弹出：")
                output.append(f"")
                if short_url:
                    output.append(f"{short_url}")
                if tkl:
                    output.append(f"")
                    output.append(f"📋 {tkl}")
                output.append(f"━━━━━━━━━━━━━━━━━━")
    
    return "\n".join(output)

def search(keyword, max_results=5):
    """全网搜索"""
    api = ZheTaoKeAPI()
    all_results = []
    
    print(f"🔍 正在搜索「{keyword}」...\n")
    
    # 淘宝搜索
    print("🍑 搜索淘宝...")
    result = api.taobao_search(keyword, page_size=max_results)
    if result and result.get('status') == 200:
        items = result.get('content', [])
        print(f"   ✅ 找到 {len(items)} 个商品")
        for item in items:
            item['plat'] = '1'
            all_results.append((item, '淘宝'))
    
    # 京东搜索
    print("🐶 搜索京东...")
    result = api.jd_search(keyword, page_size=max_results)
    if result and result.get('status') == 200:
        items = result.get('content', [])
        print(f"   ✅ 找到 {len(items)} 个商品")
        for item in items:
            item['plat'] = '2'
            all_results.append((item, '京东'))
    
    return all_results[:max_results]

def quantian(max_results=5):
    """全天销量榜"""
    api = ZheTaoKeAPI()
    
    print("📊 获取淘宝全天销量榜...\n")
    result = api.taobao_quantian(page_size=max_results)
    
    if result and result.get('status') == 200:
        items = result.get('content', [])
        print(f"✅ 找到 {len(items)} 个商品\n")
        return [(item, '淘宝') for item in items]
    
    return []

def shishi(max_results=5):
    """实时人气榜"""
    api = ZheTaoKeAPI()
    
    print("📊 获取淘宝实时人气榜...\n")
    result = api.taobao_shishi(page_size=max_results)
    
    if result and result.get('status') == 200:
        items = result.get('content', [])
        print(f"✅ 找到 {len(items)} 个商品\n")
        return [(item, '淘宝') for item in items]
    
    return []

def yongjin(max_results=5):
    """优惠榜"""
    api = ZheTaoKeAPI()
    
    print("💰 获取淘宝优惠榜...\n")
    result = api.taobao_yongjin(page_size=max_results)
    
    if result and result.get('status') == 200:
        items = result.get('content', [])
        print(f"✅ 找到 {len(items)} 个商品\n")
        return [(item, '淘宝') for item in items]
    
    return []

def detail(item_id):
    """商品详情"""
    api = ZheTaoKeAPI()
    
    print(f"🔍 查询商品 {item_id} 详情...\n")
    result = api.taobao_detail(item_id)
    
    if result and result.get('status') == 200:
        item = result.get('content', [{}])[0]
        item['plat'] = '1'
        return [(item, '淘宝')]
    
    return []

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("购物工具箱 - 所有链接自动获取优惠链接")
        print("=" * 50)
        print("\n使用方法:")
        print("  python3 shopping_tools.py <命令> [参数]")
        print("\n命令:")
        print("  search <关键词> [数量]  - 全网搜索")
        print("  quantian [数量]         - 全天销量榜")
        print("  shishi [数量]           - 实时人气榜")
        print("  yongjin [数量]          - 优惠榜")
        print("  detail <商品ID>         - 商品详情")
        print("\n示例:")
        print("  python3 shopping_tools.py search 牛奶")
        print("  python3 shopping_tools.py search 牛奶 10")
        print("  python3 shopping_tools.py quantian 5")
        print("  python3 shopping_tools.py detail 554832820990")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == 'search':
        keyword = sys.argv[2] if len(sys.argv) > 2 else '牛奶'
        max_results = int(sys.argv[3]) if len(sys.argv) > 3 else 5
        results = search(keyword, max_results)
    
    elif cmd == 'quantian':
        max_results = int(sys.argv[2]) if len(sys.argv) > 2 else 5
        results = quantian(max_results)
    
    elif cmd == 'shishi':
        max_results = int(sys.argv[2]) if len(sys.argv) > 2 else 5
        results = shishi(max_results)
    
    elif cmd == 'yongjin':
        max_results = int(sys.argv[2]) if len(sys.argv) > 2 else 5
        results = yongjin(max_results)
    
    elif cmd == 'detail':
        item_id = sys.argv[2] if len(sys.argv) > 2 else '554832820990'
        results = detail(item_id)
    
    else:
        print(f"❌ 未知命令: {cmd}")
        sys.exit(1)
    
    # 输出结果
    if results:
        print(f"📊 共找到 {len(results)} 个商品\n")
        for i, (item, plat_name) in enumerate(results, 1):
            print(format_item(item, i, plat_name))
            print()
    else:
        print("\n❌ 未找到相关商品")

if __name__ == '__main__':
    main()
