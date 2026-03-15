---
name: xeonasr
description: "xeon_asr"
---

# Xeon ASR

🎤 基于 OpenVINO Qwen3-ASR 模型的本地语音转文字技能，为 OpenClaw/QQBot 提供本地语音识别能力。

## 架构

双服务架构（自动运行）：

| 服务 | 端口 | 作用 |
|------|------|------|
| Flask ASR | 5001 | 加载 Qwen3-ASR 模型，执行本地推理 |
| ASR Skill | 9001 | 接收 QQ 语音消息，调用 5001 推理 |

## 前置要求

**唯一步骤：下载模型**

```bash
git lfs install
git clone https://huggingface.co/Qwen3-ASR-0.6B-INT8_ASYM-OpenVINO /root/model/Qwen3-ASR-0.6B-INT8_ASYM-OpenVINO
```

## 安装流程

当用户请求安装时，按以下步骤执行：

1. **从 clawhub 安装**
   ```bash
   clawhub install xeonasr
   ```

2. **运行环境配置**
   ```bash
   cd /root/.openclaw/workspace/skills/xeonasr
   bash setup_env.sh --model-path /root/model/Qwen3-ASR-0.6B-INT8_ASYM-OpenVINO
   ```

3. **配置 QQ Bot STT**
   
   修改 `~/.openclaw/openclaw.json`，添加或更新：
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

4. **启动服务**
   ```bash
   ./start_all.sh
   ```

5. **重启 gateway**
   ```bash
   openclaw gateway restart
   ```

## 使用

安装完成后，QQ 收到语音消息时自动转写。

## 管理

```bash
# 进入技能目录
cd /root/.openclaw/workspace/skills/xeonasr

# 重启服务
./stop.sh && ./start_all.sh

# 健康检查
curl http://127.0.0.1:5001/health
curl http://127.0.0.1:9001/health
```

## 常见问题

**端口被占用**：`./stop.sh` 后重试

**缺少 chat_template.json**：从模型目录复制到技能目录

**Python 版本问题**：`setup_env.sh` 会自动处理

## 依赖

- Node.js 18+
- Python 3.10
- xdp-audio-service 0.1.0
- Qwen3-ASR 模型

## 许可证

MIT License

## 作者

aurora2035
