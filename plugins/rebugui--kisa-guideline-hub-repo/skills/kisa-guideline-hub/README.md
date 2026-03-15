# KISA Guideline Hub 📋

> KISA(한국인터넷진흥원) 및 보호나라 보안 가이드라인 자동 수집 발행 시스템

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)

## ✨ 주요 기능

- **자동 수집**: KISA, 보호나라 최신 보안 가이드라인 자동 감지
- **PDF 다운로드**: 보안 가이드 PDF 자동 다운로드 및 저장
- **Notion 발행**: Notion 데이터베이스에 자동 등록
- **변경 감지**: 새로운/수정된 가이드라인 알림

## 🚀 설치

```bash
git clone https://github.com/rebugui/kisa-guideline-hub.git
cd kisa-guideline-hub
pip install -r requirements.txt
```

## ⚙️ 환경 설정

```bash
# .env 파일 생성
cat > .env << 'ENVEOF'
NOTION_API_KEY=your-notion-api-key
NOTION_DATABASE_ID=your-database-id
ENVEOF
```

## 📖 사용법

### 수동 실행

```bash
# 전체 파이프라인
python3 scripts/publish_guidelines.py

# 수집만
python3 scripts/publish_guidelines.py --collect-only

# 발행만
python3 scripts/publish_guidelines.py --publish-only
```

### Cron 설정 (일일 실행)

```bash
# 매일 오전 9시 실행
crontab -e

# 추가
0 9 * * * cd ~/.openclaw/workspace/skills/kisa-guideline-hub && python3 scripts/publish_guidelines.py >> logs/cron.log 2>&1
```

## 📊 수집 대상

### KISA (한국인터넷진흥원)
- 개인정보 보안 가이드
- 정보보호 실무 가이드
- 클라우드 보안 가이드
- 랜섬웨어 대응 가이드
- 보안성 심의 가이드

### 보호나라 (Boho)
- 정보보호 관리체계 가이드
- 개인정보 처리 시스템 가이드
- 보안 솔루션 도입 가이드

## 🔧 Notion 데이터베이스 스키마

```json
{
  "title": "가이드라인 제목",
  "url": "원문 URL",
  "pdf_url": "PDF 다운로드 링크",
  "source": "KISA | Boho",
  "category": "분류",
  "published_date": "발행일",
  "collected_date": "수집일",
  "status": "New | Updated | Existing"
}
```

## 📝 출력 예시

### Notion 페이지
- 📋 **제목**: [KISA] 개인정보 보안 가이드라인 v2.0
- 🔗 **원문**: https://kisa.or.kr/...
- 📄 **PDF**: [다운로드 링크]
- 🏷️ **분류**: 개인정보보호
- 📅 **발행일**: 2026-03-09
- ✨ **상태**: New

## 🤝 기여하기

새로운 가이드라인 소스 추가를 환영합니다!

## 📝 라이선스

[GNU Affero General Public License v3.0](LICENSE)

---

Made with 🦞 by [rebugui](https://github.com/rebugui)
