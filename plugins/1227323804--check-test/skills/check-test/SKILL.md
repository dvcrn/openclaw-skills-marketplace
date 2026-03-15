---
name: check-test
description: "错敏信息检测"
---

# 错敏信息检测 API (Sensitive Content Detection)

一个基于 FastAPI 的错敏信息检测服务，用于检测文本中的敏感词、错别字和规范表述问题。

## 功能特性

- 敏感词检测：识别文本中的敏感词汇
- 错别字检测：发现拼写错误和输入错误
- 规范表述检测：检查专用表述是否符合规范
- RESTful API：简单的 HTTP 接口调用
- 详细日志记录：完整的请求/响应日志

## 快速开始

### 环境要求

- Python 3.11+
- pip

### 安装依赖

```bash
pip install -r requirements.txt
```

### 启动服务

```bash
python main.py
```

服务将在 `http://localhost:8080` 启动。

## API 接口

### 检测接口

**请求**

```
POST /api/safeguard/check
Content-Type: application/json
```

**请求参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| userKey | string | 是 | 用户密钥 |
| content | string | 是 | 待检测的文本内容 |
| sensitiveCodeList | array | 否 | 指定检测的错敏类型 |

**请求示例**

```json
{
  "userKey": "your-user-key",
  "content": "这是一段需要检测的文本"
}
```

**响应示例**

```json
{
  "code": 0,
  "message": "ok",
  "content": [
    {
      "sentencePos": 0,
      "termPos": 0,
      "wrongTerm": "错误的词",
      "expectTerms": ["正确的词"],
      "errLevel": 3,
      "type": 3,
      "newType": "A0200E01",
      "explain": "错误说明",
      "sentence": "错误词所在句子",
      "newTypeMeaning": "错误类型含义"
    }
  ]
}
```

**响应字段说明**

| 字段 | 类型 | 说明 |
|------|------|------|
| code | number | 响应码，0表示成功，1表示失败 |
| message | string | 响应消息 |
| content | array | 检测到的问题列表 |

### 其他接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/` | GET | 服务信息 |
| `/health` | GET | 健康检查 |
| `/docs` | GET | API 文档（Swagger UI） |

## 配置说明

### 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| PORT | 8080 | 服务监听端口 |
| SAFEGUARD_API_URL | https://safeguard-pre.ucap.com.cn/... | 上游API地址 |
| API_TIMEOUT | 30 | API请求超时时间（秒） |

## 日志

日志文件位于 `logs/app.log`，记录了：

- 服务启动/关闭信息
- 每个请求的详细信息
- 上游API调用情况
- 错误和异常信息

## 使用示例

### cURL

```bash
curl -X POST "http://localhost:8080/api/safeguard/check" \
  -H "Content-Type: application/json" \
  -d '{
    "userKey": "your-key",
    "content": "待检测文本"
  }'
```

### Python

```python
import requests

response = requests.post(
    "http://localhost:8080/api/safeguard/check",
    json={
        "userKey": "your-key",
        "content": "待检测文本"
    }
)
print(response.json())
```

### JavaScript

```javascript
fetch("http://localhost:8080/api/safeguard/check", {
  method: "POST",
  headers: {"Content-Type": "application/json"},
  body: JSON.stringify({
    userKey: "your-key",
    content: "待检测文本"
  })
})
.then(res => res.json())
.then(data => console.log(data));
```

## 项目结构

```
python-app/
├── main.py          # 主应用文件
├── models.py        # 数据模型定义
├── client.py        # HTTP客户端（已废弃）
├── service.py       # 业务服务（已废弃）
├── requirements.txt # 依赖清单
├── .env            # 环境变量配置
├── logs/           # 日志目录
│   └── app.log     # 应用日志
└── SKILL.md        # 本文件
```

## 许可证

MIT License
