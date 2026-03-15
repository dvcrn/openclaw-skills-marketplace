#!/usr/bin/env python3
"""
百度千帆 Coding Plan 用量查询工具
使用 agent-browser 自动登录并查询用量详情
"""

import os
import sys
import subprocess
import json
import re
from datetime import datetime

# 颜色定义
CYAN = '\033[0;36m'
BLUE = '\033[0;34m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
RED = '\033[0;31m'
NC = '\033[0m'

# 登录状态文件
AUTH_FILE = os.path.expanduser("~/.baidu-qianfan-auth.json")

def run_browser(args):
    """运行 agent-browser 命令"""
    result = subprocess.run(
        ['agent-browser'] + args,
        capture_output=True,
        text=True
    )
    return result.stdout.strip(), result.stderr.strip(), result.returncode

def open_page(url):
    """打开页面"""
    stdout, stderr, code = run_browser(['open', url])
    return code == 0

def get_url():
    """获取当前 URL"""
    stdout, stderr, code = run_browser(['get', 'url'])
    return stdout if code == 0 else None

def get_snapshot():
    """获取页面快照"""
    stdout, stderr, code = run_browser(['snapshot', '-i'])
    return stdout if code == 0 else None

def eval_js(js_code):
    """执行 JavaScript"""
    stdout, stderr, code = run_browser(['eval', js_code])
    return stdout if code == 0 else None

def click_element(ref):
    """点击元素"""
    stdout, stderr, code = run_browser(['click', ref])
    return code == 0

def fill_input(ref, text):
    """填充输入框"""
    stdout, stderr, code = run_browser(['fill', ref, text])
    return code == 0

def close_browser():
    """关闭浏览器"""
    run_browser(['close'])

def check_element(ref):
    """勾选复选框"""
    stdout, stderr, code = run_browser(['check', ref])
    return code == 0

def load_auth():
    """加载保存的登录状态"""
    if os.path.exists(AUTH_FILE):
        stdout, stderr, code = run_browser(['state', 'load', AUTH_FILE])
        return code == 0
    return False

def save_auth():
    """保存登录状态"""
    stdout, stderr, code = run_browser(['state', 'save', AUTH_FILE])
    return code == 0

def parse_snapshot(snapshot):
    """解析快照，提取元素引用"""
    elements = {}
    for line in snapshot.split('\n'):
        # 匹配类似: textbox "手机号" [ref=e3]
        match = re.search(r'(\w+(?:\s+\w+)*)\s+"([^"]+)"\s+\[ref=(e\d+)\]', line)
        if match:
            elem_type, text, ref = match.groups()
            elements[text] = ref
            elements[f"{elem_type}:{text}"] = ref
        # 匹配按钮: button "登录/注册" [ref=e9]
        match = re.search(r'button\s+"([^"]+)"\s+\[ref=(e\d+)\]', line)
        if match:
            text, ref = match.groups()
            elements[text] = ref
    return elements

def check_login():
    """检查是否已登录"""
    # 尝试访问 API
    open_page("https://console.bce.baidu.com/api/qianfan/charge/codingPlan/quota")
    import time
    time.sleep(1)
    
    content = eval_js("document.body.innerText")
    if content and '"success":true' in content:
        return True
    
    # 检查 URL
    url = get_url()
    if url and 'login' in url:
        return False
    
    return False

def login(phone):
    """登录百度账号"""
    import time
    
    # 先尝试加载保存的登录状态
    print(f"{BLUE}正在加载登录状态...{NC}")
    if load_auth():
        print(f"{GREEN}✓ 已加载保存的登录状态{NC}")
        
        # 检查登录状态是否有效
        open_page("https://console.bce.baidu.com/qianfan/resource/subscribe")
        time.sleep(3)
        
        url = get_url()
        if url and 'qianfan/resource/subscribe' in url and 'login' not in url:
            print(f"{GREEN}✓ 登录状态有效{NC}")
            return True
        
        # 可能需要二次验证
        snapshot = get_snapshot()
        if '短信验证' in snapshot or '验证码' in snapshot:
            print(f"{YELLOW}需要进行二次验证{NC}")
            elements = parse_snapshot(snapshot)
            
            # 发送验证码
            if '发送验证码' in elements:
                click_element(elements['发送验证码'])
                print(f"{YELLOW}验证码已发送，请输入验证码：{NC}")
                code = input("验证码: ").strip()
                
                # 重新获取快照
                snapshot = get_snapshot()
                elements = parse_snapshot(snapshot)
                
                # 填写验证码
                if '验证码' in elements:
                    fill_input(elements['验证码'], code)
                
                # 勾选信任
                if '信任这台机器' in elements:
                    check_element(elements['信任这台机器'])
                
                # 点击确定
                if '确定' in elements:
                    click_element(elements['确定'])
                
                time.sleep(3)
                url = get_url()
                if url and 'qianfan' in url:
                    save_auth()
                    return True
        
        print(f"{YELLOW}登录状态已过期，需要重新登录{NC}")
    
    # 打开订阅页面（会重定向到登录页）
    open_page("https://console.bce.baidu.com/qianfan/resource/subscribe")
    time.sleep(2)
    
    # 获取登录页面元素
    snapshot = get_snapshot()
    elements = parse_snapshot(snapshot)
    
    # 填写手机号
    if '手机号' in elements:
        fill_input(elements['手机号'], phone)
    else:
        print(f"{RED}未找到手机号输入框{NC}")
        return False
    
    # 发送验证码
    if '发送验证码' in elements:
        click_element(elements['发送验证码'])
        print(f"{YELLOW}验证码已发送到 {phone}，请输入验证码：{NC}")
        code = input("验证码: ").strip()
    else:
        print(f"{RED}未找到发送验证码按钮{NC}")
        return False
    
    # 重新获取快照
    snapshot = get_snapshot()
    elements = parse_snapshot(snapshot)
    
    # 填写验证码
    if '短信验证码' in elements:
        fill_input(elements['短信验证码'], code)
    else:
        print(f"{RED}未找到验证码输入框{NC}")
        return False
    
    # 勾选协议
    if '我已阅读并同意' in elements:
        check_element(elements['我已阅读并同意'])
    
    # 重新获取快照
    snapshot = get_snapshot()
    elements = parse_snapshot(snapshot)
    
    # 点击登录
    if '登录/注册' in elements:
        click_element(elements['登录/注册'])
    else:
        print(f"{RED}未找到登录按钮{NC}")
        return False
    
    # 等待登录完成
    time.sleep(5)
    
    # 检查是否需要二次验证
    url = get_url()
    if 'verify/login' in url:
        print(f"{YELLOW}需要进行二次验证{NC}")
        snapshot = get_snapshot()
        elements = parse_snapshot(snapshot)
        
        # 发送验证码
        if '发送验证码' in elements:
            click_element(elements['发送验证码'])
            print(f"{YELLOW}验证码已发送，请输入验证码：{NC}")
            code = input("验证码: ").strip()
            
            # 重新获取快照
            snapshot = get_snapshot()
            elements = parse_snapshot(snapshot)
            
            # 填写验证码
            if '验证码' in elements:
                fill_input(elements['验证码'], code)
            
            # 勾选信任
            if '信任这台机器' in elements:
                check_element(elements['信任这台机器'])
            
            # 点击确定
            if '确定' in elements:
                click_element(elements['确定'])
            
            time.sleep(3)
    
    # 保存登录状态
    save_auth()
    
    # 检查是否登录成功
    url = get_url()
    return 'qianfan' in url

def query_quota():
    """查询 Coding Plan 用量"""
    # 直接访问 API 端点
    open_page("https://console.bce.baidu.com/api/qianfan/charge/codingPlan/quota")
    
    import time
    time.sleep(1)
    
    # 获取响应内容
    content = eval_js("document.body.innerText")
    
    if not content:
        print(f"{RED}无法获取用量数据{NC}")
        return None
    
    try:
        data = json.loads(content)
        if data.get('success'):
            return data['result']['quota']
        else:
            print(f"{RED}API 返回错误: {data}{NC}")
            return None
    except json.JSONDecodeError:
        print(f"{RED}解析响应失败{NC}")
        return None

def format_reset_time(reset_at):
    """格式化重置时间"""
    try:
        dt = datetime.fromisoformat(reset_at.replace('+08:00', '+08:00'))
        return dt.strftime('%m-%d %H:%M')
    except:
        return reset_at

def display_quota(quota):
    """显示用量信息"""
    print(f"\n{CYAN}═══════════════════════════════════════════════════════════{NC}")
    print(f"{CYAN}              百度千帆 · Coding Plan 用量详情{NC}")
    print(f"{CYAN}═══════════════════════════════════════════════════════════{NC}\n")
    
    print(f"{'周期':<8} {'已用':>8} {'限额':>8} {'剩余':>8} {'使用率':>8} {'重置时间':<12}")
    print(f"{'─'*60}")
    
    periods = [
        ('5小时', 'fiveHour'),
        ('周', 'week'),
        ('月', 'month')
    ]
    
    for name, key in periods:
        if key in quota:
            data = quota[key]
            used = data['used']
            limit = data['limit']
            remaining = limit - used
            percent = (used / limit * 100) if limit > 0 else 0
            reset = format_reset_time(data['resetAt'])
            
            # 根据使用率选择颜色
            if percent < 50:
                color = GREEN
            elif percent < 80:
                color = YELLOW
            else:
                color = RED
            
            print(f"{name:<8} {used:>8} {limit:>8} {remaining:>8} {color}{percent:>7.1f}%{NC} {reset:<12}")
    
    print(f"\n{CYAN}═══════════════════════════════════════════════════════════{NC}")
    
    # 使用建议
    five_hour = quota.get('fiveHour', {})
    five_hour_percent = (five_hour.get('used', 0) / five_hour.get('limit', 1)) * 100
    
    print(f"\n{BLUE}💡 使用建议：{NC}")
    if five_hour_percent > 80:
        print(f"   • 5小时用量较高 ({five_hour_percent:.1f}%)，建议稍后再用")
    else:
        print(f"   • 用量正常，可以继续使用")
    
    month = quota.get('month', {})
    month_percent = (month.get('used', 0) / month.get('limit', 1)) * 100
    print(f"   • 月度额度剩余 {(100-month_percent):.1f}%，非常宽裕")

def main():
    # 解析参数
    if '--web' in sys.argv or '--console' in sys.argv:
        import webbrowser
        print("正在打开百度千帆控制台...")
        webbrowser.open("https://console.bce.baidu.com/qianfan/resource/subscribe")
        return
    
    # 获取手机号
    phone = os.environ.get('QIANFAN_PHONE', '')
    
    if not phone:
        print(f"{YELLOW}未配置 QIANFAN_PHONE，请输入手机号：{NC}")
        phone = input("手机号: ").strip()
        if not phone:
            print(f"{RED}需要手机号才能登录{NC}")
            sys.exit(1)
    
    print(f"{BLUE}正在登录百度账号...{NC}")
    
    try:
        # 登录
        if login(phone):
            print(f"{GREEN}✓ 登录成功{NC}\n")
            
            # 查询用量
            print(f"{BLUE}正在查询用量...{NC}")
            quota = query_quota()
            
            if quota:
                display_quota(quota)
            else:
                print(f"{RED}查询失败{NC}")
        else:
            print(f"{RED}登录失败{NC}")
            sys.exit(1)
    
    finally:
        close_browser()

if __name__ == '__main__':
    main()
