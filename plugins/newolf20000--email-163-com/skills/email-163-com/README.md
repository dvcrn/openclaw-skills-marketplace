# email-163-com - 163 邮箱邮件管理工具

完整的 163 邮箱邮件管理解决方案，支持发送、接收、搜索和管理邮件。

## 🚀 安装

### 1. 添加到 PATH

```bash
# 方法 1: 创建软链接
ln -s ~/.openclaw/workspace/skills/email-163-com/email-163-com ~/.local/bin/email-163-com

# 方法 2: 添加到 PATH
export PATH="$PATH:~/.openclaw/workspace/skills/email-163-com"
```

### 2. 配置邮箱

```bash
# 运行配置向导
email-163-com init
```

或编辑配置文件：
```bash
nano ~/.config/email-163-com/config.json
```

## 📖 使用

### 发送邮件

```bash
# 简单发送
email-163-com send --to friend@example.com --subject "Hello" --body "Hi there!"

# 发送 HTML
email-163-com send --to friend@example.com --subject "Report" --html "<h1>Monthly Report</h1>"

# 发送附件
email-163-com send --to friend@example.com --subject "File" --attach document.pdf

# 从文件读取
email-163-com send --to friend@example.com --subject "Message" --file message.txt
```

### 读取邮件

```bash
# 读取最新 5 封
email-163-com read

# 读取 10 封
email-163-com read --count 10

# 读取指定文件夹
email-163-com read --folder "已发送" --count 5

# 只读未读
email-163-com read --unread --count 10
```

### 管理文件夹

```bash
# 列出所有文件夹
email-163-com folders
```

### 搜索邮件

```bash
# 按发件人
email-163-com search --from "Cloudflare"

# 按主题
email-163-com search --subject "verify"

# 组合搜索
email-163-com search --from "阿里云" --subject "通知" --count 10
```

### 管理附件

```bash
# 列出附件
email-163-com attachments --id 123

# 下载附件
email-163-com attachments --id 123 --download --output ~/Downloads/
```

## 📋 完整命令

```
email-163-com <command> [options]

命令:
  init          初始化配置
  send          发送邮件
  read          读取邮件
  folders       列出文件夹
  search        搜索邮件
  attachments   管理附件

帮助:
  email-163-com --help
  email-163-com <command> --help
```

## 🔧 配置

配置文件位置：`~/.config/email-163-com/config.json`

```json
{
  "email": "your_email@163.com",
  "password": "your_auth_code",
  "imap_server": "imap.163.com",
  "imap_port": 993,
  "smtp_server": "smtp.163.com",
  "smtp_port": 465,
  "imap_id": {
    "name": "OpenClaw",
    "version": "1.0.0",
    "vendor": "email-163-com",
    "support_email": "your_email@163.com"
  },
  "defaults": {
    "folder": "INBOX",
    "count": 5,
    "output_dir": "~/Downloads"
  }
}
```

## 📚 示例

### 日常工作流程

```bash
# 早上检查新邮件
email-163-com read --unread --count 20

# 回复邮件
email-163-com send --to colleague@example.com \
  --subject "Re: Project Update" \
  --file reply.txt \
  --attach report.pdf

# 搜索特定邮件
email-163-com search --from "boss@example.com" --count 5

# 下载附件
email-163-com attachments --id 456 --download
```

### 清理邮箱

```bash
# 查看垃圾邮件
email-163-com read --folder "垃圾邮件" --count 50

# 搜索旧邮件
email-163-com search --subject "广告" --count 100
```

## 🐛 故障排查

### IMAP 连接失败
```
Error: SELECT Unsafe Login
```
**解决**: 确保配置了 IMAP ID 信息（默认已配置）

### 认证失败
```
Error: LOGIN failed
```
**解决**: 检查授权码是否正确（不是登录密码）

### 找不到命令
```
bash: email-163-com: command not found
```
**解决**: 确保已添加到 PATH 或使用完整路径

## 📞 支持

- 技能目录：`~/.openclaw/workspace/skills/email-163-com/`
- 配置文件：`~/.config/email-163-com/config.json`
- 主脚本：`email.py`

## 📄 许可证

MIT License

---

**版本**: 1.0.0  
**创建日期**: 2026-02-19  
**作者**: OpenClaw
