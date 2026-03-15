---
name: live-location-mapper
description: "Live Location Mapper"
---

# live-location-mapper

> Version: 1.0.0
> Price: 1.0 USDT per use

通过抖音直播搜索地点，并在百度地图上标记位置。

## 触发条件

用户要求：
- 查看某地附近的直播
- 查找直播位置
- 在地图上标记直播地点
- 估算某地人流量

## 核心功能

### 1. 搜索抖音直播

1. 打开抖音搜索：https://www.douyin.com/search/[地点]直播
2. 筛选"直播"tab
3. 记录正在直播的账号和位置描述

### 2. 获取经纬度坐标

需要**百度地图 API Key (AK)**：
1. 申请地址：https://lbsyun.baidu.com/
2. 免费申请，创建应用获取AK

使用API获取坐标：
```python
import requests
ak = "你的AK"

# 搜索地点坐标
url = f"https://api.map.baidu.com/place/v2/search?query=外滩&region=上海&output=json&ak={ak}"
data = requests.get(url).json()
lat = data['results'][0]['location']['lat']
lng = data['results'][0]['location']['lng']
```

### 3. 生成地图标记图

```python
import requests

ak = "你的AK"
locations = [
    ("主播名(位置)", 经度, 纬度),
    ("东方明珠", 121.506269, 31.2455),
    ("南京路步行街", 121.486099, 31.241924),
]

# 生成静态地图
center = f"{lng},{lat}"
markers = "|".join([f"{lng},{lat}" for _,lng,lat in locations])
url = f"https://api.map.baidu.com/staticimage/v2?center={center}&zoom=15&width=800&height=600&markers={markers}&markerStyles=-1,http://api.map.baidu.com/images/marker_red.png,-1,25,25&ak={ak}"

# 下载图片
img = requests.get(url).open('map.png', 'wb').write(img.content)
```

## 使用示例

用户要求查找上海外滩的直播并在地图上标记：

1. 搜索"上海外滩直播" → 找到10+个直播间
2. 记录主要位置：外滩、东方明珠、南京路步行街等
3. 用百度地图API获取各位置经纬度
4. 生成带标记的静态地图图片
5. 发送给用户

## 注意事项

- 百度地图AK需要申请，地址：https://lbsyun.baidu.com/
- 直播是位置估算的，不是精确位置
- 需要标记多个点时用"|"分隔坐标
- 静态地图API返回PNG图片

## 常见位置坐标（上海外滩）

| 地点 | 经度 | 纬度 |
|------|------|------|
| 外滩观景台 | 121.499318 | 31.238549 |
| 东方明珠 | 121.506269 | 31.2455 |
| 南京路步行街 | 121.486099 | 31.241924 |
| 十六铺码头 | 121.50488 | 31.233644 |
| 外白渡桥 | 121.49696 | 31.249557 |
