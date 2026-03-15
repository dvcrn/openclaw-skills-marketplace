# HiDream API Gen Skills

A comprehensive collection of AI generation skills for the OpenClaw platform (vivago.ai), enabling seamless integration of advanced video and image generation models into your applications or AI agents.

This repository provides Python scripts and modules that handle parameter validation, payload construction, and API communication for various AIGC models.

[中文介绍](#中文介绍)

## Features

- **Multi-Model Support**: Ready-to-use scripts for popular models:
  - **Video**: Kling (Q2.5T/Q2.6), Sora-2-Pro, Seedance (1.0/1.5), Minimax Hailuo 02
  - **Image**: Seedream (M1/M2), Nano Banana
- **Dual Interface**:
  - **Python API**: Clean, type-hinted functions for direct code integration.
  - **CLI Tools**: robust command-line interface for manual testing and scripting.
- **AI-Ready**: Optimized for AI agents to understand and invoke, with built-in error handling guidance.
- **Unified Auth**: Simple token-based authentication via environment variables.

## Quick Start

### Installation

Clone the repository and install dependencies (requests):

```bash
pip install requests
```

### Configuration

Get your API token from [vivago.ai/platform/token](https://vivago.ai/platform/token) and set it:

```bash
export OPENCLAW_AUTHORIZATION="your-sk-token"
```

### Usage (Python)

```python
from scripts.seedream import run as generate_image

# Generate a cyberpunk cat image
result = generate_image(
    version="M2",
    prompt="A cyberpunk cat on the moon",
    resolution="2048*2048"
)
print(result)
```

### Usage (CLI)

```bash
python3 scripts/kling.py --version "Q2.5T-std" --prompt "A flying car"
```

---

<a id="中文介绍"></a>

# HiDream API Gen Skills (中文介绍)

这是一个针对 OpenClaw 平台 (vivago.ai) 的 AI 生成技能集合，旨在帮助开发者轻松集成先进的视频和图像生成模型。

本项目提供了封装好的 Python 脚本和模块，处理了参数校验、Payload 构建以及与 API 的通信细节。

## 功能特性

- **多模型支持**：开箱即用的主流模型支持：
  - **视频模型**: Kling (快手可灵 Q2.5T/Q2.6), Sora-2-Pro, Seedance (1.0/1.5), Minimax Hailuo 02
  - **图像模型**: Seedream (M1/M2), Nano Banana
- **双重接口**：
  - **Python API**: 清晰的、带类型提示的函数接口，适合代码直接调用。
  - **命令行工具**: 健壮的 CLI 接口，适合手动测试或脚本自动化。
- **AI 友好**: 专为 AI Agent 设计，包含错误处理指引，Agent 可轻松理解并调用。
- **统一鉴权**: 通过环境变量即可简单配置 Token。

## 快速开始

### 安装

克隆仓库并安装依赖 (`requests`)：

```bash
pip install requests
```

### 配置

前往 [vivago.ai/platform/token](https://vivago.ai/platform/token) 获取 API Token 并设置环境变量：

```bash
export OPENCLAW_AUTHORIZATION="your-sk-token"
```

### 使用示例 (Python)

```python
from scripts.seedream import run as generate_image

# 生成一张赛博朋克猫的图片
result = generate_image(
    version="M2",
    prompt="A cyberpunk cat on the moon",
    resolution="2048*2048"
)
print(result)
```

### 使用示例 (CLI)

```bash
python3 scripts/kling.py --version "Q2.5T-std" --prompt "A flying car"
```
