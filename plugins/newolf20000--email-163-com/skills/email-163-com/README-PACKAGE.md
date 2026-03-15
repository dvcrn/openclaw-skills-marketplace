# 📦 email-163-com 技能分享包

**版本**: 1.0.0  
**打包日期**: 2026-02-19  
**大小**: 22KB（压缩后）

---

## 📥 安装方法

### 方法 1: 直接解压（推荐）

```bash
# 1. 解压到技能目录
tar -xzf email-163-com.tar.gz -C ~/.openclaw/workspace/skills/

# 2. 验证安装
~/.openclaw/workspace/skills/email-163-com/email-163-com --help

# 3. 开始使用
email-163-com read --count 5
```

### 方法 2: 使用安装脚本

```bash
# 1. 运行安装脚本
bash email-163-com/install.sh

# 2. 验证安装
email-163-com --help
```

---

## 🔧 配置

配置文件位置：`~/.config/email-163-com/config.json`

```json
{
  "email": "your_email@163.com",
  "password": "your_auth_code",
  "imap_server": "imap.163.com",
  "imap_port": 993,
  "smtp_server": "smtp.163.com",
  "smtp_port": 465
}
```

**获取授权码**：
1. 登录网页版 163 邮箱：https://mail.163.com/
2. 设置 → POP3/SMTP/IMAP
3. 开启 IMAP/SMTP 服务
4. 生成客户端授权码

---

## 📖 使用示例

### 读取邮件
```bash
email-163-com read --count 5
```

### 发送邮件
```bash
email-163-com send \
  --to friend@example.com \
  --subject "Hello" \
  --body "Hi there!"
```

### 发送附件
```bash
email-163-com send \
  --to friend@example.com \
  --subject "File" \
  --attach document.pdf
```

### 搜索邮件
```bash
email-163-com search --from "Cloudflare" --count 10
```

### 列出文件夹
```bash
email-163-com folders
```

### 下载附件
```bash
email-163-com attachments --id 123 --download
```

---

## 📋 功能列表

- ✅ 发送邮件（支持 HTML/纯文本）
- ✅ 发送附件（支持多附件）
- ✅ 读取邮件（IMAP ID 认证）
- ✅ 文件夹管理
- ✅ 邮件搜索
- ✅ 附件下载
- ✅ 未读邮件过滤
- ✅ 中文支持

---

## 🎯 测试状态

✅ 10/10 测试通过

- 命令行帮助 ✅
- 读取邮件 ✅
- 读取未读 ✅
- 文件夹列表 ✅
- 搜索邮件 ✅
- 发送邮件 ✅
- 发送附件 ✅
- 附件管理 ✅
- IMAP ID 认证 ✅
- TLS 加密 ✅

---

## 📞 技术支持

- **技能文档**: `email-163-com/SKILL.md`
- **使用指南**: `email-163-com/README.md`
- **测试报告**: `email-163-com/TEST-REPORT.md`

---

## 📄 许可证

MIT License

---

**打包者**: OpenClaw  
**日期**: 2026-02-19  
**版本**: 1.0.0
