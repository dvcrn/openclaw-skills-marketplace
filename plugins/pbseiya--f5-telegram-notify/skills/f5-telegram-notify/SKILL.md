---
name: f5-telegram-notify
description: "ส่งการแจ้งเตือน Telegram เมื่อ F5-TTS training เสร็จหรือล้มเหลว ใช้สำหรับ Docker environment"
---

# F5-Telegram-Notify Skill

สคริปต์สำหรับส่งการแจ้งเตือน Telegram เมื่อ F5-TTS training process เสร็จสิ้นหรือล้มเหลว

## การใช้งาน

### 1. ส่งแจ้งเตือนสำเร็จ
```bash
node /home/seiya/projects/openclaw/workspace/skills/f5-telegram-notify/scripts/notify.mjs success "Training เสร็จแล้ว!" "model_name" "/path/to/checkpoint"
```

### 2. ส่งแจ้งเตือนล้มเหลว
```bash
node /home/seiya/projects/openclaw/workspace/skills/f5-telegram-notify/scripts/notify.mjs error "Training ล้มเหลว: CUDA out of memory" "model_name"
```

### 3. ส่งแจ้งเตือนเริ่ม training
```bash
node /home/seiya/projects/openclaw/workspace/skills/f5-telegram-notify/scripts/notify.mjs start "เริ่ม training แล้ว" "model_name"
```

## พารามิเตอร์

1. **status**: `success` | `error` | `start`
2. **message**: ข้อความที่ต้องการส่ง
3. **model_name**: ชื่อโมเดล (optional)
4. **checkpoint_path**: Path ไปยัง checkpoint (optional, สำหรับ success)

## Config Required

ต้องมีไฟล์ `.env` ที่มี:
```bash
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
```

## โครงสร้างไฟล์

```
f5-telegram-notify/
├── SKILL.md
├── scripts/
│   └── notify.mjs
└── README.md
```
