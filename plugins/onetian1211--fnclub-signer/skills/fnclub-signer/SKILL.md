---
name: fnclub-signer
description: "飞牛论坛(club.fnnas.com)自动签到。触发场景：(1) 用户要求\"飞牛签到\"、\"飞牛论坛签到\"、\"fnclub签到\"；(2) 设置定时飞牛论坛签到任务；(3) 查询飞牛论坛签到状态。"
---

# 飞牛论坛签到

自动完成飞牛私有云论坛(club.fnnas.com)每日签到，获取飞牛币奖励。

## 配置

使用前需要配置账号和百度OCR API（用于验证码识别）。

### 方式一：环境变量（推荐）

```bash
export FNCLUB_USERNAME="你的用户名"
export FNCLUB_PASSWORD="你的密码"
export BAIDU_OCR_API_KEY="百度OCR API Key"
export BAIDU_OCR_SECRET_KEY="百度OCR Secret Key"
```

### 方式二：配置文件

在 `scripts/config.json` 中配置：

```json
{
  "username": "你的用户名",
  "password": "你的密码",
  "baidu_ocr_api_key": "百度OCR API Key",
  "baidu_ocr_secret_key": "百度OCR Secret Key"
}
```

### 获取百度OCR API

1. 访问 [百度AI开放平台](https://ai.baidu.com/)
2. 创建应用，选择"文字识别"服务
3. 获取 API Key 和 Secret Key

## 使用

### 手动签到

```bash
node scripts/fnclub_signer.js
```

### 定时签到

使用 OpenClaw cron 设置每日自动签到：

```bash
openclaw cron add \
  --name "fnclub-signer" \
  --every "1d" \
  --session main \
  --system-event "fnclub-sign" \
  --description "飞牛论坛每日签到" \
  --tz "Asia/Shanghai"
```

## 文件说明

- `scripts/fnclub_signer.js` - 主签到脚本 (Node.js) ✅ 推荐
- `scripts/fnclub_signer.py` - 备用签到脚本 (Python)
- `scripts/config.json` - 配置文件
- `scripts/cookies.json` - Cookie缓存（自动生成）
- `scripts/node_modules/` - Node.js 依赖
