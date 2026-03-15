---
name: feishu-img-sender
description: "飞书图片发送工具。用于给飞书用户发送图片。需要先上传图片获取 image_key，再用 image_key 发送消息。支持 PNG、JPG、GIF 等常见图片格式。"
---

# 飞书图片发送工具

通过飞书 OpenAPI 发送图片消息。

## 环境要求

- Python 3
- 无需额外依赖（使用标准库）

## 使用方法

### 1. 基本命令

```bash
python3 scripts/feishu_image.py <图片路径> <用户ID>
```

### 2. 示例

```bash
# 发送图片
python3 scripts/feishu_image.py /path/to/image.png ou_efb8bfb0a24b26cb1bb4a45bbed22691

# 发送 JPG 图片
python3 scripts/feishu_image.py photo.jpg ou_efb8bfb0a24b26cb1bb4a45bbed22691
```

## 参数说明

| 参数 | 说明 | 示例 |
|------|------|------|
| 图片路径 | 本地图片文件路径 | `/home/admin/image.png` |
| 用户ID | 用户的 open_id | `ou_efb8bfb0a24b26cb1bb4a45bbed22691` |

## 工作原理

1. 获取飞书 tenant_access_token
2. 上传图片到飞书，获取 image_key
3. 使用 image_key 发送图片消息

## 注意事项

- 图片格式支持：PNG、JPG、GIF 等
- 图片大小有限制（通常 10MB 以内）
- 用户ID 需要是 open_id 格式（以 `ou_` 开头）
