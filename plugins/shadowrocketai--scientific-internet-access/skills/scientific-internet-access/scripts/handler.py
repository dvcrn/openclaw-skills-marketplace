#!/usr/bin/env python3
import sys, subprocess, os

def step1_device():
    print("""你用什么设备？

1. Windows 电脑
2. Mac 电脑
3. iPhone / iPad 【推荐】
4. 安卓手机

回复数字，或直接按任意键选推荐。""")

def step2_run(choice):
    skill_dir = os.path.dirname(os.path.abspath(__file__))
    fmt_map = {
        '1': ('clash', 'Clash for Windows'),
        '2': ('clash', 'ClashX'),
        '3': ('base64', 'Shadowrocket'),
        '4': ('v2ray', 'v2rayNG'),
    }
    if choice not in fmt_map:
        choice = '3'
    fmt, client = fmt_map[choice]
    subprocess.run([sys.executable, os.path.join(skill_dir, 'scraper.py')], capture_output=True, cwd=skill_dir)
    subprocess.run([sys.executable, os.path.join(skill_dir, 'tester.py')], capture_output=True, cwd=skill_dir)
    result = subprocess.run([sys.executable, os.path.join(skill_dir, 'formatter.py'), '--format', fmt, '--top', '5'], capture_output=True, text=True, cwd=skill_dir)
    config = result.stdout.strip() if result.stdout.strip() else '暂时没有可用节点，稍后再试。'
    print(f"""找到可用节点：

{config}

📱 客户端：{client}（应用商店搜索下载）
📋 用法：复制上面内容 → 打开客户端 → 导入 → 连接

⚠️ 免费节点来自公开源，别用来登银行、邮箱等重要账号。

搞不定告诉我卡在哪步。""")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        step2_run(sys.argv[1])
    else:
        step1_device()
