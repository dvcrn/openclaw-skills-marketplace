# Training Scenarios

Use this file only when running an active ClawdGo scene.

## Scene 1: CEO 紧急汇款

### Scene Card

- Attack Type: `BEC / 高管身份施压`
- Difficulty: `★★☆`
- Pressure Profile: `高额资金 + 保密要求 + 限时催促`

- From: `zhang.dong.ceo@company-finance.net`
- Display Name: `张总 (CEO)`
- Subject: `【紧急】今日必须完成的汇款`
- Body summary:
  - 需要在 1 小时内完成 `¥500,000` 汇款
  - 供应商账户刚变更
  - 要求不要电话联系，不要告诉其他同事

### Investigation Cards

1. `核验发件域名`
2. `检查供应商变更流程`
3. `独立联系 CEO`
4. `检查保密与时限要求`

### Investigation Reveals

1. 发件域名不是公司官方域名。
2. 供应商变更未走正式财务审批。
3. 可通过已知内部渠道联系 CEO，邮件要求绕过此流程。
4. `限时 + 保密` 是典型社工隔离策略。

### Good Final Action

- 拒绝直接转账
- 通过已知内部渠道核实 CEO
- 向财务或安全负责人升级

### Escalation Card

- Follow-up event:
  - 对方再次发来短消息，强调“供应商正在等最终确认，现在不方便接电话，你先付，我晚点补签”
- Good chain action:
  - 继续拒绝付款
  - 固定走公司审批链
  - 冻结该转账请求并留痕上报
- Bad chain action:
  - 因二次催促而先付款
  - 改成只回复消息确认

### Wrong Final Action

- 按邮件要求直接汇款
- 只回复邮件确认

### Knowledge Point

BEC 的核心防御不是“看起来像不像老板”，而是所有资金指令都必须走独立核验链路。

## Scene 2: 系统密码验证

### Scene Card

- Attack Type: `账号钓鱼 / 假登录页`
- Difficulty: `★☆☆`
- Pressure Profile: `异常登录预警 + 账户锁定恐吓`

- From: `security-noreply@microsofft-account.com`
- Subject: `您的账户存在异常登录，请立即验证`
- Link: `http://microsoft-secure-verify.login-check.cc/...`
- Body summary:
  - 声称账户有俄罗斯异常登录
  - 要求立即点链接验证身份

### Investigation Cards

1. `检查发件域名拼写`
2. `检查链接域名`
3. `检查协议与证书暗示`
4. `改为手动访问官网`

### Investigation Reveals

1. `microsofft` 存在拼写伪装。
2. 链接域名不是 `microsoft.com`。
3. 链接使用 `http://`，可信度极低。
4. 正确做法是手动输入官网，不通过邮件链接登录。

### Good Final Action

- 不点击邮件链接
- 手动访问微软官网或官方 App 检查账号
- 必要时修改密码并检查 MFA

### Escalation Card

- Follow-up event:
  - 假登录页又弹出“若 10 分钟内不完成，账号将锁定 24 小时”
- Good chain action:
  - 关闭页面
  - 通过官方入口检查账号状态
  - 若怀疑泄露则主动改密并检查 MFA
- Bad chain action:
  - 在压力下继续完成验证
  - 把验证码也输入伪造页面

### Wrong Final Action

- 点击链接并输入凭据
- 按页面要求输入验证码

### Knowledge Point

识别钓鱼最稳定的办法是看域名，不是看页面长相。

## Scene 3: 工资单查询

### Scene Card

- Attack Type: `内部系统仿冒 / 凭据收集`
- Difficulty: `★★☆`
- Pressure Profile: `工资影响 + 内网伪装 + 升级通知`

- From: `hr-system@hr-payroll-internal.com`
- Subject: `请重新验证身份以查看 3 月工资单`
- Link: `https://hr-payroll-internal.com/employee-login`
- Body summary:
  - HR 系统升级
  - 要求员工重新登录查看工资单

### Investigation Cards

1. `核验 HR 域名`
2. `检查是否属于内网入口`
3. `确认升级通知来源`
4. `检查是否要求重新输入密码`

### Investigation Reveals

1. 域名为外部域，不是公司内网地址。
2. 正规 HR 系统一般通过固定内网书签访问。
3. 批量通知未附带内部工单或 IT 公告编号。
4. 系统升级通常不会要求通过邮件链接重新登录。

### Good Final Action

- 不点邮件链接
- 通过公司内网入口或 IT 官方渠道确认

### Escalation Card

- Follow-up event:
  - 攻击者追加一封“最后提醒”，声称“不验证将影响本月工资发放”
- Good chain action:
  - 不被情绪话术带节奏
  - 联系 HR/IT 官方渠道核验
  - 把邮件作为仿冒样本转交安全团队
- Bad chain action:
  - 因担心工资受影响而立刻登录

### Wrong Final Action

- 直接使用企业账号登录邮件中的站点

### Knowledge Point

内部系统仿冒的关键不是“像不像内网”，而是入口是否来自可信渠道。

## Scene 4: 快递异常通知

### Scene Card

- Attack Type: `短信钓鱼 / 物流仿冒`
- Difficulty: `★☆☆`
- Pressure Profile: `包裹退回威胁 + 小额支付诱导`

- SMS From: `+86 138xxxx7823`
- Body summary:
  - 快递地址异常
  - 24 小时内补充信息，否则退回
- Link: `http://sf-express-cn.delivery-update.top/...`

### Investigation Cards

1. `检查发信号码`
2. `检查快递域名`
3. `检查顶级域与协议`
4. `改为打开官方 App`

### Investigation Reveals

1. 来自普通手机号，不是品牌官方通道。
2. 链接域名不是顺丰官方域。
3. `.top + http` 组合风险极高。
4. 正确路径是打开官方 App 查询订单状态。

### Good Final Action

- 不点击短信链接
- 打开官方 App 或官网查询
- 删除并上报可疑短信

### Escalation Card

- Follow-up event:
  - 链接页面又提示“补 3 元派送费即可重新配送”
- Good chain action:
  - 不支付任何费用
  - 继续通过官方 App 查询
  - 标记为短信钓鱼
- Bad chain action:
  - 因金额很小而放松警惕
  - 进入支付页填写银行卡信息

### Wrong Final Action

- 点链接并输入姓名、电话、地址或支付信息

### Knowledge Point

短信钓鱼常靠“小屏幕难看清域名”获胜，移动端更要坚持只用官方 App。

## Scene 5: 社保账户异常

### Scene Card

- Attack Type: `政务仿冒 / 恶意附件投递`
- Difficulty: `★★★`
- Pressure Profile: `官方权威伪装 + 附件执行风险 + 身份核验`

- From: `service@12333-shebaoju.cn`
- Subject: `您的社会保险账户存在异常，需要在 3 个工作日内处理`
- Link: `http://12333.shebaoju-verify.com/auth`
- Attachment: `账户核实申请表.exe`
- Body summary:
  - 声称社保账户被冻结风险
  - 附带可执行文件
  - 引导到伪造核验入口

### Investigation Cards

1. `检查政府域名后缀`
2. `检查附件类型`
3. `检查核验入口域名`
4. `改为拨打官方电话`

### Investigation Reveals

1. 政府网站应使用 `.gov.cn`。
2. `.exe` 附件不应出现在政府身份核验邮件中。
3. 验证域名不是官方政府域。
4. 正确核验应通过 `12333` 官方热线或官网。

### Good Final Action

- 不打开附件，不点击链接
- 通过官方社保网站或热线核验
- 隔离邮件并上报

### Escalation Card

- Follow-up event:
  - 附件名被改成 `账户核验说明.pdf.exe`，并配文“若打不开请关闭杀毒软件后再试”
- Good chain action:
  - 保持隔离，不运行附件
  - 明确识别双扩展名风险
  - 通过官方热线核验并提交样本
- Bad chain action:
  - 为了查看内容临时关闭防护或运行附件

### Wrong Final Action

- 运行附件
- 在伪造页面提交身份证、手机号、验证码

### Knowledge Point

任何伪装政府机构但不使用 `.gov.cn` 的入口都应视为高风险仿冒。
