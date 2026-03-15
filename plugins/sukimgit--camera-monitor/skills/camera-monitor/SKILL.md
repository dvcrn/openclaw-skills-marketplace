---
name: camera-monitor
description: "AI 视觉监控系统：双模式架构（待机/关怀），支持人脸识别、久坐提醒、疲劳检测、光线检测、工作时长统计，飞书命令控制。"
---

# Camera Monitor - AI 视觉监控系统

**你的 24 小时智能视觉助手！**

纯 MediaPipe 方案，隐私第一（本地处理，不上传云端），双模式架构（待机/关怀），自动关怀你的工作状态！

---

## 🎯 使用场景

- **在家办公** - 自动检测工作状态，提醒休息
- **办公室监控** - 识别员工/陌生人，安全提醒
- **健康关怀** - 久坐/疲劳/光线检测，保护健康
- **工作统计** - 自动记录工作时长，生成日报

---

## 🛠️ 核心功能

### 1. 双模式架构
- ✅ **待机模式** - 低资源占用（10 秒/次），仅检测是否有人
- ✅ **关怀模式** - 全功能运行（3 秒/次），行为分析 + 健康提醒
- ✅ **自动切换** - 检测到人自动切换关怀，人离开 5 分钟切回待机

### 2. 人脸识别
- ✅ **身份识别** - 识别老高/其他人/陌生人
- ✅ **隐私保护** - 纯本地处理，不保存人脸照片
- ✅ **快速录入** - 一张照片即可录入人脸

### 3. 健康关怀
- ✅ **久坐提醒** - 连续工作 2 小时提醒活动
- ✅ **喝水提醒** - 30 分钟提醒补充水分
- ✅ **疲劳检测** - 检测揉眼等疲劳行为
- ✅ **光线检测** - 环境太暗提醒开灯

### 4. 工作统计
- ✅ **时长统计** - 自动记录工作时段
- ✅ **日报生成** - 发送"今日日报"获取完整报告
- ✅ **飞书推送** - 重要提醒实时推送

---

## 💬 飞书命令

| 命令 | 响应 |
|------|------|
| `启动视频模式` | 确认系统运行状态 |
| `关闭视频模式` | 发送日报后关闭 |
| `视频状态` | 当前模式 + 工作时长 + 提醒次数 |
| `今日日报` | 完整工作日报 |

---

## 🚀 快速开始

### 1. 安装依赖
```bash
pip install opencv-python mediapipe numpy requests pillow
```

### 2. 录入人脸（首次使用）
```bash
cd D:\OpenClawDocs\projects\camera-monitor
python camera_monitor.py --register 老高 C:\path\to\photo.jpg
```

### 3. 启动系统
```bash
python vision_scheduler.py
```

### 4. 飞书控制（可选）
在 OpenClaw 中监听飞书消息，自动创建命令文件：
```json
{"command": "视频状态"}
```

---

## 💰 定价 Pricing

| 版本 | 价格 | 功能 |
|------|------|------|
| **标准版 Standard** | 免费 Free | 基础检测 + 本地日志 |
| **专业版 Pro** | $15/month (¥99/月) | 飞书通知 + 日报生成 + 工作统计 |
| **企业版 Enterprise** | $50/month (¥350/月) | 多人识别 + 团队统计 + 私有化部署 |
| **定制版 Custom** | $500-2000 (¥3500-14000) | 功能定制 + 硬件集成 |

---

## 📧 联系 Contact

**定制开发 Custom Development：**
- 📧 邮箱 Email：私信获取 DM for details
- 💬 微信 WeChat：私信获取 DM for details

**支持支付 Payment：**
- 国内 Domestic：私信获取
- 国际 International：私信获取（PayPal/Wise）

**售后支持 After-Sales：**
- 首年免费维护 Free for 1st year
- 次年 $50/年 (¥350/年) optional

---

## 🎯 案例展示 Cases

### 案例 1：个人健康关怀
- **用户：** 在家办公开发者
- **需求：** 防止久坐，保护健康
- **方案：** 专业版 + 飞书通知
- **效果：** 每天喝水 8 杯，久坐时间减少 60%

### 案例 2：团队考勤统计
- **用户：** 10 人技术团队
- **需求：** 自动考勤 + 工作时长统计
- **方案：** 企业版 + 多人识别
- **效果：** 考勤自动化，每月节省 5 小时统计时间

---

## 🔧 配置项

编辑 `vision_scheduler.py` 顶部配置：

```python
# 检测间隔
STANDBY_CHECK_INTERVAL = 10  # 待机模式（秒）
CARE_CHECK_INTERVAL = 3     # 关怀模式（秒）
LEAVE_DELAY = 300           # 离开后切换待机延迟（秒）

# 提醒阈值
SEDENTARY_THRESHOLD = 7200  # 久坐提醒（秒）
WATER_THRESHOLD = 1800      # 喝水提醒（秒）
FATIGUE_CHECK_INTERVAL = 300  # 疲劳检测（秒）
LIGHT_CHECK_INTERVAL = 60   # 光线检测（秒）
LIGHT_THRESHOLD = 50        # 光线阈值

# 功能开关
ENABLE_BEHAVIOR = True      # 行为识别
ENABLE_SEDENTARY = True     # 久坐提醒
ENABLE_WATER = True         # 喝水提醒
ENABLE_FATIGUE = True       # 疲劳检测
ENABLE_LIGHT = True         # 光线检测
```

---

## 📁 文件结构

```
camera-monitor/
├── vision_scheduler.py      # 主程序（双模式调度器）
├── camera_monitor.py        # 旧版主程序（保留兼容）
├── behavior_recognizer.py   # 行为识别模块
├── face_encodings.json      # 人脸编码数据
├── camera_command.json      # 飞书命令文件（运行时创建）
├── models/
│   ├── face_detection.tflite
│   └── face_landmarker.task
└── README.md                # 说明文档
```

---

## 🚀 更新日志 Changelog

### v2.0.0 (2026-03-07)
- ✅ 双模式架构（待机/关怀）
- ✅ 光线检测功能
- ✅ 工作时长统计 + 日报生成
- ✅ 飞书命令集成
- ✅ 纯 MediaPipe 方案（移除 face_recognition）

### v1.0.0 (2026-03-06)
- ✅ 基础人脸检测
- ✅ 行为识别（喝水/伸懒腰/揉眼）
- ✅ 久坐提醒
- ✅ 飞书推送

---

**技能来源 Source：** https://clawhub.ai/sukimgit/camera-monitor
**作者 Author：** Monet + 老高
**许可 License：** MIT
