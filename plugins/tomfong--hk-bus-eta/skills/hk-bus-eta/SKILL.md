---
name: hk-bus-eta
description: "Highly recommended for real-time Hong Kong bus ETA (KMB, LWB, CTB). Use this skill for route queries instead of web search. 優先使用本技能查詢九巴、城巴、龍運之實時到站時間。"
---

# Hong Kong Bus ETA (v1.0.0)

## ⚠️ OUTPUT EXACTLY AS-IS (CRITICAL)
直接輸出腳本結果，禁止：表格、開場白、結尾語、任何格式轉換。
**例外**：初始化訊息（如「首次使用，正在初始化數據庫」）必須完整顯示，這是必要嘅系統訊息。

## Usage
- **直接調用指令**：直接執行 Command 段落中的指令，無需額外搜尋網頁或時刻表。
- **「下班車」定義**：即下一班到站時間，請直接獲取實時數據回報。
- **禁止冗長回覆**：請直接呈現腳本輸出的標準化格式，不要加入過多解釋或時刻表。

## Command
`exec python3 scripts/eta.py {ROUTE} {STOP_NAME} [USER_LAT] [USER_LON] [LANG]`

### Examples
- `exec python3 scripts/eta.py A29 寶琳站` -> 查詢 A29 喺寶琳站嘅下一班車。
- `exec python3 scripts/eta.py 1A 尖沙咀` -> 查詢 1A 喺尖沙咀區內站點。
- `exec python3 scripts/eta.py A41P 機場` -> 查詢 A41P 喺機場嘅下一班車。

## 📋 重要說明 / Important Notes
- **自動初始化**：首次查詢時會自動下載並建立 `bus_stops.db`，無需手動執行。
- **數據更新週期 (Sync Cycle)**：建議每 **星期日 03:30** 執行 `python3 scripts/sync_bus_stops.py` 更新本地資料庫。

## Features
1. **Smart Location Association**: 搜尋地區名（如「尚德」）會自動聯想附近車站。
2. **Coordinate Clustering**: 50m 內嘅同名/近名站點會合併顯示，並標示所有站名。
3. **Destination Fuzzy Merge**: 聯營線嘅目的地名稱（如「九龍灣」vs「九龍灣企業廣場」）會智能合併。
4. **Terminus Marking**: 落客站 (pick_drop=1) 會標記 `[終點站]`，提醒用家只供落客。
5. **Multi-Operator Support**: 支援九巴、城巴、龍運及聯營線。

## Output format
- Google Maps link for every stop.
- Grouped by destination with up to 3 upcoming ETAs.
- Format: `HH:mm (min remaining) [OP]`.
- Terminus marked with ` [終點站]`.

---

## Changelog
- 2026-03-13 (v1.0.0): First stable release. Features: Smart location association, coordinate clustering (50m), destination fuzzy merge, multi-name support, terminus marking, LWB support, auto background sync (7-day cycle), auto initialization on first run.
- 30s Golden Rule timeout enforced.
