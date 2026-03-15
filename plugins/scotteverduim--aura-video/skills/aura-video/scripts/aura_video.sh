#!/bin/bash
# aura_video.sh - Complete Aura Creatine video generator
# Gebruik: aura_video.sh <script_id>
# Voorbeeld: aura_video.sh week1_day1_vid1
set -e

SCRIPT_ID="${1}"
if [ -z "$SCRIPT_ID" ]; then
  echo "❌ Gebruik: aura_video.sh <script_id> [--aroll-scene1 <pad>] [--aroll-scene3 <pad>]" >&2
  echo "   Voorbeeld: aura_video.sh week1_day1_vid1" >&2
  exit 1
fi

# Optionele pre-rendered A-roll clips (meegegeven door aroll_watcher.sh)
AROLL_SCENE1_PATH=""
AROLL_SCENE3_PATH=""
shift
while [ $# -gt 0 ]; do
  case "$1" in
    --aroll-scene1) AROLL_SCENE1_PATH="$2"; shift 2 ;;
    --aroll-scene3) AROLL_SCENE3_PATH="$2"; shift 2 ;;
    *) shift ;;
  esac
done

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RCLONE_CONFIG="$HOME/.gdrive-rclone.ini"
GDRIVE_BASE="manus_google_drive:Aura Creatine"
WORK_DIR="/tmp/aura_video_${SCRIPT_ID}_$$"
PYTHON="$HOME/.openclaw-workspace/skills/auraveo/venv/bin/python3"
FFMPEG="/usr/local/Cellar/ffmpeg/8.0.1_4/bin/ffmpeg"
mkdir -p "$WORK_DIR"
echo "📁 Werkmap: $WORK_DIR"

# ============================================================
# Stap 1: JSON script ophalen van Google Drive
# ============================================================
echo ""
echo "📖 Script ophalen: $SCRIPT_ID"
JSON_FILE="$WORK_DIR/script.json"
/usr/local/bin/rclone copy "$GDRIVE_BASE/Content Pipeline/01_Scripts/${SCRIPT_ID}.json" "$WORK_DIR/" --config "$RCLONE_CONFIG" 2>/dev/null
mv "$WORK_DIR/${SCRIPT_ID}.json" "$JSON_FILE" 2>/dev/null || true
if [ ! -f "$JSON_FILE" ]; then
  echo "❌ Script niet gevonden: Content Pipeline/01_Scripts/${SCRIPT_ID}.json" >&2
  exit 1
fi
echo "✅ Script geladen"

# ============================================================
# Stap 2: Kristina base image ophalen
# ============================================================
echo ""
echo "🖼️  Kristina base image ophalen..."
KRISTINA_IMAGE_PATH=$(python3 -c "import json; d=json.load(open('$JSON_FILE')); print(d['assets']['kristina_base_image'])")
KRISTINA_LOCAL="$WORK_DIR/kristina_base.png"
/usr/local/bin/rclone copy "$GDRIVE_BASE/$KRISTINA_IMAGE_PATH" "$WORK_DIR/" --config "$RCLONE_CONFIG" 2>/dev/null
KRISTINA_FILENAME=$(basename "$KRISTINA_IMAGE_PATH")
[ -f "$WORK_DIR/$KRISTINA_FILENAME" ] && mv "$WORK_DIR/$KRISTINA_FILENAME" "$KRISTINA_LOCAL"
if [ ! -f "$KRISTINA_LOCAL" ]; then
  echo "⚠️  Kristina base image niet gevonden, A-roll wordt B-roll" >&2
fi

# ============================================================
# Stap 3: Voiceover MP3 ophalen
# ============================================================
echo ""
echo "🎤 Voiceover ophalen..."
VOICEOVER_PATH=$(python3 -c "import json; d=json.load(open('$JSON_FILE')); print(d['assets']['voiceover_mp3'])")
VOICEOVER_LOCAL="$WORK_DIR/voiceover.mp3"
/usr/local/bin/rclone copy "$GDRIVE_BASE/$VOICEOVER_PATH" "$WORK_DIR/" --config "$RCLONE_CONFIG" 2>/dev/null
VOICEOVER_FILENAME=$(basename "$VOICEOVER_PATH")
[ -f "$WORK_DIR/$VOICEOVER_FILENAME" ] && mv "$WORK_DIR/$VOICEOVER_FILENAME" "$VOICEOVER_LOCAL"
if [ -f "$VOICEOVER_LOCAL" ]; then
  echo "✅ Voiceover geladen: $(du -h "$VOICEOVER_LOCAL" | cut -f1)"
else
  echo "⚠️  Voiceover niet gevonden"
fi

# ============================================================
# Stap 4: Scenes genereren
# ============================================================
echo ""
echo "🎬 Scenes genereren..."
SCENE_COUNT=$(python3 -c "import json; d=json.load(open('$JSON_FILE')); print(len(d['scenes']))")
AIML_API_KEY=$(grep AIML_API_KEY "$HOME/.openclaw/.env" 2>/dev/null | cut -d= -f2 | tr -d '"' | head -1)

for i in $(seq 0 $((SCENE_COUNT - 1))); do
  SCENE_NUM=$((i + 1))
  SCENE_TYPE=$(python3 -c "import json; d=json.load(open('$JSON_FILE')); print(d['scenes'][$i]['type'])")
  SCENE_PROMPT=$(python3 -c "import json; d=json.load(open('$JSON_FILE')); print(d['scenes'][$i]['prompt'])")
  SCENE_DURATION=$(python3 -c "import json; d=json.load(open('$JSON_FILE')); print(d['scenes'][$i].get('duration_seconds', 8))")
  SCENE_OUTPUT="$WORK_DIR/scene${SCENE_NUM}.mp4"

  echo ""
  echo "  Scene $SCENE_NUM ($SCENE_TYPE): $SCENE_PROMPT"

  if [ "$SCENE_TYPE" = "animation" ]; then
    # Animation: render via Remotion (correcte tekst, geen AI hallucinaties)
    echo "  → Remotion animatie render..."
    REMOTION_COMPOSITION=$(python3 -c "import json; d=json.load(open('$JSON_FILE')); print(d['scenes'][$i].get('remotion_composition','BarChart'))")
    REMOTION_PROPS=$(python3 -c "import json; d=json.load(open('$JSON_FILE')); print(json.dumps(d['scenes'][$i].get('remotion_props',{})))")
    bash "$HOME/aura-remotion/render_animation.sh" "$REMOTION_COMPOSITION" "$REMOTION_PROPS" "$SCENE_OUTPUT" 2>&1
    if [ -f "$SCENE_OUTPUT" ]; then
      echo "  ✅ Scene $SCENE_NUM Remotion animatie klaar"
    else
      echo "  ⚠️  Remotion mislukt, fallback naar Gemini"
      "$PYTHON" "$HOME/.openclaw-workspace/skills/auraveo/gemini_text2video.py" "$SCENE_DURATION" "$SCENE_PROMPT"
      GENERATED=$(ls /tmp/aura_veo_*.mp4 2>/dev/null | sort -t_ -k3 -n | tail -1)
      [ -n "$GENERATED" ] && mv "$GENERATED" "$SCENE_OUTPUT"
    fi

  elif [ "$SCENE_TYPE" = "a-roll" ]; then
    # A-roll: gebruik pre-rendered clip als die meegegeven is, anders AIML
    if [ "$SCENE_NUM" = "1" ] && [ -n "$AROLL_SCENE1_PATH" ] && [ -f "$AROLL_SCENE1_PATH" ]; then
      echo "  → Pre-rendered A-roll clip gebruiken (scene 1)..."
      cp "$AROLL_SCENE1_PATH" "$SCENE_OUTPUT"
      echo "  ✅ A-roll scene 1 geladen"
    elif [ "$SCENE_NUM" = "3" ] && [ -n "$AROLL_SCENE3_PATH" ] && [ -f "$AROLL_SCENE3_PATH" ]; then
      echo "  → Pre-rendered A-roll clip gebruiken (scene 3)..."
      cp "$AROLL_SCENE3_PATH" "$SCENE_OUTPUT"
      echo "  ✅ A-roll scene 3 geladen"
    else
    # A-roll: image-to-video via AIML met publieke Google Drive URL
    echo "  → AIML image-to-video (Kristina)..."
    # Gebruik vaste CDN URL voor Kristina (Google Drive links worden niet geaccepteerd door AIML)
    # CDN URL wordt bepaald op basis van de kristina_base_image in het JSON script
    KRISTINA_CDN_URL=$(python3 -c "
import json
d=json.load(open('$JSON_FILE'))
img=d['assets'].get('kristina_base_image','')
urls={
  'Brand Kit/kristina_photo_1_morning_routine.png': 'https://files.manuscdn.com/user_upload_by_module/session_file/310519663194524829/avZggANHVRChDGPg.png',
  'Brand Kit/kristina_photo_2_post_workout.png': 'https://files.manuscdn.com/user_upload_by_module/session_file/310519663194524829/avZggANHVRChDGPg.png',
  'Brand Kit/kristina_photo_3_work_focus.png': 'https://files.manuscdn.com/user_upload_by_module/session_file/310519663194524829/avZggANHVRChDGPg.png',
  'Brand Kit/kristina_photo_4_outdoor_wellness.png': 'https://files.manuscdn.com/user_upload_by_module/session_file/310519663194524829/avZggANHVRChDGPg.png',
  'Brand Kit/kristina_photo_5_product_hero.png': 'https://files.manuscdn.com/user_upload_by_module/session_file/310519663194524829/avZggANHVRChDGPg.png',
}
print(urls.get(img, 'https://files.manuscdn.com/user_upload_by_module/session_file/310519663194524829/avZggANHVRChDGPg.png'))
" 2>/dev/null)
    if [ -n "$KRISTINA_CDN_URL" ]; then
      echo "  🖼️  Kristina URL: $KRISTINA_CDN_URL"
      # Geef output path direct mee — geen globbing op /tmp nodig
      "$PYTHON" "$HOME/.openclaw-workspace/skills/auraveo/aiml_img2video.py" \
        "$SCENE_DURATION" "$SCENE_PROMPT" "$KRISTINA_CDN_URL" "$SCENE_OUTPUT" 2>&1
    fi
    # Fallback naar Gemini als AIML mislukt of output ontbreekt
    if [ ! -f "$SCENE_OUTPUT" ]; then
      echo "  ⚠️  AIML mislukt, fallback naar Gemini text-to-video"
      GEMINI_OUT="/tmp/aura_gemini_scene${SCENE_NUM}_$$.mp4"
      "$PYTHON" "$HOME/.openclaw-workspace/skills/auraveo/gemini_text2video.py" \
        "$SCENE_DURATION" "$SCENE_PROMPT" "$GEMINI_OUT" 2>&1
      [ -f "$GEMINI_OUT" ] && mv "$GEMINI_OUT" "$SCENE_OUTPUT"
    fi
    fi  # einde pre-rendered vs AIML check

  else
    # B-roll: text-to-video via Gemini
    echo "  → Gemini text-to-video..."
    "$PYTHON" "$HOME/.openclaw-workspace/skills/auraveo/gemini_text2video.py" "$SCENE_DURATION" "$SCENE_PROMPT"
    GENERATED=$(ls /tmp/aura_veo_*.mp4 2>/dev/null | sort -t_ -k3 -n | tail -1)
    [ -n "$GENERATED" ] && [ -f "$GENERATED" ] && mv "$GENERATED" "$SCENE_OUTPUT"
  fi

  if [ ! -f "$SCENE_OUTPUT" ]; then
    echo "  ❌ Scene $SCENE_NUM generatie mislukt" >&2
    rm -rf "$WORK_DIR"
    exit 1
  fi
  echo "  ✅ Scene $SCENE_NUM klaar: $SCENE_OUTPUT"
done

# ============================================================
# Stap 5: Scenes normaliseren en samenvoegen met FFmpeg
# ============================================================
echo ""
echo "✂️  Scenes normaliseren en samenvoegen..."

# Normaliseer elke scene naar 1080x1920, 30fps, H.264 (zelfde codec voor alle scenes)
NORM_CONCAT="$WORK_DIR/concat_norm.txt"
> "$NORM_CONCAT"

for i in $(seq 1 $SCENE_COUNT); do
  SCENE_IN="$WORK_DIR/scene${i}.mp4"
  SCENE_NORM="$WORK_DIR/scene${i}_norm.mp4"
  if [ -f "$SCENE_IN" ]; then
    echo "  Normaliseren scene $i..."
    $FFMPEG -y -i "$SCENE_IN" \
      -vf "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=black,setsar=1,fps=30" \
      -c:v libx264 -preset fast -crf 18 -pix_fmt yuv420p \
      -an "$SCENE_NORM" 2>/dev/null
    if [ -f "$SCENE_NORM" ]; then
      echo "file '$SCENE_NORM'" >> "$NORM_CONCAT"
      echo "  ✅ Scene $i genormaliseerd: $(du -h "$SCENE_NORM" | cut -f1)"
    fi
  fi
done

MERGED_VIDEO="$WORK_DIR/merged.mp4"
$FFMPEG -y -f concat -safe 0 -i "$NORM_CONCAT" -c copy "$MERGED_VIDEO" 2>/dev/null
echo "✅ Scenes samengevoegd: $(du -h "$MERGED_VIDEO" | cut -f1)"

# ============================================================
# Stap 6: Voiceover toevoegen
# ============================================================
echo ""
echo "🎵 Audio toevoegen..."
FINAL_VIDEO="$WORK_DIR/${SCRIPT_ID}_FINAL.mp4"

if [ -f "$VOICEOVER_LOCAL" ]; then
  $FFMPEG -y -i "$MERGED_VIDEO" -i "$VOICEOVER_LOCAL" \
    -map 0:v -map 1:a \
    -c:v copy -c:a aac \
    -shortest \
    "$FINAL_VIDEO" 2>&1 | tail -3
else
  cp "$MERGED_VIDEO" "$FINAL_VIDEO"
fi
echo "✅ Finale video: $FINAL_VIDEO ($(du -h "$FINAL_VIDEO" | cut -f1))"

# ============================================================
# Stap 7: Upload naar Google Drive
# ============================================================
echo ""
echo "☁️  Uploaden naar Google Drive..."
/usr/local/bin/rclone copy "$FINAL_VIDEO" "$GDRIVE_BASE/Content Pipeline/03_Final_Videos/" --config "$RCLONE_CONFIG" 2>/dev/null
echo "✅ Geüpload naar Content Pipeline/03_Final_Videos/${SCRIPT_ID}_FINAL.mp4"

# ============================================================
# Stap 8: Output voor OpenClaw (MEDIA: regel voor auto-attach)
# ============================================================
echo ""
echo "🎉 Video klaar!"
echo "MEDIA:$FINAL_VIDEO"

# Cleanup (bewaar finale video)
find "$WORK_DIR" -name "scene*.mp4" -delete 2>/dev/null
find "$WORK_DIR" -name "merged.mp4" -delete 2>/dev/null
