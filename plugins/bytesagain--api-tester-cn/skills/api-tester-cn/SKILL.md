---
name: api-tester-cn
description: "API请求构造、curl命令生成、Mock数据、API文档、HTTP状态码速查、Headers说明。API request builder, curl generator, mock data, API documentation, HTTP status codes, headers reference."
homepage: https://bytesagain.com
---

# api-tester-cn

API请求构造、curl命令生成、Mock数据、API文档、HTTP状态码速查、Headers说明。API request builder, curl generator, mock data, API documentation, HTTP status codes, headers reference.

## 推荐工作流

```
需求分析 → 选择命令 → 输入描述 → 获取结果 → 调整优化
```

## 命令速查

```
  request         request
  curl            curl
  mock            mock
  doc             doc
  status          status
  headers         headers
```


## 专业建议

- | 方法 | 用途 | 幂等 | 安全 | 请求体 |
- |------|------|------|------|--------|
- | GET | 查询资源 | ✅ | ✅ | ❌ |
- | POST | 创建资源 | ❌ | ❌ | ✅ |
- | PUT | 全量更新 | ✅ | ❌ | ✅ |

---
*api-tester-cn by BytesAgain*
