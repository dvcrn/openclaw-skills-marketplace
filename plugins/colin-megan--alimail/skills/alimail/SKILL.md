---
name: alimail
description: "快速查询企业内部员工邮箱、工号及部门信息。"
---

## Configuration

Configure in **`~/.openclaw/openclaw.json`**:

```json
{
    "skills": {
      "entries": {
        "alimail": {
          "enabled": true,
          "env": {
            "ALIMAIL_CLIENT_ID": "your_CLIENT_ID",
            "ALIMAIL_CLIENT_SECRET": "your_CLIENT_SECRET"
          }
        }
      }
    }
}
```


## Core Features
* **Precise Lookup**: Enter a name to retrieve the full email address.
* **Fuzzy Search**: Supports partial name searches, automatically handling `(name=*xxx)` logic.
* **Detailed Information**: Returns employee ID (`employeeNo`), email (`email`), and name (`name`).

## User Guide

AI automatically recognizes and searches for names mentioned by users. For example:
- “查一下张三的邮箱”

## Agent instructions

**SearchAlimailUser**:Run the script under workspace (do not use the path under node_modules):
```bash
   python3 ~/.openclaw/workspace/skills/alimail/main.py "张三"
```

## Output Examples
**error result1:**
```json
{"status": "error", "message": "Parameter 'name' is required"}
```
**error result:**
```json
{"status": "api_failed", "details": "403 Client Error: Forbidden for url: "}
```
**error result:**
```json
{
    "users": [
        {
            "name": "总部IT开发-张三",
            "email": "zhangsan@test.com",
            "employeeNo": "zhangsan"
        }
    ],
    "total": 1
}
```
## Privacy Statement
This skill only calls the query interface and does not have the permissions to read, delete, or send emails, ensuring the security of enterprise data.