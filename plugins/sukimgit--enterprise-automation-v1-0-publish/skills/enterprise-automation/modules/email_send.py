# -*- coding: utf-8 -*-
"""
邮件发送模块
"""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
from pathlib import Path
from typing import Optional, Dict


def send_email(
    to_address: str,
    subject: str,
    body: str,
    smtp_config: Dict,
    attachment_path: Optional[str] = None
) -> bool:
    """发送邮件
    
    Args:
        to_address: 收件人邮箱
        subject: 邮件主题
        body: 邮件正文
        smtp_config: SMTP 配置（包含 host/port/user/pass）
        attachment_path: 附件路径（可选）
    
    Returns:
        bool: 发送是否成功
    """
    try:
        # 创建邮件
        msg = MIMEMultipart()
        msg['From'] = smtp_config['smtp_user']
        msg['To'] = to_address
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        # 添加附件
        if attachment_path and Path(attachment_path).exists():
            with open(attachment_path, 'rb') as f:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(f.read())
                encoders.encode_base64(part)
                file_name = Path(attachment_path).name
                part.add_header('Content-Disposition', f'attachment; filename="{file_name}"')
                msg.attach(part)
        
        # 发送邮件
        server = smtplib.SMTP_SSL(smtp_config['smtp_host'], smtp_config['smtp_port'])
        server.login(smtp_config['smtp_user'], smtp_config['smtp_pass'])
        server.send_message(msg)
        server.quit()
        
        print(f"[OK] 邮件已发送：{to_address}")
        return True
        
    except Exception as e:
        print(f"[ERROR] 邮件发送失败：{e}")
        return False
