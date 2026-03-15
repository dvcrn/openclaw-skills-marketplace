---
name: jfbym-captcha-skill
description: "云码验证码处理 Skill。注册链接: https://console.jfbym.com/register/TG133710 。支持本地免费识别（可无 token 使用）与收费云码 API（需 token）。适用于 OpenClaw/ClawHub 与浏览器RPA自动化。"
---

# 云码（JFBYM）验证码能力 Skill
## 能力总览

本 Skill 分为两条能力线：

- 免费本地能力：完全在本地执行，不上传到第三方 API。

- 收费云码能力：通过云码 API 获取更稳定的复杂验证码识别能力。
- 收费接口保持显式 `captcha_type` 透传；`solve_common`、`solve_slide` 不会自动猜类型，`guess_captcha_type` 仅作辅助映射。

关联：验证码坐标计算、滑块偏移量、点选坐标返回、旋转角度识别、轨迹验证、空间推理验证码、RPA验证码自动化。

## 免费能力（本地）

> 适合优先降本，覆盖常见简单验证码。无需 `token`。

### 支持能力

- 通用文本识别：`solve_local_text_captcha(image_input)`
- 字符集约束识别：`solve_local_text_captcha_with_range(image_input, charset_range=...)`
- 算术验证码识别：`solve_local_math_captcha(image_input)`
- 文本框检测：`detect_local_text_boxes(image_input)`
- 滑块匹配（ddddocr）：`solve_local_slide_distance_ddddocr(back, slide)`
- 滑块匹配（OpenCV）：`solve_local_slide_distance(back_base64, slide_base64)`

### 免费能力说明

- 本地方法默认不调用云码接口，不消耗积分。
- 本地识别准确率会受图片质量、字体、噪声和变形影响。
- 本地免费能力可直接通过类方法调用，也支持无 `token` 实例化后调用。
- 建议对本地失败场景自动切换收费接口兜底。

### 免费本地调用示例

```python
from jfbym_api import JfbymClient

# 方式1：直接调用类方法，无需 token
text = JfbymClient.solve_local_text_captcha("captcha.png")

# 方式2：无 token 实例化后调用本地方法
client = JfbymClient()
slide = client.solve_local_slide_distance_ddddocr("back.png", "slide.png")
```

## 收费能力（云码 API）

> 适合复杂验证码或高成功率场景。仅在调用云端接口时需要 `token`。

### 注册与配置

- 注册邀请链接：<https://console.jfbym.com/register/TG133710>
- 调用收费云码接口前，请先配置 token：

```bash
export JFBYM_TOKEN="你的云码token"
```

Windows PowerShell:

```powershell
$env:JFBYM_TOKEN="你的云码token"
```


### 复杂类型说明

价格来源：<https://www.jfbym.com/price.html>（日期：2026-03-12）

| 场景 | 推荐 type | 低至价格 | 推荐接口 | 关键说明 |
|---|---|---|---|---|
| 空间推理点选（无确定按钮） | `50009` | `0.012元` | `solve_common` | 如: 点击侧对着你的字母 |
| 空间推理点选（有确定按钮） | `30340` | `0.01元` | `solve_common` | 如: 点击正方体上面字母的小写字母 |
| 文字点选（通用） | `30100` | `0.01元` | `solve_common` | 按顺序点击需求文字 |
| 推理拼图 | `30108` | `0.008元` | `solve_common` | 交换2个图块 |
| 九宫格点选 | `30008` | `0.01元` | `solve_common` | 9宫格图片验证 |
| 双图滑块（收费兜底） | `20111` | `0.01元` | `solve_slide` | 2个或多个缺口的滑块场景 |
| 轨迹验证/单图滑块优化 | `22222` | `0.008元` | `solve_common` | 轨迹/拖动类场景，返回坐标或偏移相关结果 |
| 单图旋转 | `90007` | `按官网/定制` | `solve_common` | 通用旋转验证码 |
| 双图旋转 | `90004` | `0.01元` | `solve_common` | 内圈, 外圈图片旋转验证 |
| 双图旋转（高频场景） | `90015` | `按官网/定制` | `solve_common` | 返回 `rotate_angle` 和 `slide_px` |
| 问答题 | `50103` | `0.016元` | `solve_common` | 看图问答 |

说明：价格与活动可能随时间变化，最终请以官网实时页面为准。

### 免费 vs 收费能力对比

- 免费本地：更适合基础文本、算术、文本检测、基础滑块距离。
- 收费云码：更适合空间推理、拼图、九宫格、旋转、轨迹验证、问答等复杂类型。
- 实战建议：基础题先免费，复杂类型直接走收费 type，减少重试次数。

### RPA 高频类型与 `extra` 传参说明

- `50009`：空间推理。
- `30100`：根据文字点选。
- `30340`：根据图标点选。
- `90015`：双图旋转（高频场景），返回 `rotate_angle` 与 `slide_px`。

示例：

```python
# 50009: 空间推理点选（无确定按钮）
ret_50009 = client.solve_common(
    image_input=image_b64,
    captcha_type="50009",
    extra="请点击侧对着你的字母",
)

# 30100: 文字点选
ret_30100 = client.solve_common(
    image_input=image_b64,
    captcha_type="30100",
    extra="猫,狗,车",
)

# 30008: 九宫格点选（通过 kwargs 透传附加字段）
ret_30008 = client.solve_common(
    image_input=image_b64,
    captcha_type="30008",
    label_image=label_image_b64,
)
```
#### 90015 双图旋转场景（高频场景）

返回值读取方式：

- 成功判定：`resp["code"] == 10000` 且 `resp["data"]["code"] == 0`
- 结果读取：`data = resp["data"]["data"]`
- 关键字段：`rotate_angle`（优先）和 `slide_px`（兜底）
- 拖动微调：`offset = (rotate_angle if rotate_angle is not None else slide_px) - 30`

原始 `requests` 调用示例：

```python
import requests

url = "https://api.jfbym.com/api/YmServer/customApi"
payload = {
    "token": "YOUR_TOKEN",
    "type": "90015",
    "out_ring_image": out_ring_b64,
    "inner_circle_image": inner_circle_b64,
    "developer_tag": "ce469e48ee0435c34c170ea3d2a1ab0f",
}

resp = requests.post(
    url,
    json=payload,
    headers={"Content-Type": "application/json"},
).json()

if resp.get("code") == 10000 and resp.get("data", {}).get("code") == 0:
    data = resp["data"]["data"]
    rotate_angle = data.get("rotate_angle")
    slide_px = data.get("slide_px")
    offset = (rotate_angle if rotate_angle is not None else slide_px) - 30
    print("rotate_angle=", rotate_angle, "slide_px=", slide_px, "offset=", offset)
else:
    print("solve failed:", resp)
```

使用 Skill 封装（推荐）：

```python
ret = client.solve_common(
    image_input=None,
    out_ring_image=out_ring_b64,
    inner_circle_image=inner_circle_b64,
    captcha_type="90015",
)

rotate_angle = ret.get("data", {}).get("rotate_angle")
slide_px = ret.get("data", {}).get("slide_px")
```

### 收费接口能力

- 单图/点选/计算/空间推理/旋转：`solve_common(image_input=None, captcha_type="...", extra=None, **kwargs)`
- 双图滑块：`solve_slide(slide_image, bg_image, captcha_type="20111", extra=None, **kwargs)`
- 双图旋转（90015）：`solve_common(image_input=None, captcha_type="90015", out_ring_image=..., inner_circle_image=...)`
- ReCaptcha/hCaptcha 异步令牌：`solve_recaptcha(googlekey, pageurl, captcha_type=...)`

## 推荐策略（免费优先，收费兜底）

- 文本验证码：先 `solve_local_text_captcha` 或 `solve_local_text_captcha_with_range`，失败再 `solve_common(..., captcha_type="10110")`
- 算术验证码：先 `solve_local_math_captcha`，失败再 `solve_common(..., captcha_type="50100")`
- 双图滑块：先 `solve_local_slide_distance_ddddocr`，失败再 `solve_local_slide_distance`，最后 `solve_slide(..., captcha_type="20111")`
- 点选、ReCaptcha、hCaptcha 等复杂类型：建议直接走收费云码 API

## 自动策略接口（详细说明）

为降低调用方复杂度，`jfbym_api.py` 提供统一自动接口：

- `solve_auto_fallback(task, image_input=None, back_image_input=None, slide_image_input=None, charset_range=None, paid_captcha_type=None, extra=None, prefer="free")`

### 参数说明

- `task`: 必填。支持 `text` / `math` / `slide`。
- `image_input`: `text`、`math` 任务必填。支持文件路径、`bytes`、base64 字符串。
- `back_image_input`、`slide_image_input`: `slide` 任务必填。支持文件路径、`bytes`、base64 字符串。
- `charset_range`: 文本任务可选。设置 ddddocr 字符集约束（如纯数字 `0123456789`）。
- `paid_captcha_type`: 可选。收费兜底时覆盖默认 type。默认：`text=10110`、`math=50100`、`slide=20111`。
- `extra`: 可选。透传给收费 `solve_common`（点选类等场景可用）。
- `prefer`: 可选。`free`（默认，先免费后收费）或 `paid`（先收费后免费）。
- 未配置 `token` 时，`solve_auto_fallback` 仍可执行免费分支；只有进入收费分支时才会报错。

### 返回结构

成功时返回结构：

```python
{
  "task": "text|math|slide",
  "mode": "free|paid",      # 实际成功通道
  "result": ... ,             # 对应通道的原始结果
  "fallback_reason": "..."   # 仅在发生降级/兜底时存在
}
```

### 使用示例

```python
from jfbym_api import JfbymClient

client = JfbymClient()  # 如需收费兜底，请先配置 JFBYM_TOKEN

# 1) 文本验证码：默认免费优先
text_result = client.solve_auto_fallback(
    task="text",
    image_input="captcha.png",
    charset_range="0123456789",
)

# 2) 算术验证码：免费失败后自动走收费 type=50100
math_result = client.solve_auto_fallback(
    task="math",
    image_input="math.png",
)

# 3) 双图滑块：先 ddddocr，再 OpenCV，最后收费 type=20111
slide_result = client.solve_auto_fallback(
    task="slide",
    back_image_input=back_img_base64,
    slide_image_input=slide_img_base64,
)
```

## 识别结果输出（逐接口说明）

结果结构目前不是强制统一的，调用时建议按具体方法解析。下面逐个说明。

### 免费本地接口返回

- `solve_local_text_captcha(...)`：返回 `str`，示例：`"a7k9"`。
- `solve_local_text_captcha_with_range(...)`：返回 `str`，示例：`"4821"`。
- `solve_local_math_captcha(...)`：返回 `dict`，固定字段：`raw_text`、`expression`、`result`。
- `detect_local_text_boxes(...)`：返回 `list`，为文本框坐标列表（具体坐标格式随 ddddocr 版本可能略有差异）。
- `solve_local_slide_distance_ddddocr(...)`：返回 `dict`，固定字段：`x`、`y`、`target`、`raw`。
- `solve_local_slide_distance(...)`：返回 `int`，表示滑块 X 方向偏移量。

示例：

```python
math_ret = {
    "raw_text": "8+6=?",
    "expression": "8+6",
    "result": "14",
}

slide_ret = {
    "x": 120,
    "y": 38,
    "target": [120, 38, 168, 86],
    "raw": {...},
}
```

### 收费云码接口返回

- `solve_common(...)`：返回 `dict`，内容为云码接口 `data` 原样返回，不同 `captcha_type` 字段可能不同。
- `solve_slide(...)`：返回 `dict`，内容为云码接口 `data` 原样返回。
- `solve_recaptcha(...)`：返回 `str`，为可直接提交的 token（如 `g-recaptcha-response`）。
- `90015` 双图旋转建议读取：`ret.get("data", {}).get("rotate_angle")`，如为空可回退读取 `slide_px`。
- `get_balance()`：返回 `str`，当前账户积分余额。
- `report_error(record_id)`：返回 `bool`，是否退款成功。
- `guess_captcha_type(description)`：返回 `str`，推荐的云码 `type` 编号。

建议：

- 对 `solve_common`、`solve_slide` 统一先读取 `ret.get("data")` 作为主结果。
- 其余附加字段按实际业务按需读取，不要在文档中写死固定结构。

### 自动策略接口返回细化

`solve_auto_fallback(...)` 外层固定返回：

```python
{
  "task": "text|math|slide",
  "mode": "free|paid",
  "result": ...,
  "fallback_reason": "..."  # 发生兜底时才有
}
```

其中 `result` 随 `task + mode` 变化：

- `text + free`：`str`
- `text + paid`：`dict`（云码 `data`）
- `math + free`：`dict`（`raw_text/expression/result`）
- `math + paid`：`dict`（云码 `data`）
- `slide + free`：`dict`，包含 `engine`（`ddddocr` 或 `opencv`）与 `x`，`ddddocr` 场景还会包含 `y/target/raw`
- `slide + paid`：`dict`（云码 `data`）

## 快速示例
```python
from jfbym_api import JfbymClient

# 免费本地优先
try:
    text = JfbymClient.solve_local_text_captcha_with_range("captcha.png", charset_range="0123456789")
except Exception:
    # 收费兜底
    client = JfbymClient()
    text = client.solve_common("captcha.png", captcha_type="10110")["data"]

print(text)
```

## 开源致谢

本 Skill 的本地免费能力基于开源项目 [ddddocr](https://github.com/sml2h3/ddddocr) 构建，感谢作者与社区贡献。

## 依赖安装

```bash
pip install -r requirements.txt
```

## 项目结构

```text
jfbym-captcha-skill/
└── skill/
    ├── SKILL.md
    ├── requirements.txt
    └── jfbym_api.py
```
