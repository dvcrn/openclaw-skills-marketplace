# -*- coding: utf-8 -*-
"""
通用邮件发送工具
复用 email-monitor 的 SMTP 配置
支持发送文本、附件、HTML
"""

import smtplib
import json
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
from pathlib import Path
from typing import List, Optional
import sys

class EmailSender:
    """通用邮件发送器"""
    
    def __init__(self, config_path: Optional[str] = None):
        """初始化邮件发送器
        
        Args:
            config_path: 邮箱配置文件路径，默认使用 email-monitor 的配置
        """
        if config_path is None:
            config_path = r"C:\Users\YourName\.openclaw\workspace\skills\email-monitor\email_config.json"
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        self.smtp_host = config['email']['smtp']['host']
        self.smtp_port = config['email']['smtp']['port']
        self.smtp_user = config['email']['smtp']['auth']['user']
        self.smtp_pass = config['email']['smtp']['auth']['pass']
        self.from_address = config['email']['address']
        self.from_name = config['email']['name']
    
    def send_email(
        self,
        to_address: str,
        subject: str,
        body: str,
        attachments: Optional[List[str]] = None,
        is_html: bool = False
    ) -> bool:
        """发送邮件
        
        Args:
            to_address: 收件人邮箱
            subject: 邮件主题
            body: 邮件正文
            attachments: 附件文件路径列表
            is_html: 是否为 HTML 格式
        
        Returns:
            bool: 发送是否成功
        """
        try:
            # 创建邮件
            msg = MIMEMultipart()
            msg['From'] = self.from_address  # QQ 邮箱要求 From 只能是邮箱地址
            msg['To'] = to_address
            msg['Subject'] = subject
            
            # 添加正文
            content_type = 'html' if is_html else 'plain'
            msg.attach(MIMEText(body, content_type, 'utf-8'))
            
            # 添加附件
            if attachments:
                for file_path in attachments:
                    with open(file_path, 'rb') as f:
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(f.read())
                        encoders.encode_base64(part)
                        file_name = Path(file_path).name
                        part.add_header('Content-Disposition', f'attachment; filename="{file_name}"')
                        msg.attach(part)
            
            # 发送邮件
            server = smtplib.SMTP_SSL(self.smtp_host, self.smtp_port)
            server.login(self.smtp_user, self.smtp_pass)
            server.send_message(msg)
            server.quit()
            
            print(f"[OK] Email sent successfully")
            print(f"To: {to_address}")
            print(f"Subject: {subject}")
            if attachments:
                print(f"Attachments: {len(attachments)} file(s)")
            
            return True
            
        except Exception as e:
            print(f"[ERROR] Email send failed: {e}")
            return False


def send_feishu_notification(content: str, webhook_url: Optional[str] = None) -> bool:
    """发送飞书通知
    
    Args:
        content: 通知内容
        webhook_url: 飞书 webhook URL，默认使用 config.json 中的配置
    
    Returns:
        bool: 发送是否成功
    """
    import urllib.request
    import json as json_lib
    
    if webhook_url is None:
        config_path = r"<YourDataDir>\reminders\config.json"
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json_lib.load(f)
        webhook_url = config['feishu_webhook']
    
    try:
        data = {
            "msg_type": "text",
            "content": {
                "text": content
            }
        }
        
        req = urllib.request.Request(
            webhook_url,
            data=json_lib.dumps(data).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        
        response = urllib.request.urlopen(req, timeout=10)
        result = json_lib.loads(response.read().decode('utf-8'))
        
        if result.get('code') == 0 or result.get('StatusCode') == 0:
            print(f"[OK] Feishu notification sent")
            return True
        else:
            print(f"[WARN] Feishu response: {result}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Feishu notification failed: {e}")
        return False


if __name__ == "__main__":
    # 测试示例
    sender = EmailSender()
    
    # 测试发送邮件
    success = sender.send_email(
        to_address="your_email@example.com",
        subject="测试邮件",
        body="这是一封测试邮件",
        attachments=[]
    )
    
    if success:
        # 发送飞书通知
        send_feishu_notification("✅ 测试邮件已发送")
    
    sys.exit(0 if success else 1)
