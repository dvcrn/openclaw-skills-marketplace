# UniSound ASR Skill for ClawHub

云知声（UniSound）语音识别 Skill，符合 ClawHub 规范。

## 功能特性

- 支持多种音频格式（WAV、MP3、M4A、FLAC、OGG）
- 完整的上传、转写、结果获取流程
- 命令行接口，易于集成
- 支持 JSON 格式输出
- 详细的错误处理和日志

## 目录结构

```
skill/
├── skill.md           # ClawHub skill 说明文档（必填）
├── README.md          # 本文件
├── .env.example       # 环境变量模板
└── scripts/
    └── transcribe.py  # 转写脚本
```

## 安装

1. 克隆或下载此 skill 到本地

2. 安装依赖：
```bash
pip install requests
```

## 配置

**必须配置环境变量才能运行脚本！**

### 测试凭据（UAT 环境）

用于测试和评估，您可以使用以下 UAT 环境凭据：

```yaml
AppKey:    681e01d78d8a40e8928bc8268020639b
Secret:    d7b2980cb61843d69fdab5e99deafcdf
UserId:    unisound-python-demo
Base URL:  http://af-asr.uat.hivoice.cn
```

> **⚠️ 重要安全提示**
>
> - **仅测试环境** — 这些凭据仅用于 UAT 测试
> - **勿用于敏感数据** — 切勿用于生产或敏感音频文件
> - **获取自己的凭据** — 生产环境请联系云知声
> - **数据隐私** — 音频文件将上传至云知声服务器

### 配置环境变量

**Linux/macOS:**
```bash
# 使用测试凭据
export UNISOUND_APPKEY="681e01d78d8a40e8928bc8268020639b"
export UNISOUND_SECRET="d7b2980cb61843d69fdab5e99deafcdf"
export UNISOUND_USERID="unisound-python-demo"
```

**Windows CMD:**
```cmd
REM 使用测试凭据
set UNISOUND_APPKEY=681e01d78d8a40e8928bc8268020639b
set UNISOUND_SECRET=d7b2980cb61843d69fdab5e99deafcdf
set UNISOUND_USERID=unisound-python-demo
```

**Windows PowerShell:**
```powershell
# 使用测试凭据
$env:UNISOUND_APPKEY="681e01d78d8a40e8928bc8268020639b"
$env:UNISOUND_SECRET="d7b2980cb61843d69fdab5e99deafcdf"
$env:UNISOUND_USERID="unisound-python-demo"
```

### 使用 .env 文件（推荐）

在项目根目录创建 `.env` 文件：
```
# 测试凭据 (UAT)
UNISOUND_APPKEY=681e01d78d8a40e8928bc8268020639b
UNISOUND_SECRET=d7b2980cb61843d69fdab5e99deafcdf
UNISOUND_USERID=unisound-python-demo
```

> **安全提示**：切勿将 `.env` 文件或实际凭据提交到版本控制系统。

> 详细配置说明请参考 [skill.md](SKILL.md)

## 使用

### 基础用法

```bash
python3 scripts/transcribe.py audio.wav
```

### 保存到文件

```bash
python3 scripts/transcribe.py audio.wav --out result.txt
```

### 输出 JSON 格式

```bash
python3 scripts/transcribe.py audio.wav --json --out result.json
```

### 指定音频格式

```bash
python3 scripts/transcribe.py audio.mp3 --format mp3
```

### 指定领域

```bash
python3 scripts/transcribe.py audio.wav --domain finance
```

## 命令行参数

| 参数 | 说明 |
|------|------|
| `audio` | 音频文件路径（必填） |
| `--out`, `-o` | 输出文件路径 |
| `--json` | 输出 JSON 格式（包含完整结果） |
| `--format` | 音频格式（默认: wav） |
| `--domain` | 领域（默认: other） |

## 环境变量

| 变量 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| `UNISOUND_APPKEY` | **是** | - | 应用密钥 |
| `UNISOUND_SECRET` | **是** | - | 认证密钥 |
| `UNISOUND_USERID` | 否 | `unisound-python-demo` | 用户ID |
| `UNISOUND_BASE_URL` | 否 | `http://af-asr.uat.hivoice.cn` | API 基础地址 |
| `UNISOUND_DOMAIN` | 否 | `other` (配置类: `finance`) | 识别领域 |
| `UNISOUND_AUDIOTYPE` | 否 | `wav` | 音频格式 |
| `UNISOUND_USE_HOT_DATA` | 否 | `true` | 是否使用热词 |

## 支持的音频格式

- WAV
- MP3
- M4A
- FLAC
- OGG

文件大小限制：最大 100MB
时长限制：最长 2 小时

## 工作流程

1. 初始化上传 - 获取任务ID
2. 上传音频文件 - 上传到服务器
3. 开始转写 - 提交转写任务
4. 轮询结果 - 等待转写完成
5. 输出文本 - 返回识别结果

## 错误处理

脚本包含详细的错误处理，常见错误：

- **未设置凭据** - 环境变量 `UNISOUND_APPKEY` 或 `UNISOUND_SECRET` 未配置
- **音频文件不存在** - 文件路径错误
- **转写超时** - 服务器繁忙或文件过大
- **不支持的音频格式** - 格式不受支持

## 安全注意事项

1. **仅用于测试** - 提供的凭据仅用于 UAT 测试环境
2. **保护隐私** - 勿上传敏感或个人隐私音频
3. **生产部署** - 生产环境请联系云知声获取独立凭据
4. **审查代码** - 使用前建议审查 `scripts/transcribe.py` 了解网络行为

详细的故障排除请参考 [skill.md](SKILL.md) 的 Troubleshooting 部分。

## 开发

### 修改 API 端点

编辑 `scripts/transcribe.py` 中的 `ASRConfig` 类：

```python
@dataclass
class ASRConfig:
    base_url: str = "https://your-api-endpoint.com"
    # ...
```

### 添加新功能

1. 在 `ASRClient` 类中添加新方法
2. 在 `main()` 函数中添加命令行参数
3. 更新 [skill.md](SKILL.md) 文档

## License

MIT License

## 联系方式

如有问题或建议，请提交 Issue。
