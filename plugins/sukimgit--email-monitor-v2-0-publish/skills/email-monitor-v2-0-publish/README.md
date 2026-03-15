# Email Monitor v2.0 - 使用说明

**效率工坊 | Efficiency Lab 出品**

---

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install requests
```

### 2. 配置邮箱

复制示例配置：
```bash
cp email_config.example.json email_config.json
```

编辑 `email_config.json`，填写你的配置：
```json
{
  "email": {
    "address": "your_email@qq.com",
    "imap": {
      "host": "imap.qq.com",
      "auth": {
        "user": "your_email@qq.com",
        "pass": "your_app_password"
      }
    }
  },
  "monitor": {
    "feishuWebhook": "your_feishu_webhook_url"
  }
}
```

**获取 QQ 邮箱授权码：**
1. 登录 QQ 邮箱网页版
2. 设置 → 账户
3. 开启 IMAP/SMTP 服务
4. 生成授权码

**获取飞书 Webhook：**
1. 飞书群 → 群设置
2. 群机器人 → 添加机器人
3. 复制 Webhook URL

### 3. 运行

```bash
python check_emails_complete.py
```

---

## 📊 功能特性

- ✅ 自动监控邮箱（每 30 分钟）
- ✅ 商机邮件自动识别
- ✅ 自动回复（中英双语模板）
- ✅ 飞书实时通知
- ✅ 垃圾邮件过滤
- ✅ 发送频次控制（防封号）

---

## 💼 商务模板

**v2.0 新增 3 个商务模板：**

1. **商机询价模板** - 触发词：询价/报价/合作/定制
2. **一般咨询模板** - 触发词：咨询/了解/服务
3. **技术对接模板** - 触发词：API/接口/技术

---

## 🔒 安全建议

1. **不要提交真实配置到 Git**
   ```bash
   echo "email_config.json" >> .gitignore
   ```

2. **使用环境变量存储敏感信息**
   ```bash
   export EMAIL_PASSWORD="your_password"
   ```

3. **定期更换授权码**

---

## 📧 联系支持

**效率工坊 | Efficiency Lab**

- 📧 Email：your_email@example.com
- 🌐 Website：https://clawhub.ai

---

## 💰 定价

| 版本 | 价格 | 功能 |
|------|------|------|
| 标准版 | 免费 | 基础监控 + 自动回复 |
| 专业版 | ¥350/月 | 多邮箱 + 数据统计 |
| 定制版 | ¥7000-20000 | 私有化部署 + 功能定制 |

---

**效率工坊 | Efficiency Lab**
*让工作更高效，让自动化更简单*
