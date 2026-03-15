---
name: jisu-weather
description: "使用极速数据全国天气预报 API 查询实时天气、7天天气预报、24小时逐小时天气、空气质量指数和生活指数等信息，并支持获取完整城市列表。"
---

# 极速数据全国天气预报（Jisu Weather）

基于 [全国天气预报 API](https://www.jisuapi.com/api/weather/) 的 OpenClaw 技能，可查询：

- **当前实时天气**
- **未来 7 天预报（`daily`）**
- **未来 24 小时逐小时预报（`hourly`）**
- **空气质量 AQI 指数**
- **生活指数（穿衣、运动、洗车等）**
- **城市列表（`/weather/city`）**

使用技能前需要申请数据，申请地址：https://www.jisuapi.com/api/weather/

## 环境变量配置

```bash
# Linux / macOS
export JISU_API_KEY="your_appkey_here"

# Windows PowerShell
$env:JISU_API_KEY="your_appkey_here"
```

## 脚本路径

脚本文件：`skills/weather/weather.py`

## 使用方式

### 1. 按城市名称查询天气

```bash
python3 skills/weather/weather.py '{"city":"杭州"}'
```

### 2. 按城市 ID / 城市代号查询

```bash
python3 skills/weather/weather.py '{"cityid":111}'
python3 skills/weather/weather.py '{"citycode":"101260301"}'
```

### 3. 按经纬度或 IP 查询

```bash
# 经纬度：纬度在前，逗号分隔
python3 skills/weather/weather.py '{"location":"39.983424,116.322987"}'

# IP
python3 skills/weather/weather.py '{"ip":"8.8.8.8"}'
```

> 请求 JSON 中至少要提供 `city` / `cityid` / `citycode` / `location` / `ip` 中的一个字段。

### 4. 获取支持的城市列表

对应极速数据 `/weather/city` 接口：

```bash
python3 skills/weather/weather.py cities
```

返回值为数组，每一项形如：

```json
{
  "cityid": "1",
  "parentid": "0",
  "citycode": "101010100",
  "city": "北京"
}
```

## 请求参数（天气查询 JSON）

| 字段名   | 类型   | 必填 | 说明                                                                 |
|---------|--------|------|----------------------------------------------------------------------|
| city    | string | 否   | 城市名称，如 `"杭州"`                                               |
| cityid  | int    | 否   | 城市 ID                                                              |
| citycode| string | 否   | 城市天气代号                                                         |
| location| string | 否   | 经纬度，纬度在前，逗号分隔，如 `"39.983424,116.322987"`              |
| ip      | string | 否   | IP 地址                                                              |

> 至少需要提供上述 5 个字段中的一个，否则脚本会报错并退出。

示例请求：

```json
{
  "city": "安顺",
  "cityid": 111,
  "citycode": "101260301"
}
```

## 返回结果示例

脚本直接输出接口的 `result` 字段（JSON），典型结构与官网示例一致：

```json
{
  "city": "安顺",
  "cityid": "111",
  "citycode": "101260301",
  "date": "2015-12-22",
  "week": "星期二",
  "weather": "多云",
  "temp": "16",
  "temphigh": "18",
  "templow": "9",
  "humidity": "55",
  "windspeed": "14.0",
  "winddirect": "南风",
  "windpower": "2级",
  "index": [
    {
      "iname": "空调指数",
      "ivalue": "较少开启",
      "detail": "您将感到很舒适，一般不需要开启空调。"
    }
  ],
  "aqi": {
    "aqi": "35",
    "primarypollutant": "PM10",
    "quality": "优",
    "timepoint": "2015-12-09 16:00:00"
  },
  "daily": [
    {
      "date": "2015-12-22",
      "week": "星期二",
      "sunrise": "07:39",
      "sunset": "18:09",
      "night": {
        "weather": "多云",
        "templow": "9",
        "img": "1",
        "winddirect": "无持续风向",
        "windpower": "微风"
      },
      "day": {
        "weather": "多云",
        "temphigh": "18",
        "img": "1",
        "winddirect": "无持续风向",
        "windpower": "微风"
      }
    }
  ],
  "hourly": [
    {
      "time": "16:00",
      "weather": "多云",
      "temp": "14",
      "img": "1"
    }
  ]
}
```

当出现错误（如城市不存在、没有天气信息等）时，脚本会输出：

```json
{
  "error": "api_error",
  "code": 202,
  "message": "城市不存在"
}
```

## 常见错误码

来源于极速数据文档部分错误码：

| 代号 | 说明                         |
|------|------------------------------|
| 201  | 城市和城市ID和城市代号都为空 |
| 202  | 城市不存在                   |
| 203  | 此城市没有天气信息           |
| 210  | 没有信息                     |

系统错误码：

| 代号 | 说明               |
|------|--------------------|
| 101  | APPKEY 为空或不存在|
| 102  | APPKEY 已过期      |
| 103  | APPKEY 无请求权限  |
| 104  | 请求超过次数限制   |
| 105  | IP 被禁止          |

## 在 OpenClaw 中的推荐用法

1. 用户输入：「查下杭州今天的天气和未来几天下雨情况」。  
2. 代理构造 JSON：`{"city":"杭州"}` 并调用：  
   `python3 skills/weather/weather.py '{"city":"杭州"}'`  
3. 从返回 JSON 中提取当前天气、`daily` / `hourly` 的降水相关字段，为用户生成自然语言总结。  
4. 如需城市编码或城市 ID，可先调用：`python3 skills/weather/weather.py cities`，在结果中查找目标城市后再发起天气查询。

