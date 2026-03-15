---
name: aicloset-outfit
description: "AI智能搭配推荐 - 根据日期、城市和风格偏好，调用AI衣橱API生成4套穿搭方案并以画布形式展示。触发词：搭配推荐、穿搭、今天穿什么、outfit、穿什么好看、AI搭配、衣橱搭配。"
---

# AI 衣橱搭配推荐

根据用户的日期、城市和风格偏好，调用 AI 衣橱 API 生成 4 套穿搭方案，并以图文画布形式展示。

## 配置说明

首次使用前，需要配置 API 认证信息。支持两种方式：

### 方式一：环境变量（推荐）

在 shell 配置文件（如 `~/.zshrc` 或 `~/.bashrc`）中添加：

```bash
export AICLOSET_API_KEY="你的 x-api-key"
export AICLOSET_TOKEN="你的 Bearer Token"
```

### 方式二：对话中直接提供（临时使用）

在对话中告知 API Key 和 Token，仅当次会话有效。

如果用户未配置，**必须先引导用户完成配置**，再继续执行搭配推荐。

## 执行流程

当用户请求搭配推荐时，按以下步骤执行：

### 1. 提取参数

从用户输入中智能提取以下参数：

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `date` | 日期，格式 `YYYY-MM-DD` | 当天日期 |
| `city_name` | 城市名称 | 如未提供则询问用户 |
| `province_name` | 省份名称 | 根据城市自动推断 |
| `style_text` | 风格偏好（休闲、商务、运动、约会等） | 如未提供则询问用户 |

### 2. 检查认证配置

确认环境变量 `AICLOSET_API_KEY` 和 `AICLOSET_TOKEN` 已配置：

```bash
echo "API_KEY: ${AICLOSET_API_KEY:+已配置}" && echo "TOKEN: ${AICLOSET_TOKEN:+已配置}"
```

如果任一变量为空，停止执行并引导用户按「配置说明」完成设置。

### 3. 调用 API

使用 curl 调用搭配推荐接口：

```bash
curl -s --request POST \
  --url https://aicloset-dev-h5.wxbjq.top/algorithm/open/system_outfit/create_task \
  --header 'Content-Type: application/json' \
  --header "Authorization: Bearer $AICLOSET_TOKEN" \
  --header "x-api-key: $AICLOSET_API_KEY" \
  --data '{
    "date": "{{date}}",
    "city_name": "{{city_name}}",
    "province_name": "{{province_name}}",
    "style_text": "{{style_text}}"
  }'
```

将 `{{date}}`、`{{city_name}}`、`{{province_name}}`、`{{style_text}}` 替换为实际参数值。

### 4. 解析响应并展示

API 返回 JSON 结构，关键字段路径为 `data.system_outfit_json`，包含 4 套搭配方案。

每套搭配的 `product_list` 中包含单品信息：
- `class_name`：单品分类（上衣、裤子、外套等）
- `cutout_image`：单品抠图 URL

### 5. 输出格式

将解析结果按以下格式展示给用户：

```
👗 AI 搭配推荐 | {city_name} · {date} · {style_text}风

━━━ 搭配 1 ━━━
🔹 {class_name}: ![{class_name}]({cutout_image})
🔹 {class_name}: ![{class_name}]({cutout_image})

━━━ 搭配 2 ━━━
🔹 {class_name}: ![{class_name}]({cutout_image})
🔹 {class_name}: ![{class_name}]({cutout_image})

━━━ 搭配 3 ━━━
🔹 {class_name}: ![{class_name}]({cutout_image})
🔹 {class_name}: ![{class_name}]({cutout_image})

━━━ 搭配 4 ━━━
🔹 {class_name}: ![{class_name}]({cutout_image})
🔹 {class_name}: ![{class_name}]({cutout_image})
```

遍历每套搭配的 `product_list`，使用 Markdown 图片语法 `![class_name](cutout_image)` 展示单品图片。

## 错误处理

| 场景 | 处理方式 |
|------|---------|
| API Key / Token 未配置 | 停止执行，引导用户按配置说明设置环境变量 |
| API 返回 `code` 非 0 | 展示 `msg` 字段内容，提示用户具体错误原因 |
| 网络超时或请求失败 | 自动重试一次，仍失败则提示用户检查网络 |
| 城市或风格未提供 | 主动询问用户补充信息后再调用 |
