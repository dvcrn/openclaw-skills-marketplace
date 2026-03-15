---
name: bili-mindmap
description: "Turn a Bilibili video URL or BV number into a summarized XMind mind map. Use when the user wants to collect subtitles, comments, AI summary, and transcript fallback, then generate structured notes, 内容梳理, or 思维导图 for a Bilibili video."
---

# Bili Mindmap

把 B 站视频链接整理成可在 XMind 中打开的思维导图。

## 先决条件

- 确认 `bili` 已安装且可用。
- 需要音频回退时，确认 `bilibili-cli[audio]` 已安装。
- Windows 上走云端 ASR 时，确认阿里云配置文件已存在。
- Linux/macOS 上若优先走本地 ASR，确认本地 Parakeet 接口已启动。

## 关键约束

- 优先使用字幕；只有字幕不可用时才走音频转写。
- 登录检查是强依赖：先运行 `bili status`，必要时再运行 `bili login`。
- Windows 优先使用内置阿里云 ASR。
- Linux/macOS 优先使用本地 Parakeet；失败时回退到内置阿里云 ASR。
- 导图中的主干内容优先来自字幕或 ASR，评论只作为补充。

## 标准流程

1. 解析用户输入，接受完整视频链接或 `BV` 号。
2. 运行 `bili status` 检查登录状态。
3. 需要时运行 `bili login` 并等待用户扫码。
4. 运行 `python scripts/prepare_bili_context.py --source <视频链接或BV号> --login-if-needed --transcribe-if-needed`。
5. 阅读输出目录中的 `context.md`、`manifest.json` 和相关文本文件。
6. 运行 `python scripts/generate_outline.py --context-dir <输出目录> --output <输出目录/outline.md>`。
7. 运行 `python scripts/render_xmind.py --outline <outline.md> --output <输出.xmind>`。
8. 向用户说明 `.xmind` 路径，并标明主要内容来源是字幕、AI 总结、评论还是 ASR。

## 一键流水线

```bash
python scripts/run_bili_mindmap.py \
  --source "BV1ABcsztEcY" \
  --output-dir output/BV1ABcsztEcY \
  --login-if-needed \
  --transcribe-if-needed
```

## 采集策略

按下面顺序收集信息：

1. `bili video <source>`：视频详情
2. `bili video <source> --subtitle`：字幕
3. `bili video <source> --ai`：站内 AI 总结
4. `bili video <source> --comments`：热门评论
5. 若字幕不可用：
   - `bili audio <source> -o <输出目录/audio>` 提取音频
   - Windows：优先内置阿里云 ASR
   - Linux/macOS：优先本地 Parakeet，失败后回退到内置阿里云 ASR

## 输出要求

- 用视频标题作为中心主题。
- 一级分支优先包含：`视频概览`、`内容脉络`、`核心内容`、`关键细节`、`评论反馈`、`总结 / 行动项`。
- 字幕 / ASR 是主干来源，评论与 AI 总结只做补充。
- 不要臆造内容；信息缺失时要明确说明。

## 关键文件

- `scripts/prepare_bili_context.py`：登录检查、内容抓取、ASR 回退
- `scripts/generate_outline.py`：大纲生成
- `scripts/render_xmind.py`：纯 Python XMind 导出
- `scripts/run_bili_mindmap.py`：总控脚本
- `references/mindmap-outline-template.md`：大纲模板
- `vendor/aliyun_asr/`：内置阿里云文件转写实现

## 常见故障

- 如果 `bili` 不存在：先安装 `bilibili-cli`
- 如果字幕不可用且音频提取失败：检查 `bilibili-cli[audio]`、FFmpeg / PyAV 依赖
- 如果阿里云 ASR 不工作：检查 `ALIYUN_ASR_CONFIG` 或默认配置文件路径
- 如果 Linux/macOS 上本地 Parakeet 不可达：自动尝试阿里云 ASR，并在 `manifest.json` 中记录回退
