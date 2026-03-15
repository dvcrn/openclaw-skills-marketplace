---
name: jisu-car
description: "使用极速数据车型大全 API 查询汽车品牌、车系、具体车款、车型详情、车型搜索、热门车型和销量排行榜。"
---

# 极速数据车型大全（Jisu Car）

基于 [车型大全 API](https://www.jisuapi.com/api/car) 的 OpenClaw 技能，提供：

- **获取所有品牌**（`/car/brand`）
- **根据品牌获取车型**（`/car/type`）
- **根据车型获取车款**（`/car/car`）
- **根据 ID 获取车型详情**（`/car/detail`）
- **车型搜索**（`/car/search`）
- **获取热门车型**（`/car/hot`）
- **获取销量排行榜**（`/car/rank`）

可用于对话中回答「某品牌有哪些车系和车款」「这款车的详细配置」「当前热门 SUV」「本月销量排行前十车型」等问题。

使用技能前需要申请数据，申请地址：https://www.jisuapi.com/api/car

## 环境变量配置

```bash
# Linux / macOS
export JISU_API_KEY="your_appkey_here"

# Windows PowerShell
$env:JISU_API_KEY="your_appkey_here"
```

## 脚本路径

脚本文件：`skills/car/car.py`

## 使用方式

### 1. 获取所有品牌（brand）

```bash
python3 skills/car/car.py brand
```

### 2. 根据品牌获取车型（type）

```bash
python3 skills/car/car.py type '{"parentid":"1"}'
```

### 3. 根据车型获取车款（car）

```bash
python3 skills/car/car.py car '{"parentid":"220"}'
```

可选参数：`sort`（如 `year`、`yearr` 等）、`isnev`（`1` 仅返回新能源）。

### 4. 根据 ID 获取车型详情（detail）

```bash
python3 skills/car/car.py detail '{"carid":2571}'
```

### 5. 车型搜索（search）

```bash
python3 skills/car/car.py search '{"keyword":"奔驰E级2017款E200运动版"}'
```

### 6. 热门车型（hot）

```bash
# 不指定价格区间：返回 5–50 万热门车型
python3 skills/car/car.py hot '{}'

# 指定价格区间：1=5-8万 2=8-15万 3=15-20万 4=20-30万 5=30-50万
python3 skills/car/car.py hot '{"pricetype":"2"}'
```

### 7. 销量排行榜（rank）

```bash
python3 skills/car/car.py rank '{"ranktype":"1","month":"2025-01","week":""}'
```

`ranktype`：`1` 车型排名，`2` 品牌排名。`month` 格式 `xxxx-xx`，`week` 格式 `xxxx-xx-xx`（周一日期）。

## 请求参数摘要

| 子命令   | 必填参数      | 可选参数                          |
|----------|---------------|-----------------------------------|
| type     | parentid      | —                                 |
| car      | parentid      | sort, isnev                       |
| detail   | carid         | —                                 |
| search   | keyword       | —                                 |
| hot      | —             | pricetype（1–5）                  |
| rank     | ranktype      | month, week                       |

## 返回结果说明

脚本直接输出接口的 `result` 字段（JSON）。结构因接口而异：

- **brand**：数组，每项含 `id`、`name`、`initial`、`parentid`、`logo`、`depth`。
- **type**：数组，每项含品牌/子公司及下属车型列表 `list`。
- **car**：对象，含车系信息及具体车款列表 `list`（含 id、name、price、yeartype、salestate、sizetype 等）。
- **detail**：对象，含车型完整详情（basic、body、engine、gearbox、safe 等）。
- **search**：对象，含 `keyword` 与匹配的 `list`。
- **hot**：数组，按车型类型分组的热门车系（sizetype、name、carid）。
- **rank**：对象，含 `date`、`week`、`ranktype` 及 `list`（carid、num、type、cartype 等）。

错误时输出形如：

```json
{
  "error": "api_error",
  "code": 202,
  "message": "车型ID错误"
}
```

## 常见错误码

来自 [极速数据车型大全文档](https://www.jisuapi.com/api/car)：

| 代号 | 说明       |
|------|------------|
| 201  | 上级ID错误 |
| 202  | 车型ID错误 |
| 205  | 没有信息   |

系统错误码：101 APPKEY 为空或不存在、102 已过期、103 无权限、104 超过次数限制、105 IP 被禁止、106 IP 超限、107 接口维护中、108 接口已停用。

## 在 OpenClaw 中的推荐用法

1. 用户例如：「奥迪有哪些车系？」→ 先 `brand` 查奥迪 id，再 `type '{"parentid":"1"}'`（以实际 id 为准）。  
2. 「奥迪 A3 有哪些具体车款？」→ `car '{"parentid":"220"}'`。  
3. 「查一下车 ID 2571 的详细配置」→ `detail '{"carid":2571}'`。  
4. 「搜一下奔驰 E 级 2017 款」→ `search '{"keyword":"奔驰E级2017款"}'`。  
5. 「当前热门 SUV / 8–15 万热门车」→ `hot '{"pricetype":"2"}'`，再根据返回解析。  
6. 「本月销量前十车型」→ `rank '{"ranktype":"1","month":"2025-01"}'`，解析 `list` 并可选结合 detail 补全名称。
