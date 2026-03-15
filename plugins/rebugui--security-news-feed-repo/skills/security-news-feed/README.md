# Security News Feed 📰

> 한국어 보안 뉴스 자동 수집 및 요약 시스템

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

## ✨ 주요 기능

- **11개 한국 보안 소스**: KRCERT, NCSC, 보호나라, Dailysec, BoanNews 등
- **AI 자동 요약**: Gemini API 기반 한국어 뉴스 요약
- **다중 발행 플랫폼**: Notion, Tistory 동시 발행
- **키워드 분석**: 보안 트렌드 자동 분석
- **시간별 자동 실행**: Cron 기반 자동화

## 🚀 설치

```bash
git clone https://github.com/rebugui/security-news-feed.git
cd security-news-feed
pip install -r requirements.txt
```

## ⚙️ 환경 설정

```bash
# .env 파일 생성
cat > .env << 'ENVEOF'
GEMINI_API_KEY=your-gemini-api-key
NOTION_API_KEY=your-notion-api-key
NOTION_DATABASE_ID=your-database-id
TISTORY_APP_ID=your-app-id        # 선택
TISTORY_SECRET_KEY=your-secret    # 선택
ENVEOF
```

### API 키 발급처
- **Gemini API**: https://aistudio.google.com/apikey
- **Notion Integration**: https://www.notion.so/my-integrations
- **Tistory API**: https://www.tistory.com/guide/api/manage

## 📖 사용법

### 수동 실행

```bash
# 전체 파이프라인 실행
python3 security_news_aggregator.py

# 개별 모듈 실행
python3 modules/crawlers/krcert.py
python3 modules/analysis/analyze_keywords.py
```

### Cron 설정 (자동 실행)

```bash
# 매시간 실행
crontab -e

# 추가
0 * * * * cd ~/.openclaw/workspace/skills/security-news-feed && python3 security_news_aggregator.py >> logs/cron.log 2>&1
```

## 📊 지원 뉴스 소스

| 소스 | 유형 | 주기 |
|------|------|------|
| KRCERT | RSS | 실시간 |
| NCSC | RSS | 실시간 |
| 보호나라 (Boho) | 웹 크롤링 | 일일 |
| Dailysec | RSS | 실시간 |
| BoanNews | RSS | 실시간 |
| AhnLab | RSS | 실시간 |
| KISA | 웹 크롤링 | 일일 |
| SK Shieldus | RSS | 실시간 |
| Hacker News | API | 실시간 |
| Google News | API | 실시간 |
| arXiv Security | API | 주간 |

## 🔧 고급 설정

```python
# config.py에서 설정
CRAWLER_CONFIG = {
    'timeout': 30,
    'max_retries': 3,
    'cache_enabled': True,
    'cache_ttl': 3600,  # 1시간
    'concurrent_limit': 5
}
```

## 📝 출력 예시

### Notion 발행
- 제목: [요약] 보안 뉴스 (2026-03-09)
- 태그: #보안 #취약점 #KRCERT
- 요약: 3줄 요약
- 원문 링크

### Tistory 발행
- 블로그 포스트 형식
- 마크다운 지원
- 이미지 자동 업로드

## 📈 통계

```bash
# 수집 통계 확인
python3 -c "from modules.log_utils import get_stats; print(get_stats())"
```

## 🤝 기여하기

새로운 뉴스 소스 추가를 환영합니다!

1. `modules/crawlers/`에 새 크롤러 추가
2. `config.py`에 소스 등록
3. Pull Request 제출

## 📝 라이선스

[GNU Affero General Public License v3.0](LICENSE)

---

Made with 🦞 by [rebugui](https://github.com/rebugui)
