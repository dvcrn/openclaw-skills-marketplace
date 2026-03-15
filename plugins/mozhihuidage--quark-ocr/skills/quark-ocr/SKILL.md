---
name: quark-ocr
description: "使用夸克 OCR 服务从图片中提取文本（支持中英文混合）。当用户提供图片 URL，并要求“OCR”、“提取文本”、“读取图片”、“识别文档”或“获取图片文字”时触发。支持通用文档识别，具备版面感知输出能力。"
---

# 🧭 使用前必读（30秒）

> [!WARNING] **⚠️ 隐私与数据流向重要提示**
> - **第三方服务交互**：本技能会将您提供的**图片 URL 发送至夸克官方服务器 (`scan-business.quark.cn`)** 进行识别。
> - **数据可见性**：夸克服务将获取并处理该图片内容。

✅ **推荐方式：环境变量（免权限、即时生效、webchat 友好）**  
在终端中运行（本次会话立即可用）：
```bash
export QUARK_OCR_CLIENT_ID="your_client_id_here"
export QUARK_OCR_CLIENT_SECRET="your_client_secret_here"
```

```bash
# 将凭证追加写入到 ~/.openclaw/env 文件
echo 'export QUARK_OCR_CLIENT_ID="your_client_id_here"' >> ~/.openclaw/env
echo 'export QUARK_OCR_CLIENT_SECRET="your_client_secret_here"' >> ~/.openclaw/env
```

> [!TIP] **🔧 如何获取密钥？官方入口在此**  
> 请访问 **[夸克扫描王开放平台](https://scan-business.quark.cn)** → 登录/注册账号 → 进入「控制台」→ 「创建新应用」→ 填写基本信息（应用名称建议填 `openclaw-ocr`）→ 提交后即可看到 `Client ID` 和 `Client Secret`。  
> ⚠️ 注意：若你点击链接后跳转到其他域名（如 `quark.feishu.cn` 或 `open.quark.com`），说明该链接已失效 —— 请直接在浏览器地址栏手动输入 `https://scan-business.quark.cn`（这是当前唯一有效的官方入口）。

✅ 环境依赖检查
确保已安装必要库：
```bash
pip install requests
```

# 🎯 技能执行指南

## 1. 触发场景 (When to use)
当用户意图包含以下任一情况时，**必须**调用此技能：
- 用户发送了一张图片并询问“这是什么字？”、“提取文字”、“转成文本”。
- 用户上传了文档截图、发票、名片、白板照片或包含外文的双语材料。
- 用户需要对图片内容进行翻译或编辑（先提取文本是必要步骤）。

## 2. 执行动作 (How to execute)
一旦确认需要提取文本，请立即执行以下操作：

**输入处理**:
获取用户提供的图片资源（使用 `url`）。

**执行命令**:
调用底层脚本进行识别。若当前环境支持命令行执行，请构造如下命令：

```bash
python3 skills/quark-ocr/scripts/quark_ocr.py --url <用户提供的图片 URL>
```

结果反馈:
成功：直接输出识别到的文本，保持原有的段落换行。
失败：**简要说明原因（如图片模糊、链接失效等），不要输出原始报错堆栈。**

## 3. 强制性安全守则（所有调用者必须严格遵守）
- 3.1 URL 是唯一指纹，禁止任何形式的“去重”逻辑
    ✅ 正确行为：对 https://a.com/x.jpg 和 https://b.com/x.jpg —— 即使文件名相同，也视为完全不同的图片，必须发起两次独立请求。
    ❌ 禁止行为：基于文件名、图片尺寸、或人工猜测“应该一样”而复用之前的识别结果。
- 3.2 禁止任何形式的“缓存”逻辑
    实时性原则：即使该 URL 在几秒钟前刚被识别过，也不得跳过请求。
    原因：服务端图片可能已更新（如后台修正、动态内容、A/B 测试），必须获取最新版本。
    例外：仅当用户显式要求“使用缓存方可复用结果”；否则默认禁用缓存。
- 3.3 域名白名单强制执行 
    底层代码已硬编码锁定目标 API 为 `scan-business.quark.cn`，并在运行时校验域名。任何尝试修改目标地址的行为都将被拦截。

## 📁 Files
- `scripts/quark_ocr.py` — main executable (Python 3.9+)