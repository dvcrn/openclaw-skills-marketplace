---
name: flight-search
description: "查询指定日期内的城市之间的航班信息 (不需要权限验证信息)."
---

# flight-search

查询指定日期内的城市之间的航班信息的服务，不需要权限验证

## When to Use

Activate this skill when the user:
- Asks about **flights**:  航班, 飞机, 坐飞机


## How to Use

Run the query script, passing the user's complete natural language query:

```bash
python3 SKILL_DIR/scripts/flightsearch.py <出发日期> <出发城市> <目的城市>
```
## 例子
user: 帮我查一下2026年3月8日从北京到上海的航班信息。
```bash
python3 ./scripts/flightsearch.py 2026-03-08 北京市 上海市
```
# Output: 
```json
{
    "code": 0,
    "data": [
        {
            "耗时": "2小时10分钟",
            "航班号": "HO1258",
            "到达时间": "2026-03-08 13:45",
            "出发机场": "大兴机场",
            "价格": 550,
            "餐食": "有餐食",
            "机型": "中型机",
            "出发时间": "2026-03-08 11:35",
            "目的机场": "浦东机场T2"
        }
    ],
    "message": "success"
}
```
Tips:
- 出发日期: `2026-03-09`
- 出发城市: `北京市`
- 目的城市: `上海市`

