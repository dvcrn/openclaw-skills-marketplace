---
name: jisu-vehiclelimit
description: "使用极速数据车辆尾号限行 API，查询各城市车辆限行时间、区域与尾号规则，并获取支持限行查询的城市列表。"
---

# 极速数据车辆尾号限行（Jisu VehicleLimit）

基于 [车辆尾号限行 API](https://www.jisuapi.com/api/vehiclelimit/) 的 OpenClaw 技能，支持：

- **获取城市列表**（`/vehiclelimit/city`）
- **城市限行查询**（`/vehiclelimit/query`）

目前支持北京、天津、杭州、成都、兰州、贵阳、南昌、长春、哈尔滨、武汉、上海、深圳等城市。

使用技能前需要申请数据，申请地址：https://www.jisuapi.com/api/vehiclelimit/

## 环境变量配置

```bash
# Linux / macOS
export JISU_API_KEY="your_appkey_here"

# Windows PowerShell
$env:JISU_API_KEY="your_appkey_here"
```

## 脚本路径

脚本文件：`skills/vehiclelimit/vehiclelimit.py`

## 使用方式

### 1. 获取支持限行的城市列表（/vehiclelimit/city）

```bash
python3 skills/vehiclelimit/vehiclelimit.py cities
```

返回结果示例：

```json
[
  {
    "city": "beijing",
    "cityname": "北京"
  },
  {
    "city": "hangzhou",
    "cityname": "杭州"
  }
]
```

### 2. 查询城市在某日的限行信息（/vehiclelimit/query）

```bash
python3 skills/vehiclelimit/vehiclelimit.py '{"city":"hangzhou","date":"2015-12-02"}'
```

请求 JSON 示例：

```json
{
  "city": "hangzhou",
  "date": "2015-12-02"
}
```

## 请求参数

### 城市列表

无需额外参数，仅需 `appkey`。

### 限行查询

| 字段名 | 类型   | 必填 | 说明                           |
|--------|--------|------|--------------------------------|
| city   | string | 是   | 城市代号，如 `hangzhou`       |
| date   | string | 是   | 日期，格式如 `2015-12-02`      |

## 返回结果示例（限行查询）

```json
{
  "city": "hangzhou",
  "cityname": "杭州",
  "date": "2015-12-03",
  "week": "星期四",
  "time": [
    "07:00-09:00",
    "16:30-18:30"
  ],
  "area": "1、本市号牌：留祥路—石祥路—石桥路……\n2、外地号牌：上述“错峰限行”区域以及绕城高速合围区域内的其他高架道路……",
  "summary": "本市号牌尾号限行，外地号牌全部限行。法定上班的周六周日不限行。",
  "numberrule": "最后一位数字",
  "number": "4和6"
}
```

## 常见错误码

来源于 [极速数据车辆尾号限行文档](https://www.jisuapi.com/api/vehiclelimit/)：

| 代号 | 说明       |
|------|------------|
| 201  | 城市为空   |
| 202  | 城市不存在 |
| 210  | 没有信息   |

系统错误码：

| 代号 | 说明                 |
|------|----------------------|
| 101  | APPKEY 为空或不存在  |
| 102  | APPKEY 已过期        |
| 103  | APPKEY 无请求权限    |
| 104  | 请求超过次数限制     |
| 105  | IP 被禁止            |

## 在 OpenClaw 中的推荐用法

1. 用户提问：「明天杭州限行什么尾号？」  
2. 代理先使用 `cities` 子命令确认 `hangzhou` 在支持列表中（可缓存），然后构造 JSON：`{"city":"hangzhou","date":"2025-04-22"}` 并调用：  
   `python3 skills/vehiclelimit/vehiclelimit.py '{"city":"hangzhou","date":"2025-04-22"}'`  
3. 从返回结果中读取 `time`、`area`、`summary`、`numberrule` 和 `number` 字段，为用户生成简要说明：当天何时、何地、哪些尾号限行。  

