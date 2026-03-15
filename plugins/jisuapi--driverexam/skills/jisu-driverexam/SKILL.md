---
name: jisu-driverexam
description: "使用极速数据驾考题库 API 获取小车、客车、货车、摩托车四类驾照的科目一和科目四试题。"
---

## 极速数据驾考题库（Jisu DriverExam）

基于 [驾考题库 API](https://www.jisuapi.com/api/driverexam/) 的 OpenClaw 技能，提供公安部最新驾照考试题库。

使用技能前需要申请数据，申请地址：https://www.jisuapi.com/api/driverexam/

包含 **小车、客车、货车、摩托车 4 类**，支持 **科目一、科目四** 顺序或随机获取试题。

当前封装一个接口：

- **获取考题**（`/driverexam/query`）

## 环境变量配置

```bash
# Linux / macOS
export JISU_API_KEY="your_appkey_here"

# Windows PowerShell
$env:JISU_API_KEY="your_appkey_here"
```

## 脚本路径

脚本文件：`skills/driverexam/driverexam.py`

## 使用方式

### 获取考题（/driverexam/query）

```bash
python3 skills/driverexam/driverexam.py '{"type":"C1","subject":"1","pagesize":"10","pagenum":"1","sort":"normal"}'
```

请求 JSON 示例：

```json
{
  "type": "C1",
  "subject": "1",
  "pagesize": "10",
  "pagenum": "1",
  "sort": "normal",
  "chapter": "1"
}
```

### 请求参数

| 字段名   | 类型   | 必填 | 说明                                                                 |
|----------|--------|------|----------------------------------------------------------------------|
| type     | string | 是   | 题目类型：A1、A3、B1、A2、B2、C1、C2、C3、D、E、F（默认 C1）        |
| subject  | string | 否   | 科目类别：`1` 为科目一、`4` 为科目四，默认 1                         |
| pagesize | string | 否   | 每页数量，默认 1                                                     |
| pagenum  | string | 否   | 当前页数                                                             |
| sort     | string | 否   | 排序方式：顺序 `normal`，随机 `rand`，默认 `normal`                 |
| chapter  | string | 否   | 章节：科目一为 1–4，科目四为 41–47，摩托车科目一为 7，科目四为 49  |

脚本仅强制要求 `type` 字段必填，其余均为可选参数，按文档原样透传给接口。

## 返回结果示例

脚本直接输出接口的 `result` 字段，结构与官网示例一致，例如（参考
[极速数据驾考题库文档](https://www.jisuapi.com/api/driverexam/)）：

```json
{
  "total": "950",
  "pagenum": "1",
  "pagesize": "3",
  "subject": "1",
  "type": "C1",
  "sort": "normal",
  "list": [
    {
      "question": "未取得驾驶证的学员在道路上学习驾驶技能，下列哪种做法是正确的？",
      "option1": "A、使用所学车型的教练车由教练员随车指导",
      "option2": "B、使用所学车型的教练车单独驾驶学习",
      "option3": "C、使用私家车由教练员随车指导",
      "option4": "D、使用所学车型的教练车由非教练员的驾驶人随车指导",
      "answer": "A",
      "explain": "《公安部令第123号》规定：未取得驾驶证的学员在道路上学习驾驶技能，使用所学车型的教练车由教练员随车指导。",
      "pic": "",
      "type": "C1,C2,C3"
    }
  ]
}
```

字段说明：

- 顶层：
  - `total`：题库总数
  - `pagenum`：当前页
  - `pagesize`：每页数量
  - `subject`：科目类别（1 或 4）
  - `type`：题目类型（驾照类型）
  - `sort`：排序方式（normal / rand）
- `list` 数组：
  - `question`：题目内容
  - `option1`–`option4`：选项（判断题可能为空）
  - `answer`：正确答案（选择题为 A/B/C/D，判断题为 “对/错”）
  - `explain`：答案解析
  - `pic`：配图 URL（如无图片则为空）
  - `type`：适用驾照类型列表（如 `C1,C2,C3`）

## 常见错误码

来自 [极速数据驾考题库文档](https://www.jisuapi.com/api/driverexam/) 的业务错误码：

| 代号 | 说明       |
|------|------------|
| 201  | 类型不正确 |
| 202  | 科目不正确 |
| 210  | 没有信息   |

系统错误码：

| 代号 | 说明                     |
|------|--------------------------|
| 101  | APPKEY 为空或不存在     |
| 102  | APPKEY 已过期           |
| 103  | APPKEY 无请求此数据权限 |
| 104  | 请求超过次数限制         |
| 105  | IP 被禁止               |
| 106  | IP 请求超过限制         |
| 107  | 接口维护中               |
| 108  | 接口已停用               |

## 在 OpenClaw 中的推荐用法

1. 用户需求示例：「我要练 C1 科目一，给我几道随机题并讲解答案。」  
2. 代理构造 JSON：`{"type":"C1","subject":"1","pagesize":"10","pagenum":"1","sort":"rand"}`，调用：  
   `python3 skills/driverexam/driverexam.py '{"type":"C1","subject":"1","pagesize":"10","pagenum":"1","sort":"rand"}'`。  
3. 从返回的 `list` 中逐题读取 `question`、`option1`–`option4`、`answer`、`explain`，将题目以问答形式展示给用户，并在用户作答后对比 `answer` 给出是否正确和解析。  
4. 可按 `chapter` 筛选章节，或基于用户表现自适应调整难度和题量，用于构建对话式刷题体验。  

