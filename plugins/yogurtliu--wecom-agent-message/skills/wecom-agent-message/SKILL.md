---
name: wecom-agent-message
description: "企业微信应用消息"
---

# WeCom Agent Message - 企业微信应用消息发送

通过企业微信应用发送文本、图片、文件到指定用户。

## 配置

在 `config.json` 中设置：

```json
{
  "corpid": "你的企业ID",
  "corpsecret": "应用Secret",
  "agentid": 1000004,
  "touser": "接收者用户ID"
}
```

## 使用

### 发送文本
```bash
wecom-send text "消息内容"
```

### 发送图片
```bash
wecom-send image /path/to/image.png
```

### 发送文件
```bash
wecom-send file /path/to/document.docx
```

## 依赖

- curl
- jq
