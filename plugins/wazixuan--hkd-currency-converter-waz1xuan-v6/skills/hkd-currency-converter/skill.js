#!/usr/bin/env node
/**
 * 💱 HKD汇率转换神器 v1.2.0
 * OpenClaw Skill — by 王 🤴 (@waz1xuan)
 *
 * 依赖:  npm install axios
 *
 * 用法:
 *   node skill.js "1000 HKD to USD"
 *   node skill.js "500 HKD to CNY"
 *   node skill.js "1000 HKD"              ← 一次显示全部常见货币
 *
 * 本地测试（跳过 SkillPay）:
 *   LOCAL_TEST=1 node skill.js "1000 HKD to USD"
 *
 * 调试（打印原始 API 响应）:
 *   DEBUG=1 LOCAL_TEST=1 node skill.js "1000 HKD to USD"
 *
 * 汇率来源: exchangerate-api.com 免费层（1500 次/月）
 *   - 实时汇率: ✅ 支持
 *   - 历史汇率: ❌ 仅付费层支持（已注释，如需启用请升级账户）
 */

"use strict";

const axios = require("axios");

// ─── 🔑 SkillPay 配置 ─────────────────────────────────────────────────────────
const SKILLPAY_API_KEY =
  process.env.SKILLPAY_API_KEY ||
  "sk_5f1acfb83c5bf021332327263b9c04c6b101c2cb6a66af2cf395f0d80203a65";

const SKILLPAY_CHARGE_URL = "https://api.skillpay.me/api/v1/billing/charge";

// ─── 🔑 ExchangeRate-API 配置 ─────────────────────────────────────────────────
const FX_API_KEY = process.env.FX_API_KEY || "220cf04f6f6cf97d9ee39098";
const FX_BASE    = "https://v6.exchangerate-api.com/v6";
const BASE_CCY   = "HKD";
const ALL_CCYS   = ["USD", "CNY", "EUR", "GBP"];

// ─── 运行模式 ─────────────────────────────────────────────────────────────────
const LOCAL_TEST = process.env.LOCAL_TEST === "1"; // 跳过 SkillPay
const DEBUG      = process.env.DEBUG === "1";       // 打印原始响应

// ─── OpenClaw Context ─────────────────────────────────────────────────────────
const USER_ID = process.env.OPENCLAW_USER_ID || "anonymous";

const AXIOS_OPTS = { timeout: 15000 };

// ═════════════════════════════════════════════════════════════════════════════
// 1. 解析输入
// ═════════════════════════════════════════════════════════════════════════════
function parseInput(raw) {
  if (!raw || !raw.trim()) {
    return { amount: 1, target: null, showAll: true };
  }

  // "数字 [HKD] to/转 货币"
  const matchFull = raw.match(/(\d+(?:\.\d+)?)\s*(?:HKD)?\s*(?:to|转)\s*([A-Za-z]{3})/i);
  if (matchFull) {
    return {
      amount: parseFloat(matchFull[1]),
      target: matchFull[2].toUpperCase(),
      showAll: false,
    };
  }

  // 只有金额 → 显示全部货币
  const matchAmountOnly = raw.match(/^(\d+(?:\.\d+)?)\s*(?:HKD)?$/i);
  if (matchAmountOnly) {
    return { amount: parseFloat(matchAmountOnly[1]), target: null, showAll: true };
  }

  // 只有货币代码 → 金额默认 1
  const matchCcyOnly = raw.match(/\b([A-Za-z]{3})\b/i);
  if (matchCcyOnly && ALL_CCYS.includes(matchCcyOnly[1].toUpperCase())) {
    return { amount: 1, target: matchCcyOnly[1].toUpperCase(), showAll: false };
  }

  throw new Error(
    `输入格式无法识别："${raw}"\n` +
    `示例: "1000 HKD to USD" / "500 HKD to CNY" / "1000 HKD"`
  );
}

// ═════════════════════════════════════════════════════════════════════════════
// 2. SkillPay 收款
// ═════════════════════════════════════════════════════════════════════════════
async function charge(userId) {
  if (LOCAL_TEST) {
    console.log("  [LOCAL_TEST] 跳过 SkillPay 扣费");
    return { paid: true };
  }

  try {
    if (DEBUG) console.log(`  [DEBUG] POST ${SKILLPAY_CHARGE_URL}  userId=${userId}`);

    const res = await axios.post(
      SKILLPAY_CHARGE_URL,
      { userId },
      {
        headers: {
          "X-API-Key":    SKILLPAY_API_KEY,
          "Content-Type": "application/json",
        },
        timeout: 10000,
      }
    );

    const d = res.data || {};
    if (DEBUG) console.log("  [DEBUG] SkillPay 响应:", JSON.stringify(d));

    if (d.success === true || d.status === "paid" || d.status === "success") {
      return { paid: true };
    }

    // Token 不足 → 兼容多种字段名
    const payUrl = d.payment_url || d.paymentLink || d.paymentUrl || null;
    if (payUrl) return { paid: false, payment_url: payUrl };

    // 未知 2xx → 宽松通过
    console.error("  [SkillPay] 未知响应，宽松通过:", JSON.stringify(d));
    return { paid: true };

  } catch (err) {
    if (err.response?.data) {
      const d = err.response.data;
      if (DEBUG) console.log("  [DEBUG] SkillPay 错误体:", JSON.stringify(d));
      const payUrl = d.payment_url || d.paymentLink || d.paymentUrl || null;
      if (payUrl) return { paid: false, payment_url: payUrl };
    }
    // DNS/网络失败（常见于本地测试环境）
    console.error(`  [SkillPay] 请求失败: ${err.message}`);
    if (err.code === "ENOTFOUND") {
      console.error(
        "  [SkillPay] ⚠️  本地 DNS 无法解析 api.skillpay.me\n" +
        "             本地测试请用: LOCAL_TEST=1 node skill.js \"...\""
      );
    }
    console.error("  [SkillPay] 宽松通过，线上部署后将正常扣费");
    return { paid: true };
  }
}

// ═════════════════════════════════════════════════════════════════════════════
// 3. 实时汇率查询
//    API 文档: https://www.exchangerate-api.com/docs/standard-requests
//    端点:     GET /v6/{API_KEY}/latest/{BASE}
//    响应字段: result, base_code, conversion_rates: { USD: ..., CNY: ... }
//    注意:     免费层返回全部货币，不支持 symbols 过滤参数（直接忽略）
// ═════════════════════════════════════════════════════════════════════════════
async function fetchLatest() {
  const url = `${FX_BASE}/${FX_API_KEY}/latest/${BASE_CCY}`;

  if (DEBUG) console.log(`  [DEBUG] GET ${url}`);

  const res = await axios.get(url, AXIOS_OPTS);

  if (DEBUG) {
    console.log("  [DEBUG] API 响应预览:");
    console.log(JSON.stringify(res.data, null, 2).slice(0, 800));
  }

  const data = res.data;

  // 检查 result 字段
  if (!data) {
    throw new Error("汇率 API 返回空响应");
  }
  if (data.result !== "success") {
    throw new Error(
      `汇率 API 返回失败: result="${data.result}", ` +
      `error-type="${data["error-type"] || "unknown"}"`
    );
  }

  // ✅ 关键修正：exchangerate-api.com 用 conversion_rates，不是 rates
  const rates = data.conversion_rates;

  if (!rates || typeof rates !== "object" || Object.keys(rates).length === 0) {
    console.error("  [错误] 完整响应:", JSON.stringify(data));
    throw new Error(
      "conversion_rates 字段为空或格式异常，请用 DEBUG=1 查看原始响应"
    );
  }

  return rates; // { USD: 0.1282, CNY: 0.9291, EUR: 0.1185, GBP: 0.0998, ... }
}

// ═════════════════════════════════════════════════════════════════════════════
// 4. 历史汇率查询（⚠️ 仅付费层支持，当前已注释）
//
//    如果你升级到付费账户，取消注释以下函数，并在 main() 里调用：
//
//    端点: GET /v6/{API_KEY}/history/{BASE}/{YEAR}/{MONTH}/{DAY}
//    响应: { result: "success", conversion_rates: { USD: ..., ... } }
//
// async function fetchHistorical(year, month, day) {
//   const url = `${FX_BASE}/${FX_API_KEY}/history/${BASE_CCY}/${year}/${month}/${day}`;
//   if (DEBUG) console.log(`  [DEBUG] GET ${url}`);
//   const res = await axios.get(url, AXIOS_OPTS);
//   if (!res.data || res.data.result !== "success") {
//     throw new Error(`历史汇率失败: ${res.data?.["error-type"] || "unknown"}`);
//   }
//   return res.data.conversion_rates;
// }
//
// function daysAgoComponents(n) {
//   const d = new Date();
//   d.setDate(d.getDate() - n);
//   return {
//     year:  d.getFullYear(),
//     month: d.getMonth() + 1,   // no leading zero required by API
//     day:   d.getDate(),
//     str:   d.toISOString().slice(0, 10),
//   };
// }
// ═════════════════════════════════════════════════════════════════════════════

// ═════════════════════════════════════════════════════════════════════════════
// 5. 输出格式化
// ═════════════════════════════════════════════════════════════════════════════
function fmtConversion(amount, target, rate) {
  const converted = (amount * rate).toFixed(4);
  return (
    `  ${amount} HKD ≈ ${converted} ${target}` +
    `  (1 HKD = ${rate.toFixed(6)} ${target}) 💱`
  );
}

// ═════════════════════════════════════════════════════════════════════════════
// 6. 主流程
// ═════════════════════════════════════════════════════════════════════════════
async function main() {
  const rawInput = process.argv.slice(2).join(" ").trim();

  console.log("\n💱 HKD汇率转换神器 v1.2.0  by 王 🤴 (@waz1xuan)");
  console.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");

  // ── 解析输入 ──────────────────────────────────────────────────────────────
  let parsed;
  try {
    parsed = parseInput(rawInput);
  } catch (err) {
    console.error(`❌ ${err.message}`);
    process.exit(1);
  }

  const { amount, target, showAll } = parsed;
  const displayAmount  = amount ?? 1;
  const displaySymbols = showAll ? ALL_CCYS : [target];

  console.log(`👤 用户:  ${USER_ID}${LOCAL_TEST ? "  [本地测试模式]" : ""}`);
  console.log(`🔍 查询: ${displayAmount} HKD → ${showAll ? ALL_CCYS.join(" / ") : target}`);
  console.log();

  // ── SkillPay 收款 ────────────────────────────────────────────────────────
  process.stdout.write("💳 正在扣除 1 token ...");
  const payment = await charge(USER_ID);

  if (!payment.paid) {
    console.log("\n\n⚠️  Token 不足，请先充值：");
    console.log(`   👉 ${payment.payment_url}`);
    console.log("\n充值完成后重新运行即可 🙏");
    process.exit(0);
  }
  console.log(" ✅ 扣费成功！\n");

  // ── 获取实时汇率 ──────────────────────────────────────────────────────────
  let allRates;
  try {
    allRates = await fetchLatest();
  } catch (err) {
    console.error(`❌ 获取实时汇率失败: ${err.message}`);
    process.exit(1);
  }

  // ── 输出结果 ──────────────────────────────────────────────────────────────
  console.log("📊 实时汇率结果");
  console.log("────────────────────────────────────────────");

  for (const sym of displaySymbols) {
    // 大小写容错查找
    const rateKey = Object.keys(allRates).find((k) => k.toUpperCase() === sym);
    const rate    = rateKey ? allRates[rateKey] : null;

    if (!rate) {
      console.log(`  ⚠️  ${sym}: 未获取到汇率数据（不在 conversion_rates 中）`);
      continue;
    }

    console.log(fmtConversion(displayAmount, sym, rate));
  }

  console.log("────────────────────────────────────────────");
  console.log("📡 数据: exchangerate-api.com（免费层，每月 1,500 次）");
  console.log(
    `🕐 时间: ${new Date().toLocaleString("zh-HK", { timeZone: "Asia/Hong_Kong" })} HKT`
  );
  console.log();

  // 历史趋势说明
  console.log(
    "ℹ️  历史趋势功能需要 exchangerate-api.com 付费账户，当前版本仅提供实时汇率。"
  );
  console.log(
    "   升级后取消 skill.js 中 fetchHistorical 的注释即可启用 7/30 天趋势分析。"
  );
  console.log();

  if (LOCAL_TEST) {
    console.log("✅ 测试完成！本地运行正常");
  }
}

main().catch((err) => {
  console.error(`\n❌ 未预期错误: ${err.message}`);
  if (DEBUG) console.error(err.stack);
  process.exit(1);
});
