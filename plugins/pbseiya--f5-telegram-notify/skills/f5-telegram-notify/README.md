# F5-Telegram-Notify

สคริปต์แจ้งเตือน Telegram สำหรับ F5-TTS Training

## 📁 โครงสร้างไฟล์

```
f5-telegram-notify/
├── SKILL.md
├── README.md
└── scripts/
    ├── notify.mjs              # Core notification (Node.js)
    ├── notify.sh               # Core notification (Bash - สำหรับ Docker)
    ├── train_with_notify.sh    # Wrapper สำหรับ training
    └── docker_notify.sh        # Helper สำหรับ Docker
```

## การใช้งาน

### 1. แบบตรงๆ (Direct)
```bash
# จาก workspace root
node skills/f5-telegram-notify/scripts/notify.mjs success "Training เสร็จแล้ว!" "F5TTS_v1_Base" "/app/outputs/checkpoint-1000"
node skills/f5-telegram-notify/scripts/notify.mjs error "CUDA out of memory" "F5TTS_v1_Base"
node skills/f5-telegram-notify/scripts/notify.mjs start "เริ่ม training แล้ว" "F5TTS_v1_Base"
```

### 2. ใช้ Wrapper Script (แนะนำ)
```bash
# รัน training พร้อมแจ้งเตือนอัตโนมัติ
./skills/f5-telegram-notify/scripts/train_with_notify.sh \
  accelerate launch src/f5_tts/train/train.py --config-name F5TTS_v1_Base.yaml
```

### 3. สำหรับ Docker

#### รันจาก Host เข้า Container (แนะนำ)
```bash
./skills/f5-telegram-notify/scripts/docker_notify.sh success "Training เสร็จ!" "MyModel"
```

#### Mount Skill เข้า Container
เพิ่มใน docker-compose.yml:
```yaml
volumes:
  - ./skills/f5-telegram-notify:/app/skills/f5-telegram-notify
```

แล้วเรียกจากใน container:
```bash
# ใช้ Bash version (ไม่มี Node.js ใน container)
docker exec f5-tts bash /app/skills/f5-telegram-notify/scripts/notify.sh success "เสร็จแล้ว!" "Model"

# หรือใช้ Node.js version (ถ้ามี)
docker exec f5-tts node /app/skills/f5-telegram-notify/scripts/notify.mjs success "เสร็จแล้ว!" "Model"
```

### 4. ผูกกับ Training Command
```bash
# แบบ manual
accelerate launch src/f5_tts/train/train.py --config-name F5TTS_v1_Base.yaml && \
  node skills/f5-telegram-notify/scripts/notify.mjs success "Training สำเร็จ!" "F5TTS_v1_Base" "/app/outputs" || \
  node skills/f5-telegram-notify/scripts/notify.mjs error "Training ล้มเหลว: $?" "F5TTS_v1_Base"
```

## ⚙️ Config

ต้องมี environment variables:
- `TELEGRAM_BOT_TOKEN`: Bot token จาก @BotFather
- `TELEGRAM_CHAT_ID`: Chat ID ของผู้รับ

สคริปต์จะโหลดจาก `.env` อัตโนมัติจาก:
1. `/home/seiya/projects/openclaw/.env`
2. `workspace/.env`
3. Current directory `.env`

## 📝 ตัวอย่าง Output

```
✅ Training สำเร็จ!

Training เสร็จแล้ว!
⏱ ระยะเวลา: 2h 15m 30s

📦 Model: F5TTS_v1_Base
💾 Checkpoint: /app/outputs/checkpoint-1000

⏰ 3/3/2569 04:15:00
```

## 🔧 Environment Variables (Optional)

```bash
export F5_MODEL_NAME="F5TTS_v1_Base"  # ชื่อโมเดล default
```

## 🧪 ทดสอบ

```bash
# ทดสอบส่งข้อความ
node skills/f5-telegram-notify/scripts/notify.mjs start "🧪 ทดสอบระบบ" "TestModel"
```
