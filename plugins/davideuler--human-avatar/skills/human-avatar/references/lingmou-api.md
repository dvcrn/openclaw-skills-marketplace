# 灵眸（LingMou）API

官方文档：
- 基于模板创建播报视频：
  `https://help.aliyun.com/zh/avatar/avatar-application/developer-reference/api-lingmou-2025-05-27-createbroadcastvideofromtemplate`
- 批量查询播报视频：
  `https://help.aliyun.com/zh/avatar/avatar-application/developer-reference/api-lingmou-2025-05-27-listbroadcastvideosbyid`

## 鉴权与地域
- 鉴权：阿里云 AK/SK（OpenAPI 签名）
- 地域：`cn-beijing`
- Endpoint：`lingmou.cn-beijing.aliyuncs.com`
- API 版本：`2025-05-27`

## 核心流程
1. 准备播报模板（控制台）并拿到 `templateId`
2. 调 `CreateBroadcastVideoFromTemplate`
3. 用返回 `id` 轮询 `ListBroadcastVideosById`
4. `status=SUCCESS` 后读取 `videoURL`

## CreateBroadcastVideoFromTemplate 入参（关键）
```json
{
  "templateId": "BS1b2WNnRMu4ouRzT4clY9Jhg",
  "name": "播报视频合成测试",
  "variables": [
    {
      "name": "text_content",
      "type": "text",
      "properties": {"content": "待播报文案"}
    }
  ],
  "videoOptions": {
    "resolution": "720p",
    "fps": 30,
    "watermark": true
  }
}
```

## ListBroadcastVideosById 返回（关键）
- `data[].status`: `SUCCESS / ERROR / ...`
- `data[].videoURL`
- `data[].captionURL`

## 变量类型
- `text`：文本
- `image`：图片资源
- `avatar`：数字人资源
- `voice`：音色资源
