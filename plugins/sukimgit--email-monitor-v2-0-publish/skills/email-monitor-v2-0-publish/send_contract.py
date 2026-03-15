# -*- coding: utf-8 -*-
"""
发送 PC 站开发合同
复用 email-monitor 的 SMTP 配置
发送完成后飞书通知
"""

import sys
import glob
from pathlib import Path

# 导入邮件发送工具
sys.path.insert(0, str(Path(__file__).parent))
from email_sender import EmailSender, send_feishu_notification

def find_contract_file() -> str:
    """查找 PC 站开发合同文件"""
    search_paths = [
        r"D:\工作\英特雷真\**\PC*.docx",
        r"D:\工作\英特雷真\合同\*.docx",
    ]
    
    for pattern in search_paths:
        files = glob.glob(pattern, recursive=True)
        if files:
            return files[0]
    
    raise FileNotFoundError("未找到 PC 站开发合同文件")

def main():
    """主函数"""
    print("=" * 60)
    print("Sending PC Station Development Contract")
    print("=" * 60)
    
    # 查找合同文件
    try:
        file_path = find_contract_file()
        file_size = Path(file_path).stat().st_size
        print(f"[OK] Found contract file: {file_path}")
        print(f"       Size: {file_size / 1024:.2f} KB")
    except FileNotFoundError as e:
        print(f"[ERROR] {e}")
        return False
    
    # 初始化邮件发送器
    sender = EmailSender()
    
    # 构建邮件内容
    to_address = "your_email@example.com"
    subject = "PC 站开发合同"
    body = f"""客户，

这是你要的 PC 站开发合同，请查收。

文件信息：
- 文件名：PC 站开发合同.docx
- 大小：{file_size / 1024:.2f} KB
- 路径：{file_path}

如有问题，随时联系我。

祝好！
Monet
"""
    
    # 发送邮件
    print("\n[MAIL] Sending email...")
    success = sender.send_email(
        to_address=to_address,
        subject=subject,
        body=body,
        attachments=[file_path]
    )
    
    if not success:
        print("[ERROR] Email send failed")
        return False
    
    # 发送飞书通知
    print("\n[FEISHU] Sending notification...")
    feishu_content = f"""[OK] PC Station Development Contract Sent

To: {to_address}
Attachment: PC 站开发合同.docx ({file_size / 1024:.2f} KB)
Please check your email!"""
    
    send_feishu_notification(feishu_content)
    
    print("\n" + "=" * 60)
    print("TASK COMPLETED!")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
