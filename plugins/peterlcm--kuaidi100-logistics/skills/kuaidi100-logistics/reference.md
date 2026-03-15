# 快递100 快递公司编码参考

## 常用快递公司编码

| 快递公司 | 编码 | 说明 |
|----------|------|------|
| 中通快递 | zhongtong | 需要手机号验证 |
| 圆通速递 | yuantong | |
| 顺丰速运 | shunfeng | 必须提供手机号后4位 |
| 申通快递 | shentong | |
| 韵达快递 | yunda | |
| 百世快递 | huitongkuaidi | |
| 京东物流 | jd | |
| EMS | ems | |
| 邮政快递 | youzhengguonei | |
| 天天快递 | tiantian | |
| 德邦快递 | debangwuliu | |
| 极兔速递 | jtexpress | |
| 宅急送 | zhaijisong | |
| 优速快递 | uc | |
| 跨越速运 | kuayue | |

## 国际快递公司编码

| 快递公司 | 编码 | 说明 |
|----------|------|------|
| DHL | dhl | |
| FedEx | fedex | |
| UPS | ups | |
| TNT | tnt | |
| 中国邮政国际 | youzhengguoji | |

## 编码使用注意事项

1. **全部小写**：编码必须使用小写字母
2. **准确匹配**：必须使用快递100官方编码
3. **手机验证**：顺丰(shunfeng)、中通(zhongtong)需要手机号参数
4. **时效预测**：需要目的地(to)参数和resultv2=8

## 获取完整编码表

完整编码表可从快递100官方获取：
- 下载地址：https://api.kuaidi100.com/manager/openapi/download/kdbm.do
- API文档：https://api.kuaidi100.com/document/5f0ffb5ebc8da837cbd8aefc

## 常见错误

1. **编码错误**：使用错误的编码会导致查询失败
2. **大小写错误**：编码必须小写
3. **拼写错误**：注意拼写准确性

## 验证方法

如果不确定编码，可以：
1. 查询快递100官网
2. 使用快递100API的智能识别功能
3. 参考官方文档