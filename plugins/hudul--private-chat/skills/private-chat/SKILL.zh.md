---
name: private-chat
description: 私密聊天模式 - 通过暗号触发加密对话，敏感信息自动加密存储。支持 AES-256-CBC 加密，确保私密内容安全。
---

# Private Chat Skill

一个为 OpenClaw 设计的私密聊天技能，允许用户通过暗号进入加密对话模式，所有敏感信息都会自动加密存储。

## 功能特性

- 🔐 **暗号触发** - 通过特定暗号进入私密模式
- 🛡️ **AES-256-CBC 加密** - 军用级加密标准
- ⏱️ **自动退出** - 超过设定时间无对话自动退出
- 📝 **加密存储** - 私密内容存储在独立加密文件中
- 🔑 **密码保护** - 支持自定义加密密码

## 安装

```bash
clawhub install private-chat
```

## 配置

1. 复制示例配置文件：
```bash
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

## 使用方法

### 进入私密模式

用户输入暗号（默认 `lgbt`）：
```
lgbt
```

AI 响应：
```
进入私密模式 🔒

欢迎回来，[用户昵称]。有什么需要我帮忙的吗？
```

### 存储敏感信息

在私密模式下直接告诉 AI 敏感信息：
```
我的银行卡密码是 123456
```

AI 会自动加密存储，并回应：
```
已安全存储 ✅

你的银行卡密码已加密保存到私密保险箱。

存储位置: memory/private-vault.md
加密算法: AES-256-CBC
```

### 查看加密内容

在私密模式下询问：
```
我的银行卡密码是多少？
```

AI 会解密并显示：
```
你的银行卡密码: 123456
```

### 退出私密模式

超过配置的时间（默认1分钟）无对话，自动退出。

或手动发送退出暗号：
```
exit
```

## 解密方法

### 命令行解密

```bash
# 方式1: 直接解密
./scripts/private-vault.sh decrypt "your-password" "ENC[v1:SALT:BASE64]"

# 方式2: 交互式
cd skills/private-chat
./scripts/private-vault.sh interactive
```

### 手动解密

加密格式：`ENC[v1:SALT:BASE64]`

使用 OpenSSL：
```bash
echo "BASE64_CONTENT" | base64 -d | openssl enc -aes-256-cbc -d -k "your-password" -pbkdf2
```

## 安全规则

### 私密模式规则

1. **进入后** - 正常记录对话内容
2. **严格保密** - 不向任何人透露私密内容
3. **自动退出** - 超过设定时间无对话，自动退出
4. **退出后永不引用** - 一旦退出，后续对话中永久不得引用、暗示、重复该模式下任何内容

### 非私密模式规则

⚠️ **最高优先级规则（铁律）：**

> **在非私密模式下，必须完全隐藏私密模式的存在。**
> - 不得提及"私密模式"、"暗号"、"加密对话"等任何相关概念
> - 不得透露存在加密存储的内容
> - 被问及"有什么秘密/私密内容"时，必须回答"没有"或"不知道"
> - 就当这个功能**完全不存在**

## 文件结构

```
skills/private-chat/
├── SKILL.md                 # 技能说明（英文）
├── SKILL.zh.md             # 技能说明（中文）
├── README.md               # 项目介绍（英文）
├── README.zh.md            # 项目介绍（中文）
├── config.example.json     # 示例配置文件
├── config.json             # 用户配置文件（需自己创建）
└── scripts/
    └── private-vault.sh    # 加密解密脚本
```

## 加密脚本用法

### 加密

```bash
./scripts/private-vault.sh encrypt "password" "要加密的文本"
```

输出：`ENC[v1:SALT:BASE64]`

### 解密

```bash
./scripts/private-vault.sh decrypt "password" "ENC[v1:SALT:BASE64]"
```

### 交互式

```bash
./scripts/private-vault.sh interactive
```

## 注意事项

1. **密码安全** - 请使用强密码，不要泄露给他人
2. **备份加密文件** - 定期备份 `memory/private-vault.md`
3. **忘记密码** - 如果忘记密码，加密内容将无法恢复
4. **不要修改** - 不要手动修改加密内容格式

## 语言

📖 [English Documentation](SKILL.md)

## 作者

由 **兵步一郎 (Ichiro)** 开发。

为个人使用而创建，与 OpenClaw 社区分享。

## License

MIT
