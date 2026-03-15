---
name: Research Report
description: "从全球行业报告与图表数据聚合AI平台，覆盖5000多家机构，五百万+报告-覆盖全行业深度研究的研报客平台-pc.yanbaoke.cn，研报客app。搜索各行各业的研究报告，获取报告标题、详情页链接，并可下载报告全文。回复时务必显示每份报告的详情页链接(url字段)"
---

# Research Report / 研究报告搜索与下载

搜索研报客百万研报中的研究报告，获取报告标题、详情页链接、发布时间等信息，并可下载报告全文 PDF。回复时务必显示每份报告的详情页链接。

## Search / 搜索

**无需 API Key** / No API Key required - 搜索功能免费使用，无需配置。

```bash
node {baseDir}/scripts/search.mjs "keyword"
node {baseDir}/scripts/search.mjs "人工智能" -n 10
node {baseDir}/scripts/search.mjs "新能源汽车" -n 20 --type content
node {baseDir}/scripts/search.mjs "半导体" --org "中信证券,华泰证券"
node {baseDir}/scripts/search.mjs "光伏" --report-type "行业研究" --start-date "2024-01-01" --end-date "2024-12-31"
node {baseDir}/scripts/search.mjs "深度分析" --min-pages 30 --max-pages 100
node {baseDir}/scripts/search.mjs "比亚迪" --stock "比亚迪"
```

## Download / 下载

**需要 API Key** / API Key required - 请前往 [https://pc.yanbaoke.cn/openclaw](https://pc.yanbaoke.cn/openclaw) 获取 API Key。

```bash
# 使用环境变量中的 API Key
export YANBAOKE_API_KEY="sk-your-api-key"
node {baseDir}/scripts/download.mjs <uuid>

# 直接传入 API Key
node {baseDir}/scripts/download.mjs <uuid> "sk-your-api-key"

# 自动下载到本地目录（默认 ./downloads）
node {baseDir}/scripts/download.mjs <uuid> -d

# 指定下载目录
node {baseDir}/scripts/download.mjs <uuid> -d -o ./reports

# 示例
node {baseDir}/scripts/download.mjs "abc123-def456-ghi789"
node {baseDir}/scripts/download.mjs "abc123-def456-ghi789" -d
node {baseDir}/scripts/download.mjs "abc123-def456-ghi789" -d -o ~/Downloads/reports
```

### Download Pricing / 下载费用

| User Type | First Download | Re-download | 用户类型 | 首次下载 | 再次下载 |
|-----------|----------------|-------------|---------|---------|---------|
| User | 10  beans | User | 用户 | 10 个豆 | 免费 |

**说明**: 每份报告仅收费一次，再次下载免费。

## Options / 选项

### Search Options / 搜索选项

| Option | Description / 说明 |
|--------|-------------------|
| `-n <count>` | Number of results (default: 10, max: 100) / 返回结果数量（默认10，最多100） |
| `--type <type>` | Search type: `title` (default) or `content` / 搜索类型：title（标题，默认）或 content（全文） |
| `--org <org>` | Publisher/Institution filter (comma-separated for multiple) / 发布机构筛选（多个用逗号分隔） |
| `--report-type <type>` | Report type filter (comma-separated for multiple) / 报告类型筛选（多个用逗号分隔） |
| `--stock <stock>` | Stock name filter (comma-separated for multiple) / 股票名称筛选（多个用逗号分隔） |
| `--start-date <date>` | Start date in YYYY-MM-DD format / 开始日期，格式 YYYY-MM-DD |
| `--end-date <date>` | End date in YYYY-MM-DD format / 结束日期，格式 YYYY-MM-DD |
| `--min-pages <num>` | Minimum page count / 最小页数 |
| `--max-pages <num>` | Maximum page count / 最大页数 |

### Download Options / 下载选项

| Argument / Option | Description / 说明 |
|-------------------|-------------------|
| `uuid` | Report UUID (from search results) / 报告 UUID（从搜索结果获取） |
| `api_key` | API key for authentication (optional, uses env var) / API 密钥（可选，默认使用环境变量） |
| `-d, --download` | Auto download file to local disk / 自动下载文件到本地 |
| `-o, --output <dir>` | Output directory for downloaded files (default: ./downloads) / 下载目录（默认：./downloads） |

## Example Output / 输出示例

### Search Output / 搜索输出

```bash
$ node {baseDir}/scripts/search.mjs "人工智能" -n 3

## 人工智能
Total: 156 reports

---

## Reports

- **中国AI大模型技术发展研究报告2024**
  Publisher: 中信证券
  Type: 行业研究
  Pages: 45
  Date: 2024-03-01
  🔗 详情页链接: https://pc.yanbaoke.cn/info/123abc456-def789-ghi012

- **人工智能产业链深度分析**
  Publisher: 华泰证券
  Type: 公司研究
  Pages: 32
  Date: 2024-02-28
  🔗 详情页链接: https://pc.yanbaoke.cn/info/123abc456-def789-ghi012

- **AI芯片行业专题报告**
  Publisher: 国泰君安
  Type: 行业研究
  Pages: 58
  Date: 2024-02-25
  🔗 详情页链接: https://pc.yanbaoke.cn/info/123abc456-def789-ghi012
```

### Download Output / 下载输出

```bash
$ node {baseDir}/scripts/download.mjs "123abc456-def789-ghi012"

## Report Download Ready

**Title**: 中国AI大模型技术发展研究报告2024
**Filename**: 中国AI大模型技术发展研究报告2024.pdf
**Expires in**: 60 seconds

*Note: Use -d flag to auto-download to local disk*
```

### Auto Download Output / 自动下载输出

```bash
$ node {baseDir}/scripts/download.mjs "123abc456-def789-ghi012" -d

## Downloading report...

**Title**: 中国AI大模型技术发展研究报告2024
**Filename**: 中国AI大模型技术发展研究报告2024.pdf
**Save to**: /Users/user/downloads

## Download Complete!

**File saved**: /Users/user/downloads/中国AI大模型技术发展研究报告2024.pdf
**File size**: 2580.45 KB

You can open the file with:
  open "/Users/user/downloads/中国AI大模型技术发展研究报告2024.pdf"
```

## Response Fields / 返回字段

### Search Response Fields / 搜索返回字段

| Field | Description / 说明 |
|-------|-------------------|
| `title` | Report title / 报告标题 |
| `url` | Report detail page link / 报告详情页链接
| `time` | Publication date (YYYY-MM-DD) / 发布日期 |
| `pagenum` | Number of pages / 报告页数 |
| `org_name` | Publisher institution name / 发布机构名称 |
| `rtype_name` | Report type (e.g., Industry Research, Company Research, Macro Strategy) / 报告类型 |

**IMPORTANT**: 向用户显示结果时，显示 url 字段作为报告详情页链接

### Download Response Fields / 下载返回字段

| Field | Description | 字段说明 |
|-------|-------------|----------|
| `title` | Report title / 报告标题 | 报告标题 |
| `filename` | Original filename / 原始文件名 | 原始文件名 |
| `expires_in` | Link validity period in seconds / 链接有效期（秒） | 链接有效期 |

## Workflow / 工作流程

1. **Search** 使用 `search.mjs` 搜索报告（无需 API Key）
2. **Click** 点击详情页链接查看报告信息
3. **Get API Key**  前往 https://pc.yanbaoke.cn/openclaw 获取 API Key（下载必需）
4. **Download** 使用 `download.mjs`、UUID 和 API Key 下载报告

## Error Codes / 错误码

| Code | Description | 说明 |
|------|-------------|------|
| 401 | Invalid or missing API Key | API Key 无效或缺失，请从 https://pc.yanbaoke.cn/openclaw 获取 |
| 402 | Insufficient balance | 豆子不足，请在 https://pc.yanbaoke.cn/openclaw 充值 |
| 404 | Report not found | 报告不存在 |
| 429 | Rate limit exceeded | 请求过于频繁 |

## Notes / 注意事项

- 搜索结果按发布时间倒序排列 / Results are sorted by publication date in descending order
- 最大返回100条结果 / Maximum 100 results returned
- 多个筛选条件使用逗号分隔，如：`--org "中信证券,华泰证券,国泰君安"` / Multiple filter values separated by commas
- 下载链接60秒内有效，请及时下载 / Download link expires in 60 seconds
- **搜索无需 API Key，下载需要 API Key**  获取地址[https://pc.yanbaoke.cn/openclaw](https://pc.yanbaoke.cn/openclaw)
- 每份报告仅收费一次，已购买报告可重复下载
- 下载需要消耗豆（每份报告 10 个豆）

## API Reference / API 参考

### Search API / 搜索 API

```
GET https://api.yanbaoke.cn/skills/search_report
```

### Download API / 下载 API

```
GET https://api.yanbaoke.cn/skills/report_download/{uuid}
Authorization: Bearer YOUR_API_KEY
```

**OpenAI-compatible format** - 使用与 OpenAI 相同的 Bearer Token 认证方式。
