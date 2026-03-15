---
name: elm-ec
description: "elm-ec"
---

# Eleme (饿了么) Skill

CLI tool for Eleme food delivery platform.

## Commands

### Search Food/Restaurants
```bash
elm search "奶茶"
elm search "汉堡" --location "北京市朝阳区" --limit 20
```

### Login
```bash
elm login
```
Opens browser with QR code for authentication.

### Red Packet Info
```bash
elm redpacket
```
Shows available coupons and red packets.

## Features

- Restaurant search with caching
- QR code login
- Coupon/red packet tracking
- Delivery time and fee info
- Rating and sales data
- Anti-detection browser automation

## Dependencies

- Python 3.9+
- `playwright>=1.40.0` (浏览器自动化)
- `cryptography>=42.0.0` (加密库)
- 安装命令: `pip install -r requirements.txt`

## 数据存储与安全

### 存储位置
- **主目录**: `~/.openclaw/data/elm/` (加密存储)
- **会话数据**: `cookies.enc` (AES-256 加密存储)
- **缓存数据**: `elm.db` (SQLite数据库)
- **加密密钥**: `.key` (权限 600)

### 隐私保护
1. **加密存储**: 所有敏感数据使用 Fernet 加密
2. **用户同意**: 首次运行需要明确同意数据使用条款
3. **数据控制**: 支持一键清除所有个人数据
4. **透明审计**: 可查看所有存储的文件和权限

### 隐私控制命令
```bash
# 查看隐私信息
elm privacy info

# 清除所有个人数据
elm privacy clear

# 导出加密数据（备份）
elm privacy export
```

## Security
This skill uses browser automation for legitimate shopping assistance only.
All user data is encrypted and stored locally. No data transmission to external servers.
See SECURITY.md for details.
