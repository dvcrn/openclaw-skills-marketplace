# V2EX 创造者节点

## 标题

privacy-mask: 本地 OCR + 正则自动打码截图中的敏感信息，防止发给 AI 时泄露隐私

## 正文

做了一个开源小工具，解决一个很具体的痛点：我们每天给 AI 编程助手发截图（Claude Code、Cursor、Copilot 等），但截图里经常不小心带上手机号、身份证号、API Key、银行卡号这些东西。

**privacy-mask** 会在图片上传之前自动扫描并打码，整个过程在本地完成，不经过任何云服务。

### 工作原理

1. 双引擎 OCR（Tesseract + RapidOCR）提取图片中的文字和位置
2. 47 条正则规则扫描匹配，覆盖 15+ 个国家的证件、电话、金融信息
3. 命中的区域自动模糊或填充遮挡

### 支持检测的类型

- **证件**：身份证、护照、港澳台证件、美国 SSN、英国 NINO、印度 Aadhaar、韩国 RRN、新加坡 NRIC、马来西亚 IC
- **电话**：国内手机和座机、美国电话、国际号码
- **金融**：银行卡（银联/Visa/万事达）、IBAN、SWIFT
- **开发者密钥**：AWS Key、GitHub Token、Stripe Key、JWT、数据库连接串、SSH 私钥
- **其他**：邮箱、IP 地址、MAC 地址、车牌号、护照 MRZ、微信号、QQ 号

### 使用方式

```bash
pip install privacy-mask

# 打码截图
privacy-mask mask screenshot.png

# 一键安装 Claude Code 钩子，之后所有截图自动打码
privacy-mask install
```

装完 `privacy-mask install` 之后就不用管了，发截图时自动拦截处理。可以用 `privacy-mask off/on` 随时开关。

### 开发过程中踩的坑

- OCR 对截图的识别噪声很大，最后用了多策略预处理（灰度、二值化、对比度增强）+ 置信度合并才稳定下来
- 误报比漏报更头疼。英文截图里 "ORGANIZATION"、"REQUIRED" 这种大写单词经常被误判成证件号，光测试用例就写了 208+，大部分是反例
- JSON 配置里的正则要双重转义反斜杠，这个调试体验一言难尽

### 链接

- GitHub: https://github.com/fullstackcrew-alpha/privacy-mask
- PyPI: https://pypi.org/project/privacy-mask/
- MIT 协议

欢迎试用和反馈，特别想听听大家日常截图里还有哪些敏感信息类型需要覆盖的。

项目完全开源（MIT），欢迎来 GitHub star 支持一下！也非常欢迎 PR — 添加新的检测规则门槛很低，只需要在 JSON 配置里加一条正则 + 写个测试用例就行。不管是补充国内特有的敏感信息格式，还是优化 OCR 识别策略，都欢迎参与。
