---
name: mapulse
description: "Daily Korean stock market briefing and AI analysis with DART disclosure alerts. Monitors KOSPI/KOSDAQ indices, tracks a personal watchlist, and delivers morning summaries via Telegram or WhatsApp. Covers index overview, top gainers/losers, foreign net trading, and DART major disclosures. Pay-per-call pricing via ButterSwap cross-chain settlement. Use when: (1) user asks about Korean stocks or 한국 주식, (2) wants daily market briefing or 매일 시황, (3) needs stock price alerts, (4) asks \"why did Samsung drop\" or analysis questions about Korean market, (5) wants DART corporate disclosure summaries."
---

# Mapulse 🇰🇷

Korean stock market AI analyst. Monitor KOSPI/KOSDAQ, track watchlist, deliver briefings, and answer questions about Korean market movements.

## Data Sources (free, no API key)

- **pykrx** (pip install pykrx): KRX official data via Naver Finance backend. Daily OHLCV for all KOSPI/KOSDAQ stocks.
  ```python
  from pykrx import stock
  # Index proxy via ETFs
  df = stock.get_market_ohlcv("20260101", "20260313", "069500")  # KODEX 200 = KOSPI proxy
  df = stock.get_market_ohlcv("20260101", "20260313", "229200")  # KODEX KOSDAQ150
  # Individual stock
  df = stock.get_market_ohlcv("20260301", "20260313", "005930")  # Samsung
  ```
- **DART OpenAPI** (free, key at https://opendart.fss.or.kr):
  `https://opendart.fss.or.kr/api/list.json?crtfc_key=KEY&bgn_de=20260313&pblntf_ty=A`
- **Yahoo Finance** (fallback): `https://query1.finance.yahoo.com/v8/finance/chart/{TICKER}.KS` for KOSPI, `.KQ` for KOSDAQ
- **Naver Finance** (fallback): `https://finance.naver.com/item/main.nhn?code=005930`

Install pykrx if not present: `pip install --break-system-packages pykrx`

## Watchlist Configuration

User watchlist in env var `KOREA_STOCK_WATCHLIST` as comma-separated KRX tickers.
Default: `005930,000660,035420,035720,373220,068270,051910,006400`

Ticker-Name reference (top 20):
```
005930 삼성전자    000660 SK하이닉스   035420 NAVER
035720 카카오      373220 LG에너지솔루션 068270 셀트리온
051910 LG화학     006400 삼성SDI      005380 현대자동차
000270 기아       096770 SK이노베이션  034020 두산에너빌리티
003670 포스코인터내셔널 012330 현대모비스  028260 삼성물산
015760 한국전력    030200 KT          009150 삼성전기
066570 LG전자     003490 대한항공
```

## Daily Morning Briefing

When triggered (cron or manual "한국 시황" / "korea pulse" / "매일 시황"):

1. **Find latest trading date** — check Samsung (005930) has data
2. **Index Overview** — KODEX 200 (KOSPI proxy) + KODEX KOSDAQ150 via pykrx
3. **Top 5 Gainers/Losers** — iterate watchlist + major stocks, rank by change%
4. **Foreign Net Trading** — if KRX investor API available; otherwise note "외국인 데이터 미제공"
5. **DART Disclosures** — if DART_API_KEY configured, fetch today's major filings
6. **AI Analysis** — one paragraph explaining WHY the market moved (connect to macro: oil, USD/KRW, Fed, geopolitics)

Format for Telegram/WhatsApp (clean, emoji-driven):
```
📊 *한국 증시 시황 — 2026년 3월 13일*

*지수 마감*
🔴 KOSPI: 2,485 (-2.1%)
🟢 KOSDAQ: 742 (+0.4%)

*관심 종목*
🔴 삼성전자: ₩182,900 (-2.7%)
🟢 SK하이닉스: ₩198,500 (+1.2%)
🔴 LG에너지솔루션: ₩367,000 (-4.4%)

*상승 TOP 3*
🟢 엔씨소프트 +7.6% | 두산에너빌리티 +2.4% | 한국전력 +1.5%

*하락 TOP 3*
🔴 포스코인터 -9.7% | SK이노 -7.2% | LG에너지 -4.4%

*DART 주요 공시*
• 삼성전자: 타법인 주식 취득 결정 (AI반도체 투자 2조원)
• SK하이닉스: 매출 45% 증가 전망 (HBM 수요)

*AI 분석*
KOSPI 하락은 국제 유가 $100 돌파에 따른 인플레 우려 + 외국인 순매도 영향. 
에너지·화학 섹터 집중 하락. 반면 게임·방산 섹터는 강세. 
내일 미국 CPI 발표 예정 — 변동성 확대 가능성.
```

## Conversational Queries (AI Analysis Mode)

When user asks questions like:
- "삼성 오늘 왜 빠졌어?" / "Why did Samsung drop today?"
- "외국인이 뭘 사고 있어?" / "What are foreigners buying?"
- "KOSPI 내일 어떨 것 같아?" / "What's the KOSPI outlook?"
- "내 포트폴리오 분석해줘" / "Analyze my portfolio"

→ Fetch relevant data via pykrx, combine with recent news context, provide analytical response.
→ Always cite data sources. Never make specific price predictions or guarantee returns.
→ Use 🟢🔴⚪ indicators. Keep responses concise (under 300 words).

## Price Alerts

When user says:
- "삼성 18만원 이하로 떨어지면 알려줘"
- "Alert me if SK Hynix goes above 200,000"
- "NAVER 20만원 돌파하면 알림"

Store as: `ALERT|TICKER|DIRECTION|TARGET|SET_DATE`
Check during heartbeat or cron. Trigger immediately when hit.

## Cron Setup

Morning briefing (8:00 AM KST = 23:00 UTC previous day, Mon-Fri):
```
openclaw cron add "korea-stock-pulse briefing" "0 23 * * 0-4"
```

Alert checks every 30 min during market hours (9:00-15:30 KST):
```
openclaw cron add "korea-stock-pulse alerts" "*/30 0-6 * * 1-5"
```

## Commands

- **"한국 시황"** / **"korea pulse"** — Full daily briefing
- **"관심종목"** / **"watchlist"** — Watchlist with live prices
- **"종목추가 005930"** / **"add 005930"** — Add to watchlist
- **"종목삭제 005930"** / **"remove 005930"** — Remove from watchlist
- **"알림설정 005930 below 180000"** — Set price alert
- **"내 알림"** / **"my alerts"** — List active alerts
- **"분석 005930"** / **"analyse 005930"** — AI analysis of specific stock
- **"공시"** / **"disclosures"** — Today's DART major filings

## Market Hours

KRX trades Mon-Fri, 9:00 AM - 3:30 PM KST.
- Before 9:00: Previous day close, note "장 시작 전"
- After 15:30: Closing data, note "장 마감"
- Weekends/holidays: Last trading day, note "휴장일"

## Regulatory Compliance

This skill provides **information only** (정보 제공). It does NOT:
- Execute trades or place orders
- Promise returns or guarantee profits
- Provide licensed investment advice

Operates under 유사투자자문업 (quasi-investment advisory) guidelines:
- ✅ Market data aggregation and analysis
- ✅ DART disclosure summaries
- ✅ General market commentary
- ❌ No specific buy/sell recommendations with target prices
- ❌ No "guaranteed profit" language
- ❌ No trade execution

## 💰 Payment — 60小时免费 + 按次计费 + ButterSwap结算

### 定价模型

| 阶段 | 说明 |
|---|---|
| **免费体验** | 注册后 **60小时** 内免费使用，上限 **50次** （先到先停） |
| **付费期** | 60小时后按次扣费，**$0.06/次**（Claude成本×2） |
| **最低充值** | **$5 USDC**（≈83次调用） |

所有功能统一单价 $0.06/次。60小时内不限次数不限功能。

### 免费期逻辑

```
用户首次使用时记录:
  TRIAL|user_id|start_time|expires_at(start + 60h)|free_used|free_limit(50)

每次调用:
  if now < expires_at AND free_used < 50 → 免费执行
  if free_used >= 50 OR now >= expires_at:
    if balance >= $0.06 → 扣费执行
    if balance < $0.06 → 提示充值（最低$5）
```

### 充值模式

60小时用完后，用户必须预先充值才能继续使用。

用户说 **"충전"** / **"충值"** / **"top up"** 时：
1. 最低充值 **$5 USDC**（推荐 $5 / $10 / $20）
2. 通过ButterSwap跨链支付（任意链、任意币）
3. 余额到账，按次扣费

### Payment Commands

- **"충전 5"** / **"top up 5"** — 充值$5 USDC（最低）
- **"잔액"** / **"balance"** — 查看余额和免费期剩余时间
- **"사용 내역"** / **"usage"** — 使用记录和费用明细

### ButterSwap充值流程

用户说"충전 10"：

```
💰 Mapulse 충전

충전 금액: $10 USDC
현재 잔액: $0.00

결제 후 잔액: $10.00
약 166회 조회 가능

[⚡ ButterSwap 크로스체인 결제]
  30+체인, 어떤 토큰이든 OK

[💎 Telegram Wallet (TON)]

[🔗 지갑 직접 결제 (USDC)]
```

충전 API (ButterNetwork one-step):
```python
GET https://bs-router-v3.chainservice.io/routeAndSwap?
  fromChainId={user_chain}&toChainId=8453&
  amount={topup_amount}&
  tokenInAddress={user_token}&
  tokenOutAddress=0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913&
  type=exactIn&slippage=100&entrance=agent&
  from={user_wallet}&receiver={SERVICE_WALLET}
```

### 免费期满 + 잔액不足时

```
⏰ 무료 체험 기간이 종료되었습니다.

60시간 동안 XX회 사용하셨습니다.
계속 이용하려면 충전이 필요합니다.

최소 충전: $5 USDC (≈83회)
단가: $0.06/회

→ '충전 5' 입력 시 ButterSwap으로 간편 충전
→ 30+체인, 어떤 토큰이든 결제 가능
```

### Environment Variables

```json
{
  "BUTTERSWAP_WALLET": "0x...",
  "BUTTERSWAP_WEBHOOK": "https://your-server.com/webhook/butterswap"
}
```

## Error Handling

If pykrx fails (KRX maintenance, network issues), fallback to Yahoo Finance (.KS suffix).
If both fail, note "데이터 일시 불가 — 잠시 후 다시 시도합니다" and retry in 5 min.
Never show raw errors to user.
