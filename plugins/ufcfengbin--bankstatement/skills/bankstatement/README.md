# 使用技能创建指南帮我实现一个流水报告生成技能，基于用户输入的Excel文件路径和问题，生成报告或者从用户query中提取客户问题

## 1 本地文件上传至服务器

### 调用上传API

```sh
curl --location --request POST 'http://rd-test.dfwytech.com:9014/lsxx/openclaw/upload' \
--header 'User-Agent: Apifox/1.0.0 (https://apifox.com)' \
--header 'Accept: */*' \
--header 'Host: rd-test.dfwytech.com:9014' \
--header 'Connection: keep-alive' \
--header 'Content-Type: multipart/form-data; boundary=--------------------------956426839192577832884197' \
--form 'file=@"C:\\Users\\15770\\Desktop\\记录\\个人流水\\工商银行历史明细（申请单号：25011413031230849278） - 副本.pdf"'
```

### 调用上传API服务端的返回报文

```json
{
  "code": 200,
  "msg": "上传成功",
  "data": {
    "file_path": "/models/app/dify_api/uploads/20260311/11c69534af014b7a9a32d834fc146872/工商银行历史明细（申请单号：25011413031230849278） - 副本.pdf",
    "file_name": "工商银行历史明细（申请单号：25011413031230849278） - 副本.pdf"
  }
}
```

### 获取上传API服务器返回的文件路径

从服务端返回的 JSON 中提取 `file_path`

### 最终输出

```sh
$file_path
```

## 2 报告生成

### 调用报告生成API

使用第1步返回的文件路径和用户输入的问题，调用报告生成API

```sh
curl --location --request POST 'http://rd-test.dfwytech.com:9014/lsxx/genarate/report' \
--header 'User-Agent: Apifox/1.0.0 (https://apifox.com)' \
--header 'Accept: */*' \
--header 'Host: rd-test.dfwytech.com:9014' \
--header 'Connection: keep-alive' \
--header 'Content-Type: application/x-www-form-urlencoded' \
--data-urlencode 'file_urls=/models/app/dify_api/uploads/20260311/f51151c7a24246ef8736355db552f43c/工商银行历史明细（申请单号：25011413031230849278） - 副本.pdf' \
--data-urlencode 'query=生成报告'
```

### 报告生成API返回报文

```json
{
  "code": 200,
  "msg": "报告生成成功",
  "data": "\n\n# **流水分析报告**\n\n"
}
```

### 报告生成API最终输出

data的内容，原样输出即可

### 例如

\n\n# **流水分析报告**\n\n
