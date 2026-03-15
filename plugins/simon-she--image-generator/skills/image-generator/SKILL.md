---
name: image-generator
description: "image-generator"
---

# Image Generator Skill

> 本地生图工作流 - SD 1.5 / SDXL 模型支持

## 激活条件
- 用户请求生成图片
- 用户说"画xxx"、"生成xxx图片"

## 工作流程

### 1. 读取提示词模板（可选）
如需特定风格，读取：
```
~/.openclaw/workspace/skills/image-prompts/SKILL.md
```

### 2. 启动 Subagent 执行
**重要：使用 subagent，不阻塞主对话**

```python
sessions_spawn(
    label="生图任务",
    mode="run",
    runtime="subagent",
    task=f"""生成图片：
1. 模型: runwayml/stable-diffusion-v1-5
2. 提示词: "{提示词}"
3. num_inference_steps=20, guidance_scale=7.5
4. 保存到 /tmp/xxx.png
5. 发到群聊 oc_9c60944330ed6a8873289d605eb668fe"""
)
```

### 3. 本地生图命令（Subagent 内执行）

**SD 1.5（默认，更快）：**
```python
import torch
torch.set_num_threads(8)  # 使用8核CPU

from diffusers import StableDiffusionPipeline
pipe = StableDiffusionPipeline.from_pretrained("runwayml/stable-diffusion-v1-5")
pipe.to("cpu")

image = pipe(
    "提示词",
    num_inference_steps=20,
    guidance_scale=7.5,
    negative_prompt="low quality, blurry, distorted"
).images[0]
image.save("/tmp/xxx.png")
```

**SDXL（更精细但慢）：**
```python
from diffusers import StableDiffusionXLPipeline
pipe = StableDiffusionXLPipeline.from_pretrained("stabilityai/stable-diffusion-xl-base-1.0")
pipe.to("cpu")

image = pipe("提示词", num_inference_steps=20, guidance_scale=7.5).images[0]
image.save("/tmp/xxx.png")
```

### 4. 发送图片到飞书

**重要：发到群聊，私聊有权限限制**

```python
import requests
import json

app_id = "cli_a92eadd694799bd3"
app_secret = "OPJrEdYF8ZPpwFUmQgrh9bXVX862LKwG"

# 1. 获取 token
r = requests.post("https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
                 json={"app_id": app_id, "app_secret": app_secret})
token = r.json()["tenant_access_token"]

# 2. 上传图片
with open("/tmp/xxx.png", "rb") as f:
    r = requests.post("https://open.feishu.cn/open-apis/im/v1/images",
                     headers={"Authorization": f"Bearer {token}"},
                     files={"image": ("img.png", f, "image/png")},
                     data={"image_type": "message"})
    img_key = r.json()["data"]["image_key"]

# 3. 发送到群聊
chat_id = "oc_9c60944330ed6a8873289d605eb668fe"
requests.post(f"https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id",
             headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
             json={"receive_id": chat_id, "msg_type": "image", 
                   "content": json.dumps({"image_key": img_key})})
```

## 模型选择

| 模型 | 速度 | 质量 | 内存 |
|------|------|------|------|
| SD 1.5 | 快3-4倍 | 基础 | ~4GB |
| SDXL | 慢 | 更精细 | ~13GB |

**默认使用 SD 1.5**

## 提示词模板

风格提示词见：`~/.openclaw/workspace/skills/image-prompts/SKILL.md`

常用风格：
- 毛绒绒玩偶
- 水晶/玻璃材质
- 皮克斯风格
- 浮世绘风格

## 注意事项

1. **必须用 subagent** - 不阻塞主对话
2. **发送到群聊** - 私聊有权限限制
3. **CPU 设置** - `torch.set_num_threads(8)`
4. **float16** - SDXL + CPU 不兼容，会报错
