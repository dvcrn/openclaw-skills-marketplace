#!/usr/bin/env python3
"""
全网商品搜索工具
支持淘宝、京东双平台商品搜索
"""

import sys
import os
import json
import urllib.parse
import urllib.request

# 淘宝客配置（已预配置，用户安装后可直接使用）
CONFIG = {
    'appkey': '07d16b40e9c7485d8573f936173aa6d9',
    'sid': '41886',
    'pid': 'mm_200970015_125850084_116244500128',
    'union_id': '1001703383',
}

def get_xianbao_groups():
    """获取线报群列表"""
    try:
        api_url = "https://api.zhetaoke.com:10001/api/api_xianbao_qun.ashx"
        params = {
            "appkey": CONFIG['appkey'],
            "page": 1,
            "page_size": 200,
        }
        
        query = urllib.parse.urlencode(params)
        full_url = f"{api_url}?{query}"
        
        req = urllib.request.Request(full_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            raw_data = response.read()
            if raw_data.startswith(b'\xef\xbb\xbf'):
                raw_data = raw_data[3:]
            data = json.loads(raw_data.decode('utf-8'))
            
            if data.get('status') == 200 and data.get('content'):
                return data['content']
    except:
        pass
    return []

def search_xianbao_groups(keyword, max_results=5):
    """从线报群搜索商品"""
    results = []
    
    # 获取群列表
    groups = get_xianbao_groups()
    if not groups:
        return results
    
    # 取前10个群搜索
    group_ids = [g.get('qunhao', '') for g in groups[:10] if g.get('qunhao')]
    
    if not group_ids:
        return results
    
    try:
        api_url = "https://api.zhetaoke.com:10001/api/api_xianbao.ashx"
        params = {
            "appkey": CONFIG['appkey'],
            "id": ','.join(group_ids),
            "type": "0",
            "page": 1,
            "page_size": 50,
            "msg": "1",
            "interval": 1440,
            "q": keyword,
        }
        
        query = urllib.parse.urlencode(params)
        full_url = f"{api_url}?{query}"
        
        req = urllib.request.Request(full_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=20) as response:
            raw_data = response.read()
            if raw_data.startswith(b'\xef\xbb\xbf'):
                raw_data = raw_data[3:]
            data = json.loads(raw_data.decode('utf-8'))
            
            if data.get('status') == 200:
                for item in data.get('data', []):
                    results.append({
                        'title': item.get('title', ''),
                        'content': item.get('content', ''),
                        'url': item.get('url', ''),
                        'price': item.get('price', ''),
                        'coupon': item.get('coupon', ''),
                        'plat': item.get('plat', '1'),
                        'time': item.get('time', ''),
                        'pic': item.get('pic', ''),
                    })
                    
                    if len(results) >= max_results:
                        break
    except Exception as e:
        print(f"搜索线报群失败: {e}")
    
    return results

def search_taobao_quanwang(keyword, max_results=5):
    """淘宝全网搜索"""
    results = []
    
    try:
        api_url = "https://api.zhetaoke.com:10003/api/api_quanwang.ashx"
        params = {
            "appkey": CONFIG['appkey'],
            "sid": CONFIG['sid'],
            "pid": CONFIG['pid'],
            "page": 1,
            "page_size": max_results,
            "sort": "new",
            "q": keyword,
            "youquan": "1",
        }
        
        query = urllib.parse.urlencode(params)
        full_url = f"{api_url}?{query}"
        
        req = urllib.request.Request(full_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=20) as response:
            raw_data = response.read()
            if raw_data.startswith(b'\xef\xbb\xbf'):
                raw_data = raw_data[3:]
            data = json.loads(raw_data.decode('utf-8'))
            
            if data.get('status') == 200:
                for item in data.get('content', []):
                    results.append({
                        'title': item.get('title', ''),
                        'tao_id': item.get('tao_id', ''),
                        'price': item.get('size', ''),
                        'quanhou_jiage': item.get('quanhou_jiage', ''),
                        'coupon': item.get('coupon_info_money', ''),
                        'plat': '1',
                        'pic': item.get('pict_url', ''),
                        'shop': item.get('nick', ''),
                        'sales': item.get('volume', ''),
                    })
    except Exception as e:
        print(f"淘宝搜索失败: {e}")
    
    return results

def search_jd_quanwang(keyword, max_results=5):
    """京东全网搜索"""
    results = []
    
    try:
        api_url = "http://api.zhetaoke.com:20000/api/api_quanwang.ashx"
        params = {
            "appkey": CONFIG['appkey'],
            "sid": CONFIG['sid'],
            "pid": CONFIG['pid'],
            "unionId": CONFIG['union_id'],
            "page": 1,
            "page_size": max_results,
            "sort": "new",
            "q": keyword,
        }
        
        query = urllib.parse.urlencode(params)
        full_url = f"{api_url}?{query}"
        
        req = urllib.request.Request(full_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=20) as response:
            raw_data = response.read()
            if raw_data.startswith(b'\xef\xbb\xbf'):
                raw_data = raw_data[3:]
            data = json.loads(raw_data.decode('utf-8'))
            
            if data.get('status') == 200:
                for item in data.get('content', []):
                    results.append({
                        'title': item.get('title', ''),
                        'tao_id': item.get('tao_id', ''),
                        'price': item.get('size', ''),
                        'quanhou_jiage': item.get('quanhou_jiage', ''),
                        'coupon': item.get('coupon_info_money', ''),
                        'plat': '2',
                        'pic': item.get('pict_url', ''),
                        'shop': item.get('nick', ''),
                        'sales': item.get('volume', ''),
                    })
    except Exception as e:
        print(f"京东搜索失败: {e}")
    
    return results

def convert_link(url, platform):
    """获取优惠链接"""
    try:
        if platform == '1':
            api_url = "https://api.zhetaoke.com:10001/api/open_gaoyongzhuanlian_tkl_piliang.ashx"
            params = {
                "appkey": CONFIG['appkey'],
                "sid": CONFIG['sid'],
                "pid": CONFIG['pid'],
                "tkl": url,
            }
        else:
            api_url = "http://api.zhetaoke.com:20000/api/open_gaoyongzhuanlian_tkl_piliang.ashx"
            params = {
                "appkey": CONFIG['appkey'],
                "tkl": url,
                "unionId": CONFIG['union_id'],
            }
        
        query = urllib.parse.urlencode(params)
        full_url = f"{api_url}?{query}"
        
        req = urllib.request.Request(full_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            raw_data = response.read()
            if raw_data.startswith(b'\xef\xbb\xbf'):
                raw_data = raw_data[3:]
            return json.loads(raw_data.decode('utf-8'))
    except:
        return None

def format_result(item, index, is_xianbao=False):
    """格式化结果 - 优化版"""
    output = []
    
    if is_xianbao:
        # 线报群结果
        title = item.get('title', '')
        content = item.get('content', '')
        url = item.get('url', '')
        plat = item.get('plat', '1')
        price = item.get('price', '')
        coupon = item.get('coupon', '')
        
        plat_names = {'1': '淘宝', '2': '京东', '3': '拼多多'}
        plat_name = plat_names.get(plat, '未知')
        
        output.append(f"🥇 线报 {index} [{plat_name}]")
        output.append(f"📦 {title}")
        
        if price:
            output.append(f"• 💰 价格：¥{price}")
        if coupon:
            output.append(f"• 🎫 优惠券：¥{coupon}")
        
        # 尝试获取优惠链接
        if url:
            result = convert_link(url, plat)
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
            else:
                # 获取优惠链接失败，显示原文
                output.append(f"")
                output.append(f"📝 {content[:150]}...")
    else:
        # 全网搜索结果
        title = item.get('title', '')
        price = item.get('price', '')
        quanhou = item.get('quanhou_jiage', '')
        coupon = item.get('coupon', '')
        plat = item.get('plat', '1')
        shop = item.get('shop', '')
        sales = item.get('sales', '')
        tao_id = item.get('tao_id', '')
        
        plat_name = '淘宝' if plat == '1' else '京东'
        
        # 计算节省金额
        save_amount = 0
        if price and price != '0' and quanhou and quanhou != '0':
            try:
                save_amount = float(price) - float(quanhou)
            except:
                pass
        
        output.append(f"🥇 商品 {index} [{plat_name}]")
        output.append(f"📦 {title}")
        
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
            if plat == '1':
                url = f"https://item.taobao.com/item.htm?id={tao_id}"
            else:
                url = f"https://item.jd.com/{tao_id}.html"
            
            result = convert_link(url, plat)
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

def main():
    if len(sys.argv) < 2:
        print("全网商品搜索工具")
        print("=" * 50)
        print("\n使用方法：")
        print("  python3 search_deals.py <关键词> [数量]")
        print("\n示例：")
        print("  python3 search_deals.py 牛奶")
        print("  python3 search_deals.py 牛奶 10")
        print("  python3 search_deals.py 天猫超市")
        sys.exit(1)
    
    keyword = sys.argv[1]
    max_results = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    
    if not CONFIG['appkey']:
        print("❌ 未配置 API Key")
        sys.exit(1)
    
    print(f"🔍 正在搜索「{keyword}」...")
    print()
    
    # 从全网搜索（线报群功能已下线）
    print("🌐 搜索全网商品...")
    taobao_results = search_taobao_quanwang(keyword, max_results=max_results)
    jd_results = search_jd_quanwang(keyword, max_results=max_results)
    
    all_results = taobao_results + jd_results
    
    if all_results:
        print(f"✅ 找到 {len(all_results)} 个商品\n")
        for i, item in enumerate(all_results[:max_results], 1):
            print(format_result(item, i, is_xianbao=False))
            print()
    else:
        print("❌ 未找到相关商品\n")
        print("💡 建议：")
        print("   • 尝试更换关键词搜索")
        print("   • 或直接发送商品链接查券")

if __name__ == '__main__':
    main()
