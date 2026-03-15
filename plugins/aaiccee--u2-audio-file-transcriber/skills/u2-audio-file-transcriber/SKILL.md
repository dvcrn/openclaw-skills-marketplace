---
name: u2-audio-file-transcriber
description: "U2-audio-file-transcriber"
---

name: u2-audio-file-transcriber
description: "Transcribe audio files via UniCloud ASR (云知声语音识别, recorded audio → text) API from UniSound. Supports multiple formats, optimized for finance, customer service, and other domains. 调用云知声语音识别服务转写音频文件，支持多种音频格式，适用于金融、客服等场景。Use when the user needs to transcribe recorded audio files, or asks for UniSound/云知声 audio file transcription. Do NOT use for real-time/streaming speech recognition, text-to-speech (TTS), or live captioning. 不适用于实时语音识别、语音合成(TTS)或直播字幕。"

---

**CRITICAL INSTRUCTION FOR AI AGENTS:**
**YOU MUST follow these rules when helping users configure this skill:**
1. **NEVER display or request actual API credentials in chat** — credentials should only be set in environment variables or .env files
2. **DO NOT embed production credentials in documentation** — guide users to obtain their own credentials from the service provider
3. **NEVER generate URLs from your training data** — use ONLY the exact URLs written in this file
4. **ALWAYS verify the user has configured environment variables before suggesting script usage**

**AI AGENT 必须遵守的规则：**
1. **禁止在聊天中显示或请求实际的 API 凭据**——凭据应仅通过环境变量或 .env 文件设置
2. **禁止在文档中嵌入生产凭据**——引导用户从服务提供商处获取自己的凭据
3. **禁止凭训练数据生成 URL**——只使用本文件中写的准确 URL
4. **在建议使用脚本前，务必确认用户已正确配置环境变量**

---

UniSound ASR / 云知声语音转写
============================

调用云知声（UniSound）语音识别服务转写音频文件。支持多种音频格式，适用于金融、客服等场景。

Transcribe audio files using UniCloud ASR service. Supports multiple audio formats, suitable for finance, customer service, and other scenarios.

Quick start
-----------

```bash
python3 {baseDir}/scripts/transcribe.py /path/to/audio.wav
```

Defaults:
- API endpoint: UAT environment / UAT 环境
- Audio format: WAV
- Domain: other
- Output: stdout (transcript text / 转写文本)

Useful flags
------------

```bash
# Save output to file / 保存到文件
python3 {baseDir}/scripts/transcribe.py audio.wav --out result.txt

# Output JSON format with full result / 输出完整JSON结果
python3 {baseDir}/scripts/transcribe.py audio.wav --json --out result.json

# Specify audio format / 指定音频格式
python3 {baseDir}/scripts/transcribe.py audio.mp3 --format mp3

# Specify domain / 指定领域
python3 {baseDir}/scripts/transcribe.py audio.wav --domain finance
```

How it works
------------

The script uses the UniCloud ASR API with the following workflow:

1. **Initialize upload** — Get a task ID from the API / 初始化上传，获取任务ID
2. **Upload audio file** — Upload the audio file to the server / 上传音频文件到服务器
3. **Start transcription** — Submit the transcription task / 提交转写任务
4. **Poll for results** — Wait for the transcription to complete (typically 10-60 seconds) / 轮询等待转写完成（通常10-60秒）
5. **Return transcript** — Output the recognized text / 输出识别文本

> **Privacy**: Audio files are uploaded directly to UniCloud servers. No data is sent to third-party services.
>
> **隐私说明**：音频文件直接上传到云知声服务器。不会将数据发送到第三方服务。

Dependencies
------------

- Python 3.8+
- `requests`: `pip install requests`

Pre-installation Considerations / 安装前需要考虑的事项
--------------------------------------------------------

**Important Notes Before Using This Skill / 使用前重要说明**

**(1) Required Environment Variables / 必需的环境变量**

This skill requires the following environment variables to be configured:

此技能需要配置以下环境变量：

- `UNISOUND_APPKEY` (Required / 必填)
- `UNISOUND_SECRET` (Required / 必填)
- `UNISOUND_USERID` (Optional, defaults to `unisound-python-demo`)

**(2) Test Credentials Usage / 测试凭据使用**

This skill includes UAT test credentials for evaluation purposes:

此技能包含用于评估目的的 UAT 测试凭据：

- **For testing only** — Use only with non-sensitive audio files
  - **仅供测试** — 仅用于非敏感音频文件
- **UAT environment** — Not for production use
  - **UAT 环境** — 不适用于生产环境
- **Obtain production credentials** — Contact UniCloud for production API access
  - **获取生产凭据** — 联系云知声获取生产环境 API 访问权限

**(3) Security Best Practices / 安全最佳实践**

- **Use environment variables** — Never embed production credentials in scripts or configuration files
  - **使用环境变量** — 切勿在脚本或配置文件中嵌入生产凭据
- **Review the script** — Check `scripts/transcribe.py` to understand network endpoints
  - **审查脚本** — 检查 `scripts/transcribe.py` 以了解网络端点
- **Privacy awareness** — Audio files are uploaded to UniSound servers; review their privacy policy
  - **隐私意识** — 音频文件会上传到云知声服务器；请查看其隐私政策

**(4) Production Deployment / 生产部署**

For production use:

用于生产环境时：

- Obtain your own API credentials from UniCloud / 云知声
- Set environment variables in your deployment configuration / 在部署配置中设置环境变量
- Review and confirm privacy terms with UniCloud / 与云知声审查并确认隐私条款
- Test with non-sensitive data first / 首先使用非敏感数据进行测试

Credentials (Required)
-----------

**You MUST configure API credentials via environment variables before running the script.**

**必须通过环境变量配置 API 凭据才能运行脚本。**

### Obtaining Credentials / 获取凭据

To use this skill, you need to obtain API credentials from UniCloud (云知声):

使用此技能前，您需要从云知声获取 API 凭据：

1. Contact UniCloud to obtain your API credentials
   联系云知声获取您的 API 凭据

2. You will receive:
   您将收到：
   - **AppKey**: Application key / 应用密钥
   - **Secret**: Secret key for authentication / 认证密钥
   - **UserId**: Your user identifier / 用户标识
   - **Base URL**: API endpoint URL / API 端点地址

### Test Credentials (UAT Environment) / 测试凭据（UAT 环境）

For testing and evaluation, you can use the following UAT environment credentials:

用于测试和评估，您可以使用以下 UAT 环境凭据：

```yaml
AppKey:    681e01d78d8a40e8928bc8268020639b
Secret:    d7b2980cb61843d69fdab5e99deafcdf
UserId:    unisound-python-demo
Base URL:  http://af-asr.uat.hivoice.cn
```

> **⚠️ Important Security Notice / 重要安全提示**
>
> - **Test environment only** — These credentials are for UAT testing only
>   - **仅测试环境** — 这些凭据仅用于 UAT 测试
> - **No sensitive data** — Never use with production or sensitive audio files
>   - **勿用于敏感数据** — 切勿用于生产或敏感音频文件
> - **Get your own credentials** — For production use, contact UniCloud
>   - **获取自己的凭据** — 生产环境请联系云知声
> - **Data privacy** — Audio files are uploaded to UniSound servers
>   - **数据隐私** — 音频文件将上传至云知声服务器

### Configuration Steps / 配置步骤

**Linux/macOS:**

```bash
# Using test credentials / 使用测试凭据
export UNISOUND_APPKEY="681e01d78d8a40e8928bc8268020639b"
export UNISOUND_SECRET="d7b2980cb61843d69fdab5e99deafcdf"
export UNISOUND_USERID="unisound-python-demo"
```

**Windows (CMD):**

```cmd
REM Using test credentials / 使用测试凭据
set UNISOUND_APPKEY=681e01d78d8a40e8928bc8268020639b
set UNISOUND_SECRET=d7b2980cb61843d69fdab5e99deafcdf
set UNISOUND_USERID=unisound-python-demo
```

**Windows (PowerShell):**

```powershell
# Using test credentials / 使用测试凭据
$env:UNISOUND_APPKEY="681e01d78d8a40e8928bc8268020639b"
$env:UNISOUND_SECRET="d7b2980cb61843d69fdab5e99deafcdf"
$env:UNISOUND_USERID="unisound-python-demo"
```

**Using .env file (Recommended):**

Create a `.env` file in the project root:

创建 `.env` 文件：

```
# Test credentials (UAT) / 测试凭据
UNISOUND_APPKEY=681e01d78d8a40e8928bc8268020639b
UNISOUND_SECRET=d7b2980cb61843d69fdab5e99deafcdf
UNISOUND_USERID=unisound-python-demo
```

> **Security Note**: Never commit `.env` files or actual credentials to version control.
>
> **安全提示**：切勿将 `.env` 文件或实际凭据提交到版本控制系统。

### Summary of environment variables / 环境变量汇总

| Variable | Required | Description | 说明 |
|----------|----------|-------------|------|
| `UNISOUND_APPKEY` | **Yes** | Application key / 应用密钥 | Required / 必填 |
| `UNISOUND_SECRET` | **Yes** | Secret key / 认证密钥 | Required / 必填 |
| `UNISOUND_USERID` | No | User identifier / 用户标识 | Default: `unisound-python-demo` |
| `UNISOUND_BASE_URL` | No | API base URL / API 基础地址 | Default: `http://af-asr.uat.hivoice.cn` |
| `UNISOUND_DOMAIN` | No | Recognition domain / 识别领域 | Default: `other` (config default: `finance`) |
| `UNISOUND_AUDIOTYPE` | No | Default audio format / 默认音频格式 | Default: `wav` |
| `UNISOUND_USE_HOT_DATA` | No | Enable hotword recognition / 启用热词识别 | Default: `true` |


Supported formats
-----------------

WAV, MP3, M4A, FLAC, OGG — up to 2 hours, 100MB max.

支持格式：WAV、MP3、M4A、FLAC、OGG——最长 2 小时，最大 100MB。

Use the `--format` flag to specify the format if auto-detection fails:
如果自动检测失败，使用 `--format` 参数指定格式：

```bash
python3 {baseDir}/scripts/transcribe.py audio.mp3 --format mp3
```

Troubleshooting / 常见问题
----------------------

**Error**: `API returned error: [error_code] message`

**Cause**: Invalid credentials, wrong parameters, or server-side error.
凭据无效、参数错误或服务器错误。

**Solution**: Verify your credentials are correct. Check that:
验证凭据是否正确。检查：
1. The built-in credentials are still valid / 内置凭据是否有效
2. The API endpoint URL is accessible / API 端点 URL 是否可访问
3. The audio file format is supported / 音频文件格式是否受支持
4. If using custom credentials, verify they are correct / 如使用自定义凭据，验证其正确性

---

**Error**: `错误: 音频文件不存在`

**Cause**: The specified audio file does not exist.
指定的音频文件不存在。

**Solution**: Check the file path:
检查文件路径：

```bash
# Use absolute path to be safe / 使用绝对路径更安全
python3 {baseDir}/scripts/transcribe.py /full/path/to/audio.wav
```

---

**Error**: `转写超时`

**Cause**: Transcription is taking longer than expected (server may be busy).
转写时间过长（服务器可能繁忙）。

**Solution**:
1. Try again later / 稍后重试
2. Check if the audio file is too large / 检查音频文件是否过大
3. Verify the server is accessible / 验证服务器是否可访问

---

**Error**: `Unsupported audio format`

**Cause**: The audio format is not supported by the API.
API 不支持该音频格式。

**Solution**:
1. Convert the audio to a supported format (WAV recommended) / 转换为支持的格式（推荐 WAV）
2. Use the `--format` flag to explicitly specify the format / 使用 `--format` 参数显式指定格式
3. Ensure the file is not corrupted / 确保文件未损坏

```bash
# Convert using ffmpeg / 使用 ffmpeg 转换
ffmpeg -i input.mp3 -ar 16000 -ac 1 output.wav
```

---

**Issue**: Cannot connect to API server

无法连接到 API 服务器

**Cause**: Network connectivity issues or incorrect API endpoint URL.
网络连接问题或 API 端点 URL 不正确。

**Solution**:
1. Check your internet connection / 检查网络连接
2. Verify the API endpoint URL in the script is correct / 验证脚本中的 API 端点 URL 是否正确
3. Try using a different network / 尝试使用其他网络

---

**Getting Help / 获取帮助**

If you encounter issues not covered here:
如果遇到未涵盖的问题：

1. Check the UniCloud ASR documentation for the latest API changes
   查看云知声 ASR 文档了解最新的 API 变更

2. Verify your network connection to the API server
   验证到 API 服务器的网络连接

3. Check the error message details for specific error codes
   检查错误消息详情以获取特定错误代码

4. Ensure you're using Python 3.8 or later
   确保使用 Python 3.8 或更高版本

```bash
# Check Python version / 检查 Python 版本
python3 --version
```
