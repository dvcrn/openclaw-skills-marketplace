#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试 163 邮箱 IMAP 连接"""

import imaplib

# 配置
EMAIL = "sukim_sy@163.com"
PASSWORD = "SYN4RyCyHWvGdGS5"  # 授权码
IMAP_HOST = "imap.163.com"
IMAP_PORT = 993

print("=" * 60)
print("测试 163 邮箱 IMAP 连接")
print("=" * 60)

try:
    # 连接
    print(f"1. 连接到 {IMAP_HOST}:{IMAP_PORT}...")
    mail = imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT)
    print("   [OK] 连接成功")
    
    # 登录
    print(f"2. 登录 {EMAIL}...")
    mail.login(EMAIL, PASSWORD)
    print("   [OK] 登录成功")
    
    # 选择收件箱
    print("3. 选择收件箱...")
    status, messages = mail.select()
    print(f"   状态：{status}")
    
    if status == 'OK':
        print("   [OK] 收件箱选择成功")
        
        # 搜索邮件
        print("4. 搜索邮件...")
        status, messages = mail.search(None, 'ALL')
        if status == 'OK':
            count = len(messages[0].split())
            print(f"   [OK] 收件箱共有 {count} 封邮件")
            
            # 显示最近 5 封
            if count > 0:
                print("\n最近 5 封邮件:")
                email_ids = messages[0].split()[-5:]
                for eid in email_ids:
                    status, msg_data = mail.fetch(eid, '(RFC822.HEADER)')
                    if status == 'OK':
                        msg = msg_data[0][1].decode('utf-8', errors='ignore')
                        # 提取主题
                        for line in msg.split('\n'):
                            if line.startswith('Subject:'):
                                print(f"  - {line[8:]}")
                                break
    else:
        print(f"   [FAIL] 收件箱选择失败：{messages}")
    
    mail.close()
    mail.logout()
    
except Exception as e:
    print(f"\n[ERROR] 错误：{e}")
    print("\n可能的原因:")
    print("  1. 授权码错误（不是登录密码）")
    print("  2. IMAP/SMTP 服务未开启")
    print("  3. 邮箱账号不存在")
    print("\n解决方法:")
    print("  1. 登录 https://mail.163.com")
    print("  2. 设置 -> POP3/SMTP/IMAP")
    print("  3. 确保 IMAP/SMTP 服务已开启")
    print("  4. 重新生成授权码")

print("\n" + "=" * 60)
