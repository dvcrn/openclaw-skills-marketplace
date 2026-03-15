#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试 Hotmail 邮箱 - 详细调试"""

import imaplib

EMAIL = "sukim_sy@hotmail.com"
PASSWORD = "VVKSY-JPCUC-LQXU8-RHRKG-L6X5K"
IMAP_HOST = "outlook.office365.com"
IMAP_PORT = 993

print("=" * 60)
print("测试 Hotmail 邮箱连接（详细调试）")
print("=" * 60)

try:
    # 连接
    print(f"\n1. 连接到 {IMAP_HOST}:{IMAP_PORT}...")
    mail = imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT)
    print("   [OK] 连接成功")
    
    # 查看支持的认证方式
    print("\n2. 查看支持的认证方式...")
    print(f"   支持：{mail.capabilities}")
    
    # 尝试登录
    print(f"\n3. 尝试登录 {EMAIL}...")
    print(f"   密码：{PASSWORD[:10]}...（隐藏部分）")
    
    try:
        mail.login(EMAIL, PASSWORD)
        print("   [OK] 登录成功！")
        
        # 选择收件箱
        print("\n4. 选择收件箱...")
        status, messages = mail.select('INBOX')
        print(f"   状态：{status}")
        
        if status == 'OK':
            print("   [OK] 收件箱选择成功")
            
            # 搜索邮件
            print("\n5. 搜索邮件...")
            status, messages = mail.search(None, 'ALL')
            if status == 'OK':
                count = len(messages[0].split())
                print(f"   [OK] 收件箱共有 {count} 封邮件")
        else:
            print(f"   [FAIL] {messages}")
        
        mail.close()
        mail.logout()
        
    except imaplib.IMAP4.error as e:
        print(f"   [FAIL] 登录错误：{e}")
        print("\n可能原因:")
        print("  1. IMAP 访问未启用")
        print("  2. 应用密码格式错误")
        print("  3. 账号被锁定")
        print("\n请检查:")
        print("  1. 登录 https://outlook.live.com")
        print("  2. 设置 -> 邮件 -> 同步电子邮件 -> POP 和 IMAP")
        print("  3. 确保'允许设备和应用使用 POP 使用 IMAP'已启用")
        
except Exception as e:
    print(f"\n[ERROR] 异常：{e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
