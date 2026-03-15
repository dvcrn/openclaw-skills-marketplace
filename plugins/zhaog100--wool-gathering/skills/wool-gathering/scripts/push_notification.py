#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
推送通知工具
支持微信、QQ、邮件等多种推送方式
"""

import json
import requests
from typing import Optional

class PushNotification:
    def __init__(self, config_path="../assets/config_template.json"):
        self.config = self.load_config(config_path)
        self.push_config = self.config.get("push_config", {})

    def load_config(self, config_path):
        """加载配置文件"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def send(self, title: str, content: str, method: Optional[str] = None):
        """发送通知（自动选择方法）"""
        if method:
            return self.send_by_method(title, content, method)

        # 按优先级尝试
        methods = ["serverchan", "pushplus", "dingtalk", "email"]
        for m in methods:
            if self.push_config.get(f"{m}_enabled"):
                result = self.send_by_method(title, content, m)
                if result:
                    return True

        print("❌ 没有可用的推送方式")
        return False

    def send_by_method(self, title: str, content: str, method: str):
        """指定方法发送"""
        if method == "serverchan":
            return self.send_serverchan(title, content)
        elif method == "pushplus":
            return self.send_pushplus(title, content)
        elif method == "dingtalk":
            return self.send_dingtalk(title, content)
        elif method == "email":
            return self.send_email(title, content)
        else:
            print(f"❌ 不支持的推送方式: {method}")
            return False

    def send_serverchan(self, title: str, content: str):
        """Server酱微信推送"""
        key = self.push_config.get("serverchan_key")
        if not key:
            print("❌ 未配置Server酱Key")
            return False

        url = f"https://sctapi.ftqq.com/{key}.send"
        data = {
            "title": title,
            "desp": content
        }

        try:
            response = requests.post(url, data=data, timeout=10)
            result = response.json()
            if result.get("code") == 0:
                print("✅ Server酱推送成功")
                return True
            else:
                print(f"❌ Server酱推送失败: {result}")
                return False
        except Exception as e:
            print(f"❌ Server酱推送异常: {e}")
            return False

    def send_pushplus(self, title: str, content: str):
        """PushPlus微信推送"""
        token = self.push_config.get("pushplus_token")
        if not token:
            print("❌ 未配置PushPlus Token")
            return False

        url = "http://www.pushplus.plus/send"
        data = {
            "token": token,
            "title": title,
            "content": content,
            "template": "markdown"
        }

        try:
            response = requests.post(url, json=data, timeout=10)
            result = response.json()
            if result.get("code") == 200:
                print("✅ PushPlus推送成功")
                return True
            else:
                print(f"❌ PushPlus推送失败: {result}")
                return False
        except Exception as e:
            print(f"❌ PushPlus推送异常: {e}")
            return False

    def send_dingtalk(self, title: str, content: str):
        """钉钉机器人推送"""
        token = self.push_config.get("dingtalk_token")
        secret = self.push_config.get("dingtalk_secret")

        if not token:
            print("❌ 未配置钉钉Token")
            return False

        url = f"https://oapi.dingtalk.com/robot/send?access_token={token}"

        # 如果有密钥，生成签名
        if secret:
            import time
            import hmac
            import hashlib
            import base64
            import urllib.parse

            timestamp = str(round(time.time() * 1000))
            string_to_sign = f"{timestamp}\n{secret}"
            hmac_code = hmac.new(
                secret.encode("utf-8"),
                string_to_sign.encode("utf-8"),
                digestmod=hashlib.sha256
            ).digest()
            sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
            url += f"&timestamp={timestamp}&sign={sign}"

        data = {
            "msgtype": "markdown",
            "markdown": {
                "title": title,
                "text": f"### {title}\n\n{content}"
            }
        }

        try:
            response = requests.post(url, json=data, timeout=10)
            result = response.json()
            if result.get("errcode") == 0:
                print("✅ 钉钉推送成功")
                return True
            else:
                print(f"❌ 钉钉推送失败: {result}")
                return False
        except Exception as e:
            print(f"❌ 钉钉推送异常: {e}")
            return False

    def send_email(self, title: str, content: str):
        """邮件推送"""
        smtp_config = self.push_config.get("email_config", {})
        if not smtp_config:
            print("❌ 未配置邮件")
            return False

        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart

            msg = MIMEMultipart()
            msg['From'] = smtp_config['from_addr']
            msg['To'] = smtp_config['to_addr']
            msg['Subject'] = title
            msg.attach(MIMEText(content, 'plain', 'utf-8'))

            server = smtplib.SMTP(
                smtp_config['smtp_server'],
                smtp_config.get('smtp_port', 25)
            )
            server.login(
                smtp_config['from_addr'],
                smtp_config['password']
            )
            server.sendmail(
                smtp_config['from_addr'],
                [smtp_config['to_addr']],
                msg.as_string()
            )
            server.quit()

            print("✅ 邮件推送成功")
            return True
        except Exception as e:
            print(f"❌ 邮件推送异常: {e}")
            return False

def main():
    import argparse

    parser = argparse.ArgumentParser(description="推送通知工具")
    parser.add_argument("--title", required=True, help="通知标题")
    parser.add_argument("--content", required=True, help="通知内容")
    parser.add_argument("--method", help="推送方式 (serverchan/pushplus/dingtalk/email)")
    parser.add_argument("--config", default="../assets/config_template.json", help="配置文件路径")

    args = parser.parse_args()

    push = PushNotification(args.config)
    push.send(args.title, args.content, args.method)

if __name__ == "__main__":
    main()
