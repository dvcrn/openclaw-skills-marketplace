# 智能顾问 API 参考

## 接口：DescribeStrategies

- **域名**：`advisor.tencentcloudapi.com`
- **Action**：`DescribeStrategies`
- **Version**：`2020-07-21`
- **无必填参数**，直接调用即可

### tccli 调用方式

```bash
tccli advisor DescribeStrategies --version 2020-07-21
```

### 返回结构

```json
{
  "Response": {
    "RequestId": "...",
    "Strategies": [
      {
        "StrategyId": 131,
        "Name": "云数据库（Redis）跨可用区部署",
        "Desc": "检查 Redis 实例是否跨可用区部署...",
        "Product": "redis",
        "ProductDesc": "云数据库（Redis）",
        "Repair": "建议采用跨可用区部署方案...",
        "GroupId": 2,
        "GroupName": "可靠",
        "IsSupportCustom": false,
        "Conditions": [
          {
            "ConditionId": 178,
            "Level": 2,
            "LevelDesc": "中风险",
            "Desc": "Redis 实例未跨可用区部署"
          }
        ]
      }
    ]
  }
}
```

### 关键字段说明

| 字段 | 说明 |
|------|------|
| `StrategyId` | 评估项唯一 ID |
| `Name` | 评估项名称（用于拼接控制台链接） |
| `Product` | 产品标识（cos / cvm / mysql / redis / cbs / cam 等） |
| `ProductDesc` | 产品中文名 |
| `GroupName` | 分组：安全 / 可靠 / 费用 / 性能 / 服务限制 |
| `Conditions[].Level` | 风险等级：3=高危 / 2=中危 / 1=低危 |

## 控制台跳转 URL 拼接

```
https://console.cloud.tencent.com/advisor/assess?strategyName={URL编码后的Name}
```

示例：
- Name = `轻量应用服务器（LH）实例到期`
- URL = `https://console.cloud.tencent.com/advisor/assess?strategyName=%E8%BD%BB%E9%87%8F%E5%BA%94%E7%94%A8%E6%9C%8D%E5%8A%A1%E5%99%A8%EF%BC%88LH%EF%BC%89%E5%AE%9E%E4%BE%8B%E5%88%B0%E6%9C%9F`

## 常见 Product 值

| Product | ProductDesc |
|---------|-------------|
| cos | 对象存储（COS） |
| cvm | 云服务器（CVM） |
| mysql | 云数据库（MySQL） |
| redis | 云数据库（Redis） |
| cbs | 云硬盘（CBS） |
| cam | 访问管理（CAM） |
| clb | 负载均衡（CLB） |
| vpc | 私有网络（VPC） |
| lighthouse | 轻量应用服务器（LH） |
| mongodb | 云数据库（MongoDB） |
