# AA（Animate Anyone）API（DashScope）

官方文档：
- `https://help.aliyun.com/zh/model-studio/animateanyone-video-generation-api`

## 鉴权与地域
- 鉴权：`Authorization: Bearer $DASHSCOPE_API_KEY`
- 地域：**北京**（`dashscope.aliyuncs.com`）
- 异步头：`X-DashScope-Async: enable`

## 提交任务
`POST https://dashscope.aliyuncs.com/api/v1/services/aigc/image2video/video-synthesis`

> AA 的具体模型名会随版本更新，使用控制台/文档里的最新 model 名。

示例请求：
```json
{
  "model": "<AA_MODEL_NAME>",
  "input": {
    "image_url": "https://.../person.jpg",
    "video_url": "https://.../motion.mp4"
  },
  "parameters": {
    "mode": "wan-std"
  }
}
```

## 查询任务
`GET https://dashscope.aliyuncs.com/api/v1/tasks/{task_id}`

成功结果：`output.results.video_url`

## 说明
- AA 与 EMO 都走 DashScope 异步任务框架（task_id + 轮询）
- 若用户只需口播头像，优先 EMO；若需要全身动作，使用 AA
