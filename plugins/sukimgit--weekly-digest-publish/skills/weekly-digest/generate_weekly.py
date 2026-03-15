#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Weekly Digest - 生成周报并发送
"""

import json
import smtplib
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from urllib.request import Request, urlopen
import sys

# 配置
CONFIG_FILE = Path(__file__).parent / 'config.json'
with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
    config = json.load(f)

def fetch_github_activity(username, token=None):
    """获取 GitHub 活动"""
    try:
        headers = {'User-Agent': 'Python'}
        if token:
            headers['Authorization'] = f'token {token}'
        
        # 获取用户信息
        user_url = f"https://api.github.com/users/{username}"
        user_req = Request(user_url, headers=headers)
        user_resp = urlopen(user_req, timeout=10)
        user_data = json.loads(user_resp.read().decode('utf-8'))
        
        # 获取仓库（带 token 可以获取私有仓库）
        repos_url = f"https://api.github.com/users/{username}/repos?affiliation=owner"
        repos_req = Request(repos_url, headers=headers)
        repos_resp = urlopen(repos_req, timeout=10)
        repos_data = json.loads(repos_resp.read().decode('utf-8'))
        
        # 获取最近提交（需要 token）
        events_url = f"https://api.github.com/users/{username}/events"
        events_req = Request(events_url, headers=headers)
        events_resp = urlopen(events_req, timeout=10)
        events_data = json.loads(events_resp.read().decode('utf-8'))
        
        # 统计提交
        push_count = sum(1 for e in events_data[:30] if e['type'] == 'PushEvent')
        
        return {
            'name': user_data.get('name', username),
            'public_repos': user_data.get('public_repos', 0),
            'followers': user_data.get('followers', 0),
            'repos': repos_data[:5],  # 最近 5 个
            'push_count': push_count,
            'total_repos': len(repos_data)
        }
    except Exception as e:
        return {'error': str(e)}

def generate_report(github_data, week_start, week_end):
    """生成周报内容"""
    report = f"""
# 📊 Weekly Digest - 周报

**生成时间：** {datetime.now().strftime('%Y-%m-%d %H:%M')}
**统计周期：** {week_start} 至 {week_end}

---

## 👤 用户信息

- **GitHub:** {github_data.get('name', 'N/A')}
- **公开仓库：** {github_data.get('public_repos', 0)} 个
- **关注者：** {github_data.get('followers', 0)} 人

---

## 📦 仓库列表

"""
    if 'repos' in github_data and github_data['repos']:
        for repo in github_data['repos']:
            report += f"- **{repo['name']}** - {repo.get('description', '无描述')} ⭐ {repo['stargazers_count']}\n"
    else:
        report += "- 暂无公开仓库\n"
    
    report += f"""
---

## 📝 本周总结

> 本周工作专注，持续学习和实践 AI 应用技术。

### 完成的工作
- 发布 Memory Manager 技能（第 5 个技能）
- 优化提醒系统，集成飞书通知
- 完善技能矩阵，提升用户体验

### 下周计划
- 推进 AI 视觉监控系统商业化
- 继续发布新技能
- 拓展客户渠道

---

**Powered by Weekly Digest** | https://clawhub.ai/sukimgit/weekly-digest
"""
    return report

def send_feishu(webhook, content):
    """发送飞书消息"""
    try:
        data = {
            "msg_type": "text",
            "content": {
                "text": content
            }
        }
        req = Request(
            webhook,
            data=json.dumps(data).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        response = urlopen(req, timeout=10)
        result = json.loads(response.read().decode('utf-8'))
        
        if result.get('code') == 0 or result.get('StatusCode') == 0 or result.get('success'):
            print("[OK] 飞书发送成功")
            return True
        else:
            print(f"[WARN] 飞书返回：{result}")
            return False
    except Exception as e:
        print(f"[ERROR] 飞书发送失败：{e}")
        return False

def send_email(email_config, subject, content):
    """发送邮件"""
    try:
        msg = MIMEMultipart()
        msg['From'] = email_config['auth_user']
        msg['To'] = email_config['address']
        msg['Subject'] = subject
        msg.attach(MIMEText(content, 'plain', 'utf-8'))
        
        server = smtplib.SMTP_SSL(email_config['smtp_host'], email_config['smtp_port'])
        server.login(email_config['auth_user'], email_config['auth_pass'])
        server.send_message(msg)
        server.quit()
        
        print("[OK] 邮件发送成功")
        return True
    except Exception as e:
        print(f"[ERROR] 邮件发送失败：{e}")
        return False

def main():
    """主函数"""
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    
    print("=" * 60)
    print("Weekly Digest - Test Run")
    print("=" * 60)
    
    # 计算本周时间
    today = datetime.now()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    
    print(f"\n[INFO] 统计周期：{week_start.strftime('%Y-%m-%d')} 至 {week_end.strftime('%Y-%m-%d')}")
    
    # 获取 GitHub 数据
    print(f"\n[INFO] 获取 GitHub 数据：{config['github']['username']}")
    github_data = fetch_github_activity(config['github']['username'], config['github'].get('token'))
    
    if 'error' in github_data:
        print(f"[WARN] GitHub 数据获取失败：{github_data['error']}")
    else:
        print(f"[OK] GitHub 数据获取成功")
        print(f"  仓库：{github_data.get('public_repos', 0)} 个")
        print(f"  关注者：{github_data.get('followers', 0)} 人")
    
    # 生成报告
    print(f"\n[INFO] 生成周报...")
    report = generate_report(github_data, week_start.strftime('%Y-%m-%d'), week_end.strftime('%Y-%m-%d'))
    print(f"[OK] 周报生成完成")
    
    # 发送飞书
    feishu_config = config.get('feishu', {})
    if feishu_config.get('enabled') and feishu_config.get('webhook'):
        print(f"\n[INFO] 发送飞书...")
        # 简化飞书内容
        feishu_text = f"""📊 Weekly Digest - 周报测试

统计周期：{week_start.strftime('%Y-%m-%d')} 至 {week_end.strftime('%Y-%m-%d')}

GitHub: {config['github']['username']}
公开仓库：{github_data.get('public_repos', 0)} 个
关注者：{github_data.get('followers', 0)} 人

这是测试消息，正式周报将在每周五 17:00 发送。

---
Powered by Weekly Digest"""
        send_feishu(feishu_config['webhook'], feishu_text)
    else:
        print(f"\n[INFO] 飞书未启用（跳过）")
    
    # 发送邮件
    email_config = config.get('email', {})
    if email_config.get('enabled') and email_config.get('auth_pass'):
        print(f"\n[INFO] 发送邮件...")
        send_email(email_config, f"Weekly Digest - 周报测试 ({week_start.strftime('%m-%d')})", report)
    else:
        print(f"\n[INFO] 邮件未启用（需要配置授权码）")
    
    print(f"\n" + "=" * 60)
    print("Test completed!")
    print("=" * 60)

if __name__ == "__main__":
    main()
