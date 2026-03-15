---
name: jisu-enterprisecontact
description: "使用极速数据企业工商联系方式查询 API，按企业名称、统一信用代码、注册号或组织机构代码查询联系方式（地址、电话、手机、邮箱、网站等）。"
---

# 极速数据企业联系方式查询（Jisu Enterprise Contact）

基于 [企业联系方式查询 API](https://www.jisuapi.com/api/enterprisecontact/) 的 OpenClaw 技能，按工商名称、统一信用代码、注册号或组织机构代码查询企业公示的联系方式，包括地址、电话、手机、邮箱、网站等；返回列表中含姓名、联系方式、职务、来源、类型及手机号检测状态等字段。

使用技能前需要申请数据，申请地址：https://www.jisuapi.com/api/enterprisecontact/

## 环境变量配置

```bash
# Linux / macOS
export JISU_API_KEY="your_appkey_here"

# Windows PowerShell
$env:JISU_API_KEY="your_appkey_here"
```

## 脚本路径

脚本文件：`skill/enterprisecontact/enterprisecontact.py`

## 使用方式

### 企业联系方式查询（query）

```bash
python3 skill/enterprisecontact/enterprisecontact.py query '{"company":"北京抖音信息服务有限公司"}'
python3 skill/enterprisecontact/enterprisecontact.py query '{"creditno":"91110000xxxx"}'
python3 skill/enterprisecontact/enterprisecontact.py query '{"regno":"110000xxxx"}'
python3 skill/enterprisecontact/enterprisecontact.py query '{"orgno":"xxxx"}'
```

| 参数     | 类型   | 必填 | 说明 |
|----------|--------|------|------|
| company  | string | 否   | 工商名称（与下列参数任选一个） |
| creditno | string | 否   | 统一信用代码 |
| regno    | string | 否   | 注册号 |
| orgno    | string | 否   | 组织机构代码 |

至少提供 `company`、`creditno`、`regno`、`orgno` 中的一个。

## 返回结果说明

`result` 为对象，包含：

- **list**：联系方式列表。每项含 name、number、position、source、url、type、num、iskeyperson、checkstatus（2 活跃/3 空号/4 沉默/5 风险）、activepr、location、epnum、dept、agentstatus 等。
- **company** / **creditno** / **regno** / **orgno**：对应查询到的企业信息。

## 常见错误码

| 代号 | 说明 |
|------|------|
| 201  | 公司名称、信用代码和注册号都为空 |
| 202  | 公司不存在（扣次数） |
| 210  | 没有信息 |

系统错误码 101–108 见极速数据官网。

## 在 OpenClaw 中的推荐用法

1. 用户问某企业的联系电话、邮箱等时，用企业全称或统一信用代码等调用 `query`。
2. 从返回的 `result.list` 中取需要的联系方式与职务，用自然语言回复；注意脱敏与合规使用。更多计费与说明见 [极速数据](https://www.jisuapi.com/)。
