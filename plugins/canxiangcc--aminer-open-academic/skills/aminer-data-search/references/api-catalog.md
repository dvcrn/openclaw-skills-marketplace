# AMiner Open Platform API Complete Reference

**Base URL**: `https://datacenter.aminer.cn/gateway/open_platform`  
**Authentication**: All endpoints require both `Authorization: <TOKEN>` and `X-Platform: openclaw` in the request headers.  
**Token**: Log in to the [Console](https://open.aminer.cn/open/board?tab=control) to generate one; replace `<TOKEN>` with your actual token in all curl examples below.

---

## Table of Contents

- [Paper APIs (9)](#paper-apis)
- [Scholar APIs (6)](#scholar-apis)
- [Institution APIs (7)](#institution-apis)
- [Journal APIs (3)](#journal-apis)
- [Patent APIs (3)](#patent-apis)

---

## Paper APIs

### 1. Paper Search

- **URL**: `GET /api/paper/search`
- **Price**: Free
- **Description**: Search by paper title; returns paper ID, title, and DOI.

**Request Parameters:**

| Parameter | Type | Required | Description |
|--------|------|------|------|
| page | number | Yes | Page number (starts at 0; maximum is 0) |
| size | number | No | Items per page |
| title | string | Yes | Paper title keyword |

**Response Fields:**

| Field | Description |
|--------|------|
| id | Paper ID |
| title | Paper title (English) |
| title_zh | Paper title (Chinese) |
| doi | DOI |
| total | Total count |

**curl Example:**
```bash
curl -X GET \
  'https://datacenter.aminer.cn/gateway/open_platform/api/paper/search?page=0&size=5&title=BERT' \
  -H 'Authorization: <TOKEN>' \
  -H 'X-Platform: openclaw'
```

---

### 2. Paper Search Pro

- **URL**: `GET /api/paper/search/pro`
- **Price**: ¥0.01/call
- **Description**: Multi-condition search; supports filtering by keyword, abstract, author, institution, and journal.

**Request Parameters:**

| Parameter | Type | Required | Description |
|--------|------|------|------|
| page | number | No | Page number (starts at 0) |
| size | number | No | Items per page |
| title | string | No | Title keyword |
| keyword | string | No | Keyword |
| abstract | string | No | Abstract keyword |
| author | string | No | Author name |
| org | string | No | Institution name |
| venue | string | No | Journal name |
| order | string | No | Sort field: `year` (descending by year) or `n_citation` (descending by citations); omit for composite ranking |

**Response Fields:**

| Field | Description |
|--------|------|
| id | Paper ID |
| title | Title (English) |
| title_zh | Title (Chinese) |
| doi | DOI |
| total | Total count |

**curl Example:**
```bash
curl -X GET \
  'https://datacenter.aminer.cn/gateway/open_platform/api/paper/search/pro?title=transformer&author=Vaswani&order=n_citation&page=0&size=5' \
  -H 'Authorization: <TOKEN>' \
  -H 'X-Platform: openclaw'
```

---

### 3. Paper QA Search

- **URL**: `POST /api/paper/qa/search`
- **Price**: ¥0.05/call
- **Description**: AI-powered intelligent Q&A search; supports natural language queries and structured keyword search.

**Request Parameters:**

| Parameter | Type | Required | Description |
|--------|------|------|------|
| use_topic | boolean | Yes | Whether to use combined keyword search. When `true`, use topic fields; when `false`, use title/query. |
| topic_high | string | No | Valid when use_topic=true; keywords that must match (AND logic). Nested array format: `[["termA","termB"],["termC"]]` — outer AND, inner OR. |
| topic_middle | string | No | Strongly boosted terms; same format as topic_high. |
| topic_low | string | No | Weakly boosted terms; same format as topic_high. |
| title | []string | No | Title query when use_topic=false. |
| doi | string | No | Exact DOI query. |
| year | []number | No | Year filter array. |
| sci_flag | boolean | No | Return SCI papers only. |
| n_citation_flag | boolean | No | Boost papers with high citation counts. |
| size | number | No | Maximum number of results to return. |
| offset | number | No | Offset. |
| force_citation_sort | boolean | No | Sort entirely by citation count. |
| force_year_sort | boolean | No | Sort entirely by year. |
| author_terms | []string | No | Author name query; OR relationship within array; include multiple variants. |
| org_terms | []string | No | Institution name query; OR relationship within array. |
| author_id | []string | No | Author entity ID filter; accepts single ID or ID list. OR relationship with author_terms when both are provided. |
| org_id | []string | No | Institution entity ID filter; accepts single ID or ID list. OR relationship with org_terms when both are provided. |
| venue_ids | []string | No | Conference/journal ID list filter. |
| query | string | No | Raw natural language question (slower); system auto-extracts keywords. Takes precedence over topic_high when both are provided. |

**Response Fields:**

| Field | Description |
|--------|------|
| data | Paper ID list |
| id | Paper ID |
| title | Paper title |
| title_zh | Title (Chinese) |
| doi | DOI |
| Total / total | Total count |

**curl Example (natural language Q&A):**
```bash
curl -X POST \
  'https://datacenter.aminer.cn/gateway/open_platform/api/paper/qa/search' \
  -H 'Content-Type: application/json;charset=utf-8' \
  -H 'Authorization: <TOKEN>' \
  -H 'X-Platform: openclaw' \
  -d '{"use_topic": false, "query": "deep learning protein structure prediction", "size": 10, "sci_flag": true}'
```

**curl Example (structured keywords):**
```bash
curl -X POST \
  'https://datacenter.aminer.cn/gateway/open_platform/api/paper/qa/search' \
  -H 'Content-Type: application/json;charset=utf-8' \
  -H 'Authorization: <TOKEN>' \
  -H 'X-Platform: openclaw' \
  -d '{
    "use_topic": true,
    "topic_high": "[[\\"transformer\\",\\"self-attention\\"],[\\"protein folding\\"]]",
    "topic_middle": "[[\"AlphaFold\"]]",
    "sci_flag": true,
    "force_citation_sort": true,
    "size": 10
  }'
```

---

### 4. Paper Info

- **URL**: `POST /api/paper/info`
- **Price**: Free
- **Description**: Batch-retrieve basic information (title, volume, journal, authors) by paper ID.

> **Mandatory Parameter Constraints (High Priority)**
> 1. `paper_info` only supports the batch parameter `ids` (array); it does not support a single `paper_id`.
> 2. `paper_detail` only supports the single-paper parameter `id` (string); in the client `raw` function wrapper, the corresponding parameter name is `paper_id`.
> 3. Never pass `ids` to `paper_detail`; doing so will trigger a parameter error (e.g., `unexpected keyword argument 'ids'`).
> 4. If many results are matched and the user has not specified a count, default to querying only the top 10 details to avoid unnecessary costs.

**Request Parameters:**

| Parameter | Type | Required | Description |
|--------|------|------|------|
| ids | []string | Yes | Paper ID array |

**Response Fields:**

| Field | Description |
|--------|------|
| _id | Paper ID |
| title | Paper title |
| authors | Author list (includes name/name_zh) |
| issue | Volume number |
| raw | Journal name |
| venue | Journal info object |

**curl Example:**
```bash
curl -X POST \
  'https://datacenter.aminer.cn/gateway/open_platform/api/paper/info' \
  -H 'Content-Type: application/json;charset=utf-8' \
  -H 'Authorization: <TOKEN>' \
  -H 'X-Platform: openclaw' \
  -d '{"ids": ["53e9ab9bb7602d97023e53b2", "53e9a98eb7602d9703e42e5a"]}'
```

**Correct raw call example (aminer_client.py):**
```bash
# Batch basic info (correct)
python scripts/aminer_client.py --action raw \
  --api paper_info --params '{"ids":["53e9ab9bb7602d97023e53b2","53e9a98eb7602d9703e42e5a"]}'
```

---

### 5. Paper Details

- **URL**: `GET /api/paper/detail`
- **Price**: ¥0.01/call
- **Description**: Retrieve full paper details by paper ID.

**Request Parameters:**

| Parameter | Type | Required | Description |
|--------|------|------|------|
| id | string | Yes | Paper ID |

**Response Fields:**

| Field | Description |
|--------|------|
| id | Paper ID |
| title | Title (English) |
| title_zh | Title (Chinese) |
| abstract | Abstract |
| abstract_zh | Abstract (Chinese) |
| authors | Author list (name/name_zh/org/org_zh) |
| doi | DOI |
| issn | ISSN |
| issue | Volume number |
| volume | Issue number |
| year | Year |
| keywords | Keywords |
| keywords_zh | Keywords (Chinese) |
| raw | Journal name |
| venue | Journal info object |

**curl Example:**
```bash
curl -X GET \
  'https://datacenter.aminer.cn/gateway/open_platform/api/paper/detail?id=53e9ab9bb7602d97023e53b2' \
  -H 'Authorization: <TOKEN>' \
  -H 'X-Platform: openclaw'
```

**Correct / incorrect raw call example (aminer_client.py):**
```bash
# Single paper details (correct)
python scripts/aminer_client.py --action raw \
  --api paper_detail --params '{"paper_id":"53e9ab9bb7602d97023e53b2"}'

# Incorrect example (do not do this: ids cannot be passed to paper_detail)
python scripts/aminer_client.py --action raw \
  --api paper_detail --params '{"ids":["53e9ab9bb7602d97023e53b2"]}'
```

---

### 6. Paper Citations

- **URL**: `GET /api/paper/relation`
- **Price**: ¥0.10/call
- **Description**: Retrieve the list of papers cited by a given paper ID.

**Request Parameters:**

| Parameter | Type | Required | Description |
|--------|------|------|------|
| id | string | Yes | Paper ID |

**Response Fields:**

| Field | Description |
|--------|------|
| _id | Paper ID |
| title | Title |
| cited | Basic info of papers cited by this paper |
| n_citation | Number of times cited |

**curl Example:**
```bash
curl -X GET \
  'https://datacenter.aminer.cn/gateway/open_platform/api/paper/relation?id=53e9ab9bb7602d97023e53b2' \
  -H 'Authorization: <TOKEN>' \
  -H 'X-Platform: openclaw'
```

---

### 7. Paper Search by Venue (Comprehensive Search)

- **URL**: `GET /api/paper/list/by/search/venue`
- **Price**: ¥0.30/call
- **Description**: Retrieve complete paper information (including abstract, institution, journal details) by keyword, author, or journal name.

**Request Parameters:**

| Parameter | Type | Required | Description |
|--------|------|------|------|
| page | number | Yes | Page number |
| size | number | Yes | Items per page |
| keyword | string | No | Keyword (choose one of: keyword/venue/author) |
| venue | string | No | Journal name (choose one of: keyword/venue/author) |
| author | string | No | Author name (choose one of: keyword/venue/author) |
| order | string | No | Sort: `year` or `n_citation`; omit for composite ranking |

**Response Fields (main):**

| Field | Description |
|--------|------|
| _id | Paper ID |
| title / title_zh | Paper title (bilingual) |
| abstract / abstract_zh | Abstract (bilingual) |
| authors | Author info (includes institution ID, aliases, details) |
| venue | Journal info (bilingual name, aliases) |
| venue_hhb_id | Journal ID |
| keywords / keywords_zh | Keywords (bilingual) |
| year | Publication year |
| n_citation | Citation count |
| doi | DOI |
| url | Paper link URL |
| total | Total count |

**curl Example:**
```bash
curl -X GET \
  'https://datacenter.aminer.cn/gateway/open_platform/api/paper/list/by/search/venue?keyword=graph+neural+network&page=0&size=10&order=n_citation' \
  -H 'Authorization: <TOKEN>' \
  -H 'X-Platform: openclaw'
```

---

### 8. Paper Batch Query (Multi-keyword)

- **URL**: `GET /api/paper/list/citation/by/keywords`
- **Price**: ¥0.10/call
- **Description**: Retrieve paper keywords, abstracts, and other information via multiple keywords.

**Request Parameters:**

| Parameter | Type | Required | Description |
|--------|------|------|------|
| page | number | Yes | Page number |
| size | number | Yes | Items per page |
| keywords | string | Yes | Keyword array (JSON string format) |

**Response Fields:**

| Field | Description |
|--------|------|
| id | Paper ID |
| title / title_zh | Title (bilingual) |
| abstract / abstract_zh | Abstract (bilingual) |
| keywords / keywords_zh | Keywords (bilingual) |
| doi | DOI |
| year | Year |
| total | Total count |

**curl Example:**
```bash
curl -X GET \
  'https://datacenter.aminer.cn/gateway/open_platform/api/paper/list/citation/by/keywords?page=0&size=10&keywords=%5B%22deep+learning%22%2C%22object+detection%22%5D' \
  -H 'Authorization: <TOKEN>' \
  -H 'X-Platform: openclaw'
```

---

### 9. Paper Details by Year and Venue

- **URL**: `GET /api/paper/platform/allpubs/more/detail/by/ts/org/venue`
- **Price**: ¥0.20/call
- **Description**: Retrieve paper titles, authors, DOIs, keywords, and other details by publication year and journal.

> **Note**: `venue_id` and `year` must be provided together; providing only `year` returns `null`. Use the **Venue Search** API first to obtain the `venue_id`.

**Request Parameters:**

| Parameter | Type | Required | Description |
|--------|------|------|------|
| year | number | Yes | Paper publication year |
| venue_id | string | Yes | Journal ID (obtained via Venue Search; returns null if not provided) |

**Response Fields (main):**

| Field | Description |
|--------|------|
| _id | Paper ID |
| title / title_zh | Title (bilingual) |
| abstract | Abstract |
| authors | Author array (name/org/email/homepage/orc_id/`_id`) |
| doi | DOI |
| issn | ISSN |
| keywords / keywords_zh | Keywords (bilingual) |
| year | Year |
| venue | Journal info |

**curl Example:**
```bash
curl -X GET \
  'https://datacenter.aminer.cn/gateway/open_platform/api/paper/platform/allpubs/more/detail/by/ts/org/venue?year=2023&venue_id=<VENUE_ID>' \
  -H 'Authorization: <TOKEN>' \
  -H 'X-Platform: openclaw'
```

---

## Scholar APIs

### 10. Scholar Search

- **URL**: `POST /api/person/search`
- **Price**: Free
- **Description**: Search for scholars by name (or institution); returns ID, name, and institution.

**Request Parameters:**

| Parameter | Type | Required | Description |
|--------|------|------|------|
| name | string | No | Scholar name |
| org | string | No | Institution name |
| org_id | []string | No | Institution entity ID array |
| offset | number | No | Starting position (maximum 0) |
| size | number | No | Number of results (maximum 10) |

**Response Fields:**

| Field | Description |
|--------|------|
| id | Scholar ID |
| name | Name (English) |
| name_zh | Name (Chinese) |
| org | Institution (English) |
| org_zh | Institution (Chinese) |
| org_id | Institution ID |
| interests | Research interests |
| n_citation | Citation count |
| total | Total count |

**curl Example:**
```bash
curl -X POST \
  'https://datacenter.aminer.cn/gateway/open_platform/api/person/search' \
  -H 'Content-Type: application/json;charset=utf-8' \
  -H 'Authorization: <TOKEN>' \
  -H 'X-Platform: openclaw' \
  -d '{"name": "Andrew Ng", "size": 5}'
```

---

### 11. Scholar Details

- **URL**: `GET /api/person/detail`
- **Price**: ¥1.00/call
- **Description**: Retrieve complete personal information by scholar ID.

**Request Parameters:**

| Parameter | Type | Required | Description |
|--------|------|------|------|
| id | string | Yes | Scholar ID |

**Response Fields:**

| Field | Description |
|--------|------|
| id / person_id | Scholar ID |
| name / name_zh | Name (bilingual) |
| bio / bio_zh | Personal bio (bilingual; not both present simultaneously) |
| edu / edu_zh | Education history (bilingual) |
| orgs / org_zhs | Institution list (English / Chinese) |
| position / position_zh | Title (bilingual) |
| domain | Research domain |
| honor | Honors |
| award | Awards |
| year | Year |

**curl Example:**
```bash
curl -X GET \
  'https://datacenter.aminer.cn/gateway/open_platform/api/person/detail?id=53f3ae78dabfae4b34b0c75d' \
  -H 'Authorization: <TOKEN>' \
  -H 'X-Platform: openclaw'
```

---

### 12. Scholar Portrait

- **URL**: `GET /api/person/figure`
- **Price**: ¥0.50/call
- **Description**: Retrieve research interests, domains, and structured work/education history.

**Request Parameters:**

| Parameter | Type | Required | Description |
|--------|------|------|------|
| id | string | Yes | Scholar ID |

**Response Fields:**

| Field | Description |
|--------|------|
| id | Scholar ID |
| ai_interests | Research interest list |
| ai_domain | Research domain list |
| edus | Structured education history |
| works | Structured work history |

**curl Example:**
```bash
curl -X GET \
  'https://datacenter.aminer.cn/gateway/open_platform/api/person/figure?id=53f3ae78dabfae4b34b0c75d' \
  -H 'Authorization: <TOKEN>' \
  -H 'X-Platform: openclaw'
```

---

### 13. Scholar Papers

- **URL**: `GET /api/person/paper/relation`
- **Price**: ¥1.50/call
- **Description**: Retrieve a list of papers published by a scholar (ID + title).

**Request Parameters:**

| Parameter | Type | Required | Description |
|--------|------|------|------|
| id | string | Yes | Scholar ID |

**Response Fields:**

| Field | Description |
|--------|------|
| author_id | Scholar ID |
| id | Paper ID |
| title | Paper title |

**curl Example:**
```bash
curl -X GET \
  'https://datacenter.aminer.cn/gateway/open_platform/api/person/paper/relation?id=53f3ae78dabfae4b34b0c75d' \
  -H 'Authorization: <TOKEN>' \
  -H 'X-Platform: openclaw'
```

---

### 14. Scholar Patents

- **URL**: `GET /api/person/patent/relation`
- **Price**: ¥1.50/call
- **Description**: Retrieve a list of patents associated with a scholar.

**Request Parameters:**

| Parameter | Type | Required | Description |
|--------|------|------|------|
| id | string | Yes | Scholar ID |

**Response Fields:**

| Field | Description |
|--------|------|
| patent_id | Patent ID |
| person_id | Scholar ID |
| title | Patent title |
| en | Title (English) |
| zh | Title (Chinese) |

**curl Example:**
```bash
curl -X GET \
  'https://datacenter.aminer.cn/gateway/open_platform/api/person/patent/relation?id=53f3ae78dabfae4b34b0c75d' \
  -H 'Authorization: <TOKEN>' \
  -H 'X-Platform: openclaw'
```

---

### 15. Scholar Projects

- **URL**: `GET /api/project/person/v3/open`
- **Price**: ¥3.00/call
- **Description**: Retrieve research projects a scholar has participated in (funding amount, dates, source).

**Request Parameters:**

| Parameter | Type | Required | Description |
|--------|------|------|------|
| id | string | No | Scholar ID |

**Response Fields:**

| Field | Description |
|--------|------|
| id | Project ID |
| titles | Project title |
| country | Country |
| project_source | Project source |
| fund_amount | Funding amount |
| fund_currency | Funding currency |
| start_date | Start date |
| end_date | End date |
| total | Total count |

**curl Example:**
```bash
curl -X GET \
  'https://datacenter.aminer.cn/gateway/open_platform/api/project/person/v3/open?id=53f3ae78dabfae4b34b0c75d' \
  -H 'Authorization: <TOKEN>' \
  -H 'X-Platform: openclaw'
```

---

## Institution APIs

### 16. Org Search

- **URL**: `POST /api/organization/search`
- **Price**: Free
- **Description**: Search for institution IDs and names by name keyword.

**Request Parameters:**

| Parameter | Type | Required | Description |
|--------|------|------|------|
| orgs | []string | No | Institution name array |

**Response Fields:**

| Field | Description |
|--------|------|
| org_id | Institution ID |
| org_name | Institution name |
| total | Total count |

**curl Example:**
```bash
curl -X POST \
  'https://datacenter.aminer.cn/gateway/open_platform/api/organization/search' \
  -H 'Content-Type: application/json;charset=utf-8' \
  -H 'Authorization: <TOKEN>' \
  -H 'X-Platform: openclaw' \
  -d '{"orgs": ["Tsinghua University"]}'
```

---

### 17. Org Details

- **URL**: `POST /api/organization/detail`
- **Price**: ¥0.01/call
- **Description**: Retrieve institution details by institution ID.

**Request Parameters:**

| Parameter | Type | Required | Description |
|--------|------|------|------|
| ids | []string | Yes | Institution ID array |

**Response Fields:**

| Field | Description |
|--------|------|
| id | Institution ID |
| name / name_en / name_zh | Institution name (raw/English/Chinese) |
| acronyms | Abbreviation |
| aliases | Alias list |
| details | Detailed institution description |
| type | Institution type (university/enterprise, etc.) |
| location | Geographic location |
| language | Language |
| total | Total count |

**curl Example:**
```bash
curl -X POST \
  'https://datacenter.aminer.cn/gateway/open_platform/api/organization/detail' \
  -H 'Content-Type: application/json;charset=utf-8' \
  -H 'Authorization: <TOKEN>' \
  -H 'X-Platform: openclaw' \
  -d '{"ids": ["5f71b2091c455f439fe9a7d7"]}'
```

---

### 18. Org Scholars

- **URL**: `GET /api/organization/person/relation`
- **Price**: ¥0.50/call
- **Description**: Retrieve the list of scholars affiliated with an institution (10 results per call).

**Request Parameters:**

| Parameter | Type | Required | Description |
|--------|------|------|------|
| org_id | string | No | Institution ID |
| offset | number | No | Starting position (returns 10 results per call) |

**Response Fields:**

| Field | Description |
|--------|------|
| id | Scholar ID |
| name / name_zh | Scholar name (bilingual) |
| org / org_zh | Institution (bilingual) |
| org_id | Institution ID |
| total | Total count |

**curl Example:**
```bash
curl -X GET \
  'https://datacenter.aminer.cn/gateway/open_platform/api/organization/person/relation?org_id=5f71b2091c455f439fe9a7d7&offset=0' \
  -H 'Authorization: <TOKEN>' \
  -H 'X-Platform: openclaw'
```

---

### 19. Org Papers

- **URL**: `GET /api/organization/paper/relation`
- **Price**: ¥0.10/call
- **Description**: Retrieve the list of papers published by scholars at an institution (10 results per call).

**Request Parameters:**

| Parameter | Type | Required | Description |
|--------|------|------|------|
| org_id | string | Yes | Institution ID |
| offset | number | Yes | Starting position (returns 10 results per call) |

**Response Fields:**

| Field | Description |
|--------|------|
| id | Paper ID |
| title / title_zh | Title (bilingual) |
| doi | DOI |
| total | Total count |

**curl Example:**
```bash
curl -X GET \
  'https://datacenter.aminer.cn/gateway/open_platform/api/organization/paper/relation?org_id=5f71b2091c455f439fe9a7d7&offset=0' \
  -H 'Authorization: <TOKEN>' \
  -H 'X-Platform: openclaw'
```

---

### 20. Org Patents

- **URL**: `GET /api/organization/patent/relation`
- **Price**: ¥0.10/call
- **Description**: Retrieve the list of patent IDs owned by an institution; supports pagination with up to 10,000 results per call.

**Request Parameters:**

| Parameter | Type | Required | Description |
|--------|------|------|------|
| id | string | Yes | Institution ID |
| page | number | No | Page number (starts at 1) |
| page_size | number | No | Items per page; maximum 10,000 |

**Response Fields:**

| Field | Description |
|--------|------|
| id | Patent ID |
| total | Total count |

**curl Example:**
```bash
curl -X GET \
  'https://datacenter.aminer.cn/gateway/open_platform/api/organization/patent/relation?id=6233173d0a6eb145604733e2&page=1&page_size=100' \
  -H 'Authorization: <TOKEN>' \
  -H 'X-Platform: openclaw'
```

---

### 21. Org Disambiguation

- **URL**: `POST /api/organization/na`
- **Price**: ¥0.01/call
- **Description**: Retrieve the standardized institution name from an institution string (including abbreviations/aliases).

**Request Parameters:**

| Parameter | Type | Required | Description |
|--------|------|------|------|
| org | string | Yes | Institution name (may include aliases/abbreviations) |

**Response Fields:**

| Field | Description |
|--------|------|
| org_name | Normalized institution name |

**curl Example:**
```bash
curl -X POST \
  'https://datacenter.aminer.cn/gateway/open_platform/api/organization/na' \
  -H 'Content-Type: application/json;charset=utf-8' \
  -H 'Authorization: <TOKEN>' \
  -H 'X-Platform: openclaw' \
  -d '{"org": "MIT CSAIL"}'
```

---

### 22. Org Disambiguation Pro

- **URL**: `POST /api/organization/na/pro`
- **Price**: ¥0.05/call
- **Description**: Extract the IDs of primary and secondary institutions from an institution string (recommended for workflows).

**Request Parameters:**

| Parameter | Type | Required | Description |
|--------|------|------|------|
| org | string | Yes | Institution name |

**Response Fields:**

| Field | Description |
|--------|------|
| 一级 | Primary institution name |
| 一级ID | Primary institution ID |
| 二级 | Secondary institution name |
| 二级ID | Secondary institution ID |
| Total / total | Total count |

**curl Example:**
```bash
curl -X POST \
  'https://datacenter.aminer.cn/gateway/open_platform/api/organization/na/pro' \
  -H 'Content-Type: application/json;charset=utf-8' \
  -H 'Authorization: <TOKEN>' \
  -H 'X-Platform: openclaw' \
  -d '{"org": "Department of Computer Science, Tsinghua University"}'
```

---

## Journal APIs

### 23. Venue Search

- **URL**: `POST /api/venue/search`
- **Price**: Free
- **Description**: Search for journal IDs and standard names by journal name.

**Request Parameters:**

| Parameter | Type | Required | Description |
|--------|------|------|------|
| name | string | No | Journal name (supports fuzzy search) |

**Response Fields:**

| Field | Description |
|--------|------|
| id | Journal ID |
| name_en | Journal name (English) |
| name_zh | Journal name (Chinese) |
| total | Total count |

**curl Example:**
```bash
curl -X POST \
  'https://datacenter.aminer.cn/gateway/open_platform/api/venue/search' \
  -H 'Content-Type: application/json;charset=utf-8' \
  -H 'Authorization: <TOKEN>' \
  -H 'X-Platform: openclaw' \
  -d '{"name": "NeurIPS"}'
```

---

### 24. Venue Details

- **URL**: `POST /api/venue/detail`
- **Price**: ¥0.20/call
- **Description**: Retrieve ISSN, abbreviation, type, and other details by journal ID.

**Request Parameters:**

| Parameter | Type | Required | Description |
|--------|------|------|------|
| id | string | Yes | Journal ID |

**Response Fields:**

| Field | Description |
|--------|------|
| id | Journal ID |
| name / name_en / name_zh | Name (raw/English/Chinese) |
| issn | ISSN |
| eissn | EISSN |
| alias | Alias |
| type | Journal type |

**curl Example:**
```bash
curl -X POST \
  'https://datacenter.aminer.cn/gateway/open_platform/api/venue/detail' \
  -H 'Content-Type: application/json;charset=utf-8' \
  -H 'Authorization: <TOKEN>' \
  -H 'X-Platform: openclaw' \
  -d '{"id": "<VENUE_ID>"}'
```

---

### 25. Venue Papers

- **URL**: `POST /api/venue/paper/relation`
- **Price**: ¥0.10/call
- **Description**: Retrieve a list of papers for a journal by journal ID (supports year filtering).

**Request Parameters:**

| Parameter | Type | Required | Description |
|--------|------|------|------|
| id | string | Yes | Journal ID |
| offset | number | No | Starting position |
| limit | number | No | Number of results to return |
| year | number | No | Filter by year |

**Response Fields:**

| Field | Description |
|--------|------|
| id | Paper ID |
| title | Paper title |
| year | Year |
| offset | Current offset |
| total | Total count |

**curl Example:**
```bash
curl -X POST \
  'https://datacenter.aminer.cn/gateway/open_platform/api/venue/paper/relation' \
  -H 'Content-Type: application/json;charset=utf-8' \
  -H 'Authorization: <TOKEN>' \
  -H 'X-Platform: openclaw' \
  -d '{"id": "<VENUE_ID>", "year": 2023, "offset": 0, "limit": 20}'
```

---

## Patent APIs

### 26. Patent Search

- **URL**: `POST /api/patent/search`
- **Price**: Free
- **Description**: Search for patents by patent name/keyword.

**Request Parameters:**

| Parameter | Type | Required | Description |
|--------|------|------|------|
| query | string | Yes | Query field (patent title/keyword) |
| page | number | Yes | Page number |
| size | number | Yes | Items per page |

**Response Fields:**

| Field | Description |
|--------|------|
| id | Patent ID |
| title | Patent title (English) |
| title_zh | Patent title (Chinese) |

**curl Example:**
```bash
curl -X POST \
  'https://datacenter.aminer.cn/gateway/open_platform/api/patent/search' \
  -H 'Content-Type: application/json;charset=utf-8' \
  -H 'Authorization: <TOKEN>' \
  -H 'X-Platform: openclaw' \
  -d '{"query": "quantum computing chip", "page": 0, "size": 10}'
```

---

### 27. Patent Info

- **URL**: `GET /api/patent/info`
- **Price**: Free
- **Description**: Retrieve basic patent information (title, patent number, inventors, country) by patent ID.

**Request Parameters:**

| Parameter | Type | Required | Description |
|--------|------|------|------|
| id | string | Yes | Patent ID |

**Response Fields:**

| Field | Description |
|--------|------|
| id | Patent ID |
| title / en | Patent title (English) |
| app_num | Application number |
| pub_num | Publication number |
| pub_kind | Publication type |
| inventor | Inventor |
| country | Country |
| sequence | Sequence |

**curl Example:**
```bash
curl -X GET \
  'https://datacenter.aminer.cn/gateway/open_platform/api/patent/info?id=<PATENT_ID>' \
  -H 'Authorization: <TOKEN>' \
  -H 'X-Platform: openclaw'
```

---

### 28. Patent Details

- **URL**: `GET /api/patent/detail`
- **Price**: ¥0.01/call
- **Description**: Retrieve full patent details by patent ID (including abstract, filing date, assignee, IPC classification, etc.).

**Request Parameters:**

| Parameter | Type | Required | Description |
|--------|------|------|------|
| id | string | Yes | Patent ID |

**Response Fields:**

| Field | Description |
|--------|------|
| id | Patent ID |
| title | Patent title |
| abstract | Abstract |
| app_date | Filing date |
| app_num | Application number |
| pub_date | Publication date |
| pub_num | Publication number |
| pub_kind | Publication type |
| assignee | Assignee |
| inventor | Inventor |
| country | Country |
| ipc | IPC classification code |
| ipcr | IPCR classification code |
| cpc | CPC classification code |
| priority | Priority info |
| description | Description |

**curl Example:**
```bash
curl -X GET \
  'https://datacenter.aminer.cn/gateway/open_platform/api/patent/detail?id=<PATENT_ID>' \
  -H 'Authorization: <TOKEN>' \
  -H 'X-Platform: openclaw'
```

---

## Appendix: API Pricing Summary

| Category | Free APIs | Paid APIs |
|------|---------|---------|
| Paper | Paper Search, Paper Info | Paper Search Pro(¥0.01), Paper Details(¥0.01), Paper Citations(¥0.10), Paper QA Search(¥0.05), Paper Search by Venue(¥0.30), Paper Batch Query(¥0.10), By Condition(¥0.20) |
| Scholar | Scholar Search | Scholar Details(¥1.00), Scholar Portrait(¥0.50), Scholar Papers(¥1.50), Scholar Patents(¥1.50), Scholar Projects(¥3.00) |
| Institution | Org Search | Org Details(¥0.01), Org Scholars(¥0.50), Org Papers(¥0.10), Org Patents(¥0.10), Org Disambiguation(¥0.01), Org Disambiguation Pro(¥0.05) |
| Journal | Venue Search | Venue Details(¥0.20), Venue Papers(¥0.10) |
| Patent | Patent Search, Patent Info | Patent Details(¥0.01) |
