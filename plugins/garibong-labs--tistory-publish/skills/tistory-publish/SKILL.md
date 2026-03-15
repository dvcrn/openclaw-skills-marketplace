---
name: tistory-publish
description: "Automate Tistory blog publishing via agent-browser (Playwright CLI). Supports any post format — handles TinyMCE editor manipulation, OG card insertion, banner upload, tag registration, category setting, and representative image selection. Includes template examples (newspaper review, simple post). Works around Tistory's isTrusted event filtering."
---

# Tistory Publish

티스토리 블로그 범용 자동 발행 스킬. 어떤 형식의 글이든 agent-browser로 자동 발행할 수 있습니다.

Tistory Open API 종료(2024.02) 이후 유일한 자동화 경로인 브라우저 자동화를 제공합니다.

## 전제 조건

- [agent-browser](https://github.com/anthropics/agent-browser) CLI + 프로필 (Kakao 로그인 완료)
- Node.js 18+ (배너 생성 시, 선택)

## 구조

```
tistory-publish/
├── SKILL.md                     # 이 파일
├── scripts/
│   ├── tistory-publish.js       # 코어 — 에디터 조작 함수 모음
│   └── publish.sh               # 범용 발행 스크립트
└── templates/
    ├── mk-review/               # 예시: 신문 리뷰 (배너+OG 4개)
    │   ├── RUNBOOK.md
    │   ├── TEMPLATE.md
    │   ├── banner.js
    │   ├── deep-dive.js
    │   └── IMAGE-MAP.md
    └── simple-post/             # 예시: 단순 글 발행
        └── RUNBOOK.md
```

## 빠른 시작

```bash
# 가장 단순한 발행
bash scripts/publish.sh \
  --title "글 제목" \
  --body-file body.html \
  --category "카테고리명" \
  --blog "your-blog.tistory.com"

# 배너 + 태그 + 비공개
bash scripts/publish.sh \
  --title "글 제목" \
  --body-file body.html \
  --category "카테고리명" \
  --banner /tmp/banner.jpg \
  --tags "태그1,태그2,태그3" \
  --private
```

## 발행 스크립트 옵션 (`publish.sh`)

| 옵션 | 필수 | 설명 |
|------|------|------|
| `--title` | ✅ | 글 제목 |
| `--body-file` | ✅ | 본문 HTML 파일 경로 |
| `--category` | ✅ | 카테고리 이름 (에디터에 표시되는 이름 그대로) |
| `--tags` | | 쉼표 구분 태그 목록 |
| `--banner` | | 배너 이미지 파일 경로 |
| `--blog` | | 블로그 도메인 (기본: tistory.com 첫 번째 블로그) |
| `--helper` | | tistory-publish.js 경로 (기본: scripts/ 내) |
| `--private` | | 비공개 발행 |

## 자동 처리 항목

스크립트가 순서대로 처리:

1. 새 글 페이지 열기
2. JS 헬퍼 함수 주입
3. 카테고리 선택 (ARIA combobox → Playwright click)
4. 제목 입력 (base64 디코딩으로 한글 처리)
5. 본문 HTML 삽입
6. 배너 이미지 업로드 (첨부→사진 메뉴 → file input)
7. OG 카드 생성 (placeholder URL → Enter 키 → 카드 렌더링)
8. 대표이미지 설정
9. 태그 등록
10. 발행 (공개/비공개)

## 본문 HTML 작성 규칙

- `<p data-ke-size="size16">` 태그 사용
- 단락 = 여러 문장 묶음 (`<p>` 하나에 2~4문장)
- OG 카드 위치: `<p data-og-placeholder="URL">&#8203;</p>`
- 구분선: `<hr contenteditable="false" data-ke-type="horizontalRule" data-ke-style="style1">`

## 템플릿 추가하기

`templates/` 디렉토리에 새 폴더를 만들어 자신만의 워크플로우를 추가할 수 있습니다:

```
templates/my-template/
├── RUNBOOK.md       # 발행 순서
├── TEMPLATE.md      # 원고 작성 템플릿
└── banner.js        # 배너 생성 스크립트 (선택)
```

## 주요 JS 함수 (`tistory-publish.js`)

### 콘텐츠
- `insertContent(html)` — TinyMCE에 HTML 삽입
- `buildBlogHTML({intro, articles})` — 구조화된 데이터 → HTML 변환

### OG 카드
- `getOGPlaceholders()` — placeholder URL 목록
- `prepareOGPlaceholder(url)` — placeholder → URL 텍스트 교체
- `verifyOGCard(url)` — 카드 렌더링 확인

### 메타데이터
- `setTags(tags[])` — 태그 등록
- `setRepresentImageFromEditor()` — 대표이미지 설정

### 배너
- `verifyBannerUpload()` — 업로드 확인

## 알려진 제약

- `isTrusted=false` 이벤트 무시 → OG/태그에 우회 로직 필요
- 카테고리가 ARIA combobox → Playwright click 필요
- 대표이미지 셀렉터가 Tistory 업데이트마다 변경 가능

## 변경 이력

### v4.0.0 (2026-03-07)
- **범용 스킬로 재설계**: 매경 리뷰 전용 → 어떤 포맷이든 발행 가능
- 범용 `publish.sh` 스크립트 추가 (`--category`, `--blog` 등 인자)
- 매경 리뷰를 `templates/mk-review/` 예시로 이동
- 단순 발행 예시 `templates/simple-post/` 추가

### v3.0.0 (2026-03-07)
- OpenClaw Playwright → agent-browser 전환
- 카테고리: JS eval → Playwright native ARIA combobox click
- 배너: base64 chunk → agent-browser upload
