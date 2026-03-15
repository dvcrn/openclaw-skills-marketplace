---
name: feishu-task
description: "飞书任务管理 - 创建、查询、更新和删除飞书任务。Use when user mentions 飞书任务、创建任务、指派任务、任务管理。\n \n Triggers:\n - \"创建一个飞书任务\"\n - \"帮我在飞书里添加任务\"\n - \"查看我的飞书任务\"\n - \"更新/修改/删除飞书任务\"\n - \"给XXX指派任务\""
---

# 飞书任务管理 (Feishu Task)

通过飞书开放平台 API 管理任务，支持创建、查询、更新和删除任务。

## 前置要求

### 1. 飞书应用权限

确保飞书应用已申请以下权限：
- `task:task:write` - 创建、更新、删除任务
- `task:task:readonly` - 读取任务信息

### 2. 环境变量

设置以下环境变量（或在调用时传入）：

```bash
export FEISHU_APP_ID="cli_xxxxx"
export FEISHU_APP_SECRET="xxxxxxxx"
```

## 使用方法

### Python 代码调用

```python
from scripts.task_client import FeishuTaskClient

# 初始化客户端
client = FeishuTaskClient()

# 创建任务
result = client.create_task(
    summary="完成月度报告",
    description="整理2月份数据并生成报告",
    due_time="2026-03-10T18:00:00+08:00",
    assignee_id="ou_xxxxx",
    priority=2  # 0=默认, 1=低, 2=中, 3=高
)
print(f"任务创建成功: {result['data']['task']['id']}")

# 获取任务列表
tasks = client.list_tasks()

# 获取任务详情
task = client.get_task("task_id_here")

# 更新任务
client.update_task(
    "task_id_here",
    summary="新的标题",
    completed=True
)

# 删除任务
client.delete_task("task_id_here")
```

### 命令行使用

```bash
# 创建任务
python3 scripts/task_client.py create "完成月度报告" --due "2026-03-10T18:00:00+08:00" --assignee "ou_xxxxx" --priority 2

# 获取任务详情
python3 scripts/task_client.py get "task_id"

# 列出任务
python3 scripts/task_client.py list

# 更新任务
python3 scripts/task_client.py update "task_id" --completed true

# 删除任务
python3 scripts/task_client.py delete "task_id"
```

## API 参数说明

### 创建任务 (create_task)

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| summary | str | ✅ | 任务标题 |
| description | str | ❌ | 任务描述 |
| due_time | str | ❌ | 截止时间 (ISO 8601格式) |
| assignee_id | str | ❌ | 执行者用户ID (ou_xxxxx) |
| follower_ids | list | ❌ | 关注者用户ID列表 |
| priority | int | ❌ | 优先级: 0=默认, 1=低, 2=中, 3=高 |

### 时间格式示例

- `2026-03-10T18:00:00+08:00` - 北京时间
- `2026-03-10T10:00:00Z` - UTC时间

### 获取用户ID

用户ID (open_id) 格式为 `ou_xxxxx`，可以通过以下方式获取：
1. 飞书管理后台 → 组织架构 → 用户详情
2. 使用飞书 `contact:user.employee_id:readonly` 权限查询

## 注意事项

1. **认证**：首次调用会自动获取 access_token，token 有效期约 2 小时
2. **时区**：建议使用带时区的时间格式，如 `+08:00` 表示北京时间
3. **权限**：确保应用已被用户或组织授权，否则接口会返回权限错误
4. **频率限制**：注意飞书 API 的调用频率限制

## 相关链接

- [飞书任务 API 文档](https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/task-v2/overview)
