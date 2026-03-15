---
name: baidu-ecommerce-search
description: "Baidu e-commerce search, including CPS product search, rankings, product specifications, brand and category knowledge.百度电商搜索,包括cps商品查询、榜单、商品参数、品牌品类知识等能力"
homepage: https://openai.baidu.com
---

# baidu-ecommerce-search

百度电商搜索，包括商品对比、榜单、商品参数、品牌品类知识等能力。

## Setup

### 环境依赖

- Python 3.x（使用标准库 `urllib`、`json`、`os`，无需额外安装依赖）

### 配置步骤

1. 访问：https://openai.baidu.com，并登录百度账号
2. 点击权限申请，勾选你需要的能力，未勾选的能力调用时会失败
3. 设置环境变量
   ```bash
   # 必需：设置 API Token
   export BAIDU_EC_SEARCH_TOKEN="your-token"

   # 可选：设置 API 调用 QPS（每秒请求数），默认为 1
   # 设置为 0 表示无限制，设置为 0.5 表示每 2 秒 1 次请求
   export BAIDU_EC_SEARCH_QPS="1"
   ```

**QPS 配置说明：**
- 默认值：`1`（每秒最多1次请求，避免触发限流）
- `BAIDU_EC_SEARCH_QPS=0`：无限制，但容易触发 `token is limit` 错误
- `BAIDU_EC_SEARCH_QPS=0.5`：每2秒1次请求，更保守的限流策略
- 建议保持默认值 `1`，如需更快的请求速度可适当调高

## 何时使用 (触发条件)

当用户提出以下类型的请求时，应优先使用本技能：

**1. 全维度对比决策助手** 
- "[商品A]和[商品B]对比"
- "[商品A]和[商品B]哪个好？"
- "帮我比较一下[商品A]和[商品B]"
- "选[商品A]还是[商品B]？"

**2.1 品牌知识** 
- "[品牌]是什么品牌？"
- "[品牌]品牌介绍"
- "[品牌]品牌故事"

**2.2 品类知识** 
- "[品类]怎么选？"
- "怎么选[品类]？"
- "[品类]选购指南"
- "[品类]选购攻略"

**2.3 商品参数** 
- "[商品]的参数是什么？"
- "[商品]配置"
- "[商品]规格"

**3.1 品牌榜单** 
- "[品类]品牌榜"
- "[品类]排行榜"
- "什么牌子的[品类]好？"
- "[品类]哪个牌子好？"

**4.1 CPS商品查询** 
- "搜索[商品]"
- "查找[商品]"
- "哪里买[商品]"
- "[商品]推荐"

## Usage

### 1. 全维度对比决策助手

提供 SPU 参数/口碑/价格全方位对比评测，协助用户做最优选择。

```bash
# 对比两个商品
python3 scripts/compare.py "iphone16和iphone15对比"
python3 scripts/compare.py "华为mate60和小米14对比"
```

**返回数据包含：**
- SPU 基本信息（名称、品牌、型号等）
- 参数对比（规格、配置等）
- 口碑对比（用户评价、优缺点）
- 价格对比（各平台价格）
- 综合推荐建议

### 2. 商品百科知识

提供品类选购指南、品牌科普知识、全维度参数库的服务。

#### 2.1 品牌知识

查询单个品牌的相关信息，包括品牌简介、品牌定位、明星产品、品牌荣誉、品牌大事记。

```bash
# 查询品牌信息
python3 scripts/knowledge.py brand "华为"
python3 scripts/knowledge.py brand "ysl"
```

**返回数据包含：**
- 品牌简介
- 品牌定位
- 明星产品
- 品牌荣誉
- 品牌大事记

#### 2.2 品类知识

查询某个品类的选购知识，如选购要点、选购建议、避坑指南等。

```bash
# 查询品类选购知识
python3 scripts/knowledge.py entity "无人机怎么选"
python3 scripts/knowledge.py entity "怎么选笔记本电脑"
```

**返回数据包含：**
- 选购要点
- 选购建议
- 避坑指南

#### 2.3 商品参数

查询单个 SPU 的参数信息，包括 SPU 名称、图片、价格、参数列表及 AI 解读。

```bash
# 查询商品参数
python3 scripts/knowledge.py param "iphone16"
python3 scripts/knowledge.py param "小米14"
```

**返回数据包含：**
- SPU 名称
- SPU 图片
- 价格
- 参数列表
- 参数 AI 解读

### 3. 实时品牌天梯榜单

基于综合搜索热度、全网声量及销量，提供客观权威的品牌排行推荐服务。

#### 3.1 品牌榜单

查询某个分类下的品牌排行榜信息。

```bash
# 查询品牌榜单
python3 scripts/ranking.py brand "手机品牌榜"
python3 scripts/ranking.py brand "冰箱品牌榜"
```

**返回数据包含：**
- 品牌排名
- 品牌名称
- 推荐理由
- 对应品牌的热门商品

#### 3.2 单品榜

查询某品牌某品类下的单品排行榜信息。

```bash
# 查询单品榜
python3 scripts/ranking.py product "苹果手机排行榜"
python3 scripts/ranking.py product "华为冰箱排行榜"
```

**返回数据包含：**
- 商品排名
- 商品名称
- 商品价格
- 推荐理由

### 4. 全网 CPS 商品

通过商品关键词，获取全网 CPS 商品链接及热卖商品信息。

```bash
# 查询商品
python3 scripts/cps.py "iphone16"
python3 scripts/cps.py "机械键盘"
```

**返回数据包含：**
- 商品名称
- 商品图片
- 商品价格
- 购买链接（使用 `url` 字段）
- 销量信息
- 优惠信息


## 错误处理

脚本返回的错误信息（`errmsg`字段）及处理措施：

| 错误信息 | 说明 | 处理措施 |
|----------|------|----------|
| `token is limit` | API调用频率限流 | 等待1秒后重试 |
| `path错误` / `请求地址错误` | API请求地址不正确 | 检查脚本路径和调用参数 |
| `token权限不足` | Token未申请对应权限 | 访问 https://openai.baidu.com 申请所需能力 |
| `非法path` | 当前功能暂未支持 | 该路径/API尚未开放，请更换查询方式 |
| `token is nil` | Token未配置 | 检查token |
| `token is invalid` | Token错误 | 检查token |

## 注意事项

1. 确保 `BAIDU_EC_SEARCH_TOKEN` 环境变量已正确设置
2. API 调用有频率限制，脚本已内置 QPS 控制避免触发限流
   - 默认 QPS=1（每秒最多1次请求）
   - 可通过 `BAIDU_EC_SEARCH_QPS` 环境变量调整
3. 部分能力需要单独申请权限，未申请会返回 `token权限不足`
4. Python 脚本使用标准库，无需额外安装依赖
5. 返回的商品链接中可能有 `|` 等特殊字符，在以markdown形式展现链接时需要注意转义
6. 当获取到和用户意图匹配的购买链接时，应优先以markdown的链接格式提供购买链接，而不是直接返回链接文本。
7. 应优先使用接口返回的购买链接，而不是自行推测购买链接