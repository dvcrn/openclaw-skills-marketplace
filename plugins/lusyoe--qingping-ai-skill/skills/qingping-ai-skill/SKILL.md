---
name: qingping-ai-skill
description: "青萍 AI 图片生成工具。通过 API 生成高质量图片并自动下载到本地。使用场景：(1) 用户需要生成 AI 图片，(2) 提到\"青萍\"、\"qingping\"、\"生成图片\"、\"AI生图\"等关键词，(3) 需要快速生成设计素材或创意图片。支持多种模型、尺寸和比例配置。"
homepage: https://auth.lusyoe.com/profile
---

# 青萍 AI 图片生成

通过青萍 AI API 生成高质量图片并自动下载到本地 `qingping-ai` 目录。

## 环境配置

首次使用前需要配置 API Key：

```bash
# 临时配置（当前终端会话）
export QINGPING_API_KEY='your-api-key-here'

# 永久配置（添加到 shell 配置文件）
echo 'export QINGPING_API_KEY="your-api-key-here"' >> ~/.zshrc
source ~/.zshrc
```

**获取 API Key**：
1. 登录青萍AI平台：https://auth.lusyoe.com/profile
2. 在个人信息页面，滚动到最下面
3. 点击生成或查看 API Key

如果未配置 API Key，脚本会提示用户进行配置。

## 快速开始

使用脚本生成图片：

```bash
# 基础用法（使用默认模型 nano-banana）
python scripts/generate_image.py "一只可爱的金鱼"

# 指定模型
python scripts/generate_image.py "一只可爱的金鱼" nano-banana-2

# 完整参数
python scripts/generate_image.py "提示词" [模型] [数量] [比例] [尺寸]

# 示例
python scripts/generate_image.py "一只可爱的小狗" nano-banana-2 1 1:1 1K
python scripts/generate_image.py "夕阳下的海滩" nano-banana-pro 1 16:9 2K
```

## 工作流程

1. **检查环境变量**：验证 `QINGPING_API_KEY` 是否配置
2. **提交任务**：POST 请求创建生成任务，获取 `task_id`
3. **轮询状态**：每 5 秒查询一次任务状态，打印详细日志，直到完成或失败
4. **下载图片**：任务完成后，自动下载生成的图片到 `qingping-ai/` 目录

## 并发限制

**重要限制**：
- ✅ **并发数为 1**：同一时间只能运行一个图片生成任务
- ✅ **顺序执行**：当一个任务未完成时，不要创建新的任务
- ✅ **等待完成**：必须等待当前任务完成（成功或失败）后，才能创建下一个任务

**原因**：
- 保证任务执行的稳定性
- 避免资源竞争和冲突
- 确保每个任务都能得到充分的系统资源

**使用建议**：
```bash
# 正确用法：等待任务完成后再创建新任务
python scripts/generate_image.py "第一张图片"
# 等待完成后再运行下一个
python scripts/generate_image.py "第二张图片"

# 错误用法：同时运行多个任务（不推荐）
python scripts/generate_image.py "图片1" &
python scripts/generate_image.py "图片2" &  # 不推荐
```

## 参数说明

| 参数 | 默认值 | 说明 |
|------|--------|------|
| prompt | 必填 | 图片描述提示词 |
| model | `nano-banana` | 模型名称（见下方模型列表） |
| count | `1` | 生成数量 |
| ratio | `1:1` | 图片比例（见下方比例列表） |
| size | `1K` | 图片尺寸（见下方尺寸列表） |
| tags | `[""]` | 自定义标签 |

**注意**: 分类固定为"青萍Claw"，无需用户指定。

## 支持的模型

| 模型名称 | 说明 |
|---------|------|
| `nano-banana` | 默认模型，快速生成 |
| `nano-banana-2` | 增强版本，更高质量 |
| `nano-banana-pro` | 专业版本，最佳质量 |

## 支持的比例

| 比例 | 说明 |
|------|------|
| `1:1` | 默认，正方形 |
| `16:9` | 横屏，适合桌面壁纸 |
| `9:16` | 竖屏，适合手机壁纸 |

## 支持的尺寸

| 尺寸 | 说明 |
|------|------|
| `1K` | 默认，1024px |
| `2K` | 2048px，更高质量 |
| `4K` | 4096px，最高质量 |

**使用示例**：

```bash
# 使用默认参数（nano-banana, 1:1, 1K）
python scripts/generate_image.py "一只可爱的金鱼"

# 指定模型
python scripts/generate_image.py "一只可爱的金鱼" nano-banana-2

# 指定模型和比例
python scripts/generate_image.py "夕阳下的海滩" nano-banana-pro 1 16:9

# 完整参数
python scripts/generate_image.py "手机壁纸" nano-banana 1 9:16 4K
```

## 输出示例

```
📤 提交生成任务...
   提示词: 一只可爱的金鱼
   模型: nano-banana
   尺寸: 1K, 比例: 1:1
✅ 任务已提交
   任务ID: e5e363b6-78ed-441f-88ed-73cfeca0971f

⏳ 开始轮询任务状态...

   [1] 轮询结果:
   状态: pending, 已等待: 5 秒
   完整响应: {
     "task_id": "e5e363b6-78ed-441f-88ed-73cfeca0971f",
     "status": "pending",
     "generated_image_urls": null,
     "error": null,
     "prompt": "一只可爱的金鱼",
     "model": "nano-banana",
     "size": "1K",
     "ratio": "1:1",
     "count": 1,
     "image_urls": null,
     "category": "青萍Claw",
     "tags": "[]",
     "created_at": "2026-03-14T08:00:00",
     "completed_at": null
   }

   [2] 轮询结果:
   状态: processing, 已等待: 10 秒
   完整响应: {
     "task_id": "e5e363b6-78ed-441f-88ed-73cfeca0971f",
     "status": "processing",
     "generated_image_urls": null,
     "error": null,
     "prompt": "一只可爱的金鱼",
     "model": "nano-banana",
     "size": "1K",
     "ratio": "1:1",
     "count": 1,
     "image_urls": null,
     "category": "青萍Claw",
     "tags": "[]",
     "created_at": "2026-03-14T08:00:00",
     "completed_at": null
   }

   [3] 轮询结果:
   状态: processing, 已等待: 15 秒
   完整响应: {
     "task_id": "e5e363b6-78ed-441f-88ed-73cfeca0971f",
     "status": "processing",
     "generated_image_urls": null,
     "error": null,
     "prompt": "一只可爱的金鱼",
     "model": "nano-banana",
     "size": "1K",
     "ratio": "1:1",
     "count": 1,
     "image_urls": null,
     "category": "青萍Claw",
     "tags": "[]",
     "created_at": "2026-03-14T08:00:00",
     "completed_at": null
   }

✅ 任务完成!
   轮询次数: 3
   总耗时: 15 秒

📋 图片信息:
   [1] 名称: zc0d3kgp3bfw
       链接: https://img-cdn.lusyoe.cn/images/test/2026/03/14/zc0d3kgp3bfw.png

📥 下载图片...
   URL: https://img-cdn.lusyoe.cn/images/test/2026/03/14/zc0d3kgp3bfw.png
   保存到: qingping-ai/zc0d3kgp3bfw.png
✅ 下载完成!

🎉 完成! 共下载 1 张图片到 /path/to/qingping-ai/

💡 提示: 可到青萍AI图床查看和管理图片
   地址: https://img.lusyoe.com
```

## 错误处理

- **未配置 API Key**: 提示配置步骤和获取方式
- **不支持的模型**: 显示支持的模型列表
- **不支持的比例**: 显示支持的比例列表
- **不支持的尺寸**: 显示支持的尺寸列表
- **API 请求失败**: 显示详细错误信息
- **任务失败**: 显示错误原因
- **下载失败**: 显示下载错误详情

## 版本更新

### v1.0.2 (2026-03-14)

- 移除 API 端点说明，端点已内置在脚本中
- 简化文档结构，用户无需关心底层端点配置

### v1.0.1

- 初始版本
- 支持基础图片生成功能
- 支持多种模型、尺寸和比例配置
- 自动下载生成的图片到本地
