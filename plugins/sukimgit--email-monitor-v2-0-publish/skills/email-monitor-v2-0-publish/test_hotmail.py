#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试 Hotmail 邮箱 IMAP 连接"""

import imaplib
import smtplib

# 配置
EMAIL = "sukim_sy@hotmail.com"
PASSWORD = "VVKSY-JPCUC-LQXU8-RHRKG-L6X5K"  # 应用密码
IMAP_HOST = "outlook.office365.com"
IMAP_PORT = 993
SMTP_HOST = "smtp-mail.outlook.com"
SMTP_PORT = 587

print("=" * 60)
print("测试 Hotmail 邮箱连接")
print("=" * 60)

try:
    # 测试 IMAP（收信）
    print("\n1. 测试 IMAP 收信...")
    print(f"   连接 {IMAP_HOST}:{IMAP_PORT}")
    mail = imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT)
    print("   [OK] 连接成功")
    
    print(f"   登录 {EMAIL}...")
    mail.login(EMAIL, PASSWORD)
    print("   [OK] 登录成功")
    
    print("   选择收件箱...")
    status, messages = mail.select('INBOX')
    if status == 'OK':
        print("   [OK] 收件箱选择成功")
        
        print("   搜索邮件...")
        status, messages = mail.search(None, 'ALL')
        if status == 'OK':
            count = len(messages[0].split())
            print(f"   [OK] 收件箱共有 {count} 封邮件")
            
            if count > 0:
                print("\n   最近 5 封邮件:")
                email_ids = messages[0].split()[-5:]
                for eid in email_ids:
                    status, msg_data = mail.fetch(eid, '(RFC822.HEADER)')
                    if status == 'OK':
                        msg = msg_data[0][1].decode('utf-8', errors='ignore')
                        for line in msg.split('\n'):
                            if line.startswith('Subject:'):
                                print(f"     - {line[8:].strip()}")
                                break
    else:
        print(f"   [FAIL] 收件箱选择失败：{messages}")
    
    mail.close()
    mail.logout()
    
    # 测试 SMTP（发信）
    print("\n2. 测试 SMTP 发信...")
    print(f"   连接 {SMTP_HOST}:{SMTP_PORT}")
    server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
    server.starttls()
    print("   [OK] 连接成功")
    
    print(f"   登录 {EMAIL}...")
    server.login(EMAIL, PASSWORD)
    print("   [OK] 登录成功")
    
    server.quit()
    print("   [OK] SMTP 测试完成")
    
    print("\n" + "=" * 60)
    print("[SUCCESS] Hotmail 邮箱配置成功！")
    print("=" * 60)
    
except Exception as e:
    print(f"\n[ERROR] 错误：{e}")
    print("\n可能的原因:")
    print("  1. 密码错误")
    print("  2. IMAP 未开启")
    print("  3. 需要应用密码")
    print("\n解决方法:")
    print("  1. 登录 https://outlook.live.com")
    print("  2. 设置 -> 邮件 -> 同步电子邮件 -> POP 和 IMAP")
    print("  3. 确保启用 POP 和 IMAP 访问")

print("\n" + "=" * 60)
