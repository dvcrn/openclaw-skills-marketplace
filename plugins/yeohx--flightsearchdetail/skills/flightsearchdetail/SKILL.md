---
name: flightsearchdetail
description: "查询指定航班号的航班详细信息 (不需要权限验证信息)."
---

# flightsearchdetail

查询指定航班号的航班详细信息，不需要权限验证

## When to Use

Activate this skill when the user:
- Asks about **flights**:  航班座位信息，航班详细信息


## How to Use

Run the query script, passing the user's complete natural language query:

```bash
python3 SKILL_DIR/scripts/flightsearchdetail.py <出发机场三字码> <目的机场三字码> <出发日期> <航班号>
```
## 例子
user: 帮我查一下HU7601航班的详细信息。
```bash
python3 ./scripts/flightsearchdetail.py PEK SHA 2026-03-08 HU7601
```
# Output: 
```json
{
  "code": 0,
  "data": [
    {
      "航班号": "HU7601",
      "舱位类型": "公务舱",
      "价格": 2150,
      "目的机场三字码": "SHA",
      "出发机场三字码": "PEK"
    }
  ]
}
```
Tips:
- 出发日期: `2026-03-09`
- 出发机场三字码: `SHA`
- 目的机场三字码: `PEK`

