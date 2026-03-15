# 企业自动化助手 - 快速使用指南

## 🚀 3 分钟快速开始

### 步骤 1：配置邮箱

编辑 `email_config.json`：
```json
{
  "smtp_host": "smtp.qq.com",
  "smtp_port": 465,
  "email": "your_email@qq.com",
  "password": "your_smtp_password"
}
```

### 步骤 2：配置飞书 Webhook

编辑 `feishu_config.json`：
```json
{
  "webhook": "https://open.feishu.cn/open-apis/bot/v2/hook/YOUR_WEBHOOK"
}
```

### 步骤 3：测试文件搜索

```bash
# 搜索文件
python file_searcher.py "D:\工作" "合同" .pdf 10
```

### 步骤 4：测试邮件发送

```bash
# 使用现有工具发送
python ../../tools/file_sender.py "D:\工作" "合同" .pdf "client@example.com"
```

---

## 📋 完整工作流

### 场景：发送合同给客户

**1. 搜索合同**
```bash
python file_searcher.py "D:\工作\合同" "某某科技公司" .pdf
```

**2. 飞书会收到确认消息**
```
📁 文件搜索确认

找到 3 个相关文件：

1. 某某科技公司服务合同 2025.pdf (111.0 KB)
2. 某某科技公司续签合同 2024.pdf (105.0 KB)
3. 某某科技公司补充协议.pdf (50.0 KB)

请回复数字选择文件（如：1）
```

**3. 回复数字选择**
```
1
```

**4. 自动发送邮件**
- 自动附加选中的文件
- 自动填写邮件主题
- 发送到客户邮箱

**5. 飞书收到完成通知**
```
✅ 文件已发送

文件：某某科技公司服务合同 2025.pdf
大小：111.0 KB
收件人：client@example.com
状态：已发送
```

---

## 🔧 高级用法

### 批量发送

创建 `batch_send.py`：
```python
from file_searcher import search_files
from file_sender import send_file

# 搜索所有合同
contracts = search_files("D:\工作\合同", "合同", ".pdf")

# 批量发送
for contract in contracts:
    send_file(
        file_path=contract['path'],
        to_address="client@example.com",
        subject=f"合同：{contract['name']}"
    )
```

### 自定义通知

创建 `notify.py`：
```python
import requests
import json

def send_notification(message: str):
    webhook = "YOUR_FEISHU_WEBHOOK"
    
    data = {
        "msg_type": "text",
        "content": {"text": message}
    }
    
    requests.post(webhook, json=data)

# 使用
send_notification("合同已发送，请查收！")
```

---

## ❓ 常见问题

**Q: 中文路径乱码怎么办？**
A: 我们的工具已完美支持中文路径，不会乱码。

**Q: 文件太大发不了怎么办？**
A: 支持最大 50MB 附件，超大文件建议用云存储。

**Q: 能自动发送吗？**
A: 可以，创建脚本调用 API 即可自动发送。

**Q: 安全吗？**
A: 发送前有飞书确认流程，不会发错。

---

## 📞 技术支持

- 私信获取联系方式
- 文档：见 SKILL.md
