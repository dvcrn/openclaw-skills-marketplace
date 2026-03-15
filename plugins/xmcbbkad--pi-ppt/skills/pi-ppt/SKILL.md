---
name: pi-ppt
description: "调用 Pi API 生成 PPT。通过传入要生成的PPT的内容描述、PPT的页数和PPT的语言来控制。"
---

# Pi PPT 生成

## 触发条件
当用户出现以下意图时使用本 skill：
- 提到 “生成 PPT”
- 提到 “使用pi-ppt skill 生成PPT”

## 使用方法

1. **配置认证凭据**：调用 API 前，需先设置 `PIPPT_APP_ID` 和 `PIPPT_APP_SECRET`。推荐通过环境变量注入：
   ```bash
   export PIPPT_APP_ID="你的 app_id"
   export PIPPT_APP_SECRET="你的 app_secret"
   ```
2. 执行代码 `scripts/generate_pi_ppt.py`
  - 调用 `generate_pi_ppt(content, cards, language, timeout_s, poll_interval_s)` 函数生成PPT，参数说明：
    - `content`（str）：PPT 的主题或描述，例如 "大模型介绍"
    - `cards`（int）：幻灯片页数，默认 8
    - `language`（str）：语言，`zh` 中文 / `en` 英文

     该函数实际上首先调用`create_document`函数触发生成任务，然后通过轮询调用`get_status`函数查看PPT的生成状态. get_status 接口状态：
        - `running`：继续轮询
        - `done`：返回 `url`
        - `fail`：抛出失败异常
      超时未完成则抛 `TimeoutError`

 **返回值**（成功时）：
    `generate_pi_ppt(...)` 成功时返回至少包含：
        - `resource_id`: 任务 ID
        - `status`: `"done"`
        - `url`: 文档可访问链接

## 最小调用示例

```python
from scripts.generate_pi_ppt import generate_pi_ppt

PIPPT_APP_ID     = os.getenv("PIPPT_APP_ID", "").strip()
PIPPT_APP_SECRET = os.getenv("PIPPT_APP_SECRET", "").strip()

result = generate_pi_ppt(
    content="做一个关于AI的PPT",
    cards=8,
    language="zh",
)
print(result["url"])
```

## 注意
- 调用API前首先要检查 PIPPT_APP_ID 和 PIPPT_APP_SECRET 这两个环境变量是否设置，如果没有设置要提醒用户设置。 
- 生成一个PPT大概要耗时2-3分钟，需要提醒用户耐心等待。