#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Email Monitor - 检查新邮件并自动回复
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
import re

# 加载环境变量
ENV_PATH = os.path.join(os.path.expanduser('~'), '.openclaw', '.env')
if os.path.exists(ENV_PATH):
    with open(ENV_PATH, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()

def resolve_env_variables(text):
    """解析 ${VAR_NAME} 格式的环境变量"""
    def replace_var(match):
        var_name = match.group(1)
        return os.environ.get(var_name, match.group(0))
    return re.sub(r'\$\{([^}]+)\}', replace_var, text)

# 加载配置
CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'email_config.json')
with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
    config_text = f.read()
    config = json.loads(resolve_env_variables(config_text))

EMAIL_CONFIG = config['email']
MONITOR_CONFIG = config['monitor']

# 关键词（新配置格式）
PRIORITY_KEYWORDS = MONITOR_CONFIG.get('priority_keywords', [])
CONSULTATION_KEYWORDS = MONITOR_CONFIG.get('consultation_keywords', [])
VERIFICATION_KEYWORDS = MONITOR_CONFIG.get('verification_keywords', [])
IGNORE_KEYWORDS = MONITOR_CONFIG.get('ignore_keywords', [])
IGNORE_SENDERS = MONITOR_CONFIG.get('ignore_senders', [])
IGNORE_TIME = MONITOR_CONFIG.get('ignoreTime', '08:00')
DELETE_SPAM = MONITOR_CONFIG.get('deleteSpam', False)

# 动作配置
PRIORITY_ACTION = MONITOR_CONFIG.get('priority_action', 'reply_and_notify')
CONSULTATION_ACTION = MONITOR_CONFIG.get('consultation_action', 'reply_with_info')
VERIFICATION_ACTION = MONITOR_CONFIG.get('verification_action', 'ignore')
SPAM_ACTION = MONITOR_CONFIG.get('spam_action', 'mark_as_spam')
IGNORE_ACTION = MONITOR_CONFIG.get('ignore_action', 'mark_as_read')

# 自动回复模板（中英双语）
REPLY_TEMPLATE = """\
【中文】
您好！感谢联系 OpenClaw 技能开发服务。

【服务内容】
- OpenClaw 技能定制开发：5000-20000 元/个
- AI 自动化系统集成：10000-50000 元/项目
- 企业培训/技术咨询：20000 元/场

【已发布技能】
- Weekly Digest（AI 周报生成器）：https://clawhub.ai/sukimgit/weekly-digest
- Email Monitor（邮件自动监控）：https://clawhub.ai/sukimgit/email-monitor
- Smart Butler（AI 智能管家）：https://clawhub.ai/sukimgit/smart-butler
- Task Reminder（任务提醒系统）：https://clawhub.ai/sukimgit/task-reminder

【支付方式 Payment】
- 国际 International:
  - PayPal: 私信获取账号（需要时提供）
  - Wise: Account 242009405 (SWIFT: TRWIAUS1XXX)
- 国内 Domestic:
  - 支付宝 Alipay: gaowf@163.com (高万峰) [推荐]
  - 银行转账 Bank Transfer: 私信获取账号

如有具体问题，欢迎继续询问！

【English】
Hello! Thank you for contacting OpenClaw skill development services.

【Services】
- Custom Skill Development: 5000-20000 CNY
- AI Automation Integration: 10000-50000 CNY
- Enterprise Training: 20000 CNY/session

【Published Skills】
- Weekly Digest: https://clawhub.ai/sukimgit/weekly-digest
- Email Monitor: https://clawhub.ai/sukimgit/email-monitor
- Smart Butler: https://clawhub.ai/sukimgit/smart-butler
- Task Reminder: https://clawhub.ai/sukimgit/task-reminder

【Payment】
- International:
  - PayPal: DM for account (provided when needed)
  - Wise: Account 242009405 (SWIFT: TRWIAUS1XXX)
- Domestic (China):
  - Alipay: gaowf@163.com (Gao Wanfeng) [Recommended]
  - Bank Transfer: DM for account details

Please share your requirements, I'll provide a detailed quote.

Best regards,
老高 | OpenClaw Team
📧 1776480440@qq.com
"""
