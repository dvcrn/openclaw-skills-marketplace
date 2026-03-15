# QWeather China Skill for OpenClaw

基于中国气象局数据的完整天气服务技能，专为OpenClaw优化。

## 🎯 功能特点

### 🌤️ 完整天气服务（基于和风天气V7 API）
- **实时天气**: 实时温度、体感温度、风力风向、相对湿度、大气压强、降水量、能见度、露点温度、云量等
- **天气预报**: 3天/7天/10天/15天/30天预报，逐小时预报
- **生活指数**: 30+种生活指数（穿衣、洗车、运动、紫外线、感冒、钓鱼、旅游等）
- **空气质量**: 实时AQI、主要污染物浓度、空气质量预报
- **天气预警**: 官方天气预警（台风、暴雨、暴雪等）
- **天文数据**: 日出日落、月升月落、月相、潮汐
- **格点天气**: 任意经纬度的精细化天气数据
- **历史天气**: 过去30天的历史天气数据

### 🌍 全球覆盖
- **中国范围**: 3000+市县区，覆盖所有地级市、县级市、县、区
- **海外范围**: 20万个城市，覆盖全球主要城市
- **数据源**: 中国气象局官方数据 + 国际权威数据源
- **权威性**: 和风天气是中国气象局战略合作伙伴

### 🚀 高性能
- **智能缓存**: 减少API调用
- **错误恢复**: 自动降级和重试
- **快速响应**: 优化请求处理

## 📦 安装

### 通过ClawHub安装（推荐）
1. 在ClawHub中搜索 "qweather-china"
2. 点击安装，按照提示输入配置参数
3. ClawHub会自动处理依赖安装和配置注入

### 手动安装
1. 复制本目录到OpenClaw技能目录
2. 安装Python依赖：
   ```bash
   pip install pyjwt cryptography requests
   ```
3. 配置环境变量（见下方配置部分）
4. 测试安装：
   ```bash
   python qweather.py now --city beijing
   ```

## 🔧 配置

### 1. 获取API密钥
1. 访问 [和风天气开发者平台](https://dev.qweather.com/) 注册账号
2. 创建项目并获取项目ID (sub)
3. 生成JWT密钥，下载私钥文件
4. 记录凭据ID (kid)

### 2. 配置方法

#### 方法一：使用环境变量（推荐）
```bash
# Windows PowerShell
$env:QWEATHER_SUB="your_project_id"
$env:QWEATHER_KID="your_credential_id"
$env:QWEATHER_API_HOST="your_api_host"
$env:QWEATHER_PRIVATE_KEY_PATH="C:\path\to\private_key.pem"

# Linux/macOS
export QWEATHER_SUB="your_project_id"
export QWEATHER_KID="your_credential_id"
export QWEATHER_API_HOST="your_api_host"
export QWEATHER_PRIVATE_KEY_PATH="/path/to/private_key.pem"
```

#### 方法二：手动设置环境变量
1. 设置系统环境变量（见下方示例）
2. 或创建环境变量配置文件

#### 方法三：OpenClaw配置
在OpenClaw配置文件中添加：

```json
{
  "skills": {
    "entries": {
      "qweather-china": {
        "enabled": true,
        "config": {
          "api_host": "${QWEATHER_API_HOST}",
          "jwt": {
            "kid": "${QWEATHER_KID}",
            "sub": "${QWEATHER_SUB}",
            "private_key_path": "${QWEATHER_PRIVATE_KEY_PATH}"
          }
        }
      }
    }
  }
}
```

## 📖 使用方法

### 在OpenClaw中直接使用
```
用户: 北京天气怎么样？
助手: 🌤️ 北京当前天气...
```

### 命令行使用
```bash
# 实时天气
python qweather.py now --city beijing

# 3天预报
python qweather.py forecast --city shanghai --days 3

# 生活指数
python qweather.py indices --city guangzhou

# 空气质量
python qweather.py air --city hangzhou

# 完整报告
python qweather.py full --city chengdu
```

### 支持的查询格式
1. `[城市]天气` - 实时天气
2. `[城市]温度` - 当前温度
3. `[城市]今天/明天/后天天气` - 特定日期
4. `[城市]预报` - 3天预报
5. `[城市]未来N天预报` - N天预报
6. `[城市]生活指数` - 生活指数
7. `[城市]空气质量` - 空气质量
8. `[城市]需要带伞吗` - 雨伞建议
9. `[城市]穿什么` - 穿衣建议

### 支持的城市范围
**全球覆盖**：
- **中国**: 3000+市县区（所有地级市、县级市、县、区）
- **海外**: 20万个城市（全球主要城市）

**查询方式**：
1. **城市拼音**: `beijing`, `shanghai`, `newyork`, `london`
2. **城市代码**: `101010100` (北京), `USNY0996` (纽约)
3. **经纬度**: `39.9042,116.4074` (北京坐标)
4. **中文名称**: `北京`, `上海`, `广州市`

**常用城市代码**：
- 北京: `101010100`
- 上海: `101020100`
- 广州: `101280101`
- 纽约: `USNY0996`
- 伦敦: `GBLO0483`
- 东京: `JAXX0085`

**完整城市列表**: https://dev.qweather.com/docs/resource/location-list/

## 🛠️ 开发

### 项目结构
```
qweather-china/
├── qweather.py          # 核心天气服务
├── openclaw_integration.py # OpenClaw集成
├── examples.py          # 使用示例
├── skill.yaml          # ClawHub技能配置
├── SKILL.md            # 技能文档
├── README.md           # 本文件
├── config.json         # 配置文件
├── openclaw_config.yaml # OpenClaw配置
├── setup.py            # 配置向导
└── examples.py         # 使用示例
```

### 扩展功能
1. **添加新城市**: 在`config.json`的`cities`部分添加
2. **自定义模板**: 修改`openclaw_config.yaml`的`templates`部分
3. **添加新命令**: 在`openclaw_integration.py`中添加处理函数

### 测试
```bash
# 运行示例
python examples.py

# 测试集成
python openclaw_integration.py

# 单元测试
python -m pytest tests/ -v
```

## 🔍 故障排除

### 常见问题
1. **API连接失败**
   - 检查私钥文件是否存在
   - 验证JWT认证信息
   - 检查网络连接

2. **城市找不到**
   - 确认城市名称正确
   - 检查城市代码映射

3. **响应缓慢**
   - 检查缓存设置
   - 确认网络状况

### 日志查看
```bash
# 查看缓存目录
ls ~/.openclaw/cache/qweather

# 调试模式
python qweather.py now --city beijing --debug
```

## 📊 数据源

### 和风天气API
- **官方文档**: https://dev.qweather.com/docs/
- **数据源**: 中国气象局
- **更新频率**: 实时更新
- **免费额度**: 天气和基础服务0~5万次/月（免费）
- **计费详情**: https://dev.qweather.com/docs/finance/pricing/

### 数据准确性
- 温度误差: ±1°C
- 降水预报: 85%准确率
- 空气质量: 实时监测站数据

## 🤝 贡献

欢迎贡献代码、报告问题或提出建议：

1. Fork本仓库
2. 创建功能分支
3. 提交更改
4. 创建Pull Request

## 📄 许可证

基于和风天气API服务条款，仅供个人和非商业使用。

## 📞 支持

- **问题反馈**: GitHub Issues
- **文档**: [SKILL.md](SKILL.md)
- **示例**: [examples.py](examples.py)
- **常见问题**: https://dev.qweather.com/help/
- **控制台支持**: https://console.qweather.com/support

## 📄 更新日志

详细更新日志请查看 [CHANGELOG.md](CHANGELOG.md)

### v1.0.0 (2026-03-14) - 发布版本
- 完整和风天气V7 API集成
- 全球城市覆盖（中国3000+市县区 + 海外20万个城市）
- 全方位天气服务
- 环境变量配置，无硬编码敏感信息
- 详细的配置指南和安装向导

---

**数据来源**: 和风天气（中国气象局战略合作伙伴）  
**覆盖范围**: 中国3000+市县区 + 海外20万个城市  
**技能维护**: OpenClaw社区  
**官方文档**: https://dev.qweather.com/docs/  
**API参考**: https://dev.qweather.com/docs/api/  
**位置列表**: https://dev.qweather.com/docs/resource/location-list/  
**常见问题**: https://dev.qweather.com/help/  
**控制台支持**: https://console.qweather.com/support  
**最后更新**: 2026年3月14日