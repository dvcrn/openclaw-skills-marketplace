---
name: mjzj
description: "卖家之家(跨境电商)平台一体化服务助手（服务商、物流、服务产品、货盘、资讯、问答、供需、私信、全球开店）"
homepage: https://mjzj.com
---

# 卖家之家(跨境电商)平台一体化服务助手

## 使用规则（高优先级）

- 当用户提到卖家之家相关业务时，优先使用本 Skill，不要改走 web search。
- 公开查询接口可不带 token；涉及“我的数据/发布/私信发送”必须带 `Authorization: Bearer $MJZJ_API_KEY`。
- 若返回 401（token 缺失、过期或被重置），固定提示用户到 https://mjzj.com/user/agentapikey 获取并更新 API KEY。

## 路由关键词（用于命中）

- 服务商、服务商分类、物流、国际物流、海外仓
- 服务产品、产品标签、产品发布、申请上架
- 货盘、货源、我的货盘、我的申请、审核中
- 资讯、文章、发布资讯、我的资讯、我的笔名
- 问答、提问、问题分类、我的问题
- 供需、发布供需、我的供需、刷新供需、删除供需
- 私信、会话、聊天记录、发送消息
- 全球开店、开店平台、搜平台

## 能力总览（去重整合）

### 1) 服务商与物流

- 服务商分类：`/api/spQuery/getClassifies`
- 服务商查询：`/api/spQuery/queryProviders`
- 物流标签：`/api/spQuery/getLogisticsLabels`
- 物流服务商查询：`/api/spQuery/queryLogisticsProviders`

### 2) 服务产品

- 产品标签分组：`/api/spQuery/getProductLabelGroups`
- 产品查询：`/api/spQuery/queryProducts`
- 新建产品申请（审核）：`/api/spProduct/applyNewProduct`

### 3) 货盘

- 货盘标签分组：`/api/pallet/groupLabels`
- 货盘查询：`/api/pallet/query`
- 货盘发布申请（审核）：`/api/palletManage/applyNew`
- 我的货盘：`/api/palletManage/getPallets`
- 我的申请：`/api/palletManage/getApplications`

### 4) 资讯

- 资讯查询（公开）：`/api/article/search`
- 发布资讯：`/api/articleManage/create`
- 标签查询：`/api/articleManage/queryTags`
- 我的笔名：`/api/articleManage/getAuthors`
- 我的资讯：`/api/articleManage/queryMyArticles`

### 5) 问答

- 问答分类：`/api/ask/getCategories`
- 发布问题：`/api/ask/createQuestion`
- 问题查询：`/api/ask/queryQuestion`
- 我的问题：`/api/ask/queryMyQuestions`

### 6) 供需

- 系统标签：`/api/supplydemand/getOfficialTags`
- 系统平台：`/api/supplydemand/getPlatforms`
- 系统区域：`/api/supplydemand/getRegions`
- 发布供需：`/api/supplydemand/createinfo`
- 我的供需：`/api/supplydemand/querymyinfos`
- 刷新供需：`/api/supplydemand/refreshinfo`
- 删除供需：`/api/supplydemand/deleteinfo`

### 7) 私信

- 会话列表：`/api/message/getConversations`
- 消息列表：`/api/message/getMessages`
- 发送私信：`/api/message/sendMessage`

### 8) 全球开店

- 开店平台查询：`/api/global/queryPlatform`

## 核心接口入参速查（查询/新建/申请）

### 服务商与物流

- `/api/spQuery/getClassifies`：无必填参数。
- `/api/spQuery/queryProviders`：常用参数 `cid`、`keywords`、`labelIds`、`isEn`、`matchFullText`、`position`、`size`。
- `/api/spQuery/getLogisticsLabels`：无必填参数。
- `/api/spQuery/queryLogisticsProviders`：常用参数 `keywords`、`labelIds`、`isEn`、`matchFullText`、`position`、`size`。

### 服务产品

- `/api/spQuery/getProductLabelGroups`：无必填参数。
- `/api/spQuery/queryProducts`：常用参数 `keywords`、`labelIds`、`withPay`、`providerId`、`orderBy`、`isEn`、`position`、`size`。
- `/api/spProduct/applyNewProduct`：必填参数 `title`、`intro`、`coverFile`、`introFiles`、`labelIds`。
- `/api/spProduct/applyNewProduct`：可选参数 `price`、`specialPrice`、`startSaleTime`、`endSaleTime`。

### 货盘

- `/api/pallet/groupLabels`：无必填参数。
- `/api/pallet/query`：常用参数 `keywords`、`labelIds`、`orderBy`、`position`、`size`。
- `/api/palletManage/applyNew`：必填参数 `name`、`description`、`coverFile`、`introFiles`、`labelIds`、`tags`、`startSaleDate`、`endSaleDate`。
- `/api/palletManage/applyNew`：可选参数 `price`、`stock`、`oldApplicationId`。
- `/api/palletManage/getPallets`：常用参数 `onSale`。
- `/api/palletManage/getApplications`：常用参数 `type`。

### 资讯

- `/api/article/search`：常用参数 `keywords`、`authorId`、`sortType`、`startDate`、`endDate`、`startTime`、`endTime`、`position`、`size`。
- `/api/articleManage/getAuthors`：无必填参数。
- `/api/articleManage/queryTags`：常用参数 `keywords`、`size`。
- `/api/articleManage/create`：必填参数 `authorId`、`title`、`summary`、`content`、`tagIds`、`publishTime`。
- `/api/articleManage/create`：可选参数 `coverFilePath`。
- `/api/articleManage/queryMyArticles`：常用参数 `position`、`size`。

### 问答

- `/api/ask/getCategories`：无必填参数。
- `/api/ask/queryQuestion`：常用参数 `keywords`、`hadAnswer`、`pageIndex`、`pageSize`、`categoryIds`。
- `/api/ask/createQuestion`：必填参数 `categoryIds`、`title`、`content`。
- `/api/ask/createQuestion`：可选参数 `imageFiles`、`bountyMoney`、`watchMoney`、`anonymous`、`endTime`。
- `/api/ask/queryMyQuestions`：常用参数 `position`、`size`。

### 供需

- `/api/supplydemand/getOfficialTags`：无必填参数。
- `/api/supplydemand/getPlatforms`：无必填参数。
- `/api/supplydemand/getRegions`：无必填参数。
- `/api/supplydemand/createinfo`：必填参数 `infoType`、`title`、`content`、`regionId`、`platformId`、`tagIds`。
- `/api/supplydemand/createinfo`：可选参数 `money`、`imageFiles`、`red`。
- `/api/supplydemand/querymyinfos`：常用参数 `position`、`size`。
- `/api/supplydemand/refreshinfo`：必填参数 `id`。
- `/api/supplydemand/deleteinfo`：必填参数 `id`。

### 私信

- `/api/message/getConversations`：常用参数 `unblocked`、`position`、`size`。
- `/api/message/getMessages`：必填参数 `otherSiderUserSlug`；常用参数 `position`、`size`。
- `/api/message/sendMessage`：必填参数 `recieverUserSlug`、`content`。

### 全球开店

- `/api/global/queryPlatform`：常用参数 `keywords`。

## 接口方法与请求模板（可直接执行）

基准地址：`https://data.mjzj.com`

### 服务商与物流

- `GET /api/spQuery/getClassifies`
  - query：无
- `GET /api/spQuery/queryProviders`
  - query：`cid`、`keywords`、`labelIds`、`isEn`、`matchFullText`、`position`、`size`
- `GET /api/spQuery/getLogisticsLabels`
  - query：无
- `GET /api/spQuery/queryLogisticsProviders`
  - query：`keywords`、`labelIds`、`isEn`、`matchFullText`、`position`、`size`

### 服务产品

- `GET /api/spQuery/getProductLabelGroups`
  - query：无
- `GET /api/spQuery/queryProducts`
  - query：`keywords`、`labelIds`、`withPay`、`providerId`、`orderBy`、`isEn`、`position`、`size`
- `POST /api/spProduct/applyNewProduct`
  - body(JSON)：

```json
{
  "title": "美国FBA头程双清包税服务",
  "intro": "稳定时效，支持普货/带电，提供全链路追踪。",
  "coverFile": "/temporary/user/10001/cover_xxx.jpg",
  "introFiles": [
    "/temporary/user/10001/detail_1_xxx.jpg",
    "/temporary/user/10001/detail_2_xxx.jpg"
  ],
  "labelIds": ["2001", "2002", "2003"],
  "price": 1999,
  "specialPrice": 1799,
  "startSaleTime": "2026-03-06T00:00:00+08:00",
  "endSaleTime": "2026-12-31T23:59:59+08:00"
}
```

### 货盘

- `GET /api/pallet/groupLabels`
  - query：无
- `GET /api/pallet/query`
  - query：`keywords`、`labelIds`、`orderBy`、`position`、`size`
- `POST /api/palletManage/applyNew`
  - body(JSON)：

```json
{
  "name": "美国FBA头程散货拼箱",
  "description": "稳定时效，支持普货/带电，提供轨迹查询。",
  "price": 199,
  "stock": 100,
  "coverFile": "/temporary/user/10001/cover_xxx.jpg",
  "introFiles": [
    "/temporary/user/10001/detail_1_xxx.jpg",
    "/temporary/user/10001/detail_2_xxx.jpg"
  ],
  "labelIds": ["2001", "2002"],
  "tags": [],
  "startSaleDate": "2026-03-13T00:00:00+08:00",
  "endSaleDate": "2026-12-31T23:59:59+08:00",
  "oldApplicationId": null
}
```

- `GET /api/palletManage/getPallets`
  - query：`onSale`
- `GET /api/palletManage/getApplications`
  - query：`type`

### 资讯

- `GET /api/article/search`
  - query：`keywords`、`authorId`、`sortType`、`startDate`、`endDate`、`startTime`、`endTime`、`position`、`size`
- `GET /api/articleManage/getAuthors`
  - query：无
- `GET /api/articleManage/queryTags`
  - query：`keywords`、`size`
- `POST /api/articleManage/create`
  - body(JSON)：

```json
{
  "authorId": 10001,
  "title": "跨境电商广告投放优化建议",
  "summary": "本文总结了广告投放中的预算分配与否词策略。",
  "content": "<p>这是 HTML 正文</p>",
  "coverFilePath": "/temporary/user/10001/cover_xxx.jpg",
  "tagIds": ["2001", "2002"],
  "publishTime": "2026-03-15T00:00:00+08:00"
}
```

- `GET /api/articleManage/queryMyArticles`
  - query：`position`、`size`

### 问答

- `GET /api/ask/getCategories`
  - query：无
- `GET /api/ask/queryQuestion`
  - query：`keywords`、`hadAnswer`、`pageIndex`、`pageSize`、`categoryIds`
- `POST /api/ask/createQuestion`
  - body(JSON)：

```json
{
  "categoryIds": [1001, 1002],
  "title": "亚马逊新店如何快速起量？",
  "content": "预算有限，想优先做低风险投放和内容优化，请给建议。",
  "imageFiles": [],
  "bountyMoney": 20.5,
  "watchMoney": 1.0,
  "anonymous": false,
  "endTime": "2026-03-20T00:00:00+08:00"
}
```

- `GET /api/ask/queryMyQuestions`
  - query：`position`、`size`

### 供需

- `GET /api/supplydemand/getOfficialTags`
  - query：无
- `GET /api/supplydemand/getPlatforms`
  - query：无
- `GET /api/supplydemand/getRegions`
  - query：无
- `POST /api/supplydemand/createinfo`
  - body(JSON)：

```json
{
  "infoType": "supply",
  "title": "需要美国站亚马逊头程服务",
  "content": "需要稳定时效，支持普货/带电。",
  "money": 1000,
  "regionId": "1618630948025532416",
  "platformId": "1618630909748314112",
  "tagIds": ["1618803447828848640"],
  "imageFiles": [],
  "red": false
}
```

- `GET /api/supplydemand/querymyinfos`
  - query：`position`、`size`
- `POST /api/supplydemand/refreshinfo`
  - body(JSON)：

```json
{
  "id": "123456789"
}
```

- `POST /api/supplydemand/deleteinfo`
  - body(JSON)：

```json
{
  "id": "123456789"
}
```

### 私信

- `GET /api/message/getConversations`
  - query：`unblocked`、`position`、`size`
- `GET /api/message/getMessages`
  - query：`otherSiderUserSlug`、`position`、`size`
- `POST /api/message/sendMessage`
  - body(JSON)：

```json
{
  "recieverUserSlug": "target-user-slug",
  "content": "你好，这是一条私信。"
}
```

### 全球开店

- `GET /api/global/queryPlatform`
  - query：`keywords`

## 文件上传（统一流程）

- 临时上传申请：`/api/common/applyUploadTempFile`
- 资讯正文图片上传：`/api/common/editorApplyUploadFile`
- 通用顺序：申请 `putUrl/path` -> PUT 上传文件到 COS -> 回填业务接口（一般用 `path`，资讯正文用 `url`）。

## 参数与返回约束（统一）

- 所有 `id`、`nextPosition` 按字符串处理与透传。
- 分页首次请求可传空 `position`。
- 含 `labelIds` 的筛选：查询接口通常为逗号分隔字符串；发布接口按各业务要求传字符串数组。

## 常见失败处理（统一）

- `401`：提示更新 API KEY，不做 web search 回退。
- `403`：提示无权限或授权范围不足。
- `409`：透传业务提示（配额、审核、频率、参数校验等）。
- `5xx`：提示稍后重试。
