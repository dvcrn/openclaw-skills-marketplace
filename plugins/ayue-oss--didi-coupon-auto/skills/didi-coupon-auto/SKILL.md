---
name: didi-coupon-auto
description: "自动领取滴滴出行优惠券。每天0点自动领取打车券包，支持网约车、顺风车、代驾等多种出行券。触发词: 领取滴滴优惠券, 运行滴滴领券技能, 设置每日自动领取滴滴, 滴滴打车券, didi coupon"
---

# 滴滴出行优惠券自动领取

每天 0:00 自动打开滴滴领券页，点击领取当日打车券包（网约车 / 顺风车 / 代驾等）。

首次运行需要在浏览器中登录滴滴账号；登录后 cookie 保留，后续全自动运行。

---

## 触发词

- "领取滴滴优惠券" / "滴滴领券"
- "运行滴滴领券技能" / "didi coupon"
- "设置每日自动领取滴滴"
- "打车有优惠券吗"

---

## 执行流程

### 步骤 1：启动浏览器

```
browser(action=status, profile=openclaw)
# 未运行则先 start
browser(action=start, profile=openclaw)
```

### 步骤 2：运行领券脚本

```bash
node skills/didi-coupon-auto/scripts/claim.mjs
```

### 步骤 3：处理结果

| 脚本输出 | 处理方式 |
|---------|---------|
| `需要登录` | 告知用户在浏览器手动登录滴滴，登录后重新运行 |
| `今日已领取` | 回复"今天已经领过了" |
| `领取完成！点击了 N 个按钮` | 回复领取成功摘要 |

---

## 定时任务（每天 0 点）

```json
{
  "name": "每日滴滴领券",
  "schedule": { "kind": "cron", "expr": "0 0 * * *", "tz": "Asia/Shanghai" },
  "payload": { "kind": "agentTurn", "message": "领取滴滴优惠券" },
  "sessionTarget": "isolated",
  "delivery": { "mode": "announce" }
}
```

---

## 页面状态说明

| 状态 | 识别关键词 | 处理 |
|------|----------|------|
| 未登录 | `登录领取` | 提示用户手动登录 |
| 可领取 | `立即领取` / `领取` | 自动点击 |
| 已领取 | `已领取` / `去使用` | 跳过，通知用户 |
| 已抢光 | `已抢光` | 跳过 |

---

## 领券地址

```
https://vv.didi.cn/a8ZdG0j?source_id=88446DIDI88446tkmmchild1001&ref_from=dunion
```
覆盖：网约车券 · 顺风车券 · 特惠券 · 代驾券

---

> 📋 测试记录 (2026-03-13)：
> - [x] 触发方式：调用 MPX 组件 `autoGetCoupon()` / 降级 `btn.click()`
> - [x] 监听 `reward/receive` API 响应判断领取结果
> - [x] 监听 `reward/list` API 响应展示券明细
> - [x] 今日已领 17 张券 ¥166，状态识别正确（errno=3000030009）
> - [x] **耗时 4.3s**
> - [ ] 明日 0:05 定时任务实测（errno=0 首次领取）
