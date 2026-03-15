---
name: jisu-weather2
description: "使用极速数据历史天气 API，按城市与日期查询历史天气（最高最低温、风级、湿度、气压、日出日落、AQI 等）。"
---

# 极速数据历史天气（Jisu Weather2）

基于 [历史天气 API](https://www.jisuapi.com/api/weather2/) 的 OpenClaw 技能，支持按城市（或城市 ID）与日期查询全国 3000+ 省市的历史天气，包括最高/最低温度、风级、湿度、气压、日出日落时间、空气质量指数、首要污染物等。

使用技能前需要申请数据，申请地址：https://www.jisuapi.com/api/weather2/

## 环境变量配置

```bash
# Linux / macOS
export JISU_API_KEY="your_appkey_here"

# Windows PowerShell
$env:JISU_API_KEY="your_appkey_here"
```

## 脚本路径

脚本文件：`skill/weather2/weather2.py`

## 使用方式

### 1. 历史天气查询（query）

```bash
python3 skill/weather2/weather2.py query '{"city":"北京","date":"2018-01-01"}'
python3 skill/weather2/weather2.py query '{"cityid":111,"date":"2018-01-01"}'
```

| 参数   | 类型   | 必填 | 说明 |
|--------|--------|------|------|
| city   | string | 否   | 城市名（与 cityid 二选一） |
| cityid | int    | 否   | 城市 ID（见 city 命令）   |
| date   | string | 是   | 日期，格式 2018-01-01，默认为昨天 |

返回字段示例：cityid, cityname, date, weather, temphigh, templow, img, humidity, pressure, windspeed, windpower, sunrise, sunset, aqi, primarypollutant 等。

### 2. 获取城市列表（city）

```bash
python3 skill/weather2/weather2.py city '{}'
```

无参数，返回支持历史天气查询的城市列表（cityid, parentid, citycode, city）。

## 常见错误码

| 代号 | 说明           |
|------|----------------|
| 201  | 城市和城市ID都为空 |
| 202  | 城市不存在     |
| 203  | 查询日期为空   |
| 204  | 日期格式不正确 |
| 210  | 没有信息       |

系统错误码 101–108 见极速数据官网。

## 在 OpenClaw 中的推荐用法

1. 用户问「北京 2018 年 1 月 1 日天气如何」时，先调用 `query`，传入 `city`（或 `cityid`）与 `date`。
2. 若需城市 ID，可先调用 `city` 获取列表再查。
3. 从返回的 result 中取 weather、temphigh、templow、aqi 等用自然语言回复。更多接口与计费见 [极速数据](https://www.jisuapi.com/)。
