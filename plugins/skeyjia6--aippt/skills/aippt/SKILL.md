---
name: aippt
description: "这是一个自动为用户生成 PPT 演示文稿的技能，用户只需要输入演示文稿的标题和内容，技能就会自动为用户生成一个 PPT 演示文稿。触发词：自动生成一份PPT、生成一份PPT、创建一份PPT、自动创建一份PPT、生成一个PPT、创建一个PPT、自动生成PPT、自动创建PPT。"
---

# 自动生成 PPT 演示文稿技能

- **接口文档：** [aippt 文档](scripts/README.md)

- **AIPPT_ACCESS_TOKEN**：从[官方网站](https://www.7niuai.com/)，个人中心中获取。

## 环境变量设置
**AIPPT_ACCESS_TOKEN** 
1. 当下面的 `AIPPT_ACCESS_TOKEN` 为空时，需要从官方网站，个人中心中获取。
2. 当下面的 `AIPPT_ACCESS_TOKEN` 是 "your-actual-access-token" 时，需要用户从官方网站，个人中心中获取。
3. 当下面的 `AIPPT_ACCESS_TOKEN` 是其他值时，直接使用该值。
```bash
export AIPPT_ACCESS_TOKEN="your-actual-access-token"
```

## 生成流程

### Step 1：生成Markdown内容
1. 对用户的内容仔细分析，并生成最终的Markdown内容。
2. Markdown结构如下：
```
# 标题
> 标题说明
## 章节标题
> 章节标题说明
### 小节标题
> 小节标题说明
- 内容项标题：内容项内容
```
3. **用户确认Markdown内容**：需要用户确认生成的Markdown内容是否符合要求。

#### 大纲要求
- **{# 标题}** 不能为空。
- **{> 标题说明}** 可以为空。
- **{## 章节标题}** 不能超过 8 个。
- **{> 章节标题说明}** 可以为空。
- **{### 小节标题}** 不能为空。
- **{> 小节标题说明}** 可以为空。
- **{内容项标题}**不能为空。
- **{内容项内容}** 不能为空。
- **{内容项标题：内容项内容}个数限制**：每个小节下最少有 1 个内容项，最多可以有 5 个内容项，但不能超过 6 个。

## Step 2：选择一个模板
**模板规则**：模板每页数量为 10 个，可以通过 `--page` 参数指定页码，默认值为 1。
**调用脚本:** `get_tpl_list.py` 获取可用的 PPT 模板。
```bash
python3 get_tpl_list.py --page=$page --num=10
```
### 列表展示
- **展示字段**：序号、模板名称、热度、预览图片。
- **预览图片**：使用 picture 字段，示例：[预览](https://ppt-img.7niuai.com/73542801a25c926cf226c6634d664006/ab762d5f49b8a3386f032dcbfd9043d_picture.jpg)。
- **图片链接**：保证图片链接的完整性。
- **点击预览**：点击预览图片，会在浏览器中打开预览页面。
| 序号 | 模板名称 |热度| 预览 |
| --- | --- | --- | --- |
| 1 | 模板1 | 100 | [预览](https://ppt-img.7niuai.com/73542801a25c926cf226c6634d664006/ab762d5f49b8a3386f032dcbfd9043d_picture.jpg) |

### 注意事项
- **模板ID**：长度32位，保持模板ID的完整性。
- **图片链接**：保证图片链接的完整性，避免链接失效导致预览失败。
- **图片链接格式**：图片链接格式为 `https://ppt-img.7niuai.com/{32位字符串}/{32位字符串}_picture.jpg`。

## Step 3：获取PPT的下载链接
**调用脚本：** `generate_by_content.py` 获取PPT的下载链接。
```bash
python3 generate_by_content.py --tpl_id=$tpl_id --markdown_content="Markdown内容"
```

### 注意事项
- **检查Markdown内容是否符合要求**：确保Markdown内容符合要求，否则会导致生成失败。
- **{tpl_id}** 是模版ID，不能为空。
- **链接：** 需要对链接进行URLENCODE编码。
- **不要为用户直接打开浏览器**：用户需要手动点击链接，打开浏览器。
- **链接显示：** 链接以Markdown格式呈现，用户需要手动点击链接。
- **链接完整性**：
1. 链接示例：https://7niuai.com/preview-in-ai/ed4d5e71ff632cfef4e6e5d97807e7e6?title=%E8%84%91%E6%9C%BA%E6%8E%A5%E5%8F%A3%E6%8A%80%E6%9C%AF&tplid=b308ae8fa5550166065b695782c3a5da
2. 链接中的 preview-in-ai/ed4d5e71ff632cfef4e6e5d97807e7e6 中的 ed4d5e71ff632cfef4e6e5d97807e7e6 是一个32位的字符串。
3. 链接中的 tplid=b308ae8fa5550166065b695782c3a5da 中的 b308ae8fa5550166065b695782c3a5da 是一个32位的字符串。