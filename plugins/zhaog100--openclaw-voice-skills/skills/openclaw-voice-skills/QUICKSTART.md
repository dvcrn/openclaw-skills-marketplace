# 快速开始指南

## 安装步骤

1. 解压技能包
```bash
tar -xzf openclaw-voice-skills-*.tar.gz
cd openclaw-voice-skills-*
```

2. 运行安装脚本
```bash
chmod +x install.sh
./install.sh
```

3. 配置OpenClaw
```bash
# 将技能目录移动到OpenClaw技能目录
mv voice-chat voice-wake talk-mode ~/.openclaw/skills/
```

4. 测试技能
```bash
# 测试语音识别
python3 ~/.openclaw/skills/voice-chat/scripts/test_recognition.py
```

## 技能说明

- **voice-chat**: 语音对话（6种方言）
- **voice-wake**: 语音唤醒（5种唤醒词）
- **talk-mode**: 持续对话模式

## 详细文档

查看各技能目录下的 SKILL.md 文件
