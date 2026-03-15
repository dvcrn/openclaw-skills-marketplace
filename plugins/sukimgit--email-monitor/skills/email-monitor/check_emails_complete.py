#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Email Monitor - 检查新邮件并自动回复（完整版）
"""

import json
import smtplib
import imaplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header, decode_header
from datetime import datetime, timedelta
import email.utils
import os
import sys
import requests
import time

# 加载配置
CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'email_config.json')
try:
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        config = json.load(f)
except FileNotFoundError:
    print("错误：找不到配置文件 email_config.json，请先创建配置文件。")
    sys.exit(1)

EMAIL_CONFIG = config['email']
MONITOR_CONFIG = config['monitor']

# 关键词
PRIORITY_KEYWORDS = MONITOR_CONFIG.get('priority_keywords', ["定制", "开发", "报价", "订单", "price", "order"])
CONSULTATION_KEYWORDS = MONITOR_CONFIG.get('consultation_keywords', ["咨询", "询问", "功能", "服务"])
VERIFICATION_KEYWORDS = MONITOR_CONFIG.get('verification_keywords', ["验证", "确认", "激活", "code"])
IGNORE_KEYWORDS = MONITOR_CONFIG.get('ignore_keywords', ["发票", "广告", "促销", "spam"])
IGNORE_SENDERS = MONITOR_CONFIG.get('ignore_senders', ["10000@qq.com", "no-reply@"])

# 自动回复模板 - 效率工坊 | Efficiency Lab

# 模板 1：商机询价邮件
REPLY_TEMPLATE_BUSINESS = """\
Subject: Re: {subject} - 效率工坊 | Efficiency Lab

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【中文】

尊敬的客户：

您好！感谢您联系效率工坊。

【关于我们】
效率工坊是专业的 AI 自动化解决方案提供商，专注于帮助企业实现工作流程智能化。

【服务内容】
1. AI 技能定制开发：¥5,000-20,000/个
   - 根据需求复杂度定价
   - 包含需求分析、开发、测试、部署
   - 首年免费维护

2. 自动化系统集成：¥10,000-50,000/项目
   - 企业工作流程自动化
   - 邮件/消息自动处理
   - 数据自动采集与分析

3. 技术咨询与培训：¥20,000/场
   - AI 技术应用培训
   - 自动化方案设计
   - 现场指导与答疑

【合作流程】
1. 需求沟通（1-2 天）
2. 方案评估与报价（1-2 天）
3. 签订合同（1 天）
4. 开发与测试（7-15 天）
5. 部署与培训（1-2 天）
6. 售后维护（首年免费）

【付款方式】
- 支付宝：gaowf@163.com（高万峰）
- PayPal：回复获取账号
- Wise：回复获取账号
- 支持对公转账（需提前沟通）

【下一步】
为了给您提供更精准的报价，请您提供：
1. 具体需求描述
2. 期望完成时间
3. 预算范围（可选）

我们会在收到您的需求后 1-2 个工作日内提供详细方案和报价。

期待与您的合作！

此致
敬礼

老高 | 效率工坊 创始人
📧 1776480440@qq.com
📱 微信：回复获取

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【English】

Dear Valued Customer,

Thank you for contacting Efficiency Lab!

【About Us】
Efficiency Lab is a professional AI automation solutions provider.

【Our Services】
1. Custom AI Skill Development: ¥5,000-20,000/skill
2. Automation System Integration: ¥10,000-50,000/project
3. Technical Consulting & Training: ¥20,000/session

【Cooperation Process】
1. Requirements discussion (1-2 days)
2. Solution evaluation and quotation (1-2 days)
3. Contract signing (1 day)
4. Development and testing (7-15 days)
5. Deployment and training (1-2 days)
6. After-sales support (First year free)

【Payment Methods】
- Alipay: gaowf@163.com
- PayPal/Wise: Reply for details

【Next Steps】
Please provide:
1. Detailed requirements description
2. Expected completion time
3. Budget range (optional)

We will provide a detailed solution within 1-2 business days.

Looking forward to cooperating with you!

Best regards,

老高 (Gao) | Founder, Efficiency Lab
📧 1776480440@qq.com

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

# 模板 2：一般咨询邮件
REPLY_TEMPLATE_CONSULTATION = """\
Subject: Re: {subject} - 效率工坊 | Efficiency Lab

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【中文】

您好！感谢联系效率工坊。

【快速了解】
效率工坊是 AI 自动化技能开发平台，帮助企业实现工作流程自动化。

【核心功能】
✅ 邮件自动监控与回复
✅ 消息自动处理与通知
✅ 数据自动采集与分析
✅ 定时任务与提醒
✅ 知识库管理与检索

【价格区间】
- 技能定制：¥5,000-20,000/个
- 系统集成：¥10,000-50,000/项目
- 技术咨询：¥20,000/场

【获取详细方案】
请回复邮件告诉我们您的具体需求，我们会提供详细方案和报价。

访问 https://clawhub.ai 查看已发布技能

如有任何问题，欢迎随时联系！

老高 | 效率工坊
📧 1776480440@qq.com

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【English】

Hello! Thank you for contacting Efficiency Lab.

【Quick Overview】
Efficiency Lab is an AI automation skill development platform.

【Core Features】
✅ Automatic email monitoring and reply
✅ Message automatic processing and notification
✅ Data automatic collection and analysis
✅ Scheduled tasks and reminders
✅ Knowledge base management and retrieval

【Price Range】
- Custom Skill: ¥5,000-20,000/skill
- System Integration: ¥10,000-50,000/project
- Technical Consulting: ¥20,000/session

【Get Detailed Solution】
Please reply with your specific requirements.

Visit https://clawhub.ai to view published skills.

If you have any questions, feel free to contact us!

老高 (Gao) | Efficiency Lab
📧 1776480440@qq.com

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

# 默认模板（兼容旧版本）
REPLY_TEMPLATE = REPLY_TEMPLATE_CONSULTATION

def get_reply_template(email_type, keywords_found):
    """根据邮件类型和关键词获取回复模板"""
    # 商机邮件（询价/合作）
    business_keywords = ['询价', '报价', '价格', '多少钱', '合作', '定制', '开发', '项目', 'quote', 'price', 'custom']
    if email_type == 'priority' or any(kw in keywords_found for kw in business_keywords):
        return REPLY_TEMPLATE_BUSINESS
    
    # 技术咨询
    tech_keywords = ['API', '接口', '集成', '技术', '对接']
    if any(kw in keywords_found for kw in tech_keywords):
        return REPLY_TEMPLATE_CONSULTATION  # 暂时用咨询模板，后续可添加技术模板
    
    # 默认咨询模板
    return REPLY_TEMPLATE_CONSULTATION

def decode_mime_words(s):
    """解码 MIME 编码的字符串"""
    if not s:
        return ""
    decoded = []
    for part, encoding in decode_header(s):
        if isinstance(part, bytes):
            try:
                decoded.append(part.decode(encoding or 'utf-8', errors='ignore'))
            except:
                decoded.append(part.decode('latin-1', errors='ignore'))
        else:
            decoded.append(part)
    return ''.join(decoded)

def check_keywords(subject, body, keywords):
    """检查是否包含关键词"""
    text = (subject + " " + body).lower()
    return any(kw.lower() in text for kw in keywords)

def send_feishu_message(webhook_url, title, content):
    """发送飞书消息通知"""
    headers = {'Content-Type': 'application/json'}
    payload = {
        "msg_type": "post",
        "content": {
            "post": {
                "zh_cn": {
                    "title": title,
                    "content": [
                        [
                            {
                                "tag": "text",
                                "text": content
                            }
                        ]
                    ]
                }
            }
        }
    }
    
    try:
        response = requests.post(webhook_url, headers=headers, json=payload)
        if response.status_code == 200:
            print("   [✓] 飞书通知发送成功")
            return True
        else:
            print(f"   [✗] 飞书通知发送失败：{response.status_code}")
            return False
    except Exception as e:
        print(f"   [✗] 飞书通知发送异常：{e}")
        return False

def send_feishu_notification(subject, sender, email_type):
    """发送飞书通知"""
    webhook_url = MONITOR_CONFIG.get('feishuWebhook', '')
    if not webhook_url:
        print("   [⚠] 未配置飞书 Webhook，跳过通知")
        return
    
    title = f"📧 {email_type}邮件提醒"
    content = f"发件人：{sender}\n主题：{subject}"
    
    send_feishu_message(webhook_url, title, content)

def send_auto_reply(to_address, subject, body, email_type='consultation'):
    """发送自动回复（根据邮件类型选择模板）"""
    try:
        # 收集找到的关键词
        keywords_found = []
        all_keywords = (
            MONITOR_CONFIG.get('priority_keywords', []) +
            MONITOR_CONFIG.get('consultation_keywords', []) +
            MONITOR_CONFIG.get('verification_keywords', [])
        )
        for kw in all_keywords:
            if kw.lower() in (subject + " " + body).lower():
                keywords_found.append(kw)
        
        # 根据邮件类型和关键词选择模板
        template = get_reply_template(email_type, keywords_found)
        
        # 格式化模板（替换主题）
        reply_content = template.format(subject=subject)
        
        msg = MIMEMultipart()
        msg['From'] = EMAIL_CONFIG['address']
        msg['To'] = to_address
        msg['Subject'] = f"Re: {decode_mime_words(subject)}"
        msg.attach(MIMEText(reply_content, 'plain', 'utf-8'))
        
        server = smtplib.SMTP_SSL(EMAIL_CONFIG['smtp']['host'], EMAIL_CONFIG['smtp']['port'])
        server.login(EMAIL_CONFIG['smtp']['auth']['user'], EMAIL_CONFIG['smtp']['auth']['pass'])
        server.send_message(msg)
        server.quit()
        print("   [✓] 已发送自动回复")
        return True
    except Exception as e:
        print(f"   [✗] 回复失败：{e}")
        return False

def check_emails():
    """主函数：检查新邮件"""
    print("=" * 60)
    print(f"📧 邮件检查 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    try:
        # 连接 IMAP
        print(f"1. 连接到 {EMAIL_CONFIG['imap']['host']}...")
        mail = imaplib.IMAP4_SSL(EMAIL_CONFIG['imap']['host'], EMAIL_CONFIG['imap']['port'])
        mail.login(EMAIL_CONFIG['imap']['auth']['user'], EMAIL_CONFIG['imap']['auth']['pass'])
        mail.select()
        print("   [OK] 连接成功")
        
        # 搜索未读邮件（最近 24 小时）
        since = (datetime.now() - timedelta(days=1)).strftime("%d-%b-%Y")
        status, messages = mail.search(None, f'(UNSEEN SINCE {since})')
        
        if status != 'OK':
            print("   [✗] 搜索失败")
            return
        
        email_ids = messages[0].split()
        count = len(email_ids)
        print(f"\n2. 发现 {count} 封新邮件")
        
        if count == 0:
            print("\n✅ 没有新邮件")
            mail.logout()
            return
        
        # 处理每封邮件
        processed = 0
        for eid in email_ids:
            status, msg_data = mail.fetch(eid, '(RFC822)')
            if status != 'OK':
                continue
            
            msg = email.message_from_bytes(msg_data[0][1])
            
            # 提取信息
            sender = decode_mime_words(msg.get('From', ''))
            subject = decode_mime_words(msg.get('Subject', ''))
            
            # 提取正文
            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        try:
                            body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                        except:
                            pass
                        break
            else:
                try:
                    body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
                except:
                    pass
            
            print(f"\n--- 邮件 {processed + 1}/{count} ---")
            print(f"发件人：{sender}")
            print(f"主题：{subject}")
            
            # 检查是否忽略的发件人
            if any(ignore in sender for ignore in IGNORE_SENDERS):
                print("   [跳过] 忽略的发件人")
                processed += 1
                continue
            
            # 检查是否包含垃圾关键词
            if check_keywords(subject, body, IGNORE_KEYWORDS):
                print("   [分类] 🗑️ 垃圾邮件（跳过）")
                processed += 1
                continue
            
            # 检查邮件类型
            email_type = "普通"
            if check_keywords(subject, body, PRIORITY_KEYWORDS):
                email_type = "商机"
                print("   [分类] 🎯 商机邮件")
                if MONITOR_CONFIG.get('notifyFeishu', True):
                    send_feishu_notification(subject, sender, "商机")
                if MONITOR_CONFIG.get('autoReply', True):
                    send_auto_reply(msg.get('From', ''), subject, body, "priority")
            elif check_keywords(subject, body, CONSULTATION_KEYWORDS):
                email_type = "咨询"
                print("   [分类] 💬 咨询邮件")
                if MONITOR_CONFIG.get('notifyFeishu', True):
                    send_feishu_notification(subject, sender, "咨询")
                if MONITOR_CONFIG.get('autoReply', True):
                    send_auto_reply(msg.get('From', ''), subject, body, "consultation")
            elif check_keywords(subject, body, VERIFICATION_KEYWORDS):
                email_type = "验证"
                print("   [分类] 🔐 验证邮件（跳过）")
            else:
                print("   [分类] 📮 普通邮件")
            
            processed += 1
        
        mail.logout()
        print(f"\n{'=' * 60}")
        print(f"✅ 检查完成，处理了 {processed} 封邮件")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n[ERROR] 错误：{e}")
        import traceback
        traceback.print_exc()

def main():
    """主入口函数"""
    import sys
    import io
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    check_emails()

if __name__ == "__main__":
    main()