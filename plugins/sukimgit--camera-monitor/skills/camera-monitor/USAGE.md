# Camera Monitor - OpenClaw 使用说明

## 🎯 快速开始

### 1. 安装依赖
```bash
pip install opencv-python mediapipe numpy requests pillow psutil
```

### 2. 录入人脸（首次使用）
```bash
cd D:\OpenClawDocs\projects\camera-monitor
python camera_monitor.py --register 老高 C:\path\to\photo.jpg
```

### 3. 启动系统

**方法 A：直接运行**
```bash
python vision_scheduler.py
```

**方法 B：OpenClaw 集成**
```bash
python openclaw_integration.py
```

---

## 💬 飞书命令

在飞书中发送以下命令（通过 OpenClaw 监听）：

| 命令 | 响应 |
|------|------|
| `启动视频模式` | 启动视觉监控系统 |
| `关闭视频模式` | 发送日报后关闭 |
| `视频状态` | 查询当前状态 |
| `今日日报` | 获取工作日报 |

---

## 🔧 OpenClaw 集成配置

### 在 HEARTBEAT.md 中添加
```markdown
## 📹 视觉监控检查
- [ ] 检查视觉系统是否运行
- [ ] 如果有飞书命令，创建命令文件
```

### 在 OpenClaw 中监听飞书消息
```python
# 示例：监听飞书消息并处理命令
if message in ["启动视频模式", "关闭视频模式", "视频状态", "今日日报"]:
    create_command(message)
```

---

## 📊 日报格式

```
📊 今日工作日报
========================================
⏱️ 总工作时长：6.5 小时 (390 分钟)
📅 工作时段数：3 个
💧 喝水次数：5 次
🧘 久坐提醒：3 次
😴 疲劳提醒：2 次
💡 光线提醒：1 次
========================================
辛苦了，早点休息！🌙
```

---

## 🚀 开机自启

### 任务计划程序
1. 打开"任务计划程序"
2. 创建基本任务
3. 触发器：登录时
4. 操作：启动程序 `pythonw.exe`
5. 参数：`D:\OpenClawDocs\projects\camera-monitor\vision_scheduler.py`
6. 起始于：`D:\OpenClawDocs\projects\camera-monitor`

---

## 📁 文件位置

| 文件 | 路径 |
|------|------|
| 主程序 | `D:\OpenClawDocs\projects\camera-monitor\vision_scheduler.py` |
| OpenClaw 集成 | `C:\Users\GWF\.openclaw\workspace\skills\camera-monitor\` |
| 人脸数据 | `D:\OpenClawDocs\projects\camera-monitor\face_encodings.json` |
| 命令文件 | `D:\OpenClawDocs\projects\camera-monitor\camera_command.json` |

---

## 💡 使用技巧

1. **后台运行** - 使用 `pythonw.exe` 隐藏控制台
2. **命令文件** - OpenClaw 创建 JSON 文件触发响应
3. **日报定时** - 每天 20:00 自动发送
4. **光线阈值** - 根据环境调整 `LIGHT_THRESHOLD`

---

**最后更新：** 2026-03-07
**版本：** v2.0.0
