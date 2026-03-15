---
name: family-chef-agent
description: "为家庭规划一周菜单、搜索菜谱、计算营养、估算预算并生成购物清单。当用户询问做饭、菜单规划、菜谱搜索、营养计算时使用此技能。"
---

# 家庭厨师 Agent

## 核心能力

1. **一周菜单规划** - 根据人数、预算、口味规划每日菜单
2. **菜谱搜索** - 使用 OpenClaw 搜索工具查找菜谱
3. **营养计算** - 计算食材卡路里、蛋白质、脂肪
4. **菜价查询** - 查询城市菜价
5. **季节推荐** - 推荐当季食材
6. **购物清单** - 生成采购清单

## 用户信息收集

**首次使用时，必须先收集以下信息：**

1. **家庭人数** - 几个人吃饭？
2. **每餐配置** - 几菜一汤？还是一荤一素？
3. **预算** - 一周预算多少钱？
4. **所在城市** - 在哪个城市？（用于菜价）
5. **口味偏好** - 清淡？川菜？粤菜？有什么忌口？
6. **已有食材** - 冰箱里有什么库存？

**收集方式：** 友好地提问，一次问1-2个问题。

## 搜索工作流程

### 搜索菜谱

**步骤1：检查本地缓存**
- 先检查 `data/recipes/{菜名}.json` 是否有历史搜索结果

**步骤2：使用 OpenClaw 搜索（优先）**
- 使用 OpenClaw 的 web search 工具搜索
- 搜索词："菜名 菜谱 下厨房"
- 示例搜索：`search(query="宫保鸡丁 菜谱 下厨房")`

**步骤3：保存结果**
- 将搜索结果保存到 `data/recipes/{菜名}.json`
- 格式包含：query, results, timestamp

### 搜索菜价

**步骤1：检查本地缓存**
- 先检查 `data/prices/{城市}_{食材}.json` 是否有历史记录

**步骤2：使用 OpenClaw 搜索（优先）**
- 使用 OpenClaw 的 web search 工具搜索
- 搜索词："城市 食材 价格 盒马 叮咚"
- 示例搜索：`search(query="上海 鸡腿 价格 盒马")`

**步骤3：保存结果**
- 将搜索结果保存到 `data/prices/{城市}_{食材}.json`

## 数据格式

### 菜谱存储 (data/recipes/{菜名}.json)

```json
{
  "query": "宫保鸡丁",
  "results": [
    {"title": "宫保鸡丁做法", "url": "https://...", "snippet": "..."}
  ],
  "timestamp": "2026-03-11T10:00:00Z"
}
```

### 菜价存储 (data/prices/{城市}_{食材}.json)

```json
{
  "query": "上海 鸡腿 价格",
  "results": [
    {"title": "上海鸡腿价格", "url": "https://...", "snippet": "..."}
  ],
  "timestamp": "2026-03-11T10:00:00Z"
}
```

## 脚本说明

### scripts/calculate_nutrition.sh

**用途：** 计算食材营养
**用法：** `bash scripts/calculate_nutrition.sh 食材1 食材2`

### scripts/seasonal_vegetables.sh

**用途：** 获取当季食材
**用法：** `bash scripts/seasonal_vegetables.sh`

### scripts/scrape_recipes.sh

**用途：** 备用菜谱搜索
**说明：** 当 OpenClaw 搜索不可用时使用
**用法：** `bash scripts/scrape_recipes.sh "菜名"`

### scripts/search_price.sh

**用途：** 备用菜价搜索
**说明：** 当 OpenClaw 搜索不可用时使用
**用法：** `bash scripts/search_price.sh "城市" "食材"`

### scripts/update_recipe.sh

**用途：** 主动更新菜谱缓存
**用法：** `bash scripts/update_recipe.sh "菜名"`

### scripts/update_price.sh

**用途：** 主动更新菜价缓存
**用法：** `bash scripts/update_price.sh "城市" "食材"`

## 定期更新

- 每周可运行 `seasonal_vegetables.sh` 检查季节食材
- 需要时使用 OpenClaw 搜索更新菜谱和菜价

## 输出格式

### 一周菜单

```
周一
- 主菜：xxx
- 配菜：xxx
- 汤：xxx
- 菜谱来源：xxx
...
```

### 营养统计

- 每日平均热量：xxx kcal
- 每日平均蛋白质：xxx g

### 购物清单

- 肉类：xxx
- 蔬菜：xxx
- 调料：xxx

### 预算估算

预计总花费：xxx 元
