#!/bin/bash
# /prep-video <script_id>
# Controleert alle assets voor een video en start de pipeline als alles aanwezig is.

# ── Configuratie ────────────────────────────────────────────────────────────
SCRIPT_ID="${1:-}"
RCLONE="/usr/local/bin/rclone"
JQ="/usr/local/bin/jq"
BOT_TOKEN="8501038356:AAHhhywqpA97okbyEsxXmdQYuJXi848Tm3g"
CHAT_ID="1835871910"
GDRIVE="manus_google_drive"
BASE="$GDRIVE:Aura Creatine/Content Pipeline"
SCRIPTS_PATH="$BASE/01_Scripts"
AROLL_PATH="$BASE/04_A-Roll"
VO_PATH="$BASE/02_Assets/voiceovers"
# Voiceover bestandsnaam staat al als 'voiceovers/filename.mp3' in de JSON, dus strip het prefix
VO_PATH_BASE="$BASE/02_Assets"
PIPELINE_SCRIPT="$HOME/.openclaw-workspace/skills/aura-video/scripts/aura_video.sh"
TMP_DIR="/tmp/prep_video_$$"

# ── Helpers ──────────────────────────────────────────────────────────────────
tg_send() {
  local msg="$1"
  curl -s -X POST "https://api.telegram.org/bot${BOT_TOKEN}/sendMessage" \
    -d chat_id="$CHAT_ID" \
    -d parse_mode="Markdown" \
    --data-urlencode "text=${msg}" > /dev/null
}

cleanup() { rm -rf "$TMP_DIR"; }
trap cleanup EXIT

# ── Validatie ────────────────────────────────────────────────────────────────
if [ -z "$SCRIPT_ID" ]; then
  tg_send "❌ Gebruik: /prep-video <script_id>  (bijv. /prep-video week1_day2_vid1)"
  exit 1
fi

tg_send "🔍 Checking assets voor \`$SCRIPT_ID\`..."

mkdir -p "$TMP_DIR"

# ── Stap 1: Download JSON script ─────────────────────────────────────────────
JSON_FILE="$TMP_DIR/${SCRIPT_ID}.json"
if ! $RCLONE copy "$SCRIPTS_PATH/${SCRIPT_ID}.json" "$TMP_DIR/" 2>/dev/null || [ ! -f "$JSON_FILE" ]; then
  tg_send "❌ Script niet gevonden op Google Drive:
$(printf '\`')$SCRIPTS_PATH/${SCRIPT_ID}.json$(printf '\`')

Upload het script eerst naar die locatie."
  exit 1
fi

# ── Stap 2: Parseer JSON ──────────────────────────────────────────────────────
TITLE=$($JQ -r '.meta.title // "Onbekend"' "$JSON_FILE")
NUM_SCENES=$($JQ -r '.scenes | length' "$JSON_FILE")
SCENE_TYPES=$($JQ -r '[.scenes[].type] | join(", ")' "$JSON_FILE")
VO_FILE=$($JQ -r '.assets.voiceover_mp3 // ""' "$JSON_FILE")

# ── Stap 3: Controleer assets ─────────────────────────────────────────────────
MISSING=""

# Voiceover check — VO_FILE bevat al het subpad 'voiceovers/filename.mp3'
if [ -n "$VO_FILE" ]; then
  if ! $RCLONE lsf "$VO_PATH_BASE/$VO_FILE" 2>/dev/null | grep -q .; then
    MISSING="$MISSING
• Voiceover: \`$VO_PATH_BASE/$VO_FILE\`"
  fi
fi

# A-roll check
for CLIP in scene1.mp4 scene3.mp4; do
  if ! $RCLONE lsf "$AROLL_PATH/$SCRIPT_ID/$CLIP" 2>/dev/null | grep -q .; then
    MISSING="$MISSING
• A-roll: \`$AROLL_PATH/$SCRIPT_ID/$CLIP\`"
  fi
done

# ── Stap 4: Rapport en actie ──────────────────────────────────────────────────
SUMMARY="📋 Script: \`$SCRIPT_ID\`
Titel: $TITLE
Scenes: $NUM_SCENES ($SCENE_TYPES)"

if [ -z "$MISSING" ]; then
  tg_send "$SUMMARY

✅ Alle assets aanwezig. Pipeline wordt gestart..."
  bash "$PIPELINE_SCRIPT" "$SCRIPT_ID"
else
  tg_send "$SUMMARY

❌ Ontbrekende bestanden:$MISSING

Upload deze bestanden naar Google Drive en stuur opnieuw \`/prep-video $SCRIPT_ID\`"
fi
