# 和风天气技能配置指南

## 1. 获取和风天气API密钥

### 1.1 注册和风天气开发者账号
1. 访问 [和风天气开发者平台](https://dev.qweather.com/)
2. 注册账号并登录

### 1.2 创建项目
1. 进入控制台，点击"创建项目"
2. 填写项目信息：
   - 项目名称：OpenClaw天气技能
   - 项目类型：个人项目
   - 使用场景：个人天气查询
3. 创建成功后，获取项目ID (sub)

### 1.3 获取API密钥
1. 在项目设置中，进入"API密钥管理"
2. 点击"创建密钥"
3. 选择认证方式：JWT (推荐)
4. 生成并下载私钥文件
5. 记录凭据ID (kid)
6. 在"设置 → 开发者信息"中查看API Host

## 2. 配置环境变量

### 2.1 通过ClawHub安装时配置
当通过ClawHub安装此技能时，系统会提示你输入以下配置参数：

1. **QWEATHER_SUB** - 和风天气项目ID
2. **QWEATHER_KID** - 和风天气凭据ID  
3. **QWEATHER_API_HOST** - API Host
4. **QWEATHER_PRIVATE_KEY_PATH** - 私钥文件路径
5. **QWEATHER_CACHE_DIR** - 缓存目录（可选）

ClawHub会自动将这些配置注入为环境变量，技能运行时可以直接使用。

### 2.2 手动配置环境变量（非ClawHub安装）
如果手动安装技能，需要设置以下环境变量：

- **Windows PowerShell**:
  ```powershell
  $env:QWEATHER_SUB="your_project_id"
  $env:QWEATHER_KID="your_credential_id"
  $env:QWEATHER_API_HOST="your_api_host"
  $env:QWEATHER_PRIVATE_KEY_PATH="C:\path\to\private_key.pem"
  ```

- **Linux/macOS**:
  ```bash
  export QWEATHER_SUB="your_project_id"
  export QWEATHER_KID="your_credential_id"
  export QWEATHER_API_HOST="your_api_host"
  export QWEATHER_PRIVATE_KEY_PATH="/path/to/private_key.pem"
  ```

## 3. 安装依赖

### 3.1 Python依赖
```bash
pip install pyjwt cryptography requests
```

### 3.2 验证安装
```bash
python qweather.py --help
```

## 4. 测试配置

### 4.1 测试API连接
```bash
python qweather.py now --city beijing
```

### 4.2 如果出现错误
1. **认证失败**：检查私钥文件路径和权限
2. **网络错误**：检查网络连接
3. **API限制**：免费版有调用次数限制

## 5. OpenClaw集成

### 5.1 安装技能
```bash
# 将技能目录复制到OpenClaw技能目录
cp -r qweather-china ~/.openclaw/skills/
```

### 5.2 配置OpenClaw
确保环境变量已设置，OpenClaw会自动读取。

### 5.3 测试集成
在OpenClaw中发送：
```
北京天气怎么样？
```

## 6. 故障排除

### 常见问题

#### Q1: 私钥文件找不到
**错误信息**：`FileNotFoundError: 私钥文件不存在`
**解决方案**：
1. 检查 `QWEATHER_PRIVATE_KEY_PATH` 路径是否正确
2. 确保文件有读取权限
3. 使用绝对路径

#### Q2: 认证失败
**错误信息**：`401 Unauthorized`
**解决方案**：
1. 检查 `QWEATHER_SUB` 和 `QWEATHER_KID` 是否正确
2. 确认私钥文件与kid匹配
3. 检查API Host是否正确

#### Q3: 城市代码错误
**错误信息**：`404 City not found`
**解决方案**：
1. 使用正确的城市拼音或代码
2. 查看支持的城市列表

## 7. API限制

### 免费额度（开发者版）
- **天气和基础服务**：0~5万次/月（免费）[¹]
- **台风和海洋服务**：无免费额度
- **太阳辐照服务**：无免费额度
- **QPS限制**：5次/秒（免费版）[²]
- **并发请求**：10次/秒
- **数据更新频率**：
  - 实时天气：15分钟更新一次
  - 天气预报：每天更新3次（08、12、20时）
  - 空气质量：每小时更新一次
  - 生活指数：每天更新一次

详细计费信息：https://dev.qweather.com/docs/finance/pricing/

[¹] 免费额度基于和风天气官方定价页面  
[²] QPS限制参考和风天气API使用限制文档

### 数据精度
- 温度误差：±1°C
- 降水预报准确率：85%
- 空气质量数据：来自实时监测站
- 海外数据：基于国际权威数据源

### 建议优化
1. 启用缓存减少API调用
2. 合理设置缓存时间（实时数据10分钟，预报数据1小时）
3. 监控API使用情况，避免超限
4. 对于高频率需求，考虑升级到付费版

### 建议
1. 启用缓存减少API调用
2. 合理设置缓存时间
3. 监控API使用情况

## 8. 安全建议

1. **不要提交私钥文件到版本控制**
2. **使用环境变量而不是硬编码**
3. **定期轮换API密钥**
4. **监控异常API调用**

## 9. 获取帮助

- 和风天气官方文档：https://dev.qweather.com/docs/
- API参考文档：https://dev.qweather.com/docs/api/
- 位置列表文档：https://dev.qweather.com/docs/resource/location-list/
- 常见问题：https://dev.qweather.com/help/
- 控制台支持：https://console.qweather.com/support
- 问题反馈：GitHub Issues或ClawHub
- 社区支持：OpenClaw Discord