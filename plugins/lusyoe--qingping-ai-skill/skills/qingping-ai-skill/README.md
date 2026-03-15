# 青萍 AI 图片生成技能

通过青萍 AI API 生成高质量图片并自动下载到本地。

## 项目信息

- **作者**: lusyoe
- **主页**: https://auth.lusyoe.com/profile
- **许可证**: MIT License
- **API 端点**: https://video.lusyoe.com
- **图片 CDN**: https://img-cdn.lusyoe.cn 或 https://img-cdn.lusyoe.com

## 安全说明

- 本技能仅使用 HTTPS 加密通信
- 图片下载到本地 `qingping-ai/` 目录
- 不读取或上传本地其他文件
- API Key 仅用于认证图片生成请求

## 功能特性

- ✅ **多模型支持**：nano-banana、nano-banana-2、nano-banana-pro
- ✅ **多尺寸支持**：1K、2K、4K
- ✅ **多比例支持**：1:1、16:9、9:16
- ✅ **自动下载**：生成的图片自动下载到本地 `qingping-ai` 目录
- ✅ **详细日志**：每次轮询都打印状态和已等待时间
- ✅ **并发限制**：同一时间只能运行一个任务，避免资源竞争
- ✅ **完善验证**：所有参数自动验证，错误提示友好
- ✅ **零依赖**：仅使用 Python 标准库，无需安装第三方包

## 快速开始

### 1. 配置 API Key

```bash
# 临时配置
export QINGPING_API_KEY='your-api-key-here'

# 永久配置
echo 'export QINGPING_API_KEY="your-api-key-here"' >> ~/.zshrc
source ~/.zshrc
```

**获取 API Key**：https://auth.lusyoe.com/profile

### 2. 生成图片

```bash
# 基础用法（使用默认参数）
python scripts/generate_image.py "一只可爱的金鱼"

# 指定模型
python scripts/generate_image.py "一只可爱的金鱼" nano-banana-2

# 指定模型、比例和尺寸
python scripts/generate_image.py "夕阳下的海滩" nano-banana-pro 1 16:9 2K

# 手机壁纸（竖屏）
python scripts/generate_image.py "手机壁纸" nano-banana 1 9:16 4K
```

## 支持的参数

### 模型

| 模型 | 说明 |
|------|------|
| `nano-banana` | 默认模型，快速生成 |
| `nano-banana-2` | 增强版本，更高质量 |
| `nano-banana-pro` | 专业版本，最佳质量 |

### 比例

| 比例 | 说明 |
|------|------|
| `1:1` | 默认，正方形 |
| `16:9` | 横屏，适合桌面壁纸 |
| `9:16` | 竖屏，适合手机壁纸 |

### 尺寸

| 尺寸 | 说明 |
|------|------|
| `1K` | 默认，1024px |
| `2K` | 2048px，更高质量 |
| `4K` | 4096px，最高质量 |

## 完整参数说明

```python
generate_image(
    prompt="图片描述",           # 必填：图片描述提示词
    model="nano-banana",        # 可选：模型名称，默认 nano-banana
    count=1,                    # 可选：生成数量，默认 1
    ratio="1:1",                # 可选：图片比例，默认 1:1
    size="1K",                  # 可选：图片尺寸，默认 1K
    tags=[""]                   # 可选：自定义标签
)
```

**注意**: 分类固定为"青萍Claw"，无需用户指定。

## 使用示例

### 命令行使用

```bash
# 生成正方形图片（默认 1:1, 1K）
python scripts/generate_image.py "一只可爱的橙色小金鱼"

# 生成横屏壁纸（16:9, 2K）
python scripts/generate_image.py "夕阳下的海滩，金色的阳光洒在海面上" nano-banana-pro 1 16:9 2K

# 生成手机壁纸（9:16, 4K）
python scripts/generate_image.py "星空下的城市夜景" nano-banana-2 1 9:16 4K
```

### Python 代码使用

```python
from scripts.generate_image import generate_image

# 基础用法
paths = generate_image(prompt="一只可爱的金鱼")

# 完整参数
paths = generate_image(
    prompt="夕阳下的海滩",
    model="nano-banana-pro",
    count=1,
    ratio="16:9",
    size="2K",
    category="青萍 Claw",
    tags=["风景", "海滩"]
)

print(f"图片已保存到: {paths}")
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

✅ 任务完成!
   轮询次数: 2
   总耗时: 10 秒

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

### 未配置 API Key

```
❌ 错误: 未找到环境变量 QINGPING_API_KEY

======================================================================
🔑 获取 API Key 步骤：
======================================================================

1. 登录青萍AI平台:
   https://auth.lusyoe.com/profile

2. 在个人信息页面，滚动到最下面

3. 点击生成或查看 API Key

======================================================================
⚙️  配置环境变量：
======================================================================

方法一: 临时配置（仅当前终端会话有效）
   export QINGPING_API_KEY='your-api-key-here'

方法二: 永久配置（推荐）
   # 添加到 ~/.zshrc (macOS 默认) 或 ~/.bashrc (Linux)
   echo 'export QINGPING_API_KEY="your-api-key-here"' >> ~/.zshrc
   source ~/.zshrc
```

### 不支持的参数

```bash
# 无效模型
❌ 错误: 不支持的模型 'invalid-model'
支持的模型:
   - nano-banana (默认)
   - nano-banana-2
   - nano-banana-pro

# 无效比例
❌ 错误: 不支持的比例 '4:3'
支持的比例:
   - 1:1 (默认)
   - 16:9
   - 9:16

# 无效尺寸
❌ 错误: 不支持的尺寸 '8K'
支持的尺寸:
   - 1K (默认)
   - 2K
   - 4K
```

## API 端点

- **创建任务**: `POST https://video.lusyoe.com/api/img/generations`
- **查询状态**: `GET https://video.lusyoe.com/api/img/generations/{task_id}/status`

## 相关链接

- **青萍AI平台**: https://auth.lusyoe.com/profile
- **获取API Key**: https://auth.lusyoe.com/profile

## 系统要求

- Python 3.6+
- 无需安装第三方依赖（仅使用标准库）

## 许可证

MIT License

## 技术支持

如有问题，请访问青萍AI平台获取帮助。
