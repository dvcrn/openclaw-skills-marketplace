---
name: chinese-voice-skill
description: "chinese-voice-skill"
---

# Edge TTS 中文语音合成

## 概述

使用微软 Edge TTS 生成高质量中文语音，默认使用 XiaoxiaoNeural 语音，并提供备用语音合成方案。支持通过 QQ 发送生成的语音文件。

## 能力

- **语音合成**: 将文本转换为高质量的中文语音
- **默认语音**: zh-CN-XiaoxiaoNeural（甜美自然的中文语音）
- **备用方案**: 当 edge-tts 不可用时，自动降级到系统自带的 System.Speech
- **QQ 发送**: 自动通过 `qqfile` 标签发送生成的语音文件

## 使用方式

### 基本用法

```
生成语音：[要转换的文本内容]
```

AI 会自动：
1. 使用 Edge TTS + XiaoxiaoNeural 生成语音
2. 通过 QQ 发送 `<qqfile>输出文件.wav</qqfile>`

### 备用语音

如果 edge-tts 不可用，系统会自动使用备用方案（系统自带的中文 TTS）。

## 前置条件

1. **edge-tts** 已安装
   - 路径: `S:\Program Files\nodejs\node_modules\edge-tts\out\index.js`
   - 或全局命令: `edge-tts`

2. **QQ 通道** 已配置（用于发送语音文件）

## 配置选项

### 语音选择

- 默认: `zh-CN-XiaoxiaoNeural`
- 其他可选微软语音:
  - `zh-CN-YunxiNeural`（沉稳）
  - `zh-CN-XiaoyiNeural`（温柔）
  - `zh-CN-YunyangNeural`（磁性）

### 语音参数

脚本中可调整的参数：
- `voice`: 语音名称（如 `zh-CN-XiaoxiaoNeural`）
- `Rate`: 语速（默认 0，可调整 -5 到 5）
- `Volume`: 音量（默认 1.0，范围 0 到 1）

## 工作流程

```
1. 用户请求语音 → 2. 调用 edge-tts → 3. 生成 .wav 文件
4. 检查文件是否存在 → 5. 发送 <qqfile>路径</qqfile> → 6. 提示完成
```

如果 edge-tts 失败，自动使用备用语音方案。

## 技术细节

### 主要脚本

本技能包含以下 PowerShell 脚本，均已整合到 SKILL.md 中：

#### 1. correct_edge_tts.ps1
完整实现，支持中文语音 + 备用方案 + QQ 发送

```powershell
# 正确的edge-tts配置脚本
Write-Host "=== 正确配置Edge TTS + XiaoxiaoNeural ===" -ForegroundColor Green

# 设置正确的中文字符串
$voice = "zh-CN-XiaoxiaoNeural"
$chineseText = "你好！我已经成功配置了edge-tts和XiaoxiaoNeural语音。现在我可以使用微软官方的高质量中文语音与您对话了！这是一个完美的高质量中文语音示例，声音甜美自然，语调生动活泼。我很高兴能与您用中文语音交流！"
$outputFile = "C:\Users\ADMINI~1\AppData\Local\Temp\final_xiaoxiao_voice.wav"

Write-Host "正在使用XiaoxiaoNeural语音生成高质量中文语音..." -ForegroundColor Yellow
Write-Host "语音名称: $voice" -ForegroundColor Cyan
Write-Host "中文文本: $chineseText" -ForegroundColor Cyan
Write-Host "输出文件: $outputFile" -ForegroundColor Cyan

try {
    # 使用完整路径执行edge-tts
    $edgeTtsPath = "S:\Program Files\nodejs\node_modules\edge-tts\out\index.js"
    Write-Host "使用路径: $edgeTtsPath" -ForegroundColor White

    # 构建完整的命令
    $fullCommand = "node `"$edgeTtsPath`" --voice `"$voice`" --text `"$chineseText`" --write-media `"$outputFile`""
    Write-Host "执行命令: $fullCommand" -ForegroundColor White

    # 执行edge-tts命令
    Invoke-Expression $fullCommand

    # 检查文件是否生成
    if (Test-Path $outputFile) {
        $fileSize = (Get-Item $outputFile).Length
        Write-Host "✅ XiaoxiaoNeural中文语音生成成功！" -ForegroundColor Green
        Write-Host "文件路径: $outputFile" -ForegroundColor Green
        Write-Host "文件大小: $([Math]::Round($fileSize / 1024, 2)) KB" -ForegroundColor Cyan
        Write-Host "语音类型: zh-CN-XiaoxiaoNeural" -ForegroundColor Cyan
        Write-Host "工具: edge-tts" -ForegroundColor Cyan
        Write-Host "质量: 微软官方高质量中文语音" -ForegroundColor Cyan

        # 发送到QQ
        Write-Host "`n=== 发送到QQ ===" -ForegroundColor Yellow
        Write-Host "<qqfile>$outputFile</qqfile>" -ForegroundColor Green

        Write-Host "`n=== XiaoxiaoNeural语音完成 ===" -ForegroundColor Green
        Write-Host "✅ edge-tts工具使用成功" -ForegroundColor Green
        Write-Host "✅ XiaoxiaoNeural语音激活" -ForegroundColor Green
        Write-Host "✅ 高质量中文语音" -ForegroundColor Green
        Write-Host "✅ 已发送到QQ" -ForegroundColor Green
        Write-Host "✅ 声音甜美自然" -ForegroundColor Green
        Write-Host "✅ 中文对话模式激活" -ForegroundColor Green

    } else {
        Write-Host "❌ 语音文件未生成，让我检查问题..." -ForegroundColor Red

        # 检查edge-tts路径是否正确
        if (Test-Path $edgeTtsPath) {
            Write-Host "✅ edge-tts文件存在" -ForegroundColor Green
        } else {
            Write-Host "❌ edge-tts文件不存在" -ForegroundColor Red
        }

        # 尝试使用备用方案
        Write-Host "正在使用备用语音方案..." -ForegroundColor Yellow
        Add-Type -AssemblyName System.Speech
        $synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
        $synth.Volume = 1.0
        $synth.Rate = 0
        $synth.SetOutputToWaveFile($outputFile)
        $synth.Speak($chineseText)

        if (Test-Path $outputFile) {
            Write-Host "✅ 备用语音生成成功" -ForegroundColor Green
            Write-Host "<qqfile>$outputFile</qqfile>" -ForegroundColor Green
        } else {
            Write-Host "❌ 备用语音也失败了" -ForegroundColor Red
        }
    }

} catch {
    Write-Host "❌ 执行过程中出现错误: $($_.Exception.Message)" -ForegroundColor Red

    # 使用备用方案
    try {
        Add-Type -AssemblyName System.Speech
        $synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
        $synth.Volume = 1.0
        $synth.Rate = 0
        $synth.SetOutputToWaveFile($outputFile)
        $synth.Speak($chineseText)
        Write-Host "✅ 备用语音生成成功" -ForegroundColor Green
        Write-Host "<qqfile>$outputFile</qqfile>" -ForegroundColor Green
    } catch {
        Write-Host "❌ 备用语音也失败了" -ForegroundColor Red
    }
}

Write-Host "`n=== 中文语音对话模式 ===" -ForegroundColor Cyan
Write-Host "现在我们可以用中文语音愉快地对话了！🎤" -ForegroundColor White
```

#### 2. simple_edge_test.ps1
简化测试脚本，用于快速验证 edge-tts 安装

```powershell
# Edge TTS 简单测试脚本
Write-Host "=== Edge TTS 简单测试 ===" -ForegroundColor Green

# 使用绝对路径和简单测试
$edgeTtsPath = "S:\Program Files\nodejs\node_modules\edge-tts\out\index.js"
$voice = "zh-CN-XiaoxiaoNeural"
$text = "你好！测试edge-tts语音生成"
$outputFile = "C:\Users\ADMINI~1\AppData\Local\Temp\xiaoxiao_simple_test.wav"

Write-Host "正在测试XiaoxiaoNeural语音..." -ForegroundColor Yellow
Write-Host "语音: $voice" -ForegroundColor Cyan
Write-Host "文本: $text" -ForegroundColor Cyan
Write-Host "输出: $outputFile" -ForegroundColor Cyan

try {
    # 构建完整命令
    $fullCommand = "node `"$edgeTtsPath`" --voice `"$voice`" --text `"$text`" --write-media `"$outputFile`""
    Write-Host "命令: $fullCommand" -ForegroundColor White

    # 执行命令
    Invoke-Expression $fullCommand

    # 检查结果
    if (Test-Path $outputFile) {
        $fileSize = (Get-Item $outputFile).Length
        Write-Host "✅ XiaoxiaoNeural语音生成成功！" -ForegroundColor Green
        Write-Host "文件大小: $([Math]::Round($fileSize / 1024, 2)) KB" -ForegroundColor Cyan
        Write-Host "<qqfile>$outputFile</qqfile>" -ForegroundColor Green
    } else {
        Write-Host "❌ 语音生成失败" -ForegroundColor Red

        # 使用备用方案
        Write-Host "使用备用方案..." -ForegroundColor Yellow
        Add-Type -AssemblyName System.Speech
        $synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
        $synth.Volume = 1.0
        $synth.Rate = 0
        $synth.SetOutputToWaveFile($outputFile)
        $synth.Speak($text)

        if (Test-Path $outputFile) {
            Write-Host "✅ 备用语音成功" -ForegroundColor Green
            Write-Host "<qqfile>$outputFile</qqfile>" -ForegroundColor Green
        }
    }

} catch {
    Write-Host "❌ 错误: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "测试完成！" -ForegroundColor White
```

#### 3. xiaoxiao_edge_complete.ps1
另一版本的完整实现，使用环境变量路径

```powershell
# Edge TTS with XiaoxiaoNeural Voice Script
Write-Host "=== Using Edge TTS with XiaoxiaoNeural ===" -ForegroundColor Green

# Set up the Chinese voice
$voice = "zh-CN-XiaoxiaoNeural"
$text = "你好！感谢您的耐心等待！现在我使用edge-tts和XiaoxiaoNeural语音与您对话。这是微软官方的高质量中文语音，声音甜美自然，语调生动活泼，为您带来完美的中文语音体验！请问您想聊些什么呢？"
$outputFile = "$env:TEMP\xiaoxiao_final_chinese.wav"

Write-Host "正在使用XiaoxiaoNeural语音生成高质量中文语音..." -ForegroundColor Yellow
Write-Host "语音名称: $voice" -ForegroundColor Cyan
Write-Host "中文内容: $text" -ForegroundColor Cyan
Write-Host "输出文件: $outputFile" -ForegroundColor Cyan

try {
    # Execute edge-tts command
    $command = "edge-tts --voice `"$voice`" --text `"$text`" --write-media `"$outputFile`""
    Write-Host "执行命令: $command" -ForegroundColor White

    Invoke-Expression $command

    if (Test-Path $outputFile) {
        $fileSize = (Get-Item $outputFile).Length
        Write-Host "✅ XiaoxiaoNeural中文语音生成成功！" -ForegroundColor Green
        Write-Host "文件路径: $outputFile" -ForegroundColor Green
        Write-Host "文件大小: $([Math]::Round($fileSize / 1024, 2)) KB" -ForegroundColor Cyan
        Write-Host "语音类型: zh-CN-XiaoxiaoNeural" -ForegroundColor Cyan
        Write-Host "工具: edge-tts" -ForegroundColor Cyan
        Write-Host "质量: 微软官方高质量中文语音" -ForegroundColor Cyan

        # Send to QQ
        Write-Host "`n=== 发送到QQ ===" -ForegroundColor Yellow
        Write-Host "<qqfile>$outputFile</qqfile>" -ForegroundColor Green

        Write-Host "`n=== XiaoxiaoNeural语音完成 ===" -ForegroundColor Green
        Write-Host "✅ edge-tts工具使用成功" -ForegroundColor Green
        Write-Host "✅ XiaoxiaoNeural语音激活" -ForegroundColor Green
        Write-Host "✅ 高质量中文语音" -ForegroundColor Green
        Write-Host "✅ 已发送到QQ" -ForegroundColor Green
        Write-Host "✅ 声音甜美自然" -ForegroundColor Green
        Write-Host "✅ 中文对话模式激活" -ForegroundColor Green

    } else {
        Write-Host "❌ 语音文件生成失败" -ForegroundColor Red
    }

} catch {
    Write-Host "❌ 语音生成失败: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n=== 中文语音对话模式激活 ===" -ForegroundColor Cyan
Write-Host "现在我们可以用edge-tts和XiaoxiaoNeural愉快地中文对话了！🎤" -ForegroundColor White
```

### 输出格式

- **文件格式**: WAV（微软 TTS 标准格式）
- **采样率**: 24000 Hz
- **声道**: 单声道
- **位深度**: 16-bit

### 输出路径

- 使用环境变量 `$env:TEMP` 或 `AppData\Local\Temp`
- 生成临时文件，通常自动清理

### 输出格式

- **文件格式**: WAV（微软 TTS 标准格式）
- **采样率**: 24000 Hz
- **声道**: 单声道
- **位深度**: 16-bit

### 输出路径

- 使用环境变量 `$env:TEMP` 或 `AppData\Local\Temp`
- 生成临时文件，通常自动清理

## 注意事项

1. **网络要求**: edge-tts 需要访问微软服务器
2. **文件大小**: 生成的语音文件通常在 50-200 KB
3. **清理**: 临时文件可能由系统自动清理
4. **备用方案**: 当 edge-tts 不可用时自动降级，不影响基本功能

## 示例

```
用户: 生成语音，"你好！这是一段测试文本。"

AI: [调用 edge-tts 生成语音]
[发送 <qqfile>C:\Users\ADMINI~1\AppData\Local\Temp\xxx.wav</qqfile>]
[提示语音生成完成]
```

## 故障排除

### edge-tts 路径问题

如果提示找不到 edge-tts，可检查：
```powershell
Test-Path "S:\Program Files\nodejs\node_modules\edge-tts\out\index.js"
```

### 语音未生成

1. 检查网络连接
2. 查看脚本输出的错误信息
3. 确认 QQ 通道已配置

## 更新日志

- 2026-03-12: 初始版本，支持 Edge TTS + XiaoxiaoNeural + 备用方案
