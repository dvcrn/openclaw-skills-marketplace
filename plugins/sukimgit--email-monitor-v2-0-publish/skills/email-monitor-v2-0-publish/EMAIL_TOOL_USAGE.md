# 邮件发送工具使用说明

**版本：** v1.0  
**创建时间：** 2026-03-10  
**位置：** `skills/email-monitor/`

---

## 📧 功能概述

基于 email-monitor 技能的 SMTP 配置，提供通用邮件发送功能，支持：
- 发送文本邮件
- 发送 HTML 邮件
- 发送附件（支持多个）
- 飞书 webhook 通知

---

## 🔧 配置文件

**SMTP 配置：** `email_config.json`
```json
{
  "email": {
    "smtp": {
      "host": "smtp.qq.com",
      "port": 465,
      "auth": {
        "user": "your_email@example.com",
        "pass": "授权码"
      }
    }
  }
}
```

**飞书 Webhook：** `<YourDataDir>\reminders\config.json`
```json
{
  "feishu_webhook": "https://open.feishu.cn/open-apis/bot/v2/hook/..."
}
```

---

## 📚 使用方法

### 方法 1：使用 EmailSender 类

```python
from email_sender import EmailSender

# 初始化
sender = EmailSender()

# 发送简单邮件
sender.send_email(
    to_address="user@example.com",
    subject="测试邮件",
    body="这是正文"
)

# 发送带附件的邮件
sender.send_email(
    to_address="user@example.com",
    subject="合同文件",
    body="请查收附件",
    attachments=["合同.docx", "报价单.pdf"]
)

# 发送 HTML 邮件
sender.send_email(
    to_address="user@example.com",
    subject="HTML 邮件",
    body="<h1>这是 HTML 正文</h1>",
    is_html=True
)
```

### 方法 2：使用专用脚本

**发送合同：**
```bash
python skills/email-monitor/send_contract.py
```

自动查找 `D:\工作\英特雷真\**\PC*.docx` 并发送到 `your_email@example.com`，完成后飞书通知。

### 方法 3：发送飞书通知

```python
from email_sender import send_feishu_notification

send_feishu_notification("任务完成通知")
```

---

## 📋 完整示例

### 示例：发送报告 + 飞书通知

```python
from email_sender import EmailSender, send_feishu_notification

# 初始化
sender = EmailSender()

# 发送邮件
success = sender.send_email(
    to_address="your_email@example.com",
    subject="周报 - 2026-03-10",
    body="本周工作总结...",
    attachments=["周报.docx"]
)

# 飞书通知
if success:
    send_feishu_notification("""✅ 周报已发送

收件人：your_email@example.com
附件：周报.docx
请查收邮箱！""")
```

---

## 🔍 错误处理

### SMTP 错误

- **550 From header invalid** - QQ 邮箱要求 From 只能是邮箱地址，不能带名称
- **Authentication failed** - 检查授权码是否正确（不是密码）
- **Connection timeout** - 检查网络连接或 SMTP 服务器

### 飞书错误

- **Webhook 失败** - 检查 webhook URL 是否正确
- **内容过长** - 飞书文本消息限制 4096 字符

---

## 📝 最佳实践

1. **长任务流程：**
   - 任务完成 → 发送邮件（带附件）
   - 邮件发送成功 → 飞书通知
   - 用户收到飞书 → 查看邮箱

2. **附件大小：**
   - 建议 < 10MB（QQ 邮箱限制 50MB）
   - 大文件建议使用云文档链接

3. **邮件格式：**
   - 普通通知：纯文本
   - 报告/合同：带附件
   - 营销/周报：HTML 格式

---

## 🎯 实际应用场景

### 场景 1：合同发送
```bash
python skills/email-monitor/send_contract.py
```

### 场景 2：周报自动发送
```python
# 每周五下午 5 点自动发送周报
sender.send_email(
    to_address="your_email@example.com",
    subject=f"周报 - {datetime.now().strftime('%Y-%m-%d')}",
    body=weekly_report,
    attachments=["周报.docx"]
)
send_feishu_notification("✅ 周报已发送")
```

### 场景 3：技能购买自动回复
```python
# 检测到商机邮件
sender.send_email(
    to_address=customer_email,
    subject="感谢咨询 - OpenClaw 技能开发",
    body=reply_template,
    attachments=["技能介绍.pdf", "报价单.docx"]
)
send_feishu_notification(f"📧 已回复客户：{customer_email}")
```

---

## 📊 配置检查清单

- [ ] SMTP 配置正确（host/port/user/pass）
- [ ] 授权码已更新（QQ 邮箱定期更换）
- [ ] 飞书 webhook URL 正确
- [ ] 网络连接正常
- [ ] 附件文件路径存在

---

## 🔗 相关文件

- `email_sender.py` - 通用邮件发送工具
- `send_contract.py` - 合同发送脚本
- `email_config.json` - 邮箱配置
- `REPORTING_RULES.md` - 主动汇报规则

---

**记住：邮件 + 飞书 = 完美搭配！** 📧📢
