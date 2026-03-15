---
name: amber_energy_manager
description: "获取 Amber Electric 的实时电价、预测电价及站点信息。支持获取当前价格、预测价格和站点列表。"
---

# Amber Electric 能源助手
此技能允许 OpenClaw 接入澳洲 Amber Electric 的批发电价数据。

### 主要功能
- **查看站点**：获取你名下的 NMI 和站点 ID。
- **实时价格**：获取当前的电价等级（如 `extremelyLow`, `spike`）和具体数值。
- **电价预测**：获取未来 24 小时的价格趋势，优化大功率电器使用时间。

### 配置要求
需要在环境变量或 `openclaw.json` 中配置：
`AMBER_API_KEY`: 你的 Amber API 令牌。

