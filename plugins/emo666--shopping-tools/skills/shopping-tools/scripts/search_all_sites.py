#!/usr/bin/env python3
"""
全站商品搜索工具
同时搜索淘宝和京东的领券商品
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from zhetaoke_api import ZheTaoKeAPI

def format_item(item, index, plat_name):
    """格式化商品信息"""
    api = ZheTaoKeAPI()
    
    output = []
    
    title = item.get('title', '')
    price = item.get('size', '')
    quanhou = item.get('quanhou_jiage', '')
    coupon = item.get('coupon_info_money', '')
    shop = item.get('nick', '')
    sales = item.get('volume', '')
    tao_id = item.get('tao_id', '')
    
    output.append(f"【{index}】{title[:40]}")
    output.append(f"    平台：{plat_name}")
    
    if shop:
        output.append(f"    店铺：{shop}")
    
    if sales and sales != '0':
        output.append(f"    销量：{sales}")
    
    if price:
        output.append(f"    原价：¥{price}")
    if coupon and coupon != '0':
        output.append(f"    优惠券：¥{coupon}")
    if quanhou:
        output.append(f"    券后价：¥{quanhou}")
    
    return "\n".join(output)

def search_taobao_all(max_results=5):
    """搜索淘宝全站领券商品"""
    api = ZheTaoKeAPI()
    
    print("🍑 搜索淘宝全站...")
    result = api.taobao_all(page_size=max_results, sort='new')
    
    if result and result.get('status') == 200:
        items = result.get('content', [])
        print(f"   ✅ 找到 {len(items)} 个商品")
        return [(item, '淘宝') for item in items]
    else:
        print(f"   ❌ 搜索失败")
        return []

def search_jd_all(max_results=5):
    """搜索京东全站领券商品"""
    api = ZheTaoKeAPI()
    
    print("🐶 搜索京东全站...")
    result = api.jd_all(page_size=max_results, sort='new')
    
    if result and result.get('status') == 200:
        items = result.get('content', [])
        print(f"   ✅ 找到 {len(items)} 个商品")
        return [(item, '京东') for item in items]
    else:
        print(f"   ❌ 搜索失败")
        return []

def get_item_link(index, results):
    """获取指定商品的链接"""
    api = ZheTaoKeAPI()
    
    if not results:
        print("❌ 请先搜索商品")
        return
    
    try:
        idx = int(index) - 1
        if idx < 0 or idx >= len(results):
            print(f"❌ 编号 {index} 不存在")
            return
    except:
        print("❌ 请输入正确的编号")
        return
    
    item, plat_name = results[idx]
    tao_id = item.get('tao_id', '')
    
    if not tao_id:
        print("❌ 商品ID缺失")
        return
    
    print(f"\n🔍 正在获取商品【{index}】的购买链接...\n")
    
    # 获取优惠链接
    if plat_name == '淘宝':
        url = f"https://item.taobao.com/item.htm?id={tao_id}"
        result = api.taobao_convert(url)
    else:
        url = f"https://item.jd.com/{tao_id}.html"
        result = api.jd_convert(url)
    
    if result and result.get('status') == 200:
        short_url = result.get('shorturl', '')
        tkl = result.get('result_tkl', '')
        
        title = item.get('title', '')
        quanhou = item.get('quanhou_jiage', '')
        coupon = item.get('coupon_info_money', '')
        
        print(f"📦 {title}")
        if coupon and coupon != '0':
            print(f"🎫 优惠券：¥{coupon}")
        if quanhou:
            print(f"💰 券后价：¥{quanhou}")
        
        print(f"\n━━━━━━━━━━━━━━━━━━")
        print(f"👇 点击购买（或复制打开淘宝APP自动弹出）：")
        if short_url:
            print(f"{short_url}")
        if tkl:
            print(f"")
            print(f"📋 淘口令：{tkl}")
        print(f"━━━━━━━━━━━━━━━━━━")
    else:
        print("❌ 获取链接失败")

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("全站商品搜索工具")
        print("=" * 50)
        print("\n使用方法:")
        print("  python3 search_all_sites.py search [数量]")
        print("  python3 search_all_sites.py get <编号>")
        print("\n示例:")
        print("  python3 search_all_sites.py search 5")
        print("  python3 search_all_sites.py get 1")
        sys.exit(1)
    
    import pickle
    
    cmd = sys.argv[1]
    
    if cmd == 'search':
        max_results = int(sys.argv[2]) if len(sys.argv) > 2 else 5
        
        print(f"🔍 正在搜索全站领券商品...\n")
        
        # 搜索淘宝
        taobao_results = search_taobao_all(max_results)
        
        # 搜索京东
        jd_results = search_jd_all(max_results)
        
        # 合并结果
        all_results = taobao_results + jd_results
        
        if all_results:
            print(f"\n✅ 共找到 {len(all_results)} 个商品\n")
            print("=" * 50)
            
            for i, (item, plat_name) in enumerate(all_results, 1):
                print(f"\n{format_item(item, i, plat_name)}")
            
            print(f"\n" + "=" * 50)
            print(f"\n💡 请回复商品编号（如：1）获取购买链接")
            
            # 保存结果
            with open('/tmp/search_all_results.pkl', 'wb') as f:
                pickle.dump(all_results, f)
        else:
            print("\n❌ 未找到商品")
    
    elif cmd == 'get':
        # 读取结果
        try:
            with open('/tmp/search_all_results.pkl', 'rb') as f:
                results = pickle.load(f)
        except:
            print("❌ 请先搜索商品")
            sys.exit(1)
        
        index = sys.argv[2] if len(sys.argv) > 2 else '1'
        get_item_link(index, results)
    
    else:
        print(f"❌ 未知命令: {cmd}")

if __name__ == '__main__':
    main()
