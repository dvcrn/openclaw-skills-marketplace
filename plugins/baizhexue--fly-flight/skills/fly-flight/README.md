# Fly Flight

An OpenClaw skill for querying China domestic flights from publicly accessible Tongcheng flight pages, without requiring a private API key.

## 中文介绍

`fly-flight` 是一个面向 OpenClaw 的国内航班查询技能。它不依赖私有航班 API，而是基于同程公开航班页面抓取国内航班信息，返回航司、航班号、起降机场、起降时间、飞行时长和公开页面参考票价。

### 适用场景

- 查询指定日期的中国国内航班
- 对比不同航班的参考票价
- 按中文城市名、机场名或 IATA 三字码查询
- 给出行助手或旅行 agent 提供公开航班信息

### 功能特点

- 支持中国国内单程航班查询
- 支持往返查询
- 支持中文城市名、机场名和 IATA 三字码输入
- 返回航司、航班号、起降机场、时间、时长和参考票价
- 默认按价格排序
- 支持按价格、最早出发、最早到达、最短时长排序
- 支持仅直飞、航司筛选、机场偏好筛选
- 不需要申请私有 API key
- 支持直接命令行查询
- 支持可选本地 HTTP 服务模式

### 信息来源

- 同程公开航班页面：`https://www.ly.com/flights/`
- 通过抓取公开 HTML 并解析页面中的 `window.__NUXT__` 数据获取航班列表

### 运行依赖

- `python3`
- `node`
- 可访问同程公开航班页面的网络环境

### 使用说明

直接命令行查询：

```bash
python3 ./scripts/domestic_flight_public_service.py search \
  --from 北京 --to 上海 --date 2026-03-20 --sort-by price --pretty
```

往返查询：

```bash
python3 ./scripts/domestic_flight_public_service.py search \
  --from 北京 --to 上海 --date 2026-03-20 --return-date 2026-03-23 \
  --direct-only --sort-by price --pretty
```

启动本地 HTTP 服务：

```bash
python3 ./scripts/domestic_flight_public_service.py serve --port 8766
```

然后请求：

```bash
curl 'http://127.0.0.1:8766/search?from=北京&to=上海&date=2026-03-20'
```

### 示例提问

- `帮我查 2026-03-20 北京到上海最便宜的航班`
- `帮我查 2026-03-20 北京到上海往返直飞航班`
- `查一下明天广州到成都的航班和价格`
- `帮我看首都机场到深圳宝安当天有哪些航班`
- `上海虹桥到重庆，按价格从低到高列 5 个`
- `帮我找东航从北京到上海最早出发的航班`

### 限制说明

- 仅支持中国国内航班
- 价格来自公开页面，仅作参考，不保证等于最终出票价
- 抓取逻辑依赖公开网页结构，页面改版或反爬加强后可能失效
- 数据完整性和时效性由公开页面决定
- 往返查询本质上由两次单程公开页抓取组合而成

### 仓库结构

- `SKILL.md`: skill 指令和触发描述
- `agents/openai.yaml`: UI 展示信息
- `scripts/domestic_flight_public_service.py`: 主查询脚本
- `scripts/extract_tongcheng_state.js`: 页面数据提取脚本
- `references/provider-public-web.md`: 信息源说明
- `assets/data/*.json`: 城市与机场别名映射

## English

`fly-flight` is an OpenClaw skill for querying China domestic flights from publicly accessible Tongcheng flight pages. It does not rely on a private flight API. Instead, it fetches public route pages and extracts airline, flight number, airports, departure and arrival times, duration, and public reference fares.

### Use Cases

- Query China domestic flights for a specific date
- Compare public reference fares across flight options
- Search by Chinese city names, airport names, or IATA codes
- Power travel assistants or flight lookup agents with public flight data

### Features

- China domestic one-way flight lookup
- Round-trip lookup via paired one-way searches
- Chinese city, airport, and IATA code input support
- Airline, flight number, airport, time, duration, and fare output
- Price-sorted results
- Sorting by price, departure time, arrival time, or duration
- Direct-only, airline, and airport-preference filters
- No private API key required
- Direct CLI usage
- Optional local HTTP service mode

### Data Source

- Tongcheng public flight pages: `https://www.ly.com/flights/`
- The scraper fetches public HTML and extracts flight data from the page's `window.__NUXT__` payload

### Requirements

- `python3`
- `node`
- Network access to Tongcheng public flight pages

### Usage

Direct CLI query:

```bash
python3 ./scripts/domestic_flight_public_service.py search \
  --from 北京 --to 上海 --date 2026-03-20 --sort-by price --pretty
```

Round-trip query:

```bash
python3 ./scripts/domestic_flight_public_service.py search \
  --from 北京 --to 上海 --date 2026-03-20 --return-date 2026-03-23 \
  --direct-only --sort-by price --pretty
```

Start the optional local HTTP service:

```bash
python3 ./scripts/domestic_flight_public_service.py serve --port 8766
```

Then request:

```bash
curl 'http://127.0.0.1:8766/search?from=北京&to=上海&date=2026-03-20'
```

### Example Prompts

- `Find the cheapest flights from Beijing to Shanghai on 2026-03-20`
- `Find round-trip nonstop flights from Beijing to Shanghai`
- `Show flights and fares from Guangzhou to Chengdu tomorrow`
- `List today's flights from Beijing Capital to Shenzhen Bao'an`
- `Show 5 Shanghai Hongqiao to Chongqing flights sorted by price`
- `Find the earliest China Eastern flight from Beijing to Shanghai`

### Limitations

- China domestic flights only
- Fares are public-page reference fares, not guaranteed checkout prices
- The scraper depends on the public page structure and may break if the site changes
- Data freshness and completeness depend on the public source
- Round trips are assembled from two one-way public page lookups

## Publishing

This repository is structured so it can be used directly as a GitHub-backed OpenClaw skill source.
