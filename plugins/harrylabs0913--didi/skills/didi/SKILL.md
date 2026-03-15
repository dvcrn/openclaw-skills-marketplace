---
name: didi
description: "Didi"
---

# 滴滴出行助手 (Didi Skill)

CLI工具，帮助用户使用滴滴出行打车服务。

## 功能

- **价格预估** - 查询不同车型的预估价格
- **呼叫车辆** - 快速叫车（快车、专车、豪华车）
- **行程状态** - 实时查看当前行程
- **历史订单** - 查看历史打车记录
- **优惠券** - 查询可用优惠券
- **扫码登录** - 支持APP扫码登录

## 安装

```bash
cd ~/.openclaw/workspace/skills/didi
pip install -r requirements.txt
playwright install chromium
```

## 使用方法

### 1. 登录
```bash
python didi.py login
```
使用滴滴APP扫码登录，保存会话信息。

### 2. 价格预估
```bash
python didi.py estimate "国贸" "天安门"
python didi.py estimate "北京南站" "首都机场"
```

### 3. 呼叫车辆
```bash
# 默认叫快车
python didi.py call "国贸" "天安门"

# 指定车型
python didi.py call "国贸" "天安门" --type premier
```

支持车型:
- `express` - 滴滴快车（默认）
- `select` - 滴滴优享
- `premier` - 滴滴专车
- `luxury` - 豪华车

### 4. 查看行程状态
```bash
python didi.py status
```
显示当前进行中的行程、司机信息、预计到达时间。

### 5. 查看历史订单
```bash
python didi.py history
```

### 6. 查询优惠券
```bash
python didi.py coupon
```

## 数据存储与安全

### 存储架构
- **主目录**: `~/.openclaw/data/didi/secure/` (加密存储)
- **会话数据**: `cookies.enc` (AES-256 加密存储)
- **缓存数据**: `didi.db` (SQLite数据库)
- **加密密钥**: `.key` (权限 600)

### 隐私保护
1. **加密存储**: 所有敏感数据使用 Fernet 加密 (AES-256)
2. **用户同意**: 首次运行需要明确同意数据使用条款
3. **数据控制**: 支持一键清除所有个人数据
4. **透明审计**: 可查看所有存储的文件和权限

### 隐私控制命令
```bash
# 查看隐私信息
didi privacy info

# 清除所有个人数据  
didi privacy clear

# 导出加密数据（备份）
didi privacy export
```

## 技术实现

- Python + Playwright 浏览器自动化
- SQLite 本地数据存储 (加密)
- 反检测措施（避免被识别为爬虫）
- 支持滴滴网页版和小程序

## 依赖

- Python 3.8+
- `playwright>=1.40.0` (浏览器自动化)
- `cryptography>=42.0.0` (加密库)
- Chromium 浏览器

## 注意事项

1. 首次使用需要先登录
2. 叫车功能会打开浏览器窗口，请保持浏览器开启
3. 价格预估为参考价格，实际价格可能因路况、时间等因素有所变化
4. 建议使用前先进行价格预估
