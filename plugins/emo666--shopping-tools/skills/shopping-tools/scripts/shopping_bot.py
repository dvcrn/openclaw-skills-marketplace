#!/usr/bin/env python3
"""
购物机器人 - 交互式查券
流程：搜索商品 → 显示列表 → 用户选编号 → 返回链接
"""

import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from zhetaoke_api import ZheTaoKeAPI

class ShoppingBot:
    """购物机器人"""
    
    def __init__(self):
        self.api = ZheTaoKeAPI()
        self.current_results = []  # 存储当前搜索结果
    
    def search(self, keyword, max_results=5):
        """搜索商品"""
        self.current_results = []
        
        print(f"🔍 正在搜索「{keyword}」...\n")
        
        # 淘宝搜索
        result = self.api.taobao_search(keyword, page_size=max_results)
        if result and result.get('status') == 200:
            for item in result.get('content', []):
                item['plat'] = '1'
                self.current_results.append((item, '淘宝'))
        
        # 京东搜索
        result = self.api.jd_search(keyword, page_size=max_results)
        if result and result.get('status') == 200:
            for item in result.get('content', []):
                item['plat'] = '2'
                self.current_results.append((item, '京东'))
        
        return self.current_results[:max_results]
    
    def show_list(self, results):
        """显示商品列表（不带链接）"""
        if not results:
            print("❌ 未找到相关商品")
            return
        
        print(f"✅ 找到 {len(results)} 个商品\n")
        print("=" * 50)
        
        for i, (item, plat_name) in enumerate(results, 1):
            title = item.get('title', '')
            price = item.get('size', '')
            quanhou = item.get('quanhou_jiage', '')
            coupon = item.get('coupon_info_money', '')
            shop = item.get('nick', '')
            sales = item.get('volume', '')
            
            print(f"\n【{i}】{title[:40]}")
            print(f"    平台：{plat_name}")
            if shop:
                print(f"    店铺：{shop}")
            if sales and sales != '0':
                print(f"    销量：{sales}")
            if price:
                print(f"    原价：¥{price}")
            if coupon and coupon != '0':
                print(f"    优惠券：¥{coupon}")
            if quanhou:
                print(f"    券后价：¥{quanhou}")
        
        print(f"\n" + "=" * 50)
        print(f"\n💡 请回复商品编号（如：1）获取购买链接")
        print(f"💡 回复 'q' 退出")
    
    def get_link(self, index):
        """获取指定商品的链接（已获取优惠链接）"""
        if not self.current_results:
            print("❌ 请先搜索商品")
            return
        
        try:
            idx = int(index) - 1
            if idx < 0 or idx >= len(self.current_results):
                print(f"❌ 编号 {index} 不存在，请输入 1-{len(self.current_results)}")
                return
        except:
            print("❌ 请输入正确的编号")
            return
        
        item, plat_name = self.current_results[idx]
        tao_id = item.get('tao_id', '')
        
        if not tao_id:
            print("❌ 商品ID缺失")
            return
        
        print(f"\n🔍 正在获取商品【{index}】的购买链接...\n")
        
        # 获取优惠链接
        if plat_name == '淘宝':
            url = f"https://item.taobao.com/item.htm?id={tao_id}"
            result = self.api.taobao_convert(url)
        else:
            url = f"https://item.jd.com/{tao_id}.html"
            result = self.api.jd_convert(url)
        
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
            
            print(f"\n💡 回复其他编号继续查看，或回复 'q' 退出")
        else:
            print("❌ 获取链接失败，请稍后再试")


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("购物机器人")
        print("=" * 50)
        print("\n使用方法:")
        print("  1. 搜索商品：python3 shopping_bot.py search <关键词>")
        print("  2. 获取链接：python3 shopping_bot.py get <编号>")
        print("\n示例:")
        print("  python3 shopping_bot.py search 牛奶")
        print("  python3 shopping_bot.py get 1")
        sys.exit(1)
    
    bot = ShoppingBot()
    cmd = sys.argv[1]
    
    if cmd == 'search':
        keyword = sys.argv[2] if len(sys.argv) > 2 else '牛奶'
        results = bot.search(keyword, max_results=5)
        bot.show_list(results)
        
        # 保存结果到临时文件，供下次使用
        import pickle
        with open('/tmp/shopping_bot_results.pkl', 'wb') as f:
            pickle.dump(results, f)
    
    elif cmd == 'get':
        # 读取上次搜索结果
        import pickle
        try:
            with open('/tmp/shopping_bot_results.pkl', 'rb') as f:
                bot.current_results = pickle.load(f)
        except:
            print("❌ 请先搜索商品")
            sys.exit(1)
        
        index = sys.argv[2] if len(sys.argv) > 2 else '1'
        bot.get_link(index)
    
    else:
        print(f"❌ 未知命令: {cmd}")


if __name__ == '__main__':
    main()
