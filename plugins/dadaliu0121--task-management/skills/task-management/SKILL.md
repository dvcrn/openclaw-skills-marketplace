---
name: task-management
description: "Sales task management tool for SCRM. Create, update, delete, and list sales follow-up tasks. 销售任务管理工具，支持查询、创建、更新、删除销售人员的客户跟进任务。"
---

# 销售任务管理 Skill

## 1. Description
这是一个销售任务管理技能，用于帮助销售人员管理客户跟进任务。支持以下操作：
- **查询任务**：查询指定销售和客户的任务列表，支持按日期筛选
- **创建任务**：为销售人员创建新的客户跟进任务
- **更新任务**：修改已有任务的标题、内容或时间
- **删除任务**：根据任务 ID 删除一个或多个任务

后端 API 地址：`https://iautomark.sdm.qq.com/ai-assistant`

## 2. When to use
- 用户说："帮我查一下销售 XXX 的任务"
- 用户说："查看客户 XXX 今天的跟进任务"
- 用户说："帮我创建一个任务，明天下午3点跟进客户"
- 用户说："新建一个任务提醒我联系客户"
- 用户说："把任务 123 的时间改成后天上午10点"
- 用户说："更新任务标题为..."
- 用户说："删除任务 456"
- 用户说："批量删除任务 1,2,3"
- 用户提到"日程"、"任务"、"跟进"、"提醒"等与销售任务相关的关键词

## 3. How to use

### 3.1 查询任务 (list_tasks)
从用户消息中提取参数，调用 `agent.py` 中的 `list_tasks` 函数：
- `sale_id`（必填）：销售人员 ID
- `external_id`（可选）：客户 ID。不传则查询该销售的所有任务
- `task_date`（可选）：指定日期，格式为 `yyyy-MM-dd`

返回任务列表，包含任务 ID、标题、详情、时间、目标客户昵称。

### 3.2 创建任务 (create_task)
从用户消息中提取参数，调用 `agent.py` 中的 `create_task` 函数：
- `sale_id`（必填）：销售人员 ID
- `external_id`（必填）：客户 ID
- `title`（必填）：任务标题
- `content`（必填）：任务内容
- `task_time`（必填）：任务时间，格式为 `yyyy-MM-dd HH:mm`
- `sop_id`（可选）：SOP ID，格式为 `sopId` 或 `sopId-groupId`

### 3.3 更新任务 (update_task)
使用前需已知任务的详情信息（建议先查询）。调用 `agent.py` 中的 `update_task` 函数：
- `sale_id`（必填）：销售人员 ID
- `task_id`（必填）：任务 ID（数字）
- `title`（可选）：新的任务标题
- `content`（可选）：新的任务内容
- `task_time`（可选）：新的任务时间，格式为 `yyyy-MM-dd HH:mm`

### 3.4 删除任务 (delete_task)
调用 `agent.py` 中的 `delete_task` 函数：
- `task_ids`（必填）：要删除的任务 ID，多个用逗号分隔，如 `"1,2,3"`

## 4. Implementation
- 核心文件：`agent.py`
- 依赖库：`aiohttp`（异步 HTTP 请求）
- 后端 API 基础地址：`https://iautomark.sdm.qq.com/ai-assistant`
- 接口列表：
  - `POST /v1/task/getMyTask` - 查询任务
  - `POST /v1/task/create` - 创建任务
  - `POST /v1/task/updateMyTask` - 更新任务
  - `POST /v1/task/deleteMyTask` - 删除任务
- 时间格式：`yyyy-MM-dd HH:mm`（上海时区）

## 5. Edge cases
- 时间格式不正确：提示用户使用 `yyyy-MM-dd HH:mm` 格式
- 未提供必填参数：提示用户补充
- 查询无结果：告知用户没有找到匹配的任务
- API 请求失败：返回错误信息，建议用户重试
- 删除部分失败：返回失败的任务 ID 列表
- 更新任务前建议先查询确认任务存在
