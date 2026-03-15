# Feishu Task Skill for OpenClaw

飞书任务管理 Skill - 通过 OpenClaw 自动化创建、指派和管理飞书任务

## 功能特性

- ✅ 创建任务（支持标题、描述、截止时间、优先级）
- ✅ 指派执行者（通过邮箱或 Open ID）
- ✅ 添加关注者
- ✅ 查询任务列表和详情
- ✅ 更新任务信息
- ✅ 删除任务

## 安装

### 1. 下载 Skill

```bash
git clone https://github.com/youyoude/feishu-task.git
```

### 2. 复制到 OpenClaw Skills 目录

```bash
cp -r feishu-task ~/.openclaw/skills/
# 或安装打包文件
cp feishu-task.skill ~/.openclaw/skills/
```

### 3. 配置环境变量

在 ~/.openclaw/openclaw.json 中添加：

```json
{
  "skills": {
    "entries": {
      "feishu-task": {
        "enabled": true,
        "env": {
          "FEISHU_APP_ID": "cli_xxxxx",
          "FEISHU_APP_SECRET": "xxxxxx"
        }
      }
    }
  }
}
```

### 4. 重启 OpenClaw

```bash
openclaw gateway restart
```

---

## ⚠️ 重要：飞书权限配置

### 必需权限

使用此 Skill 前，必须在 **飞书开放平台** 为你的应用申请以下权限：

#### 核心权限（必须）

| 权限 | 权限码 | 说明 |
|------|--------|------|
| **任务读写** | task:task:write | 创建、更新、删除任务 |
| **任务读取** | task:task:readonly | 查询任务列表和详情 |

#### 用户查询权限（可选但推荐）

| 权限 | 权限码 | 说明 |
|------|--------|------|
| **通过邮箱查用户** | contact:user.id:readonly | 通过邮箱获取用户 Open ID |
| **获取用户ID** | contact:user.employee_id:readonly | 获取员工ID信息 |

### 申请权限步骤

1. 登录 [飞书开放平台](https://open.feishu.cn/)
2. 进入你的应用 → **权限管理**
3. 搜索并添加上述权限
4. 发布版本（需要管理员审核）

### 权限说明

#### 为什么需要 task:task:write？
- 创建新任务
- 更新任务信息（标题、描述、截止时间等）
- 删除任务

#### 为什么需要 task:task:readonly？
- 获取任务列表
- 查询任务详情
- 检查任务状态

#### 为什么需要 contact:user.id:readonly？
- 通过邮箱地址（如 user@example.com）获取用户 Open ID
- 如果没有此权限，需要手动提供用户的 Open ID（格式：ou_xxxxx）

---

## 使用方法

### 在 OpenClaw 中使用

安装并配置完成后，可以直接对 OpenClaw 说：

```
给李四创建一个飞书任务，AI机器人集成方案，截止下周二
```

```
创建一个任务：完成月度报告，截止3月15日，指派给张三，关注人是李四
```

### Python API 调用

```python
from scripts.task_client import FeishuTaskClient

client = FeishuTaskClient()

# 创建任务
result = client.create_task(
    summary="完成月度报告",
    description="整理2月份数据并生成报告",
    due_time="2026-03-15T18:00:00+08:00",
    assignee_id="ou_xxxxx",           # 执行者
    follower_ids=["ou_xxxxx"],         # 关注者列表
    priority=2                         # 0=默认, 1=低, 2=中, 3=高
)
```

### 命令行使用

```bash
# 创建任务
python3 scripts/task_client.py create "任务标题" \\
  --due "2026-03-15T18:00:00+08:00" \\
  --assignee "ou_xxxxx" \\
  --priority 2
```

---

## 时间格式说明

### 支持的格式

- ISO 8601: 2026-03-15T18:00:00+08:00（带时区）
- ISO 8601: 2026-03-15T10:00:00Z（UTC时间）
- 时间戳: 毫秒级时间戳（如 1773568800000）

### 北京时间示例

```python
# 2026年3月15日 18:00（北京时间）
due_time="2026-03-15T18:00:00+08:00"
```

---

## 获取用户 Open ID

### 方法一：通过邮箱查询（需要权限）

使用 contact:user.id:readonly 权限，Skill 会自动将邮箱转换为 Open ID

### 方法二：飞书管理后台

1. 登录飞书管理后台
2. 进入 **组织架构** → **成员管理**
3. 点击用户 → 查看 **Open ID**

---

## 常见问题

### Q: 创建任务时提示权限不足？

A: 请检查：
1. 应用是否申请了 task:task:write 权限
2. 权限是否已发布并通过审核
3. 用户是否已授权应用访问其任务数据

### Q: 无法通过邮箱指派任务？

A: 请检查：
1. 是否申请了 contact:user.id:readonly 权限
2. 邮箱地址是否正确
3. 该用户是否在企业通讯录中

### Q: 截止时间设置后不显示？

A: 请确保：
1. 时间格式正确（ISO 8601 或毫秒时间戳）
2. 时区信息正确（建议用 +08:00 表示北京时间）

---

## API 参考

- [飞书任务 API 文档](https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/task-v2/overview)
- [飞书权限说明](https://open.feishu.cn/document/ukTMukTMukTM/uQjN3QjL0YzN04CN2cDN)

---

## 版本历史

### v1.0.0 (2026-03-05)

- ✨ 初始版本发布
- 支持创建、查询、更新、删除任务
- 支持指派执行者和关注者
- 支持截止时间设置（自动处理时区）

---

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License

---

**作者**: youyoude  
**项目地址**: https://github.com/youyoude/feishu-task
