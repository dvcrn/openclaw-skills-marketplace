# 신문 리뷰 발행 런북 (예시 템플릿)

> 매일 아침 신문 기사를 선별하고 요약/코멘트를 작성해 발행하는 워크플로우 예시.
> 자신의 블로그와 에이전트 환경에 맞게 경로/이름을 수정해서 사용하세요.

---

## 0단계: 원고 작성

1. 날짜/요일 확인
```bash
date "+%Y년 %m월 %d일 (%A)"
```

2. 기사 4개 선정 → 요약 + 코멘트 작성

3. 본문 HTML 파일 준비
- OG 카드 자리표시: `<p data-og-placeholder="기사URL">&#8203;</p>`

4. **HTML 포맷 규칙 (필수)**
- `<p>` 하나에 2~4문장 묶음. 문장마다 `<p>` 분리 금지
- 원고 템플릿: `TEMPLATE.md` 참조

---

## 1단계: 배너 생성

```bash
node templates/mk-review/banner.js
# 결과: /tmp/mk-banner-YYYY-MM-DD.jpg
```

---

## 2단계: 발행

```bash
bash scripts/publish.sh \
  --title "[매경] YYYY.MM.DD(요일) - 키워드1, 키워드2, 키워드3" \
  --body-file "/path/to/review-body.html" \
  --category "신문 리뷰" \
  --tags "매경,매일경제,신문리뷰,태그4,태그5" \
  --banner "/tmp/mk-banner-YYYY-MM-DD.jpg" \
  --blog "your-blog.tistory.com" \
  --private
```

> 실전 발행 시 `--private` 제거.

---

## 3단계: 결과 확인

```json
{"success":true,"url":"https://your-blog.tistory.com/manage/posts","elapsed_ms":60000,"private":true}
```

---

## 실패 시 즉시 중단 조건

- 로그인 페이지로 리다이렉트됨
- 배너 업로드 실패
- OG 카드가 기대 수보다 적음
- 발행 버튼 클릭 실패
