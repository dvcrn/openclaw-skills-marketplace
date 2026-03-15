#!/usr/bin/env bash
# tistory-publish — 범용 티스토리 발행 스크립트 (agent-browser 기반)
#
# 사용법:
#   bash publish.sh \
#     --title "글 제목" \
#     --body-file "/path/to/body.html" \
#     --category "카테고리명" \
#     [--tags "태그1,태그2,..."] \
#     [--banner "/path/to/banner.jpg"] \
#     [--blog "your-blog.tistory.com"] \
#     [--helper "/path/to/tistory-publish.js"] \
#     [--private]
#
# 필수: --title, --body-file, --category
# 선택: --tags, --banner, --blog(기본: 첫 번째 블로그), --helper, --private

set -euo pipefail

# ── 기본값 ──
TITLE=""
BODY_FILE=""
CATEGORY=""
TAGS=""
BANNER=""
BLOG=""
HELPER=""
PRIVATE=false
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# ── 인자 파싱 ──
while [[ $# -gt 0 ]]; do
  case "$1" in
    --title)     TITLE="$2"; shift 2;;
    --body-file) BODY_FILE="$2"; shift 2;;
    --category)  CATEGORY="$2"; shift 2;;
    --tags)      TAGS="$2"; shift 2;;
    --banner)    BANNER="$2"; shift 2;;
    --blog)      BLOG="$2"; shift 2;;
    --helper)    HELPER="$2"; shift 2;;
    --private)   PRIVATE=true; shift;;
    *) echo "Unknown option: $1"; exit 1;;
  esac
done

[[ -z "$TITLE" ]]     && { echo "ERROR: --title required"; exit 1; }
[[ -z "$BODY_FILE" ]] && { echo "ERROR: --body-file required"; exit 1; }
[[ -z "$CATEGORY" ]]  && { echo "ERROR: --category required"; exit 1; }
[[ ! -f "$BODY_FILE" ]] && { echo "ERROR: body file not found: $BODY_FILE"; exit 1; }
[[ -n "$BANNER" && ! -f "$BANNER" ]] && { echo "ERROR: banner file not found: $BANNER"; exit 1; }

# Helper JS 경로
if [[ -z "$HELPER" ]]; then
  HELPER="$SCRIPT_DIR/tistory-publish.js"
fi
[[ ! -f "$HELPER" ]] && { echo "ERROR: helper JS not found: $HELPER"; exit 1; }

# ── 유틸 ──
ab() { agent-browser "$@" --json 2>/dev/null; }
log() { echo "[$(date +%H:%M:%S)] $*"; }
fail() { echo "ERROR: $*" >&2; exit 1; }

START_MS=$(($(date +%s) * 1000))

# ── Step 1: 새 글 페이지 열기 ──
log "Step 1: 새 글 페이지 열기"
if [[ -n "$BLOG" ]]; then
  NEWPOST_URL="https://${BLOG}/manage/newpost/?type=post"
else
  NEWPOST_URL="https://www.tistory.com/manage/newpost/?type=post"
fi
agent-browser navigate "$NEWPOST_URL" >/dev/null 2>&1
agent-browser wait --fn "typeof tinymce !== 'undefined' && tinymce.activeEditor && tinymce.activeEditor.initialized" 2>/dev/null
log "Step 1: 완료"

# ── Helper JS 주입 ──
log "Injecting helper scripts..."
JS_HELPER_B64=$(python3 -c "import base64,sys;print(base64.b64encode(open(sys.argv[1],'rb').read()).decode('ascii'),end='')" "$HELPER")
ab eval "(()=>{const bytes=Uint8Array.from(atob('${JS_HELPER_B64}'),c=>c.charCodeAt(0));const code=new TextDecoder('utf-8').decode(bytes);const script=document.createElement('script');script.textContent=code;document.head.appendChild(script);return 'ok'})()" >/dev/null 2>&1

# ── Step 2: 카테고리 & 제목 설정 ──
log "Step 2: 카테고리 & 제목 설정"
# 카테고리: Playwright로 ARIA combobox 조작
agent-browser find role combobox click --name '카테고리 선택' >/dev/null 2>&1
sleep 0.5
agent-browser find role option click --name "$CATEGORY" >/dev/null 2>&1
sleep 0.3

# 제목: base64 디코딩으로 한글 처리
TITLE_B64=$(python3 -c "import base64,sys;print(base64.b64encode(sys.argv[1].encode('utf-8')).decode('ascii'),end='')" "$TITLE")
TITLE_RESULT=$(ab eval "(()=>{const t=document.getElementById('post-title-inp');if(!t)return 'no el';const bytes=Uint8Array.from(atob('${TITLE_B64}'),c=>c.charCodeAt(0));const title=new TextDecoder('utf-8').decode(bytes);t.textContent=title;t.dispatchEvent(new Event('input',{bubbles:true}));return 'ok'})()")
TITLE_OK=$(echo "$TITLE_RESULT" | python3 -c "import sys,json;print(json.load(sys.stdin).get('data',{}).get('result','err'))" 2>/dev/null)
[ "$TITLE_OK" != "ok" ] && fail "title insert failed"
log "Step 2: 완료"

# ── Step 3: 본문 삽입 ──
log "Step 3: 본문 삽입"
BODY_B64=$(python3 -c "import base64,sys;print(base64.b64encode(open(sys.argv[1],'rb').read()).decode('ascii'),end='')" "$BODY_FILE")
ab eval "(()=>{const bytes=Uint8Array.from(atob('${BODY_B64}'),c=>c.charCodeAt(0));const html=new TextDecoder('utf-8').decode(bytes);return insertContent(html);})()" >/dev/null 2>&1
log "Step 3: 완료"

# ── Step 4: 배너 이미지 업로드 (선택) ──
if [[ -n "$BANNER" ]]; then
  log "Step 4: 배너 이미지 업로드"
  agent-browser find role button click --name '첨부' >/dev/null 2>&1
  agent-browser find role menuitem click --name '사진' >/dev/null 2>&1
  agent-browser upload "#openFile" "$BANNER" >/dev/null 2>&1
  sleep 3
  ab eval "verifyBannerUpload()" >/dev/null 2>&1
  log "Step 4: 완료"
else
  log "Step 4: 배너 생략 (--banner 미지정)"
fi

# ── Step 5: OG 카드 생성 ──
log "Step 5: OG 카드 생성"
OG_URLS=$(ab eval "JSON.stringify(getOGPlaceholders())" 2>/dev/null | python3 -c "import sys,json;d=json.load(sys.stdin);urls=d.get('data',{}).get('result',[]); [print(u) for u in (urls if isinstance(urls,list) else [])]" 2>/dev/null)
OG_COUNT=0
while IFS= read -r url; do
  [[ -z "$url" ]] && continue
  log "  - OG 카드 처리 중: $url"
  ab eval "prepareOGPlaceholder('$url')" >/dev/null 2>&1
  sleep 0.5
  agent-browser press Enter >/dev/null 2>&1
  sleep 3
  ab eval "verifyOGCard('$url')" >/dev/null 2>&1
  OG_COUNT=$((OG_COUNT + 1))
done <<< "$OG_URLS"
if [[ $OG_COUNT -gt 0 ]]; then
  ab eval "cleanupOGResiduals()" >/dev/null 2>&1
fi
log "Step 5: 완료"

# ── Step 6: 대표 이미지 설정 ──
log "Step 6: 대표 이미지 설정"
ab eval "setRepresentImageFromEditor()" >/dev/null 2>&1
sleep 1
log "Step 6: 완료"

# ── Step 7: 태그 입력 (선택) ──
if [[ -n "$TAGS" ]]; then
  log "Step 7: 태그 입력"
  IFS=',' read -ra TAG_ARRAY <<< "$TAGS"
  TAG_JSON=$(python3 -c "import json,sys;print(json.dumps(sys.argv[1:]))" "${TAG_ARRAY[@]}")
  ab eval "setTags($TAG_JSON)" >/dev/null 2>&1
  sleep 1
  log "Step 7: 완료"
else
  log "Step 7: 태그 생략 (--tags 미지정)"
fi

# ── Step 8: 발행 ──
log "Step 8: 발행"
if [[ "$PRIVATE" == "false" ]]; then
  # 공개 발행: 공개 라디오 버튼 선택
  ab eval "(()=>{const r=document.getElementById('open20');if(r){r.click();return 'public'}return 'no radio'})()" >/dev/null 2>&1
  sleep 0.3
fi
agent-browser find role button click --name '완료' >/dev/null 2>&1
sleep 3
agent-browser wait --url '/manage/posts' --timeout 30000 >/dev/null 2>&1

END_MS=$(($(date +%s) * 1000))
ELAPSED=$((END_MS - START_MS))
CURRENT_URL=$(agent-browser eval "window.location.href" --json 2>/dev/null | python3 -c "import sys,json;print(json.load(sys.stdin).get('data',{}).get('result',''))" 2>/dev/null)

log "Step 8: 완료 — $CURRENT_URL"
echo "{\"success\":true,\"url\":\"$CURRENT_URL\",\"elapsed_ms\":$ELAPSED,\"private\":$PRIVATE}"
