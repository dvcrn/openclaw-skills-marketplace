# bili-mindmap

`bili-mindmap` 是一个可发布到 ClawHub 的单-skill 目录：输入 Bilibili 视频链接或 `BV` 号，自动抓取视频详情、字幕、AI 总结和热门评论，在字幕缺失时按操作系统选择 ASR 回退，最终生成 `outline.md` 和可在 XMind 中打开的 `.xmind` 文件。

这个目录是从开发工作区中整理出来的 **发布版 skill 包**，目标是满足 ClawHub 的单 skill 目录结构要求。

## 这个发布包包含什么

- `SKILL.md`：主 skill 入口
- `agents/openai.yaml`：UI 元数据
- `references/mindmap-outline-template.md`：导图结构参考
- `scripts/prepare_bili_context.py`：登录检查、上下文抓取、ASR 回退
- `scripts/generate_outline.py`：根据采集结果生成 `outline.md`
- `scripts/render_xmind.py`：纯 Python `.xmind` 导出器
- `scripts/run_bili_mindmap.py`：一键串起完整流程
- `vendor/aliyun_asr/`：打包内置的阿里云文件音频转写实现

## 外部前置依赖

这个 skill 仍然依赖以下外部能力，但不再依赖其他 skill 目录：

- 已安装并可执行的 `bili` 命令
- 如果需要音频回退，建议安装 `bilibili-cli[audio]`
- Windows 上若需云端 ASR，请准备阿里云配置文件
- Linux / macOS 上若需本地 ASR，请自行启动兼容 OpenAI Transcriptions API 的 Parakeet 服务

## 平台策略

### Windows

- 优先使用内置的阿里云 ASR 回退能力

### Linux / macOS

- 优先尝试本地 Parakeet 接口
- 如果本地接口不可用、失败或返回空文本，则回退到内置的阿里云 ASR

## 安装前检查

先确认：

```bash
bili --help
```

如果计划使用阿里云 ASR，默认读取：

- Windows：`%USERPROFILE%\.openclaw\aliyun-asr-config.json`
- Linux / macOS：`~/.openclaw/aliyun-asr-config.json`

也支持通过环境变量覆盖：

```bash
ALIYUN_ASR_CONFIG=/path/to/aliyun-asr-config.json
```

## 一键使用

```bash
python scripts/run_bili_mindmap.py \
  --source "https://www.bilibili.com/video/BV1ABcsztEcY" \
  --output-dir output/BV1ABcsztEcY \
  --login-if-needed \
  --transcribe-if-needed
```

## 分步使用

### 1. 采集上下文

```bash
python scripts/prepare_bili_context.py \
  --source "BV1ABcsztEcY" \
  --output output/BV1ABcsztEcY \
  --login-if-needed \
  --transcribe-if-needed
```

### 2. 生成大纲

```bash
python scripts/generate_outline.py \
  --context-dir output/BV1ABcsztEcY \
  --output output/BV1ABcsztEcY/outline.md
```

### 3. 导出 XMind

```bash
python scripts/render_xmind.py \
  --outline output/BV1ABcsztEcY/outline.md \
  --output output/BV1ABcsztEcY/result.xmind
```

## 致谢

这个 skill 的工作流与实现思路受以下项目启发或复用部分能力：

- `bilibili-cli`
- `aliyun-asr`
- `parakeet-local-asr`
- `xmind-generator`

详见：`THIRD_PARTY_NOTICES.md`
