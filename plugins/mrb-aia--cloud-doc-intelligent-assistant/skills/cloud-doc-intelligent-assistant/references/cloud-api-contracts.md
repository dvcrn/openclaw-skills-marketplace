# 云厂商 API 契约

这份文档记录 crawler 当前依赖的在线接口契约。只要 API 字段映射变化，就要同步更新这里。

## 标准输出要求

所有云厂商的详情抓取，最终都要能落到这些统一字段：

- `Document.url`
- `Document.title`
- `Document.content`
- `Document.last_modified`
- `Document.metadata`

metadata key 在各云之间保持对齐：

- `cloud`
- `image_urls`
- `image_count`
- 云厂商特有标识，例如 `product_id`、`doc_id`、`lib_id`、`slug`
- 来源时间字段，例如 `recent_release_time`、`update_time`、`date`

## 阿里云

| 项目 | 值 |
| --- | --- |
| 代码文件 | `src/crawler.py` |
| 发现接口 | `menupath.json` |
| 详情接口 | `document_detail.json` |
| 产品标识 | alias，例如 `/vpc` |
| 页面标识 | alias，例如 `/vpc/what-is-vpc` |
| 更新时间字段 | `lastModifiedTime` |

## 腾讯云

| 项目 | 值 |
| --- | --- |
| 代码文件 | `src/tencent_crawler.py` |
| 发现接口 | `startup` 搜索 API |
| 详情接口 | `getDocPageDetail` |
| 产品标识 | 人类可读产品名，例如 `VPN 连接` |
| 页面标识 | `product_id + doc_id` |
| 更新时间字段 | 优先 `recentReleaseTime` |

## 百度云

| 项目 | 值 |
| --- | --- |
| 代码文件 | `src/baidu_crawler.py` |
| 发现接口 | `portalsearch` |
| 详情接口 | Gatsby `page-data.json` |
| 产品标识 | 产品代码，例如 `VPC` |
| 页面标识 | `product + slug` |
| 更新时间字段 | `fields.date` |

## 火山引擎

| 项目 | 值 |
| --- | --- |
| 代码文件 | `src/volcano_crawler.py` |
| 发现接口 | `searchAll` |
| 详情接口 | `getDocDetail` |
| 产品标识 | 人类可读产品名，例如 `NAT网关` |
| 页面标识 | `lib_id + doc_id` |
| 更新时间字段 | `UpdatedTime` |
