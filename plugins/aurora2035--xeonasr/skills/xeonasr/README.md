# Xeon ASR Skill

基于 OpenVINO Qwen3-ASR 模型的语音转文字技能，为 OpenClaw/QQBot 提供本地语音识别能力。

## 架构说明

双服务架构（必须同时运行）：

| 服务 | 端口 | 类型 | 作用 |
|------|------|------|------|
| **Flask ASR** | 5001 | Python | 加载 Qwen3-ASR 模型，执行本地推理 |
| **ASR Skill** | 9001 | Node.js | 接收 QQ 语音消息，格式转换，调用 5001 推理 |

数据流：
QQ 语音 → qqbot(OpenClaw) → 9001(Node) → 5001(Python/模型) → 返回文字 → QQ

## 快速开始

### 1. 下载模型

```bash

https://huggingface.co/Qwen3-ASR-0.6B-INT8_ASYM-OpenVINO 
mv Qwen3-ASR-0.6B-INT8_ASYM-OpenVINO   /root/model/Qwen3-ASR-0.6B-INT8_ASYM-OpenVINO
```

### 2. 安装技能

#### 方式 A：通过 OpenClaw Bot（推荐）

发送以下指令给你的 OpenClaw Bot：

```bash
帮我安装并配置 xeonasr 技能，模型路径是 /root/model/Qwen3-ASR-0.6B-INT8_ASYM-OpenVINO
```

```bash
若提前已安装xeonasr，则指令变更为：
本机器已安装 xeonasr skill， 模型路径是 /root/model/Qwen3-ASR-0.6B-INT8_ASYM-OpenVINO，请帮我继续配置该技能
```

Bot 会自动完成：

- 从 clawhub 安装 xeonasr(未安装状态下)
- 运行环境配置脚本
- 配置 QQ Bot STT
- 启动服务
- 重启 gateway

```json
若提示无法直接执行系统命令来安装技能，请修改openclaw.json文件的tools, 给予openclaw更大权限(谨慎修改,后续及时回复)：
  "tools": {
    "profile": "full",
    "allow": [
      "*"
    ],
    "exec": {
      "host": "gateway",
      "security": "full",
      "ask": "off"
    }
  },
```



#### 方式 B：手动部署

```bash
# 安装技能
clawhub install xeonasr
cd /root/.openclaw/workspace/skills/xeonasr

# 运行环境配置
bash setup_env.sh --model-path /root/model/Qwen3-ASR-0.6B-INT8_ASYM-OpenVINO

# 启动服务
./start_all.sh

# 重启 gateway
openclaw gateway restart
```

## 目录结构

安装后位于 `/root/.openclaw/workspace/skills/xeonasr/`

```
xeonasr/
├── setup_env.sh          # 环境准备（Python + 依赖 + 配置）
├── start_asr_service.sh  # 启动 Flask ASR (5001)
├── start_all.sh          # 一键启动 5001 + 9001
├── stop.sh               # 停止所有服务
├── config.json           # Node.js Skill 配置
├── audio_config.json     # Python 模型配置
├── venv/                 # Python 虚拟环境
├── package.json          # Node 依赖配置
└── server.js             # Skill 主逻辑
```

## 使用

安装完成后，QQ 收到语音消息时自动转写，无需额外操作。

## 管理命令

```bash
# 进入技能目录
cd /root/.openclaw/workspace/skills/xeonasr

# 启动服务
./start_all.sh

# 停止服务
./stop.sh

# 查看状态
ps aux | grep -E "xdp-asr|server.js"
netstat -tulnp | grep -E "5001|9001"

# 健康检查
curl http://127.0.0.1:5001/health
curl http://127.0.0.1:9001/health

# 测试语音识别
curl -X POST -F "file=@test.wav" http://127.0.0.1:9001/audio/transcriptions
```

## 配置说明

### audio_config.json（Python 模型配置）

```json
{
  "qwen3_asr_ov": {
    "model": "/root/model/Qwen3-ASR-0.6B-INT8_ASYM-OpenVINO",
    "device": "CPU",
    "sample_rate": 16000,
    "language": "zh",
    "max_tokens": 256
  },
  "server": {
    "host": "127.0.0.1",
    "port": 5001
  }
}
```

### config.json（Node Skill 配置）

```json
{
  "port": 9001,
  "flaskAsrUrl": "http://127.0.0.1:5001/transcribe",
  "modelName": "Qwen3-ASR-0.6B-INT8_ASYM-OpenVINO",
  "openclawSession": "default"
}
```

### ~/.openclaw/openclaw.json（OpenClaw 全局配置）

```json
{
  "channels": {
    "qqbot": {
      "stt": {
        "enabled": true,
        "provider": "custom",
        "baseUrl": "http://127.0.0.1:9001",
        "model": "Qwen3-ASR-0.6B-INT8_ASYM-OpenVINO",
        "apiKey": "not-needed"
      }
    }
  }
}
```

## 常见问题

### ⚠️ 端口被占用

```bash
./stop.sh
# 或
pkill -f "xdp-asr-service|server.js"
```

### ⚠️ 缺少 chat_template.json

```bash
cp /root/model/Qwen3-ASR-0.6B-INT8_ASYM-OpenVINO/chat_template.json ./
./start_asr_service.sh
```

### ⚠️ Python 版本问题

`setup_env.sh` 会自动使用 Miniconda 安装 Python 3.10。如遇编译错误：

```bash
rm -rf venv ~/miniconda3
bash setup_env.sh --model-path /root/model/Qwen3-ASR-0.6B-INT8_ASYM-OpenVINO
```

## API 接口

### POST /audio/transcriptions（OpenAI 兼容）

```bash
curl -X POST -F "file=@voice.wav" -F "model=Qwen3-ASR-0.6B-INT8_ASYM-OpenVINO" http://localhost:9001/audio/transcriptions
```

响应：
```json
{"text": "转写结果文字"}
```

### GET /health

```bash
curl http://localhost:9001/health
```

响应：
```json
{"status": "ok", "port": 9001}
```

## 依赖

- Node.js 18+
- Python 3.10
- xdp-audio-service 0.1.0
- Qwen3-ASR 模型

## 许可证

MIT License

## 作者

aurora2035
