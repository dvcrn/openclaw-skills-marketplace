---
name: xiaohongshu-api
description: "小红书数据API - 通过TikHub获取小红书帖子、评论、用户信息 / Xiaohongshu Data API via TikHub"
---

# 小红书数据API / Xiaohongshu API

基于TikHub获取小红书公开数据。

## 功能 / Features

- 📝 获取帖子详情 / Get post details
- 💬 获取评论 / Get comments
- 👤 获取用户信息 / Get user info
- 🔍 搜索帖子 / Search posts
- 🔥 获取热门 / Get trending

## 使用方法 / Usage

```bash
# 获取帖子
python xiaohongshu.py --post-id <帖子ID>

# 搜索
python xiaohongshu.py --search <关键词>

# 热门
python xiaohongshu.py --trending
```

## 配置 / Configuration

需要TikHub API Key（免费注册）：
https://api.tikhub.io

```python
TIKHUB_API_KEY = "your_api_key"
```

## API示例 / Examples

```python
from xiaohongshu import XiaohongshuAPI

api = XiaohongshuAPI(api_key="your_key")

# 获取帖子
post = api.get_post("67c8a0ed0000000001f00e2b")

# 搜索
results = api.search("AI教程")

# 热门
trending = api.get_trending()
```

## 注意事项

- 仅获取公开数据
- 遵守TikHub使用条款
- 尊重用户隐私
