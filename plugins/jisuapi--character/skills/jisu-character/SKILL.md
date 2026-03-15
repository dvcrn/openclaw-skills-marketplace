---
name: jisu-character
description: "使用极速数据 MBTI 性格测试 API（full 93 题 / simple 28 题），逐题返回题目供用户作答，完成后拼接选项并获取测试结果。"
---

## 极速数据 MBTI 性格测试（Jisu Character / MBTI）

基于 [性格测试 API（MBTI）](https://www.jisuapi.com/api/character/) 的 OpenClaw 技能，支持：

- **获取题目**（`/character/questions`），支持 `full`（93 题）与 `simple`（28 题）
- **提交答案获取结果**（`/character/answer`）
- **逐题推进模式**：每次返回 1 道题，用户选择 A/B 后继续下一题，最后自动提交并返回 MBTI 结果

使用技能前需要申请数据，申请地址：https://www.jisuapi.com/api/character/

## 环境变量配置

```bash
# Linux / macOS
export JISU_API_KEY="your_appkey_here"

# Windows PowerShell
$env:JISU_API_KEY="your_appkey_here"
```

## 脚本路径

脚本文件：`skill/character/character.py`

## 使用方式与请求参数

### 1. 获取题目列表（/character/questions）

```bash
# full（默认）
python3 skill/character/character.py questions

# simple
python3 skill/character/character.py questions '{"version":"simple"}'
```

请求 JSON：

```json
{
  "version": "full"
}
```

| 字段名   | 类型   | 必填 | 说明                 |
|----------|--------|------|----------------------|
| version  | string | 否   | `full` / `simple`，默认 `full` |

### 2. 逐题返回题目并作答（推荐）

这个模式用于「拿到题目以后，一个个返回题目让用户做；用户完成以后，再拼接选项拿到结果」。

#### 2.1 获取第一题

```bash
python3 skill/character/character.py next '{"version":"full"}'
```

返回里会包含：

- `cursor`：当前题索引（0 开始）
- `total`：题目总数
- `picked`：已选择的选项编码数组（用于下一次调用原样带回）
- `question`：当前题（包含 `answer1/answer2` 文案）

#### 2.2 用户选择 A/B 后拿下一题

把上一轮返回的 `cursor` 与 `picked` 带上，再附加 `choice`（A 或 B）：

```bash
python3 skill/character/character.py next '{"version":"full","cursor":0,"picked":[],"choice":"A"}'
```

当最后一题完成后，返回将包含：

- `done: true`
- `answer`：拼接后的答案字符串（逗号分隔）
- `result`：MBTI 结果（type/name/summary/characteristic/field/job 等）

请求 JSON（逐题模式）：

```json
{
  "version": "full",
  "cursor": 0,
  "picked": ["x1", "y2"],
  "choice": "A"
}
```

| 字段名  | 类型          | 必填 | 说明 |
|--------|---------------|------|------|
| version | string       | 否   | `full` / `simple`，默认 `full` |
| cursor  | int          | 否   | 当前题索引（0 开始），默认 0 |
| picked  | array<string>| 否   | 已选编码数组（原样回传） |
| choice  | string       | 否   | 当前题选择：`A` 或 `B`（不传则仅返回当前题） |

### 3. 直接提交答案拿结果（/character/answer）

如果你已经在对话里收集到所有编码（例如 `x1,y1,x2,...`），可直接提交：

```bash
python3 skill/character/character.py answer '{"version":"simple","answer":"x1,y1,x2,y2"}'
```

也支持传数组：

```bash
python3 skill/character/character.py answer '{"version":"simple","answers":["x1","y1","x2","y2"]}'
```

### 4. 本地交互模式（终端逐题输入）

适合你自己在命令行里跑一遍测试（会逐题提示输入 A/B）：

```bash
python3 skill/character/character.py quiz '{"version":"full"}'
```

## 常见错误码

来自 [极速数据性格测试文档](https://www.jisuapi.com/api/character/) 的业务错误码：

| 代号 | 说明     |
|------|----------|
| 201  | 答案不足 |
| 210  | 没有信息 |

系统错误码：

| 代号 | 说明                 |
|------|----------------------|
| 101  | APPKEY 为空或不存在  |
| 102  | APPKEY 已过期        |
| 103  | APPKEY 无请求权限    |
| 104  | 请求超过次数限制     |
| 105  | IP 被禁止            |
| 106  | IP 请求超过限制      |
| 107  | 接口维护中           |
| 108  | 接口已停用           |

## 在 OpenClaw 中的推荐用法

1. 用户提问：「给我做一个 MBTI 测试（简单版）。」  
2. 代理调用：`python3 skill/character/character.py next '{"version":"simple"}'`，把返回的 `question` 展示给用户，只让用户回答 A 或 B。  
3. 用户每回答一次，代理把上一轮的 `cursor/picked` 带回，再加上 `choice` 调用 `next`，继续拿下一题。  
4. 当返回 `done: true` 时，把 `result` 里的 `type/name/summary/characteristic` 等字段整理成自然语言结果，并给出适合的职业建议（`field/job`）。  

