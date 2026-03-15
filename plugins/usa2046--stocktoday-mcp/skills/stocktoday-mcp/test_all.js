#!/usr/bin/env node

const tools = [
  // 基础数据
  "stock_basic", "stk_premarket", "trade_cal", "namechange", "hs_const", 
  "stock_company", "stk_managers", "stk_rewards", "new_share", "bak_basic",
  // 行情数据
  "daily", "weekly", "monthly", "pro_bar", "adj_factor", "daily_basic", 
  "stk_limit", "suspend_d", "hsgt_top10", "ggt_top10", "ggt_daily", "ggt_monthly", "bak_daily",
  // 财务数据
  "income", "balancesheet", "cashflow", "forecast", "express", "dividend", 
  "fina_indicator", "fina_audit", "fina_mainbz", "disclosure_date",
  // 参考数据
  "top10_holders", "top10_floatholders", "pledge_stat", "pledge_detail", 
  "repurchase", "concept", "concept_detail", "share_float", "block_trade", 
  "stk_holdernumber", "stk_holdertrade",
  // 特色数据
  "report_rc", "cyq_perf", "cyq_chips", "stk_factor", "stk_factor_pro", 
  "ccass_hold", "ccass_hold_detail", "hk_hold", "stk_auction_o", "stk_auction_c", 
  "stk_nineturn", "stk_surv", "broker_recommend",
  // 两融
  "margin", "margin_detail", "margin_secs", "slb_sec", "slb_len", "slb_sec_detail", "slb_len_mm",
  // 资金流向
  "moneyflow", "moneyflow_ths", "moneyflow_cnt_ths", "moneyflow_dc", 
  "moneyflow_ind_ths", "moneyflow_ind_dc", "moneyflow_mkt_dc", "moneyflow_hsgt",
  // 打板专题
  "kpl_concept", "kpl_concept_cons", "kpl_list", "top_list", "top_inst", 
  "limit_list_ths", "limit_list_d", "limit_step", "limit_cpt_list", 
  "ths_index", "ths_member", "dc_index", "dc_member", "stk_auction", 
  "hm_list", "hm_detail", "ths_hot", "dc_hot",
  // 指数
  "index_basic", "index_daily", "index_weekly", "index_monthly", "index_weight", 
  "index_dailybasic", "index_classify", "index_member", "index_member_all", 
  "daily_info", "sz_daily_info", "ths_daily", "ci_daily", "sw_daily", "index_global", "idx_factor_pro",
  // 基金
  "fund_basic", "fund_company", "fund_manager", "fund_share", "fund_nav", 
  "fund_div", "fund_portfolio", "fund_daily", "fund_adj", "fund_factor_pro",
  // 期货
  "fut_basic", "fut_daily", "fut_weekly_monthly", "ft_mins", "fut_wsr", 
  "fut_settle", "fut_holding", "fut_mapping", "fut_weekly_detail", "ft_limit",
  // 现货
  "sge_basic", "sge_daily",
  // 期权
  "opt_basic", "opt_daily",
  // 可转债
  "cb_basic", "cb_issue", "cb_call", "cb_rate", "cb_daily", "cb_price_chg", "cb_share",
  // 其他
  "repo_daily", "bc_otcqt", "bc_bestotcqt", "bond_blk", "bond_blk_detail", 
  "yc_cb", "eco_cal", "fx_obasic", "fx_daily",
  // 港股
  "hk_basic", "hk_tradecal", "hk_daily", "hk_daily_adj", "hk_mins",
  // 美股
  "us_basic", "us_tradecal", "us_daily", "us_daily_adj"
];

const BASE_URL = "https://tushare.citydata.club/";
const TOKEN = "citydata";

async function callAPI(endpoint, params = {}) {
  const formData = new URLSearchParams();
  formData.append("TOKEN", TOKEN);
  for (const [k, v] of Object.entries(params)) {
    if (v !== undefined && v !== "") formData.append(k, String(v));
  }
  try {
    const res = await fetch(`${BASE_URL}${endpoint}`, {
      method: "POST",
      body: formData,
      headers: { "Content-Type": "application/x-www-form-urlencoded" }
    });
    return await res.json();
  } catch (e) {
    return { error: e.message };
  }
}

async function testTools() {
  console.log(`Testing ${tools.length} tools...\n`);
  
  let success = 0;
  let failed = 0;
  const errors = [];

  for (const tool of tools) {
    const endpoint = "/" + tool;
    try {
      // 通用参数测试
      const params = getTestParams(tool);
      const result = await callAPI(endpoint, params);
      
      if (result.error) {
        failed++;
        errors.push(`${tool}: ${result.error}`);
      } else if (Array.isArray(result)) {
        success++;
        process.stdout.write(`✅ ${tool} (${result.length} rows)\n`);
      } else if (result.data) {
        success++;
        process.stdout.write(`✅ ${tool} (${result.data.length || 1} rows)\n`);
      } else {
        success++;
        process.stdout.write(`✅ ${tool}\n`);
      }
    } catch (e) {
      failed++;
      errors.push(`${tool}: ${e.message}`);
    }
  }

  console.log(`\n=== Results ===`);
  console.log(`Success: ${success}`);
  console.log(`Failed: ${failed}`);
  
  if (errors.length > 0) {
    console.log(`\nErrors:`);
    errors.forEach(e => console.log(`  - ${e}`));
  }
}

function getTestParams(tool) {
  const params = {};
  
  // 股票代码
  if (tool.includes("stock") || tool.includes("stk") || tool.includes("daily") || 
      tool.includes("income") || tool.includes("balance") || tool.includes("cashflow") ||
      tool.includes("dividend") || tool.includes("fina") || tool.includes("holder") ||
      tool.includes("margin") || tool.includes("moneyflow") || tool.includes("auction") ||
      tool.includes("factor") || tool.includes("pledge") || tool.includes("concept") ||
      tool.includes("report") || tool.includes("cyq") || tool.includes("surv") || 
      tool.includes("manager") || tool.includes("reward")) {
    params.ts_code = "600519.SH";
  }
  
  // 指数代码
  if (tool.includes("index") && !tool.includes("stock")) {
    params.ts_code = "000001.SH";
  }
  
  // 基金代码
  if (tool.includes("fund")) {
    params.ts_code = "000001.OF";
  }
  
  // 期货代码
  if (tool.includes("fut")) {
    params.ts_code = "IF9999.CF";
  }
  
  // 日期参数
  if (tool !== "stock_basic" && tool !== "index_basic" && tool !== "fund_basic" &&
      tool !== "fut_basic" && tool !== "concept" && tool !== "ths_index" &&
      tool !== "hk_basic" && tool !== "us_basic" && tool !== "sge_basic" &&
      tool !== "cb_basic" && tool !== "opt_basic" && tool !== "hm_list" &&
      tool !== "trade_cal" && tool !== "report_rc") {
    params.trade_date = "20250110";
    params.start_date = "20250101";
    params.end_date = "20250110";
  }
  
  return params;
}

testTools();
