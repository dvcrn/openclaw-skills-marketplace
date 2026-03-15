# 04 - 决策层与执行层设计

## 一、决策层（Decision Layer）

### 1.1 设计目标

决策层接收认知层的分析结果，回答三个核心问题：
1. **风险有多大？** → RiskAssessment
2. **应该做什么？** → ActionPlanner
3. **谁来批准？** → ApprovalManager

---

## 二、RiskAssessment - 风险评估

### 2.1 风险评估模型

```
┌──────────────────────────────────────────────────────┐
│                    风险评估输入                         │
│                                                        │
│  ┌────────────┐ ┌────────────┐ ┌────────────────────┐ │
│  │ 异常检测    │ │ 趋势预测   │ │ 根因分析            │ │
│  │ 结果       │ │ 结果       │ │ 结果               │ │
│  └──────┬─────┘ └──────┬─────┘ └──────────┬─────────┘ │
│         └──────────────┼──────────────────┘            │
│                        ▼                                │
│  ┌─────────────────────────────────────────────────┐   │
│  │           多维度风险评估矩阵                       │   │
│  │                                                   │   │
│  │  严重性 (Severity)     × 0.30                    │   │
│  │  紧急性 (Urgency)      × 0.25                    │   │
│  │  影响范围 (Impact)     × 0.25                    │   │
│  │  操作复杂度 (Complexity) × 0.10                  │   │
│  │  业务敏感度 (Sensitivity) × 0.10                 │   │
│  └──────────────────────┬──────────────────────────┘   │
│                          ▼                               │
│           risk_score = Σ(wi × di) ∈ [0, 1]             │
└──────────────────────────────────────────────────────────┘
```

### 2.2 评估维度详解

#### 严重性（Severity）- 权重 30%

| 等级 | 分值 | 条件 |
|------|------|------|
| Critical (1.0) | 服务不可用 | 错误率 > 50% 或 撮合引擎停止 |
| High (0.75) | 性能严重下降 | P99 延迟 > 阈值 3 倍 或 部分功能不可用 |
| Medium (0.5) | 部分受影响 | 指标偏离基线 > 2σ 但服务仍可用 |
| Low (0.25) | 潜在风险 | 趋势异常，但尚未影响服务 |

#### 紧急性（Urgency）- 权重 25%

| 等级 | 分值 | 条件 |
|------|------|------|
| Immediate (1.0) | 正在影响交易 | 撮合延迟飙升、API 大面积超时 |
| High (0.75) | 预计 1h 内恶化 | 趋势预测 1h 内达到阈值 |
| Medium (0.5) | 预计 3h 内恶化 | 趋势预测 3h 内达到阈值 |
| Low (0.25) | 预计 6h+ | 趋势缓慢，可白天处理 |

#### 影响范围（Impact）- 权重 25%

```python
def assess_impact(anomaly, service_dependency_graph):
    # 受影响的服务数
    affected_services = get_downstream_services(anomaly.service, service_dependency_graph)
    service_score = min(len(affected_services) / 10, 1.0)

    # 业务影响
    if anomaly.service in CRITICAL_TRADING_SERVICES:
        # 撮合引擎、钱包服务、API 网关
        business_score = 1.0
    elif anomaly.service in IMPORTANT_SERVICES:
        # 行情推送、报表、清算
        business_score = 0.6
    else:
        business_score = 0.3

    # 交易量影响（基于当前交易量占比）
    current_trading_volume = get_current_volume()
    if is_peak_trading_hour():
        volume_score = 0.8
    else:
        volume_score = 0.4

    return 0.4 * service_score + 0.4 * business_score + 0.2 * volume_score
```

#### 操作复杂度（Complexity）- 权重 10%

| 等级 | 分值 | 条件 |
|------|------|------|
| Simple (0.25) | 标准化操作 | Pod 重启、HPA 扩容 |
| Medium (0.5) | 需要验证 | 服务回滚、配置变更 |
| Complex (0.75) | 多步骤操作 | 跨服务协调、数据库操作 |
| Critical (1.0) | 需要专家 | 撮合引擎调整、资金相关 |

#### 业务敏感度（Sensitivity）- 权重 10%

```python
# 交易系统特殊加权
SENSITIVITY_MAP = {
    "matching-engine": 1.0,    # 撮合引擎：最高敏感度
    "wallet-service": 1.0,     # 钱包服务：最高敏感度
    "trading-api": 0.8,        # 交易 API
    "market-data": 0.7,        # 行情服务
    "settlement": 0.8,         # 清算服务
    "risk-engine": 0.9,        # 风控引擎
    "user-service": 0.5,       # 用户服务
    "admin-service": 0.3,      # 管理后台
}
```

### 2.3 风险等级与处理策略

```python
def determine_strategy(risk_score, anomaly):
    """根据风险评分确定处理策略"""

    # 硬性规则：无论评分如何，资金相关操作一律 CRITICAL
    if anomaly.service in ["wallet-service", "settlement"]:
        if requires_financial_operation(anomaly):
            return Strategy.CRITICAL  # 仅诊断，不执行

    # 基于评分的策略
    if risk_score < 0.4:
        return Strategy.AUTO           # 自动执行
    elif risk_score < 0.6:
        return Strategy.SEMI_AUTO      # 单人审批
    elif risk_score < 0.8:
        return Strategy.MANUAL         # 多人审批
    else:
        return Strategy.CRITICAL       # 仅诊断
```

### 2.4 风险评估输出

```python
@dataclass
class RiskAssessmentResult:
    risk_score: float              # 综合风险评分 0-1
    risk_level: str                # LOW / MEDIUM / HIGH / CRITICAL
    strategy: str                  # AUTO / SEMI_AUTO / MANUAL / CRITICAL

    severity: SeverityDetail
    urgency: UrgencyDetail
    impact: ImpactDetail
    complexity: ComplexityDetail
    sensitivity: SensitivityDetail

    affected_services: List[str]
    estimated_business_impact: str  # "预计影响 ~5000 活跃用户"
    time_to_impact: Optional[str]   # "预计 2.5 小时后影响扩大"

    escalation_needed: bool
    escalation_target: Optional[str] # "trading-team-lead"
```

---

## 三、ActionPlanner - 行动规划

### 3.1 方案生成流程

```
风险评估结果 + RCA 结果 + RAG 建议
              │
              ▼
┌──────────────────────────────────────────┐
│  1. 匹配 Playbook (预定义操作手册)        │
│     → 如果有匹配的 Playbook，直接生成方案  │
└──────────────┬───────────────────────────┘
               │ 无匹配 Playbook
               ▼
┌──────────────────────────────────────────┐
│  2. LLM 生成方案                          │
│     → 基于 RCA 结果和 RAG 建议生成方案     │
│     → 人工审核后可转化为新 Playbook        │
└──────────────┬───────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────┐
│  3. 方案验证                              │
│     → 检查操作权限                         │
│     → 检查资源黑名单                       │
│     → 检查操作频率限制                     │
│     → 检查前置条件                         │
└──────────────────────────────────────────┘
```

### 3.2 Playbook 定义格式

```yaml
# playbooks/pod-restart.yaml
playbook:
  name: pod-restart
  description: 重启异常 Pod
  version: "1.0"

  # 触发条件
  match:
    anomaly_type: [CrashLoopBackOff, HighMemoryUsage, Unresponsive]
    severity: [MEDIUM, HIGH]

  # 风险评估
  risk:
    level: LOW
    max_risk_score: 0.4  # 超过此评分不使用此 Playbook

  # 前置检查
  pre_checks:
    - name: check_replica_count
      description: 确保至少有 2 个健康副本
      check: "kubectl get pods -l app={{service}} --field-selector=status.phase=Running | wc -l >= 2"
      on_fail: abort  # abort | warn | skip

    - name: check_recent_restarts
      description: 确保最近 1 小时内未重启超过 3 次
      check: "pod_restart_count_1h < 3"
      on_fail: abort

  # 执行步骤
  steps:
    - name: create_snapshot
      action: record_current_state
      description: 记录当前 Pod 状态

    - name: delete_pod
      action: kubectl_delete_pod
      params:
        namespace: "{{namespace}}"
        pod: "{{pod_name}}"
        grace_period: 30
      timeout: 60s

    - name: wait_for_ready
      action: wait_for_pod_ready
      params:
        namespace: "{{namespace}}"
        label_selector: "app={{service}}"
        timeout: 120s

    - name: verify_health
      action: health_check
      params:
        checks:
          - "error_rate < 0.05"         # 错误率低于 5%
          - "latency_p99 < {{threshold}}" # 延迟恢复正常
      timeout: 180s
      on_fail: rollback

  # 回滚方案
  rollback:
    steps:
      - name: notify_human
        action: send_alert
        params:
          message: "Pod 重启后验证失败，需要人工介入"
          severity: HIGH

  # 后续操作
  post_actions:
    - update_ticket
    - send_notification
    - record_audit_log

---
# playbooks/service-rollback.yaml
playbook:
  name: service-rollback
  description: 回滚服务到上一个稳定版本
  version: "1.0"

  match:
    root_cause_category: [部署变更]
    severity: [HIGH, CRITICAL]

  risk:
    level: MEDIUM
    max_risk_score: 0.7
    requires_approval: true

  pre_checks:
    - name: check_previous_version
      description: 确认上一个版本可用
      check: "previous_version_image_exists"
      on_fail: abort

    - name: check_not_blacklisted
      description: 确认服务不在回滚黑名单中
      check: "service not in rollback_blacklist"
      on_fail: abort

  steps:
    - name: create_ticket
      action: create_incident_ticket
      params:
        title: "自动回滚: {{service}} {{current_version}} → {{previous_version}}"
        severity: "{{severity}}"
        assignee: "{{oncall_sre}}"

    - name: request_approval
      action: send_approval_request
      params:
        channel: slack
        approvers: ["{{oncall_sre}}"]
        timeout: 15m
        message: |
          🔄 **回滚审批请求**
          服务: {{service}}
          当前版本: {{current_version}}
          回滚到: {{previous_version}}
          原因: {{root_cause}}
          风险评分: {{risk_score}}
      on_timeout: escalate

    - name: execute_rollback
      action: kubectl_rollout_undo
      params:
        namespace: "{{namespace}}"
        deployment: "{{deployment}}"
        to_revision: "{{previous_revision}}"
      timeout: 300s

    - name: verify_rollback
      action: health_check
      params:
        wait: 60s
        checks:
          - "all_pods_running"
          - "error_rate < 0.01"
          - "latency_p99 within baseline"
      timeout: 300s
      on_fail: notify_human

  post_actions:
    - update_ticket_resolved
    - send_completion_notification
    - record_audit_log
    - update_knowledge_base

---
# playbooks/hpa-scale-up.yaml
playbook:
  name: hpa-scale-up
  description: 临时调高 HPA 上限
  version: "1.0"

  match:
    anomaly_type: [HighCPU, HighLatency, TrafficSpike]
    condition: "hpa_current_replicas >= hpa_max_replicas * 0.9"

  risk:
    level: LOW
    max_risk_score: 0.4

  pre_checks:
    - name: check_node_capacity
      description: 确认集群有足够资源
      check: "cluster_allocatable_cpu > required_cpu"
      on_fail: warn

  steps:
    - name: scale_hpa
      action: kubectl_patch_hpa
      params:
        namespace: "{{namespace}}"
        hpa: "{{hpa_name}}"
        max_replicas: "{{current_max * 1.5}}"
      timeout: 30s

    - name: wait_for_scale
      action: wait_for_replicas
      params:
        timeout: 300s

    - name: schedule_revert
      action: schedule_task
      params:
        delay: 2h
        action: revert_hpa_max
        description: "2 小时后恢复 HPA 上限"

  post_actions:
    - send_notification
    - record_audit_log
```

### 3.3 行动计划输出

```python
@dataclass
class ActionPlan:
    plan_id: str                    # "PLAN-20260209-143022"
    strategy: str                   # AUTO / SEMI_AUTO / MANUAL / CRITICAL
    playbook_name: Optional[str]    # 使用的 Playbook 名称
    generated_by: str               # "playbook" / "llm"

    anomaly_id: str
    risk_score: float
    risk_level: str

    steps: List[ActionStep]
    rollback_plan: RollbackPlan

    requires_approval: bool
    approvers: List[str]
    approval_timeout: timedelta

    estimated_duration: timedelta
    success_probability: float      # 基于历史数据的成功率
    similar_cases_count: int        # 历史相似案例数

    created_at: datetime
    expires_at: datetime            # 方案有效期（超期需重新评估）

@dataclass
class ActionStep:
    step_number: int
    name: str
    action_type: str    # "automated" / "approval" / "manual" / "verification"
    description: str
    params: Dict
    timeout: timedelta
    on_fail: str        # "abort" / "rollback" / "skip" / "notify_human"
```

---

## 四、ApprovalManager - 审批管理

### 4.1 审批流程

```
┌───────────────────────────────────────────────────────────┐
│                    审批流程                                  │
│                                                             │
│  ActionPlan (requires_approval=true)                       │
│       │                                                     │
│       ▼                                                     │
│  ┌─────────────────┐                                       │
│  │ 发送审批请求     │                                       │
│  │ → Slack Interactive Message                             │
│  │ → API Webhook                                           │
│  │ → PagerDuty (如配置)                                    │
│  └────────┬────────┘                                       │
│           │                                                 │
│           ▼                                                 │
│  ┌─────────────────┐     ┌─────────────────┐              │
│  │ 等待审批         │────▶│ 超时处理         │              │
│  │ (timeout: 15min)│     │ → 升级通知       │              │
│  └────────┬────────┘     │ → 通知 Team Lead │              │
│           │               └─────────────────┘              │
│     ┌─────┴─────┐                                          │
│     ▼           ▼                                          │
│  APPROVED    REJECTED                                      │
│     │           │                                          │
│     ▼           ▼                                          │
│  执行方案    记录原因                                       │
│     │        创建手动工单                                   │
│     ▼                                                       │
│  执行结果验证                                               │
│     │                                                       │
│     ▼                                                       │
│  发送完成通知                                               │
└───────────────────────────────────────────────────────────┘
```

### 4.2 Slack 审批消息设计

```json
{
  "blocks": [
    {
      "type": "header",
      "text": "🔧 SRE Agent - 操作审批请求"
    },
    {
      "type": "section",
      "fields": [
        {"type": "mrkdwn", "text": "*Plan ID:*\nPLAN-20260209-143022"},
        {"type": "mrkdwn", "text": "*Risk Level:*\n🟡 MEDIUM (0.55)"},
        {"type": "mrkdwn", "text": "*Service:*\ntrading-api"},
        {"type": "mrkdwn", "text": "*Strategy:*\nSEMI_AUTO"}
      ]
    },
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": "*异常描述:*\n`trading-api` 的 P99 延迟从 50ms 上升到 250ms，持续 10 分钟。\n\n*根因分析:*\n最近 15 分钟前部署了 v2.3.1，部署后延迟开始上升（置信度 85%）。\n\n*建议操作:*\n回滚 `trading-api` 从 v2.3.1 到 v2.3.0"
      }
    },
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": "*历史参考:*\n类似操作历史成功率 95%（8 次相似案例）\n预计执行时间: 5 分钟"
      }
    },
    {
      "type": "actions",
      "elements": [
        {
          "type": "button",
          "text": {"type": "plain_text", "text": "✅ 批准执行"},
          "style": "primary",
          "action_id": "approve_plan",
          "value": "PLAN-20260209-143022"
        },
        {
          "type": "button",
          "text": {"type": "plain_text", "text": "❌ 拒绝"},
          "style": "danger",
          "action_id": "reject_plan",
          "value": "PLAN-20260209-143022"
        },
        {
          "type": "button",
          "text": {"type": "plain_text", "text": "📋 查看详情"},
          "action_id": "view_details",
          "value": "PLAN-20260209-143022"
        }
      ]
    },
    {
      "type": "context",
      "elements": [
        {"type": "mrkdwn", "text": "⏰ 审批超时: 15 分钟 | 超时将升级通知 Team Lead"}
      ]
    }
  ]
}
```

### 4.3 审批规则

```yaml
approval_rules:
  # SEMI_AUTO: 单人审批
  semi_auto:
    approvers:
      - oncall_sre             # 当前 On-call SRE
    timeout: 15m
    on_timeout: escalate_to_team_lead
    on_reject: create_manual_ticket

  # MANUAL: 多人审批
  manual:
    approvers:
      - oncall_sre             # On-call SRE
      - team_lead              # 技术 Lead
    required_approvals: 2      # 需要 2 人批准
    timeout: 30m
    on_timeout: escalate_to_director
    on_reject: create_manual_ticket

  # 特殊规则
  special:
    # 非工作时间自动提升审批级别
    - condition: "not is_business_hours()"
      action: escalate_one_level  # SEMI_AUTO → MANUAL

    # 撮合引擎相关操作，即使低风险也需要审批
    - condition: "affected_service == 'matching-engine'"
      action: require_approval_always
```

---

## 五、执行层（Action Layer）

### 5.1 AlertManager - 告警管理

#### 5.1.1 与 n9e 的集成

SRE Agent 不替代 n9e，而是作为**增强层**：

```
原有流程:
  Prometheus → n9e 告警规则 → 通知 (Slack/WeChat/PagerDuty)

增强后流程:
  Prometheus → n9e 告警规则 ──────────────────▶ 通知 (保留原有)
       │                                           │
       ▼                                           │
  SRE Agent 感知层 → 认知层 → 决策层               │
       │                                           │
       ▼                                           │
  增强告警: 附带根因分析 + 修复建议 + 相似案例 ─────┘
       │
       ▼
  (如需) 触发自愈操作
```

#### 5.1.2 告警降噪策略

```yaml
alert_noise_reduction:
  # 1. 聚合: 同一根因的告警合并为一条
  aggregation:
    window: 5m
    group_by: [root_cause_id, service]
    template: "{{service}} 出现 {{count}} 个关联异常，根因: {{root_cause}}"

  # 2. 抑制: 上游故障抑制下游告警
  inhibition:
    rules:
      # 如果 matching-engine 故障，抑制 trading-api 的超时告警
      - source: {service: matching-engine, severity: CRITICAL}
        target: {service: trading-api, anomaly_type: HighLatency}
        duration: 30m

      # 如果 Redis 故障，抑制所有依赖 Redis 的服务告警
      - source: {service: redis, severity: CRITICAL}
        target: {label: depends_on=redis}
        duration: 30m

  # 3. 静默: 维护窗口期间降低告警级别
  silence:
    # 通过 API 动态设置
    api: POST /api/silence
    params:
      - services: ["trading-api"]
        duration: 2h
        reason: "计划内部署"
        creator: "deploy-bot"

  # 4. 频率限制: 同一告警不重复发送
  rate_limit:
    same_alert_interval: 30m   # 同一告警 30 分钟内不重复
    same_service_max: 5        # 同一服务 30 分钟内最多 5 条
```

#### 5.1.3 告警通知路由

```yaml
notification_routing:
  channels:
    # Slack
    slack:
      - channel: "#sre-alerts-critical"
        condition: "severity == CRITICAL"
      - channel: "#sre-alerts"
        condition: "severity in [HIGH, MEDIUM]"
      - channel: "#sre-alerts-low"
        condition: "severity == LOW"

    # PagerDuty
    pagerduty:
      - service_key: "trading-critical"
        condition: "severity == CRITICAL and service in critical_trading_services"
      - service_key: "infra-high"
        condition: "severity == HIGH"

    # 邮件 (低优先级摘要)
    email:
      - recipients: ["sre-team@company.com"]
        condition: "severity in [MEDIUM, LOW]"
        digest: true            # 每 30 分钟汇总发送
        digest_interval: 30m

    # n9e (回写告警事件)
    n9e_webhook:
      - url: "http://n9e-server:17000/api/v1/alert"
        condition: "always"  # 所有 Agent 产生的告警都同步回 n9e
```

### 5.2 TicketManager - 工单管理

#### 5.2.1 工单自动创建

```python
def create_incident_ticket(anomaly, rca_result, risk_assessment):
    """异常检测到后自动创建事件工单"""

    ticket = {
        "title": f"[{risk_assessment.risk_level}] {anomaly.service}: {anomaly.metric_name} 异常",
        "priority": risk_to_priority(risk_assessment.risk_level),
        "assignee": get_oncall_sre(),
        "labels": [
            f"service:{anomaly.service}",
            f"severity:{anomaly.severity}",
            f"auto-created",
        ],

        "description": f"""
## 异常概况
- **指标**: {anomaly.metric_name}
- **当前值**: {anomaly.current_value} (基线: {anomaly.expected_value})
- **偏离**: {anomaly.deviation_percent}%
- **开始时间**: {anomaly.start_time}
- **持续时间**: {anomaly.duration}

## 根因分析
{format_rca(rca_result)}

## 风险评估
- **风险评分**: {risk_assessment.risk_score}
- **处理策略**: {risk_assessment.strategy}
- **影响范围**: {risk_assessment.estimated_business_impact}

## 修复建议
{format_actions(rca_result.recommended_actions)}

## 相似历史案例
{format_similar_incidents(rca_result.similar_incidents)}

---
_此工单由 SRE Agent 自动创建_
        """,
    }

    # 根据配置选择工单系统
    if config.ticket_system == "jira":
        return jira_client.create_issue(ticket)
    elif config.ticket_system == "internal":
        return internal_api.create_ticket(ticket)
```

#### 5.2.2 工单生命周期管理

```
工单创建 (Agent 自动)
    │
    ├── OPEN: 分配给 On-call SRE
    │
    ├── IN_PROGRESS: Agent 开始执行自愈 or SRE 手动处理
    │
    ├── PENDING_APPROVAL: 等待审批 (自动更新)
    │
    ├── RESOLVED: 自愈成功或人工确认修复
    │       │
    │       └── Agent 自动添加处理摘要:
    │           - 根因确认
    │           - 执行的操作
    │           - 恢复时间
    │
    └── CLOSED: 人工确认关闭
            │
            └── Agent 将事件写入 RAG 知识库
```

### 5.3 AutoRemediation - 自愈执行

#### 5.3.1 执行引擎设计

```
┌──────────────────────────────────────────────────────────────┐
│                    AutoRemediation 执行引擎                    │
│                                                                │
│  ActionPlan (已审批)                                          │
│       │                                                        │
│       ▼                                                        │
│  ┌─────────────────┐                                          │
│  │ Pre-Execution    │ • 再次验证当前状态                       │
│  │ Validation       │ • 检查黑名单                             │
│  │                  │ • 检查操作频率限制                        │
│  │                  │ • 创建操作快照 (rollback point)          │
│  └────────┬────────┘                                          │
│           │ 通过                                               │
│           ▼                                                    │
│  ┌─────────────────┐                                          │
│  │ Step Executor    │ 按顺序执行每个 Step:                     │
│  │                  │ • kubectl 操作 (rollout, scale, delete)  │
│  │                  │ • AWS CLI 操作 (EC2, RDS, ElastiCache)   │
│  │                  │ • Helm 操作 (upgrade, rollback)           │
│  │                  │ • API 调用 (配置变更, 限流)               │
│  └────────┬────────┘                                          │
│           │                                                    │
│           ▼                                                    │
│  ┌─────────────────┐                                          │
│  │ Post-Execution   │ • 等待服务稳定 (configurable wait)      │
│  │ Verification     │ • 检查关键指标是否恢复                   │
│  │                  │ • 检查是否引入新问题                     │
│  └────────┬────────┘                                          │
│     ┌─────┴─────┐                                             │
│     ▼           ▼                                             │
│  SUCCESS      FAILURE                                         │
│     │           │                                             │
│     │           ▼                                             │
│     │     ┌─────────────────┐                                 │
│     │     │ Auto Rollback   │ • 回到快照点                    │
│     │     │                 │ • 通知人工介入                   │
│     │     │                 │ • 升级工单                       │
│     │     └─────────────────┘                                 │
│     │                                                          │
│     ▼                                                          │
│  完成通知 + 更新工单 + 审计日志 + 知识库更新                   │
└──────────────────────────────────────────────────────────────┘
```

#### 5.3.2 安全保障

```yaml
safety_mechanisms:
  # 操作黑名单: 这些资源永远不自动操作
  blacklist:
    namespaces:
      - kube-system
      - monitoring
    deployments:
      - matching-engine-core    # 撮合引擎核心
      - wallet-signer           # 钱包签名服务
    resources:
      - "rds:trading-db-primary"  # 生产数据库主库
      - "elasticache:session-*"   # 会话缓存集群

  # 操作频率限制
  rate_limits:
    per_resource:
      max_operations: 3
      window: 1h
      on_exceed: block_and_notify

    per_namespace:
      max_operations: 10
      window: 1h

    global:
      max_operations: 20
      window: 1h

  # 操作时间窗口
  operation_windows:
    # 自动操作仅在特定时间允许
    auto_remediation:
      allowed: "always"  # 交易系统 7×24 都可能需要自愈
      blocked_during:
        - "scheduled_maintenance"  # 维护窗口期间不自动操作

  # 回滚策略
  rollback:
    auto_rollback_on_failure: true
    rollback_timeout: 300s
    max_rollback_attempts: 1  # 回滚失败不再重试，通知人工
```

### 5.4 AuditLogger - 审计日志

```python
@dataclass
class AuditLog:
    log_id: str
    timestamp: datetime
    event_type: str          # "detection", "analysis", "decision", "approval", "execution", "rollback"
    actor: str               # "sre-agent" / "john@company.com" (审批人)

    # 异常信息
    anomaly_id: Optional[str]
    plan_id: Optional[str]

    # 操作信息
    action: str              # "pod_restart", "rollback_deployment", etc.
    target: str              # "trading-api/deployment/trading-api-v2"
    namespace: str

    # 执行详情
    pre_state: Dict          # 操作前状态快照
    post_state: Dict         # 操作后状态
    result: str              # "success" / "failure" / "rollback"
    error_message: Optional[str]
    duration: float          # 执行耗时 (秒)

    # 审批信息
    approved_by: Optional[str]
    approval_time: Optional[datetime]

# 审计日志存储:
#   - 写入 RDS MySQL (结构化查询)
#   - 同步到 Kafka topic: sre-agent-audit (用于合规留存)
#   - 保留期限: >= 1 年
```
