# JD Lawsuit API Schema

> 基础地址: `https://jdlawsuit-web.jd.com/api/v1`
> 认证方式: 浏览器 Cookie（HttpOnly，必须通过 Electron/browser_fetch_json）

## POST /workbench/searchCaseList — 我的案件列表（推荐）

> ⚠️ 前端实际调用此接口。自动按登录用户过滤，只返回当前用户相关的案件。
> `/workbench/search` 是管理接口，返回全量数据，普通用户不应使用。

### 请求体

```json
{
  "current": 1,           // 页码（必填）
  "size": 10,             // 每页条数（必填，前端默认10）
  "caseType": 1,          // 案件类型：1=诉讼, 11=仲裁（必填）
  "stageStatus": 1,       // 状态：1=处理中, 2=已生效, 3=执行中, 4=已执结（必填）
  "origin": "",           // 发起方：1=主诉, 2=被诉（可选，不传=全部）
  "innerCaseCode": "",    // 内部案号（可选）
  "outerCaseCode": "",    // 外部案号（可选）
  "plaintiff": "",        // 原告（可选）
  "defendant": "",        // 被告（可选）
  "caseSummary": "",      // 案由（可选）
  "courtName": "",        // 审理机构（可选）
  "primaryChargeName": "", // 承办人（可选）
  "orderByColumns": "",   // 排序列（可选，如 "amount_involved"）
  "orderByRules": ""      // 排序方向（可选，"ASC" 或 "DESC"）
}
```

## POST /workbench/search — 全量案件搜索（管理接口）

> ⚠️ 返回全量数据，不按用户过滤。普通场景请用 searchCaseList。

### 请求体

```json
{
  "current": 1,           // 页码（必填）
  "size": 15,             // 每页条数（必填）
  "caseType": 1,          // 案件类型：1=诉讼, 11=仲裁（必填）
  "stageStatus": 1,       // 状态：1=处理中, 2=已生效, 3=执行中, 4=已执结（必填）
  "innerCaseCode": "",    // 内部案号（可选）
  "outerCaseCode": "",    // 外部案号（可选）
  "plaintiff": "",        // 原告（可选）
  "defendant": "",        // 被告（可选）
  "caseSummary": "",      // 案由（可选）
  "courtName": "",        // 审理机构（可选）
  "primaryChargeName": "" // 承办人（可选）
}
```

### 响应结构

```json
{
  "code": 200,
  "data": {
    "current": "1",
    "total": 2,
    "records": [
      {
        "id": "9157931097637273600",
        "innerCaseCode": "AJ-20241126-1554399489",
        "outerCaseCode": "（2024）陕0117民初5977号",
        "plaintiff": "杨凯",
        "defendant": "陕西京东信成供应链科技有限公司",
        "caseSummary": "劳动争议、人事争议-劳动争议",
        "caseBehaviorOne": "劳动关系解除",
        "amountInvolved": 64509.70,
        "riskLevel": "1",
        "currentState": 49,
        "currentStateStr": "诉讼完结",
        "primaryChargeName": "陈子豪",
        "primaryChargeErp": "chenzihao73",
        "openCourtTalkTime": "2024-11-28 10:30",
        "courtName": "西安市高陵区人民法院",
        "provinceName": "陕西省",
        "cityName": "西安市",
        "allLawFirm": "上海百事通法务技术有限公司",
        "allLawyer": "陈可可",
        "caseType": "1",
        "caseSource": "3",
        "enteredTime": "2024-11-26 15:54:40",
        "enteredByName": "陈子豪",
        "assignerName": "田甜",
        "assignTime": "2024-11-26 15:54:40",
        "closingAmount": 0.00,
        "diffAmount": 64509.70,
        "effectedTime": "2025-10-29 00:00:00",
        "entrustModel": "1",
        "productModelStr": "其他",
        "handleType": "2",
        "hasLawFirm": "有",
        "departFullName": "京东集团-CHO体系-物流人力资源部-用工保障中心-西北组"
      }
    ]
  }
}
```

### 风险等级 (riskLevel)

| 值 | 含义 |
|----|------|
| 1  | 蓝色常规案件 |
| 2  | 黄色关注案件 |
| 3  | 红色重大案件 |

### 案件状态 (stageStatus)

| 值 | 含义 |
|----|------|
| 1  | 处理中 |
| 2  | 已生效 |
| 3  | 执行中 |
| 4  | 已执结 |

### 案件类型 (caseType)

| 值 | 含义 |
|----|------|
| 1  | 诉讼案件 |
| 11 | 仲裁案件 |

## 其他已知 API

| 接口 | 方法 | 说明 |
|------|------|------|
| `/user/me3` | GET | 当前用户信息 |
| `/user/me2` | GET | 用户详情 |
| `/uim/roles` | GET | 用户角色 |
| `/uim/menus` | GET | 菜单权限 |
| `/workbench/searchCount` | POST | 各状态案件数量统计 |
| `/workbench/getCustomizedTableColumn?from=1` | GET | 自定义列配置 |
| `/innerCaseReminders/search` | POST | 提醒搜索 |
| `/innerCaseReminders/todayAndThreeDaysReminders` | GET | 近期提醒 |
| `/remind/openCourtTalkTime?current=1&size=200` | GET | 开庭时间提醒 |
| `/remind/notices?current=1&size=200` | GET | 通知 |
| `/remind/demands?current=1&size=200` | GET | 需求 |
| `/remind/caseDelArchives?current=1&size=200` | GET | 归档提醒 |
| `/dataDict/allCategoryBehaviorNew` | GET | 案由字典 |
| `/dataDict/pageSize/MAIN_CASE` | GET | 分页配置 |
| `/assign/primaryChargers` | GET | 承办人列表 |
| `/vender/chat/log/getUnreadChatList/{erp}/{caseType}` | GET | 商家未读消息 |
| `/vender/inform/getUnreplyList/{erp}/{caseType}` | GET | 商家未回复 |
| `/mail/inbox` | GET | 站内信 |

## 页面 URL 规则

- 案件列表: `https://jdlawsuit-web.jd.com/#/case-list`
- 案件详情: `https://jdlawsuit-web.jd.com/#/case-detail?no={id}`
  - `no` 参数是 `id` 字段（如 `-7896699726227267508`），不是 `innerCaseCode`
