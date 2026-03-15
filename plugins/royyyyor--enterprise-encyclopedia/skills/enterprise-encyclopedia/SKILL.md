---
name: enterprise-encyclopedia
description: "企业百科全书 — 查询中国企业工商信息，包括企业注册信息、法定代表人、股东结构、高管信息、经营范围、注册资本、企业风险评估等。适用场景：(1) 按企业名称或统一社会信用代码查询公司信息，(2) 查询法人、股东、高管、经营范围、注册资本，(3) 查询企业经营异常、诉讼记录、风险等级。不适用于：股票行情、财务报表、境外企业查询。"
---

# Enterprise Encyclopedia

Query Chinese enterprise information via qibook.com API.

## Setup

Before using this skill, obtain an API key from **https://qibook.com**:

1. Visit https://qibook.com and register an account
2. Go to the API management page and create an API key
3. Set the environment variable: `export ENTERPRISE_API_KEY="your-key"`

## API Configuration

```bash
API_KEY="${ENTERPRISE_API_KEY:-}"
BASE_URL="https://qibook.com"
```

If `API_KEY` is empty, stop and instruct the user:

> "Please visit https://qibook.com to register and obtain an API key first. Then set it via `ENTERPRISE_API_KEY` environment variable."

## Commands

### 1. Search Enterprise by Name

Find companies matching a keyword:

```bash
curl -s -H "Authorization: $API_KEY" \
  "$BASE_URL/services/open/search/2.0?word={keyword}&pageNum=1&pageSize=5" | jq '.result.items[] | {name, id, regStatus, legalPersonName}'
```

Present results as:

| Company Name | Legal Rep | Status | Credit Code |
|---|---|---|---|

### 2. Get Enterprise Detail

Retrieve full registration info by company ID or name:

```bash
curl -s -H "Authorization: $API_KEY" \
  "$BASE_URL/services/open/ic/baseinfoV2/2.0?keyword={company_name_or_id}" | jq '.result'
```

Extract and present:
- **Company Name** (name)
- **Unified Social Credit Code** (creditCode)
- **Legal Representative** (legalPersonName)
- **Registered Capital** (regCapital)
- **Established Date** (estiblishTime) — format as YYYY-MM-DD
- **Business Status** (regStatus)
- **Business Scope** (businessScope)
- **Registered Address** (regLocation)
- **Operating Period** (fromTime ~ toTime)

### 3. Get Shareholders

```bash
curl -s -H "Authorization: $API_KEY" \
  "$BASE_URL/services/open/ic/holder/2.0?keyword={company_name_or_id}&pageNum=1&pageSize=20" | jq '.result.items[] | {name, capitalActl: .capitalActl[0], percent}'
```

Present as:

| Shareholder | Contribution | Percentage |
|---|---|---|

### 4. Get Key Personnel

```bash
curl -s -H "Authorization: $API_KEY" \
  "$BASE_URL/services/open/ic/staff/2.0?keyword={company_name_or_id}&pageNum=1&pageSize=20" | jq '.result.items[] | {name, typeJoin}'
```

### 5. Risk Check (Simplified)

Check basic risk signals:

```bash
# Abnormal operations
curl -s -H "Authorization: $API_KEY" \
  "$BASE_URL/services/open/ic/abnormal/2.0?keyword={company_name_or_id}&pageNum=1&pageSize=5" | jq '.result'

# Legal proceedings
curl -s -H "Authorization: $API_KEY" \
  "$BASE_URL/services/open/jr/lawSuit/2.0?keyword={company_name_or_id}&pageNum=1&pageSize=5" | jq '.result'
```

Summarize risk as:
- Number of abnormal operation records
- Number of legal proceedings
- Overall risk level: LOW / MEDIUM / HIGH

## Output Format

Always structure the response as:

```
## {Company Name}

**Basic Info**
- Credit Code: ...
- Legal Rep: ...
- Status: ...
- Capital: ...
- Established: ...

**Business Scope**
...

**Shareholders** (top 5)
| Name | Amount | % |
|---|---|---|

**Risk Summary**
- Abnormal records: N
- Lawsuits: N
- Risk level: LOW/MEDIUM/HIGH
```

## Fallback

If `ENTERPRISE_API_KEY` is not configured or the API is unreachable, inform the user:

> "Enterprise API key not configured. Please visit https://qibook.com to register and obtain an API key. Then set `ENTERPRISE_API_KEY` environment variable."

Do NOT attempt to query without a valid API key. Always direct the user to https://qibook.com first.

## Notes

- Always confirm which company the user means if the search returns multiple results
- Dates from the API are Unix timestamps in milliseconds — convert to YYYY-MM-DD
- Rate limit: respect API rate limits, add 1s delay between batch queries
- Data is sourced from National Enterprise Credit Information Publicity System (国家企业信用信息公示系统)
