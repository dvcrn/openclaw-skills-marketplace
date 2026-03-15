---
name: image-understanding
description: "使用智谱AI的GLM-4V-Flash免费多模态API理解图片内容。当用户需要理解图片内容、描述图片、识别图中物体时使用此skill。"
---

# Image Understanding Skill

这个skill用于理解图片内容，使用智谱AI的GLM-4V-Flash免费多模态API。

## 何时使用

当用户需要理解图片内容时使用此skill，例如：
- "这张图里是什么"
- "描述一下这个图片"
- "这张细胞图显示了什么"
- "分析这张图片的内容"

## 前置要求

用户需要：
1. 访问 https://bigmodel.cn/ 注册账号
2. 获取API Key：https://bigmodel.cn/console/apikeys
3. 将API Key以环境变量方式提供：`ZHIPU_API_KEY`

## 使用方法

### 方式一：使用内置脚本

skill提供了 `scripts/analyze_image.py` 脚本，可以直接调用：

```bash
python scripts/analyze_image.py <图片路径> "<问题>"
```

参数：
- `<图片路径>`: 图片文件路径（建议使用jpg格式）
- `<问题>`: 要问的问题，如"这张图片里有什么"

### 方式二：手动调用API

如果没有脚本，可以直接用Python调用智谱API：

```python
from zhipuai import ZhipuAI

client = ZhipuAI(api_key="你的API Key")

response = client.chat.completions.create(
    model="glm-4v",
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "这张图片里有什么？请详细描述。"},
                {"type": "image_url", "image_url": {"url": "图片URL或base64"}}
            ]
        }
    ]
)

print(response.choices[0].message.content)
```

## 输出格式

返回图片内容的详细描述，包括：
- 图像中的主要物体/人物
- 场景/背景
- 颜色、布局等视觉特征
- 文字（如果有）
- 可能的含义或推断

## 注意事项

- GLM-4V-Flash完全免费，但有调用频率限制
- 支持图片URL或Base64编码
- 最佳支持图片尺寸：1024x1024以内
- 建议使用JPG格式，PNG格式可能存在兼容性问题
