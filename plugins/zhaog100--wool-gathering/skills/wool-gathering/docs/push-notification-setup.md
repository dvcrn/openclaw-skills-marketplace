# 推送通知配置指南

## 📱 支持的推送方式

### **1. Server酱（微信推送）** ⭐⭐⭐⭐⭐
**推荐指数**: ⭐⭐⭐⭐⭐（最简单，免费）
**推送方式**: 微信服务号
**免费额度**: 每天最多5条

#### 注册步骤
1. 访问：https://sct.ftqq.com/
2. 微信扫码登录
3. 绑定微信服务号
4. 复制 SendKey（格式：SCT开头的字符串）

#### 配置示例
```json
{
  "push_config": {
    "serverchan_enabled": true,
    "serverchan_key": "SCTxxxxxxxxxxxxxxxxxxxxxxxx"
  }
}
```

---

### **2. PushPlus（微信推送）** ⭐⭐⭐⭐
**推荐指数**: ⭐⭐⭐⭐（稳定，免费额度大）
**推送方式**: 微信公众号
**免费额度**: 每天200条

#### 注册步骤
1. 访问：https://www.pushplus.plus/
2. 微信扫码登录
3. 复制 Token

#### 配置示例
```json
{
  "push_config": {
    "pushplus_enabled": true,
    "pushplus_token": "YOUR_TOKEN_HERE"
  }
}
```

---

### **3. 钉钉机器人** ⭐⭐⭐
**推荐指数**: ⭐⭐⭐（适合团队）
**推送方式**: 钉钉群消息
**免费额度**: 无限制

#### 配置步骤
1. 创建钉钉群
2. 群设置 → 智能群助手 → 添加机器人
3. 选择"自定义"机器人
4. 安全设置选择"加签"
5. 复制 Webhook URL 和 密钥

#### 配置示例
```json
{
  "push_config": {
    "dingtalk_enabled": true,
    "dingtalk_token": "YOUR_TOKEN_HERE",
    "dingtalk_secret": "YOUR_SECRET_HERE"
  }
}
```

---

### **4. 邮件推送** ⭐⭐
**推荐指数**: ⭐⭐（传统但可靠）
**推送方式**: 邮件
**免费额度**: 取决于邮箱服务商

#### 配置步骤（QQ邮箱为例）
1. 登录QQ邮箱 → 设置 → 账户
2. 开启POP3/SMTP服务
3. 生成授权码（不是QQ密码）
4. SMTP服务器：smtp.qq.com
5. 端口：587

#### 配置示例
```json
{
  "push_config": {
    "email_enabled": true,
    "email_config": {
      "smtp_server": "smtp.qq.com",
      "smtp_port": 587,
      "from_addr": "your_email@qq.com",
      "password": "授权码（不是QQ密码）",
      "to_addr": "target@example.com"
    }
  }
}
```

---

## 🚀 快速配置

### **方法1：直接修改配置文件**

```bash
vi /root/.openclaw/workspace/skills/wool-gathering/assets/config_template.json
```

修改 `push_config` 部分，填入你的 API Key。

---

### **方法2：使用环境变量（推荐）**

```bash
# Server酱
export SERVERCHAN_KEY="SCTxxxxxxxx"

# PushPlus
export PUSHPLUS_TOKEN="xxxxxxxx"

# 钉钉
export DINGTALK_TOKEN="xxxxxxxx"
export DINGTALK_SECRET="SECxxxxxxxx"
```

---

## 🧪 测试推送

### **测试命令**

```bash
cd /root/.openclaw/workspace/skills/wool-gathering/scripts

# 测试Server酱
python3 push_notification.py --title "测试推送" --content "这是一条测试消息" --method serverchan

# 测试PushPlus
python3 push_notification.py --title "测试推送" --content "这是一条测试消息" --method pushplus

# 测试钉钉
python3 push_notification.py --title "测试推送" --content "这是一条测试消息" --method dingtalk

# 测试邮件
python3 push_notification.py --title "测试推送" --content "这是一条测试消息" --method email
```

---

## 📊 对比表格

| 推送方式 | 难度 | 免费 | 实时性 | 推荐 |
|---------|------|------|--------|------|
| Server酱 | ⭐ | 5条/天 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| PushPlus | ⭐ | 200条/天 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 钉钉 | ⭐⭐ | 无限 | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| 邮件 | ⭐⭐⭐ | 无限 | ⭐⭐⭐ | ⭐⭐ |

---

## 💡 推荐方案

### **个人使用**（推荐）
- **首选**: Server酱（简单，够用）
- **备选**: PushPlus（额度大）

### **团队使用**
- **推荐**: 钉钉机器人（免费，实时）

### **稳定可靠**
- **推荐**: 邮件推送（传统但可靠）

---

## 🔗 注册链接

- **Server酱**: https://sct.ftqq.com/
- **PushPlus**: https://www.pushplus.plus/
- **钉钉**: https://www.dingtalk.com/

---

## ⚠️ 注意事项

1. **API Key保密** - 不要泄露给他人
2. **免费额度** - 注意每日限制
3. **测试后再用** - 先发送测试消息确认可用
4. **定期检查** - 确保推送服务正常

---

**最后更新**: 2026-03-03
