import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { CallToolRequestSchema, ListToolsRequestSchema } from "@modelcontextprotocol/sdk/types.js";

const TOKEN = process.env.STOCKTODAY_TOKEN || "";
const BASE_URL = process.env.STOCKTODAY_URL || "https://tushare.citydata.club/";

if (!TOKEN) {
  console.error("⚠️ 请设置环境变量 STOCKTODAY_TOKEN 或 TUSHARE_TOKEN");
}

const server = new Server({ name: "stocktoday-mcp", version: "1.0.0" }, { capabilities: { tools: {} } });

async function callAPI(endpoint: string, params: Record<string, any> = {}, token: string = TOKEN): Promise<any> {
  const formData = new URLSearchParams();
  formData.append("TOKEN", token);
  for (const [k, v] of Object.entries(params)) {
    if (v !== undefined && v !== "") formData.append(k, String(v));
  }
  try {
    const res = await fetch(`${BASE_URL}${endpoint}`, { method: "POST", body: formData, headers: { "Content-Type": "application/x-www-form-urlencoded" } });
    return await res.json();
  } catch (e: any) { return { error: e.message }; }
}

// Tool definition type
interface ToolDef {
  name: string;
  desc: string;
  params: Record<string, string>;
}

// All tools
const tools: ToolDef[] = [
  // 股票-基础数据
  { name: "stock_basic", desc: "股票基本信息", params: { exchange: "交易所", list_status: "上市状态", ts_code: "股票代码", market: "市场", fields: "返回字段" }},
  { name: "stk_premarket", desc: "新股上市", params: { ts_code: "股票代码", trade_date: "交易日期", start_date: "开始日期", end_date: "结束日期" }},
  { name: "trade_cal", desc: "交易日历", params: { exchange: "交易所", start_date: "开始日期", end_date: "结束日期" }},
  { name: "namechange", desc: "股票名称变更", params: { ts_code: "股票代码", start_date: "开始日期", end_date: "结束日期" }},
  { name: "hs_const", desc: "沪深股通成分股", params: { hs_type: "类型", is_new: "是否最新" }},
  { name: "stock_company", desc: "上市公司信息", params: { ts_code: "股票代码", exchange: "交易所" }},
  { name: "stk_managers", desc: "公司管理层", params: { ts_code: "股票代码", start_date: "开始日期", end_date: "结束日期", ann_date: "公告日期" }},
  { name: "stk_rewards", desc: "高管薪酬", params: { ts_code: "股票代码" }},
  { name: "new_share", desc: "新股上市", params: { start_date: "开始日期", end_date: "结束日期" }},
  { name: "bak_basic", desc: "备用基础数据", params: { exchange: "交易所", ts_code: "股票代码" }},

  // 股票-行情数据
  { name: "daily", desc: "日线行情", params: { ts_code: "股票代码", trade_date: "交易日期", start_date: "开始日期", end_date: "结束日期" }},
  { name: "weekly", desc: "周线行情", params: { ts_code: "股票代码", trade_date: "交易日期", start_date: "开始日期", end_date: "结束日期", fields: "返回字段" }},
  { name: "monthly", desc: "月线行情", params: { ts_code: "股票代码", trade_date: "交易日期", start_date: "开始日期", end_date: "结束日期", fields: "返回字段" }},
  { name: "pro_bar", desc: "行情(支持复权)", params: { ts_code: "股票代码", start_date: "开始日期", end_date: "结束日期", asset: "资产", adj: "复权", freq: "频率", ma: "均线", factors: "因子" }},
  { name: "adj_factor", desc: "复权因子", params: { ts_code: "股票代码", trade_date: "交易日期", start_date: "开始日期", end_date: "结束日期" }},
  { name: "daily_basic", desc: "每日指标", params: { ts_code: "股票代码", trade_date: "交易日期", fields: "返回字段" }},
  { name: "stk_limit", desc: "涨跌停", params: { ts_code: "股票代码", trade_date: "交易日期", start_date: "开始日期", end_date: "结束日期" }},
  { name: "suspend_d", desc: "停复牌", params: { ts_code: "股票代码", trade_date: "交易日期", start_date: "开始日期", end_date: "结束日期", suspend_type: "类型" }},
  { name: "hsgt_top10", desc: "沪深股通前十", params: { trade_date: "交易日期", start_date: "开始日期", end_date: "结束日期", market_type: "市场类型" }},
  { name: "ggt_top10", desc: "广港通前十", params: { trade_date: "交易日期", ts_code: "股票代码", start_date: "开始日期", end_date: "结束日期" }},
  { name: "ggt_daily", desc: "广港通每日", params: { trade_date: "交易日期", start_date: "开始日期", end_date: "结束日期" }},
  { name: "ggt_monthly", desc: "广港通每月", params: { trade_date: "交易日期", start_date: "开始日期", end_date: "结束日期" }},
  { name: "bak_daily", desc: "备用每日行情", params: { ts_code: "股票代码", trade_date: "交易日期", start_date: "开始日期", end_date: "结束日期", fields: "返回字段" }},

  // 股票-财务数据
  { name: "income", desc: "利润表", params: { ts_code: "股票代码", start_date: "开始日期", end_date: "结束日期", fields: "返回字段" }},
  { name: "balancesheet", desc: "资产负债表", params: { ts_code: "股票代码", start_date: "开始日期", end_date: "结束日期", fields: "返回字段" }},
  { name: "cashflow", desc: "现金流量表", params: { ts_code: "股票代码", start_date: "开始日期", end_date: "结束日期", fields: "返回字段" }},
  { name: "forecast", desc: "业绩预告", params: { ann_date: "公告日期", fields: "返回字段" }},
  { name: "express", desc: "业绩快报", params: { ts_code: "股票代码", start_date: "开始日期", end_date: "结束日期", fields: "返回字段" }},
  { name: "dividend", desc: "分红送股", params: { ts_code: "股票代码", fields: "返回字段" }},
  { name: "fina_indicator", desc: "财务指标", params: { ts_code: "股票代码" }},
  { name: "fina_audit", desc: "财务审计", params: { ts_code: "股票代码", start_date: "开始日期", end_date: "结束日期" }},
  { name: "fina_mainbz", desc: "主营业务", params: { ts_code: "股票代码", type: "类型" }},
  { name: "disclosure_date", desc: "披露日期", params: { end_date: "结束日期" }},

  // 股票-参考数据
  { name: "top10_holders", desc: "十大股东", params: { ts_code: "股票代码", start_date: "开始日期", end_date: "结束日期" }},
  { name: "top10_floatholders", desc: "十大流通股东", params: { ts_code: "股票代码", start_date: "开始日期", end_date: "结束日期" }},
  { name: "pledge_stat", desc: "股权质押统计", params: { ts_code: "股票代码" }},
  { name: "pledge_detail", desc: "股权质押明细", params: { ts_code: "股票代码" }},
  { name: "repurchase", desc: "股份回购", params: { ann_date: "公告日期", start_date: "开始日期", end_date: "结束日期" }},
  { name: "concept", desc: "概念列表", params: {} },
  { name: "concept_detail", desc: "概念详情", params: { id: "概念ID", ts_code: "股票代码" }},
  { name: "share_float", desc: "流通股本", params: { ann_date: "公告日期" }},
  { name: "block_trade", desc: "大宗交易", params: { trade_date: "交易日期" }},
  { name: "stk_holdernumber", desc: "股东户数", params: { ts_code: "股票代码", start_date: "开始日期", end_date: "结束日期" }},
  { name: "stk_holdertrade", desc: "股东增减持", params: { ts_code: "股票代码", ann_date: "公告日期", trade_type: "交易类型" }},

  // 股票-特色数据
  { name: "report_rc", desc: "研报", params: { ts_code: "股票代码", report_date: "报告日期" }},
  { name: "cyq_perf", desc: "筹码活跃度", params: { ts_code: "股票代码", start_date: "开始日期", end_date: "结束日期" }},
  { name: "cyq_chips", desc: "筹码分布", params: { ts_code: "股票代码", start_date: "开始日期", end_date: "结束日期" }},
  { name: "stk_factor", desc: "股票因子", params: { ts_code: "股票代码", start_date: "开始日期", end_date: "结束日期", fields: "返回字段" }},
  { name: "stk_factor_pro", desc: "股票因子(专业版)", params: { ts_code: "股票代码", start_date: "开始日期", end_date: "结束日期", fields: "返回字段" }},
  { name: "ccass_hold", desc: "中央结算持股", params: { ts_code: "股票代码" }},
  { name: "ccass_hold_detail", desc: "中央结算持股明细", params: { ts_code: "股票代码", trade_date: "交易日期", fields: "返回字段" }},
  { name: "hk_hold", desc: "港股持股", params: { ts_code: "股票代码", exchange: "交易所" }},
  { name: "stk_auction_o", desc: "集合竞价", params: { ts_code: "股票代码", trade_date: "交易日期", start_date: "开始日期", end_date: "结束日期" }},
  { name: "stk_auction_c", desc: "盘后定价", params: { ts_code: "股票代码", trade_date: "交易日期", start_date: "开始日期", end_date: "结束日期" }},
  { name: "stk_nineturn", desc: "九转序列", params: { ts_code: "股票代码", trade_date: "交易日期", start_date: "开始日期", end_date: "结束日期", fields: "返回字段" }},
  { name: "stk_surv", desc: "舆情监控", params: { ts_code: "股票代码", trade_date: "交易日期", fields: "返回字段" }},
  { name: "broker_recommend", desc: "券商研报推荐", params: { month: "月份" }},

  // 股票-两融
  { name: "margin", desc: "融资融券", params: { trade_date: "交易日期" }},
  { name: "margin_detail", desc: "融资融券明细", params: { trade_date: "交易日期" }},
  { name: "margin_secs", desc: "融资融券证券", params: { trade_date: "交易日期", exchange: "交易所" }},
  { name: "slb_sec", desc: "融券余量", params: { trade_date: "交易日期" }},
  { name: "slb_len", desc: "融资期限", params: { trade_date: "交易日期", start_date: "开始日期", end_date: "结束日期" }},
  { name: "slb_sec_detail", desc: "融券余量明细", params: { trade_date: "交易日期" }},
  { name: "slb_len_mm", desc: "融资期限明细", params: { trade_date: "交易日期" }},

  // 股票-资金流向
  { name: "moneyflow", desc: "资金流向", params: { ts_code: "股票代码", trade_date: "交易日期", start_date: "开始日期", end_date: "结束日期" }},
  { name: "moneyflow_ths", desc: "资金流向(同花顺)", params: { ts_code: "股票代码", trade_date: "交易日期", start_date: "开始日期", end_date: "结束日期" }},
  { name: "moneyflow_cnt_ths", desc: "资金流向分类(同花顺)", params: { trade_date: "交易日期" }},
  { name: "moneyflow_dc", desc: "资金流向(东方财富)", params: { ts_code: "股票代码", trade_date: "交易日期", start_date: "开始日期", end_date: "结束日期" }},
  { name: "moneyflow_ind_ths", desc: "行业资金流向(同花顺)", params: { ts_code: "股票代码", trade_date: "交易日期", start_date: "开始日期", end_date: "结束日期" }},
  { name: "moneyflow_ind_dc", desc: "行业资金流向(东方财富)", params: { ts_code: "股票代码", trade_date: "交易日期", start_date: "开始日期", end_date: "结束日期" }},
  { name: "moneyflow_mkt_dc", desc: "市场资金流向(东方财富)", params: { trade_date: "交易日期", start_date: "开始日期", end_date: "结束日期" }},
  { name: "moneyflow_hsgt", desc: "沪深港通资金流向", params: { ts_code: "股票代码", trade_date: "交易日期", start_date: "开始日期", end_date: "结束日期" }},

  // 股票-打板专题
  { name: "kpl_concept", desc: "开盘啦概念", params: { trade_date: "交易日期" }},
  { name: "kpl_concept_cons", desc: "开盘啦概念成分", params: { trade_date: "交易日期" }},
  { name: "kpl_list", desc: "开盘啦列表", params: { trade_date: "交易日期", tag: "标签", fields: "返回字段" }},
  { name: "top_list", desc: "龙虎榜上榜", params: { trade_date: "交易日期" }},
  { name: "top_inst", desc: "龙虎榜机构", params: { trade_date: "交易日期" }},
  { name: "limit_list_ths", desc: "涨停列表(同花顺)", params: { trade_date: "交易日期", limit_type: "涨停类型", fields: "返回字段" }},
  { name: "limit_list_d", desc: "涨跌停明细", params: { trade_date: "交易日期", limit_type: "涨跌停类型", fields: "返回字段" }},
  { name: "limit_step", desc: "涨停阶梯", params: { ts_code: "股票代码", trade_date: "交易日期", start_date: "开始日期", end_date: "结束日期", nums: "数量" }},
  { name: "limit_cpt_list", desc: "涨停股票池", params: { ts_code: "股票代码", trade_date: "交易日期", start_date: "开始日期", end_date: "结束日期" }},
  { name: "ths_index", desc: "同花顺指数", params: {} },
  { name: "ths_member", desc: "同花顺成分股", params: { ts_code: "股票代码" }},
  { name: "dc_index", desc: "东财指数", params: { ts_code: "股票代码", trade_date: "交易日期", start_date: "开始日期", end_date: "结束日期" }},
  { name: "dc_member", desc: "东财成分股", params: { ts_code: "股票代码", trade_date: "交易日期" }},
  { name: "stk_auction", desc: "股票集合竞价", params: { ts_code: "股票代码", trade_date: "交易日期", start_date: "开始日期", end_date: "结束日期" }},
  { name: "hm_list", desc: "活跃股列表", params: {} },
  { name: "hm_detail", desc: "活跃股明细", params: { trade_date: "交易日期" }},
  { name: "ths_hot", desc: "同花顺热点", params: { market: "市场", trade_date: "交易日期", fields: "返回字段" }},
  { name: "dc_hot", desc: "东方财富热点", params: { market: "市场", hot_type: "热点类型", trade_date: "交易日期", fields: "返回字段" }},

  // 指数
  { name: "index_basic", desc: "指数基本信息", params: { market: "市场" }},
  { name: "index_daily", desc: "指数日线", params: { ts_code: "指数代码", start_date: "开始日期", end_date: "结束日期" }},
  { name: "index_weekly", desc: "指数周线", params: { ts_code: "指数代码", start_date: "开始日期", end_date: "结束日期", fields: "返回字段" }},
  { name: "index_monthly", desc: "指数月线", params: { ts_code: "指数代码", start_date: "开始日期", end_date: "结束日期", fields: "返回字段" }},
  { name: "index_weight", desc: "指数成分", params: { index_code: "指数代码", start_date: "开始日期", end_date: "结束日期" }},
  { name: "index_dailybasic", desc: "指数每日指标", params: { trade_date: "交易日期", fields: "返回字段" }},
  { name: "index_classify", desc: "指数分类", params: { level: "级别", src: "来源" }},
  { name: "index_member", desc: "指数成分股", params: { index_code: "指数代码", ts_code: "股票代码" }},
  { name: "index_member_all", desc: "指数成分股(全)", params: { l1_code: "一级代码", l2_code: "二级代码", l3_code: "三级代码", ts_code: "股票代码" }},
  { name: "daily_info", desc: "每日信息", params: { trade_date: "交易日期", exchange: "交易所", fields: "返回字段" }},
  { name: "sz_daily_info", desc: "深市每日信息", params: { trade_date: "交易日期", ts_code: "股票代码" }},
  { name: "ths_daily", desc: "同花顺指数日线", params: { ts_code: "指数代码", start_date: "开始日期", end_date: "结束日期", fields: "返回字段" }},
  { name: "ci_daily", desc: "中证指数日线", params: { trade_date: "交易日期", fields: "返回字段" }},
  { name: "sw_daily", desc: "申万指数日线", params: { trade_date: "交易日期", fields: "返回字段" }},
  { name: "index_global", desc: "全球指数", params: { ts_code: "指数代码", start_date: "开始日期", end_date: "结束日期" }},
  { name: "idx_factor_pro", desc: "指数因子(专业版)", params: { ts_code: "指数代码", trade_date: "交易日期", start_date: "开始日期", end_date: "结束日期" }},

  // 基金
  { name: "fund_basic", desc: "基金基本信息", params: { market: "市场" }},
  { name: "fund_company", desc: "基金公司", params: {} },
  { name: "fund_manager", desc: "基金经理", params: { ts_code: "基金代码" }},
  { name: "fund_share", desc: "基金份额", params: { ts_code: "基金代码" }},
  { name: "fund_nav", desc: "基金净值", params: { ts_code: "基金代码" }},
  { name: "fund_div", desc: "基金分红", params: { ann_date: "公告日期" }},
  { name: "fund_portfolio", desc: "基金持仓", params: { ts_code: "基金代码" }},
  { name: "fund_daily", desc: "基金日线", params: { ts_code: "基金代码", start_date: "开始日期", end_date: "结束日期" }},
  { name: "fund_adj", desc: "基金复权", params: { ts_code: "基金代码", start_date: "开始日期", end_date: "结束日期" }},
  { name: "fund_factor_pro", desc: "基金因子(专业版)", params: { ts_code: "基金代码", trade_date: "交易日期", start_date: "开始日期", end_date: "结束日期" }},

  // 期货
  { name: "fut_basic", desc: "期货基本信息", params: { exchange: "交易所", fut_type: "期货类型", fields: "返回字段" }},
  { name: "fut_daily", desc: "期货日线", params: { ts_code: "期货代码", trade_date: "交易日期", start_date: "开始日期", end_date: "结束日期", exchange: "交易所", fields: "返回字段" }},
  { name: "fut_weekly_monthly", desc: "期货周/月线", params: { ts_code: "期货代码", trade_date: "交易日期", start_date: "开始日期", end_date: "结束日期", freq: "频率", exchange: "交易所" }},
  { name: "ft_mins", desc: "期货分钟线", params: { ts_code: "期货代码", start_date: "开始日期", end_date: "结束日期", freq: "频率" }},
  { name: "fut_wsr", desc: "期货持仓", params: { trade_date: "交易日期", symbol: "合约" }},
  { name: "fut_settle", desc: "期货结算", params: { trade_date: "交易日期", exchange: "交易所" }},
  { name: "fut_holding", desc: "期货持仓量", params: { trade_date: "交易日期", symbol: "合约", exchange: "交易所" }},
  { name: "fut_mapping", desc: "期货映射", params: { ts_code: "期货代码", trade_date: "交易日期", start_date: "开始日期", end_date: "结束日期" }},
  { name: "fut_weekly_detail", desc: "期货每周详情", params: { prd: "产品", start_week: "开始周", end_week: "结束周", fields: "返回字段" }},
  { name: "ft_limit", desc: "期货涨跌停", params: { trade_date: "交易日期", ts_code: "期货代码", cont: "合约" }},

  // 现货
  { name: "sge_basic", desc: "现货基本信息", params: {} },
  { name: "sge_daily", desc: "现货每日行情", params: {} },

  // 期权
  { name: "opt_basic", desc: "期权基本信息", params: { exchange: "交易所", fields: "返回字段" }},
  { name: "opt_daily", desc: "期权每日行情", params: { ts_code: "期权代码", trade_date: "交易日期", start_date: "开始日期", end_date: "结束日期" }},

  // 可转债
  { name: "cb_basic", desc: "可转债基本信息", params: {} },
  { name: "cb_issue", desc: "可转债发行", params: {} },
  { name: "cb_call", desc: "可转债回售", params: {} },
  { name: "cb_rate", desc: "可转债转股溢价率", params: {} },
  { name: "cb_daily", desc: "可转债每日行情", params: { ts_code: "可转债代码", trade_date: "交易日期", start_date: "开始日期", end_date: "结束日期" }},
  { name: "cb_price_chg", desc: "可转债价格变化", params: {} },
  { name: "cb_share", desc: "可转债转股", params: {} },

  // 其他
  { name: "repo_daily", desc: "回购每日行情", params: {} },
  { name: "bc_otcqt", desc: "银行间报价", params: {} },
  { name: "bc_bestotcqt", desc: "银行间最优报价", params: {} },
  { name: "bond_blk", desc: "债券大宗交易", params: {} },
  { name: "bond_blk_detail", desc: "债券大宗交易明细", params: {} },
  { name: "yc_cb", desc: "可转债收益率", params: {} },
  { name: "eco_cal", desc: "经济日历", params: {} },
  { name: "fx_obasic", desc: "外汇基本信息", params: {} },
  { name: "fx_daily", desc: "外汇每日行情", params: {} },

  // 港股
  { name: "hk_basic", desc: "港股基本信息", params: {} },
  { name: "hk_tradecal", desc: "港股交易日历", params: { start_date: "开始日期", end_date: "结束日期" }},
  { name: "hk_daily", desc: "港股每日行情", params: { ts_code: "港股代码", start_date: "开始日期", end_date: "结束日期" }},
  { name: "hk_daily_adj", desc: "港股每日行情(复权)", params: { ts_code: "港股代码", start_date: "开始日期", end_date: "结束日期" }},
  { name: "hk_mins", desc: "港股分钟线", params: { ts_code: "港股代码", start_date: "开始日期", end_date: "结束日期", freq: "频率" }},

  // 美股
  { name: "us_basic", desc: "美股基本信息", params: {} },
  { name: "us_tradecal", desc: "美股交易日历", params: { start_date: "开始日期", end_date: "结束日期" }},
  { name: "us_daily", desc: "美股每日行情", params: { ts_code: "美股代码", start_date: "开始日期", end_date: "结束日期" }},
  { name: "us_daily_adj", desc: "美股每日行情(复权)", params: { ts_code: "美股代码", start_date: "开始日期", end_date: "结束日期" }},
];

// Register tools
server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: tools.map(t => ({
    name: t.name,
    description: t.desc,
    inputSchema: { type: "object", properties: t.params },
  })),
}));

// Endpoint mapping
const endpointMap: Record<string, string> = {};
for (const t of tools) {
  endpointMap[t.name] = "/" + t.name;
}

// Handle calls
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params as { name: string; arguments: Record<string, any> };
  const endpoint = endpointMap[name];
  if (!endpoint) {
    return { content: [{ type: "text", text: JSON.stringify({ error: `Unknown tool: ${name}` }) }] };
  }
  try {
    const params: Record<string, any> = {};
    for (const [k, v] of Object.entries(args || {})) {
      if (v !== undefined && v !== "" && v !== null) {
        params[k] = v;
      }
    }
    // 支持通过参数传入 token
    const token = params.token || TOKEN;
    if (!token) {
      return { content: [{ type: "text", text: JSON.stringify({ error: "请设置 STOCKTODAY_TOKEN 环境变量或传入 token 参数" }) }] };
    }
    // 从 params 中移除 token，避免传递给 API
    delete params.token;
    const result = await callAPI(endpoint, params, token);
    return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
  } catch (e: any) {
    return { content: [{ type: "text", text: JSON.stringify({ error: e.message }) }] };
  }
});

// Start server
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("StockToday MCP running");
}
main().catch(console.error);
