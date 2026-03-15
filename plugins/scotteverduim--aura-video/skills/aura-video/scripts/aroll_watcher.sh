#!/bin/bash
# aroll_watcher.sh — Monitort de 04_A-Roll map op Google Drive
# Zodra scene1.mp4 EN scene3.mp4 aanwezig zijn voor een video,
# wordt de pipeline automatisch gestart.
# Draait elke 30 minuten via cron.

export PATH="/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin"

RCLONE="/usr/local/bin/rclone"
CONFIG="$HOME/.gdrive-rclone.ini"
AROLL_BASE="manus_google_drive:Aura Creatine/Content Pipeline/04_A-Roll"
SCRIPTS_BASE="manus_google_drive:Aura Creatine/Content Pipeline/01_Scripts"
FINAL_BASE="manus_google_drive:Aura Creatine/Content Pipeline/03_Final_Videos"
PIPELINE="$HOME/.openclaw-workspace/skills/aura-video/scripts/aura_video.sh"
STATE_FILE="$HOME/.aroll_watcher_state"
LOG_FILE="$HOME/.aroll_watcher.log"
TELEGRAM_SCRIPT="$HOME/.openclaw-workspace/skills/auraveo/send_telegram.sh"

# Laad env vars
source "$HOME/.openclaw/.env" 2>/dev/null || true

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

send_telegram() {
  local msg="$1"
  if [ -f "$TELEGRAM_SCRIPT" ]; then
    bash "$TELEGRAM_SCRIPT" "$msg" 2>/dev/null
  elif [ -n "$TELEGRAM_BOT_TOKEN" ] && [ -n "$TELEGRAM_CHAT_ID" ]; then
    curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
      -d "chat_id=${TELEGRAM_CHAT_ID}" \
      -d "text=${msg}" > /dev/null 2>&1
  fi
}

log "=== Watcher gestart ==="

# Haal lijst van alle video mappen op
VIDEO_IDS=$($RCLONE lsd "$AROLL_BASE" --config "$CONFIG" 2>/dev/null | awk '{print $NF}')

if [ -z "$VIDEO_IDS" ]; then
  log "Geen video mappen gevonden in 04_A-Roll"
  exit 0
fi

for VIDEO_ID in $VIDEO_IDS; do
  log "Check: $VIDEO_ID"

  # Sla over als al verwerkt
  if grep -q "^${VIDEO_ID}:done$" "$STATE_FILE" 2>/dev/null; then
    log "  → Al verwerkt, overgeslagen"
    continue
  fi

  # Sla over als finale video al bestaat
  FINAL_EXISTS=$($RCLONE ls "$FINAL_BASE/${VIDEO_ID}_FINAL.mp4" --config "$CONFIG" 2>/dev/null)
  if [ -n "$FINAL_EXISTS" ]; then
    log "  → Finale video bestaat al, markeer als done"
    echo "${VIDEO_ID}:done" >> "$STATE_FILE"
    continue
  fi

  # Check of scene1.mp4 aanwezig is
  SCENE1=$($RCLONE ls "$AROLL_BASE/$VIDEO_ID/scene1.mp4" --config "$CONFIG" 2>/dev/null)
  SCENE3=$($RCLONE ls "$AROLL_BASE/$VIDEO_ID/scene3.mp4" --config "$CONFIG" 2>/dev/null)

  if [ -n "$SCENE1" ] && [ -n "$SCENE3" ]; then
    log "  → Beide A-roll clips aanwezig! Start pipeline voor $VIDEO_ID"
    send_telegram "🎬 A-roll clips gevonden voor $VIDEO_ID — pipeline gestart..."

    # Download A-roll clips lokaal
    WORK_DIR="/tmp/aroll_${VIDEO_ID}_$$"
    mkdir -p "$WORK_DIR"
    $RCLONE copy "$AROLL_BASE/$VIDEO_ID/scene1.mp4" "$WORK_DIR/" --config "$CONFIG" 2>/dev/null
    $RCLONE copy "$AROLL_BASE/$VIDEO_ID/scene3.mp4" "$WORK_DIR/" --config "$CONFIG" 2>/dev/null

    # Start pipeline met A-roll clips als pre-rendered scenes
    AROLL_SCENE1="$WORK_DIR/scene1.mp4"
    AROLL_SCENE3="$WORK_DIR/scene3.mp4"

    if bash "$PIPELINE" "$VIDEO_ID" \
        --aroll-scene1 "$AROLL_SCENE1" \
        --aroll-scene3 "$AROLL_SCENE3" \
        >> "$LOG_FILE" 2>&1; then
      log "  ✅ Pipeline succesvol voor $VIDEO_ID"
      echo "${VIDEO_ID}:done" >> "$STATE_FILE"
      send_telegram "✅ Video klaar: $VIDEO_ID — check Google Drive!"
    else
      log "  ❌ Pipeline mislukt voor $VIDEO_ID (exit code $?)"
      send_telegram "❌ Pipeline mislukt voor $VIDEO_ID — check de logs"
    fi

    # Ruim werkmap op
    rm -rf "$WORK_DIR"

  elif [ -n "$SCENE1" ] && [ -z "$SCENE3" ]; then
    log "  → scene1.mp4 aanwezig, wacht nog op scene3.mp4"
    send_telegram "⏳ $VIDEO_ID: scene1.mp4 ontvangen, wacht nog op scene3.mp4"

  elif [ -z "$SCENE1" ] && [ -n "$SCENE3" ]; then
    log "  → scene3.mp4 aanwezig, wacht nog op scene1.mp4"
    send_telegram "⏳ $VIDEO_ID: scene3.mp4 ontvangen, wacht nog op scene1.mp4"

  else
    log "  → Nog geen A-roll clips"
  fi

done

log "=== Watcher klaar ==="
