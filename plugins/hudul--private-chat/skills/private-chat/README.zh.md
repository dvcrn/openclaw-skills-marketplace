# Private Chat for OpenClaw

🔐 私密聊天模式 - 为你的 OpenClaw 助手添加加密对话功能

[📖 English Documentation](README.md)

## 功能亮点

- 🔑 **暗号触发** - 通过特定暗号进入私密模式
- 🛡️ **AES-256-CBC 加密** - 军用级加密标准保护敏感信息
- ⏱️ **自动超时** - 无对话自动退出，防止信息泄露
- 📝 **安全存储** - 加密内容存储在独立文件中
- 🔓 **随时解密** - 提供命令行和交互式解密工具

## 演示

### 进入私密模式
```
用户: lgbt
AI: 进入私密模式 🔒
    欢迎回来。有什么需要我帮忙的吗？
```

### 存储敏感信息
```
用户: 我的银行卡密码是 123456
AI: 已安全存储 ✅
    你的银行卡密码已加密保存到私密保险箱。
    存储位置: memory/private-vault.md
    加密算法: AES-256-CBC
```

### 查看加密内容
```
用户: 我的银行卡密码是多少？
AI: 你的银行卡密码: 123456
```

## 安装

```bash
clawhub install private-chat
```

## 配置

1. 复制示例配置：
```bash
cd skills/private-chat
cp config.example.json config.json
```

2. 编辑 `config.json`：
```json
{
  "codeword": "your-secret-codeword",
  "password": "your-encryption-password",
  "autoExitMinutes": 1,
  "storageFile": "memory/private-vault.md"
}
```

## 加密格式

所有加密内容使用标准格式：
```
ENC[v1:SALT:BASE64]
```

示例：
```
ENC[v1:a1b2c3d4:U2FsdGVkX1+...]
```

## 解密工具

### 命令行解密

```bash
# 加密
./scripts/private-vault.sh encrypt "password" "secret text"

# 解密
./scripts/private-vault.sh decrypt "password" "ENC[v1:...]"

# 交互式
./scripts/private-vault.sh interactive
```

### 使用 OpenSSL

```bash
echo "BASE64_CONTENT" | base64 -d | \
  openssl enc -aes-256-cbc -d -k "password" -pbkdf2
```

## 安全提示

⚠️ **请务必：**
- 使用强密码（16位以上，包含大小写+数字+符号）
- 定期备份 `memory/private-vault.md`
- 不要与他人分享你的加密密码

⚠️ **警告：**
- 如果忘记密码，加密内容**无法恢复**
- 不要手动修改加密文件格式
- 退出私密模式后，AI 不会记得任何对话内容

## 工作原理

1. **触发检测** - AI 检测到暗号，进入私密模式
2. **内容识别** - 识别敏感信息（密码、密钥等）
3. **自动加密** - 使用 AES-256-CBC 加密敏感内容
4. **安全存储** - 保存到独立的加密文件
5. **自动退出** - 超时后自动退出，清除上下文

## 作者

由 OpenClaw 社区贡献

## License

MIT
