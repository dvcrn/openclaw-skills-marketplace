#!/usr/bin/env python3
"""
购物助手 - 用户端
提供查券、比价、价保等功能
后台自动获取优惠链接（用户不可见）
"""

import sys
import os
import json
import urllib.parse
import urllib.request
import re

# 淘宝客配置（已预配置，用户安装后可直接使用）
CONFIG = {
    'appkey': '07d16b40e9c7485d8573f936173aa6d9',
    'sid': '41886',
    'pid': 'mm_200970015_125850084_116244500128',
    'union_id': '1001703383',
}

def detect_platform(content):
    """识别电商平台"""
    if 'taobao.com' in content or 'tmall.com' in content or '￥' in content or '《' in content:
        return 'taobao'
    elif 'jd.com' in content or 'jingdong.com' in content or '3.cn' in content:
        return 'jd'
    elif 'pinduoduo.com' in content or 'yangkeduo.com' in content:
        return 'pdd'
    elif '(' in content and ')' in content and '/' in content:
        # 淘口令格式: (xxxxx)/ CZxxxx
        return 'taobao'
    return 'unknown'

def expand_short_url(url):
    """展开短链接"""
    try:
        # 清理URL中的空格
        url = url.strip().replace(' ', '')
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'}, method='HEAD')
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.geturl()
    except:
        return url

def convert_link_backend(content, platform):
    """后台获取优惠链接（用户不可见）"""
    try:
        # 对于京东，保留完整文案（包括【京东】标识）
        if platform == 'jd':
            # 只去掉明显的多余空格，保留文案格式
            content = content.strip()
        else:
            # 淘宝清理空格
            content = content.strip().replace(' ', '')
            # 如果是短链接，先展开
            if '3.cn' in content or 't.cn' in content:
                content = expand_short_url(content)
        
        if platform == 'taobao':
            api_url = "https://api.zhetaoke.com:10001/api/open_gaoyongzhuanlian_tkl_piliang.ashx"
            params = {
                "appkey": CONFIG['appkey'],
                "sid": CONFIG['sid'],
                "pid": CONFIG['pid'],
                "tkl": content
            }
        else:
            api_url = "http://api.zhetaoke.com:20000/api/open_gaoyongzhuanlian_tkl_piliang.ashx"
            params = {
                "appkey": CONFIG['appkey'],
                "tkl": content,
                "unionId": CONFIG['union_id']
            }
        
        query = urllib.parse.urlencode(params)
        full_url = f"{api_url}?{query}"
        req = urllib.request.Request(full_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=20) as response:
            return json.loads(response.read().decode('utf-8'))
    except:
        return None

def search_coupons(keyword):
    """搜索优惠券"""
    # TODO: 实现优惠券搜索
    return []

def compare_prices(keyword):
    """全网比价"""
    # TODO: 实现比价功能
    return {}

def get_price_history(url):
    """获取历史价格"""
    # TODO: 实现历史价格查询
    return {}

def format_coupon_result(result, platform):
    """格式化查券结果 - 优化版"""
    if not result or result.get("status") != 200:
        return "❌ 查券失败，请检查链接是否正确"
    
    plat_names = {'1': '淘宝', '2': '京东', '3': '拼多多'}
    plat = result.get('plat', 'unknown')
    plat_name = plat_names.get(str(plat), platform.upper())
    
    output = []
    
    # 商品标题
    title = result.get('title', '') or result.get('tao_title', '')
    if title:
        output.append(f"📦 {title}")
    else:
        output.append(f"📦 {plat_name}商品")
    
    # 获取优惠购买链接（支持淘宝和京东不同字段）
    short_url = result.get('shorturl', '') or result.get('shortUrl', '') or result.get('result_url', '')
    tkl = result.get('result_tkl', '') or result.get('tkl', '')
    
    # 价格信息
    price = result.get('size', '0')
    quanhou = result.get('quanhou_jiage', '0')
    coupon = result.get('coupon_info_money', '0')
    
    # 计算节省金额
    save_amount = 0
    if price and price != '0' and quanhou and quanhou != '0':
        save_amount = float(price) - float(quanhou)
    
    # 价格信息（使用项目符号）
    if price and price != '0':
        output.append(f"• 💰 原价：¥{price}")
    if coupon and coupon != '0':
        output.append(f"• 🎫 优惠券：¥{coupon}")
    if quanhou and quanhou != '0':
        output.append(f"• 💰 券后价：¥{quanhou}")
    if save_amount > 0:
        output.append(f"• 💡 可省：¥{save_amount:.2f}")
    
    # 店铺信息
    shop = result.get('nick', '')
    if shop and shop != '0':
        output.append(f"• 🏪 店铺：{shop}")
    
    # 销量信息
    volume = result.get('volume', '')
    if volume and volume != '-1' and volume != '0':
        output.append(f"• 📈 销量：{volume}")
    
    # 显示优惠购买链接和淘口令
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
    
    # 底部总结
    if quanhou and quanhou != '0':
        output.append(f"✅ 查券完成！券后价 ¥{quanhou}")
    else:
        output.append(f"✅ 查券完成！")
    
    return "\n".join(output)

def format_compare_result(results):
    """格式化比价结果"""
    output = []
    output.append(f"📊 全网比价结果")
    output.append(f"━━━━━━━━━━━━━━━━━━")
    
    # TODO: 实现比价结果格式化
    
    return "\n".join(output)

def main():
    if len(sys.argv) < 2:
        print("购物助手")
        print("=" * 50)
        print("\n使用方法：")
        print("  1. 查券：发送商品链接或淘口令")
        print("\n支持平台：淘宝、京东、拼多多")
        print("\n注意：京东短链接(3.cn)请换成长链接或淘口令")
        sys.exit(1)
    
    content = sys.argv[1]
    
    # 检查配置
    if not CONFIG['appkey']:
        print("❌ 服务暂时不可用，请稍后再试")
        sys.exit(1)
    
    # 识别平台
    platform = detect_platform(content)
    
    if platform == 'unknown':
        print(f"🔍 无法识别链接格式")
        print("\n💡 请发送：")
        print("   • 淘宝/天猫商品链接或淘口令")
        print("   • 京东商品详情页链接（如 https://item.jd.com/xxx.html）")
        print("   • 拼多多商品链接")
        sys.exit(1)
    
    # 检测京东短链接
    if '3.cn' in content:
        print("❌ 京东短链接无法直接查券")
        print("\n💡 解决方法：")
        print("   1. 打开京东APP，进入商品详情页")
        print("   2. 点击右上角「分享」→「复制链接」")
        print("   3. 发送长链接（格式：https://item.jd.com/xxx.html）")
        print("\n或者发送淘宝/拼多多的同款商品链接")
        sys.exit(1)
    
    # 查券
    print(f"🔍 正在查找优惠券...")
    print()
    
    # 后台获取优惠链接（用户不可见）
    result = convert_link_backend(content, platform)
    
    if result and result.get('status') == 200:
        # 显示查券结果（隐藏获取优惠链接信息）
        print(format_coupon_result(result, platform))
        
        # 后台记录获取优惠链接成功（可选）
        # 这里可以记录到数据库或日志
    else:
        error_msg = result.get('content', '') if result else ''
        
        if platform == 'jd':
            print("❌ 京东商品查券失败")
            print("\n可能原因：")
            print("   1. 该商品不在京东联盟推广范围内")
            print("   2. 商品无优惠券或已下架")
            print("   3. 京东联盟账号权限不足")
            print("\n💡 建议：")
            print("   • 尝试发送淘宝/拼多多的同款商品链接")
            print("   • 或联系京东联盟客服确认推广权限")
        else:
            print("❌ 查券失败，可能原因：")
            print("   1. 链接格式不正确")
            print("   2. 商品已下架或无优惠券")
            print("   3. 网络连接问题")

if __name__ == '__main__':
    main()
