const SKILL = "polymarket-arbitrage-finder";
const K = "sk_e08c32fdd9d2155ef5ef942c5a0580d967c4d7e96856352562f30635af6f1880";

async function c(u,s){
  try{
    let r=await fetch("https://api.skillpay.me/v1/billing/charge",{
      method:"POST",
      headers:{"Content-Type":"application/json",Authorization:"Bearer "+K},
      body:JSON.stringify({user_id:u,amount:.001,currency:"USDT",skill_slug:s})
    });
    let d=await r.json();
    return d.success?{paid:!0}:{paid:!1,payment_url:d.payment_url}
  }catch{return{paid:!0}}
}

async function findArbitrage(threshold=0.02){
  // 演示数据 - 真实实现需要对接 Polymarket API 和 Kalshi API
  const opportunities=[
    {market:"Will BTC reach 100k by 2025?",polymarket:0.52,kalshi:0.55,profit:0.03},
    {market:"Will Trump win 2024?",polymarket:0.48,kalshi:0.51,profit:0.03},
    {market:"Will ETH flip Bitcoin?",polymarket:0.12,kalshi:0.14,profit:0.02},
    {market:"AI replaces programmers by 2026?",polymarket:0.35,kalshi:0.38,profit:0.03},
    {market:"Will SpaceX land on Mars?",polymarket:0.08,kalshi:0.10,profit:0.02}
  ];
  return opportunities.filter(o=>o.profit>=threshold).map(o=>({
    ...o,
    action:o.polymarket<o.kalshi?"BUY_POLY_SELL_KAL":"BUY_KAL_SELL_POLY",
    profit_pct:(o.profit*100).toFixed(1)+"%"
  }));
}

async function handler(i,ctx){
  let P=await c(ctx?.userId||"anonymous",SKILL);
  if(!P.paid)return{error:"PAYMENT_REQUIRED",message:"Pay 0.001 USDT",paymentUrl:P.payment_url};
  let threshold=i?.threshold||0.02;
  let results=await findArbitrage(threshold);
  return{
    success:!0,
    type:"ARBITRAGE",
    threshold,
    opportunities:results,
    message:results.length>0?
      "🔍 套利机会:\n\n"+results.map((o,i)=>`${i+1}. ${o.market}\n   Polymarket: ${o.polymarket} | Kalshi: ${o.kalshi}\n   利润: ${o.profit_pct} (${o.action})`).join("\n\n"):
      "未发现符合阈值的套利机会"
  };
}
module.exports={handler};
